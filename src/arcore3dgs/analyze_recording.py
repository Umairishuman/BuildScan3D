"""Analyzer, first part (PIPELINE_ANALYZER_PLAN §2.1, D-095): label a recording's time windows from the outputs the
pipeline already has, and say which camera route the numbers point to. CPU only, a few seconds, no new heavy pass.

Inputs:
  --selection <work dir>   frames.json of the selected keyframes (select_sharp.py: pts, sharpness, pred_blur_px,
                           arcore_pose); the frames the camera stage was asked to place
  --model <sfm dir>        the camera stage's output: frames.json (placed frames, c2w), sparse.npz (3D observations
                           per camera: cam, pt), report.json (registered / total, Sim3 to ARCore)
Per --win seconds window: selected and placed keyframes, the placed share, 3D observations per placed camera (median),
predicted motion blur (px, median), Laplacian sharpness (median), share of frames ARCore tracked. Holes: gaps in the
placed path of >= --hole_dt s, or one step >= --hole_step times the median step (loop_path.py --hole_dt uses the same
rule, R-123). Labels, first thresholds (set by hand, NOT yet tuned on the test bench, PIPELINE_ANALYZER_PLAN §3):
  hole         placed share < --min_placed, or the window lies inside a hole
  featureless  placed, but 3D observations per camera < --obs_low
  weak         observations < --obs_ok, or blur > --blur_high px
  textured     otherwise
Route (printed, written to the json): "normal SfM" when the model placed >= --route_placed of the selection and the
holes cover < --route_hole of the recording; otherwise "sensor path". A suggestion with its numbers, not a decision.

  python src/arcore3dgs/analyze_recording.py --selection <work dir> --model <sfm dir> [--out analysis.json] [--win 5]
"""
import argparse
import json
import os

import numpy as np


