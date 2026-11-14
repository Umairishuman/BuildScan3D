"""SfM-anchored monocular depth + normal priors for geometry-regularised 3DGS (v8geo).

Metric3D (ViT-L) predicts dense depth on every frame, including plain walls where stereo / SfM has no
points; its scale is unreliable (median error ~25% on newRoom), but its SHAPE (planarity, corners) is good.
Each frame's prediction is therefore aligned to the metric SfM points that frame observes with a robust
least-squares fit z_sfm = a * z_mono + b ("SfM-supervised monocular depth", as in Textureless-Splatter).
Normals are computed from the aligned depth (finite differences, OpenCV camera frame), so depth and
normal priors share one convention.

Writes <work>/mono_prior/<name>.npz at 1/4 resolution: depth (float16, m), normal (int8 x127, camera
frame), valid (bool), plus <work>/mono_prior/stats.json (alignment residuals per frame).

  python src/arcore3dgs/mono_prior.py --work <work_sfm>          (system python: Metric3D lives there)
  speed: --model small (ViT-S) and/or --fp16; --out / --limit for benchmarking without touching the priors
"""
import sys, types, os, json, argparse, time
import numpy as np, cv2, torch

mm = types.ModuleType("mmcv"); mu = types.ModuleType("mmcv.utils"); mu.collect_env = lambda: {"OS": "Windows"}
sys.modules["mmcv"] = mm; sys.modules["mmcv.utils"] = mu

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--down", type=int, default=4)
ap.add_argument("--model", choices=["large", "small"], default="large")
ap.add_argument("--fp16", action="store_true", help="autocast the network to half precision")
ap.add_argument("--out", default="mono_prior", help="output folder inside --work")
ap.add_argument("--limit", type=int, default=0, help="only the first N frames (benchmarking)")
args = ap.parse_args()
meta = json.load(open(os.path.join(args.work, "frames.json"))); fr = meta["frames"]
W, H, d = meta["W"], meta["H"], args.down
w, h = W // d, H // d
out_dir = os.path.join(args.work, args.out); os.makedirs(out_dir, exist_ok=True)
sp = np.load(os.path.join(args.work, "sparse.npz")); X, cam, pt, uv = sp["X"], sp["cam"], sp["pt"], sp["uv"]
G = np.diag([1.0, -1.0, -1.0, 1.0])
dev = torch.device("cuda")
model = torch.hub.load("yvanyin/metric3d", f"metric3d_vit_{args.model}", pretrain=True).to(dev).eval()
INPUT = (616, 1064)
MEAN = torch.tensor([123.675, 116.28, 103.53], device=dev).view(1, 3, 1, 1)
STD = torch.tensor([58.395, 57.12, 57.375], device=dev).view(1, 3, 1, 1)


