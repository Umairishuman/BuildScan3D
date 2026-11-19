"""Fixture check sheet for one processed room (COMPLETION_PLAN 4.2 / E3).

Turns semantics v10's output (`semantic.json`) into a Markdown sheet the person who knows the room fills in while
viewing the model: for every accepted fixture its class, height above the floor, size and wall, with a column to
mark it real / wrong; then a table for fixtures the pipeline missed. The filled-in sheet gives the room's found /
missed / false counts (precision and recall per class for E3).

  python src/arcore3dgs/fixture_checklist.py --semantic <gs>/semantic_v10/semantic.json [--layout <gs>/layout/layout.json]
      [--out <gs>/semantic_v10/fixture_check.md] [--title "scan #3 classroom, R-035"] [--rejected]

--rejected adds a table of the candidates the class rules rejected (with the rule that failed), so the person can
mark rejections that were real fixtures (missed by the rules, not by the detector).

Standard library only.
"""
import argparse, json, os

ap = argparse.ArgumentParser()
ap.add_argument("--semantic", required=True); ap.add_argument("--layout", default="")
ap.add_argument("--out", default=""); ap.add_argument("--title", default="")
ap.add_argument("--rejected", action="store_true", help="also list the rejected candidates for checking")
args = ap.parse_args()
sem = json.load(open(args.semantic))
out = args.out or os.path.join(os.path.dirname(args.semantic), "fixture_check.md")
lay = json.load(open(args.layout)) if args.layout else None

L = [f"# Fixture check: {args.title or os.path.dirname(os.path.dirname(os.path.abspath(args.semantic)))}", ""]
L.append(f"Model: `{os.path.abspath(args.semantic)}`. Checked by: ____ on ____ (date), while viewing the model.")
L.append("")
if lay:
    L.append(f"Room from the layout: height {lay['height']:.2f} m"
             + (f" ({lay['ceiling_source']})" if lay.get("ceiling_source") else "")
             + f", {len(lay['walls'])} walls ("
             + ", ".join(f"wall {w['id']} {w['length']:.2f} m" for w in lay["walls"]) + f"), {len(lay['corners'])} corners."
             + (" Warnings: " + "; ".join(lay["warnings"]) if lay.get("warnings") else ""))
    L.append("")
L.append("Heights are above the fitted floor; \"centre\" is the middle of the fixture. Wall numbers as in the layout "
         "plan (`layout/plan.png`). Mark each row **real** (it is there and is that kind of thing), **wrong class** "
         "(something is there but it is another thing: write what), or **false** (nothing like it there).")
L.append("")
L.append("| # | Fixture | Class | Centre above floor | Bottom – top | Width × height | Wall (m along) | Frames | Real / wrong class / false | Note |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
fx = sorted(sem["fixtures"], key=lambda f: (f["cls"], f["id"]))
for i, f in enumerate(fx, 1):
    bt = f"{f['bottom']:.2f} – {f['top']:.2f} m" if "bottom" in f and "top" in f else "–"
    wall = f"{f['wall']} ({f['along_wall']:.2f})" if f.get("wall") is not None and f.get("along_wall") is not None else "none"
    L.append(f"| {i} | {f['id']} | {f['cls']} | {f['height_above_floor']:.2f} m | {bt} | {f['width']:.2f} × {f['height']:.2f} m "
             f"| {wall} | {f['views']} | | |")
L += ["", "## Missed: fixtures in the room that are not in the list above", "",
      "Only fixtures that were visible in the recording count (not ones behind furniture).", "",
      "| # | Class | Where (wall, height, near what) | Note |", "|---|---|---|---|", "| 1 | | | |", "| 2 | | | |", "| 3 | | | |", ""]
counts = {}
for f in fx:
    counts[f["cls"]] = counts.get(f["cls"], 0) + 1
L += ["## Summary (filled in after the check)", "",
      "| Class | Found by the pipeline | Real | Wrong class | False | Missed |", "|---|---|---|---|---|---|"]
L += [f"| {c} | {n} | | | | |" for c, n in sorted(counts.items())]
L += [f"| **all** | {len(fx)} | | | | |", ""]
L.append(f"{len(sem.get('rejected', []))} candidates were rejected by the class rules (`semantic.json` → `rejected`, with reasons).")
if args.rejected and sem.get("rejected"):
    L += ["", "## Rejected candidates: was any of them a real fixture?", "",
          "The detector saw these but a size / position rule or the crop check threw them out. Mark **yes** only if "
          "that fixture really is there (then it counts as missed by the rules).", "",
          "| # | Detected as | Centre above floor | Bottom – top | Width × height | Wall (m off it) | Frames | Rule that failed | Real fixture? |",
          "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(sorted(sem["rejected"], key=lambda r: (r["cls"], -r["views"])), 1):
        bt = f"{r['bottom']:.2f} – {r['top']:.2f} m" if "bottom" in r and "top" in r else "–"
        wall = f"{r['wall']} ({r['dist_to_wall']:.2f})" if r.get("wall") is not None and r.get("dist_to_wall") is not None else "none"
        L.append(f"| {i} | {r['cls']} | {r['height_above_floor']:.2f} m | {bt} | {r['width']:.2f} × {r['height']:.2f} m "
                 f"| {wall} | {r['views']} | {r['rejected']} | |")
open(out, "w").write("\n".join(L) + "\n")
print(f"{len(fx)} fixtures -> {out}")
