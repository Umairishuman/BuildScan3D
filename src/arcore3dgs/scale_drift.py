"""Correct the scale drift of a sensor camera path with the room height (FEATURELESS_TRACKING_PLAN §11.b).

Found 2026-11-21: on scan_009 the camera path of rot_sfm.py / prior_ba.py (R-071 -> R-080) has a scale that drifts
along the walk. The camera stays at one height in the model, but its distance to the floor (from the per-frame
depth priors, which are scaled to the SfM points, i.e. in local model units) falls from 4.85 units at 0 - 10 s to
2.3 at 130 - 140 s, the distance to the ceiling likewise, and the ratio model units / Metric3D metre falls from
~2.7 - 5.3 (20 - 50 s) to ~1.4 - 2.7 (after 60 s). Every part of the room is built at its own size, so views agree
only where they were taken. The room's floor-to-ceiling height is fixed, so it is the ruler:

  1. per well-fitted frame (>= --min_inliers SfM inliers, prior residual < --max_err): distances from the camera to
     its horizontal planes (plane_seg.py, |d| of n.P = d with |n_y| > 0.97 in the world), floor or ceiling by side;
  2. fit log dist = c_floor|c_ceiling + log s(t) (s piecewise linear in time, knots every --knot s, smoothness
     --smooth on second differences, Huber IRLS, mean log s = 0);
  3. rescale every step of the path by 1 / s(t) at the step's middle time (rotations unchanged);
  4. re-triangulate every point from its observations (linear, normalised undistorted coordinates), drop points
     behind a camera or > --max_px reprojection error;
  5. check: per frame, median(z_new / z_metric3d_raw) over its points (Metric3D's raw depth is roughly metric), per
     10 s bin before and after; it should flatten.

  python src/arcore3dgs/scale_drift.py <model_in> <sfm dir (frames.json, planes/, mono_prior/)> <model_out>
      [--knot 10] [--smooth 3] [--min_inliers 20] [--max_err 0.15]
Writes cameras.txt, images.txt, points3D.txt (text) and scale_drift.json (s(t) at the knots, per-bin checks).
"""
import argparse
import json
import os
import shutil

import cv2
import numpy as np
from scipy.spatial.transform import Rotation as Rot

G = np.diag([1.0, -1.0, -1.0, 1.0])


