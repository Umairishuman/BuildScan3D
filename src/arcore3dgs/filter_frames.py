"""Remove keyframes recorded during / shortly after an ARCore tracking loss from an existing work dir
(prepare.py now does this itself for new runs). Images and depth files stay on disk; only frames.json
changes, and stale stage caches (ba_tracks.npz) are deleted so later stages recompute.
"""
import os, sys, json, argparse
sys.path.insert(0, os.path.dirname(__file__))
from common import Capture

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--settle", type=float, default=3.0)
args = ap.parse_args()
p = os.path.join(args.work, "frames.json")
meta = json.load(open(p))
cap = Capture(meta["dataset"], pose_offset=meta.get("pose_offset", 0.0))
keep = [f for f in meta["frames"] if cap.tracking_settled(f["pts"] + meta.get("pose_offset", 0.0), args.settle)]
removed = len(meta["frames"]) - len(keep)
for f in keep:                                  # restart BA from raw ARCore poses
    if "c2w_arcore" in f:
        f["c2w"] = f["c2w_arcore"]
meta["frames"] = keep
json.dump(meta, open(p, "w"), indent=1)
for c in ("ba_tracks.npz",):
    if os.path.exists(os.path.join(args.work, c)):
        os.remove(os.path.join(args.work, c))
print(f"tracking-loss segments: {len(cap.lost)}; removed {removed} keyframes within {args.settle}s of a loss; {len(keep)} remain")
