"""Initial point cloud for 3DGS from MEASURED geometry only (PocketGS / standard 3DGS style).

Previously the splats were initialised on the fused TSDF mesh, which is built mostly from single-image
(Metric3D) depth and misses 19-26% of the triangulated points - exactly the textured detail.
Here the initialisation uses:
  * bundle-adjustment points seen in >= 3 views (sparse.npz, ~0.6 px reprojection error), coloured by
    averaging their observations in the images
  * MVS pixels that passed the multi-view consistency check (mvs_mask), back-projected with BA poses
Points are voxel-balanced (one per voxel), statistical outliers removed, and normals estimated from the
16 nearest neighbours (used by train.py only to orient the initial discs, never as a training constraint).
Output: <work>/init_points.ply (x, y, z, nx, ny, nz, red, green, blue). Run with nerfstudio-env python.
"""
import os, json, argparse
import numpy as np, cv2, open3d as o3d

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--min_views", type=int, default=3)
ap.add_argument("--voxel", type=float, default=0.01, help="m; one point per voxel (spatial balance)")
ap.add_argument("--mvs_every", type=int, default=2, help="use MVS pixels from every n-th keyframe")
ap.add_argument("--mvs_stride", type=int, default=2, help="pixel stride within the MVS mask (half-res)")
args = ap.parse_args()

meta = json.load(open(os.path.join(args.work, "frames.json")))
frames = meta["frames"]
G = np.diag([1.0, -1.0, -1.0])

# ---- 1. bundle-adjustment points, coloured from their observations ----
sp = np.load(os.path.join(args.work, "sparse.npz"))
X, cam, pt, uv = sp["X"], sp["cam"], sp["pt"], sp["uv"]
nobs = np.bincount(pt, minlength=len(X))
good = nobs >= args.min_views
col_sum = np.zeros((len(X), 3)); col_n = np.zeros(len(X))
for c in np.unique(cam):
    sel = (cam == c) & good[pt]
    if not sel.any():
        continue
    im = cv2.imread(os.path.join(args.work, "images", frames[c]["name"] + ".jpg"))
    h, w = im.shape[:2]
    u = np.clip(uv[sel, 0].astype(int), 0, w - 1); v = np.clip(uv[sel, 1].astype(int), 0, h - 1)
    np.add.at(col_sum, pt[sel], im[v, u, ::-1].astype(np.float64))
    np.add.at(col_n, pt[sel], 1)
ba_pts = X[good]
ba_col = col_sum[good] / np.maximum(col_n[good], 1)[:, None]
print(f"BA points seen in >= {args.min_views} views: {len(ba_pts)}")

# ---- 2. MVS-measured pixels ----
s = meta["depth_scale"]
K = np.array([[meta["fx"] * s, 0, meta["cx"] * s], [0, meta["fy"] * s, meta["cy"] * s], [0, 0, 1]])
Kinv = np.linalg.inv(K)
mvs_p, mvs_c = [], []
for k, f in enumerate(frames):
    if k % args.mvs_every:
        continue
    mp = os.path.join(args.work, "mvs_mask", f["name"] + ".npy")
    if not os.path.exists(mp):
        continue
    mm = np.load(mp)
    if mm.sum() < 50:
        continue
    d = np.load(os.path.join(args.work, "depth_mvs", f["name"] + ".npy")).astype(np.float32)
    st = args.mvs_stride
    vv, uu = np.nonzero(mm[::st, ::st]); vv, uu = vv * st, uu * st
    z = d[vv, uu]
    ok = np.isfinite(z) & (z > 0.1)
    vv, uu, z = vv[ok], uu[ok], z[ok]
    Xc = (Kinv @ np.stack([uu + 0.5, vv + 0.5, np.ones(len(uu))])) * z
    c2w = np.array(f["c2w"])
    mvs_p.append((c2w[:3, :3] @ G @ Xc + c2w[:3, 3:4]).T)
    im = cv2.imread(os.path.join(args.work, "images", f["name"] + ".jpg"))
    im = cv2.resize(im, (mm.shape[1], mm.shape[0]), interpolation=cv2.INTER_AREA)
    mvs_c.append(im[vv, uu, ::-1].astype(np.float64))
mvs_p = np.concatenate(mvs_p) if mvs_p else np.zeros((0, 3))
mvs_c = np.concatenate(mvs_c) if mvs_c else np.zeros((0, 3))
print(f"MVS-measured points (before balancing): {len(mvs_p)}")

# ---- 3. merge, voxel-balance, clean, normals ----
P = np.concatenate([ba_pts, mvs_p]); C = np.concatenate([ba_col, mvs_c])
# drop stray MVS points far outside the room: keep the BA points' 1-99% box plus a 0.5 m margin
lo, hi = np.percentile(ba_pts, 1, axis=0) - 0.5, np.percentile(ba_pts, 99, axis=0) + 0.5
inside = np.all((P >= lo) & (P <= hi), axis=1)
print(f"removed {np.sum(~inside)} points outside the room box")
P, C = P[inside], C[inside]
_, uniq = np.unique(np.floor(P / args.voxel).astype(np.int64), axis=0, return_index=True)
P, C = P[uniq], C[uniq]
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(P)
pcd.colors = o3d.utility.Vector3dVector(np.clip(C / 255.0, 0, 1))
pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=16, std_ratio=2.5)
pcd.estimate_normals(o3d.geometry.KDTreeSearchParamKNN(knn=16))
o3d.io.write_point_cloud(os.path.join(args.work, "init_points.ply"), pcd)
ext = np.asarray(pcd.get_axis_aligned_bounding_box().get_extent())
print(f"init_points.ply: {len(pcd.points)} points ({args.voxel * 1000:.0f} mm voxels), extent (m) {np.round(ext, 2)}")
