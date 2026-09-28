import sys
import types
import os
import json
import cv2
import torch
import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation as R
import open3d as o3d

# Fake mmcv module for Windows
mmcv = types.ModuleType('mmcv')
mmcv_utils = types.ModuleType('mmcv.utils')
mmcv_utils.collect_env = lambda: {"OS": "Windows Bypassed"}
sys.modules['mmcv'] = mmcv
sys.modules['mmcv.utils'] = mmcv_utils

# Paths
DATASET_DIR = r"C:\Users\tyb\Documents\University\Sem7\FYP\dataset\roomAttemptSadness"
VIDEO_PATH = os.path.join(DATASET_DIR, "dataset.mp4")
POSES_PATH = os.path.join(DATASET_DIR, "poses.csv")
OUTPUT_PLY = os.path.join(DATASET_DIR, "dense_prior.ply")
FRAMES_OUT_DIR = os.path.join(DATASET_DIR, "images")

# Hyperparameters
FRAME_STEP = 5         # Process every 5th frame for smooth fusion & 3DGS
BLUR_THRESHOLD = 80.0  # Discard smeared frames
DEPTH_MIN = 0.2        # Meters
DEPTH_MAX = 5.0        # Meters
STRIDE = 4             # Pixel step to keep VRAM/RAM balanced

# Load Metric3D ViT-Large
print("Loading Metric3D ViT-Large...")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = torch.hub.load('yvanyin/metric3d', 'metric3d_vit_large', pretrain=True)
model = model.to(device).eval()

# Load ARCore Poses
poses_df = pd.read_csv(POSES_PATH, header=None)
poses = poses_df.values

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print(f"Error: Could not open {VIDEO_PATH}")
    sys.exit()

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
total_poses = len(poses)
limit = min(total_frames, total_poses)

frames_rgb = []
depths_raw_list = []
depths_vis_list = []
valid_pose_indices = []

# --- PASS 1: Fast CPU Filtering ---
print(f"\n--- PASS 1: Fast Filtering {limit} frames ---")
frame_id = 0
frames_rgb = []
valid_pose_indices = []

while cap.isOpened() and frame_id < limit:
    ret, raw_frame = cap.read()
    if not ret:
        break

    # Subsample check
    if frame_id % FRAME_STEP != 0:
        frame_id += 1
        continue

    # Motion blur check
    gray = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    if sharpness >= BLUR_THRESHOLD:
        # Rotate immediately so we store the upright version
        upright = cv2.rotate(raw_frame, cv2.ROTATE_90_CLOCKWISE)
        frames_rgb.append(upright)
        valid_pose_indices.append(frame_id)
        
    frame_id += 1
    
    # Update console every 10 frames to avoid terminal lag
    if frame_id % 10 == 0 or frame_id == limit:
        print(f"\rFiltering: {frame_id}/{limit} | Selected: {len(frames_rgb)}", end="")

cap.release()

total_selected = len(frames_rgb)
print(f"\nPass 1 Complete. Selected {total_selected} sharp keyframes out of {limit}.")

if total_selected == 0:
    print("No frames passed the sharpness filter. Try lowering BLUR_THRESHOLD.")
    sys.exit()


# --- PASS 2: Heavy GPU Inference ---
print(f"\n--- PASS 2: Metric3D Depth Inference ---")
depths_raw_list = []
depths_vis_list = []

mean = np.array([123.675, 116.28, 103.53], dtype=np.float32)
std = np.array([58.395, 57.12, 57.375], dtype=np.float32)

