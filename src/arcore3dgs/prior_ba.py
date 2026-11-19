"""Bundle adjustment of a COLMAP text model with soft priors on the relative motion between consecutive keyframes.

Made for `rot_sfm.py` models (FEATURELESS_TRACKING_PLAN step 5): their rotations come from the gyro (accurate over
seconds) and their positions from pair directions + the accelerometer (connected but noisy). A free COLMAP
bundle_adjuster lets the images pull the rotations away from the gyro again (R-052: 106 of 706 frames > 2 deg off),
so here the priors stay in the cost:

  - relative rotation between consecutive keyframes (time order): sigma = s_r0 + s_r1 * dt (deg), from the gyro;
  - relative position: sigma = s_t0 + s_t1 * |dC| (model units), from the sensor solution (loose);
  - weak absolute pose prior (gauge).

Reprojection: Huber (2 px) on undistorted pixel coordinates (intrinsics and distortion fixed). Levenberg-Marquardt
with a Schur complement on the GPU (same solver as ba.py). Points with large errors are dropped after round 1.

Writes the refined model (images.txt, frames.txt, points3D.txt, cameras.txt, rigs.txt and .bin via model_converter
when --colmap is given) to the output folder.

  python prior_ba.py <model_in> <work with frames.json> <model_out> [--s_r0 0.1 --s_r1 0.1 --s_t0 0.02 --s_t1 0.3]
"""
import os, sys, json, time, argparse, shutil, subprocess
import numpy as np, cv2, torch
from scipy.sparse import coo_matrix
from scipy.spatial.transform import Rotation as Rot

ap = argparse.ArgumentParser()
ap.add_argument("model_in"); ap.add_argument("work"); ap.add_argument("model_out")
ap.add_argument("--s_r0", type=float, default=0.1, help="deg, relative rotation prior sigma at dt=0")
ap.add_argument("--s_r1", type=float, default=0.1, help="deg/s, growth with the time between keyframes (gyro drift)")
ap.add_argument("--s_t0", type=float, default=0.02, help="model units, relative position prior sigma floor")
ap.add_argument("--s_t1", type=float, default=0.3, help="fraction of the step length")
ap.add_argument("--max_dt", type=float, default=3.0, help="s; no relative prior across longer gaps")
ap.add_argument("--s_abs_t", type=float, default=2.0); ap.add_argument("--s_abs_r", type=float, default=10.0)
ap.add_argument("--huber", type=float, default=2.0)
ap.add_argument("--drop_px", type=float, default=4.0, help="observations above this after round 1 are dropped")
ap.add_argument("--iters", type=int, default=30)
ap.add_argument("--colmap", default=None, help="COLMAP executable, to also write .bin")
args = ap.parse_args()
dev = "cuda" if torch.cuda.is_available() else "cpu"
torch.set_default_dtype(torch.float64)
t_start = time.time()

# ---------------- read the model ----------------
def lines(p):
    return [l.rstrip("\n") for l in open(p) if not l.startswith("#")]

cam_line = lines(os.path.join(args.model_in, "cameras.txt"))[0].split()
assert cam_line[1] == "OPENCV", cam_line[1]
fx, fy, cx, cy, k1, k2, p1, p2 = map(float, cam_line[4:12])
Kcv = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1.0]]); dist = np.array([k1, k2, p1, p2])

L = lines(os.path.join(args.model_in, "images.txt"))
imgs = []                                                   # (id, name, Rcw, tcw, header rest, points line)
for i in range(0, len(L), 2):
    h = L[i].split(); iid = int(h[0]); q = list(map(float, h[1:5])); t = np.array(list(map(float, h[5:8])))
    Rcw = Rot.from_quat([q[1], q[2], q[3], q[0]]).as_matrix()
    imgs.append(dict(id=iid, name=h[9], cam=h[8], Rcw=Rcw, tcw=t, pts2d=L[i + 1]))
meta = json.load(open(os.path.join(args.work, "frames.json")))
pts_of = {f["name"]: f["pts"] for f in meta["frames"]}
imgs.sort(key=lambda d: pts_of[os.path.splitext(d["name"])[0]])
N = len(imgs)
id2k = {d["id"]: k for k, d in enumerate(imgs)}
times = np.array([pts_of[os.path.splitext(d["name"])[0]] for d in imgs])
R0 = np.stack([d["Rcw"].T for d in imgs])                    # camera(OpenCV) -> world
C0 = np.stack([-d["Rcw"].T @ d["tcw"] for d in imgs])

