"""Image quality of the compressed web splats (.spz) against the trained model (.ply) (COMPLETION_PLAN 5.4 / E6).

The web bundle stores the model as .spz (Spark's encoder: 24-bit fixed-point positions, 8-bit opacity, colour, log
scale, rotation and spherical harmonics, gzip). This script decodes the .spz files of a bundle (format: Niantic spz
v2 / v3), renders the decoded model and the original .ply from the same cameras (held-out frames if the work folder
has offpath_test.txt, else every Nth frame) and reports the PSNR / SSIM of the compressed render against the
original render, so the number is the loss from compression alone (no photo involved). Sizes are reported too.

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/spz_quality.py --ply <gs>/splat.ply --spz <bundle dir or file>
      --work <work_sfm> [--every 20] [--out spz_quality.json]
"""
import argparse
import glob
import gzip
import json
import os
import struct

import numpy as np
import torch
from gsplat import rasterization
from plyfile import PlyData
from pytorch_msssim import ssim

C0 = 0.28209479177387814


def read_spz(path):
    raw = gzip.decompress(open(path, "rb").read())
    magic, version, n, sh_deg, frac, flags, _ = struct.unpack_from("<IIIBBBB", raw, 0)
    assert magic == 0x5053474E, f"{path}: not an spz file"
    assert version in (2, 3), f"{path}: spz version {version} not supported"
    o = 16
    def take(k):
        nonlocal o
        b = np.frombuffer(raw, np.uint8, k, o); o += k
        return b
    pb = take(n * 9).reshape(n, 3, 3).astype(np.int32)
    p = pb[..., 0] | (pb[..., 1] << 8) | (pb[..., 2] << 16)
    p = np.where(p & 0x800000, p - (1 << 24), p).astype(np.float32) / (1 << frac)
    alpha = take(n).astype(np.float32) / 255.0
    col = (take(n * 3).reshape(n, 3).astype(np.float32) / 255.0 - 0.5) / 0.15         # SH DC coefficients
    scl = take(n * 3).reshape(n, 3).astype(np.float32) / 16.0 - 10.0                # log scale
    if version == 2:
        r = take(n * 3).reshape(n, 3).astype(np.float32) / 127.5 - 1.0
        w = np.sqrt(np.clip(1.0 - (r ** 2).sum(1), 0, None))
        q = np.concatenate([w[:, None], r], 1)                                         # w x y z
    else:                                                                              # smallest-three, 4 bytes
        b = take(n * 4).reshape(n, 4).astype(np.uint32)
        v = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16) | (b[:, 3] << 24)
        largest = (v >> 30).astype(np.int64); mask = (1 << 9) - 1
        xyzw = np.zeros((n, 4), np.float32); rest = v.copy()
        sq = np.zeros(n, np.float32)
        for i in range(3, -1, -1):
            is_l = largest == i
            mag = (rest & mask).astype(np.float32); neg = ((rest >> 9) & 1).astype(bool)
            val = mag / mask * np.sqrt(0.5); val = np.where(neg, -val, val)
            xyzw[~is_l, i] = val[~is_l]; sq += np.where(is_l, 0, val ** 2)
            rest = np.where(is_l, rest, rest >> 10)
        xyzw[np.arange(n), largest] = np.sqrt(np.clip(1 - sq, 0, None))
        q = xyzw[:, [3, 0, 1, 2]]
    dim = {0: 0, 1: 3, 2: 8, 3: 15}[sh_deg]
    sh = (take(n * dim * 3).reshape(n, dim, 3).astype(np.float32) - 128.0) / 128.0 if dim else np.zeros((n, 0, 3), np.float32)
    return dict(means=p, opac=alpha, dc=col, log_scale=scl, quat=q, sh=sh, sh_deg=sh_deg, version=version)


def read_ply(path):
    v = PlyData.read(path)["vertex"]; names = v.data.dtype.names
    rest = sorted([k for k in names if k.startswith("f_rest_")], key=lambda k: int(k.split("_")[-1]))
    dim = len(rest) // 3
    sh = np.stack([np.asarray(v[k]) for k in rest], 1).reshape(-1, 3, dim).transpose(0, 2, 1) if dim else np.zeros((len(v), 0, 3))
    return dict(means=np.stack([v["x"], v["y"], v["z"]], 1), opac=1 / (1 + np.exp(-np.asarray(v["opacity"]))),
                dc=np.stack([v[f"f_dc_{i}"] for i in range(3)], 1),
                log_scale=np.stack([v[f"scale_{i}"] for i in range(3)], 1),
                quat=np.stack([v[f"rot_{i}"] for i in range(4)], 1), sh=sh.astype(np.float32),
                sh_deg={0: 0, 3: 1, 8: 2, 15: 3}[dim])


def to_torch(m, dev):
    t = lambda a: torch.tensor(np.ascontiguousarray(a), dtype=torch.float32, device=dev)
    q = t(m["quat"]); q = q / q.norm(dim=1, keepdim=True).clamp_min(1e-8)
    coeffs = torch.cat([t(m["dc"])[:, None, :], t(m["sh"])], 1)
    return t(m["means"]), q, torch.exp(t(m["log_scale"])), t(m["opac"]), coeffs, m["sh_deg"]