@torch.no_grad()
def metric_depth(bgr):
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB); hh, ww = rgb.shape[:2]
    s = min(INPUT[0] / hh, INPUT[1] / ww)
    rgb = cv2.resize(rgb, (int(ww * s), int(hh * s)), interpolation=cv2.INTER_LINEAR)
    ph, pw = INPUT[0] - rgb.shape[0], INPUT[1] - rgb.shape[1]
    pad = [ph // 2, ph - ph // 2, pw // 2, pw - pw // 2]
    rgb = cv2.copyMakeBorder(rgb, pad[0], pad[1], pad[2], pad[3], cv2.BORDER_CONSTANT, value=[123.675, 116.28, 103.53])
    x = (torch.from_numpy(rgb.transpose(2, 0, 1)).float().to(dev)[None] - MEAN) / STD
    with torch.autocast("cuda", dtype=torch.float16, enabled=args.fp16):
        dd, _, _ = model.inference({"input": x})
    dd = dd.float()
    dd = dd.squeeze()[pad[0]:INPUT[0] - pad[1], pad[2]:INPUT[1] - pad[3]]
    dd = torch.nn.functional.interpolate(dd[None, None], (h, w), mode="bilinear").squeeze()
    return (dd * (meta["fx"] * s / 1000.0)).clamp(0, 50).cpu().numpy()


fx, fy, cx, cy = meta["fx"] / d, meta["fy"] / d, meta["cx"] / d, meta["cy"] / d
uu, vv = np.meshgrid(np.arange(w) + 0.5, np.arange(h) + 0.5)


def normals_from_depth(D):
    P = np.dstack([(uu - cx) / fx * D, (vv - cy) / fy * D, D])          # OpenCV camera frame
    dx = np.zeros_like(P); dy = np.zeros_like(P)
    dx[:, 1:-1] = P[:, 2:] - P[:, :-2]; dy[1:-1] = P[2:] - P[:-2]
    n = np.cross(dx, dy); n /= np.linalg.norm(n, axis=2, keepdims=True) + 1e-9
    flip = (n * P).sum(2) > 0                                          # face the camera
    n[flip] *= -1
    return n


stats = {}; t0 = time.time()
for i, f in enumerate(fr[:args.limit] if args.limit else fr):
    img = cv2.imread(os.path.join(args.work, "images", f["name"] + ".jpg"))
    m = metric_depth(img)
    o = cam == i
    c2w = np.array(f["c2w"]) @ G
    z = ((X[pt[o]] - c2w[:3, 3]) @ c2w[:3, :3])[:, 2]
    px = np.clip((uv[o, 0] / d).astype(int), 0, w - 1); py = np.clip((uv[o, 1] / d).astype(int), 0, h - 1)
    zm = m[py, px]; ok = (z > 0.1) & (zm > 0.1)
    z, zm = z[ok], zm[ok]
    a, b, n_in = 1.0, 0.0, 0
    if len(z) >= 20:
        keep = np.ones(len(z), bool)
        for _ in range(4):                                              # robust LSQ: trim outliers
            A = np.stack([zm[keep], np.ones(keep.sum())], 1)
            a, b = np.linalg.lstsq(A, z[keep], rcond=None)[0]
            r = np.abs(a * zm + b - z) / z
            keep = r < max(0.03, 3 * np.median(r[keep]))
        n_in = int(keep.sum())
        if a <= 0.2 or a > 5:                                           # degenerate fit -> scale only
            a, b = float(np.median(z / zm)), 0.0
    elif len(z) >= 5:
        a = float(np.median(z / zm))
    D = a * m + b
    rel = np.abs(D[py[ok], px[ok]] - z) / z if len(z) else np.array([1.0])
    valid = (D > 0.15) & (D < 15) & (len(z) >= 5)
    Dn = cv2.medianBlur(D.astype(np.float32), 5)
    n = normals_from_depth(Dn)
    np.savez_compressed(os.path.join(out_dir, f["name"] + ".npz"), depth=D.astype(np.float16),
                        normal=np.clip(n * 127, -127, 127).astype(np.int8), valid=valid)
    stats[f["name"]] = dict(scale=float(a), shift=float(b), n_sfm=int(len(z)), inliers=n_in,
                            median_rel_err=float(np.median(rel)), raw_median_rel_err=float(np.median(np.abs(zm - z) / z)) if len(z) else None)
    if i % 100 == 0:
        print(f"{i}/{len(fr)}  aligned median err {100 * np.median(rel):.1f}% (raw Metric3D "
              f"{100 * stats[f['name']]['raw_median_rel_err'] if len(z) else -1:.1f}%), scale {a:.3f}", flush=True)
json.dump(stats, open(os.path.join(out_dir, "stats.json"), "w"), indent=1)
e = np.array([s["median_rel_err"] for s in stats.values()]); r = np.array([s["raw_median_rel_err"] for s in stats.values() if s["raw_median_rel_err"] is not None])
print(f"done: {len(stats)} frames in {time.time() - t0:.0f} s, aligned median error {100 * np.median(e):.1f}% (raw Metric3D {100 * np.median(r):.1f}%)")
