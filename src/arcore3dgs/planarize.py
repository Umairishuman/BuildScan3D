"""Plane-regularised 3DGS: snap wall / floor / ceiling splats onto detected planes, then a short re-fit.

Never modifies the input model; everything is written to --out.

1. Planes from splat POSITIONS, using ARCore gravity (+Y up; the model is in the ARCore metric world):
   - horizontal planes (floor, ceiling, table tops): density peaks of splat height;
   - walls: the Manhattan angle that makes projected splat positions sharpest, then density peaks of the
     offset along both wall directions. (Splat orientations on plain walls are too noisy to use.)
   Each plane is limited to its connected support (5 cm occupancy grid, components >= --min_area m2), so an
   infinite plane does not swallow unrelated objects at the same height / offset.
2. Snap: splats within --tau of a plane, inside its support and facing the same way, get their centre moved
   onto the plane, their thin axis aligned to the plane normal and their thickness set to --thickness.
3. Re-fit (--refit_steps): gsplat fine-tune on the training frames (full res, nerfstudio 90% split) with
   per-image affine colour correction (stands in for splatfacto's bilateral grid); planar splats stay on
   their plane (projected after every step, rotation + thickness frozen), all other splats are free.

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/planarize.py --ply <splat.ply> --work <work_sfm> --out <dir>
Outputs: <out>/splat_snapped.ply, <out>/splat.ply (re-fitted), <out>/planes.json
"""
import os, json, argparse, time
import numpy as np, cv2, torch, torch.nn.functional as F
from plyfile import PlyData, PlyElement
from scipy import ndimage
from scipy.spatial.transform import Rotation as Rot

ap = argparse.ArgumentParser()
ap.add_argument("--ply", required=True)
ap.add_argument("--work", required=True, help="work_sfm dir (frames.json + undistorted images/) for the re-fit")
ap.add_argument("--out", required=True)
ap.add_argument("--tau", type=float, default=0.025, help="m, max distance of a splat to its plane")
ap.add_argument("--angle", type=float, default=30.0, help="deg, max angle between splat normal and plane normal")
ap.add_argument("--inner_planes", type=int, default=0, help="1 = also snap inner planes (table tops, furniture faces)")
ap.add_argument("--use_normals", type=int, default=0, help="1 = flat splats must face the plane to be snapped")
ap.add_argument("--min_area", type=float, default=0.5, help="m2, smallest plane support component kept")
ap.add_argument("--thickness", type=float, default=0.002, help="m, splat thickness along the plane normal")
ap.add_argument("--refit_steps", type=int, default=3000)
args = ap.parse_args()
assert os.path.abspath(args.out) != os.path.abspath(os.path.dirname(args.ply)), "write to a new folder"
os.makedirs(args.out, exist_ok=True)
dev = "cuda"
UP = np.array([0.0, 1.0, 0.0])

ply = PlyData.read(args.ply); v = ply["vertex"]; D = v.data
P = np.stack([D["x"], D["y"], D["z"]], 1).astype(np.float64)
logS = np.stack([D[f"scale_{i}"] for i in range(3)], 1).astype(np.float64); S = np.exp(logS)
Q = np.stack([D[f"rot_{i}"] for i in range(4)], 1).astype(np.float64); Q /= np.linalg.norm(Q, axis=1, keepdims=True)
OP = 1 / (1 + np.exp(-D["opacity"].astype(np.float64)))
Rm = Rot.from_quat(Q[:, [1, 2, 3, 0]]).as_matrix()                       # ply quats are wxyz
order = np.argsort(S, 1); smin, smid, smax = [np.take_along_axis(S, order[:, k:k + 1], 1)[:, 0] for k in range(3)]
Nrm = np.take_along_axis(Rm, order[:, None, 0:1].repeat(3, 1), 2)[..., 0]  # axis of the smallest scale
flat = (smin < 0.35 * smid) & (OP > 0.3)
area = smid * smax * OP
print(f"{len(P)} splats, {flat.sum()} flat & opaque")


def peaks(x, lo, hi, bin_=0.01, min_rel=0.15, sep=0.15):
    """density peaks of splat positions above a local background (walls/floors are thin dense layers)."""
    h, e = np.histogram(x, bins=max(10, int((hi - lo) / bin_)), range=(lo, hi))
    h = ndimage.gaussian_filter1d(h.astype(float), 1.0); c = 0.5 * (e[1:] + e[:-1])
    pr = h - ndimage.median_filter(h, size=41); out = []
    for i in np.argsort(-pr):
        if pr[i] < min_rel * pr.max():
            break
        if all(abs(c[i] - c[j]) > sep for j in out):
            out.append(i)
    return [float(c[i]) for i in out]


