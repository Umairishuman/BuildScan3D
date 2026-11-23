"""Reject image pairs whose matches contradict the gyroscope (wrong matches between look-alike places).

FEATURELESS_TRACKING_PLAN, found on scan_009 (R-046 / R-048): both COLMAP mappers built locally wrong models, most
likely from matches between different but similar-looking places (repeated cabinet doors, plain walls). The phone's
gyroscope knows how the camera turned between any two moments. With that relative rotation R fixed, a correct pair's
matches must agree on one translation direction t (epipolar constraint b2 . (t x R b1) = 0, linear in t, two matches
fix it); for a pair of different places they do not. Per pair: 2-point RANSAC for t, inlier ratio under the gyro
rotation. The gyro error grows slowly with the time between the frames, so the threshold grows with it.

The orientation is integrated ONCE over the whole video (400 Hz), so any pair's rotation is a lookup.

  python src/arcore3dgs/gyro_pairs.py <dataset> <keyframe dir> <sfm dir with database.db + sparse/0>
      [--write <new sfm dir>] [--min_ratio 0.5]
--write copies database.db into the new folder and deletes the rejected pairs from two_view_geometries (the mapper
input); without it, only statistics are printed.
"""
import argparse
import json
import os
import shutil
import sqlite3
import sys

import numpy as np
from scipy.spatial.transform import Rotation as R

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from known_rot_pnp import bearings, load_model  # noqa: E402

PAIR = 2147483647
F = np.diag([1.0, -1.0, -1.0])


class Orientation:
    """IMU body orientation Q(t) (IMU frame -> start frame) integrated once over the whole capture."""

    def __init__(self, imu, off, t0, t1, rate=400.0, bg=None):
        self.tt = np.arange(t0, t1 + 1 / rate, 1 / rate)
        w = imu.gyro(self.tt[:-1] + 0.5 / rate + off)
        if bg is not None:
            w = w - np.asarray(bg)[None]                                 # gyro bias (IMU frame)
        steps = R.from_rotvec(w / rate)
        q = [R.identity()]
        for s_ in steps:
            q.append(q[-1] * s_)
        self.Q = R.from_quat(np.array([x.as_quat() for x in q]))

    def at(self, t):
        return self.Q[int(np.clip(np.round((t - self.tt[0]) * 400.0), 0, len(self.tt) - 1))]


def rel_cam(orient, Rci, ta, tb):
    """cam_b <- cam_a rotation (OpenCV cameras) from the gyro: X_b = R_ba X_a + t."""
    rel_imu = orient.at(ta).inv() * orient.at(tb)                    # IMU orientation change a -> b
    rel_gl = Rci @ rel_imu.as_matrix() @ Rci.T                       # camera(GL) b expressed in camera(GL) a
    return (F @ rel_gl @ F).T


def pair_ratio(Rba, b1, b2, thr, iters=100, rng=None):
    """Best inlier ratio of the matches under the fixed rotation (translation by 2-point RANSAC)."""
    n = np.cross(b1 @ Rba.T, b2)                                     # each row is orthogonal to t
    nn = np.linalg.norm(n, axis=1)
    if len(n) < 5:
        return np.nan
    if np.median(nn) < thr:                                          # (near) pure rotation: consistent by itself
        return float(np.mean(nn < thr))
    rng = rng or np.random.default_rng(0)
    best = 0.0
    for _ in range(iters):
        i, j = rng.choice(len(n), 2, replace=False)
        t = np.cross(n[i], n[j])
        if np.linalg.norm(t) < 1e-9:
            continue
        t /= np.linalg.norm(t)
        best = max(best, float(np.mean(np.abs(n @ t) < thr)))
    return best


if __name__ == "__main__":
    from gyro_check import check
    from common import Capture
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset"); ap.add_argument("work"); ap.add_argument("sfm")
    ap.add_argument("--write", default=None)
    ap.add_argument("--min_ratio", type=float, default=0.5)
    ap.add_argument("--thr", type=float, default=0.004, help="epipolar threshold (rad) at dt = 0")
    ap.add_argument("--thr_per_s", type=float, default=0.0002, help="added per second between the frames (gyro drift)")
    a = ap.parse_args()
    meta = json.load(open(os.path.join(a.work, "frames.json")))
    pts = {f["name"]: f["pts"] + meta.get("pose_offset", 0.0) for f in meta["frames"]}
    imgs, _, cam = load_model(os.path.join(a.sfm, "sparse", "0"))
    rep = check(a.dataset, meta["frames"], {n: v[0] for n, v in imgs.items()}, Capture(a.dataset).t0_ns,
                meta.get("pose_offset", 0.0))
    orient = Orientation(rep["imu"], rep["off"], min(pts.values()) - 1, max(pts.values()) + 1)
    db = os.path.join(a.sfm, "database.db")
    c = sqlite3.connect(db)
    names = {i: os.path.splitext(n)[0] for i, n in c.execute("select image_id, name from images")}
    kps = {i: np.frombuffer(d, np.float32).reshape(r, cols)[:, :2]
           for i, r, cols, d in c.execute("select image_id, rows, cols, data from keypoints") if r > 0}
    rows = list(c.execute("select pair_id, rows, data from two_view_geometries where rows > 0"))
    rng = np.random.default_rng(0)
    res = []
    for pid, r, d in rows:
        i2 = pid % PAIR; i1 = (pid - i2) // PAIR
        na, nb = names[i1], names[i2]
        if na not in pts or nb not in pts:
            continue
        m = np.frombuffer(d, np.uint32).reshape(r, 2)
        b1 = bearings(kps[i1][m[:, 0]], cam); b2 = bearings(kps[i2][m[:, 1]], cam)
        dt = abs(pts[nb] - pts[na])
        ratio = pair_ratio(rel_cam(orient, rep["Rci"], pts[na], pts[nb]), b1, b2, a.thr + a.thr_per_s * dt, rng=rng)
        res.append((pid, na, nb, dt, r, ratio))
    dts = np.array([x[3] for x in res]); rat = np.array([x[5] for x in res])
    ok = ~(rat < a.min_ratio)                                            # NaN (too few matches) kept
    print(f"{len(res)} verified pairs; rejected {np.sum(~ok)} ({np.mean(~ok) * 100:.1f}%) with ratio < {a.min_ratio}")
    for lo, hi in ((0, 2), (2, 10), (10, 30), (30, 90), (90, 1e9)):
        sel = (dts >= lo) & (dts < hi)
        if sel.any():
            print(f"  dt {lo:>3}-{hi if hi < 1e9 else 'inf':>3} s: {sel.sum():6d} pairs, ratio median {np.nanmedian(rat[sel]):.2f}, "
                  f"rejected {np.mean(~ok[sel]) * 100:5.1f}%")
    if a.write:
        os.makedirs(a.write, exist_ok=True)
        dst = os.path.join(a.write, "database.db")
        shutil.copy(db, dst)
        c2 = sqlite3.connect(dst)
        bad = [int(x[0]) for x, k in zip(res, ok) if not k]
        c2.executemany("delete from two_view_geometries where pair_id = ?", [(b,) for b in bad])
        c2.commit()
        json.dump(dict(rejected=len(bad), pairs=len(res), min_ratio=a.min_ratio, thr=a.thr, thr_per_s=a.thr_per_s),
                  open(os.path.join(a.write, "gyro_pairs.json"), "w"), indent=1)
        print(f"wrote {dst} without {len(bad)} pairs")
