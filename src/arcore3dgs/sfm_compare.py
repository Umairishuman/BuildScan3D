"""Two SfM models of the same keyframes: how many frames each placed, and how far their cameras are apart.

For COMPLETION_PLAN E1 (final-1 exit gate d): visual-only SfM (sfm_colmap.py --pairs visual) against ARCore-guided SfM
(--pairs arcore) on the same selection. Reads COLMAP text or binary models (images.txt / images.bin) via pycolmap if
available, else the text files. Track completion = placed frames / keyframes (also per 15 s of the walk); the camera
difference is a Sim3 fit of the common camera centres (a disagreement, not an error against ground truth).

  python src/arcore3dgs/sfm_compare.py <work (frames.json)> <model A dir> <model B dir> [--names A B] [--out x.json]
"""
import argparse
import json
import os
import struct

import numpy as np


def read_images(d):
    """{image name: camera centre} from images.txt or images.bin of a COLMAP model."""
    out = {}
    t = os.path.join(d, "images.txt")
    if os.path.exists(t):
        lines = [x for x in open(t) if not x.startswith("#")]
        for i in range(0, len(lines), 2):
            p = lines[i].split()
            if len(p) < 10:
                continue
            q = np.array(list(map(float, p[1:5]))); tv = np.array(list(map(float, p[5:8])))
            out[p[9]] = centre(q, tv)
        return out
    with open(os.path.join(d, "images.bin"), "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        for _ in range(n):
            f.read(4); q = np.array(struct.unpack("<4d", f.read(32))); tv = np.array(struct.unpack("<3d", f.read(24)))
            f.read(4); name = b""
            while (c := f.read(1)) != b"\0":
                name += c
            k = struct.unpack("<Q", f.read(8))[0]; f.read(24 * k)
            out[name.decode()] = centre(q, tv)
    return out


def centre(q, t):
    w, x, y, z = q / np.linalg.norm(q)
    R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                  [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    return -R.T @ t


def umeyama(X, Y):
    mx, my = X.mean(0), Y.mean(0); Xc, Yc = X - mx, Y - my
    U, S, Vt = np.linalg.svd(Yc.T @ Xc / len(X)); D = np.eye(3); D[2, 2] = np.sign(np.linalg.det(U @ Vt))
    R = U @ D @ Vt; s = np.trace(np.diag(S) @ D) / Xc.var(0).sum(); return s, R, my - s * R @ mx


ap = argparse.ArgumentParser()
ap.add_argument("work"); ap.add_argument("a"); ap.add_argument("b")
ap.add_argument("--names", nargs=2, default=["A", "B"]); ap.add_argument("--out", default="")
args = ap.parse_args()
fr = json.load(open(os.path.join(args.work, "frames.json")))["frames"]
fps_t = {x["name"]: x.get("pts", int(x["name"].split("_")[1]) / 30.0) for x in fr}
A = {k[:-4] if k.endswith(".jpg") else k: v for k, v in read_images(args.a).items()}
B = {k[:-4] if k.endswith(".jpg") else k: v for k, v in read_images(args.b).items()}
n = len(fr); res = dict(keyframes=n)
for nm, M in zip(args.names, (A, B)):
    res[nm] = dict(placed=len(M), placed_pct=round(100 * len(M) / n, 1))
com = sorted(set(A) & set(B))
if len(com) >= 3:
    X = np.array([A[k] for k in com]); Y = np.array([B[k] for k in com])
    s, R, t = umeyama(X, Y); e = np.linalg.norm((s * (R @ X.T)).T + t - Y, axis=1)
    res["common"] = len(com)
    res[f"{args.names[0]}_vs_{args.names[1]}"] = dict(median=round(float(np.median(e)), 4), p90=round(float(np.percentile(e, 90)), 4),
                                                       rmse=round(float(np.sqrt((e ** 2).mean())), 4), scale=round(float(s), 4))
T = max(fps_t.values()); per = []
for a0 in np.arange(0, T, 15.0):
    ks = [x["name"] for x in fr if a0 <= fps_t[x["name"]] < a0 + 15]
    if ks:
        per.append(dict(t0=float(a0), keyframes=len(ks), **{nm: sum(k in M for k in ks) for nm, M in zip(args.names, (A, B))}))
res["per_15s"] = per
print(json.dumps({k: v for k, v in res.items() if k != "per_15s"}, indent=1))
for p in per:
    print(f"  {p['t0']:5.0f} s  {p['keyframes']:4d} keyframes  " + "  ".join(f"{nm} {p[nm]:4d}" for nm in args.names))
if args.out:
    json.dump(res, open(args.out, "w"), indent=1)
