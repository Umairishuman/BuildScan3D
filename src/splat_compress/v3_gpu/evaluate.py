"""Quality of a compressed splat against the original: render both at the same cameras and compare (PSNR, SSIM).

This measures the loss from compression only, not the accuracy against the real photos (same method as the v2 README).
Needs CUDA and gsplat (the nerfstudio environment). NOT YET RUN: written 2026-11-23 on a machine without a GPU.

  python -m splat_compress.v3_gpu.evaluate original.ply compressed.ply --frames-json <work>/frames.json [--set ...]

Cameras come from the pipeline's frames.json (same fields compare_models.py reads: W, H, fx, fy, cx, cy and per frame
`c2w` in the OpenGL convention). Views = the held-out split in the config, capped at evaluate.max_views.
"""
import argparse
import json

import numpy as np
import torch

from .config import load_config
from .splat_io import read_ply, sh_degree_of

GL_TO_CV = np.diag([1, -1, -1, 1.0])


def pick_views(n_frames, split, max_views):
    if split == "every10":
        ids = list(range(0, n_frames, 10))
    elif split == "nerfstudio":          # train = linspace(0, n-1, ceil(0.9 n)); the rest are held out
        train = set(np.linspace(0, n_frames - 1, int(np.ceil(n_frames * 0.9)), dtype=int).tolist())
        ids = [i for i in range(n_frames) if i not in train]
    else:
        raise ValueError(f"evaluate.split must be 'every10' or 'nerfstudio', got {split!r}")
    if max_views and len(ids) > max_views:
        ids = [ids[i] for i in np.linspace(0, len(ids) - 1, max_views, dtype=int)]
    return ids


def psnr(a, b):
    mse = ((a - b) ** 2).mean().clamp(min=1e-12)
    return float(-10 * torch.log10(mse))


@torch.no_grad()
def render(splats, c2w_gl, K, W, H, cfg, dev):
    from gsplat import rasterization          # imported here so the module loads (and its helpers test) without gsplat
    w2c = torch.tensor(np.linalg.inv(np.array(c2w_gl) @ GL_TO_CV), dtype=torch.float32, device=dev)[None]
    colors = torch.cat([splats["dc"][:, None, :], splats["rest"].transpose(1, 2)], 1)   # (N, 1 + K, 3)
    quats = torch.nn.functional.normalize(splats["rot"], dim=-1)
    out, _, _ = rasterization(splats["xyz"], quats, torch.exp(splats["scale"]), torch.sigmoid(splats["opacity"]),
                              colors, w2c, K, W, H, sh_degree=sh_degree_of(splats),
                              near_plane=cfg["near"], far_plane=cfg["far"])
    return out[0, ..., :3].clamp(0, 1)


def evaluate(original_ply, compressed_ply, frames_json, cfg):
    if not torch.cuda.is_available():
        raise RuntimeError("evaluate needs CUDA (gsplat's rasterizer)")
    from pytorch_msssim import ssim
    dev = torch.device("cuda")
    ev = cfg["evaluate"]
    with open(frames_json, encoding="utf-8") as f:
        meta = json.load(f)
    s = ev["scale"]
    W, H = meta["W"] // s, meta["H"] // s
    K = torch.tensor([[[meta["fx"] / s, 0, meta["cx"] / s], [0, meta["fy"] / s, meta["cy"] / s], [0, 0, 1]]],
                     dtype=torch.float32, device=dev)
    a, b = read_ply(original_ply, dev), read_ply(compressed_ply, dev)
    rows = []
    for i in pick_views(len(meta["frames"]), ev["split"], ev["max_views"]):
        c2w = meta["frames"][i]["c2w"]
        ra, rb = render(a, c2w, K, W, H, ev, dev), render(b, c2w, K, W, H, ev, dev)
        rows.append(dict(frame=i, psnr=psnr(ra, rb),
                         ssim=float(ssim(ra.permute(2, 0, 1)[None], rb.permute(2, 0, 1)[None], data_range=1.0))))
    return dict(views=len(rows), psnr_mean=float(np.mean([r["psnr"] for r in rows])),
                psnr_min=float(np.min([r["psnr"] for r in rows])),
                ssim_mean=float(np.mean([r["ssim"] for r in rows])), per_view=rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("original")
    ap.add_argument("compressed")
    ap.add_argument("--frames-json", required=True)
    ap.add_argument("--config")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--out", help="write the result as JSON here")
    a = ap.parse_args(argv)
    res = evaluate(a.original, a.compressed, a.frames_json, load_config(a.config, a.set))
    print(f"{res['views']} views: PSNR mean {res['psnr_mean']:.2f} dB (min {res['psnr_min']:.2f}), SSIM {res['ssim_mean']:.4f}")
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
