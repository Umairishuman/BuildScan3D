# BuildScan3D: Decision Log

Every decision that shaped the project: what was decided, why, the evidence, what was rejected, and who decided.
Newest decisions are added at the end with the next free number. A decision is never deleted: when it is replaced,
its status becomes **Superseded by D-xxx** and the new entry says what changed. Rules: [CLAUDE.md](../../CLAUDE.md).

- **Status:** Active · Superseded by D-xxx · Rejected (an option that was tried and dropped) · Parked.
- **By:** the person who decided, when recorded. Entries D-001 to D-043 were backfilled on 2026-11-06 from
  `Problems_and_Solutions.md` (P&S), the old `TODO.md` ([archive/TODO.md](archive/TODO.md)), the mid-evaluation
  summary, proposal v4 and the report fix brief. Where the source does not name a person, "By" gives the
  commit author of that work; "the user" means the person running that session, as the source says.
- **Open decisions** that still need the team are at the end (OD-x). Agents must not settle them on their own.

| # | Date | Decision (short) | Status |
|---|---|---|---|
| D-001 | 2026-08-22 | Original plan from proposal v4 | Partly superseded |
| D-002 | 2026-10-07 | Pose per video frame by timestamp interpolation | Active |
| D-003 | 2026-10-07 | All geometry on the raw landscape image | Active |
| D-004 | 2026-10-07 | Metric3D only with the official preprocessing, and anchored to metric data | Active |
| D-005 | 2026-10-07 | Own GPU bundle adjustment with ARCore priors | Superseded by D-014 |
| D-006 | 2026-10-07 | Own plane-sweep MVS with Metric3D fill | Superseded by D-018 / D-023 |
| D-007 | 2026-10-07 | Two-pass depth fusion | Superseded by D-014 |
| D-008 | 2026-10-09 | Skip frames after tracking loss; no motion prior across gaps | Active in the legacy pipeline |
| D-009 | 2026-10-09 | Supervise depth with each frame's own MVS depth | Superseded by D-010 |
| D-010 | 2026-10-10 | Splatfacto trains; our code does the phone-specific preprocessing | Active |
| D-011 | 2026-10-10 | Every extra loss term must be ablated against the plain recipe | Active (rule) |
| D-012 | 2026-10-10 | Viewer defaults: 45° FOV, 15 cm near clip | Active |
| D-013 | 2026-10-10 | PocketGS-style dense prior + short training as default | Superseded by D-014 |
| D-014 | 2026-10-11 | Poses from COLMAP SfM; ARCore only for scale, gravity, guidance, fallback | Active |
| D-015 | 2026-10-11 | Bilateral grid + scale regularisation, no camera optimiser | Active |
| D-016 | 2026-10-10 | IMU featureless-tracking fallback as a project novelty | Active (not in v9) |
| D-017 | 2026-10-12 | Post-hoc wall / floor flattening rejected; structural layer for measurement | Active |
| D-018 | 2026-10-12 | v6: gyro-aware frames + dense MVS init + grad 0.0006 | Superseded by D-023 |
| D-019 | 2026-10-12 | Evaluation rules: trimmed Sim3, pose refinement, off-path split, visual check | Active |
| D-020 | 2026-10-21 | v7 fast pipeline rejected; ARCore-guided matching kept | Active |
| D-021 | 2026-10-24 | v8: DashGaussian + SfM-anchored priors 0.05 / 0.05, 15k iterations | Active (part of v9) |
| D-022 | 2026-10-26 | SfM with vocabulary-tree retrieval; ALIKED + LightGlue rejected | Active |
| D-023 | 2026-10-26 | v9 recipe: fast MVS init, planar 0.2, motion blur 1/45 s | Active |
| D-024 | 2026-10-26 | Room layout from planar regions (`layout.py`) | Active |
| D-025 | 2026-10-27 | PGSR-lite kept for the final model although the gain is marginal | Active |
| D-026 | 2026-10-27 | Semantics = 2D proposals + 3D verification, decoy classes, own env | Active |
| D-027 | 2026-11-03 | Semantics v10 changes | Active |
| D-028 | 2026-10-27 | Priors matched by frame name; don't use the v8_geofast15 model | Active |
| D-029 | 2026-10-27 | Checkpoint every 2500 steps, `--resume` | Active |
| D-030 | 2026-10-24 | Web viewer renders splats in the browser (Spark) from `.spz` | Active (see OD-1) |
| D-031 | 2026-10-12 | App logs exposure, rolling shutter, anchors and lens calibration | Active |
| D-032 | 2026-10-23 | App: predicted-blur IQA, lighter recording; overlay features reverted | Active |
| D-033 | 2026-10-22 | Scope and claims fixed for the mid report | Active |
| D-034 | 2026-10-12 | Processing server: FastAPI + subprocesses, four modes, RunPod safety | Active |
| D-035 | 2026-10-19 | Prebuilt GPU Docker image for RunPod | Active (image outdated) |
| D-036 | 2026-10-10 | CI/CD on GitHub Actions, branch-and-PR workflow | Active |
| D-037 | 2026-11-06 | Three Python environments with their own requirements files | Active |
| D-038 | 2026-10 | Environment fixes on the RTX 3070 PC | Active |
| D-039 | 2026-10-11 | Median filtering only on depth, never on images | Active |
| D-040 | 2026-10-11 | No floater pruning by default | Active |
| D-041 | 2026-10-09 | MCMC densification off | Active |
| D-042 | 2026-10-12 | Exposure lock not pursued | Parked |
| D-043 | 2026-10-12 | Folder clean-up | Superseded by D-044 |
| D-044 | 2026-11-06 | Project records: STATUS / DECISIONS / LOG / TRAINING; mid-eval to `report/`; archive | Active |
| D-045 | 2026-11-06 | Pipeline must run on this PC, a friend's PC and RunPod; Docker not installed here yet | Active |
| D-046 | 2026-11-06 | Umair's next focus: semantic labelling, after the organisation work | Active |
| D-047 | 2026-11-06 | Set up this PC first, same versions as the 3070 PC, in conda envs; Docker after | Active |
| D-048 | 2026-11-06 | One setup script for this PC, the friend's PC and the Docker image | Active |
| D-049 | 2026-11-06 | Reorganise in two steps; never delete files, archive them | Active |
| D-050 | 2026-11-06 | `MAP.md` is the first file every session reads | Active |
| D-051 | 2026-11-06 | Merge `feature/semantics-mesh` + organisation + Linux port into `master` by PR | Active |
| D-052 | 2026-11-06 | Delete only fully merged branches, never unmerged ones | Active |
| D-053 | 2026-11-06 | This PC: no auto-suspend; remote access by Tailscale (plan) | Active |
| D-054 | 2026-11-06 | CI coverage gate lowered 40% → 35% until the tests are written | Active (temporary) |
| D-055 | 2026-11-06 | Unused 12.5 MB `newroom_v6.spz` out of git, kept locally | Active |
| D-056 | 2026-11-06 | The GitHub repository stays public | Active |
| D-057 | 2026-11-06 | Linux upload server: own env `bs-server` + `scripts/start_server.sh`, `dry_run` by default | Active |
| D-058 | 2026-11-06 | App package name `com.buildscan3d.app` instead of Google's sample name | Active |
| D-059 | 2026-11-06 | Release APKs signed with a private key kept in GitHub Secrets | Active |
| D-060 | 2026-11-06 | App fixes ship by PR → merge → CD release | Active |

