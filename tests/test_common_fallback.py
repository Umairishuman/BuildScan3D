"""common.Capture when fallback.py has repaired the tracking gaps (poses_fused.csv + fallback_report.json),
plus edge cases of the loss-interval logic."""
import json

import numpy as np

from conftest import LINE, write_poses


def write_fused(tmp_path, intervals):
    write_poses(tmp_path / "poses_fused.csv", [(t / 10, (t, 0.0, 0.0), 0.0) for t in range(0, 11)])
    (tmp_path / "fallback_report.json").write_text(json.dumps({"fallback_intervals_s": intervals}))


def lost_states():
    return [(k * 0.1, "TRACKING" if k < 5 or k >= 8 else "PAUSED") for k in range(13)]


def test_fused_poses_are_used_when_present(tmp_path, make_capture):
    write_fused(tmp_path, [[0.5, 0.8]])
    cap = make_capture(LINE)
    assert cap.using_fallback is True
    assert len(cap.t) == 11                                    # 11 rows from poses_fused.csv, not 3 from poses.csv


def test_fallback_can_be_switched_off(tmp_path, make_capture):
    write_fused(tmp_path, [[0.5, 0.8]])
    cap = make_capture(LINE, fallback=False)
    assert cap.using_fallback is False and len(cap.t) == 3


def test_is_fallback_marks_only_the_bridged_interval(tmp_path, make_capture):
    write_fused(tmp_path, [[0.5, 0.8]])
    cap = make_capture(LINE)
    assert cap.is_fallback(0.6) is True
    assert cap.is_fallback(0.5) is True and cap.is_fallback(0.8) is True      # interval ends are included
    assert cap.is_fallback(0.2) is False and cap.is_fallback(0.9) is False


def test_bridged_gap_counts_as_settled_but_a_plain_loss_does_not(tmp_path, make_capture):
    write_fused(tmp_path, [[0.5, 0.8]])
    with_fallback = make_capture(LINE, tracking=lost_states())
    assert with_fallback.tracking_settled(0.6) is True        # IMU-bridged: usable, flagged lower confidence
    plain = make_capture(LINE, tracking=lost_states(), fallback=False)
    assert plain.tracking_settled(0.6) is False


def test_no_fallback_files_means_no_fallback_intervals(make_capture):
    cap = make_capture(LINE)
    assert cap.using_fallback is False
    assert cap.is_fallback(0.1) is False


# ---------------------------------------------------------------- loss-interval edge cases
def test_no_tracking_csv_means_no_losses(make_capture):
    cap = make_capture(LINE)
    assert cap.lost.shape == (0, 2)
    assert cap.tracking_settled(0.1) is True
    assert cap.loss_between(0.0, 100.0) is False


def test_tracking_never_lost_gives_no_intervals(make_capture):
    cap = make_capture(LINE, tracking=[(k * 0.1, "TRACKING") for k in range(10)])
    assert cap.lost.shape == (0, 2)


def test_two_separate_losses_give_two_intervals(make_capture):
    states = ["TRACKING"] * 3 + ["PAUSED"] * 2 + ["TRACKING"] * 3 + ["PAUSED"] * 2 + ["TRACKING"] * 2
    cap = make_capture(LINE, tracking=[(k * 0.1, s) for k, s in enumerate(states)])
    assert cap.lost.shape == (2, 2)
    assert np.allclose(cap.lost, [[0.3, 0.5], [0.8, 1.0]])


def test_loss_that_never_recovers_ends_at_the_last_sample(make_capture):
    states = ["TRACKING"] * 3 + ["PAUSED"] * 3
    cap = make_capture(LINE, tracking=[(k * 0.1, s) for k, s in enumerate(states)])
    assert cap.lost.shape == (1, 2) and np.isclose(cap.lost[0, 1], 0.5)


# ---------------------------------------------------------------- pose_at edge cases
def test_pose_at_the_last_sample_time_is_valid(make_capture):
    cap = make_capture(LINE)
    assert np.allclose(cap.pose_at(0.2)[:3, 3], [2.0, 0.0, 0.0])
    assert np.allclose(cap.pose_at(0.0)[:3, 3], [0.0, 0.0, 0.0])


def test_interpolated_rotation_stays_a_valid_rotation(make_capture):
    cap = make_capture(LINE)
    for t in np.linspace(0.0, 0.2, 9):
        Rm = cap.pose_at(t)[:3, :3]
        assert np.allclose(Rm @ Rm.T, np.eye(3), atol=1e-9)
        assert np.isclose(np.linalg.det(Rm), 1.0)


def test_interpolated_position_stays_between_its_neighbours(make_capture):
    cap = make_capture(LINE)
    xs = [cap.pose_at(t)[0, 3] for t in np.linspace(0.0, 0.2, 21)]
    assert np.all(np.diff(xs) >= -1e-12)                       # moving along +x, never backwards
