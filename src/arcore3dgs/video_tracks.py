"""Point tracks through every video frame (not only the keyframes), added to a COLMAP text model as extra 2D/3D points.

For captures where keyframe-to-keyframe matching finds little (blur, plain walls: scan_009 has ~0 matched points per
camera at 45 - 60 s and 90 - 105 s). Between two keyframes the video has ~6 more frames, so a point moves a few pixels
per frame and KLT can follow it on texture too faint or blurred for SIFT / ALIKED matching (scan_009, 45 - 60 s:
~260 points survive one keyframe gap, median over 9 starts; FEATURELESS_TRACKING_PLAN §10).

  1. decode the video in order (seeking in the mp4 is not frame-exact), half resolution, CLAHE;
  2. at every keyframe of the model start new corners away from live tracks; track all live points frame to frame
     (pyramidal LK, forward-backward check); record each track's position at every keyframe it reaches;
  3. reject observations that contradict the model's rotations (gyro-based for rot_sfm / prior_ba models): for each
     keyframe pair, RANSAC on the translation direction with the rotation fixed (two points fix it);
  4. triangulate tracks with the current poses, keep those with enough parallax and a sane reprojection; write the
     model with the new points appended (existing points untouched). Then run prior_ba.py on it.

  python video_tracks.py <dataset> <work with frames.json> <model_in (txt)> <model_out> [options]
"""
import os, sys, json, time, shutil, argparse
import numpy as np, cv2
from scipy.spatial.transform import Rotation as Rot

ap = argparse.ArgumentParser()
ap.add_argument("dataset"); ap.add_argument("work"); ap.add_argument("model_in"); ap.add_argument("model_out")
ap.add_argument("--scale", type=float, default=0.5, help="tracking resolution relative to the video")
ap.add_argument("--max_corners", type=int, default=300, help="new corners per keyframe")
ap.add_argument("--quality", type=float, default=0.001)
ap.add_argument("--min_dist", type=float, default=12, help="px at tracking resolution, also from live tracks")
ap.add_argument("--fb", type=float, default=0.7, help="forward-backward error limit, px at tracking resolution")
ap.add_argument("--max_span", type=float, default=2.0, help="s; tracks end after this")
ap.add_argument("--epi_px", type=float, default=3.0, help="RANSAC: distance to the epipolar plane, full-res px")
ap.add_argument("--min_pair", type=int, default=8, help="RANSAC only for keyframe pairs with this many tracks")
ap.add_argument("--min_parallax", type=float, default=1.0, help="deg, largest angle between a track's rays")
ap.add_argument("--max_reproj", type=float, default=10.0, help="px with the current poses (prior_ba refines them)")
ap.add_argument("--only_weak", type=int, default=0,
                help="if > 0: start tracks only in keyframes with fewer than this many 3D observations in the model")
ap.add_argument("--pairs_out", default=None, help="also write the tracks as keyframe-pair correspondences (.npz) "
                "for rot_sfm.py --extra_pairs")
ap.add_argument("--debug_window", type=float, nargs=2, default=None, help="t0 t1 (s): per-stage counts for tracks "
                "starting in this window")
args = ap.parse_args()
t_start = time.time()


def lines(p):
    return [l.rstrip("\n") for l in open(p) if not l.startswith("#")]


# ---------------- model ----------------
cam = lines(os.path.join(args.model_in, "cameras.txt"))[0].split()
assert cam[1] == "OPENCV"
W_, H_ = int(cam[2]), int(cam[3])
fx, fy, cx, cy, k1, k2, p1, p2 = map(float, cam[4:12])
K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1.0]]); dist = np.array([k1, k2, p1, p2])
L = lines(os.path.join(args.model_in, "images.txt"))
imgs = {}
for i in range(0, len(L), 2):
    h = L[i].split(); q = list(map(float, h[1:5]))
    Rcw = Rot.from_quat([q[1], q[2], q[3], q[0]]).as_matrix(); tcw = np.array(list(map(float, h[5:8])))
    a = L[i + 1].split()
    n3d = sum(1 for j in range(2, len(a), 3) if a[j] != "-1")
    imgs[os.path.splitext(h[9])[0]] = dict(id=int(h[0]), header=L[i], pts=L[i + 1], n2d=len(a) // 3, n3d=n3d,
                                            R=Rcw.T, C=-Rcw.T @ tcw)
