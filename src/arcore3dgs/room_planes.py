"""Room planes (walls, floor, ceiling) from the per-frame planar regions, before any training
(FEATURELESS_TRACKING_PLAN §11.b).

layout.py (Umair's Step 4) fits the layout to a trained splat's rendered depth; on scan_009 that depth is the thing
that is wrong, so the planes here come only from inputs that do not depend on a trained model:
  - plane_seg.py's planar regions of every frame (<sfm>/planes/<name>.png, label k = stats detail[k-1], n.P = d in
    the OpenCV camera frame), lifted to the world with that frame's Metric3D prior depth (<sfm>/mono_prior) and pose;
  - the SfM points (<sfm>/sparse.npz), which are multi-view consistent, to anchor a plane where it has any.
The model is levelled (+Y up, rot_sfm.py / sfm_colmap.py), and scan_009's surfaces line up with the world axes
(area-weighted plane normals: X 33 %, Y 16 %, Z 48 % within 25 deg). A region whose world normal is within --snap
deg of an axis is assigned to it; per axis its points' median coordinate is the region's offset. Offsets are
clustered across frames (--tol model units), weighted by pixel count; a cluster needs --min_frames frames. Each
cluster's offset is then the median axis coordinate of the SfM points within --sfm_tol of it inside its extent (if
>= --min_sfm points), else the weighted median of its regions. Extent: 2nd - 98th percentile of its region points.

Frames used: those whose prior scale is trustworthy, i.e. >= --min_inliers SfM inliers and residual < --max_err in
mono_prior/stats.json (frames without SfM support carry a guessed scale and are left out of the fit).

  python src/arcore3dgs/room_planes.py --work <sfm dir> --out <dir> [--snap 12] [--tol 0.15]
Writes <out>/room_planes.json and <out>/room_plan.png (top view: walls by support, camera path, SfM points).
"""
import argparse
import json
import os

import cv2
import numpy as np

