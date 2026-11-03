"""Stage A+B of the compression engine: prune low-value splats, drop unused data, reduce spherical harmonics (SH).

Input and output are standard 3DGS .ply files, so any splat viewer (and the later .ksplat converter) can read them.

  python src/splat_compress/v1_ply_prune_sh_ksplat/compress.py in.ply out.ply [--min-opacity 0.05] [--sh-degree 1] [--max-scale-mult 0]

What it does, in order:
  1. prune   splats whose opacity is below --min-opacity (nearly transparent, they contribute almost nothing);
             optionally (--max-scale-mult K > 0) also splats whose largest axis is more than K x the median
             (large blobs, usually floaters). The second rule is OFF by default because it can remove real surfaces.
  2. drop    the unused normals (nx, ny, nz); renderers ignore them.
  3. reduce  SH from degree 3 down to --sh-degree (view-dependent colour detail). Degree 0 = flat colour.
Positions, DC colour, opacity, scale and rotation are kept as-is (float32); quantisation is a later stage.
"""
import argparse
import numpy as np
from plyfile import PlyData, PlyElement

SH_REST_PER_CHANNEL = {0: 0, 1: 3, 2: 8, 3: 15}


def compress(vertex, min_opacity=0.05, sh_degree=1, max_scale_mult=0.0):
    names = vertex.data.dtype.names
    n = vertex.count
    n_rest = sum(c.startswith("f_rest") for c in names)
    per_ch_in = n_rest // 3
    keep_per_ch = min(SH_REST_PER_CHANNEL[sh_degree], per_ch_in)

    opacity = 1.0 / (1.0 + np.exp(-np.asarray(vertex["opacity"], dtype=np.float64)))
    keep = opacity >= min_opacity
    if max_scale_mult > 0:
        smax = np.exp(np.stack([np.asarray(vertex[f"scale_{i}"], dtype=np.float64) for i in range(3)], 1)).max(1)
        keep &= smax <= max_scale_mult * np.median(smax)

    # SH coefficients are stored channel-major: f_rest_0..per_ch-1 = R, next per_ch = G, next per_ch = B.
    rest_keep = [f"f_rest_{c * per_ch_in + k}" for c in range(3) for k in range(keep_per_ch)]
    out_names = (["x", "y", "z", "f_dc_0", "f_dc_1", "f_dc_2"] + rest_keep
                 + ["opacity", "scale_0", "scale_1", "scale_2", "rot_0", "rot_1", "rot_2", "rot_3"])
    # renumber kept SH names so the output reads as a valid lower-degree file
    renum = iter(range(len(rest_keep)))
    final_names = [f"f_rest_{next(renum)}" if nm.startswith("f_rest") else nm for nm in out_names]

    dtype = [(nm, "f4") for nm in final_names]
    out = np.empty(int(keep.sum()), dtype=dtype)
    for src, dst in zip(out_names, final_names):
        out[dst] = np.asarray(vertex[src], dtype=np.float32)[keep]
    stats = dict(total=n, kept=int(keep.sum()), sh_in=n_rest, sh_out=len(rest_keep),
                 bytes_in=vertex.data.dtype.itemsize * n, bytes_out=out.dtype.itemsize * out.shape[0])
    return PlyElement.describe(out, "vertex"), stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--min-opacity", type=float, default=0.05)
    ap.add_argument("--sh-degree", type=int, default=1, choices=[0, 1, 2, 3])
    ap.add_argument("--max-scale-mult", type=float, default=0.0)
    a = ap.parse_args()
    el, s = compress(PlyData.read(a.src)["vertex"], a.min_opacity, a.sh_degree, a.max_scale_mult)
    PlyData([el], text=False).write(a.dst)
    print(f"splats {s['total']:,} -> {s['kept']:,} ({100 * s['kept'] / s['total']:.1f}% kept)")
    print(f"SH floats {s['sh_in']} -> {s['sh_out']}")
    print(f"data {s['bytes_in'] / 1e6:.1f} MB -> {s['bytes_out'] / 1e6:.1f} MB "
          f"({100 * (1 - s['bytes_out'] / s['bytes_in']):.0f}% smaller)")
