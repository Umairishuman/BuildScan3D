"""Stage 1b: bundle adjustment of ARCore keyframe poses (PocketGS-style "VIO poses -> global BA").

ARCore poses are good locally but carry mm-cm errors and slow drift, which blurs 3DGS texture.
  1. SIFT features on every keyframe (full res, CLAHE so plain walls still yield features)
  2. Pairs: temporal neighbours + spatially close / similar-view pairs (catches loop revisits)
  3. GPU mutual-NN + ratio matching, fundamental-matrix RANSAC, and a check against the ARCore
     epipolar geometry (rejects repeated-texture mismatches)
  4. Tracks (union-find), multi-view DLT triangulation with ARCore poses, outlier filtering
  5. Sparse Levenberg-Marquardt (scipy, analytic-by-autodiff Jacobian on GPU) over all camera
     poses + points. ARCore enters as priors: tight on frame-to-frame relative motion (keeps metric
     scale, VIO is locally excellent), weak on absolute pose (fixes the gauge, allows drift fixes).

Writes refined poses into frames.json ("c2w"; originals kept as "c2w_arcore") and the sparse
points to sparse.npz. Run with nerfstudio-env python.
"""
import os, sys, json, time, argparse
import numpy as np, cv2, torch
from scipy.optimize import least_squares
from scipy.sparse import coo_matrix
from scipy.spatial.transform import Rotation as Rot

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--n_features", type=int, default=6000)
ap.add_argument("--seq_window", type=int, default=5)
ap.add_argument("--loop_k", type=int, default=5)
ap.add_argument("--max_points", type=int, default=120000)
ap.add_argument("--sigma_rel_t", type=float, default=0.005, help="m, frame-to-frame ARCore translation prior")
ap.add_argument("--sigma_rel_r", type=float, default=0.3, help="deg, frame-to-frame ARCore rotation prior")
ap.add_argument("--sigma_abs_t", type=float, default=0.5)
ap.add_argument("--sigma_abs_r", type=float, default=5.0)
ap.add_argument("--verbose", action="store_true")
args = ap.parse_args()
dev = torch.device("cuda")
t_start = time.time()

meta = json.load(open(os.path.join(args.work, "frames.json")))
frames = meta["frames"]
N = len(frames)
K = np.array([[meta["fx"], 0, meta["cx"]], [0, meta["fy"], meta["cy"]], [0, 0, 1]])
GL_TO_CV = np.diag([1.0, -1.0, -1.0])
c2w_key = "c2w_arcore" if "c2w_arcore" in frames[0] else "c2w"     # always start from raw ARCore
R0 = np.stack([np.array(f[c2w_key])[:3, :3] @ GL_TO_CV for f in frames])   # c2w rotation, OpenCV cam
C0 = np.stack([np.array(f[c2w_key])[:3, 3] for f in frames])                # camera centres

cache = os.path.join(args.work, "ba_tracks.npz")
if os.path.exists(cache):
    c = np.load(cache)
    X, obs_cam, obs_pt, obs_uv, err_before = c["X"], c["cam"], c["pt"], c["uv"], c["err_before"]
    print(f"loaded cached tracks: {len(X)} points, {len(obs_cam)} observations, "
          f"raw ARCore reprojection median {np.median(err_before):.2f}px")
