"""More loop pairs, chosen with the loop-closed cameras (FEATURELESS_TRACKING_PLAN §11.d, second round).

loop_path.py (R-096) closed the loops with the verified image pairs that already were in the COLMAP database: the
pairs the first matching round chose by retrieval. With the cameras roughly right, the pairs that look at the same
surfaces at different times can be chosen geometrically and matched on purpose:

  1. per keyframe, its depth prior (<sfm>/mono_prior, scaled to the model) sampled on a coarse grid and lifted to the
     world: the set of --voxel sized cells it sees;
  2. candidate pairs: >= --min_dt s apart, overlap |A & B| / min(|A|, |B|) >= --min_overlap, viewing directions
     within --max_angle, not matched before; the --per_frame best per keyframe, at most --max_pairs;
  3. matched with COLMAP matches_importer (ALIKED + LightGlue, as the database) in a COPY of the database;
  4. for every verified pair >= --min_dt s apart (old and new), the direction of C_a - C_b from the matches with the
     model's rotations fixed (rot_sfm.pair_direction), in the model's world.
Writes <out>/database.db, pairs_new.txt, and pair_directions.json in rot_sfm's cache format (name_a, name_b,
direction, weight) but in the model's world: use loop_path.py --model_frame.

  python src/arcore3dgs/loop_match.py <model> <sfm dir with frames.json, mono_prior> <database.db> <out>
"""
import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import toolpaths  # noqa: E402
from known_rot_pnp import bearings  # noqa: E402
from rot_sfm import PAIR, pair_direction  # noqa: E402
from scale_drift import read_model  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("sfm"); ap.add_argument("database"); ap.add_argument("out")
    ap.add_argument("--min_dt", type=float, default=5.0); ap.add_argument("--voxel", type=float, default=0.3)
    ap.add_argument("--min_overlap", type=float, default=0.3); ap.add_argument("--max_angle", type=float, default=60.0)
    ap.add_argument("--per_frame", type=int, default=8); ap.add_argument("--max_pairs", type=int, default=4000)
    ap.add_argument("--min_inliers", type=int, default=15); ap.add_argument("--min_parallax", type=float, default=1.0)
    ap.add_argument("--thr", type=float, default=0.004)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t_start = time.time()
    meta = json.load(open(os.path.join(a.sfm, "frames.json"))); pts_of = {f["name"]: f["pts"] for f in meta["frames"]}
    K, dist, fx, fy, imgs = read_model(a.model, pts_of)
    by = {d["key"]: d for d in imgs}
    cam_line = [ln.split() for ln in open(os.path.join(a.model, "cameras.txt")) if ln[0] != "#" and ln.strip()][0]
    cam = (cam_line[1], list(map(float, cam_line[4:])))

    # ---- 1. cells seen per keyframe ----
    cells, fwd = {}, {}
    for d in imgs:
        p = os.path.join(a.sfm, "mono_prior", d["key"] + ".npz")
        if not os.path.exists(p):
            continue
        D = np.load(p)["depth"].astype(np.float32); h, w = D.shape; s = meta["W"] / w
        v, u = np.mgrid[h // 24:h:h // 12, w // 32:w:w // 16]; z = D[v, u]; ok = z > 0
        X = np.stack([(u[ok] * s + s / 2 - meta["cx"]) / meta["fx"] * z[ok], (v[ok] * s + s / 2 - meta["cy"]) / meta["fy"] * z[ok],
                      z[ok]], 1) @ d["Rcw"] + d["C"]                      # Rcw.T applied on the right = Rwc
        cells[d["key"]] = set(map(tuple, np.floor(X / a.voxel).astype(int)))
        fwd[d["key"]] = d["Rcw"][2]
    keys = sorted(cells, key=lambda k: pts_of[k])
    print(f"{len(keys)} keyframes with a depth prior ({time.time() - t_start:.0f}s)", flush=True)

    con = sqlite3.connect(a.database)
    ids = {n[:-4]: i for i, n in con.execute("select image_id, name from images")}
    done = set()
    for (pid,) in con.execute("select pair_id from matches"):
        i2 = pid % PAIR; i1 = (pid - i2) // PAIR; done.add((min(i1, i2), max(i1, i2)))
    con.close()

    # ---- 2. candidates ----
    cand = {}
    cosA = np.cos(np.radians(a.max_angle))
    for i, ka in enumerate(keys):
        for kb in keys[i + 1:]:
            if pts_of[kb] - pts_of[ka] < a.min_dt or ka not in ids or kb not in ids:
                continue
            if (min(ids[ka], ids[kb]), max(ids[ka], ids[kb])) in done or fwd[ka] @ fwd[kb] < cosA:
                continue
            A, B = cells[ka], cells[kb]
            ov = len(A & B) / max(1, min(len(A), len(B)))
            if ov >= a.min_overlap:
                cand[(ka, kb)] = ov
    cnt = {}; sel = []                                              # best overlap first, per-frame and total caps
    for (ka, kb), ov in sorted(cand.items(), key=lambda x: -x[1]):
        if len(sel) >= a.max_pairs:
            break
        if cnt.get(ka, 0) < a.per_frame and cnt.get(kb, 0) < a.per_frame:
            cnt[ka] = cnt.get(ka, 0) + 1; cnt[kb] = cnt.get(kb, 0) + 1; sel.append((ka, kb))
    dts = np.array([pts_of[kb] - pts_of[ka] for ka, kb in sel])
    print(f"{len(cand)} candidate pairs not matched before; {len(sel)} chosen (dt 5-20 s {int(((dts < 20)).sum())}, "
          f"20-60 s {int(((dts >= 20) & (dts < 60)).sum())}, >= 60 s {int((dts >= 60).sum())}) ({time.time() - t_start:.0f}s)",
          flush=True)
    with open(os.path.join(a.out, "pairs_new.txt"), "w") as f:
        for ka, kb in sel:
            f.write(f"{ka}.jpg {kb}.jpg\n")

    # ---- 3. match them in a copy of the database ----
    db = os.path.join(a.out, "database.db")
    if not os.path.exists(db):
        shutil.copy(a.database, db)
    dll = [os.path.abspath(os.path.join(HERE, "..", "..", "tools", "cudnn9"))]
    import importlib.util
    ts = importlib.util.find_spec("torch")
    if ts and ts.origin:
        dll.append(os.path.join(os.path.dirname(ts.origin), "lib"))
    env = dict(os.environ, PATH=os.pathsep.join([d for d in dll if os.path.isdir(d)] + [os.environ.get("PATH", "")]))
    subprocess.run([toolpaths.colmap(), "matches_importer", "--database_path", db, "--match_list_path",
                    os.path.join(a.out, "pairs_new.txt"), "--match_type", "pairs", "--FeatureMatching.use_gpu", "1",
                    "--FeatureMatching.type", "ALIKED_LIGHTGLUE"], check=True, env=env,
                   stdout=open(os.path.join(a.out, "matches_importer.log"), "w"), stderr=subprocess.STDOUT)
    print(f"matched ({time.time() - t_start:.0f}s)", flush=True)

    # ---- 4. directions in the model's world ----
    con = sqlite3.connect(db)
    names_db = {i: n[:-4] for i, n in con.execute("select image_id, name from images")}
    kps = {i: np.frombuffer(d_, np.float32).reshape(r, c)[:, :2] for i, r, c, d_ in
           con.execute("select image_id, rows, cols, data from keypoints") if d_ is not None and r > 0}
    newset = {(x, y) for x, y in sel} | {(y, x) for x, y in sel}
    rng = np.random.default_rng(0); out = []; n_new = n_new_ok = 0
    for pid, r, d_ in con.execute("select pair_id, rows, data from two_view_geometries where rows > 0"):
        i2 = pid % PAIR; i1 = (pid - i2) // PAIR
        na, nb = names_db.get(i1), names_db.get(i2)
        if na not in by or nb not in by or abs(pts_of[na] - pts_of[nb]) < a.min_dt:
            continue
        is_new = (na, nb) in newset; n_new += is_new
        if r < a.min_inliers or i1 not in kps or i2 not in kps:
            continue
        m = np.frombuffer(d_, np.uint32).reshape(r, 2)
        b1 = bearings(kps[i1][m[:, 0]], cam); b2 = bearings(kps[i2][m[:, 1]], cam)
        Ra, Rb = by[na]["Rcw"].T, by[nb]["Rcw"].T                      # camera (OpenCV) -> world
        t, inl, par = pair_direction(Rb.T @ Ra, b1, b2, a.thr, rng=rng)
        if t is None or inl.sum() < a.min_inliers or par < a.min_parallax:
            continue
        n_new_ok += is_new
        out.append((na, nb, (Rb @ t).tolist(), float(inl.sum()) * min(par, 10.0) / 10.0))
    con.close()
    json.dump(out, open(os.path.join(a.out, "pair_directions.json"), "w"))
    dt = np.array([abs(pts_of[x] - pts_of[y]) for x, y, _, _ in out])
    print(f"new pairs verified by COLMAP: {n_new}, with a direction: {n_new_ok}; directions >= {a.min_dt} s in total: "
          f"{len(out)} (5-20 s {int((dt < 20).sum())}, 20-60 s {int(((dt >= 20) & (dt < 60)).sum())}, >= 60 s "
          f"{int((dt >= 60).sum())}) ({time.time() - t_start:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
