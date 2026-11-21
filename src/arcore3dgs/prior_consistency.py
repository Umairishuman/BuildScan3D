"""Drop the depth-prior pixels that other views contradict (FEATURELESS_TRACKING_PLAN §11.c, second form).

The per-frame Metric3D priors (mono_prior.py) disagree between frames (R-093: 15.1 % with R-080's poses; R-095:
6.8 % with R-094's). R-095 forced every frame onto the room planes and lost 1 dB, because the plane set still held
ghost copies of walls. Here nothing is imposed: each frame keeps its own depth, but a prior pixel is switched off
(valid = False) when other views see free space in front of where it puts the surface:

  partners of frame i: its --nb time neighbours on each side + up to --loop loop partners (loop_path.py's
  loop_pairs.json: views of the same place at another time);
  per pixel of i (prior resolution), moved into each partner j with i's depth: agree if |z - D_j| < --tol * D_j,
  contradict if z < (1 - --tol) * D_j (i's surface lies in free space of j); behind j's surface = occluded, no vote;
  the pixel is dropped when it has >= 1 contradiction and at least as many contradictions as agreements.
Writes the priors in place (<work>/mono_prior/<name>.npz, run it on a copy) and mono_prior/consistency.json; prints
the share of valid prior pixels dropped and the neighbour disagreement (vggt_chunk.depth_consistency) before / after.

  python src/arcore3dgs/prior_consistency.py --work <sfm dir> [--pairs <loop_pairs.json>] [--tol 0.1]
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
G = np.diag([1.0, -1.0, -1.0, 1.0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True); ap.add_argument("--pairs", default=None)
    ap.add_argument("--nb", type=int, default=3); ap.add_argument("--loop", type=int, default=6)
    ap.add_argument("--tol", type=float, default=0.1)
    ap.add_argument("--dry", action="store_true", help="report only, write nothing")
    a = ap.parse_args()
    meta = json.load(open(os.path.join(a.work, "frames.json"))); fr = sorted(meta["frames"], key=lambda f: f["pts"])
    names = [f["name"] for f in fr]; k_of = {n: k for k, n in enumerate(names)}
    mp = os.path.join(a.work, "mono_prior")
    D, V, N = [], [], []
    for n in names:
        z = np.load(os.path.join(mp, n + ".npz"))
        D.append(z["depth"].astype(np.float32)); V.append(z["valid"].copy()); N.append(z["normal"])
    h, w = D[0].shape; s = meta["W"] / w
    K = np.array([[meta["fx"] / s, 0, meta["cx"] / s], [0, meta["fy"] / s, meta["cy"] / s], [0, 0, 1.0]])
    C2W = [np.array(f["c2w"]) @ G for f in fr]
    partners = {k: [j for j in range(k - a.nb, k + a.nb + 1) if j != k and 0 <= j < len(names)] for k in range(len(names))}
    n_loop = 0
    if a.pairs:
        lp = {}
        for x, y in json.load(open(a.pairs)):
            if x in k_of and y in k_of:
                lp.setdefault(k_of[x], []).append(k_of[y]); lp.setdefault(k_of[y], []).append(k_of[x])
        for k, js in lp.items():
            add = [j for j in js if j not in partners[k]][:a.loop]; partners[k] += add; n_loop += len(add)
    print(f"{len(names)} frames; partners: {a.nb} time neighbours each side + {n_loop} loop links", flush=True)

    v, u = np.mgrid[0:h, 0:w]
    ray = np.stack([(u + 0.5 - K[0, 2]) / K[0, 0], (v + 0.5 - K[1, 2]) / K[1, 1], np.ones((h, w))], -1)
    newV, stats = [], {}
    for i in range(len(names)):
        m = V[i] & (D[i] > 0)
        if not m.any():
            newV.append(V[i]); continue
        Pc = ray[m] * D[i][m][:, None]
        Pw = Pc @ C2W[i][:3, :3].T + C2W[i][:3, 3]
        agree = np.zeros(len(Pw), int); contra = np.zeros(len(Pw), int)
        for j in partners[i]:
            Pj = (Pw - C2W[j][:3, 3]) @ C2W[j][:3, :3]
            ok = Pj[:, 2] > 1e-3
            uj = np.full(len(Pw), -1.0); vj = np.full(len(Pw), -1.0)
            uj[ok] = K[0, 0] * Pj[ok, 0] / Pj[ok, 2] + K[0, 2]; vj[ok] = K[1, 1] * Pj[ok, 1] / Pj[ok, 2] + K[1, 2]
            inb = ok & (uj >= 0) & (uj < w) & (vj >= 0) & (vj < h)
            zj = np.zeros(len(Pw)); vj_ok = np.zeros(len(Pw), bool)
            zj[inb] = D[j][vj[inb].astype(int), uj[inb].astype(int)]
            vj_ok[inb] = V[j][vj[inb].astype(int), uj[inb].astype(int)]      # only trusted prior pixels of j vote
            g = inb & (zj > 0) & vj_ok
            zp = Pj[:, 2]
            agree += g & (np.abs(zp - zj) < a.tol * zj)
            contra += g & (zp < (1 - a.tol) * zj)
        drop = (contra >= 1) & (contra >= agree)
        Vn = V[i].copy(); idx = np.flatnonzero(m.ravel())[drop]; Vn.ravel()[idx] = False
        newV.append(Vn)
        stats[names[i]] = dict(valid=int(m.sum()), dropped=int(drop.sum()), agree_any=float(np.mean(agree > 0)))
        if i % 100 == 0:
            print(f"{i}/{len(names)} {names[i]}: dropped {100 * drop.mean():.1f} % of {int(m.sum())} prior pixels", flush=True)
    from vggt_chunk import depth_consistency
    pairs = [(i, i + k) for k in (1, 2) for i in range(0, len(names) - k)]
    lpairs = [(i, j) for i in partners for j in partners[i] if abs(j - i) > a.nb]
    for tag, VV in (("before", V), ("after", newV)):
        e = depth_consistency(D, [K] * len(D), C2W, pairs, valid=VV)
        el = depth_consistency(D, [K] * len(D), C2W, lpairs, valid=VV) if lpairs else []
        print(f"depth disagreement {tag}: neighbours median {100 * np.median(e):.1f} % ({len(e)} pairs); loop partners "
              f"median {100 * np.median(el) if el else float('nan'):.1f} % ({len(el)} pairs)", flush=True)
    tot = sum(s_["valid"] for s_ in stats.values()); dr = sum(s_["dropped"] for s_ in stats.values())
    print(f"dropped {dr} of {tot} valid prior pixels ({100 * dr / max(tot, 1):.1f} %)", flush=True)
    if a.dry:
        return
    for n, Vn, Nn, Dn in zip(names, newV, N, D):
        np.savez_compressed(os.path.join(mp, n + ".npz"), depth=Dn.astype(np.float16), normal=Nn, valid=Vn)
    json.dump(dict(params=vars(a), dropped=dr, valid=tot, frames=stats), open(os.path.join(mp, "consistency.json"), "w"))


if __name__ == "__main__":
    main()
