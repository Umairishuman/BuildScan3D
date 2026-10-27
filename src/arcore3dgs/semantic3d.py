"""Semantic labelling of the metric 3DGS model: structure (walls, floor, ceiling) + building fixtures.

Inputs: the model (splat.ply), its work dir (frames.json, images), the per-frame 2D fixture masks from
semantic2d.py and the room layout from layout.py (walls, floor, ceiling planes).
  1. 2D -> 3D votes: for every frame with 2D masks, render the model's depth; a Gaussian whose centre lies on
     the visible surface of that frame (|z - rendered depth| small) takes one vote for the class under it
     (or a "seen, nothing there" vote). A Gaussian becomes a fixture if that class wins >= --min_frac of
     the frames that saw it, in at least --min_votes frames.
  2. structure: Gaussians within --band of the floor / ceiling / a wall plane of the layout (and inside the
     wall's extent) are floor / ceiling / wall_k; fixtures take precedence; the rest is "other" (furniture).
  3. fixtures -> instances (connected components on a 4 cm voxel grid), each checked against the class's
     geometry (doors reach the floor and are tall, switches / sockets are small and on a wall, ceiling lights
     and fans hang from the ceiling, ...) and needing >= --min_views supporting frames. Rejections are kept,
     with the reason, in semantic.json.
  4. outputs: semantic.json (fixtures with position, wall, height above floor, distance along the wall, size;
     walls with gross / opening / net area; floor area; ceiling height), labels.npy (per-Gaussian class id),
     semantic.ply (the model coloured by class), plan_semantic.png, views_semantic.jpg.

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/semantic3d.py --ply <splat.ply> --work <work_sfm>
      --layout <layout.json> --out <dir>
"""
import os, json, argparse, time
import numpy as np, cv2, torch, torch.nn.functional as F
from plyfile import PlyData, PlyElement
from scipy import ndimage
from gsplat import rasterization

