"""fallback.py bridges ARCore tracking losses with the IMU. Tests of its CPU-side maths on synthetic data."""
import numpy as np
from scipy.spatial.transform import Rotation as R

import fallback
from conftest import T0_NS, write_poses


class FakeImu:
    """Stands in for fallback.Imu: constant gyro and accelerometer readings, no recording needed."""

    def __init__(self, gyro=(0.0, 0.0, 0.0), accel=(0.0, 9.81, 0.0)):
        self._g, self._a = np.array(gyro, float), np.array(accel, float)

    def gyro(self, t):
        return np.tile(self._g, (len(np.atleast_1d(t)), 1))

    def accel(self, t):
        return np.tile(self._a, (len(np.atleast_1d(t)), 1))


IDENTITY_CAL = dict(Rci=np.eye(3), off=0.0, bg=np.zeros(3), ba=np.zeros(3))


# ---------------------------------------------------------------- loading
def test_load_poses_sorts_and_drops_duplicate_times(tmp_path):
    rows = [(0.2, (2, 0, 0), 20.0), (0.0, (0, 0, 0), 0.0), (0.1, (1, 0, 0), 10.0), (0.1, (1, 0, 0), 10.0)]
    write_poses(tmp_path / "poses.csv", rows)
    P = fallback.load_poses(str(tmp_path))
    assert P.shape == (3, 12)
    assert np.all(np.diff(P[:, 0]) > 0)


def test_load_lost_returns_the_tracking_loss_interval(tmp_path):
    states = ["TRACKING"] * 5 + ["PAUSED"] * 3 + ["TRACKING"] * 5
    with open(tmp_path / "tracking.csv", "w") as f:
        for k, s in enumerate(states):
            f.write(f"{int(T0_NS + k * 1e8)},{s},NONE\n")
    segs = fallback.load_lost(str(tmp_path), T0_NS)
    assert len(segs) == 1
    assert np.allclose(segs[0], (0.5, 0.8))


def test_load_lost_with_no_loss_is_empty(tmp_path):
    with open(tmp_path / "tracking.csv", "w") as f:
        for k in range(6):
            f.write(f"{int(T0_NS + k * 1e8)},TRACKING,NONE\n")
    assert fallback.load_lost(str(tmp_path), T0_NS) == []


def test_load_lost_loss_at_the_very_end_is_closed_at_the_last_sample(tmp_path):
    with open(tmp_path / "tracking.csv", "w") as f:
        for k, s in enumerate(["TRACKING", "TRACKING", "PAUSED", "PAUSED"]):
            f.write(f"{int(T0_NS + k * 1e8)},{s},NONE\n")
    segs = fallback.load_lost(str(tmp_path), T0_NS)
    assert len(segs) == 1 and np.isclose(segs[0][1], 0.3)


# ---------------------------------------------------------------- helpers
def test_smooth_keeps_length_and_constant_signal():
    x = np.ones((50, 3)) * [1.0, 2.0, 3.0]
    y = fallback.smooth(x, 5)
    assert y.shape == x.shape
    assert np.allclose(y[5:-5], x[5:-5])                      # interior untouched (edges are zero-padded)


def test_smooth_window_of_one_is_identity():
    x = np.random.default_rng(0).normal(size=(20, 3))
    assert np.allclose(fallback.smooth(x, 1), x)


def test_imu_interpolates_linearly_between_samples():
    obj = fallback.Imu.__new__(fallback.Imu)                  # skip reading a recording
    obj.gt = np.array([0.0, 1.0]); obj.g = np.array([[0.0, 0.0, 0.0], [2.0, 4.0, 6.0]])
    obj.at = np.array([0.0, 1.0]); obj.a = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
    assert np.allclose(obj.gyro(np.array([0.5])), [[1.0, 2.0, 3.0]])
    assert np.allclose(obj.accel(np.array([0.25])), [[0.25, 0.25, 0.25]])


# ---------------------------------------------------------------- rotation integration
def test_gyro_forward_constant_rate_gives_the_expected_angle():
    ts = np.linspace(0.0, 1.0, 101)
    w = (0.0, 0.0, np.deg2rad(90.0))                          # 90 deg/s about the camera z axis
    rots = fallback.gyro_forward(ts, R.identity(), FakeImu(gyro=w), IDENTITY_CAL)
    assert len(rots) == len(ts)
    assert np.isclose(np.degrees(rots[-1].magnitude()), 90.0, atol=0.1)
    assert np.allclose(rots[-1].as_rotvec() / rots[-1].magnitude(), [0, 0, 1], atol=1e-6)


def test_gyro_forward_without_rotation_stays_put():
    ts = np.linspace(0.0, 1.0, 11)
    start = R.from_euler("y", 30, degrees=True)
    rots = fallback.gyro_forward(ts, start, FakeImu(), IDENTITY_CAL)
    assert all(np.isclose((start.inv() * r).magnitude(), 0.0, atol=1e-9) for r in rots)


def test_gyro_bias_is_subtracted():
    ts = np.linspace(0.0, 1.0, 51)
    cal = dict(IDENTITY_CAL, bg=np.array([0.0, 0.0, 0.2]))
    rots = fallback.gyro_forward(ts, R.identity(), FakeImu(gyro=(0.0, 0.0, 0.2)), cal)
    assert np.isclose(rots[-1].magnitude(), 0.0, atol=1e-9)


