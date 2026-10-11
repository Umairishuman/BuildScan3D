"""Image-based check of the fallback re-alignment: do frames recorded AFTER a tracking gap agree
geometrically with frames recorded BEFORE it, using ARCore's raw poses vs the fused (re-aligned) poses?
SIFT matches (RANSAC-verified, independent of any pose) are scored by their Sampson epipolar error under
each pose set. Lower = poses consistent with what the images show.
  python src/arcore3dgs/validate_realign.py <dataset> <work>
"""
import os, sys, json
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Capture

root, work = sys.argv[1], sys.argv[2]
meta = json.load(open(os.path.join(work, "frames.json"))); fr = meta["frames"]
raw = Capture(root, pose_offset=meta.get("pose_offset", 0.0), fallback=False)
fus = Capture(root, pose_offset=meta.get("pose_offset", 0.0), fallback=True)
rep = json.load(open(os.path.join(root, "fallback_report.json")))
K = np.array([[meta["fx"], 0, meta["cx"]], [0, meta["fy"], meta["cy"]], [0, 0, 1]]); Ki = np.linalg.inv(K)
G = np.diag([1.0, -1.0, -1.0])
sift = cv2.SIFT_create(4000)
cache = {}

def feats(i):
    if i not in cache:
        g = cv2.imread(os.path.join(work, "images", fr[i]["name"] + ".jpg"), 0)
        kp, d = sift.detectAndCompute(g, None)
        cache[i] = (np.array([k.pt for k in kp], np.float32), d)
    return cache[i]

def F_of(c2w_i, c2w_j):
    Ri, Ci = c2w_i[:3, :3] @ G, c2w_i[:3, 3]; Rj, Cj = c2w_j[:3, :3] @ G, c2w_j[:3, 3]
    Rij = Rj.T @ Ri; tij = Rj.T @ (Ci - Cj)
    tx = np.array([[0, -tij[2], tij[1]], [tij[2], 0, -tij[0]], [-tij[1], tij[0], 0]])
    return Ki.T @ tx @ Rij @ Ki

def sampson(F, a, b):
    ah = np.c_[a, np.ones(len(a))]; bh = np.c_[b, np.ones(len(b))]
    Fa = ah @ F.T; Fb = bh @ F
    return np.sqrt(np.sum(bh * Fa, 1) ** 2 / (Fa[:, 0] ** 2 + Fa[:, 1] ** 2 + Fb[:, 0] ** 2 + Fb[:, 1] ** 2 + 1e-12))

pts = np.array([f["pts"] + meta.get("pose_offset", 0.0) for f in fr])
pose = lambda cap, t: cap.pose_at(t)
before = [i for i in range(len(fr)) if pts[i] < rep["gaps"][0]["start"] - 1] if rep["gaps"] else []
bm = cv2.BFMatcher(cv2.NORM_L2)
for gi, g in enumerate(rep["gaps"]):
    end = rep["gaps"][gi + 1]["start"] if gi + 1 < len(rep["gaps"]) else 1e9
    after = [i for i in range(len(fr)) if g["bridged"][1] + 0.2 < pts[i] < end - 0.2][::2]
    res = {"raw": [], "fused": []}
    for i in after:
        Pi_f, Pi_r = pose(fus, pts[i]), pose(raw, pts[i])
        if Pi_f is None or Pi_r is None:
            continue
        look_f = Pi_f[:3, 3] - 1.5 * Pi_f[:3, 2]
        cand = sorted(before, key=lambda j: np.linalg.norm((pose(fus, pts[j])[:3, 3] - 1.5 * pose(fus, pts[j])[:3, 2]) - look_f))[:4]
        look_r = Pi_r[:3, 3] - 1.5 * Pi_r[:3, 2]
        cand += sorted(before, key=lambda j: np.linalg.norm((pose(raw, pts[j])[:3, 3] - 1.5 * pose(raw, pts[j])[:3, 2]) - look_r))[:4]
        for j in set(cand):
            (ka, da), (kb, db) = feats(i), feats(j)
            if da is None or db is None or len(ka) < 50 or len(kb) < 50:
                continue
            mm = [m for m, n in bm.knnMatch(da, db, k=2) if m.distance < 0.75 * n.distance]
            if len(mm) < 40:
                continue
            a = ka[[m.queryIdx for m in mm]]; b = kb[[m.trainIdx for m in mm]]
            Fm, inl = cv2.findFundamentalMat(a, b, cv2.USAC_MAGSAC, 1.5, 0.999, 5000)
            if Fm is None or inl.sum() < 40:
                continue
            inl = inl.ravel().astype(bool)
            # pose-implied F maps frame i -> frame j: x_j^T F x_i = 0  (b = j, a = i)
            res["raw"].append(np.median(sampson(F_of(Pi_r, pose(raw, pts[j])), a[inl], b[inl])))
            res["fused"].append(np.median(sampson(F_of(Pi_f, pose(fus, pts[j])), a[inl], b[inl])))
    if res["raw"]:
        print(f"after gap {g['start']:.0f}-{g['end']:.0f}s ({'ARCore jump' if g['arcore_frame_jump'] else 'clean'}): "
              f"{len(res['raw'])} verified pairs with earlier frames | epipolar error median: ARCore raw "
              f"{np.median(res['raw']):.1f} px  vs  fused {np.median(res['fused']):.1f} px")
    else:
        print(f"after gap {g['start']:.0f}-{g['end']:.0f}s: no verified overlapping pairs found")