else:
    # ---------------- 1. features ----------------
    print("1/5 SIFT features")
    sift = cv2.SIFT_create(nfeatures=args.n_features, contrastThreshold=0.02)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    kps, descs = [], []
    for i, f in enumerate(frames):
        g = clahe.apply(cv2.imread(os.path.join(args.work, "images", f["name"] + ".jpg"), cv2.IMREAD_GRAYSCALE))
        kp, d = sift.detectAndCompute(g, None)
        d = np.sqrt(d / (d.sum(1, keepdims=True) + 1e-7))               # RootSIFT
        kps.append(np.array([k.pt for k in kp], np.float32))
        descs.append(d.astype(np.float16))
    print(f"   median {np.median([len(k) for k in kps]):.0f} features/frame ({time.time() - t_start:.0f}s)")

    # ---------------- 2. pairs ----------------
    fwd = R0[:, :, 2]                                                    # viewing direction (OpenCV +z)
    pairs = set()
    for i in range(N):
        for j in range(i + 1, min(i + 1 + args.seq_window, N)):
            pairs.add((i, j))
    dist = np.linalg.norm(C0[:, None] - C0[None], axis=2)
    cosang = fwd @ fwd.T
    for i in range(N):
        cand = np.where((np.abs(np.arange(N) - i) > args.seq_window) & (dist[i] < 1.0) & (cosang[i] > np.cos(np.radians(35))))[0]
        for j in cand[np.argsort(dist[i, cand])][:args.loop_k]:
            pairs.add((min(i, j), max(i, j)))
    pairs = sorted(pairs)
    print(f"2/5 {len(pairs)} candidate pairs")


    # ---------------- 3. matching ----------------
    def skew(v):
        return np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


    def F_from_prior(i, j):
        # x_j^T F x_i = 0 with ARCore poses; w2c: x = R^T (X - C)
        Rij = R0[j].T @ R0[i]
        tij = R0[j].T @ (C0[i] - C0[j])
        E = skew(tij) @ Rij
        Kinv = np.linalg.inv(K)
        return Kinv.T @ E @ Kinv


    def sampson(F, a, b):
        ah = np.c_[a, np.ones(len(a))]; bh = np.c_[b, np.ones(len(b))]
        Fa = ah @ F.T; Ftb = bh @ F
        num = np.sum(bh * Fa, 1) ** 2
        return np.sqrt(num / (Fa[:, 0] ** 2 + Fa[:, 1] ** 2 + Ftb[:, 0] ** 2 + Ftb[:, 1] ** 2 + 1e-12))


    print("3/5 matching")
    matches = {}
    gpu_desc = {}
    def gd(i):
        if i not in gpu_desc:
            if len(gpu_desc) > 64:
                gpu_desc.pop(next(iter(gpu_desc)))
            gpu_desc[i] = torch.from_numpy(descs[i].astype(np.float32)).to(dev)
        return gpu_desc[i]

    n_rej_prior = 0
    for (i, j) in pairs:
        if len(kps[i]) < 50 or len(kps[j]) < 50:
            continue
        d = torch.cdist(gd(i), gd(j))
        v, idx = d.topk(2, dim=1, largest=False)
        nn12 = idx[:, 0]
        nn21 = d.argmin(dim=0)
        ok = (v[:, 0] < 0.85 * v[:, 1]) & (nn21[nn12] == torch.arange(len(nn12), device=dev))
        a = torch.nonzero(ok).squeeze(1).cpu().numpy(); b = nn12[ok].cpu().numpy()
        if len(a) < 30:
            continue
        pa, pb = kps[i][a], kps[j][b]
        Fm, inl = cv2.findFundamentalMat(pa, pb, cv2.USAC_MAGSAC, 1.5, 0.999, 10000)
        if Fm is None or inl is None or inl.sum() < 30:
            continue
        inl = inl.ravel().astype(bool)
        # consistency with ARCore geometry: true matches sit within a few px of the prior epipolar lines
        sd = sampson(F_from_prior(i, j), pa[inl], pb[inl])
        if np.median(sd) > 6.0:
            n_rej_prior += 1
            continue
        keep = np.zeros(len(a), bool); keep[np.where(inl)[0][sd < 15.0]] = True
        if keep.sum() >= 30:
            matches[(i, j)] = np.stack([a[keep], b[keep]], 1)
    del gpu_desc
    print(f"   {len(matches)} verified pairs, {sum(len(m) for m in matches.values())} matches, "
          f"{n_rej_prior} pairs rejected as inconsistent with ARCore ({time.time() - t_start:.0f}s)")

    # ---------------- 4. tracks + triangulation ----------------
    print("4/5 tracks + triangulation")
    offs = np.cumsum([0] + [len(k) for k in kps])
    parent = np.arange(offs[-1])
    def find(x):
        r = x
        while parent[r] != r:
            r = parent[r]
        while parent[x] != r:
            parent[x], x = r, parent[x]
        return r
    for (i, j), m in matches.items():
        for a, b in zip(offs[i] + m[:, 0], offs[j] + m[:, 1]):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
    used = np.zeros(offs[-1], bool)
    for (i, j), m in matches.items():
        used[offs[i] + m[:, 0]] = True; used[offs[j] + m[:, 1]] = True
    nodes = np.where(used)[0]
    roots = np.array([find(x) for x in nodes])
    img_of = np.searchsorted(offs, nodes, side="right") - 1
    order = np.argsort(roots, kind="stable")
    roots, nodes, img_of = roots[order], nodes[order], img_of[order]
    splits = np.flatnonzero(np.diff(roots)) + 1
    tracks = []
    for grp_n, grp_i in zip(np.split(nodes, splits), np.split(img_of, splits)):
        if len(grp_n) < 2 or len(np.unique(grp_i)) != len(grp_i):     # drop short / self-inconsistent
            continue
        tracks.append((grp_i, grp_n - offs[grp_i]))
    tracks.sort(key=lambda t: -len(t[0]))
    tracks = tracks[:args.max_points]
    print(f"   {len(tracks)} tracks, median length {np.median([len(t[0]) for t in tracks]):.0f}")

    Pmats = np.stack([K @ np.c_[R0[i].T, -R0[i].T @ C0[i]] for i in range(N)])
    MAXL = 12
    X = np.zeros((len(tracks), 3))
    for s in range(0, len(tracks), 20000):
        chunk = tracks[s:s + 20000]
        A = np.zeros((len(chunk), 2 * MAXL, 4))
        for t, (ims, ki) in enumerate(chunk):
            sel = np.linspace(0, len(ims) - 1, min(len(ims), MAXL)).astype(int)
            for r, q in enumerate(sel):
                P = Pmats[ims[q]]; u, v = kps[ims[q]][ki[q]]
                A[t, 2 * r] = u * P[2] - P[0]; A[t, 2 * r + 1] = v * P[2] - P[1]
        _, _, Vt = np.linalg.svd(A)
        Xh = Vt[:, -1]
        X[s:s + len(chunk)] = Xh[:, :3] / Xh[:, 3:4]

    obs_cam, obs_pt, obs_uv = [], [], []
    for t, (ims, ki) in enumerate(tracks):
        obs_cam.append(ims); obs_pt.append(np.full(len(ims), t)); obs_uv.append(np.stack([kps[c][k] for c, k in zip(ims, ki)]))
    obs_cam = np.concatenate(obs_cam); obs_pt = np.concatenate(obs_pt); obs_uv = np.concatenate(obs_uv).astype(np.float64)


    def project_np(Rc2w, C, Xw, cam, pt):
        xc = np.einsum("nji,nj->ni", Rc2w[cam], Xw[pt] - C[cam])
        z = xc[:, 2]
        return np.stack([K[0, 0] * xc[:, 0] / z + K[0, 2], K[1, 1] * xc[:, 1] / z + K[1, 2]], 1), z


    uv_p, z = project_np(R0, C0, X, obs_cam, obs_pt)
    err0 = np.linalg.norm(uv_p - obs_uv, axis=1)
    good = (err0 < 8.0) & (z > 0.05)
    # keep points with >= 2 good observations
    cnt = np.bincount(obs_pt[good], minlength=len(tracks))
    good &= cnt[obs_pt] >= 2
    keep_pts = np.where(cnt >= 2)[0]
    remap = -np.ones(len(tracks), int); remap[keep_pts] = np.arange(len(keep_pts))
    obs_cam, obs_pt, obs_uv = obs_cam[good], remap[obs_pt[good]], obs_uv[good]
    X = X[keep_pts]
    uv_p, _ = project_np(R0, C0, X, obs_cam, obs_pt)
    err_before = np.linalg.norm(uv_p - obs_uv, axis=1)
    print(f"   {len(X)} points, {len(obs_cam)} observations; reprojection error with raw ARCore poses: "
          f"median {np.median(err_before):.2f}px, p90 {np.percentile(err_before, 90):.2f}px ({time.time() - t_start:.0f}s)")

    np.savez(cache, X=X, cam=obs_cam, pt=obs_pt, uv=obs_uv, err_before=err_before)

