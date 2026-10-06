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
ap.add_argument("--steps", type=int, default=7000)
ap.add_argument("--downscale", type=int, default=2)
ap.add_argument("--depth_w", type=float, default=0.5, help="initial depth loss weight")
ap.add_argument("--depth_w_final", type=float, default=0.05)
ap.add_argument("--flat_w", type=float, default=1.0)
ap.add_argument("--pose_opt", type=int, default=1)
ap.add_argument("--exposure", type=int, default=1)
ap.add_argument("--antialiased", type=int, default=1)
ap.add_argument("--prune_dist", type=float, default=0.10, help="after training drop splats farther than this (m) from the fused surface; 0=off")
ap.add_argument("--test_every", type=int, default=10)
ap.add_argument("--sh_degree", type=int, default=3)
args = ap.parse_args()

dev = torch.device("cuda")
torch.manual_seed(0)
OUT = args.out or os.path.join(args.work, "gs")
os.makedirs(os.path.join(OUT, "renders"), exist_ok=True)
meta = json.load(open(os.path.join(args.work, "frames.json")))
frames = meta["frames"]
ds = args.downscale
W, H = meta["W"] // ds, meta["H"] // ds
K = torch.tensor([[meta["fx"] / ds, 0, meta["cx"] / ds], [0, meta["fy"] / ds, meta["cy"] / ds], [0, 0, 1]],
                 dtype=torch.float32, device=dev)
GL_TO_CV = np.diag([1.0, -1.0, -1.0, 1.0])

# ---------------- data ----------------
imgs, depths, w2cs = [], [], []
for f in frames:
    im = cv2.imread(os.path.join(args.work, "images", f["name"] + ".jpg"))
    im = cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA)
    imgs.append(torch.from_numpy(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)))
    d = np.load(os.path.join(args.work, "depth_fused", f["name"] + ".npy")).astype(np.float32)
    if d.shape != (H, W):
        d = cv2.resize(d, (W, H), interpolation=cv2.INTER_NEAREST)
    depths.append(torch.from_numpy(d))
    c2w = np.array(f["c2w"]) @ GL_TO_CV                     # OpenGL cam -> OpenCV cam
    w2cs.append(torch.from_numpy(np.linalg.inv(c2w)).float())
imgs = torch.stack(imgs).to(dev)                              # uint8 [N,H,W,3]
depths = torch.stack(depths).to(dev)                          # [N,H,W], 0 = no surface
w2cs = torch.stack(w2cs).to(dev)
N = len(frames)
test_ids = list(range(0, N, args.test_every)) if args.test_every > 0 else []
train_ids = [i for i in range(N) if i not in set(test_ids)]
cam_centers = torch.linalg.inv(w2cs)[:, :3, 3]
scene_scale = float((cam_centers - cam_centers.mean(0)).norm(dim=1).max()) * 1.1
print(flush=True); print(f"{N} frames ({len(train_ids)} train / {len(test_ids)} test) at {W}x{H}, scene scale {scene_scale:.2f} m")

# ---------------- init gaussians ----------------
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
C0 = 0.28209479177387814
n_sh = (args.sh_degree + 1) ** 2
params = torch.nn.ParameterDict({
    "means": torch.nn.Parameter(xyz),
    "scales": torch.nn.Parameter(init_logscale),
    "quats": torch.nn.Parameter(init_quats),
    "opacities": torch.nn.Parameter(torch.logit(torch.full((len(xyz),), 0.5, device=dev))),
    "sh0": torch.nn.Parameter(((rgb - 0.5) / C0)[:, None, :]),
    "shN": torch.nn.Parameter(torch.zeros(len(xyz), n_sh - 1, 3, device=dev)),
})
lrs = {"means": 1.6e-4 * scene_scale, "scales": 5e-3, "quats": 1e-3, "opacities": 5e-2, "sh0": 2.5e-3, "shN": 2.5e-3 / 20}
optimizers = {k: torch.optim.Adam([params[k]], lr=lrs[k], eps=1e-15) for k in params}
means_sched = torch.optim.lr_scheduler.ExponentialLR(optimizers["means"], gamma=0.01 ** (1.0 / args.steps))

strategy = DefaultStrategy(refine_start_iter=500, refine_stop_iter=int(args.steps * 0.7), reset_every=3000,
                           refine_every=100, prune_opa=0.005, grow_grad2d=0.0002, verbose=False)
strategy.check_sanity(params, optimizers)
state = strategy.initialize_state(scene_scale=scene_scale)

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


def render(w2c, sh_deg):
    colors = torch.cat([params["sh0"], params["shN"]], 1)
    out, alpha, info = rasterization(
        params["means"], F.normalize(params["quats"], dim=-1), torch.exp(params["scales"]),
        torch.sigmoid(params["opacities"]), colors, w2c, K[None], W, H,
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
    rgb_r, dep_r, alpha_r, info = render(w2c, sh_deg)
    strategy.step_pre_backward(params, optimizers, state, step, info)

    gt = imgs[i].float() / 255.0
    if args.exposure:
        rgb_r = rgb_r * torch.exp(expo[i, :3]) + expo[i, 3:]
    l1 = (rgb_r - gt).abs().mean()
    ssim_l = 1 - ssim(rgb_r.permute(2, 0, 1)[None], gt.permute(2, 0, 1)[None], data_range=1.0, size_average=True)
    loss = 0.8 * l1 + 0.2 * ssim_l

    # depth: relative L1 against the fused (multi-view consistent) depth
    dt = depths[i]
    m = dt > 0
    a = min(step / (0.6 * args.steps), 1.0)
    dw = args.depth_w * (1 - a) + args.depth_w_final * a
    if m.any():
        loss = loss + dw * ((dep_r[m] - dt[m]).abs() / dt[m]).mean()

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
    strategy.step_post_backward(params, optimizers, state, step, info, packed=False)

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
        gt = imgs[i].float() / 255.0
        mse = ((rgb_r - gt) ** 2).mean()
        ps.append(float(-10 * torch.log10(mse)))
        ss.append(float(ssim(rgb_r.permute(2, 0, 1)[None], gt.permute(2, 0, 1)[None], data_range=1.0)))
        m = depths[i] > 0
        drel.append(float(((dep_r[m] - depths[i][m]).abs() / depths[i][m]).median()))
        if j % max(1, len(test_ids) // 6) == 0:
            dv = (dep_r / 5.0).clamp(0, 1).cpu().numpy()
            dv = cv2.applyColorMap((dv * 255).astype(np.uint8), cv2.COLORMAP_TURBO)
            row = np.hstack([(gt.cpu().numpy() * 255).astype(np.uint8)[..., ::-1],
                             (rgb_r.cpu().numpy() * 255).astype(np.uint8)[..., ::-1], dv])
            cv2.imwrite(os.path.join(OUT, "renders", f"test_{frames[i]['name']}.jpg"), row)
    return np.mean(ps), np.mean(ss), np.median(drel)


psnr, ssim_v, drel = evaluate() if test_ids else (float("nan"),) * 3
pose_shift = pose_delta[:, 3:].norm(dim=1)
print(f"TEST  PSNR {psnr:.2f}  SSIM {ssim_v:.3f}  depth rel.err {drel * 100:.1f}%  | "
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
json.dump({"psnr": psnr, "ssim": ssim_v, "depth_rel_err": drel, "train_minutes": train_time / 60,
           "gaussians": len(xyz), "steps": args.steps,
           "antialiased": bool(args.antialiased)}, open(os.path.join(OUT, "metrics.json"), "w"), indent=1)
print("Exported", os.path.join(OUT, "splat.ply"))
