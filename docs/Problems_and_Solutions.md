# BuildScan3D: Problems Encountered and Solutions

This log covers the ARCore → metric 3D Gaussian Splatting pipeline, developed and tested on the `roomAttemptSadness` capture (166 s handheld video, 1920×1080, about 30 fps). Each entry records the symptom, the root cause, how the cause was confirmed, the fix and the measured result. Code lives in `src/arcore3dgs/` unless stated otherwise.

---

## 1. Data alignment and coordinate systems

### 1.1 No evidence that the IMU/pose data matched the video
- **Symptom:** There was no way to tell whether `poses.csv` lined up with the video frames.
- **Investigation:** We compared camera rotation speed from the poses with image motion measured from the video (phase correlation between consecutive frames), and scanned over time offsets.
- **Finding:**
  - The two signals correlate at r ≈ 0.76–0.79 when the offset is about 0.00 s (±0.05 s).
  - So pose timestamps (ARCore `frame.getTimestamp()`) match video PTS to within about one frame.
- **Result:** The sync was fine. The earlier "MediaRecorder lag" theory was wrong, because the ARCore Recording API writes video and poses from the same frames.

### 1.2 Ghosting / duplicated geometry caused by frame-index matching
- **Symptom:** Room geometry was smeared into duplicated, overlapping copies.
- **Root cause:** `fusion_pipeline.py` paired video frame *k* with pose row *k*.
  - Poses are only logged while ARCore is `TRACKING`, so `poses.csv` has gaps of up to 0.44 s, 25 out-of-order or duplicate timestamps, and 62 fewer rows than the video has frames.
  - The index error grew from about −0.5 s at the start to about +2 s (58 frames) by the end.
  - A constant `POSE_OFFSET` cannot fix error that grows over time.
- **Fix:**
  - Read each frame's PTS with ffprobe.
  - Sort and de-duplicate the poses.
  - Interpolate the pose at each frame's timestamp (linear for position, slerp for rotation).
  - Skip frames that fall inside tracking gaps longer than 0.12 s.
- **Result:** Pose-to-motion correlation rose from 0.17–0.23 with index matching to 0.76–0.79.

### 1.3 Video appeared rotated 90°; unclear which frame the poses refer to
- **Symptom:** The video plays rotated 90° anticlockwise. It was unclear whether geometry should use the rotated or the raw image.
- **Finding:**
  - The video is stored in the sensor's native landscape orientation.
  - `camera.getPose()` refers to that same landscape camera frame, in OpenGL axes (x right, y up, looking along −z).
  - The motion correlation confirmed it: image-x motion follows camera-Y rotation and image-y follows camera-X, both with positive sign, and the cross terms are about 0.
- **Fix:** Do all geometry on the raw landscape image. Rotate only for display.

---

## 2. Depth estimation

### 2.1 Metric3D output was not metric
- **Symptom:** Depth scale was wrong.
- **Root cause:**
  - The torch-hub Metric3D model ignores the `intrinsic` argument the scripts passed in.
  - It returns depth for a canonical camera with focal length 1000 px.
  - The official recipe has three steps the scripts skipped: resize the image to fit 616×1064 and pad it, then multiply the output by `fx × resize_scale / 1000`.
- **Fix:** Implemented the full official preprocessing and the de-canonical rescaling (`prepare.py`).

### 2.2 VRAM overflow at native resolution
- **Symptom:** Metric3D ViT-Large at 1080p spilled out of the RTX 3070's 8 GB into system RAM and ran very slowly.
- **Fix:** This is solved by 2.1. The model's fixed 616×1064 input keeps memory bounded, and the depth is upsampled afterwards.

### 2.3 "Painting broken into pieces": per-frame scale inconsistency
- **Symptom:** Each view lined up from its own camera, but surfaces sat at different depths across views.
- **Root cause:**
  - Monocular depth is predicted independently for every frame.
  - Against ARCore's metric feature points, the per-frame scale varied from 0.85× to 1.50× (5th–95th percentile).
  - That is about ±25% disagreement between views of the same wall.
- **Fix (`align_fuse.py`):**
  - Rescale each frame's depth to the ARCore points visible in it, with outlier rejection and temporal smoothing.
  - Fuse all frames into one TSDF volume.
  - Ray-cast the fused mesh back into every camera, so the depth supervision is consistent across views by construction.
- **Result:** Per-frame depth agrees with the fused surface to within 5.3% (median), and rendered depth matches it to within 2.1% on held-out views.

---

## 3. Camera poses

### 3.1 ARCore pose error blurred fine texture
- **Symptom:** Fine patterns (bedsheet, wall art) were smeared even when the overall geometry was right.
- **Investigation:**
  - SIFT tracks were matched across keyframes and triangulated with the raw ARCore poses.
  - Median reprojection error was 2.32 px (p90 5.41 px) at full resolution.
  - Pose jitter was small (under 3 mm locally), so the error came from slow drift.