def lines(p):
    return [l.rstrip("\n") for l in open(p) if not l.startswith("#")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model_in"); ap.add_argument("sfm"); ap.add_argument("model_out")
    ap.add_argument("--knot", type=float, default=10.0); ap.add_argument("--smooth", type=float, default=3.0)
    ap.add_argument("--min_inliers", type=int, default=20); ap.add_argument("--max_err", type=float, default=0.15)
    ap.add_argument("--max_px", type=float, default=8.0)
    a = ap.parse_args()
    os.makedirs(a.model_out, exist_ok=True)
    meta = json.load(open(os.path.join(a.sfm, "frames.json"))); pts_of = {f["name"]: f["pts"] for f in meta["frames"]}
    t_first = min(pts_of.values())
    st = json.load(open(os.path.join(a.sfm, "planes", "stats.json")))
    ms = json.load(open(os.path.join(a.sfm, "mono_prior", "stats.json")))

    # ---- model ----
    cam = lines(os.path.join(a.model_in, "cameras.txt"))[0].split(); assert cam[1] == "OPENCV"
    fx, fy, cx, cy, k1, k2, p1, p2 = map(float, cam[4:12])
    K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1.0]]); dist = np.array([k1, k2, p1, p2])
    L = lines(os.path.join(a.model_in, "images.txt"))
    imgs = []
    for i in range(0, len(L), 2):
        h = L[i].split(); q = list(map(float, h[1:5])); t = np.array(list(map(float, h[5:8])))
        Rcw = Rot.from_quat([q[1], q[2], q[3], q[0]]).as_matrix()
        imgs.append(dict(id=int(h[0]), name=h[9], key=os.path.splitext(h[9])[0], h=h, Rcw=Rcw, C=-Rcw.T @ t, pts2d=L[i + 1]))
    imgs.sort(key=lambda d: pts_of.get(d["key"], 1e18))
    imgs = [d for d in imgs if d["key"] in pts_of]
    T = np.array([pts_of[d["key"]] - t_first for d in imgs])

    # ---- 1. floor / ceiling distances ----
    obs_t, obs_kind, obs_d = [], [], []
    for d, t in zip(imgs, T):
        s = ms.get(d["key"])
        if s is None or s.get("inliers", 0) < a.min_inliers or s.get("median_rel_err", 1) >= a.max_err:
            continue
        Rwc = d["Rcw"].T
        for p in st.get(d["key"], {}).get("detail", []):
            n = np.array(p["n"]); nw = Rwc @ n
            if abs(nw[1]) < 0.97:
                continue
            y = (Rwc @ (p["d"] * n) + d["C"])[1]
            obs_t.append(t); obs_kind.append(0 if y < d["C"][1] else 1); obs_d.append(abs(p["d"]))
    obs_t, obs_kind, obs_d = map(np.array, (obs_t, obs_kind, obs_d))
    print(f"{len(obs_d)} floor / ceiling distances ({(obs_kind == 0).sum()} floor, {(obs_kind == 1).sum()} ceiling) "
          f"from well-fitted frames", flush=True)

    # ---- 2. fit log s(t) ----
    knots = np.arange(0, T.max() + a.knot, a.knot); nk = len(knots)

    def basis(t):
        B = np.zeros((len(t), nk))
        j = np.clip((t // a.knot).astype(int), 0, nk - 2); f = t / a.knot - j
        B[np.arange(len(t)), j] = 1 - f; B[np.arange(len(t)), j + 1] = f
        return B
    Bo = basis(obs_t)
    A = np.c_[(obs_kind == 0).astype(float), (obs_kind == 1).astype(float), Bo]; y = np.log(obs_d)
    Dm = np.zeros((nk - 2, 2 + nk))
    for i in range(nk - 2):
        Dm[i, 2 + i:2 + i + 3] = [1, -2, 1]
    gauge = np.r_[0, 0, np.full(nk, 1.0 / nk)]
    w = np.ones(len(y))
    for it in range(10):                                        # Huber IRLS (delta 0.1 in log = 10 %)
        Aw = A * w[:, None]
        lhs = A.T @ Aw + a.smooth * Dm.T @ Dm + 1e3 * np.outer(gauge, gauge)
        x = np.linalg.solve(lhs, Aw.T @ y)
        r = y - A @ x
        w = np.where(np.abs(r) < 0.1, 1.0, 0.1 / np.abs(r))
    ls = x[2:]; s_k = np.exp(ls)
    print(f"floor at {np.exp(x[0]):.2f}, ceiling at {np.exp(x[1]):.2f} units (scale 1); residual median "
          f"{np.median(np.abs(r)) * 100:.1f} %", flush=True)
    print("s(t) at the knots: " + " ".join(f"{k:.0f}s:{v:.2f}" for k, v in zip(knots, s_k)), flush=True)
    s_of = lambda t: np.exp(basis(np.atleast_1d(t)) @ ls)

    # ---- 3. rescale the path ----
    C0 = np.array([d["C"] for d in imgs]); C1 = C0.copy()
    for k in range(1, len(imgs)):
        C1[k] = C1[k - 1] + (C0[k] - C0[k - 1]) / s_of((T[k] + T[k - 1]) / 2)[0]
    C1 += C0.mean(0) - C1.mean(0)
    step0 = np.linalg.norm(np.diff(C0, axis=0), axis=1); step1 = np.linalg.norm(np.diff(C1, axis=0), axis=1)
    print(f"path length {step0.sum():.1f} -> {step1.sum():.1f} units; extent {np.ptp(C0, 0).round(2)} -> {np.ptp(C1, 0).round(2)}",
          flush=True)

    # ---- 4. re-triangulate ----
    id2k = {d["id"]: k for k, d in enumerate(imgs)}
    uv = {d["id"]: (np.array(d["pts2d"].split(), float).reshape(-1, 3) if d["pts2d"].strip() else np.zeros((0, 3)))
          for d in imgs}
    P = [np.c_[d["Rcw"], -d["Rcw"] @ c] for d, c in zip(imgs, C1)]
    rows = lines(os.path.join(a.model_in, "points3D.txt")); out_pts, kept, dropped = [], set(), 0
    for row in rows:
        s = row.split(); pid = int(s[0]); tr = np.array(s[8:], int).reshape(-1, 2)
        tr = np.array([t_ for t_ in tr if t_[0] in id2k])
        if len(tr) < 2:
            dropped += 1; continue
        xy = np.array([uv[i][j, :2] for i, j in tr])
        nrm = cv2.undistortPoints(xy.reshape(-1, 1, 2), K, dist).reshape(-1, 2)
        Am = []
        for (i, _), (u_, v_) in zip(tr, nrm):
            Pm = P[id2k[i]]; Am += [u_ * Pm[2] - Pm[0], v_ * Pm[2] - Pm[1]]
        _, _, Vt = np.linalg.svd(np.array(Am)); Xh = Vt[-1]
        if abs(Xh[3]) < 1e-12:
            dropped += 1; continue
        Xw = Xh[:3] / Xh[3]
        zc = np.array([(P[id2k[i]] @ np.r_[Xw, 1])[2] for i, _ in tr])
        proj = np.array([P[id2k[i]] @ np.r_[Xw, 1] for i, _ in tr]); pr = proj[:, :2] / proj[:, 2:]
        err = np.linalg.norm((pr - nrm) * [fx, fy], axis=1)
        if (zc <= 0).any() or np.median(err) > a.max_px:
            dropped += 1; continue
        kept.add(pid)
        out_pts.append(f"{pid} {Xw[0]} {Xw[1]} {Xw[2]} {' '.join(s[4:7])} {np.median(err):.3f} " + " ".join(f"{i} {j}" for i, j in tr))
    print(f"re-triangulated {len(out_pts)} points, dropped {dropped}", flush=True)

    with open(os.path.join(a.model_out, "points3D.txt"), "w") as f:
        f.write(f"# Number of points: {len(out_pts)}\n" + "\n".join(out_pts) + "\n")
    with open(os.path.join(a.model_out, "images.txt"), "w") as f:
        f.write(f"# Number of images: {len(imgs)}\n")
        for d, c in zip(imgs, C1):
            q = Rot.from_matrix(d["Rcw"]).as_quat(); t = -d["Rcw"] @ c
            f.write(f"{d['id']} {q[3]} {q[0]} {q[1]} {q[2]} {t[0]} {t[1]} {t[2]} {' '.join(d['h'][8:])}\n")
            a2 = np.array(d["pts2d"].split()).reshape(-1, 3) if d["pts2d"].strip() else np.zeros((0, 3), str)
            for r_ in a2:
                if r_[2] != "-1" and int(r_[2]) not in kept:
                    r_[2] = "-1"
            f.write(" ".join(" ".join(r_) for r_ in a2) + "\n")
    for fn in ("cameras.txt", "rigs.txt", "frames.txt"):                 # COLMAP 4 text model (prior_ba.py copies them)
        if os.path.exists(os.path.join(a.model_in, fn)):
            shutil.copy(os.path.join(a.model_in, fn), os.path.join(a.model_out, fn))

    # ---- 5. check against Metric3D's raw (roughly metric) depth ----
    def ratio_bins(Cs, Xd):
        out = {}
        for k, d in enumerate(imgs):
            s = ms.get(d["key"]); pth = os.path.join(a.sfm, "mono_prior", d["key"] + ".npz")
            if s is None or s.get("n_sfm", 0) < 20 or not os.path.exists(pth):
                continue
            D = np.load(pth)["depth"].astype(np.float32); sc = s.get("scale_filled", s["scale"]); sh = s["shift"]
            m = (D - sh) / sc                                  # raw Metric3D depth (metres, roughly)
            h_, w_ = D.shape; dd = meta["W"] / w_
            a2 = uv[d["id"]]; ids = a2[:, 2].astype(int); sel = np.array([i in Xd for i in ids])
            if sel.sum() < 20:
                continue
            Xs = np.array([Xd[i] for i in ids[sel]])
            Rcw = d["Rcw"]; z = ((Xs - Cs[k]) @ Rcw.T)[:, 2]
            nrm = cv2.undistortPoints(a2[sel, :2].reshape(-1, 1, 2).astype(np.float64), K, dist, P=K).reshape(-1, 2)
            px = np.clip((nrm[:, 0] / dd).astype(int), 0, w_ - 1); py = np.clip((nrm[:, 1] / dd).astype(int), 0, h_ - 1)
            zm = m[py, px]; ok = (z > 0) & (zm > 0.1)
            if ok.sum() >= 20:
                out.setdefault(int(T[k] // 10) * 10, []).append(float(np.median(z[ok] / zm[ok])))
        return {b: float(np.median(v)) for b, v in sorted(out.items())}
    X_old = {int(r.split()[0]): np.array(list(map(float, r.split()[1:4]))) for r in rows}
    X_new = {int(r.split()[0]): np.array(list(map(float, r.split()[1:4]))) for r in out_pts}
    before, after = ratio_bins(C0, X_old), ratio_bins(C1, X_new)
    print("model units per Metric3D metre, median per 10 s bin (before -> after):")
    for b in before:
        print(f"   {b:3d}-{b + 10:<3d}s  {before[b]:5.2f} -> {after.get(b, float('nan')):5.2f}")
    bv, av = np.array(list(before.values())), np.array([after[b] for b in before if b in after])
    print(f"spread across bins (p90 / p10): {np.percentile(bv, 90) / np.percentile(bv, 10):.2f} -> "
          f"{np.percentile(av, 90) / np.percentile(av, 10):.2f}", flush=True)
    json.dump(dict(knots=knots.tolist(), s=s_k.tolist(), floor=float(np.exp(x[0])), ceiling=float(np.exp(x[1])),
                   n_obs=int(len(y)), resid_median=float(np.median(np.abs(r))), path_len=[float(step0.sum()), float(step1.sum())],
                   points=len(out_pts), dropped=dropped, ratio_before=before, ratio_after=after, params=vars(a)),
              open(os.path.join(a.model_out, "scale_drift.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
