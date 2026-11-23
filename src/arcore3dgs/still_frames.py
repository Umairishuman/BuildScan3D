"""Find the moments the camera was held still, from the gyroscope (FEATURELESS_TRACKING_PLAN §10).

Tayyab (2026-11-20): during the scan_009 recording he held the phone still at several points along the room so there
would be clear pictures. Still means no motion blur and no rolling-shutter shear, so frames from those moments are
the best references: as held-out test views (10.a: their error then measures the 3D model, not blur) and as anchors.

A still stretch: the camera's rotation speed stays under --max_deg_s (default 6 deg/s, computed over 0.1 s windows)
for at least --min_s seconds (default 0.4 s). scan_009 (median 16.8 deg/s): 4 deg/s / 0.5 s -> 4 stretches (2.2 s),
6 / 0.4 -> 9 (6.7 s), 8 / 0.4 -> 15 (14.5 s); at 6 deg/s and 25 ms exposure the blur is ~4 px. Rotation dominates image motion in a room, so the gyro alone is enough.

  python src/arcore3dgs/still_frames.py <dataset> <keyframe or sfm dir (frames.json)> <sfm dir with sparse/0>
      [--bg_json …] [--max_deg_s 6] [--min_s 0.4] [--split_out <file>] [--per_stretch 1] [--json_out <file>]

--split_out writes a held-out list for run_v8.py --split / eval_offpath.py: the --per_stretch keyframes nearest the
middle of each still stretch (the rest of the stretch keeps training, so the model still sees that view).
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.spatial.transform import Rotation as R

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs_rectify  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset"); ap.add_argument("work"); ap.add_argument("calib")
    ap.add_argument("--bg_json", default=None)
    ap.add_argument("--max_deg_s", type=float, default=6.0)
    ap.add_argument("--min_s", type=float, default=0.4)
    ap.add_argument("--split_out", default=None); ap.add_argument("--per_stretch", type=int, default=1)
    ap.add_argument("--json_out", default=None)
    a = ap.parse_args()

    meta = json.load(open(os.path.join(a.work, "frames.json")))
    off = meta.get("pose_offset", 0.0)
    camrot, _, _ = rs_rectify.setup(a.dataset, meta, a.calib, a.bg_json)
    T = np.array([f["pts"] for f in meta["frames"]]) + off
    tt = np.arange(T.min(), T.max(), 0.02)
    Rs = camrot(tt)
    rate = np.zeros(len(tt))
    h = 2                                                                   # +-0.04 s, i.e. a 0.08 - 0.1 s window
    for i in range(len(tt)):
        i0, i1 = max(i - h, 0), min(i + h, len(tt) - 1)
        rate[i] = np.degrees(np.linalg.norm(R.from_matrix(Rs[i0].T @ Rs[i1]).as_rotvec())) / (tt[i1] - tt[i0])
    still = rate < a.max_deg_s
    stretches, i = [], 0
    while i < len(tt):
        if still[i]:
            j = i
            while j + 1 < len(tt) and still[j + 1]:
                j += 1
            if tt[j] - tt[i] >= a.min_s:
                stretches.append((float(tt[i]), float(tt[j]), float(np.median(rate[i:j + 1]))))
            i = j + 1
        else:
            i += 1
    print(f"rotation speed over the walk: median {np.median(rate):.1f} deg/s; still (< {a.max_deg_s:g} deg/s for >= "
          f"{a.min_s:g} s): {len(stretches)} stretches, {sum(b - s for s, b, _ in stretches):.1f} s of "
          f"{tt[-1] - tt[0]:.0f} s")
    names = [f["name"] for f in meta["frames"]]
    held, rows = [], []
    for s, e, r in stretches:
        inside = [k for k in range(len(T)) if s <= T[k] <= e]
        mid = sorted(inside, key=lambda k: abs(T[k] - (s + e) / 2))[:a.per_stretch]
        held += [names[k] for k in mid]
        rows.append(dict(start=round(s - off, 2), end=round(e - off, 2), rate_deg_s=round(r, 2),
                         keyframes=[names[k] for k in inside], held_out=[names[k] for k in mid]))
        print(f"   {s - off:6.1f} - {e - off:6.1f} s ({e - s:4.1f} s, {r:.1f} deg/s): {len(inside)} keyframes"
              + (f", held out {', '.join(names[k] for k in mid)}" if mid else ""))
    if a.split_out:
        open(a.split_out, "w").write("\n".join(sorted(held)) + "\n")
        print(f"{len(held)} held-out keyframes -> {a.split_out}")
    if a.json_out:
        json.dump(dict(max_deg_s=a.max_deg_s, min_s=a.min_s, stretches=rows), open(a.json_out, "w"), indent=1)


if __name__ == "__main__":
    main()