ap = argparse.ArgumentParser()
ap.add_argument("--ply", required=True)
ap.add_argument("--spz", required=True, help="a bundle folder (all its *.spz are merged) or one .spz file")
ap.add_argument("--work", required=True, help="work_<tag>_sfm folder with frames.json (camera poses)")
ap.add_argument("--every", type=int, default=20)
ap.add_argument("--down", type=int, default=2)
ap.add_argument("--out", default="")
args = ap.parse_args()
dev = "cuda"

spz_files = sorted(glob.glob(os.path.join(args.spz, "*.spz"))) if os.path.isdir(args.spz) else [args.spz]
parts = [read_spz(f) for f in spz_files]
deg = min(p["sh_deg"] for p in parts)
dimk = {0: 0, 1: 3, 2: 8, 3: 15}[deg]
S = {k: np.concatenate([p[k] for p in parts]) for k in ["means", "opac", "dc", "log_scale", "quat"]}
S["sh"] = np.concatenate([p["sh"][:, :dimk] for p in parts]); S["sh_deg"] = deg
P = read_ply(args.ply)
print(f"ply {len(P['means']):,} Gaussians, SH degree {P['sh_deg']}, {os.path.getsize(args.ply) / 1e6:.1f} MB; "
      f"spz {len(S['means']):,} Gaussians in {len(spz_files)} file(s), version {parts[0]['version']}, SH degree {deg}, "
      f"{sum(os.path.getsize(f) for f in spz_files) / 1e6:.1f} MB")

# The spz may store another axis convention than the ply: find the axis signs that put the spz points on the ply's.
from scipy.spatial import cKDTree
tree = cKDTree(P["means"]); best = None
for sx in (1, -1):
    for sy in (1, -1):
        for sz in (1, -1):
            sgn = np.array([sx, sy, sz], np.float32)
            d, _ = tree.query(S["means"][:: max(1, len(S["means"]) // 20000)] * sgn)
            if best is None or np.median(d) < best[0]:
                best = (float(np.median(d)), sgn)
med, sgn = best
print(f"axis signs spz -> ply {sgn.tolist()}, median distance to the nearest ply point {med * 1000:.2f} mm (model units x 1000)")
if (sgn != 1).any():
    S["means"] = S["means"] * sgn
    # flipping two axes = rotation by 180 deg about the third: q' = r q; spherical harmonics change too, so only the
    # identity case is supported for SH > 0 (report if it happens)
    raise SystemExit("spz axes differ from the ply: add the rotation for quaternions / SH before scoring")

meta = json.load(open(os.path.join(args.work, "frames.json")))
names = [f["name"] for f in meta["frames"]]
held_p = os.path.join(args.work, "offpath_test.txt")
held = set(open(held_p).read().split()) if os.path.exists(held_p) else set()
frames = [f for f in meta["frames"] if f["name"] in held] or meta["frames"][:: args.every]
d = args.down
W, H = meta["W"] // d, meta["H"] // d
K = torch.tensor([[[meta["fx"] / d, 0, meta["cx"] / d], [0, meta["fy"] / d, meta["cy"] / d], [0, 0, 1]]], dtype=torch.float32, device=dev)
G = np.diag([1, -1, -1, 1]).astype(np.float64)                 # OpenGL c2w in frames.json -> OpenCV (as layout.py)
mp, ms = to_torch(P, dev), to_torch(S, dev)
ps, ss = [], []
for f in frames:
    c2w = np.array(f["c2w"]) @ G
    w2c = torch.tensor(np.linalg.inv(c2w)[None], dtype=torch.float32, device=dev)
    ims = []
    for (m, q, s, o, c, deg_) in (mp, ms):
        with torch.no_grad():
            im, _, _ = rasterization(m, q, s, o, c, w2c, K, W, H, sh_degree=deg_)
        ims.append(im[0].clamp(0, 1))
    a, b = ims
    mse = torch.mean((a - b) ** 2).item()
    ps.append(10 * np.log10(1.0 / max(mse, 1e-12)))
    ss.append(ssim(a.permute(2, 0, 1)[None], b.permute(2, 0, 1)[None], data_range=1.0).item())
res = dict(ply=args.ply, spz=spz_files, frames=len(frames), held_out=bool(held),
           ply_mb=round(os.path.getsize(args.ply) / 1e6, 1), spz_mb=round(sum(os.path.getsize(f) for f in spz_files) / 1e6, 1),
           gaussians_ply=int(len(P["means"])), gaussians_spz=int(len(S["means"])), sh_ply=P["sh_deg"], sh_spz=deg,
           psnr_mean=round(float(np.mean(ps)), 2), psnr_min=round(float(np.min(ps)), 2), ssim_mean=round(float(np.mean(ss)), 4))
res["size_reduction_pct"] = round(100 * (1 - res["spz_mb"] / res["ply_mb"]), 1)
print(json.dumps(res, indent=1))
if args.out:
    json.dump(res, open(args.out, "w"), indent=1)
