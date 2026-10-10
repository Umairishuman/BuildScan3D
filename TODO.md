# BuildScan3D — To Do

Status as of 2026-10-06. Pipeline lives in `src/arcore3dgs/`:
`prepare.py → ba.py → mvs.py → align_fuse.py --depth_dir depth_mvs → train.py`
(one command: `run_arcore3dgs.bat <dataset_dir>`, view with `view_splat.bat`, evaluate with `compare.py`).

## Now — finish the current capture (roomAttemptSadness)

- [x] **Train v3 on the cleaned two-pass fusion** (paused to free the PC). Close the viewer first; 8 GB VRAM overflows otherwise.
      `nerfstudio-env\Scripts\python.exe -W ignore -u src/arcore3dgs/train.py --work dataset/roomAttemptSadness/work --out dataset/roomAttemptSadness/work/gs_v3 --steps 7000`
- [x] Check that the floating curtain/cupboard copies above the bed are gone. Free-space floaters 10.7% → 7.4% of visible splats; the big ghost in front of the curtain is gone. Colour-fit PSNR 21.74 → 21.37 dB, SSIM unchanged at 0.769.
- [ ] Remaining 7.4% free-space floaters: try a free-space loss during training (see Novelty) rather than more pruning.
- [x] Run `compare.py` on v1 / v2 / v3 (renders in `work/compare_v3/`), then point `view_splat.bat` at `gs_v3`.
- [ ] Commit `src/arcore3dgs/`, the app changes (`CaptureLogger.java`) and the `.bat` launchers. Nothing is committed yet.

## Next — new capture with the updated app

- [x] Install the updated app and record: `roomAttemptSadness2` (292 s, realme RMX5111). All files written; fixed NaN rows in `points.csv` (app + loader).
- [ ] Record one room using the capture protocol:
  - [ ] ceiling and floor sweeps, **but in plain/white rooms keep an edge, corner, light fitting or furniture in frame** — pure blank ceiling/wall views caused all 4 tracking losses in roomAttemptSadness2 and 50–94% of upward-looking keyframes were inconsistent
  - [ ] after a tracking loss, go back to an area that was tracked well and pause ~3 s before continuing
  - [ ] every wall at two heights (chest and knee)
  - [ ] slow movement (about half the speed of roomAttemptSadness)
  - [ ] close passes (30–50 cm) over anything that must look sharp up close
  - [ ] lock exposure if possible (add to app)
- [x] ARCore raw depth as an extra anchor (`mvs.py --arcore_depth 1`): ARCore vs MVS agree within 2.7%; fusion keeps 573 instead of 525 frames, p90 depth disagreement 22.1% → 15.7%, floaters 8.1% → 7.1%; image quality unchanged (colour-fit PSNR 21.35, SSIM 0.810). Consider making it the default.
- [ ] Full-quality run on the new capture: full resolution, 15–30k steps.

## Current default (2026-10-10): PocketGS-style pipeline — see Problems 4.7

- [x] `pocket_prior.py`: movement-gated keyframes (8 cm / 6°) + multi-view-consistent dense prior (70% of pixels verified, 2 cm voxels).
- [x] Short photometric training from the prior: `gs_pocket8k` (12.7 min) is coherent off-path and reasonably sharp; default in `run_arcore3dgs.bat` and `view_splat.bat`.
- [ ] Speed: try 5k steps / smaller full-res fraction (3k half-res = 2.3 min but softer).
- [ ] Sharpness at recorded viewpoints: still below splatfacto — try a weak depth term towards the consistent prior during the full-res phase.
- [ ] Off-path evaluation metric for the thesis (e.g. free-space violations + rendered-depth agreement with the prior), since held-out PSNR near the path is misleading.

## PRIORITY 0 — rebuild the training recipe (2026-10-10, see `docs/Training_Analysis.md`)

`gs_fixed2` still looks worse than the early Nerfstudio splatfacto runs. Splat statistics explain it: our splats are degenerate (thickness/width 0.000 vs 0.13–0.25 in splatfacto), half-transparent (48–51% opacity < 0.1 vs 11–19%) and twice as wide. Causes: flattening regulariser × Adam, anti-aliased opacity compensation on zero-thickness splats, initialisation from a TSDF/Metric3D surface that misses 19–26% of the triangulated points, depth loss from single-image fill, and joint pose drift.

