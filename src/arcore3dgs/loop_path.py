"""Close the loops of a sensor camera path with the image pairs that see the same place at different times
(FEATURELESS_TRACKING_PLAN §11.d).

Found 2026-11-22 on scan_009: the camera model of R-094 (rot_sfm -> prior_ba -> scale_drift -> prior_ba) has
almost no point tracks between distant times (of 29,207 points, 1,327 span >= 60 s, nearly all start <-> end), so
the bundle adjustment never sees the places the walk revisits, and the walls seen at different times land in
parallel copies. The evidence exists: rot_sfm.py's pair-direction cache holds 852 verified pairs >= 60 s apart
(direction of C_a - C_b from the matches with the gyro rotation fixed). After the room-height correction they
agree worse with the path (p75 angle 11.4 -> 28.6 deg). Here the camera centres are solved again (rotations kept):

  - path shape: C_k - C_(k-1) = the input path's step, sigma = --s0 + --s1 * |step| (model units);
  - loop pairs (|dt| >= --min_dt): (C_a - C_b) x u_ab = 0, normalised by |C_a - C_b| (so the residual is the sine
    of the angle), sigma --sigma_dir deg, weight from the pair's inliers / parallax, Cauchy reweighting;
  - u_ab is in rot_sfm's world; one rotation to the model's world is fitted on the short pairs (|dt| < 5 s)
    (--model_frame: directions from loop_match.py, already in the model's world);
  - a tiny pull to the input positions fixes the gauge.
Pair check (--gate deg, 2026-11-22, after R-097): pairs whose direction disagrees with the INPUT path by more than
the gate are left out before solving. For a second round on an already loop-closed path (R-096): new pairs may only
make small corrections; R-097 without the check broke the 134 - 137 s stretch with wrong pairs.
Holes (--hole_dt s / --hole_step x median step, 2026-11-23, after R-121): a gap in the path (no placed keyframes for
>= --hole_dt s, or one step >= --hole_step times the median) only joins its two sides by one loose path step, so loop
pairs elsewhere can shift one side against the other (R-121 moved 115 - 125 s by 0.2 - 0.28 units against 133 s+ and
broke 134 - 140 s). A hole stays free only when >= --hole_min_tie pairs tie the --hole_win seconds on each side
directly; otherwise its step keeps the input path's offset (sigma --hole_sigma units), and loop_pairs.json gets
cross-hole pairs (5 x 5 frames) so prior_ba.py --pair_priors keeps it too.
Validation: a --hold fraction of the loop pairs is left out of a first solve, and their angle before / after is
printed; the written model uses all pairs. Points are re-triangulated (scale_drift.write_model).

  python src/arcore3dgs/loop_path.py <model_in> <sfm dir with frames.json> <pair_directions json> <model_out>
      [--min_dt 5] [--sigma_dir 5] [--s0 0.01] [--s1 0.05] [--hold 0.2]
Writes the text model and loop_path.json (settings, residuals, how far the cameras moved per 10 s).
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scale_drift import read_model, write_model  # noqa: E402


def skew(u):
    return np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0.0]])


def angles(C, E):
    D = np.array([C[a] - C[b] for a, b, _, _ in E]); n = np.linalg.norm(D, axis=1)
    U = np.array([u for _, _, u, _ in E])
    return np.degrees(np.arccos(np.clip(np.sum(U * D, 1) / np.maximum(n, 1e-9), -1, 1)))


def solve(C0, steps, sig_step, E, a):
    N = len(C0); C = C0.copy()
    wq = np.array([w for _, _, _, w in E]); wq = wq / np.median(wq)
    sd = np.sin(np.radians(a.sigma_dir))
    for it in range(a.iters):
        r_, c_, v_, b_ = [], [], [], []
        row = 0
        for k in range(1, N):                                   # path shape
            for j in range(3):
                r_ += [row, row]; c_ += [3 * k + j, 3 * (k - 1) + j]; v_ += [1 / sig_step[k - 1], -1 / sig_step[k - 1]]
                b_.append(steps[k - 1, j] / sig_step[k - 1]); row += 1
        ang = angles(C, E)
        cw = 1.0 / (1.0 + (ang / a.sigma_dir) ** 2)             # Cauchy
        for (ia, ib, u, _), q, w in zip(E, wq, cw):             # loop pairs
            L = max(np.linalg.norm(C[ia] - C[ib]), 0.1)
            M = skew(u) * (np.sqrt(q * w) / (sd * L))
            for j in range(3):
                for m in range(3):
                    if M[j, m] != 0:
                        r_ += [row, row]; c_ += [3 * ia + m, 3 * ib + m]; v_ += [M[j, m], -M[j, m]]
                b_.append(0.0); row += 1
        g = 1e-3                                                # gauge
        for k in range(N):
            for j in range(3):
                r_.append(row); c_.append(3 * k + j); v_.append(g); b_.append(g * C0[k, j]); row += 1
        A = coo_matrix((v_, (r_, c_)), shape=(row, 3 * N)).tocsr(); b = np.array(b_)
        x = spsolve((A.T @ A).tocsc(), A.T @ b)
        C_new = x.reshape(N, 3)
        moved = np.abs(C_new - C).max(); C = C_new
        if moved < 1e-4:
            break
    return C


def report(tag, C, E, T_e):
    ang = angles(C, E); out = {}
    for lo, hi in ((5, 20), (20, 60), (60, 400)):
        s = (T_e >= lo) & (T_e < hi)
        if s.any():
            out[f"{lo}-{hi}s"] = dict(n=int(s.sum()), median=float(np.median(ang[s])), p75=float(np.percentile(ang[s], 75)),
                                      below5=float(np.mean(ang[s] < 5)))
    print(f"  {tag}: " + "; ".join(f"dt {k}: n {v['n']}, median {v['median']:.2f}, p75 {v['p75']:.2f} deg, "
                                   f"{100 * v['below5']:.0f} % < 5 deg" for k, v in out.items()), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model_in"); ap.add_argument("sfm"); ap.add_argument("pairs"); ap.add_argument("model_out")
    ap.add_argument("--min_dt", type=float, default=5.0, help="s; shorter pairs are left to the path shape")
    ap.add_argument("--sigma_dir", type=float, default=5.0, help="deg")
    ap.add_argument("--s0", type=float, default=0.01); ap.add_argument("--s1", type=float, default=0.05)
    ap.add_argument("--hold", type=float, default=0.2); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--iters", type=int, default=12); ap.add_argument("--max_px", type=float, default=8.0)
    ap.add_argument("--gate", type=float, default=0.0,
                    help="deg; > 0: drop pairs whose angle on the input path exceeds this before solving")
    ap.add_argument("--hole_dt", type=float, default=0.0, help="s; > 0: gaps this long are holes (0 = off)")
    ap.add_argument("--hole_step", type=float, default=15.0, help="x median step: a step this long is a hole too")
    ap.add_argument("--hole_win", type=float, default=10.0, help="s on each side of a hole for the tie count")
    ap.add_argument("--hole_min_tie", type=int, default=5, help="pairs across a hole that leave it free")
    ap.add_argument("--hole_sigma", type=float, default=0.01, help="model units: step sigma of a held hole")
    ap.add_argument("--model_frame", action="store_true",
                    help="the directions are already in the model's world (loop_match.py), no rotation is fitted")
    a = ap.parse_args()
    meta = json.load(open(os.path.join(a.sfm, "frames.json"))); pts_of = {f["name"]: f["pts"] for f in meta["frames"]}
    t_first = min(pts_of.values())
    K, dist, fx, fy, imgs = read_model(a.model_in, pts_of)
    idx = {d["key"]: k for k, d in enumerate(imgs)}
    T = np.array([pts_of[d["key"]] - t_first for d in imgs])
    C0 = np.array([d["C"] for d in imgs])

    raw = [(p[0], p[1], np.array(p[2]), p[3]) for p in json.load(open(a.pairs)) if p[0] in idx and p[1] in idx]
    dt = np.array([abs(T[idx[x]] - T[idx[y]]) for x, y, _, _ in raw])
    # rotation from rot_sfm's world to this model's world, on the short pairs
    sh = [(x, y, u, w) for (x, y, u, w), d_ in zip(raw, dt) if d_ < 5 and np.linalg.norm(C0[idx[x]] - C0[idx[y]]) > 0.05]
    if a.model_frame:
        Q = np.eye(3); sh = []
    else:
        U = np.array([u for _, _, u, _ in sh]); D = np.array([C0[idx[x]] - C0[idx[y]] for x, y, _, _ in sh])
        D /= np.linalg.norm(D, axis=1, keepdims=True); W = np.array([w for _, _, _, w in sh])
        Us, _, Vt = np.linalg.svd((U * W[:, None]).T @ D)
        Q = Vt.T @ np.diag([1, 1, np.linalg.det(Vt.T @ Us.T)]) @ Us.T
    print(f"{len(raw)} pair directions in the model; rotation to the model's world fitted on {len(sh)} short pairs "
          f"({np.degrees(np.arccos(np.clip((np.trace(Q) - 1) / 2, -1, 1))):.2f} deg)", flush=True)

    E_all = [(idx[x], idx[y], Q @ u, w) for (x, y, u, w), d_ in zip(raw, dt) if d_ >= a.min_dt]
    T_all = dt[dt >= a.min_dt]
    print(f"{len(E_all)} loop pairs with |dt| >= {a.min_dt} s", flush=True)
    n_gated = 0
    if a.gate > 0 and E_all:
        ok = angles(C0, E_all) <= a.gate
        bad_t = sorted(T[e[0]] for e, o in zip(E_all, ok) if not o) + sorted(T[e[1]] for e, o in zip(E_all, ok) if not o)
        hist = np.histogram(bad_t, bins=np.arange(0, T.max() + 10, 10))[0]
        n_gated = int((~ok).sum())
        print(f"pair check: {n_gated} of {len(E_all)} pairs disagree with the input path by > {a.gate:g} deg, left out; "
              f"their frames per 10 s: " + " ".join(f"{10 * k}s:{n}" for k, n in enumerate(hist) if n), flush=True)
        E_all = [e for e, o in zip(E_all, ok) if o]; T_all = T_all[ok]
    steps = np.diff(C0, axis=0); sig = a.s0 + a.s1 * np.linalg.norm(steps, axis=1)

    held = []
    if a.hole_dt > 0:
        dts = np.diff(T); st = np.linalg.norm(steps, axis=1)
        for k in np.flatnonzero((dts >= a.hole_dt) | (st >= a.hole_step * np.median(st))):
            t0_, t1_ = T[k], T[k + 1]
            tie = sum(1 for ia, ib, _, _ in E_all if (t0_ - a.hole_win <= min(T[ia], T[ib]) <= t0_) and (t1_ <= max(T[ia], T[ib]) <= t1_ + a.hole_win))
            free = tie >= a.hole_min_tie
            if not free:
                sig[k] = a.hole_sigma; held.append(k)
            print(f"hole {t0_:.1f} -> {t1_:.1f} s ({t1_ - t0_:.1f} s, step {st[k]:.2f}): {tie} pairs tie its sides -> "
                  f"{'free' if free else 'held'}", flush=True)
        print(f"{len(held)} holes held at the input path's offset (sigma {a.hole_sigma:g})", flush=True)
    rng = np.random.default_rng(a.seed); hold = rng.random(len(E_all)) < a.hold
    E_fit = [e for e, h in zip(E_all, hold) if not h]; E_hold = [e for e, h in zip(E_all, hold) if h]
    print(f"validation: {len(E_fit)} pairs fitted, {len(E_hold)} held out", flush=True)
    res = dict(input=report("held-out pairs, input path ", C0, E_hold, T_all[hold]))
    Cv = solve(C0, steps, sig, E_fit, a)
    res["validation"] = report("held-out pairs, solved path", Cv, E_hold, T_all[hold])

    C1 = solve(C0, steps, sig, E_all, a)
    print("all pairs:")
    res["all_input"] = report("input ", C0, E_all, T_all); res["all_solved"] = report("solved", C1, E_all, T_all)
    mv = np.linalg.norm(C1 - C0, axis=1)
    per10 = {}
    for k in range(int(T.max() // 10) + 1):
        s = (T >= 10 * k) & (T < 10 * k + 10)
        if s.any():
            per10[f"{10 * k}"] = [float(x) for x in np.median(C1[s] - C0[s], axis=0)]
    print(f"cameras moved: median {np.median(mv):.3f}, p90 {np.percentile(mv, 90):.3f}, max {mv.max():.3f} units; "
          f"path length {np.linalg.norm(steps, axis=1).sum():.1f} -> {np.linalg.norm(np.diff(C1, axis=0), axis=1).sum():.1f}",
          flush=True)
    print("median shift per 10 s (x, y, z): " + "  ".join(f"{k}s:({v[0]:.2f},{v[1]:.2f},{v[2]:.2f})" for k, v in per10.items()),
          flush=True)
    out_pts, dropped, _, _ = write_model(a.model_in, a.model_out, imgs, C1, K, dist, fx, fy, a.max_px)
    print(f"re-triangulated {len(out_pts)} points, dropped {dropped}", flush=True)
    # the pairs the solved path agrees with (< 3 sigma): prior_ba.py --pair_priors keeps their relative positions
    ang = angles(C1, E_all); ok = ang < 3 * a.sigma_dir
    lp = [[imgs[ia]["key"], imgs[ib]["key"]] for (ia, ib, _, _), o in zip(E_all, ok) if o]
    for k in held:                                              # cross-hole pairs keep the held offset in prior_ba
        lp += [[imgs[i]["key"], imgs[j]["key"]] for i in range(max(0, k - 4), k + 1) for j in range(k + 1, min(len(imgs), k + 6))]
    json.dump(lp, open(os.path.join(a.model_out, "loop_pairs.json"), "w"))
    print(f"{int(ok.sum())} of {len(E_all)} loop pairs agree with the solved path (< {3 * a.sigma_dir:g} deg): "
          f"loop_pairs.json", flush=True)
    json.dump(dict(params=vars(a), gated=n_gated, held_holes=[[float(T[k]), float(T[k + 1])] for k in held], residuals=res, moved_median=float(np.median(mv)), moved_max=float(mv.max()),
                   shift_per_10s=per10, points=len(out_pts), dropped=dropped),
              open(os.path.join(a.model_out, "loop_path.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
