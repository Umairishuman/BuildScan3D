"""Baseline analysis of a 3DGS splat.ply: where the bytes go and how much simple pruning would remove.

Read-only; nothing is written. Run:  python src/splat_compress/v1_ply_prune_sh_ksplat/analyze.py path/to/splat.ply

The INRIA/nerfstudio splat.ply layout is one float32 row per Gaussian:
  x y z | nx ny nz | f_dc_0..2 | f_rest_0..44 | opacity (logit) | scale_0..2 (log) | rot_0..3 (quaternion)
Spherical harmonics (SH) degree 3 needs 3 + 45 colour floats per splat; lower degrees need far fewer.
"""
import sys
import numpy as np
from plyfile import PlyData

path = sys.argv[1]
ply = PlyData.read(path)
v = ply["vertex"]
n = v.count
names = v.data.dtype.names
row_bytes = v.data.dtype.itemsize

groups = {
    "position (x,y,z)": [c for c in names if c in ("x", "y", "z")],
    "normals (unused by renderers)": [c for c in names if c in ("nx", "ny", "nz")],
    "colour DC (f_dc)": [c for c in names if c.startswith("f_dc")],
    "colour SH rest (f_rest)": [c for c in names if c.startswith("f_rest")],
    "opacity": [c for c in names if c == "opacity"],
    "scale": [c for c in names if c.startswith("scale")],
    "rotation": [c for c in names if c.startswith("rot")],
}

print(f"file: {path}")
print(f"splats: {n:,}   bytes/splat: {row_bytes}   data size: {n * row_bytes / 1e6:.1f} MB")
print(f"{'attribute group':34s}{'floats':>7s}{'MB':>9s}{'share':>8s}")
for g, cols in groups.items():
    b = n * 4 * len(cols)
    print(f"{g:34s}{len(cols):7d}{b / 1e6:9.1f}{100 * b / (n * row_bytes):7.1f}%")

n_rest = len(groups["colour SH rest (f_rest)"])
deg = {0: 0, 1: 9, 2: 24, 3: 45}
cur = [d for d, c in deg.items() if c == n_rest]
print(f"\nSH degree in file: {cur[0] if cur else 'unknown'}  ({n_rest} rest coefficients)")

opacity = 1.0 / (1.0 + np.exp(-np.asarray(v["opacity"], dtype=np.float64)))
scales = np.exp(np.stack([np.asarray(v[f"scale_{i}"], dtype=np.float64) for i in range(3)], 1))
smax, smin = scales.max(1), scales.min(1)
vol = scales.prod(1)

def pct(a, qs=(1, 5, 25, 50, 75, 95, 99)):
    return "  ".join(f"p{q}={np.percentile(a, q):.4g}" for q in qs)

print("\nopacity:", pct(opacity))
print("scale max axis (m):", pct(smax))
print("scale min/max ratio (flatness):", pct(smin / np.maximum(smax, 1e-12)))
xyz = np.stack([np.asarray(v[c]) for c in ("x", "y", "z")], 1)
lo, hi = np.percentile(xyz, 1, axis=0), np.percentile(xyz, 99, axis=0)
print("extent p1-p99 (m):", np.round(hi - lo, 2))

print("\nsimple pruning: share of splats removed (size scales linearly with splat count)")
for t in (0.01, 0.02, 0.05, 0.1):
    print(f"  opacity < {t:<5}: {100 * (opacity < t).mean():5.1f}%")
for q in (1, 5, 10):
    thr = np.percentile(vol, q)
    print(f"  smallest {q:>2}% by volume (vol < {thr:.3g}): {100 * (vol < thr).mean():5.1f}%")
big = smax > 5 * np.median(smax)
print(f"  scale > 5x median (likely blobs/floaters): {100 * big.mean():5.1f}%")

print("\nprojected raw float32 size after dropping data not needed to render:")
base = row_bytes * n
no_norm = base - 12 * n
print(f"  now                                : {base / 1e6:7.1f} MB")
print(f"  drop normals                       : {no_norm / 1e6:7.1f} MB  ({100 * (1 - no_norm / base):.0f}% smaller)")
for d in (2, 1, 0):
    drop = (n_rest - deg[d]) * 4 * n
    size = no_norm - drop
    print(f"  ... + SH degree {d}                  : {size / 1e6:7.1f} MB  ({100 * (1 - size / base):.0f}% smaller)")
