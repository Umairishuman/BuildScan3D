"""Off-path evaluation for models trained on the same SfM solution with transforms_offpath.json
(6 contiguous 3 s stretches of the walk held out, so test views are away from / rotated relative to the
training cameras -- where far walls and corners break).

Metrics on the held-out frames (half res): colour-fit PSNR, SSIM, render sharpness / photo sharpness, and
(if plane_seg.py has run) flatness: median rms (cm) of the rendered surface around its best-fit plane inside
each planar region (walls, floor, ceiling, doors) -- "walls are not flat from off-path views".
Sheets: one held-out frame per stretch (photo | models), full-res centre crops, room-centre views (never
visited by the camera) in 4 directions.

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/eval_offpath.py --work <work_sharp_sfm> --out <dir>
      --models v6=<ply> v8a=<ply> ... [--times v6=58.2 v8a=31.0]
"""
import os, json, argparse
import numpy as np, cv2, torch, torch.nn.functional as F
from plyfile import PlyData
from gsplat import rasterization
from pytorch_msssim import ssim

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--models", nargs="+", required=True)
ap.add_argument("--times", nargs="*", default=[], help="name=minutes (training time) for the table")
args = ap.parse_args()
dev = "cuda"; os.makedirs(args.out, exist_ok=True); G = np.diag([1, -1, -1, 1.0])
meta = json.load(open(os.path.join(args.work, "frames.json"))); by = {f["name"]: f for f in meta["frames"]}
test = open(os.path.join(args.work, "offpath_test.txt")).read().split()
W, H = meta["W"], meta["H"]
Kh = torch.tensor([[[meta["fx"] / 2, 0, meta["cx"] / 2], [0, meta["fy"] / 2, meta["cy"] / 2], [0, 0, 1]]], dtype=torch.float32, device=dev)
Kf = torch.tensor([[[meta["fx"], 0, meta["cx"]], [0, meta["fy"], meta["cy"]], [0, 0, 1]]], dtype=torch.float32, device=dev)
times = dict(t.split("=") for t in args.times)


def load(path):
    v = PlyData.read(path)["vertex"]; c = lambda n: torch.tensor(np.asarray(v[n]), dtype=torch.float32, device=dev)
    m = torch.stack([c("x"), c("y"), c("z")], 1); nr = len([n for n in v.data.dtype.names if n.startswith("f_rest")])
    col = torch.stack([c(f"f_dc_{i}") for i in range(3)], 1)[:, None]
    if nr:
        col = torch.cat([col, torch.stack([c(f"f_rest_{i}") for i in range(nr)], 1).reshape(len(m), 3, -1).transpose(1, 2)], 1)
    return dict(means=m, quats=F.normalize(torch.stack([c(f"rot_{i}") for i in range(4)], 1), dim=-1),
                scales=torch.exp(torch.stack([c(f"scale_{i}") for i in range(3)], 1)), opac=torch.sigmoid(c("opacity")),
                col=col, sh=int(round(np.sqrt(col.shape[1]))) - 1, n=len(m))


