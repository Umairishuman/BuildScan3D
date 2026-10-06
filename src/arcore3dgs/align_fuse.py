"""Stage 2: make monocular depth multi-view consistent.

1. Per-frame scale: Metric3D depth is predicted independently per image, so its scale wanders from
   frame to frame. Each frame is rescaled to the ARCore SLAM feature points visible in it (metric,
   shared world frame). Scales are robustly smoothed over time; frames without enough points
   borrow the smoothed value.
2. TSDF fusion of all rescaled depth maps -> a single watertight-ish surface (averages out per-frame
   errors, removes floaters).
3. The fused mesh is ray-cast back into every keyframe -> depth_fused/*.npy: depth maps that are
   consistent across all views by construction. These supervise 3DGS training.
4. init.ply: points sampled on the fused mesh (with colour) -> Gaussian initialisation.

Run with any python that has open3d (system python or nerfstudio-env).
"""
import os, sys, json, argparse
import numpy as np, cv2, open3d as o3d
from scipy.ndimage import median_filter

sys.path.insert(0, os.path.dirname(__file__))
from common import Capture, project, GL_TO_CV

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--voxel", type=float, default=0.02)
ap.add_argument("--trunc", type=float, default=0.08)
ap.add_argument("--depth_max", type=float, default=5.0)
ap.add_argument("--min_points", type=int, default=15)
ap.add_argument("--init_points", type=int, default=300000)
ap.add_argument("--min_mvs", type=float, default=0.03, help="frames with at least this MVS-measured fraction are trusted")
ap.add_argument("--max_frame_err", type=float, default=0.05, help="drop frames whose depth disagrees more than this with the trusted surface")
ap.add_argument("--depth_dir", default="depth_m3d", help="depth_mvs = metric MVS depth from mvs.py (skips scale alignment)")
args = ap.parse_args()

meta = json.load(open(os.path.join(args.work, "frames.json")))
cap = Capture(meta["dataset"], pose_offset=meta["pose_offset"])
s = meta["depth_scale"]
W, H = int(meta["W"] * s), int(meta["H"] * s)
K = cap.K(s)
frames = meta["frames"]
os.makedirs(os.path.join(args.work, "depth_fused"), exist_ok=True)


def load_depth(f):
    return np.load(os.path.join(args.work, args.depth_dir, f["name"] + ".npy")).astype(np.float32)


def edge_mask(d):
    gx = cv2.Sobel(d, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(d, cv2.CV_32F, 0, 1, ksize=3)
    return np.hypot(gx, gy) / np.maximum(d, 1e-3) > 0.3


# ---------- 1. per-frame scale against ARCore sparse points ----------
if args.depth_dir != "depth_m3d":
    print(f"Step 1: skipped ({args.depth_dir} is already metric)")
    scale = np.ones(len(frames))
else:
    print("Step 1: per-frame scale alignment to ARCore feature points")
    raw_scale, npts = np.full(len(frames), np.nan), np.zeros(len(frames), int)
    for i, f in enumerate(frames):
        d = load_depth(f)
        P = cap.sparse_points_near(f["pts"], window=0.5)
        if len(P) == 0:
            continue
        u, v, z, m = project(P, np.array(f["c2w"]), K, W, H)
        if m.sum() < args.min_points:
            continue
        zm = d[v[m].astype(int), u[m].astype(int)]
        ok = (zm > 0.1) & (zm < args.depth_max)
        r = z[m][ok] / zm[ok]
        if len(r) < args.min_points:
            continue
        # reject occluded / mismatched points: keep ratios near the median, then re-estimate
        med = np.median(r)
        r = r[np.abs(np.log(r / med)) < 0.25]
        if len(r) >= args.min_points:
            raw_scale[i], npts[i] = np.median(r), len(r)

    valid = ~np.isnan(raw_scale)
    print(f"  frames with enough ARCore points: {valid.sum()}/{len(frames)} (median {np.median(npts[valid]):.0f} pts)")
    rs = raw_scale[valid]
    print(f"  raw Metric3D->ARCore scale: median {np.median(rs):.3f}, p5 {np.percentile(rs, 5):.3f}, "
          f"p95 {np.percentile(rs, 95):.3f}  (spread = per-frame scale inconsistency)")

    # temporal smoothing + fill
    idx = np.arange(len(frames))
    filled = np.interp(idx, idx[valid], raw_scale[valid])
    scale = median_filter(filled, size=9, mode="nearest")
    print(f"  smoothed scale range: {scale.min():.3f} .. {scale.max():.3f}")


# ---------- 2. TSDF fusion (two-pass when MVS masks exist) ----------
intr = o3d.camera.PinholeCameraIntrinsic(W, H, K[0, 0], K[1, 1], K[0, 2], K[1, 2])
uu, vv = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5)
dirs_cam = np.stack([(uu - K[0, 2]) / K[0, 0], (vv - K[1, 2]) / K[1, 1], np.ones_like(uu)], -1).reshape(-1, 3)


