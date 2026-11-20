"""Held-out scores after test-pose alignment (FEATURELESS_TRACKING_PLAN §10, for 10.d).

eval_offpath.py renders each held-out frame from its SfM pose. When training refines the camera poses (--pose_opt,
R-084), the training cameras can move as a whole, and an unrefined held-out pose no longer lines up with the model:
the score drops although the model may be better. Standard practice for pose-refining methods: freeze the model and
optimise only the held-out camera (6-DoF, plus a per-channel colour gain / bias for exposure) against the photo, then
score. Done the same way for every model, so the comparison is fair; the size of each correction is reported too
(a large correction on a model without pose refinement = the SfM pose of that frame was off).

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/eval_align.py --work <sfm dir with frames.json, offpath_test.txt>
      --models a=<ply> b=<ply> [--iters 150] [--csv <per-frame csv>]

Prints per model: mean colour-fit PSNR / SSIM before and after alignment, and the median correction (degrees,
model units). Half resolution, as eval_offpath.py.
"""
import argparse
import json
import os

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from gsplat import rasterization
from plyfile import PlyData
from pytorch_msssim import ssim

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--models", nargs="+", required=True)
ap.add_argument("--iters", type=int, default=150)
ap.add_argument("--csv", default=None)
a = ap.parse_args()
dev = "cuda"; G = np.diag([1, -1, -1, 1.0])
meta = json.load(open(os.path.join(a.work, "frames.json"))); by = {f["name"]: f for f in meta["frames"]}
test = sorted(open(os.path.join(a.work, "offpath_test.txt")).read().split(), key=lambda n: by[n]["pts"])
t0 = min(f["pts"] for f in meta["frames"])
W, H = meta["W"], meta["H"]


def Kmat(s):
    return torch.tensor([[[meta["fx"] / s, 0, meta["cx"] / s], [0, meta["fy"] / s, meta["cy"] / s], [0, 0, 1]]],
                        dtype=torch.float32, device=dev)


def load(path):
    v = PlyData.read(path)["vertex"]; c = lambda n: torch.tensor(np.asarray(v[n]), dtype=torch.float32, device=dev)
    m = torch.stack([c("x"), c("y"), c("z")], 1); nr = len([n for n in v.data.dtype.names if n.startswith("f_rest")])
    col = torch.stack([c(f"f_dc_{i}") for i in range(3)], 1)[:, None]
    if nr:
        col = torch.cat([col, torch.stack([c(f"f_rest_{i}") for i in range(nr)], 1).reshape(len(m), 3, -1).transpose(1, 2)], 1)
    return dict(means=m, quats=F.normalize(torch.stack([c(f"rot_{i}") for i in range(4)], 1), dim=-1),
                scales=torch.exp(torch.stack([c(f"scale_{i}") for i in range(3)], 1)), opac=torch.sigmoid(c("opacity")),
                col=col, sh=int(round(np.sqrt(col.shape[1]))) - 1)


def so3_exp(w):
    th = w.norm() + 1e-12; k = w / th
    Kx = torch.zeros(3, 3, device=dev)
    Kx[0, 1], Kx[0, 2], Kx[1, 0], Kx[1, 2], Kx[2, 0], Kx[2, 1] = -k[2], k[1], k[2], -k[0], -k[1], k[0]
    return torch.eye(3, device=dev) + torch.sin(th) * Kx + (1 - torch.cos(th)) * Kx @ Kx


def render(g, w2c, s):
    out, _, _ = rasterization(g["means"], g["quats"], g["scales"], g["opac"], g["col"], w2c[None], Kmat(s), W // s, H // s,
                              sh_degree=g["sh"])
    return out[0].clamp(0, 1)


def photo(n, s):
    im = cv2.resize(cv2.imread(os.path.join(a.work, "images", n + ".jpg")), (W // s, H // s), interpolation=cv2.INTER_AREA)
    return torch.from_numpy(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).to(dev).float() / 255


def score(r, gt):
    A = torch.cat([r.reshape(-1, 3), torch.ones(r.shape[0] * r.shape[1], 1, device=dev)], 1)
    ra = (A @ torch.linalg.lstsq(A, gt.reshape(-1, 3)).solution).reshape(gt.shape).clamp(0, 1)
    return (float(-10 * torch.log10(((ra - gt) ** 2).mean())),
            float(ssim(ra.permute(2, 0, 1)[None], gt.permute(2, 0, 1)[None], data_range=1.0)))


def align(g, w2c0, n):
    """optimise a camera-frame correction dT (w2c = dT @ w2c0) and a colour gain / bias, coarse to fine"""
    w = torch.zeros(3, device=dev, requires_grad=True); t = torch.zeros(3, device=dev, requires_grad=True)
    gain = torch.ones(3, device=dev, requires_grad=True); bias = torch.zeros(3, device=dev, requires_grad=True)
    opt = torch.optim.Adam([{"params": [w], "lr": 2e-3}, {"params": [t], "lr": 2e-3},
                            {"params": [gain, bias], "lr": 1e-2}])
    for s, it in ((8, a.iters), (4, a.iters // 2), (2, a.iters // 3)):
        gt = photo(n, s)
        for _ in range(it):
            T = torch.eye(4, device=dev); T[:3, :3] = so3_exp(w); T[:3, 3] = t
            r = render(g, T @ w2c0, s) * gain + bias
            loss = (r - gt).abs().mean()
            opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        T = torch.eye(4, device=dev); T[:3, :3] = so3_exp(w); T[:3, 3] = t
    return T.detach(), float(np.degrees(w.norm().item())), float(t.norm().item())


rows, summary = [], {}
for spec in a.models:
    name, path = spec.split("=", 1); g = load(path)
    for k in ("means", "quats", "scales", "opac", "col"):
        g[k].requires_grad_(False)
    b_ps, b_ss, a_ps, a_ss, rot, tr = [], [], [], [], [], []
    for n in test:
        w2c0 = torch.tensor(np.linalg.inv(np.array(by[n]["c2w"]) @ G), dtype=torch.float32, device=dev)
        gt = photo(n, 2)
        with torch.no_grad():
            p0, s0 = score(render(g, w2c0, 2), gt)
        T, dr, dt = align(g, w2c0, n)
        with torch.no_grad():
            p1, s1 = score(render(g, T @ w2c0, 2), gt)
        if p1 < p0:                                        # alignment wandered off: keep the SfM pose
            p1, s1, dr, dt = p0, s0, 0.0, 0.0
        b_ps.append(p0); b_ss.append(s0); a_ps.append(p1); a_ss.append(s1); rot.append(dr); tr.append(dt)
        rows.append((name, n, by[n]["pts"] - t0, p0, p1, dr, dt))
    summary[name] = dict(psnr=np.mean(b_ps), ssim=np.mean(b_ss), psnr_al=np.mean(a_ps), ssim_al=np.mean(a_ss),
                         rot_deg=np.median(rot), trans=np.median(tr))
    print(f"{name:16s} PSNR {np.mean(b_ps):6.2f} -> aligned {np.mean(a_ps):6.2f}   SSIM {np.mean(b_ss):.4f} -> {np.mean(a_ss):.4f}"
          f"   correction median {np.median(rot):.2f} deg, {np.median(tr):.3f} units", flush=True)
if a.csv:
    with open(a.csv, "w") as f:
        f.write("model,name,t_s,psnr,psnr_aligned,corr_deg,corr_units\n")
        for r in rows:
            f.write(f"{r[0]},{r[1]},{r[2]:.2f},{r[3]:.2f},{r[4]:.2f},{r[5]:.3f},{r[6]:.4f}\n")
