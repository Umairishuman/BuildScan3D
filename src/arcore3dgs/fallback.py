"""Featureless-tracking fallback: bridge ARCore tracking losses with the IMU, re-align on re-tracking.

When ARCore loses tracking (plain walls / ceiling -> INSUFFICIENT_FEATURES) the video keeps recording but
there are no poses. This module estimates those poses in a lower-confidence "fallback" mode:

  1. calibration (from the tracked parts): IMU->camera rotation and time offset (gyro vs ARCore
     angular velocity, Kabsch), gyro bias, accelerometer bias
  2. bridging each gap [A, B]: A = last trusted pose before the loss, B = first *settled* pose after
     re-tracking (ARCore relocalises against the familiar map; poses right after it are unreliable)
       rotation: gyro integrated forward from A and backward from B, slerp-blended (drift spread)
       position: accelerometer double-integrated from A's position/velocity, then the minimal cubic
                 correction that matches B's position AND velocity (re-alignment on re-tracking)
  3. validation: simulated gaps cut out of well-tracked stretches, bridged and compared with ARCore,
     against plain interpolation (baseline)

Output: <dataset>/poses_fallback.csv (same 12 columns as poses.csv, 100 Hz inside the gaps) and
<dataset>/fallback_report.json. common.Capture merges these poses (flagged as fallback) when present.
Run: python src/arcore3dgs/fallback.py <dataset_dir>
"""
import os, sys, json
import numpy as np
from scipy.spatial.transform import Rotation as R, Slerp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from imu import extract_imu

G_WORLD = np.array([0.0, 9.81, 0.0])          # ARCore world is +Y up; accelerometer reads +g upward at rest
SETTLE = 1.5                                   # s after re-tracking before ARCore poses are trusted again
CAM_GL_TO_CV = np.diag([1.0, -1.0, -1.0])


def load_poses(root):
    P = np.loadtxt(os.path.join(root, "poses.csv"), delimiter=",")
    P = P[np.argsort(P[:, 0], kind="stable")]
    P = P[np.unique(P[:, 0], return_index=True)[1]]
    return P


def load_lost(root, t0):
    ts, ok = [], []
    for line in open(os.path.join(root, "tracking.csv")):
        p = line.strip().split(",")
        if len(p) >= 2 and p[0].isdigit():
            ts.append(int(p[0])); ok.append(p[1] == "TRACKING")
    ts = (np.array(ts, dtype=np.float64) - t0) / 1e9; ok = np.array(ok)
    segs, i = [], 0
    while i < len(ok):
        if not ok[i]:
            j = i
            while j < len(ok) and not ok[j]:
                j += 1
            segs.append((ts[i], ts[min(j, len(ts) - 1)]))
            i = j
        else:
            i += 1
    return segs


class Imu:
    def __init__(self, root, t0_ns):
        d = extract_imu(root)
        self.gt = (d["gyro"][0] - t0_ns) / 1e9; self.g = d["gyro"][1]
        self.at = (d["accel"][0] - t0_ns) / 1e9; self.a = d["accel"][1]

    def gyro(self, t):
        return np.stack([np.interp(t, self.gt, self.g[:, k]) for k in range(3)], -1)

    def accel(self, t):
        return np.stack([np.interp(t, self.at, self.a[:, k]) for k in range(3)], -1)


def smooth(x, n):
    k = np.ones(n) / n
    return np.stack([np.convolve(x[:, i], k, mode="same") for i in range(x.shape[1])], 1)