ap = argparse.ArgumentParser()
ap.add_argument("--ply", required=True); ap.add_argument("--work", required=True)
ap.add_argument("--layout", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--band", type=float, default=0.06, help="m: distance to a structural plane counted as on it")
ap.add_argument("--min_votes", type=int, default=2); ap.add_argument("--min_frac", type=float, default=0.3)
ap.add_argument("--min_views", type=int, default=6); ap.add_argument("--voxel", type=float, default=0.04)
ap.add_argument("--min_gaussians", type=int, default=30)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
dev = "cuda"; G = np.diag([1, -1, -1, 1.0]); t0 = time.time()
det = json.load(open(os.path.join(args.work, "semantic2d", "detections.json")))
FIX = det["classes"]                                         # 2D label i -> FIX[i-1] (fixtures + decoys)
DECOY = set(det.get("decoys", []))                           # e.g. picture frame: absorbs false "windows", never a fixture
lay = json.load(open(args.layout))

# ---------------- model ----------------
v = PlyData.read(args.ply)["vertex"]; Dv = v.data
c = lambda n: torch.tensor(np.asarray(Dv[n]), dtype=torch.float32, device=dev)
means = torch.stack([c("x"), c("y"), c("z")], 1); N = len(means)
quats = F.normalize(torch.stack([c(f"rot_{i}") for i in range(4)], 1), dim=-1)
scales = torch.exp(torch.stack([c(f"scale_{i}") for i in range(3)], 1)); opac = torch.sigmoid(c("opacity"))
dc = torch.stack([c(f"f_dc_{i}") for i in range(3)], 1)
meta = json.load(open(os.path.join(args.work, "frames.json")))
W2, H2 = meta["W"] // 2, meta["H"] // 2
K = torch.tensor([[meta["fx"] / 2, 0, meta["cx"] / 2], [0, meta["fy"] / 2, meta["cy"] / 2], [0, 0, 1]], device=dev)

# ---------------- 1. 2D -> 3D votes ----------------
C1 = len(FIX) + 1
votes = torch.zeros(N, C1, dtype=torch.int32, device=dev)   # column 0 = seen, no fixture
frames_of = {}                                               # (class) -> list of (frame idx, gaussian idx tensor)
by = {f["name"]: f for f in meta["frames"]}
names = sorted(n for n in det["frames"] if os.path.exists(os.path.join(args.work, "semantic2d", n + ".npz")))
seen_frames = torch.zeros(N, dtype=torch.int32, device=dev)
fix_frame_votes = []                                         # (frame index, gaussian ids, class) for view counting
for fi, n in enumerate(names):
    z = np.load(os.path.join(args.work, "semantic2d", n + ".npz"))
    cls = torch.from_numpy(z["cls"].astype(np.int64)).to(dev)
    c2w = np.array(by[n]["c2w"]) @ G; w2c = torch.tensor(np.linalg.inv(c2w), dtype=torch.float32, device=dev)
    with torch.no_grad():
        out, alpha, _ = rasterization(means, quats, scales, opac, torch.sigmoid(dc), w2c[None], K[None], W2, H2,
                                      render_mode="RGB+ED")
    D = out[0, ..., 3]; A = alpha[0, ..., 0]
    pc = means @ w2c[:3, :3].T + w2c[:3, 3]
    zc = pc[:, 2]; u = (K[0, 0] * pc[:, 0] / zc + K[0, 2]).long(); vv = (K[1, 1] * pc[:, 1] / zc + K[1, 2]).long()
    ok = (zc > 0.1) & (u >= 0) & (u < W2) & (vv >= 0) & (vv < H2)
    idx = torch.nonzero(ok).squeeze(1)
    du = D[vv[idx], u[idx]]
    vis = (torch.abs(zc[idx] - du) < torch.clamp(0.02 * du, min=0.03)) & (A[vv[idx], u[idx]] > 0.5)
    idx = idx[vis]
    lab = cls[vv[idx], u[idx]]
    votes.index_put_((idx, lab), torch.ones_like(idx, dtype=torch.int32), accumulate=True)
    seen_frames[idx] += 1
    m = lab > 0
    if m.any():
        fix_frame_votes.append((fi, idx[m].cpu().numpy(), lab[m].cpu().numpy()))
    if fi % 100 == 0:
        print(f"{fi}/{len(names)} {n}: {int(vis.sum())} visible Gaussians, {int(m.sum())} on fixtures", flush=True)
votes = votes.cpu().numpy(); seen = seen_frames.cpu().numpy()
fc = votes[:, 1:].argmax(1) + 1; fv = votes[np.arange(N), fc]
is_decoy = np.array([FIX[c - 1] in DECOY for c in range(1, C1)])[fc - 1]
is_fix = (fv >= args.min_votes) & (fv >= args.min_frac * np.maximum(seen, 1)) & ~is_decoy

# ---------------- 2. structure from the layout ----------------
P = means.cpu().numpy(); o = opac.cpu().numpy()
fy, cy_ = lay["floor_y"], lay["ceiling_y"]; has_ceil = np.isfinite(cy_)
walls = lay["walls"]


def fit_level(y0, win):
    """robust plane y = a x + b z + c through the opaque Gaussians within +-win of height y0 (a slightly
    tilted floor / ceiling falls out of a flat band over a 7 m room)"""
    Q = P[(np.abs(P[:, 1] - y0) < win) & (o > 0.3)]
    A = np.c_[Q[:, 0], Q[:, 2], np.ones(len(Q))]; keep = np.ones(len(Q), bool)
    for _ in range(6):
        coef = np.linalg.lstsq(A[keep], Q[keep, 1], rcond=None)[0]; r = Q[:, 1] - A @ coef
        keep = np.abs(r) < max(0.015, 2.5 * np.median(np.abs(r[keep])))
    return coef, float(np.degrees(np.arctan(np.hypot(coef[0], coef[1])))), float(np.median(np.abs(r[keep])))


level = lambda coef, Q: Q[:, 1] - (coef[0] * Q[:, 0] + coef[1] * Q[:, 2] + coef[2])
fcoef, ftilt, fres = fit_level(fy, 0.15)
print(f"floor plane: tilt {ftilt:.2f} deg, median residual {fres * 100:.1f} cm")
if has_ceil:
    ccoef, ctilt, cres = fit_level(cy_, 0.10)
    if cres > 0.03 or ctilt > 3:                              # too few / too scattered ceiling Gaussians: keep it level
        print(f"ceiling fit rejected (tilt {ctilt:.2f} deg, residual {cres * 100:.1f} cm): level at the layout height")
        ccoef, ctilt, cres = np.array([0.0, 0.0, cy_]), 0.0, float("nan")
    print(f"ceiling plane: tilt {ctilt:.2f} deg, median residual {cres * 100:.1f} cm")
STRUCT = ["other", "floor", "ceiling"] + [f"wall_{k}" for k in range(len(walls))]
label = np.zeros(N, np.int32)                                 # index into STRUCT first, fixtures appended below
dist_struct = np.full(N, np.inf)
dfl = np.abs(level(fcoef, P)); label[dfl < args.band] = 1; dist_struct = np.where(dfl < args.band, dfl, dist_struct)
if has_ceil:
    # ceiling Gaussians scatter more (seen only from below, plain): a wider band; nothing else structural is there
    dce = np.abs(level(ccoef, P)); m = (dce < 2.5 * args.band) & (dce < dist_struct); label[m] = 2; dist_struct[m] = dce[m]
for k, w in enumerate(walls):
    p0, p1 = np.array(w["p0"]), np.array(w["p1"]); d = (p1 - p0) / np.linalg.norm(p1 - p0); nrm = np.array([-d[1], d[0]])
    rel = P[:, [0, 2]] - p0; t = rel @ d; s = np.abs(rel @ nrm)
    m = (s < args.band) & (t > -0.1) & (t < w["length"] + 0.1) & (P[:, 1] > fy - args.band) & \
        ((P[:, 1] < cy_ + args.band) if has_ceil else True) & (s < dist_struct)
    label[m] = 3 + k; dist_struct[m] = s[m]
NAMES = STRUCT + FIX
fix_label = len(STRUCT) + fc - 1
label_struct = label.copy()                                   # what a rejected fixture falls back to
label = np.where(is_fix, fix_label, label)


# ---------------- 3. fixtures -> instances, verified by geometry ----------------
def wall_of(xz):
    """nearest wall whose extent covers xz: (index, |distance|, distance along it, signed distance, + = into the room)"""
    best = (None, np.inf, 0.0, np.inf)
    for k, w in enumerate(walls):
        p0, p1 = np.array(w["p0"]), np.array(w["p1"]); d = (p1 - p0) / np.linalg.norm(p1 - p0)
        nrm = np.array(w["normal"]) / np.linalg.norm(w["normal"])          # layout.py: points into the room
        t = (xz - p0) @ d; sd = float((xz - p0) @ nrm)
        if -0.2 < t < w["length"] + 0.2 and abs(sd) < best[1]:
            best = (k, abs(sd), float(t), sd)
    return best


ctr0 = P[o > 0.5][:, [0, 2]].mean(0)
H_room = (float(ccoef @ [ctr0[0], ctr0[1], 1]) - float(fcoef @ [ctr0[0], ctr0[1], 1])) if has_ceil else 2.7
RULES = {   # (check, reason) on: h0/h1 = bottom/top above the floor, w = width, wd = distance to the nearest wall
    # a room door / window sits IN the wall: from the wall face to ~a brick wall's depth behind it
    # (sd -0.35..+0.15 m); a wardrobe front stands ~0.5 m in front of the wall
    "door": lambda q: (q["h1"] - q["h0"] >= 1.6 and q["h0"] < 0.3 and 0.45 < q["w"] < 2.0 and -0.35 < q["sd"] < 0.15,
                       "door: tall, from the floor, 0.45-2 m wide, in a wall"),
    "window": lambda q: (q["h0"] > 0.5 and 0.3 < q["h1"] - q["h0"] < 2.5 and 0.3 < q["w"] and -0.35 < q["sd"] < 0.15,
                         "window: in a wall, sill >= 0.5 m, >= 0.3 m wide"),
    "light switch": lambda q: (q["size"] < 0.4 and q["wd"] < 0.12 and 0.6 < q["hc"] < 1.9, "switch: small, on a wall, 0.6-1.9 m"),
    "power socket": lambda q: (q["size"] < 0.4 and q["wd"] < 0.12 and 0.05 < q["hc"] < 1.9, "socket: small, on a wall"),
    "ceiling light": lambda q: (q["h1"] > H_room - 0.6 and q["h0"] > 1.5 and 0.08 < q["size"] < 1.5 and q["h1"] < H_room + 0.1,
                                "ceiling light: 8 cm - 1.5 m, at the ceiling"),
    "lamp": lambda q: (q["size"] < 1.8, "lamp: < 1.8 m"),
    "air conditioner": lambda q: (q["wd"] < 0.4 and q["h0"] > 1.4 and 0.4 < q["w"] < 1.6, "AC: high on a wall"),
    "ceiling fan": lambda q: (H_room - 0.9 < q["h1"] < H_room + 0.1 and 0.6 < q["w"] < 1.8 and q["wd"] > 0.4,
                              "fan: 0.6-1.8 m wide, under the ceiling, away from walls"),
}
fixtures, rejected = [], []
accepted = np.zeros(N, bool)
gid_frames = {}                                               # gaussian -> set of frames where it was labelled
for fi, ids, labs in fix_frame_votes:
    for g, l in zip(ids, labs):
        gid_frames.setdefault((int(g), int(l)), set()).add(fi)
for ci, cname in enumerate(FIX):
    if cname in DECOY:
        continue
    sel = np.nonzero(is_fix & (fc == ci + 1))[0]
    if len(sel) == 0:
        continue
    q0 = np.floor(P[sel] / args.voxel).astype(np.int64); lo = q0.min(0); q0 -= lo
    grid = np.zeros(q0.max(0) + 1, bool); grid[tuple(q0.T)] = True
    lab_cc, ncc = ndimage.label(grid, structure=np.ones((3, 3, 3)))
    comp = lab_cc[tuple(q0.T)]
    for k in range(1, ncc + 1):
        g = sel[comp == k]
        if len(g) < args.min_gaussians:
            continue
        Q = P[g]; lo_, hi_ = np.percentile(Q, 3, 0), np.percentile(Q, 97, 0)
        cen = (lo_ + hi_) / 2
        wk, wd, along, sd = wall_of(cen[[0, 2]])
        if wk is not None:                                    # width along the wall it is on
            p0, p1 = np.array(walls[wk]["p0"]), np.array(walls[wk]["p1"]); d = (p1 - p0) / np.linalg.norm(p1 - p0)
            tt = (Q[:, [0, 2]] - p0) @ d; width = float(np.percentile(tt, 97) - np.percentile(tt, 3))
        else:
            width = float(np.linalg.norm(hi_[[0, 2]] - lo_[[0, 2]]))
        views = set()
        for gg in g:
            views |= gid_frames.get((int(gg), ci + 1), set())
        fl_ = float(fcoef @ [cen[0], cen[2], 1])              # floor height under the object
        q = dict(h0=float(lo_[1] - fl_), h1=float(hi_[1] - fl_), hc=float(cen[1] - fl_), w=width,
                 size=float(np.max(hi_ - lo_)), wd=float(wd), sd=float(sd))
        ok, rule = RULES.get(cname, lambda q: (True, ""))(q)
        rec = dict(cls=cname, position=[round(float(x), 3) for x in cen], height_above_floor=round(q["hc"], 3),
                   bottom=round(q["h0"], 3), top=round(q["h1"], 3), width=round(width, 3),
                   height=round(q["h1"] - q["h0"], 3), wall=wk, dist_to_wall=round(float(wd), 3) if np.isfinite(wd) else None,
                   into_room=round(float(sd), 3) if np.isfinite(sd) else None,
                   along_wall=round(along, 3) if wk is not None else None, views=len(views), gaussians=int(len(g)))
        if ok and len(views) >= args.min_views:
            rec["id"] = f"{cname.replace(' ', '_')}_{sum(f['cls'] == cname for f in fixtures) + 1}"
            fixtures.append(rec); accepted[g] = True
        else:
            rec["rejected"] = rule if not ok else f"seen in {len(views)} < {args.min_views} frames"
            rejected.append(rec)
# fixture votes that did not end up in an accepted instance fall back to their structural label
label = np.where(is_fix & ~accepted, label_struct, label)
print(f"{len(fixtures)} fixtures accepted, {len(rejected)} rejected")

# ---------------- areas ----------------
def poly_area(pts):
    x, y = np.array(pts).T; return float(0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))))


