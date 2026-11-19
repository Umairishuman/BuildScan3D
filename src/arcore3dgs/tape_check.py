"""Model vs tape measure (COMPLETION_PLAN E2, proposal NFR6: error <= 5%).

A room's tape sheet is a CSV next to the dataset (`<dataset>/tape.csv`), one row per measured item:

    item,kind,tape_m,model_m,note
    room length,room_length,6.700,,wall to wall along the long side
    room height,height,2.71;2.72;2.71,,three readings
    table long side,manual,1.750,1.748,viewer measure tool (v3 model)

  kind  room_length / room_width   the larger / smaller wall-to-wall distance in layout.json
        height                     floor-to-ceiling height in layout.json
        manual                     model_m holds a value measured in the viewer (or anywhere else)
  tape_m   one reading, or several separated by ';' (their mean is used, their spread is reported)

  python src/arcore3dgs/tape_check.py --tape <dataset>/tape.csv --layout <gs dir>/layout/layout.json [--out tape.json]

Prints a table (model, tape, error cm and %), the mean / max absolute error, and whether NFR6 (<= 5%) holds.
"""
import argparse
import csv
import json
import sys

import numpy as np


def layout_values(layout):
    """room_length / room_width / height from a layout.json dict (missing ones are left out)."""
    v = {}
    d = sorted(x["distance"] for x in layout.get("dimensions", []) if x.get("distance"))
    if d:
        v["room_length"] = d[-1]
        if len(d) > 1:
            v["room_width"] = d[0]
    h = layout.get("height")
    if h is not None and np.isfinite(h):
        v["height"] = float(h)
    return v


def readings(text):
    vals = [float(x) for x in str(text).replace(",", ";").split(";") if x.strip()]
    if not vals:
        raise ValueError("no tape reading")
    return vals


def compare(rows, layout=None):
    """rows: dicts with item, kind, tape_m, model_m -> list of result dicts (rows without a model value are skipped
    with a reason)."""
    lv = layout_values(layout) if layout else {}
    out = []
    for r in rows:
        kind = (r.get("kind") or "manual").strip()
        tape = readings(r["tape_m"])
        model = lv.get(kind) if kind != "manual" else (float(r["model_m"]) if str(r.get("model_m", "")).strip() else None)
        res = dict(item=r["item"], kind=kind, tape=float(np.mean(tape)), tape_spread=float(np.ptp(tape)),
                   n_readings=len(tape), model=model, note=r.get("note", ""))
        if model is None:
            res["skipped"] = "no model value (no layout.json value of this kind / empty model_m)"
        else:
            res["error_m"] = model - res["tape"]
            res["error_pct"] = 100 * res["error_m"] / res["tape"]
        out.append(res)
    return out


def summary(results, limit_pct=5.0):
    e = [r for r in results if "error_m" in r]
    if not e:
        return dict(n=0)
    a = np.array([abs(r["error_pct"]) for r in e]); c = np.array([abs(r["error_m"]) * 100 for r in e])
    return dict(n=len(e), mean_abs_pct=float(a.mean()), max_abs_pct=float(a.max()), mean_abs_cm=float(c.mean()),
                max_abs_cm=float(c.max()), nfr6_met=bool(a.max() <= limit_pct))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tape", required=True); ap.add_argument("--layout", default="")
    ap.add_argument("--out", default=""); ap.add_argument("--limit_pct", type=float, default=5.0)
    args = ap.parse_args(argv)
    rows = list(csv.DictReader(open(args.tape, encoding="utf-8")))
    layout = json.load(open(args.layout)) if args.layout else None
    res = compare(rows, layout); s = summary(res, args.limit_pct)
    print(f"{'item':28s} {'kind':12s} {'model m':>8s} {'tape m':>8s} {'error cm':>9s} {'error %':>8s}")
    for r in res:
        if "error_m" in r:
            print(f"{r['item'][:28]:28s} {r['kind']:12s} {r['model']:8.3f} {r['tape']:8.3f} {100 * r['error_m']:9.1f} "
                  f"{r['error_pct']:8.2f}" + (f"  (n={r['n_readings']}, spread {100 * r['tape_spread']:.1f} cm)"
                                              if r["n_readings"] > 1 else ""))
        else:
            print(f"{r['item'][:28]:28s} {r['kind']:12s} skipped: {r['skipped']}")
    if s["n"]:
        print(f"\n{s['n']} items: mean |error| {s['mean_abs_cm']:.1f} cm / {s['mean_abs_pct']:.2f}%, max "
              f"{s['max_abs_cm']:.1f} cm / {s['max_abs_pct']:.2f}% -> NFR6 (<= {args.limit_pct:g}%) "
              f"{'met' if s['nfr6_met'] else 'NOT met'}")
    if args.out:
        json.dump(dict(results=res, summary=s), open(args.out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