- [x] Init from BA triangulated points + MVS-measured points only (`make_init.py`): 662k points, 1 cm voxels, discs thickness 0.2, opacity 0.1.
- [x] Flattening term and needle cap off by default.
- [x] Depth loss off, classic rasterisation, pose refinement off (defaults in `train.py`).
- [x] Splatfacto on the same BA poses + init (`export_nerfstudio.py`): **held-out colour-fit PSNR 27.81 dB, sharpness 0.49** — best so far; now the default trainer in `run_arcore3dgs.bat`. Our trainer with the new recipe: 24.70 dB.
- [x] Acceptance met by splatfacto (28.08 dB train views, thickness 0.11, 21% opacity < 0.1).
- [x] Viewer: 45° FOV + 15 cm near clip by default, with sliders (the 75° default showed never-filmed directions → smears).
- [x] Floater pruning tool `clean_splats.py` (measured free space; not used by default: −0.3 dB, no visible gain).
- [ ] Ceiling / upper-wall coverage: still poor; needs capture (keep an edge in view) or the planar prior.
- [ ] Tape-measure check on roomAttemptSadness2 using the splatfacto model (metric accuracy).
- [ ] Optional: close the remaining gap in our own `train.py` (absgrad densification, resolution schedule, SH 3) if we need features splatfacto lacks.

## PRIORITY — fix the baseline before adding ARCore depth (2026-10-09)

The baseline itself is bad, so anything layered on top (ARCore depth anchors) inherits it. `diagnose.py` (render-only, no training) shows the trainer **underfits**: the model cannot reproduce its own training images.

| | Room 1 (gs_v3) | Room 2 (gs) |
|---|---|---|
| Colour-fit PSNR on its own *training* views | 22.06 dB | 21.36 dB |
| Render sharpness / photo sharpness (same view) | 0.11 | 0.04 |
| Splats with opacity < 0.1 ("cotton") | 49% | 48% |

A healthy 3DGS fits its training views at ~28–35 dB. Train ≈ test, so this is not a generalisation problem.

**Root cause:** the depth supervision target (`depth_fused/`, the fused TSDF mesh rendered back into each view) is wrong in many places. Where stereo actually measured the depth, the target is off by >5% on ~30% of pixels and >10% on ~21%; ~25% of the time it lies *behind* the real surface, so foreground objects are erased. Example: the mesh-back chair is measured by MVS but missing from the fused target, because other views see through it and TSDF carves it away. The depth loss (weight 0.5 → 0.05 over the first 60% of training) then drags those splats to the wall/floor behind, fighting the photometric loss → averaged, cotton-like texture. The post-training 10 cm prune then deletes what is left of such objects.

Secondary limits: training at half resolution (960x540) and only 7k steps.

**Results of the fixes (2026-10-09, roomAttemptSadness2):** training-view PSNR 21.36 → 22.97 (`gs_fixed`) → 23.60 dB (`gs_fixed2`); visibly sharper (desk, posters, walls no longer blotchy). Remaining gap is **capacity**: a 20-frame region fits at 31 dB and a 100-frame region at 28 dB, but the whole room shares one 3.2M-splat budget (8 GB VRAM) and the *sharpest* frames fit worst. MCMC densification was unstable here (photo error rose) and is off by default.

- [x] Supervise depth with each frame's own depth (`depth_mvs`), weighted by `mvs_mask`, instead of the fused TSDF render.
- [x] Add stereo-measured points to the initialisation (thin objects the mesh misses).
- [x] Outlier-frame rejection during training (dropped 16 frames, 13 from the post-tracking-loss tail).
- [x] Training data in pinned RAM + splat cap (VRAM); SH degree 2; 25 steps/frame; refined poses exported (`frames_refined.json`).
- [ ] **Block-wise training** (VastGaussian/CityGaussian style): split the room into 3–6 spatial blocks, train each with its own full splat budget on the cameras that see it, merge. Expected to close most of the 23.6 → 28 dB gap; costs ~1.5–2 h of GPU per room.
- [x] Fused TSDF used only for initialisation.
- [x] Depth loss 0.2 during densification, decaying to 0, error capped at 20%.
- [x] Mesh-distance prune off by default.
- [x] Last 30% of steps at full resolution (images streamed from disk).
- [ ] Re-run `diagnose.py` after each change: target train-view PSNR > 27 dB and sharpness ratio > 0.5 **before** re-enabling ARCore depth anchoring.
- [ ] Optional check: rolling-shutter signature in BA residuals (row-dependent error vs angular speed).