pt_rows = lines(os.path.join(args.model_in, "points3D.txt"))
pid, X, rgb, obs_cam, obs_pt, obs_uv = [], [], [], [], [], []
uv2d = {}
for d in imgs:
    a = np.array(d["pts2d"].split(), dtype=float).reshape(-1, 3) if d["pts2d"].strip() else np.zeros((0, 3))
    uv2d[d["id"]] = a[:, :2]
for j, row in enumerate(pt_rows):
    s = row.split(); pid.append(int(s[0])); X.append(list(map(float, s[1:4]))); rgb.append(s[4:7])
    tr = np.array(s[8:], dtype=int).reshape(-1, 2)
    for iid, idx in tr:
        obs_cam.append(id2k[iid]); obs_pt.append(j); obs_uv.append(uv2d[iid][idx])
X = np.array(X); obs_cam = np.array(obs_cam); obs_pt = np.array(obs_pt); obs_uv = np.array(obs_uv)
# undistort observations once -> pinhole pixels with the same K
und = cv2.undistortPoints(obs_uv.reshape(-1, 1, 2), Kcv, dist, P=Kcv).reshape(-1, 2)
print(f"model: {N} cameras, {len(X)} points, {len(obs_uv)} observations ({time.time() - t_start:.0f}s)", flush=True)

# ---------------- the solver (as ba.py) ----------------
Kt = torch.tensor(Kcv, device=dev)


def so3_exp(w):
    th2 = (w * w).sum(-1, keepdim=True)[..., None]
    th = th2.clamp_min(1e-24).sqrt()
    small = th < 1e-4
    A = torch.where(small, 1 - th2 / 6, torch.sin(th) / th.clamp_min(1e-12))
    B = torch.where(small, 0.5 - th2 / 24, (1 - torch.cos(th)) / th2.clamp_min(1e-24))
    z = torch.zeros_like(w[..., 0])
    W = torch.stack([torch.stack([z, -w[..., 2], w[..., 1]], -1),
                     torch.stack([w[..., 2], z, -w[..., 0]], -1),
                     torch.stack([-w[..., 1], w[..., 0], z], -1)], -2)
    return torch.eye(3, device=w.device) + A * W + B * (W @ W)


R0t = torch.tensor(R0, device=dev); C0t = torch.tensor(C0, device=dev)


def proj_one(cam6, X3, R0c, C0c):
    Rc2w = so3_exp(cam6[:3]) @ R0c
    xc = Rc2w.T @ (X3 - (C0c + cam6[3:]))
    return torch.stack([Kt[0, 0] * xc[0] / xc[2] + Kt[0, 2], Kt[1, 1] * xc[1] / xc[2] + Kt[1, 2]])


jac_fn = torch.func.vmap(torch.func.jacrev(proj_one, argnums=(0, 1)))
proj_v = torch.func.vmap(proj_one)
n_cam_p = 6 * N
dt = np.diff(times)
dC0 = C0[1:] - C0[:-1]
dR0 = np.einsum("nij,nkj->nik", R0[1:], R0[:-1])
link = (dt <= args.max_dt).astype(float)
s_r = np.radians(args.s_r0 + args.s_r1 * dt)
s_t = args.s_t0 + args.s_t1 * np.linalg.norm(dC0, axis=1)
print(f"relative priors on {int(link.sum())} of {N - 1} consecutive pairs; rotation sigma median "
      f"{np.degrees(np.median(s_r)):.2f} deg, position sigma median {np.median(s_t):.3f}", flush=True)
wt = np.repeat(link / s_t, 3); wr = np.repeat(link / s_r, 3)
s_at, s_ar = args.s_abs_t, np.radians(args.s_abs_r)
k = np.repeat(np.arange(N - 1), 3); a3 = np.tile(np.arange(3), N - 1)
kk = np.repeat(np.arange(N), 3); aa = np.tile(np.arange(3), N)
nr = 3 * (N - 1)
pr_rows = np.concatenate([np.arange(nr), np.arange(nr), nr + np.arange(nr), nr + np.arange(nr),
                          2 * nr + np.arange(3 * N), 2 * nr + 3 * N + np.arange(3 * N)])
pr_cols = np.concatenate([6 * (k + 1) + 3 + a3, 6 * k + 3 + a3, 6 * (k + 1) + a3, 6 * k + a3, 6 * kk + 3 + aa, 6 * kk + aa])
pr_vals = np.concatenate([wt, -wt, wr, -wr, np.full(3 * N, 1 / s_at), np.full(3 * N, 1 / s_ar)])
Jpr = coo_matrix((pr_vals, (pr_rows, pr_cols)), shape=(2 * nr + 6 * N, n_cam_p)).tocsr()
JtJ_pr = (Jpr.T @ Jpr).toarray()
HUBER = args.huber


