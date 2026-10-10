"""Stage 3: depth-supervised 3D Gaussian Splatting on an ARCore capture (gsplat).

What keeps the splats on real surfaces (the "painting broken into pieces" failure):
  * init from the fused TSDF surface (init.ply), not from stacked per-frame depth
  * depth loss against depth_fused/ (multi-view consistent by construction), weighted high early,
    decayed later so photometric detail can refine
  * flatness regulariser: the smallest scale axis of each Gaussian is pushed down (surfels on
    surfaces, like PGSR / 2DGS-style flattening) and extreme anisotropy is penalised
  * optional per-camera pose refinement (small SE(3) residuals on training cameras)
Everything stays in ARCore world coordinates: metres, +Y up.

Run with nerfstudio-env python inside the MSVC environment (see run_arcore3dgs.bat).
"""
import os, sys, json, math, time, argparse, functools
print = functools.partial(print, flush=True)
import numpy as np, cv2, torch, torch.nn.functional as F
from plyfile import PlyData, PlyElement
from gsplat import rasterization
from gsplat.strategy import DefaultStrategy
from pytorch_msssim import ssim

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--out", default=None)
ap.add_argument("--steps", type=int, default=0, help="0 = auto: max(7000, steps_per_frame x training frames)")
ap.add_argument("--steps_per_frame", type=int, default=30)
ap.add_argument("--downscale", type=int, default=2)
ap.add_argument("--depth_src", default="mvs", choices=["mvs", "fused"],
                help="mvs: each frame's own depth (depth_mvs, weighted by mvs_mask); fused: old TSDF re-render target")
ap.add_argument("--depth_w", type=float, default=0.0, help="depth loss weight during densification (0 = off: metric scale comes from BA poses)")
ap.add_argument("--depth_w_final", type=float, default=0.0, help="depth weight reached at the end (decays after densification)")
ap.add_argument("--fill_w", type=float, default=0.05, help="weight of filled (not stereo-measured) depth pixels")
ap.add_argument("--init_mvs", type=int, default=0, help="(mesh init only) add stereo-measured points")
ap.add_argument("--init", default="points", choices=["points", "mesh"],
                help="points: init_points.ply from make_init.py (BA + MVS-measured); mesh: old TSDF init.ply")
ap.add_argument("--init_opacity", type=float, default=0.1)
ap.add_argument("--frames_file", default="frames.json", help="e.g. frames_pocket.json (PocketGS keyframe gate)")
ap.add_argument("--init_ply", default="", help="override initial point cloud, e.g. prior_points.ply (pocket_prior.py)")
ap.add_argument("--init_thickness", type=float, default=0.2, help="initial disc thickness / width (PocketGS: thin but not degenerate)")
ap.add_argument("--densify_until", type=float, default=0.5, help="fraction of steps with densification (3DGS: 15k of 30k)")
ap.add_argument("--frame_range", default="", help="debug: train only on frames a:b (e.g. 200:220)")
ap.add_argument("--strategy", default="default", choices=["mcmc", "default"],
                help="mcmc: fixed splat budget, dead splats relocated to high-error areas (3DGS-as-MCMC)")
ap.add_argument("--max_gaussians", type=float, default=3.2e6, help="splat budget (MCMC cap / VRAM safety cap)")
ap.add_argument("--outlier_reject", type=int, default=1, help="drop training frames that fit far worse than the rest")
ap.add_argument("--fullres_frac", type=float, default=0.3, help="last fraction of steps trained at full resolution")
ap.add_argument("--flat_w", type=float, default=0.0, help="flattening regulariser (0 = off: with Adam it collapsed splats to zero thickness)")
ap.add_argument("--pose_opt", type=int, default=0, help="BA poses are already refined; joint refinement drifted up to 73 mm")
ap.add_argument("--exposure", type=int, default=1)
ap.add_argument("--antialiased", type=int, default=0, help="classic raster; antialiased opacity compensation crushed thin splats")
ap.add_argument("--prune_dist", type=float, default=0.0, help="drop splats farther than this (m) from the fused mesh; 0=off (it deletes thin objects the mesh misses)")
ap.add_argument("--test_every", type=int, default=10)
ap.add_argument("--sh_degree", type=int, default=2)
args = ap.parse_args()

