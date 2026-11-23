"""rs_rectify.py: rolling-shutter rectification with a known rotation. Synthetic camera, no capture needed."""
import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R

import rs_rectify

K = np.array([[300.0, 0, 160.0], [0, 300.0, 120.0], [0, 0, 1.0]])
D = (0.05, -0.02, 0.001, -0.001)
W, H = 320, 240


class SpinCam:
    """camera -> world rotation turning at a constant rate about a fixed axis."""

    def __init__(self, deg_s=60.0, axis=(0.2, 1.0, 0.1)):
        self.w = np.radians(deg_s) * np.asarray(axis) / np.linalg.norm(axis)

    def __call__(self, t):
        return R.from_rotvec(np.outer(np.atleast_1d(t), self.w)).as_matrix()


def test_distort_matches_opencv():
    rng = np.random.default_rng(0)
    b = np.c_[rng.uniform(-0.4, 0.4, (50, 2)), np.ones(50)]
    ref = cv2.projectPoints(b, np.zeros(3), np.zeros(3), K, np.array(D))[0].reshape(-1, 2)
    assert np.allclose(rs_rectify.distort(b, K, D), ref, atol=1e-6)


def test_no_motion_is_identity():
    rect = rs_rectify.Rectifier(W, H, K, D, SpinCam(0.0), skew=0.02)
    mx, my = rect.maps(1.0, "rows", 1)
    assert np.abs(mx - rect.pix[..., 0]).max() < 1e-3 and np.abs(my - rect.pix[..., 1]).max() < 1e-3


def test_points_invert_the_image_map():
    cam = SpinCam(60.0)
    rect = rs_rectify.Rectifier(W, H, K, D, cam, skew=0.02)
    for axis, N in (("rows", H), ("cols", W)):
        mx, my = rect.maps(1.0, axis, 1)
        v, u = np.mgrid[20:H - 20:15, 20:W - 20:15]
        src = np.c_[mx[v, u].ravel(), my[v, u].ravel()]
        assert np.abs(src - np.c_[u.ravel(), v.ravel()]).max() > 1.0          # the shear is not negligible
        back = rs_rectify.rectify_points(src, np.full(len(src), 1.0), cam, K, D, axis, 1, 0.02, N)
        assert np.abs(back - np.c_[u.ravel(), v.ravel()]).max() < 0.3
