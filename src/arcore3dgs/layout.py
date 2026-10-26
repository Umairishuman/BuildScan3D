"""Room layout from a metric splat model: walls (any number, any angle), floor, ceiling, corners.

structure.py assumes a box room (the outermost wall on each side of two Manhattan directions). Here:
  1. every --every-th training frame: render the model's depth (1/4 res) and lift the planar regions found by
     plane_seg.py (walls, floor, ceiling, doors, furniture faces) to world points; fit a plane per region
     (kept if the fit is tight: the rendered surface really is flat there).
  2. gravity is +Y (ARCore world): vertical planes become 2D lines in the floor plane, horizontal ones heights.
     Floor / ceiling = lowest / highest strong horizontal cluster.
  3. vertical planes are clustered (angle < --ang deg, offset < --off m) across frames, weighted by area;
     each cluster is refit (robust PCA line on all its points) with its extent along the line and its height.
     A cluster is a WALL if it is tall (>= half the room height) and nothing parallel lies behind it
     (furniture fronts, doors in their frames and pictures sit in front of a wall).
  4. corners = intersections of non-parallel walls whose segments end near each other.
Works for any number of walls and non-Manhattan angles.

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/layout.py --ply <splat.ply> --work <work_sfm> --out <dir>
Outputs: layout.json (floor/ceiling heights, walls with lengths, corners), plan.png (top view), corners.jpg
(corner edges projected into frames).
"""
import os, json, argparse
import numpy as np, cv2, torch, torch.nn.functional as F
from plyfile import PlyData
from gsplat import rasterization