- [x] Diagnosed why it looked worse than the first capture: more plain wall/ceiling footage (49% flat pixels vs 38%), stereo measured only 5% of pixels, 28% of keyframes inconsistent. Inconsistency tracks viewing direction (floor/down 11–23%, up 50%, ceiling 94%) and tracking loss (< 2 s after a loss: 91%), not blur or IQA level.
- [x] Pipeline fixes: skip frames within 3 s after a tracking loss (`prepare.py --settle`, `filter_frames.py`); no BA relative-motion prior across tracking gaps; ARCore depth on by default; training steps auto-scale (15 x training frames).
- [ ] Retrain roomAttemptSadness2 with the fixes (auto steps ≈ 10–12k, ~20 min) and compare with `gs` / `gs_arcore`.
- [ ] Planar prior for blank walls/ceiling (see Novelty) — the remaining failure mode in plain rooms.

## Evaluation (thesis numbers)

- [ ] Tape-measure 10–15 references in the new room: wall lengths, room height, door width/height, desk, bed.
- [ ] Script: compare model measurements against tape measurements → mean / max dimensional error (cm).
- [ ] Report alongside: reprojection error before/after BA, MVS coverage, colour-fit PSNR/SSIM, free-space violation ratio.

## Novelty (after the optimisations above)

- [ ] **Certified measurements (headline):** every measurement comes with an error bound (e.g. 3.42 m ± 1.1 cm), built from BA pose uncertainty, measured-vs-predicted depth (`mvs_mask`) and multi-view agreement. Validate the bounds against tape-measure error.
- [ ] **Planar / right-angle priors → as-built floor plan:**
  - detect walls, floor and ceiling as planes;
  - snap Gaussians onto them and enforce right angles between near-perpendicular walls;
  - export room dimensions and a floor plan.
- [ ] **Free-space-aware training:** a loss that penalises Gaussians in space that cameras saw through (turns `consistency.py` into a training term).

## Android app

- [x] **Basic live IQA (tier 1)** — `QualityMonitor.java`: colour banner (tracking lost / moving or turning too fast / blurry / too dark / overexposed), vibration on bad quality while recording, ceiling/floor/8-direction coverage checklist, end-of-recording summary, per-frame `quality.csv`. Builds (`app-debug.apk`); **thresholds not yet tuned on a device.**
- [x] Added a "too plain / low texture" IQA warning (calibrated on roomAttemptSadness2: flags ~52% of frames just before a tracking loss, ~2% of normal frames).
- [ ] Tune IQA thresholds on the phone. (Note: the IQA level itself did not predict inconsistent frames — tracking loss and texture did.)
- [ ] **Live IQA + coverage guidance (tier 2):** on-device image quality assessment while recording, which tells the user live:
  - which sections are left to record or need further scanning (surfaces seen from too few viewpoints or angles, ceiling or floor missing, holes in ARCore depth coverage);
  - when frames are too blurry, too dark or overexposed, or the camera is moving too fast;
  - when tracking is degraded or lost (from `tracking.csv` state and failure reason).

  Show this as an overlay or heatmap on the camera view, so missed areas are fixed during capture instead of after processing.
- [ ] Lock exposure / white balance during recording (cuts the per-image colour drift that training compensates for).

## Known environment notes

- gsplat CUDA extension is prebuilt and loaded via `nerfstudio-env/Lib/site-packages/gsplat/csrc.py`. That file explains how to refresh it after a gsplat, torch or CUDA upgrade.
- Open3D 0.20 (system Python) has broken TSDF fusion. Run fusion with `nerfstudio-env` (Open3D 0.19).
- Steam uses port 8080, so the viewer runs on **7010**.