- **Fix (`ba.py`):** Bundle adjustment of all keyframe poses and 3D points, as PocketGS does. ARCore enters as priors:
  - tight on frame-to-frame relative motion, which keeps metric scale;
  - weak on absolute pose, which fixes the overall position and orientation of the solution while allowing drift correction.
- **Result:**
  - Reprojection error fell to 0.61 px median (p90 1.50 px).
  - Trajectory length is 0.998× ARCore's, so metric scale is preserved.
  - Corrections were 1–5 cm and about 1°, varying over time with a mean rotation under 0.1°. That rules out a systematic intrinsics error.

### 3.2 Bundle adjustment solver problems
| Problem | Cause | Fix |
|---|---|---|
| scipy `least_squares` ran 15+ min without finishing one round | A generic sparse solver doesn't exploit BA structure | Custom Levenberg–Marquardt with the Schur complement (points eliminated as 3×3 blocks, dense 3402×3402 camera system) |
| Schur product still took minutes | CPU sparse product cost grows with track length squared; some tracks span hundreds of frames | Accumulate the Schur complement on the GPU in dense chunks of points |
| Every LM step returned NaN | The rotation exponential map takes `sqrt(θ²)`, whose derivative is infinite at θ = 0, and all cameras start at the identity | Clamp θ² before the square root; reject non-finite steps |
| vmap crash | In-place writes inside `torch.func.vmap` | Build the skew matrix out of place (`torch.stack`) |
| Matching took 4 min on every rerun | Features were recomputed each time | Cache tracks in `ba_tracks.npz` |

Final BA runtime is about 2 minutes, plus a one-time 4 minutes for features.

---

## 4. Multi-view geometry

### 4.1 Wavy, lumpy walls from monocular depth
- **Fix (`mvs.py`):** GPU plane-sweep multi-view stereo:
  - 5 source views per frame, chosen from BA covisibility;
  - 64 depth hypotheses per pixel within ±35–55% of the Metric3D depth;
  - 7×7 NCC cost, using the best 3 of 5 sources;
  - a geometric consistency check (forward-backward reprojection under 1 px and depth error under 1%, in at least 2 views).
- **Limitation found:** Only about 11% of pixels per frame are measured, because the room has a lot of plain wall.
- **Mitigation:**
  - Fill the rest with Metric3D corrected by a smooth quadratic field (in log-depth) fitted to the measured pixels.
  - This corrects Metric3D's tilt and bending as well as its scale.
  - Its error against MVS dropped from 2.4% (single scale factor) to 1.1%.

### 4.2 Floating copies of the curtain and cupboard above the bed
- **Symptom:** After the MVS run, pieces of curtain and cupboard floated in the air above the bed.
- **Wrong first diagnosis:**
  - 98.6% of splats lie within 10 cm of the fused surface, so the floaters were first blamed on real objects seen against the uncaptured ceiling.
  - That was wrong: bad frames had baked the ghost copies into the fused surface itself.
- **Investigation (`consistency.py`):**
  - Free-space test: project each frame's depth into neighbouring cameras and count points that land in front of what those cameras saw through.
  - The worst frames contradicted 50–99% of what neighbouring cameras saw, and had 0% MVS-measured depth.
  - Example: frame 1282 looks across the bed at the curtain. Metric3D placed the curtain at about 1.2 m, too close, so its copy landed above the bed. That frame was also motion-blurred and had only 32 BA observations.
- **Fix: two-pass fusion (`align_fuse.py`):**
  1. Fuse only the 419 frames that have at least 3% MVS-measured depth into a trusted surface.
  2. Fit every other frame's depth to that surface with the same smooth correction (148 frames re-anchored).
  3. Drop frames that still disagree by more than 5% from fusion (85 frames). They still contribute colour in training.
- **Result:**
  - Fused room height dropped from 5.5 m to 3.9 m, which is realistic.
  - Per-frame depth agrees with the fused surface to within 2.2% (median).
  - Retraining on the cleaned surface is still pending (see `TODO.md`).

---

### 4.3 A second capture of the same room came out worse (roomAttemptSadness2)
- **Symptom:** Following the new filming checklist (ceiling and floor sweeps, walls at two heights) produced blurrier, messier results than the first capture.
- **Investigation:** Per-keyframe comparison of the two captures, then the dropped (inconsistent) frames correlated against texture, sharpness, IQA level, time since tracking loss and viewing direction.
- **Finding:**
  - The new footage had much more blank surface: 49% flat pixels vs 38%; stereo measured 5% of pixels vs 9.5%; fusion dropped 28% of keyframes vs 15%.
  - Inconsistency followed viewing direction: floor/down 11–23%, level 40%, up 50%, ceiling 94%. The walls and ceiling are plain white.
  - It also followed tracking loss: all 4 losses (233–292 s) happened while looking up; 91% of keyframes within 2 s after a loss were inconsistent, and ARCore's pose jumped 21–115 cm across the gaps.
  - Blur and the live IQA level did *not* predict it (drop rate 24–30% at every level).
