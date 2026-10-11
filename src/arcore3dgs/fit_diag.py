"""Why are renders blurrier than the photos? Full-resolution fit diagnostic on TRAINING views.

For each sampled frame: render at full res, then
  * PSNR / sharpness ratio (Laplacian variance render / photo)
  * misalignment: dense optical flow render -> photo (DIS). Flow that grows towards the image border
    means lens distortion / wrong intrinsics; uniform flow means pose error; ~0 flow + blur means the
    model itself is too coarse (capacity / training).
Writes crops (photo | render, centre and corner) to --out.

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/fit_diag.py --work <work> --ply <splat.ply> --out <dir>
"""
import os, json, argparse, numpy as np, cv2, torch, torch.nn.functional as F
from plyfile import PlyData
from gsplat import rasterization

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--ply", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--frames_file", default="frames.json")
ap.add_argument("--images", default="images")
ap.add_argument("--n", type=int, default=12)
args = ap.parse_args()
dev = "cuda"; os.makedirs(args.out, exist_ok=True)
meta = json.load(open(os.path.join(args.work, args.frames_file))); fr = meta["frames"]
W, H = meta["W"], meta["H"]
K = torch.tensor([[[meta["fx"], 0, meta["cx"]], [0, meta["fy"], meta["cy"]], [0, 0, 1]]], dtype=torch.float32, device=dev)
G = np.diag([1, -1, -1, 1.0])
v = PlyData.read(args.ply)["vertex"]; c = lambda n: torch.tensor(np.asarray(v[n]), dtype=torch.float32, device=dev)
means = torch.stack([c("x"), c("y"), c("z")], 1)
nr = len([n for n in v.data.dtype.names if n.startswith("f_rest")])
col = torch.stack([c(f"f_dc_{i}") for i in range(3)], 1)[:, None]
if nr:
    col = torch.cat([col, torch.stack([c(f"f_rest_{i}") for i in range(nr)], 1).reshape(len(means), 3, -1).transpose(1, 2)], 1)
sh = int(round(np.sqrt(col.shape[1]))) - 1
quats = F.normalize(torch.stack([c(f"rot_{i}") for i in range(4)], 1), dim=-1)
scales = torch.exp(torch.stack([c(f"scale_{i}") for i in range(3)], 1)); opac = torch.sigmoid(c("opacity"))
test = set(range(0, len(fr), 10))
ids = [i for i in np.linspace(0, len(fr) - 1, args.n * 2).astype(int) if i not in test][: args.n]
dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
yy, xx = np.mgrid[0:H, 0:W]; rad = np.hypot(xx - W / 2, yy - H / 2) / np.hypot(W / 2, H / 2)
bins = [0, 0.25, 0.5, 0.75, 1.01]
rows = []; acc = {"psnr": [], "sharp": [], "flow": [[] for _ in bins[:-1]], "flow_dir": []}
for i in ids:
    w2c = torch.tensor(np.linalg.inv(np.array(fr[i]["c2w"]) @ G), dtype=torch.float32, device=dev)[None]
    with torch.no_grad():
        out, _, _ = rasterization(means, quats, scales, opac, col, w2c, K, W, H, sh_degree=sh)
    r = (out[0].clamp(0, 1).cpu().numpy() * 255).astype(np.uint8)[..., ::-1]
    p = cv2.imread(os.path.join(args.work, args.images, fr[i]["name"] + ".jpg"))
    psnr = 10 * np.log10(255 ** 2 / np.mean((r.astype(float) - p) ** 2))
    gr, gp = cv2.cvtColor(r, cv2.COLOR_BGR2GRAY), cv2.cvtColor(p, cv2.COLOR_BGR2GRAY)
    sharp = cv2.Laplacian(gr, cv2.CV_64F).var() / cv2.Laplacian(gp, cv2.CV_64F).var()
    fl = dis.calc(gr, gp, None); mag = np.hypot(fl[..., 0], fl[..., 1])
    tex = cv2.Laplacian(gp, cv2.CV_64F, ksize=3) ** 2 > 200                 # only textured pixels have reliable flow
    for k in range(len(bins) - 1):
        m = tex & (rad >= bins[k]) & (rad < bins[k + 1])
        acc["flow"][k].append(np.median(mag[m]) if m.sum() > 500 else np.nan)
    # radial component of flow (positive = photo content further out than render = barrel/pincushion signature)
    ur = np.stack([xx - W / 2, yy - H / 2], -1) / (np.hypot(xx - W / 2, yy - H / 2)[..., None] + 1e-6)
    m = tex & (rad > 0.6); acc["flow_dir"].append(np.median((fl * ur).sum(-1)[m]) if m.sum() > 500 else np.nan)
    acc["psnr"].append(psnr); acc["sharp"].append(sharp)
    cy, cx = H // 2, W // 2; s = 270
    crop = lambda a, y, x: a[y - s:y + s, x - s:x + s]
    rows.append(np.hstack([crop(p, cy, cx), crop(r, cy, cx), crop(p, s, s), crop(r, s, s)]))
print(f"model {args.ply}\n{len(ids)} TRAINING views at full res {W}x{H}")
print(f"  PSNR {np.mean(acc['psnr']):.2f} dB   sharpness render/photo {np.mean(acc['sharp']):.2f}")
print("  median misalignment (px) by distance from image centre: " +
      "  ".join(f"{bins[k]:.2f}-{bins[k+1]:.2f}: {np.nanmean(acc['flow'][k]):.2f}" for k in range(len(bins) - 1)))
print(f"  radial flow at the border (px, + = photo content further out): {np.nanmean(acc['flow_dir']):+.2f}")
cv2.imwrite(os.path.join(args.out, "fit_crops.jpg"), np.vstack(rows[:6]), [cv2.IMWRITE_JPEG_QUALITY, 90])
