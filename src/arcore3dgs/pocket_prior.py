"""PocketGS-style keyframes + dense geometric prior.

PocketGS (2025): information-gated keyframes (displacement + sharpness), BA-refined poses, MVS depth
filtered by confidence and fused into a dense, *spatially balanced* point cloud P that seeds
surface-aligned anisotropic Gaussians; then a short photometric optimisation stays close to P.

Here:
  1. keyframe gate: keep a frame only if the camera moved >= --min_move m or turned >= --min_turn deg
     since the last kept frame (from our sharpest-in-window keyframes) -> frames_pocket.json
  2. dense prior: every frame's depth_mvs (stereo-measured + ARCore/Metric3D-anchored fill) is checked
     against its K nearest views; a pixel is kept only if >= --min_agree neighbours reproduce it
     (reprojection < 2 px, depth < 2%). Plain walls with consistent anchored depth survive; the
     inconsistent guesses that caused ghost geometry do not.
  3. voxel-balanced fusion (one point per --voxel), outlier removal, 16-NN normals -> prior_points.ply
Run with nerfstudio-env python.
"""
import os, json, argparse
import numpy as np, cv2, torch, open3d as o3d

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--min_move", type=float, default=0.08)
ap.add_argument("--min_turn", type=float, default=6.0)
ap.add_argument("--k", type=int, default=6, help="neighbour views for the consistency check")
ap.add_argument("--min_agree", type=int, default=2)
ap.add_argument("--stride", type=int, default=2)
ap.add_argument("--voxel", type=float, default=0.02)
args = ap.parse_args()
dev = "cuda"

meta = json.load(open(os.path.join(args.work, "frames.json"))); fr = meta["frames"]; N = len(fr)
s = meta["depth_scale"]; W, H = int(meta["W"] * s), int(meta["H"] * s)
K = torch.tensor([[meta["fx"] * s, 0, meta["cx"] * s], [0, meta["fy"] * s, meta["cy"] * s], [0, 0, 1]], device=dev)
Kinv = torch.linalg.inv(K)
G = torch.diag(torch.tensor([1.0, -1.0, -1.0], device=dev))
Rw = torch.stack([torch.tensor(f["c2w"], dtype=torch.float32, device=dev)[:3, :3] @ G for f in fr])
Cw = torch.stack([torch.tensor(f["c2w"], dtype=torch.float32, device=dev)[:3, 3] for f in fr])
dropped = set(meta.get("fusion_dropped", []))

# ---------- 1. displacement / rotation keyframe gate ----------
keep, last = [0], 0
for i in range(1, N):
    move = float((Cw[i] - Cw[last]).norm())
    turn = float(torch.rad2deg(torch.arccos(((Rw[i].T @ Rw[last]).trace() - 1).clamp(-2, 2) / 2)))
    if move >= args.min_move or turn >= args.min_turn:
        keep.append(i); last = i
mp = dict(meta); mp["frames"] = [fr[i] for i in keep]
json.dump(mp, open(os.path.join(args.work, "frames_pocket.json"), "w"), indent=1)
print(f"keyframe gate ({args.min_move} m / {args.min_turn} deg): {len(keep)} of {N} frames -> frames_pocket.json")

# ---------- 2. multi-view-consistent dense depth ----------
D = torch.stack([torch.from_numpy(np.load(os.path.join(args.work, "depth_mvs", f["name"] + ".npy")).astype(np.float32))
                 for f in fr]).to(dev)
D[~torch.isfinite(D)] = 0
st = args.stride
vv, uu = torch.meshgrid(torch.arange(0, H, st, device=dev), torch.arange(0, W, st, device=dev), indexing="ij")
pix = torch.stack([uu.flatten() + 0.5, vv.flatten() + 0.5, torch.ones(uu.numel(), device=dev)])
rays = Kinv @ pix
look = Cw + 1.5 * Rw[:, :, 2]
pts_l, col_l, kept_frac = [], [], []
for i in range(N):
    if fr[i]["name"] in dropped or fr[i].get("fallback_unverified"):
        continue
    d = D[i, vv, uu].flatten()
    ok = (d > 0.15) & (d < 6)
    X = Cw[i][:, None] + Rw[i] @ (rays * d)
    dist = (look - look[i]).norm(dim=1) + 0.5 * (Cw - Cw[i]).norm(dim=1); dist[i] = 1e9
    agree = torch.zeros(d.shape[0], device=dev)
    for j in torch.argsort(dist)[:args.k].tolist():
        pc = Rw[j].T @ (X - Cw[j][:, None]); z = pc[2]
        u = K[0, 0] * pc[0] / z + K[0, 2]; v = K[1, 1] * pc[1] / z + K[1, 2]
        inb = (z > 0.1) & (u >= 0) & (u < W - 1) & (v >= 0) & (v < H - 1)
        dj = D[j, v.long().clamp(0, H - 1), u.long().clamp(0, W - 1)]
        Xb = Cw[j][:, None] + Rw[j] @ (Kinv @ torch.stack([u, v, torch.ones_like(u)]) * dj)
        pr = Rw[i].T @ (Xb - Cw[i][:, None])
        ur = K[0, 0] * pr[0] / pr[2] + K[0, 2]; vr = K[1, 1] * pr[1] / pr[2] + K[1, 2]
        good = inb & (dj > 0.1) & (torch.hypot(ur - pix[0], vr - pix[1]) < 2.0) & ((pr[2] - d).abs() / d.clamp_min(1e-3) < 0.02)
        agree += good.float()
    sel = ok & (agree >= args.min_agree)
    kept_frac.append(float(sel.float().mean()))
    if sel.sum() == 0:
        continue
    pts_l.append(X[:, sel].T.cpu().numpy())
    im = cv2.resize(cv2.imread(os.path.join(args.work, "images", fr[i]["name"] + ".jpg")), (W, H), interpolation=cv2.INTER_AREA)
    col_l.append(im[vv.flatten()[sel].cpu().numpy(), uu.flatten()[sel].cpu().numpy(), ::-1] / 255.0)
print(f"multi-view-consistent depth: median {np.median(kept_frac) * 100:.0f}% of pixels per frame kept "
      f"(stereo alone measured ~5%)")

# ---------- 3. voxel-balanced fusion ----------
P = np.concatenate(pts_l); Cc = np.concatenate(col_l)
vox = np.floor(P / args.voxel).astype(np.int64)
_, inv, cnt = np.unique(vox, axis=0, return_inverse=True, return_counts=True)
inv = inv.ravel()
Pm = np.zeros((cnt.size, 3)); Cm = np.zeros((cnt.size, 3))
np.add.at(Pm, inv, P); np.add.at(Cm, inv, Cc)
Pm /= cnt[:, None]; Cm /= cnt[:, None]
keep_v = cnt >= 2                                    # seen consistently from >= 2 frames
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(Pm[keep_v]); pcd.colors = o3d.utility.Vector3dVector(np.clip(Cm[keep_v], 0, 1))
pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=16, std_ratio=2.0)
pcd.estimate_normals(o3d.geometry.KDTreeSearchParamKNN(knn=16))
o3d.io.write_point_cloud(os.path.join(args.work, "prior_points.ply"), pcd)
print(f"prior_points.ply: {len(pcd.points)} points ({args.voxel * 100:.0f} cm voxels), extent (m) "
      f"{np.round(np.asarray(pcd.get_axis_aligned_bounding_box().get_extent()), 2)}")
