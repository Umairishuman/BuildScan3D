"""SfM with rotations from the gyroscope ("known-rotation SfM") for captures where feature-based SfM fails locally.

FEATURELESS_TRACKING_PLAN, from the scan_009 nights (R-046 – R-050). COLMAP's mappers estimate rotations and
positions from matches together; on blurry, plain, repetitive rooms that goes wrong locally. Here rotations come
from the phone's gyroscope (integrated once over the video, aligned to the camera with gyro_check's calibration),
which leaves only positions to estimate:

  1. per verified image pair (COLMAP database): with the gyro rotation fixed, the direction of motion from the
     matches (2-point RANSAC on the epipolar constraint, sign by cheirality), and how much parallax supports it;
  2. linear translation averaging: camera centres C with (C_a - C_b) x u_ab = 0 for every pair direction u_ab,
     iteratively reweighted to suppress wrong pairs; largest connected set only;
  3. a COLMAP model with these poses (distorted OPENCV camera from a calibration model), then
     point_triangulator + bundle_adjuster refine it from the images.

The result goes to <out>/sparse/0 (and TXT), so sfm_colmap.py --stage undistort / export continue as usual.

  python src/arcore3dgs/rot_sfm.py <dataset> <keyframe dir> <calibration sfm dir (sparse/0, database.db)> <out sfm dir>
      [--max_dt 20] [--min_inliers 15]
"""
import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import lsqr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import toolpaths  # noqa: E402
from common import Capture  # noqa: E402
from gyro_check import check  # noqa: E402
from gyro_pairs import Orientation  # noqa: E402
from known_rot_pnp import bearings, load_model  # noqa: E402

PAIR = 2147483647
F = np.diag([1.0, -1.0, -1.0])


def pair_direction(Rba, b1, b2, thr, iters=200, rng=None):
    """Translation t (cam b frame, X_b = R_ba X_a + t, unit) with the rotation fixed; returns (t, inlier mask, parallax)."""
    q = b1 @ Rba.T                                                   # cam-a bearings rotated into cam b
    n = np.cross(q, b2)
    if len(n) < 8:
        return None, None, 0.0
    rng = rng or np.random.default_rng(0)
    best = (None, None)
    for _ in range(iters):
        i, j = rng.choice(len(n), 2, replace=False)
        t = np.cross(n[i], n[j]); nt = np.linalg.norm(t)
        if nt < 1e-9:
            continue
        t /= nt
        m = np.abs(n @ t) < thr
        if best[1] is None or m.sum() > best[1].sum():
            best = (t, m)
    t, m = best
    if t is None or m.sum() < 8:
        return None, None, 0.0
    # refit: smallest singular vector of the inliers' n
    t = np.linalg.svd(n[m])[2][-1]
    # sign by cheirality: points must lie in front of both cameras
    # X_b = d_b * b2 = d_a * q + t  ->  solve [b2, -q] [d_b, d_a]^T = t per match
    def front(tt):
        ok = 0
        for k in np.where(m)[0][:200]:
            A = np.c_[b2[k], -q[k]]
            d = np.linalg.lstsq(A, tt, rcond=None)[0]
            ok += (d[0] > 0) and (d[1] > 0)
        return ok
    if front(-t) > front(t):
        t = -t
    parallax = float(np.median(np.degrees(np.arccos(np.clip(np.sum(q[m] * b2[m], 1), -1, 1)))))
    return t, m, parallax


