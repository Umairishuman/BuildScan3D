"""Shared fixtures: put the pipeline code on sys.path and build small synthetic ARCore capture folders."""
import os
import sys

import pytest
from scipy.spatial.transform import Rotation as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (os.path.join(ROOT, "src"), os.path.join(ROOT, "src", "arcore3dgs")):
    if p not in sys.path:
        sys.path.insert(0, p)

T0_NS = 1_000_000_000  # arbitrary first pose timestamp (ns)

# poses every 0.1 s along +x at 10 m/s, turning 100 deg/s about the y axis
LINE = [(0.0, (0.0, 0.0, 0.0), 0.0), (0.1, (1.0, 0.0, 0.0), 10.0), (0.2, (2.0, 0.0, 0.0), 20.0)]


def write_poses(path, rows, fx=500.0, fy=500.0, cx=320.0, cy=240.0):
    """rows: (t_seconds, (x, y, z), yaw_degrees). Writes the 12-column poses.csv the Android app logs."""
    with open(path, "w") as f:
        for t, pos, yaw in rows:
            q = R.from_euler("y", yaw, degrees=True).as_quat()  # x y z w
            f.write(f"{int(T0_NS + t * 1e9)},{pos[0]},{pos[1]},{pos[2]},"
                    f"{q[0]},{q[1]},{q[2]},{q[3]},{fx},{fy},{cx},{cy}\n")


@pytest.fixture
def make_capture(tmp_path, monkeypatch):
    """Build a capture folder and return a loaded common.Capture.

    ffprobe is replaced by a stub that returns the given video frame times, so the tests need no ffmpeg."""
    import common

    def _make(rows, frame_times=(0.0, 0.05, 0.10), tracking=None, points=None, **kw):
        write_poses(tmp_path / "poses.csv", rows)
        (tmp_path / "dataset.mp4").write_bytes(b"")  # only has to exist
        if tracking is not None:
            with open(tmp_path / "tracking.csv", "w") as f:
                for t, state in tracking:
                    f.write(f"{int(T0_NS + t * 1e9)},{state},NONE\n")
        if points is not None:
            with open(tmp_path / "points.csv", "w") as f:
                for t, xyz in points:
                    f.write(f"{int(T0_NS + t * 1e9)},{xyz[0]},{xyz[1]},{xyz[2]},0.9\n")
        out = ("\n".join(str(t) for t in frame_times) + "\n").encode()
        monkeypatch.setattr(common.subprocess, "check_output", lambda *a, **k: out)
        return common.Capture(str(tmp_path), **kw)

    return _make
