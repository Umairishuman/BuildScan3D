"""Stage 3: depth-supervised 3D Gaussian Splatting on an ARCore capture (gsplat).

Photometric loss does the work; geometry only keeps splats on real surfaces:
  * init from the fused TSDF surface (init.ply), not from stacked per-frame depth
  * depth loss against each frame's OWN depth (depth_mvs), weighted by mvs_mask: pixels stereo actually
    measured count fully, filled-in pixels count little (and not at all in frames fusion rejected).
    The fused TSDF render (depth_fused) is only an optional target (--depth_src fused): it carves away
    foreground objects that other views see through, which made the old trainer underfit.
  * the depth and flatness losses fade out early so photometric detail wins
  * schedule scales with the number of frames (but not too long: 15k steps over 186 frames overfit), low-res first, full-res final phase
  * flatness regulariser: the smallest scale axis of each Gaussian is pushed down (surfels on
    surfaces, like PGSR / 2DGS-style flattening) and extreme anisotropy is penalised
  * optional per-camera pose refinement and per-image exposure / white balance
  * checkpoints (--ckpt_every, --max_minutes) so a stopped session (Kaggle) can resume with --resume 1
Everything stays in ARCore world coordinates: metres, +Y up.

Run with nerfstudio-env python inside the MSVC environment (see run_arcore3dgs.bat).
"""
import os, sys, json, math, time, argparse, functools, gc
print = functools.partial(print, flush=True)
import numpy as np, cv2, torch, torch.nn.functional as F
from plyfile import PlyData, PlyElement
from gsplat import rasterization
from gsplat.strategy import DefaultStrategy
from pytorch_msssim import ssim

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--out", default=None)
ap.add_argument("--steps", type=int, default=0, help="0 = auto: max(7000, 15 x training frames); more steps overfit small captures")
ap.add_argument("--ds_start", type=int, default=2, help="image downscale for the first phase")
ap.add_argument("--ds_end", type=int, default=1, help="image downscale for the final phase (1 = full resolution)")
ap.add_argument("--hires_frac", type=float, default=0.6, help="fraction of steps after which training switches to ds_end")
ap.add_argument("--depth_src", choices=["mvs", "fused"], default="mvs")
ap.add_argument("--depth_w", type=float, default=0.1, help="initial depth loss weight")
ap.add_argument("--depth_w_final", type=float, default=0.0)
ap.add_argument("--depth_fade", type=float, default=0.35, help="fraction of steps over which the depth weight fades to its final value")
ap.add_argument("--fill_w", type=float, default=0.1, help="weight of filled-in (not stereo-measured) depth pixels relative to measured ones")
ap.add_argument("--flat_w", type=float, default=0.1)
ap.add_argument("--flat_stop", type=float, default=0.7, help="flatness weight fades to 0 at this fraction of steps")
ap.add_argument("--init_opacity", type=float, default=0.1)
ap.add_argument("--refine_stop_frac", type=float, default=0.6, help="densification stops at this fraction of steps")
ap.add_argument("--pose_opt", type=int, default=1)
ap.add_argument("--exposure", type=int, default=1)
ap.add_argument("--antialiased", type=int, default=1)
ap.add_argument("--prune_dist", type=float, default=0.0, help="after training drop splats farther than this (m) from the fused surface; 0=off (default: it deletes thin objects the mesh lacks)")
ap.add_argument("--test_every", type=int, default=10)
ap.add_argument("--sh_degree", type=int, default=3)
ap.add_argument("--ckpt_every", type=int, default=2000, help="save a resumable checkpoint every N steps (0 = off)")
ap.add_argument("--resume", type=int, default=1, help="continue from <out>/ckpt.pt if it exists")
ap.add_argument("--max_minutes", type=float, default=0, help="stop gracefully (checkpoint saved) after this many minutes; 0 = no limit")
args = ap.parse_args()

dev = torch.device("cuda")
torch.manual_seed(0)
OUT = args.out or os.path.join(args.work, "gs")
os.makedirs(os.path.join(OUT, "renders"), exist_ok=True)
CKPT = os.path.join(OUT, "ckpt.pt")
meta = json.load(open(os.path.join(args.work, "frames.json")))
frames = meta["frames"]
dropped = set(meta.get("fusion_dropped", []))
GL_TO_CV = np.diag([1.0, -1.0, -1.0, 1.0])
DEPTH_DIR = "depth_mvs" if args.depth_src == "mvs" else "depth_fused"
WLUT = torch.tensor([0.0, args.fill_w, 1.0], device=dev)       # weight code 0 = no depth, 1 = filled, 2 = measured