dev = torch.device("cuda")
torch.manual_seed(0)
OUT = args.out or os.path.join(args.work, "gs")
os.makedirs(os.path.join(OUT, "renders"), exist_ok=True)
meta = json.load(open(os.path.join(args.work, args.frames_file)))
frames = meta["frames"]
if args.frame_range:
    _a, _b = map(int, args.frame_range.split(":"))
    frames = frames[_a:_b]
ds = args.downscale
W, H = meta["W"] // ds, meta["H"] // ds
K = torch.tensor([[meta["fx"] / ds, 0, meta["cx"] / ds], [0, meta["fy"] / ds, meta["cy"] / ds], [0, 0, 1]],
                 dtype=torch.float32, device=dev)
GL_TO_CV = np.diag([1.0, -1.0, -1.0, 1.0])

# ---------------- data ----------------
# Depth target. The old target (fused TSDF re-rendered per view) erased thin/foreground objects that
# other views see through: on stereo-measured pixels it was >5% off on ~30% of pixels, so the depth loss
# fought the photometric loss -> underfitting, "cotton" texture. Now each frame is supervised with its
# own depth: stereo-measured pixels at full weight, filled (Metric3D/ARCore-corrected) pixels low weight,
# and no fill weight for frames that fusion flagged as inconsistent.
dropped = set(meta.get("fusion_dropped", []))
imgs, depths, dweights, w2cs = [], [], [], []
for f in frames:
    im = cv2.imread(os.path.join(args.work, "images", f["name"] + ".jpg"))
    im = cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA)
    imgs.append(torch.from_numpy(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)))
    if args.depth_src == "mvs":
        d = np.load(os.path.join(args.work, "depth_mvs", f["name"] + ".npy")).astype(np.float32)
        mm = np.load(os.path.join(args.work, "mvs_mask", f["name"] + ".npy"))
        wgt = np.where(mm, 1.0, 0.0 if f["name"] in dropped else args.fill_w).astype(np.float32)
    else:
        d = np.load(os.path.join(args.work, "depth_fused", f["name"] + ".npy")).astype(np.float32)
        wgt = np.ones_like(d)
    if d.shape != (H, W):
        d = cv2.resize(d, (W, H), interpolation=cv2.INTER_NEAREST)
        wgt = cv2.resize(wgt, (W, H), interpolation=cv2.INTER_NEAREST)
    wgt[(d <= 0.05) | ~np.isfinite(d)] = 0
    depths.append(torch.from_numpy(np.nan_to_num(d)).half())
    dweights.append(torch.from_numpy((wgt * 255).astype(np.uint8)))
    c2w = np.array(f["c2w"]) @ GL_TO_CV                     # OpenGL cam -> OpenCV cam
    w2cs.append(torch.from_numpy(np.linalg.inv(c2w)).float())
# kept in pinned system RAM (~2.4 GB for 760 frames) and moved one frame per step: on an 8 GB GPU the
# Gaussians need that memory once densification passes ~2.5M splats
imgs = torch.stack(imgs).pin_memory()                         # uint8 [N,H,W,3]
depths = torch.stack(depths).pin_memory()                     # float16 [N,H,W]
dweights = torch.stack(dweights).pin_memory()                 # uint8 [N,H,W], weight*255
IMG = lambda i: imgs[i].to(dev, non_blocking=True)
DEP = lambda i: depths[i].to(dev, non_blocking=True)
DW = lambda i: dweights[i].to(dev, non_blocking=True)
w2cs = torch.stack(w2cs).to(dev)
Kfull = torch.tensor([[meta["fx"], 0, meta["cx"]], [0, meta["fy"], meta["cy"]], [0, 0, 1]], dtype=torch.float32, device=dev)
Wf, Hf = meta["W"], meta["H"]
N = len(frames)
test_ids = list(range(0, N, args.test_every)) if args.test_every > 0 else []
train_ids = [i for i in range(N) if i not in set(test_ids)]
cam_centers = torch.linalg.inv(w2cs)[:, :3, 3]
scene_scale = float((cam_centers - cam_centers.mean(0)).norm(dim=1).max()) * 1.1
if args.steps <= 0:
    args.steps = max(7000, args.steps_per_frame * len(train_ids))
