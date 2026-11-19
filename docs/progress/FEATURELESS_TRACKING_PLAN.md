# Featureless tracking: plan

2026-11-18 · drafted for Muhammad Tayyab (Workflow B), to be reviewed by the team · status: **option 1 chosen, then
continue (D-080, Tayyab, 2026-11-18)**; progress in §8

**The problem.** On plain walls, ceilings and poorly lit rooms, the cameras cannot be placed, so most of the recording is
lost. The worst case so far is `scan_009_057ed3beb4fc`:

- ARCore lost tracking for 63.7% of the walk;
- the default recipe trained on 87 frames (R-045);
- the pose-free + ALIKED run reached 535 frames, but with misplaced cameras and no reliable scale (R-046).

**The question** (Tayyab, 2026-11-18): can the pipeline track a featureless room another way?

- **Lines and junctions:** wall/wall, wall/floor, wall/ceiling edges and the corners where three surfaces meet.
- **Faint contrast:** whatever subtle shading the image still has.
- **Phone sensors:** to aid the above.

**Short answer:** yes, and the data supports it. The cheapest wins come from the gyroscope (rotation) and from using
straight lines and the room's layout once part of it is mapped. Full line/plane/IMU SLAM is the end state, but too big
for 2026-12-04.

---

## 1. What we measured (2026-11-18)

### 1.1 Texture in the keyframes

Tool: [`src/arcore3dgs/texture_probe.py`](../../src/arcore3dgs/texture_probe.py), half resolution (960 × 540). The
columns are:

- **SIFT keypoints:** what COLMAP's default features see.
- **Long lines:** LSD segments longer than 15% of the image size, i.e. room junctions, door and window frames.
- **Faint-gradient pixels:** Sobel magnitude 8–40, the signal a photometric (direct) method uses.

| Keyframes | n | SIFT keypoints, median (10th pct.) | Long lines, median | Faint-gradient pixels |
|---|---|---|---|---|
| newRoomAttemptSadness (`work_v9e2e`, every 6th) | 195 | 797 (285) | 5 | 30.5% |
| roomAttemptSadness2 (`work_v9pgsr8`, every 6th) | 174 | 526 (118) | 7 | 24.6% |
| lecture hall `scan_3028a4de8fa0` (`work_v10`, every 6th) | 141 | 445 (170) | 12 | 29.5% |
| scan_009, ARCore tracking | 230 | 66 (16) | 7 | 14.3% |
| scan_009, ARCore **lost** | 571 | **39 (2)** | **6** | 11.7% |
| scan_009, not in the R-046 model | 359 | 17 (0) | 5 | 10.2% |

**What it shows:**

- **Corners are scarce.** Frames where ARCore lost tracking have about 13× fewer SIFT corners than the bedroom
  (39 vs 526). The frames SfM could not place have almost none (median 17, 10th percentile 0).
- **Straight lines survive.** The same frames still have as many long lines as the well-tracked rooms (median 6 vs
  5–12). This is the signal Tayyab's junction idea would use, and it is present.
- **Faint contrast is reduced but not gone.** 10–14% of pixels against 25–30% in the good rooms.
- **Even the tracked part of scan_009 is poor** (SIFT median 66). This is the whole room and the way it was filmed,
  not a few bad seconds.
- **Confound: motion blur.** scan_009's median predicted blur was 21.7 px (`check_capture.py`), 10.5 px after
  pose-free selection. Blur removes corners and faint gradients too, so part of the "featureless" signal here is blur,
  not the walls. A sharp recording of the same room is needed to separate the two (§4, step 0).

### 1.2 Phone sensors (from earlier work, P&S §4.10)

The ARCore MP4 already stores the gyroscope and accelerometer at 201 Hz on the same clock as the frames (`imu.py`;
scan_009 has 37,844 gyro samples). On gaps cut out of tracked data, IMU bridging (`fallback.py`) gave:

| Gap length | Rotation error | Position error, median (max) | Plain interpolation, position median |
|---|---|---|---|
| 2 s | 0.16° | 0.6 cm (2.8 cm) | 5.0 cm |
| 5 s | 0.34° | 1.5 cm (3.4 cm) | 20.6 cm |
| 9 s | 0.38° | 3.8 cm (8.5 cm) | 30.6 cm |

The error is low only because both ends of each gap were anchored by tracked frames. Without the end anchor,
position drifts quickly: 33 cm median over 9 s.