- **Fix:**
  - `prepare.py --settle` / `filter_frames.py`: skip frames within 3 s after a tracking loss (read from `tracking.csv`).
  - `ba.py`: no frame-to-frame motion prior across a tracking gap, so ARCore's relocalisation jump isn't baked into the poses.
  - `mvs.py`: ARCore depth anchoring on by default (it agrees with stereo within 2.7%).
  - `train.py`: training steps scale with the number of frames (the second capture had 40% more frames on the same 7k-step budget).
  - App: new "too plain / low texture" IQA warning, calibrated on this capture to fire before tracking is lost.
  - Capture guidance: in plain rooms, keep an edge, corner or object in view when sweeping walls/ceiling.
- **Lesson:** Coverage advice has to account for texture. A blank ceiling adds frames that hurt rather than help, unless the reconstruction has a planar prior for it.

### 4.4 The baseline itself underfits ("cotton" texture): wrong depth supervision target
- **Symptom:** Blurry, cotton-like, messy renders in both rooms; ARCore depth made no visible difference.
- **Investigation (`diagnose.py`, render only):** colour-fit PSNR on the model's *own training views* was only 21–22 dB (healthy 3DGS: ~28–35 dB); render sharpness was 4–11% of the photo's; ~48% of splats were near-transparent. Train ≈ test, so the trainer underfits.
- **Root cause:**
  - The depth loss uses the fused TSDF mesh rendered into each view as its target.
  - Fusion carves away thin/foreground objects that other views see through (e.g. a mesh chair back is measured by MVS but absent from the target).
  - Where stereo measured the true depth, the target was off by >5% on ~30% of pixels and lay *behind* the real surface ~25% of the time.
  - The depth loss then drags those splats onto the wall/floor behind them, fighting the photometric loss; the 10 cm post-prune deletes the remainder.
- **Planned fix:** supervise with per-frame depth weighted by the MVS mask, keep the fused mesh for initialisation only, weaken/shorten the depth loss, drop the mesh-distance prune, train the last phase at full resolution; verify with `diagnose.py` (train-view PSNR > 27 dB) before re-adding ARCore depth.
- **Lesson:** a geometrically "clean" fused surface is not automatically a good per-pixel training target; check that the model can fit its training views before judging extra inputs.
- **Result after the fix (`gs_fixed2`):** training-view PSNR 21.36 → 23.60 dB; visibly sharper. Further experiments:
  - Overfit tests: 20 frames fit at 31.15 dB, 100 frames at 26.81 dB (15 steps/frame) / 28.15 dB (30 steps/frame) → the trainer works; the whole room is limited by **capacity** (one 3.2M-splat budget on 8 GB VRAM), and the sharpest frames fit worst.
  - Per-frame fit was uniform except the last 30 s after the tracking losses (14 dB) → automatic outlier-frame rejection (dropped 16 frames, 13 from that tail).
  - MCMC densification was unstable with this setup (photo error rose to 0.16–0.23) and overflowed VRAM at 3.5M splats; default densification kept.
  - Trainer memory: images/depths moved to pinned RAM (VRAM 7.4 GB → ~4.5 GB), splat cap, SH degree 2.
  - Learned pose corrections were not exported, so evaluation rendered at slightly wrong poses → now saved to `frames_refined.json`.
  - Next: block-wise training to raise the effective splat budget.

### 4.5 Our trainer produced degenerate, half-transparent splats (worse than plain splatfacto)
- **Symptom:** Even after 4.4, `gs_fixed2` looked worse ("cotton", hazy, messy) than the very first Nerfstudio splatfacto runs.
- **Investigation (no training; details in `docs/Training_Analysis.md`):**
  - Re-read PocketGS, VIGS-SLAM and the original 3DGS paper for their initialisation, losses and schedules.
  - Compared splat-shape statistics of every model we have trained:

    | | Splatfacto (earlier) | Ours (all versions) |
    |---|---|---|
    | Thickness ÷ width, median | 0.13–0.25 | 0.000 |
    | Splats thinner than 1% of width | 2–12% | 77–100% |
    | Opacity < 0.1 | 11–19% | 48–51% |
    | Opacity > 0.9 | 33–55% | 12–17% |
    | Typical width | ~7 mm | 13–15 mm |

  - Checked initialisation accuracy against bundle-adjustment points (≥ 3 views, 0.6 px): 19–26% lie more than 5 cm from the TSDF mesh used for initialisation.
