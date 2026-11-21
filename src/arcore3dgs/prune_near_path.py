"""Remove Gaussians that reach into the camera's path (FEATURELESS_TRACKING_PLAN §10.e).

The phone was physically carried along the camera path, so no real surface can lie within a few centimetres of it.
3DGS still puts Gaussians there: on scan_009 (R-087) a held-out view at 134 s and the last view at 186 s were
blocked by Gaussians whose rendered depth was 0.01 - 0.04 model units, while the walls are 1.3 - 2.4 units away.
They explain a training view from right in front of the lens and block every nearby view.

A Gaussian is removed when its extent reaches the path: distance from its centre to the path minus --sigmas times
its largest scale is below --radius. The path is the polyline through all keyframe camera centres (training and
held-out: the poses come from SfM / sensors, not from the held-out images), densified every 1 cm; segments longer
than --max_gap (tracking gaps, SfM jumps) are left out.

  python src/arcore3dgs/prune_near_path.py <splat.ply> <frames.json> <out.ply> [--radius 0.1] [--sigmas 2]
      [--max_gap 0.5]

Units are model units (scan_009: ~2.15 per metre, sfm_scale_check), so --radius 0.1 is ~5 cm.
"""
import argparse
import json

import numpy as np
from plyfile import PlyData, PlyElement
from scipy.spatial import cKDTree


def path_points(frames, step, max_gap):
    C = np.array([np.array(f["c2w"])[:3, 3] for f in sorted(frames, key=lambda f: f["pts"])])
    pts = [C[:1]]
    for a, b in zip(C[:-1], C[1:]):
        d = np.linalg.norm(b - a)
        if d > max_gap:
            pts.append(b[None])
            continue
        n = max(int(np.ceil(d / step)), 1)
        pts.append(a + np.outer(np.arange(1, n + 1) / n, b - a))
    return np.concatenate(pts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ply"); ap.add_argument("frames"); ap.add_argument("out")
    ap.add_argument("--radius", type=float, default=0.1)
    ap.add_argument("--sigmas", type=float, default=2.0)
    ap.add_argument("--max_gap", type=float, default=0.5)
    ap.add_argument("--step", type=float, default=0.02)
    a = ap.parse_args()
    ply = PlyData.read(a.ply); v = ply["vertex"].data
    X = np.c_[v["x"], v["y"], v["z"]].astype(np.float64)
    s = np.exp(np.c_[v["scale_0"], v["scale_1"], v["scale_2"]]).max(1)
    P = path_points(json.load(open(a.frames))["frames"], a.step, a.max_gap)
    d, _ = cKDTree(P).query(X)
    bad = d - a.sigmas * s < a.radius
    op = 1 / (1 + np.exp(-v["opacity"]))
    print(f"{len(X)} Gaussians, path {len(P)} points; removed {bad.sum()} ({100 * bad.mean():.2f} %): centre within "
          f"{a.radius:g} {int((d < a.radius).sum())}, reaching in by size {int((bad & (d >= a.radius)).sum())}; "
          f"their opacity median {np.median(op[bad]) if bad.any() else 0:.2f}, largest scale median "
          f"{np.median(s[bad]) if bad.any() else 0:.3f}")
    PlyData([PlyElement.describe(v[~bad], "vertex")], text=False).write(a.out)


if __name__ == "__main__":
    main()