def support(mask, U, V, cell=0.05):
    """keep splats of a plane candidate that lie in large connected regions of the plane."""
    if mask.sum() < 50:
        return np.zeros_like(mask), 0.0
    u, w_ = U[mask], V[mask]; u0, w0 = u.min(), w_.min()
    iu = ((u - u0) / cell).astype(int); iv = ((w_ - w0) / cell).astype(int)
    G = np.zeros((iu.max() + 1, iv.max() + 1), bool); G[iu, iv] = True
    G = ndimage.binary_closing(G, iterations=2)
    lab, n = ndimage.label(G); sizes = ndimage.sum(G, lab, range(1, n + 1)) * cell * cell
    keep_lab = np.zeros(n + 1, bool); keep_lab[1:] = sizes >= args.min_area
    out = np.zeros_like(mask); out[np.flatnonzero(mask)] = keep_lab[lab[iu, iv]]
    return out, float(sizes[sizes >= args.min_area].sum()) if n else 0.0


cosA = np.cos(np.radians(args.angle))
# Planes from splat POSITIONS (on plain walls 3DGS splat orientations are too noisy to use; their centres
# still lie on the surface). Gravity from ARCore gives the vertical; walls are found in a Manhattan frame.
op = OP > 0.5; Y = P[:, 1]
planes = [dict(n=UP.copy(), d=y0, kind="horizontal")
          for y0 in peaks(Y[op], *np.percentile(Y[op], [0.5, 99.5]))]
floor = min(p_["d"] for p_ in planes)
mid = op & (Y > floor + 0.3) & (Y < floor + 2.6); XZ = P[mid][:, [0, 2]]


def sharp(a):                                       # walls give sharp 1D histograms when projected on their normal
    return sum((np.histogram(XZ @ np.array([np.cos(b), np.sin(b)]), bins=1000)[0].astype(float) ** 2).sum()
               for b in (a, a + np.pi / 2))


th = np.radians(np.arange(0, 90, 0.25))[int(np.argmax([sharp(a) for a in np.radians(np.arange(0, 90, 0.25))]))]
fine = th + np.radians(np.arange(-0.5, 0.5, 0.02)); th = fine[int(np.argmax([sharp(a) for a in fine]))]
for k in range(2):
    a = th + k * np.pi / 2; dvec = np.array([np.cos(a), 0.0, np.sin(a)]); off = XZ @ dvec[[0, 2]]
    for d0 in peaks(off, *np.percentile(off, [0.5, 99.5])):
        planes.append(dict(n=dvec, d=d0, kind="wall"))
print(f"wall direction {np.degrees(th):.2f} deg; {len(planes)} plane candidates")

# ---- assignment: nearest admissible plane, within tau, facing it, inside its connected support ----
best = np.full(len(P), -1); bestd = np.full(len(P), np.inf); kept = []
for pi, pl in enumerate(planes):
    n = pl["n"]; dist = P @ n - pl["d"]
    cand = (np.abs(dist) < args.tau) & (OP > 0.05)
    if args.use_normals:
        cand &= (np.abs(Nrm @ n) > cosA) | (smin > 0.35 * smid)       # flat splats must face the plane
    t1 = np.cross(n, UP if pl["kind"] == "wall" else np.array([1.0, 0, 0])); t1 /= np.linalg.norm(t1); t2 = np.cross(n, t1)
    sup, a_ = support(cand, P @ t1, P @ t2) if cand.sum() >= 50 else (np.zeros(len(P), bool), 0.0)
    if a_ < args.min_area:
        continue
    pl.update(area_m2=a_, n_splats=int(sup.sum()))
    # refine offset with the robust centre of its supporting splats
    pl["d"] = float(pl["d"] + np.median(dist[sup])); dist = P @ n - pl["d"]
    better = sup & (np.abs(dist) < bestd)
    best[better] = len(kept); bestd[better] = np.abs(dist[better]); kept.append(pl)
planes = kept
# room shell = floor (lowest horizontal), ceiling (highest, if > 2 m above the floor) and the outermost wall
# on each side of both wall directions. Inner planes (table tops, furniture faces, partitions) slice
# furniture when snapped (chair backs doubled, frames flattened) -> recorded but not snapped by default.
hor = [i for i, p_ in enumerate(planes) if p_["kind"] == "horizontal"]
shell = set()
if hor:
    lo_i = min(hor, key=lambda i: planes[i]["d"]); hi_i = max(hor, key=lambda i: planes[i]["d"]); shell.add(lo_i)
    if planes[hi_i]["d"] > planes[lo_i]["d"] + 2.0:
        shell.add(hi_i)
