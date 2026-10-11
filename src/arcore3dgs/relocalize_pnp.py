"""Re-align post-tracking-loss segments to the map with PnP ("once a familiar point is re-tracked").

The map = keyframes recorded before the first tracking loss (trusted, BA-refined poses) and the BA's
triangulated 3D points (sparse.npz). For every keyframe after a loss, SIFT features are matched to the map
features that carry a 3D point, and the camera's absolute metric pose is solved with PnP + RANSAC.
One robust rigid correction per segment is applied to that segment and every later frame; the corrected
poses are stored as c2w / c2w_init in frames.json so the next BA run starts from them (ba.py uses
c2w_init when present). Segments with no familiar view keep the IMU fallback alignment (flagged).

  python src/arcore3dgs/relocalize_pnp.py --work <dataset>/work
"""
import os, sys, json, argparse
import numpy as np, cv2
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation as R

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--min_inliers", type=int, default=20)
ap.add_argument("--map_every", type=int, default=1)
args = ap.parse_args()

meta = json.load(open(os.path.join(args.work, "frames.json"))); fr = meta["frames"]
rp = os.path.join(meta["dataset"], "fallback_report.json")
gaps = json.load(open(rp)).get("gaps", []) if os.path.exists(rp) else []
if not gaps:
    print("no tracking gaps -> nothing to relocalise"); sys.exit(0)
pts = np.array([f["pts"] + meta.get("pose_offset", 0.0) for f in fr])
K = np.array([[meta["fx"], 0, meta["cx"]], [0, meta["fy"], meta["cy"]], [0, 0, 1]])
G = np.diag([1.0, -1.0, -1.0, 1.0])
sp = np.load(os.path.join(args.work, "sparse.npz")); X, cam, pt, uv = sp["X"], sp["cam"], sp["pt"], sp["uv"]
sift = cv2.SIFT_create(nfeatures=6000, contrastThreshold=0.02); clahe = cv2.createCLAHE(2.0, (8, 8))


def features(i):
    g = clahe.apply(cv2.imread(os.path.join(args.work, "images", fr[i]["name"] + ".jpg"), cv2.IMREAD_GRAYSCALE))
    kp, d = sift.detectAndCompute(g, None)
    d = np.sqrt(d / (d.sum(1, keepdims=True) + 1e-7)).astype(np.float32)        # RootSIFT, as in ba.py
    return np.array([k.pt for k in kp], np.float32), d


# ---- map: trusted keyframes before the first loss, keypoints tied to BA 3D points ----
first = gaps[0]["bridged"][0] - 1.0
map_ids = [i for i in range(len(fr)) if pts[i] < first][:: args.map_every]
D_l, X_l = [], []
for i in map_ids:
    obs = cam == i
    if obs.sum() < 20:
        continue
    kpt, d = features(i)
    dist, idx = cKDTree(uv[obs]).query(kpt, distance_upper_bound=1.5)
    ok = np.isfinite(dist)
    D_l.append(d[ok]); X_l.append(X[pt[obs][idx[ok]]])
Dm = np.concatenate(D_l); Xm = np.concatenate(X_l)
print(f"map: {len(map_ids)} keyframes before {first:.0f} s, {len(Dm)} descriptors with 3D points")
flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=4), dict(checks=64))
flann.add([Dm]); flann.train()


def pnp(i):
    kpt, d = features(i)
    mm = [m for m, n in flann.knnMatch(d, k=2) if m.distance < 0.8 * n.distance]
    if len(mm) < args.min_inliers:
        return None
    p2 = kpt[[m.queryIdx for m in mm]].astype(np.float64); p3 = Xm[[m.trainIdx for m in mm]].astype(np.float64)
    ok, rvec, tvec, inl = cv2.solvePnPRansac(p3, p2, K, None, iterationsCount=3000, reprojectionError=3.0,
                                             confidence=0.999, flags=cv2.SOLVEPNP_SQPNP)
    if not ok or inl is None or len(inl) < args.min_inliers:
        return None
    inl = inl.ravel()
    rvec, tvec = cv2.solvePnPRefineLM(p3[inl], p2[inl], K, None, rvec, tvec)
    Rw2c = cv2.Rodrigues(rvec)[0]
    c2w = np.eye(4); c2w[:3, :3] = Rw2c.T; c2w[:3, 3] = (-Rw2c.T @ tvec).ravel()
    proj, _ = cv2.projectPoints(p3[inl], rvec, tvec, K, None)
    err = float(np.median(np.linalg.norm(proj.reshape(-1, 2) - p2[inl], axis=1)))
    return c2w @ G, len(inl), err                                          # back to OpenGL camera convention


C = [np.array(f["c2w"]) for f in fr]
for f in fr:
    f.setdefault("c2w_init", f.get("c2w_arcore", f["c2w"]))
for gi, g in enumerate(gaps):
    end = gaps[gi + 1]["bridged"][0] if gi + 1 < len(gaps) else 1e9
    seg = [i for i in range(len(fr)) if g["bridged"][1] <= pts[i] < end]
    Ts = []
    for i in seg[::2][:20]:
        r = pnp(i)
        if r is not None and r[2] < 2.0:
            Ts.append(r[0] @ np.linalg.inv(C[i]))
    if len(Ts) >= 3:
        tr = np.stack([T[:3, 3] for T in Ts]); med = np.median(tr, 0)
        keep = np.linalg.norm(tr - med, axis=1) < max(0.1, 3 * np.median(np.linalg.norm(tr - med, axis=1)))
    if len(Ts) >= 3 and keep.sum() >= 3:
        Tc = np.eye(4); Tc[:3, :3] = R.from_matrix(np.stack([T[:3, :3] for T in Ts])[keep]).mean().as_matrix()
        Tc[:3, 3] = tr[keep].mean(0)
        later = [i for i in range(len(fr)) if pts[i] >= g["bridged"][1]]
        for i in later:
            C[i] = Tc @ C[i]
        g.update(pnp_relocalised=True, pnp_frames=int(keep.sum()),
                 pnp_rotation_deg=float(np.degrees(R.from_matrix(Tc[:3, :3]).magnitude())), pnp_shift_cm=float(np.linalg.norm(Tc[:3, 3]) * 100))
        print(f"gap {g['start']:.0f}-{g['end']:.0f}s: PnP relocalised from {int(keep.sum())}/{len(Ts)} keyframes -> segment "
              f"corrected by {g['pnp_rotation_deg']:.1f} deg, {g['pnp_shift_cm']:.0f} cm")
    else:
        g.update(pnp_relocalised=False)
        for i in seg:
            fr[i]["fallback_unverified"] = True               # kept out of the geometry prior and training
        print(f"gap {g['start']:.0f}-{g['end']:.0f}s: no familiar view found ({len(Ts)} PnP solutions) -> IMU fallback alignment kept")
    for i in seg:
        fr[i]["fallback_segment"] = gi
for i, f in enumerate(fr):
    f["c2w"] = C[i].tolist(); f["c2w_init"] = C[i].tolist()
json.dump(meta, open(os.path.join(args.work, "frames.json"), "w"), indent=1)
rep = json.load(open(rp)); rep["gaps"] = gaps; json.dump(rep, open(rp, "w"), indent=1)
print("frames.json updated (c2w / c2w_init); run ba.py next to refine from these poses")
