import os
import glob
import json
import argparse
import numpy as np
from scipy.spatial.transform import Rotation as R
import cv2

def parse_args():
    parser = argparse.ArgumentParser(description="Convert ARCore poses and points to Nerfstudio format.")
    parser.add_argument("--csv", type=str, required=True, help="Path to poses.csv")
    parser.add_argument("--points", type=str, default=None, help="Path to points.csv")
    parser.add_argument("--images_dir", type=str, default=None, help="Path to extracted frames")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory for transforms.json and ply")
    return parser.parse_args()

def export_ply(points_file, output_ply):
    """Reads points.csv and writes a basic colored PLY file for Nerfstudio."""
    if not os.path.exists(points_file):
        print(f"Warning: Points file not found at {points_file}. No PLY will be generated.")
        return False

    points = []
    with open(points_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split(',')
                if len(parts) >= 3:
                    points.append([float(parts[0]), float(parts[1]), float(parts[2])])

    if not points:
        print("Warning: points.csv is empty.")
        return False

    with open(output_ply, 'w') as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {len(points)}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("property uchar red\n")
        f.write("property uchar green\n")
        f.write("property uchar blue\n")
        f.write("end_header\n")
        for pt in points:
            f.write(f"{pt[0]} {pt[1]} {pt[2]} 128 128 128\n")
            
    print(f"Successfully exported {len(points)} points to {output_ply}")
    return True

def main():
    args = parse_args()

    csv_path = os.path.abspath(args.csv)
    output_dir = os.path.abspath(args.output_dir)
    images_dir = os.path.abspath(args.images_dir) if args.images_dir else os.path.join(output_dir, "images")
    points_path = os.path.abspath(args.points) if args.points else os.path.join(os.path.dirname(csv_path), "points.csv")

    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Poses CSV not found at: {csv_path}")

    # 1. Export Point Cloud
    ply_filename = "points3D.ply"
    ply_path = os.path.join(output_dir, ply_filename)
    has_ply = export_ply(points_path, ply_path)

    # 2. Load CSV poses
    poses_data = []
    with open(csv_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = [float(x) for x in line.split(",")]
            poses_data.append(parts)

    poses_data = np.array(poses_data)
    if len(poses_data) == 0:
        raise ValueError("The provided CSV file contains no pose records.")

    # 3. Get images
    image_paths = sorted(glob.glob(os.path.join(images_dir, "*.jpg")) + glob.glob(os.path.join(images_dir, "*.png")))
    num_frames = len(image_paths)

    if num_frames == 0:
        raise FileNotFoundError(f"No images found in: {images_dir}")

    sample_img = cv2.imread(image_paths[0])
    height, width, _ = sample_img.shape

    camera_angle_x = 1.0472
    fl_x = 0.5 * width / np.tan(0.5 * camera_angle_x)
    fl_y = fl_x

    # 4. Interpolate poses
    frames_list = []
    csv_indices = np.linspace(0, len(poses_data) - 1, num_frames, dtype=int)

    for i, img_path in enumerate(image_paths):
        row = poses_data[csv_indices[i]]
        tx, ty, tz = row[1:4]
        qx, qy, qz, qw = row[4:8]

        r = R.from_quat([qx, qy, qz, qw])
        rot_mat = r.as_matrix()

        c2w = np.eye(4)
        c2w[:3, :3] = rot_mat
        c2w[:3, 3] = [tx, ty, tz]

        # --- ARCORE TO NERFSTUDIO MATH FIX ---
        # Flip Y and Z axes to fix the divergent rays (converts OpenGL to OpenCV)
        # The rot90 hack has been completely removed!
        c2w[0:3, 1:3] *= -1

        rel_img_path = os.path.relpath(img_path, output_dir).replace("\\", "/")

        frames_list.append({
            "file_path": rel_img_path,
            "transform_matrix": c2w.tolist()
        })

    # 5. Write transforms.json
    output_data = {
        "camera_angle_x": camera_angle_x,
        "fl_x": fl_x,
        "fl_y": fl_y,
        "cx": width / 2.0,
        "cy": height / 2.0,
        "w": width,
        "h": height,
    }
    
    if has_ply:
        output_data["ply_file_path"] = ply_filename

    output_data["frames"] = frames_list

    out_file = os.path.join(output_dir, "transforms.json")
    with open(out_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Successfully generated: {out_file} ({len(frames_list)} frames processed)")

if __name__ == "__main__":
    main()