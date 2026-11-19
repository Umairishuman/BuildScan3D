"""Gyro bias from image pairs far apart in time (loop closures), for captures where SfM itself is unreliable.

gyro_check.py estimates the gyro bias against the SfM model's rotations over 1 s windows; when the model is locally
wrong (scan_009) that estimate is off by a few hundredths of a degree per second, which adds up to a heading drift of
~14 deg over a 3-minute walk (R-053). Here every verified image pair in the COLMAP database gives its own relative
rotation (5-point essential matrix, RANSAC); each one is noisy (scan_009: 3.3 deg median even for pairs < 5 s apart)
but they are independent of each other and of the SfM model, and pairs minutes apart see the accumulated drift.
The bias correction (3 numbers, IMU frame) that makes the integrated gyro agree with all pairs is fitted with a robust
(Cauchy) loss.

  python gyro_loop_bias.py <dataset> <work with frames.json> <calib dir with sparse/0 and database.db> [--out bias.json]

Prints the residual per time-gap bin before and after, and writes {"bg": [...] (rad/s, IMU frame, total), ...} for
rot_sfm.py --bg_json.
"""
import os, sys, json, sqlite3, argparse
import numpy as np, cv2
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation as R

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gyro_check import check                                   # noqa: E402
from common import Capture                                     # noqa: E402
from known_rot_pnp import load_model                           # noqa: E402

PAIR = 2147483647
F = np.diag([1.0, -1.0, -1.0])


class FastOrientation:
    """IMU orientation over the capture at 400 Hz, re-integrable quickly for a changed bias (quaternion cumprod)."""

    def __init__(self, imu, off, t0, t1, rate=400.0):
        self.rate = rate
        self.tt = np.arange(t0, t1 + 1 / rate, 1 / rate)
        self.w = imu.gyro(self.tt[:-1] + 0.5 / rate + off)

    def build(self, bg):
        bg = np.asarray(bg, float)
        b = bg[None] if bg.ndim == 1 else bg                                        # constant or per sample
        steps = R.from_rotvec((self.w - b) / self.rate).as_quat()                  # x y z w
        q = np.empty((len(steps) + 1, 4)); q[0] = [0, 0, 0, 1]
        cur = R.identity()
        # chunked cumulative product: exact, fast enough (~76k steps)
        Rs = R.from_quat(steps)
        out = [cur]
        for k in range(0, len(steps), 2000):
            blk = Rs[k:k + 2000]
            # prefix products inside the block
            acc = [cur * blk[0]]
            for j in range(1, len(blk)):
                acc.append(acc[-1] * blk[j])
            out.extend(acc); cur = acc[-1]
        self.Q = R.from_quat(np.array([o.as_quat() for o in out]))
        return self

    def idx(self, t):
        return np.clip(np.round((np.asarray(t) - self.tt[0]) * self.rate).astype(int), 0, len(self.tt) - 1)


def five_point_pairs(calib, names_ok, pts, min_inliers=40, min_ep=30):
    db = sqlite3.connect(os.path.join(calib, "database.db"))
    names = {i: os.path.splitext(n)[0] for i, n in db.execute("select image_id, name from images")}
    kps = {i: np.frombuffer(d, np.float32).reshape(r, c)[:, :2]
           for i, r, c, d in db.execute("select image_id, rows, cols, data from keypoints") if r > 0}
    cam = [l for l in open(os.path.join(calib, "sparse", "0", "cameras.txt")) if l[0] != "#" and l.strip()][0].split()
    fx, fy, cx, cy, k1, k2, p1, p2 = map(float, cam[4:12])
    K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1.0]]); dist = np.array([k1, k2, p1, p2])
    out = []
    for pid, r, d in db.execute("select pair_id, rows, data from two_view_geometries where rows >= ?", (min_inliers,)):
        i2 = pid % PAIR; i1 = (pid - i2) // PAIR
        a, b = names[i1], names[i2]
        if a not in names_ok or b not in names_ok:
            continue
        m = np.frombuffer(d, np.uint32).reshape(r, 2)
        x1 = cv2.undistortPoints(kps[i1][m[:, 0]].reshape(-1, 1, 2).astype(np.float64), K, dist)
        x2 = cv2.undistortPoints(kps[i2][m[:, 1]].reshape(-1, 1, 2).astype(np.float64), K, dist)
        E, inl = cv2.findEssentialMat(x1, x2, np.eye(3), cv2.RANSAC, 0.999, 1.0 / fx)
        if E is None or E.shape != (3, 3):
            continue
        n, Rab, _, _ = cv2.recoverPose(E, x1, x2, np.eye(3), mask=inl)
        if n < min_ep:
            continue
        out.append((pts[a], pts[b], Rab, n))
    return out


