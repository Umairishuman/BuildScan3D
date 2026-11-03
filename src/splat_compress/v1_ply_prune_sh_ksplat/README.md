# v1: prune, reduce colour detail, pack as .ksplat

Post-processing for the `splat.ply` that the pipeline exports, so it can be delivered to a browser.

## Scripts
| Script | Use |
|---|---|
| `analyze.py` | `python analyze.py splat.ply` prints where the bytes go and how much simple pruning would remove (read-only). |
| `compress.py` | `python compress.py in.ply out.ply [--min-opacity 0.05] [--sh-degree 1]` prunes nearly transparent splats, drops unused normals, and reduces spherical harmonics (SH). Output is a standard 3DGS PLY. |

The `.ksplat` step uses the GaussianSplats3D converter (`util/create-ksplat.js`, node):
`node create-ksplat.js in.ply out.ksplat <level 0-2> <alpha threshold /255> "0,0,0" 5.0 256 <SH degree>`

## What the sample showed (596,638 splats, 148 MB, SH degree 3)
- 72.6% of the file is SH colour detail, 4.8% is normals that renderers ignore.
- Pruned PLY (opacity < 0.05, SH degree 1): 51.3 MB, 65% smaller.
- `.ksplat` level 2, SH degree 1: 18.4 MB, 88% smaller.

## Notes
- The viewer in GaussianSplats3D defaults to SH degree 0 (flat colour). Set `sphericalHarmonicsDegree` when viewing, or compressed files look flatter than the original.
- Image quality was compared by rendering the original and the compressed file in the same viewer; see `../v2_ksplat_high_fidelity/README.md` for the numbers.
- Large files, viewers and renders are kept outside the repository.
