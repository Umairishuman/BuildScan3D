"""Room-plane anchoring, preview without training (2026-11-24, R-125): one shared plane per wall / floor / ceiling,
found in the trained model itself, and the splats near it snapped onto it.

Why: splats float off walls and floor because the frames that see a wall disagree slightly (residual camera error)
and a plain wall gives no texture to say which depth is right; training then keeps several thin layers ("copies").
The per-frame planar term (geo_splatfacto --planar_lambda) flattens a wall inside each frame but never makes frames
agree on one wall. Here, on a trained splat:
  1. splats whose normal (axis of the smallest scale) is within --snap deg of a world axis (the model is levelled and
     scan_009's surfaces follow the axes, room_planes.py) and that are flat (smallest / middle scale < --flat) vote
     for their coordinate along that axis, weighted by opacity x area;
  2. per axis, peaks of the vote histogram (--bin units, smoothed) are candidate planes; a weaker peak within --merge
     units of a stronger one whose footprint (cells of --cell units on the other two axes) overlaps the stronger's by
     >= --overlap of its own cells is a copy of the same surface and is merged into it (a separate surface beside a
     wall, e.g. a wardrobe front, covers other cells and stays a plane of its own);
  3. every axis-aligned splat within --band units of a plane is moved onto it, its rotation set so its normal is the
     axis, and its scale along the normal set to the smallest scale of the model's flat splats (thin);
     everything else (furniture, doors, the AC) is left as it is.
Prints per plane offset, support and how thick the layer was (weighted std of the snapped splats' offsets), and
writes <out>.ply and <out>_planes.json. A preview: rendering checks only; the real method moves this into training.

  python src/arcore3dgs/plane_snap.py --ply <splat.ply> --out <out.ply> [--snap 15 --band 0.3 --merge 0.35]
"""
import argparse
import json

import numpy as np
from plyfile import PlyData, PlyElement


def quat_to_R(q):
    q = q / np.linalg.norm(q, axis=1, keepdims=True); w, x, y, z = q.T
    return np.stack([np.stack([1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)], -1),
                     np.stack([2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)], -1),
                     np.stack([2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)], -1)], 1)