def residuals(orient, Rci, pairs, bg):
    orient.build(bg)
    ta = np.array([p[0] for p in pairs]); tb = np.array([p[1] for p in pairs])
    Qa = orient.Q[orient.idx(ta)]; Qb = orient.Q[orient.idx(tb)]
    rel = (Qa.inv() * Qb).as_matrix()                                    # IMU a -> b
    rel_cam = np.einsum("ij,njk,kl->nil", F @ Rci, rel, Rci.T @ F)
    Rg = np.transpose(rel_cam, (0, 2, 1))                                # cam_b <- cam_a
    Rab = np.stack([p[2] for p in pairs])
    return R.from_matrix(np.einsum("nij,nkj->nik", Rab, Rg)).as_rotvec()  # (n, 3) rad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset"); ap.add_argument("work"); ap.add_argument("calib")
    ap.add_argument("--out", default=None)
    ap.add_argument("--min_dt", type=float, default=0.0, help="use only pairs at least this far apart (s)")
    ap.add_argument("--scale_deg", type=float, default=3.0, help="Cauchy loss scale (deg)")
    ap.add_argument("--linear", action="store_true", help="bias changing linearly over the capture (6 numbers)")
    a = ap.parse_args()
    meta = json.load(open(os.path.join(a.work, "frames.json")))
    off_p = meta.get("pose_offset", 0.0)
    pts = {f["name"]: f["pts"] + off_p for f in meta["frames"]}
    imgs0, _, _ = load_model(os.path.join(a.calib, "sparse", "0"))
    rep = check(a.dataset, meta["frames"], {n: v[0] for n, v in imgs0.items()}, Capture(a.dataset).t0_ns, off_p)
    bg0 = np.asarray(rep["bg"], float)
    cache = os.path.join(a.calib, "five_point_pairs.npz")
    if os.path.exists(cache):
        z = np.load(cache); allp = [(x[0], x[1], r_, int(x[2])) for x, r_ in zip(z["t"], z["R"])]
    else:
        allp = five_point_pairs(a.calib, set(pts), pts)
        np.savez(cache, t=np.array([(p[0], p[1], p[3]) for p in allp]), R=np.stack([p[2] for p in allp]))
    pairs = [p for p in allp if abs(p[1] - p[0]) >= a.min_dt]
    print(f"{len(pairs)} image pairs with a 5-point rotation")
    orient = FastOrientation(rep["imu"], rep["off"], min(pts.values()) - 1, max(pts.values()) + 1)
    dts = np.array([abs(p[1] - p[0]) for p in pairs])
    s = np.radians(a.scale_deg)

    def report(tag, bg):
        e = np.degrees(np.linalg.norm(residuals(orient, rep["Rci"], pairs, bg), axis=1))
        txt = []
        for lo, hi in [(0, 5), (5, 20), (20, 60), (60, 120), (120, 1e9)]:
            m = (dts >= lo) & (dts < hi)
            if m.any():
                txt.append(f"{lo:g}-{hi if hi < 1e8 else 'end'} s: {m.sum()} pairs median {np.median(e[m]):.2f}")
        b_ = np.degrees(np.asarray(bg)); b_ = b_ if b_.ndim == 1 else b_[[0, -1]]
        print(f"{tag}: bias {b_.round(4).tolist()} deg/s | " + " | ".join(txt), flush=True)
        return e

    report("before (gyro_check bias)", bg0)
    tm = 0.5 * (orient.tt[0] + orient.tt[-1]); T = 0.5 * (orient.tt[-1] - orient.tt[0])
    u = ((orient.tt[:-1] - tm) / T)[:, None]                                     # -1 .. 1 over the capture

    def bias_of(d):
        if not a.linear:
            return bg0 + d[:3] * 1e-3
        return bg0[None] + d[None, :3] * 1e-3 + u * d[None, 3:] * 1e-3
    fun = lambda d: residuals(orient, rep["Rci"], pairs, bias_of(d)).ravel() / s
    sol = least_squares(fun, np.zeros(6 if a.linear else 3), loss="cauchy", f_scale=1.0, diff_step=1e-1)
    bg1 = bias_of(sol.x)
    e1 = report("after (loop fit" + (", linear in time)" if a.linear else ")"), bg1)
    out = dict(bg=(bg0 + sol.x[:3] * 1e-3).tolist(), bg_slope=(sol.x[3:] * 1e-3).tolist() if a.linear else None,
               t_mid=float(tm), t_half=float(T), bg_gyro_check=bg0.tolist(),
               delta_deg_s=np.degrees(sol.x[:3] * 1e-3).tolist(), pairs=len(pairs), residual_deg_median=float(np.median(e1)))
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)
        print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
