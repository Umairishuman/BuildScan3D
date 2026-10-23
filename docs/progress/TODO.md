# BuildScan3D — To Do

## IMMEDIATE PRIORITY: make v3 top-notch (run overnight, one experiment per night)

Baseline: `saved_models/2026-10-11_sfm_v3/` (newRoomAttemptSadness: held-out SSIM 0.857, PSNR(cf) 25.57, geometry median 0.59%). It is never overwritten.

Every experiment writes to its own folder, is compared with `compare_models.py --split nerfstudio` (held-out frames + room-centre views), `fit_diag.py` (full-res training views) and full-res crops against the source photos, and replaces v3 only if it is clearly better visually *and* in the numbers. Use only the bilateral-grid recipe (no SO3xR3, no splatfacto-big thresholds: those run out of the 8 GB VRAM).

**Overnight 2026-10-12 results: new best = `saved_models/2026-10-12_sharp_mvs_v6/` (viewer default).** Fair test on 42 frames no model trained on: v3 26.04 dB / SSIM 0.8756, v4_sharp 26.30 / 0.8849, v5 26.51 / 0.8879, **v6 26.52 / 0.8886**. Finest detail at full res; room-centre views clean. Tools: `select_sharp.py`, `mvs_init.py`, `fair_compare.py`; nerfstudio pin_memory patch for > 1000 frames (see memory / GPU notes).