def calibrate(t, pos, rot, imu, lost):
    """IMU->camera rotation R_ci (camera = ARCore OpenGL camera frame), time offset, gyro/accel biases."""
    ok_t = np.ones(len(t), bool)
    for a, b in lost:
        ok_t &= ~((t > a - 1.0) & (t < b + SETTLE + 1.0))
    dt = np.diff(t)
    w_cam = (rot[:-1].inv() * rot[1:]).as_rotvec() / np.maximum(dt, 1e-4)[:, None]   # body rates, camera frame
    tm = (t[:-1] + t[1:]) / 2
    m = ok_t[:-1] & ok_t[1:] & (dt > 0.02) & (dt < 0.06)
    best = None
    for off in np.arange(-0.06, 0.0601, 0.002):
        wi = smooth(imu.gyro(tm + off), 1)
        sel = m & (np.linalg.norm(w_cam, axis=1) > 0.15)
        A, B = wi[sel], w_cam[sel]
        H = A.T @ B
        U, _, Vt = np.linalg.svd(H)
        D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
        Rci = Vt.T @ D @ U.T                                  # w_cam = Rci @ w_imu
        res = np.median(np.linalg.norm(B - A @ Rci.T, axis=1))
        if best is None or res < best[0]:
            best = (res, off, Rci)
    res, off, Rci = best
    wi = imu.gyro(tm[m] + off)
    bg = np.median(wi - w_cam[m] @ Rci, axis=0)               # gyro bias in IMU frame
    # accelerometer bias: ARCore acceleration (smoothed 2nd derivative) vs IMU specific force in world
    ts = np.arange(t[0] + 1, t[-1] - 1, 0.02)
    ps = np.stack([np.interp(ts, t, pos[:, k]) for k in range(3)], 1)
    ps = smooth(ps, 9)
    acc_w = np.gradient(np.gradient(ps, 0.02, axis=0), 0.02, axis=0)
    okm = np.ones(len(ts), bool)
    for a, b in lost:
        okm &= ~((ts > a - 1.5) & (ts < b + SETTLE + 1.5))
    okm[:20] = okm[-20:] = False
    Rwc = Slerp(t, rot)(ts).as_matrix()
    f = imu.accel(ts + off)
    # model: acc_w = Rwc Rci (f - ba) - g  ->  Rwc Rci ba = Rwc Rci f - g - acc_w
    A = np.einsum("nij,jk->nik", Rwc, Rci)[okm]
    y = (np.einsum("nij,nj->ni", A, f[okm]) - G_WORLD - acc_w[okm])
    ba = np.linalg.lstsq(A.reshape(-1, 3), y.reshape(-1), rcond=None)[0]
    corr = np.corrcoef(np.linalg.norm(w_cam[m], axis=1), np.linalg.norm(imu.gyro(tm[m] + off) - bg, axis=1))[0, 1]
    return dict(Rci=Rci, off=off, bg=bg, ba=ba, gyro_residual=res, gyro_corr=corr)


def bridge(t_a, t_b, pose_at, vel_at, imu, cal, rate=100.0):
    """Fallback poses between trusted anchors A (t_a) and B (t_b). Returns times, positions, rotations."""
    Rci, off, bg, ba = cal["Rci"], cal["off"], cal["bg"], cal["ba"]
    ts = np.arange(t_a, t_b + 1e-9, 1.0 / rate)
    if ts[-1] < t_b:
        ts = np.append(ts, t_b)
    pA, RA = pose_at(t_a); pB, RB = pose_at(t_b)
    vA, vB = vel_at(t_a), vel_at(t_b)
    w = (imu.gyro(ts + off) - bg) @ Rci.T                   # camera-frame body rates
    n = len(ts)
    fwd = [RA]
    for k in range(n - 1):
        fwd.append(fwd[-1] * R.from_rotvec(w[k] * (ts[k + 1] - ts[k])))
    bwd = [RB]
    for k in range(n - 1, 0, -1):
        bwd.append(bwd[-1] * R.from_rotvec(-w[k - 1] * (ts[k] - ts[k - 1])))
    bwd = bwd[::-1]
    s = np.clip((ts - t_a) / max(t_b - t_a, 1e-6), 0.0, 1.0)
    rots = []
    for k in range(n):
        pair = R.from_quat(np.stack([fwd[k].as_quat(), bwd[k].as_quat()]))
        rots.append(Slerp([0, 1], pair)([s[k]])[0])
    closure_deg = np.degrees((fwd[-1].inv() * RB).magnitude())
    Rw = R.from_quat(np.stack([r.as_quat() for r in rots])).as_matrix()
    acc = np.einsum("nij,nj->ni", Rw @ Rci, imu.accel(ts + off) - ba) - G_WORLD
    v = np.zeros((n, 3)); p = np.zeros((n, 3)); v[0], p[0] = vA, pA
    for k in range(n - 1):
        h = ts[k + 1] - ts[k]
        v[k + 1] = v[k] + 0.5 * (acc[k] + acc[k + 1]) * h
        p[k + 1] = p[k] + 0.5 * (v[k] + v[k + 1]) * h
    T = ts[-1] - ts[0]
    ep, ev = pB - p[-1], vB - v[-1]
    # cubic correction dp(t) = c2 t^2 + c3 t^3 with dp(T) = ep, dp'(T) = ev  (dp(0) = dp'(0) = 0)
    c3 = (ev * T - 2 * ep) / T ** 3
    c2 = (ep - c3 * T ** 3) / T ** 2
    tt = (ts - ts[0])[:, None]
    p_corr = p + c2 * tt ** 2 + c3 * tt ** 3
    drift_m = float(np.linalg.norm(ep))
    return ts, p_corr, R.from_quat(np.stack([r.as_quat() for r in rots])), closure_deg, drift_m