**Conclusion:**

- **Rotation is essentially solved by the gyroscope**, for gaps of many seconds, with or without texture.
- **Position (translation) is the hard part.** The accelerometer drifts, so position needs a visual or geometric
  signal: lines, planes, faint contrast or depth.

### 1.3 What we do and do not control

- **Live tracking in the app is ARCore.** It is closed; we cannot add line features to it. In the app we can only
  guide the user, record more, and detect bad stretches.
- **Offline pose recovery is ours** (`select_sharp.py` → `sfm_colmap.py` → priors → training). Every approach below
  runs on the PC after upload, using the video, the 201 Hz IMU, ARCore depth and the ARCore poses where they exist.

---

## 2. Ideas, mapped to known methods

| Idea | What it gives | Known methods | Fit for us |
|---|---|---|---|
| **A. Gyro for rotation** | Rotation of every frame, including lost ones; an independent check of SfM | IMU pre-integration (Forster et al. 2017); known-rotation 2-point relative pose (Kneip et al. 2011) | **High.** Already calibrated in `fallback.py`. With rotation known, two matched points fix the direction of motion between two frames (five without it), so sparse matches on plain walls become usable |
| **B. Lines and junctions** (Tayyab's idea) | Rotation from vanishing directions (with gravity: a Manhattan frame); position from triangulated lines and corners | LSD / DeepLSD (2023) detection; GlueStick (ICCV 2023) point + line matching; LIMAP (CVPR 2023) line mapping and line bundle adjustment on a COLMAP model; PL-SLAM, PL-VINS; ManhattanSLAM | **High.** Long lines survive in lost frames (§1.1). A single line does not pin position along its own direction, but corners (wall/wall/ceiling) do, and a few lines in different directions do |
| **C. Room layout as the map** | Place a featureless frame by aligning its image lines to the projected wall / floor / ceiling edges of the layout | Model-based tracking; the layout comes from our own `layout.py` | **High, and a novelty.** `layout.py` already finds walls, floor, ceiling and corners in 3D. Once part of the room is placed, the rest can be placed against that layout, with the gyro giving rotation |
| **D. Faint contrast (direct)** | Motion from all image gradients, not only corners | DSO (Engel et al. 2017), DM-VIO (2022, with IMU); dense learned matchers RoMa (CVPR 2024), MASt3R (2024); DROID-SLAM (2021) | **Medium.** Lost frames have half the usable gradient (§1.1). Dense matchers are easy to try as COLMAP matches. Full direct odometry is a big build |
| **E. Learned whole-sequence pose** | Poses for a whole chunk in one network pass, robust to low texture | VGGT (CVPR 2025), MASt3R-SfM (2024) | **Medium.** Quick to try on scan_009 chunks; GPU memory on the 8 GB RTX 3070 limits chunk size (the RTX 4000 Ada has more); check the licences (research / non-commercial) |
| **F. Planes from depth** | Position from aligning walls seen in depth (point-to-plane ICP), no texture needed | Planar SLAM; we already have ARCore raw depth (5 Hz) and Metric3D | **Medium.** ARCore depth is sparse (160 × 90, ~25% valid on this phone), and on scan_009 only 17 maps were usable. Metric3D's scale is off by 7–48% (R-046), so only its *shape* (plane normals) is safe |
| **G. Full fusion** | One optimisation over IMU + points + lines + planes | Factor graphs (GTSAM), VINS-style back ends | **Low before 2026-12-04.** The right end state; weeks of work |
| **H. Capture guidance** | Fewer featureless stretches in the first place | — | **High, cheap.** The app already warns "Low texture – keep some detail in view" (`QualityMonitor`); scan_009's walk faced the upper walls and ceiling, with the floor barely in view |

Ideas A–C use what we already have (gyro, lines, our own layout), so they are the core of the plan. D–E are quick
experiments with existing code. F–G come later.

---

## 3. The proposed approach

**Step 1: anchor.** Run SfM as today (pose-free keyframes, ALIKED or SIFT) and take the frames it places with
confidence.

**Step 2: check with the gyro.** For every pair of consecutive placed frames, compare SfM's relative rotation with the
gyro's. A mismatch of more than a few degrees means a misplaced camera. This replaces the current filter, which only
catches jumps over 30 cm. Whether it catches R-046's bad placements is not measured yet (step 1 checks it).

**Step 3: fill the gaps.** For each unplaced frame:

1. Rotation from the gyro, chained from the nearest placed frame.
2. Gravity from the accelerometer.
3. Vanishing directions of its long lines, to correct slow gyro drift.

**Step 4: position from structure.** With rotation fixed, solve only position (3 unknowns per frame) from:

- **Lines:** match its long lines to lines already triangulated (LIMAP) or to the layout's edges (`layout.py`: walls,
  floor, ceiling, corners).