# ---------------- 5. bundle adjustment ----------------
print("5/5 bundle adjustment")
Kt = torch.tensor(K, dtype=torch.float64, device=dev)


def so3_exp(w):
    th2 = (w * w).sum(-1, keepdim=True)[..., None]
    th = th2.clamp_min(1e-24).sqrt()      # clamp: d sqrt/dx is infinite at 0 -> NaN Jacobians at identity
    small = th < 1e-4
    A = torch.where(small, 1 - th2 / 6, torch.sin(th) / th.clamp_min(1e-12))
    B = torch.where(small, 0.5 - th2 / 24, (1 - torch.cos(th)) / th2.clamp_min(1e-24))
    z = torch.zeros_like(w[..., 0])
    W = torch.stack([torch.stack([z, -w[..., 2], w[..., 1]], -1),
                     torch.stack([w[..., 2], z, -w[..., 0]], -1),
                     torch.stack([-w[..., 1], w[..., 0], z], -1)], -2)
    I = torch.eye(3, dtype=w.dtype, device=w.device)
    return I + A * W + B * (W @ W)


R0t = torch.tensor(R0, device=dev); C0t = torch.tensor(C0, device=dev)


def proj_one(cam6, X3, R0c, C0c):
    Rc2w = so3_exp(cam6[:3]) @ R0c
    xc = Rc2w.T @ (X3 - (C0c + cam6[3:]))
    return torch.stack([Kt[0, 0] * xc[0] / xc[2] + Kt[0, 2], Kt[1, 1] * xc[1] / xc[2] + Kt[1, 2]])