# ---------------------------------------------------------------- bridging a tracking gap
def _anchors(pA, vA, pB, vB, RA=None, RB=None):
    RA = R.identity() if RA is None else RA
    RB = R.identity() if RB is None else RB
    pose = {0.0: (np.array(pA, float), RA), 2.0: (np.array(pB, float), RB)}
    vel = {0.0: np.array(vA, float), 2.0: np.array(vB, float)}
    return (lambda t: pose[float(t)]), (lambda t: vel[float(t)])


def test_bridge_stationary_camera_stays_where_it_is():
    pose_at, vel_at = _anchors((1, 2, 3), (0, 0, 0), (1, 2, 3), (0, 0, 0))
    ts, p, rots, closure_deg, drift_m = fallback.bridge(0.0, 2.0, pose_at, vel_at, FakeImu(), IDENTITY_CAL)
    assert np.allclose(p, [1, 2, 3], atol=1e-6)               # gravity cancels, nothing moves
    assert np.allclose(rots.magnitude(), 0.0, atol=1e-9)
    assert closure_deg < 1e-6 and drift_m < 1e-6


def test_bridge_constant_acceleration_matches_physics():
    # accelerometer reads gravity + 1 m/s^2 along x: after 2 s from rest, x = 0.5 * 1 * 2^2 = 2 m, v = 2 m/s
    pose_at, vel_at = _anchors((0, 0, 0), (0, 0, 0), (2, 0, 0), (2, 0, 0))
    ts, p, _, _, drift_m = fallback.bridge(0.0, 2.0, pose_at, vel_at, FakeImu(accel=(1.0, 9.81, 0.0)), IDENTITY_CAL)
    assert drift_m < 1e-3                                      # integration already agrees with the anchor
    assert np.allclose(p[-1], [2, 0, 0], atol=1e-3)
    assert np.allclose(p[len(p) // 2], [0.5, 0, 0], atol=1e-2) # halfway (t = 1 s): 0.5 * 1 * 1^2


def test_bridge_always_lands_on_the_end_anchor():
    # IMU says "stationary" but the second anchor is 1 m away: the correction must close the gap
    pose_at, vel_at = _anchors((0, 0, 0), (0, 0, 0), (1, 0, 0), (0, 0, 0))
    ts, p, _, _, drift_m = fallback.bridge(0.0, 2.0, pose_at, vel_at, FakeImu(), IDENTITY_CAL)
    assert np.isclose(drift_m, 1.0, atol=1e-6)                 # reported drift before correction
    assert np.allclose(p[0], [0, 0, 0], atol=1e-9)
    assert np.allclose(p[-1], [1, 0, 0], atol=1e-6)


def test_bridge_ends_with_the_velocity_of_the_end_anchor():
    # the IMU says "stationary", but the camera is known to be moving at 1 m/s when tracking returns
    pose_at, vel_at = _anchors((0, 0, 0), (0, 0, 0), (1, 0, 0), (1, 0, 0))
    ts, p, _, _, _ = fallback.bridge(0.0, 2.0, pose_at, vel_at, FakeImu(), IDENTITY_CAL, rate=100.0)
    v_end = (p[-1] - p[-2]) / (ts[-1] - ts[-2])
    v_start = (p[1] - p[0]) / (ts[1] - ts[0])
    assert np.isclose(v_end[0], 1.0, atol=0.05)                # matches anchor B, not just its position
    assert np.isclose(v_start[0], 0.0, atol=0.05)              # and still starts at rest


def test_bridge_times_cover_the_gap_at_the_requested_rate():
    pose_at, vel_at = _anchors((0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0))
    ts, p, rots, _, _ = fallback.bridge(0.0, 2.0, pose_at, vel_at, FakeImu(), IDENTITY_CAL, rate=50.0)
    assert np.isclose(ts[0], 0.0) and np.isclose(ts[-1], 2.0)
    assert np.allclose(np.diff(ts), 1 / 50.0, atol=1e-9)
    assert len(ts) == len(p) == len(rots)


def test_bridge_rotation_blends_from_start_to_end_orientation():
    RB = R.from_euler("y", 40, degrees=True)
    pose_at, vel_at = _anchors((0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), RB=RB)
    _, _, rots, closure_deg, _ = fallback.bridge(0.0, 2.0, pose_at, vel_at, FakeImu(), IDENTITY_CAL)
    assert np.isclose(closure_deg, 40.0, atol=1e-6)            # gyro saw no rotation, anchor B is 40 deg away
    assert np.isclose(rots[0].magnitude(), 0.0, atol=1e-9)
    assert np.isclose((RB.inv() * rots[-1]).magnitude(), 0.0, atol=1e-6)


def test_forward_positions_velocity_correction_hits_the_end_velocity():
    ts = np.linspace(0.0, 2.0, 201)
    rots = R.from_quat(np.tile(R.identity().as_quat(), (len(ts), 1)))
    p = fallback.forward_positions(ts, rots, np.zeros(3), np.zeros(3), np.array([1.0, 0, 0]), FakeImu(), IDENTITY_CAL)
    v_end = (p[-1] - p[-2]) / (ts[-1] - ts[-2])
    assert np.isclose(v_end[0], 1.0, atol=0.02)                # end velocity forced to vB = 1 m/s along x
    assert np.allclose(p[0], 0.0)
