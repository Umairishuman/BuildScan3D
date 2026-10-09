"""Shared loading of an ARCore capture (dataset.mp4 + poses.csv + points.csv).

Conventions (verified on roomAttemptSadness by correlating pose angular velocity with optical flow):
  * Video frames are the raw landscape sensor image (W=1920, H=1080). Do NOT rotate for geometry.
  * poses.csv = camera.getPose(): camera-to-world, OpenGL camera axes (x right, y up, looking -z),
    expressed for that same landscape image. World frame is gravity aligned, +Y up, metres.
  * poses.csv timestamps (frame.getTimestamp, ns) minus the first one == video PTS (s), +/- ~1 frame.
"""
import os, subprocess
import numpy as np
from scipy.spatial.transform import Rotation as R, Slerp

# OpenGL camera (x right, y up, -z fwd) <-> OpenCV camera (x right, y down, +z fwd)
GL_TO_CV = np.diag([1.0, -1.0, -1.0])


class Capture:
    def __init__(self, root, pose_offset=0.0, max_pose_gap=0.12):
        self.root = root
        self.video = os.path.join(root, "dataset.mp4")
        self.pose_offset = pose_offset
        self.max_pose_gap = max_pose_gap

        P = np.loadtxt(os.path.join(root, "poses.csv"), delimiter=",", dtype=np.float64)
        P = P[np.argsort(P[:, 0], kind="stable")]
        P = P[np.unique(P[:, 0], return_index=True)[1]]
        self.t0_ns = P[0, 0]
        self.t = (P[:, 0] - self.t0_ns) / 1e9
        self.pos = P[:, 1:4]
        self.rot = R.from_quat(P[:, 4:8])
        self._slerp = Slerp(self.t, self.rot)
        self.fx, self.fy, self.cx, self.cy = P[:, 8:12].mean(0)

        self.pts = np.sort(np.array(subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time",
             "-of", "csv=p=0", self.video]).split(), dtype=np.float64))

        pts_path = os.path.join(root, "points.csv")
        if os.path.exists(pts_path):
            Q = np.loadtxt(pts_path, delimiter=",", dtype=np.float64, usecols=(0, 1, 2, 3))
            Q = Q[np.isfinite(Q).all(1)]                  # older app builds logged NaN points
            self.sp_t = (Q[:, 0] - self.t0_ns) / 1e9
            self.sp_xyz = Q[:, 1:4]
            self.sp_times = np.unique(self.sp_t)
        else:
            self.sp_t = None

        # tracking.csv (newer app builds): every frame incl. non-TRACKING -> intervals where ARCore lost
        # tracking. After a loss ARCore relocalises and its world frame can jump, so frames shortly after
        # a loss are unreliable (roomAttemptSadness2: 91% of keyframes < 2 s after a loss were inconsistent).
        self.lost = np.zeros((0, 2))
        tr_path = os.path.join(root, "tracking.csv")
        if os.path.exists(tr_path):
            ts, ok = [], []
            for line in open(tr_path):
                parts = line.strip().split(",")
                if len(parts) >= 2 and parts[0].isdigit():
                    ts.append(int(parts[0])); ok.append(parts[1] == "TRACKING")
            ts = (np.array(ts, dtype=np.float64) - self.t0_ns) / 1e9
            ok = np.array(ok)
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
            self.lost = np.array(segs).reshape(-1, 2)

    def tracking_settled(self, t, settle=3.0):
        """False if pose-time t is inside a tracking loss or within `settle` s after one."""
        if len(self.lost) == 0:
            return True
        return not np.any((t >= self.lost[:, 0]) & (t <= self.lost[:, 1] + settle))

    def loss_between(self, ta, tb):
        """True if a tracking loss happened between pose-times ta < tb."""
        return bool(np.any((self.lost[:, 1] >= ta) & (self.lost[:, 0] <= tb))) if len(self.lost) else False

    def K(self, scale=1.0):
        return np.array([[self.fx * scale, 0, self.cx * scale], [0, self.fy * scale, self.cy * scale], [0, 0, 1]])

    def pose_at(self, t):
        """c2w (4x4, OpenGL camera convention) at pose-time t, or None inside a tracking gap."""
        if t < self.t[0] or t > self.t[-1]:
            return None
        i = np.searchsorted(self.t, t, side="right")
        i0, i1 = max(i - 1, 0), min(i, len(self.t) - 1)
        if self.t[i1] - self.t[i0] > self.max_pose_gap:
            return None
        a = 0.0 if i0 == i1 else (t - self.t[i0]) / (self.t[i1] - self.t[i0])
        c2w = np.eye(4)
        c2w[:3, :3] = self._slerp([t]).as_matrix()[0]
        c2w[:3, 3] = (1 - a) * self.pos[i0] + a * self.pos[i1]
        return c2w

    def frame_pose(self, k):
        return self.pose_at(self.pts[k] + self.pose_offset)

    def sparse_points_near(self, t, window=0.5):
        """ARCore feature points (world, metres) from point-cloud snapshots within +/- window s of t."""
        if self.sp_t is None:
            return np.zeros((0, 3))
        m = np.abs(self.sp_t - t) <= window
        return self.sp_xyz[m]


def project(points_w, c2w_gl, K, W, H):
    """World points -> pixel (u,v) and OpenCV depth z for an OpenGL c2w. Returns u, v, z, in-view mask."""
    w2c = np.linalg.inv(c2w_gl)
    pc = (w2c[:3, :3] @ points_w.T).T + w2c[:3, 3]
    pc = pc @ GL_TO_CV.T
    z = pc[:, 2]
    u = K[0, 0] * pc[:, 0] / np.maximum(z, 1e-6) + K[0, 2]
    v = K[1, 1] * pc[:, 1] / np.maximum(z, 1e-6) + K[1, 2]
    m = (z > 0.1) & (u >= 0) & (u < W) & (v >= 0) & (v < H)
    return u, v, z, m