print(flush=True); print(f"{N} frames ({len(train_ids)} train / {len(test_ids)} test) at {W}x{H}, scene scale {scene_scale:.2f} m, {args.steps} steps")

# ---------------- init gaussians ----------------
ply = PlyData.read(os.path.join(args.work, args.init_ply or ("init_points.ply" if args.init == "points" else "init.ply")))["vertex"]
xyz = torch.tensor(np.stack([ply["x"], ply["y"], ply["z"]], 1), dtype=torch.float32, device=dev)
rgb = torch.tensor(np.stack([ply["red"], ply["green"], ply["blue"]], 1) / 255.0, dtype=torch.float32, device=dev)
n_mesh = len(xyz)
if args.init == "mesh" and args.init_mvs and args.depth_src == "mvs":
    # add stereo-measured points (thin / foreground objects the fused mesh misses, e.g. a mesh chair back)
    Kh = K.cpu().numpy(); Kinv = np.linalg.inv(Kh)
    pts_l, col_l = [], []
    for k, f in enumerate(frames):
        if k % 2:
            continue
        mm = np.load(os.path.join(args.work, "mvs_mask", f["name"] + ".npy"))
        if mm.shape != (H, W) or mm.sum() < 50:
            continue
        d = np.load(os.path.join(args.work, "depth_mvs", f["name"] + ".npy")).astype(np.float32)
        vv, uu = np.nonzero(mm[::3, ::3]); vv, uu = vv * 3, uu * 3
        z = d[vv, uu]
        Xc = (Kinv @ np.stack([uu + 0.5, vv + 0.5, np.ones(len(uu))])) * z
        c2w = np.array(f["c2w"]) @ GL_TO_CV
        pts_l.append((c2w[:3, :3] @ Xc + c2w[:3, 3:4]).T)
        col_l.append(imgs[k][vv, uu].cpu().numpy() / 255.0)
    if pts_l:
        P = np.concatenate(pts_l); Cc = np.concatenate(col_l)
        _, uniq = np.unique(np.floor(P / 0.005).astype(np.int64), axis=0, return_index=True)   # 5 mm voxels
        P, Cc = P[uniq], Cc[uniq]
        if len(P) > 400000:
            sel = np.random.default_rng(0).choice(len(P), 400000, replace=False); P, Cc = P[sel], Cc[sel]
        xyz = torch.cat([xyz, torch.tensor(P, dtype=torch.float32, device=dev)])
        rgb = torch.cat([rgb, torch.tensor(Cc, dtype=torch.float32, device=dev)])
        print(f"init: {n_mesh} mesh points + {len(P)} stereo-measured points")
# initial scale = mean distance to 3 nearest neighbours
from scipy.spatial import cKDTree
xyz_np = xyz.cpu().numpy()
nn = cKDTree(xyz_np).query(xyz_np, k=4)[0][:, 1:].mean(1)
nn = torch.tensor(nn, dtype=torch.float32, device=dev).clamp(1e-4, 0.05)
# surface-aligned discs (PocketGS / PGSR): Gaussian z-axis = surface normal, thin along it
if "nx" in ply.data.dtype.names:
    from scipy.spatial.transform import Rotation as _Rot
    nrm = np.stack([ply["nx"], ply["ny"], ply["nz"]], 1).astype(np.float64)
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
    helper = np.where(np.abs(nrm[:, 1:2]) < 0.9, np.array([[0, 1, 0]]), np.array([[1, 0, 0]]))
    t1 = np.cross(helper, nrm); t1 /= np.linalg.norm(t1, axis=1, keepdims=True)
    t2 = np.cross(nrm, t1)
    q_xyzw = _Rot.from_matrix(np.stack([t1, t2, nrm], 2)).as_quat()
    init_quats = torch.tensor(q_xyzw[:, [3, 0, 1, 2]], dtype=torch.float32, device=dev)   # gsplat: wxyz
    init_logscale = torch.log(torch.stack([nn[:n_mesh], nn[:n_mesh], nn[:n_mesh] * args.init_thickness], 1))
    if len(xyz) > n_mesh:                                      # stereo points: no normal -> isotropic
        extra = len(xyz) - n_mesh
        init_quats = torch.cat([init_quats, F.normalize(torch.randn(extra, 4, device=dev), dim=-1)])
        init_logscale = torch.cat([init_logscale, torch.log(nn[n_mesh:])[:, None].repeat(1, 3)])
    print(f"init: {n_mesh} surface-aligned discs (thickness {args.init_thickness} x width, opacity {args.init_opacity}) from {args.init}")
