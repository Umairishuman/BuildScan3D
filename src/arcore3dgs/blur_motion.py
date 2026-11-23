"""Per-frame camera motion during the exposure, for motion-blur-aware training in geo_splatfacto.

"Gaussian Splatting on the Move" (Seiskari et al., ECCV 2024) models each phone frame as the average of the
scene rendered along the camera's motion during the exposure, with the motion from the IMU / VIO. Our frames
have a median predicted blur of ~7 px (1/45 s exposure), so a sharp model cannot match them exactly and the
optimiser blurs the splats instead. ARCore poses come at 30 Hz with low local drift, so the camera's angular
and linear velocity at each frame (in its own camera frame, OpenGL axes like nerfstudio) are taken from the
ARCore poses at t -/+ dt. Velocities are clipped (ARCore re-anchors cause pose jumps).

Captures without ARCore tracking (scan_009: ARCore lost, 417 of 622 frames got zero motion, so the blur model did
nothing there) can use the gyroscope instead (FEATURELESS_TRACKING_PLAN 10.f): --gyro_calib <sfm dir> aligns the
gyro to that model's rotations (as rs_rectify.py / rot_sfm.py) and gives the angular velocity; the linear velocity
comes from the model's own camera centres (neighbouring keyframes). --source auto uses ARCore where it has a pose and
the gyro elsewhere. --per_frame_exposure scales each frame's motion by its recorded exposure (camera.csv) over
--exposure, so the trainer's single blur_exposure acts as the real per-frame exposure.

Writes <work>/blur_motion.json: {name: [wx, wy, wz (rad/s), vx, vy, vz (m/s)]} + the exposure used for
the per-frame predicted blur report.

  python src/arcore3dgs/blur_motion.py --work <work_sfm>          (system python: needs ffprobe like prepare.py)
      [--source auto|arcore|gyro --gyro_calib <work_sfm> --bg_json gyro_loop_bias.json --per_frame_exposure]
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
ap.add_argument("--source", default="arcore", choices=["arcore", "gyro", "auto"],
                help="auto: ARCore where it has a pose, the gyro elsewhere (needs --gyro_calib)")
ap.add_argument("--gyro_calib", default=None, help="sfm dir with sparse/0 to align the gyro to (usually --work itself)")
ap.add_argument("--bg_json", default=None, help="gyro bias from gyro_loop_bias.py")
ap.add_argument("--per_frame_exposure", action="store_true", help="scale motion by camera.csv exposure / --exposure")
args = ap.parse_args()
meta = json.load(open(os.path.join(args.work, "frames.json")))
cap = Capture(meta["dataset"], fallback=False)
F_ = np.diag([1.0, -1.0, -1.0])

camrot = None
if args.source in ("gyro", "auto") and args.gyro_calib:
    import rs_rectify
    camrot, _, _ = rs_rectify.setup(meta["dataset"], meta, args.gyro_calib, args.bg_json)
elif args.source == "gyro":
    sys.exit("--source gyro needs --gyro_calib")
fr = sorted(meta["frames"], key=lambda f: f["pts"])
T = np.array([f["pts"] for f in fr]); Cw = np.array([np.array(f["c2w"])[:3, 3] for f in fr])
idx = {f["name"]: k for k, f in enumerate(fr)}
exp_of = None
if args.per_frame_exposure and os.path.exists(os.path.join(meta["dataset"], "camera.csv")):
    Cm = np.genfromtxt(os.path.join(meta["dataset"], "camera.csv"), delimiter=",", skip_header=1); Cm = Cm[Cm[:, 1] > 0]
    exp_of = lambda t: float(np.interp(t, (Cm[:, 0] - cap.t0_ns) / 1e9, Cm[:, 1] / 1e9))


def gyro_motion(f):
    """angular velocity from the gyro, linear velocity from the model's neighbouring keyframes (OpenGL camera frame)"""
    t = f["pts"] + meta.get("pose_offset", 0.0)
    Ra, Rb = camrot(np.array([t - args.dt, t + args.dt]))
    w = F_ @ R.from_matrix(Ra.T @ Rb).as_rotvec() / (2 * args.dt)        # OpenCV camera -> OpenGL axes
    k = idx[f["name"]]; k0, k1 = max(k - 1, 0), min(k + 1, len(fr) - 1)
    v = np.zeros(3)
    if k1 > k0 and T[k1] - T[k0] < 1.0:
        Rgl = np.array(f["c2w"])[:3, :3]                                   # c2w in frames.json: OpenGL camera
        v = Rgl.T @ (Cw[k1] - Cw[k0]) / (T[k1] - T[k0])
    return w, v


out, blur, used = {}, [], {"arcore": 0, "gyro": 0, "none": 0}
for f in meta["frames"]:
    w = v = None; src = "none"
    if args.source in ("arcore", "auto"):
        a, b = cap.pose_at(f["pts"] - args.dt), cap.pose_at(f["pts"] + args.dt)
        if a is not None and b is not None:
            rel = np.linalg.inv(a) @ b                              # motion over 2*dt, in the camera frame at t - dt
            w = R.from_matrix(rel[:3, :3]).as_rotvec() / (2 * args.dt)
            v = rel[:3, 3] / (2 * args.dt); src = "arcore"
    if w is None and camrot is not None:
        w, v = gyro_motion(f); src = "gyro"
    if w is None:
        out[f["name"]] = [0.0] * 6; used["none"] += 1; continue
    if np.linalg.norm(w) > args.max_w or np.linalg.norm(v) > args.max_v:   # pose jump, not motion
        w, v = np.zeros(3), np.zeros(3)
    if exp_of is not None:
        sc = exp_of(f["pts"]) / args.exposure; w, v = w * sc, v * sc
    used[src] += 1
    out[f["name"]] = [round(float(x), 5) for x in np.concatenate([w, v])]
    blur.append(np.linalg.norm(w[:2]) * args.exposure * meta["fx"])
json.dump({"exposure": args.exposure, "motion": out, "source": used, "per_frame_exposure": exp_of is not None},
          open(os.path.join(args.work, "blur_motion.json"), "w"))
blur = np.array(blur)
print(f"{len(out)} frames (motion from ARCore {used['arcore']}, gyro {used['gyro']}, none {used['none']}); "
      f"rotational blur at {1 / args.exposure:.0f}-th s exposure: median {np.median(blur):.1f} px, "
      f"p90 {np.percentile(blur, 90):.1f} px")
