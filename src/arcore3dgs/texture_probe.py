"""How featureless are a capture's keyframes, and what else in them could be tracked?

Per keyframe (at half resolution): SIFT keypoints (what COLMAP's default features see), LSD line segments and long
lines (> 15% of the image size: wall / floor / ceiling junctions, door and window frames), and the share of pixels
with a faint but usable gradient (Sobel magnitude 8-40: the signal a direct / photometric method tracks) or a strong
one (>= 40). Grouped by ARCore pose state and, with --model, by whether SfM kept the frame.

  python src/arcore3dgs/texture_probe.py dataset/<capture>/work_v9pf [--model dataset/<capture>/work_v9pf_sfm/frames.json]
      [--step 1] [--out probe.json]

Written 2026-11-18 for docs/progress/FEATURELESS_TRACKING_PLAN.md (first numbers: scan_009_057ed3beb4fc).
"""
import argparse
import json
import os

import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("work", help="keyframe folder with frames.json and images/")
ap.add_argument("--model", default=None, help="frames.json of an SfM / export step: which keyframes it kept")
ap.add_argument("--step", type=int, default=1, help="use every N-th keyframe")
ap.add_argument("--out", default=None, help="write the per-frame rows as JSON")
args = ap.parse_args()

frames = json.load(open(os.path.join(args.work, "frames.json")))["frames"][::args.step]
kept = None
if args.model:
    kept = {f["name"] for f in json.load(open(args.model))["frames"]}

sift = cv2.SIFT_create()
lsd = cv2.createLineSegmentDetector()
rows = []
for f in frames:
    name = f["name"] if f["name"].endswith(".jpg") else f["name"] + ".jpg"
    im = cv2.imread(os.path.join(args.work, "images", name), cv2.IMREAD_GRAYSCALE)
    if im is None:
        continue
    im = cv2.resize(im, (im.shape[1] // 2, im.shape[0] // 2), interpolation=cv2.INTER_AREA)
    H, W = im.shape
    n_sift = len(sift.detect(im, None))
    seg = lsd.detect(im)[0]
    length = np.zeros(0) if seg is None else np.hypot(seg[:, 0, 2] - seg[:, 0, 0], seg[:, 0, 3] - seg[:, 0, 1])
    g = np.hypot(cv2.Sobel(im, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(im, cv2.CV_32F, 0, 1, ksize=3))
    rows.append(dict(name=f["name"], arcore=f.get("arcore_pose", "ok"),
                     kept=None if kept is None else f["name"] in kept, sift=n_sift, lines=int(len(length)),
                     long_lines=int((length > 0.15 * max(H, W)).sum()),
                     faint=float(((g > 8) & (g < 40)).mean()), strong=float((g >= 40).mean()),
                     brightness=float(im.mean())))

if args.out:
    json.dump(rows, open(args.out, "w"), indent=1)


def summary(sel, label):
    if not sel:
        return
    med = lambda k: float(np.median([r[k] for r in sel]))
    p10 = lambda k: float(np.percentile([r[k] for r in sel], 10))
    print(f"{label:24s} n={len(sel):5d}  SIFT median {med('sift'):5.0f} (p10 {p10('sift'):4.0f})  "
          f"lines {med('lines'):4.0f}  long lines {med('long_lines'):3.0f} (p10 {p10('long_lines'):2.0f})  "
          f"faint-gradient px {med('faint') * 100:4.1f}%  strong px {med('strong') * 100:4.1f}%  "
          f"brightness {med('brightness'):5.1f}")


summary(rows, "all keyframes")
for state in ["ok", "unsettled", "lost"]:
    summary([r for r in rows if r["arcore"] == state], f"ARCore {state}")
if kept is not None:
    summary([r for r in rows if r["kept"]], "kept by the model")
    summary([r for r in rows if not r["kept"]], "not kept")