ap = argparse.ArgumentParser()
ap.add_argument("--ply", required=True); ap.add_argument("--work", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--every", type=int, default=6); ap.add_argument("--down", type=int, default=4)
ap.add_argument("--ang", type=float, default=6.0); ap.add_argument("--off", type=float, default=0.08)
ap.add_argument("--min_len", type=float, default=0.5)
ap.add_argument("--max_rms", type=float, default=0.05, help="m: a region is used if the rendered surface fits a plane this well")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
dev = "cuda"; G = np.diag([1, -1, -1, 1.0]); UP = np.array([0.0, 1.0, 0.0])

v = PlyData.read(args.ply)["vertex"]; c = lambda n: torch.tensor(np.asarray(v[n]), dtype=torch.float32, device=dev)
means = torch.stack([c("x"), c("y"), c("z")], 1)
quats = F.normalize(torch.stack([c(f"rot_{i}") for i in range(4)], 1), dim=-1)
scales = torch.exp(torch.stack([c(f"scale_{i}") for i in range(3)], 1)); opac = torch.sigmoid(c("opacity"))
cols = torch.sigmoid(torch.stack([c(f"f_dc_{i}") for i in range(3)], 1) * 0.28209479177387814)  # only geometry matters
meta = json.load(open(os.path.join(args.work, "frames.json"))); d = args.down
W, H = meta["W"] // d, meta["H"] // d
K = np.array([[meta["fx"] / d, 0, meta["cx"] / d], [0, meta["fy"] / d, meta["cy"] / d], [0, 0, 1]])
Kt = torch.tensor(K[None], dtype=torch.float32, device=dev)
vv, uu = np.mgrid[0:H, 0:W]
rays = np.dstack([(uu + 0.5 - K[0, 2]) / K[0, 0], (vv + 0.5 - K[1, 2]) / K[1, 1], np.ones((H, W))])

# ---------------- 1. planar regions -> world planes ----------------
regs = []                                                    # (normal, d, points[<=400], area)
stats_rms = []
frames = meta["frames"][:: args.every]
for f in frames:
    pp = os.path.join(args.work, "planes", f["name"] + ".png")
    pl = cv2.imread(pp, cv2.IMREAD_UNCHANGED) if os.path.exists(pp) else None
    if pl is None or pl.max() == 0:
        continue
    pl = cv2.resize(pl, (W, H), interpolation=cv2.INTER_NEAREST)
    c2w = np.array(f["c2w"]) @ G                             # OpenCV camera -> world
    w2c = torch.tensor(np.linalg.inv(c2w)[None], dtype=torch.float32, device=dev)
    with torch.no_grad():
        out, alpha, _ = rasterization(means, quats, scales, opac, cols, w2c, Kt, W, H, render_mode="RGB+ED")
    D = out[0, ..., 3].cpu().numpy(); A = alpha[0, ..., 0].cpu().numpy()
    Pw = (rays * D[..., None]) @ c2w[:3, :3].T + c2w[:3, 3]
    for k in range(1, int(pl.max()) + 1):
        m = (pl == k) & (A > 0.8)
        if m.sum() < 150:
            continue
        Q = Pw[m]; cen = Q.mean(0); _, sv, Vt = np.linalg.svd(Q - cen, full_matrices=False)
        n = Vt[2]; rms = sv[2] / np.sqrt(len(Q))
        ceiling_like = abs(n @ UP) > 0.95 and cen[1] > c2w[1, 3] + 0.3
        stats_rms.append((rms, ceiling_like))
        if rms > args.max_rms * (2 if ceiling_like else 1):   # the rendered surface is not flat here
            continue
        sel = Q[np.random.default_rng(len(regs)).choice(len(Q), min(400, len(Q)), replace=False)]
        regs.append((n, float(n @ cen), sel, int(m.sum())))
sr = np.array(stats_rms)
print(f"{len(regs)} flat regions of {len(sr)} planar regions from {len(frames)} frames; rendered-plane rms median "
      f"{100 * np.median(sr[:, 0]):.1f} cm (ceiling regions {100 * np.median(sr[sr[:, 1] > 0, 0]) if (sr[:, 1] > 0).any() else float('nan'):.1f} cm)")

# ---------------- 2. floor / ceiling ----------------
hor = [r for r in regs if abs(r[0] @ UP) > 0.95]
ys = np.concatenate([r[2][:, 1] for r in hor]); wts = np.concatenate([np.full(len(r[2]), r[3] / len(r[2])) for r in hor])
hist, edges = np.histogram(ys, bins=np.arange(ys.min() - 0.05, ys.max() + 0.05, 0.02), weights=wts)
peaks = [i for i in range(1, len(hist) - 1) if hist[i] >= hist[i - 1] and hist[i] >= hist[i + 1] and hist[i] > 0.05 * hist.max()]
# the floor is well below every camera, the ceiling above every camera (table tops / counters are in between)
cy_ = np.array([np.array(f["c2w"])[1, 3] for f in meta["frames"]])
# (the ceiling is seen less and at grazing angles: its peak is searched on its own, not relative to the floor's)
def mode_y(sel):
    if sel.sum() < 50:
        return float("nan")
    h_, e_ = np.histogram(ys[sel], bins=np.arange(ys[sel].min() - 0.03, ys[sel].max() + 0.05, 0.02), weights=wts[sel])
    y0 = e_[h_.argmax()] + 0.01
    return float(np.median(ys[sel & (np.abs(ys - y0) < 0.03)]))
floor_y = mode_y(ys < cy_.min() - 0.5); ceil_y = mode_y(ys > cy_.max() + 0.1)
if not np.isfinite(ceil_y):
    print("no ceiling found above the cameras")
height = ceil_y - floor_y
print(f"floor y {floor_y:.3f}, ceiling y {ceil_y:.3f} -> room height {height:.3f} m")

# ---------------- 3. walls ----------------
lines = []                                                   # canonical (theta in [0, pi), rho), points xz, area, y-range
for n, dd, pts, area in regs:
    if abs(n @ UP) > 0.15:
        continue
    n2 = np.array([n[0], n[2]]); n2 /= np.linalg.norm(n2)
    rho = float(n2 @ pts[:, [0, 2]].mean(0)); th = np.arctan2(n2[1], n2[0])
    if th < 0:
        th += np.pi; rho = -rho
    if th >= np.pi:
        th -= np.pi; rho = -rho
    lines.append([th, rho, pts, area])
lines.sort(key=lambda l: -l[3])
clusters = []
for th, rho, pts, area in lines:
    for cl in clusters:
        dth = abs(th - cl["th"]); flip = dth > np.pi / 2
        dth = min(dth, np.pi - dth); r2 = -rho if flip else rho
        if np.degrees(dth) < args.ang and abs(r2 - cl["rho"]) < args.off:
            cl["pts"].append(pts); cl["area"] += area; break
    else:
        clusters.append(dict(th=th, rho=rho, pts=[pts], area=area))
C = np.array([np.array(f["c2w"])[:3, 3] for f in meta["frames"]])
walls = []
for cl in clusters:
    Q = np.concatenate(cl["pts"]); xz = Q[:, [0, 2]]
    for _ in range(3):                                       # robust 2D line fit
        cen = xz.mean(0); _, _, Vt = np.linalg.svd(xz - cen); dirv, nrm = Vt[0], Vt[1]
        r = (xz - cen) @ nrm; keep = np.abs(r) < max(0.03, 2.5 * np.median(np.abs(r)))
        xz_in = xz[keep]
        if len(xz_in) < 50:
            break
        xz = xz_in
    tt = (xz - cen) @ dirv; t0, t1 = np.percentile(tt, [2, 98])
    yr = np.percentile(Q[:, 1], [2, 98])
    side = np.sign((C[:, [0, 2]] - cen) @ nrm)
    if side.mean() < 0:                                      # normal points into the room (towards the cameras)
        nrm = -nrm
    walls.append(dict(cen=cen, dir=dirv, nrm=nrm, t0=t0, t1=t1, y0=yr[0], y1=yr[1], area=cl["area"],
                      cam_side=float(abs(side.mean()))))
def refit(Q):
    xz = Q[:, [0, 2]]
    for _ in range(3):                                       # robust 2D line fit
        cen = xz.mean(0); _, _, Vt = np.linalg.svd(xz - cen); dirv, nrm = Vt[0], Vt[1]
        r = (xz - cen) @ nrm; keep = np.abs(r) < max(0.03, 2.5 * np.median(np.abs(r)))
        if keep.sum() < 50:
            break
        xz = xz[keep]
    tt = (xz - cen) @ dirv; t0, t1 = np.percentile(tt, [2, 98])
    side = np.sign((C[:, [0, 2]] - cen) @ nrm)
    if side.mean() < 0:
        nrm = -nrm
    return cen, dirv, nrm, t0, t1


for w, cl in zip(walls, clusters):
    w["Q"] = np.concatenate(cl["pts"])
# a wall is tall and long
hmin = 0.5 * height if np.isfinite(height) else 1.0
cand = [w for w in walls if w["t1"] - w["t0"] >= args.min_len and (w["y1"] - w["y0"]) >= hmin]
# merge near-duplicates (same wall split by a slight bend in the model): parallel within 8 deg and 0.2 m
merged = True
while merged:
    merged = False
    for i in range(len(cand)):
        for j in range(i + 1, len(cand)):
            a_, b_ = cand[i], cand[j]
            if abs(a_["dir"] @ b_["dir"]) < np.cos(np.radians(8)):
                continue
            if abs((b_["cen"] - a_["cen"]) @ a_["nrm"]) > 0.2:
                continue
            Q = np.concatenate([a_["Q"], b_["Q"]]); cen, dirv, nrm, t0, t1 = refit(Q)
            a_.update(Q=Q, cen=cen, dir=dirv, nrm=nrm, t0=t0, t1=t1, area=a_["area"] + b_["area"],
                      y0=min(a_["y0"], b_["y0"]), y1=max(a_["y1"], b_["y1"]))
            cand.pop(j); merged = True; break
        if merged:
            break
# drop surfaces in front of a wall (furniture fronts, doors, pictures): something parallel lies behind them
inner = []
for w in cand:
    behind = False
    for o in cand:
        if o is w or o["nrm"] @ w["nrm"] < np.cos(np.radians(10)):
            continue
        depth_ = (o["cen"] - w["cen"]) @ (-w["nrm"])             # > 0: o is behind w (further from the room)
        p = [o["cen"] + o["dir"] * o["t0"], o["cen"] + o["dir"] * o["t1"]]
        a_, b_ = sorted([(x - w["cen"]) @ w["dir"] for x in p])
        overlap = max(0.0, min(b_, w["t1"]) - max(a_, w["t0"])) / (w["t1"] - w["t0"])
        if depth_ > 0.05 and overlap > 0.5:
            behind = True; break
    if not behind:
        inner.append(w)
# drop surfaces outside the room (seen through a doorway): beyond a long wall, within its extent
final = []
for w in inner:
    outside = False
    for o in inner:
        if o is w or o["t1"] - o["t0"] < 2.0:
            continue
        mid = w["cen"] + w["dir"] * (w["t0"] + w["t1"]) / 2
        if (mid - o["cen"]) @ o["nrm"] < -0.15 and o["t0"] - 0.3 < (mid - o["cen"]) @ o["dir"] < o["t1"] + 0.3:
            outside = True; break
    if not outside:
        final.append(w)
print(f"{len(clusters)} vertical plane clusters -> {len(walls) and len(cand)} tall + long after merging -> "
      f"{len(inner)} without furniture fronts -> {len(final)} walls")

# ---------------- 4. corners: walls in angular order around the room centre ----------------
ctr = C[:, [0, 2]].mean(0)
def ang_of(w):
    m_ = w["cen"] + w["dir"] * (w["t0"] + w["t1"]) / 2 - ctr
    return np.arctan2(m_[1], m_[0])
order = sorted(final, key=ang_of)
corners = []
for k in range(len(order)):
    a, b = order[k], order[(k + 1) % len(order)]
    if abs(a["dir"] @ b["dir"]) > np.cos(np.radians(30)):   # parallel neighbours (a step in the wall): no corner
        continue
    Am = np.stack([a["dir"], -b["dir"]], 1); s_ = np.linalg.solve(Am, b["cen"] - a["cen"])
    X = a["cen"] + s_[0] * a["dir"]
    ga = max(a["t0"] - s_[0], s_[0] - a["t1"], 0); gb = max(b["t0"] - s_[1], s_[1] - b["t1"], 0)
    if ga > 2.5 or gb > 2.5:                                 # the walls do not meet near here (furniture hides corners)
        continue
    ia, ib = next(i for i, w in enumerate(final) if w is a), next(i for i, w in enumerate(final) if w is b)
    corners.append(dict(xz=X.tolist(), walls=[ia, ib], angle=float(np.degrees(np.arccos(abs(a["dir"] @ b["dir"]))))))
    for w, s in ((a, s_[0]), (b, s_[1])):                    # extend / trim the wall to the corner
        w.setdefault("ends", []).append(s)
for w in final:
    e = sorted(w.get("ends", []))
    if len(e) >= 2:
        w["t0"], w["t1"] = e[0], e[-1]
    elif len(e) == 1:
        if abs(e[0] - w["t0"]) < abs(e[0] - w["t1"]):
            w["t0"] = e[0]
        else:
            w["t1"] = e[0]
# room dimensions wall-to-wall: opposite (anti-parallel) walls, mean separation over their common extent
dims = []
for i in range(len(final)):
    for j in range(i + 1, len(final)):
        a, b = final[i], final[j]
        if a["nrm"] @ b["nrm"] > -np.cos(np.radians(8)):
            continue
        Qb = b["Q"][:, [0, 2]]; sep = float(np.median((Qb - a["cen"]) @ a["nrm"]))
        dims.append(dict(walls=[i, j], distance=abs(sep)))
        print(f"walls {i} <-> {j}: {abs(sep):.3f} m apart")
res = dict(floor_y=floor_y, ceiling_y=ceil_y, height=height, dimensions=dims,
           walls=[dict(id=k, p0=(w["cen"] + w["dir"] * w["t0"]).tolist(), p1=(w["cen"] + w["dir"] * w["t1"]).tolist(),
                       length=float(w["t1"] - w["t0"]), normal=w["nrm"].tolist(), corners=len(w.get("ends", [])))
                  for k, w in enumerate(final)],
           corners=corners)
json.dump(res, open(os.path.join(args.out, "layout.json"), "w"), indent=1)
for k, w in enumerate(res["walls"]):
    print(f"wall {k}: length {w['length']:.3f} m, {w['corners']} corner(s)")
for cn in corners:
    print(f"corner walls {cn['walls']}: angle {cn['angle']:.1f} deg at x={cn['xz'][0]:.3f} z={cn['xz'][1]:.3f}")

# ---------------- plan.png ----------------
P = means.cpu().numpy(); o = opac.cpu().numpy()
m = (o > 0.5) & (P[:, 1] > floor_y + 0.1) & (P[:, 1] < (ceil_y if np.isfinite(ceil_y) else floor_y + 2.4) - 0.1)
xz = P[m][:, [0, 2]]; lo = np.percentile(xz, 0.5, 0) - 0.5; hi = np.percentile(xz, 99.5, 0) + 0.5
sc = 150; Wp, Hp = ((hi - lo) * sc).astype(int)
img = np.full((Hp, Wp, 3), 255, np.uint8)
q = ((xz - lo) * sc).astype(int); q = q[(q[:, 0] >= 0) & (q[:, 0] < Wp) & (q[:, 1] >= 0) & (q[:, 1] < Hp)]
cnt = np.zeros((Hp, Wp)); np.add.at(cnt, (q[:, 1], q[:, 0]), 1)
img[cnt > 0] = (np.clip(200 - 25 * np.log1p(cnt[cnt > 0])[:, None], 60, 200)).astype(np.uint8)
pt_ = lambda p: tuple(int(x) for x in ((np.array(p) - lo) * sc))
cp = ((C[:, [0, 2]] - lo) * sc).astype(int)
for a_, b_ in zip(cp[:-1], cp[1:]):
    cv2.line(img, tuple(a_), tuple(b_), (230, 180, 120), 1)
for w in res["walls"]:
    cv2.line(img, pt_(w["p0"]), pt_(w["p1"]), (40, 160, 40), 3)
    mid = (np.array(w["p0"]) + np.array(w["p1"])) / 2
    cv2.putText(img, f"{w['length']:.2f} m", pt_(mid), 0, 0.6, (0, 90, 0), 2)
for cn in corners:
    cv2.circle(img, pt_(cn["xz"]), 7, (0, 0, 220), -1)
cv2.putText(img, f"height {height:.2f} m, {len(final)} walls, {len(corners)} corners", (10, 25), 0, 0.7, (0, 0, 0), 2)
cv2.imwrite(os.path.join(args.out, "plan.png"), img)

# ---------------- corners.jpg: vertical corner edges in a few frames ----------------
tiles = []
for f in meta["frames"][:: max(1, len(meta["frames"]) // 60)]:
    c2w = np.array(f["c2w"]) @ G; w2c = np.linalg.inv(c2w)
    vis = []
    for cn in corners:
        seg = []
        for y in np.linspace(floor_y, ceil_y if np.isfinite(ceil_y) else floor_y + 2.4, 20):
            X = w2c @ np.array([cn["xz"][0], y, cn["xz"][1], 1.0])
            if X[2] > 0.2:
                u_, v_ = K[0, 0] * d * X[0] / X[2] + K[0, 2] * d, K[1, 1] * d * X[1] / X[2] + K[1, 2] * d
                if 0 <= u_ < meta["W"] and 0 <= v_ < meta["H"]:
                    seg.append((int(u_), int(v_)))
        if len(seg) > 5:
            vis.append(seg)
    if vis:
        im = cv2.imread(os.path.join(args.work, "images", f["name"] + ".jpg"))
        for seg in vis:
            for a_, b_ in zip(seg[:-1], seg[1:]):
                cv2.line(im, a_, b_, (0, 0, 255), 4)
        tiles.append(cv2.resize(im, (640, 360)))
    if len(tiles) == 6:
        break
if tiles:
    cv2.imwrite(os.path.join(args.out, "corners.jpg"), np.vstack([np.hstack(tiles[i:i + 2]) for i in range(0, len(tiles) - 1, 2)]))
print("->", args.out)