meta = json.load(open(os.path.join(args.work, "frames.json")))
kf = sorted([(f["video_index"], f["name"]) for f in meta["frames"] if f["name"] in imgs])
kf_at = {v: n for v, n in kf}
print(f"model: {len(imgs)} images, {len(kf)} with a video index; video frames {kf[0][0]} - {kf[-1][0]}", flush=True)
fps = 30.0
pts_of = {f["name"]: f["pts"] for f in meta["frames"]}
if len(kf) > 10:
    fps = (kf[-1][0] - kf[0][0]) / (pts_of[kf[-1][1]] - pts_of[kf[0][1]])
max_frames = int(args.max_span * fps)

# ---------------- tracking ----------------
cap = cv2.VideoCapture(os.path.join(args.dataset, "dataset.mp4"))
clahe = cv2.createCLAHE(3.0, (8, 8))
lk = dict(winSize=(21, 21), maxLevel=4, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 40, 0.01))
s = args.scale
cur = np.zeros((0, 1, 2), np.float32); tid = np.zeros(0, int); born = np.zeros(0, int)
obs = []                                      # (track id, keyframe name, x, y) at full resolution
next_tid = 0; prev = None; vi = -1
while True:
    ok, im = cap.read(); vi += 1
    if not ok or vi > kf[-1][0]:
        break
    if vi < kf[0][0]:
        continue
    g = clahe.apply(cv2.resize(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), None, fx=s, fy=s, interpolation=cv2.INTER_AREA))
    if prev is not None and len(cur):
        nxt, st, _ = cv2.calcOpticalFlowPyrLK(prev, g, cur, None, **lk)
        back, st2, _ = cv2.calcOpticalFlowPyrLK(g, prev, nxt, None, **lk)
        fb = np.linalg.norm(back - cur, axis=2).ravel()
        inside = (nxt[:, 0, 0] >= 0) & (nxt[:, 0, 1] >= 0) & (nxt[:, 0, 0] < g.shape[1] - 1) & (nxt[:, 0, 1] < g.shape[0] - 1)
        keep = (st.ravel() == 1) & (st2.ravel() == 1) & (fb < args.fb) & inside & (vi - born <= max_frames)
        cur, tid, born = nxt[keep], tid[keep], born[keep]
    if vi in kf_at:
        n = kf_at[vi]
        full = cur[:, 0, :] / s + (0.5 / s - 0.5)                       # tracking px -> full-res px
        obs += [(t, n, x, y) for t, (x, y) in zip(tid, full)]
        if args.only_weak <= 0 or imgs[n]["n3d"] < args.only_weak:
            mask = np.full(g.shape, 255, np.uint8)
            for x, y in cur[:, 0, :]:
                cv2.circle(mask, (int(x), int(y)), int(args.min_dist), 0, -1)
            p = cv2.goodFeaturesToTrack(g, args.max_corners, args.quality, args.min_dist, mask=mask)
            if p is not None:
                p = p.astype(np.float32)
                cur = np.concatenate([cur, p]); tid = np.concatenate([tid, np.arange(next_tid, next_tid + len(p))])
                born = np.concatenate([born, np.full(len(p), vi)])
                full = p[:, 0, :] / s + (0.5 / s - 0.5)
                obs += [(next_tid + j, n, x, y) for j, (x, y) in enumerate(full)]
                next_tid += len(p)
    prev = g
    if vi % 1000 == 0:
        print(f"  frame {vi}: {len(cur)} live tracks, {len(obs)} keyframe observations ({time.time() - t_start:.0f}s)",
              flush=True)
print(f"tracking done: {next_tid} tracks, {len(obs)} keyframe observations ({time.time() - t_start:.0f}s)", flush=True)

# ---------------- rotation-fixed RANSAC per keyframe pair ----------------
O_t = np.array([o[0] for o in obs]); O_n = np.array([o[1] for o in obs]); O_uv = np.array([o[2:] for o in obs])
und = cv2.undistortPoints(O_uv.reshape(-1, 1, 2).astype(np.float64), K, dist).reshape(-1, 2)
bear = np.c_[und, np.ones(len(und))]; bear /= np.linalg.norm(bear, axis=1, keepdims=True)
Rw = np.stack([imgs[n]["R"] for n in O_n]); dw = np.einsum("nij,nj->ni", Rw, bear)     # world-frame rays
order = np.lexsort((np.array([pts_of[n] for n in O_n]), O_t))
O_t, O_n, O_uv, dw, bear = O_t[order], O_n[order], O_uv[order], dw[order], bear[order]
starts = np.r_[0, np.flatnonzero(np.diff(O_t)) + 1, len(O_t)]
good = np.ones(len(O_t), bool)
# consecutive observations of a track -> keyframe pairs
pa = []; pb = []
for a_, b_ in zip(starts[:-1], starts[1:]):
    for j in range(a_, b_ - 1):
        pa.append(j); pb.append(j + 1)