def prior_res(cp):
    Rn = (so3_exp(torch.tensor(cp[:, :3], device=dev)) @ R0t).cpu().numpy()
    C = C0 + cp[:, 3:]
    r_t = ((C[1:] - C[:-1]) - dC0).ravel() * wt
    dR = np.einsum("nij,nkj->nik", Rn[1:], Rn[:-1])
    r_r = Rot.from_matrix(np.einsum("nij,nkj->nik", dR, dR0)).as_rotvec().ravel() * wr
    return np.concatenate([r_t, r_r, (cp[:, 3:] / s_at).ravel(), (cp[:, :3] / s_ar).ravel()])


def huber_cost(e):
    return torch.where(e <= HUBER, 0.5 * e ** 2, HUBER * (e - 0.5 * HUBER)).sum()


def total_cost(cp, Xp, ci, pi, uvt):
    r = proj_v(torch.tensor(cp, device=dev)[ci], torch.tensor(Xp, device=dev)[pi], R0t[ci], C0t[ci]) - uvt
    e = r.norm(dim=1)
    e = torch.where(torch.isfinite(e), e, torch.full_like(e, 1e6))
    return float(huber_cost(e)) + 0.5 * float((prior_res(cp) ** 2).sum()), e


def lm_solve(cp, Xp, cam_idx, pt_idx, uv, iters):
    P = len(Xp)
    ci = torch.tensor(cam_idx, device=dev); pi = torch.tensor(pt_idx, device=dev)
    uvt = torch.tensor(uv, device=dev)
    M = len(cam_idx)
    lam = 1e-2
    cost, e_new = total_cost(cp, Xp, ci, pi, uvt)
    print(f"     start: cost {cost:.0f}  median reproj {float(e_new.median()):.3f}px", flush=True)
    CHUNK = 8000
    order_by_pt = torch.argsort(pi)
    obs_bounds = torch.searchsorted(pi[order_by_pt], torch.arange(P + 1, device=dev)).cpu().numpy()
    ar3 = torch.arange(3, device=dev); ar6 = torch.arange(6, device=dev)
    for it in range(iters):
        cpt = torch.tensor(cp, device=dev); Xt = torch.tensor(Xp, device=dev)
        Jc, Jx = [], []
        r = proj_v(cpt[ci], Xt[pi], R0t[ci], C0t[ci]) - uvt
        for s0 in range(0, M, 200000):
            sl = slice(s0, s0 + 200000)
            a_, b_ = jac_fn(cpt[ci[sl]], Xt[pi[sl]], R0t[ci[sl]], C0t[ci[sl]])
            Jc.append(a_); Jx.append(b_)
        Jc = torch.cat(Jc); Jx = torch.cat(Jx)
        e = r.norm(dim=1)
        w = torch.where(e <= HUBER, torch.ones_like(e), HUBER / e)[:, None, None]
        JcT = Jc.transpose(1, 2); JxT = Jx.transpose(1, 2)
        U_o = JcT @ (w * Jc); V_o = JxT @ (w * Jx); W_o = JcT @ (w * Jx)
        gc_o = (JcT @ (w * r[:, :, None]))[..., 0]; gp_o = (JxT @ (w * r[:, :, None]))[..., 0]
        U = torch.zeros(N, 6, 6, device=dev).index_add_(0, ci, U_o)
        V = torch.zeros(P, 3, 3, device=dev).index_add_(0, pi, V_o)
        gc = torch.zeros(N, 6, device=dev).index_add_(0, ci, gc_o)
        gp = torch.zeros(P, 3, device=dev).index_add_(0, pi, gp_o)
        g_cam = gc.cpu().numpy().ravel() + Jpr.T @ prior_res(cp)
        rel = 0.0
        while True:
            Vd = V + lam * torch.diag_embed(torch.diagonal(V, dim1=1, dim2=2)) + 1e-4 * torch.eye(3, device=dev)
            Vinv = torch.linalg.inv(Vd)
            Y_o = W_o @ Vinv[pi]
            S = torch.zeros(n_cam_p, n_cam_p, device=dev, dtype=torch.float32)
            Yf, Wf = Y_o.float(), W_o.float()
            for c0_ in range(0, P, CHUNK):
                lo, hi = obs_bounds[c0_], obs_bounds[min(c0_ + CHUNK, P)]
                sl = order_by_pt[lo:hi]
                cols = (3 * (pi[sl] - c0_))[:, None, None] + ar3[None, None, :]
                rows = (6 * ci[sl])[:, None, None] + ar6[None, :, None]
                shape = (n_cam_p, 3 * min(CHUNK, P - c0_))
                ridx = rows.expand(-1, 6, 3).reshape(-1); cidx = cols.expand(-1, 6, 3).reshape(-1)
                Yd = torch.zeros(shape, device=dev, dtype=torch.float32).index_put_((ridx, cidx), Yf[sl].reshape(-1), accumulate=True)
                Wd = torch.zeros(shape, device=dev, dtype=torch.float32).index_put_((ridx, cidx), Wf[sl].reshape(-1), accumulate=True)
                S += Yd @ Wd.T
                del Yd, Wd
            Hcc = torch.block_diag(*U).cpu().numpy() + JtJ_pr
            Hcc[np.diag_indices_from(Hcc)] *= (1 + lam)
            S = Hcc - S.double().cpu().numpy()
            Yg = torch.zeros(N, 6, device=dev).index_add_(0, ci, (Y_o @ gp[pi][:, :, None])[..., 0])
            rhs = -(g_cam - Yg.cpu().numpy().ravel())
            try:
                dc = np.linalg.solve(S, rhs)
            except np.linalg.LinAlgError:
                lam *= 10; continue
            dct = torch.tensor(dc, device=dev).reshape(N, 6)
            WtDc = torch.zeros(P, 3, device=dev).index_add_(0, pi, (W_o.transpose(1, 2) @ dct[ci][:, :, None])[..., 0])
            dp = (Vinv @ (-gp - WtDc)[:, :, None])[..., 0].cpu().numpy()
            if not (np.isfinite(dc).all() and np.isfinite(dp).all()):
                lam *= 10
                if lam > 1e6:
                    return cp, Xp, e
                continue
            cp_new, Xp_new = cp + dc.reshape(N, 6), Xp + dp
            new_cost, e_new = total_cost(cp_new, Xp_new, ci, pi, uvt)
            if new_cost < cost:
                rel = (cost - new_cost) / cost
                cp, Xp, cost = cp_new, Xp_new, new_cost
                lam = max(lam / 3, 1e-7)
                break
            lam *= 5
            if lam > 1e6:
                _, e_new = total_cost(cp, Xp, ci, pi, uvt)
                return cp, Xp, e_new
        print(f"     iter {it + 1:2d}: cost {cost:.0f}  median reproj {float(e_new.median()):.3f}px  lambda {lam:.1e} "
              f"({time.time() - t_start:.0f}s)", flush=True)
        if rel < 1e-6:
            break
    _, e = total_cost(cp, Xp, ci, pi, uvt)
    return cp, Xp, e


