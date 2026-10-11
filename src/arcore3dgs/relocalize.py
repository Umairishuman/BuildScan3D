"""Visual relocalisation of ARCore segments after tracking losses ("re-align once a familiar point is re-tracked").

After a tracking loss ARCore may continue in a shifted/rotated world frame. For every segment that follows a
gap, frames are matched BY IMAGE CONTENT (SIFT, RANSAC-verified) against earlier frames whose poses are
trusted (the map). Each verified pair gives the relative rotation and the direction of the baseline
(essential matrix); rays from >= 2 map cameras intersect at the query camera centre (metric, because the
map poses are metric). One robust rigid correction per segment is then applied to the segment and to
everything after it, and the segment's frames join the map.

Used by fallback.py (stage 2). Works directly on dataset.mp4 (no keyframe extraction needed).
"""
import numpy as np, cv2
from scipy.spatial.transform import Rotation as R

G = np.diag([1.0, -1.0, -1.0])           # OpenGL camera <-> OpenCV camera


class FrameBank:
    """Decodes the video once and keeps SIFT features for requested pose-times."""

    def __init__(self, video, pts, scale=0.5, n_features=3000):
        self.video, self.pts, self.scale = video, pts, scale
        self.sift = cv2.SIFT_create(n_features)
        self.feats = {}

    def load(self, times):
        want = {}
        for tq in times:
            k = int(np.argmin(np.abs(self.pts - tq)))
            if k not in self.feats:
                want[k] = True
        if not want:
            return
        cap = cv2.VideoCapture(self.video)
        last = max(want)
        for k in range(last + 1):
            ok = cap.grab()
            if not ok:
                break
            if k in want:
                _, im = cap.retrieve()
                g = cv2.cvtColor(cv2.resize(im, None, fx=self.scale, fy=self.scale, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
                kp, d = self.sift.detectAndCompute(g, None)
                self.feats[k] = (np.array([p.pt for p in kp], np.float32) / self.scale, d)
        cap.release()

    def get(self, tq):
        return self.feats.get(int(np.argmin(np.abs(self.pts - tq))))


def _match(fa, fb, K, bm=cv2.BFMatcher(cv2.NORM_L2), min_inl=60):
    (ka, da), (kb, db) = fa, fb
    if da is None or db is None or len(ka) < 80 or len(kb) < 80:
        return None
    mm = [m for m, n in bm.knnMatch(da, db, k=2) if m.distance < 0.75 * n.distance]
    if len(mm) < min_inl:
        return None
    a = ka[[m.queryIdx for m in mm]]; b = kb[[m.trainIdx for m in mm]]
    E, inl = cv2.findEssentialMat(a, b, K, cv2.RANSAC, 0.999, 1.5)
    if E is None or inl is None or inl.sum() < min_inl:
        return None
    n, Rab, tab, mask = cv2.recoverPose(E[:3], a, b, K, mask=inl.copy())
    if n < min_inl:
        return None
    return Rab, tab.ravel(), int(n)          # x_b = Rab x_a + tab  (OpenCV cameras, |t| = 1)


def relocalize_query(qf, map_entries, K, max_pairs=6):
    """map_entries: list of (features, c2w_gl). Returns (c2w_gl estimate, n_rays, residual_m) or None."""
    scored = []
    for mf, c2w in map_entries:
        r = _match(mf, qf, K)
        if r is not None:
            scored.append((r[2], r, c2w))
    scored.sort(key=lambda x: -x[0])
    scored = scored[:max_pairs]
    if len(scored) < 2:
        return None
    origins, dirs, rots = [], [], []
    for _, (Rmq, tmq, _), c2w in scored:
        Rm = c2w[:3, :3] @ G; Cm = c2w[:3, 3]               # map camera, OpenCV axes in world
        Cq_in_m = -Rmq.T @ tmq                                # query centre in map-camera coords (unit length)
        origins.append(Cm); dirs.append(Rm @ Cq_in_m / np.linalg.norm(Cq_in_m))
        rots.append(Rm @ Rmq.T)                               # query c2w rotation (OpenCV)
    O, D = np.array(origins), np.array(dirs)
    # least-squares closest point to all rays
    A = np.zeros((3, 3)); b = np.zeros(3)
    for o, d in zip(O, D):
        P = np.eye(3) - np.outer(d, d); A += P; b += P @ o
    if np.linalg.cond(A) > 1e6:
        return None
    C = np.linalg.solve(A, b)
    res = np.median([np.linalg.norm((np.eye(3) - np.outer(d, d)) @ (C - o)) for o, d in zip(O, D)])
    # rays must actually intersect in front of the map cameras
    if np.any([(C - o) @ d < 0 for o, d in zip(O, D)]):
        return None
    Rq = R.from_matrix(np.stack(rots)).mean().as_matrix()
    out = np.eye(4); out[:3, :3] = Rq @ G; out[:3, 3] = C
    return out, len(scored), float(res)


def segment_correction(estimates, current):
    """Rigid correction T (4x4) with T @ current_k ~ estimate_k, robust over the query frames."""
    Ts = [e @ np.linalg.inv(c) for e, c in zip(estimates, current)]
    rots = R.from_matrix(np.stack([T[:3, :3] for T in Ts]))
    tr = np.stack([T[:3, 3] for T in Ts])
    med = np.median(tr, axis=0)
    keep = np.linalg.norm(tr - med, axis=1) < max(0.25, 2.5 * np.median(np.linalg.norm(tr - med, axis=1)))
    T = np.eye(4); T[:3, :3] = rots[keep].mean().as_matrix(); T[:3, 3] = tr[keep].mean(0)
    return T, int(keep.sum())