else:
    init_quats = F.normalize(torch.randn(len(xyz), 4, device=dev), dim=-1)
    init_logscale = torch.log(nn)[:, None].repeat(1, 3)
C0 = 0.28209479177387814
n_sh = (args.sh_degree + 1) ** 2
params = torch.nn.ParameterDict({
    "means": torch.nn.Parameter(xyz),
    "scales": torch.nn.Parameter(init_logscale),
    "quats": torch.nn.Parameter(init_quats),
    "opacities": torch.nn.Parameter(torch.logit(torch.full((len(xyz),), args.init_opacity, device=dev))),
    "sh0": torch.nn.Parameter(((rgb - 0.5) / C0)[:, None, :]),
    "shN": torch.nn.Parameter(torch.zeros(len(xyz), n_sh - 1, 3, device=dev)),
})
lrs = {"means": 1.6e-4 * scene_scale, "scales": 5e-3, "quats": 1e-3, "opacities": 5e-2, "sh0": 2.5e-3, "shN": 2.5e-3 / 20}
optimizers = {k: torch.optim.Adam([params[k]], lr=lrs[k], eps=1e-15) for k in params}
means_sched = torch.optim.lr_scheduler.ExponentialLR(optimizers["means"], gamma=0.01 ** (1.0 / args.steps))

if args.strategy == "mcmc":
    from gsplat.strategy import MCMCStrategy
    strategy = MCMCStrategy(cap_max=int(args.max_gaussians), refine_start_iter=500,
                            refine_stop_iter=int(args.steps * args.densify_until), refine_every=100, min_opacity=0.005)
    strategy.check_sanity(params, optimizers)
    state = strategy.initialize_state()
else:
    strategy = DefaultStrategy(refine_start_iter=500, refine_stop_iter=int(args.steps * args.densify_until), reset_every=3000,
                               refine_every=100, prune_opa=0.005, grow_grad2d=0.0002, verbose=False)
    strategy.check_sanity(params, optimizers)
    state = strategy.initialize_state(scene_scale=scene_scale)
frame_l1 = np.full(N, np.nan)                                   # running photometric error per frame

# per-camera pose residual (axis-angle + translation), applied as w2c' = dT @ w2c
pose_delta = torch.nn.Parameter(torch.zeros(N, 6, device=dev))
# per-image exposure / white-balance: rgb' = rgb * exp(gain) + bias (absorbs ARCore auto-exposure)
expo = torch.nn.Parameter(torch.zeros(N, 6, device=dev))
expo_optim = torch.optim.Adam([expo], lr=1e-3 if args.exposure else 0.0)
pose_optim = torch.optim.Adam([pose_delta], lr=1e-4 if args.pose_opt else 0.0, weight_decay=0)


def so3_exp(w):
    th = w.norm(dim=-1, keepdim=True).clamp_min(1e-8)
    k = w / th
    Kx = torch.zeros(w.shape[0], 3, 3, device=w.device)
    Kx[:, 0, 1], Kx[:, 0, 2], Kx[:, 1, 0] = -k[:, 2], k[:, 1], k[:, 2]
    Kx[:, 1, 2], Kx[:, 2, 0], Kx[:, 2, 1] = -k[:, 0], -k[:, 1], k[:, 0]
    th = th[..., None]
    return torch.eye(3, device=w.device) + torch.sin(th) * Kx + (1 - torch.cos(th)) * Kx @ Kx