- **Root causes:**
  1. **Flattening regulariser × Adam.** On a face-on disc the photometric gradient on the thin axis is ~0, so the regulariser is the only gradient there. Adam rescales it to full step size, driving every splat to zero thickness. PocketGS: normals "only for initialization, never as training constraints"; VIGS-SLAM uses the opposite (anti-elongation) term.
  2. **Anti-aliased rasterisation × zero-thickness splats.** gsplat's opacity compensation scales opacity by how much screen area the splat covers; a zero-thickness splat covers almost none, so its opacity collapses and the optimiser piles on semi-transparent sheets.
  3. **Initialisation from a single-image-depth surface** (TSDF mesh) instead of triangulated / multi-view-measured points; the ~110k BA points were never used.
  4. **Depth loss including single-image fill**, which none of the image-only methods use; metric scale already comes from the BA poses.
  5. **Joint pose refinement after BA**: poses drifted up to 73 mm to absorb other errors.
  6. Initial opacity 0.5 instead of 0.1.
- **Fix (implemented next, see below):**
  - Initialisation from BA triangulated points + MVS-measured points only, voxel-balanced, PocketGS-style discs (normals from 16-NN, width from 3-NN, thickness 0.2 × width), opacity 0.1.
  - No flattening / needle terms; depth loss off by default; classic rasterisation; poses fixed after BA.
  - Standard 3DGS schedule (densify until 50% of steps, opacity reset every 3000, 30 steps per frame).
  - Sanity baseline: Nerfstudio splatfacto trained on the same poses and initial points.
- **Acceptance:** `diagnose.py` train-view PSNR > 27 dB, thickness/width median > 0.05, < 25% of splats with opacity < 0.1.
- **Result (2026-10-10):**

| `diagnose.py`, roomAttemptSadness2 | Old baseline | `gs_fixed2` | Our trainer, new recipe (`gs_v4`) | **Splatfacto on our inputs** |
|---|---|---|---|---|
| Training views, colour-fit PSNR | 21.36 dB | 22.16 dB | 26.06 dB | **28.08 dB** |
| Held-out views, colour-fit PSNR | 21.48 dB | 21.65 dB | 24.70 dB | **27.81 dB** |
| Render/photo sharpness ratio | 0.04 | 0.07 | 0.36 | **0.49** |
| Splat thickness ÷ width | 0.000 | 0.000 | 0.08 | **0.11** |
| Opacity < 0.1 / > 0.9 | 48% / 12% | 48% / 17% | 59% / 15% | **21% / 55%** |

  - New measured-only initialisation (`make_init.py`): 662k points (BA points in ≥ 3 views + MVS-measured pixels, 1 cm voxels, room-box filter); realistic extent 5.2 × 3.2 × 4.4 m.
  - Our trainer with the plain recipe improved a lot (100-frame benchmark 26.81 → 28.03 dB).
  - Nerfstudio splatfacto trained on exactly the same BA poses and initial points (`export_nerfstudio.py`) is better still, and meets every acceptance criterion.
  - **Decision:** our pipeline does the phone-specific preprocessing (sync, tracking-loss filtering, metric BA, MVS, measured initialisation); splatfacto does the training. `run_arcore3dgs.bat` now does this by default. `train.py` remains for experiments.
- **Lesson:** every "physically motivated" extra term (flatness, depth, pose refinement) needs an ablation against the plain recipe. Here, all of them together made the result worse than doing nothing.

### 4.6 The best model still "looked like a mess" in the viewer
- **Symptom:** The splatfacto model (held-out PSNR 27.8 dB) looked smeared and full of streaks in the viewer, especially at the edges of the screen and near the ceiling.
- **Investigation:** Rendered off-path viewpoints three ways: the viewer's settings, a phone-like field of view with a near clip, and a floater-pruned model.
- **Findings:**
  - **Field of view (main cause).** The viewer used a 75° vertical FOV (~113° horizontal in a 2:1 window), while the phone frames cover ~63° × 38°. The edges of the screen showed directions and distances never filmed, where any 3DGS smears; free movement also put the virtual camera inside near floaters. At 45° with a 15 cm near clip the same model is clean.
  - **Floater pruning (`clean_splats.py`).** Measured-depth evidence removes 1.4% of splats for −0.3 dB and no visible change. Adding filled (ARCore/Metric3D) depth as evidence removed 9.8% but deleted real surfaces (held-out 27.8 → 22.4 dB). Pruning is not used by default; filled-depth evidence is off.
  - **Coverage (remaining limit).** Upward views of the ceiling / wardrobe top stay poor in every variant: plain, barely filmed areas.
- **Fix:** Viewer defaults to a 45° FOV and 15 cm near clip, with sliders to adjust both.
- **Lesson:** Judge a splat model at camera settings close to the capture before blaming the reconstruction.

### 4.7 Sharp near the camera path, incoherent away from it: copying PocketGS's workflow
- **Symptom:** The splatfacto model scored best on held-out frames (27.8 dB) but still looked like a mess when navigating; an earlier, blurrier model (`gs`) looked more coherent. PocketGS gets clean results from phone video in minutes.
- **Investigation:** Rendered all six room-2 models at the same off-path viewpoints (45° FOV, 15 cm near clip).
- **Finding: a trade-off.**
  - Photometric-only training (splatfacto, `gs_v4`) is sharpest near recorded viewpoints, but only textured spots were initialised, so walls and empty space are free for the optimiser to fill with floaters.
  - The early depth-supervised model was blurry (degenerate splats, wrong prior) but its geometry was held in place, so it stayed coherent off-path.
  - PocketGS gets both: a **dense, multi-view-consistent, spatially balanced prior** (walls included) plus a **short** optimisation that stays close to it.
