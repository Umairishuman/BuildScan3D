"""Per-frame camera motion during the exposure, for motion-blur-aware training in geo_splatfacto.

"Gaussian Splatting on the Move" (Seiskari et al., ECCV 2024) models each phone frame as the average of the
scene rendered along the camera's motion during the exposure, with the motion from the IMU / VIO. Our frames
have a median predicted blur of ~7 px (1/45 s exposure), so a sharp model cannot match them exactly and the
optimiser blurs the splats instead. ARCore poses come at 30 Hz with low local drift, so the camera's angular
and linear velocity at each frame (in its own camera frame, OpenGL axes like nerfstudio) are taken from the
ARCore poses at t -/+ dt. Velocities are clipped (ARCore re-anchors cause pose jumps).

Writes <work>/blur_motion.json: {name: [wx, wy, wz (rad/s), vx, vy, vz (m/s)]} + the exposure used for
the per-frame predicted blur report.

  python src/arcore3dgs/blur_motion.py --work <work_sfm>          (system python: needs ffprobe like prepare.py)
"""
import os, sys, json, argparse
import numpy as np
from scipy.spatial.transform import Rotation as R

sys.path.insert(0, os.path.dirname(__file__))
from common import Capture

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--dt", type=float, default=0.034, help="half-window (s) for the finite difference")
ap.add_argument("--max_w", type=float, default=3.0); ap.add_argument("--max_v", type=float, default=1.5)
ap.add_argument("--exposure", type=float, default=1 / 45)
args = ap.parse_args()
meta = json.load(open(os.path.join(args.work, "frames.json")))
cap = Capture(meta["dataset"], fallback=False)
out, blur = {}, []
for f in meta["frames"]:
    a, b = cap.pose_at(f["pts"] - args.dt), cap.pose_at(f["pts"] + args.dt)
    if a is None or b is None:
        out[f["name"]] = [0.0] * 6; continue
    rel = np.linalg.inv(a) @ b                                  # motion over 2*dt, in the camera frame at t - dt
    w = R.from_matrix(rel[:3, :3]).as_rotvec() / (2 * args.dt)
    v = rel[:3, 3] / (2 * args.dt)
    if np.linalg.norm(w) > args.max_w or np.linalg.norm(v) > args.max_v:   # ARCore jump, not motion
        w, v = np.zeros(3), np.zeros(3)
    out[f["name"]] = [round(float(x), 5) for x in np.concatenate([w, v])]
    blur.append(np.linalg.norm(w[:2]) * args.exposure * meta["fx"])
json.dump({"exposure": args.exposure, "motion": out}, open(os.path.join(args.work, "blur_motion.json"), "w"))
blur = np.array(blur)
print(f"{len(out)} frames; rotational blur at {1 / args.exposure:.0f}-th s exposure: median {np.median(blur):.1f} px, "
      f"p90 {np.percentile(blur, 90):.1f} px")