pa = np.array(pa); pb = np.array(pb)
pair_key = np.array([f"{O_n[i]}|{O_n[j]}" for i, j in zip(pa, pb)])
thr = args.epi_px / fx
rng = np.random.default_rng(0)
n_tested = n_rej = 0
o_ = np.argsort(pair_key, kind="stable"); sk = pair_key[o_]
cut = np.r_[0, np.flatnonzero(sk[1:] != sk[:-1]) + 1, len(sk)]
for g0, g1 in zip(cut[:-1], cut[1:]):
    m = o_[g0:g1]
    if len(m) < args.min_pair:
        continue
    nv = np.cross(dw[pa[m]], dw[pb[m]])                               # (C_b - C_a) . (d_a x d_b) = 0
    best = None
    for _ in range(100):
        i, j = rng.choice(len(m), 2, replace=False)
        t = np.cross(nv[i], nv[j]); nt = np.linalg.norm(t)
        if nt < 1e-12:
            continue
        inl = np.abs(nv @ (t / nt)) < thr
        if best is None or inl.sum() > best.sum():
            best = inl
    if best is None:
        continue
    n_tested += len(m); n_rej += int((~best).sum())
    good[pb[m[~best]]] = False                                         # the later observation goes
# a rejected observation ends its track there (later ones were tracked from a wrong point)
for a_, b_ in zip(starts[:-1], starts[1:]):
    bad = np.flatnonzero(~good[a_:b_])
    if len(bad):
        good[a_ + bad[0]:b_] = False
print(f"rotation-fixed RANSAC: {n_rej} of {n_tested} tested pair observations rejected; "
      f"{int(good.sum())} of {len(good)} observations kept", flush=True)
if args.pairs_out:
    # every keyframe pair a kept track links (not only neighbours: longer baselines), camera-frame unit bearings,
    # for rot_sfm.py --extra_pairs (pair directions with the rotation fixed: no 3D point and no position needed)
    pairs = {}
    for a_, b_ in zip(starts[:-1], starts[1:]):
        idx = np.arange(a_, b_)[good[a_:b_]]
        for i in range(len(idx)):
            for j in range(i + 1, len(idx)):
                pairs.setdefault((O_n[idx[i]], O_n[idx[j]]), []).append((idx[i], idx[j]))
    keys = sorted(pairs, key=lambda k: (pts_of[k[0]], pts_of[k[1]]))
    off = np.cumsum([0] + [len(pairs[k]) for k in keys])
    ii = np.array([p[0] for k in keys for p in pairs[k]], int); jj = np.array([p[1] for k in keys for p in pairs[k]], int)
    np.savez(args.pairs_out, a=np.array([k[0] for k in keys]), b=np.array([k[1] for k in keys]), off=off,
             b1=bear[ii], b2=bear[jj])
    cnt = np.diff(off)
    print(f"wrote {args.pairs_out}: {len(keys)} keyframe pairs, correspondences per pair median {np.median(cnt):.0f}, "
          f">= 15: {int((cnt >= 15).sum())}", flush=True)

# ---------------- triangulate with the current poses ----------------
Cw = {n: imgs[n]["C"] for n in imgs}
new_pts = []                                                            # (X, [(name, x, y)])
rej = dict(short=0, parallax=0, behind=0, reproj=0)
tri_ok = []
for a_, b_ in zip(starts[:-1], starts[1:]):
    tri_ok.append(False)
    idx = np.arange(a_, b_)[good[a_:b_]]
    if len(idx) < 2:
        rej["short"] += 1; continue
    D = dw[idx]; C = np.stack([Cw[n] for n in O_n[idx]])
    cosmin = (D @ D.T).min()
    if np.degrees(np.arccos(np.clip(cosmin, -1, 1))) < args.min_parallax:
        rej["parallax"] += 1; continue
    A = np.zeros((3, 3)); bvec = np.zeros(3)
    for d, c in zip(D, C):
        P = np.eye(3) - np.outer(d, d); A += P; bvec += P @ c
    X = np.linalg.solve(A, bvec)
    ok = True; errs = []
    for n, (x, y) in zip(O_n[idx], O_uv[idx]):
        R = imgs[n]["R"]; xc = R.T @ (X - Cw[n])
        if xc[2] <= 0:
            ok = False; break
        uv, _ = cv2.projectPoints(xc[None], np.zeros(3), np.zeros(3), K, dist)
        errs.append(np.linalg.norm(uv.ravel() - [x, y]))
    if not ok:
        rej["behind"] += 1; continue
    if max(errs) > args.max_reproj:
        rej["reproj"] += 1; continue
    new_pts.append((X, [(n, x, y) for n, (x, y) in zip(O_n[idx], O_uv[idx])])); tri_ok[-1] = True
