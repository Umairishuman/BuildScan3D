import sys
import types
import os
import cv2
import torch
import numpy as np
import pandas as pd
import subprocess
from scipy.spatial.transform import Rotation as R, Slerp
import open3d as o3d

# 1. Fake the mmcv module to bypass Windows C++ compilation
mmcv = types.ModuleType('mmcv')
mmcv_utils = types.ModuleType('mmcv.utils')
mmcv_utils.collect_env = lambda: {"OS": "Windows Bypassed"}
sys.modules['mmcv'] = mmcv
sys.modules['mmcv.utils'] = mmcv_utils

# --- CONFIGURATION ---
DATASET_DIR = r"C:\Users\tyb\Documents\University\Sem7\FYP\dataset\roomAttemptSadness"
VIDEO_PATH = os.path.join(DATASET_DIR, "dataset.mp4")
POSES_PATH = os.path.join(DATASET_DIR, "poses.csv")
OUTPUT_PLY = os.path.join(DATASET_DIR, "dense_prior.ply")

BLUR_THRESHOLD = 100.0  # Increase if you want stricter sharpness filtering
FRAME_SKIP = 10         # Process 1 frame every X frames (e.g., 6 fps from a 60fps video)
DEPTH_MIN = 0.2         # Ignore pixels closer than 20cm
DEPTH_MAX = 5.0         # Ignore pixels further than 5 meters (prevents sky/window artifacts)
POSE_OFFSET = 0.0       # seconds: pose_time = video_pts + POSE_OFFSET (measured ~0.0 +/- 0.05s for roomAttemptSadness)
MAX_POSE_GAP = 0.12     # skip frames that fall inside a longer hole in poses.csv (tracking lost)
PIXEL_STRIDE = 4        # Sample every 4th pixel to prevent RAM explosion (16GB safe)
# ---------------------

print("Loading Metric3D ViT-Large...")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = torch.hub.load('yvanyin/metric3d', 'metric3d_vit_large', pretrain=True)
model = model.to(device).eval()

print(f"Loading ARCore poses from {POSES_PATH}...")
poses = pd.read_csv(POSES_PATH, header=None).values
# ARCore can log out-of-order / duplicate timestamps: sort and drop duplicates.
poses = poses[np.argsort(poses[:, 0], kind="stable")]
poses = poses[np.unique(poses[:, 0], return_index=True)[1]]
t_poses = (poses[:, 0] - poses[0, 0]) / 1e9          # seconds, 0 = first logged pose
slerp = Slerp(t_poses, R.from_quat(poses[:, 4:8]))
print(f"{len(poses)} poses spanning {t_poses[-1]:.1f}s")

def pose_at(t):
    """Interpolated (position, quaternion xyzw, intrinsics) at time t, or None if t is in a tracking hole."""
    if t < t_poses[0] or t > t_poses[-1]:
        return None
    i = np.searchsorted(t_poses, t, side="right")
    i0, i1 = max(i - 1, 0), min(i, len(t_poses) - 1)
    if t_poses[i1] - t_poses[i0] > MAX_POSE_GAP:
        return None
    a = 0.0 if i0 == i1 else (t - t_poses[i0]) / (t_poses[i1] - t_poses[i0])
    pos = (1 - a) * poses[i0, 1:4] + a * poses[i1, 1:4]
    quat = slerp([t]).as_quat()[0]
    return pos, quat, poses[i0, 8:12]

# Per-frame presentation timestamps of the 1080p video track (frame index != pose row index!)
pts = np.sort(np.array(subprocess.check_output(
    ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time",
     "-of", "csv=p=0", VIDEO_PATH]).split(), dtype=np.float64))

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print(f"Error: Could not open video at {VIDEO_PATH}")
    sys.exit()

total_frames = min(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), len(pts))
print(f"Video frames: {total_frames}, poses: {len(poses)} (matched by timestamp, not index)")

global_points = []
global_colors = []

frame_idx = 0
processed_count = 0

