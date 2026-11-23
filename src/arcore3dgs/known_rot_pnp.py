"""Place a camera when its rotation is known (gyro) and only a few image points match the map.

FEATURELESS_TRACKING_PLAN step 4 (point part). With the camera-to-world rotation R fixed, each 2D-3D match gives two
LINEAR equations in the camera centre C ([d]x C = [d]x X, d = R * bearing), so two matches are enough (standard PnP
needs 3-4 and is fragile with few, noisy matches on plain walls). RANSAC over pairs, least-squares refit on inliers.

2D-3D matches come from the COLMAP database (verified two-view matches of the frame to frames already in the model)
and the model's tracks (which keypoint of a placed frame became which 3D point).

Test on a trusted capture (cut gaps, rotation from the gyro, matches subsampled to simulate few features):
  python src/arcore3dgs/known_rot_pnp.py <dataset> <keyframe dir> <sfm dir (database.db, sparse/0, report.json)>
      [--gaps 2 5 9] [--every 20] [--subsample 0 20 10 5 3]
"""
import argparse
import json
import os
import sqlite3
import sys

import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R

PAIR = 2147483647


def load_db(db):
    c = sqlite3.connect(db)
    names = {i: os.path.splitext(n)[0] for i, n in c.execute("select image_id, name from images")}
    kps = {i: np.frombuffer(d, np.float32).reshape(r, cols)[:, :2]
           for i, r, cols, d in c.execute("select image_id, rows, cols, data from keypoints") if r > 0}
    matches = {}
    for pid, r, d in c.execute("select pair_id, rows, data from two_view_geometries where rows > 0"):
        i2 = pid % PAIR; i1 = (pid - i2) // PAIR
        m = np.frombuffer(d, np.uint32).reshape(r, 2)
        matches.setdefault(names[i1], {})[names[i2]] = m
        matches.setdefault(names[i2], {})[names[i1]] = m[:, ::-1]
    return {names[i]: k for i, k in kps.items()}, matches


def load_model(d):
    """name -> (R_c2w, C, point3D id per keypoint); point id -> XYZ; camera (model, params)."""
    cam = [ln.split() for ln in open(os.path.join(d, "cameras.txt")) if ln[0] != "#" and ln.strip()][0]
    imgs = {}
    L = [ln for ln in open(os.path.join(d, "images.txt")) if ln[0] != "#"]
    for a, b in zip(L[0::2], L[1::2]):
        p = a.split()
        q = list(map(float, p[1:5])); t = np.array(list(map(float, p[5:8])))
        Rw2c = R.from_quat([q[1], q[2], q[3], q[0]]).as_matrix()
        obs = np.array(b.split(), float).reshape(-1, 3)[:, 2].astype(np.int64) if b.strip() else np.zeros(0, np.int64)
        imgs[os.path.splitext(p[9])[0]] = (Rw2c.T, -Rw2c.T @ t, obs)
    X = {}
    for ln in open(os.path.join(d, "points3D.txt")):
        if ln[0] != "#" and ln.strip():
            p = ln.split(); X[int(p[0])] = np.array(list(map(float, p[1:4])))
    return imgs, X, (cam[1], list(map(float, cam[4:])))


def bearings(uv, camera):
    if len(uv) == 0:
        return np.zeros((0, 3))
    model, prm = camera
    fx, fy, cx, cy = prm[:4]
    K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
    dist = np.array(prm[4:8] if model == "OPENCV" else [0, 0, 0, 0], float)
    n = cv2.undistortPoints(uv.reshape(-1, 1, 2).astype(np.float64), K, dist).reshape(-1, 2)
    b = np.c_[n, np.ones(len(n))]
    return b / np.linalg.norm(b, axis=1, keepdims=True)


def correspondences(name, kps, matches, imgs, X, anchors, valid_pts):
    """2D (keypoint index) -> 3D point id for frame `name`, through verified matches to anchor frames."""
    got = {}
    for other, m in matches.get(name, {}).items():
        if other not in anchors or other not in imgs:
            continue
        obs = imgs[other][2]
        for ku, ko in m:
            if ko < len(obs) and obs[ko] >= 0 and obs[ko] in valid_pts:
                got.setdefault(int(ku), int(obs[ko]))
    ku = np.array(list(got), int)
    return (kps[name][ku], np.array([X[got[k]] for k in ku])) if len(ku) else (np.zeros((0, 2)), np.zeros((0, 3)))


def _solve(d, Xs):
    A, b = [], []
    for di, xi in zip(d, Xs):
        S = np.array([[0, -di[2], di[1]], [di[2], 0, -di[0]], [-di[1], di[0], 0]])
        A.append(S); b.append(S @ xi)
    return np.linalg.lstsq(np.vstack(A), np.concatenate(b), rcond=None)[0]


