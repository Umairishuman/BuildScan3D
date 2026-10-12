"""Pose-correction helpers from relocalize.py and sfm_colmap.py.

sfm_colmap.py runs its whole pipeline when imported, so its Sim3 fit (umeyama) is loaded from the source file
by itself, without executing the rest of the script."""
import ast
import os

import numpy as np
from scipy.spatial.transform import Rotation as R

import relocalize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_function(path, name, **namespace):
    """Compile one top-level function from a script without running the script."""
    tree = ast.parse(open(path, encoding="utf8").read())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = dict(np=np, **namespace)
    exec(compile(ast.Module(body=[node], type_ignores=[]), path, "exec"), ns)
    return ns[name]


umeyama = load_function(os.path.join(ROOT, "src", "arcore3dgs", "sfm_colmap.py"), "umeyama")


def rigid(yaw_deg, t):
    T = np.eye(4)
    T[:3, :3] = R.from_euler("y", yaw_deg, degrees=True).as_matrix()
    T[:3, 3] = t
    return T


# ---------------------------------------------------------------- relocalize.segment_correction
def _poses(n=8):
    rng = np.random.default_rng(1)
    return [rigid(rng.uniform(-60, 60), rng.uniform(-2, 2, 3)) for _ in range(n)]


def test_segment_correction_recovers_a_known_rigid_shift():
    true = rigid(12.0, [0.4, -0.1, 0.25])
    current = _poses()
    estimates = [true @ c for c in current]
    T, kept = relocalize.segment_correction(estimates, current)
    assert kept == len(current)
    assert np.allclose(T, true, atol=1e-6)


def test_segment_correction_ignores_a_wildly_wrong_estimate():
    true = rigid(-8.0, [0.3, 0.0, -0.2])
    current = _poses(9)
    estimates = [true @ c for c in current]
    estimates[3] = rigid(0.0, [5.0, 5.0, 5.0]) @ estimates[3]      # one bad match, 8.6 m off
    T, kept = relocalize.segment_correction(estimates, current)
    assert kept == len(current) - 1
    assert np.allclose(T[:3, 3], true[:3, 3], atol=1e-6)


def test_segment_correction_identity_when_nothing_moved():
    current = _poses(5)
    T, kept = relocalize.segment_correction(list(current), current)
    assert np.allclose(T, np.eye(4), atol=1e-9) and kept == 5


# ---------------------------------------------------------------- sfm_colmap.umeyama (similarity fit)
def test_umeyama_recovers_scale_rotation_translation():
    rng = np.random.default_rng(2)
    src = rng.normal(size=(30, 3))
    Rm = R.from_euler("xyz", [20, -35, 70], degrees=True).as_matrix()
    dst = 2.5 * src @ Rm.T + np.array([1.0, -2.0, 0.5])
    s, Rf, t = umeyama(src, dst)
    assert np.isclose(s, 2.5)
    assert np.allclose(Rf, Rm, atol=1e-8)
    assert np.allclose(t, [1.0, -2.0, 0.5], atol=1e-8)
    assert np.allclose(s * src @ Rf.T + t, dst, atol=1e-8)


def test_umeyama_identity():
    pts = np.random.default_rng(3).normal(size=(10, 3))
    s, Rf, t = umeyama(pts, pts)
    assert np.isclose(s, 1.0) and np.allclose(Rf, np.eye(3), atol=1e-9) and np.allclose(t, 0.0, atol=1e-9)


def test_umeyama_result_is_a_proper_rotation_not_a_mirror():
    pts = np.random.default_rng(4).normal(size=(12, 3))
    mirrored = pts * [1.0, 1.0, -1.0]                              # a reflection cannot be a rotation
    _, Rf, _ = umeyama(pts, mirrored)
    assert np.isclose(np.linalg.det(Rf), 1.0)