# ---------------- data ----------------
def load_view(ds):
    """All per-frame tensors stay on the CPU and are moved to the GPU one frame at a time."""
    W, H = meta["W"] // ds, meta["H"] // ds
    K = torch.tensor([[meta["fx"] / ds, 0, meta["cx"] / ds], [0, meta["fy"] / ds, meta["cy"] / ds], [0, 0, 1]],
                     dtype=torch.float32, device=dev)
    imgs, deps, wgts = [], [], []
    for f in frames:
        im = cv2.imread(os.path.join(args.work, "images", f["name"] + ".jpg"))
        if im.shape[:2] != (H, W):
            im = cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA)
        imgs.append(torch.from_numpy(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)))
        d = np.load(os.path.join(args.work, DEPTH_DIR, f["name"] + ".npy")).astype(np.float32)
        code = (d > 0).astype(np.uint8) * 2
        mp = os.path.join(args.work, "mvs_mask", f["name"] + ".npy")
        if args.depth_src == "mvs" and os.path.exists(mp):
            measured = np.load(mp).astype(bool)
            code = np.where(d > 0, np.where(measured, 2, 0 if f["name"] in dropped else 1), 0).astype(np.uint8)
        if d.shape != (H, W):
            d = cv2.resize(d, (W, H), interpolation=cv2.INTER_NEAREST)
            code = cv2.resize(code, (W, H), interpolation=cv2.INTER_NEAREST)
        deps.append(torch.from_numpy(d.astype(np.float16)))
        wgts.append(torch.from_numpy(code))
    return dict(ds=ds, W=W, H=H, K=K, imgs=imgs, deps=deps, wgts=wgts)


def view_for_step(step):
    return args.ds_end if step >= int(args.hires_frac * args.steps) else args.ds_start


w2cs = []
for f in frames:
    c2w = np.array(f["c2w"]) @ GL_TO_CV                         # OpenGL cam -> OpenCV cam
    w2cs.append(torch.from_numpy(np.linalg.inv(c2w)).float())
w2cs = torch.stack(w2cs).to(dev)
N = len(frames)
test_ids = list(range(0, N, args.test_every)) if args.test_every > 0 else []
test_set = set(test_ids)
train_ids = [i for i in range(N) if i not in test_set]
cam_centers = torch.linalg.inv(w2cs)[:, :3, 3]
scene_scale = float((cam_centers - cam_centers.mean(0)).norm(dim=1).max()) * 1.1

ck = None
if args.resume and os.path.exists(CKPT):
    ck = torch.load(CKPT, map_location="cpu", weights_only=False)
    args.steps = ck["steps"]
    print(f"RESUMING from {CKPT} at step {ck['step']} / {args.steps}")
elif args.steps <= 0:
    args.steps = max(7000, 15 * len(train_ids))
print(f"{N} frames ({len(train_ids)} train / {len(test_ids)} test), scene scale {scene_scale:.2f} m, {args.steps} steps, "
      f"depth target {DEPTH_DIR}, {len(dropped)} fusion-rejected frames")
start_step = ck["step"] if ck else 0
view = load_view(view_for_step(start_step))
print(f"training view: {view['W']}x{view['H']}")

# ---------------- gaussians ----------------
C0 = 0.28209479177387814
n_sh = (args.sh_degree + 1) ** 2
if ck:
    params = torch.nn.ParameterDict({k: torch.nn.Parameter(v.to(dev)) for k, v in ck["params"].items()})
else:
    ply = PlyData.read(os.path.join(args.work, "init.ply"))["vertex"]
    xyz = torch.tensor(np.stack([ply["x"], ply["y"], ply["z"]], 1), dtype=torch.float32, device=dev)
    rgb = torch.tensor(np.stack([ply["red"], ply["green"], ply["blue"]], 1) / 255.0, dtype=torch.float32, device=dev)
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
        init_logscale = torch.log(torch.stack([nn, nn, nn * 0.1], 1))
        print("init: surface-aligned discs from mesh normals")
    else:
        init_quats = F.normalize(torch.randn(len(xyz), 4, device=dev), dim=-1)
        init_logscale = torch.log(nn)[:, None].repeat(1, 3)
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

strategy = DefaultStrategy(refine_start_iter=500, refine_stop_iter=int(args.steps * args.refine_stop_frac), reset_every=3000,
                           refine_every=100, prune_opa=0.005, grow_grad2d=0.0002, verbose=False)
strategy.check_sanity(params, optimizers)
state = strategy.initialize_state(scene_scale=scene_scale)

# per-camera pose residual (axis-angle + translation), applied as w2c' = dT @ w2c
pose_delta = torch.nn.Parameter(torch.zeros(N, 6, device=dev))
# per-image exposure / white-balance: rgb' = rgb * exp(gain) + bias (absorbs ARCore auto-exposure)
expo = torch.nn.Parameter(torch.zeros(N, 6, device=dev))
expo_optim = torch.optim.Adam([expo], lr=1e-3 if args.exposure else 0.0)
pose_optim = torch.optim.Adam([pose_delta], lr=1e-4 if args.pose_opt else 0.0, weight_decay=0)

