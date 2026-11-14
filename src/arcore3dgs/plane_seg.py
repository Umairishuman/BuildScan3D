"""Per-frame planar regions (walls, floor, ceiling, doors, table tops) for the planar prior in geo_splatfacto.

PlanarGS (NeurIPS 2025) gets its planes from a vision-language segmenter; we have SfM-anchored Metric3D depth
and normals for every frame (mono_prior.py), which are reliable on exactly the large plain surfaces that 3DGS
gets wrong. Planes are found per frame by 1-point RANSAC: a pixel's 3D point + normal is a plane hypothesis;
inliers are pixels within --tau of the plane (relative to depth) whose normal agrees within --angle deg.
The best plane is refit by least squares, its largest connected regions (>= --min_area of the image) are kept
and eroded by 2 px so plane borders (corners, wall-object edges) are not flattened. Repeat up to --max_planes.

Writes <work>/planes/<name>.png (uint8 label map at the prior resolution, 0 = not planar) and planes/stats.json.

  python src/arcore3dgs/plane_seg.py --work <work_sfm>
"""
import os, json, argparse
import numpy as np, cv2

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--down", type=int, default=4)
ap.add_argument("--max_planes", type=int, default=8)
ap.add_argument("--min_area", type=float, default=0.02)
ap.add_argument("--tau", type=float, default=0.02, help="inlier distance as a fraction of depth")
ap.add_argument("--angle", type=float, default=15.0)
ap.add_argument("--hyp", type=int, default=300)
ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--debug", type=int, default=0, help="write N overlay images to planes/_debug")
args = ap.parse_args()
meta = json.load(open(os.path.join(args.work, "frames.json"))); d = args.down
fx, fy, cx, cy = meta["fx"] / d, meta["fy"] / d, meta["cx"] / d, meta["cy"] / d
out = os.path.join(args.work, "planes"); os.makedirs(out, exist_ok=True)
rng = np.random.default_rng(0); cosT = np.cos(np.radians(args.angle))
frames = meta["frames"][: args.limit] if args.limit else meta["frames"]
stats = {}; dbg = 0
for fi, f in enumerate(frames):
    z = np.load(os.path.join(args.work, "mono_prior", f["name"] + ".npz"))
    D = z["depth"].astype(np.float32); N = z["normal"].astype(np.float32) / 127.0; V = z["valid"].copy()
    h, w = D.shape
    v, u = np.mgrid[0:h, 0:w]
    P = np.dstack([(u + 0.5 - cx) / fx * D, (v + 0.5 - cy) / fy * D, D])
    # normals from depth are noisy at depth edges: only seed / accept pixels with a locally consistent normal
    Nb = cv2.blur(N, (5, 5)); V &= np.linalg.norm(Nb, axis=2) > 0.9
    labels = np.zeros((h, w), np.uint8); free = V.copy(); planes = []
    Pf, Nf = P.reshape(-1, 3), N.reshape(-1, 3)
    sub = np.zeros((h, w), bool); sub[::2, ::2] = True
    for k in range(args.max_planes):
        cand = np.flatnonzero((free & sub).ravel())
        if len(cand) < args.min_area * h * w / 4:
            break
        seeds = rng.choice(cand, min(args.hyp, len(cand)), replace=False)
        Ps, Ns = Pf[seeds], Nf[seeds]; ds = (Ns * Ps).sum(1)
        # score hypotheses on the subsampled free pixels
        Pc, Nc, zc = Pf[cand], Nf[cand], Pf[cand, 2]
        best, bscore = None, 0
        for j in range(0, len(seeds), 50):
            r = np.abs(Pc @ Ns[j:j + 50].T - ds[j:j + 50]) < args.tau * zc[:, None]
            r &= (Nc @ Ns[j:j + 50].T) > cosT
            sc = r.sum(0)
            if sc.max() > bscore:
                bscore = sc.max(); best = j + int(sc.argmax())
        if bscore < args.min_area * h * w / 4:
            break
        n, dd = Ns[best], ds[best]
        for _ in range(2):                                   # least-squares refit on all free inliers
            inl = free & (np.abs(P @ n - dd) < args.tau * D) & ((N @ n) > cosT)
            Q = P[inl]; c = Q.mean(0); _, _, Vt = np.linalg.svd(Q - c, full_matrices=False)
            n = Vt[2] * np.sign(Vt[2] @ n); dd = n @ c
        inl = free & (np.abs(P @ n - dd) < args.tau * D) & ((N @ n) > cosT)
        # fill the speckle holes (normal noise on plain surfaces) where the surface is still at the plane's depth
        near = (np.abs(P @ n - dd) < 2 * args.tau * D) & V & free
        inl = cv2.morphologyEx(inl.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)) & near.astype(np.uint8)
        inl = cv2.morphologyEx(inl, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        nc, cc, st, _ = cv2.connectedComponentsWithStats(inl, connectivity=4)
        keep = np.zeros((h, w), np.uint8)
        for c_ in range(1, nc):
            if st[c_, cv2.CC_STAT_AREA] >= args.min_area * h * w:
                keep[cc == c_] = 1
        free &= ~inl.astype(bool)                            # whatever happens, do not re-propose these pixels
        if keep.sum() == 0:
            continue
        keep = cv2.erode(keep, np.ones((5, 5), np.uint8))   # leave plane borders (corners, edges) free
        lab = len(planes) + 1
        labels[(keep > 0) & (labels == 0)] = lab
        planes.append(dict(n=n.round(4).tolist(), d=float(dd), area=float(keep.mean())))
    cv2.imwrite(os.path.join(out, f["name"] + ".png"), labels)
    stats[f["name"]] = dict(planes=len(planes), coverage=float((labels > 0).mean()), detail=planes)
    if dbg < args.debug and fi % max(1, len(frames) // args.debug) == 0:
        os.makedirs(os.path.join(out, "_debug"), exist_ok=True)
        img = cv2.resize(cv2.imread(os.path.join(args.work, "images", f["name"] + ".jpg")), (w, h), interpolation=cv2.INTER_AREA)
        pal = np.array([[0, 0, 0]] + [list(cv2.cvtColor(np.uint8([[[i * 22 % 180, 220, 255]]]), cv2.COLOR_HSV2BGR)[0, 0]) for i in range(1, 16)], np.uint8)
        ov = np.where(labels[..., None] > 0, (0.45 * img + 0.55 * pal[labels]).astype(np.uint8), img)
        cv2.imwrite(os.path.join(out, "_debug", f["name"] + ".jpg"), np.hstack([img, ov])); dbg += 1
    if fi % 100 == 0:
        print(f"{fi}/{len(frames)} {f['name']}: {len(planes)} planes, {100 * (labels > 0).mean():.0f}% of pixels", flush=True)
json.dump(stats, open(os.path.join(out, "stats.json"), "w"), indent=1)
cov = np.array([s["coverage"] for s in stats.values()]); npl = np.array([s["planes"] for s in stats.values()])
print(f"done: {len(stats)} frames, median {np.median(npl):.0f} planes covering {100 * np.median(cov):.0f}% of pixels")