def translation_averaging(n_cams, edges, iters=8):
    """edges: (a, b, u, w) with u the unit direction of C_a - C_b (world). Linear LS of (C_a - C_b) x u = 0 with the
    gauge fixed by C_0 = 0 and mean projected length 1; IRLS (Cauchy) on the angular residual."""
    w = np.array([e[3] for e in edges], float)
    for it in range(iters):
        rows, cols, vals, rhs = [], [], [], []
        r = 0
        for (a, b, u, _), wk in zip(edges, w):
            S = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]]) * np.sqrt(wk)
            for i in range(3):
                for j in range(3):
                    if S[i, j] != 0:
                        rows += [r + i, r + i]; cols += [3 * a + j, 3 * b + j]; vals += [S[i, j], -S[i, j]]
            rhs += [0, 0, 0]; r += 3
        # gauge: C_0 = 0 (3 rows), scale: sum_k w_k u_k . (C_a - C_b) = sum w_k
        for j in range(3):
            rows.append(r); cols.append(j); vals.append(1e3); rhs.append(0); r += 1
        for (a, b, u, _), wk in zip(edges, w):
            for j in range(3):
                rows += [r, r]; cols += [3 * a + j, 3 * b + j]; vals += [wk * u[j], -wk * u[j]]
        rhs.append(w.sum()); r += 1
        A = coo_matrix((vals, (rows, cols)), shape=(r, 3 * n_cams)).tocsr()
        C = lsqr(A, np.array(rhs, float), atol=1e-10, btol=1e-10, iter_lim=20000)[0].reshape(-1, 3)
        ang = np.array([np.degrees(np.arccos(np.clip((C[a] - C[b]) @ u / max(np.linalg.norm(C[a] - C[b]), 1e-12), -1, 1)))
                        for a, b, u, _ in edges])
        base = np.array([e[3] for e in edges], float)
        w = base / (1 + (ang / 5.0) ** 2)
        print(f"  translation averaging iteration {it}: angular residual median {np.median(ang):.2f} deg, "
              f"p90 {np.percentile(ang, 90):.2f} deg", flush=True)
    return C, ang


def vio_average(n_cams, times, edges, imu_terms, w_dir=1.0, w_a=1000.0, w_b=100.0, iters=6, g_seg=15.0):
    """Metric camera centres from pair directions AND the accelerometer, one sparse linear system per iteration.
    Unknowns: C (3N, metres), v (3N, m/s), gravity per g_seg-second segment (world, pointing down; neighbours tied
    softly: residual gyro drift), accelerometer bias b_a (3).
      accelerometer, interval i->j: C_j - C_i - v_i T - g T^2/2 + J_a b_a = alpha,   v_j - v_i - g T + J_b b_a = beta
      direction (a, b, u):          C_a - C_b - lambda_ab u = 0,  lambda_ab = |C_a - C_b| from the
                                    previous iteration (fixed lengths: the homogeneous form (C_a - C_b) x u = 0 lets the
                                    solution shrink, R-051), sigma = 5 mm + 3% of lambda, Cauchy weight on the angle.
    Iteration 0 is accelerometer-only (correct local scale, drifts); later ones add the directions."""
    N = n_cams
    seg = np.floor((np.asarray(times) - times[0]) / g_seg).astype(int)
    nseg = int(seg.max()) + 1
    bi = 6 * N; gi0 = 6 * N + 3; nv = 6 * N + 3 + 3 * nseg
    C = None; ang = np.zeros(len(edges)); g = np.zeros((nseg, 3)); x = np.zeros(nv)
    rw = np.ones(len(edges))
    for it in range(iters + 1):
        rows, cols, vals, rhs = [], [], [], []
        r = 0

        def put(rr, cc, vv):
            rows.append(rr); cols.append(cc); vals.append(vv)
        if it > 0:
            for (a, b, u, q), wk, k in zip(edges, rw, range(len(edges))):
                lam = float(np.linalg.norm(C[a] - C[b]))           # keep the length, take the direction
                w = w_dir * np.sqrt(wk * q) / (0.005 + 0.03 * lam)
                for m in range(3):
                    put(r + m, 3 * a + m, w); put(r + m, 3 * b + m, -w)
                rhs += list(w * lam * u); r += 3
        for (i, j, T, al, be, Ja, Jb) in imu_terms:
            gi = gi0 + 3 * seg[i]
            for k in range(3):
                put(r + k, 3 * j + k, w_a); put(r + k, 3 * i + k, -w_a)
                put(r + k, 3 * N + 3 * i + k, -w_a * T); put(r + k, gi + k, -w_a * T * T / 2)
                for m in range(3):
                    put(r + k, bi + m, w_a * Ja[k, m])
            rhs += list(w_a * al); r += 3
            for k in range(3):
                put(r + k, 3 * N + 3 * j + k, w_b); put(r + k, 3 * N + 3 * i + k, -w_b); put(r + k, gi + k, -w_b * T)
                for m in range(3):
                    put(r + k, bi + m, w_b * Jb[k, m])
            rhs += list(w_b * be); r += 3
        for k in range(3):
            put(r, k, 1e4); rhs.append(0.0); r += 1
        for q_ in range(nseg - 1):
            for k in range(3):
                put(r, gi0 + 3 * q_ + k, 10.0); put(r, gi0 + 3 * (q_ + 1) + k, -10.0); rhs.append(0.0); r += 1
        A = coo_matrix((vals, (rows, cols)), shape=(r, nv)).tocsr()
        x = lsqr(A, np.array(rhs, float), atol=1e-12, btol=1e-12, iter_lim=50000, x0=x)[0]
        C = x[:3 * N].reshape(-1, 3); g = x[gi0:].reshape(-1, 3)
        ang = np.array([np.degrees(np.arccos(np.clip((C[a] - C[b]) @ u / max(np.linalg.norm(C[a] - C[b]), 1e-12), -1, 1)))
                        for a, b, u, _ in edges])
        rw = 1.0 / (1 + (ang / 5.0) ** 2)
        print(f"  VIO averaging iteration {it}{' (accelerometer only)' if it == 0 else ''}: direction residual median "
              f"{np.median(ang):.2f} deg, p90 {np.percentile(ang, 90):.2f} deg, |g| median "
              f"{np.median(np.linalg.norm(g, axis=1)):.3f} m/s^2 ({nseg} segments)", flush=True)
    return C, ang, g, x[bi:bi + 3]


