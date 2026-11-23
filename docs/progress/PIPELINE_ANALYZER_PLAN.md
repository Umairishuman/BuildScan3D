# Pipeline analyzer: one pipeline for textured and featureless recordings (plan)

Status: **planned, not started** (Tayyab, 2026-11-22, D-095). The scan_009 camera fixes (steps 4 and 3 of the
2026-11-22 plan, R-120 / R-121) go first; this plan is what they are folded into afterwards.
Related: [FEATURELESS_TRACKING_PLAN.md](FEATURELESS_TRACKING_PLAN.md) (§10 – §11, how the scan_009 recipe was found),
OD-10 (fast recipe), OD-11 (SfM fallback), OD-15 (sensor-path recipe), [STATUS.md](STATUS.md) §7.

## 1. The problem (Tayyab, 2026-11-22)

"This isn't a proper pipeline overall, we're specifically targeting some areas of recordings. Can it not be
automatically decided by an analyzer in the pipeline so it works on all types of datasets, featureful and
featureless?" And: "we need to consider total processing time very much, we have to reach good numbers by the end."

What is hand-made today:

- `run_v8.py` makes no decisions. The route is chosen per recording with flags (`--pose_free`, `--planar`, `--pgsr`,
  `--blur`, `--train_args "--path_prune 0.1"`, ...).
- The sensor-path camera chain that made R-096 (`rot_sfm.py` → `prior_ba.py` → `scale_drift.py` → `loop_path.py` →
  `prior_ba.py --pair_priors`) runs outside `run_v8.py`, from hand-written `dataset/.../r0xx.sh` scripts.
- Every choice in that chain (which step, which settings, which stretch of the walk is the problem) was made by
  looking at scan_009's numbers. Nothing guarantees it helps, or does no harm, on another recording.

What is already generic (keep):

- `loop_path.py` validates itself: 20 % of the loop pairs are held out and their angle before / after is reported.
- `prior_ba.py --adapt_n`: position priors tight where a frame has few 3D observations, loose where it has many.
- `sfm_scale_check.py`, `eval_align.py`, `offpath_views.py`, `clean_splats.py` work on any recording.

## 2. Design

### 2.1 Analyzer (first stage, cheap)

Measures the recording per time window (e.g. 5 s) and writes `analysis.json`:

| Signal | Source (existing) |
|---|---|
| keypoints per frame, texture (gradient energy) | feature extraction (`sfm_colmap.py`, ALIKED), done anyway; `texture_probe.py` (SIFT keypoints, long lines, gradient share per keyframe) |
| verified matches / pairs per frame, long-range pairs | COLMAP database, done anyway |
| frames registered by normal SfM, in one model | `sfm_colmap.py` mapper output |
| 3D observations per camera | `sfm_colmap.py` / `prior_ba.py` |
| SfM rotation vs gyro agreement | `rot_sfm.py` / `gyro_loop_bias.py` |
| ARCore tracking state, sensor-path jumps | `poses.csv` |
| blur | `select_sharp.py` sharpness, `blur_motion.json` |
| holes in the camera path: keyframes not placed, one long step | camera model vs `frames.json` (R-121: scan_009 125.4 – 133.2 s, 35 keyframes, none placed, blur 12 – 42 px, no ARCore pose) |
| scale consistency | `sfm_scale_check.py` |

Each window gets a label: **textured / weak / featureless**. The analyzer must not add a heavy pass of its own: it
reads what the stages compute anyway, plus cheap image statistics.

### 2.2 Route decision

