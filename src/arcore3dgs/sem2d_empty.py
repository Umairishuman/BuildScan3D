"""Stand-in for semantic2d.py when fixture detection is skipped (run_full.sh with SEMANTICS=0, 2026-11-28).

Writes <work>/<out>/detections.json with semantic2d.py's class list and no frames, so semantic3d.py runs without any
2D votes: it labels walls / floor / ceiling (and openings) from the layout only, no fixtures. Mesh labels, the web
bundle and the plan then work as usual. Saves the 2D detection (~12 - 14 min per room on the RTX 3070), the CLIP
check and the second semantic3d pass.

  python src/arcore3dgs/sem2d_empty.py --work <work_sfm> [--out semantic2d_none]
"""
import argparse
import ast
import json
import os

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--out", default="semantic2d_none")
args = ap.parse_args()

# the class lists as semantic2d.py defines them (read from its source: importing it would load the models)
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "semantic2d.py"), encoding="utf-8").read()
lists = {}
for node in ast.parse(src).body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) \
            and node.targets[0].id in ("CLASSES", "DECOYS"):
        lists[node.targets[0].id] = ast.literal_eval(node.value)
out = os.path.join(args.work, args.out)
os.makedirs(out, exist_ok=True)
det = dict(classes=lists["CLASSES"] + lists["DECOYS"], decoys=lists["DECOYS"], frames={}, skipped=True,
           note="SEMANTICS=0: no fixture detection; semantic3d.py labels the structure from the layout only")
json.dump(det, open(os.path.join(out, "detections.json"), "w"), indent=1)
print(f"no fixture detection: {os.path.join(out, 'detections.json')} ({len(det['classes'])} classes, 0 frames)")