def place_known_rotation(R_c2w, bear, Xs, thr_deg=1.0, iters=300, rng=None):
    """Camera centre with the rotation fixed. Returns (C, inlier mask) or (None, None)."""
    if len(Xs) < 2:
        return None, None
    rng = rng or np.random.default_rng(0)
    d = bear @ R_c2w.T
    cos_thr = np.cos(np.deg2rad(thr_deg))

    def inl(C):
        v = Xs - C; v /= np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-9)
        return np.sum(v * d, axis=1) > cos_thr

    best = None
    pairs = [(i, j) for i in range(len(Xs)) for j in range(i + 1, len(Xs))]
    sel = pairs if len(pairs) <= iters else [tuple(rng.choice(len(Xs), 2, replace=False)) for _ in range(iters)]
    for i, j in sel:
        C = _solve(d[[i, j]], Xs[[i, j]])
        m = inl(C)
        if best is None or m.sum() > best[1].sum():
            best = (C, m)
    C, m = best
    if m.sum() >= 2:
        C = _solve(d[m], Xs[m]); m = inl(C)
    return C, m


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from gyro_check import check, fill_rotations
    from common import Capture
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset"); ap.add_argument("work"); ap.add_argument("sfm")
    ap.add_argument("--gaps", type=float, nargs="+", default=[2, 5, 9])
    ap.add_argument("--every", type=float, default=20.0)
    ap.add_argument("--subsample", type=int, nargs="+", default=[0, 20, 10, 5, 3], help="0 = all matches")
    a = ap.parse_args()

    meta = json.load(open(os.path.join(a.work, "frames.json")))
    imgs, X, camera = load_model(os.path.join(a.sfm, "sparse", "0"))
    kps, matches = load_db(os.path.join(a.sfm, "database.db"))
    scale = json.load(open(os.path.join(a.sfm, "report.json")))["sim3_scale"]      # COLMAP units -> metres
    rep = check(a.dataset, meta["frames"], {n: v[0] for n, v in imgs.items()}, Capture(a.dataset).t0_ns,
                meta.get("pose_offset", 0.0), verbose=True)
    good = sorted([f for f in meta["frames"] if f["name"] in imgs and rep["frame_score_deg"].get(f["name"], 99) <= 2.0],
                  key=lambda f: f["pts"])
    t = np.array([f["pts"] + meta.get("pose_offset", 0.0) for f in good]); names = [f["name"] for f in good]
    rng = np.random.default_rng(0)
    print(f"scale {scale:.4f} m per model unit; position error in cm; 'ok' = error < 10 cm")
    print(f"{'gap s':>5} {'matches':>7} {'frames':>6} | known rotation (gyro): median / p90 / ok% | PnP RANSAC (no gyro): median / p90 / ok%")
    for g in a.gaps:
        for sub in a.subsample:
            e_kr, e_pnp = [], []
            for start in np.arange(t[0] + 2, t[-1] - g - 2, a.every):
                inside = np.where((t >= start) & (t < start + g))[0]
                outside = np.where((t < start) | (t >= start + g))[0]
                if len(inside) < 2:
                    continue
                anchors = {names[i] for i in outside}
                # points still supported by >= 2 anchor frames (the map without the gap frames)
                cnt = {}
                for n in anchors:
                    for pid in imgs[n][2][imgs[n][2] >= 0]:
                        cnt[pid] = cnt.get(pid, 0) + 1
                valid = {p for p, c in cnt.items() if c >= 2}
                Rq = fill_rotations(rep["imu"], rep["Rci"], rep["off"], t[outside], [imgs[names[i]][0] for i in outside], t[inside])
                for k, i in enumerate(inside):
                    uv, Xs = correspondences(names[i], kps, matches, imgs, X, anchors, valid)
                    if sub and len(Xs) > sub:
                        s = rng.choice(len(Xs), sub, replace=False); uv, Xs = uv[s], Xs[s]
                    Ctrue = imgs[names[i]][1]
                    C, m = place_known_rotation(Rq[k], bearings(uv, camera), Xs)
                    e_kr.append(np.inf if C is None else np.linalg.norm(C - Ctrue) * scale * 100)
                    if len(Xs) >= 4:
                        b = bearings(uv, camera); pts = (b[:, :2] / b[:, 2:3]).astype(np.float64)
                        ok, rv, tv, _ = cv2.solvePnPRansac(Xs.astype(np.float64), pts, np.eye(3), None,
                                                           reprojectionError=np.tan(np.deg2rad(1.0)), iterationsCount=300,
                                                           flags=cv2.SOLVEPNP_AP3P)
                        if ok:
                            Rw2c = cv2.Rodrigues(rv)[0]; Cp = -Rw2c.T @ tv.ravel()
                            e_pnp.append(np.linalg.norm(Cp - Ctrue) * scale * 100)
                        else:
                            e_pnp.append(np.inf)
                    else:
                        e_pnp.append(np.inf)
            q = lambda e: (f"{np.median(e):6.1f} / {np.percentile(e, 90):7.1f} / {np.mean(np.array(e) < 10) * 100:4.0f}%"  # noqa: E731
                           if e else "-")
            print(f"{g:5.0f} {('all' if sub == 0 else sub):>7} {len(e_kr):6d} | {q(e_kr):>38} | {q(e_pnp):>38}")
