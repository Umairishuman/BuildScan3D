# Why our 3DGS looks worse than the papers (and the earlier splatfacto runs)

Analysis from 2026-10-10. No training was run; all numbers come from the existing models and data.

## 1. What the reference methods do

| | 3DGS (Kerbl et al.) | PocketGS | VIGS-SLAM | **Our trainer (`train.py`)** |
|---|---|---|---|---|
| Initial points | Triangulated SfM points | Multi-view stereo depth only (census + SGM), confidence ≥ 0.4, **spatially balanced** | Multi-view (DROID) depth | TSDF mesh built mostly from **single-image Metric3D depth**, plus stereo points |
| Initial shape | Isotropic | Surface-aligned disc; tangential scale from 3-NN, normal from 16-NN, thickness = r·tangential (**"enough thickness for stable training"**) | Isotropic | Disc, thickness 0.1·width |
| Initial opacity | 0.1 | **0.1** | 0.5 | 0.5 |
| Shape terms during training | none | **none** ("normals serve only for initialization, never as training constraints") | **isotropic regulariser** (prevents elongation) | **flattening term** (pushes thin axis → 0) + needle cap |
| Depth loss | none | none | multi-view depth | yes, includes single-image fill |
| Poses | SfM, fixed | BA, fixed | SLAM | BA + **joint pose refinement** (up to 73 mm drift in `gs_fixed2`) |
| Rasterisation | classic | classic | classic | **anti-aliased** (opacity compensation) |

## 2. What our models actually look like

| | Splatfacto (earlier, cleaner) | **Ours (all versions)** |
|---|---|---|
| Thickness ÷ width (median) | 0.13–0.25 | **0.000** |
| Splats thinner than 1% of their width | 2–12% | **77–100%** |
| Nearly transparent (opacity < 0.1) | 11–19% | **48–51%** |
| Solid (opacity > 0.9) | 33–55% | **12–17%** |
| Typical splat width | ~7 mm | 13–15 mm |
| Splat count | ~1M | 2.3–3.2M |

Splatfacto builds the room from small, solid, slightly thick splats. Ours are wide, paper-thin, half-transparent sheets layered by the millions. Layered semi-transparent sheets are exactly the hazy, cotton-like look.

## 3. Root causes, ranked

1. **Flattening regulariser × Adam → degenerate splats.**
   - For a disc seen face-on, the photometric loss barely depends on its thin axis, so the flattening term is effectively the *only* gradient on that parameter.
   - Adam normalises gradient magnitude, so even a tiny weight drives the thin axis to zero at full learning rate (median thickness/width 0.000).
   - Seen at any angle other than face-on, such discs become streaks and needles.
   - PocketGS keeps a minimum thickness and never constrains shape during training; VIGS-SLAM does the opposite (anti-elongation).
2. **Anti-aliased rasterisation × degenerate splats → crushed opacity.**
   - gsplat's anti-aliased mode scales opacity by how much screen area a splat's footprint covers after a small blur.
   - A zero-thickness disc covers almost none, so its effective opacity collapses.
   - The optimiser compensates with more, larger, semi-transparent sheets (48–51% of splats at opacity < 0.1).
3. **Initialisation from the wrong surface.**
   - 19–26% of bundle-adjustment points (accurate to 0.6 px, seen in ≥ 3 views) lie more than 5 cm from the TSDF mesh, and 20–26% are more than 5 cm from any initial point.
   - Those points sit exactly on the textured detail. The 110–115k triangulated points we already have were never used for initialisation.
4. **Depth loss partly from single-image depth.** Even with low weight on filled pixels, it pulls geometry toward Metric3D's guess. None of the image-only methods use a depth loss; metric scale already comes from the BA poses.
5. **Joint pose refinement after BA** lets poses drift (median 10.8 mm, max 73 mm in `gs_fixed2`) to absorb errors elsewhere. The papers keep BA poses fixed.
6. **Initial opacity 0.5** instead of 0.1 (minor).

What is *not* the main problem:
- **Poses and sync:** BA reprojection error is 0.6 px.
- **The trainer's capacity in principle:** on 20 frames it fits at 31 dB.
- **The preprocessing:** keyframe selection, tracking-loss filtering, BA and MVS are sound and should be kept.

## 4. Rebuilt training recipe (standard 3DGS + PocketGS-style initialisation)

**Keep:** keyframes, tracking-loss filter, BA poses (metric scale), MVS, exposure compensation, outlier-frame rejection, data in RAM, splat cap, full-resolution final phase.

**Change:**
1. **Initialisation:**
   - BA triangulated points (≥ 3 views) plus MVS-measured points only, with no TSDF and no Metric3D.
   - Voxel-downsampled for spatial balance.
   - Normals from 16-NN PCA, tangential scale from 3-NN mean distance, thickness ≈ 0.2 × tangential scale.
   - Initial opacity 0.1.
2. **Loss:** L1 + SSIM only (+ exposure). Remove the flattening term and the needle cap. Optionally add a weak VIGS-style anti-elongation term.
3. **Depth loss off by default.** At most a weak term on MVS-measured pixels only, as an ablation.
4. **Classic rasterisation** (anti-aliasing off).
5. **Pose refinement off** (BA poses fixed).
6. **Standard schedule:** densify from 500 to ~50% of steps, opacity reset every 3000, gradient threshold 0.0002, ≥ 30 steps per frame.
7. **Sanity baseline:** train Nerfstudio splatfacto (known-good) on the same BA poses and BA/MVS init. Our trainer should match or beat it before adding anything.

**Acceptance checks (`diagnose.py`):**
- training-view PSNR > 27 dB;
- render/photo sharpness ratio near the 20-frame reference (0.29);
- thickness/width median > 0.05;
- opacity < 0.1 for under 25% of splats.

**Metric accuracy** comes from the BA poses (verified trajectory scale 1.000–1.003). Validate it with tape-measure comparisons, not with a depth loss.

## 5. Results after the fix (2026-10-10)

| `diagnose.py`, roomAttemptSadness2 | Old baseline | `gs_fixed2` | Our trainer, new recipe (`gs_v4`) | **Splatfacto on our inputs** |
|---|---|---|---|---|
| Training views, colour-fit PSNR | 21.36 dB | 22.16 dB | 26.06 dB | **28.08 dB** |
| Held-out views, colour-fit PSNR | 21.48 dB | 21.65 dB | 24.70 dB | **27.81 dB** |
| Render/photo sharpness ratio | 0.04 | 0.07 | 0.36 | **0.49** |
| Splat thickness ÷ width | 0.000 | 0.000 | 0.08 | **0.11** |
| Opacity < 0.1 / > 0.9 | 48% / 12% | 48% / 17% | 59% / 15% | **21% / 55%** |

- **Splatfacto meets every acceptance check:** train-view PSNR > 27 dB, thickness/width 0.11, 21% of splats with opacity < 0.1. Its held-out PSNR (27.81) is close to its training PSNR, so it generalises.
- **Our own trainer, with the plain recipe, closes most of the gap** but not all of it. Remaining differences from splatfacto include densification thresholds (absolute gradients), its resolution schedule, SH degree 3, culling rules and 30k iterations.
- **Pipeline decision:** preprocessing is ours; training is splatfacto on BA poses (fixed, metric) with `init_points.ply`. See `run_arcore3dgs.bat`.
