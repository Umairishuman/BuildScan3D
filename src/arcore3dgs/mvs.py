"""Stage 1c: multi-view stereo depth (PocketGS-style plane sweep, guided by Metric3D).

Monocular depth is a per-image guess; MVS measures depth by triangulating pixels across real
camera baselines, so it is metric (via the BA-refined ARCore poses) and consistent across views.

Per reference keyframe (half resolution, same as training):
  * sources: the 5 keyframes sharing most BA points with a useful baseline/depth ratio
  * hypotheses: per-pixel, 64 log-spaced depths in [0.65, 1.55] x the Metric3D depth (scaled to the
    BA points) -> fine sampling where it matters, robust prior in low texture
  * cost: 1 - NCC over 7x7 windows, mean of the best 3 of 5 sources (occlusion robust),
    sub-plane parabola refinement
  * filters: NCC confidence + cost-curve distinctiveness, then a geometric consistency check
    (forward-backward reprojection < 1 px and < 1% depth error in >= 2 sources)
  * output depth_mvs/: confirmed MVS depth; elsewhere Metric3D re-scaled to the confirmed MVS
    depth of that frame. mvs_mask/ marks which pixels are measured (not predicted).
Run with nerfstudio-env python.
"""
import os, json, time, argparse
import numpy as np, cv2, torch, torch.nn.functional as F

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--n_src", type=int, default=5)
ap.add_argument("--n_planes", type=int, default=64)
ap.add_argument("--range_lo", type=float, default=0.65)
ap.add_argument("--range_hi", type=float, default=1.55)
ap.add_argument("--win", type=int, default=7)
ap.add_argument("--min_ncc", type=float, default=0.5)
ap.add_argument("--skip_sweep", action="store_true", help="reuse depth_mvs_raw/ from a previous run")
ap.add_argument("--arcore_depth", type=int, default=-1, help="anchor the Metric3D fill to ARCore raw depth: 1 on, 0 off, -1 auto (on if <dataset>/depth/ exists)")
ap.add_argument("--arcore_conf", type=int, default=128, help="min ARCore depth confidence (0-255)")
ap.add_argument("--arcore_weight", type=float, default=0.3, help="weight of ARCore anchors vs MVS pixels in the correction fit")
args = ap.parse_args()
dev = torch.device("cuda")
t0 = time.time()

meta = json.load(open(os.path.join(args.work, "frames.json")))
frames = meta["frames"]
N = len(frames)
s = meta["depth_scale"]
W, H = int(meta["W"] * s), int(meta["H"] * s)
K = torch.tensor([[meta["fx"] * s, 0, meta["cx"] * s], [0, meta["fy"] * s, meta["cy"] * s], [0, 0, 1]], device=dev)
Kinv = torch.linalg.inv(K)
GL_TO_CV = torch.diag(torch.tensor([1.0, -1.0, -1.0], device=dev))
Rc2w = torch.stack([torch.tensor(f["c2w"], dtype=torch.float32, device=dev)[:3, :3] @ GL_TO_CV for f in frames])
Cw = torch.stack([torch.tensor(f["c2w"], dtype=torch.float32, device=dev)[:3, 3] for f in frames])
for d in ("depth_mvs_raw", "depth_mvs", "mvs_mask"):
    os.makedirs(os.path.join(args.work, d), exist_ok=True)

sp = np.load(os.path.join(args.work, "sparse.npz"))
Xs, s_cam, s_pt = sp["X"], sp["cam"], sp["pt"]

# ---------- source selection from BA covisibility ----------
pts_of = [set(s_pt[s_cam == i].tolist()) for i in range(N)]
Xs_t = torch.tensor(Xs, dtype=torch.float32, device=dev)


def cam_depths(i, idx):
    pc = (Xs_t[idx] - Cw[i]) @ Rc2w[i]
    return pc[:, 2]