if ck:
    for k, o in optimizers.items():
        o.load_state_dict(ck["opt"][k])
    means_sched.load_state_dict(ck["sched"])
    for k, v in ck["strategy"].items():
        state[k] = v.to(dev) if torch.is_tensor(v) else v
    pose_delta.data.copy_(ck["pose_delta"].to(dev)); expo.data.copy_(ck["expo"].to(dev))
    pose_optim.load_state_dict(ck["pose_optim"]); expo_optim.load_state_dict(ck["expo_optim"])
    del ck
    gc.collect()


def save_ckpt(step):
    """Atomic write so a killed session never leaves a half-written checkpoint."""
    ck_new = dict(step=step, steps=args.steps, args=vars(args),
                  params={k: v.detach().cpu() for k, v in params.items()},
                  opt={k: o.state_dict() for k, o in optimizers.items()}, sched=means_sched.state_dict(),
                  strategy={k: (v.cpu() if torch.is_tensor(v) else v) for k, v in state.items()},
                  pose_delta=pose_delta.detach().cpu(), expo=expo.detach().cpu(),
                  pose_optim=pose_optim.state_dict(), expo_optim=expo_optim.state_dict())
    torch.save(ck_new, CKPT + ".tmp")
    os.replace(CKPT + ".tmp", CKPT)
    print(f"checkpoint saved at step {step} ({os.path.getsize(CKPT) / 1e6:.0f} MB)")


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


def render(w2c, sh_deg):
    colors = torch.cat([params["sh0"], params["shN"]], 1)
    out, alpha, info = rasterization(
        params["means"], F.normalize(params["quats"], dim=-1), torch.exp(params["scales"]),
        torch.sigmoid(params["opacities"]), colors, w2c, view["K"][None], view["W"], view["H"],
        sh_degree=sh_deg, near_plane=0.05, far_plane=50.0, render_mode="RGB+ED", packed=False,
        rasterize_mode="antialiased" if args.antialiased else "classic")
    return out[0, ..., :3].clamp(0, 1), out[0, ..., 3], alpha[0, ..., 0], info


def frame_gt(i):
    return (view["imgs"][i].to(dev).float() / 255.0,
            view["deps"][i].to(dev).float(), WLUT[view["wgts"][i].to(dev).long()])