def get_w2c(i, refine=True):
    w2c = w2cs[i:i + 1]
    if not (refine and args.pose_opt):
        return w2c
    d = pose_delta[i:i + 1]
    T = torch.eye(4, device=dev)[None].clone()
    T[:, :3, :3] = so3_exp(d[:, :3])
    T[:, :3, 3] = d[:, 3:]
    return T @ w2c


def render(w2c, sh_deg, full=False):
    colors = torch.cat([params["sh0"], params["shN"]], 1)
    Kr, Wr, Hr = (Kfull, Wf, Hf) if full else (K, W, H)
    out, alpha, info = rasterization(
        params["means"], F.normalize(params["quats"], dim=-1), torch.exp(params["scales"]),
        torch.sigmoid(params["opacities"]), colors, w2c, Kr[None], Wr, Hr,
        sh_degree=sh_deg, near_plane=0.05, far_plane=50.0, render_mode="RGB+ED", packed=False,
        rasterize_mode="antialiased" if args.antialiased else "classic")
    return out[0, ..., :3].clamp(0, 1), out[0, ..., 3], alpha[0, ..., 0], info


# ---------------- train ----------------
t_start = time.time()
order = []
for step in range(args.steps):
    if not order:
        order = list(np.random.permutation(train_ids))
    i = order.pop()
    sh_deg = min(step // 1000, args.sh_degree)
    w2c = get_w2c(i)
    full = step >= int(args.steps * (1 - args.fullres_frac))
    rgb_r, dep_r, alpha_r, info = render(w2c, sh_deg, full)
    if args.strategy != "mcmc":
        strategy.step_pre_backward(params, optimizers, state, step, info)

    if full:   # stream full-res photo from disk (all of them would not fit in 8 GB VRAM)
        im = cv2.imread(os.path.join(args.work, "images", frames[i]["name"] + ".jpg"))
        gt = torch.from_numpy(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).to(dev).float() / 255.0
        dt = F.interpolate(DEP(i)[None, None].float(), (Hf, Wf), mode="nearest")[0, 0]
        dwt = F.interpolate(DW(i)[None, None].float(), (Hf, Wf), mode="nearest")[0, 0] / 255.0
    else:
        gt = IMG(i).float() / 255.0
        dt = DEP(i).float(); dwt = DW(i).float() / 255.0
    if args.exposure:
        rgb_r = rgb_r * torch.exp(expo[i, :3]) + expo[i, 3:]
    l1 = (rgb_r - gt).abs().mean()
    ssim_l = 1 - ssim(rgb_r.permute(2, 0, 1)[None], gt.permute(2, 0, 1)[None], data_range=1.0, size_average=True)
    loss = 0.8 * l1 + 0.2 * ssim_l
    if args.strategy == "mcmc":
        loss = loss + 0.01 * torch.sigmoid(params["opacities"]).mean() + 0.01 * torch.exp(params["scales"]).mean()
    frame_l1[i] = l1.item() if np.isnan(frame_l1[i]) else 0.7 * frame_l1[i] + 0.3 * l1.item()

    # depth: weighted relative L1, capped at 20% so a wrong target cannot dominate the photo loss;
    # full weight during densification, then decays to depth_w_final
    stop = int(args.steps * args.densify_until)
    a = 0.0 if step < stop else (step - stop) / max(1, args.steps - stop)
    dw = args.depth_w * (1 - a) + args.depth_w_final * a
    m = dwt > 0
    if dw > 0 and m.any():
        rel = ((dep_r[m] - dt[m]).abs() / dt[m]).clamp(max=0.2)
        loss = loss + dw * (rel * dwt[m]).sum() / dwt[m].sum()

    # flatten gaussians onto surfaces + limit needles
    if args.flat_w > 0:
        sc = torch.exp(params["scales"])
        smin = sc.min(dim=1).values
        loss = loss + args.flat_w * smin.mean()
        ratio = sc.max(dim=1).values / sc.median(dim=1).values
        loss = loss + 0.01 * F.relu(ratio - 10).mean()

    loss.backward()
    for opt in optimizers.values():
        opt.step(); opt.zero_grad(set_to_none=True)
    if args.pose_opt and step > 500:
        pose_optim.step()
    pose_optim.zero_grad(set_to_none=True)
    expo_optim.step(); expo_optim.zero_grad(set_to_none=True)
    means_sched.step()
    if args.strategy == "mcmc":
        strategy.step_post_backward(params, optimizers, state, step, info, lr=means_sched.get_last_lr()[0])
    else:
        strategy.step_post_backward(params, optimizers, state, step, info, packed=False)
    # outlier frames (wrong pose after tracking loss, moving objects, ...): at 40% of training drop frames whose
    # running photo error is far above the rest, so they stop corrupting their region
    if args.outlier_reject and step == int(args.steps * 0.4):
        seen = np.array([i for i in train_ids if not np.isnan(frame_l1[i])])
        e = frame_l1[seen]; med = np.median(e); mad = np.median(np.abs(e - med)) + 1e-6
        bad = set(seen[e > med + 4 * 1.4826 * mad].tolist())
        train_ids = [i for i in train_ids if i not in bad]; order = [i for i in order if i not in bad]
        print(f"outlier rejection: dropped {len(bad)} training frames (running L1 > {med + 4 * 1.4826 * mad:.3f}; median {med:.3f}): "
              f"{sorted(frames[i]['name'] for i in bad)[:20]}", flush=True)
    if args.strategy != "mcmc" and len(params["means"]) > args.max_gaussians and step % 100 == 0:
        with torch.no_grad():
            excess = len(params["means"]) - int(args.max_gaussians)
            idx = torch.topk(params["opacities"].detach(), excess, largest=False).indices
            mask = torch.zeros(len(params["means"]), dtype=torch.bool, device=dev); mask[idx] = True
        from gsplat.strategy.ops import remove as _remove
        _remove(params, optimizers, state, mask)

    if step % 250 == 0 or step == args.steps - 1:
        el = time.time() - t_start
        print(f"step {step:5d}  loss {loss.item():.4f}  l1 {l1.item():.4f}  gaussians {len(params['means'])/1e6:.2f}M  "
              f"{el:.0f}s elapsed, ETA {el / (step + 1) * (args.steps - step - 1):.0f}s", flush=True)

train_time = time.time() - t_start
print(f"Training done in {train_time / 60:.1f} min")

# ---------------- eval ----------------
@torch.no_grad()
def evaluate():
    ps, ss, drel = [], [], []
    for j, i in enumerate(test_ids):
        rgb_r, dep_r, _, _ = render(w2cs[i:i + 1], args.sh_degree)
        gt = IMG(i).float() / 255.0
        mse = ((rgb_r - gt) ** 2).mean()
        ps.append(float(-10 * torch.log10(mse)))
        ss.append(float(ssim(rgb_r.permute(2, 0, 1)[None], gt.permute(2, 0, 1)[None], data_range=1.0)))
        m = DW(i) >= 255                                      # stereo-measured pixels only
        if m.sum() > 100:
            dtf = DEP(i).float()
            drel.append(float(((dep_r[m] - dtf[m]).abs() / dtf[m]).median()))
        if j % max(1, len(test_ids) // 6) == 0:
            dv = (dep_r / 5.0).clamp(0, 1).cpu().numpy()
            dv = cv2.applyColorMap((dv * 255).astype(np.uint8), cv2.COLORMAP_TURBO)
            row = np.hstack([(gt.cpu().numpy() * 255).astype(np.uint8)[..., ::-1],
                             (rgb_r.cpu().numpy() * 255).astype(np.uint8)[..., ::-1], dv])
            cv2.imwrite(os.path.join(OUT, "renders", f"test_{frames[i]['name']}.jpg"), row)
    return np.mean(ps), np.mean(ss), (np.median(drel) if drel else float("nan"))


@torch.no_grad()
def train_fit(n=40):
    """PSNR on training views (with their learned exposure): the model must at least fit what it saw."""
    ids = train_ids[:: max(1, len(train_ids) // n)]
    ps = []
    for i in ids:
        rgb_r, _, _, _ = render(get_w2c(i), args.sh_degree)
        if args.exposure:
            rgb_r = (rgb_r * torch.exp(expo[i, :3]) + expo[i, 3:]).clamp(0, 1)
        ps.append(float(-10 * torch.log10(((rgb_r - IMG(i).float() / 255.0) ** 2).mean())))
    return np.mean(ps)


psnr, ssim_v, drel = evaluate() if test_ids else (float("nan"),) * 3
pose_shift = pose_delta[:, 3:].norm(dim=1)
train_psnr = train_fit()
print(f"TRAIN-VIEW PSNR {train_psnr:.2f} dB (target > 27: the model must reproduce what it saw)")
print(f"TEST  PSNR {psnr:.2f}  SSIM {ssim_v:.3f}  depth rel.err (stereo pixels) {drel * 100:.1f}%  | "
      f"pose corrections: median {pose_shift.median() * 1000:.1f} mm, max {pose_shift.max() * 1000:.1f} mm")

# ---------------- prune splats far from the fused surface (residual floaters) ----------------
keep_np = None
if args.prune_dist > 0 and os.path.exists(os.path.join(args.work, "fused_mesh.ply")):
    import open3d as o3d
    mesh = o3d.io.read_triangle_mesh(os.path.join(args.work, "fused_mesh.ply"))
    rs = o3d.t.geometry.RaycastingScene(); rs.add_triangles(o3d.t.geometry.TriangleMesh.from_legacy(mesh))
    dist = rs.compute_distance(o3d.core.Tensor(params["means"].detach().cpu().numpy().astype(np.float32))).numpy()
    keep_np = dist <= args.prune_dist
    print(f"pruned {(~keep_np).sum()} splats (> {args.prune_dist * 100:.0f} cm from fused surface)")

# ---------------- export (INRIA 3DGS ply, ARCore world: metres, +Y up) ----------------
with torch.no_grad():
    xyz = params["means"].cpu().numpy()
    f_dc = params["sh0"].squeeze(1).cpu().numpy()
    f_rest = params["shN"].transpose(1, 2).reshape(len(xyz), -1).cpu().numpy()
    op = params["opacities"][:, None].cpu().numpy()
    sc = params["scales"].cpu().numpy()
    q = F.normalize(params["quats"], dim=-1).cpu().numpy()
if keep_np is not None:
    xyz, f_dc, f_rest, op, sc, q = xyz[keep_np], f_dc[keep_np], f_rest[keep_np], op[keep_np], sc[keep_np], q[keep_np]
attrs = (["x", "y", "z", "nx", "ny", "nz"] + [f"f_dc_{i}" for i in range(3)] +
         [f"f_rest_{i}" for i in range(f_rest.shape[1])] + ["opacity"] +
         [f"scale_{i}" for i in range(3)] + [f"rot_{i}" for i in range(4)])
data = np.concatenate([xyz, np.zeros_like(xyz), f_dc, f_rest, op, sc, q], 1).astype(np.float32)
el = np.empty(len(xyz), dtype=[(a, "f4") for a in attrs])
for j, a in enumerate(attrs):
    el[a] = data[:, j]
PlyData([PlyElement.describe(el, "vertex")]).write(os.path.join(OUT, "splat.ply"))
# poses refined during training (pose_opt): without them, evaluation renders at slightly wrong poses
with torch.no_grad():
    fr_out = json.loads(json.dumps(meta)); fr_out["frames"] = [dict(f) for f in frames]
    for k in range(N):
        c2w_cv = torch.linalg.inv(get_w2c(k)[0]).cpu().numpy()
        fr_out["frames"][k]["c2w"] = (c2w_cv @ GL_TO_CV).tolist()
    json.dump(fr_out, open(os.path.join(OUT, "frames_refined.json"), "w"), indent=1)
json.dump({"psnr": psnr, "ssim": ssim_v, "depth_rel_err": drel, "train_minutes": train_time / 60,
           "gaussians": len(xyz), "steps": args.steps, "train_view_psnr": train_psnr,
           "antialiased": bool(args.antialiased)}, open(os.path.join(OUT, "metrics.json"), "w"), indent=1)
print("Exported", os.path.join(OUT, "splat.ply"))
