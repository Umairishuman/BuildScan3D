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
