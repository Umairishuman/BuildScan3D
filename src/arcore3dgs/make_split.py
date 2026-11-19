"""Held-out split for eval_offpath.py: N contiguous stretches of the walk (default 6 x 3 s), the same kind of split as
offpath_test.txt in R-014 / R-020. The stretches are spread evenly over the middle 90% of the recording, so start and
end (often the camera still settling) are not used. Deterministic: same frames.json -> same list.

  python src/arcore3dgs/make_split.py --work <work_sfm> --out <dataset>/offpath_test.txt [--n 6] [--seconds 3]

Then: run_v8.py ... --split <dataset>/offpath_test.txt, and score with eval_offpath.py.
"""
import argparse, json, os

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True, help="work_<tag>_sfm folder with frames.json")
ap.add_argument("--out", required=True)
ap.add_argument("--n", type=int, default=6, help="number of held-out stretches")
ap.add_argument("--seconds", type=float, default=3.0, help="length of each stretch")
args = ap.parse_args()

frames = json.load(open(os.path.join(args.work, "frames.json")))["frames"]
t = [f["pts"] for f in frames]
t0, t1 = min(t), max(t)
lo, span = t0 + 0.05 * (t1 - t0), 0.9 * (t1 - t0)
held = []
for k in range(args.n):
    c = lo + (k + 0.5) / args.n * span
    held += [f["name"] for f in frames if abs(f["pts"] - c) <= args.seconds / 2]
held = sorted(set(held))
open(args.out, "w").write("\n".join(held) + "\n")
print(f"{len(held)} of {len(frames)} frames held out ({100 * len(held) / len(frames):.1f}%), "
      f"{args.n} stretches of {args.seconds:g} s over {t1 - t0:.1f} s -> {args.out}")
