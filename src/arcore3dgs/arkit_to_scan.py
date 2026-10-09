"""Convert one ARKitScenes raw video (vga_wide + vga_wide_intrinsics + lowres_wide.traj) into the folder
layout the pipeline reads (poses.csv + frames/ + pts.txt), with a +Y-up world like ARCore.

    py -3.13 arkit_to_scan.py <.../raw/Training/<video_id>> <out_dir>

Conventions (from Apple's tenFpsDataLoader.TrajStringToMatrix): traj = world->camera (axis-angle, translation),
camera axes OpenCV (x right, y down, z forward). The pipeline wants camera->world, OpenGL axes
(x right, y up, -z forward), world +Y up, metres.
"""
import os, sys, glob
import numpy as np, cv2
from scipy.spatial.transform import Rotation as R

src, out = sys.argv[1], sys.argv[2]
vid = os.path.basename(os.path.normpath(src))
os.makedirs(os.path.join(out, "frames"), exist_ok=True)

# ---- poses ----
T = np.loadtxt(os.path.join(src, "lowres_wide.traj"))
w2c = np.tile(np.eye(4), (len(T), 1, 1))
w2c[:, :3, :3] = R.from_rotvec(T[:, 1:4]).as_matrix()
w2c[:, :3, 3] = T[:, 4:7]
c2w_cv = np.linalg.inv(w2c)

# world up = the direction perpendicular to all camera x-axes (handheld cameras barely roll);
# sign: image-up (= -y in OpenCV) should point up on average.
X = c2w_cv[:, :3, 0]
up = np.linalg.svd(X, full_matrices=False)[2][-1]
if (-c2w_cv[:, :3, 1] @ up).mean() < 0:
    up = -up
print("estimated world up (source frame):", np.round(up, 3))
# rotation taking `up` to +Y
v = np.cross(up, [0, 1, 0]); s = np.linalg.norm(v); c = float(up @ [0, 1, 0])
if s < 1e-8:
    Rup = np.eye(3) if c > 0 else np.diag([1, -1, -1.0])
else:
    k = v / s
    Kx = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    Rup = np.eye(3) + s * Kx + (1 - c) * Kx @ Kx
W = np.eye(4); W[:3, :3] = Rup
GL = np.diag([1.0, -1.0, -1.0, 1.0])
c2w_gl = np.array([W @ m @ GL for m in c2w_cv])
print("camera heights (new Y) min/median/max:", np.round(np.percentile(c2w_gl[:, 1, 3], [0, 50, 100]), 2))

# ---- intrinsics (constant to ~1 px; average) ----
files = sorted(glob.glob(os.path.join(src, "vga_wide", "*.png")))
ts = np.array([float(os.path.basename(f)[:-4].split("_")[-1]) for f in files])
intr = np.mean([np.loadtxt(f) for f in sorted(glob.glob(os.path.join(src, "vga_wide_intrinsics", "*.pincam")))], axis=0)
_, _, fx, fy, cx, cy = intr
print(f"{len(files)} frames, {intr[0]:.0f}x{intr[1]:.0f}, fx {fx:.1f} fy {fy:.1f} cx {cx:.1f} cy {cy:.1f}")

t0 = T[0, 0]
with open(os.path.join(out, "poses.csv"), "w") as f:
    for i in range(len(T)):
        q = R.from_matrix(c2w_gl[i, :3, :3]).as_quat()                 # x y z w
        p = c2w_gl[i, :3, 3]
        f.write(f"{T[i, 0] * 1e9:.0f},{p[0]:.6f},{p[1]:.6f},{p[2]:.6f},{q[0]:.7f},{q[1]:.7f},{q[2]:.7f},{q[3]:.7f},"
                f"{fx:.4f},{fy:.4f},{cx:.4f},{cy:.4f}\n")
np.savetxt(os.path.join(out, "pts.txt"), ts - t0, fmt="%.4f")          # frame times in the same clock as poses.csv

for i, fpath in enumerate(files):
    cv2.imwrite(os.path.join(out, "frames", f"{i:06d}.jpg"), cv2.imread(fpath), [cv2.IMWRITE_JPEG_QUALITY, 98])
    if i % 300 == 0:
        print("  frames", i, flush=True)
open(os.path.join(out, "meta.json"), "w").write(f'{{"source": "ARKitScenes raw {vid}", "note": "converted, no video file"}}\n')
print("done ->", out, "| pose rows", len(T), "| frames", len(files))