---

## D-001 · 2026-08-22 · Original plan (proposal v4)
- **Decision:** Android ARCore capture with live IQA → upload to object storage → Redis-queued, Dockerised cloud GPU
  workers (RunPod) that fuse ARCore with COLMAP, train 3DGS, run 2D CNN material segmentation (drywall, wiring) and
  project it to 3D, prune and compress to `.ksplat` → Next.js dashboard with a Three.js viewer, adaptive splat budget,
  measurement and an "X-ray / rough-in" overlay. Ownership: Umair mobile capture, Tayyab cloud orchestration + 3DGS,
  Zaid semantics + compression + web.
- **Why:** ARCore gives metric scale and gravity directly; VIGS-SLAM motivates visual-inertial tracking on plain
  surfaces; GSemSplat motivates decoupling semantics from training; 3DGS output is too large for browsers uncompressed.
- **Status:** partly superseded: poses (D-014), semantics scope (D-033), compression format (D-030, OD-1), queue (D-034, OD-2).
- **Source:** `docs/proposal/BuildScan3D_FYP_Proposal_v4.docx`. **By:** team (proposal).

## D-002 · 2026-10-07 · Pose per video frame by timestamp interpolation
- **Decision:** read every frame's PTS (ffprobe), sort and de-duplicate poses, interpolate the pose at each frame time
  (linear position, slerp rotation), skip frames inside tracking gaps > 0.12 s.
- **Why:** `fusion_pipeline.py` paired frame *k* with pose row *k*; poses are only logged while tracking, so the index
  error grew to +2 s. A constant `POSE_OFFSET` (the earlier "MediaRecorder lag" theory in
  [archive/FYP Problems Faced.docx](archive/)) cannot fix growing error.
- **Evidence:** pose-to-image-motion correlation 0.17–0.23 → 0.76–0.79; sync offset 0.00 ± 0.05 s. **Rejected:** POSE_OFFSET.
- **Source:** P&S §1.1–1.2. **By:** committed by Tayyab (BlazingBeam).

## D-003 · 2026-10-07 · All geometry on the raw landscape image
- **Decision:** the video is stored sideways in sensor orientation and `camera.getPose()` refers to that frame (OpenGL
  axes), so geometry uses the raw landscape image; rotate only for display (and for detectors, `semantic2d.py`).
- **Evidence:** motion correlation signs and near-zero cross terms. **Source:** P&S §1.3.

## D-004 · 2026-10-07 · Metric3D only with official preprocessing, anchored to metric data
- **Decision:** resize/pad to 616×1064 and rescale by `fx × scale / 1000`; never use Metric3D depth raw: align it to metric
  points (ARCore points then, SfM points per frame since v8: 19.5% → 2.7% median error).
- **Why:** torch-hub Metric3D ignores the intrinsics; per-frame scale varied 0.85–1.50×. Lesson: "monocular depth is a prior, not a measurement".
- **Source:** P&S §2.1–2.3, §4.15.

## D-005 · 2026-10-07 · Own GPU bundle adjustment with ARCore priors — Superseded by D-014
- **Decision:** custom Schur-complement Levenberg–Marquardt on the GPU; tight ARCore relative-motion priors (keep
  scale), weak absolute priors.
- **Evidence:** reprojection 2.32 → 0.61 px, trajectory 0.998× ARCore. **Why superseded:** it starts from and keeps
  ARCore's poses, so it kept the 1 m / 28° re-anchor error (D-014). **Rejected along the way:** scipy `least_squares` (too slow). **Source:** P&S §3.

## D-006 · 2026-10-07 · Own plane-sweep MVS + Metric3D fill — Superseded
- **Decision:** 5-source NCC plane sweep around Metric3D depth with strict consistency; fill unmeasured pixels with
  Metric3D corrected by a smooth log-depth field. **Limit:** only ~11% of pixels measured on plain walls.
- **Superseded by:** COLMAP PatchMatch dense init (D-018), then `fast_mvs.py` (D-023). **Source:** P&S §4.1.

## D-007 · 2026-10-07 · Two-pass depth fusion — Superseded by D-014
- **Decision:** fuse only frames with ≥ 3% MVS-measured depth, fit the rest to that surface, drop frames > 5% off.
- **Evidence:** fused room height 5.5 → 3.9 m; curtain/cupboard ghosts gone. **Source:** P&S §4.2.

## D-008 · 2026-10-09 · Skip frames after tracking loss; no motion prior across gaps
- **Decision:** `prepare.py --settle` / `filter_frames.py` drop frames within 3 s after a tracking loss; no BA
  relative-motion prior across a gap; ARCore depth anchoring on by default; training steps scale with frame count;
  new "too plain / low texture" IQA warning; capture advice: keep an edge or object in view in plain rooms.
- **Why:** roomAttemptSadness2: 91% of keyframes within 2 s after a loss were inconsistent; inconsistency followed viewing
  direction (ceiling 94%), not blur or IQA level. **Source:** P&S §4.3. Applies to the legacy pipeline; v9 relies on SfM.

