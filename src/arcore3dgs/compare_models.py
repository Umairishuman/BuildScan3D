"""Side-by-side comparison of trained splat models: photometric + geometric metrics and image sheets.

Metrics on the held-out frames (every 10th of frames.json, as train.py --test_every 10):
  PSNR after a per-image colour-affine fit, SSIM, sharpness ratio (Laplacian variance render / photo),
  geometry = rendered depth vs BA points seen in >= 5 views (median rel. error, share > 10% / > 25% off).
Image sheets (rotated upright):
  heldout.jpg  - photo | model renders, for 4 held-out frames spread over the recording
  offpath.jpg  - views from the room centre (never visited by the camera) in 4 directions
  depth.jpg    - rendered depth (turbo, 0.3-8 m) for the same held-out frames

  python src/arcore3dgs/compare_models.py --work <work> --out <dir> --models final=<work>/gs_final/splat.ply ...
"""
import os, json, argparse, numpy as np, cv2, torch, torch.nn.functional as F
from plyfile import PlyData
from gsplat import rasterization
from pytorch_msssim import ssim

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--models", nargs="+", required=True, help="name=path/to/splat.ply")
ap.add_argument("--out", required=True)
ap.add_argument("--split", default="every10", choices=["every10", "nerfstudio"],
                help="held-out frames: every 10th (train.py) or nerfstudio-data's 90/10 linspace split (splatfacto)")
ap.add_argument("--rotate", type=int, default=1, help="rotate sheets 90 deg clockwise (portrait recordings)")
args = ap.parse_args()
dev = "cuda"; os.makedirs(args.out, exist_ok=True)
meta = json.load(open(os.path.join(args.work, "frames.json"))); fr = meta["frames"]
W, H = meta["W"] // 2, meta["H"] // 2
Kn = np.array([[meta["fx"] / 2, 0, meta["cx"] / 2], [0, meta["fy"] / 2, meta["cy"] / 2], [0, 0, 1]])
K = torch.tensor(Kn[None], dtype=torch.float32, device=dev)
G = np.diag([1, -1, -1, 1.0])
sp = np.load(os.path.join(args.work, "sparse.npz")); X, cam, pt, uv = sp["X"], sp["cam"], sp["pt"], sp["uv"]
good = np.bincount(pt, minlength=len(X))[pt] >= 5


def load(path):
    v = PlyData.read(path)["vertex"]; c = lambda n: torch.tensor(np.asarray(v[n]), dtype=torch.float32, device=dev)
    m = torch.stack([c("x"), c("y"), c("z")], 1)
    nr = len([n for n in v.data.dtype.names if n.startswith("f_rest")])
    col = torch.stack([c(f"f_dc_{i}") for i in range(3)], 1)[:, None]
    if nr:
        col = torch.cat([col, torch.stack([c(f"f_rest_{i}") for i in range(nr)], 1).reshape(len(m), 3, -1).transpose(1, 2)], 1)
    return dict(means=m, quats=F.normalize(torch.stack([c(f"rot_{i}") for i in range(4)], 1), dim=-1),
                scales=torch.exp(torch.stack([c(f"scale_{i}") for i in range(3)], 1)), opacities=torch.sigmoid(c("opacity")),
                colors=col, sh=int(round(np.sqrt(col.shape[1]))) - 1)


@torch.no_grad()
def render(g, c2w_gl):
    w2c = torch.tensor(np.linalg.inv(np.array(c2w_gl) @ G), dtype=torch.float32, device=dev)[None]
    out, _, _ = rasterization(g["means"], g["quats"], g["scales"], g["opacities"], g["colors"], w2c, K, W, H,
                              sh_degree=g["sh"], render_mode="RGB+ED", near_plane=0.05, far_plane=50.0)
    return out[0, ..., :3].clamp(0, 1), out[0, ..., 3]


def look(pos, tgt):
    f = tgt - pos; f /= np.linalg.norm(f); r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    c2w = np.eye(4); c2w[:3, 0], c2w[:3, 1], c2w[:3, 2], c2w[:3, 3] = r, u, -f, pos      # OpenGL camera
    return c2w


def photo(i):
    im = cv2.resize(cv2.imread(os.path.join(args.work, "images", fr[i]["name"] + ".jpg")), (W, H), interpolation=cv2.INTER_AREA)
    return torch.from_numpy(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).to(dev).float() / 255


