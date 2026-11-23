"""Remove floaters from a trained splat using MEASURED free space (no retraining).

A splat is a floater if cameras demonstrably looked *through* it:
  * violation: in a training view, the splat projects onto a stereo-measured pixel (mvs_mask) whose
    measured depth is clearly behind it (z < d - margin)
  * support:   in some view it coincides with a measured surface (|z - d| < margin)
Prune if violations >= --min_violations AND support == 0. Thin/foreground objects that stereo measured in
at least one view (e.g. a chair) keep support and survive; splats only in front of unmeasured (blank)
surfaces are never judged. Also removes splats never inside any training camera's view (pure
extrapolation junk), and splats closer than --cam_radius to the camera path (nothing real sits within
a few cm of the lens; these fake reflections/glare and become "splats in the air"). Output: <ply dir>/splat_clean.ply. Run with nerfstudio-env python.

Sensor-path models (scan_009, 2026-11-22) have no stereo depth (no depth_mvs/ / mvs_mask/): --mono 1 uses the
per-frame depth priors (<work>/mono_prior, scaled to the model) as the measured depth, with a relative tolerance
(--mono_tol; the priors disagree between views by ~3 - 12 %, R-098). --exclude <list> leaves frames (the held-out
test frames) out of the evidence, so a held-out score stays fair. The BA points are projected with the frame's
camera (the stored uv can belong to a differently sized image). Dropped splat positions: <out>_dropped.npz.
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
ap.add_argument("--ba_evidence", type=int, default=1, help="use BA-triangulated points (sparse.npz, 0.6 px) as free-space evidence")
ap.add_argument("--cam_radius", type=float, default=0.2, help="m: drop splats this close to the camera path (0 = off)")
ap.add_argument("--colmap", type=int, default=1, help="also use COLMAP depth (depth_colmap/, colmap_mvs.py) as measured depth")
ap.add_argument("--mono", type=int, default=0, help="use the depth priors (mono_prior/) as measured depth (sensor-path models)")
ap.add_argument("--mono_tol", type=float, default=0.2, help="relative: violation z < (1 - tol) d, support |z - d| < tol d")
ap.add_argument("--exclude", default=None, help="file with frame names not used as evidence (held-out frames)")
ap.add_argument("--max_depth", type=float, default=8.0, help="model units: splats farther from a camera are not judged by it")
args = ap.parse_args()
dev = "cuda"

meta = json.load(open(os.path.join(args.work, "frames.json"))); fr = meta["frames"]
excl = set(open(args.exclude).read().split()) if args.exclude else set()
if "depth_scale" in meta:
    s = meta["depth_scale"]; W, H = int(meta["W"] * s), int(meta["H"] * s)
else:                                                       # sensor-path export: the depth priors' resolution
    H, W = np.load(os.path.join(args.work, "mono_prior", fr[0]["name"] + ".npz"))["depth"].shape; s = W / meta["W"]
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
    if k % args.every or f["name"] in excl:
        continue
    mp = os.path.join(args.work, "mvs_mask", f["name"] + ".npy")
    if not os.path.exists(mp):
        continue
    m = torch.from_numpy(np.load(mp)).to(dev)
    d = torch.from_numpy(np.load(os.path.join(args.work, "depth_mvs", f["name"] + ".npy")).astype(np.float32)).to(dev)
    pcm = os.path.join(args.work, "depth_colmap", f["name"] + ".npy")
    if args.colmap and os.path.exists(pcm):
        dc = torch.from_numpy(np.load(pcm)).to(dev)
        if dc.shape == d.shape:
            d = torch.where(dc > 0, dc, d); m = m | (dc > 0)
    c2w = torch.tensor(f["c2w"], dtype=torch.float32, device=dev)
    R = c2w[:3, :3] @ G; C = c2w[:3, 3]
    pc = (X - C) @ R                                          # OpenCV camera coords
    z = pc[:, 2]
    u = (K[0, 0] * pc[:, 0] / z + K[0, 2]).long(); vv = (K[1, 1] * pc[:, 1] / z + K[1, 2]).long()
    inb = (z > 0.1) & (z < args.max_depth) & (u >= 0) & (u < W) & (vv >= 0) & (vv < H)
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

used_mono = 0
if args.mono:                                               # depth priors as measured depth, relative tolerance
    for k, f in enumerate(fr):
        if k % args.every or f["name"] in excl:
            continue
        mp = os.path.join(args.work, "mono_prior", f["name"] + ".npz")
        if not os.path.exists(mp):
            continue
        zz = np.load(mp)
        d = torch.from_numpy(zz["depth"].astype(np.float32)).to(dev)
        m = torch.from_numpy(zz["valid"]).to(dev) & (d > 0)
        c2w = torch.tensor(f["c2w"], dtype=torch.float32, device=dev)
        R = c2w[:3, :3] @ G; C = c2w[:3, 3]
        pc = (X - C) @ R; z = pc[:, 2]
        u = (K[0, 0] * pc[:, 0] / z + K[0, 2]).long(); vv = (K[1, 1] * pc[:, 1] / z + K[1, 2]).long()
        inb = (z > 0.1) & (z < args.max_depth) & (u >= 0) & (u < W) & (vv >= 0) & (vv < H)
        seen += inb.float()
        ui, vi = u.clamp(0, W - 1), vv.clamp(0, H - 1)
        meas = inb & m[vi, ui]; dm = d[vi, ui]
        viol += (meas & (z < (1 - args.mono_tol) * dm)).float()
        supp += (meas & ((z - dm).abs() < args.mono_tol * dm)).float()
        used_mono += 1
    print(f"depth-prior evidence from {used_mono} views (tol {args.mono_tol:g})")

# BA evidence: every BA point a frame observed proves the ray camera -> point is empty
if args.ba_evidence and os.path.exists(os.path.join(args.work, "sparse.npz")):
    import torch.nn.functional as Fnn
    sp = np.load(os.path.join(args.work, "sparse.npz"))
    Xb, camb, ptb, uvb = sp["X"], sp["cam"], sp["pt"], sp["uv"]
    Gn = np.diag([1.0, -1.0, -1.0])
    nb = 0
    Kn = K.cpu().numpy()
    for k, f in enumerate(fr):
        o = camb == k
        if o.sum() < 20 or f["name"] in excl:
            continue
        c2w = np.array(f["c2w"]); Rn = c2w[:3, :3] @ Gn; Cn = c2w[:3, 3]
        pb = (Xb[ptb[o]] - Cn) @ Rn; zb = pb[:, 2]
        zs = np.maximum(zb, 1e-6)                                  # projected with this camera (not the stored uv)
        ub = (Kn[0, 0] * pb[:, 0] / zs + Kn[0, 2]).astype(int); vb = (Kn[1, 1] * pb[:, 1] / zs + Kn[1, 2]).astype(int)
        okb = (zb > 0.1) & (ub >= 0) & (ub < W) & (vb >= 0) & (vb < H)
        zmap = torch.full((H, W), 1e9, device=dev)
        zmap[torch.tensor(vb[okb], device=dev), torch.tensor(ub[okb], device=dev)] = torch.tensor(zb[okb], dtype=torch.float32, device=dev)
        zmap = -Fnn.max_pool2d(-zmap[None, None], 5, 1, 2)[0, 0]          # nearest BA depth within 2 px
        R = torch.tensor(Rn, dtype=torch.float32, device=dev); C = torch.tensor(Cn, dtype=torch.float32, device=dev)
        pc = (X - C) @ R; z = pc[:, 2]
        u = (K[0, 0] * pc[:, 0] / z + K[0, 2]).long(); vv = (K[1, 1] * pc[:, 1] / z + K[1, 2]).long()
        inb = (z > 0.1) & (u >= 0) & (u < W) & (vv >= 0) & (vv < H)
        seen += inb.float()
        dm = zmap[vv.clamp(0, H - 1), u.clamp(0, W - 1)]
        has = inb & (dm < 1e8)
        viol += (has & (z < 0.8 * dm - 0.05)).float()
        supp += (has & ((z - dm).abs() < 0.1 * dm + 0.03)).float()
        nb += 1
    print(f"BA free-space evidence from {nb} views")

floater = (viol >= args.min_violations) & (supp == 0)
unseen = seen == 0
near = torch.zeros(N, dtype=torch.bool, device=dev)
if args.cam_radius > 0:
    from scipy.spatial import cKDTree
    Cs = np.array([np.array(f["c2w"])[:3, 3] for f in fr])
    path = np.concatenate([np.linspace(a, b, 8, endpoint=False) for a, b in zip(Cs[:-1], Cs[1:])] + [Cs[-1:]])
    dist, _ = cKDTree(path).query(X.cpu().numpy())
    near = torch.tensor(dist < args.cam_radius, device=dev)
    print(f"near the camera path (< {args.cam_radius * 100:.0f} cm): {int(near.sum())} ({near.float().mean() * 100:.1f}%)")
drop = (floater | unseen | near).cpu().numpy()
print(f"checked against {used} stereo / {used_mono} prior views ({len(excl)} frames excluded): floaters {int(floater.sum())} ({floater.float().mean() * 100:.1f}%), "
      f"never in view {int(unseen.sum())} ({unseen.float().mean() * 100:.1f}%) -> keeping {N - drop.sum()} of {N}")
out = args.out or os.path.join(os.path.dirname(args.ply), "splat_clean.ply")
PlyData([PlyElement.describe(v.data[~drop], "vertex")]).write(out)
np.savez_compressed(out[:-4] + "_dropped.npz", X=X.cpu().numpy()[drop], floater=floater.cpu().numpy()[drop],
                    unseen=unseen.cpu().numpy()[drop], near=near.cpu().numpy()[drop],
                    viol=viol.cpu().numpy()[drop], supp=supp.cpu().numpy()[drop])
print("wrote", out)