def forward_positions(ts, rots, pA, vA, vB, imu, cal):
    """Accelerometer integration from A, with a constant acceleration correction so the velocity at the end
    matches vB (velocity is known after re-tracking even if ARCore's position frame jumped)."""
    Rw = rots.as_matrix()
    acc = np.einsum("nij,nj->ni", Rw @ cal["Rci"], imu.accel(ts + cal["off"]) - cal["ba"]) - G_WORLD
    n = len(ts); v = np.zeros((n, 3)); p = np.zeros((n, 3)); v[0], p[0] = vA, pA
    for k in range(n - 1):
        h = ts[k + 1] - ts[k]
        v[k + 1] = v[k] + 0.5 * (acc[k] + acc[k + 1]) * h
        p[k + 1] = p[k] + 0.5 * (v[k] + v[k + 1]) * h
    T = ts[-1] - ts[0]
    da = (vB - v[-1]) / T
    tt = (ts - ts[0])[:, None]
    return p + 0.5 * da * tt ** 2


def gyro_forward(ts, RA, imu, cal):
    w = (imu.gyro(ts + cal["off"]) - cal["bg"]) @ cal["Rci"].T
    out = [RA]
    for k in range(len(ts) - 1):
        out.append(out[-1] * R.from_rotvec(w[k] * (ts[k + 1] - ts[k])))
    return R.from_quat(np.stack([r.as_quat() for r in out]))


