"""Remove floaters from a trained splat using MEASURED free space (no retraining).

A splat is a floater if cameras demonstrably looked *through* it:
  * violation: in a training view, the splat projects onto a stereo-measured pixel (mvs_mask) whose
    measured depth is clearly behind it (z < d - margin)
  * support:   in some view it coincides with a measured surface (|z - d| < margin)
Prune if violations >= --min_violations AND support == 0. Thin/foreground objects that stereo measured in
at least one view (e.g. a chair) keep support and survive; splats only in front of unmeasured (blank)
surfaces are never judged. Also removes splats never inside any training camera's view (pure
extrapolation junk). Output: <ply dir>/splat_clean.ply. Run with nerfstudio-env python.
"""
import os, json, argparse
import numpy as np, torch
from plyfile import PlyData, PlyElement

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--ply", required=True)
ap.add_argument("--out", default=None)
ap.add_argument("--min_violations", type=int, default=3)
ap.add_argument("--margin", type=float, default=0.05, help="m, plus 3%% of depth")
ap.add_argument("--every", type=int, default=2, help="use every n-th keyframe")
ap.add_argument("--use_fill", type=int, default=0, help="also count violations against filled depth (OFF: on roomAttemptSadness2 it removed real surfaces, held-out PSNR 27.8 -> 22.4)")
ap.add_argument("--fill_margin", type=float, default=0.15, help="m, plus 10%% of depth, for filled pixels")
args = ap.parse_args()
dev = "cuda"

meta = json.load(open(os.path.join(args.work, "frames.json"))); fr = meta["frames"]
s = meta["depth_scale"]; W, H = int(meta["W"] * s), int(meta["H"] * s)
K = torch.tensor([[meta["fx"] * s, 0, meta["cx"] * s], [0, meta["fy"] * s, meta["cy"] * s], [0, 0, 1]], device=dev)
G = torch.diag(torch.tensor([1.0, -1.0, -1.0], device=dev))

ply = PlyData.read(args.ply)
v = ply["vertex"]
X = torch.tensor(np.stack([v["x"], v["y"], v["z"]], 1), dtype=torch.float32, device=dev)
N = len(X)
viol = torch.zeros(N, device=dev); supp = torch.zeros(N, device=dev); seen = torch.zeros(N, device=dev)
used = 0
dropped = set(meta.get("fusion_dropped", []))
for k, f in enumerate(fr):
    if k % args.every:
        continue
    mp = os.path.join(args.work, "mvs_mask", f["name"] + ".npy")
    if not os.path.exists(mp):
        continue
    m = torch.from_numpy(np.load(mp)).to(dev)
    d = torch.from_numpy(np.load(os.path.join(args.work, "depth_mvs", f["name"] + ".npy")).astype(np.float32)).to(dev)
    c2w = torch.tensor(f["c2w"], dtype=torch.float32, device=dev)
    R = c2w[:3, :3] @ G; C = c2w[:3, 3]
    pc = (X - C) @ R                                          # OpenCV camera coords
    z = pc[:, 2]
    u = (K[0, 0] * pc[:, 0] / z + K[0, 2]).long(); vv = (K[1, 1] * pc[:, 1] / z + K[1, 2]).long()
    inb = (z > 0.1) & (z < 8.0) & (u >= 0) & (u < W) & (vv >= 0) & (vv < H)
    seen += inb.float()
    ui, vi = u.clamp(0, W - 1), vv.clamp(0, H - 1)
    meas = inb & m[vi, ui]
    dm = d[vi, ui]
    tol = args.margin + 0.03 * dm
    viol += (meas & (z < dm - tol)).float()
    supp += (meas & ((z - dm).abs() < tol)).float()
    if args.use_fill and f["name"] not in dropped:             # blank walls/ceiling: filled depth, wide margin
        fill = inb & ~m[vi, ui] & (dm > 0.1)
        viol += (fill & (z < dm - (args.fill_margin + 0.10 * dm))).float()
    used += 1

floater = (viol >= args.min_violations) & (supp == 0)
unseen = seen == 0
drop = (floater | unseen).cpu().numpy()
print(f"checked against {used} views: floaters {int(floater.sum())} ({floater.float().mean() * 100:.1f}%), "
      f"never in view {int(unseen.sum())} ({unseen.float().mean() * 100:.1f}%) -> keeping {N - drop.sum()} of {N}")
out = args.out or os.path.join(os.path.dirname(args.ply), "splat_clean.ply")
PlyData([PlyElement.describe(v.data[~drop], "vertex")]).write(out)
print("wrote", out)