def arcore_tracked(f):
    """select_sharp.py: a frame with an ARCore pose has c2w_arcore; without one, arcore_pose is "lost" / "unsettled"."""
    return isinstance(f.get("c2w_arcore"), list) and f.get("arcore_pose") not in ("lost", "unsettled")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selection", required=True); ap.add_argument("--model", required=True)
    ap.add_argument("--out", default=None); ap.add_argument("--win", type=float, default=5.0)
    ap.add_argument("--hole_dt", type=float, default=2.5); ap.add_argument("--hole_step", type=float, default=15.0)
    ap.add_argument("--min_placed", type=float, default=0.3)
    ap.add_argument("--obs_low", type=float, default=30); ap.add_argument("--obs_ok", type=float, default=100)
    ap.add_argument("--blur_high", type=float, default=15.0)
    ap.add_argument("--route_placed", type=float, default=0.95); ap.add_argument("--route_hole", type=float, default=0.05)
    a = ap.parse_args()

    sel = json.load(open(os.path.join(a.selection, "frames.json")))["frames"]
    mod = json.load(open(os.path.join(a.model, "frames.json")))
    placed = mod["frames"]
    rep = json.load(open(os.path.join(a.model, "report.json"))) if os.path.exists(os.path.join(a.model, "report.json")) else {}
    t0 = min(f["pts"] for f in sel); dur = max(f["pts"] for f in sel) - t0
    obs = np.zeros(len(placed))
    sp = os.path.join(a.model, "sparse.npz")
    if os.path.exists(sp):
        cam = np.load(sp)["cam"]; c = np.bincount(cam, minlength=len(placed)); obs = c[:len(placed)].astype(float)
    pl_name = {f["name"]: k for k, f in enumerate(placed)}
    order = sorted(range(len(placed)), key=lambda k: placed[k]["pts"])
    Tp = np.array([placed[k]["pts"] - t0 for k in order]); Cp = np.array([np.array(placed[k]["c2w"])[:3, 3] for k in order])

    holes = []
    if len(Tp) > 1:
        st = np.linalg.norm(np.diff(Cp, axis=0), axis=1); med = np.median(st)
        for k in np.flatnonzero((np.diff(Tp) >= a.hole_dt) | (st >= a.hole_step * med)):
            holes.append(dict(start=float(Tp[k]), end=float(Tp[k + 1]), dt=float(Tp[k + 1] - Tp[k]), step=float(st[k]),
                              step_x_median=float(st[k] / med)))
    # also the stretches before the first / after the last placed frame
    if len(Tp) and Tp[0] >= a.hole_dt:
        holes.insert(0, dict(start=0.0, end=float(Tp[0]), dt=float(Tp[0]), step=None, step_x_median=None))
    if len(Tp) and dur - Tp[-1] >= a.hole_dt:
        holes.append(dict(start=float(Tp[-1]), end=float(dur), dt=float(dur - Tp[-1]), step=None, step_x_median=None))
    hole_time = sum(h["dt"] for h in holes if h["dt"] >= a.hole_dt)

    wins = []
    for w0 in np.arange(0, dur + 1e-6, a.win):
        w1 = w0 + a.win
        s = [f for f in sel if w0 <= f["pts"] - t0 < w1]
        if not s:
            continue
        p = [f for f in s if f["name"] in pl_name]
        o = [obs[pl_name[f["name"]]] for f in p]
        share = len(p) / len(s)
        mid = (w0 + w1) / 2
        in_hole = any(h["dt"] >= a.hole_dt and h["start"] < mid < h["end"] for h in holes)
        om = float(np.median(o)) if o else 0.0
        blur = float(np.median([f.get("pred_blur_px", 0) or 0 for f in s]))
        if share < a.min_placed or in_hole:
            lab = "hole"
        elif om < a.obs_low:
            lab = "featureless"
        elif om < a.obs_ok or blur > a.blur_high:
            lab = "weak"
        else:
            lab = "textured"
        wins.append(dict(t0=float(w0), t1=float(w1), selected=len(s), placed=len(p), placed_share=share, obs_median=om,
                         blur_px=blur, sharpness=float(np.median([f.get("sharpness", 0) or 0 for f in s])),
                         arcore_tracked=float(np.mean([arcore_tracked(f) for f in s])), label=lab))

    n_sel = len(sel); n_pl = sum(1 for f in sel if f["name"] in pl_name)
    labels = {k: sum(1 for w in wins if w["label"] == k) for k in ("textured", "weak", "featureless", "hole")}
    route = "normal SfM" if (n_pl / max(n_sel, 1) >= a.route_placed and hole_time / max(dur, 1e-6) < a.route_hole) else "sensor path"
    out = dict(selection=a.selection, model=a.model, duration_s=float(dur), selected=n_sel, placed=n_pl,
               placed_share=n_pl / max(n_sel, 1), obs_median=float(np.median(obs)) if len(obs) else 0.0,
               arcore_tracked=float(np.mean([arcore_tracked(f) for f in sel])),
               sim3_inliers=rep.get("align_inliers"), sim3_median_cm=rep.get("align_median_cm"),
               holes=holes, hole_time_s=float(hole_time), labels=labels, route=route, params=vars(a), windows=wins)
    print(f"{a.model}: {dur:.0f} s, {n_pl}/{n_sel} keyframes placed ({100 * n_pl / max(n_sel, 1):.0f} %), 3D obs per camera "
          f"median {out['obs_median']:.0f}, ARCore tracked {100 * out['arcore_tracked']:.0f} %, Sim3 inliers "
          f"{rep.get('align_inliers')}")
    print(f"  holes >= {a.hole_dt:g} s: {sum(1 for h in holes if h['dt'] >= a.hole_dt)} ({hole_time:.0f} s, "
          f"{100 * hole_time / max(dur, 1e-6):.0f} % of the recording); windows: " + ", ".join(f"{k} {v}" for k, v in labels.items()))
    print("  " + "".join({"textured": "T", "weak": "w", "featureless": "f", "hole": "_"}[w["label"]] for w in wins)
          + f"   ({a.win:g} s per letter: T textured, w weak, f featureless, _ hole)")
    print(f"  route: {route}")
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