## D-009 · 2026-10-09 · Depth supervised by each frame's own MVS depth — Superseded by D-010
- **Decision:** replace the fused-TSDF depth target by per-frame `depth_mvs` weighted by `mvs_mask`; fused mesh only for
  init; weaker depth loss; full-res last phase; outlier-frame rejection; pinned RAM + splat cap.
- **Why:** the fused target was wrong on ~30% of measured pixels and lay behind real surfaces (cotton texture).
- **Evidence:** train-view PSNR 21.36 → 23.60 dB. On ARKitScenes (Zaid, Kaggle) the depth target alone made no measurable
  difference (`origin/exp/trainer-arkitscenes`). **Source:** P&S §4.4.

## D-010 · 2026-10-10 · Splatfacto trains; our code does the phone-specific preprocessing
- **Decision:** our pipeline does sync, tracking-loss filtering, poses, MVS, measured initialisation; Nerfstudio
  splatfacto does the training (now via `geo_splatfacto.py`, a splatfacto subclass). Own `train.py` stays for experiments.
  Init from triangulated + MVS-measured points only, PocketGS discs, opacity 0.1; no flattening / needle terms, depth
  loss off, classic rasterisation, BA poses fixed.
- **Why:** six root causes of degenerate, half-transparent splats in our trainer (flattening × Adam, anti-aliasing ×
  zero-thickness splats, init from single-image depth, mono depth loss, pose drift, opacity 0.5).
- **Evidence (roomAttemptSadness2):** held-out 21.48 → 24.70 dB (own trainer, new recipe) vs **27.81 dB** (splatfacto, same inputs).
- **Source:** P&S §4.5, [archive/Training_Analysis.md](archive/Training_Analysis.md).

## D-011 · 2026-10-10 · Ablate every extra term against the plain recipe (rule)
- **Decision:** a "physically motivated" extra (flatness, depth, pose refinement, priors) is only kept if it beats the
  plain recipe in a controlled comparison. **Why:** all of them together made results worse than none. **Source:** P&S §4.5 lesson.

## D-012 · 2026-10-10 · Viewer defaults: 45° FOV, 15 cm near clip
- **Why:** a 75° vertical FOV showed directions never filmed (smears); at 45° the same model is clean. Lesson: judge
  a model at capture-like camera settings. **Source:** P&S §4.6.

## D-013 · 2026-10-10 · PocketGS-style dense prior + short training — Superseded by D-014
- **Decision:** 8 cm / 6° keyframe gate, multi-view-consistent dense prior (70% of pixels), discs, 8k steps (12.7 min).
- **Why:** photometric-only training left walls free for floaters; a correct dense prior keeps off-path views coherent.
- **Rejected:** a literal PocketGS copy (500 iterations): its own quality is 22–23.5 dB, below ours. **Source:** P&S §4.7–4.8.

## D-014 · 2026-10-11 · Poses from COLMAP SfM; ARCore for scale, gravity, guidance and fallback
- **Decision:** COLMAP 4.2 (SIFT, global mapper, one OPENCV camera with self-calibrated distortion, undistortion); a
  RANSAC Sim3 to ARCore camera centres gives metric scale and up; mis-registrations (> 30 cm jumps) dropped; training at full resolution.
- **Why:** a silent ARCore re-anchor at ~60 s put every earlier pose ~1.0 m / 28° off (part of the room existed twice);
  ARCore intrinsics have no distortion (k1 = 0.093, k2 = −0.22); 8% of frames never registered; half-res training.
  Invisible to the earlier geometry check because its reference points used the same wrong poses.
- **Evidence (newRoom):** training views 21.9 → 28.2 dB, held-out 22.7 → 27.2 dB, SSIM 0.782 → 0.864, misalignment
  12–30 → 2–3 px; tape mean error 4.8 mm. **Thesis finding:** ARCore is a good live tracker but not an offline scanning system.
- **Source:** P&S §4.11–4.12, mid-evaluation summary §5–6. **By:** committed by Tayyab (BlazingBeam).

## D-015 · 2026-10-11 · Bilateral grid + scale regularisation, no camera optimiser
- **Decision:** `--pipeline.model.use-bilateral-grid True` (absorbs auto-exposure / white balance), scale regularisation
  (no needles), **no SO3xR3** camera optimiser, default densify thresholds.
- **Rejected:** SO3xR3 (shifts the scene 3–16 px); `splatfacto-big` thresholds (OOM on 8 GB at full res).
- **Evidence:** v3 25.57 dB / 0.857, geometry median 0.59%, "clean and aligned" (v1 had cloudy walls). **Source:** P&S §4.11.

## D-016 · 2026-10-10 · IMU featureless-tracking fallback as a novelty
- **Decision:** IMU from the ARCore MP4 (201 Hz), self-calibrated IMU→camera rotation, gap bridging (gyro rotation,
  accelerometer position with cubic correction), heading-jump detection, PnP re-alignment of post-gap segments;
  unverified segments are excluded.
- **Evidence:** simulated 9 s gap 3.8 cm vs 30.6 cm interpolation; post-gap epipolar error 49.7 → 8.2 px.
- **Status:** in `run_arcore3dgs.bat` and the server pipeline, **not in `run_v8.py`** (see OD-6). **Source:** P&S §4.10.

## D-017 · 2026-10-12 · Post-hoc flattening rejected; structural layer for measurement
- **Decision:** don't snap splats onto planes after training (`planarize.py`); use the structural layer
  (`structure.py`, later `layout.py`) for measurements, openings and floor plans; get visual flatness from training priors.
- **Why:** flattening killed the glossy floor's reflections and crushed door frames. **By:** rejected by the user after a visual check.
- **Source:** archive/TODO.md "Parked", mid-evaluation summary §9.