def main(root):
    P = load_poses(root)
    t0 = P[0, 0]; t = (P[:, 0] - t0) / 1e9
    pos = P[:, 1:4]; rot = R.from_quat(P[:, 4:8]); intr = P[:, 8:12].mean(0)
    lost = load_lost(root, t0)
    imu = Imu(root, t0)
    slerp = Slerp(t, rot)

    def pose_at(tq):
        return np.array([np.interp(tq, t, pos[:, k]) for k in range(3)]), slerp([tq])[0]

    def vel_at(tq, h=0.15):
        # one-sided next to a tracking gap: a central difference would interpolate straight across the hole
        lo, hi = tq - h, tq + h
        for la, lb in lost:
            if tq <= la + 0.05 and hi > la - 0.05:      # gap starts just after tq -> use the past only
                lo, hi = tq - 2 * h, tq
            if tq >= lb - 0.05 and lo < lb + 0.05:      # gap ended just before tq -> use the future only
                lo, hi = tq, tq + 2 * h
        a = np.array([np.interp(lo, t, pos[:, k]) for k in range(3)])
        b = np.array([np.interp(hi, t, pos[:, k]) for k in range(3)])
        return (b - a) / (hi - lo)

    cal = calibrate(t, pos, rot, imu, lost)
    print(f"calibration: IMU->camera rotation fitted (median gyro residual {cal['gyro_residual']:.3f} rad/s, "
          f"|w| correlation {cal['gyro_corr']:.2f}), time offset {cal['off'] * 1000:+.0f} ms, "
          f"gyro bias {np.round(cal['bg'], 4)}, accel bias {np.round(cal['ba'], 3)}")

    # ---- validation on simulated gaps in well-tracked stretches ----
    rng = np.random.default_rng(0)
    report = {"calibration": {"R_ci": cal["Rci"].tolist(), "time_offset_s": cal["off"], "gyro_bias": cal["bg"].tolist(),
                              "accel_bias": cal["ba"].tolist(), "gyro_residual": cal["gyro_residual"]}, "validation": {}}
    print("\nvalidation on simulated gaps (ARCore poses removed, bridged, compared with ARCore):")
    print(f"{'gap':>5s} {'n':>3s} | {'IMU fallback: pos median / max':>32s} {'rot median':>10s} | {'interpolation: pos median / max':>32s} {'rot median':>10s}")
    for L in (2.0, 5.0, 9.0):
        e_imu, e_lin, r_imu, r_lin, e_fwd = [], [], [], [], []
        tries = 0
        while len(e_imu) < 25 and tries < 2000:
            tries += 1
            a = rng.uniform(t[0] + 3, t[-1] - L - 3)
            b = a + L
            if any(not (b + SETTLE + 2 < la or a - 2 > lb) for la, lb in lost):
                continue
            ts, pf, rf, _, _ = bridge(a, b, pose_at, vel_at, imu, cal)
            gt_p = np.stack([np.interp(ts, t, pos[:, k]) for k in range(3)], 1)
            gt_r = slerp(ts)
            e_imu.append(np.linalg.norm(pf - gt_p, axis=1).max())
            r_imu.append(np.degrees((rf.inv() * gt_r).magnitude()).max())
            pa, ra = pose_at(a); pb, rb = pose_at(b)
            s = ((ts - a) / L)[:, None]
            pl = pa + s * (pb - pa)
            rl = Slerp([a, b], R.from_quat(np.stack([ra.as_quat(), rb.as_quat()])))(np.clip(ts, a, b))
            e_lin.append(np.linalg.norm(pl - gt_p, axis=1).max())
            rg = gyro_forward(ts, pa_r := pose_at(a)[1], imu, cal)
            pfw = forward_positions(ts, rg, pa, vel_at(a), vel_at(b), imu, cal)
            e_fwd.append(np.linalg.norm(pfw - gt_p, axis=1).max())
            r_lin.append(np.degrees((rl.inv() * gt_r).magnitude()).max())
        e_imu, e_lin, r_imu, r_lin, e_fwd = map(np.array, (e_imu, e_lin, r_imu, r_lin, e_fwd))
        print(f"{L:4.0f}s {len(e_imu):3d} | {np.median(e_imu) * 100:14.1f} cm / {e_imu.max() * 100:5.1f} cm {np.median(r_imu):8.2f} deg |"
              f" {np.median(e_lin) * 100:14.1f} cm / {e_lin.max() * 100:5.1f} cm {np.median(r_lin):8.2f} deg |"
              f" forward-only (jump case): {np.median(e_fwd) * 100:.1f} / {e_fwd.max() * 100:.1f} cm")
        report["validation"][f"{L:.0f}s"] = dict(n=int(len(e_imu)), imu_pos_cm_median=float(np.median(e_imu) * 100),
                                                imu_pos_cm_max=float(e_imu.max() * 100), imu_rot_deg_median=float(np.median(r_imu)),
                                                interp_pos_cm_median=float(np.median(e_lin) * 100), interp_rot_deg_median=float(np.median(r_lin)),
                                                forward_only_pos_cm_median=float(np.median(e_fwd) * 100), forward_only_pos_cm_max=float(e_fwd.max() * 100))

    # ---- real tracking losses: bridge, detect ARCore world-frame jumps, re-align what follows ----
    # After a loss ARCore may start a NEW map with an arbitrary heading (gravity stays aligned). The gyro
    # carries the true orientation through the gap, so a yaw mismatch at re-tracking reveals the jump; the
    # whole post-gap segment is then re-aligned (rotation about vertical + translation). Corrections chain.
    JUMP_DEG = 3.0
    Cr, Ct = R.identity(), np.zeros(3)                      # cumulative correction for the current segment

    def corrected(Cr, Ct):
        def pa(q):
            p_, r_ = pose_at(q)
            return Ct + Cr.apply(p_), Cr * r_

        def va(q):
            return Cr.apply(vel_at(q))
        return pa, va

    rows, gaps, seg_corr = [], [], []                        # seg_corr: (segment start time, Cr, Ct)
    seg_corr.append((-1e9, Cr, Ct))
    intervals = []
    print("\nreal tracking losses:")
    for la, lb in lost:
        a, b = la - 0.1, lb + SETTLE
        if a <= t[0] or b >= t[-1]:
            continue
        pa_c, va_c = corrected(Cr, Ct)
        ts = np.arange(a, b + 1e-9, 0.01)
        if ts[-1] < b:
            ts = np.append(ts, b)
        pA, RA = pa_c(a)
        rg = gyro_forward(ts, RA, imu, cal)
        pBc, RBc = pa_c(b)
        dW = (rg[-1] * RBc.inv()).as_rotvec()                # world-frame mismatch at re-tracking
        jump = np.degrees(np.linalg.norm(dW)) > JUMP_DEG
        if jump:
            Ry = R.from_rotvec([0.0, dW[1], 0.0])            # heading-only (ARCore keeps gravity)
            vB_true = Ry.apply(va_c(b))
            pB_est = forward_positions(ts, rg, pA, va_c(a), vB_true, imu, cal)[-1]
            # new correction x -> Ry (Cr x + Ct_old) + t_new, with Ry pBc + t_new = pB_est
            t_new = pB_est - Ry.apply(pBc)
            Ct_old = seg_corr[-1][2]
            Cr = Ry * Cr
            Ct = Ry.apply(Ct_old) + t_new
            pa_c, va_c = corrected(Cr, Ct)
        seg_corr.append((b, Cr, Ct))
        # bridge with both anchors in the (now consistent) frame
        ts2, pf, rf, clos, drift = bridge(a, b, lambda q: pa_c(q) if q >= b - 1e-9 else corrected(*seg_corr[-2][1:])[0](q),
                                          lambda q: va_c(q) if q >= b - 1e-9 else corrected(*seg_corr[-2][1:])[1](q), imu, cal)
        q = rf.as_quat()
        for k in range(len(ts2)):
            rows.append([t0 + ts2[k] * 1e9, *pf[k], *q[k], *intr])
        intervals.append([float(a), float(b)])
        gaps.append(dict(start=float(la), end=float(lb), bridged=[float(a), float(b)], seconds=float(b - a),
                         arcore_frame_jump=bool(jump), jump_yaw_deg=float(np.degrees(dW[1])) if jump else 0.0,
                         jump_total_deg=float(np.degrees(np.linalg.norm(dW))),
                         residual_closure_deg=float(clos), residual_drift_cm=float(drift * 100)))
        print(f"  {la:7.1f}-{lb:7.1f} s ({b - a:4.1f} s): " + (
            f"ARCore frame JUMP {np.degrees(dW[1]):+.1f} deg yaw -> post-gap segment re-aligned; " if jump else "clean re-track; ")
            + f"bridge closure {clos:.2f} deg, drift {drift * 100:.1f} cm")
    report["gaps"] = gaps
    report["fallback_intervals_s"] = intervals

    # fused trajectory: ARCore poses (segment-corrected) outside the bridged intervals + fallback poses inside
    fused = []
    for k in range(len(t)):
        if any(a <= t[k] <= b for a, b in intervals):
            continue
        c = [sc for sc in seg_corr if sc[0] <= t[k]][-1]
        pk = c[2] + c[1].apply(pos[k]); rk = (c[1] * rot[k]).as_quat()
        fused.append([P[k, 0], *pk, *rk, *P[k, 8:12]])
    fused = np.array(fused + rows)
    fused = fused[np.argsort(fused[:, 0], kind="stable")]
    np.savetxt(os.path.join(root, "poses_fused.csv"), fused, fmt=["%d"] + ["%.6f"] * 3 + ["%.7f"] * 4 + ["%.4f"] * 4, delimiter=",")
    if rows:
        np.savetxt(os.path.join(root, "poses_fallback.csv"), np.array(rows),
                   fmt=["%d"] + ["%.6f"] * 3 + ["%.7f"] * 4 + ["%.4f"] * 4, delimiter=",")
    json.dump(report, open(os.path.join(root, "fallback_report.json"), "w"), indent=1)
    print(f"\nwrote poses_fused.csv ({len(fused)} poses: {len(rows)} fallback in {len(intervals)} gaps, "
          f"{sum(g['arcore_frame_jump'] for g in gaps)} ARCore frame jumps corrected) and fallback_report.json")