for dv in {tuple(np.round(p_["n"], 6)) for p_ in planes if p_["kind"] == "wall"}:
    ws = [i for i, p_ in enumerate(planes) if p_["kind"] == "wall" and tuple(np.round(p_["n"], 6)) == dv]
    shell |= {min(ws, key=lambda i: planes[i]["d"]), max(ws, key=lambda i: planes[i]["d"])}
for i, pl in enumerate(planes):
    pl["shell"] = i in shell
    pl["kind"] = {True: "floor" if pl["kind"] == "horizontal" and pl["d"] == planes[min(hor, key=lambda j: planes[j]['d'])]["d"]
                  else ("ceiling" if pl["kind"] == "horizontal" else "wall"), False: pl["kind"] + "_inner"}[i in shell]
if not args.inner_planes:
    best[~np.isin(best, list(shell))] = -1
for i, pl in enumerate(planes):
    pl["n_assigned"] = int((best == i).sum())
print(f"{len(planes)} planes kept ({len(shell)} room shell), {int((best >= 0).sum())} splats snapped "
      f"({100 * (best >= 0).mean():.1f}%)")
for i, pl in enumerate(sorted(planes, key=lambda p: -p["area_m2"])):
    print(f"  {pl['kind']:10s} n=({pl['n'][0]:+.3f},{pl['n'][1]:+.3f},{pl['n'][2]:+.3f}) d={pl['d']:+.3f} m  "
          f"support {pl['area_m2']:6.2f} m2  splats {pl['n_assigned']}")

# room dimensions from parallel wall planes (thesis: compare to tape)
walls = [p for p in planes if p["kind"] in ("wall", "wall_inner")]
dims = []
for i in range(len(walls)):
    for j in range(i + 1, len(walls)):
        if abs(walls[i]["n"] @ walls[j]["n"]) > 0.999:
            dims.append(dict(a=i, b=j, dist_m=abs(walls[i]["d"] - walls[j]["d"] * np.sign(walls[i]["n"] @ walls[j]["n"]))))
json.dump(dict(planes=[{**p, "n": p["n"].tolist()} for p in planes], parallel_wall_distances=dims,
               wall_direction_deg=float(np.degrees(th))), open(os.path.join(args.out, "planes.json"), "w"), indent=1)

# ---- snap ----
idx = np.flatnonzero(best >= 0)
Npl = np.array([planes[b]["n"] for b in best[idx]]).reshape(-1, 3); Dpl = np.array([planes[b]["d"] for b in best[idx]]).reshape(-1)
P2 = P.copy(); P2[idx] -= ((P[idx] * Npl).sum(1) - Dpl)[:, None] * Npl
sgn = np.sign((Nrm[idx] * Npl).sum(1)); sgn[sgn == 0] = 1; nz = Npl * sgn[:, None]
amaj = np.take_along_axis(Rm[idx], order[idx, None, 2:3].repeat(3, 1), 2)[..., 0]
amaj = amaj - (amaj * nz).sum(1, keepdims=True) * nz
bad = np.linalg.norm(amaj, axis=1) < 1e-6                                 # major axis parallel to the normal
if bad.any():
    ref = np.where((np.abs(nz[bad] @ UP) > 0.9)[:, None], np.array([1.0, 0, 0]), UP)
    amaj[bad] = np.cross(nz[bad], ref)
amaj /= np.linalg.norm(amaj, axis=1, keepdims=True); amid = np.cross(nz, amaj)
Rnew = np.stack([amaj, amid, nz], 2)                                       # columns: major, mid, normal
Q2 = Q.copy()
if len(idx):
    qq = Rot.from_matrix(Rnew).as_quat(); Q2[idx] = qq[:, [3, 0, 1, 2]]
logS2 = logS.copy()
logS2[idx, 0] = np.log(smax[idx]); logS2[idx, 1] = np.log(smid[idx]); logS2[idx, 2] = np.log(args.thickness)


def write(path, P_, Q_, logS_, extra=None):
    out = D.copy()
    out["x"], out["y"], out["z"] = P_.T.astype(np.float32)
    for i in range(4):
        out[f"rot_{i}"] = Q_[:, i].astype(np.float32)
    for i in range(3):
        out[f"scale_{i}"] = logS_[:, i].astype(np.float32)
    if extra:
        for k, val in extra.items():
            out[k] = val.astype(np.float32)
    PlyData([PlyElement.describe(out, "vertex")]).write(path)


write(os.path.join(args.out, "splat_snapped.ply"), P2, Q2, logS2)
print("wrote splat_snapped.ply")
if args.refit_steps <= 0:
    raise SystemExit

