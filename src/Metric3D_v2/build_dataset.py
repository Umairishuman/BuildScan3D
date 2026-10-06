"""
ARCore recording -> metric-scaled Nerfstudio dataset (images/, transforms.json, dense_prior.ply).

Fixes vs fusion_pipeline.py / interactive_viewer.py:
  * Poses are matched to frames by TIMESTAMP (video PTS vs ARCore frame timestamp), interpolated.
    Index matching drifts by up to ~2s because poses are only logged while TRACKING.
  * Metric3D hub model returns depth in a *canonical* camera space (f=1000). Input must be resized
    to fit 616x1064 and the output multiplied by (fx * resize_scale / 1000) to become metric.
  * Everything stays in the raw landscape sensor frame, which is what camera.getPose() refers to
    (verified by correlating pose angular velocity with video optical flow). No rotation needed,
    transforms.json uses the raw 1920x1080 images + raw intrinsics + ARCore OpenGL c2w.
"""
import sys, types, os, json, subprocess, argparse
import cv2, torch, numpy as np, pandas as pd
import open3d as o3d
from scipy.spatial.transform import Rotation as R, Slerp

mmcv = types.ModuleType('mmcv'); mmcv_utils = types.ModuleType('mmcv.utils')
mmcv_utils.collect_env = lambda: {"OS": "Windows Bypassed"}
sys.modules['mmcv'] = mmcv; sys.modules['mmcv.utils'] = mmcv_utils

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", default=r"C:\Users\tyb\Documents\University\Sem7\FYP\dataset\roomAttemptSadness")
ap.add_argument("--out", default=None, help="default: <dataset>/nerf")
ap.add_argument("--frame_step", type=int, default=8)
ap.add_argument("--blur_threshold", type=float, default=80.0)
ap.add_argument("--pose_offset", type=float, default=0.0, help="pose_time = video_pts + offset (s)")
ap.add_argument("--max_pose_gap", type=float, default=0.12)
ap.add_argument("--depth_min", type=float, default=0.2)
ap.add_argument("--depth_max", type=float, default=6.0)
ap.add_argument("--stride", type=int, default=4)
ap.add_argument("--max_frames", type=int, default=0, help="debug: stop after N selected frames")
args = ap.parse_args()

OUT = args.out or os.path.join(args.dataset, "nerf")
IMG_DIR = os.path.join(OUT, "images"); os.makedirs(IMG_DIR, exist_ok=True)
VIDEO = os.path.join(args.dataset, "dataset.mp4")

# ---------- poses ----------
poses = pd.read_csv(os.path.join(args.dataset, "poses.csv"), header=None).values
poses = poses[np.argsort(poses[:, 0], kind="stable")]
poses = poses[np.unique(poses[:, 0], return_index=True)[1]]
t_poses = (poses[:, 0] - poses[0, 0]) / 1e9
slerp = Slerp(t_poses, R.from_quat(poses[:, 4:8]))
FX, FY, CX, CY = poses[:, 8:12].mean(0)
print(f"{len(poses)} poses over {t_poses[-1]:.1f}s | intrinsics fx={FX:.1f} fy={FY:.1f} cx={CX:.1f} cy={CY:.1f}")

def pose_at(t):
    if t < t_poses[0] or t > t_poses[-1]: return None
    i = np.searchsorted(t_poses, t, side="right")
    i0, i1 = max(i - 1, 0), min(i, len(t_poses) - 1)
    if t_poses[i1] - t_poses[i0] > args.max_pose_gap: return None
    a = 0.0 if i0 == i1 else (t - t_poses[i0]) / (t_poses[i1] - t_poses[i0])
    pos = (1 - a) * poses[i0, 1:4] + a * poses[i1, 1:4]
    return pos, slerp([t]).as_matrix()[0]

pts = np.sort(np.array(subprocess.check_output(
    ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time",
     "-of", "csv=p=0", VIDEO]).split(), dtype=np.float64))

# ---------- model ----------
print("Loading Metric3D ViT-Large...")
dev = torch.device("cuda")
model = torch.hub.load('yvanyin/metric3d', 'metric3d_vit_large', pretrain=True).to(dev).eval()
INPUT = (616, 1064)
MEAN = torch.tensor([123.675, 116.28, 103.53], device=dev).view(1, 3, 1, 1)
STD = torch.tensor([58.395, 57.12, 57.375], device=dev).view(1, 3, 1, 1)