jac_fn = torch.func.vmap(torch.func.jacrev(proj_one, argnums=(0, 1)))
proj_v = torch.func.vmap(proj_one)
n_cam_p = 6 * N
s_rt, s_rr = args.sigma_rel_t, np.radians(args.sigma_rel_r)
s_at, s_ar = args.sigma_abs_t, np.radians(args.sigma_abs_r)
# ARCore relative motion between consecutive keyframes (world frame)
dC0 = C0[1:] - C0[:-1]
dR0 = np.einsum("nij,nkj->nik", R0[1:], R0[:-1])                  # R_{k+1} R_k^T
# No relative-motion prior across an ARCore tracking loss (or a long time gap): after relocalisation the
# ARCore world frame can jump, and forcing that "motion" would bake the jump into the poses. Segments are
# then tied together only by feature matches (+ the weak absolute prior).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Capture
_cap = Capture(meta["dataset"], pose_offset=meta.get("pose_offset", 0.0))
_pt = np.array([f["pts"] for f in frames]) + meta.get("pose_offset", 0.0)
rel_w = np.array([0.0 if (_cap.loss_between(_pt[k], _pt[k + 1]) or _pt[k + 1] - _pt[k] > 2.0) else 1.0
                  for k in range(N - 1)])
print(f"   relative-motion prior broken at {int((rel_w == 0).sum())} tracking gaps")
rw3 = np.repeat(rel_w, 3)
HUBER = 2.0                                                       # px

# Prior Jacobian is constant (linearised): relative t/r between consecutive frames + absolute t/r.
k = np.repeat(np.arange(N - 1), 3); a3 = np.tile(np.arange(3), N - 1)
kk = np.repeat(np.arange(N), 3); aa = np.tile(np.arange(3), N)
nr = 3 * (N - 1)
pr_rows = np.concatenate([np.arange(nr), np.arange(nr), nr + np.arange(nr), nr + np.arange(nr),
                          2 * nr + np.arange(3 * N), 2 * nr + 3 * N + np.arange(3 * N)])
pr_cols = np.concatenate([6 * (k + 1) + 3 + a3, 6 * k + 3 + a3, 6 * (k + 1) + a3, 6 * k + a3, 6 * kk + 3 + aa, 6 * kk + aa])
pr_vals = np.concatenate([rw3 / s_rt, -rw3 / s_rt, rw3 / s_rr, -rw3 / s_rr,
                          np.full(3 * N, 1 / s_at), np.full(3 * N, 1 / s_ar)])
Jpr = coo_matrix((pr_vals, (pr_rows, pr_cols)), shape=(2 * nr + 6 * N, n_cam_p)).tocsr()
JtJ_pr = (Jpr.T @ Jpr).toarray()


def prior_res(cp):
    Rn = (so3_exp(torch.tensor(cp[:, :3], device=dev)) @ R0t).cpu().numpy()
    C = C0 + cp[:, 3:]
    r_t = ((C[1:] - C[:-1]) - dC0).ravel() / s_rt * rw3
    dR = np.einsum("nij,nkj->nik", Rn[1:], Rn[:-1])
    r_r = Rot.from_matrix(np.einsum("nij,nkj->nik", dR, dR0)).as_rotvec().ravel() / s_rr * rw3
    return np.concatenate([r_t, r_r, (cp[:, 3:] / s_at).ravel(), (cp[:, :3] / s_ar).ravel()])


def huber_cost(e):
    return torch.where(e <= HUBER, 0.5 * e ** 2, HUBER * (e - 0.5 * HUBER)).sum()


def total_cost(cp, Xp, ci, pi, uvt):
    r = proj_v(torch.tensor(cp, device=dev)[ci], torch.tensor(Xp, device=dev)[pi], R0t[ci], C0t[ci]) - uvt
    e = r.norm(dim=1)
    return float(huber_cost(e)) + 0.5 * float((prior_res(cp) ** 2).sum()), e