# ---- re-fit ----
from gsplat import rasterization
from pytorch_msssim import ssim
meta = json.load(open(os.path.join(args.work, "frames.json"))); fr = meta["frames"]
W, H = meta["W"], meta["H"]
K = torch.tensor([[[meta["fx"], 0, meta["cx"]], [0, meta["fy"], meta["cy"]], [0, 0, 1]]], dtype=torch.float32, device=dev)
n_ = len(fr); tr = sorted(set(np.linspace(0, n_ - 1, int(np.ceil(n_ * 0.9)), dtype=int).tolist()))   # nerfstudio split
G = np.diag([1, -1, -1, 1.0])
w2c = torch.tensor(np.stack([np.linalg.inv(np.array(fr[i]["c2w"]) @ G) for i in tr]), dtype=torch.float32, device=dev)
print(f"loading {len(tr)} training images at {W}x{H} ...", flush=True)
imgs = torch.stack([torch.from_numpy(cv2.cvtColor(cv2.imread(os.path.join(args.work, "images", fr[i]["name"] + ".jpg")),
                                                  cv2.COLOR_BGR2RGB)) for i in tr]).pin_memory()
nr = len([k for k in D.dtype.names if k.startswith("f_rest")])
t = lambda a, g=True: torch.tensor(np.asarray(a), dtype=torch.float32, device=dev).requires_grad_(g)
params = dict(means=t(P2), quats=t(Q2), scales=t(logS2), opac=t(D["opacity"]),
              dc=t(np.stack([D[f"f_dc_{i}"] for i in range(3)], 1)),
              rest=t(np.stack([D[f"f_rest_{i}"] for i in range(nr)], 1).reshape(len(P), 3, -1).transpose(0, 2, 1)))
affine = torch.zeros(len(tr), 3, 4, device=dev); affine[:, :, :3] = torch.eye(3); affine.requires_grad_(True)
lr = dict(means=1e-5, quats=5e-4, scales=2e-3, opac=1e-2, dc=1e-3, rest=5e-5)
opt = torch.optim.Adam([{"params": [params[k]], "lr": lr[k]} for k in lr] + [{"params": [affine], "lr": 1e-3}], eps=1e-15)
pidx = torch.tensor(idx, device=dev); pn = torch.tensor(Npl, dtype=torch.float32, device=dev)
pd = torch.tensor(Dpl, dtype=torch.float32, device=dev); qfix = params["quats"].detach()[pidx].clone()
sh = int(round(np.sqrt(1 + params["rest"].shape[1]))) - 1
t0 = time.time()
for step in range(args.refit_steps):
    k = np.random.randint(len(tr))
    gt = imgs[k].to(dev, non_blocking=True).float() / 255
    col = torch.cat([params["dc"][:, None], params["rest"]], 1)
    bg = torch.rand(1, 3, device=dev)
    out, _, _ = rasterization(params["means"], F.normalize(params["quats"], dim=-1), torch.exp(params["scales"]),
                              torch.sigmoid(params["opac"]), col, w2c[k:k + 1], K, W, H, sh_degree=sh, backgrounds=bg)
    r = out[0]
    r = (r.reshape(-1, 3) @ affine[k, :, :3].T + affine[k, :, 3]).reshape(H, W, 3)
    loss = 0.8 * (r - gt).abs().mean() + 0.2 * (1 - ssim(r.permute(2, 0, 1)[None], gt.permute(2, 0, 1)[None], data_range=1.0))
    opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
    with torch.no_grad():                                                   # keep planar splats on their plane
        m = params["means"][pidx]; m -= ((m * pn).sum(1) - pd)[:, None] * pn; params["means"][pidx] = m
        params["quats"][pidx] = qfix; params["scales"][pidx, 2] = float(np.log(args.thickness))
    if step % 250 == 0 or step == args.refit_steps - 1:
        el = time.time() - t0
        print(f"refit {step:5d} loss {loss.item():.4f}  {el:.0f}s, ETA {el / (step + 1) * (args.refit_steps - step - 1):.0f}s", flush=True)
p = {k: v_.detach().cpu().numpy() for k, v_ in params.items()}
extra = {"opacity": p["opac"]}
for i in range(3):
    extra[f"f_dc_{i}"] = p["dc"][:, i]
rest = p["rest"].transpose(0, 2, 1).reshape(len(P), -1)
for i in range(nr):
    extra[f"f_rest_{i}"] = rest[:, i]
write(os.path.join(args.out, "splat.ply"), p["means"], p["quats"], p["scales"], extra)
print("wrote splat.ply (re-fitted)")