from scipy.sparse import coo_matrix
Mv = coo_matrix((np.ones(len(s_cam)), (s_cam, s_pt)), shape=(N, len(Xs))).tocsr()
Mv.data[:] = 1
covis = (Mv @ Mv.T).toarray()
np.fill_diagonal(covis, 0)
med_depth = np.array([float(cam_depths(i, torch.tensor(sorted(pts_of[i]), device=dev, dtype=torch.long)).median())
                      if len(pts_of[i]) else 1.5 for i in range(N)])
Cn = Cw.cpu().numpy()
sources = []
for i in range(N):
    cand = []
    for j in np.where(covis[i] >= 30)[0]:
        ratio = np.linalg.norm(Cn[i] - Cn[j]) / max(med_depth[i], 1e-3)
        if ratio < 0.03:            # too little baseline to triangulate
            continue
        score = covis[i, j] * min(1.0, ratio / 0.1) * (1.0 if ratio < 0.5 else 0.5)
        cand.append((score, int(j)))
    cand.sort(reverse=True)
    sources.append([j for _, j in cand[:args.n_src]])
print(f"source views: median {np.median([len(x) for x in sources]):.0f} per frame "
      f"({sum(len(x) == 0 for x in sources)} frames without any) [{time.time() - t0:.0f}s]")


def load_gray(i):
    im = cv2.imread(os.path.join(args.work, "images", frames[i]["name"] + ".jpg"), cv2.IMREAD_GRAYSCALE)
    im = cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    return torch.from_numpy(im).to(dev)[None, None]


def load_mono(i):
    return torch.from_numpy(np.load(os.path.join(args.work, "depth_m3d", frames[i]["name"] + ".npy")).astype(np.float32)).to(dev)


uu, vv = torch.meshgrid(torch.arange(W, device=dev, dtype=torch.float32) + 0.5,
                        torch.arange(H, device=dev, dtype=torch.float32) + 0.5, indexing="xy")