def stage2_relocalize(root, imu, cal, t0, intr):
    """Visual relocalisation of every post-gap segment, then IMU re-bridging between the corrected anchors."""
    import subprocess
    from relocalize import FrameBank, relocalize_query, segment_correction
    rp = os.path.join(root, "fallback_report.json")
    report = json.load(open(rp))
    gaps = report.get("gaps", [])
    if not gaps:
        return
    F = np.loadtxt(os.path.join(root, "poses_fused.csv"), delimiter=",")
    tf = (F[:, 0] - t0) / 1e9
    iv = [tuple(g["bridged"]) for g in gaps]
    keep = np.array([not any(a <= x <= b for a, b in iv) for x in tf])
    T_, Pp, Q = tf[keep], F[keep, 1:4].copy(), F[keep, 4:8].copy()
    Rr = R.from_quat(Q)

    def c2w_at(tq):
        k = int(np.clip(np.searchsorted(T_, tq), 1, len(T_) - 1))
        a = (tq - T_[k - 1]) / max(T_[k] - T_[k - 1], 1e-9)
        rr = Slerp([0, 1], R.from_quat(np.stack([Rr[k - 1].as_quat(), Rr[k].as_quat()])))([np.clip(a, 0, 1)])[0]
        M = np.eye(4); M[:3, :3] = rr.as_matrix(); M[:3, 3] = (1 - a) * Pp[k - 1] + a * Pp[k]
        return M

    video = os.path.join(root, "dataset.mp4")
    vpts = np.sort(np.array(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                                     "packet=pts_time", "-of", "csv=p=0", video]).split(), dtype=float))
    K = np.array([[intr[0], 0, intr[2]], [0, intr[1], intr[3]], [0, 0, 1]])
    map_times = list(np.arange(2.0, gaps[0]["bridged"][0] - 0.5, 0.5))
    seg_queries = []
    for i, g in enumerate(gaps):
        end = gaps[i + 1]["bridged"][0] if i + 1 < len(gaps) else T_[-1]
        q = np.arange(g["bridged"][1] + 0.3, end - 0.3, 0.75)[:14]
        seg_queries.append(q)
    bank = FrameBank(video, vpts)
    print(f"\nstage 2: visual relocalisation (decoding {len(map_times) + sum(len(q) for q in seg_queries)} frames)...")
    bank.load(map_times + [x for q in seg_queries for x in q])
    map_entries = [(bank.get(x), c2w_at(x)) for x in map_times if bank.get(x) is not None]
    for i, g in enumerate(gaps):
        ests, curs = [], []
        for x in seg_queries[i]:
            qf = bank.get(x)
            if qf is None:
                continue
            r = relocalize_query(qf, map_entries, K)
            if r is not None and r[2] < 0.15:
                ests.append(r[0]); curs.append(c2w_at(x))
        b = g["bridged"][1]
        if len(ests) >= 2:
            Tc, n_in = segment_correction(ests, curs)
            sel = T_ >= b - 1e-9                         # this segment and everything after it
            Pp[sel] = (Tc[:3, :3] @ Pp[sel].T).T + Tc[:3, 3]
            Rr = R.from_quat(np.concatenate([Rr[~sel].as_quat(), (R.from_matrix(Tc[:3, :3]) * Rr[sel]).as_quat()]))
            ang = np.degrees(R.from_matrix(Tc[:3, :3]).magnitude()); dist = np.linalg.norm(Tc[:3, 3])
            g.update(visual_relocalised=True, reloc_frames=int(n_in), reloc_rotation_deg=float(ang),
                     reloc_shift_m=float(np.linalg.norm(Tc[:3, 3])))
            print(f"  gap {g['start']:.0f}-{g['end']:.0f}s: relocalised from {n_in}/{len(ests)} frames -> "
                  f"segment corrected by {ang:.1f} deg, {dist * 100:.0f} cm")
            for x in seg_queries[i]:
                if bank.get(x) is not None:
                    map_entries.append((bank.get(x), c2w_at(x)))
        else:
            g.update(visual_relocalised=False)
            print(f"  gap {g['start']:.0f}-{g['end']:.0f}s: no visual match with earlier frames "
                  f"({len(ests)} usable) -> keeping the IMU-only alignment (lower confidence)")
    # re-bridge every gap between the corrected anchors
    lost = [(g["start"], g["end"]) for g in gaps]
    sl = Slerp(T_, Rr)

    def pose_at(q):
        return np.array([np.interp(q, T_, Pp[:, k]) for k in range(3)]), sl([q])[0]

    def vel_at(q, h=0.15):
        lo, hi = q - h, q + h
        for la, lb in iv:
            if q <= la + 0.05 and hi > la - 0.05:
                lo, hi = q - 2 * h, q
            if q >= lb - 0.05 and lo < lb + 0.05:
                lo, hi = q, q + 2 * h
        return (pose_at(hi)[0] - pose_at(lo)[0]) / (hi - lo)

    rows = []
    for g in gaps:
        a, b = g["bridged"]
        ts, pf, rf, clos, drift = bridge(a, b, pose_at, vel_at, imu, cal)
        q = rf.as_quat()
        rows += [[t0 + ts[k] * 1e9, *pf[k], *q[k], *intr] for k in range(len(ts))]
        g.update(final_closure_deg=float(clos), final_drift_cm=float(drift * 100))
    base = np.c_[t0 + T_ * 1e9, Pp, Rr.as_quat(), np.tile(intr, (len(T_), 1))]
    fused = np.concatenate([base, np.array(rows)]) if rows else base
    fused = fused[np.argsort(fused[:, 0], kind="stable")]
    np.savetxt(os.path.join(root, "poses_fused.csv"), fused, fmt=["%d"] + ["%.6f"] * 3 + ["%.7f"] * 4 + ["%.4f"] * 4, delimiter=",")
    report["gaps"] = gaps
    json.dump(report, open(rp, "w"), indent=1)
    print(f"stage 2 done: {sum(g.get('visual_relocalised', False) for g in gaps)}/{len(gaps)} segments visually relocalised; "
          f"poses_fused.csv rewritten")


if __name__ == "__main__":
    root = sys.argv[1]
    if not os.path.exists(os.path.join(root, "tracking.csv")):
        print("no tracking.csv (older app build) -> fallback skipped"); sys.exit(0)
    main(root)
    if "--stage2" in sys.argv:      # experimental ray-intersection relocalisation (relocalize_pnp.py after BA is the validated path)
        _P = load_poses(root); _t0 = _P[0, 0]
        _imu = Imu(root, _t0)
        _t = (_P[:, 0] - _t0) / 1e9
        _cal = calibrate(_t, _P[:, 1:4], R.from_quat(_P[:, 4:8]), _imu, load_lost(root, _t0))
        stage2_relocalize(root, _imu, _cal, _t0, _P[:, 8:12].mean(0))