- **Fix (`pocket_prior.py` + `train.py --frames_file --init_ply`):**
  1. **Keyframe gate** as in PocketGS: keep a frame only if the camera moved ≥ 8 cm or turned ≥ 6° (342 of 759 frames).
  2. **Dense prior:** each frame's full depth (stereo + ARCore-anchored fill), keeping pixels that ≥ 2 of 6 neighbouring views reproduce (< 2 px, < 2% depth). Median 70% of pixels kept, vs ~5% from stereo alone; voxel-fused at 2 cm (890k points, voxels seen from ≥ 2 frames).
  3. Surface-aligned discs (16-NN normals, 3-NN width, thickness 0.2), opacity 0.1, photometric loss only.
  4. Short training: 8k steps, last 30% at full resolution.
- **Result:**
  - Off-path views are as coherent as the early depth-supervised model and much sharper; no large floaters or wall streaks.
  - Training takes 12.7 min (3k half-res steps: 2.3 min), vs 32 min for our previous trainer and ~45 min for splatfacto.
  - Still softer than splatfacto at recorded viewpoints; ceiling / wardrobe-top areas remain weak (coverage).
  - Now the default in `run_arcore3dgs.bat` (output `work/gs_pocket`).
- **Lesson:** Held-out PSNR near the camera path does not measure what a user sees when navigating. Judge off-path coherence too, and give the optimiser a correct dense prior rather than leaving free space unconstrained.

### 4.8 Audit: is the recording pipeline bugged? Is PocketGS implemented fully?
**Recording checks on roomAttemptSadness2** (all passed):

| Check | Result |
|---|---|
| Video ↔ pose sync (optical flow vs pose angular velocity) | Best offset +0.05 s (~1.5 frames), r = 0.72 |
| Bundle adjustment residual | 0.62 px median over 626k observations |
| Lens distortion (radial residual vs distance from centre) | ±0.25 px, no monotonic trend; negligible |
| Rolling shutter (residual vs row × angular velocity) | Fitted readout 0.4 ms; explains 0% of residual; negligible |
| Metric scale | BA trajectory length 1.000–1.003 × ARCore |

Conclusion: the capture app and the preprocessing produce correct, synchronised, metric data. The remaining limits are the *content* of the recording (plain walls/ceiling, 4 tracking losses, coverage along a single walking path), not a bug.

**PocketGS fidelity:**

| PocketGS component | Ours |
|---|---|
| Information-gated keyframes (displacement + sharpness) | Yes (8 cm / 6° gate + sharpest-in-window) |
| GPU global BA from VIO poses | Yes (Schur-complement LM, ARCore priors) |
| Single-reference cost-volume MVS, **Census + SGM**, depth range from BA points, confidence ≥ 0.4 | **Different:** multi-source NCC plane sweep around the Metric3D depth + strict consistency, then ARCore/Metric3D fill verified across views |
| Surface-aligned init (16-NN normal, 3-NN width, thin), opacity 0.1 | Yes |
| Photometric loss, normals never a training constraint | Yes |
| **500-iteration budget, 33–77k Gaussians** | **Different:** 8k steps, ~1–3M Gaussians, densification |
| Mobile-GPU kernels | Not applicable (desktop) |

PocketGS's own reported quality is 22–23.5 dB PSNR on near-path test views (LLFF / Mip-NeRF 360 / MobileScan). Our models already score 24.7–27.8 dB on near-path views, so copying it more literally would not fix free-navigation quality. No 3DGS method reconstructs reliably far from where the camera went.

### 4.9 Capture guidance: show what is unmapped while recording
- **Problem:** Off-path quality is limited by coverage (surfaces filmed from one direction only, plain ceiling barely filmed), and the user cannot see coverage while recording.
- **Fix (app):**
  - `CoverageMap` accumulates ARCore raw depth (5 Hz) into 10 cm voxels and stores, per voxel, the set of directions it was seen from.
  - `CoverageOverlayView` draws the visible voxels over the camera image (red 1 direction, yellow 2–3, green 4+, none = unmapped), with a coarse screen-space z-buffer so hidden voxels are not drawn.
  - The end-of-recording dialog reports the share of well-covered cells.
- **Fix (desktop):** `check_capture.py` validates a recording in ~1–2 min before the 1.5 h pipeline is run.