G = np.diag([1.0, -1.0, -1.0, 1.0])
AX = "XYZ"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--snap", type=float, default=12.0)
    ap.add_argument("--tol", type=float, default=0.15)
    ap.add_argument("--min_frames", type=int, default=5)
    ap.add_argument("--min_inliers", type=int, default=20); ap.add_argument("--max_err", type=float, default=0.15)
    ap.add_argument("--sfm_tol", type=float, default=0.12); ap.add_argument("--min_sfm", type=int, default=30)
    ap.add_argument("--stride", type=int, default=4, help="pixel subsampling when lifting regions")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    meta = json.load(open(os.path.join(a.work, "frames.json")))
    st = json.load(open(os.path.join(a.work, "planes", "stats.json")))
    ms = json.load(open(os.path.join(a.work, "mono_prior", "stats.json")))
    X = np.load(os.path.join(a.work, "sparse.npz"))["X"]
    cos_snap = np.cos(np.radians(a.snap))

    regions = []                                   # (axis, sign, offset, npx, frame, points[k,3])
    used = 0
    for f in meta["frames"]:
        n = f["name"]; s = ms.get(n)
        if n not in st or s is None or s.get("inliers", 0) < a.min_inliers or s.get("median_rel_err", 1) >= a.max_err:
            continue
        L = cv2.imread(os.path.join(a.work, "planes", n + ".png"), cv2.IMREAD_UNCHANGED)
        D = np.load(os.path.join(a.work, "mono_prior", n + ".npz"))["depth"].astype(np.float32)
        h, w = D.shape; d = meta["W"] / w
        fx, fy, cx, cy = meta["fx"] / d, meta["fy"] / d, meta["cx"] / d, meta["cy"] / d
        c2w = np.array(f["c2w"]) @ G
        used += 1
        for k, p in enumerate(st[n]["detail"], start=1):
            nw = c2w[:3, :3] @ np.array(p["n"])
            ax = int(np.argmax(np.abs(nw)))
            if abs(nw[ax]) < cos_snap:
                continue
            v, u = np.nonzero(L == k)
            sel = (v % a.stride == 0) & (u % a.stride == 0); v, u = v[sel], u[sel]
            z = D[v, u]
            if len(z) < 20:
                continue
            P = np.stack([(u + 0.5 - cx) / fx * z, (v + 0.5 - cy) / fy * z, z], 1) @ c2w[:3, :3].T + c2w[:3, 3]
            # the side the camera sees the plane from (+1: camera at larger coordinate than the plane)
            off = float(np.median(P[:, ax])); side = 1 if c2w[ax, 3] > off else -1
            regions.append((ax, side, off, len(z), n, P))
    print(f"{used} frames with a trusted prior scale, {len(regions)} axis-aligned planar regions "
          f"(X {sum(r[0] == 0 for r in regions)}, Y {sum(r[0] == 1 for r in regions)}, Z {sum(r[0] == 2 for r in regions)})",
          flush=True)

    planes = []
    for ax in range(3):
        for side in (1, -1):
            R = sorted([r for r in regions if r[0] == ax and r[1] == side], key=lambda r: r[2])
            groups, cur = [], []
            for r in R:                               # 1D agglomeration on the offset
                if cur and r[2] - np.average([c[2] for c in cur], weights=[c[3] for c in cur]) > a.tol:
                    groups.append(cur); cur = []
                cur.append(r)
            if cur:
                groups.append(cur)
            for g in groups:
                frames = sorted({r[4] for r in g})
                if len(frames) < a.min_frames:
                    continue
                P = np.concatenate([r[5] for r in g]); wts = np.concatenate([np.full(len(r[5]), 1.0) for r in g])
                o_reg = float(np.median(P[:, ax]))
                oth = [i for i in range(3) if i != ax]
                lo = np.percentile(P[:, oth], 2, axis=0); hi = np.percentile(P[:, oth], 98, axis=0)
                inside = np.all((X[:, oth] >= lo) & (X[:, oth] <= hi), axis=1) & (np.abs(X[:, ax] - o_reg) < a.sfm_tol)
                n_sfm = int(inside.sum())
                o = float(np.median(X[inside, ax])) if n_sfm >= a.min_sfm else o_reg
                spread = float(np.median(np.abs(P[:, ax] - o)))
                planes.append(dict(axis=AX[ax], side=side, offset=o, offset_regions=o_reg, n_sfm=n_sfm,
                                   anchored=n_sfm >= a.min_sfm, frames=len(frames), pixels=int(sum(r[3] for r in g)),
                                   spread=spread,
                                   extent={AX[oth[0]]: [float(lo[0]), float(hi[0])], AX[oth[1]]: [float(lo[1]), float(hi[1])]},
                                   first_frame=frames[0], last_frame=frames[-1]))
    planes.sort(key=lambda p: -p["pixels"])
    for i, p in enumerate(planes):
        p["id"] = i
        kind = ("floor" if p["side"] == 1 else "ceiling") if p["axis"] == "Y" else "wall"
        p["kind"] = kind
    ys = [p for p in planes if p["axis"] == "Y"]
    print(f"{len(planes)} planes (needs >= {a.min_frames} frames):")
    for p in planes:
        ext = ", ".join(f"{k} {v[0]:.2f}..{v[1]:.2f}" for k, v in p["extent"].items())
        print(f"  #{p['id']:2d} {p['kind']:7s} {p['axis']}{'+' if p['side'] > 0 else '-'} offset {p['offset']:7.3f} "
              f"({'SfM ' + str(p['n_sfm']) + ' pts' if p['anchored'] else 'regions only'}, regions {p['offset_regions']:.3f}, "
              f"spread {p['spread']:.3f}) {p['frames']:3d} frames {p['pixels']:6d} px  {ext}", flush=True)
    json.dump(dict(work=a.work, up="+Y", units="model", params=vars(a), planes=planes),
              open(os.path.join(a.out, "room_planes.json"), "w"), indent=1)

    # top view (X right, Z down): walls as segments (width ~ support), camera path, SfM points
    C = np.array([np.array(f["c2w"])[:3, 3] for f in meta["frames"]])
    pts = np.r_[C[:, [0, 2]], X[:, [0, 2]]]
    lo2 = np.percentile(pts, 1, axis=0) - 0.5; hi2 = np.percentile(pts, 99, axis=0) + 0.5
    S = 900 / max(hi2 - lo2); img = np.full((int((hi2[1] - lo2[1]) * S) + 40, int((hi2[0] - lo2[0]) * S) + 40, 3), 255, np.uint8)
    to = lambda x, z: (int((x - lo2[0]) * S) + 20, int((z - lo2[1]) * S) + 20)
    for x, z in X[:, [0, 2]][::3]:
        if lo2[0] <= x <= hi2[0] and lo2[1] <= z <= hi2[1]:
            cv2.circle(img, to(x, z), 1, (200, 200, 200), -1)
    for a_, b_ in zip(C[:-1], C[1:]):
        cv2.line(img, to(a_[0], a_[2]), to(b_[0], b_[2]), (255, 150, 0), 1)
    for p in planes:
        if p["axis"] == "Y":
            continue
        if p["axis"] == "X":
            z0, z1 = p["extent"]["Z"]; e = (to(p["offset"], z0), to(p["offset"], z1))
        else:
            x0, x1 = p["extent"]["X"]; e = (to(x0, p["offset"]), to(x1, p["offset"]))
        col = (0, 140, 0) if p["anchored"] else (0, 0, 220)
        cv2.line(img, e[0], e[1], col, max(1, min(6, p["frames"] // 15)))
        cv2.putText(img, f"#{p['id']}", e[0], 0, 0.45, col, 1)
    cv2.putText(img, "walls: green = anchored on SfM points, red = regions only; blue = camera path; grey = SfM points",
                (10, img.shape[0] - 8), 0, 0.45, (0, 0, 0), 1)
    if ys:
        cv2.putText(img, "  ".join(f"{p['kind']} #{p['id']} y={p['offset']:.2f}" for p in ys[:4]), (10, 16), 0, 0.45, (0, 0, 0), 1)
    cv2.imwrite(os.path.join(a.out, "room_plan.png"), img)


if __name__ == "__main__":
    main()
