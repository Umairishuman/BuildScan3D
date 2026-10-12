import json
import os
import sys

import cv2
import numpy as np
import pytest

import process_dataset
from conftest import write_poses


def test_export_ply_writes_header_and_points(tmp_path):
    pts = tmp_path / "points.csv"
    pts.write_text("1.0,2.0,3.0,0.9\n4.0,5.0,6.0,0.5\n")
    out = tmp_path / "out.ply"
    assert process_dataset.export_ply(str(pts), str(out)) is True
    lines = out.read_text().splitlines()
    assert lines[0] == "ply" and "element vertex 2" in lines
    assert lines[lines.index("end_header") + 1].startswith("1.0 2.0 3.0")
    assert len(lines) == lines.index("end_header") + 1 + 2


def test_export_ply_without_points_returns_false(tmp_path):
    assert process_dataset.export_ply(None, str(tmp_path / "x.ply")) is False
    assert process_dataset.export_ply(str(tmp_path / "missing.csv"), str(tmp_path / "x.ply")) is False
    empty = tmp_path / "empty.csv"
    empty.write_text("")
    assert process_dataset.export_ply(str(empty), str(tmp_path / "x.ply")) is False


def test_main_builds_transforms_json_from_a_synthetic_capture(tmp_path, monkeypatch):
    video = tmp_path / "dataset.avi"
    writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (64, 48))
    if not writer.isOpened():
        pytest.skip("this OpenCV build cannot write test videos")
    for i in range(20):
        writer.write(np.full((48, 64, 3), i * 10, dtype=np.uint8))
    writer.release()
    write_poses(tmp_path / "poses.csv", [(t / 10, (t / 10, 0.0, 0.0), t * 5.0) for t in range(0, 20)],
                fx=55.0, fy=56.0, cx=32.0, cy=24.0)
    out = tmp_path / "ns"
    monkeypatch.setattr(sys, "argv", ["process_dataset.py", "--video", str(video),
                                      "--csv", str(tmp_path / "poses.csv"), "--output_dir", str(out)])
    process_dataset.main()

    data = json.loads((out / "transforms.json").read_text())
    assert (data["w"], data["h"]) == (64, 48)
    assert np.isclose(data["fl_x"], 55.0) and np.isclose(data["fl_y"], 56.0)
    assert len(data["frames"]) == 20
    assert all(os.path.exists(out / fr["file_path"]) for fr in data["frames"])
    first = np.array(data["frames"][0]["transform_matrix"])
    assert first.shape == (4, 4) and np.allclose(first[3], [0, 0, 0, 1])
    assert np.allclose(first[:3, 3], [0.0, 0.0, 0.0])   # frame 0 is matched to the first pose
    assert "ply_file_path" not in data                  # no points.csv given