- [ ] **Put v6's recipe into `run_arcore3dgs.bat`.** Not done yet: needs testing on room 2. Tonight's frames were registered into v3's existing COLMAP model; a fresh pipeline would need `select_sharp.py` → `sfm_colmap.py` on ~1100 frames (exhaustive matching ~4× longer, ~90 min, so switch to sequential/spatial matching) → dense → `mvs_init.py` → splatfacto with `--pipeline.model.densify-grad-thresh 0.0006`.
- [x] **0. Blur check.** Median keyframe blur from the gyroscope is **~6–12 px** (exposure 1/60–1/30 s); 89–97% of keyframes are above 3 px. The rotation part dominates (median 9.7°/s while walking). Laplacian sharpness hardly correlates with gyro blur (r = 0.20), so the old selection was mostly picking texture, not stillness. → Step 3 is worth doing.
- [x] **1. Dense MVS initialisation.** Done overnight: COLMAP PatchMatch at 1000 px with 8 sources (2 h 15 min, deleting depth maps afterwards keeps it at 123 MB) → 1.15M fused points → `mvs_init.py` (trimmed Sim3 into the training world, 1 cm voxels + SfM points, ~460k points). Adds +0.21 dB / +0.003 SSIM on top of sharp frames. Original plan: (PocketGS operator G; PocketGS's own table: 3DGS from dense COLMAP MVS points beats SfM-initialised 3DGS, SSIM 0.834 vs 0.791). v3 starts from ~69k SfM points with almost none on plain walls or the floor.
  - Run COLMAP `patch_match_stereo` + `stereo_fusion` on `work_sfm` (undistorted SfM model, ~960 px, 12 sources): ~1.5 h.
  - Voxel-downsample the fused cloud (~1 cm) to `init_points.ply` in a copy of work_sfm.
  - Retrain with the v3 recipe (~45 min). Optionally seed splats as surface-aligned flat discs (PocketGS operator I: PCA normals from K=16 neighbours, width = mean distance to 3 neighbours, thickness 0.3×, opacity 0.1).
- [x] **2. More (and sharper) training frames.** Done overnight as gyro-aware selection (`select_sharp.py`, least predicted blur per 0.2 s window): 1166 frames, registered into v3's model in ~16 min (CPU SIFT, 8.4k time-neighbour pairs, `image_registrator` + global BA 0.97 → 0.88 px), 1108 kept. The biggest single gain: +0.26 dB / +0.009 SSIM. Original plan: v3 uses 574 of 7,177 video frames (one per ~0.4 s).
  - Extract ~2× keyframes (`prepare.py --window 4 --depth 0` into a new work dir).
  - Register the new frames into the existing COLMAP model (`feature_extractor` + matching against temporal and spatial neighbours + `image_registrator` + `bundle_adjuster`), rather than a new exhaustive match.
  - Undistort, export, retrain. ~1–2 h.
- [ ] **3. Motion-blur + rolling-shutter compensation using the IMU** ("Gaussian Splatting on the Move", Seiskari et al. 2024). Model each frame as a blur along the camera motion during exposure plus the row-by-row rolling-shutter time offset; the motion comes from our calibrated IMU (`imu.py`, `fallback.py`). Also a thesis novelty: ARCore/IMU data improving 3DGS quality, not just scale.
  - First check whether the paper's code can be ported to our nerfstudio 1.1.5 / prebuilt gsplat 1.4 (we cannot recompile gsplat CUDA). Otherwise render N sub-frames per training step in Python; training becomes ~1.5–3 h.
  - Exposure time: **the app now logs it** (2026-10-12, see below), so new recordings have the real per-frame exposure and rolling-shutter readout. Older recordings need it estimated or learned.
  - Estimate: 3–5 days, 6–10 h GPU. Only if step 0 shows meaningful blur.
- [ ] **4. PGSR-style geometric regularisation during training** (PGSR paper in `docs/Research Papers`): flatten Gaussians (min-scale loss), unbiased plane-based depth, single-view depth/normal consistency with edge-aware weights, multi-view homography consistency. Rendering quality stays about the same as 3DGS while geometry gets much flatter and sharper. This is the proper way to get flat walls/floors (see the parked flattening project) without losing the glossy floor. Needs a custom splatfacto model: several days.
- [ ] **5. Anti-aliasing (Mip-Splatting idea / gsplat `rasterize_mode="antialiased"`)** for zooming in/out in the viewer without sparkle or blur. Cheap to try with step 1 or 2. Note: antialiased PLYs need an antialiased-aware viewer, so update `view.py` too.

### Fast pipeline v7 (2026-10-21): REJECTED on quality, continue later
Goal: < 15 min end to end at v6-like quality.
- Recipe: `select_sharp.py --window 12` (592 frames) → `sfm_colmap.py --pairs arcore` (new: temporal ±10 + 20 nearest by ARCore pose, 13.3k pairs vs 175k exhaustive) → global_mapper → no dense MVS → splatfacto 10k iterations with the schedule scaled down (stop-split 5k, resolution-schedule 1k, sh-interval 333, means/bilateral-grid lr max-steps 10k). Output: `dataset/newRoomAttemptSadness/work_v7_sfm/gs_v7_10000/`.
- Time: **24 min 56 s** = selection 1:47, SfM 5:15 (matching **54 s instead of 23 min**; 586/592 registered, Sim3 4.1 cm), training ~17 min (~100 ms/step at full res on the 3070).
- Quality (`fair_compare.py`, now with test-time pose refinement, which is needed because independent SfM solutions differ ~0.1–0.2° / mm–cm per camera; without it v7 scored a misleading 21.4 dB): v3 25.81 / 0.866, v6 26.45 / 0.883, **v7 24.83 / 0.848**. Fine detail lost (printer vents), and **views off the camera path are clearly worse**. The user rejected it. Sheets: `dataset/newRoomAttemptSadness/night_compare/v7_refined/`.
- Kept: the ARCore-guided matching (a large, safe win) and the pose-refined `fair_compare.py`.
- Ideas for "fast without losing quality", not yet tried:
  1. Train mostly at half resolution and finish at full res (training is now 2/3 of the time).
  2. Fast dense init to replace the 2 h COLMAP PatchMatch: low-res PatchMatch on ~100 frames, or our GPU plane-sweep `mvs.py` on SfM poses, or ARCore depth where valid. Dense init is what keeps off-path views coherent.
  3. Keep v6's frame count (~1100) but match them with ARCore-guided pairs (SfM stays ~5–8 min).
  4. Faster 3DGS training methods from the literature (PocketGS's training-side baselines: DashGaussian, Taming-3DGS, FastGS, speedy-splat) to reach 30k-quality in fewer steps; check what runs with gsplat 1.4.
  5. Cloud RTX 3090/4090 (RunPod path in `server/`) roughly halves training.
  6. Add an off-path quality metric (room-centre / novel views, e.g. agreement with a 30k reference model), so speed experiments are judged on what failed here, not only on held-out frames along the path.

### App update (2026-10-12, `CaptureLogger.java`), built into `app-debug.apk`
- [x] `camera.csv`: per-frame exposure time, rolling-shutter skew, frame duration, ISO, focus distance, AE/AWB/lens state (ARCore `Frame.getImageMetadata()`). This is the input for IMU motion-blur / rolling-shutter modelling (step 3).
- [x] `anchors.csv`: a reference anchor at the camera every 10 s, all anchor poses logged at 5 Hz. ARCore moves anchors when it silently corrects its world frame, so a jump = a re-anchor event, and its size is the correction (the newRoom 1 m / 28° event would now be visible). `check_capture.py` reports these events.
- [x] `lens_metadata.json` / `camera_characteristics.json`: the phone's own lens calibration and distortion (ARCore metadata + Camera2 `LENS_INTRINSIC_CALIBRATION` / `LENS_DISTORTION`), for comparison with COLMAP's self-calibration (k1 ≈ 0.08, k2 ≈ −0.2).
- [x] Raw depth is saved only when ARCore produced a new map (the same stale map used to be written repeatedly).
- [x] `select_sharp.py` uses the recorded per-frame exposure instead of the 1/45 s assumption; `check_capture.py` reports exposure, rolling-shutter readout and re-anchor events.
- [ ] Exposure lock is not possible through the normal ARCore session API (ARCore owns the camera's auto-exposure). It would need ARCore's Shared Camera API (custom capture requests), a larger refactor. The bilateral grid already absorbs exposure changes, so this is low priority.
- [ ] Use `anchors.csv` corrections in the pipeline: re-align pre-correction ARCore poses (better Sim3 inliers, and a COLMAP-free fallback).

### Parked (later)
- **Wall/floor flattening.** Post-hoc snapping (`planarize.py`) killed the glossy-floor reflections and crushed door frames, so it was rejected by the user. The structural layer (`structure.py`) works for geometry: per-wall planes, corners, wall lengths 6.649/6.682 × 4.451/4.475 m, 5 doors detected. Its flat textures can't reproduce the glossy floor. Use it for measurements, openings and the floor plan; fix the ceiling-height detection (2.555 m is probably the top of the cupboards or doors). Visual flattening should come from step 4.

## CURRENT PIPELINE (2026-10-11): image-based SfM + ARCore scale — see Problems_and_Solutions 4.11

`run_arcore3dgs.bat <dataset>` runs `prepare.py --depth 0`, then `sfm_colmap.py` (COLMAP 4.2: SIFT, exhaustive matching, global mapper, lens self-calibration, undistortion, Sim3 to raw ARCore, mis-registration filter), then `export_nerfstudio.py --downscale 1`, then splatfacto at full resolution (bilateral grid, SO3xR3 camera optimiser, scale regularisation) and `ns-export`. The output is `<dataset>/work_sfm/gs_sfm/splat.ply`. The old ARCore-pose pipeline is in `run_arcore3dgs_legacy.bat`.

- [x] Root cause of every bad model: an ARCore silent re-anchor (first 60 s off by 1 m / 28°), no lens distortion in ARCore's intrinsics, 8% of frames unregistered, and half-resolution training.
- [x] newRoomAttemptSadness v1 (`work_sfm/gs_sfm`): training views 28.2 dB (was 21.9), held-out 27.2 dB / SSIM 0.864 (was 22.7 / 0.782). The room centre is coherent.
- [x] `splatfacto-big` thresholds (cull 0.005, grad 0.0005) run out of the 8 GB VRAM at full res around step 12.5k. Use the default thresholds.
- [x] Bilateral grid removes the cloudy walls. v3 (bilateral grid + scale regularisation, **no** camera optimiser) is the best model: `newRoomAttemptSadness/work_sfm/gs_sfm_v3` (viewer default).
- [x] Validated on roomAttemptSadness2 (`work_sfm/gs_sfm_v3`):
  - COLMAP registered 748/759 frames, including the tracking-gap frames the old pipeline had to discard; 739 kept.
  - Held-out SSIM 0.912; geometry median 0.45%, 1.1% > 25% off.
  - Room-centre views are clean where the old model had ghosts.
  - Before/after sheets are in `roomAttemptSadness2/before_after/`.
- [ ] End-to-end time is about 75 min (matching 23, mapping 6, training 45). Speed-ups: ARCore-pose-guided matching pairs instead of exhaustive; 15k iterations; fewer keyframes on slow walks.
- [ ] Novelty re-scope: ARCore remains valuable for metric scale, gravity, live IQA, coverage guidance and frames SfM cannot register (fallback). Measure tape-measure accuracy of the Sim3 scale.
- [ ] More keyframes, by registering extra frames into the model, for better off-path views.
- [ ] Speed: exhaustive matching takes 23 min for 592 frames. Try sequential + loop detection (vocab tree) or ARCore-pose-guided pairs.

---

Status as of 2026-10-06 (legacy). Pipeline lives in `src/arcore3dgs/`:
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

## newRoomAttemptSadness (2026-10-10)

- [x] Capture checks passed: 240 s, 0% tracking loss, 5% bad IQA, sync r = 0.92, 0% NaN.
- [x] Processed in ~1 h 50 min. Final model `work/gs_final` = splatfacto (15k iterations, all 592 keyframes) initialised from the PocketGS-style dense prior (3 cm voxels). Clean near the walked path; off-path views from the room centre still messy.
- [ ] **App bug: ARCore depth was stale** in this recording (every map identical, median 9.3 m, confidence ≈ 0), so depth anchors and the coverage overlay had no data. Investigate (DepthMode / acquireRawDepthImage after the coverage changes).
- [ ] 168/592 keyframes had no stereo neighbours (turning on the spot) → only 28% of pixels in the dense prior. Encourage sideways sway while turning.
- [x] `mvs.py --min_votes` option (1 used here); fixed a crash when a neighbour frame had no stereo sweep.
- [x] Geometry check (rendered depth vs BA points seen in ≥ 5 views, held-out frames) explains "objects move when rotating":

  | Model | Median depth error | > 25% off | Held-out colour-fit PSNR |
  |---|---|---|---|
  | `gs_final` (splatfacto from dense prior) | 6.9% | 25% | 21.8 dB |
  | `gs_measured` (splatfacto, measured-only init) | 5.2% | 18% | — |
  | `gs_sparse` (our trainer + BA sparse depth loss) | 1.9% | 19% | 21.6 dB |

  For comparison, room 2 splatfacto: 2.9% / 4%. The dense prior was wrong here because only ~28% of pixels had real stereo support and the Metric3D fill errs consistently across neighbouring frames, so it passes the consistency check.
- [x] New: `train.py --sparse_depth_w` (depth loss at BA-triangulated points); `clean_splats.py --ba_evidence`. Pruning did not remove the error tail (−0.4 dB), so it is not used.
- [x] The remaining tail is concentrated in the first 20 s (76% bad, always "something in front"). Inspected: a **glossy polished wooden floor** (reflections of the lamp and furniture) and a **glass dining table**. The disagreement sits at floor level, so the reference BA points there are likely reflections triangulated "behind" the floor, not only a depth error. Every dense method disagrees there.
- [x] **COLMAP PatchMatch depth (2026-10-11)**: `colmap_mvs.py` (COLMAP 4.2.0 CUDA in `tools/colmap_dl/`). Our BA poses are held fixed (verified unchanged), BA co-visibility gives the matching pairs, then `point_triangulator`, PatchMatch at 960 px with 12 sources, and fusion. About 2 h on the RTX 3070. Output: `depth_colmap/`, `colmap_points.ply` (1.08M fused → 515k points at 1 cm). Depth vs BA points (every 3rd frame):

  | Depth | Pixels | Median err | > 10% off | > 25% off | Walls > 5 m, > 25% off |
  |---|---|---|---|---|---|
  | ours, stereo only | 12.4% | 0.73% | 8.2% | 3.5% | 5.5% |
  | ours + Metric3D fill (used for training so far) | 100% | 1.72% | 22.4% | 11.0% | 17.3% |
  | COLMAP (geometric) | 24.0% | 0.59% | 5.1% | 1.5% | 5.4% |
  | COLMAP ∪ our stereo (`--depth_src colmap`) | 25.1% | 0.62% | 5.2% | 1.6% | 4.4% |

- [x] **Median filtering** (suggested by the user's uncle; tested here). A hole-aware 5–9 px median on our stereo depth cut > 25% outliers from 3.3% to 2.4–2.7%. Across 7 views it cut them to 2.1%, but lost coverage. It does nothing for the Metric3D fill, whose errors are regional, not speckle. On COLMAP depth it changes nothing, because COLMAP already filters. Kept as a 5×5 step in `colmap_mvs.py --median`. Do not median-filter images: it removes the texture 3DGS needs.
- [x] Trained and compared (`compare_models.py`, 60 held-out frames; geometry = rendered depth vs BA points seen in ≥ 5 views):

  | Model | Colour-fit PSNR | SSIM | Geometry median | > 10% off | > 25% off | Train time |
  |---|---|---|---|---|---|---|
  | `gs_final` (splatfacto, dense prior) | 21.82 | 0.759 | 6.32% | 40.5% | 22.8% | — |
  | `gs_sparse` | 22.08 | 0.771 | 1.25% | 15.6% | 8.9% | 22 min |
  | `gs_colmap` (COLMAP depth + init) | 22.12 | 0.768 | 1.36% | 16.7% | 9.4% | 17 min |
  | **`gs_colmap_nc`** (+ `--near_cam 0.25`) | **22.67** | **0.782** | 1.32% | **14.8%** | **7.3%** | 28 min |

  `gs_colmap` alone was the sharpest from 60 s on, but a large floater sat on the start viewpoint: 10 of 17 frames in 0–20 s were more than 20% covered at < 30 cm. Post-hoc pruning (`clean_splats.py --cam_radius`, COLMAP evidence) made every model worse (−1.3 to −1.6 dB; it exposed clutter behind the removed splats). Removing near-camera splats *during* training (`--near_cam`) fixed the start view and is the best overall → viewer default.
- [ ] `--near_cam` slows training (28 vs 17 min) because the CPU KD-tree query runs every 100 steps; use a GPU voxel hash or query every 500 steps.
- [ ] Off-path views from the room centre are still messy in every model, because no camera ever stood there. Capture fix: a few 360° turns from the middle of the room.
- [ ] Reflective surfaces (glossy floor, glass): mask them out of BA, depth and the evaluation reference, e.g. by excluding points below the fitted floor plane.
- [ ] Bring splatfacto's densification (absgrad, culling, resolution schedule) into `train.py` so sparse depth supervision can be combined with splatfacto-level sharpness.
- [ ] Large rooms: walls 5–9 m away exceed ARCore depth range; capture closer passes (≤ 3 m) or split the room into sections.

## Next capture (2026-10-10) — recording pipeline verified correct (Problems 4.8); limit is coverage

- [ ] Record a 3DGS-oriented capture of a room (~3 min, all lights on, slow):
  - loop 1: walk the room perimeter at chest height, phone facing the room centre;
  - loop 2: same at knee height, tilted slightly up;
  - loop 3: stand at 2–3 points in the middle, turn slowly through 360° facing the walls;
  - keep an edge/corner/object in frame when filming plain walls or ceiling; pause ~3 s after any tracking warning.
- [ ] Optional: Census + SGM MVS as in PocketGS (expected small gain; our verified dense prior already covers 70% of pixels).
- [x] Viewer: up to 60 fps while moving (`--fps`, half resolution while moving).

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

- [x] Tape vs model (viewer measure tool), newRoomAttemptSadness, SfM v3 model, 2026-10-11:

  | Object | Model | Tape | Error | Relative |
  |---|---|---|---|---|
  | Table (short side) | 0.458 m | 0.459 m | −1 mm | −0.22% |
  | Chair (soft edge) | 0.361 m | 0.368 m | −7 mm | −1.90% |
  | Rug, 2 points (soft edge) | 0.858 m | 0.870 m | −12 mm | −1.38% |
  | Table (long side) | 1.748 m | 1.750 m | −2 mm | −0.11% |
  | Wall | 2.792 m | 2.800 m | −8 mm | −0.29% |
  | Room length | 6.692 m | 6.700 m | −8 mm | −0.12% |

  Rigid objects: mean 4.8 mm / 0.19%. The error does not grow with length (−8 mm at both 2.8 m and 6.7 m), so the scale is good to about 0.1%. The consistent small negative offset looks like endpoint picking (clicks land just inside edges and corners).
- [ ] More references (room 2, room height, doors) plus 3 repeated clicks each, to quantify clicking error.
- [ ] Viewer: snap measure clicks to corners/edges to remove the endpoint-picking bias.
- [ ] Script: compare model measurements against tape measurements → mean / max dimensional error (cm).
- [ ] Report alongside: reprojection error before/after BA, MVS coverage, colour-fit PSNR/SSIM, free-space violation ratio.

## Novelty (after the optimisations above)

- [x] **Featureless-tracking fallback (2026-10-10, Problems 4.10):** IMU extracted from the ARCore MP4; self-calibrated; gaps bridged (9 s gap: 3.8 cm / 0.38° vs 30.6 cm / 17.3° interpolation); ARCore post-gap frame jumps detected and corrected; PnP re-alignment to the map; unverified segments excluded. In `run_arcore3dgs.bat`.
- [ ] Tune BA pass 2 so it keeps PnP accuracy (8.2 px → 15.1 px after BA): weaker within-segment ARCore priors after a gap.
- [ ] Use bridged fallback frames in training with per-frame pose refinement (currently only re-aligned segments are used).

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
- [x] **Live coverage overlay (tier 2, 2026-10-10)** — `CoverageMap.java` + `CoverageOverlayView.java`: ARCore depth → 10 cm voxels, each remembers from how many directions (8 azimuth × 2 elevation) it was seen; dots over the camera view: red = 1 direction, yellow = 2–3, green = 4+, no dot = unmapped. End-of-recording dialog adds the coverage summary. Builds; **not yet tested on device**.
- [x] `check_capture.py`: validates a recording (files, video, poses, tracking, IQA, depth, NaN, sync) before processing.
- [x] **Performance fix (2026-10-12)**: during recording, skip all demo rendering (planes, virtual objects, PBR lighting, cubemap filtering). Only camera feed + capture logging + quality overlay runs. Reduces GL thread load significantly. Also: IQA image analysis every 5th frame (was 3rd), coverage overlay at 2 Hz (was 5 Hz), coverage projection capped at 5000 voxels, overlay drawing capped at 2000 dots.
- [x] **Upload & Process UI (2026-10-12)** — `ProcessingActivity.java`: after recording stops, dialog offers "Upload & Process" button. Zips depth folder, uploads all dataset files to the processing server via OkHttp multipart POST. Polls `/status/{job_id}` every 3s and shows progress bar, step label, elapsed time, and recent logs. Retry on failure. OkHttp 4.12.0 added as dependency.
- [x] **Configurable server URL (2026-10-12)**: settings menu → "Server URL" → saves to SharedPreferences. No recompile needed to change the server address.
- [ ] (remaining tier-2 ideas) on-device image quality assessment while recording, which tells the user live:
  - which sections are left to record or need further scanning (surfaces seen from too few viewpoints or angles, ceiling or floor missing, holes in ARCore depth coverage);
  - when frames are too blurry, too dark or overexposed, or the camera is moving too fast;
  - when tracking is degraded or lost (from `tracking.csv` state and failure reason).

  Show this as an overlay or heatmap on the camera view, so missed areas are fixed during capture instead of after processing.
- [ ] Lock exposure / white balance during recording (cuts the per-image colour drift that training compensates for).
- [ ] Download and preview the finished splat.ply on the phone after processing completes.

## Server & automation

- [x] **Processing server (2026-10-12)** — `server/main.py` (FastAPI): receives dataset uploads from the app, runs the pipeline as subprocesses with per-step timeouts (watchdog kills hung steps), serves progress via `/status/{job_id}`. Endpoints: `/upload`, `/status/{job_id}`, `/jobs`, `/download/{job_id}`, `/config`, `/health`.
- [x] **RunPod on-demand integration (2026-10-12)** — `server/runpod_client.py`: creates a GPU pod via RunPod API, installs deps via SSH, uploads dataset via SCP, runs pipeline remotely, downloads result, always terminates the pod (even on error). Supports configurable GPU type (default RTX 4090). Switch between local and RunPod mode via `POST /config` or `RUNPOD_API_KEY` env var.
- [ ] End-to-end test of RunPod flow (create pod → process → terminate).
- [ ] Build a Docker image with pre-installed deps (COLMAP, nerfstudio) to skip the setup step on each pod launch (~5 min saved).
- [ ] Move server to a cheap always-on VPS so the phone can upload without the PC running.

## Project organisation

- [x] **Folder cleanup (2026-10-12)**: moved all `.bat` launchers to `scripts/`, proposal docs to `docs/proposal/`, progress docs to `docs/progress/`. Added `docs/Flow.md` documenting the full system flow and project structure.

## Known environment notes

- gsplat CUDA extension is prebuilt and loaded via `nerfstudio-env/Lib/site-packages/gsplat/csrc.py`. That file explains how to refresh it after a gsplat, torch or CUDA upgrade.
- Open3D 0.20 (system Python) has broken TSDF fusion. Run fusion with `nerfstudio-env` (Open3D 0.19).
- Steam uses port 8080, so the viewer runs on **7010**.