ctr = np.array([np.array(f["c2w"])[:3, 3] for f in meta["frames"]])[:, [0, 2]].mean(0)
crn = sorted([cn["xz"] for cn in lay.get("corners", [])], key=lambda p: np.arctan2(p[1] - ctr[1], p[0] - ctr[0]))
wall_rep = []
for k, w in enumerate(walls):
    gross = w["length"] * H_room
    op = [f for f in fixtures if f["wall"] == k and f["cls"] in ("door", "window") and f["into_room"] is not None
          and -0.35 < f["into_room"] < 0.15]
    op_area = sum(f["width"] * f["height"] for f in op)
    wall_rep.append(dict(id=k, length=round(w["length"], 3), height=round(H_room, 3), gross_area=round(gross, 2),
                         openings=[f["id"] for f in op], openings_area=round(op_area, 2), net_area=round(gross - op_area, 2),
                         fixtures=[f["id"] for f in fixtures if f["wall"] == k and f["cls"] not in ("door", "window")
                                   and f["dist_to_wall"] is not None and f["dist_to_wall"] < 0.3]))
counts = {nm: int((label == i).sum()) for i, nm in enumerate(NAMES)}
res = dict(model=os.path.abspath(args.ply), classes=NAMES, decoys=sorted(DECOY), gaussian_counts=counts,
           floor_tilt_deg=round(ftilt, 2), ceiling_tilt_deg=round(ctilt, 2) if has_ceil else None,
           floor_area=round(poly_area(crn), 2) if len(crn) >= 3 else None, ceiling_height=round(H_room, 3) if has_ceil else None,
           walls=wall_rep, free_standing=[f["id"] for f in fixtures if f["cls"] not in ("door", "window")
                                          and (f["dist_to_wall"] is None or f["dist_to_wall"] >= 0.3)],
           fixtures=fixtures, rejected=rejected, params=vars(args))