- **Points:** any point matches, using the 2-point known-rotation solver.
- **Motion bounds:** the IMU-bridged position from `fallback.py` as a prior (accurate to a few cm when both ends of the
  gap are anchored).

**Step 5: refine and train.**

1. Joint bundle adjustment of all frames with point, line and rotation-prior terms.
2. Frames that stay inconsistent are flagged and kept out of training, as `relocalize_pnp.py` does today.
3. Train as usual. Scale still comes from ARCore where it tracked; where it never did, see §5.

This uses Tayyab's junction idea where it is strongest (rotation from lines and gravity; position from corners and from
lines in several directions), and the gyro where vision is weakest.

---

## 4. Steps, effort and how each is checked

Each step is a run in TRAINING.md with a before/after number. Effort is a rough estimate, not measured.

| # | Step | Effort | Checked by | Needs |
|---|---|---|---|---|
| 0 | **Test set and baseline.** Fix the captures (scan_009; newRoom and the bedroom with gaps cut out of tracked stretches, where the true poses are known), the metrics (frames placed; rotation / position error against the uncut solution; held-out PSNR) and the current numbers. Ideally also a **new sharp recording of scan_009's room**, to separate blur from missing texture (§1.1) | 1 day | numbers in TRAINING | — |
| 1 | **Gyro rotation check in `sfm_colmap.py`**: flag and drop frames whose SfM rotation disagrees with the gyro (reuse the IMU-to-camera calibration in `fallback.py`) | 1 day | R-046 again: misplaced cameras removed, top-down path continuous; no good frames lost on newRoom | 0 |
| 2 | **Quick experiments: dense matchers and VGGT/MASt3R** on scan_009 (RoMa matches into COLMAP for pairs with few ALIKED matches; VGGT on chunks) | 1–2 days | frames placed and rotation agreement with the gyro, against R-046 | 0, 1 |
| 3 | **Gyro + gravity rotation for unplaced frames**, plus a vanishing-point correction from long lines | 1–2 days | cut-gap captures: rotation error against the uncut solution | 1 |
| 4 | **Position from lines and the layout**: LIMAP line triangulation on the anchored model; match lines of unplaced frames to it and to the `layout.py` edges; solve position with rotation fixed | 3–4 days | cut-gap captures: position error (target: better than IMU-only bridging, §1.2); scan_009: frames placed | 3 |
| 5 | **Joint refinement** with line and rotation-prior terms (LIMAP's line BA, or our `ba.py`), inconsistent frames flagged | 2 days | held-out PSNR on scan_009 and on newRoom (must not get worse) | 4 |
| 6 | **App guidance for featureless stretches**: when texture is low, say "keep a corner or edge in view" (wall / floor / ceiling junctions are what step 4 uses); log the count of long lines per frame in `quality.csv` | 1 day, parallel | device test; fewer lost seconds on a new recording | — |
| 7 | **Later (not before 2026-12-04):** planes from depth (F), a full fusion back end (G), direct odometry (D) | weeks | — | 5 |

**Total for steps 0–6:** about 10–13 working days if all go well. That does not fit next to the Must items of
[COMPLETION_PLAN.md](COMPLETION_PLAN.md) (week 2, gate G2 on 2026-11-26, is the evaluation week). So the realistic
choice is between the options in §6.

---

## 5. Scale where ARCore never tracked

Scale stays an open problem, and this plan does not fully solve it:

- Metric3D is off by 7–48% against ARCore on the rooms where both are known (R-046).
- ARCore depth was sparse and inconsistent on scan_009. The pairing bug fixed in app v0.3.8 may be part of why; the
  next recording's `depth/timestamps.csv` will show.

Options, in order of cost:

1. Any stretch where ARCore tracks gives scale for the whole connected model (today's Sim3); capture guidance (step 6)
   makes such stretches likely.
2. Accelerometer double integration over short, well-excited motions (scale observability as in visual-inertial
   odometry); needs testing on cut-gap data.
3. A known length: the room height from `layout.py` against a typical 2.6–3.0 m, or one tape measurement entered by the
   user. Approximate, but honest if labelled.

---

## 6. Options for the team

**Option 1 (recommended): steps 0, 1, 6 now, then 2–3 if week 2 allows.**

- Costs about 3 days, and fixes R-046's misplaced cameras.
- Gives the app guidance.
- Leaves a measured baseline and a clear write-up of the line/layout method (steps 4–5) as future work and novelty in
  the final report.
- Fits COMPLETION_PLAN week 1–2 without moving a Must.

**Option 2: the full steps 0–5 before 2026-12-04.**

- The strongest novelty: featureless frames placed with lines, layout and gyro.
- About 2 weeks of Tayyab's time, overlapping the evaluation week.
- Risks Musts (E1–E9, the report).

**Option 3: capture only (step 6 and re-recording rooms carefully).**

- Cheapest.
- Does not address the question, and scan_009-type rooms stay unsolved.

**Related open decisions:**

- **D-022 (ALIKED rejected on 2026-10-26).** R-046 gave new evidence on another capture; step 2 tests it properly.
- **OD-6 (IMU fallback in the v9 pipeline).** This plan is the answer to OD-6: the gyro enters `sfm_colmap.py`
  (steps 1 and 3).

**Decision: OD-14, Tayyab with the team.** Record the choice in DECISIONS.md, with the name under "By".

---

## 7. References

- Kneip, Chli, Siegwart, "Robust real-time visual odometry with a single camera and an IMU", BMVC 2011: known-rotation
  relative pose with 2 points.
- Forster et al., "On-manifold preintegration for real-time visual-inertial odometry", IEEE T-RO 2017.
- Pumarola et al., "PL-SLAM: real-time monocular visual SLAM with points and lines", ICRA 2017; Fu et al., "PL-VINS",
  2020.
- Liu et al., "3D line mapping revisited" (LIMAP), CVPR 2023; Pautrat et al., "GlueStick", ICCV 2023; Pautrat et al.,
  "DeepLSD", CVPR 2023.
- Yunus et al., "ManhattanSLAM", ICRA 2021.
- Engel et al., "Direct sparse odometry", IEEE TPAMI 2017; von Stumberg & Cremers, "DM-VIO", RA-L 2022.
- Teed & Deng, "DROID-SLAM", NeurIPS 2021; Edstedt et al., "RoMa", CVPR 2024; Leroy et al., "MASt3R", ECCV 2024;
  Duisterhof et al., "MASt3R-SfM", 2024; Wang et al., "VGGT", CVPR 2025.
- Our own: P&S §4.10 (IMU fallback), §4.11 (why COLMAP places the cameras), TRAINING R-045 / R-046.

---

## 8. Progress

| Step | State (2026-11-18) | Evidence |
|---|---|---|
| 0 · test set | Cut-gap test on newRoom built (`gap_test.py`): windows of keyframes removed every 20 s and predicted from the frames outside. Sharp re-recording of scan_009's room: not done | below |
| 1 · gyro rotation check | Built: `gyro_check.py`, `sfm_colmap.py --gyro_thr` (default 0 = off). IMU→camera rotation and time offset estimated from the SfM model, no ARCore tracking needed | newRoom: pair error median 0.15°, frame score p99 1.03°, 3 of 1,166 frames over 2°. scan_009: 330 of 761 over 2°, of them 185 of the 226 the 30 cm jump filter dropped and 144 it kept; after both filters 370 frames, steps > 5× median speed 21 (R-046: 51). R-047 (trained): +1.0 dB on common training views (not held out), sharper in some views, worse in one; long path jumps and a shrunken block remain: the rest are **position / scale** errors, which need step 4 or the incremental mapper (OD-11). Inconclusive, `--gyro_thr` off by default |
| 3 · gyro rotation for unplaced frames | Rotation part built (`gyro_check.fill_rotations`); position (step 4) not started | cut gaps on newRoom, rotation error median / p90 / max: 2 s 0.15 / 0.48 / 1.15°; 9 s 0.28 / 0.91 / 1.76°; 15 s 0.30 / 0.83 / 2.10°; 30 s 0.47 / 0.91 / 5.83° (one end only, 15 s: 0.59 / 1.19 / 1.89°). Calibration estimated on the same model (a per-phone constant), one capture only |
| 6 · app prompt | Compiled locally (JDK 21: Android Studio's JBR is now Java 25, which this Gradle cannot run). Messages changed: "Low texture - keep a room corner or edge in view", "Tracking lost (plain surface) - aim at a corner or edge". Long-line count in `quality.csv`: not done | not tested on a phone |
| 5 · refinement | `prior_ba.py`: BA with gyro / accelerometer priors (R-052, R-071, R-072) | §8.2 |
| 2, 4 | Not started (VGGT blocked, needs Tayyab's OK) | — |

### 8.1 Night of 2026-11-18 (Tayyab: "work throughout the night, I need scan_009 to be working properly soon")

- **Step 4, points part:** `known_rot_pnp.py`. With the gyro rotation fixed, two matched 3D points place a camera
  (linear in the centre). Cut gaps on newRoom, error in cm (ok = < 10 cm):

  | Gap | Matches per frame | Gyro rotation + points | PnP RANSAC (no gyro) |
  |---|---|---|---|
  | 2 s | 3 | median 0.8, ok 95% | impossible (needs 4) |
  | 2 s | 5 | 0.8, ok 96% | 1.2, ok 91% |
  | 9 s | 5 | 1.8, ok 88% | 2.7, ok 76%, p90 396 cm |
  | 9 s | all | 1.2, ok 90% | 0.6, ok 91% |

  In `sfm_colmap.py --place_unplaced N` (with `--gyro_thr`). On scan_009's GLOMAP model (R-049): 157 of 442 unplaced
  frames placed, 90 survive the jump filter, but the path has more jumps (40 vs 21): the map points are partly wrong.
- **Scale from the accelerometer** (`imu_scale.py`, §5 option 2). First version (second derivative of a spline through
  the SfM positions) was too noisy: forward and inverse fits bracket the truth but disagree by up to 5× (bedroom 0.215
  vs 1.07). Second version, pre-integrated accelerometer over keyframe triplets 1 s apart (VINS-style linear
  initialisation, velocity eliminated), against the ARCore Sim3 scale:

  | Capture | IMU scale (1 s) | ARCore Sim3 | Difference | Fitted \|g\| |
  |---|---|---|---|---|
  | newRoom (v9e2e) | 0.649 | 0.668 (inliers: most) | −2.8% | 9.85 |
  | roomAttemptSadness2 (v9pgsr8) | 0.227 | 0.222 (777 / 1,014) | +2.5% | 9.86 |
  | lecture hall (v10inc) | 0.749 | 0.922 (100 / 581, weak) | −18.7% | 9.98 |
  | scan_009 GLOMAP (R-046) | ~0 | 0.48 – 0.85 (26 – 29 inliers) | — | 6 – 7.8 |

  Not tuned per room (same settings everywhere). The hall disagreement is unexplained: either ARCore (weak fit) or the
  IMU is off there; no tape measurement of the hall.
- **Finding: scan_009's GLOMAP model is locally wrong.** Fitting scale per 15 s window: newRoom gives 0.48 – 0.93
  (mostly 0.6 – 0.7); scan_009 gives −4.5 to +24 with most windows lacking continuous frames. Filtering cameras cannot
  fix that model; a locally correct base model is needed (incremental mapper, R-048), whose pieces can then get scale
  and gravity from the IMU and be joined with the gyro.
- **Why SfM fails on scan_009 (R-050):** not wrong matches between look-alike places (the gyro rejects only 0.6% of
  verified pairs; 0.2% on newRoom) and not the timestamps (sync PASS). ARCore itself barely tracked (its rotation vs
  the gyro: correlation 0.34, bedroom 0.99), so it is no reference. The IMU data is clean. Images (21.7 px median blur,
  plain and repeated surfaces) give roughly right rotations but locally wrong positions in both COLMAP mappers.
- **Known-rotation SfM with the accelerometer** (`rot_sfm.py`, R-051): rotations from the gyro (bias removed:
  0.055°/s newRoom, 0.134°/s scan_009; without it the gravity leak broke everything), pair directions with the rotation
  fixed, positions + velocities + gravity (per 15 s) + accelerometer bias in one sparse linear system. Lessons: the
  homogeneous direction form `(C_a − C_b) × u = 0` collapses the path (steps 0.02× true); fixed-length direction
  equations do not. On newRoom: Sim3 scale 0.936, median 1-s step 0.98× true but noisy (spread 7×) and 63 – 71 cm
  median position error: far below normal SfM where normal SfM works. On scan_009: all 894 keyframes connected, the
  images triangulate 23,508 points at 1.76 px with these poses fixed (GLOMAP model: 9,349), but the metric scale looks
  2 – 3× too large (Metric3D ratio 3.0, cameras spread 7.5 × 7 m).
- **VGGT (step 2):** code and weights fetched outside the repo (`C:\Users\tyb\.cache\buildscan`); running them was
  blocked by the session's permission check (third-party code downloaded from the internet). Needs Tayyab's OK.

### 8.2 Night of 2026-11-19 (Tayyab: "work on featureless overnight")

- **Refining the sensor path with the images** (`prior_ba.py`, R-052): a free COLMAP BA of R-051's model pulled the
  rotations off the gyro again (106 of 706 frames > 2°). With the gyro / accelerometer solution as soft relative
  priors: reprojection 1.77 → 1.22 px, rotations stay within 0.1° of the gyro. Trained: +0.5 dB vs R-051, about equal
  to R-047 on training views, with 698 instead of 370 frames.
- **Loop closure** (R-071): each verified image pair's own rotation (5-point) against the gyro chain showed that pairs
  > 2 min apart disagree by a consistent 14° yaw: the gyro bias from `gyro_check` (fitted against the wrong SfM model)
  was off by ~0.08°/s. `gyro_loop_bias.py` fits the bias from all pairs (> 120 s pairs: 14.6 → 3.5°, the noise floor
  of these images is ~3°); `rot_sfm.py --bg_json --max_dt 300` then uses far-apart pairs too, and `prior_ba.py`
  refines. Result: the start and end of the walk share 3,625 of 5,603 points (R-052: 115), the scale check says "ok"
  for the first time on scan_009, training-view PSNR ≈ R-047. Two stretches (45 – 60 s, 90 – 105 s) have almost no
  matched points and rest on the IMU alone: this is where step 4 (lines, layout) would help.
- **Validation on newRoom** (R-072): position error of the sensor path against normal SfM, median (p90): 72 (166) cm →
  31 (68) cm with the full recipe; scale 0.89. Still far worse than normal SfM: the recipe is a fallback for captures
  where SfM fails, not a replacement.
- **Scale of scan_009:** accelerometer 0.37 – 0.48, Metric3D ~0.44 – 0.53, room height (if 2.6 – 3.0 m) 0.56 – 0.64 m
  per model unit: about 2× too large, but no source is reliable enough to apply.

---

## 9. Plan from 2026-11-20 (after merging `master`, 2026-11-19)

Written for Tayyab after `master` (Umair's Step 4 work, the online site, app v0.3.9) was merged into this branch.
**A proposal, not a decision:** the rows marked "decision" are Tayyab's or the team's.

### 9.1 What changed on `master` that matters here

- **Week 2 (2026-11-20 → 11-26) is the evaluation week**; gate G2 on 11-26 wants every evaluation number measured
  ([COMPLETION_PLAN.md](COMPLETION_PLAN.md)). **E1** ("COLMAP with vs without ARCore priors on low-texture captures:
  ATE, track completion", Must, no owner yet) is the evaluation this work answers. So the featureless work should go
  into E1 first and into new methods second.
- **Step 4 layout** (`layout.py` with D-075 defaults, openings, `--square`, `plan_export.py`): it was never run on a
  sensor-path model. It may give scan_009 a cleaner outline and a room height, which is scale option 3 in §5.
  COMPLETION_PLAN **4.11** ("edge-based corners, gravity-aware lines, wall–floor boundary", Could, W3) needs the same
  line detector as step 4 here. Build it once, with Umair.
- **Gravity (D-071):** `sfm_colmap.py` export now levels the world with ARCore gravity. `--sim3 none` (sensor-path
  models, already +Y up) skips both the Sim3 and the levelling. That is correct for `rot_sfm.py --imu 1` output; it is
  checked only by `py_compile`, not by a run after the merge.
- **Online site (D-076, D-077):** the deployed site shows only scans published to R2 (cap 10 GB). `scan-009-gyro` /
  `scan-009-loop` exist only in `mockData.ts` on this PC. Showing scan_009 online needs a web bundle (`export_web.py`)
  and `publish_scan.py`, and a clear "scale not reliable" label. Part of OD-15.
- **Run IDs (D-079):** check `origin/master`'s TRAINING.md before every run. The next free numbers after this merge
  are **R-073** and **D-081** (R-060 / R-061 and D-078 are Umair's).

### 9.2 Steps, in order

| # | Step | Effort | Done when | Needs | When |
|---|---|---|---|---|---|
| 9.a | **E1 table.** Cut-gap captures (newRoom, bedroom, roomAttemptSadness2: windows of 2 / 9 / 15 / 30 s removed) placed by (1) normal SfM, (2) SfM + gyro check / placement, (3) the sensor-path recipe (R-071). Report ATE (median / p90) and frames placed. Add scan_009's frames placed (R-046 370 → R-071 680) and loop error. Move `eval_rot.py` and `render_compare.py` from the agent's scratch folder into `src/arcore3dgs/` as eval tools | 1.5 days | table in TRAINING + report draft | E1 owner (decision) | 11-20 → 11-22 |
| 9.b | **Scale for scan_009.** (1) Run `layout.py` (D-075 defaults) on R-071 and record the room height. (2) Ask who recorded scan_009 and tape the room: one length and the height. (3) Apply the scale, check it against the accelerometer / Metric3D estimates (§8.2), and run `tape_check.py` (E2) | 0.5 day + a tape visit | scale applied with its error stated, or "not measured" | access to the room | 11-21 → 11-23 |
| 9.c | **Sharp re-recording of scan_009's room** with the capture protocol (COMPLETION_PLAN 1.4). This separates blur (21.7 px median) from missing texture. Process with the normal pipeline first, then with 9.d if SfM fails | 1 h recording + 1 run | logged run; frames placed and scale check vs R-071 | the app with the corner prompt (9.g) helps but is not required | 11-21 → 11-24 |
| 9.d | **Pipeline option (if OD-15 = a).** `run_full.sh` / `run_v8.py` option that runs `gyro_loop_bias.py` → `rot_sfm.py --bg_json --max_dt 300` → `prior_ba.py` → export `--sim3 none`, **only** when `sfm_scale_check.py` fails, with "scale unknown" in the web bundle. Tested on scan_009 (must reproduce R-071) and newRoom (must not trigger) | 1 day | two logged runs; default off until tested | OD-15 (decision) | 11-23 → 11-25 |
| 9.e | **Step 4, lines and layout, for the IMU-only stretches** (45 – 60 s, 90 – 105 s of scan_009): wall–floor / wall–wall junction lines (LSD, gravity-aware) matched to the R-071 layout, position solved with the gyro rotation fixed (like `known_rot_pnp.py`). Shared with COMPLETION_PLAN 4.11 | 3 – 4 days | cut-gap position error better than R-072's 31 cm median; scan_009 stretches with points | 9.a, 9.b; agree the split with Umair | W3 (11-27 →), only if G2 is met |
| 9.f | **VGGT (step 2)** on the two IMU-only stretches, as a quick comparison | 0.5 day | frames placed, gyro agreement | **Tayyab's OK to run downloaded code** (decision) | any time once approved |
| 9.g | **App:** the corner / edge prompt is under "Unreleased" in `android/CHANGELOG.md` (not in v0.3.9). It ships with the next release once this branch is merged. Add the long-line count to `quality.csv` | 0.5 day + device test | prompt seen on a phone | merge to `master` | with the merge |
| 9.h | **Report section** for the final report: method (gyro check, loop bias, prior BA), E1 numbers, scan_009 before / after renders, limits (scale, IMU-only stretches) | 1 day | section drafted | 9.a, 9.b | W3 |

**Not planned before 2026-12-04:** step 5's line BA, step 7 (planes from depth, full fusion back end, direct odometry).

### 9.3 Decisions needed (none taken here)

- **OD-15** (Tayyab): sensor-path recipe as an opt-in pipeline fallback, and which scan_009 model to show. Now also:
  whether to publish scan_009 to the online site before its scale is known.
- **E1 owner** (team): proposed Tayyab, since 9.a reuses this branch's tools.
- **VGGT** (Tayyab): run the downloaded code, or drop step 2.
- **Merge this branch to `master`** (Tayyab, through a PR with CI green). It carries the app prompt, the tools and the
  records Umair's side does not have yet. One test fails on `master` and here alike (`test_changelog`, v0.3.9 released
  with an empty "Unreleased"), so CI may be red for a reason that is not this branch's.
- **Disk on the 3070 PC** (Tayyab): ~9 GB free; scan_009's `work_v9pfb*` / `work_v9pfl*` hold ~4 GB. Keep R-071's
  folders, and ask before removing the rest.