pix = torch.stack([uu, vv, torch.ones_like(uu)], 0).reshape(3, -1)       # 3 x HW
rays = Kinv @ pix
pool = lambda x: F.avg_pool2d(x, args.win, 1, args.win // 2, count_include_pad=False)


def mono_prior(i):
    """Metric3D depth scaled to BA points seen by frame i."""
    dm = load_mono(i)
    idx = torch.tensor(sorted(pts_of[i]), device=dev, dtype=torch.long)
    if len(idx) < 20:
        return dm
    pc = (Xs_t[idx] - Cw[i]) @ Rc2w[i]
    z = pc[:, 2]
    u = (K[0, 0] * pc[:, 0] / z + K[0, 2]).long(); v = (K[1, 1] * pc[:, 1] / z + K[1, 2]).long()
    ok = (z > 0.1) & (u >= 0) & (u < W) & (v >= 0) & (v < H)
    r = z[ok] / dm[v[ok], u[ok]].clamp_min(1e-3)
    return dm * r.median()


# ---------- pass 1: plane sweep ----------
factors = torch.exp(torch.linspace(np.log(args.range_lo), np.log(args.range_hi), args.n_planes, device=dev))
step = float(np.log(args.range_hi / args.range_lo) / (args.n_planes - 1))
priors = {}
for i in range(N):
    if not sources[i]:
        continue
    if args.skip_sweep:
        priors[i] = mono_prior(i)
        continue
    ref = load_gray(i)
    mu_r = pool(ref); var_r = (pool(ref * ref) - mu_r ** 2).clamp_min(1e-6)
    prior = mono_prior(i)
    priors[i] = prior
    srcs = [(load_gray(j), j) for j in sources[i]]
    # per source: p_s = d * A @ rays + b
    AB = []
    for _, j in srcs:
        A = K @ Rc2w[j].T @ Rc2w[i]
        b = K @ Rc2w[j].T @ (Cw[i] - Cw[j])
        AB.append((A @ rays, b[:, None]))
    cost = torch.empty(args.n_planes, H, W, device=dev, dtype=torch.float16)
    with torch.no_grad():
        for k in range(args.n_planes):
            d = (prior * factors[k]).reshape(1, -1)
            cs = []
            for (img, _), (Ar, b) in zip(srcs, AB):
                p = Ar * d + b
                z = p[2]
                gx = (p[0] / z.clamp_min(1e-6)) / W * 2 - 1
                gy = (p[1] / z.clamp_min(1e-6)) / H * 2 - 1
                grid = torch.stack([gx, gy], -1).reshape(1, H, W, 2)
                warped = F.grid_sample(img, grid, mode="bilinear", padding_mode="zeros", align_corners=False)
                mu_w = pool(warped); var_w = (pool(warped * warped) - mu_w ** 2).clamp_min(1e-6)
                ncc = (pool(ref * warped) - mu_r * mu_w) / torch.sqrt(var_r * var_w)
                c = (1 - ncc[0, 0]).clamp(0, 2)
                bad = (z.reshape(H, W) <= 0) | (gx.abs().reshape(H, W) > 1) | (gy.abs().reshape(H, W) > 1)
                cs.append(torch.where(bad, torch.full_like(c, 2.0), c))
            cs = torch.stack(cs).sort(dim=0).values
            cost[k] = cs[:min(3, len(cs))].mean(0).half()
        cost = cost.float()
        best_c, best_k = cost.min(0)
        k0 = best_k.clamp(1, args.n_planes - 2)
        cm = cost.gather(0, (k0 - 1)[None])[0]; c0 = cost.gather(0, k0[None])[0]; cp = cost.gather(0, (k0 + 1)[None])[0]
        denom = (cm - 2 * c0 + cp)
        off = torch.where(denom > 1e-4, 0.5 * (cm - cp) / denom, torch.zeros_like(denom)).clamp(-0.5, 0.5)
        logf = torch.log(factors[0]) + (k0.float() + off) * step
        depth = prior * torch.exp(logf)
        distinct = cost.mean(0) - best_c
        textured = var_r[0, 0].sqrt() > 0.02
        conf = ((1 - best_c) > args.min_ncc) & (distinct > 0.15) & textured & (best_k > 0) & (best_k < args.n_planes - 1)
    np.save(os.path.join(args.work, "depth_mvs_raw", frames[i]["name"] + ".npy"),
            torch.where(conf, depth, torch.zeros_like(depth)).cpu().numpy().astype(np.float32))
    if (i + 1) % 50 == 0:
        print(f"  plane sweep {i + 1}/{N}  (confident {conf.float().mean() * 100:.0f}% of pixels) [{time.time() - t0:.0f}s]", flush=True)

# ---------- optional: ARCore raw depth anchors ----------
arcore = None
if args.arcore_depth == -1:
    args.arcore_depth = int(os.path.isdir(os.path.join(meta["dataset"], "depth")))
if args.arcore_depth:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from common import Capture
    ddir = os.path.join(meta["dataset"], "depth")
    cap = Capture(meta["dataset"], pose_offset=meta.get("pose_offset", 0.0))
    dW, dH = map(int, open(os.path.join(ddir, "size.txt")).read().split())
    d_ts = np.array(sorted(int(f[:-6]) for f in os.listdir(ddir) if f.endswith(".depth")), dtype=np.int64)
    sd = dW / meta["W"]
    Kd_inv = np.linalg.inv(np.array([[meta["fx"] * sd, 0, meta["cx"] * sd], [0, meta["fy"] * sd, meta["cy"] * sd], [0, 0, 1]]))
    dv, du = np.mgrid[0:dH, 0:dW]
    d_rays = Kd_inv @ np.stack([du.ravel() + 0.5, dv.ravel() + 0.5, np.ones(du.size)])
    G3 = np.diag([1.0, -1.0, -1.0])
    print(f"ARCore depth: {len(d_ts)} maps at {dW}x{dH}, confidence >= {args.arcore_conf}")

    def arcore(i):
        """ARCore depth nearest in time to keyframe i, re-projected into its (half-res) image.
        Uses ARCore poses for the short relative motion between depth and keyframe timestamps."""
        t_ns = cap.t0_ns + (frames[i]["pts"] + meta.get("pose_offset", 0.0)) * 1e9
        k = int(np.argmin(np.abs(d_ts - t_ns)))
        if abs(d_ts[k] - t_ns) > 0.15e9:
            return None
        c2w_d = cap.pose_at((d_ts[k] - cap.t0_ns) / 1e9)
        if c2w_d is None:
            return None
        d = np.fromfile(os.path.join(ddir, f"{d_ts[k]}.depth"), dtype="<u2").reshape(-1) / 1000.0
        c = np.fromfile(os.path.join(ddir, f"{d_ts[k]}.conf"), dtype=np.uint8).reshape(-1)
        ok = (d > 0.1) & (c >= args.arcore_conf)
        if ok.sum() < 50:
            return None
        Xc = d_rays[:, ok] * d[ok]                                         # depth camera, OpenCV
        Xw = c2w_d[:3, :3] @ G3 @ Xc + c2w_d[:3, 3:4]
        c2w_k = np.array(frames[i].get("c2w_arcore", frames[i]["c2w"]))
        Xk = G3 @ c2w_k[:3, :3].T @ (Xw - c2w_k[:3, 3:4])                  # keyframe camera, OpenCV
        z = Xk[2]
        Kn = K.cpu().numpy()
        u = (Kn[0, 0] * Xk[0] / z + Kn[0, 2]).astype(int); v = (Kn[1, 1] * Xk[1] / z + Kn[1, 2]).astype(int)
        m = (z > 0.1) & (u >= 0) & (u < W) & (v >= 0) & (v < H)
        return (torch.tensor(u[m], device=dev), torch.tensor(v[m], device=dev),
                torch.tensor(z[m], dtype=torch.float32, device=dev))

# ---------- pass 2: geometric consistency + fill ----------
print("geometric consistency check + fill")
def raw(i):
    f = os.path.join(args.work, "depth_mvs_raw", frames[i]["name"] + ".npy")      # frames without sources have no raw depth
    return torch.from_numpy(np.load(f)).to(dev) if os.path.exists(f) else torch.zeros(H, W, device=dev)
kept_frac, mono_err, ar_vs_mvs, n_ar = [], [], [], 0
for i in range(N):
    name = frames[i]["name"]
    # frames without MVS sources still get the BA-point scale (previously raw Metric3D -> ghost geometry)
    prior = priors[i] if i in priors else mono_prior(i)
    anc = arcore(i) if arcore is not None else None
    if not sources[i]:
        dr = torch.zeros(H, W, device=dev)
        valid = dr > 0
    else:
        dr = raw(i)
        valid = dr > 0
    X = Cw[i][:, None] + Rc2w[i] @ (rays * dr.reshape(1, -1))                 # 3 x HW world points
    votes = torch.zeros(H * W, device=dev)
    for j in sources[i] if valid.any() else []:
        dj = raw(j)
        pc = Rc2w[j].T @ (X - Cw[j][:, None])
        z = pc[2]
        us = K[0, 0] * pc[0] / z + K[0, 2]; vs = K[1, 1] * pc[1] / z + K[1, 2]
        inb = (z > 0) & (us >= 0) & (us < W - 1) & (vs >= 0) & (vs < H - 1)
        ui, vi = us.long().clamp(0, W - 1), vs.long().clamp(0, H - 1)
        dj_s = dj[vi, ui]
        Xb = Cw[j][:, None] + Rc2w[j] @ (Kinv @ torch.stack([us, vs, torch.ones_like(us)]) * dj_s)
        pr = Rc2w[i].T @ (Xb - Cw[i][:, None])
        ur = K[0, 0] * pr[0] / pr[2] + K[0, 2]; vr = K[1, 1] * pr[1] / pr[2] + K[1, 2]
        reproj = torch.hypot(ur - pix[0], vr - pix[1])
        drel = (pr[2] - dr.reshape(-1)).abs() / dr.reshape(-1).clamp_min(1e-3)
        votes += (inb & (dj_s > 0) & (reproj < 1.0) & (drel < 0.01)).float()
    keep = valid & (votes.reshape(H, W) >= 2)
    out = prior.clone()
    # anchors for the smooth correction field: MVS pixels (weight 1) + ARCore depth (weight arcore_weight)
    au, av, az, aw = [], [], [], []
    if keep.sum() > 0:
        vk, uk = torch.nonzero(keep, as_tuple=True)
        au.append(uk); av.append(vk); az.append(dr[keep]); aw.append(torch.ones(len(uk), device=dev))
    if anc is not None:
        n_ar += 1
        u_a, v_a, z_a = anc
        both = keep[v_a, u_a]
        if both.sum() > 50:
            ar_vs_mvs.append(float(((z_a[both] - dr[v_a[both], u_a[both]]).abs() / dr[v_a[both], u_a[both]]).median()))
        free = ~both
        au.append(u_a[free]); av.append(v_a[free]); az.append(z_a[free])
        aw.append(torch.full((int(free.sum()),), args.arcore_weight, device=dev))
    n_anchor = sum(len(x) for x in au)
    if keep.sum() > 500 or n_anchor > 300:
        # smooth correction field: log(anchor/mono) ~ quadratic in (u, v). Fixes Metric3D's scale AND its
        # low-frequency tilt/bending, not just one global factor. Robust: refit after trimming outliers.
        u_all, v_all, z_all, w_all = torch.cat(au), torch.cat(av), torch.cat(az), torch.cat(aw).sqrt()
        un, vn = u_all.float() / W - 0.5, v_all.float() / H - 0.5
        basis = lambda a, b: torch.stack([torch.ones_like(a), a, b, a ** 2, b ** 2, a * b], 1)
        y = torch.log(z_all / prior[v_all, u_all].clamp_min(1e-3))
        A = basis(un, vn)
        sel = torch.ones_like(y, dtype=torch.bool)
        for _ in range(3):
            coef = torch.linalg.lstsq(A[sel] * w_all[sel, None], (y[sel] * w_all[sel])[:, None]).solution
            res_ = (A @ coef)[:, 0] - y
            sel = res_.abs() < 3 * res_[sel].abs().median().clamp_min(1e-3)
        gu, gv = pix[0].reshape(H, W) / W - 0.5, pix[1].reshape(H, W) / H - 0.5
        out = prior * torch.exp((basis(gu.reshape(-1), gv.reshape(-1)) @ coef)[:, 0].reshape(H, W))
        if keep.sum() > 500:
            mono_err.append(float(((out[keep] - dr[keep]).abs() / dr[keep]).median()))
        out[keep] = dr[keep]
    kept_frac.append(float(keep.float().mean()))
    np.save(os.path.join(args.work, "depth_mvs", name + ".npy"), out.cpu().numpy().astype(np.float16))
    np.save(os.path.join(args.work, "mvs_mask", name + ".npy"), keep.cpu().numpy())

print(f"MVS-measured pixels per frame: median {np.median(kept_frac) * 100:.0f}% (p10 {np.percentile(kept_frac, 10) * 100:.0f}%, "
      f"p90 {np.percentile(kept_frac, 90) * 100:.0f}%)")
print(f"Metric3D vs MVS (after smooth per-frame correction), median rel. error on measured pixels: {np.median(mono_err) * 100:.1f}%")
if arcore is not None:
    print(f"ARCore depth anchors used in {n_ar}/{N} frames; ARCore vs MVS on shared pixels: median rel. error "
          f"{np.median(ar_vs_mvs) * 100:.1f}% ({len(ar_vs_mvs)} frames)" if ar_vs_mvs else f"ARCore depth anchors used in {n_ar}/{N} frames")
print(f"Done in {time.time() - t0:.0f}s -> depth_mvs/, mvs_mask/")
