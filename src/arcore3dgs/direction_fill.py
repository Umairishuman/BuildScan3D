"""Place unplaced keyframes in the holes of a camera path from their image matches, with gyro rotations (2026-11-25).

scan_009's 125 - 133 s frames (the view into the bathroom) are textured and well matched (30 of 33 have pairs with
>= 30 inliers, 193 such pairs to placed frames at 123 - 140 s) but were dropped by the camera chain's filters.
ARCore cannot place them: its rotations are good but its positions in this stretch are not (arcore_fill.py, R-127:
it jumps 3.48 m at 127.5 s and its scale vs the model is far off). Here:
  1. rotations: gyro integrated from the placed neighbours (gyro_check.fill_rotations, calibrated on the model);
  2. directions: for every verified pair (COLMAP database) of a hole frame with a placed or another hole frame, the
     direction between the camera centres with both rotations fixed (rot_sfm.pair_direction, as loop_match.py);
  3. centres: linear least squares, (C_a - C_b) x u_ab = 0 for every pair (placed centres fixed), Cauchy
     reweighting (--sigma deg), a weak pull to the time-interpolated path across the hole (--prior units) so a frame
     with few pairs stays near the path;
  4. checks per frame: >= --min_placed pairs to placed frames, median Sampson error of its pairs <= --max_sampson
     px (arcore_fill.sampson_check); frames that fail are left out.
Writes the model with the new images and <model_out>/direction_fill.json.

  python src/arcore3dgs/direction_fill.py <dataset> <selection dir> <model_in> <database.db> <model_out>
"""
import argparse
import json
import os
import sqlite3
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from arcore_fill import PAIR, sampson_check, write_with_new  # noqa: E402
from common import Capture  # noqa: E402
from gyro_check import check, fill_rotations  # noqa: E402
from known_rot_pnp import bearings  # noqa: E402
from rot_sfm import pair_direction  # noqa: E402
from scale_drift import read_model  # noqa: E402


