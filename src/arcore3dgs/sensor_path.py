"""Sensor-path camera chain as one stage (D-099; PIPELINE_ANALYZER_PLAN §2.2): for recordings normal SfM cannot place.

The chain that made scan_009's cameras was assembled by hand over ~20 runs (R-071 -> R-080 -> R-094 -> R-096, each
from its own shell script). Here it runs in one go, with the settings those runs used, on any recording:

  1 gyro_loop_bias.py   gyro bias from verified image pairs far apart in time (R-071)
  2 rot_sfm.py          rotations from the gyro, positions from pair directions + accelerometer, all pairs <= 300 s
                        apart (--max_dt 300 --bg_json --triangulate_only, R-071); writes the pair-direction cache
  3 prior_ba.py         BA with soft priors on consecutive motion, adaptive (--adapt_n 150 --loose_t0 2 --loose_t1 30
                        --iters 150, R-078 / R-080)
  4 video_tracks.py     video point tracks between keyframes as extra observations, then prior_ba.py again (R-080)
  5 mid export          undistort / export (--sim3 none) + depth priors + plane regions of this model: the inputs of
                        scale_drift.py
  6 scale_drift.py      scale drift corrected with the room height, then prior_ba.py again (R-094)
  7 loop_path.py        loops closed with the image pairs that see the same place at different times, then
                        prior_ba.py --pair_priors (R-096)
Output: <out>/model (COLMAP text model, metric, +Y up: use sfm_colmap.py --sim3 none) and <out>/sensor_path.json
(steps, times, the checks each script prints are in <out>/*.log). Not included (scan_009 only, not general):
R-079's second rot_sfm with the track directions weighted up.

  python src/arcore3dgs/sensor_path.py <dataset> <selection dir (frames.json, images/)> <sfm dir (sparse/0,
      database.db from sfm_colmap.py)> <out dir> [--prior_args "--da3 <weights> --fill_scale --da3_conf_min 1.1"]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import toolpaths  # noqa: E402

PBA = ["--adapt_n", "150", "--loose_t0", "2", "--loose_t1", "30", "--iters", "150"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset"); ap.add_argument("work"); ap.add_argument("calib"); ap.add_argument("out")
    ap.add_argument("--prior_args", default="", help="mono_prior.py options for the mid export (scale_drift's depth)")
    ap.add_argument("--from_step", type=int, default=1, help="resume at this step (earlier outputs reused)")
    a = ap.parse_args()
    py, O, W, D = sys.executable, os.path.abspath(a.out), os.path.abspath(a.work), os.path.abspath(a.dataset)
    os.makedirs(O, exist_ok=True)
    colmap = toolpaths.colmap()
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    rep_file = os.path.join(O, "sensor_path.json")
    rep = json.load(open(rep_file)) if os.path.exists(rep_file) else {"steps": {}}

    def step(n, name, cmds):
        if n < a.from_step:
            return
        t0 = time.time()
        with open(os.path.join(O, f"{n}_{name}.log"), "w") as log:
            for c in cmds:
                print(f"== sensor_path {n} {name}: {' '.join(c)}", flush=True)
                log.write("== " + " ".join(c) + "\n"); log.flush()
                r = subprocess.run(c, cwd=os.path.dirname(os.path.dirname(HERE)), env=env, stdout=log, stderr=subprocess.STDOUT)
                if r.returncode:
                    sys.exit(f"sensor_path step {n} {name} failed ({r.returncode}), see {log.name}")
        rep["steps"][f"{n}_{name}"] = round((time.time() - t0) / 60, 2)
        json.dump(rep, open(rep_file, "w"), indent=1)
        print(f"   sensor_path {n} {name} {rep['steps'][f'{n}_{name}']:.1f} min", flush=True)

    p = lambda *x: os.path.join(O, *x)
    S = lambda f: os.path.join(HERE, f)
    bias = p("gyro_bias.json")
    step(1, "gyro_bias", [[py, S("gyro_loop_bias.py"), D, W, a.calib, "--out", bias]])
    step(2, "rot_sfm", [[py, S("rot_sfm.py"), D, W, a.calib, p("rot"), "--max_dt", "300", "--bg_json", bias,
                          "--triangulate_only"]])
    step(3, "prior_ba", [[py, S("prior_ba.py"), p("rot", "sparse", "0"), W, p("pba"), *PBA, "--colmap", colmap]])
    step(4, "video_tracks", [[py, S("video_tracks.py"), D, W, p("pba"), p("vt")],
                             [py, S("prior_ba.py"), p("vt"), W, p("vt_pba"), *PBA, "--colmap", colmap]])

    mid = p("mid")                                            # an sfm dir for this model: frames, priors, planes
    def mid_export():
        shutil.rmtree(os.path.join(mid, "sparse"), ignore_errors=True)
        shutil.copytree(p("vt_pba"), os.path.join(mid, "sparse", "0"))
    if 5 >= a.from_step:
        os.makedirs(mid, exist_ok=True); mid_export()
    step(5, "mid_export", [[py, S("sfm_colmap.py"), "--work", W, "--out", mid, "--stage", "undistort", "--sim3", "none"],
                           [py, S("sfm_colmap.py"), "--work", W, "--out", mid, "--stage", "export", "--sim3", "none"],
                           toolpaths.ns_cmd("python") + [S("export_nerfstudio.py"), "--work", mid, "--downscale", "1"],
                           [py, S("mono_prior.py"), "--work", mid, "--fp16"] + a.prior_args.split(),
                           [py, S("plane_seg.py"), "--work", mid]])
    step(6, "scale_drift", [[py, S("scale_drift.py"), p("vt_pba"), mid, p("scalefix")],
                            [py, S("prior_ba.py"), p("scalefix"), W, p("scalefix_pba"), *PBA, "--colmap", colmap]])
    cache = p("rot", "pair_directions_dt300_par1_bg.json")
    step(7, "loop_path", [[py, S("loop_path.py"), p("scalefix_pba"), mid, cache, p("loop")],
                          [py, S("prior_ba.py"), p("loop"), W, p("model"), "--pair_priors", p("loop", "loop_pairs.json"),
                           *PBA, "--colmap", colmap]])
    rep["total_min"] = round(sum(rep["steps"].values()), 1)
    json.dump(rep, open(rep_file, "w"), indent=1)
    print(f"sensor_path done: {p('model')}  ({rep['total_min']} min)", flush=True)


if __name__ == "__main__":
    main()