def w2c_cv(c2w_gl):
    c2w = np.array(c2w_gl).copy()
    c2w[:3, :3] = c2w[:3, :3] @ GL_TO_CV
    return np.linalg.inv(c2w)


def fuse(items):
    """items: list of (frame_index, depth). Returns cleaned mesh."""
    vol = o3d.pipelines.integration.ScalableTSDFVolume(
        voxel_length=args.voxel, sdf_trunc=args.trunc, color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8)
    for n, (i, d) in enumerate(items):
        d = d.copy()
        d[edge_mask(d) | (d > args.depth_max)] = 0
        img = cv2.cvtColor(cv2.resize(cv2.imread(os.path.join(args.work, "images", frames[i]["name"] + ".jpg")), (W, H),
                                      interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
        rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
            o3d.geometry.Image(img), o3d.geometry.Image(d.astype(np.float32)),
            depth_scale=1.0, depth_trunc=args.depth_max, convert_rgb_to_intensity=False)
        vol.integrate(rgbd, intr, w2c_cv(frames[i]["c2w"]))
    m = vol.extract_triangle_mesh()
    cl, n_tri, _ = m.cluster_connected_triangles()          # drop small disconnected blobs
    cl, n_tri = np.asarray(cl), np.asarray(n_tri)
    m.remove_triangles_by_mask(n_tri[cl] < 500)
    m.remove_unreferenced_vertices()
    m.compute_vertex_normals()
    return m


def raycaster(m):
    sc = o3d.t.geometry.RaycastingScene()
    sc.add_triangles(o3d.t.geometry.TriangleMesh.from_legacy(m))
    def cast(i):
        c2w = np.linalg.inv(w2c_cv(frames[i]["c2w"]))
        dirs = dirs_cam @ c2w[:3, :3].T                      # z_cam = 1 -> t_hit is OpenCV depth
        rays = np.concatenate([np.broadcast_to(c2w[:3, 3], dirs.shape), dirs], 1).astype(np.float32)
        t = sc.cast_rays(o3d.core.Tensor(rays))["t_hit"].numpy().reshape(H, W)
        t[~np.isfinite(t)] = 0
        return t
    return cast


def smooth_fit(d, t, m):
    """Fit log(t/d) ~ quadratic(u, v) on mask m (robust), return corrected d."""
    un, vn = uu / W - 0.5, vv / H - 0.5
    B = lambda k: np.stack([np.ones(k.sum()), un[k], vn[k], un[k] ** 2, vn[k] ** 2, un[k] * vn[k]], 1)
    y = np.log(t[m] / d[m]); A = B(m); sel = np.ones(len(y), bool)
    for _ in range(3):
        coef = np.linalg.lstsq(A[sel], y[sel], rcond=None)[0]
        r = A @ coef - y
        sel = np.abs(r) < 3 * max(np.median(np.abs(r[sel])), 1e-3)
    full = np.ones_like(m)
    return (d * np.exp((B(full) @ coef).reshape(H, W))).astype(np.float32)


depths = {i: load_depth(f) * scale[i] for i, f in enumerate(frames)}
mask_dir = os.path.join(args.work, "mvs_mask")
if args.depth_dir != "depth_m3d" and os.path.isdir(mask_dir):
    mvs_frac = np.array([np.load(os.path.join(mask_dir, f["name"] + ".npy")).mean() for f in frames])
    reliable = mvs_frac >= args.min_mvs
    print(f"Step 2a: fusing {reliable.sum()} frames with >= {args.min_mvs * 100:.0f}% MVS-measured depth")
    mesh_a = fuse([(i, depths[i]) for i in np.where(reliable)[0]])
    cast_a = raycaster(mesh_a)
    print(f"Step 2b: checking every frame against the trusted surface ({len(mesh_a.triangles)} tris)")
    accepted, n_fixed, n_drop = [], 0, 0
    for i in range(len(frames)):
        t = cast_a(i); d = depths[i]
        m = (t > 0) & (d > 0) & (d < args.depth_max)
        cov = m.mean()
        if not reliable[i] and cov > 0.2:
            d = smooth_fit(d, t, m)                             # re-anchor unmeasured depth to trusted surface
            n_fixed += 1
        err = np.median(np.abs(d[m] - t[m]) / t[m]) if m.sum() > 1000 else (0.0 if reliable[i] else 1.0)
        frames[i]["fuse_err"] = float(err)
        if err < args.max_frame_err and (reliable[i] or cov > 0.2):
            depths[i] = d
            accepted.append(i)
        else:
            n_drop += 1
    frames_dropped = sorted(set(range(len(frames))) - set(accepted))
    meta["fusion_dropped"] = [frames[i]["name"] for i in frames_dropped]
    print(f"  re-anchored {n_fixed} unmeasured frames; dropped {n_drop} inconsistent frames from fusion")
    print(f"Step 2c: final fusion of {len(accepted)} frames")
    mesh = fuse([(i, depths[i]) for i in accepted])
else:
    print("Step 2: TSDF fusion")
    mesh = fuse(list(depths.items()))
o3d.io.write_triangle_mesh(os.path.join(args.work, "fused_mesh.ply"), mesh)
bb = mesh.get_axis_aligned_bounding_box().get_extent()
print(f"  mesh: {len(mesh.triangles)} tris, extent (m) {np.round(bb, 2)}")

# ---------- 3. ray-cast fused depth into each view + consistency report ----------
print("Step 3: rendering fused depth per keyframe")
cast = raycaster(mesh)
rel_err = []
for i, f in enumerate(frames):
    t = cast(i)
    np.save(os.path.join(args.work, "depth_fused", f["name"] + ".npy"), t.astype(np.float16))
    d = depths[i]
    m = (t > 0) & (d > 0) & (d < args.depth_max)
    if m.sum() > 1000:
        rel_err.append(np.median(np.abs(d[m] - t[m]) / t[m]))
    f["scale"] = float(scale[i])
    f["fused_coverage"] = float((t > 0).mean())
rel_err = np.array(rel_err)
print(f"  per-frame depth vs fused depth, median rel. error: {np.median(rel_err) * 100:.1f}% "
      f"(p90 {np.percentile(rel_err, 90) * 100:.1f}%)")

# ---------- 4. init point cloud ----------
pcd = mesh.sample_points_uniformly(number_of_points=args.init_points)
o3d.io.write_point_cloud(os.path.join(args.work, "init.ply"), pcd)
json.dump(meta, open(os.path.join(args.work, "frames.json"), "w"), indent=1)
print(f"Done. init.ply ({len(pcd.points)} pts), fused depth for {len(frames)} frames.")
