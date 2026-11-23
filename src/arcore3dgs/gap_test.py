"""Cut-gap test for featureless tracking (FEATURELESS_TRACKING_PLAN step 0 / 3).

On a well-tracked capture whose SfM model is trusted, cut out windows of keyframes (simulated featureless gaps),
predict their camera rotation from the gyroscope chained from the frames outside the gap (both ends: slerp blend,
one end: forward only), and compare with the SfM rotation. The IMU->camera calibration is estimated on the whole
model (gyro_check.check), which is a per-phone constant.

  python src/arcore3dgs/gap_test.py <dataset> <keyframe dir> <COLMAP model dir> [--gaps 2 5 9 15] [--every 20]
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.spatial.transform import Rotation as R

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gyro_check import check, fill_rotations, gyro_rotation, read_images_txt  # noqa: E402
from common import Capture  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("dataset")
ap.add_argument("work")
ap.add_argument("model")
ap.add_argument("--gaps", type=float, nargs="+", default=[2, 5, 9, 15])
ap.add_argument("--every", type=float, default=20.0, help="one gap start every N s of video")
a = ap.parse_args()

meta = json.load(open(os.path.join(a.work, "frames.json")))
rots = read_images_txt(a.model)
rep = check(a.dataset, meta["frames"], rots, Capture(a.dataset).t0_ns, meta.get("pose_offset", 0.0), verbose=True)
imu, Rci, off = rep["imu"], rep["Rci"], rep["off"]
good = [f for f in meta["frames"] if f["name"] in rots and rep["frame_score_deg"].get(f["name"], 99) <= 2.0]
t = np.array([f["pts"] + meta.get("pose_offset", 0.0) for f in good])
Rs = [rots[f["name"]] for f in good]
ang = lambda A, B: float(np.rad2deg(R.from_matrix(A.T @ B).magnitude()))  # noqa: E731

print(f"{'gap s':>6} {'gaps':>5} {'frames':>7} | both ends: median / p90 / max deg | one end (forward): median / p90 / max deg")
for g in a.gaps:
    both, fwd, ngaps = [], [], 0
    for start in np.arange(t[0] + 2, t[-1] - g - 2, a.every):
        inside = (t >= start) & (t < start + g)
        if inside.sum() < 2:
            continue
        ngaps += 1
        known = ~inside
        pred = fill_rotations(imu, Rci, off, t[known], [Rs[i] for i in np.where(known)[0]], t[inside])
        both += [ang(p, Rs[i]) for p, i in zip(pred, np.where(inside)[0])]
        # forward only: chain from the last frame before the gap
        k = np.where(known & (t < start))[0][-1]
        fwd += [ang(gyro_rotation(imu, Rci, off, t[k], Rs[k], t[i]), Rs[i]) for i in np.where(inside)[0]]
    if both:
        q = lambda x: f"{np.median(x):5.2f} / {np.percentile(x, 90):5.2f} / {np.max(x):5.2f}"  # noqa: E731
        print(f"{g:6.1f} {ngaps:5d} {len(both):7d} | {q(both):>28} | {q(fwd):>28}")