json.dump(res, open(os.path.join(args.out, "semantic.json"), "w"), indent=1)
np.save(os.path.join(args.out, "labels.npy"), label.astype(np.int16))
print(f"floor {res['floor_area']} m2, ceiling {res['ceiling_height']} m; Gaussians per class: " +
      ", ".join(f"{k} {v}" for k, v in counts.items() if v))
for f_ in fixtures:
    print(f"  {f_['id']:18s} wall {f_['wall']} ({f_['dist_to_wall']} m off it)  {f_['height_above_floor']:.2f} m above floor, "
          f"{f_['width']:.2f} x {f_['height']:.2f} m, {f_['views']} views")

# ---------------- coloured model + sheets ----------------
PAL = {"other": (150, 150, 150), "floor": (140, 90, 50), "ceiling": (235, 235, 235), "door": (40, 90, 255),
       "window": (0, 200, 255), "light switch": (255, 0, 200), "power socket": (255, 120, 0), "ceiling light": (255, 255, 0),
       "lamp": (255, 220, 120), "air conditioner": (0, 220, 120), "ceiling fan": (160, 80, 255)}
WALLC = [(120, 200, 120), (120, 160, 220), (220, 170, 120), (190, 120, 200), (120, 210, 210), (210, 210, 120)]
col = np.array([PAL.get(nm, WALLC[int(nm.split("_")[1]) % len(WALLC)] if nm.startswith("wall_") else (150, 150, 150))
                for nm in NAMES], np.float32) / 255