def lapvar(x):
    g = cv2.cvtColor((x * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    return cv2.Laplacian(g, cv2.CV_64F).var()


def label(img, text):
    img = np.ascontiguousarray(cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) if args.rotate else img)
    cv2.putText(img, text, (8, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4)
    cv2.putText(img, text, (8, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    return img


def bgr(x):
    return (x[..., ::-1] * 255).astype(np.uint8)


if args.split == "nerfstudio":                     # nerfstudio_dataparser: train = linspace(0, n-1, ceil(0.9 n))
    n_ = len(fr); tr_ = set(np.linspace(0, n_ - 1, int(np.ceil(n_ * 0.9)), dtype=int).tolist())
    test_ids = [i for i in range(n_) if i not in tr_]
else:
    test_ids = list(range(0, len(fr), 10))
models = [(s.split("=", 1)[0], load(s.split("=", 1)[1])) for s in args.models]
t0 = fr[0]["pts"]
print(f"{len(test_ids)} held-out frames; geometry vs BA points seen in >= 5 views")
print(f"{'model':12s} {'splats':>8s} {'PSNR(cf)':>9s} {'SSIM':>6s} {'sharp':>6s} {'geo med':>8s} {'>10%':>6s} {'>25%':>6s}")
res = {}
for name, g in models:
    ps, ss, sh, E = [], [], [], []
    for i in test_ids:
        gt = photo(i); r, d = render(g, fr[i]["c2w"])
        A = torch.cat([r.reshape(-1, 3), torch.ones(H * W, 1, device=dev)], 1)
        ra = (A @ torch.linalg.lstsq(A, gt.reshape(-1, 3)).solution).reshape(H, W, 3).clamp(0, 1)
        ps.append(float(-10 * torch.log10(((ra - gt) ** 2).mean())))
        ss.append(float(ssim(ra.permute(2, 0, 1)[None], gt.permute(2, 0, 1)[None], data_range=1.0)))
        sh.append(lapvar(r.cpu().numpy()) / max(lapvar(gt.cpu().numpy()), 1e-6))
        o = (cam == i) & good
        if o.sum():
            c2w = np.array(fr[i]["c2w"]) @ G
            z = ((X[pt[o]] - c2w[:3, 3]) @ c2w[:3, :3])[:, 2]
            u = np.clip((uv[o, 0] / 2).astype(int), 0, W - 1); v = np.clip((uv[o, 1] / 2).astype(int), 0, H - 1)
            dv = d.cpu().numpy()[v, u]; ok = (z > 0.1) & (dv > 0)
            E.append(np.abs(dv[ok] - z[ok]) / z[ok])
    E = np.concatenate(E)
    res[name] = dict(splats=len(g["means"]), psnr_cf=np.mean(ps), ssim=np.mean(ss), sharpness=float(np.mean(sh)),
                     geo_median=float(np.median(E)), geo_10=float((E > 0.1).mean()), geo_25=float((E > 0.25).mean()))
    m = res[name]
    print(f"{name:12s} {m['splats']:8d} {m['psnr_cf']:9.2f} {m['ssim']:6.3f} {m['sharpness']:6.2f} "
          f"{100*m['geo_median']:7.2f}% {100*m['geo_10']:5.1f}% {100*m['geo_25']:5.1f}%", flush=True)
json.dump(res, open(os.path.join(args.out, "metrics.json"), "w"), indent=1)

# held-out sheet: 4 frames spread over the recording (first one inside the first 20 s)
pick = [test_ids[k] for k in np.linspace(1, len(test_ids) - 1, 4).astype(int)]
pick[0] = min(test_ids, key=lambda i: abs(fr[i]["pts"] - t0 - 10))
rows, drows = [], []
for i in pick:
    row = [label(bgr(photo(i).cpu().numpy()), f"photo {fr[i]['pts'] - t0:.0f}s")]; drow = [row[0]]
    for name, g in models:
        r, d = render(g, fr[i]["c2w"])
        row.append(label(bgr(r.cpu().numpy()), name))
        dn = np.clip((np.log(d.cpu().numpy().clip(0.3, 8)) - np.log(0.3)) / (np.log(8) - np.log(0.3)), 0, 1)
        drow.append(label(cv2.applyColorMap((dn * 255).astype(np.uint8), cv2.COLORMAP_TURBO), name + " depth"))
    rows.append(np.hstack(row)); drows.append(np.hstack(drow))
cv2.imwrite(os.path.join(args.out, "heldout.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
cv2.imwrite(os.path.join(args.out, "depth.jpg"), np.vstack(drows), [cv2.IMWRITE_JPEG_QUALITY, 88])

# off-path sheet: from the room centre (mean camera position) looking N/E/S/W, slightly down
C = np.array([np.array(f["c2w"])[:3, 3] for f in fr]); c = C.mean(0)
rows = []
for k, ang in enumerate(np.radians([0, 90, 180, 270])):
    tgt = c + np.array([np.cos(ang), -0.35, np.sin(ang)])
    c2w = look(c, tgt)
    if args.rotate:                                    # portrait recordings: roll so the sheet rotation shows it upright
        c2w = c2w @ np.array([[0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1.0]])
    rows.append(np.hstack([label(bgr(render(g, c2w)[0].cpu().numpy()), f"{name} centre {k * 90}deg") for name, g in models]))
cv2.imwrite(os.path.join(args.out, "offpath.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
print("sheets ->", args.out)