# ---------------- train ----------------
t_start = time.time()
order = []
stopped_early = False
for step in range(start_step, args.steps):
    want = view_for_step(step)
    if want != view["ds"]:
        del view
        gc.collect()
        view = load_view(want)
        print(f"step {step}: switched to {view['W']}x{view['H']}")
    if args.max_minutes > 0 and time.time() - t_start > args.max_minutes * 60:
        save_ckpt(step)
        print(f"time budget reached at step {step}; rerun the same command with --resume 1 to continue")
        stopped_early = True
        break
    if not order:
        order = list(np.random.permutation(train_ids))
    i = order.pop()
    sh_deg = min(step // 1000, args.sh_degree)
    w2c = get_w2c(i)
    rgb_r, dep_r, alpha_r, info = render(w2c, sh_deg)
    strategy.step_pre_backward(params, optimizers, state, step, info)

    gt, dt, wt = frame_gt(i)
    if args.exposure:
        rgb_r = rgb_r * torch.exp(expo[i, :3]) + expo[i, 3:]
    l1 = (rgb_r - gt).abs().mean()
    ssim_l = 1 - ssim(rgb_r.permute(2, 0, 1)[None], gt.permute(2, 0, 1)[None], data_range=1.0, size_average=True)
    loss = 0.8 * l1 + 0.2 * ssim_l

    # depth: relative L1 against the frame's own depth, per-pixel confidence weights
    a = min(step / max(args.depth_fade * args.steps, 1), 1.0)
    dw = args.depth_w * (1 - a) + args.depth_w_final * a
    if dw > 0 and wt.sum() > 0:
        loss = loss + dw * (wt * (dep_r - dt).abs() / dt.clamp_min(1e-3)).sum() / wt.sum()

    # flatten gaussians onto surfaces + limit needles (fades out so it cannot fight photometric detail)
    fw = args.flat_w * max(0.0, 1 - step / max(args.flat_stop * args.steps, 1))
    if fw > 0:
        sc = torch.exp(params["scales"])
        smin = sc.min(dim=1).values
        loss = loss + fw * smin.mean()
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
    strategy.step_post_backward(params, optimizers, state, step, info, packed=False)

    if step % 250 == 0 or step == args.steps - 1:
        el = time.time() - t_start
        done = step - start_step + 1
        print(f"step {step:6d}/{args.steps}  loss {loss.item():.4f}  l1 {l1.item():.4f}  gaussians {len(params['means'])/1e6:.2f}M  "
              f"{el:.0f}s elapsed, ETA {el / done * (args.steps - step - 1):.0f}s")
    if args.ckpt_every > 0 and (step + 1) % args.ckpt_every == 0 and step + 1 < args.steps:
        save_ckpt(step + 1)

if stopped_early:
    sys.exit(0)
train_time = time.time() - t_start
print(f"Training done in {train_time / 60:.1f} min")
if args.ckpt_every > 0:
    save_ckpt(args.steps)


# ---------------- eval ----------------
@torch.no_grad()
def evaluate():
    ps_te, ss, drel, ps_tr = [], [], [], []
    for j, i in enumerate(test_ids):
        rgb_r, dep_r, _, _ = render(w2cs[i:i + 1], args.sh_degree)
        gt, dt, wt = frame_gt(i)
        ps_te.append(float(-10 * torch.log10(((rgb_r - gt) ** 2).mean())))
        ss.append(float(ssim(rgb_r.permute(2, 0, 1)[None], gt.permute(2, 0, 1)[None], data_range=1.0)))
        m = wt >= 1.0
        if m.any():
            drel.append(float(((dep_r[m] - dt[m]).abs() / dt[m]).median()))
        if j % max(1, len(test_ids) // 6) == 0:
            dv = (dep_r / 5.0).clamp(0, 1).cpu().numpy()
            dv = cv2.applyColorMap((dv * 255).astype(np.uint8), cv2.COLORMAP_TURBO)
            row = np.hstack([(gt.cpu().numpy() * 255).astype(np.uint8)[..., ::-1],
                             (rgb_r.cpu().numpy() * 255).astype(np.uint8)[..., ::-1], dv])
            row = cv2.resize(row, (row.shape[1] // 2, row.shape[0] // 2), interpolation=cv2.INTER_AREA) if view["ds"] == 1 else row
            cv2.imwrite(os.path.join(OUT, "renders", f"test_{frames[i]['name']}.jpg"), row)
    # fit on the TRAINING views (with the learned exposure): the number that exposed the underfitting
    for i in train_ids[::max(1, len(train_ids) // 25)]:
        rgb_r, _, _, _ = render(get_w2c(i, refine=True), args.sh_degree)
        if args.exposure:
            rgb_r = rgb_r * torch.exp(expo[i, :3]) + expo[i, 3:]
        gt, _, _ = frame_gt(i)
        ps_tr.append(float(-10 * torch.log10(((rgb_r.clamp(0, 1) - gt) ** 2).mean())))
    return np.mean(ps_te), np.mean(ss), (np.median(drel) if drel else float("nan")), np.mean(ps_tr)


psnr, ssim_v, drel, psnr_train = evaluate() if test_ids else (float("nan"),) * 4
pose_shift = pose_delta[:, 3:].norm(dim=1)
print(f"TRAIN-view PSNR {psnr_train:.2f} dB (with learned exposure)")
print(f"TEST  PSNR {psnr:.2f}  SSIM {ssim_v:.3f}  depth rel.err {drel * 100:.1f}%  | "
      f"pose corrections: median {pose_shift.median() * 1000:.1f} mm, max {pose_shift.max() * 1000:.1f} mm")

# ---------------- optional: prune splats far from the fused surface ----------------
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
invisible = (1 / (1 + np.exp(-op[:, 0]))) < 0.005
keep_all = ~invisible if keep_np is None else (keep_np & ~invisible)
xyz, f_dc, f_rest, op, sc, q = xyz[keep_all], f_dc[keep_all], f_rest[keep_all], op[keep_all], sc[keep_all], q[keep_all]
attrs = (["x", "y", "z", "nx", "ny", "nz"] + [f"f_dc_{i}" for i in range(3)] +
         [f"f_rest_{i}" for i in range(f_rest.shape[1])] + ["opacity"] +
         [f"scale_{i}" for i in range(3)] + [f"rot_{i}" for i in range(4)])
data = np.concatenate([xyz, np.zeros_like(xyz), f_dc, f_rest, op, sc, q], 1).astype(np.float32)
el = np.empty(len(xyz), dtype=[(a, "f4") for a in attrs])
for j, a in enumerate(attrs):
    el[a] = data[:, j]
PlyData([PlyElement.describe(el, "vertex")]).write(os.path.join(OUT, "splat.ply"))
json.dump({"psnr": psnr, "ssim": ssim_v, "psnr_train": psnr_train, "depth_rel_err": drel, "train_minutes": train_time / 60,
           "gaussians": len(xyz), "steps": args.steps, "antialiased": bool(args.antialiased),
           "depth_src": args.depth_src, "config": {k: v for k, v in vars(args).items() if k not in ("work", "out")}},
          open(os.path.join(OUT, "metrics.json"), "w"), indent=1)
print("Exported", os.path.join(OUT, "splat.ply"))