rgb = col[label]
SH0 = 0.28209479177387814
new = Dv.copy()
for i in range(3):
    new[f"f_dc_{i}"] = ((rgb[:, i] - 0.5) / SH0).astype(np.float32)
for nm in Dv.dtype.names:
    if nm.startswith("f_rest"):
        new[nm] = 0
PlyData([PlyElement.describe(new, "vertex")]).write(os.path.join(args.out, "semantic.ply"))
# views: real render | class render with fixture labels, from a spread of training frames
colt = torch.tensor(rgb, device=dev)
tiles = []
pick = names[:: max(1, len(names) // 8)][:8]
for n in pick:
    c2w = np.array(by[n]["c2w"]) @ G; w2c = torch.tensor(np.linalg.inv(c2w), dtype=torch.float32, device=dev)
    with torch.no_grad():
        a, _, _ = rasterization(means, quats, scales, opac, torch.clamp(dc * SH0 + 0.5, 0, 1), w2c[None], K[None], W2, H2)
        b, _, _ = rasterization(means, quats, scales, opac, colt, w2c[None], K[None], W2, H2)
    A_ = (a[0].clamp(0, 1).cpu().numpy()[..., ::-1] * 255).astype(np.uint8).copy()
    B_ = (b[0].clamp(0, 1).cpu().numpy()[..., ::-1] * 255).astype(np.uint8).copy()
    k_ = det["frames"][n]["rot"]
    rot = [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE][k_]
    if rot is not None:
        A_, B_ = np.ascontiguousarray(cv2.rotate(A_, rot)), np.ascontiguousarray(cv2.rotate(B_, rot))
    for f_ in fixtures:
        X = np.linalg.inv(c2w) @ np.array(f_["position"] + [1.0])
        if X[2] > 0.2:
            u_, v_ = K[0, 0].item() * X[0] / X[2] + K[0, 2].item(), K[1, 1].item() * X[1] / X[2] + K[1, 2].item()
            if 0 <= u_ < W2 and 0 <= v_ < H2:
                for _ in range(k_):                           # follow the 90 deg clockwise turns: (x, y) -> (h - 1 - y, x)
                    u_, v_ = (H2 if _ % 2 == 0 else W2) - 1 - v_, u_
                p_ = (int(u_), int(v_))
                cv2.circle(B_, p_, 6, (0, 0, 0), -1)
                cv2.putText(B_, f_["id"], (p_[0] + 8, p_[1] + 5), 0, 0.55, (0, 0, 0), 4)
                cv2.putText(B_, f_["id"], (p_[0] + 8, p_[1] + 5), 0, 0.55, (255, 255, 255), 1)
    tiles.append(np.hstack([A_, B_]))
h_ = max(t.shape[0] for t in tiles)
tiles = [cv2.copyMakeBorder(t, 0, h_ - t.shape[0], 0, 0, cv2.BORDER_CONSTANT) for t in tiles]
rows = [np.hstack(tiles[i:i + 4]) for i in range(0, len(tiles) - 3, 4)]
wmax = max(r.shape[1] for r in rows)
rows = [cv2.copyMakeBorder(r, 0, 0, 0, wmax - r.shape[1], cv2.BORDER_CONSTANT) for r in rows]
cv2.imwrite(os.path.join(args.out, "views_semantic.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])
# plan with fixtures
m = (o > 0.5) & (P[:, 1] > fy + 0.1) & (P[:, 1] < (cy_ if has_ceil else fy + 2.4) - 0.1)
xz = P[m][:, [0, 2]]; lo = np.percentile(xz, 0.5, 0) - 0.5; hi = np.percentile(xz, 99.5, 0) + 0.5
sc = 150; Wp, Hp = ((hi - lo) * sc).astype(int)
img = np.full((Hp, Wp, 3), 255, np.uint8)
qq = ((xz - lo) * sc).astype(int); qq = qq[(qq[:, 0] >= 0) & (qq[:, 0] < Wp) & (qq[:, 1] >= 0) & (qq[:, 1] < Hp)]
img[qq[:, 1], qq[:, 0]] = 200
pt_ = lambda p: tuple(int(x) for x in ((np.array(p) - lo) * sc))
for k, w in enumerate(walls):
    cv2.line(img, pt_(w["p0"]), pt_(w["p1"]), (40, 160, 40), 3)
    mid = (np.array(w["p0"]) + np.array(w["p1"])) / 2
    cv2.putText(img, f"wall {k}: {w['length']:.2f} m", pt_(mid), 0, 0.55, (0, 90, 0), 2)
for f_ in fixtures:
    p = pt_([f_["position"][0], f_["position"][2]]); cc = tuple(int(x) for x in PAL.get(f_["cls"], (0, 0, 0))[::-1])
    cv2.circle(img, p, 8, cc, -1); cv2.circle(img, p, 8, (0, 0, 0), 1)
    cv2.putText(img, f"{f_['id']} h{f_['height_above_floor']:.2f}", (p[0] + 10, p[1] + 4), 0, 0.45, (0, 0, 0), 1)
cv2.putText(img, f"floor {res['floor_area']} m2, ceiling {res['ceiling_height']} m, {len(fixtures)} fixtures", (10, 25), 0, 0.7, (0, 0, 0), 2)
cv2.imwrite(os.path.join(args.out, "plan_semantic.png"), img)
print(f"done in {time.time() - t0:.0f} s -> {args.out}")
