"""Geometry-regularised splatfacto (v8geo): SfM-anchored monocular depth + normal priors.

Why: far walls and corners are not flat when viewed off the camera path. Plain walls give the photometric
loss nothing to lock onto, so splats spread in depth (fuzzy walls, bent corners). DN-Splatter / PlanarGS /
Textureless-Splatter show that monocular depth + normal priors fix exactly this in indoor scenes; anchoring
the monocular depth to metric SfM points (mono_prior.py) removes its scale error.

Losses added to splatfacto (after `geo_start` steps, at the prior's 1/4 resolution):
  depth : |D_render - D_prior| / D_prior on valid, opaque pixels                 (weight depth_lambda)
  normal: (1 - n_render . n_prior) * (1 - |grad I|)^2 on valid, opaque pixels      (weight normal_lambda)
          n_render = normals of the rendered depth (finite differences, PGSR single-view style); the
          edge-aware weight keeps real corners / object edges sharp.
  planar: per-frame planar regions (plane_seg.py: walls, floor, ceiling, doors) -> the rendered 3D points of
          each region are pulled onto their own best-fit plane (PlanarGS-style flattening; only the region
          masks come from the prior, the plane itself is fitted to the render, so mono scale/tilt errors
          cannot bend the wall)                                                     (weight planar_lambda)
PGSR-lite (--pgsr; PGSR, Chen et al. TVCG 2024, without its multi-view terms): Gaussians are flattened into discs
(min-scale loss, flat_lambda); from pgsr_start a second, cheap pass at the prior's 1/4 resolution renders each
disc's normal and camera-to-plane distance, giving PGSR's unbiased depth (ray / plane intersection -- ON the
surface, unlike alpha-blended depth). The depth / normal / planar losses then use the unbiased depth and the
rendered normals, plus PGSR's single-view consistency: normals of the unbiased depth must match the rendered
normals (edge-aware, sv_lambda). splatfacto's scale regularisation (max/min < 10) would forbid discs, so it is
replaced by a max/middle-scale limit. Meshes: mesh.py --depth unbiased.
Motion blur (blur_motion.py, "Gaussian Splatting on the Move"-style): a training frame is rendered at 2-5 poses
spread over the exposure along the camera's ARCore velocity and the renders are averaged, so the sharp model
explains the blurred photo instead of being blurred itself (blur_exposure > 0).
Everything else is the v6 recipe. Run (nerfstudio-env python, from the repo root):

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/geo_splatfacto.py --data <work_sfm>/transforms_offpath.json
      --name v8geo --iters 30000 [--depth_lambda 0.05 --normal_lambda 0.05]
Export afterwards with PYTHONPATH=src/arcore3dgs (the config references this module).
"""
import os, sys, json, copy, argparse
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Type

import numpy as np
import torch
import torch.nn.functional as F
from nerfstudio.models.splatfacto import SplatfactoModel, SplatfactoModelConfig


@dataclass
class GeoSplatfactoModelConfig(SplatfactoModelConfig):
    _target: Type = field(default_factory=lambda: GeoSplatfactoModel)
    prior_file: str = ""
    depth_lambda: float = 0.05
    normal_lambda: float = 0.05
    geo_start: int = 1000
    output_depth_during_training: bool = True
    # DashGaussian-style resolution schedule "step:factor,step:factor,..." (empty = splatfacto default)
    dash_schedule: str = ""
    planar_lambda: float = 0.0
    blur_exposure: float = 0.0       # s; 0 = no motion-blur model
    blur_start: int = 0
    blur_px_per_sub: float = 3.0     # one extra sub-render per this many px of blur (at the current resolution)
    blur_max_sub: int = 5
    pgsr: bool = False
    flat_lambda: float = 100.0       # PGSR's minimum-scale loss weight
    sv_lambda: float = 0.05          # single-view depth-normal consistency
    pgsr_start: int = 3000