while cap.isOpened() and frame_idx < total_frames:
    ret, raw_frame = cap.read()
    if not ret:
        break
        
    # Check if we should skip this frame based on our pacing
    if frame_idx % FRAME_SKIP != 0:
        frame_idx += 1
        continue
        
    # Blur Detection (Laplacian Variance)
    gray = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    if sharpness < BLUR_THRESHOLD:
        print(f"Frame {frame_idx:04d} | SKIPPED (Blurry: {sharpness:.1f})")
        frame_idx += 1
        continue
        
    print(f"Frame {frame_idx:04d} | Processing (Sharpness: {sharpness:.1f})...")
    
    # Extract ARCore Telemetry for this exact frame
    interp = pose_at(pts[frame_idx] + POSE_OFFSET)
    if interp is None:
        print(f"Frame {frame_idx:04d} | SKIPPED (no pose at t={pts[frame_idx]:.2f}s)")
        frame_idx += 1
        continue
    (tx, ty, tz), (qx, qy, qz, qw), (fx, fy, cx, cy) = interp
    
    # 1. Rotate CW to make the image upright for Metric3D
    rgb_upright = cv2.rotate(raw_frame, cv2.ROTATE_90_CLOCKWISE)
    
    # 2. Metric3D Inference
    rgb_tensor = cv2.cvtColor(rgb_upright, cv2.COLOR_BGR2RGB)
    h_up, w_up = rgb_tensor.shape[:2]
    
    mean = np.array([123.675, 116.28, 103.53], dtype=np.float32)
    std = np.array([58.395, 57.12, 57.375], dtype=np.float32)
    norm_img = (rgb_tensor.astype(np.float32) - mean) / std
    
    input_tensor = torch.from_numpy(norm_img).permute(2, 0, 1).unsqueeze(0).to(device)
    intrinsic_approx = [1000.0, 1000.0, w_up / 2, h_up / 2]
    
    with torch.no_grad():
        pred_depth, _, _ = model.inference({'input': input_tensor, 'intrinsic': intrinsic_approx})
        
    depth_upright = pred_depth.squeeze().cpu().to(torch.float32).numpy()
    depth_upright = cv2.resize(depth_upright, (w_up, h_up), interpolation=cv2.INTER_NEAREST)
    
    # 3. Rotate Depth Map CCW back to the raw sensor orientation to match poses.csv
    depth_raw = cv2.rotate(depth_upright, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
    # 4. Generate Pixel Grid (Applying Memory Stride)
    H, W = depth_raw.shape
    u, v = np.meshgrid(np.arange(0, W, PIXEL_STRIDE), np.arange(0, H, PIXEL_STRIDE))
    
    # Flatten arrays for vectorized math
    u_flat = u.flatten()
    v_flat = v.flatten()
    z_flat = depth_raw[v_flat, u_flat]
    
    # 5. Filter Invalid Depth
    valid = (z_flat > DEPTH_MIN) & (z_flat < DEPTH_MAX)
    u_valid = u_flat[valid]
    v_valid = v_flat[valid]
    z_cv = z_flat[valid]
    
    if len(z_cv) == 0:
        frame_idx += 1
        continue
        
    # 6. Unproject to OpenCV Camera Space (using ARCore intrinsics)
    x_cv = (u_valid - cx) * z_cv / fx
    y_cv = (v_valid - cy) * z_cv / fy
    
    # 7. Convert to ARCore OpenGL Camera Space (Y down -> Y up, Z forward -> Z back)
    camera_points = np.stack([x_cv, -y_cv, -z_cv], axis=-1)
    
    # 8. Transform to Absolute World Space
    rot_matrix = R.from_quat([qx, qy, qz, qw]).as_matrix()
    world_points = (rot_matrix @ camera_points.T).T + np.array([tx, ty, tz])
    
    # 9. Extract Colors
    colors = raw_frame[v_valid, u_valid]
    colors = cv2.cvtColor(colors, cv2.COLOR_BGR2RGB) / 255.0
    
    global_points.append(world_points)
    global_colors.append(colors)
    
    processed_count += 1
    frame_idx += 1

cap.release()

if len(global_points) == 0:
    print("No valid points generated. Check depth thresholds or dataset.")
    sys.exit()

# 10. Merge and Export
print(f"\nMerging {processed_count} frames into global point cloud...")
all_points = np.vstack(global_points)
all_colors = np.vstack(global_colors)

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(all_points)
pcd.colors = o3d.utility.Vector3dVector(all_colors)

print(f"Raw Point Count: {len(all_points)}")
print("Voxel downsampling to clean noise and reduce size...")
pcd = pcd.voxel_down_sample(voxel_size=0.02) # 2cm physical voxels
print(f"Final Point Count: {len(pcd.points)}")

o3d.io.write_point_cloud(OUTPUT_PLY, pcd)
print(f"Success! Saved dense prior to: {OUTPUT_PLY}")