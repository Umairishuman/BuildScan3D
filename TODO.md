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

- [ ] Supervise depth with each frame's own depth (`depth_mvs`), weighted by `mvs_mask` (measured pixels full weight, filled pixels low weight), instead of the fused TSDF render.
- [ ] Use the fused TSDF only for initialisation (and maybe a weak far-plane/free-space hint), never as a hard per-pixel target.
- [ ] Lower and shorten the depth loss (e.g. 0.1 → 0, off after densification) so photometric detail wins.
- [ ] Remove the post-train "distance to fused mesh" prune, or prune against per-frame depth instead (it deletes thin/foreground objects missing from the mesh).
- [ ] Full-resolution training for the final phase; auto steps already scale with frame count.
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
