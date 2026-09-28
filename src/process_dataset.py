import os
import json
import argparse
import numpy as np
from scipy.spatial.transform import Rotation as R
import cv2

def parse_args():
    parser = argparse.ArgumentParser(description="Extract ARCore data into Nerfstudio format.")
    parser.add_argument("--video", type=str, required=True, help="Path to dataset.mp4")
    parser.add_argument("--csv", type=str, required=True, help="Path to poses.csv")
    parser.add_argument("--points", type=str, default=None, help="Path to points.csv")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory")
    return parser.parse_args()

def export_ply(points_file, output_ply):
    if not points_file or not os.path.exists(points_file): return False
    points = []
    with open(points_file, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 3: points.append([float(parts[0]), float(parts[1]), float(parts[2])])
    if not points: return False
    with open(output_ply, "w") as f:
        f.write(f"ply\nformat ascii 1.0\nelement vertex {len(points)}\nproperty float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n")
        for pt in points: f.write(f"{pt[0]} {pt[1]} {pt[2]} 128 128 128\n")
    return True

def main():
    args = parse_args()
    images_dir = os.path.join(args.output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    # 1. Parse the new rich 12-column CSV
    data = []
    with open(args.csv, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 12: data.append([float(x) for x in parts[:12]])
    data = np.array(data)

    # Normalize pose timestamps to start at 0.0 seconds
    timestamps_nanos = data[:, 0]
    t_poses = (timestamps_nanos - timestamps_nanos[0]) / 1e9 

    tx, ty, tz = data[:, 1], data[:, 2], data[:, 3]
    qx, qy, qz, qw = data[:, 4], data[:, 5], data[:, 6], data[:, 7]
    fl_x_avg = np.mean(data[:, 8])
    fl_y_avg = np.mean(data[:, 9])
    cx_avg = np.mean(data[:, 10])
    cy_avg = np.mean(data[:, 11])

    # 2. Extract Frames via OpenCV & Time-Sync
    cap = cv2.VideoCapture(args.video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0 or np.isnan(fps): fps = 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Target ~350 frames so the optimizer runs fast on your GPU
    step = max(1, total_frames // 350)
    print(f"[Info] Extracting 1 out of every {step} frames from the video...")

    frames_list = []
    frame_idx = 0
    w, h = 0, 0

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        if frame_idx % step == 0:
            h, w, _ = frame.shape
            t_frame = frame_idx / fps # Normalize video time to seconds
            
            # Nearest-Neighbor matching to find the exact pose for this frame's timestamp
            time_diffs = np.abs(t_poses - t_frame)
            best_idx = np.argmin(time_diffs)

            # Build Matrix
            rot_mat = R.from_quat([qx[best_idx], qy[best_idx], qz[best_idx], qw[best_idx]]).as_matrix()
            c2w = np.eye(4)
            c2w[:3, :3] = rot_mat
            c2w[:3, 3] = [tx[best_idx], ty[best_idx], tz[best_idx]]

            # # OpenGL to OpenCV Axis conversion
            # c2w[0:3, 1:3] *= -1

            img_name = f"frame_{frame_idx:05d}.jpg"
            cv2.imwrite(os.path.join(images_dir, img_name), frame)
            
            frames_list.append({"file_path": f"images/{img_name}", "transform_matrix": c2w.tolist()})

        frame_idx += 1
    cap.release()

    # 3. Export Point Cloud
    has_ply = export_ply(args.points, os.path.join(args.output_dir, "points3D.ply"))

    # 4. Write perfectly mapped transforms
    out = {
        "fl_x": fl_x_avg, "fl_y": fl_y_avg, "cx": cx_avg, "cy": cy_avg, 
        "w": w, "h": h, "frames": frames_list
    }
    if has_ply: out["ply_file_path"] = "points3D.ply"

    with open(os.path.join(args.output_dir, "transforms.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"[Success] Mapped {len(frames_list)} frames with True Intrinsics to transforms.json!")

if __name__ == "__main__":
    main()