cp, Xp = np.zeros((N, 6)), X.copy()
cam_idx, pt_idx, uv = obs_cam, obs_pt, und
for rnd in range(2):
    cp, Xp, e = lm_solve(cp, Xp, cam_idx, pt_idx, uv, args.iters)
    e = e.cpu().numpy()
    print(f"   round {rnd + 1}: reprojection median {np.median(e):.2f}px p90 {np.percentile(e, 90):.2f}px "
          f"({time.time() - t_start:.0f}s)", flush=True)
    if rnd == 0:
        keep = e < args.drop_px
        cam_idx, pt_idx, uv = cam_idx[keep], pt_idx[keep], uv[keep]
        print(f"   dropped {int((~keep).sum())} observations > {args.drop_px}px", flush=True)

Rn = (so3_exp(torch.tensor(cp[:, :3], device=dev)) @ R0t).cpu().numpy()
Cn = C0 + cp[:, 3:]
dtr = np.linalg.norm(cp[:, 3:], axis=1); drr = np.degrees(np.linalg.norm(cp[:, :3], axis=1))
dRn = np.einsum("nij,nkj->nik", Rn[1:], Rn[:-1])
rel_r = np.degrees(np.linalg.norm(Rot.from_matrix(np.einsum("nij,nkj->nik", dRn, dR0)).as_rotvec(), axis=1))
step0 = np.linalg.norm(dC0, axis=1); step1 = np.linalg.norm(np.diff(Cn, axis=0), axis=1)
print(f"pose change: position median {np.median(dtr):.3f} p95 {np.percentile(dtr, 95):.3f} | rotation median "
      f"{np.median(drr):.2f} deg max {drr.max():.2f} | relative rotation vs prior median {np.median(rel_r):.3f} deg "
      f"p95 {np.percentile(rel_r, 95):.3f} | path length ratio {step1.sum() / step0.sum():.3f}", flush=True)