### 4.10 Novelty: featureless-tracking fallback (IMU bridging + re-alignment on re-tracking)
- **Problem:** On plain surfaces ARCore loses tracking (INSUFFICIENT_FEATURES). Those frames had no poses and were thrown away. Worse, after re-tracking ARCore sometimes continued in a **shifted/rotated world frame**: on roomAttemptSadness2, 3 of 4 gaps ended with pure heading jumps of 109°, 31° and 35° about gravity. Even the "clean" gap left a position offset: post-gap frames disagreed with earlier frames by 50–650 px epipolar error, while pre-gap pairs agree to 3.8 px (raw) / 0.7 px (BA).
- **Approach:**
  1. **IMU from the recording itself** (`imu.py`): ARCore's MP4 stores gyroscope + accelerometer at 201 Hz (protobuf data tracks), on the same clock as the frames. No app change needed.
  2. **Self-calibration** (`fallback.py`): IMU→camera rotation by Kabsch on gyro vs ARCore angular velocity (correlation 0.99, residual 0.010 rad/s, time offset 0 ms), plus gyro/accelerometer biases.
  3. **Gap bridging** (lower-confidence fallback poses):
     - rotation by gyro integration;
     - position by accelerometer integration with the minimal cubic correction matching position and velocity at both anchors.
  4. **Jump detection:** a yaw mismatch between the gyro-propagated orientation and ARCore at re-tracking reveals a new-map frame; the post-gap segment is re-aligned (heading + translation) and corrections chain.
  5. **Visual re-alignment** (`relocalize_pnp.py`): post-gap keyframes are matched to the BA map (≥ 3 agreeing PnP solutions required), the segment gets one rigid correction, and BA re-runs from the corrected poses. Segments with no familiar view are flagged *unverified* and kept out of the prior and training.
- **Validation:**

  | Simulated gap (cut from tracked data) | IMU fallback: position median / max | rotation | Interpolation: position median / max | rotation |
  |---|---|---|---|---|
  | 2 s | 0.6 / 2.8 cm | 0.16° | 5.0 / 12.3 cm | 3.14° |
  | 5 s | 1.5 / 3.4 cm | 0.34° | 20.6 / 52.4 cm | 11.8° |
  | 9 s | 3.8 / 8.5 cm | 0.38° | 30.6 / 75.9 cm | 17.3° |

  - Real gaps: all 3 heading jumps detected (axis ‖y‖ = 1.00). The segment after the first gap was relocalised by 14/14 PnP keyframes; its epipolar error against earlier frames fell 49.7 → 8.2 px (PnP) → 15.1 px after BA. BA's starting reprojection error fell 3.37 → 0.85 px, with 23% more verified observations (786k vs 640k).
  - The 3 short ceiling-facing segments had no familiar view; they are flagged unverified (the frames that previously caused ghosts).
- **Limits:**
  - IMU-only *position* is reliable only when both ends are anchored (forward-only 9 s: 33 cm median).
  - Re-alignment needs the user to come back to a mapped area; the app now says so during tracking loss and the coverage overlay shows where "mapped" is.
- **Pipeline:** `fallback.py` → `prepare.py` (gap frames included, flagged) → `ba.py` → `relocalize_pnp.py` → `ba.py` again (starts from `c2w_init`).

### 4.11 ROOT CAUSE: ARCore poses and calibration are not good enough for 3DGS (2026-10-11)
- **Symptom:** On newRoomAttemptSadness every model:
  - moved objects with the viewing angle;
  - had splats hanging in the air;
  - was far blurrier than the video.

  Tuning did not help: dense priors, sparse depth loss, COLMAP depth, floater pruning and near-camera removal were each tried in turn.
- **Diagnosis** (`fit_diag.py`: full-resolution renders of *training* views against their photos, with optical flow between them):
  - **Training views only reached 22–24 dB.** A model cannot reproduce its own inputs when they are geometrically inconsistent.
  - **The scene itself was misplaced.** Median misalignment was 7–30 px, and some training frames rendered a completely different part of the room.
- **Causes:**
  1. **Silent ARCore map correction at about 60 s.** There was no tracking loss. Every pose before 60 s is rigidly off by **about 1.0 m and 28°** from the image-based (COLMAP) solution; after 60 s the two agree within 2–4 cm. Our BA starts from ARCore and keeps ARCore priors, so it kept the wrong segment. The first part of the room existed twice in every model, giving ghosts, moving objects and floaters. This was invisible to our geometry check, because its reference points were triangulated with the same wrong poses.
  2. **Lens model.** ARCore's intrinsics have no distortion. Self-calibration finds k1 = 0.093, k2 = −0.22 (several px at mid-image) and f +0.3–1%. Every view was slightly misaligned, so 3DGS averaged them into blur.
  3. **49 of 592 keyframes (8%) never registered in our BA.** They were still trained on with raw ARCore poses.
  4. **Training mostly at half resolution.** Renders cannot be as sharp as the 1080p video.