@torch.no_grad()
def metric_depth(bgr, fx):
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    h, w = rgb.shape[:2]
    s = min(INPUT[0] / h, INPUT[1] / w)
    rgb = cv2.resize(rgb, (int(w * s), int(h * s)), interpolation=cv2.INTER_LINEAR)
    ph, pw = INPUT[0] - rgb.shape[0], INPUT[1] - rgb.shape[1]
    pad = [ph // 2, ph - ph // 2, pw // 2, pw - pw // 2]
    rgb = cv2.copyMakeBorder(rgb, pad[0], pad[1], pad[2], pad[3], cv2.BORDER_CONSTANT, value=[123.675, 116.28, 103.53])
    x = torch.from_numpy(rgb.transpose(2, 0, 1)).float().to(dev)[None]
    x = (x - MEAN) / STD
    d, _, _ = model.inference({'input': x})
    d = d.squeeze()[pad[0]:INPUT[0] - pad[1], pad[2]:INPUT[1] - pad[3]]
    d = torch.nn.functional.interpolate(d[None, None], (h, w), mode='bilinear').squeeze()
    d = d * (fx * s / 1000.0)            # canonical -> metric
    return torch.clamp(d, 0, 300).float().cpu().numpy()

# ---------- main loop ----------
cap = cv2.VideoCapture(VIDEO)
n_total = min(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), len(pts))
all_pts, all_cols, frames_meta = [], [], []
skipped_blur = skipped_pose = 0
k = 0
while k < n_total:
    ok, frame = cap.read()
    if not ok: break
    if k % args.frame_step:
        k += 1; continue
    sharp = cv2.Laplacian(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
    if sharp < args.blur_threshold:
        skipped_blur += 1; k += 1; continue
    pz = pose_at(pts[k] + args.pose_offset)
    if pz is None:
        skipped_pose += 1; k += 1; continue
    pos, rot = pz
    H, W = frame.shape[:2]

    depth = metric_depth(frame, FX)
    # drop flying pixels at depth discontinuities
    gx = cv2.Sobel(depth, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(depth, cv2.CV_32F, 0, 1, ksize=3)
    edge = np.hypot(gx, gy) / np.maximum(depth, 1e-3) > 0.5
    u, v = np.meshgrid(np.arange(0, W, args.stride), np.arange(0, H, args.stride))
    u, v = u.ravel(), v.ravel()
    z = depth[v, u]
    m = (z > args.depth_min) & (z < args.depth_max) & ~edge[v, u]
    u, v, z = u[m], v[m], z[m]
    cam = np.stack([(u - CX) * z / FX, -(v - CY) * z / FY, -z], -1)   # OpenCV px -> ARCore/OpenGL camera
    all_pts.append((rot @ cam.T).T + pos)
    all_cols.append(cv2.cvtColor(frame[v, u].reshape(-1, 1, 3), cv2.COLOR_BGR2RGB).reshape(-1, 3) / 255.0)

    name = f"frame_{k:05d}.jpg"
    cv2.imwrite(os.path.join(IMG_DIR, name), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
    c2w = np.eye(4); c2w[:3, :3] = rot; c2w[:3, 3] = pos
    frames_meta.append({"file_path": f"images/{name}", "transform_matrix": c2w.tolist()})
    print(f"frame {k:04d} t={pts[k]:.2f}s sharp={sharp:.0f} median depth={np.median(z):.2f}m  [{len(frames_meta)} kept]", flush=True)
    if args.max_frames and len(frames_meta) >= args.max_frames: break
    k += 1
cap.release()
print(f"Kept {len(frames_meta)} frames | skipped blurry={skipped_blur} no-pose={skipped_pose}")

P = np.vstack(all_pts); C = np.vstack(all_cols)
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(P); pcd.colors = o3d.utility.Vector3dVector(C)
pcd = pcd.voxel_down_sample(0.02)
pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
o3d.io.write_point_cloud(os.path.join(OUT, "dense_prior.ply"), pcd)
bb = pcd.get_axis_aligned_bounding_box()
print(f"dense_prior.ply: {len(pcd.points)} pts, extent (m) = {np.round(bb.get_extent(), 2)}")

meta = {"camera_model": "OPENCV", "fl_x": float(FX), "fl_y": float(FY), "cx": float(CX), "cy": float(CY),
        "w": int(W), "h": int(H), "k1": 0.0, "k2": 0.0, "p1": 0.0, "p2": 0.0,
        "ply_file_path": "dense_prior.ply", "frames": frames_meta}
json.dump(meta, open(os.path.join(OUT, "transforms.json"), "w"), indent=2)
print("Wrote", os.path.join(OUT, "transforms.json"))
