"""Iterate video tracks <-> camera path (FEATURELESS_TRACKING_PLAN §10, step 10.c).

R-079 / R-080 did one round by hand: tracks extracted on a model give pair directions for rot_sfm.py, the new path
lets more tracks triangulate. Each round starts from the previous round's model, so the tracks are checked against
better rotations and triangulated with better positions. One round:

  1. video_tracks.py on the current model --pairs_out      -> round_k/vt_pairs.npz
  2. rot_sfm.py --extra_pairs (pair-direction cache copied)  -> round_k/sparse/0 (cameras kept: rot_sfm.json)
  3. prior_ba.py --adapt_n                                   -> round_k/sparse_pba
  4. video_tracks.py on that (adds the track points)        -> round_k/sparse_vt
  5. prior_ba.py --adapt_n                                   -> round_k/sparse_vt_pba   (next round's model)

Stops after --rounds, or earlier when the kept cameras do not rise by at least --min_gain. Prints one line per round
(cameras kept, 3D observations per camera, reprojection) and writes track_loop.json.

  python src/arcore3dgs/track_loop.py <dataset> <keyframe dir> <calib sfm dir> <start model> <out root>
      --pair_cache <rot_sfm pair-direction json> [--bg_json …] [--rounds 3] [--extra_w 30] [--extra_min_inliers 8]
      [--adapt_n 150] [--rs 0|1] [--colmap COLMAP.bat]

With --rs 1 the keyframe dir must be rs_rectify.py output and the calib dir an SfM of those rectified keyframes.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def n3d_median(model):
    L = [l for l in open(os.path.join(model, "images.txt")) if not l.startswith("#")]
    c = [sum(1 for j in range(2, len(b.split()), 3) if b.split()[j] != "-1") for b in L[1::2]]
    return float(np.median(c)), int(np.sum(np.array(c) < 10)), len(c)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset"); ap.add_argument("work"); ap.add_argument("calib"); ap.add_argument("start_model")
    ap.add_argument("out")
    ap.add_argument("--pair_cache", required=True, help="rot_sfm pair-direction cache (saves ~15 min per round)")
    ap.add_argument("--bg_json", default=None)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--min_gain", type=int, default=5, help="stop when the kept cameras rise by less than this")
    ap.add_argument("--extra_w", type=float, default=30.0); ap.add_argument("--extra_min_inliers", type=int, default=8)
    ap.add_argument("--adapt_n", type=int, default=150)
    ap.add_argument("--ba_args", default="--loose_t0 2 --loose_t1 30 --iters 150")
    ap.add_argument("--rs", type=int, default=0)
    ap.add_argument("--colmap", default=None)
    a = ap.parse_args()
    py = sys.executable
    os.makedirs(a.out, exist_ok=True)

    def run(cmd, log):
        t = time.time()
        with open(log, "w") as f:
            r = subprocess.run([str(c) for c in cmd], stdout=f, stderr=subprocess.STDOUT)
        if r.returncode:
            sys.exit(f"failed ({r.returncode}): {' '.join(map(str, cmd))}\n  see {log}")
        return time.time() - t

    def pba(m_in, m_out, log):
        cmd = [py, os.path.join(HERE, "prior_ba.py"), m_in, a.work, m_out, "--adapt_n", a.adapt_n] + a.ba_args.split()
        if a.colmap:
            cmd += ["--colmap", a.colmap]
        return run(cmd, log)

    model, rows = a.start_model, []
    m0, w0, c0 = n3d_median(model)
    print(f"start {model}: {c0} cameras, 3D obs median {m0:.0f}, {w0} with < 10", flush=True)
    prev_kept = c0
    for k in range(1, a.rounds + 1):
        V = os.path.join(a.out, f"round_{k}"); os.makedirs(V, exist_ok=True)
        rs = ["--rs", "1"] if a.rs else []
        tt = run([py, os.path.join(HERE, "video_tracks.py"), a.dataset, a.work, model, os.path.join(V, "vt_seed"),
                  "--pairs_out", os.path.join(V, "vt_pairs.npz")] + rs, os.path.join(V, "1_tracks.log"))
        shutil.copy(a.pair_cache, V)
        cmd = [py, os.path.join(HERE, "rot_sfm.py"), a.dataset, a.work, a.calib, V, "--max_dt", "300", "--triangulate_only",
               "--extra_pairs", os.path.join(V, "vt_pairs.npz"), "--extra_w", a.extra_w,
               "--extra_min_inliers", a.extra_min_inliers]
        if a.bg_json:
            cmd += ["--bg_json", a.bg_json]
        tr = run(cmd, os.path.join(V, "2_rot_sfm.log"))
        kept = json.load(open(os.path.join(V, "rot_sfm.json")))["kept"]
        tb1 = pba(os.path.join(V, "sparse", "0"), os.path.join(V, "sparse_pba"), os.path.join(V, "3_prior_ba.log"))
        tt2 = run([py, os.path.join(HERE, "video_tracks.py"), a.dataset, a.work, os.path.join(V, "sparse_pba"),
                   os.path.join(V, "sparse_vt")] + rs, os.path.join(V, "4_tracks.log"))
        tb2 = pba(os.path.join(V, "sparse_vt"), os.path.join(V, "sparse_vt_pba"), os.path.join(V, "5_prior_ba.log"))
        model = os.path.join(V, "sparse_vt_pba")
        med, weak, n = n3d_median(model)
        rep = json.load(open(os.path.join(model, "prior_ba.json")))
        row = dict(round=k, kept=kept, cameras=n, obs_median=med, under_10=weak, reproj=rep.get("reproj_median"),
                   minutes=round((tt + tr + tb1 + tt2 + tb2) / 60, 1), model=model)
        rows.append(row)
        print(f"round {k}: {kept} cameras kept by rot_sfm, 3D obs median {med:.0f}, {weak} with < 10, reprojection "
              f"{row['reproj']:.2f} px ({row['minutes']} min)", flush=True)
        json.dump(rows, open(os.path.join(a.out, "track_loop.json"), "w"), indent=1)
        if kept - prev_kept < a.min_gain:
            print(f"stop: kept cameras rose by {kept - prev_kept} (< {a.min_gain})")
            break
        prev_kept = kept
    print(f"last model: {model}")


if __name__ == "__main__":
    main()