- **Fix: `sfm_colmap.py`.** This is the standard phone-video recipe; ARCore is used only for metric scale and gravity.
  - Pipeline: COLMAP 4.2 SIFT → exhaustive GPU matching (23 min) → `global_mapper` (6 min).
  - Lens and poses are estimated from the images: one OPENCV camera.
  - Images are undistorted.
  - A RANSAC Sim3 fit to the ARCore/BA camera centres gives metric scale (inlier median 2.5 cm).
  - 18 SfM mis-registrations (jumps > 30 cm between consecutive keyframes, impossible when walking slowly) are dropped.
  - Training: splatfacto at **full resolution**.
- **Result** (same room and recording):

  | | Training views (full res) | Held-out colour-fit PSNR | SSIM | Sharpness vs photo | Misalignment |
  |---|---|---|---|---|---|
  | best previous (`gs_colmap_nc`) | 21.9 dB | 22.7 dB | 0.782 | 0.11 | 12–30 px |
  | **`work_sfm/gs_sfm`** | **28.2 dB** | **27.2 dB** | **0.864** | 0.41 | 2–3 px |

  Views from the room centre (never visited) are now coherent: the door, fridge, sofa, pictures and cupboard are recognisable.
- **Follow-up: cloudy, mottled plain walls.** Phone auto-exposure and white balance change from frame to frame. Plain splatfacto bakes those changes into the splats, which shows up as cloudy walls and swirls on the floor.
  - Splatfacto's **bilateral grid** (`--pipeline.model.use-bilateral-grid True`, per-image learned colour correction, BilaRF) absorbs them; the exported splat keeps a clean, consistent colour.
  - **Scale regularisation** removes needle splats.
  - **Do not use the SO3xR3 camera optimiser:** unanchored, it shifts the scene (v2b renders 3–16 px off the photos).
  - **`splatfacto-big` thresholds run out of the 8 GB VRAM at full resolution.**

  | newRoom, held-out (nerfstudio 10%) | Colour-fit PSNR | SSIM | Geometry median / > 25% off | Look |
  |---|---|---|---|---|
  | v1 (plain splatfacto) | 27.22 | 0.864 | 1.02% / 5.2% | cloudy walls, floor swirls |
  | v2b (+ bilateral grid, scale reg., SO3xR3) | 24.46 | 0.824 | 0.74% / 2.6% | clean, but shifted |
  | **v3 (+ bilateral grid, scale reg., no camera opt.)** | 25.57 | 0.857 | **0.59%** / 3.1% | **clean and aligned** |

  PSNR against the photos favours v1 because the photos contain the exposure flicker that v1 memorised. At full resolution, v3's renders match the source frames almost pixel for pixel, and are sometimes sharper (multi-view averaging removes motion blur and noise). Before/after sheets are in `newRoomAttemptSadness/before_after/`.
- **Lesson:** ARCore's VIO world frame is not globally consistent. It re-anchors silently, and its factory intrinsics ignore distortion. Both are harmless for AR overlays and fatal for 3DGS. Poses for 3DGS must come from image-based SfM with lens self-calibration; ARCore should provide scale, gravity and a fallback only.

## 5. 3DGS training quality

### 5.1 Scene rotated in the Nerfstudio viewer
- **Cause:** Training ran with `--orientation-method none`, so the viewer's assumed up direction didn't match ARCore's +Y-up world.
- **Fix:** Rotation-only orientation in Nerfstudio. Later the custom viewer simply set +Y up.

### 5.2 Slow training: about 25 min for 30k splatfacto steps
- **Cause:** Initialisation from a 1.3M-point prior, too many iterations, Windows without `torch.compile` (no Triton), and densification growth.
- **Fix:**
  - Custom gsplat trainer (`train.py`).
  - Initialisation from 300k points sampled on the fused surface.
  - 7k steps, with densification stopping at 70% of training.
- **Result:** About 5–8 min of actual training. Earlier "18–20 min" timings included gsplat recompiles or VRAM contention (see 6.x).

### 5.3 Fuzzy surfaces at grazing angles; exposure drift
- **Fixes in `train.py`:**
  - Gaussians start as flat discs aligned to the fused-surface normals.
  - A flatness regulariser.
  - Per-image exposure and white-balance gains to absorb ARCore auto-exposure.
  - Optional per-camera pose refinement.
  - Depth loss against the fused depth, decaying from 0.5 to 0.05 over training.
- **Evaluation pitfall:** Plain PSNR got worse (19.90 → 18.95), because test images get no learned exposure correction. Fair evaluation fits only a per-image colour affine on each test image, with no geometry change (`compare.py`).
- **Result (fair metric):** PSNR 20.39 → 21.74 dB and SSIM 0.737 → 0.769, close to PocketGS's reported 22–23.5 dB on easier benchmark scenes. Visibly sharper ironwork, wall art and fabric patterns.

### 5.4 Remaining limitations, which come from the capture rather than processing
- The ceiling was never filmed, so objects near it are surrounded by black void.
- Close-ups beyond what the 1–2 m capture distance supports stay blurry.
- Grazing views were never captured.
- These are addressed by the new capture protocol and the live IQA / coverage-guidance item in `TODO.md`.