- **Normal SfM route** (today's v9 / fast recipe) when SfM registers nearly all frames in one model and the scale
  check passes.
- **Sensor-path route** (R-096's chain, moved into `run_v8.py`) when it does not; on the windows that SfM could not
  place, or on the whole recording when no reliable single model exists.
- Thresholds are set on the test bench (§3), not on one recording. The decision and every number behind it are
  written to `report.json`, so a run explains itself.

### 2.3 Every corrective step checks itself

A step is kept only when a measured check improves; otherwise it is skipped and the report says why:

| Step | Check |
|---|---|
| loop closure (`loop_path.py`, `prior_ba.py --pair_priors`) | held-out loop pairs' angle improves (already built in) |
| scale-drift correction (`scale_drift.py`) | room height along the walk more constant, Metric3D ratio spread not worse (R-094) |
| extra loop pairs (`loop_match.py`) | new pairs agree with the current path within a gate (R-121); a correction must not move one side of a path hole against the other unless pairs tie both sides (R-121 broke 134 – 140 s) |
| pose refinement in training (`--pose_opt`) | held-out aligned PSNR (R-120) |
| floater clean-up (`clean_splats.py`) | held-out aligned PSNR not worse (R-100: the camera-path rule failed this) |

### 2.4 Frames weighted by camera trust

Frames in featureless windows whose camera could not be checked (no 3D observations, no long-range pairs) get less
photometric weight in training, or are left out (Tayyab's idea, 2026-11-21), decided by the analyzer's labels.

## 3. Test bench (so the rules are not tuned to scan_009)

| Recording | Type | Reference result |
|---|---|---|
| newRoomAttemptSadness | textured, trusted SfM path | v9 / fast recipe (R-062, R-063) |
| roomAttemptSadness2 | textured | R-069 (`v9pgsr8`) |
| scan_3028a4de8fa0 | lecture hall, GLOMAP scale collapse | R-068 (incremental mapper) |
| scan_009_057ed3beb4fc | featureless, re-recording impossible | R-096 / R-099 |

Pass: the automatic pipeline matches or beats the best hand-made result on each, on held-out aligned PSNR (and
`offpath_views.py` for off-path coherence), and reports its processing time.

## 4. Processing time (a primary target)

Targets (STATUS §2): proposal < 15 min on a 4090; FYP-2 target < 35 min on a 4090 (a projection). Measured so far on
the RTX 3070, all from TRAINING.md:

| What | Time | Source |
|---|---|---|
| v9 end to end, normal SfM | 96 min (SfM 22, priors 8, init 20, training 43) | STATUS §2 |
| training with the speed-ups | 28.2 min (was 42.5) | R-062 |
| photometric fast-MVS init | 7.5 min (was 20.1) | R-063 |
| sensor-path model from export | 28.3 min (prior 3.45, init 1.67, train 22.46, ply 0.63) | R-096 |
| rot_sfm + prior BA per variant | rot_sfm 2.8, prior BA 1.2 – 1.5 min | R-079 |
| loop solve + BA | 7 min (incl. a failed first BA) | R-096 |
| held-out evaluation (`eval_align.py`) | ~8.5 min per model | R-100 |

Not measured: the sensor-path chain end to end as one run (feature extraction and matching through the final BA).
That is the first number the pipeline version must produce.

Rules for the pipeline:

- Every stage writes its time to `timing.json` (exists for training) and the total goes in `report.json`.
- Steps that a check says are not needed are skipped, which is also the main time saving on textured recordings.
- Evaluation (held-out split, `eval_align.py`, off-path views) is for development runs only, never in the user path.
- Each new step states its time cost next to its quality gain in TRAINING.md; a step that costs much time for a
  gain inside the noise (~0.1 – 0.25 dB) is not adopted.

## 5. Order of work (after R-120 / R-121)

1. Analyzer (`analysis.json`) on the four recordings, from outputs that already exist; check the labels against what
   we know of each recording.
2. Route decision in `run_v8.py`; the sensor-path chain moved from the shell scripts into `run_v8.py` stages, each
   with its check (§2.3) and its time.
3. Test bench run of all four; compare with the reference results; tune the thresholds on all four together.
4. Frame weighting by camera trust (§2.4), if time allows.

Open questions for the team: owners (OD on COMPLETION_PLAN owners), and whether the analyzer's labels are also shown
to the user (capture feedback in the app, Umair's area).
