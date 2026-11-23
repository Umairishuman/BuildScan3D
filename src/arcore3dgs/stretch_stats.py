"""Per model: 3D observations per camera and path smoothness, overall and in given time stretches; position change
against a reference model (Sim3 aligned). Used for the featureless runs R-076 - R-091 (moved here from a scratchpad
2026-11-21).

  python src/arcore3dgs/stretch_stats.py <keyframe dir with frames.json> <reference model> <model> [<model> ...]
"""
import sys, json, numpy as np
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from known_rot_pnp import load_model

pts = {f["name"]: f["pts"] for f in json.load(open(sys.argv[1] + "/frames.json"))["frames"]}
STR = [(0, 1e9, "all"), (45, 60, "45-60 s"), (90, 105, "90-105 s")]


def umeyama(src, dst):
    ms, md = src.mean(0), dst.mean(0); S, D = src - ms, dst - md
    U, s, Vt = np.linalg.svd(D.T @ S / len(src)); E = np.eye(3)
    if np.linalg.det(U @ Vt) < 0: E[2, 2] = -1
    Rm = U @ E @ Vt; sc = np.trace(np.diag(s) @ E) / S.var(0).sum(); return sc, Rm, md - sc * Rm @ ms


def n3d(model):
    out = {}; L = [l for l in open(model + "/images.txt") if l[0] != "#"]
    for i in range(0, len(L), 2):
        n = L[i].split()[9].rsplit(".", 1)[0]; a = L[i + 1].split()
        out[n] = sum(1 for j in range(2, len(a), 3) if a[j] != "-1")
    return out


Aref, _, _ = load_model(sys.argv[2])
for p in sys.argv[2:]:
    B, _, _ = load_model(p); cnt = n3d(p)
    names = sorted(B, key=lambda n: pts[n]); t = np.array([pts[n] for n in names])
    C = np.array([B[n][1] for n in names])
    step = np.linalg.norm(np.diff(C, axis=0), axis=1) / np.maximum(np.diff(t), 1e-3)     # units / s
    sh = [n for n in names if n in Aref]
    sc, Rm, tr = umeyama(np.array([B[n][1] for n in sh]), np.array([Aref[n][1] for n in sh]))
    moved = {n: np.linalg.norm(sc * Rm @ B[n][1] + tr - Aref[n][1]) for n in sh}
    txt = []
    for lo, hi, lab in STR:
        m = (t >= lo) & (t < hi); ms = m[1:] & m[:-1]
        c = np.array([cnt[n] for n in np.array(names)[m]])
        sp = step[ms]
        mv = np.array([moved[n] for n in np.array(names)[m] if n in moved])
        txt.append(f"{lab}: {m.sum()} cams, 3D obs median {np.median(c):.0f}, <10: {(c < 10).sum()}, speed p90/p50 "
                   f"{np.percentile(sp, 90) / max(np.median(sp), 1e-9):.1f}, max/p50 {sp.max() / max(np.median(sp), 1e-9):.1f}, "
                   f"moved vs ref median {np.median(mv):.3f}")
    print(p.split("/")[-1] or p, "| " + " | ".join(txt))
