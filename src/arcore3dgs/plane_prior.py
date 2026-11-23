"""Depth / normal priors that agree across frames, from the room planes (FEATURELESS_TRACKING_PLAN §11.c).

mono_prior.py scales each frame's Metric3D depth on its own, so overlapping frames disagree about where a wall is
(R-093: 15.1 % median depth disagreement between neighbouring frames, VGGT 5.3 %). Here every frame is tied to one
geometry, the room planes of room_planes.py:
  1. per frame, ray-cast the planes (axis-aligned, within their extent + --margin): depth Dp and plane id per pixel;
  2. scale s_f = median(Dp / D_mono) over plane_seg pixels whose normal agrees with the hit plane (<= --agree_deg):
     the frame's whole Metric3D depth is rescaled by s_f (its shape kept, its scale now the room's);
  3. "trusted" pixels (plane_seg region, normal agrees, rescaled depth within --agree_rel of Dp): depth = Dp, normal
     = the plane's normal; they become valid even if mono_prior had no SfM support for the frame.
Writes the priors in place (<work>/mono_prior/<name>.npz, same format; run it on a copy) and
<work>/mono_prior/plane_prior.json; prints the depth disagreement between neighbouring frames before and after.

  python src/arcore3dgs/plane_prior.py --work <sfm dir> --planes <room_planes.json> [--min_frames 10]
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
G = np.diag([1.0, -1.0, -1.0, 1.0])
AXI = {"X": 0, "Y": 1, "Z": 2}


def consistency(D, K, C, V, pairs):
    from vggt_chunk import depth_consistency
    e = depth_consistency(D, K, C, pairs, valid=V)
    return float(np.median(e)) if e else float("nan"), len(e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True); ap.add_argument("--planes", required=True)
    ap.add_argument("--min_frames", type=int, default=10, help="use room planes seen in at least this many frames")
    ap.add_argument("--margin", type=float, default=0.3, help="model units added around each plane's extent")
    ap.add_argument("--agree_deg", type=float, default=15.0); ap.add_argument("--agree_rel", type=float, default=0.2)
    ap.add_argument("--check_every", type=int, default=3, help="frame step for the before / after consistency check")
    a = ap.parse_args()
    meta = json.load(open(os.path.join(a.work, "frames.json"))); fr = sorted(meta["frames"], key=lambda f: f["pts"])
    PL = [p for p in json.load(open(a.planes))["planes"] if p["frames"] >= a.min_frames]
    print(f"{len(PL)} room planes with >= {a.min_frames} frames", flush=True)
    cosA = np.cos(np.radians(a.agree_deg))
    mp = os.path.join(a.work, "mono_prior")
    D0 = np.load(os.path.join(mp, fr[0]["name"] + ".npz"))["depth"]; h, w = D0.shape; d = meta["W"] / w
    K = np.array([[meta["fx"] / d, 0, meta["cx"] / d], [0, meta["fy"] / d, meta["cy"] / d], [0, 0, 1.0]])
    v, u = np.mgrid[0:h, 0:w]
    rays = np.stack([(u + 0.5 - K[0, 2]) / K[0, 0], (v + 0.5 - K[1, 2]) / K[1, 1], np.ones_like(u, float)], -1)  # z = 1

    before = dict(D=[], V=[], C=[]); after = dict(D=[], V=[], C=[]); stats = {}
    for fi, f in enumerate(fr):
        n = f["name"]; p_ = os.path.join(mp, n + ".npz"); z = np.load(p_)
        Dm = z["depth"].astype(np.float32); Nm = z["normal"].astype(np.float32) / 127.0; Vm = z["valid"]
        c2w = np.array(f["c2w"]) @ G; Rwc, C = c2w[:3, :3], c2w[:3, 3]
        dw = rays @ Rwc.T                                                  # world direction per pixel (z_cam = 1)
        Dp = np.full((h, w), np.inf, np.float32); Np = np.zeros((h, w, 3), np.float32)
        for p in PL:
            ax = AXI[p["axis"]]; den = dw[..., ax]
            with np.errstate(divide="ignore", invalid="ignore"):
                t = (p["offset"] - C[ax]) / den
            hit = C + dw * t[..., None]
            ok = (t > 0.05) & np.isfinite(t)
            for k, (lo, hi) in p["extent"].items():
                ok &= (hit[..., AXI[k]] >= lo - a.margin) & (hit[..., AXI[k]] <= hi + a.margin)
            closer = ok & (t < Dp)
            if closer.any():
                Dp[closer] = t[closer]
                nw = np.zeros(3); nw[ax] = float(p["side"])                  # points towards the camera's side
                Np[closer] = Rwc.T @ nw
        has = np.isfinite(Dp)
        L = cv2.imread(os.path.join(a.work, "planes", n + ".png"), cv2.IMREAD_UNCHANGED)
        region = (L > 0) if L is not None else np.zeros((h, w), bool)
        agree = has & region & ((Nm * Np).sum(-1) > cosA) & (Dm > 0)
        s_f = float(np.median(Dp[agree] / Dm[agree])) if agree.sum() > 200 else 1.0
        # the plane set can hold parallel duplicates of a wall (residual drift, R-094): refit the scale on the pixels
        # whose depth already agrees with the hit plane within 30 %, twice, so a wrong ("ghost") plane cannot pull it
        for _ in range(2):
            close = agree & (np.abs(Dm * s_f - Dp) < 0.3 * Dp)
            if close.sum() > 200:
                s_f = float(np.median(Dp[close] / Dm[close]))
        agree &= np.abs(Dm * s_f - Dp) < 0.3 * Dp
        Dn = Dm * s_f
        trusted = agree & (np.abs(Dn - Dp) < a.agree_rel * Dp)
        Dn[trusted] = Dp[trusted]
        Nn = Nm.copy(); Nn[trusted] = Np[trusted]
        Vn = (Vm & (s_f > 0)) | trusted
        if agree.sum() <= 200 and not Vm.any():
            Vn = Vm
        np.savez_compressed(p_, depth=Dn.astype(np.float16), normal=np.clip(Nn * 127, -127, 127).astype(np.int8), valid=Vn)
        stats[n] = dict(scale=s_f, agree_px=int(agree.sum()), trusted=float(trusted.mean()), had_prior=bool(Vm.any()),
                        valid=float(Vn.mean()))
        if fi % a.check_every == 0:
            before["D"].append(Dm); before["V"].append(Vm); before["C"].append(c2w)
            after["D"].append(Dn); after["V"].append(Vn); after["C"].append(c2w)
        if fi % 100 == 0:
            print(f"{fi}/{len(fr)} {n}: scale {s_f:.3f}, trusted {100 * trusted.mean():.0f} % of pixels", flush=True)
    json.dump(stats, open(os.path.join(mp, "plane_prior.json"), "w"), indent=1)
    sc = np.array([s["scale"] for s in stats.values()]); tr = np.array([s["trusted"] for s in stats.values()])
    print(f"frames: {len(stats)}; scale change median {np.median(sc):.3f} (p10 {np.percentile(sc, 10):.3f}, p90 "
          f"{np.percentile(sc, 90):.3f}); trusted pixels median {100 * np.median(tr):.0f} %; frames that had no prior "
          f"and now have one: {sum(1 for s in stats.values() if not s['had_prior'] and s['valid'] > 0)}", flush=True)
    m = len(before["D"]); pairs = [(i, i + k) for k in (1, 2) for i in range(m - k)]
    Ks = [K] * m
    b = consistency(before["D"], Ks, before["C"], before["V"], pairs)
    c = consistency(after["D"], Ks, after["C"], after["V"], pairs)
    print(f"depth disagreement between neighbouring frames (every {a.check_every}th frame, 1 - 2 apart, median): "
          f"before {100 * b[0]:.1f} % ({b[1]} pairs) -> after {100 * c[0]:.1f} % ({c[1]} pairs)", flush=True)


if __name__ == "__main__":
    main()