def skew(u):
    return np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0.0]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset"); ap.add_argument("selection"); ap.add_argument("model_in"); ap.add_argument("database")
    ap.add_argument("model_out")
    ap.add_argument("--hole_dt", type=float, default=2.5)
    ap.add_argument("--min_inliers", type=int, default=15); ap.add_argument("--min_parallax", type=float, default=1.0)
    ap.add_argument("--thr", type=float, default=0.004)
    ap.add_argument("--sigma", type=float, default=5.0, help="deg, direction residual scale (Cauchy)")
    ap.add_argument("--prior", type=float, default=1.0, help="units, sigma of the pull to the interpolated path")
    ap.add_argument("--min_placed", type=int, default=2); ap.add_argument("--max_sampson", type=float, default=4.0)
    ap.add_argument("--iters", type=int, default=10)
    a = ap.parse_args()

    meta = json.load(open(os.path.join(a.selection, "frames.json"))); sel = meta["frames"]
    pts_of = {f["name"]: f["pts"] for f in sel}; t0 = min(pts_of.values()); off = meta.get("pose_offset", 0.0)
    K, dist, fx, fy, imgs = read_model(a.model_in, pts_of)
    pl = {d["key"]: d for d in imgs}
    T = np.array([pts_of[d["key"]] - t0 for d in imgs])
    cam_line = [ln.split() for ln in open(os.path.join(a.model_in, "cameras.txt")) if ln[0] != "#" and ln.strip()][0]
    camera = (cam_line[1], list(map(float, cam_line[4:])))

    # 1. gyro rotations for the unplaced frames inside holes
    holes = [(T[k], T[k + 1]) for k in np.flatnonzero(np.diff(T) >= a.hole_dt)]
    cand = sorted([f for f in sel if f["name"] not in pl and any(s0 < f["pts"] - t0 < s1 for s0, s1 in holes)],
                  key=lambda f: f["pts"])
    rep = check(a.dataset, sel, {d["key"]: d["Rcw"].T for d in imgs}, Capture(a.dataset).t0_ns, off, verbose=True)
    tk = np.array([pts_of[d["key"]] + off for d in imgs])
    Rq = fill_rotations(rep["imu"], rep["Rci"], rep["off"], tk, [d["Rcw"].T for d in imgs],
                        np.array([f["pts"] + off for f in cand]))
    newR = {f["name"]: R.T for f, R in zip(cand, Rq)}                  # Rcw
    print(f"{len(holes)} holes >= {a.hole_dt:g} s, {len(cand)} unplaced keyframes inside them", flush=True)

    # 2. directions of the verified pairs touching a hole frame
    rot = {d["key"]: d["Rcw"] for d in imgs}; rot.update(newR)
    con = sqlite3.connect(a.database)
    name_of = {i: n.rsplit(".", 1)[0] for i, n in con.execute("select image_id, name from images")}
    kps = {}
    E = []                                                             # (a, b, u = dir of C_a - C_b in the world, weight)
    rng = np.random.default_rng(0)
    for pid, r, d_ in con.execute("select pair_id, rows, data from two_view_geometries where rows >= ?", (a.min_inliers,)):
        i2 = pid % PAIR; i1 = (pid - i2) // PAIR
        na, nb = name_of.get(i1), name_of.get(i2)
        if na not in rot or nb not in rot or not ({na, nb} & set(newR)):
            continue
        for i in (i1, i2):
            if i not in kps:
                row = con.execute("select rows, cols, data from keypoints where image_id=?", (i,)).fetchone()
                kps[i] = np.frombuffer(row[2], np.float32).reshape(row[0], row[1])[:, :2] if row and row[2] else None
        if kps[i1] is None or kps[i2] is None:
            continue
        m = np.frombuffer(d_, np.uint32).reshape(r, 2)
        b1 = bearings(kps[i1][m[:, 0]], camera); b2 = bearings(kps[i2][m[:, 1]], camera)
        Rba = rot[nb] @ rot[na].T
        t, inl, par = pair_direction(Rba, b1, b2, a.thr, rng=rng)
        if t is None or inl.sum() < a.min_inliers or par < a.min_parallax:
            continue
        E.append((na, nb, rot[nb].T @ t, float(inl.sum()) * min(par, 10.0) / 10.0))
    con.close()
    print(f"{len(E)} pair directions touch the hole frames", flush=True)

    # 3. centres: placed fixed, hole frames solved
    idx = {f["name"]: k for k, f in enumerate(cand)}; n = len(cand)
    C0 = np.zeros((n, 3))
    for k, f in enumerate(cand):                                       # time-interpolated path as the start and pull
        t_ = f["pts"] - t0; j = np.searchsorted(T, t_)
        w = (t_ - T[j - 1]) / max(T[j] - T[j - 1], 1e-6)
        C0[k] = (1 - w) * imgs[j - 1]["C"] + w * imgs[j]["C"]
    C = C0.copy(); sd = np.sin(np.radians(a.sigma))
    wq = np.array([w for *_, w in E]); wq = wq / max(np.median(wq), 1e-9)
    for _ in range(a.iters):
        A_ = np.zeros((0, 3 * n)); b_ = []
        rows = []
        for (na, nb, u, _), q in zip(E, wq):
            Ca = C[idx[na]] if na in idx else pl[na]["C"]; Cb = C[idx[nb]] if nb in idx else pl[nb]["C"]
            L = max(np.linalg.norm(Ca - Cb), 0.05)
            ang = np.degrees(np.arcsin(min(1.0, np.linalg.norm(np.cross(Ca - Cb, u)) / L)))
            if (Ca - Cb) @ u < 0:
                ang = 180 - ang
            wgt = np.sqrt(q / (1 + (ang / a.sigma) ** 2)) / (sd * L)
            M = skew(u) * wgt; row = np.zeros((3, 3 * n)); rhs = np.zeros(3)
            if na in idx:
                row[:, 3 * idx[na]:3 * idx[na] + 3] += M
            else:
                rhs -= M @ pl[na]["C"]
            if nb in idx:
                row[:, 3 * idx[nb]:3 * idx[nb] + 3] -= M
            else:
                rhs += M @ pl[nb]["C"]
            rows.append(row); b_.append(rhs)
        P = np.eye(3 * n) / a.prior
        A_ = np.vstack(rows + [P]); b_ = np.concatenate(b_ + [C0.reshape(-1) / a.prior])
        C = np.linalg.lstsq(A_, b_, rcond=None)[0].reshape(n, 3)

    # 4. checks
    n_pl = {f["name"]: 0 for f in cand}
    for na, nb, *_ in E:
        if na in idx and nb not in idx:
            n_pl[na] += 1
        if nb in idx and na not in idx:
            n_pl[nb] += 1
    pose = {d["key"]: (d["Rcw"], d["C"]) for d in imgs}
    pose.update({f["name"]: (newR[f["name"]], C[idx[f["name"]]]) for f in cand})
    errs = sampson_check(a.database, K, dist, fx, pose, set(idx))
    new, rows = [], []
    for f in cand:
        nm = f["name"]; e = errs[nm]; med = float(np.median(e)) if e else None
        ok = n_pl[nm] >= a.min_placed and med is not None and med <= a.max_sampson
        rows.append(dict(name=nm, t=float(f["pts"] - t0), placed_pairs=n_pl[nm], sampson_median=med,
                         moved_from_path=float(np.linalg.norm(C[idx[nm]] - C0[idx[nm]])), added=bool(ok)))
        if ok:
            new.append(dict(key=nm, Rcw=newR[nm], C=C[idx[nm]]))
    for r_ in rows:
        print(f"  {r_['t']:6.1f}s {r_['name']}: {r_['placed_pairs']:3d} pairs to placed frames, Sampson "
              f"{'-' if r_['sampson_median'] is None else round(r_['sampson_median'], 1)} px, "
              f"{r_['moved_from_path']:.2f} units from the interpolated path -> {'ADD' if r_['added'] else 'left out'}")
    n_in = write_with_new(a.model_in, a.model_out, new)
    json.dump(dict(params=vars(a), gyro_pair_err_deg_median=rep["pair_err_deg_median"], directions=len(E), frames=rows),
              open(os.path.join(a.model_out, "direction_fill.json"), "w"), indent=1)
    print(f"wrote {a.model_out}: {n_in} + {len(new)} images ({len(cand) - len(new)} of {len(cand)} left out)", flush=True)


if __name__ == "__main__":
    main()