if args.debug_window:
    lo, hi = args.debug_window
    t_first = np.array([pts_of[O_n[a_]] for a_ in starts[:-1]])
    win = (t_first >= lo) & (t_first < hi)
    raw2 = np.array([b_ - a_ >= 2 for a_, b_ in zip(starts[:-1], starts[1:])])
    good2 = np.array([good[a_:b_].sum() >= 2 for a_, b_ in zip(starts[:-1], starts[1:])])
    span = np.array([pts_of[O_n[b_ - 1]] - pts_of[O_n[a_]] for a_, b_ in zip(starts[:-1], starts[1:])])
    kfs = sorted({n for n in O_n if lo <= pts_of[n] < hi}, key=lambda n: pts_of[n])
    gaps = np.diff([pts_of[n] for n in kfs])
    print(f"[window {lo}-{hi} s] keyframes {len(kfs)} (gap median {np.median(gaps):.2f} s, max {gaps.max():.2f}); "
          f"tracks started {int(win.sum())}; reach a 2nd keyframe {int((win & raw2).sum())}; after RANSAC "
          f"{int((win & good2).sum())}; span of those median {np.median(span[win & raw2]) if (win & raw2).any() else 0:.2f} s; "
          f"triangulated {int(sum(1 for w_, k_ in zip(win, tri_ok) if w_ and k_))}", flush=True)
print(f"triangulated {len(new_pts)} new points ({sum(len(p[1]) for p in new_pts)} observations); rejected {rej}",
      flush=True)

# ---------------- write ----------------
os.makedirs(args.model_out, exist_ok=True)
for fn in ("cameras.txt", "rigs.txt", "frames.txt"):
    if os.path.exists(os.path.join(args.model_in, fn)):
        shutil.copy(os.path.join(args.model_in, fn), os.path.join(args.model_out, fn))
P3 = lines(os.path.join(args.model_in, "points3D.txt"))
pid0 = max(int(r.split()[0]) for r in P3) + 1 if P3 else 1
extra = {n: [] for n in imgs}                                           # name -> [(x, y, pid)]
tracks_out = []
for k, (X, ob) in enumerate(new_pts):
    pid = pid0 + k; tr = []
    for n, x, y in ob:
        tr.append((imgs[n]["id"], imgs[n]["n2d"] + len(extra[n]))); extra[n].append((x, y, pid))
    tracks_out.append(f"{pid} {X[0]!r} {X[1]!r} {X[2]!r} 128 128 128 1.0 " + " ".join(f"{a} {b}" for a, b in tr))
with open(os.path.join(args.model_out, "images.txt"), "w") as f:
    f.write(f"# Number of images: {len(imgs)}\n")
    for n, d in sorted(imgs.items(), key=lambda x: x[1]["id"]):
        add = " ".join(f"{x:.3f} {y:.3f} {p}" for x, y, p in extra[n])
        f.write(d["header"] + "\n" + (d["pts"] + " " + add if d["pts"].strip() and add else d["pts"] or add) + "\n")
with open(os.path.join(args.model_out, "points3D.txt"), "w") as f:
    f.write(f"# Number of points: {len(P3) + len(tracks_out)}\n")
    for r in P3 + tracks_out:
        f.write(r + "\n")
before = np.array([d["n3d"] for d in imgs.values()]); after = before + np.array([len(extra[n]) for n in imgs])
print(f"3D observations per image: median {np.median(before):.0f} -> {np.median(after):.0f}; images with < 20: "
      f"{int((before < 20).sum())} -> {int((after < 20).sum())}; < 50: {int((before < 50).sum())} -> "
      f"{int((after < 50).sum())}", flush=True)
json.dump(dict(tracks=int(next_tid), observations=len(obs), kept=int(good.sum()), new_points=len(new_pts),
               rejected=rej, args=vars(args), seconds=time.time() - t_start),
          open(os.path.join(args.model_out, "video_tracks.json"), "w"), indent=1)
print(f"wrote {args.model_out} ({time.time() - t_start:.0f}s)")