def R_to_quat(R):
    t = np.trace(R, axis1=1, axis2=2); q = np.zeros((len(R), 4))
    s = np.sqrt(np.maximum(1 + t, 1e-12)) * 2
    q[:, 0] = s / 4; q[:, 1] = (R[:, 2, 1] - R[:, 1, 2]) / s; q[:, 2] = (R[:, 0, 2] - R[:, 2, 0]) / s
    q[:, 3] = (R[:, 1, 0] - R[:, 0, 1]) / s
    return q / np.linalg.norm(q, axis=1, keepdims=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ply", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--snap", type=float, default=15.0, help="deg between a splat's normal and the axis")
    ap.add_argument("--flat", type=float, default=0.3, help="smallest / middle scale below this = a flat splat")
    ap.add_argument("--min_opacity", type=float, default=0.2)
    ap.add_argument("--bin", type=float, default=0.02); ap.add_argument("--smooth", type=float, default=0.04)
    ap.add_argument("--min_support", type=float, default=0.02, help="share of an axis's votes a plane needs")
    ap.add_argument("--merge", type=float, default=0.9, help="units: a weaker peak this close may be a copy")
    ap.add_argument("--cell", type=float, default=0.25); ap.add_argument("--overlap", type=float, default=0.3)
    ap.add_argument("--band", type=float, default=0.15, help="units: splats this close to a peak belong to it")
    a = ap.parse_args()

    ply = PlyData.read(a.ply); v = ply["vertex"]; d = v.data.copy()
    X = np.stack([d["x"], d["y"], d["z"]], 1).astype(np.float64)
    S = np.exp(np.stack([d[f"scale_{i}"] for i in range(3)], 1).astype(np.float64))
    Q = np.stack([d[f"rot_{i}"] for i in range(4)], 1).astype(np.float64)
    op = 1 / (1 + np.exp(-d["opacity"].astype(np.float64)))
    R = quat_to_R(Q)
    srt = np.sort(S, 1); imin = np.argmin(S, 1)
    nrm = R[np.arange(len(R)), :, imin]                                   # world normal = column of the smallest axis
    flat = (srt[:, 0] / np.maximum(srt[:, 1], 1e-9) < a.flat) & (op > a.min_opacity)
    thin = max(float(np.median(srt[flat, 0])) if flat.any() else 1e-3, 1e-4)
    area = srt[:, 1] * srt[:, 2]
    cos = np.cos(np.radians(a.snap))
    planes, assign = [], np.full(len(X), -1)
    for ax in range(3):
        al = np.abs(nrm[:, ax]) > cos
        vote = al & flat
        c = X[vote, ax]; w = op[vote] * area[vote]
        if len(c) < 100:
            continue
        lo, hi = np.percentile(c, 0.5), np.percentile(c, 99.5)
        edges = np.arange(lo, hi + a.bin, a.bin); h, _ = np.histogram(c, edges, weights=w)
        k = int(max(1, round(a.smooth / a.bin))); ker = np.exp(-0.5 * (np.arange(-3 * k, 3 * k + 1) / k) ** 2)
        hs = np.convolve(h, ker / ker.sum(), "same"); ctr = (edges[:-1] + edges[1:]) / 2
        pk = [i for i in range(1, len(hs) - 1) if hs[i] >= hs[i - 1] and hs[i] > hs[i + 1] and hs[i] > a.min_support * hs.max()]
        pk = sorted(pk, key=lambda i: -hs[i])
        idx = np.flatnonzero(al)
        dist = np.abs(X[idx, ax][:, None] - ctr[pk][None])               # every aligned splat -> its nearest peak
        nb = np.argmin(dist, 1); inb = dist[np.arange(len(idx)), nb] < a.band
        oth = [o for o in range(3) if o != ax]
        foot = [set(map(tuple, np.floor(X[idx[inb & (nb == j)]][:, oth] / a.cell).astype(int))) for j in range(len(pk))]
        owner = list(range(len(pk)))                                     # strongest first: weaker copies join it
        for j in range(len(pk)):
            for i in range(j):
                if owner[i] == i and abs(ctr[pk[i]] - ctr[pk[j]]) <= a.merge and foot[j] and                         len(foot[j] & foot[i]) >= a.overlap * len(foot[j]):
                    owner[j] = i; break
        for i in range(len(pk)):
            if owner[i] != i:
                continue
            grp = [j for j in range(len(pk)) if owner[j] == i]
            m = idx[inb & np.isin(nb, grp)]
            if len(m) == 0:
                continue
            off = float(ctr[pk[i]]); ww = op[m] * area[m]
            th = float(np.sqrt(np.average((X[m, ax] - off) ** 2, weights=ww)))
            planes.append(dict(axis="XYZ"[ax], offset=off, splats=int(len(m)), support=float(hs[pk[i]] / hs.max()),
                               thickness_before=th, merged_copies=[float(ctr[pk[j]]) for j in grp if j != i]))
            assign[m] = len(planes) - 1
    # snap
    m = assign >= 0
    for p_i, p in enumerate(planes):
        s = assign == p_i; ax = "XYZ".index(p["axis"])
        X[s, ax] = p["offset"]
        n = np.zeros(3); n[ax] = 1.0
        for i in np.flatnonzero(s):                                      # rotate so the smallest axis is exactly n
            Ri = R[i]; c0 = Ri[:, imin[i]] * np.sign(Ri[:, imin[i]] @ n)
            v_ = np.cross(c0, n); s_ = np.linalg.norm(v_); c_ = c0 @ n
            if s_ > 1e-9:
                K = np.array([[0, -v_[2], v_[1]], [v_[2], 0, -v_[0]], [-v_[1], v_[0], 0]])
                R[i] = (np.eye(3) + K + K @ K * ((1 - c_) / s_ ** 2)) @ Ri
        S[s, imin[s]] = np.minimum(S[s, imin[s]], thin)
    Qn = R_to_quat(R[m])
    d["x"], d["y"], d["z"] = X[:, 0].astype(np.float32), X[:, 1].astype(np.float32), X[:, 2].astype(np.float32)
    for i in range(4):
        col = d[f"rot_{i}"].copy(); col[m] = Qn[:, i]; d[f"rot_{i}"] = col
    for i in range(3):
        d[f"scale_{i}"] = np.log(S[:, i]).astype(np.float32)
    PlyData([PlyElement.describe(d, "vertex")]).write(a.out)
    json.dump(dict(params=vars(a), thin=thin, snapped=int(m.sum()), total=len(X), planes=planes),
              open(a.out[:-4] + "_planes.json", "w"), indent=1)
    print(f"{len(X)} splats, {int(flat.sum())} flat; thin scale {thin:.4f}; snapped {int(m.sum())} "
          f"({100 * m.mean():.1f} %) onto {len(planes)} planes")
    for p in sorted(planes, key=lambda p: (p["axis"], p["offset"])):
        print(f"  {p['axis']} = {p['offset']:7.3f}: {p['splats']:6d} splats, support {p['support']:.2f}, layer thickness "
              f"before {p['thickness_before']:.3f} units, merged copies at {[round(c, 2) for c in p['merged_copies']]}")


if __name__ == "__main__":
    main()
