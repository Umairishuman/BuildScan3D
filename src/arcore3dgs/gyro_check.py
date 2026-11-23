"""Gyro rotation check of an SfM model: flag cameras whose rotation disagrees with the phone's gyroscope.

FEATURELESS_TRACKING_PLAN.md step 1. Global SfM sometimes snaps a frame onto a similar-looking place (R-046:
misplaced cameras on scan_009). The gyroscope (201 Hz in the ARCore MP4, imu.py) measures how the phone turned
between two keyframes, independent of texture and of ARCore tracking. For every pair of registered keyframes less
than --window s apart, the SfM relative rotation is compared with the integrated gyro rotation; a frame's score is
the median disagreement over its pairs (robust when a neighbour is itself wrong).

The IMU->camera rotation and the gyro time offset are estimated from the SfM model itself (Kabsch on the rotation
vectors of the pairs, trimmed, best offset in +-60 ms), so ARCore tracking is not needed.

  python src/arcore3dgs/gyro_check.py <dataset> <keyframe dir with frames.json> <COLMAP model dir (images.txt)>
      [--window 1.0] [--thr 2.0] [--out report.json]
As a module: check(dataset, frames, c2w_cv, ...) -> dict (used by sfm_colmap.py export).
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.spatial.transform import Rotation as R

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fallback import Imu  # noqa: E402

F = np.diag([1.0, -1.0, -1.0])          # OpenCV <-> OpenGL camera axes


def read_images_txt(model_dir):
    """name (without .jpg) -> 3x3 camera-to-world rotation (OpenCV camera, model world)."""
    out = {}
    L = [ln for ln in open(os.path.join(model_dir, "images.txt")) if ln[0] != "#"]
    for a in L[0::2]:
        p = a.split()
        if len(p) < 10:
            continue
        q = list(map(float, p[1:5]))
        Rw2c = R.from_quat([q[1], q[2], q[3], q[0]]).as_matrix()
        out[os.path.splitext(p[9])[0]] = Rw2c.T
    return out


def _integrate(imu, ta, tb, off, n=None):
    """Rotation of the IMU body from ta to tb (IMU frame), by integrating the gyro."""
    n = n or max(4, int((tb - ta) * 400))
    ts = np.linspace(ta, tb, n + 1)
    w = imu.gyro(0.5 * (ts[:-1] + ts[1:]) + off)
    rot = R.identity()
    for k in range(n):
        rot = rot * R.from_rotvec(w[k] * (ts[k + 1] - ts[k]))
    return rot


def _kabsch(A, B):
    """Rotation Rm with B ~ A @ Rm.T (rows are vectors)."""
    U, _, Vt = np.linalg.svd(A.T @ B)
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    return Vt.T @ D @ U.T


def check(dataset, frames, c2w_rot, t0_ns, pose_offset=0.0, window=1.0, thr_deg=2.0, verbose=True):
    """frames: list of dicts with name, pts; c2w_rot: name -> 3x3 camera-to-world rotation (OpenCV camera)."""
    imu = Imu(dataset, t0_ns)
    reg = sorted([f for f in frames if f["name"] in c2w_rot], key=lambda f: f["pts"])
    names = [f["name"] for f in reg]
    t = np.array([f["pts"] + pose_offset for f in reg])
    Rs = [c2w_rot[n] for n in names]
    pairs = [(i, j) for i in range(len(reg)) for j in range(i + 1, len(reg)) if t[j] - t[i] <= window]
    if len(pairs) < 20:
        raise ValueError(f"only {len(pairs)} keyframe pairs within {window} s")
    # SfM relative rotation of the camera (OpenGL camera frame, to match the IMU convention in fallback.py)
    rel_sfm = [R.from_matrix(F @ (Rs[i].T @ Rs[j]) @ F) for i, j in pairs]
    rv_sfm = np.array([r.as_rotvec() for r in rel_sfm])
    # calibration on a subset of pairs with enough rotation: offset grid, Kabsch, trim the worst 30%, refit
    big = np.where(np.linalg.norm(rv_sfm, axis=1) > np.deg2rad(2))[0]
    cal_idx = big[np.linspace(0, len(big) - 1, min(len(big), 400)).astype(int)] if len(big) else np.arange(len(pairs))
    best = None
    for off in np.arange(-0.2, 0.2001, 0.005):
        rv_imu = np.array([_integrate(imu, t[pairs[k][0]], t[pairs[k][1]], off, n=40).as_rotvec() for k in cal_idx])
        keep = np.arange(len(cal_idx))
        for _ in range(3):
            Rci = _kabsch(rv_imu[keep], rv_sfm[cal_idx][keep])
            res = np.linalg.norm(rv_sfm[cal_idx] - rv_imu @ Rci.T, axis=1)
            keep = np.argsort(res)[: max(10, int(0.7 * len(res)))]
        score = float(np.median(res[keep]))
        if best is None or score < best[0]:
            best = (score, off, Rci)
    _, off, Rci = best
    # gyro bias (IMU frame): over a pair, SfM rotation vector (IMU frame) ~ integrated gyro - b_g * dt (trimmed LS)
    rv_imu_all = np.array([_integrate(imu, t[pairs[k][0]], t[pairs[k][1]], off, n=40).as_rotvec() for k in cal_idx])
    rv_sfm_imu = rv_sfm[cal_idx] @ Rci                                  # camera(GL) rotvec -> IMU frame
    dts = np.array([t[pairs[k][1]] - t[pairs[k][0]] for k in cal_idx])
    resid = rv_imu_all - rv_sfm_imu                                     # ~ b_g * dt
    ok_b = np.linalg.norm(resid, axis=1) < np.percentile(np.linalg.norm(resid, axis=1), 70)
    bg = np.linalg.lstsq(np.repeat(dts[ok_b], 3)[:, None] * np.tile(np.eye(3), (ok_b.sum(), 1)),
                         resid[ok_b].reshape(-1), rcond=None)[0]
    # per pair: angle between the SfM and gyro relative rotations
    err = np.empty(len(pairs))
    for k, (i, j) in enumerate(pairs):
        g = R.from_matrix(Rci @ _integrate(imu, t[i], t[j], off).as_matrix() @ Rci.T)
        err[k] = np.rad2deg((rel_sfm[k].inv() * g).magnitude())
    per = [[] for _ in reg]
    for k, (i, j) in enumerate(pairs):
        per[i].append(err[k]); per[j].append(err[k])
    score = np.array([np.median(p) if p else np.nan for p in per])
    flagged = [names[i] for i in range(len(reg)) if not np.isfinite(score[i]) or score[i] > thr_deg]
    rep = dict(imu=imu, Rci=Rci, off=off, bg=bg, gyro_bias_deg_s=float(np.degrees(np.linalg.norm(bg))),
               frames=len(reg), pairs=len(pairs), window_s=window, thr_deg=thr_deg, time_offset_ms=float(off * 1000),
               R_imu_to_cam_gl=Rci.tolist(), pair_err_deg_median=float(np.median(err)),
               pair_err_deg_p90=float(np.percentile(err, 90)), frame_score_deg=dict(zip(names, map(float, score))),
               flagged=flagged)
    if verbose:
        print(f"gyro check: {len(reg)} frames, {len(pairs)} pairs within {window} s, time offset {off * 1000:.0f} ms, "
              f"pair error median {rep['pair_err_deg_median']:.2f} deg, p90 {rep['pair_err_deg_p90']:.2f} deg; "
              f"{len(flagged)} frames over {thr_deg} deg")
    return rep


def gyro_rotation(imu, Rci, off, t_from, R_from, t_to):
    """Camera-to-world rotation (OpenCV camera) at t_to, from a known one at t_from plus the integrated gyro."""
    if t_to >= t_from:
        rel = Rci @ _integrate(imu, t_from, t_to, off).as_matrix() @ Rci.T
    else:
        rel = (Rci @ _integrate(imu, t_to, t_from, off).as_matrix() @ Rci.T).T
    return R_from @ (F @ rel @ F)


def fill_rotations(imu, Rci, off, t_known, R_known, t_query):
    """Rotations at t_query from the nearest known frames before and after (slerp-blended by time, as fallback.py
    bridges gaps), or from the one side that exists."""
    order = np.argsort(t_known); tk = np.asarray(t_known)[order]; Rk = [R_known[i] for i in order]
    out = []
    for tq in t_query:
        i = np.searchsorted(tk, tq)
        cands = []
        if i > 0:
            cands.append((tk[i - 1], gyro_rotation(imu, Rci, off, tk[i - 1], Rk[i - 1], tq)))
        if i < len(tk):
            cands.append((tk[i], gyro_rotation(imu, Rci, off, tk[i], Rk[i], tq)))
        if len(cands) == 1:
            out.append(cands[0][1]); continue
        (ta, Ra), (tb, Rb) = cands
        w = (tq - ta) / max(tb - ta, 1e-6)
        rel = R.from_matrix(Ra.T @ Rb).as_rotvec()
        out.append(Ra @ R.from_rotvec(w * rel).as_matrix())
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("work", help="keyframe folder with frames.json (names, pts)")
    ap.add_argument("model", help="COLMAP model folder with images.txt (e.g. <work>_sfm/sparse/0)")
    ap.add_argument("--window", type=float, default=1.0)
    ap.add_argument("--thr", type=float, default=2.0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    meta = json.load(open(os.path.join(a.work, "frames.json")))
    from common import Capture
    t0 = Capture(a.dataset).t0_ns
    rep = check(a.dataset, meta["frames"], read_images_txt(a.model), t0, meta.get("pose_offset", 0.0), a.window, a.thr)
    if a.out:
        json.dump({k: v for k, v in rep.items() if k not in ("imu", "Rci", "off", "bg")}, open(a.out, "w"), indent=1)