def lm_solve(cp, Xp, cam_idx, pt_idx, uv, iters=25):
    """Levenberg-Marquardt with Schur complement: points eliminated per point (3x3 blocks),
    reduced camera system (6N x 6N) solved densely."""
    P = len(Xp)
    ci = torch.tensor(cam_idx, device=dev); pi = torch.tensor(pt_idx, device=dev)
    uvt = torch.tensor(uv, device=dev)
    M = len(cam_idx)
    lam = 1e-2
    T = lambda m: print(f'       [{time.time() - t_start:6.1f}s] {m}', flush=True)
    cost, _ = total_cost(cp, Xp, ci, pi, uvt)
    CHUNK = 8000                                                    # points per dense Schur chunk
    order_by_pt = torch.argsort(pi)
    obs_bounds = torch.searchsorted(pi[order_by_pt], torch.arange(P + 1, device=dev)).cpu().numpy()
    ar3 = torch.arange(3, device=dev); ar6 = torch.arange(6, device=dev)
    for it in range(iters):
        cpt = torch.tensor(cp, device=dev); Xt = torch.tensor(Xp, device=dev)
        Jc, Jx = [], []
        r = proj_v(cpt[ci], Xt[pi], R0t[ci], C0t[ci]) - uvt                       # (M,2)
        for s0 in range(0, M, 200000):
            sl = slice(s0, s0 + 200000)
            a_, b_ = jac_fn(cpt[ci[sl]], Xt[pi[sl]], R0t[ci[sl]], C0t[ci[sl]])
            Jc.append(a_); Jx.append(b_)
        Jc = torch.cat(Jc); Jx = torch.cat(Jx)                                       # (M,2,6), (M,2,3)
        e = r.norm(dim=1)
        w = torch.where(e <= HUBER, torch.ones_like(e), HUBER / e)[:, None, None]    # IRLS Huber weights
        JcT = Jc.transpose(1, 2); JxT = Jx.transpose(1, 2)
        U_o = JcT @ (w * Jc); V_o = JxT @ (w * Jx); W_o = JcT @ (w * Jx)
        gc_o = (JcT @ (w * r[:, :, None]))[..., 0]; gp_o = (JxT @ (w * r[:, :, None]))[..., 0]
        U = torch.zeros(N, 6, 6, device=dev, dtype=U_o.dtype).index_add_(0, ci, U_o)
        V = torch.zeros(P, 3, 3, device=dev, dtype=V_o.dtype).index_add_(0, pi, V_o)
        gc = torch.zeros(N, 6, device=dev, dtype=U_o.dtype).index_add_(0, ci, gc_o)
        gp = torch.zeros(P, 3, device=dev, dtype=U_o.dtype).index_add_(0, pi, gp_o)
        rp = prior_res(cp)
        g_cam = gc.cpu().numpy().ravel() + Jpr.T @ rp
        while True:
            ta = time.time()
            Vd = V + lam * torch.diag_embed(torch.diagonal(V, dim1=1, dim2=2)) + 1e-4 * torch.eye(3, device=dev)
            Vinv = torch.linalg.inv(Vd)
            Y_o = W_o @ Vinv[pi]                                                     # (M,6,3)
            # reduced camera system S = Hcc - sum_p Y_p W_p^T, accumulated on GPU in dense point chunks
            S = torch.zeros(n_cam_p, n_cam_p, device=dev, dtype=torch.float32)
            Yf, Wf = Y_o.float(), W_o.float()
            for c0_ in range(0, P, CHUNK):
                lo, hi = obs_bounds[c0_], obs_bounds[min(c0_ + CHUNK, P)]
                sl = order_by_pt[lo:hi]
                cols = (3 * (pi[sl] - c0_))[:, None, None] + ar3[None, None, :]
                rows = (6 * ci[sl])[:, None, None] + ar6[None, :, None]
                shape = (n_cam_p, 3 * min(CHUNK, P - c0_))
                Yd = torch.zeros(shape, device=dev).index_put_((rows.expand(-1, 6, 3).reshape(-1), cols.expand(-1, 6, 3).reshape(-1)), Yf[sl].reshape(-1), accumulate=True)
                Wd = torch.zeros(shape, device=dev).index_put_((rows.expand(-1, 6, 3).reshape(-1), cols.expand(-1, 6, 3).reshape(-1)), Wf[sl].reshape(-1), accumulate=True)
                S += Yd @ Wd.T
                del Yd, Wd
            tb = time.time()
            Hcc = torch.block_diag(*U).cpu().numpy() + JtJ_pr
            Hcc[np.diag_indices_from(Hcc)] *= (1 + lam)
            S = Hcc - S.double().cpu().numpy()
            Yg = torch.zeros(N, 6, device=dev, dtype=W_o.dtype).index_add_(0, ci, (Y_o @ gp[pi][:, :, None])[..., 0])
            rhs = -(g_cam - Yg.cpu().numpy().ravel())
            try:
                dc = np.linalg.solve(S, rhs)
            except np.linalg.LinAlgError:
                lam *= 10; continue
            dct = torch.tensor(dc, device=dev).reshape(N, 6)
            WtDc = torch.zeros(P, 3, device=dev, dtype=W_o.dtype).index_add_(0, pi, (W_o.transpose(1, 2) @ dct[ci][:, :, None])[..., 0])
            dp = (Vinv @ (-gp - WtDc)[:, :, None])[..., 0].cpu().numpy()
            if not (np.isfinite(dc).all() and np.isfinite(dp).all()):
                print("       non-finite step, increasing damping", flush=True)
                lam *= 10
                if lam > 1e6:
                    return cp, Xp, e
                continue
            cp_new, Xp_new = cp + dc.reshape(N, 6), Xp + dp
            new_cost, e_new = total_cost(cp_new, Xp_new, ci, pi, uvt)
            if args.verbose: print(f"       try lam={lam:.1e}: schur {tb - ta:.1f}s, total {time.time() - ta:.1f}s, cost {cost:.0f} -> {new_cost:.0f}", flush=True)
            if new_cost < cost:
                rel = (cost - new_cost) / cost
                cp, Xp, cost = cp_new, Xp_new, new_cost
                lam = max(lam / 3, 1e-7)
                break
            lam *= 5
            if lam > 1e6:
                return cp, Xp, e_new
        print(f"     iter {it + 1:2d}: cost {cost:.0f}  median reproj {float(e_new.median()):.3f}px  lambda {lam:.1e}", flush=True)
        if rel < 1e-5:
            break
    _, e = total_cost(cp, Xp, ci, pi, uvt)
    return cp, Xp, e


