"""Compression stages. Each is `stage(splats, cfg, ctx) -> (splats, stats)`; cfg is that stage's config section,
ctx carries `device`, `seed` and the full config. Splat layout: see splat_io.py."""
import math

import torch

from .splat_io import SH_REST_PER_CHANNEL, subset


def prune(splats, cfg, ctx):
    n = len(splats["xyz"])
    keep = torch.sigmoid(splats["opacity"]) >= cfg["min_opacity"]
    scale = torch.exp(splats["scale"])
    if cfg["max_scale_mult"] > 0:
        smax = scale.max(1).values
        keep &= smax <= cfg["max_scale_mult"] * smax.median()
    q = cfg["importance_quantile"]
    if q > 0:
        # importance = opacity x ellipsoid volume; drop the lowest q share of what is left
        imp = torch.sigmoid(splats["opacity"]) * scale.prod(1)
        alive = imp[keep]
        if len(alive):
            k = max(1, int(math.ceil(q * len(alive))))
            thr = torch.kthvalue(alive, k).values
            keep &= imp > thr
    out = subset(splats, keep)
    return out, dict(splats_in=n, splats_out=int(keep.sum()))


def sh_reduce(splats, cfg, ctx):
    deg = cfg["sh_degree"]
    if deg not in SH_REST_PER_CHANNEL:
        raise ValueError(f"sh_degree must be one of {sorted(SH_REST_PER_CHANNEL)}, got {deg}")
    have = splats["rest"].shape[2]
    keep = min(SH_REST_PER_CHANNEL[deg], have)
    out = dict(splats)
    out["rest"] = splats["rest"][:, :, :keep].contiguous()
    if cfg["drop_normals"]:
        out["normals"] = None
    return out, dict(sh_per_channel_in=have, sh_per_channel_out=keep)


def kmeans(x, k, iters, chunk, gen):
    """Plain Lloyd k-means on (N, D); the assignment step is chunked so N x k distances never sit in memory at once."""
    n = len(x)
    k = min(k, n)
    cent = x[torch.randperm(n, generator=gen)[:k].to(x.device)].clone()
    idx = torch.zeros(n, dtype=torch.long, device=x.device)
    for _ in range(iters):
        for s in range(0, n, chunk):
            idx[s:s + chunk] = torch.cdist(x[s:s + chunk], cent).argmin(1)
        sums = torch.zeros_like(cent).index_add_(0, idx, x)
        cnt = torch.bincount(idx, minlength=k).to(x.dtype)
        empty = cnt == 0
        cent = torch.where(empty[:, None], cent, sums / cnt.clamp(min=1)[:, None])
        if empty.any():                                   # re-seed empty clusters on random points
            pick = torch.randint(0, n, (int(empty.sum()),), generator=gen).to(x.device)
            cent[empty] = x[pick]
    for s in range(0, n, chunk):
        idx[s:s + chunk] = torch.cdist(x[s:s + chunk], cent).argmin(1)
    return cent, idx


def vq_sh(splats, cfg, ctx):
    """Replace the SH rest coefficients by their nearest codebook entry. Stores codebook + indices in splats['vq']
    (what a codebook container would hold); `rest` holds the dequantised values so every writer and the evaluator
    work unchanged."""
    rest = splats["rest"]
    n, _, per_ch = rest.shape
    if per_ch == 0 or n == 0:
        return splats, dict(skipped="no SH rest coefficients")
    x = rest.reshape(n, -1)
    gen = torch.Generator().manual_seed(ctx["seed"])
    cent, idx = kmeans(x, cfg["codebook_size"], cfg["iters"], cfg["chunk"], gen)
    deq = cent[idx]
    mse = float(((deq - x) ** 2).mean())
    k = len(cent)
    index_bytes = 1 if k <= 256 else 2 if k <= 65536 else 4
    packed = n * index_bytes + k * x.shape[1] * 4
    out = dict(splats)
    out["rest"] = deq.reshape(n, 3, per_ch)
    out["vq"] = dict(codebook=cent, indices=idx)
    return out, dict(codebook_size=k, mse=mse, rest_bytes_before=n * x.shape[1] * 4, rest_bytes_packed=packed)


STAGES = {"prune": prune, "sh_reduce": sh_reduce, "vq_sh": vq_sh}
# vq_sh stores indices for the splats it saw, so nothing that removes splats may run after it
MUST_BE_LAST = {"vq_sh"}