def preintegrate(imu, off, R_world_imu, ta, tb, rate=400.0):
    tt = np.arange(ta, tb, 1 / rate); dt = 1 / rate
    Rw_ = np.array([R_world_imu(x) for x in tt])
    rf = np.einsum("nij,nj->ni", Rw_, imu.accel(tt + off))
    beta = np.cumsum(rf, 0) * dt; Jb = np.cumsum(Rw_, 0) * dt
    return np.sum(beta, 0) * dt, beta[-1], np.sum(Jb, 0) * dt, Jb[-1]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset"); ap.add_argument("work"); ap.add_argument("calib"); ap.add_argument("out")
    ap.add_argument("--max_dt", type=float, default=20.0, help="only pairs closer in time (gyro drift)")
    ap.add_argument("--min_inliers", type=int, default=15)
    ap.add_argument("--min_parallax", type=float, default=1.0, help="deg; pairs with less give no direction")
    ap.add_argument("--thr", type=float, default=0.004)
    ap.add_argument("--colmap", default=toolpaths.colmap())
    ap.add_argument("--imu", type=int, default=1, help="1: metric VIO averaging with the accelerometer; 0: directions only")
    ap.add_argument("--w_dir", type=float, default=1.0, help="multiplier of the direction equations (sigma 5 mm + 3%%)")
    ap.add_argument("--w_a", type=float, default=1000.0, help="weight of an accelerometer position equation (1 / ~1 mm)")
    ap.add_argument("--w_b", type=float, default=100.0, help="weight of an accelerometer velocity equation (1 / ~1 cm/s)")
    ap.add_argument("--iters", type=int, default=15)
    ap.add_argument("--triangulate_only", action="store_true", help="poses stay as solved (metric, from the IMU)")
    ap.add_argument("--no_ba", action="store_true", help="stop after the initial model (rot_init), no triangulation / BA")
    ap.add_argument("--bg_json", default=None, help="gyro bias from gyro_loop_bias.py (replaces gyro_check's estimate)")
    ap.add_argument("--imu_max_gap", type=float, default=2.0, help="s; longer keyframe gaps get no accelerometer link")
    a = ap.parse_args()
    OUT = os.path.abspath(a.out); os.makedirs(OUT, exist_ok=True)
    meta = json.load(open(os.path.join(a.work, "frames.json")))
    pts = {f["name"]: f["pts"] + meta.get("pose_offset", 0.0) for f in meta["frames"]}
    imgs0, _, cam = load_model(os.path.join(a.calib, "sparse", "0"))
    # IMU->camera calibration from the calibration model (Kabsch on its rotations, trimmed: robust to bad frames)
    rep = check(a.dataset, meta["frames"], {n: v[0] for n, v in imgs0.items()}, Capture(a.dataset).t0_ns,
                meta.get("pose_offset", 0.0))
    if a.bg_json:
        rep["bg"] = np.array(json.load(open(a.bg_json))["bg"])
        rep["gyro_bias_deg_s"] = float(np.degrees(np.linalg.norm(rep["bg"])))
        print(f"gyro bias from {a.bg_json}")
    orient = Orientation(rep["imu"], rep["off"], min(pts.values()) - 1, max(pts.values()) + 1, bg=rep["bg"])
    print(f"gyro bias {rep['gyro_bias_deg_s']:.3f} deg/s removed")
    Rci = rep["Rci"]

    def Rw(t):                                                        # camera(OpenCV) -> world, world = camera at t=0
        return F @ Rci @ orient.at(t).as_matrix() @ Rci.T @ F

    shutil.copy(os.path.join(a.calib, "database.db"), os.path.join(OUT, "database.db"))
    c = sqlite3.connect(os.path.join(OUT, "database.db"))
    ids = {os.path.splitext(n)[0]: i for i, n in c.execute("select image_id, name from images")}
    names_db = {i: n for n, i in ids.items()}
    kps = {i: np.frombuffer(d, np.float32).reshape(r, cols)[:, :2]
           for i, r, cols, d in c.execute("select image_id, rows, cols, data from keypoints") if r > 0}
    rng = np.random.default_rng(0)
    edges_raw = []
    rows = list(c.execute("select pair_id, rows, data from two_view_geometries where rows > 0"))
    cache = os.path.join(OUT, f"pair_directions_dt{a.max_dt:g}_par{a.min_parallax:g}{'_bg' if a.bg_json else ''}.json")
    if os.path.exists(cache):
        edges_raw = [(x[0], x[1], np.array(x[2]), x[3]) for x in json.load(open(cache))]
        rows_todo = []
    else:
        rows_todo = rows
    for pid, r, d in rows_todo:
        i2 = pid % PAIR; i1 = (pid - i2) // PAIR
        na, nb = names_db[i1], names_db[i2]
        if na not in pts or nb not in pts or abs(pts[na] - pts[nb]) > a.max_dt or r < a.min_inliers:
            continue
        m = np.frombuffer(d, np.uint32).reshape(r, 2)
        b1 = bearings(kps[i1][m[:, 0]], cam); b2 = bearings(kps[i2][m[:, 1]], cam)
        Ra, Rb = Rw(pts[na]), Rw(pts[nb])
        Rba = Rb.T @ Ra
        t, inl, par = pair_direction(Rba, b1, b2, a.thr, rng=rng)
        if t is None or inl.sum() < a.min_inliers or par < a.min_parallax:
            continue
        u = Rb @ t                                                    # direction of C_a - C_b in the world
        edges_raw.append((na, nb, u, float(inl.sum()) * min(par, 10.0) / 10.0))
    if not os.path.exists(cache):
        json.dump([(x[0], x[1], x[2].tolist(), x[3]) for x in edges_raw], open(cache, "w"))
    print(f"{len(edges_raw)} pair directions from {len(rows)} verified pairs (dt <= {a.max_dt} s, parallax >= "
          f"{a.min_parallax} deg)")
    # largest connected set
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for na, nb, _, _ in edges_raw:
        parent[find(na)] = find(nb)
    if a.imu:                       # the accelerometer links consecutive keyframes, also ones without image matches
        seq = sorted([n for n in pts if n in ids], key=lambda n: pts[n])
        for n1, n2 in zip(seq[:-1], seq[1:]):
            if pts[n2] - pts[n1] <= a.imu_max_gap:
                parent[find(n1)] = find(n2)
    groups = {}
    for n in parent:
        groups.setdefault(find(n), []).append(n)
    main = max(groups.values(), key=len)
    print(f"connected sets: {sorted((len(g) for g in groups.values()), reverse=True)[:8]}")
    order = sorted(main, key=lambda n: pts[n]); idx = {n: k for k, n in enumerate(order)}
    edges = [(idx[na], idx[nb], u, w) for na, nb, u, w in edges_raw if na in idx and nb in idx]
    if a.imu:
        def R_world_imu(t):                                           # = Rw(t) @ F @ Rci
            return F @ Rci @ orient.at(t).as_matrix()
        tk = np.array([pts[n] for n in order])
        terms = []
        for i in range(len(order) - 1):
            T = tk[i + 1] - tk[i]
            if 0 < T <= a.imu_max_gap:
                al, be, Ja, Jb = preintegrate(rep["imu"], rep["off"], R_world_imu, tk[i], tk[i + 1])
                terms.append((i, i + 1, T, al, be, Ja, Jb))
        print(f"{len(terms)} accelerometer links between consecutive keyframes (gap <= {a.imu_max_gap} s)")
        C, ang, g_vec, b_a = vio_average(len(order), tk, edges, terms, w_dir=a.w_dir, w_a=a.w_a, w_b=a.w_b, iters=a.iters)
    else:
        C, ang = translation_averaging(len(order), edges)
    # drop cameras whose edges mostly disagree
    bad = {}
    for (ia, ib, _, _), e in zip(edges, ang):
        for k in (ia, ib):
            bad.setdefault(k, []).append(e)
    keep = [k for k in range(len(order)) if np.median(bad.get(k, [0.0 if a.imu else 99])) < 10]
    print(f"cameras: {len(order)} in the main set, {len(keep)} with median edge residual < 10 deg")
    # metric VIO result: rotate the world so gravity points along -Y (ARCore convention, +Y up)
    Rg = np.eye(3)
    if a.imu:
        gm = np.median(g_vec, axis=0); up = -gm / np.linalg.norm(gm)
        v = np.cross(up, [0.0, 1.0, 0.0]); sn = np.linalg.norm(v); cs = float(up @ [0.0, 1.0, 0.0])
        if sn > 1e-9:
            from scipy.spatial.transform import Rotation as Rot_
            Rg = Rot_.from_rotvec(v / sn * np.arctan2(sn, cs)).as_matrix()
    # COLMAP model (OPENCV camera of the calibration model; poses world-to-camera)
    from scipy.spatial.transform import Rotation as Rot
    tri_in = os.path.join(OUT, "rot_init"); os.makedirs(tri_in, exist_ok=True)
    cam_line = [ln for ln in open(os.path.join(a.calib, "sparse", "0", "cameras.txt")) if ln[0] != "#" and ln.strip()][0]
    cam_id = int(cam_line.split()[0])
    open(os.path.join(tri_in, "cameras.txt"), "w").write(cam_line)
    with open(os.path.join(tri_in, "images.txt"), "w") as f:
        for k in keep:
            n = order[k]; Rcw = (Rg @ Rw(pts[n])).T; tcw = -Rcw @ (Rg @ C[k])
            q = Rot.from_matrix(Rcw).as_quat()                        # x y z w
            f.write(f"{ids[n]} {q[3]} {q[0]} {q[1]} {q[2]} {tcw[0]} {tcw[1]} {tcw[2]} {cam_id} {n}.jpg\n\n")
    open(os.path.join(tri_in, "points3D.txt"), "w").write("")
    json.dump(dict(pairs=len(rows), directions=len(edges_raw), main_set=len(order), kept=len(keep), imu=a.imu,
                   gravity=(g_vec.tolist() if a.imu else None), metric=bool(a.imu),
                   edge_residual_deg_median=float(np.median(ang)), max_dt=a.max_dt, min_parallax=a.min_parallax),
              open(os.path.join(OUT, "rot_sfm.json"), "w"), indent=1)

    def colmap(*args_):
        r_ = subprocess.run([a.colmap, *map(str, args_)], capture_output=True, text=True)
        if r_.returncode:
            print(r_.stdout[-2000:], r_.stderr[-2000:]); sys.exit(f"colmap {args_[0]} failed")
    if a.no_ba:
        sys.exit(0)
    sp = os.path.join(OUT, "sparse", "0"); os.makedirs(sp, exist_ok=True)
    colmap("point_triangulator", "--database_path", os.path.join(OUT, "database.db"), "--image_path",
           os.path.join(a.work, "images"), "--input_path", tri_in, "--output_path", sp)
    if not a.triangulate_only:
        colmap("bundle_adjuster", "--input_path", sp, "--output_path", sp)
    colmap("model_converter", "--input_path", sp, "--output_path", sp, "--output_type", "TXT")
    print(f"wrote {sp}")
