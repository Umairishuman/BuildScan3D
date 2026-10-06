"""Compare trained splat models on held-out frames (+ colour-affine-corrected PSNR) and novel views."""
import os, json, argparse, numpy as np, cv2, torch, torch.nn.functional as F
from plyfile import PlyData
from gsplat import rasterization
from pytorch_msssim import ssim

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--models", nargs="+", required=True, help="name=path/to/splat.ply:pose_key")
ap.add_argument("--out", required=True)
args = ap.parse_args()
dev = "cuda"
os.makedirs(args.out, exist_ok=True)
meta = json.load(open(os.path.join(args.work, "frames.json"))); frames = meta["frames"]
W, H = meta["W"] // 2, meta["H"] // 2
K = torch.tensor([[[meta["fx"] / 2, 0, meta["cx"] / 2], [0, meta["fy"] / 2, meta["cy"] / 2], [0, 0, 1]]], device=dev)
G = np.diag([1, -1, -1, 1.0])


def load(path):
    v = PlyData.read(path)["vertex"]; c = lambda n: torch.tensor(np.asarray(v[n]), dtype=torch.float32, device=dev)
    m = torch.stack([c("x"), c("y"), c("z")], 1)
    nr = len([n for n in v.data.dtype.names if n.startswith("f_rest")])
    col = torch.cat([torch.stack([c(f"f_dc_{i}") for i in range(3)], 1)[:, None],
                     torch.stack([c(f"f_rest_{i}") for i in range(nr)], 1).reshape(len(m), 3, -1).transpose(1, 2)], 1)
    return dict(means=m, quats=F.normalize(torch.stack([c(f"rot_{i}") for i in range(4)], 1), dim=-1),
                scales=torch.exp(torch.stack([c(f"scale_{i}") for i in range(3)], 1)), opacities=torch.sigmoid(c("opacity")),
                colors=col, sh=int(round(np.sqrt(col.shape[1]))) - 1,
                aa="antialiased" if os.path.exists(os.path.join(os.path.dirname(path), "metrics.json")) and
                json.load(open(os.path.join(os.path.dirname(path), "metrics.json"))).get("antialiased") else "classic")


@torch.no_grad()
def render(g, c2w_gl):
    w2c = torch.tensor(np.linalg.inv(np.array(c2w_gl) @ G), dtype=torch.float32, device=dev)[None]
    out, _, _ = rasterization(g["means"], g["quats"], g["scales"], g["opacities"], g["colors"], w2c, K, W, H, sh_degree=g["sh"], rasterize_mode=g["aa"])
    return out[0].clamp(0, 1)


def look(pos, tgt):
    f = tgt - pos; f /= np.linalg.norm(f); r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    c2w = np.eye(4); c2w[:3, 0], c2w[:3, 1], c2w[:3, 2], c2w[:3, 3] = r, u, -f, pos   # OpenGL camera
    return c2w


test_ids = list(range(0, len(frames), 10))
models = []
for spec in args.models:
    name, rest = spec.split("=", 1); path, key = rest.rsplit(":", 1)
    models.append((name, load(path), key))

print(f"{'model':10s} {'PSNR':>6s} {'PSNR(colour-fit)':>17s} {'SSIM':>6s}")
for name, g, key in models:
    ps, psa, ss = [], [], []
    for i in test_ids:
        gt = torch.from_numpy(cv2.cvtColor(cv2.resize(cv2.imread(os.path.join(args.work, "images", frames[i]["name"] + ".jpg")), (W, H), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)).to(dev).float() / 255
        r = render(g, frames[i][key])
        ps.append(float(-10 * torch.log10(((r - gt) ** 2).mean())))
        A = torch.cat([r.reshape(-1, 3), torch.ones(H * W, 1, device=dev)], 1)          # per-image colour affine
        X = torch.linalg.lstsq(A, gt.reshape(-1, 3)).solution
        ra = (A @ X).reshape(H, W, 3).clamp(0, 1)
        psa.append(float(-10 * torch.log10(((ra - gt) ** 2).mean())))
        ss.append(float(ssim(ra.permute(2, 0, 1)[None], gt.permute(2, 0, 1)[None], data_range=1.0)))
    print(f"{name:10s} {np.mean(ps):6.2f} {np.mean(psa):17.2f} {np.mean(ss):6.3f}")

# novel views: low near the floor looking along it, and grazing along a wall
c = np.array(frames[len(frames) // 2]["c2w"])[:3, 3]
fwd = -np.array(frames[len(frames) // 2]["c2w"])[:3, 2]; fwd[1] = 0; fwd /= np.linalg.norm(fwd)
views = {"low_floor": look(c + np.array([0, -0.9, 0]), c + np.array([0, -1.2, 0]) + 2.5 * fwd),
         "grazing": look(c, c + 2.0 * fwd + 1.2 * np.cross(fwd, [0, 1, 0])),
         "test_view": np.array(frames[test_ids[len(test_ids) // 2]]["c2w"])}
for vn, c2w in views.items():
    row = [(render(g, c2w).cpu().numpy() * 255).astype(np.uint8) for _, g, _ in models]
    img = np.hstack(row)[..., ::-1].copy()
    for k, (name, _, _) in enumerate(models):
        cv2.putText(img, name, (10 + k * W, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.imwrite(os.path.join(args.out, f"{vn}.jpg"), cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) if False else img)
print("renders ->", args.out)