class GeoSplatfactoModel(SplatfactoModel):
    config: GeoSplatfactoModelConfig

    def populate_modules(self):
        super().populate_modules()
        self._geo_idx = None
        self.has_prior = bool(self.config.prior_file) and os.path.exists(self.config.prior_file)
        if self.has_prior:
            z = np.load(self.config.prior_file)
            self.prior_depth = torch.from_numpy(z["depth"])          # [N, h, w] float16 (CPU)
            self.prior_normal = torch.from_numpy(z["normal"])        # [N, h, w, 3] int8 x127
            self.prior_valid = torch.from_numpy(z["valid"])          # [N, h, w] bool
            self.prior_K = [float(v) for v in z["K"]]                # fx, fy, cx, cy at prior resolution
            self.prior_planes = torch.from_numpy(z["planes"]) if "planes" in z.files else None   # [N, h, w] uint8
            self.blur_motion = torch.from_numpy(z["motion"]).float() if "motion" in z.files else None  # [N, 6]
        self._blur_n = 1

    @staticmethod
    def _so3_exp(w):
        th = w.norm()
        if th < 1e-8:
            return torch.eye(3, device=w.device)
        k = w / th
        Kx = torch.zeros(3, 3, device=w.device)
        Kx[0, 1], Kx[0, 2], Kx[1, 0], Kx[1, 2], Kx[2, 0], Kx[2, 1] = -k[2], k[1], k[2], -k[0], -k[1], k[0]
        return torch.eye(3, device=w.device) + torch.sin(th) * Kx + (1 - torch.cos(th)) * Kx @ Kx

    def _get_downscale_factor(self):
        if self.training and self.config.dash_schedule:
            f = 1
            for item in self.config.dash_schedule.split(","):
                st, fac = item.split(":")
                if self.step >= int(st):
                    f = int(fac)
            return f
        return super()._get_downscale_factor()

    def get_outputs(self, camera):
        out = self._get_outputs(camera)
        if self.training and self.config.pgsr and self.has_prior and self.step >= self.config.pgsr_start:
            out["geo"] = self._render_geometry(camera)
        return out

    @staticmethod
    def _quat_to_rot(q):                                     # wxyz
        w, x, y, z = q.unbind(1)
        return torch.stack([1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y),
                            2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x),
                            2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)], 1).reshape(-1, 3, 3)

    def _render_geometry(self, camera):
        """PGSR pass at the prior resolution: rendered disc normals (camera frame, OpenCV axes, facing the
        camera), alpha and unbiased depth = (alpha-blended plane offset) / (alpha-blended normal . ray)"""
        from gsplat import rasterization
        from nerfstudio.models.splatfacto import get_viewmat
        h, w = self.prior_depth.shape[1:]
        fx, fy, cx, cy = self.prior_K
        viewmat = get_viewmat(camera.camera_to_worlds.to(self.device))
        Kp = torch.tensor([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=torch.float32, device=viewmat.device)[None]
        quats = self.quats / self.quats.norm(dim=-1, keepdim=True); scales = torch.exp(self.scales)
        R = self._quat_to_rot(quats)
        n_w = torch.gather(R, 2, scales.argmin(1)[:, None, None].expand(-1, 3, 1)).squeeze(2)
        Rv, tv = viewmat[0, :3, :3], viewmat[0, :3, 3]
        mc = self.means @ Rv.T + tv; nc = n_w @ Rv.T
        nc = torch.where((nc * mc).sum(1, keepdim=True) > 0, -nc, nc)
        geo = torch.cat([nc, (nc * mc).sum(1, keepdim=True)], 1)
        r, a, _ = rasterization(self.means, quats, scales, torch.sigmoid(self.opacities).squeeze(-1), geo, viewmat, Kp, w, h,
                                rasterize_mode=self.config.rasterize_mode)
        n_ = r[0, ..., :3]; d_ = r[0, ..., 3]; A = a[0, ..., 0]
        v, u = torch.meshgrid(torch.arange(h, device=A.device) + 0.5, torch.arange(w, device=A.device) + 0.5, indexing="ij")
        ray = torch.stack([(u - cx) / fx, (v - cy) / fy, torch.ones_like(u)], -1)
        D = d_ / (n_ * ray).sum(-1).clamp(max=-1e-4)
        return dict(normal=F.normalize(n_, dim=-1), depth=D, alpha=A)

    def _get_outputs(self, camera):
        if self.training and camera.metadata is not None and "cam_idx" in camera.metadata:
            self._geo_idx = int(camera.metadata["cam_idx"])
        self._blur_n = 1
        cfg = self.config
        if (self.training and cfg.blur_exposure > 0 and self.has_prior and self.blur_motion is not None
                and self._geo_idx is not None and self.step >= cfg.blur_start):
            m = self.blur_motion[self._geo_idx].to(camera.camera_to_worlds.device)
            w, v = m[:3], m[3:]
            px = float(w[:2].norm()) * cfg.blur_exposure * float(camera.fx) / self._get_downscale_factor()
            n = min(cfg.blur_max_sub, 1 + int(px / cfg.blur_px_per_sub))
            if n >= 2:
                from nerfstudio.cameras.cameras import Cameras
                taus = torch.linspace(-cfg.blur_exposure / 2, cfg.blur_exposure / 2, n).tolist()
                taus.sort(key=lambda t: -abs(t))                     # the most central pose is rendered last:
                c2w = camera.camera_to_worlds[0]                     # its info drives densification
                rgbs = []
                for t in taus:
                    Rd = self._so3_exp(w * t)
                    new = torch.cat([c2w[:, :3] @ Rd, (c2w[:, :3] @ (v * t) + c2w[:, 3])[:, None]], 1)[None]
                    cam = Cameras(camera_to_worlds=new, fx=camera.fx, fy=camera.fy, cx=camera.cx, cy=camera.cy,
                                  width=camera.width, height=camera.height, camera_type=camera.camera_type,
                                  metadata=camera.metadata)
                    out = super().get_outputs(cam)
                    rgbs.append(out["rgb"])
                out["rgb"] = torch.stack(rgbs).mean(0)
                self._blur_n = n
                return out
        return super().get_outputs(camera)

    def step_post_backward(self, step):
        # with n sub-renders the image-space gradient of the last (central) render is ~1/n of a normal step;
        # rescale it so densification keeps its usual threshold
        if self._blur_n > 1 and self.info is not None:
            m2d = self.info["means2d"]
            if m2d.grad is not None:
                m2d.grad.mul_(self._blur_n)
            if getattr(m2d, "absgrad", None) is not None:
                m2d.absgrad.mul_(self._blur_n)
        super().step_post_backward(step)

    def _points(self, D):
        fx, fy, cx, cy = self.prior_K
        h, w = D.shape
        v, u = torch.meshgrid(torch.arange(h, device=D.device) + 0.5, torch.arange(w, device=D.device) + 0.5, indexing="ij")
        return torch.stack([(u - cx) / fx * D, (v - cy) / fy * D, D], -1)

    def _normals(self, D):
        P = self._points(D)
        dx = torch.zeros_like(P); dy = torch.zeros_like(P)
        dx[:, 1:-1] = P[:, 2:] - P[:, :-2]
        dy[1:-1] = P[2:] - P[:-2]
        n = F.normalize(torch.cross(dx, dy, dim=-1), dim=-1)
        flip = ((n * P).sum(-1, keepdim=True) > 0).float()           # face the camera
        return n * (1 - 2 * flip)

    def _edge_weight(self, batch, h, w):
        """(1 - |grad I|)^2 at the prior resolution: geometry losses relax at image edges (corners, objects)"""
        gt = self.get_gt_img(batch["image"])[..., :3]
        g = F.interpolate(gt.permute(2, 0, 1)[None].mean(1, keepdim=True), (h, w), mode="area")[0, 0]
        gx = torch.zeros_like(g); gy = torch.zeros_like(g)
        gx[:, 1:-1] = (g[:, 2:] - g[:, :-2]).abs(); gy[1:-1] = (g[2:] - g[:-2]).abs()
        grad = (gx + gy).clamp(max=1.0)
        return (1 - grad / (grad.max() + 1e-6)) ** 2

    def get_loss_dict(self, outputs, batch, metrics_dict=None):
        loss = super().get_loss_dict(outputs, batch, metrics_dict)
        cfg = self.config
        if self.training and cfg.pgsr:
            sc = torch.exp(self.scales).sort(dim=1).values      # ascending
            loss["flat"] = cfg.flat_lambda * sc[:, 0].mean()
            loss["disc_aniso"] = 0.1 * torch.relu(sc[:, 2] / sc[:, 1].clamp(min=1e-8) - 10).mean()
        if not (self.training and self.has_prior and self._geo_idx is not None and self.step >= cfg.geo_start):
            return loss
        D = outputs.get("depth")
        if D is None:
            return loss
        i = self._geo_idx
        h, w = self.prior_depth.shape[1:]
        geo = outputs.get("geo")
        if geo is not None:                                  # PGSR: unbiased depth + rendered disc normals
            Dr, Ar, Nr = geo["depth"], geo["alpha"], geo["normal"]
        else:
            Dr = F.interpolate(D[..., 0][None, None], (h, w), mode="area")[0, 0]
            Ar = F.interpolate(outputs["accumulation"][..., 0][None, None], (h, w), mode="area")[0, 0]
            Nr = None
        Dp = self.prior_depth[i].to(self.device).float()
        V = self.prior_valid[i].to(self.device) & (Ar > 0.9) & (Dr > 0.05) & (Dr < 20)
        V[:2] = False; V[-2:] = False; V[:, :2] = False; V[:, -2:] = False
        if V.sum() < 100:
            return loss
        if cfg.depth_lambda > 0:
            loss["depth_prior"] = cfg.depth_lambda * ((Dr - Dp).abs() / Dp.clamp(min=0.1))[V].mean()
        wgt = self._edge_weight(batch, h, w) if (cfg.normal_lambda > 0 or geo is not None) else None
        Nd = self._normals(Dr)                               # normals of the (unbiased) depth
        if cfg.normal_lambda > 0:
            Np = self.prior_normal[i].to(self.device).float() / 127.0
            loss["normal_prior"] = cfg.normal_lambda * (wgt * (1 - ((Nr if Nr is not None else Nd) * Np).sum(-1)))[V].mean()
        if geo is not None and cfg.sv_lambda > 0:
            loss["sv_consistency"] = cfg.sv_lambda * (wgt * (1 - (Nr * Nd).sum(-1)))[V].mean()
        if self.config.planar_lambda > 0 and self.prior_planes is not None:
            Lb = self.prior_planes[i].to(self.device)
            P = self._points(Dr)
            terms = []
            for k in range(1, int(Lb.max()) + 1):
                m = (Lb == k) & V
                if m.sum() < 200:
                    continue
                Q = P[m]; c = Q.mean(0)
                _, evec = torch.linalg.eigh(((Q - c).T @ (Q - c)).detach())
                terms.append(((Q - c) @ evec[:, 0]).abs().mean() / Q[:, 2].mean().detach())
            if terms:
                loss["planar_prior"] = self.config.planar_lambda * torch.stack(terms).mean()
        return loss


def dash_schedule(data_json, res_steps, a=4.0, n_img=24):
    """DashGaussian (CVPR'25) frequency-guided resolution schedule.
    X(r) = mean over training views of sum |DFT| of the image downsampled by r. Start at the largest r with
    X(r) >= X(1)/a; factor r is used from step s_r = S * ln(X(r)/X(r_m)) / ln(X(1)/X(r_m)) on, with S =
    res_steps (step by which full resolution is reached)."""
    import cv2
    tj = json.load(open(data_json)); work = os.path.dirname(data_json)
    files = [f["file_path"] for f in tj["frames"]][:: max(1, len(tj["frames"]) // n_img)][:n_img]
    X = {r: 0.0 for r in range(1, 9)}
    for f in files:
        g = cv2.imread(os.path.join(work, f), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
        mag = np.abs(np.fft.fft2(g))
        fy = np.abs(np.fft.fftfreq(g.shape[0]))[:, None]; fx = np.abs(np.fft.fftfreq(g.shape[1]))[None, :]
        for r in X:                       # spectrum representable at 1/r resolution: |f| < 0.5 / r cycles/pixel
            X[r] += mag[(fy < 0.5 / r) & (fx < 0.5 / r)].sum() / len(files)
    rm = max(r for r in X if X[r] >= X[1] / a)
    steps = {r: int(res_steps * np.log(X[r] / X[rm]) / np.log(X[1] / X[rm])) for r in range(1, rm + 1)}
    sched = ",".join(f"{steps[r]}:{r}" for r in sorted(steps, reverse=True))
    print("DashGaussian energy X(r)/X(1): " + ", ".join(f"r{r}={X[r] / X[1]:.3f}" for r in X) + f" -> schedule {sched}")
    return sched


def build_prior(data_json, out_file, names, down=4):
    """pack mono_prior/<name>.npz into one file, in the given order (nerfstudio's TRAIN image order: the
    model looks priors up by the camera's cam_idx). The frame names are stored with it (checked on reuse)."""
    tj = json.load(open(data_json)); work = os.path.dirname(data_json)
    import cv2
    D, N, V, PL = [], [], [], []
    has_pl = os.path.isdir(os.path.join(work, "planes"))
    for n in names:
        z = np.load(os.path.join(work, "mono_prior", n + ".npz"))
        D.append(z["depth"]); N.append(z["normal"]); V.append(z["valid"])
        if has_pl:
            pl = cv2.imread(os.path.join(work, "planes", n + ".png"), cv2.IMREAD_UNCHANGED)
            PL.append(pl if pl is not None else np.zeros(z["valid"].shape, np.uint8))
    K = [tj["fl_x"] / down, tj["fl_y"] / down, tj["cx"] / down, tj["cy"] / down]
    extra = {}
    if has_pl:
        extra["planes"] = np.stack(PL)
    bm = os.path.join(work, "blur_motion.json")
    if os.path.exists(bm):
        mo = json.load(open(bm))["motion"]
        extra["motion"] = np.array([mo.get(n, [0.0] * 6) for n in names], np.float32)
    np.savez(out_file, depth=np.stack(D), normal=np.stack(N), valid=np.stack(V), K=np.array(K), names=np.array(names), **extra)
    print(f"prior: {len(names)} training frames (+{', '.join(extra) or 'nothing'}) -> {out_file}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True); ap.add_argument("--name", required=True)
    ap.add_argument("--iters", type=int, default=30000)
    ap.add_argument("--depth_lambda", type=float, default=0.05); ap.add_argument("--normal_lambda", type=float, default=0.05)
    ap.add_argument("--geo_start", type=int, default=1000)
    ap.add_argument("--densify_grad", type=float, default=0.0006)
    ap.add_argument("--num_downscales", type=int, default=2); ap.add_argument("--resolution_schedule", type=int, default=3000)
    ap.add_argument("--stop_split_at", type=int, default=15000)
    ap.add_argument("--dash_res_steps", type=int, default=0, help="> 0: DashGaussian resolution schedule reaching full res at this step")
    ap.add_argument("--no_prior", action="store_true", help="geometry losses off (speed-only experiments)")
    ap.add_argument("--no_eval", action="store_true", help="skip nerfstudio's in-training eval passes (~3 min per 30k run)")
    ap.add_argument("--prior", default="", help="packed prior .npz to reuse (same train frames, e.g. a different init cloud)")
    ap.add_argument("--planar_lambda", type=float, default=0.0, help="> 0: flatten plane_seg.py regions (needs planes/)")
    ap.add_argument("--blur_exposure", type=float, default=0.0, help="> 0 (s): motion-blur model (needs blur_motion.json)")
    ap.add_argument("--blur_start", type=int, default=0)
    ap.add_argument("--pgsr", action="store_true", help="PGSR-lite: flat Gaussians, unbiased depth, rendered normals")
    ap.add_argument("--flat_lambda", type=float, default=100.0); ap.add_argument("--sv_lambda", type=float, default=0.05)
    ap.add_argument("--pgsr_start", type=int, default=3000)
    ap.add_argument("--save_every", type=int, default=2500, help="checkpoint interval (only the latest is kept)")
    ap.add_argument("--resume", action="store_true", help="continue from this run name's latest checkpoint (power cut)")
    args = ap.parse_args()
    from nerfstudio.configs.method_configs import method_configs
    from nerfstudio.data.dataparsers.nerfstudio_dataparser import NerfstudioDataParserConfig
    from nerfstudio.scripts.train import main as ns_main

    # Without train/val/test lists in the json nerfstudio would hold out 10% of the frames by itself
    # (eval_mode "fraction"), and per-frame priors packed for all frames would then belong to the wrong
    # images (2026-10-27 bug: the offset grew to > 100 frames). "all" = every frame trains; split lists in
    # the json still take precedence.
    dataparser = NerfstudioDataParserConfig(auto_scale_poses=False, center_method="none", orientation_method="none",
                                            downscale_factor=1, load_3D_points=True, eval_mode="all")
    prior = args.prior or os.path.join(os.path.dirname(os.path.abspath(args.data)), "mono_prior", f"train_{Path(args.data).stem}.npz")
    if args.no_prior:
        prior = ""
        args.depth_lambda = args.normal_lambda = 0.0
    else:
        probe = copy.deepcopy(dataparser); probe.data = Path(args.data)
        train_names = [Path(f).stem for f in probe.setup().get_dataparser_outputs(split="train").image_filenames]
        packed = list(np.load(prior)["names"]) if os.path.exists(prior) and "names" in np.load(prior).files else None
        if packed != train_names:
            if os.path.exists(prior):
                print(f"prior {prior}: {'no frame names' if packed is None else 'different frames / order'} -> rebuilt")
            build_prior(args.data, prior, train_names)
    sched = dash_schedule(args.data, args.dash_res_steps) if args.dash_res_steps > 0 else ""
    cfg = copy.deepcopy(method_configs["splatfacto"])
    base = cfg.pipeline.model
    kw = {f.name: getattr(base, f.name) for f in fields(SplatfactoModelConfig) if f.name != "_target" and f.init}
    kw.update(prior_file=os.path.abspath(prior) if prior else "", dash_schedule=sched, depth_lambda=args.depth_lambda, normal_lambda=args.normal_lambda,
              geo_start=args.geo_start, planar_lambda=args.planar_lambda, blur_exposure=args.blur_exposure,
              blur_start=args.blur_start, pgsr=args.pgsr, flat_lambda=args.flat_lambda, sv_lambda=args.sv_lambda,
              pgsr_start=args.pgsr_start, random_init=False, use_bilateral_grid=True, use_scale_regularization=not args.pgsr,
              densify_grad_thresh=args.densify_grad, num_downscales=args.num_downscales,
              resolution_schedule=args.resolution_schedule, stop_split_at=args.stop_split_at,
              output_depth_during_training=not args.no_prior)
    # import this file under its module name so the saved config references geo_splatfacto.* (not __main__),
    # which ns-export can re-import with PYTHONPATH=src/arcore3dgs
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import geo_splatfacto as gs
    cfg.pipeline.model = gs.GeoSplatfactoModelConfig(**kw)
    cfg.pipeline.datamanager.dataparser = dataparser
    cfg.pipeline.datamanager.cache_images = "cpu"
    cfg.pipeline.datamanager.cache_images_type = "uint8"
    cfg.data = Path(args.data)
    cfg.max_num_iterations = args.iters
    cfg.steps_per_save = min(args.save_every, args.iters)     # the machine has power cuts: keep a recent checkpoint
    ckpt_dir = Path("outputs") / "v8" / "splatfacto" / args.name / "nerfstudio_models"
    if args.resume and ckpt_dir.is_dir() and any(ckpt_dir.glob("step-*.ckpt")):
        last = sorted(ckpt_dir.glob("step-*.ckpt"))[-1]
        cfg.load_dir = ckpt_dir
        # nerfstudio runs max_num_iterations MORE steps after a checkpoint: give it only what is left
        cfg.max_num_iterations = max(1, args.iters - (int(last.stem.split("-")[1]) + 1))
        print(f"resuming from {last.name}: {cfg.max_num_iterations} steps left")
    for k in ("means", "bilateral_grid", "camera_opt"):
        if k in cfg.optimizers and cfg.optimizers[k]["scheduler"] is not None:
            cfg.optimizers[k]["scheduler"].max_steps = args.iters
    if args.no_eval:
        # never (an eval would cache every eval image -- with eval_mode "all" a second copy of the dataset)
        cfg.steps_per_eval_image = cfg.steps_per_eval_all_images = cfg.steps_per_eval_batch = 10 ** 9
    cfg.vis = "tensorboard"
    cfg.viewer.quit_on_train_completion = True
    cfg.output_dir = Path("outputs"); cfg.experiment_name = "v8"; cfg.timestamp = args.name
    ns_main(cfg)
