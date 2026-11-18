"""Metric scale of an SfM model from the phone's accelerometer (no ARCore tracking needed).

FEATURELESS_TRACKING_PLAN §5 option 2. SfM camera positions p(t) are in arbitrary units; the accelerometer measures
specific force f in the IMU frame. With the camera rotations from SfM and the IMU->camera rotation from the gyro
check (gyro_check.py), for every time t:

    s * p''(t) + g + R_wi(t) b_a = R_wi(t) f(t)        (R_wi = R_wc_gl(t) @ Rci, world = SfM world)

is LINEAR in the unknowns: scale s (m per model unit), gravity g in the SfM world (3) and accelerometer bias b_a (3).
Solved both ways (forward: p'' as regressor, biased low by its noise; inverse: p'' = k R f + ..., biased high) and
combined as their geometric mean (reduced major axis). newRoom: forward 0.621, inverse 0.718, ARCore Sim3 0.668.
p'' comes from a smoothing spline through the keyframe positions; both sides are low-passed with the same Gaussian, so
the fit only uses motion the keyframes resolve. Only stretches without gaps between accepted keyframes are used.
|g| is not constrained in the fit; its fitted length (should be ~9.81) is a sanity check.

  python src/arcore3dgs/imu_scale.py <dataset> <keyframe dir> <COLMAP model dir> [--max_gap 0.5] [--sigma 0.25]
As a module: estimate(dataset, frames, c2w (name -> 4x4 OpenCV c2w, model world), t0_ns, rep_gyro) -> dict.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.interpolate import make_smoothing_spline
from scipy.ndimage import gaussian_filter1d
from scipy.spatial.transform import Rotation as R, Slerp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

F = np.diag([1.0, -1.0, -1.0])


def estimate(frames, c2w, rep, pose_offset=0.0, max_gap=0.5, sigma=0.25, rate=100.0, min_len=2.0, verbose=True):
    imu, Rci, off = rep["imu"], rep["Rci"], rep["off"]
    reg = sorted([f for f in frames if f["name"] in c2w], key=lambda f: f["pts"])
    t = np.array([f["pts"] + pose_offset for f in reg])
    P = np.array([c2w[f["name"]][:3, 3] for f in reg])
    Rgl = R.from_matrix(np.array([c2w[f["name"]][:3, :3] @ F for f in reg]))     # camera(GL) -> world
    # continuous stretches
    cuts = np.where(np.diff(t) > max_gap)[0]
    segs = np.split(np.arange(len(t)), cuts + 1)
    rows_A, rows_b, used = [], [], 0.0
    for sidx in segs:
        if len(sidx) < 8 or t[sidx[-1]] - t[sidx[0]] < min_len:
            continue
        ts = t[sidx]
        tt = np.arange(ts[0], ts[-1], 1 / rate)
        acc = np.zeros((len(tt), 3))
        for k in range(3):
            sp = make_smoothing_spline(ts, P[sidx, k], lam=None)
            acc[:, k] = sp.derivative(2)(tt)
        Rw = Slerp(ts, Rgl[sidx])(tt).as_matrix() @ Rci                            # IMU -> world
        f = imu.accel(tt + off)
        rf = np.einsum("nij,nj->ni", Rw, f)
        sg = sigma * rate
        acc = gaussian_filter1d(acc, sg, axis=0); rf = gaussian_filter1d(rf, sg, axis=0)
        Rw_f = gaussian_filter1d(Rw.reshape(len(tt), 9), sg, axis=0).reshape(-1, 3, 3)
        trim = int(2 * sg)                                                          # filter edge effects
        sl = slice(trim, len(tt) - trim)
        if sl.stop - sl.start < 10:
            continue
        n = sl.stop - sl.start
        Rf = Rw_f[sl]
        rows_A.append((acc[sl], rf[sl], Rf)); rows_b.append(None)
        used += n / rate
    if not rows_A:
        raise ValueError("no continuous stretch long enough")

    def fit(segs_):
        """Forward (s p'' = R f - g - R b_a, regressor p'') and inverse (p'' = k R f + ..., regressor R f) least squares.
        Noise in p'' biases the forward scale low and the inverse one high; their geometric mean is the
        reduced-major-axis estimate used when both sides are noisy."""
        acc_ = np.concatenate([a_ for a_, _, _ in segs_]); rf_ = np.concatenate([r_ for _, r_, _ in segs_])
        Rf_ = np.concatenate([q_ for _, _, q_ in segs_]); n_ = len(acc_)
        out_ = []
        for X, y in ((acc_, rf_), (rf_, acc_)):
            A = np.zeros((n_, 3, 7)); A[:, :, 0] = X; A[:, :, 1:4] = np.eye(3)[None]; A[:, :, 4:7] = Rf_
            A = A.reshape(-1, 7); b = y.reshape(-1)
            x = np.linalg.lstsq(A, b, rcond=None)[0]
            keep = np.abs(A @ x - b) < np.percentile(np.abs(A @ x - b), 80)        # drop the worst 20% rows
            out_.append(np.linalg.lstsq(A[keep], b[keep], rcond=None)[0])
        fwd, inv = out_
        return float(fwd[0]), float(1 / inv[0]), fwd

    s_fwd, s_inv, xf = fit(rows_A)
    out = dict(scale=float(np.sqrt(s_fwd * s_inv)), scale_forward=s_fwd, scale_inverse=s_inv,
               gravity_norm=float(np.linalg.norm(xf[1:4])), accel_bias=xf[4:7].tolist(),
               seconds_used=float(used), stretches=len(rows_A))
    if len(rows_A) >= 3:                       # bootstrap over stretches: spread of the combined scale
        rng = np.random.default_rng(0); sc = []
        for _ in range(100):
            f_, i_, _ = fit([rows_A[k] for k in rng.integers(0, len(rows_A), len(rows_A))])
            sc.append(np.sqrt(f_ * i_))
        out["scale_p5_p95"] = [float(np.percentile(sc, 5)), float(np.percentile(sc, 95))]
    if verbose:
        p5 = out.get("scale_p5_p95", [np.nan, np.nan])
        print(f"IMU scale: {out['scale']:.4f} m per model unit (forward {s_fwd:.4f}, inverse {s_inv:.4f}; bootstrap "
              f"p5-p95 {p5[0]:.4f}-{p5[1]:.4f}), |g| fitted {out['gravity_norm']:.2f} m/s^2, {len(rows_A)} stretches, "
              f"{used:.0f} s used")
    return out


def estimate_preint(frames, c2w, rep, pose_offset=0.0, T=1.0, max_gap=0.5, rate=400.0, verbose=True, return_rows=False, gyro_orient=False):
    """Visual-inertial scale with pre-integrated accelerometer over keyframe triplets (i, j, k), j - i ~ k - j ~ T s
    (the linear initialisation of VINS-type systems). With alpha / beta the double / single integral of R_wi f and
    J_alpha / J_beta the same integrals of R_wi (for the bias), velocity eliminated:

        s [(p_k - p_j) - (T2/T1)(p_j - p_i)] - g T2 (T1+T2)/2 + (J_a,jk - (T2/T1) J_a,ij + T2 J_b,ij) b_a
            = alpha_jk - (T2/T1) alpha_ij + T2 beta_ij

    Linear in s, gravity g (world) and bias b_a. Positions enter as ~1 s differences, not second derivatives."""
    imu, Rci, off = rep["imu"], rep["Rci"], rep["off"]
    reg = sorted([f for f in frames if f["name"] in c2w], key=lambda f: f["pts"])
    t = np.array([f["pts"] + pose_offset for f in reg])
    P = np.array([c2w[f["name"]][:3, 3] for f in reg])
    Rgl = R.from_matrix(np.array([c2w[f["name"]][:3, :3] @ F for f in reg]))

    def integ(ta, tb, sl):
        tt = np.arange(ta, tb, 1 / rate); dt = 1 / rate
        Rw = sl(np.clip(tt, t[0], t[-1])).as_matrix() @ Rci
        rf = np.einsum("nij,nj->ni", Rw, imu.accel(tt + off))
        beta = np.cumsum(rf, 0) * dt; Jb = np.cumsum(Rw, 0) * dt
        alpha = np.sum(beta, 0) * dt; Ja = np.sum(Jb, 0) * dt
        return alpha, beta[-1], Ja, Jb[-1]

    if gyro_orient:
        # world <- IMU rotation from the gyro (smooth, accurate to a fraction of a degree over seconds), aligned to the
        # SfM world once per continuous stretch (chordal mean over its frames). SfM rotations of a poor capture can be
        # off by ~1-2 deg, which leaks 0.2-0.3 m/s^2 of gravity into the acceleration.
        from gyro_pairs import Orientation
        orient = Orientation(imu, off, t[0] - 1, t[-1] + 1)
        Rwi_sfm = Rgl.as_matrix() @ Rci
        cuts = np.where(np.diff(t) > max_gap)[0]
        seg_of = np.zeros(len(t), int)
        for c_ in cuts:
            seg_of[c_ + 1:] += 1
        align = {}
        for sg_ in np.unique(seg_of):
            M = sum(Rwi_sfm[k] @ orient.at(t[k]).as_matrix().T for k in np.where(seg_of == sg_)[0])
            U, _, Vt = np.linalg.svd(M); align[sg_] = U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt

        class _Sl:
            def __init__(self, sg_):
                self.A = align[sg_]

            def __call__(self, tt):
                return R.from_matrix(np.array([self.A @ orient.at(x).as_matrix() for x in tt]) @ Rci.T)
    slerp = Slerp(t, Rgl)
    rows, rhs, n_trip, t_mid = [], [], 0, []
    for i in range(len(t)):
        j = np.searchsorted(t, t[i] + T)
        if j >= len(t):
            break
        k = np.searchsorted(t, t[j] + T)
        if k >= len(t):
            break
        if np.max(np.diff(t[i:k + 1])) > max_gap:
            continue
        T1, T2 = t[j] - t[i], t[k] - t[j]
        if abs(T1 - T) > 0.3 or abs(T2 - T) > 0.3:
            continue
        sl_ = _Sl(seg_of[i]) if gyro_orient else slerp
        a_ij, b_ij, Ja_ij, Jb_ij = integ(t[i], t[j], sl_)
        a_jk, _, Ja_jk, _ = integ(t[j], t[k], sl_)
        D = (P[k] - P[j]) - (T2 / T1) * (P[j] - P[i])
        A = np.zeros((3, 7))
        A[:, 0] = D
        A[:, 1:4] = -np.eye(3) * T2 * (T1 + T2) / 2
        A[:, 4:7] = Ja_jk - (T2 / T1) * Ja_ij + T2 * Jb_ij
        rows.append(A); rhs.append(a_jk - (T2 / T1) * a_ij + T2 * b_ij); n_trip += 1; t_mid.append(t[j])
    if n_trip < 20:
        raise ValueError(f"only {n_trip} keyframe triplets")
    A = np.vstack(rows); b = np.concatenate(rhs)
    if return_rows:
        return dict(A=A, b=b, t_mid=np.array(t_mid))
    x = np.linalg.lstsq(A, b, rcond=None)[0]
    for _ in range(2):                                   # trim the worst 20% triplets (fast motion, sync errors)
        r = np.linalg.norm((A @ x - b).reshape(-1, 3), axis=1)
        keep = np.repeat(r < np.percentile(r, 80), 3)
        x = np.linalg.lstsq(A[keep], b[keep], rcond=None)[0]
    out = dict(scale=float(x[0]), gravity_norm=float(np.linalg.norm(x[1:4])), accel_bias=x[4:7].tolist(),
               triplets=n_trip, window_s=T)
    rng = np.random.default_rng(0); sc = []
    blocks = np.array_split(np.arange(n_trip), max(3, n_trip // 20))      # bootstrap over blocks of triplets
    for _ in range(200):
        pick = np.concatenate([blocks[q] for q in rng.integers(0, len(blocks), len(blocks))])
        idx = (pick[:, None] * 3 + np.arange(3)).ravel()
        sc.append(np.linalg.lstsq(A[idx], b[idx], rcond=None)[0][0])
    out["scale_p5_p95"] = [float(np.percentile(sc, 5)), float(np.percentile(sc, 95))]
    if verbose:
        print(f"IMU scale (pre-integrated, {T:.1f} s): {out['scale']:.4f} m per model unit (bootstrap p5-p95 "
              f"{out['scale_p5_p95'][0]:.4f}-{out['scale_p5_p95'][1]:.4f}), |g| fitted {out['gravity_norm']:.2f} m/s^2, "
              f"{n_trip} triplets")
    return out


if __name__ == "__main__":
    from gyro_check import check, read_images_txt  # noqa: F401
    from known_rot_pnp import load_model
    from common import Capture
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset"); ap.add_argument("work"); ap.add_argument("model")
    ap.add_argument("--max_gap", type=float, default=0.5)
    ap.add_argument("--gyro_orient", action="store_true", help="rotate the accelerometer with the gyro orientation")
    ap.add_argument("--windows", type=float, nargs="+", default=[1.0], help="pre-integration window(s), s")
    ap.add_argument("--gyro_thr", type=float, default=2.0, help="only frames the gyro check accepts")
    a = ap.parse_args()
    meta = json.load(open(os.path.join(a.work, "frames.json")))
    imgs, _, _ = load_model(a.model)
    rep = check(a.dataset, meta["frames"], {n: v[0] for n, v in imgs.items()}, Capture(a.dataset).t0_ns,
                meta.get("pose_offset", 0.0), thr_deg=a.gyro_thr)
    good = set(imgs) - set(rep["flagged"])
    c2w = {}
    for n in good:
        M = np.eye(4); M[:3, :3] = imgs[n][0]; M[:3, 3] = imgs[n][1]; c2w[n] = M
    for T in a.windows:
        estimate_preint(meta["frames"], c2w, rep, meta.get("pose_offset", 0.0), T=T, max_gap=a.max_gap,
                        gyro_orient=a.gyro_orient)