---

## 6. Environment and tooling

| Problem | Cause | Fix |
|---|---|---|
| Nerfstudio dataparser flags rejected | tyro needs dataparser options after the `nerfstudio-data` subcommand | Reordered the arguments |
| `UnicodeEncodeError` when logging to a file | Rich console under Windows cp1252 | `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8` |
| `FileNotFoundError: images_2/...` | Nerfstudio doesn't generate downscaled folders itself | Generated `images_2/` manually |
| `where cl` failed; gsplat couldn't build | MSVC not on PATH | Launch through `vcvars64.bat` (VS 18) |
| CUDA 12.8 folder empty; CUDA 13.2 rejected the MSVC preprocessor | Leftover install; CCCL requires a conforming preprocessor | Use 13.2 with `CL=/Zc:preprocessor`, `TORCH_CUDA_ARCH_LIST=8.6` |
| gsplat recompiled for ~15 min on almost every launch | The torch JIT rebuilds whenever the shell environment differs; two processes compiling at once deleted each other's lock | Prebuilt module plus a loader shim (`gsplat/csrc.py` with `_prebuilt/gsplat_cuda.pyd`); loads in about 6 s from any shell |
| Empty TSDF mesh | Open3D 0.20 `ScalableTSDFVolume` is broken on this Windows build (fails even on a synthetic plane) | Run fusion with Open3D 0.19 from `nerfstudio-env`; removed the pandas dependency |
| Nearest-neighbour init hung training | Brute-force `cdist` on 300k points overflowed VRAM into system RAM | scipy `cKDTree` on the CPU (about 1 s) |
| Output appeared only at the end | Python block-buffers stdout when redirected | `print(..., flush=True)` / `python -u` |
| Training 10× slower at times | The viewer and training together exceeded 8 GB VRAM | Close the viewer before training |
| Two power outages killed long jobs | — | Checkpoint every 1000 steps; stages cache their outputs (`frames.json`, depth folders, `ba_tracks.npz`) |

---

## 7. Viewer (`view.py` / `view_splat.bat`)

| Symptom | Cause | Fix |
|---|---|---|
| `localhost:8080` showed a "Steam … Inspectable WebContents" page | Steam's built-in browser debugger owns port 8080 | Viewer moved to port 7010; it now prints the port it actually got |
| Blank page, 100% GPU, 7 GB RAM | The background-image depth map hid the frame; every tiny camera event triggered a full render | Dropped the depth map; renders now run from a single loop |
| Still blank | The first gsplat call (CUDA extension load) stalls when made from a worker thread on Windows | Warm-up render on the main thread at startup |
| Browser connected to a stale instance | viser silently moves to the next free port | Print `server.get_port()` |
| Mouse drag only placed measurement points | viser disables orbit controls while a click listener exists | Measuring became a toggle button; the listener is removed after two points |
| Lag that grew until it felt like 0 fps | The browser receives frames in a web worker, so it never tells the server to slow down; frames queued up faster than they could be shown | At most 15 fps at half resolution while moving, one full-resolution frame after stopping, no rendering when idle, and splats with opacity under 0.02 dropped at load |

---

## 8. Android capture app (`googleARCore/samples/hello_ar_java`)

| Problem | Fix (`CaptureLogger.java`, wired into `HelloArActivity`) |
|---|---|
| Pose and point files were opened and closed on every frame on the GL thread, which blocked rendering and could drop frames | Buffered writers on a background thread; safe shutdown when recording stops (late frames are dropped, not crashed on) |
| No record of tracking quality | `tracking.csv`: state and failure reason for every frame |
| Point IDs and confidence discarded | `points.csv` now includes `id` and `confidence` |
| ARCore depth enabled but never saved | Raw depth and confidence saved at 5 Hz (`depth/*.depth`, `*.conf`) |
| Camera config and intrinsics resolution unknown at processing time | `meta.json` with device, CPU image and texture size, fps range and intrinsics dimensions |

The app compiles (Gradle, Android Studio's bundled JDK). It has **not** yet been tested on a device.

---

## 9. Lessons learned

1. **Measure before fixing.** Several plausible stories were wrong: MediaRecorder lag, a constant pose offset, floaters being real objects. A quantitative check settled each one.
2. **Monocular depth is a prior, not a measurement.** It needs anchoring to metric data (ARCore points, BA points, MVS). Frames without an anchor caused most of the remaining artifacts.
3. **Phone VIO poses are a starting point.** Bundle adjustment with VIO priors cut reprojection error by about 4× while keeping metric scale.
4. **Evaluate fairly.** Exposure differences can hide real improvement in plain PSNR.
5. **Capture coverage limits everything.** Anything the camera never saw (ceiling, grazing angles, close-ups) can't be reconstructed. This motivates the live capture guidance planned for the app.
