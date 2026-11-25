"""More training frames where the recording is weak (2026-11-25): add video frames between placed keyframes.

Keyframe selection keeps 1 video frame in --window (6) and drops the rest. In weak stretches (fast pans, blur, little
texture; analyze_recording.py labels "weak" / "featureless") the dropped frames see slightly different parts of the
surfaces, so they carry coverage the keyframes miss. Between two placed keyframes at most --max_gap s apart, inside
such a window, --extra video frames are added at even video-index spacing:
  rotation: integrated gyro from the placed neighbours (gyro_check.fill_rotations, calibrated on the model);
  position: linear interpolation between the two neighbours (the phone moves ~cm in 0.1 - 0.2 s; --pose_opt in
            training refines it).
At most --max_new frames in total (RAM: every training image is cached, ~5.8 MB each at 1839 x 1048). The frames
are written into <work>/images and <work>/frames.json (the selection the export stage reads) and into the camera
model (no 2D-3D observations). Writes <model_out>/densify.json.

  python src/arcore3dgs/densify_frames.py <dataset> <work dir (copy of the selection)> <model_in> <analysis.json>
      <model_out> [--extra 1] [--max_gap 0.5] [--max_new 300] [--labels weak featureless]
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from arcore_fill import write_with_new  # noqa: E402
from common import Capture  # noqa: E402
from gyro_check import check, fill_rotations  # noqa: E402
from scale_drift import read_model  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset"); ap.add_argument("work"); ap.add_argument("model_in"); ap.add_argument("analysis")
    ap.add_argument("model_out")
    ap.add_argument("--extra", type=int, default=1); ap.add_argument("--max_gap", type=float, default=0.5)
    ap.add_argument("--max_new", type=int, default=300)
    ap.add_argument("--labels", nargs="+", default=["weak", "featureless"])
    a = ap.parse_args()

    fj = os.path.join(a.work, "frames.json"); meta = json.load(open(fj)); sel = meta["frames"]
    pts_of = {f["name"]: f["pts"] for f in sel}; t0 = min(pts_of.values()); off = meta.get("pose_offset", 0.0)
    by = {f["name"]: f for f in sel}
    K, dist, fx, fy, imgs = read_model(a.model_in, pts_of)
    an = json.load(open(a.analysis))
    wins = [(w["t0"], w["t1"]) for w in an["windows"] if w["label"] in a.labels]
    cap_info = Capture(a.dataset)
    vid_pts = np.asarray(cap_info.pts)

    # candidate video frames between consecutive placed keyframes inside weak windows
    plan = []
    for d1, d2 in zip(imgs[:-1], imgs[1:]):
        f1, f2 = by[d1["key"]], by[d2["key"]]
        ta, tb = f1["pts"] - t0, f2["pts"] - t0
        if tb - ta > a.max_gap or not any(w0 <= (ta + tb) / 2 < w1 for w0, w1 in wins):
            continue
        i1, i2 = f1["video_index"], f2["video_index"]
        for j in range(1, a.extra + 1):
            vi = int(round(i1 + (i2 - i1) * j / (a.extra + 1)))
            if vi in (i1, i2) or f"frame_{vi:05d}" in pts_of:
                continue
            w = (vid_pts[vi] - f1["pts"]) / max(f2["pts"] - f1["pts"], 1e-6)
            plan.append(dict(vi=vi, name=f"frame_{vi:05d}", pts=float(vid_pts[vi]), C=(1 - w) * d1["C"] + w * d2["C"],
                             between=[d1["key"], d2["key"]]))
    if len(plan) > a.max_new:                                         # spread the cap evenly over the walk
        keep = np.linspace(0, len(plan) - 1, a.max_new).round().astype(int)
        plan = [plan[k] for k in sorted(set(keep))]
    print(f"{len(wins)} windows labelled {a.labels}; {len(plan)} frames to add", flush=True)
    if not plan:
        write_with_new(a.model_in, a.model_out, []); return

    # rotations from the gyro
    rep = check(a.dataset, sel, {d["key"]: d["Rcw"].T for d in imgs}, cap_info.t0_ns, off, verbose=True)
    tk = np.array([pts_of[d["key"]] + off for d in imgs])
    Rq = fill_rotations(rep["imu"], rep["Rci"], rep["off"], tk, [d["Rcw"].T for d in imgs], np.array([p["pts"] + off for p in plan]))

    # images from the video (sequential read; seeking is not frame-exact for every codec)
    want = {p["vi"]: p for p in plan}; got = 0
    cap = cv2.VideoCapture(cap_info.video); k = 0; last = max(want)
    while k <= last:
        ok, fr = cap.read()
        if not ok:
            break
        if k in want:
            g = cv2.cvtColor(cv2.resize(fr, (960, 540), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
            want[k]["sharpness"] = float(cv2.Laplacian(g, cv2.CV_64F).var())
            cv2.imwrite(os.path.join(a.work, "images", want[k]["name"] + ".jpg"), fr, [cv2.IMWRITE_JPEG_QUALITY, 95])
            got += 1
        k += 1
    cap.release()
    plan = [p for p in plan if "sharpness" in p]
    print(f"extracted {got} video frames", flush=True)

    new = []
    for p, Rwc in zip(plan, Rq):
        new.append(dict(key=p["name"], Rcw=Rwc.T, C=p["C"]))
        sel.append(dict(name=p["name"], video_index=p["vi"], pts=p["pts"], sharpness=p["sharpness"],
                        pred_blur_px=None, fallback=False, c2w=None, c2w_arcore=None, arcore_pose="densified",
                        densified_between=p["between"]))
    sel.sort(key=lambda f: f["pts"])
    json.dump(meta, open(fj, "w"))
    n_in = write_with_new(a.model_in, a.model_out, new)
    json.dump(dict(params=vars(a), gyro_pair_err_deg_median=rep["pair_err_deg_median"], added=[p["name"] for p in plan]),
              open(os.path.join(a.model_out, "densify.json"), "w"), indent=1)
    print(f"wrote {a.model_out}: {n_in} + {len(new)} images; {fj}: {len(sel)} frames", flush=True)


if __name__ == "__main__":
    main()