# ---------------- write ----------------
os.makedirs(args.model_out, exist_ok=True)
for fn in ("cameras.txt", "rigs.txt"):
    shutil.copy(os.path.join(args.model_in, fn), os.path.join(args.model_out, fn))
keep_pts = np.zeros(len(Xp), bool); keep_pts[np.unique(pt_idx)] = True
kept_obs = set(zip(cam_idx.tolist(), pt_idx.tolist()))
pose = {}
for kx, d in enumerate(imgs):
    Rcw = Rn[kx].T; tcw = -Rcw @ Cn[kx]; q = Rot.from_matrix(Rcw).as_quat()
    pose[d["id"]] = f"{q[3]!r} {q[0]!r} {q[1]!r} {q[2]!r} {tcw[0]!r} {tcw[1]!r} {tcw[2]!r}"
# image points of dropped observations / points lose their 3D id
pid_new = {j: pid[j] for j in range(len(Xp)) if keep_pts[j]}
pid2j = {pid[j]: j for j in range(len(Xp))}
with open(os.path.join(args.model_out, "images.txt"), "w") as f:
    f.write(f"# Number of images: {N}\n")
    for d in sorted(imgs, key=lambda d: d["id"]):
        f.write(f"{d['id']} {pose[d['id']]} {d['cam']} {d['name']}\n")
        a = d["pts2d"].split(); out = []
        kx = id2k[d["id"]]
        for i3 in range(0, len(a), 3):
            p3 = int(a[i3 + 2])
            if p3 != -1 and (kx, pid2j[p3]) not in kept_obs:
                p3 = -1
            out += [a[i3], a[i3 + 1], str(p3)]
        f.write(" ".join(out) + "\n")
with open(os.path.join(args.model_out, "frames.txt"), "w") as f:
    f.write(f"# Number of frames: {N}\n")
    for d in sorted(imgs, key=lambda d: d["id"]):
        f.write(f"{d['id']} 1 {pose[d['id']]} 1 CAMERA {d['cam']} {d['id']}\n")
# tracks: keep only surviving observations
tracks = {}
inv_img = {k_: d["id"] for k_, d in enumerate(imgs)}
pos_in_img = {}
for d in imgs:
    a = d["pts2d"].split()
    for i3 in range(0, len(a), 3):
        p3 = int(a[i3 + 2])
        if p3 != -1:
            pos_in_img[(d["id"], p3)] = i3 // 3
for c_, j in kept_obs:
    tracks.setdefault(j, []).append((inv_img[c_], pos_in_img[(inv_img[c_], pid[j])]))
with open(os.path.join(args.model_out, "points3D.txt"), "w") as f:
    f.write(f"# Number of points: {int(sum(1 for j in tracks if len(tracks[j]) >= 2))}\n")
    for j, tr in tracks.items():
        if len(tr) < 2:
            continue
        f.write(f"{pid[j]} {Xp[j, 0]!r} {Xp[j, 1]!r} {Xp[j, 2]!r} {' '.join(rgb[j])} 1.0 "
                + " ".join(f"{a_} {b_}" for a_, b_ in tr) + "\n")
# single-observation points must not be referenced by images
single = {pid[j] for j, tr in tracks.items() if len(tr) < 2}
if single:
    p = os.path.join(args.model_out, "images.txt"); L2 = open(p).read().split("\n"); out = [L2[0]]
    for i in range(1, len(L2) - 1, 2):
        out.append(L2[i]); a = L2[i + 1].split()
        for i3 in range(2, len(a), 3):
            if int(a[i3]) in single:
                a[i3] = "-1"
        out.append(" ".join(a))
    open(p, "w").write("\n".join(out) + "\n")
json.dump(dict(cameras=N, points=int(len(tracks)), observations=int(len(cam_idx)),
               reproj_median=float(np.median(e)), args=vars(args)),
          open(os.path.join(args.model_out, "prior_ba.json"), "w"), indent=1)
if args.colmap:
    r_ = subprocess.run([args.colmap, "model_converter", "--input_path", args.model_out, "--output_path",
                         args.model_out, "--output_type", "BIN"], capture_output=True, text=True)
    print("model_converter", "ok" if r_.returncode == 0 else r_.stderr[-1500:])
print(f"wrote {args.model_out} ({time.time() - t_start:.0f}s)")
