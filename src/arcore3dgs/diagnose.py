"""Diagnose why a trained splat looks blurry ("cotton"): no training, rendering only.

  * renders training AND held-out views; compares colour-fit PSNR and a sharpness ratio
    (Laplacian variance of render / of the real image, same view: < 1 means the model is blurrier
    than the photo). Training views blurry too -> underfitting; only test views -> bad geometry/poses.
  * full-resolution crops (render vs photo) to see whether half-res training caps detail
  * Gaussian statistics: opacity and size distribution (large semi-transparent splats = cotton look)
"""
import os, json, argparse
import numpy as np, cv2, torch, torch.nn.functional as F
from plyfile import PlyData
from gsplat import rasterization

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--ply", required=True)
ap.add_argument("--frames", default="frames.json", help="frames file the model was trained with")
ap.add_argument("--out", required=True)
ap.add_argument("--test_every", type=int, default=10)
ap.add_argument("--n", type=int, default=40, help="views sampled per split")
args = ap.parse_args()
dev = "cuda"
os.makedirs(args.out, exist_ok=True)
meta = json.load(open(os.path.join(args.work, args.frames))); fr = meta["frames"]
G = np.diag([1, -1, -1, 1.0])

v = PlyData.read(args.ply)["vertex"]
c = lambda n: torch.tensor(np.asarray(v[n]), dtype=torch.float32, device=dev)
means = torch.stack([c("x"), c("y"), c("z")], 1)
nr = len([n for n in v.data.dtype.names if n.startswith("f_rest")])
colors = torch.cat([torch.stack([c(f"f_dc_{i}") for i in range(3)], 1)[:, None],
                    torch.stack([c(f"f_rest_{i}") for i in range(nr)], 1).reshape(len(means), 3, -1).transpose(1, 2)], 1)
quats = F.normalize(torch.stack([c(f"rot_{i}") for i in range(4)], 1), dim=-1)
scales = torch.exp(torch.stack([c(f"scale_{i}") for i in range(3)], 1))
opac = torch.sigmoid(c("opacity"))
sh = int(round(np.sqrt(colors.shape[1]))) - 1
mj = os.path.join(os.path.dirname(args.ply), "metrics.json")
aa = "antialiased" if os.path.exists(mj) and json.load(open(mj)).get("antialiased") else "classic"

# ---------- Gaussian statistics ----------
smax, smin = scales.max(1).values, scales.min(1).values
vis = opac > 0.05
print(f"gaussians {len(means) / 1e6:.2f}M | opacity: <0.1 {(opac < 0.1).float().mean() * 100:.0f}%, "
      f"0.1-0.5 {((opac >= 0.1) & (opac < 0.5)).float().mean() * 100:.0f}%, >0.9 {(opac > 0.9).float().mean() * 100:.0f}%")
print(f"largest axis (visible splats): median {smax[vis].median() * 1000:.1f} mm, p90 {smax[vis].quantile(0.9) * 1000:.1f} mm, "
      f"p99 {smax[vis].quantile(0.99) * 1000:.1f} mm | flatness (min/max) median {(smin / smax)[vis].median():.2f}")
big_soft = vis & (smax > 0.02) & (opac < 0.5)
print(f"large (>2 cm) semi-transparent (<0.5) splats: {big_soft.float().mean() * 100:.1f}% of visible")


@torch.no_grad()
def render(c2w_gl, W, H, s):
    K = torch.tensor([[[meta["fx"] * s, 0, meta["cx"] * s], [0, meta["fy"] * s, meta["cy"] * s], [0, 0, 1]]], device=dev)
    w2c = torch.tensor(np.linalg.inv(np.array(c2w_gl) @ G), dtype=torch.float32, device=dev)[None]
    out, _, _ = rasterization(means, quats, scales, opac, colors, w2c, K, W, H, sh_degree=sh, rasterize_mode=aa)
    return out[0].clamp(0, 1)


def colour_fit(r, gt):
    A = torch.cat([r.reshape(-1, 3), torch.ones(r.shape[0] * r.shape[1], 1, device=dev)], 1)
    X = torch.linalg.lstsq(A, gt.reshape(-1, 3)).solution
    return (A @ X).reshape(r.shape).clamp(0, 1)


def lapvar(img):
    g = cv2.cvtColor((img.cpu().numpy() * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    return cv2.Laplacian(g, cv2.CV_64F).var()


test = list(range(0, len(fr), args.test_every))
train = [i for i in range(len(fr)) if i not in set(test)]
rng = np.random.default_rng(0)
W2, H2 = meta["W"] // 2, meta["H"] // 2
for split, ids in (("train", train), ("test", test)):
    ids = sorted(rng.choice(ids, min(args.n, len(ids)), replace=False).tolist())
    ps, ratio = [], []
    for i in ids:
        im = cv2.imread(os.path.join(args.work, "images", fr[i]["name"] + ".jpg"))
        gt = torch.from_numpy(cv2.cvtColor(cv2.resize(im, (W2, H2), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)).to(dev).float() / 255
        r = colour_fit(render(fr[i]["c2w"], W2, H2, 0.5), gt)
        ps.append(float(-10 * torch.log10(((r - gt) ** 2).mean())))
        ratio.append(lapvar(r) / max(lapvar(gt), 1e-6))
    print(f"{split:5s} views ({len(ids)}): colour-fit PSNR {np.mean(ps):.2f} dB | render/photo sharpness ratio median "
          f"{np.median(ratio):.2f} (p10 {np.percentile(ratio, 10):.2f}, p90 {np.percentile(ratio, 90):.2f})")

# ---------- full-resolution crops: is half-res training capping detail? ----------
for i in [train[len(train) // 3], train[2 * len(train) // 3]]:
    im = cv2.imread(os.path.join(args.work, "images", fr[i]["name"] + ".jpg"))
    H, W = im.shape[:2]
    rf = (render(fr[i]["c2w"], W, H, 1.0).cpu().numpy() * 255).astype(np.uint8)[..., ::-1]
    # crop the most textured 480x270 window of the photo
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    e = cv2.boxFilter(np.abs(cv2.Laplacian(g, cv2.CV_32F)), -1, (480, 270))
    y, x = np.unravel_index(np.argmax(e[135:H - 135, 240:W - 240]), e[135:H - 135, 240:W - 240].shape)
    y, x = y, x
    crop = np.hstack([im[y:y + 270, x:x + 480], rf[y:y + 270, x:x + 480]])
    cv2.imwrite(os.path.join(args.out, f"crop_{fr[i]['name']}.jpg"), crop)
print("crops (photo | render, full res) ->", args.out)
