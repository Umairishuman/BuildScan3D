import numpy as np
from scipy.spatial.transform import Rotation as R

from conftest import LINE


def test_pose_at_sample_time_returns_that_pose(make_capture):
    cap = make_capture(LINE)
    c2w = cap.pose_at(0.1)
    assert np.allclose(c2w[:3, 3], [1.0, 0, 0])
    assert np.allclose(c2w[:3, :3], R.from_euler("y", 10, degrees=True).as_matrix(), atol=1e-6)


def test_pose_between_samples_is_interpolated(make_capture):
    cap = make_capture(LINE)
    c2w = cap.pose_at(0.15)                           # halfway between 0.1 s and 0.2 s
    assert np.allclose(c2w[:3, 3], [1.5, 0, 0])
    assert np.allclose(c2w[:3, :3], R.from_euler("y", 15, degrees=True).as_matrix(), atol=1e-6)


def test_no_pose_outside_the_recorded_range(make_capture):
    cap = make_capture(LINE)
    assert cap.pose_at(-0.01) is None
    assert cap.pose_at(0.21) is None


def test_no_pose_inside_a_tracking_gap(make_capture):
    rows = [(0.0, (0, 0, 0), 0.0), (0.1, (1, 0, 0), 0.0), (0.5, (5, 0, 0), 0.0), (0.6, (6, 0, 0), 0.0)]
    cap = make_capture(rows)
    assert cap.pose_at(0.05) is not None
    assert cap.pose_at(0.3) is None                    # 0.4 s without poses is longer than max_pose_gap
    assert cap.pose_at(0.55) is not None


def test_unsorted_and_duplicate_rows_are_cleaned(make_capture):
    rows = [LINE[2], LINE[0], LINE[1], LINE[1]]        # shuffled, one timestamp twice
    cap = make_capture(rows)
    assert len(cap.t) == 3
    assert np.all(np.diff(cap.t) > 0)
    assert np.isclose(cap.t[0], 0.0)


def test_intrinsics_and_scaled_matrix(make_capture):
    cap = make_capture(LINE)
    assert (cap.fx, cap.fy, cap.cx, cap.cy) == (500.0, 500.0, 320.0, 240.0)
    assert np.allclose(cap.K(0.5), [[250, 0, 160], [0, 250, 120], [0, 0, 1]])


def test_frame_pose_uses_video_frame_time_and_offset(make_capture):
    cap = make_capture(LINE, frame_times=(0.0, 0.05, 0.10))
    assert np.allclose(cap.frame_pose(1)[:3, 3], cap.pose_at(0.05)[:3, 3])


def test_pose_offset_shifts_the_frame_time(make_capture):
    cap = make_capture(LINE, frame_times=(0.0, 0.05, 0.10), pose_offset=0.1)
    assert np.allclose(cap.frame_pose(1)[:3, 3], cap.pose_at(0.15)[:3, 3])


def test_points_csv_skips_nan_rows_and_filters_by_time(make_capture):
    pts = [(0.0, (1.0, 2.0, 3.0)), (0.05, (float("nan"), 0.0, 0.0)), (1.0, (9.0, 9.0, 9.0))]
    cap = make_capture(LINE, points=pts)
    near = cap.sparse_points_near(0.0, window=0.5)
    assert near.shape == (1, 3) and np.allclose(near[0], [1.0, 2.0, 3.0])
    assert cap.sparse_points_near(5.0, window=0.5).shape == (0, 3)


def test_missing_points_csv_gives_empty_result(make_capture):
    cap = make_capture(LINE)
    assert cap.sparse_points_near(0.0).shape == (0, 3)


def test_tracking_loss_intervals(make_capture):
    # tracking lost from 0.5 s until it is regained at 0.8 s
    states = [(k * 0.1, "TRACKING" if k < 5 or k >= 8 else "PAUSED") for k in range(13)]
    cap = make_capture(LINE, tracking=states)
    assert cap.lost.shape == (1, 2)
    assert np.allclose(cap.lost[0], [0.5, 0.8])
    assert cap.tracking_settled(0.3)
    assert not cap.tracking_settled(0.6)               # during the loss
    assert not cap.tracking_settled(1.0, settle=3.0)   # shortly after the loss
    assert cap.tracking_settled(4.0, settle=3.0)       # long after it
    assert cap.loss_between(0.4, 0.9)
    assert not cap.loss_between(0.0, 0.4)
    assert not cap.loss_between(0.9, 1.2)