cp, Xp = np.zeros((N, 6)), X.copy()
cam_idx, pt_idx, uv = obs_cam, obs_pt, obs_uv
for rnd in range(2):
    cp, Xp, e = lm_solve(cp, Xp, cam_idx, pt_idx, uv)
    e = e.cpu().numpy()
    print(f"   round {rnd + 1}: reprojection median {np.median(e):.2f}px p90 {np.percentile(e, 90):.2f}px ({time.time() - t_start:.0f}s)")
    if rnd == 0:            # drop outlier observations and re-solve
        keep = e < 3.0
        cam_idx, pt_idx, uv = cam_idx[keep], pt_idx[keep], uv[keep]

Rn = (so3_exp(torch.tensor(cp[:, :3], device=dev)) @ R0t).cpu().numpy()
Cn = C0 + cp[:, 3:]
dt = np.linalg.norm(cp[:, 3:], axis=1)
dr = np.degrees(np.linalg.norm(cp[:, :3], axis=1))
print(f"   pose corrections: translation median {np.median(dt) * 1000:.1f}mm p95 {np.percentile(dt, 95) * 1000:.1f}mm "
      f"max {dt.max() * 1000:.1f}mm | rotation median {np.median(dr):.2f}deg max {dr.max():.2f}deg")
scale = np.sum(np.linalg.norm(np.diff(Cn, axis=0), axis=1)) / np.sum(np.linalg.norm(np.diff(C0, axis=0), axis=1))
print(f"   trajectory length ratio refined/ARCore = {scale:.4f} (metric scale preserved if ~1)")

for i, f in enumerate(frames):
    if "c2w_arcore" not in f:
        f["c2w_arcore"] = f["c2w"]
    c2w = np.eye(4); c2w[:3, :3] = Rn[i] @ GL_TO_CV; c2w[:3, 3] = Cn[i]
    f["c2w"] = c2w.tolist()
meta["ba"] = {"reproj_median_before": float(np.median(err_before)), "reproj_median_after": float(np.median(e)),
              "points": int(len(Xp)), "observations": int(len(cam_idx))}
json.dump(meta, open(os.path.join(args.work, "frames.json"), "w"), indent=1)
np.savez(os.path.join(args.work, "sparse.npz"), X=Xp, cam=cam_idx, pt=pt_idx, uv=uv)
print(f"Done in {time.time() - t_start:.0f}s -> frames.json (refined c2w), sparse.npz")
