"""openings.py: doorways and window openings from gaps in a synthetic wall (#9)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "arcore3dgs"))
from openings import find_openings  # noqa: E402

CEN, DIR, NRM = np.array([0.0, 0.0]), np.array([1.0, 0.0]), np.array([0.0, 1.0])   # wall along x at z = 0, room at z > 0


def wall_points(holes, behind=True, step=0.02, length=5.0, height=3.0):
    """Dense points on the wall face except inside the holes [(x0, x1, y0, y1)], plus points 1.5 m behind the wall
    (z = -1.5) everywhere if `behind`: what the cameras see through a gap."""
    xs, ys = np.meshgrid(np.arange(0, length, step), np.arange(0, height, step))
    x, y = xs.ravel(), ys.ravel()
    on = np.ones(len(x), bool)
    for x0, x1, y0, y1 in holes:
        on &= ~((x >= x0) & (x < x1) & (y >= y0) & (y < y1))
    pts = [np.c_[x[on], y[on], np.zeros(on.sum())]]
    if behind:
        pts.append(np.c_[x, y, np.full(len(x), -1.5)])
    P = np.vstack(pts)
    return P, np.ones(len(P))


def run(P, o):
    return find_openings(P, o, CEN, DIR, NRM, 0.0, 5.0, 0.0, 3.0)


def test_doorway_found():
    P, o = wall_points([(1.0, 1.9, 0.0, 2.1)])
    ops = run(P, o)
    assert [op["kind"] for op in ops] == ["doorway"]
    assert abs(ops[0]["width"] - 0.9) <= 0.11 and abs(ops[0]["along"] - 1.45) <= 0.1 and ops[0]["bottom"] < 0.1


def test_window_opening_found():
    P, o = wall_points([(3.0, 4.2, 0.9, 2.1)])
    ops = run(P, o)
    assert [op["kind"] for op in ops] == ["window opening"]
    assert abs(ops[0]["bottom"] - 0.9) <= 0.11 and abs(ops[0]["top"] - 2.1) <= 0.11


def test_unseen_gap_is_not_an_opening():
    P, o = wall_points([(1.0, 1.9, 0.0, 2.1)], behind=False)
    assert run(P, o) == []


def test_small_gap_ignored():
    P, o = wall_points([(2.0, 2.15, 1.0, 1.15)])
    assert run(P, o) == []


def test_full_wall_has_no_openings():
    P, o = wall_points([])
    assert run(P, o) == []


def test_few_stray_points_behind_are_not_an_opening():
    """a gap with only a sprinkle of the model behind it (stray splats, R-054 scan #3) is not an opening"""
    P, o = wall_points([(1.0, 1.9, 0.0, 2.1)], behind=False)
    stray = np.c_[np.random.default_rng(0).uniform(1.0, 1.9, 40), np.random.default_rng(1).uniform(0, 2.1, 40), np.full(40, -1.0)]
    P = np.vstack([P, stray])
    assert run(P, np.ones(len(P))) == []