for i, upright in enumerate(frames_rgb):
    orig_frame_id = valid_pose_indices[i]
    h_u, w_u = upright.shape[:2]

    # Model inference
    rgb = cv2.cvtColor(upright, cv2.COLOR_BGR2RGB)
    norm_img = (rgb.astype(np.float32) - mean) / std
    input_tensor = torch.from_numpy(norm_img).permute(2, 0, 1).unsqueeze(0).to(device)

    # Use hardware intrinsics from poses.csv (adjusted for 90-deg CW rotation)
    fx_raw, fy_raw, cx_raw, cy_raw = poses[orig_frame_id, 8:12]
    intrinsic = [fy_raw, fx_raw, h_u - cy_raw, cx_raw]

    with torch.no_grad():
        pred_depth, _, _ = model.inference({'input': input_tensor, 'intrinsic': intrinsic})

    depth_u = pred_depth.squeeze().cpu().to(torch.float32).numpy()
    depth_u = np.nan_to_num(depth_u, nan=0.1, posinf=10.0, neginf=0.1)
    depth_u = cv2.resize(depth_u, (w_u, h_u), interpolation=cv2.INTER_NEAREST)

    # Rotate depth back 90 CCW to match raw sensor space (1920x1080) for unprojection
    depth_sensor = cv2.rotate(depth_u, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # Visualization heatmap (upright)
    vis_clamped = np.clip(depth_u, 0.5, 4.0)
    vis_u = ((vis_clamped - 0.5) / 3.5 * 255.0).astype(np.uint8)
    vis_colored = cv2.applyColorMap(vis_u, cv2.COLORMAP_INFERNO)

    depths_raw_list.append(depth_sensor)
    depths_vis_list.append(vis_colored)

    print(f"\rProcessed: {i+1}/{total_selected} depth maps", end="")

print("\nPass 2 Complete. Opening Viewer...")

# Interactive Reviewer
current_idx = 0
total_selected = len(frames_rgb)
paused = True
window_name = "Metric3D Reviewer - [SPACE]: Play | [A/D]: Skim | [E]: Export Fusion Data | [Q]: Quit"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

h_disp, w_disp = frames_rgb[0].shape[:2]
cv2.resizeWindow(window_name, min(1600, w_disp * 2), min(900, h_disp))

def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and current_idx < total_selected:
        target_x = x % w_disp
        # Sample from the raw depth map
        depth_val = depths_vis_list[current_idx][y, target_x]
        print(f"Frame {valid_pose_indices[current_idx]} | Pixel ({target_x}, {y})")

cv2.setMouseCallback(window_name, on_mouse)

def export_data():
    os.makedirs(FRAMES_OUT_DIR, exist_ok=True)
    all_pts, all_cols = [], []
    frames_meta = []

    print("\nStarting Fusion & Export...")
    for i, orig_idx in enumerate(valid_pose_indices):
        # Save RGB keyframe (upright)
        img_name = f"frame_{i:05d}.png"
        img_path = os.path.join(FRAMES_OUT_DIR, img_name)
        cv2.imwrite(img_path, frames_rgb[i])

        # Pose & Intrinsics
        p = poses[orig_idx]
        tx, ty, tz = p[1:4]
        qx, qy, qz, qw = p[4:8]
        fx, fy, cx, cy = p[8:12]

        depth = depths_raw_list[i]
        H, W = depth.shape

        u, v = np.meshgrid(np.arange(0, W, STRIDE), np.arange(0, H, STRIDE))
        u_f, v_f = u.flatten(), v.flatten()
        z_f = depth[v_f, u_f]

        valid = (z_f > DEPTH_MIN) & (z_f < DEPTH_MAX)
        u_val, v_val, z_val = u_f[valid], v_f[valid], z_f[valid]

        # Camera frame unprojection
        x_cv = (u_val - cx) * z_val / fx
        y_cv = (v_val - cy) * z_val / fy
        cam_pts = np.stack([x_cv, -y_cv, -z_val], axis=-1)

        # World transform
        rot = R.from_quat([qx, qy, qz, qw]).as_matrix()
        world_pts = (rot @ cam_pts.T).T + np.array([tx, ty, tz])

        # Color extraction
        raw_landscape = cv2.rotate(frames_rgb[i], cv2.ROTATE_90_COUNTERCLOCKWISE)
        raw_landscape_rgb = cv2.cvtColor(raw_landscape, cv2.COLOR_BGR2RGB)
        cols = np.ascontiguousarray(raw_landscape_rgb[v_val, u_val] / 255.0, dtype=np.float64)

        all_pts.append(world_pts)
        all_cols.append(cols)

        # 3DGS camera matrix record
        c2w = np.eye(4)
        c2w[:3, :3] = rot
        c2w[:3, 3] = [tx, ty, tz]
        frames_meta.append({
            "file_path": f"images/{img_name}",
            "transform_matrix": c2w.tolist()
        })

    # Save point cloud
    merged_pts = np.vstack(all_pts)
    merged_cols = np.vstack(all_cols)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(merged_pts)
    pcd.colors = o3d.utility.Vector3dVector(merged_cols)
    pcd = pcd.voxel_down_sample(voxel_size=0.02)
    o3d.io.write_point_cloud(OUTPUT_PLY, pcd)

    # Save transforms.json for 3DGS
    fl_x = float(poses[0, 8])
    w_orig = float(depths_raw_list[0].shape[1])
    fov_x = 2 * np.arctan(w_orig / (2 * fl_x))
    meta = {
        "camera_angle_x": float(fov_x),
        "frames": frames_meta
    }
    with open(os.path.join(DATASET_DIR, "transforms.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Export Complete:\n - Point cloud: {OUTPUT_PLY}\n - Images: {FRAMES_OUT_DIR}\n - Meta: transforms.json")

while True:
    combined = np.hstack((frames_rgb[current_idx], depths_vis_list[current_idx]))
    cv2.imshow(window_name, combined)

    if not paused:
        current_idx = (current_idx + 1) % total_selected

    key = cv2.waitKey(30) & 0xFF
    if key == ord('q') or key == 27:
        break
    elif key == 32:
        paused = not paused
    elif key == ord('d'):
        paused = True
        current_idx = min(total_selected - 1, current_idx + 1)
    elif key == ord('a'):
        paused = True
        current_idx = max(0, current_idx - 1)
    elif key == ord('e'):
        export_data()

cv2.destroyAllWindows()