## D-018 · 2026-10-12 · v6: gyro-aware frames + dense MVS init + grad 0.0006 — Superseded by D-023
- **Decision:** least-blurred frame per 0.2 s from the gyro (`select_sharp.py`, 1166 frames registered into v3's model),
  COLMAP PatchMatch dense init (~460k points), densify grad 0.0006.
- **Why:** gyro shows 6–12 px median blur; Laplacian sharpness hardly tracks it (r = 0.20).
- **Evidence:** v3 26.04 → v6 26.52 dB / 0.8886 (mid-report headline). Cost: ~4 h end to end. **Source:** P&S §4.13.

## D-019 · 2026-10-12 → 10-24 · Evaluation rules
- **Decision:** compare on frames no model trained on; map test poses with a **trimmed** Sim3 (untrimmed cost 3 dB);
  refine test-camera poses photometrically for models from different SfM runs (`fair_compare.py`); judge off-path
  quality on the 79-frame off-path split (`eval_offpath.py`) plus off-path flatness; the visual check decides.
- **Why:** held-out frames on the walked path hide off-path failures; unaligned SfM runs made v7 look 5 dB worse.
- **Source:** P&S §4.13–4.16.

## D-020 · 2026-10-21 · v7 fast pipeline rejected; ARCore-guided matching kept
- **Decision:** reject the 25-min v7 recipe (24.83 dB vs 26.45, fine detail lost, off-path views worse); keep
  `sfm_colmap.py --pairs arcore` (matching 54 s instead of 23 min). **By:** rejected by the user. **Source:** P&S §4.14.

## D-021 · 2026-10-24 · v8: DashGaussian + SfM-anchored priors, 15k iterations
- **Decision:** DashGaussian resolution schedule, Metric3D depth/normal priors 0.05 / 0.05 aligned to SfM points,
  15k iterations, `--no_eval`; Metric3D fp16 by default.
- **Rejected:** stronger priors 0.1 / 0.2 (over-smooth); mono-depth dense init alone (loses few-view detail).
- **Evidence:** 30.2 vs 64.3 min training, SSIM 0.8281 vs 0.8241, only model keeping the hardest frame's painting. **Source:** P&S §4.15.

## D-022 · 2026-10-26 · SfM with vocabulary-tree retrieval; ALIKED + LightGlue rejected
- **Decision:** `sfm_colmap.py --retrieval 20` (+ `--bridge 1`). **Evidence:** one component, 1164/1166 frames, 5.8 cm /
  0.52° from v6. **Rejected:** ALIKED + LightGlue (slower, folded reconstruction, 74 cm off). Lesson: compare whole
  trajectories, not only Sim3 inliers. **Source:** P&S §4.16.

## D-023 · 2026-10-26 · v9 recipe
- **Decision:** `run_v8.py --sfm_args "--retrieval 20" --init fmvs --planar 0.2 --blur 0.0222` (fast PatchMatch on every
  7th frame, planar-region prior, motion-blur model at 1/45 s).
- **Evidence:** 96 min end to end; 25.16 dB / 0.8247, sharpness 0.80, flatness 0.77 cm, hardest frame complete for the
  first time. **Open:** scale 1.9% smaller than v6 (7.4 in STATUS). **Source:** P&S §4.16.

## D-024 · 2026-10-26 · Room layout from planar regions
- **Decision:** `layout.py`: planar regions lifted with rendered depth → floor / ceiling / wall lines (any number, any
  angle), furniture fronts and see-through surfaces dropped, corners from wall intersections. **Evidence:** 6.675 × 4.406 m
  on v9planar (tape 6.70). **Source:** P&S §4.16.

## D-025 · 2026-10-27 · PGSR-lite kept in the final model
- **Decision:** `geo_splatfacto.py --pgsr` (flat discs, unbiased depth, single-view consistency) for the final model and
  `mesh.py --depth unbiased`. **Why:** sharper splats (0.88 vs 0.80), slightly flatter on 4 of 6 surfaces; the verdict
  was "marginal". Multi-view terms not implemented. **Source:** P&S §4.17.

## D-026 · 2026-10-27 · Semantics: 2D proposals + 3D verification
- **Decision:** Grounding DINO tiny + SAM on gravity-upright frames with decoy classes; Gaussians vote with the 2D
  labels; structure from the layout; fixtures must be seen in ≥ 6 frames and pass class geometry rules; separate
  `semantic-env`. Follows the proposal's decoupled-semantics decision (GSemSplat). **Source:** P&S §4.17.

## D-027 · 2026-11-03 · Semantics v10
- **Decision:** wardrobe / cabinet decoys stop competing with "door"; door fragments merge; tube-light class; a tiled
  second detector pass; fallback to the next most voted class; CLIP crop check of switches / sockets (threshold 0.5);
  > 25% switch votes → switchboard. **Evidence:** 15/15 correct, 15/17 found, but tuned on the same 17 fixtures.
  Cost: 2D stage 8 → 38 min. **By:** fixes against the user's room check (2026-11-02). **Source:** P&S §4.18.

## D-028 · 2026-10-27 · Priors matched by frame name; don't use v8_geofast15
- **Decision:** the dataparser uses `eval_mode="all"`; packed priors store frame names and are checked against the
  trainer's image order. `saved_models/2026-10-24_v8_geofast15` was trained with misaligned priors: don't use it.
- **Why:** without a split, nerfstudio held out 10% itself, so 1039 of 1049 cameras got another frame's priors. **Source:** P&S §4.17.

## D-029 · 2026-10-27 · Checkpoint every 2500 steps, `--resume`
- **Why:** a power cut at 83% of the final run lost it. Resumed runs get only the remaining steps (nerfstudio adds
  `max_num_iterations`). Earlier rule: checkpoint every 1000 steps in `train.py`, stages cache outputs. **Source:** P&S §4.17, §6.

## D-030 · 2026-10-24 · Browser-side splat rendering with Spark and `.spz`
- **Decision:** replace the server-rendered viser viewer by Spark (World Labs, Three.js) in `prototype/web-ui`, deliver
  compressed `.spz` (148 → 12.5 MB), labelled groups via `export_web.py`.
- **Why:** viser rendered on the server and streamed JPEGs (lag). **Note:** the proposal named `.ksplat`; Zaid's branch
  evaluates `.ksplat` — see OD-1. **Source:** Research_Notes §5, P&S §4.15, prototype/web-ui/STATUS.md.

## D-031 · 2026-10-12 · App logging for blur, re-anchors and lens
- **Decision:** `camera.csv` (exposure, rolling-shutter skew, ISO, focus), `anchors.csv` (re-anchor detection),
  `lens_metadata.json` / `camera_characteristics.json`, raw depth saved only when new; `select_sharp.py` uses real exposure.
- **Why:** inputs for blur / rolling-shutter modelling and for detecting silent re-anchors. **Source:** archive/TODO.md 2026-10-12.

## D-032 · 2026-10-23 · App capture-quality audit; overlay features reverted
- **Decision:** predicted-blur IQA ((angular + linear/2.5 m speed) × exposure × focal; warn > 5 px, bad > 10 px) replaces
  the 30 / 60 °/s limits; environmental-HDR light estimation off; IQA reads every 8th pixel; demo pawn and its rendering removed.
- **Also:** surface map, room-layout overlay, autofocus toggle, feature-starvation warning and vertical plane finding were
  built the same day and **reverted at the user's request** (the layout overlay was messy). Notes kept in archive/TODO.md (OD-5).
- **Source:** archive/TODO.md 2026-10-23.

## D-033 · 2026-10-22 · Scope and claims fixed for the mid report
- **Decision (team, "final"):** processing time reported as measured (~75 min, RTX 3070); FYP-2 target < 35 min on an
  RTX 4090, labelled a projection; accuracy target 5%; v6 (26.52 / 0.8886) is the headline; 27.81 dB only as the
  splatfacto-vs-own-trainer result; second room SSIM 0.91 / 1%; **MEP / material semantic segmentation removed, replaced by
  the structural layer**; **X-ray dropped**; 3D mesh creation in scope; Iteration 1 = "core pipeline complete, refinement
  ongoing"; exactly two supervisor meetings, no claimed approvals; tests reported only as executed; commit counts reflect
  commit granularity, not effort; never invent a number.
- **Source:** [report/mid-eval/report-fix-notes/REPORT_FIX_BRIEF.md](../../report/mid-eval/report-fix-notes/REPORT_FIX_BRIEF.md). **By:** team.

## D-034 · 2026-10-12 → 10-18 · Processing server design
- **Decision:** FastAPI server (`server/main.py`) runs pipeline steps as subprocesses with per-step timeouts; modes
  `local`, `runpod`, `remote` (SSH to a friend's GPU), `dry_run` (default); RunPod pods are always terminated in a
  `finally`, plus a lifetime watchdog; the API never returns the RunPod key; `.env` is untracked (`.env.example` template, 2026-10-22).
- **Differs from the proposal:** no Redis / Node queue (OD-2). **By:** Umair (commits). **Source:** docs/PROCESSING_GUIDE.md, archive/TODO.md.

## D-035 · 2026-10-19 · Prebuilt GPU Docker image for RunPod
- **Decision:** `docker/Dockerfile.gpu`, built and pushed by `.github/workflows/docker-gpu.yml` as
  `umairishuman/buildscan-gpu:latest`, to skip ~5 min of setup per pod. **Status:** outdated vs the current pipeline (STATUS §6).
- **By:** Umair (commit 70001af).

## D-036 · 2026-10-10 → 10-18 · CI/CD and branch workflow
- **Decision:** GitHub Actions CI on every branch / PR (ruff errors, pytest with a 40% coverage gate, web build, APK
  build + signing with a shared debug key + manifest checks, repo hygiene, actionlint); CD on `master` (artifacts,
  `latest` pre-release, tagged releases, auto-versioned APKs). `master` is stable; work on `feature/`, `fix/`, `exp/`,
  `ci/`, `docs/` branches and merge by PR.
- **By:** Zaid (CI/CD, tests), Umair (CD auto-versioning). **Source:** docs/CI_CD.md.

## D-037 · 2026-11-06 · Three Python environments
- **Decision:** system Python 3.10 (`requirements-system.txt`: driver, COLMAP wrappers, Metric3D), `nerfstudio-env`
  (`requirements.txt`), `semantic-env` on the system torch (`requirements-semantic.txt`, transformers pinned 4.46.3).
- **Why:** Metric3D, nerfstudio and transformers need incompatible versions on torch 2.1.2. **Source:** requirements files, README.

## D-038 · 2026-10 · Environment fixes on the RTX 3070 PC
- Open3D 0.19 for TSDF (0.20 returns empty meshes); prebuilt gsplat module + loader shim (no 15-min recompiles);
  viewer on port 7010 (Steam owns 8080); nerfstudio pin-memory patch above 4 GB; `PYTHONUTF8=1`. **Source:** P&S §6–7, §4.13.

## D-039 · 2026-10-11 · Median filtering only on depth
- **Decision:** a 5×5 hole-aware median on stereo depth (`colmap_mvs.py --median`); never median-filter images (removes
  the texture 3DGS needs). **Why:** tested on the suggestion of the user's uncle; > 25% outliers 3.3 → 2.4–2.7%; no effect on COLMAP depth.
- **Source:** archive/TODO.md 2026-10-11.

## D-040 · 2026-10-11 · No floater pruning by default
- **Decision:** `clean_splats.py` stays optional. **Why:** post-hoc pruning made every model worse (−0.3 to −1.6 dB;
  with filled-depth evidence it deleted real surfaces). Removing near-camera splats *during* training (`--near_cam`) helped
  the own trainer. **Source:** P&S §4.6, archive/TODO.md.

## D-041 · 2026-10-09 · MCMC densification off
- **Why:** unstable (photo error rose to 0.16–0.23) and overflowed VRAM at 3.5M splats. **Source:** P&S §4.4.

## D-042 · 2026-10-12 · Exposure lock not pursued — Parked
- **Why:** not possible through the normal ARCore session API (needs the Shared Camera API); the bilateral grid already
  absorbs exposure changes. **Source:** archive/TODO.md.

## D-043 · 2026-10-12 · Folder clean-up — Superseded by D-044
- `.bat` launchers to `scripts/`, proposal docs to `docs/proposal/`, progress docs to `docs/progress/`, `docs/Flow.md` added.

## D-044 · 2026-11-06 · Project records and folder organisation
- **Decision:** four maintained records in `docs/progress/`: `STATUS.md` (done + left; absorbs `TODO.md`),
  `DECISIONS.md`, `LOG.md`, `TRAINING.md` (every run and every error during it). `Problems_and_Solutions.md` stays as the
  detailed technical reference. Unused files go to `docs/progress/archive/` (old `TODO.md`, `Training_Analysis.md`,
  `FYP Problems Faced.docx`, `To Dos and some future Plans.docx`); `TODO.md` and `Training_Analysis.md` leave one-line
  pointers because the mid report cites them. All mid-evaluation material moves to `report/mid-eval/`. Logging rules and
  per-member preferences live in `CLAUDE.md`.
- **Why:** the old organisation mixed task lists, history and run notes; the team needs one flow everyone follows.
- **By:** Umair. Work on branch `docs/project-organisation` (off `feature/semantics-mesh`).

## D-045 · 2026-11-06 · Target machines; Docker not installed on this PC yet
- **Decision:** the pipeline must work on this PC (Ubuntu, RTX 4000 Ada), a friend's PC and RunPod. Docker is not to
  be installed on this PC for now; updating the image's dependencies is a to-do. **By:** Umair.

## D-046 · 2026-11-06 · Umair's next focus
- **Decision:** semantic labelling, after the organisation work; processing-time optimisation added as a priority to-do. **By:** Umair.
- **Updated by D-047:** the setup of this PC and the Docker rebuild come first.

## D-047 · 2026-11-06 · Set up this PC first, with the same versions, in conda envs
- **Decision:** step 1 is getting the pipeline running on this Ubuntu PC (RTX 4000 Ada); the Docker image comes after.
  Use the **same versions as the RTX 3070 PC** (Python 3.10, torch 2.1.2 + cu121, nerfstudio 1.1.5, gsplat 1.4.0,
  Open3D 0.19, transformers 4.46.3) in **micromamba / conda envs** that also provide CUDA toolkit 12.1, gcc 11, ffmpeg
  and Node.js. Only the NVIDIA driver is installed system-wide (Umair, with sudo). Plan: STATUS §7.1 step 1.
- **Why:** this PC has Python 3.14, no compiler and no CUDA toolkit, and gsplat / tiny-cuda-nn compile CUDA code
  that needs a gcc CUDA 12.1 accepts. Equal versions keep results comparable with the 3070 PC. The conda recipe also
  becomes the Docker recipe.
- **Rejected:** uv + system CUDA and gcc from apt (needs sudo, and Ubuntu 26.04's gcc is likely too new for CUDA 12.1);
  upgrading the stack on Linux (easier install, but the two machines would diverge and every result would need re-checking).
- **By:** Umair.

## D-048 · 2026-11-06 · One setup script for every machine and the Docker image
- **Decision:** the setup of this PC is written as a script plus env files (`scripts/setup_linux.sh`, planned); the
  friend's PC runs it, and the new `docker/Dockerfile.gpu` runs the same script.
- **Why:** dependencies are written down in one place, so this PC, the friend's PC and RunPod get identical environments;
  the old image drifted from the pipeline because it was maintained separately.
- **Rejected:** a separately written Dockerfile. **By:** Umair.

## D-049 · 2026-11-06 · Reorganise in two steps; never delete, archive
- **Decision:** step 1 now: `MAP.md` with status markers for every file; unused files are **archived, never deleted**
  (`git mv` into an archive / legacy folder with a note), once their owner agrees. Step 2, after the pipeline runs on
  Linux: regroup `src/arcore3dgs/` by stage (proposal in MAP.md §10) on its own branch, verified with a real run.
- **Why:** moving code changes script paths in `run_v8.py`, imports, the server, launchers and tests; with no working
  GPU setup here, moves could only be checked by CI. Umair: "deleting never ends well".
- **Rejected:** regrouping the code now; keeping the flat layout with a map only. **By:** Umair.

## D-050 · 2026-11-06 · `MAP.md` is the first read
- **Decision:** a root `MAP.md` says what is where and what every file does (status markers v9 / eval / v3 / legacy / exp /
  dead); every session (person or agent) reads it first, then CLAUDE.md and STATUS.md. Whoever adds, moves or retires a
  file updates MAP.md in the same commit. **By:** Umair.

---

## D-051 · 2026-11-06 · Merge the v9/v10 work and the organisation into `master`
- **Decision:** one PR from `feature/linux-port` into `master`, which brings in `feature/semantics-mesh` (Tayyab's v9 + v10,
  5 commits), `docs/project-organisation` and the Linux port (22 commits, no conflicts: none of the branches is behind
  `master`). Merge method: merge commit, so every small commit stays revertible. CI must pass first (CLAUDE.md §4).
- **Why:** `master` (2026-10-23) had neither v9 nor v10 nor the new records. Settles OD-3. **By:** Umair; Tayyab informed.

## D-052 · 2026-11-06 · Delete only fully merged branches
- **Decision:** after the merge, delete the branches whose every commit is in `master` (local and on GitHub); never a
  branch with unmerged commits (Zaid's `feat/splat-compress` and `exp/trainer-arkitscenes` stay). Deleting a merged
  branch loses nothing: its commits live in `master`. **By:** Umair.

## D-053 · 2026-11-06 · This PC stays awake; remote access by Tailscale
- **Decision:** GNOME auto-suspend on AC turned off (`sleep-inactive-ac-type 'nothing'`; the timeout was already 0 =
  never). Remote access from Umair's laptop by Tailscale (SSH over the tailnet), to be set up with Umair's sudo; long
  runs inside `tmux` / `screen`. Other lab PCs have the same home directory `/home/i230662` when access is given, so the
  setup can also be copied between them. Screen lock after 5 min idle kept on purpose (lab PC; locking does not stop runs or Tailscale). Remote power-on: **not set up** — Umair has no BIOS access (needed for Wake-on-LAN or Intel AMT); instead the PC is
  left switched on, which Umair asked the lab about (2026-11-06). Options kept in STATUS §7.1. **By:** Umair.

## D-054 · 2026-11-06 · Coverage gate 40% → 35%, temporarily
- **Decision:** `ci.yml` `--cov-fail-under=35` (was 40); docs/CI_CD.md updated. Back to 40% once the tests are written
  (planned for the end of the project).
- **Why:** `master` itself has failed the 40% gate since 2026-10-19 (38%), so CD has published no APK / web bundle since
  then; the PR #1 merge brings it to 37.4% (`sfm_colmap.py` +45 untested lines from v9). 35% leaves headroom while
  still catching a real drop. **Rejected:** writing the missing tests now; merging with CI red. **By:** Umair.

## D-055 · 2026-11-06 · Unused `newroom_v6.spz` out of git
- **Decision:** `prototype/web-ui/public/splats/newroom_v6.spz` (12.5 MB, added in `6d0cab5`) is no longer tracked; the
  unused `splatUrl` line is gone from `mockData.ts`. Local copy: `saved_models/web/newroom_v6.spz` (Ubuntu PC). Git
  history still has it (never-delete rule, D-049).
- **Why:** CI's 10 MB file limit; the viewer loads `newroom-scan` from the labelled bundle `/scans/newroom/` and never
  read this file. **Rejected:** exempting `public/splats/` from the limit; Git LFS. **By:** Umair.

## D-056 · 2026-11-06 · The repository stays public
- **Decision:** `Umairishuman/BuildScan3D` stays public. The RunPod key that commit `00bc021` exposed was revoked by Umair
  the same day; secrets go only in the untracked `.env` (`.env.example` is the template). docs/CI_CD.md no longer
  calls the repo private. Removing the revoked key from history is optional (STATUS §7.1). **By:** Umair.

## D-057 · 2026-11-06 · Linux upload server in its own env, `dry_run` by default
- **Decision:** on Linux the phone-upload server runs from `scripts/start_server.sh` in a small micromamba env
  `bs-server` (Python 3.10 + `server/requirements.txt`), not in the pipeline envs; mode defaults to `dry_run`. The
  server logs each device that connects, uploads while they arrive (progress, cut off), and every failed request.
- **Why:** Umair asked for a separate small env or venv and for upload / error / device messages in the server
  terminal. A venv is not possible without sudo (system Python 3.14 has no `ensurepip`).
- **Rejected / deferred:** a venv (needs `sudo apt install python3-venv`); a pipeline env; Docker for the server
  (asked by Umair; deferred, Docker is not installed on this PC for now, D-045, STATUS §7.1). **By:** Umair.

## D-058 · 2026-11-06 · App package name `com.buildscan3d.app`
- **Decision:** the Android `applicationId` changes from Google's sample name `com.google.ar.core.examples.java.helloar`
  to `com.buildscan3d.app`. The Java package / Gradle `namespace` stay as they are for now (moving the code is part of
  the D-049 reorganisation).
- **Why:** Android warns the APK "may be dangerous" on install; an app using Google's own sample package name is
  a main reason Play Protect flags it. **Cost:** Android sees a new app: it installs **next to** the old one (no
  uninstall needed); recordings made in the old app stay in the old app until it is uninstalled, which deletes them
  (upload them first). **Rejected:** keeping the name. **By:** Umair.

## D-059 · 2026-11-06 · Release APKs signed with a private key
- **Decision:** CD signs release APKs with a new private release key, stored only as GitHub Actions secrets (and a
  backup copy kept by Umair). `.github/android/debug.keystore` (public password) stays for the CI check builds of pull
  requests only, which are not distributed.
- **Why:** with the key and its password public in the repository, anyone can sign an APK that installs as an update
  of ours; a public debug key also adds to Play Protect's warning. **Risk:** losing the key means phones cannot update
  to new builds (uninstall needed again). **Rejected:** keeping the public key. **By:** Umair.

## D-060 · 2026-11-06 · App fixes ship through PR → merge → CD release
- **Decision:** the app fixes (server discovery, in-app updates, D-058, D-059) go on `fix/android-app`, through a pull
  request with CI green, merged into `master`; CD then bumps the version and publishes the APK on GitHub Releases.
- **Rejected:** also building locally first (would need JDK + Android SDK on this PC); PR only with Umair merging.
  **By:** Umair.

## D-061 · 2026-11-12 · Per-run web bundles stay out of git
- **Decision:** `prototype/web-ui/.gitignore` ignores `public/scans/scan_*/`, the bundle the `web` stage of
  `scripts/run_full.sh` writes for every run (`<scan>_<tag>/`, ~20 MB each). Only demo bundles that are picked on purpose,
  such as `public/scans/newroom/`, are tracked; a scan is shown in the dashboard by adding it to `mockData.ts`.
- **Why:** each run added an untracked ~20 MB folder (R-029 `scan_056fe94d3399_umair/`, the unrecorded `r1106` run
  `scan_646070948603_r1106/`); no single file passes CI's 10 MB limit, so one could be committed by mistake.
- **Rejected:** `export_web.py` writing to `saved_models/web/` instead and copying demos by hand; committing every bundle
  (~20 MB of repo growth per scan). **By:** Umair.

## D-062 · 2026-11-12 · Uploads over a USB cable, preferred over Wi-Fi
- **Decision:** the app uploads over a USB cable when one is connected: `scripts/usb_link.sh` (started by
  `scripts/start_server.sh`) keeps `adb reverse tcp:8000 tcp:8000` set while a phone is plugged in, and the app's
  `ServerLink` tries `http://127.0.0.1:8000` before the saved and recent Wi-Fi servers. The Scans screen shows the route
  (USB / Wi-Fi / not connected, with the reason), uploads show MB/s and time left, fail within 30 s when the link drops,
  and restart by themselves up to 3 times.
- **Why:** on 2026-11-12 uploads ran at ~1.4 MB/s on the lab Wi-Fi (772.5 MB recording, ~9 min) and ~1 MB/s on the
  phone hotspot (PC Wi-Fi signal −76 dBm); the PC's address changed four times that day, so the app kept losing the
  server; the app's write timeout of 10 min hid dropped connections.
- **Rejected:** resumable (chunked) uploads (server change, later if needed); a fixed IP from lab IT (not in our
  control); asking the user to pick USB by hand. **By:** Umair.

## D-063 · 2026-11-12 · The capture app lives in `android/` with its own Java package
- **Decision:** the app moved from `googleARCore/samples/hello_ar_java/` to `android/` (`git mv`, history kept), Java
  package `com.buildscan3d.app` (was Google's `com.google.ar.core.examples.java.helloar`), `HelloArActivity` renamed
  `CaptureActivity`, Google's helpers under `com.buildscan3d.app.common`. CI, CD, `scripts/release.bat`, the APK
  expectations and the manifest test follow the new path; `googleARCore/samples/hello_ar_java/MOVED.md` points to it.
  `applicationId` stays `com.buildscan3d.app` (D-058), so installed apps update in place.
- **Why:** asked by Umair on 2026-11-06 ("the app UI is hard to find", STATUS 7.7) and again on 2026-11-12 ("give
  the folder proper structure"); MAP §10 had planned it. **Evidence:** CI green after the move (Android build + APK
  checks + Python tests, run 43189543479).
- **Rejected:** `app/android/` (MAP §10's example; one level deeper for no gain); sub-packages per feature (several
  classes share package-private constants, so a split needs more refactoring than it is worth now). **By:** Umair.

## D-064 · 2026-11-12 · App UI: light theme from the logo, bottom navigation, checked and stoppable uploads
- **Decision:** the app uses a light theme taken from the logo and the web UI (AGENTS.md §2): background `#F8FAFC`, white
  cards, primary `#2563EB`, navy `#1B4B8A`, text `#0F172A` (`res/values/colors.xml`); the logo is in the screen headers
  and on the capture screen. Bottom navigation Capture / Scans / Server (hidden while recording); a new Server tab
  (connection, USB steps, Wi-Fi address with save-and-test and search, updates) replaces the server dialog. Before an
  upload the app checks the recording's files, then the connection: no server -> it asks to connect the USB cable or
  the Wi-Fi; Wi-Fi only -> it offers the cable first; then the progress bar starts. Uploads can be stopped (Scans tab
  and processing screen).
- **Why:** asked by Umair on 2026-11-12; the dark sample UI did not match the brand, and the slow, dropping Wi-Fi
  uploads of that day (D-062) needed the user to be told what to connect before an upload starts.
- **Rejected:** Material `BottomNavigationView` (would need a newer Material library than the app's 1.1.0); keeping the
  server dialog on the capture screen. Not tested on a device yet. **By:** Umair.

## D-065 · 2026-11-12 · Recordings are numbered 1, 2, 3 in the order they arrived
- **Decision:** every recording in `dataset/` has a fixed number, kept in `dataset/.scan_numbers.tsv`
  (`server/scan_numbers.py`). New uploads are saved as `scan_<NNN>_<id>` (e.g. `scan_004_6de634cbb8b2`) and the
  server answers with the number; the app shows it ("Saved on the PC as scan #4", badge "UPLOADED #4"). The three
  earlier recordings keep their folder names and are #1 `scan_056fe94d3399`, #2 `scan_646070948603`, #3
  `scan_6de634cbb8b2` (arrival order). `scripts/buildscan` lists the numbers and accepts them (`run 4 mytag`); `latest`
  is the highest number. Folders copied in by hand get the next number on first sight.
- **Why:** asked by Umair on 2026-11-12, to see which recording is the latest. The folder names were random ids, and
  `buildscan` picked "latest" by folder date, which every processing run changes (an old recording became "latest"
  after being processed).
- **Rejected:** renaming the three earlier folders (TRAINING.md R-028 to R-030 and the web bundles use those names);
  numbering by date at display time only (a copied-in or processed folder would shift the numbers). **By:** Umair.
- **Status:** the "keep the old names" part superseded by D-066 the same day.

## D-066 · 2026-11-12 · The three earlier recordings renamed with their numbers
- **Decision:** `scan_056fe94d3399` → `scan_001_056fe94d3399`, `scan_646070948603` → `scan_002_646070948603`,
  `scan_6de634cbb8b2` → `scan_003_6de634cbb8b2`, so every folder in `dataset/` starts with its number. The folder paths
  stored in the working files (`frames.json`, COLMAP `project.ini`, `semantic.json`, `mesh_*.json`) were updated; the
  run logs were left as written. Web bundles renamed to match (`scan_001_056fe94d3399_umair`,
  `scan_002_646070948603_r1106`). TRAINING.md and LOG.md keep the old names (history) with a note.
- **Why:** asked by Umair (2026-11-12) after D-065. **Checked:** `buildscan results 1 umair` finds the model; no old
  path left in the working files. **By:** Umair.

## D-067 · 2026-11-12 · Close the stale ARCore depth bug (COMPLETION_PLAN 1.7) as not reproduced
- **Decision:** the "ARCore depth was stale" item (newRoomAttemptSadness, 2026-10-10) is closed without a code fix.
- **Why:** the newest recording does not show it, and the old recording is on the RTX 3070 PC only.
- **Evidence:** scan #3 (`scan_003_6de634cbb8b2`, Infinix X6833B, app v0.3.5, R-031): 782 depth maps (160 × 90,
  4.2 / s), all 782 different (MD5), median valid fraction 0.86–0.87, median depth 0–5.5 m across maps, mean confidence
  0–81. In newRoomAttemptSadness (realme RMX5111, older app) every map was identical, median 9.3 m, confidence ≈ 0
  (R-007). The cause was not found; it was the other phone, the older app, or both.
- **Rejected:** investigating further on newRoomAttemptSadness now (needs the 3070 PC, Should-priority, no current
  recording shows it); turning depth off for this reason (1.12 stays open, decided on the NFR1 numbers instead).
- **If it comes back:** `check_capture.py` warns when depth maps are invalid; reopen this item.
- **By:** Umair · **Source:** session 2026-11-12, agent check of scan #3 · **Status:** Active

## Open decisions (need the team; agents must not decide these)

| # | Question | Context |
|---|---|---|
| OD-1 | `.spz` (in the viewer now) or `.ksplat` (proposal, Zaid's `feat/splat-compress`)? | `.spz` 148 → 12.5 MB; `.ksplat` v2-A 40 MB visually lossless, v1 18 MB with a small loss |
| OD-2 | Keep the FastAPI + thread server, or build the proposal's Redis / Node queue (FR4)? | Proposal CCP claim 5 ("beyond standard practice") cites the queue |
| ~~OD-3~~ | ~~When to merge `feature/semantics-mesh` into `master`?~~ | Settled by D-051 (2026-11-06) |
| OD-4 | Merge, keep or close `origin/feat/splat-compress` and `origin/exp/trainer-arkitscenes`? | Both by Zaid, unmerged |
| OD-5 | Re-implement any of the app overlay features reverted on 2026-10-23? | Notes in archive/TODO.md; the patch is lost |
| OD-6 | Should the v9 pipeline use the IMU fallback (the stated novelty)? | SfM now registers 1165/1166 frames on newRoom |
| OD-7 | Server / RunPod: wire in the v9/v10 pipeline? | The image's torch / CUDA base is settled by D-047 / D-048 (same versions, same script) |
| OD-8 | Archive (never delete, D-049) `train_fixed2_backup.py`, `train_v3_backup.py`, the old `run_*.bat`, `scratch/`, `ViewerHUD.tsx`? Into which folder? | Owners must agree |
| OD-9 | Update README / AGENTS.md content that no longer matches (MEP layers, ~75 min, `structure.py`)? | Facts changed by D-023, D-024, D-033 |