@torch.no_grad()
def render(g, c2w, full=False, depth=False):
    w2c = torch.tensor(np.linalg.inv(np.array(c2w) @ G), dtype=torch.float32, device=dev)[None]
    w, h = (W, H) if full else (W // 2, H // 2)
    out, alpha, _ = rasterization(g["means"], g["quats"], g["scales"], g["opac"], g["col"], w2c, Kf if full else Kh, w, h,
                                  sh_degree=g["sh"], render_mode="RGB+ED" if depth else "RGB")
    if depth:
        return out[0, ..., :3].clamp(0, 1), out[0, ..., 3], alpha[0, ..., 0]
    return out[0].clamp(0, 1)


vv_, uu_ = torch.meshgrid(torch.arange(H // 2, device=dev) + 0.5, torch.arange(W // 2, device=dev) + 0.5, indexing="ij")
RAYS = torch.stack([(uu_ - Kh[0, 0, 2]) / Kh[0, 0, 0], (vv_ - Kh[0, 1, 2]) / Kh[0, 1, 1], torch.ones_like(uu_)], -1)


def flatness(n, D, A):
    """rms (m) of the rendered surface around its best-fit plane, per planar region of frame n"""
    p = os.path.join(args.work, "planes", n + ".png")
    if not os.path.exists(p):
        return []
    L = torch.from_numpy(cv2.resize(cv2.imread(p, cv2.IMREAD_UNCHANGED), (W // 2, H // 2), interpolation=cv2.INTER_NEAREST)).to(dev)
    P = RAYS * D[..., None]; out = []
    for k in range(1, int(L.max()) + 1):
        m = (L == k) & (A > 0.9)
        if m.sum() < 300:
            continue
        Q = P[m]; Q = Q - Q.mean(0)
        out.append(float(torch.linalg.svdvals(Q)[2] / np.sqrt(len(Q))))
    return out


def photo(n, full=False):
    im = cv2.imread(os.path.join(args.work, "images", n + ".jpg"))
    if not full:
        im = cv2.resize(im, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    return torch.from_numpy(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).to(dev).float() / 255


def lap(x):
    return cv2.Laplacian(cv2.cvtColor((x * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY), cv2.CV_64F).var()


models = []
for spec in args.models:
    name, path = spec.split("=", 1)
    models.append((name, load(path)))
res = {}
print(f"{len(test)} off-path test frames")
print(f"{'model':16s} {'splats':>8s} {'PSNR(cf)':>9s} {'SSIM':>7s} {'sharp':>6s} {'flat cm':>7s} {'train min':>9s}")
for name, g in models:
    ps, ss, sh, fl = [], [], [], []
    for n in test:
        gt = photo(n); r, Dr, Ar = render(g, by[n]["c2w"], depth=True)
        fl += flatness(n, Dr, Ar)
        A = torch.cat([r.reshape(-1, 3), torch.ones(r.shape[0] * r.shape[1], 1, device=dev)], 1)
        ra = (A @ torch.linalg.lstsq(A, gt.reshape(-1, 3)).solution).reshape(gt.shape).clamp(0, 1)
        ps.append(float(-10 * torch.log10(((ra - gt) ** 2).mean())))
        ss.append(float(ssim(ra.permute(2, 0, 1)[None], gt.permute(2, 0, 1)[None], data_range=1.0)))
        sh.append(lap(r.cpu().numpy()) / max(lap(gt.cpu().numpy()), 1e-6))
    flat = 100 * float(np.median(fl)) if fl else float("nan")
    res[name] = dict(splats=g["n"], psnr_cf=float(np.mean(ps)), ssim=float(np.mean(ss)), sharpness=float(np.mean(sh)),
                     flat_cm=flat, train_min=float(times[name]) if name in times else None)
    print(f"{name:16s} {g['n']:8d} {np.mean(ps):9.2f} {np.mean(ss):7.4f} {np.mean(sh):6.2f} {flat:7.2f} {times.get(name, '-'):>9s}", flush=True)
json.dump(res, open(os.path.join(args.out, "metrics.json"), "w"), indent=1)


def lab(img, t, rot=True):
    img = np.ascontiguousarray(cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) if rot else img)
    cv2.putText(img, t, (8, 30), 0, 0.9, (0, 0, 0), 5); cv2.putText(img, t, (8, 30), 0, 0.9, (0, 255, 255), 2)
    return img


bgr = lambda x: (x.cpu().numpy()[..., ::-1] * 255).astype(np.uint8)
# one frame per held-out stretch (the middle one = farthest from training)
pts = np.array([by[n]["pts"] for n in test]); order = np.argsort(pts); stretches = np.split(order, np.flatnonzero(np.diff(pts[order]) > 2) + 1)
pick = [test[s[len(s) // 2]] for s in stretches]
rows = [np.hstack([lab(bgr(photo(n)), "photo")] + [lab(bgr(render(g, by[n]["c2w"])), nm) for nm, g in models]) for n in pick]
cv2.imwrite(os.path.join(args.out, "offpath_frames.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])
rows = []
for n in pick[:4]:
    cy, cx, s_ = H // 2, W // 2, 240
    tiles = [bgr(photo(n, True))[cy - s_:cy + s_, cx - s_:cx + s_]] + [bgr(render(g, by[n]["c2w"], True))[cy - s_:cy + s_, cx - s_:cx + s_] for _, g in models]
    rows.append(np.hstack([lab(t, l) for t, l in zip(tiles, ["photo"] + [nm for nm, _ in models])]))
cv2.imwrite(os.path.join(args.out, "crops.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 90])
UP = np.array([0.0, 1, 0]); c = np.array([np.array(f["c2w"])[:3, 3] for f in meta["frames"]]).mean(0)


def look(pos, tgt):
    fw = tgt - pos; fw /= np.linalg.norm(fw); r = np.cross(fw, UP); r /= np.linalg.norm(r); u = np.cross(r, fw)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = r, u, -fw, pos
    return m @ np.array([[0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1.0]])


rows = []
for k, a in enumerate(np.radians([0, 90, 180, 270])):
    c2w = look(c, c + np.array([np.cos(a), -0.35, np.sin(a)]))
    rows.append(np.hstack([lab(bgr(render(g, c2w)), f"{nm} centre {k * 90}") for nm, g in models]))
cv2.imwrite(os.path.join(args.out, "centre.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])
print("sheets ->", args.out)
