# BuildScan3D: Training and Processing Run Log

**Purpose.** One entry for every processing or training run (local, friend's PC, RunPod, Kaggle), and **every error
that happens during that run**: crashes, OOMs, hangs, wrong outputs, environment problems, and how each was fixed or
worked around. Write to it during the run, not afterwards from memory. A run that failed still gets an entry.
Rules for all team members and agents: [CLAUDE.md](../../CLAUDE.md). Why a recipe was chosen goes in
[DECISIONS.md](DECISIONS.md); deep analysis goes in [Problems_and_Solutions.md](Problems_and_Solutions.md).

## How to add a run

Copy the template below to the **end** of "Runs" with the next run ID (`R-NNN`). Fill in the header before starting,
add errors as they happen, fill in the result at the end, and add a one-line row to the index.

```markdown
### R-NNN · YYYY-MM-DD · <short name, e.g. v9 room 2 full pipeline>
- **Who / machine:** <name> · <RTX 3070 PC | this PC (Ubuntu, RTX 4000 Ada) | friend's PC | RunPod <GPU> | Kaggle>
- **Branch / commit:** <branch> @ <short hash> (uncommitted changes: yes/no)
- **Dataset:** <capture name> (<frames>, <length>)
- **Command(s):** `<exact command lines>`
- **Goal:** <what this run should show, what it is compared against>
- **Start → end:** HH:MM → HH:MM (<total min>), stage times: <select / SfM / prior / init / train / export>
- **Errors during the run:**
  1. HH:MM <stage> — <exact error message or symptom> → cause: <...> → fix / workaround: <...> (resolved: yes/no)
- **Result:** <output folder>; <metrics: PSNR / SSIM / sharpness / flatness / room size / fixtures>
- **Verdict:** <kept / rejected / inconclusive> — <one line why>; decision → D-xxx if one was made
```

## Run index

Backfilled on 2026-11-06 from Problems_and_Solutions.md (P&S), the old TODO ([archive/TODO.md](archive/TODO.md)) and
branch notes: those runs were not logged at the time, so commands and exact times are only given where the sources
have them. All backfilled runs were on the Windows RTX 3070 PC (8 GB) unless stated.

| Run | Date | Name | Machine | Time | Result | Verdict |
|---|---|---|---|---|---|---|
| R-001 | 2026-10-06 | roomAttemptSadness own trainer v1–v3 (7k steps) | 3070 | 5–8 min train | v3: colour-fit 21.37 dB, SSIM 0.769; floaters 10.7 → 7.4% | Superseded |
| R-002 | 2026-10-09 | roomAttemptSadness2 `gs`, `gs_fixed`, `gs_fixed2` | 3070 | — | train-view 21.36 → 22.97 → 23.60 dB | Superseded |
| R-003 | 2026-10-09 | Overfit / capacity tests (20 / 100 frames) | 3070 | — | 31.15 / 26.81–28.15 dB | Diagnosis |
| R-004 | 2026-10-10 | `gs_v4` own trainer new recipe vs splatfacto on same inputs | 3070 | — | held-out 24.70 vs **27.81 dB** | Splatfacto adopted (D-010) |
| R-005 | 2026-10-10 | `gs_pocket8k` PocketGS-style prior | 3070 | 12.7 min train | coherent off-path, softer | Default, then superseded |
| R-006 | 2026-10-10 | ARKitScenes 47333462 trainer experiments (Zaid) | Kaggle T4 | 8.6 + 1.3 min prep | depth target alone no gain; fading losses +0.8 dB | Branch only |
| R-007 | 2026-10-10 | newRoom `gs_final`, `gs_measured`, `gs_sparse` | 3070 | ~1 h 50 processing; 22 min | geometry median 6.9 / 5.2 / 1.9% | Superseded |
| R-008 | 2026-10-11 | COLMAP PatchMatch depth (`colmap_mvs.py`) + `gs_colmap`, `gs_colmap_nc` | 3070 | ~2 h MVS; 17 / 28 min | best 22.67 dB / 0.782 | Superseded by SfM |
| R-009 | 2026-10-11 | SfM v1, v2b, **v3** (newRoom) | 3070 | ~75 min e2e | v3 25.57 dB / 0.857, 0.59% geometry | v3 kept (D-014, D-015) |
| R-010 | 2026-10-11 | v3 recipe on roomAttemptSadness2 | 3070 | — | SSIM 0.912, geometry 0.45% | Validated |
| R-011 | 2026-10-11 | splatfacto-big thresholds | 3070 | died ~step 12.5k | CUDA OOM | Rejected |
| R-012 | 2026-10-12 | Overnight v4_sharp, v5, **v6** | 3070 | ~4 h e2e (PatchMatch 2 h 15) | v6 26.52 / 0.8886 | v6 kept (D-018) |
| R-013 | 2026-10-21 | v7 fast pipeline | 3070 | 24 min 56 s | 24.83 / 0.848 | Rejected (D-020) |
| R-014 | 2026-10-24 | v8 ablation: R0, v8dash30, v8geo, v8fast15, **v8geofast15**, strong20, mono15 | 3070 | 27.8–69.6 min train | v8geofast15 25.27 / 0.8281 in 30.2 min | Kept (D-021) |
| R-015 | 2026-10-24 | v8geofast15 on all frames → `saved_models/2026-10-24_v8_geofast15` | 3070 | — | priors misaligned (bug found 10-27) | Do not use (D-028) |
| R-016 | 2026-10-24 | `run_v8.py` end to end (v8e2e) | 3070 | 44 min | door wall breaks off-path; 956 frames registered | Rejected |
| R-017 | 2026-10-24 | Metric3D speed test (100 frames) | 3070 | 75 / 39 / 14 s | aligned error 1.8 / 1.8 / 2.0% | fp16 default |
| R-018 | 2026-10-26 | SfM variants: guided, `--bridge`, `--retrieval 20`, ALIKED | 3070 | 9.6 / 24.6 / 21.8 / 33.1 min | retrieval: 1164 frames, 5.8 cm from v6 | Retrieval kept (D-022) |
| R-019 | 2026-10-26 | v9planar, v9fmvs, v9fmvsmono, v9blur | 3070 | 27.7–40.0 min train | see entry | Inputs to D-023 |
| R-020 | 2026-10-26 | **v9e2e** end to end | 3070 | 96 min | 25.16 / 0.8247, flatness 0.77 cm | Kept (D-023) |
| R-021 | 2026-10-27 | v9pgsr | 3070 | 46 min train | 25.09 / 0.8254, sharpness 0.88 | Kept (D-025) |
| R-022 | 2026-10-27 | First all-frames v9 model | 3070 | — | walls 1.9–5.0 cm, "ceiling" 2.42 m | Bug found (D-028) |
| R-023 | 2026-10-27 | Final all-frames v9 + PGSR-lite → `2026-10-27_v9_semantic_pgsr` | 3070 | 46 min (+ rerun after power cut) | best model | Kept |
| R-024 | 2026-10-27 | Semantics v9 (`semantic2d` + `semantic3d`), mesh | 3070 | 7–8 min 2D; seconds 3D; 20 s mesh | 15 fixtures, 13 correct | Kept |
| R-025 | 2026-11-03 | Semantics v10 | 3070 | 38 min 2D | 15/15 correct, 15/17 found | Kept (D-027) |
| R-026 | 2026-11-03 | `.ksplat` compression v1 / v2 (Zaid) | not recorded (software rendering) | — | v1 18.4 MB (−88%), v2-A 40.2 MB (−73%) | Branch only (OD-1) |
| R-027 | 2026-11-06 | Environment setup of this PC (STATUS §7.1 step 1) | this PC (Ubuntu, RTX 4000 Ada) | ~2.5 h | all checks pass; `scripts/setup_linux.sh` | Envs ready; first data run pending |
| R-028 | 2026-11-06 | First Linux run: Umair's room, full v9 + PGSR → semantics → mesh → web | this PC (Ubuntu, RTX 4000 Ada) | stopped after ~5 min | select / SfM / prior OK on Linux | Abandoned (stopped by Umair) |
| R-029 | 2026-11-06 | Umair's own run of the same recording, full pipeline (`--tag umair`) | this PC (Ubuntu, RTX 4000 Ada) | 34.7 min | **first complete run on Linux**; corridor end, 0 fixtures, 1 wall | Kept as pipeline test (scene not a room) |
| R-030 | 2026-11-06 | `scan_646070948603` (lab room, 97 s), full pipeline through `scripts/buildscan` (`--tag r1106`) | this PC (Ubuntu, RTX 4000 Ada) | 50.2 min | ran clean; 2 walls, 8 fixtures; **room height 1.50 m looks wrong** | Inconclusive (scale / ceiling not checked) |
| R-031 | 2026-11-12 | scan #3 `scan_003_6de634cbb8b2` (classroom, first v0.3.6 recording, 185 s), full pipeline (`--tag r1112`) | this PC (Ubuntu, RTX 4000 Ada) | running | — | — |
| R-032 | 2026-11-12 | Training speed-up: exact TV-loss / colour-affine fixes, blur colour grid once (`fast_t1`) | 3070 | 28.2 min train (was 42.5) | 25.14 / 0.8251, sharp 0.80, flat 0.81 | Kept (proposed) |
| R-033 | 2026-11-12 | Photometric-only fast-MVS init (`fast_t2_photo`) | 3070 | init 7.5 min (was 20.1) | 25.16 / 0.8240, flat 0.78 | Kept (proposed) |
| R-034 | 2026-11-12 | Global mapper settings (`ba1`, `noretri`, default rerun) | 3070 | mapper 9.4 – 14.5 min | default runs differ by ~16 cameras | Inputs to R-035 |
| R-035 | 2026-11-12 | Fast pipeline end to end incl. `--skip_retriangulation` (`v10fast`) | 3070 | 61.6 min (was 96.2) | 24.56 / 0.8078, visible smears | Rejected (SfM shortcut) |
| R-036 | 2026-11-12 | New room `scan_3028a4de8fa0` (tiered lecture hall), normal SfM + speed-ups | 3070 | 48.8 min | fits training views; mini room inside the room (SfM scale collapse, see R-037) | Rejected |
| R-037 | 2026-11-12 | `scan_3028a4de8fa0`: incremental mapper instead of GLOMAP (fix R-036 mini room) | 3070 (CPU) | map 25.4 min | 581/842 frames in one correctly scaled model; front of room split off | Diagnosis confirmed |
| R-038 | 2026-11-12 | `scan_3028a4de8fa0`: fast recipe on R-037's 581-frame SfM (`v10inc`) | 3070 | 35.8 min (+ map 25.4, R-037) | no mini room; right-side walk missing | Kept |
| R-039 | 2026-11-14 | roomAttemptSadness2: full v9 + PGSR → semantics → mesh → web (`v9pgsr8`) | 3070 | 87.7 min to the model + 32 min after | height 2.78 m; 22 fixtures (unchecked) | Kept (fixtures to check) |
| R-040 | 2026-11-14 | newRoom: MCMC densification at the baseline budget (`mcmc620`) | 3070 | 35.0 min train | 24.65 / 0.8216, sharpness 0.64 (softer) | Rejected |
| R-041 | 2026-11-14 | newRoom: Fast training + PGSR-lite on newRoom (`pgsrfast`) | 3070 | 33.0 min train (R-021: 46) | 25.02 / 0.8232, sharpness 0.87 | Speed-ups OK with PGSR (R-021 flatness 1.27 vs 1.34 cm) |
| R-042 | 2026-11-14 | newRoom: MCMC with a larger budget (`mcmc1m`) | 3070 | 40.4 min train | 24.74 / 0.8200, sharpness 0.69 | Rejected |
| R-043 | 2026-11-14 | newRoom: revised opacity on clone / split (`revop`) | 3070 | 28.5 min train | 25.02 / 0.8244, flat 0.73 cm, −10% size | Inconclusive |
| R-044 | 2026-11-14 | newRoom: lower densification threshold (`dg4`) | 3070 | 30.8 min train | 25.07 / 0.8243, sharpness 0.85, +40% size | Inconclusive |
| R-045 | 2026-11-15 | scan_009_057ed3beb4fc: full v9 + PGSR pipeline (`v9pgsr`), capture failed check_capture | 3070 | 32.4 min to the model; layout crashed | 87 / 5,629 frames registered, partial, scale unreliable | Rejected (record again) |
| R-046 | 2026-11-15 | scan_009_057ed3beb4fc: pose-free keyframes + SfM tests; ALIKED SfM model (`v9pf`) | 3070 | 34.0 min from export (train 25.1) | 535 frames over the whole walk (R-045: 87); misplaced cameras remain, scale unreliable | Inconclusive |
| R-047 | 2026-11-18 | scan_009: R-046's ALIKED model with the gyro rotation check (`--gyro_thr 2`, `v9pfg`) | 3070 | 32.2 min from export (train 25.3) | 370 frames; path jumps 51 → 21; +1.0 dB on common training views (not held out); jumps and shrunken blocks remain | Inconclusive |
| R-048 | 2026-11-18 | scan_009: incremental mapper on R-046's ALIKED matches + gyro check (`v9pfm`) | 3070 | 73 min SfM (stopped before training) | 684 frames in one component but locally wrong (IMU \|g\| 1.9); ARCore Sim3 182 broke the jump filter | Rejected |
| R-049 | 2026-11-18 | scan_009: SfM export only, gyro check + placing unplaced frames with gyro rotation + known-rotation fit (`v9pfp`) | 3070 (CPU) | ~1.5 min | 157 of 442 placed, 90 kept; 476 frames; path jumps 40 (R-047: 21) | Inconclusive |
| R-050 | 2026-11-18 | scan_009: diagnosis of the SfM failure (IMU scale per window, gyro pair test, short-range mapping, ARCore vs gyro) | 3070 | ~55 min | SfM locally wrong in both mappers; not wrong matches, not timing; ARCore poor (gyro corr 0.34); IMU clean | Diagnosis |
| R-051 | 2026-11-18 | scan_009: gyro-rotation + accelerometer SfM (`rot_sfm.py`, `v9pfr`) | 3070 | 30.0 min from export (train 22.8) | 698 frames, 23,508 points at 1.76 px; −1.9 dB vs R-047, blurrier; scale ~2–3× too large | Rejected |
| R-052 | 2026-11-19 | scan_009: R-051's poses refined by BA with gyro / accelerometer priors (`prior_ba.py`, `v9pfb`) | 3070 | ~78 min (two trainings) | 698 frames, reprojection 1.77 → 1.22 px, gyro kept (2 frames > 2°); +0.49 dB vs R-051; ≈ R-047 (mean 19.30 vs 19.31), loop not closed | Kept (coverage) |
| R-071 | 2026-11-19 | scan_009: loop closure (gyro bias from far-apart pairs, rot_sfm with all pairs, prior BA; `v9pfl`) | 3070 | 55 min | 680 frames, loop closed (> 120 s pairs 15.6° → 3.5°), scale check ok; PSNR ≈ R-047 / R-052; scale ~2× too large (not applied) | Kept (most complete) |
| R-072 | 2026-11-19 | newRoom: validation of the R-071 recipe against the trusted SfM path | 3070 | 34 min | position error median 72 → 31 cm (p90 166 → 68 cm), scale 0.89; still far worse than normal SfM | Validation |

## Runs

> **Renamed 2026-11-12 (D-066):** `scan_056fe94d3399` is now `dataset/scan_001_056fe94d3399`, `scan_646070948603` is
> `dataset/scan_002_646070948603`. The entries below keep the names they had when they were run.

### R-001 · 2026-10-06 · roomAttemptSadness, own gsplat trainer v1–v3
- **Pipeline:** `prepare.py → ba.py → mvs.py → align_fuse.py --depth_dir depth_mvs → train.py` (7k steps).
- **Command (v3):** `nerfstudio-env\Scripts\python.exe -W ignore -u src/arcore3dgs/train.py --work dataset/roomAttemptSadness/work --out dataset/roomAttemptSadness/work/gs_v3 --steps 7000`
- **Errors / problems:** training ran 10× slower when the viewer was open (8 GB VRAM exceeded) → close the viewer first;
  gsplat recompiled ~15 min on most launches → prebuilt module + shim; nearest-neighbour init hung (`cdist` on 300k
  points overflowed VRAM) → scipy `cKDTree`; output appeared only at the end → `python -u`; two power outages killed
  long jobs → checkpoints every 1000 steps and cached stage outputs (P&S §5.2, §6).
- **Result:** free-space floaters 10.7 → 7.4%; colour-fit PSNR 21.74 → 21.37 dB; SSIM 0.769.

### R-002 / R-003 · 2026-10-09 · roomAttemptSadness2 baseline fixes and capacity tests
- **Problem found:** `diagnose.py` showed the trainer underfits its own training views (21–22 dB), caused by the fused
  TSDF depth target (P&S §4.4).
- **Errors:** MCMC densification unstable (photo error 0.16–0.23) and VRAM overflow at 3.5M splats → off (D-041).
  Learned pose corrections were not exported, so evaluation used slightly wrong poses → `frames_refined.json`.
- **Result:** `gs_fixed2` train-view 23.60 dB; 20 frames fit at 31.15 dB, 100 frames at 26.81 dB (15 steps/frame) /
  28.15 dB (30 steps/frame): capacity-limited on one 3.2M-splat budget.

### R-004 · 2026-10-10 · New recipe in our trainer vs splatfacto (roomAttemptSadness2)
- **Result:** train / held-out colour-fit PSNR: `gs_v4` 26.06 / 24.70 dB; splatfacto on the same BA poses and
  `make_init.py` points 28.08 / **27.81 dB**, sharpness 0.49, thickness/width 0.11, 21% opacity < 0.1.
- **Verdict:** splatfacto becomes the trainer (D-010). Analysis: [archive/Training_Analysis.md](archive/Training_Analysis.md).

### R-005 · 2026-10-10 · `gs_pocket8k` (PocketGS-style prior, 8k steps)
- 342 of 759 frames by the 8 cm / 6° gate; 70% of pixels in the dense prior; 12.7 min training (3k half-res: 2.3 min).
- Coherent off-path, softer than splatfacto at recorded viewpoints. Default then, superseded by D-014.

### R-006 · 2026-10-10 · ARKitScenes trainer experiments on Kaggle (Zaid, `origin/exp/trainer-arkitscenes`)
- **Machine:** Kaggle, Tesla T4 15.6 GB, PyTorch 2.11 / CUDA 12.8. Scene ARKitScenes 47333462 (1805 frames, 640×480).
- **Errors during the run:**
  1. gsplat 1.4.0 compiled its CUDA extension on first use (~25 min) → waited; worked.
  2. Open3D 0.20 (only version Kaggle installs) TSDF returns an empty mesh → ran `align_fuse.py` in a separate
     Python 3.12 env with Open3D 0.19.
  3. Metric3D `torch.hub` asked interactively to trust the repo → crash in a non-interactive run → `trust_repo=True`; also needs `mmengine`.
  4. `mvs.py` crashed: five keyframes had no neighbours, so no depth file, but others listed them as sources → a missing
     file now counts as "no depth" (commit 972ea01).
  5. The stage runner skipped `mvs` after the crash because the output folder already existed → deleted half-finished
     folders by hand; a proper completion marker is still to do.
- **Result:** depth target alone: no measurable difference; 15k steps worse than 7k; weaker fading depth + flatness
  losses +0.8 dB held-out colour-fit PSNR at 7k steps. The old trainer did not underfit on this scene.

### R-007 · 2026-10-10 · newRoomAttemptSadness first models
- Capture checks passed (240 s, 0% tracking loss, sync r = 0.92). Processing ~1 h 50 min.
- **Problems:** ARCore depth was stale in this recording (every map identical, median 9.3 m, confidence ≈ 0) → open app
  bug; 168/592 keyframes had no stereo neighbours (turning on the spot); `mvs.py` crashed when a neighbour frame had no
  stereo sweep → fixed, `--min_votes` added.
- **Result:** geometry median / > 25% off: `gs_final` 6.9% / 25%, `gs_measured` 5.2% / 18%, `gs_sparse` 1.9% / 19% (22 min).
  The error tail sits on the glossy floor and glass table (reflections).

### R-008 · 2026-10-11 · COLMAP PatchMatch depth on fixed BA poses
- `colmap_mvs.py` with COLMAP 4.2 CUDA, PatchMatch 960 px, 12 sources: ~2 h. `gs_colmap` 17 min, `gs_colmap_nc`
  (`--near_cam 0.25`) 28 min: 22.67 dB / 0.782 (best of the ARCore-pose era).
- **Problems:** a large floater on the start viewpoint in `gs_colmap`; post-hoc pruning made every model worse (−1.3 to
  −1.6 dB) → `--near_cam` during training instead; `--near_cam` slow (CPU KD-tree every 100 steps), open.

### R-009 / R-010 · 2026-10-11 · Image-based SfM v1 → v3, and room 2
- `scripts/run_arcore3dgs.bat dataset\newRoomAttemptSadness`: ~75 min (matching 23, mapping 6, training ~45).
- **Problems:** v2b with the SO3xR3 camera optimiser rendered 3–16 px off the photos → optimiser off (D-015).
- **Result:** v1 27.22 / 0.864 (cloudy walls); v2b 24.46 / 0.824 (shifted); **v3 25.57 / 0.857, geometry 0.59%**.
  Room 2: COLMAP registered 748/759, 739 kept, SSIM 0.912, geometry 0.45%. Tape check on v3: mean 4.8 mm.

### R-011 · 2026-10-11 · `splatfacto-big` thresholds
- **Error:** CUDA out of memory at full resolution around step 12.5k (cull 0.005, grad 0.0005) on 8 GB → use default thresholds.

### R-012 · 2026-10-12 overnight · v4_sharp, v5, v6
- `select_sharp.py` (1166 frames) registered into v3's COLMAP model (~16 min, BA 0.97 → 0.88 px, 1108 kept); PatchMatch
  at 1000 px, 8 sources (2 h 15 min; depth maps deleted afterwards, 123 MB) → 1.15M points → `mvs_init.py` ~460k.
- **Errors during the run:**
  1. Nerfstudio pins cached images in page-locked RAM; > 1000 full-res frames (~6.7 GB) → "CUDA error: out of memory"
     on Windows, CUDA context broken → patched nerfstudio-env to skip pinning above 4 GB.
  2. COLMAP PatchMatch caches ~7 GB RAM → never train alongside it on the 16 GB machine.
  3. COLMAP writes PLY headers with `\r\n` → reader handles it.
  4. Untrimmed Sim3 for evaluation gave a 1.5 cm offset (better model looked 3 dB worse) → trimmed Sim3.
- **Result:** v3 26.04 / 0.8756, v4_sharp 26.30 / 0.8849, v5 26.51 / 0.8879, **v6 26.52 / 0.8886** (42 frames).

### R-013 · 2026-10-21 · v7 fast pipeline
- `select_sharp.py --window 12` (592) → `sfm_colmap.py --pairs arcore` (13.3k pairs) → no dense MVS → splatfacto 10k.
  Output `dataset/newRoomAttemptSadness/work_v7_sfm/gs_v7_10000/`.
- **Time:** 24 min 56 s (selection 1:47, SfM 5:15, training ~17 min at ~100 ms/step).
- **Problem:** scored without pose refinement, v7 looked 21.4 dB (misleading) → `fair_compare.py` refines test poses.
- **Result:** 24.83 / 0.848 vs v6 26.45 / 0.883; fine detail and off-path views worse. Rejected by the user.

### R-014 · 2026-10-24 · v8 ablation (79 off-path frames, same SfM)
| Run | Recipe | Train | PSNR(cf) | SSIM |
|---|---|---|---|---|
| R0 | v6 recipe (30k, MVS init) | 64.3 min | 25.13 | 0.8241 |
| v8dash30 | + DashGaussian | 55.5 min | 25.28 | 0.8267 |
| v8geo | + priors 0.05/0.05, 30k | 69.6 min | 25.43 | 0.8272 |
| v8fast15 | DashGaussian, 15k | 27.9 min | 24.82 | 0.8227 |
| **v8geofast15** | priors + DashGaussian, 15k | **30.2 min** | 25.27 | **0.8281** |
| strong20 | priors 0.1/0.2, 20k | 38.1 min | 25.03 | 0.8219 |
| mono15 | v8geofast15 with mono init | 27.8 min | 24.84 | 0.8210 |
- **Profiling:** ~75 ms/step low-res, 110–130 ms full-res, ~20 s start-up; nerfstudio eval passes 2–3 min/run → `--no_eval`.

### R-015 · 2026-10-24 · v8geofast15 retrained on all 1108 frames
- Trained on `transforms_mvs.json` without a split → nerfstudio held out 10% itself → priors on the wrong images
  (found 2026-10-27, D-028). `saved_models/2026-10-24_v8_geofast15/`: **don't use**.

### R-016 · 2026-10-24 · `run_v8.py` end to end (v8e2e)
- 44 min (select 1.7, SfM 9.6, prior 6.2, init 0.1, train 26.0, export 0.6). Output `work_v8e2e_sfm/gs_v8e2e/`.
- **Problem:** guided SfM from scratch registered 956 frames (+20 dropped) vs 1108; the door wall breaks from the room
  centre. Cause: the global mapper split the walk into 2 components (976 + 190), found 2026-10-26.

### R-017 · 2026-10-24 · Metric3D speed (100 frames)
- ViT-L 75 s, ViT-L fp16 39 s, ViT-S fp16 14 s; aligned error 1.8 / 1.8 / 2.0% → fp16 default (1108 frames: 14 → ~6 min).

### R-018 · 2026-10-26 · SfM variants (1166 frames)
| Variant | SfM time | Registered | vs v6: centre / rotation / scale |
|---|---|---|---|
| guided pairs | 9.6 min | 956 (2 components) | 14.2 cm / 3.46° / 0.953 |
| + `--bridge 1` | 24.6 min | 1142 | 8.5 cm / 1.01° / 0.973 |
| + `--retrieval 20` | 21.8 min | **1164 (one component)** | **5.8 cm / 0.52° / 0.981** |
| `--feature aliked` | 33.1 min | 1159 | 74 cm / 15.7° / 0.959 |
- **Errors / setup:** COLMAP's ONNX models need cuBLAS 12 + cuDNN 9 DLLs → `tools/cudnn9` added to PATH by
  `sfm_colmap.py`; COLMAP ≥ 3.12 needs faiss vocabulary trees → `tools/colmap_dl/vocab/`. ALIKED's Sim3 looked fine
  (3.1 cm on inliers) while the trajectory was folded.

### R-019 · 2026-10-26 · v9 component runs (15k, DashGaussian, priors)
| Run | Train | PSNR(cf) | SSIM | flat cm |
|---|---|---|---|---|
| v9planar (+ planar 0.2) | 30.1 min | 25.02 | 0.8241 | **0.85** |
| v9fmvs (fast MVS init) | 27.7 min | 24.88 | 0.8232 | 1.39 |
| v9fmvsmono (fast MVS + mono walls) | 28.0 min | 24.85 | 0.8203 | 1.23 |
| v9blur (+ blur 1/45 s) | 40.0 min | 25.00 | 0.8205 | 1.34 |
- **Error during the run:** the first v9blur run died of **CUDA OOM** because a layout check ran on the GPU at the same
  time → never share the GPU with a `--blur` run (up to 5 sub-renders per step).
- v9blur renders 43% sharper (0.80 vs 0.56); `fast_mvs.py` ~19 min vs 2 h 15 min; `plane_seg.py` ~0.6 s/frame on CPU.

### R-020 · 2026-10-26 · v9e2e end to end
- **Command:** `run_v8.py --tag v9e2e --split <offpath_test.txt> --sfm_args "--retrieval 20" --init fmvs --planar 0.2 --blur 0.0222`
- **Time:** 96 min (select 1.9, SfM 22.4, prior 8.1, fast init 20.4 with plane_seg in parallel, train 42.5, export 0.7).
- **Result:** 1165/1166 frames, poses 5.5 cm / 0.42° from v6; PSNR 25.16, SSIM 0.8247, sharpness 0.80, flatness
  0.77 cm; hardest off-path frame complete. Scale 1.9% smaller than v6 (room 6.617 m vs tape 6.70). `saved_models/2026-10-26_v9_e2e/`.

### R-021 · 2026-10-27 · v9pgsr
- 46 vs 42.5 min training. PSNR 25.09, SSIM 0.8254, sharpness 0.88. Mesh shell flatness slightly better on 4 of 6 surfaces.

### R-022 · 2026-10-27 · First all-frames v9 model (bug)
- **Symptom:** far worse than its held-out twin (walls 1.9–5.0 cm instead of 0.8–3.3, a "ceiling" at 2.42 m, room width
  3.89 m). **Cause:** 1039 of 1049 cameras got another frame's priors (nerfstudio `eval_mode="fraction"`). **Fix:** D-028.

### R-023 · 2026-10-27 · Final model, all 1165 frames, v9 + PGSR-lite
- **Errors during the run:**
  1. **Power cut at 83%**; only the last step was ever saved → `--save_every 2500` + `--resume`, rerun.
  2. A resumed nerfstudio trainer runs `max_num_iterations` *more* steps → resumed runs get only the remaining steps.
  3. `--no_eval` scheduled the first eval at iters + 1; an over-long run cached every eval image (a second copy of all
     frames with `eval_mode="all"`) and stalled → eval off.
- **Result:** `saved_models/2026-10-27_v9_semantic_pgsr/`; layout 6.60 × 4.36 m, ceiling 2.72 m; mesh walls 0.69–1.01 cm
  (0.03–0.34 after denoising); web demo `/scans/newroom/`.

### R-024 · 2026-10-27 · Semantics v9 and meshing
- `semantic2d.py` on every 2nd frame (583): 7–8 min; `semantic3d.py` seconds; `mesh.py` 20 s, 1.9M triangles.
- **Environment problems:** Hugging Face downloads failed behind the TLS-intercepting network → `truststore`; newer
  `transformers` silently disables PyTorch on torch 2.1.2 → pinned 4.46.3; Open3D 0.20 TSDF empty → 0.19.
- **Result:** 15 fixtures; user room check 2026-11-02: 13/15 correct, recall 13/17.

### R-025 · 2026-11-03 · Semantics v10
- `semantic2d.py --every 2 --box_thr 0.28 --tiles 640 --out semantic2d_v10`: 38 min (tiles) → `semantic3d.py` →
  `verify_fixtures.py` → `semantic3d.py --verdicts`.
- **Problem:** the tile pass caused new errors that the fallback rule then repaired.
- **Result:** 15/15 correct, 15/17 found (tuned on the same room).

### R-026 · 2026-11-03 · `.ksplat` compression (Zaid, `origin/feat/splat-compress`)
- Converter: GaussianSplats3D `create-ksplat.js`; sample 596,638 splats, 148 MB, SH 3.
- **Result:** pruned PLY (opacity < 0.05, SH 1) 51.3 MB; `.ksplat` v1 18.4 MB (37.7 / 32.3 / 24.1 dB vs original
  render), v2-A 40.2 MB (63.8 / 55.4 dB, visually identical). Rendered with software graphics; FPS on a real GPU not measured.

### R-027 · 2026-11-06 · Environment setup of this PC (STATUS §7.1 step 1)
- **Who / machine:** Umair (+ Claude) · this PC (`gpu-lab-Precision-3680`, Ubuntu 26.04.1, RTX 4000 Ada 20 GB, compute 8.9)
- **Branch / commit:** `docs/project-organisation` @ b27b1b7
- **Goal:** same versions as the RTX 3070 PC (D-047) in micromamba envs; captured as `scripts/setup_linux.sh` (D-048).
- **Steps and errors during the setup:**
  1. 1a NVIDIA driver (Umair, sudo): `sudo ubuntu-drivers install nvidia-driver-595-open`, reboot → `nvidia-smi`:
     driver 595.99.02, "CUDA Version 13.2" (the newest CUDA the driver supports; CUDA 12.1 wheels run on it), 20475 MiB.
     Secure Boot still enabled and the driver loads. The kernel moved from 7.0.0-42 to 7.0.0-43 over the reboot. No errors.
  2. 1b micromamba 2.10.0 into `~/.local/bin/micromamba`, root prefix `~/micromamba` (no sudo, `.bashrc` untouched).
     **Error:** `tar (child): bzip2: Cannot exec: No such file or directory` — the micromamba download is `.tar.bz2` and
     this PC has no `bzip2` → unpacked with Python's `tarfile` instead. Resolved.
  3. Package check on conda-forge (2026-11-06): COLMAP 4.2.0 exists with CUDA builds `cuda_129` and `cuda_130`; the
     newest 4.2.1 `cuda_134` builds need a CUDA 13.4 driver (ours supports 13.2) and would not run. Chosen:
     **4.2.0 `cuda_129`** (same version as the 3070 PC's `colmap-4.2.0`), in its own env `bs-colmap` because its CUDA
     runtime (12.9) differs from the torch envs (12.1). Also available: cuda-nvcc 12.1.105, gxx 11.4, Python 3.10, Node 22, ffmpeg.
  4. Env files written: `envs/linux/{colmap,nerfstudio,system}.yml`, `envs/linux/requirements-nerfstudio.txt`
     (the Windows freeze minus `msvc_runtime`, `pywinpty`, torch / torchvision, tinycudann; other versions unchanged).
     Conda envs `bs-colmap`, `bs-ns`, `bs-system` being created.
  5. `bs-colmap` created 12:37 → 12:50 (COLMAP 4.2.0 `cuda_129`, ~10 GB of packages incl. CUDA libraries). OK.
  6. **Stall:** `bs-ns` (221 packages, 1 GB) had every package by 12:51 except `libcusparse-12.1.0.106` (113 MB), whose
     download crawled at ~22 KB/s on micromamba's connection (22 MB after 6 min), with no error message. A fresh `curl`
     to the same URL got ~57 MB/s, so the server was fine; one stalled connection. → Stopped the job at ~12:58, removed
     the partial file and the lock files, and restarted with a watchdog that kills and retries `micromamba create` after
     120 s without progress (up to 3 attempts). The restart crawled again (~34 KB/s on the same file), too slow for the
     watchdog to fire. → Downloaded the file with `curl` (113 MB in ~6 s), checked it against the conda-forge sha256
     (`758ca758…a2be3`, OK) and put it in `~/micromamba/pkgs/`; micromamba used it from the cache. Resolved.
     (Side errors of my own: the scratchpad `tools/` folder had been wiped by the reboot, so the first watchdog run found
     no script; `pkill -f <pattern>` also killed its own shell because the pattern was in its command line.)
  7. `bs-ns` and `bs-system` created 13:01 (seconds, all cached). Checked: Python 3.10.22, nvcc 12.1.105, gcc 11.4.0,
     Node 22.23.4, ffmpeg 9.0.2, ninja 1.13.2, cmake 4.4.5.
  8. **Error:** `colmap: error while loading shared libraries: libOpenImageIO.so.3.1: cannot open shared object file` —
     the conda-forge `colmap 4.2.0 cuda_129` build links OpenImageIO 3.1 (+ `libOpenImageIO_Util.so.3.1`) but declares
     only FreeImage, so it was never installed. → Added `openimageio=3.1` to `envs/linux/colmap.yml` and installed it
     (74 packages, 1 changed, 3 downgraded). `colmap help` → "COLMAP 4.2.0 (Commit Unknown on Unknown with CUDA)",
     no missing libraries. Resolved. GPU use not yet tested on real images.
  9. pip `torch==2.1.2+cu121 torchvision==0.16.2+cu121` into `bs-ns` (14:33 → 14:35, 2.2 GB wheel). Check: torch sees
     the "NVIDIA RTX 4000 Ada Generation", capability (8, 9), 19.5 GiB; a 4096² matmul runs. The torch install pulled
     NumPy 2.2.6, which torch 2.1.2 cannot use (`Failed to initialize NumPy: _ARRAY_API not found`); the pinned list
     (`numpy==1.26.4`) installed next replaces it — to re-check after the pins are in.
  10. Code port on branch `feature/linux-port` (commit 09c7f6e): `toolpaths.py` + five scripts (MAP.md §3). Compiles;
      `toolpaths` resolves `~/micromamba/envs/bs-colmap/bin/colmap`, `bs-ns/bin/python`, `bs-ns/bin/ns-export`; the
      symlink replacement for `mklink /J` tested (link removed, target kept).
  11. SIFT vocabulary tree `vocab_tree_faiss_flickr100K_words32K.bin` from the COLMAP 3.11.1 release into
      `tools/colmap_dl/vocab/` (9,477,067 bytes = the release size; sha256 `921e894b…c639e`; compare with Tayyab's copy).
      ALIKED tree not downloaded (rejected path, D-022).
  12. COLMAP GPU test on 4 generated 1920×1080 test images: `feature_extractor` with GPU SIFT (~2,200 features each),
      `exhaustive_matcher` on GPU, `vocab_tree_matcher` with the tree: all exit 0. `global_mapper` and
      `patch_match_stereo` not tested yet (need a real scene).
  13. **Error:** first `pip install -r envs/linux/requirements-nerfstudio.txt` into `bs-ns` (14:35 → 14:40) failed:
      `Failed to build installable wheels ... fpsample, pyliblzfse` (`CMAKE_CXX_COMPILER not set`,
      `No such file or directory: 'gcc'`), so pip installed none of the 228 packages. Cause: pip was run with the env's
      Python by absolute path, without activating the env, so conda's compiler activation (`CC` / `CXX` →
      `x86_64-conda-linux-gnu-*`) never ran. → Rerun through `micromamba run -n bs-ns` (CC, CXX and nvcc now found).
      **Lesson for the setup script and the pipeline:** anything that compiles (pip sdists, gsplat's CUDA JIT) must run
      inside the activated `bs-ns` env.
  14. `bs-system`: `pip install -r requirements-system.txt` (cu121 index) OK, 14:40. Pins confirmed: torch 2.1.2+cu121
      (CUDA available), numpy 1.26.4, scipy 1.11.4, opencv 4.11.0, timm 1.0.30, mmengine 0.10.7, xformers 0.0.23.post1.
      Unpinned dependencies came in at their newest versions (e.g. huggingface_hub 2.4.0); to compare with Tayyab's `pip freeze`.
  15. `semantic-env` (repo root, gitignored): `bs-system`'s Python `-m venv --system-site-packages`, then
      `requirements-semantic.txt`. OK: transformers 4.46.3, tokenizers 0.20.3, huggingface_hub 0.36.2, Pillow 10.1.0,
      safetensors 0.7.0, and transformers sees torch 2.1.2 (the known pitfall).
  16. `bs-ns` pins installed (activated rerun, 14:41 → ~14:50). Confirmed: torch 2.1.2+cu121 (CUDA available), numpy
      1.26.4, nerfstudio 1.1.5, gsplat 1.4.0, open3d 0.19.0, nerfacc 0.5.2; `pip check`: no broken requirements.
      **tiny-cuda-nn left out:** nothing in `src/`, `server/` or nerfstudio's splatfacto imports it; build it later only if needed.
  17. Model weights (cached in `~/.cache/torch/hub` 1.6 GB and `~/.cache/huggingface` 1.6 GB): Metric3D ViT-L
      (`metric_depth_vit_large_800k.pth`, loaded the way `mono_prior.py` does) loads in 34 s, one fp16 forward 0.38 s,
      finite, 2.9 GiB peak VRAM; Grounding DINO tiny, SAM ViT-B, CLIP ViT-B/16 load and run once on the GPU. Note:
      `torch.hub` takes the Metric3D code from `yvanyin/metric3d` `main` (not pinned to a commit).
  18. **Error:** first gsplat call → `ModuleNotFoundError: No module named 'pkg_resources'` in torch 2.1.2's
      `cpp_extension`. Cause: conda installed setuptools 84, which no longer ships `pkg_resources` (Windows never showed
      this: `pip freeze` doesn't list setuptools). → `setuptools<70` added to `nerfstudio.yml` and `system.yml`,
      69.5.1 installed in both. Resolved.
  19. **Error:** gsplat JIT build → `ninja: build stopped`, `fatal error: cuda_runtime_api.h: No such file or directory`
      (only `ext.o`, compiled by g++; the `.cu` files built). Cause: conda's CUDA 12.1 keeps headers in
      `targets/x86_64-linux/include`, has no `lib64/`, and `CUDA_HOME` was unset. → `envs/linux/bs-ns-activate.sh`
      (CUDA_HOME, CPATH, LIBRARY_PATH, TORCH_CUDA_ARCH_LIST=8.9) installed as
      `bs-ns/etc/conda/activate.d/zz-buildscan.sh`. Resolved: gsplat 1.4.0 compiled for compute 8.9 in 124 s (one-time,
      cached in `~/.cache/torch_extensions`, 21 MB); then 100k Gaussians at 1920×1080 render in 1.2 ms per frame.
  20. **Error:** the cached gsplat build does not load when `bs-ns`'s Python is started by path without activation
      (`AttributeError: 'NoneType' object has no attribute 'CameraModelType'`), which is how `run_v8.py` started it.
      → `toolpaths.ns_cmd()` returns `micromamba run -r ~/micromamba -n bs-ns <program>` on Linux (the program path on
      Windows); `run_v8.py` uses it for export, train and ns-export. Tested from an unactivated `bs-system` shell: gsplat
      loads from the cache in < 1 s (no rebuild), `ns-export --help` exits 0. Resolved.
  21. Open3D 0.19.0 TSDF check (synthetic wall, 3 views, `ScalableTSDFVolume`): 104,668 triangles, i.e. the Open3D 0.20
      empty-mesh bug does not apply here.
  22. Test suite on this PC (throwaway venv on `bs-system`'s Python + `tests/requirements.txt`, run inside `bs-ns` for
      ffmpeg): `pytest` 210 passed, 1 skipped (`test_apk_checks.py:163`, no Java `keytool`); `ruff check .` all checks passed.
  23. `scripts/setup_linux.sh` written from steps 1–22 and run on this PC (14:54:16 → 14:54:37, exit 0): every step
      skipped or completed (env update changed no packages, `npm ci` added 383 packages, vocab tree size OK), all checks
      passed (torch + GPU in bs-ns / bs-system, semantic-env transformers 4.46.3, COLMAP 4.2.0 CUDA, gsplat, Open3D TSDF).
      **Not yet tested: a run on a fresh machine** (the Docker build or the friend's PC will be the first).
- **State after 2026-11-06 15:00:** environments ready. Still open in step 1: `server/pipeline.py` and `.sh` versions of the
  `.bat` launchers (1f), and the first real run (1h, needs Tayyab's dataset).

### R-028 · 2026-11-06 · First Linux run: Umair's own recording, full pipeline to the web bundle
- **Who / machine:** Umair (agent runs it) · this PC (Ubuntu 26.04, RTX 4000 Ada 20 GB, 30 GB RAM)
- **Branch / commit:** `exp/first-linux-run` @ `76a68cc` (uncommitted changes: no)
- **Dataset:** `dataset/scan_056fe94d3399` — recorded 2026-11-06 by Umair on an **Infinix X6833B** (first capture from this
  phone; all earlier runs used the realme RMX5111), uploaded through the server (`dry_run`). 1293 video frames, 46 s,
  1920×1080 @ 28 fps, 1203 poses, 131 ARCore depth maps, 204 MB.
- **Capture check** (`check_capture.py`): READY TO PROCESS; warnings: duration < 1 min, live IQA good 43% / ok 26% /
  bad 31%, 47 dropped-frame gaps (3.6%, longest 124 ms), **`camera.csv` and `anchors.csv` missing** (the app records
  them but its upload does not send them, STATUS §7.7) → frame selection runs without exposure data, re-anchors are
  not detected. Tracking lost 3.0%; video↔pose sync +0.05 s, correlation 0.95.
- **Command(s):** `screen -dmS r028 bash -c 'scripts/run_full.sh dataset/scan_056fe94d3399 v9 -- --sfm_args "--retrieval 20" --init fmvs --planar 0.2 --blur 0.0222 --pgsr'`
  (recipe chosen by Umair: v9 + PGSR in one training as in R-023; `--blur 0.0222` = 1/45 s, the exposure select_sharp.py
  assumes (ARCore does not record it; `camera.csv` would have it, but the upload dropped it); stages to the web bundle).
- **Goal:** STATUS §7.1 step 1h: the whole pipeline runs on Linux (first run on this PC), and the first result on a
  second room and a second phone. Not comparable with R-020 / R-023 (other room); the machine-agreement check on
  newRoomAttemptSadness stays open.
- **Errors during the run:**
  1. 17:53 check_capture — `FileNotFoundError: 'ffprobe'` when run with the env's python directly: ffmpeg is in the
     env but only on `PATH` when the env is activated → run through `micromamba run -n bs-system` (resolved: yes;
     `run_full.sh` always uses `micromamba run`).
  2. 17:53 select — `FileNotFoundError: .../scan_056fe94d3399/imu.npz`: `select_sharp.py` loads the IMU cache but nothing
     in `run_v8.py` creates it (on Windows an earlier script had made it for every capture) → `select_sharp.py` now
     calls `imu.extract_imu()` when the cache is missing; restarted from `select` at 17:54 (resolved: yes, select wrote 207 frames).
- **Start → end:** 17:54 → 18:00, **stopped by Umair** during the dense init (fast_mvs / PatchMatch): he wants to run
  this dataset himself. Stage times until then (`timing.json`): select 0.1, sfm 1.46, export 0.01, prior 0.75 min;
  166 of 207 frames went into the priors (aligned median depth error 2.1%).
- **Result:** none (stopped). Partial outputs left in `dataset/scan_056fe94d3399/work_v9/` and `work_v9_sfm/`.
- **Verdict:** abandoned (stopped by Umair). His own run gets the next run ID.

### R-029 · 2026-11-06 · Umair's run of scan_056fe94d3399, full pipeline to the web bundle
- **Who / machine:** Umair (started it himself in a terminal on the PC) · this PC (Ubuntu 26.04, RTX 4000 Ada 20 GB)
- **Branch / commit:** `exp/first-linux-run` @ `84a267f` (uncommitted changes: no)
- **Dataset:** `dataset/scan_056fe94d3399` (Infinix X6833B, 46 s, 1293 frames; capture check and missing `camera.csv` /
  `anchors.csv`: see R-028).
- **Command(s):** `scripts/run_full.sh dataset/scan_056fe94d3399 umair -- --sfm_args "--retrieval 20" --init fmvs --planar 0.2 --blur 0.0222 --pgsr`
  (same recipe as R-028; new tag so the outputs do not mix with R-028's partial ones).
- **Goal:** as R-028: first complete run on Linux, second room, second phone.
- **Start → end:** 18:01 → 18:35:54 (34.7 min). Stage times so far (`timing.json`, min): select 0.09 (207 frames), sfm 1.49
  (174 / 207 cameras registered; Sim3 to ARCore from 174 cameras, scale 0.24571), export 0.01, prior 0.75, init 2.05
  (PatchMatch 2.0 min, 13,622 fused + 4,905 SfM points → 17,592 at 1 cm); train from 18:05, 15,000 steps, at 18:29
  step 13,980 (93%), GPU 97%, 4.6 / 20 GB, 76 °C, 101 W.
- **Errors during the run:**
  1. 18:05–18:22 train — looked stuck to Umair: the terminal showed nothing after `== train:`. Cause: `run_v8.py`
     writes the training output only to `train.log`; training was running (step 11,900 at 18:22). → `run_full.sh` now
     prints a GPU / training status line every 30 s (`b8aef7a`, used from the next run) (resolved: yes).
- **Progress (18:34):** train 26.45 min, ply 0.25 min, run_v8 total 31.1 min → `gs_umair/splat.ply` (121 MB). Layout
  (2 s): 68 flat of 119 planar regions from 29 frames, rendered-plane rms median 4.5 cm; floor y −2.988, ceiling y
  1.204 → **room height 4.193 m**; 11 vertical plane clusters → **only 1 wall, 0.873 m long, 0 corners**. Looks wrong
  (to compare with the real room; likely the 46 s capture saw too little wall). sem2d running on 87 frames.
  **Scene (Umair, 18:40):** the end of a corridor, poor lighting, recorded only to test the pipeline, so one short wall
  and a tall space are plausible; the room-oriented layout / semantics rules do not fit a corridor end.
- **Stage times after the 3DGS** (`stages.tsv`, min): layout 0.0 (2 s), sem2d 2.8 (87 frames), sem3d 0.1, verify 0.1,
  sem3d2 0.1, mesh 0.1, meshlabels 0.4, web 0.1. No errors in these stages.
- **Result:** `dataset/scan_056fe94d3399/work_umair_sfm/gs_umair/` (`splat.ply` 121 MB, `layout/`, `semantic_v10/`,
  `mesh/`), web bundle `prototype/web-ui/public/scans/scan_056fe94d3399_umair/` (18.0 MB).
  Semantics: floor plane tilt 0.28°, residual 6.9 cm; ceiling fit rejected, set at the layout height 4.177 m;
  **0 fixtures accepted, 61 rejected**; CLIP check: 1 of 4 rejected candidates kept (light switch, p 0.52 "an
  electrical outlet"), 3 dropped (sticker / paper label, picture frame); Gaussians per class: other 449,883, floor
  8,639, ceiling 28,082, wall_0 584. Mesh: 1,568,501 triangles → 1,430,921 after removing small pieces; areas (m²):
  other 95.19, floor 12.79, ceiling 3.02, wall 0.09; `mesh_web.glb` 400k triangles 8.5 MB. Model quality not
  measured (no held-out split, no tape measurements).
- **Verdict:** kept as a **pipeline test**: the whole v9 / v10 pipeline ran end to end on Linux for the first time
  (34.7 min on the RTX 4000 Ada; 207 selected frames, so not comparable with the 96 + 40 min of R-020 / R-025 on
  1165 frames). Scene results are not meaningful (corridor end, poor light, 46 s). STATUS §7.1 1h: Linux run done; the
  machine-agreement check on newRoomAttemptSadness stays open.

### R-030 · 2026-11-06 · scan_646070948603 full pipeline (tag `r1106`), first run through `scripts/buildscan`
*Not logged at the time; written on 2026-11-12 from `run_full.log`, `stages.tsv`, `timing.json` and the output files.*
- **Who / machine:** started on Umair's PC; the person who started it was not recorded · this PC (Ubuntu, RTX 4000 Ada)
- **Branch / commit:** `exp/first-linux-run` @ `718f884` (from the `run_full.log` header; uncommitted changes: not recorded)
- **Dataset:** `scan_646070948603`: a computer lab (desks, red chairs, glass partition), Infinix X6833B, 97.3 s,
  2,899 ARCore poses; 482 frames selected. Uploaded with app ≤ v0.3.4, so no `camera.csv` / `anchors.csv` (fixed in
  v0.3.5, PR #4).
- **Command(s):** `scripts/buildscan run latest r1106` → `scripts/run_full.sh` with the default recipe
  `--sfm_args "--retrieval 20" --init fmvs --planar 0.2 --blur 0.0222 --pgsr` (15,000 steps).
- **Goal:** first real room on Linux with the best-model recipe (R-023); first run started through `scripts/buildscan`.
- **Start → end:** 18:58:05 → 19:48:15 (50.2 min). run_v8 41.7 min: select 0.2, SfM 4.93, prior 1.92, init 6.57,
  train 27.76, ply 0.29. Then layout 0.1, sem2d 7.7, sem3d 0.1, verify 0.1, sem3d2 0.1, mesh 0.1, meshlabels 0.2,
  web 0.1. GPU during training: 92–100%, up to 5.9 of 20.5 GB, 59–76 °C.
- **Errors during the run:** none in `run_full.log` (only timm `FutureWarning`s).
- **Result:** `dataset/scan_646070948603/work_r1106_sfm/gs_r1106/` (`splat.ply` 162 MB); web bundle
  `prototype/web-ui/public/scans/scan_646070948603_r1106/` (20.4 MB, gitignored by D-061).
  SfM: 482 / 482 frames registered; Sim3 to ARCore scale 0.0937, 242 inliers, median 5.25 cm (`report.json`).
  Metric3D prior aligned median error 3.6%. Layout: 2 walls (3.86 m, 4.45 m), 0 corners, floor y −1.205, ceiling y
  0.291 → **height 1.50 m**. Semantics v10: floor tilt 2.13°, ceiling height 1.528 m; 8 fixtures accepted (window,
  2 light switches, 2 power sockets, ceiling light, lamp, air conditioner), 44 rejected. Mesh: 663,551 → 576,792
  triangles; area 46.63 m² (other 32.1, wall_0 7.65, floor 3.99, ceiling 2.49). Model quality not measured (no
  held-out split, no tape measurements); fixtures not checked by a person.
- **Verdict:** **inconclusive.** The pipeline ran end to end without errors, but a 1.50 m room height cannot be right
  for this lab (the ceiling plane is probably not the real ceiling, or the scale is off); not checked against the
  room or a tape. To do: view the model (`scripts/buildscan view scan_646070948603 r1106`), check the ceiling plane
  and one tape length.
- **Follow-up 2026-11-12:** Zaid's `analyze.py` (`feat/splat-compress`) on this `splat.ply`: 652,392 splats, extent
  p1–p99 8.46 × 3.08 × 4.78 m. The model itself is ~3.1 m tall, so the 1.50 m height is the layout taking a wrong
  plane as the ceiling, not a scale error (not yet confirmed by viewing the model or a tape).

### R-031 · 2026-11-12 · scan #3 (classroom, `scan_003_6de634cbb8b2`) full pipeline (tag `r1112`)
*Header written by the agent while the run was going, from `run_full.log` and the dataset files.*
- **Who / machine:** Umair · this PC (Ubuntu, RTX 4000 Ada), in `screen` session `run-r1112`
- **Branch / commit:** `feature/numbered-scans` @ `e4c3ee6` (from the `run_full.log` header; uncommitted changes: no)
- **Dataset:** scan #3, `scan_003_6de634cbb8b2`: a classroom (rows of wooden desks with red seats, projector screen; room number not recorded, STATUS §2 "Which recording is which"), Infinix X6833B, app v0.3.6 (server log: USB upload 14:53:06, 815 MB in 22 s at 37 MB/s; only v0.3.6 uploads over USB), uploaded 2026-11-12 14:53 with `camera.csv`,
  `anchors.csv`, `lens_metadata.json`, `camera_characteristics.json` (first recording with all of them). 184.7 s,
  5,335 ARCore poses; 885 of 5,346 frames selected (predicted blur median 6.6 px over all frames, 5.3 px selected;
  recorded exposure median 30.0 ms, used instead of the fixed 1/45 s).
- **Command(s):** `scripts/run_full.sh dataset/scan_003_6de634cbb8b2 r1112 -- --sfm_args "--retrieval 20" --init fmvs
  --planar 0.2 --blur 0.0222 --pgsr`
- **Goal:** first room recorded with v0.3.5 (COMPLETION_PLAN 1.4 / 3.2); check the layout height against tape (4.1).
- **Start → end:** 15:04:02 → (running)
- **Errors during the run:** none so far.
- **Capture facts measured on 2026-11-12 (agent, from the dataset files, for COMPLETION_PLAN 1.6 / 1.7):**
  `check_capture.py`: READY TO PROCESS; **video 28.9 fps average, 176 dropped-frame gaps in 5,346 frames (3.3%),
  longest 99 ms** (NFR1 not met); poses 28.9 Hz, tracking lost 0.0%; predicted blur median 6.7 px (> 5 px on 75% of
  frames, > 10 px on 21%); exposure median 30.0 ms (range 10–30 ms), ISO median 842; rolling-shutter readout 28.2 ms;
  ARCore world corrections at 22.3 s (123 cm, 6.0°), 31.5 s (26 cm) and six smaller ones; video ↔ pose sync +0.05 s,
  r = 0.89. (A first count from `poses.csv` gaps gave 0.24% dropped; that count used a 1.5 × median threshold on pose
  timestamps and missed most gaps, so the video count is the one to use.) ARCore depth: 782 maps
  (160 × 90), all 782 different, median valid fraction 0.86, median depth 0–5.5 m across maps, mean confidence
  0–81: **not stale** in this recording. IQA levels in `quality.csv`: GOOD 1,279, WARN 2,894, BAD 1,164.
- **Result:** (to fill in at the end)
- **Verdict:** (to fill in at the end)

### R-032 · 2026-11-12 · Training speed-up, phase 1: profiling + exact fixes + blur colour grid once (`fast_t1`)
*Runs R-032 – R-038 were numbered R-029 – R-035 on the unmerged branch (the chat of 2026-11-12 uses those numbers);
renumbered on 2026-11-13 when `origin/master` (which already had R-029 – R-031) was merged into `exp/fast-pipeline`.*
- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/fast-pipeline` @ f33aeaf (uncommitted changes: yes, `geo_splatfacto.py`)
- **Dataset:** newRoomAttemptSadness, the v9e2e work folder (`work_v9e2e_sfm`: same SfM, Metric3D prior, fast-MVS init,
  plane masks, blur motion and 79-frame off-path split as R-020); only training changes.
- **Command(s):** `geo_splatfacto.py --data work_v9e2e_sfm/transforms_fmvs.json --name fast_t1 --iters 15000
  --dash_res_steps 7500 --stop_split_at 7500 --no_eval --prior mono_prior/train_v9e2e.npz --planar_lambda 0.2
  --blur_exposure 0.0222` (R-020's train stage), then `ns-export`, then `eval_offpath.py` against `gs_v9e2e`.
- **Goal:** same quality as R-020's training (PSNR 25.16 / SSIM 0.8247 / sharpness 0.80 / flatness 0.77 cm on the
  79 held-out frames) in less than its 42.5 min.
- **Profiling before the run (torch.profiler, 30-step windows, 01:00 – 01:10):**
  - Low-res steps took 77 ms although rendering at 1/8 resolution costs ~3 ms: 29% of GPU time was `index_select` /
    `index_add_` in nerfstudio's `total_variation_loss` on **all** 1086 per-image bilateral grids (107 MB) every step.
    → `_TotalVariation` (same value and gradient, checked: max gradient difference 5e-12): 50 → 13 ms per call.
    Low-res step 77 → 41 ms.
  - Full-res steps took ~220 ms: the bilateral grid was applied to each motion-blur sub-render (2.8 per step on
    average), and its per-pixel colour affine ran as a batched matmul of 2 M 3×3 matrices (~26 ms per call).
    → elementwise affine (same result, max difference 2e-7; 31.5 → 18.3 ms per call) and, with the blur model,
    the grid applied **once to the averaged render** (the camera's colour processing acts on the light integrated over
    the exposure; not bit-identical to before, hence this run). `--blur_grid_per_sub` restores the old behaviour.
    Full-res step 220 → 160 ms.
- **Start → end:** 01:14 → 01:47 (training 28.2 min; then export + eval). Step times vs R-020 at the same step:
  2k 64 vs 86 ms, 5k 63 vs 98, 8k (full res) 158 vs 233, 11k 135 vs 216, 14k 174 vs 261.
- **Errors during the run:**
  1. 01:08 (profiling, before the run) — `AssertionError` in `lib_bilagrid.py:311` (`len(rgb.shape) == input_ndims`):
     the blur path passes an [H, W, 3] image, splatfacto [1, H, W, 3] → reshape both to [1, 1, H, W, 3]. Resolved.
- **Result:** `work_v9e2e_sfm/gs_fast_t1/` (eval sheets in `eval/`). 79 off-path frames, same eval as R-020:

  | model | splats | PSNR(cf) | SSIM | sharpness | flatness cm | train min |
  |---|---|---|---|---|---|---|
  | v9e2e (R-020) | 619,056 | 25.16 | 0.8247 | 0.80 | 0.77 | 42.5 |
  | fast_t1 | 621,430 | 25.14 | 0.8251 | 0.80 | 0.81 | **28.2** |

  Off-path frames and the 4 room-centre views look the same (same printer-edge smear, same table top). Run-to-run
  noise is not measured, so the 0.02 dB / 0.04 cm differences cannot be told apart from it.
- **Verdict:** kept (proposed) — training −34% (−14.3 min) at equal quality; the TV and colour-affine changes are exact,
  the blur colour-grid change is the only behaviour change.

### R-033 · 2026-11-12 · Speed-up phase 2: photometric-only fast-MVS init (`fast_t2_photo`)
- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/fast-pipeline` @ f33aeaf (uncommitted changes: yes, R-032's + `fast_mvs.py --iters / --photometric / --suffix`)
- **Dataset:** newRoomAttemptSadness, `work_v9e2e_sfm` (as R-032).
- **Command(s):** init variants: `fast_mvs.py --work work_v9e2e_sfm --json transforms.json --out_json transforms_fmvs_it3.json
  --suffix _it3 --iters 3` and `... --suffix _photo --photometric`; then R-032's training on `transforms_fmvs_photo.json`.
- **Goal:** cut the 20 min dense init without losing quality (compared with R-032, same training code).
- **Init variants (PatchMatch time; cloud vs the current `init_fmvs.ply`, 258,364 points):**
  current 5 iterations + geometric pass 20.1 min (in R-020) · 3 iterations 12.1 min, 244,948 points, 94.3% of the
  current points within 2 cm, 96.1% of its points within 2 cm of the current cloud, 99.1% within 5 cm · photometric only
  **7.5 min**, 262,592 points, 93.2% / 90.9% / 99.1%.
- **Start → end:** first attempt 02:16 → stopped at step 8240 (~02:45); restarted 16:45 → 17:20 (training 30.6 min, slowed by R-034 running on the CPU at the same time)
- **Errors during the run:**
  1. ~02:45 training — the run stopped at step 8240 of 15000 with exit code 4 and no Python traceback, at the same moment
     as R-034's COLMAP process (both started from the agent's shell; likely the shell session was ended). Nothing else on
     the PC was affected. → restarted from scratch at 16:45 (partial outputs removed). (resolved: restarted)
- **Result:** `work_v9e2e_sfm/gs_fast_t2_photo/`. 79 off-path frames:

  | model | splats | PSNR(cf) | SSIM | sharpness | flatness cm |
  |---|---|---|---|---|---|
  | v9e2e (R-020) | 619,056 | 25.16 | 0.8247 | 0.80 | 0.77 |
  | fast_t1 (R-032, current init) | 621,430 | 25.14 | 0.8251 | 0.80 | 0.81 |
  | fast_t2_photo (photometric init) | 622,049 | 25.16 | 0.8240 | 0.80 | 0.78 |

  Room-centre and off-path views look the same as v9e2e (no new holes or floaters).
- **Verdict:** kept (proposed) — dense init 20.1 → 7.5 min (−12.6 min) at equal quality. The 3-iteration variant was not trained (slower, no reason to prefer it).

### R-034 · 2026-11-12 · Speed-up phase 2: COLMAP global mapper settings (CPU)
- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/fast-pipeline` @ f33aeaf (no code change; COLMAP options only)
- **Dataset:** newRoomAttemptSadness, a copy of `work_v9e2e_sfm/database.db` (R-020's matches), output in `work_v9e2e_sfm/_mapper_exp/`.
- **Command(s):** `COLMAP global_mapper --database_path db.db --image_path work_v9e2e/images --output_path <variant>`
  with `--GlobalMapper.ba_num_iterations 1` (`ba1`) and with `--GlobalMapper.skip_retriangulation 1` (`noretri`).
- **Goal:** the mapper took 14.3 min in R-020 (global positioning 3.0, bundle adjustment 4.8, retriangulation +
  refinement 6.5; Ceres has no CUDA in this COLMAP build, so all on the CPU). Compare poses (Sim3-aligned camera
  centres in cm, rotations), points and lens parameters with R-020's `sparse/0`.
- **Start → end:** first attempt 02:18 → stopped during `ba1`'s retriangulation (~02:45, see R-033 error 1); restarted 16:45 → (running)
- **Errors during the run:**
  1. ~02:45 — stopped with exit code 4 together with R-033 (no COLMAP error in the log). Restarted at 16:45. (resolved: restarted)
- **Result:** (pending)
- **Verdict:** (pending)

### R-035 · 2026-11-12 · Fast pipeline end to end (`v10fast`): all kept speed-ups from the raw capture
- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/fast-pipeline` @ f33aeaf (uncommitted changes: yes: R-032 training changes, threaded
  `mono_prior.py`, `fast_mvs.py --photometric`, `sfm_colmap.py --skip_retriangulation`, `run_v8.py --init_args`)
- **Dataset:** newRoomAttemptSadness raw capture (nothing reused), same 79-frame off-path split as R-020
  (`dataset/newRoomAttemptSadness/offpath_test.txt`, a copy of `work_v9e2e_sfm/offpath_test.txt`).
- **Command(s):** `python src/arcore3dgs/run_v8.py --dataset dataset/newRoomAttemptSadness --tag v10fast
  --split dataset/newRoomAttemptSadness/offpath_test.txt --sfm_args "--retrieval 20 --skip_retriangulation"
  --init fmvs --init_args=--photometric --planar 0.2 --blur 0.0222`, then
  `eval_offpath.py --work work_v10fast_sfm --models v10fast=gs_v10fast/splat.ply`.
- **Goal:** R-020 took 96.2 min end to end (select 1.9, SfM 22.4, prior 8.1, init 20.4, train 42.5, export 0.7) for
  PSNR 25.16 / SSIM 0.8247 / sharpness 0.80 / flatness 0.77 cm. Expected here: ~55–65 min at the same quality.
- **R-034 result (mapper settings, used here):** two runs of the **default** mapper on the same matches already differ:
  median camera 0.48 cm, 16 cameras > 10 cm, 4 > 30 cm, 14 rotated > 2° (GLOMAP is not deterministic).
  `skip_retriangulation`: 9.4 vs 14.3 min, median 0.90 cm, 16 / 2 / 9 — within that run-to-run spread; kept.
  `ba_num_iterations 1`: 14.2 min (no faster under CPU load), 51 cameras > 10 cm — rejected.
- **Start → end:** 17:28 → 18:31 (total 61.6 min: select 1.77, SfM 17.58, export 0.01, prior 6.80, init 8.08, CPU wait 0.0, train 26.66, export 0.66)
- **Errors during the run:**
  1. 17:26 start — `run_v8.py: error: argument --init_args: expected one argument`: argparse takes a value that starts
     with `--` and has no space for an option → `--init_args=--photometric`. Resolved (restarted 17:28).
- **Result:** `work_v10fast_sfm/gs_v10fast/` (eval sheets in `eval/`). SfM registered 1157/1166 (9 frames dropped as
  jumps > 30 cm, R-020: 1); all 79 held-out frames present; ARCore alignment median 3.16 cm (R-020 3.11); Sim3 scale
  0.6756 vs 0.6682 in R-020 (1.1% different: the metric-scale issue, STATUS 7.4).

  | model | splats | PSNR(cf) | SSIM | sharpness | flatness cm | total min |
  |---|---|---|---|---|---|---|
  | v9e2e (R-020) | 619,056 | 25.16 | 0.8247 | 0.80 | 0.77 | 96.2 |
  | v10fast | 635,797 | **24.56** | **0.8078** | **0.75** | **0.95** | **61.6** |

  Visibly worse off-path: a floater over the rug (frame 1), more smear at the door frame by the printer (frame 2) and on the
  armchair edge (frame 4).
- **Verdict:** rejected as a recipe. Training (R-032) and the photometric init (R-033) each held quality on R-020's SfM,
  so the loss comes from the SfM stage: `--skip_retriangulation` and/or the mapper's run-to-run randomness (R-034). One
  run cannot separate the two. Next: the same run with the default mapper.

### R-036 · 2026-11-12 · New room `scan_3028a4de8fa0` with the proposed fast recipe (normal SfM + R-032/R-033 speed-ups)
- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/fast-pipeline` @ f33aeaf (uncommitted changes: yes, as R-035)
- **Dataset:** `dataset/scan_3028a4de8fa0` (uploaded from the phone 2026-11-12 18:00 through the server in dry-run mode;
  178 s, 5331 video frames, 389 depth maps). `check_capture.py`: READY TO PROCESS, but a hard capture: exposure 30 ms
  (app-logged), turning median 17.6°/s (p90 36.0), walking 0.39 m/s (newRoom: 12.3°/s, 0.13 m/s), predicted blur median
  24.9 px (> 10 px in 92% of frames), live IQA "bad" 93%, tracking lost 2.2%, 3.1% dropped video frames, no
  camera.csv / anchors.csv (older app build).
- **Command(s):** `python src/arcore3dgs/run_v8.py --dataset dataset/scan_3028a4de8fa0 --tag v10 --sfm_args "--retrieval 20"
  --init fmvs --init_args=--photometric --planar 0.2 --blur 0.030` (all frames train: no held-out split, no
  baseline model of this room).
- **Goal:** end-to-end time of the proposed recipe on a second room (expected ~67 min); a usable model of the new room.
- **Start → end:** 18:47 failed at once; restarted 18:52 → 19:37 (total **48.8 min**: select 1.55, SfM 8.67, export 0.01, prior 4.73, init 4.65, CPU wait 0.33, train 28.27, export 0.59)
- **Errors during the run:**
  1. 18:47 select — `FileNotFoundError: ...scan_3028a4de8fa0\imu.npz` in `select_sharp.py:28`. Cause: `select_sharp.py`
     loaded the gyro cache `imu.npz` directly; it only existed for older datasets because `fallback.py` had made it. A
     fresh capture (and the raw-capture zip shared on 2026-11-12) has none. → `select_sharp.py` now calls
     `imu.extract_imu()` (reads the IMU tracks of `dataset.mp4`, caches `imu.npz`): 35,858 gyro samples over 178.2 s.
     (resolved)
- **Result:** `dataset/scan_3028a4de8fa0/work_v10_sfm/gs_v10/` (570,297 Gaussians, 141 MB). The room is a **tiered lecture
  hall** (stepped seating). SfM: one component, 830 / 842 frames (12 dropped as jumps), 41,996 points, lens k1 0.094 /
  k2 −0.216 (same phone as newRoom); **ARCore alignment only 97 inlier frames** (newRoom ~800), median 4.9 cm: ARCore
  probably re-anchored around the 3.9 s tracking gap, so the metric scale rests on few frames (not checked with a tape).
  Sheets in `views/` (6 *training* frames vs photos: they show fit, not off-path quality; PSNR 23.67 / SSIM 0.804 on
  them) and room-centre views. Training views: seats, desks, curtains, ceiling tiles, AC units sharp; a green floater by
  the window, a smeared wall band behind the seats, a ghosted chair. Room-centre views: poor (the camera-centroid
  "centre" lies among the tiered seats, and the fast walk leaves thin off-path coverage). `layout.py`: 9.27 × 11.58 m,
  height 3.21 m above the lowest floor, one corner 73.6° (layout assumes one floor level: rough for a tiered hall).
- **Verdict:** recipe ran end to end on a second room in 48.8 min with no manual steps after the `imu.npz` fix. Quality
  cannot be compared with the old recipe on this room (no baseline run); the capture itself is hard (25 px median blur).
- **Follow-up 2026-11-12 (Umair/Tayyab viewing the model):** the viewer shows a **"mini room inside the room"**. Diagnosis
  (R-037): part of the SfM model is rebuilt at a smaller scale. Metric3D-to-SfM depth ratio per frame (`mono_prior/stats.json`)
  is ~2.2 up to frame ~3100 but ~0.6 for frames ~3180–3700 and ~4170–4600 (3.5× smaller). ARCore poses are broken
  after frame ~2200 (ARCore path 15–71 m per 60 keyframes), so `--pairs arcore` picked wrong spatial neighbours there,
  those frames were only weakly linked, and GLOMAP's global positioning shrank them. **Verdict changed: rejected (broken SfM).**
  Scale check: a table measured in the viewer (`view.py` measure tool) in the main ("outer") room gives the real table
  length (reported by the user 2026-11-12; value not recorded), so the main model's metric scale is right despite only
  97 ARCore inliers. Metric3D reads ~1.3× short on this room (newRoom: SfM/Metric3D ratio 1.35, here 1.75): not a scale error.


### R-037 · 2026-11-12 · `scan_3028a4de8fa0`: incremental mapper instead of GLOMAP (fix for R-036's mini room)
- **Who / machine:** Tayyab (agent) · RTX 3070 PC (CPU only)
- **Branch / commit:** `exp/fast-pipeline` @ f33aeaf (uncommitted changes: yes, as R-036)
- **Dataset:** `dataset/scan_3028a4de8fa0`, R-036's keyframes and matches (`work_v10_sfm/database.db` copied to
  `work_v10inc_sfm/`)
- **Command(s):** `python src/arcore3dgs/sfm_colmap.py --work dataset/scan_3028a4de8fa0/work_v10 --out
  dataset/scan_3028a4de8fa0/work_v10inc_sfm --mapper mapper --stage map`, then `--stage undistort`, `--stage export`
- **Goal:** one consistently scaled model of the hall (no shrunken sub-model); compare camera path with R-036's.
- **Start → end:** 20:58 → 21:24 (map stage 25.4 min, two mapping rounds)
- **Progress:** started 20:58. Mapping round 0 (12 min): incremental mapper split the frames into 7 components
  [565, 162, 33, 21, 19, 12, 3] of 842: it refuses to join the weakly linked part instead of shrinking it (as GLOMAP did).
  Bridge round 0: 277 frames outside the main component matched against 81 of it (22,437 pairs), mapping round 1 from 21:12.
- **Errors during the run:** none so far (many Ceres `CHOLMOD warning: Matrix not positive definite` lines in
  `mapper.log` during round 1: a failed LM step that Ceres retries, not a crash)
- **Result:** round 1 components [581, 162, 33, 21, 20, 2] of 842: the bridge round joined only 16 more frames. The
  main component (`sparse/0`, 581 frames) has **no shrunken part**: SfM/Metric3D depth ratio per frame within 0.83–1.44×
  of its median, 0 frames < 0.5× (R-036 model: 175 frames at ~0.38×; newRoom v9e2e control: 0). Check:
  `src/arcore3dgs/sfm_scale_check.py` (per-frame median of SfM depth / Metric3D depth, R-036's `mono_prior`). Missing from it:
  video frames 2640–3875 (162-frame component 2: walking along the side wall past the seat rows, then the front with
  the teacher's desk and screen) and 4182–4734 (front of the room near the desk: white floor and walls, close range,
  blurred). These are the frames GLOMAP shrank into the "mini room": repeated seat rows, plain white surfaces, fast
  motion, and wrong ARCore neighbours give too few correct matches to tie them to the rest.
- **Verdict:** confirms the R-036 diagnosis; incremental mapping gives a correctly scaled model of ~69% of the frames,
  not the whole walk. Next step chosen by Tayyab 2026-11-12: train on the main component (R-038).

### R-038 · 2026-11-12 · `scan_3028a4de8fa0`: rest of the fast recipe on R-037's main SfM component
- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/fast-pipeline` @ f33aeaf (uncommitted changes: yes, as R-036)
- **Dataset:** `dataset/scan_3028a4de8fa0`, SfM = R-037 `work_v10inc_sfm/sparse/0` (581 / 842 keyframes)
- **Command(s):** `python src/arcore3dgs/sfm_colmap.py --work dataset/scan_3028a4de8fa0/work_v10 --out
  dataset/scan_3028a4de8fa0/work_v10inc_sfm --mapper mapper --stage undistort` (and `--stage export`), then
  `python src/arcore3dgs/run_v8.py --dataset dataset/scan_3028a4de8fa0 --tag v10inc --from_stage export --init fmvs
  --init_args=--photometric --planar 0.2 --blur 0.030`
- **Goal:** a model of the hall without R-036's shrunken "mini room" (front of the room expected thin or missing).
- **Start → end:** 21:27 → 22:03 (undistort + SfM export ~3 min; run_v8 35.8 min: export 0.01, prior 3.30, init 3.44, CPU wait 0.00, train 28.43, ply 0.60)
- **Errors during the run:** none so far
- **Result:** `dataset/scan_3028a4de8fa0/work_v10inc_sfm/gs_v10inc/splat.ply` (158 MB). SfM export: 572 frames (9 more
  dropped as pose jumps), 32,418 points, ARCore alignment 100 inliers, median 6.6 cm. Metric3D/SfM scale per frame: 5 of
  572 frames < 0.5× the median, 2 > 2× (R-036: 175 < 0.5×). Top-down splat density with camera path
  (`gs_v10inc/topdown_vs_R-036.jpg`): R-036 shows a tight camera cluster and a ghost copy of the seat rows in the middle
  of the hall; R-038 shows clean seat rows and no ghost; the right-hand walk (component 2) is missing from the camera
  path, but that side of the hall is still built from the opposite side. Not measured: off-path PSNR (no held-out
  split), table length in the viewer (asked the user to re-measure).
- **Verdict:** mini room gone; kept as the model of this room until a recapture.

### R-039 · 2026-11-14 · roomAttemptSadness2: full v9 + PGSR pipeline → layout → semantics v10 → mesh → web (COMPLETION_PLAN 3.2, 4.2)
- **Who / machine:** Tayyab (agent, overnight session) · RTX 3070 PC
- **Branch / commit:** `exp/overnight-2026-11-14` (from `exp/fast-pipeline` d936e66; uncommitted: `scripts/run_full.sh`
  made to run on Windows Git Bash too)
- **Dataset:** `dataset/roomAttemptSadness2` (realme RMX5111, recorded by 2026-10-09; the second room of the mid report,
  so far only v3 / splatfacto runs R-002, R-004, R-010)
- **Command(s):** first attempt `GPU_EVERY=120 bash scripts/run_full.sh dataset/roomAttemptSadness2 v9pgsr -- --sfm_args "--retrieval 20"
  --init fmvs --planar 0.2 --blur 0.0222 --pgsr` (the R-023 / R-031 recipe; training uses this branch's exact TV-loss
  speed-up and the blur colour grid applied once, R-032; first run of those together with `--pgsr`)
- **Goal:** a v9 model + semantics of the second room (3.2, 4.2), and the first check of the speed-ups with PGSR.
- **Restart (01:42):** `GPU_EVERY=120 bash scripts/run_full.sh dataset/roomAttemptSadness2 v9pgsr8 -- --window 8
  --sfm_args "--retrieval 20" --init fmvs --planar 0.2 --blur 0.0222 --pgsr`
- **Start → end:** 01:30 first attempt (failed 01:39); 01:42 → 03:27 (stopped in sem2d); resumed 05:54 → 06:21
- **Errors during the run:**
  1. 01:39 sfm — `vocab_tree_matcher` exited with status 3221226505 (0xC0000409) right after `matches_importer`; Git Bash
     also printed `child_copy: cygheap read copy failed ... Win32 error 299`. Cause: system RAM exhausted (16 GB PC,
     ~7 GB taken by other programs; the agent was running a `layout.py` test (2.5 GB, stuck) and an MCMC smoke test
     that caches ~6.6 GB of images at the same time; the smoke test also died, `numpy ... _ArrayMemoryError`). Fix: one
     GPU/RAM job at a time. Select had picked 1,381 keyframes (window 6) = ~8.4 GB of cached images in training, more
     than the ~9 GB this PC has free, so the run was restarted at 01:42 as tag `v9pgsr8` with `--window 8`
     (~1,090 frames, like newRoom's 1,165). (resolved by restart)
  2. 03:16–03:27 sem2d — ~12 s per frame (50 of 500 frames in ~10 min; R-025 on newRoom: ~4 s per frame). GPU memory
     7,944 / 8,192 MiB at 100%: the batched tile pass (`exp/fast-pipeline` ddd33e8, all zoomed tiles of a frame in one
     Grounding DINO call) filled the 8 GB card and Windows spilled GPU memory into system RAM. Stopped by the agent at
     03:27 (sem2d killed, run_full.sh ended). Fix: `semantic2d.py --tile_batch` (default 1 = one tile per call, the
     pre-ddd33e8 behaviour). The run continues with `--from sem2d` after the newRoom experiments (scratchpad `queue3.sh`).
- **Progress (v9pgsr8):** select 1,042 keyframes (window 8; predicted blur median 7.0 px over all 8,731 frames).
  SfM 21.3 min: one component, 1,014 / 1,042 registered, 1,000 kept (14 dropped as jumps), 146,818 points; Sim3 to
  ARCore 777 inliers, median 3.3 cm. SfM vs ARCore camera centres: median 3.0 cm up to video frame 5800, 8.0 cm for
  5800–6250, 43 cm (p90 2.6 m) after 6250 (ARCore drifts late in the walk; SfM is the reference there).
  `sfm_scale_check.py`: no shrunken block; one block at 2.2× (frames ~5898–6200) = close-ups of a curtain filling the
  view, where Metric3D reads too near (SfM agrees with ARCore there): this is why the check only flags blocks < 0.5×.
- **Stage times so far:** select 4.5 (first attempt) / not re-timed, SfM 21.3, prior ~6, init 19.1 (PatchMatch 18.7),
  train 36.2 (with PGSR, 15k steps), ply 1.2, layout 5.6 min (2.775 m room height; ceiling candidates 2.78 m weight 1.00
  with 1.7% above, 3.02 m weight 0.26, 2.46 m weight 0.20).
- **Result:** `dataset/roomAttemptSadness2/work_v9pgsr8_sfm/gs_v9pgsr8/` (`splat.ply`, `layout/`, `semantic_v10/`,
  `mesh/`, `stages.tsv`, `sfm_scale_check` not run: the warning was added after this run's prior stage); web bundle
  `prototype/web-ui/public/scans/roomAttemptSadness2_v9pgsr8/` (33 MB, gitignored). Stage times: run_v8 87.7 min
  (select 3.6, SfM 21.3, prior 6.3, init 19.1, train 36.2, ply 1.3), layout 5.6, sem2d 24.6 (resumed run, one tile per
  call, 500 frames), sem3d 0.4, verify 0.3, sem3d2 0.4, mesh 0.3, meshlabels 0.5, web 0.2 min. Layout: 2.775 m
  height. Semantics v10: floor tilt 0.67°, ceiling height 2.819 m, floor area 11.92 m²; **22 fixtures accepted**
  (door 1, window 1, light switch 8, power socket 5, ceiling light 4, tube light 1, lamp 2), 51 rejected. Not
  measured: off-path quality (no held-out split), tape, fixture correctness (no person has checked them; the v10 rules
  were tuned on newRoom).
- **Verdict:** **kept as the v9 model of the second room** (COMPLETION_PLAN 3.2 done for this room; 4.2 needs a person
  to check the 22 fixtures against the room). Not copied to `saved_models/` (Tayyab to decide).

### R-040 · 2026-11-14 · newRoom: MCMC densification at the baseline budget (`mcmc620`)
- **Who / machine:** Tayyab (agent, overnight session) · RTX 3070 PC
- **Branch / commit:** `exp/overnight-2026-11-14` (uncommitted: the `--mcmc_cap` option in `geo_splatfacto.py` until it is tested)
- **Dataset:** newRoomAttemptSadness, `work_v9e2e_sfm` (R-020's SfM, prior, fast-MVS init and off-path split)
- **Command(s):** `train_eval.sh mcmc620 --mcmc_cap 620000` (scratchpad helper = R-032's commands: `geo_splatfacto.py --data work_v9e2e_sfm/transforms_fmvs.json --iters 15000 --dash_res_steps 7500 --stop_split_at 7500 --no_eval --prior mono_prior/train_v9e2e.npz --planar_lambda 0.2 --blur_exposure 0.0222 --mcmc_cap 620000`, `ns-export`, `eval_offpath.py` vs `gs_v9e2e` on the 79 off-path frames)
- **Goal:** gsplat `MCMCStrategy` (3DGS as MCMC, Kheradmand et al. 2024: relocation of dead Gaussians + position noise, opacity / scale regularisers 0.01) instead of splatfacto's split / clone / prune, capped at ~620k Gaussians (v9e2e has 619,056). New `--mcmc_cap` option in `geo_splatfacto.py`. Does it beat R-032 (25.14 / 0.8251) at the same size?
- **Start → end:** 03:27 → 04:03 (train 35.0 min)
- **Errors during the run:** none so far
- **Result:** `work_v9e2e_sfm/gs_mcmc620/` (eval sheets in `eval/`). MCMC grew from the 258k-point init by 5% per 100
  steps as expected (e.g. step 900: 15,352 relocated, 14,954 added, 314,042 total); the exported `splat.ply` has
  402,989 Gaussians (why fewer than the cap was not investigated). Off-path, 79 frames: **PSNR(cf) 24.65 / SSIM 0.8216 /
  sharpness 0.64 / flatness 0.98 cm** vs v9e2e 25.16 / 0.8247 / 0.80 / 0.77 and R-032 25.14 / 0.8251 / 0.80 / 0.81.
  Full-resolution steps ~209 ms (R-032 ~160 ms). Crops: printer edges, plant leaves and floor grain visibly softer.
- **Verdict:** **rejected** (one setting). Possible reasons, not tested: relocation stops at step 7,500 (half of
  training; gsplat's default keeps it to 25k of 30k), interaction with the DashGaussian low-resolution phase and the
  depth / normal priors, the opacity regulariser pushing opacities down.

### R-041 · 2026-11-14 · newRoom: Fast training + PGSR-lite on newRoom (`pgsrfast`)
- **Who / machine:** Tayyab (agent, overnight session) · RTX 3070 PC
- **Branch / commit:** `exp/overnight-2026-11-14` (uncommitted: the `--mcmc_cap` option in `geo_splatfacto.py` until it is tested)
- **Dataset:** newRoomAttemptSadness, `work_v9e2e_sfm` (R-020's SfM, prior, fast-MVS init and off-path split)
- **Command(s):** `train_eval.sh pgsrfast --pgsr` (scratchpad helper = R-032's commands: `geo_splatfacto.py --data work_v9e2e_sfm/transforms_fmvs.json --iters 15000 --dash_res_steps 7500 --stop_split_at 7500 --no_eval --prior mono_prior/train_v9e2e.npz --planar_lambda 0.2 --blur_exposure 0.0222 --pgsr`, `ns-export`, `eval_offpath.py` vs `gs_v9e2e` on the 79 off-path frames)
- **Goal:** The speed-ups (R-032) together with `--pgsr` (the best model's recipe, R-021 / R-023): same quality as R-021 v9pgsr (25.09 / 0.8254, 46 min training)?
- **Start → end:** 04:03 → 04:37 (train 33.0 min)
- **Errors during the run:** none so far
- **Result:** `work_v9e2e_sfm/gs_pgsrfast/` (623,022 Gaussians). Off-path, 79 frames: **PSNR(cf) 25.02 / SSIM 0.8232 /
  sharpness 0.87 / flatness 1.34 cm** in **33.0 min** of training, vs R-021 v9pgsr (old training code) 25.09 / 0.8254 /
  sharpness 0.88 in 46 min, and v9e2e 25.16 / 0.8247 / 0.80 / 0.77 cm. R-021's off-path flatness was never measured,
  so the 1.34 cm cannot yet be called a regression (to do: eval `gs_v9pgsr` with `eval_offpath.py` on the same frames).
- **Verdict:** speed-ups work with PGSR (−13 min, −28%); PSNR −0.07 dB / SSIM −0.002 vs R-021 is within what one run
  per setting can resolve (run-to-run noise not measured). Flatness check done 2026-11-14 06:53 (same 79 frames, `eval_offpath.py`): R-021 v9pgsr 25.09 / 0.8254 / sharpness 0.88 /
  **flatness 1.27 cm**, R-041 25.02 / 0.8232 / 0.87 / **1.34 cm**: PGSR models score worse than v9e2e (0.77 cm) on this
  flatness measure with or without the speed-ups, so the speed-ups are not the cause. **Speed-ups kept with PGSR.**

### R-042 · 2026-11-14 · newRoom: MCMC with a larger budget (`mcmc1m`)
- **Who / machine:** Tayyab (agent, overnight session) · RTX 3070 PC
- **Branch / commit:** `exp/overnight-2026-11-14` (uncommitted: the `--mcmc_cap` option in `geo_splatfacto.py` until it is tested)
- **Dataset:** newRoomAttemptSadness, `work_v9e2e_sfm` (R-020's SfM, prior, fast-MVS init and off-path split)
- **Command(s):** `train_eval.sh mcmc1m --mcmc_cap 1000000` (scratchpad helper = R-032's commands: `geo_splatfacto.py --data work_v9e2e_sfm/transforms_fmvs.json --iters 15000 --dash_res_steps 7500 --stop_split_at 7500 --no_eval --prior mono_prior/train_v9e2e.npz --planar_lambda 0.2 --blur_exposure 0.0222 --mcmc_cap 1000000`, `ns-export`, `eval_offpath.py` vs `gs_v9e2e` on the 79 off-path frames)
- **Goal:** Does a 1M-Gaussian MCMC model improve off-path quality, and at what time / size cost?
- **Start → end:** 04:37 → 05:19 (train 40.4 min)
- **Errors during the run:** none so far
- **Result:** `work_v9e2e_sfm/gs_mcmc1m/` (601,002 Gaussians exported). Off-path, 79 frames: **PSNR(cf) 24.74 / SSIM
  0.8200 / sharpness 0.69 / flatness 0.93 cm**, 40.4 min training (v9e2e 25.16 / 0.8247 / 0.80 / 0.77, 42.5 min).
- **Verdict:** **rejected**: a larger budget helps MCMC a little over R-040 (+0.09 dB, sharpness 0.64 → 0.69) but it
  stays below splatfacto's densification on this pipeline. MCMC as wired here (relocation stopping at 7,500 steps,
  DashGaussian, depth / normal / planar priors) is not worth more runs without changing those first.

### R-043 · 2026-11-14 · newRoom: revised opacity on clone / split (`revop`)
- **Who / machine:** Tayyab (agent, overnight session) · RTX 3070 PC
- **Branch / commit:** `exp/overnight-2026-11-14` (new `--revised_opacity` option in `geo_splatfacto.py`, uncommitted until tested)
- **Dataset:** newRoomAttemptSadness, `work_v9e2e_sfm` (as R-040)
- **Command(s):** as R-040 with `--revised_opacity` (gsplat `DefaultStrategy(revised_opacity=True)`: Bulò et al. 2024,
  "Revising Densification in Gaussian Splatting"; splatfacto turns it off)
- **Goal:** cheaper floater / over-opacity fix than MCMC: does it beat R-032 (25.14 / 0.8251)?
- **Start → end:** 05:24 → 05:53 (train 28.5 min)
- **Errors during the run:** none so far
- **Result:** `work_v9e2e_sfm/gs_revop/` (561,425 Gaussians, −10% vs R-032's 621,430). Off-path, 79 frames: **PSNR(cf)
  25.02 / SSIM 0.8244 / sharpness 0.79 / flatness 0.73 cm**, 28.5 min, vs R-032 (same code without the option)
  25.14 / 0.8251 / 0.80 / 0.81 cm, 28.2 min.
- **Verdict:** **inconclusive, not adopted**: −0.12 dB PSNR, flatness 0.08 cm better, 10% smaller model; differences of
  this size are within what one run per setting can resolve (run-to-run noise not measured, STATUS 7.3).

### R-044 · 2026-11-14 · newRoom: lower densification threshold (`dg4`)
- **Who / machine:** Tayyab (agent, overnight session) · RTX 3070 PC
- **Branch / commit:** `exp/overnight-2026-11-14`
- **Dataset:** newRoomAttemptSadness, `work_v9e2e_sfm` (as R-040)
- **Command(s):** as R-040 with `--densify_grad 0.0004` (default 0.0006): more splitting / cloning where the image
  gradient is high
- **Goal:** do more Gaussians in detailed areas sharpen the off-path views (R-040 showed softness is the weak point),
  and at what size / time cost?
- **Start → end:** 06:21 → 06:53 (train 30.8 min); then the R-021 / R-041 flatness eval (06:53)
- **Errors during the run:** none so far
- **Result:** `work_v9e2e_sfm/gs_dg4/` (**868,556 Gaussians, +40%** vs R-032). Off-path, 79 frames: **PSNR(cf) 25.07 /
  SSIM 0.8243 / sharpness 0.85 / flatness 0.74 cm**, 30.8 min, vs R-032 25.14 / 0.8251 / 0.80 / 0.81 (28.2 min).
  Crops next to v9e2e: printer, floor and plant look the same; leaves perhaps slightly crisper.
- **Verdict:** **inconclusive, not adopted**: higher sharpness score and flatness, slightly lower PSNR / SSIM, no
  visible gain, and 40% larger models (web delivery).

### R-045 · 2026-11-15 · scan_009_057ed3beb4fc: full v9 + PGSR pipeline on a capture that failed check_capture
- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/overnight-2026-11-14` @ eeebb42 (uncommitted changes: no, apart from the untracked
  roomAttemptSadness2 web bundle)
- **Dataset:** `dataset/scan_009_057ed3beb4fc` (realme RMX5111, uploaded 2026-11-15 13:47 over Wi-Fi to a dry-run
  server on 192.168.18.78:8010; 1920x1080, 5,629 frames, 188 s; 285 depth files)
- **Capture check (`check_capture.py`, before the run):** FAIL: tracking lost on 63.7% of frames (7 pose gaps > 0.5 s,
  longest 26.9 s); FAIL: predicted blur median 21.7 px (> 10 px on 77% of frames); live IQA bad 92%; exposure 20 ms at
  ISO 689. Run at Tayyab's request anyway, to see what the pipeline makes of it.
- **Command(s):** `GPU_EVERY=120 bash scripts/run_full.sh dataset/scan_009_057ed3beb4fc v9pgsr -- --sfm_args
  "--retrieval 20" --init fmvs --planar 0.2 --blur 0.0222 --pgsr` (the R-039 recipe, default select window)
- **Goal:** a v9 model of this capture; see whether SfM recovers where ARCore tracking was lost.
- **Errors during the run:**

  1. 14:47 select — only 238 keyframes from 5,629 frames (window 6 would give ~940); selected frames' predicted blur
     median 18.2 px vs 12.9 px over all frames. Likely cause (not confirmed): selection only uses frames with an ARCore
     pose, and tracking was lost on 63.7% of the capture. Run continued (resolved: n/a, observation).
  2. 14:5x sfm — 6 components [101, 76, 16, 10, 8, 3] of 238 frames; the bridge round joined none. 87 frames kept
     (14 dropped as jumps), all from video frames 3443–4855 (115–162 s of 188 s, with a gap 3884–4759). Sim3 to
     ARCore: scale 0.207, only 23 inliers, median 2.3 cm. Cause: the blur / tracking loss check_capture flagged.
     Run continued (resolved: no; the model can only cover this part of the walk).
  3. prior — `sfm_scale_check.json` verdict "ok" but `ratio_median` 6.86 (SfM depth / Metric3D depth; ~1 expected):
     the whole model is likely ~7x off in metric scale (weak ARCore alignment). The check only flags blocks relative
     to the median, not a global ratio far from 1 → follow-up: also flag a global median outside ~0.5–2x
     (resolved: no).
  4. 15:18 layout — `IndexError: index -1 is out of bounds for axis 0 with size 0` in `layout.py` line 295 (plan.png
     bounds). Cause: no floor found in the fragment (`floor y nan`), so the splat mask for the plan was empty; ceiling
     candidate y 2.416, 10 short walls (0.55–2.0 m). run_full.sh stopped; semantics, mesh and web export not run.
     Follow-up: layout.py should skip plan.png / exit cleanly when the floor is not found (resolved: no; not re-run,
     semantics of an 87-frame fragment would not be meaningful).
- **Start → end:** 14:46 → 15:19 (run_v8 32.4 min: select 1.51, sfm 1.18, export 0.01, prior 0.95, init 0.39,
  train 27.87, ply 0.50; layout crashed at once)
- **Result:** `dataset/scan_009_057ed3beb4fc/work_v9pgsr_sfm/gs_v9pgsr/splat.ply` (353,628 Gaussians, 88 MB), around a
  bathroom doorway only. Web viewer copy `prototype/web-ui/public/splats/scan009_v9pgsr.spz` (7.1 MB, local only).
  No metrics (no held-out split); metric scale unreliable (errors 2–3).
- **Verdict:** rejected as a room model (partial, scale unreliable): the capture must be recorded again. Kept on disk
  as an example of what a capture that fails check_capture produces.

### R-046 · 2026-11-15 · scan_009_057ed3beb4fc: v9 + PGSR with pose-free keyframe selection
- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/overnight-2026-11-14` @ eeebb42 (uncommitted changes: yes: `select_sharp.py --pose_free`,
  `sfm_colmap.py` handles frames without an ARCore pose, `run_v8.py --pose_free`; web-ui project list)
- **Dataset:** `dataset/scan_009_057ed3beb4fc` (as R-045)
- **Why:** R-045 trained on 87 frames because select_sharp.py dropped every frame without a settled ARCore pose
  (63.7% tracking loss) before SfM. Tayyab: ARCore is guidance (matching pairs where featureless) and scale only;
  COLMAP should place the frames. `--pose_free` keeps those frames (`c2w` null); sfm_colmap gives them temporal +
  retrieval pairs only and leaves them out of the Sim3 fit.
- **Select test (14:5x→15:4x, before the run):** 894 keyframes (window 6), 230 with a usable ARCore pose, 664
  without; predicted blur median 10.5 px (R-045's pose-only selection: 238 frames, 18.2 px).
- **Command(s):** `GPU_EVERY=120 bash scripts/run_full.sh dataset/scan_009_057ed3beb4fc v9pf -- --pose_free
  --sfm_args "--retrieval 20" --init fmvs --planar 0.2 --blur 0.0222 --pgsr`
- **Goal:** more of the room registered than R-045's 87 frames, at a usable scale.
- **Errors during the run:**
  1. (before the run) select_sharp.py `--pose_free` first attempt: `ValueError: The truth value of an array with more
     than one element is ambiguous` (`if not idx` on a numpy array once the pose filter is skipped) → fixed to
     `len(idx) == 0` (resolved: yes).

  2. 15:4x sfm — 701 of 894 frames registered, in 5 components [234, 234, 150, 63, 20]; the bridge round joined none.
     Components are not time segments: component 0 covers video 13–19, 27–35, 108–130, 154–164, 186–188 s (places
     revisited), so the breaks are between places the images cannot link (blur, plain walls). Kept component: 224
     frames (10 dropped as jumps), Sim3 to ARCore 22 inliers, scale 0.292 (resolved: no).
  3. Diagnosis (agent, 2026-11-15): ARCore lost tracking 7 times (13.4–16.9, 22.6–38.7, 45.4–47.4, 52.1–78.9,
     85.2–110.0, 134.0–155.8, 162.3–186.9 s), and its poses are not consistent across these stretches. They are not
     consistent inside one stretch either: component 0's 82 poses in stretch 5 (110–134 s) span 7.3 m and fit the SfM
     camera centres with a 1.48 m median residual (component 1 vs stretch 0: 12.9 cm over a 0.4 m path). So ARCore can
     neither scale nor join the components of this capture; the low inlier count and R-045's wrong scale come from this.
  4. 16:0x — run stopped by the agent during `prior` (training a 224-frame component at an unreliable scale was not
     worth it); GPU used for SfM connectivity experiments instead (scratchpad `sfm_exp.sh`: A = temporal 30 +
     retrieval 30, B = A's matches with the incremental mapper, C = ALIKED + LightGlue) (resolved: n/a).
  5. 15:44–16:19 SfM experiments on the 894 pose-free keyframes (scratchpad `sfm_exp.sh`, SfM only):
     A (SIFT, `--temporal 30 --retrieval 30`, global mapper): round 0 [237, 234, 150, 65, 24, 20, 3], after the bridge
     round **[409, 234, 65, 24]**; B (A's matches, incremental mapper): [194, 141, 110, 22, 20]; C (`--feature aliked`
     ALIKED + LightGlue, `--temporal 30 --retrieval 30`, global mapper): **one component, 761 / 894** (no bridge needed).
  6. Scale sources checked on C (none reliable for this capture): ARCore Sim3 per tracking stretch gives scales
     0.06–3.3 (stretch 5's ARCore path spans 7.3 m around one doorway); ARCore depth maps: only 17 keyframes within
     40 ms of a map, scale 0.10–0.42 by part of the video; Metric3D: calibrated on rooms with good ARCore scale,
     Metric3D ÷ ARCore scale = 0.83 newRoom, 0.93 roomAttemptSadness2, 0.52 lecture hall (`sfm_scale_check.py` on
     `sparse/0`, 1 / ratio_median vs report.json sim3_scale), so not a usable fallback either.
     **Correction to R-045 error 3:** `ratio_median` is against the raw COLMAP model (`sparse/0`, arbitrary units), so
     6.86 is not a 7x metric error; R-045's Metric3D vs ARCore scales were 0.146 vs 0.207 (~30% apart).
  7. 16:2x export of C (`work_v9pf_sfmC` renamed to `work_v9pf_sfm`; the SIFT model kept as `work_v9pf_sfm_sift`):
     226 of 761 frames dropped as jumps > 30 cm (many of C's frames are placed absurdly: raw extent ~90 km), 535 kept,
     covering the whole video (0–188 s); Sim3 to ARCore 26 inliers, median 5.0 cm, scale 0.558 (unreliable, see 6);
     kept cameras' height spread 2 m (p5–p95), 1% of steps > 3.4 m: some wrong placements remain.
  8. 16:3x continued: `GPU_EVERY=120 bash scripts/run_full.sh dataset/scan_009_057ed3beb4fc v9pf --from export --
     --pose_free --sfm_args "--feature aliked --temporal 30 --retrieval 30" --init fmvs --planar 0.2 --blur 0.0222 --pgsr`
  9. 16:57 layout — same `IndexError` as R-045 (no floor / ceiling: the walk films upper walls, cabinets, AC and
     curtains; the floor is hardly in view). Fixed in `layout.py`: the plan uses all opaque splats when no floor /
     ceiling is found instead of crashing; re-run by hand: completes, 2 walls, no height (resolved: yes). The rest of
     run_full (semantics, mesh, web) not run: not meaningful on this model.
- **Start → end:** 15:37 → 17:0x (select 15:37; SIFT SfM; stopped 15:5x; SfM tests 15:44–16:19; 16:23 → 16:57
  export → ply: export 0.01, prior 3.15, init 4.78, train 25.13, ply 0.93 min)
- **Result:** `dataset/scan_009_057ed3beb4fc/work_v9pf_sfm/gs_v9pf/splat.ply` (534,096 Gaussians); web copy
  `prototype/web-ui/public/splats/scan009_v9pf.spz` (10.1 MB, local), project `scan-009-posefree`. Renders at 8
  training views over the walk (scratchpad `r046_views.jpg`): recognisable but soft, smeared dark cabinet doors (45 s)
  and curtain; top-down (`r046_topdown.jpg`): camera path with long jumps, splats spread over ~9 x 11 m. No held-out
  metrics. Scale unreliable (error 6).
- **Verdict:** inconclusive. Pose-free selection + ALIKED SfM register the whole walk where R-045 got 87 frames, so
  frames without an ARCore pose are usable; but this capture's blur and ARCore drift still leave misplaced cameras and
  no metric scale: record again. Follow-ups: test `--pose_free` and `--feature aliked` on newRoom (does it change a
  good capture?), and a stricter mis-registration filter (reprojection / neighbour consistency, not just 30 cm jumps).

### R-047 · 2026-11-18 · scan_009_057ed3beb4fc: R-046's model with the gyro rotation check (`v9pfg`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 1ccc414 (uncommitted changes: yes: new `gyro_check.py`,
  `sfm_colmap.py --gyro_thr`, `texture_probe.py`, the plan)
- **Dataset:** scan_009_057ed3beb4fc (894 pose-free keyframes of R-046, 188 s); R-046's ALIKED SfM model reused
  (`work_v9pf` and `work_v9pf_sfm` copied to `work_v9pfg` / `work_v9pfg_sfm`, the R-046 folders untouched)
- **Command(s):** `python src/arcore3dgs/run_v8.py --dataset dataset/scan_009_057ed3beb4fc --tag v9pfg --from_stage export
  --pose_free --sfm_args "--feature aliked --temporal 30 --retrieval 30 --gyro_thr 2" --init fmvs --planar 0.2
  --blur 0.0222 --pgsr`
- **Goal:** FEATURELESS_TRACKING_PLAN step 1 (D-080). Before the run, `gyro_check.py` on the same model: newRoom
  (v9e2e SfM, 1,166 frames) pair error median 0.15°, p99 frame score 1.03°, 3 frames over 2°; scan_009 (761 frames)
  pair error median 1.41°, p90 16.9°, 330 frames over 2°, of them 185 of the 226 frames R-046's 30 cm jump filter
  dropped and 144 of the 535 it kept. Does dropping the gyro-flagged frames (before the Sim3 and the jump filter) give
  a continuous camera path and a cleaner model than R-046?
- **Start → end:** 00:2x → 01:06 (false start and init fix included); stage times: export 0.01, prior 2.47, init 3.88,
  train 25.25, ply 0.63 min (total 32.2 from export)
- **Errors during the run:**
  1. 00:2x run_v8 `--from_stage export` is the *nerfstudio* export; sfm_colmap's export (where `--gyro_thr` acts)
     runs inside the `sfm` stage, so the run started training R-046's 535 frames unchanged. Stopped by the agent at
     the prior stage (only this run's python processes). Fix: `sfm_colmap.py --stage export` by hand (below), then
     run_v8 `--from_stage export`. Resolved: yes.
  2. Not an error: `No module named 'triton'` at the nerfstudio export, as in every run on this PC.
  3. 00:32 init (`fast_mvs.py`): `OSError: [WinError 145] The directory is not empty: ...\work_v9pfg_sfm\undist_fast\images`.
     Cause: `cp -r` of R-046's folder copied the `undist_fast/images` directory link as a real folder, which
     `toolpaths.unlink_dir` refuses to remove (by design). Fix: deleted `work_v9pfg_sfm/undist_fast` (the agent's own
     copy), resumed `--from_stage init`. Resolved: yes. Lesson: copy work folders without `undist_fast/`.
  - Prior stage output: 370 frames in 134 s, Metric3D aligned median error 3.6%; `sfm_scale_check`: "PART OF THE
    MODEL SHRUNKEN" (blocks at frame_02280, frame_03707, frame_04153; 96 frames < 0.5x of the median ratio).
- **SfM export with the gyro check** (`sfm_colmap.py --work …/work_v9pfg --out …/work_v9pfg_sfm --feature aliked
  --temporal 30 --retrieval 30 --gyro_thr 2 --stage export`, log `sfm_export_v9pfg.log`): 761 registered, 330 dropped
  by the gyro check (time offset 85 ms), then 61 by the 30 cm jump filter → **370 frames** (R-046: 535). Sim3 29
  inliers of 130 trusted, median 2.4 cm (R-046: 26 of 211, 5.0 cm), scale 0.481 (R-046: 0.558; neither reliable).
  Camera path (SfM units, speed between consecutive keyframes ÷ median): steps > 5× median 21 (R-046: 51), p99
  12.3× (16.1×). Keyframes per 15 s: [49, 31, 62, 21, 5, 33, 10, 37, 44, 40, 14, 5] (R-046: [55, 31, 68, 34, 17,
  35, 20, 55, 59, 64, 49, 22]): 60–75 s and the end are now thin.
- **Result:** `dataset/scan_009_057ed3beb4fc/work_v9pfg_sfm/gs_v9pfg/splat.ply` (562,769 Gaussians).
  - Training-view PSNR on the 367 keyframes both models kept (half res, scratchpad `render_compare.py`): R-046 median
    18.84 dB, R-047 **19.86 dB** (+1.03 dB, better on 78% of frames). Not a held-out test: R-047 trained on 370 frames
    instead of 535, which by itself makes each training view easier to fit.
  - Inside R-046, the 144 frames the gyro flagged fit only slightly worse than the 391 it accepted (median 18.29 vs
    18.81 dB): weak evidence that they were misplaced.
  - Photo | R-046 | R-047 sheet (8 common frames): R-047 sharper on the door at 0 s and the ceiling lamp at 36 s,
    similar on the curtain / AC, worse at 125 s (door into the bathroom: dark smear with a green speck).
  - Top-down: camera path more compact than R-046's but still with long straight jumps; opaque splats still spread
    over ~8 × 12 m (p1–p99), far larger than the room: floaters / misplaced geometry remain.
  - `sfm_scale_check`: part of the model shrunken (3 blocks), the GLOMAP "mini room" problem of OD-11, which a
    rotation check cannot see.
- **Verdict:** inconclusive (slight improvement). The gyro check removes rotation-inconsistent cameras and halves the
  big path jumps, but the remaining errors are position / scale errors with consistent rotation. Next: a position
  check (step 4, or the IMU-bridged position of `fallback.py` as a bound) and the incremental mapper on this capture
  (OD-11). `--gyro_thr` stays off by default.


### R-048 · 2026-11-18 · scan_009_057ed3beb4fc: incremental mapper on R-046's ALIKED matches, with the gyro check (`v9pfm`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 1ccc414 (uncommitted changes: yes: `gyro_check.py`,
  `sfm_colmap.py --gyro_thr`, the plan, R-047 records)
- **Dataset:** scan_009_057ed3beb4fc, R-046's 894 pose-free keyframes (`work_v9pf` copied to `work_v9pfm`) and its
  ALIKED feature / match database (`database.db`, `pairs.txt` copied to `work_v9pfm_sfm`; no re-extraction or
  re-matching)
- **Command(s):** `python src/arcore3dgs/sfm_colmap.py --work …/work_v9pfm --out …/work_v9pfm_sfm --feature aliked
  --temporal 30 --retrieval 30 --mapper mapper --gyro_thr 2 --stage {map, undistort, export}`, then `python
  src/arcore3dgs/run_v8.py --dataset dataset/scan_009_057ed3beb4fc --tag v9pfm --from_stage export --pose_free
  --sfm_args "--feature aliked --temporal 30 --retrieval 30 --mapper mapper --gyro_thr 2" --init fmvs --planar 0.2
  --blur 0.0222 --pgsr` (scratchpad `r048.sh`)
- **Goal:** R-047 left position / scale errors (long path jumps, a shrunken block) that a rotation check cannot see.
  Does COLMAP's incremental mapper (correct but partial on the lecture hall, R-038; OD-11) give a cleaner model of
  scan_009 than GLOMAP (R-046 / R-047)? Compared on frames placed, path jumps, the scale check and renders.
- **Start → end:** 01:13 → 02:27 (stopped by the agent at the prior stage); map round 0 01:13 → ~01:36 (components
  [417, 191, 40, 20, 2]), bridge matching (477 × 84 → 40,068 pairs) → 01:50, map round 1 01:50 → 02:25 (**[684, 3]**),
  undistort + export 02:25 → 02:26
- **Errors during the run:**
  1. 02:26 export: Sim3 to ARCore scale **182.3** from 28 inliers (meaningless), so the 30 cm jump filter, which works in
     metres after the Sim3, dropped 303 frames → 209 left. Not a crash: a design weakness (the jump filter trusts the
     ARCore scale). Training of these 209 frames stopped at the prior stage (only this run's processes).
- **Result:** gyro check on the 684-frame model: pair error median 0.85° (GLOMAP R-046: 1.41°), p90 4.0°, 172 frames
  over 2°. Accelerometer test (`imu_scale.py`, 1 s triplets): scale 0.72 with fitted |g| 1.86 m/s² (should be 9.81);
  per 15 s window scale −0.26 … 78. Like GLOMAP's model, locally inconsistent with the phone's motion.
- **Verdict:** rejected. One large component, but locally wrong; most likely wrong matches between look-alike places
  (repeated cabinet doors, plain walls) in both mappers. Next: reject image pairs whose two-view rotation disagrees
  with the gyro, then map again (R-050).

### R-049 · 2026-11-18 · scan_009_057ed3beb4fc: SfM export only, gyro check + placing unplaced frames (`v9pfp`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC (CPU only, while R-048's mapper ran)
- **Branch / commit:** `docs/featureless-tracking-plan` @ 1ccc414 (uncommitted: `known_rot_pnp.py`,
  `sfm_colmap.py --place_unplaced`)
- **Dataset:** scan_009, R-047's GLOMAP model copied (`sparse`, `undist`, `database.db`, the 761 undistorted images)
  into `work_v9pfp_sfm`; keyframes copied to `work_v9pfp`
- **Command(s):** `python src/arcore3dgs/sfm_colmap.py --work …/work_v9pfp --out …/work_v9pfp_sfm --feature aliked
  --gyro_thr 2 --place_unplaced 4 --stage export`
- **Goal:** FEATURELESS_TRACKING_PLAN step 4 (points part). Before the run, on newRoom (`known_rot_pnp.py`, cut gaps,
  rotation from the gyro, matches subsampled; position error in cm, ok = < 10 cm): 2 s gaps, 3 matches: known rotation
  median 0.8 / p90 4.9 / ok 95% (PnP RANSAC: impossible with 3); 5 matches: 0.8 / 3.0 / 96% (PnP 1.2 / 7.3 / 91%);
  9 s gaps, 5 matches: 1.8 / 12.0 / 88% (PnP 2.7 / 396 / 76%); with all matches PnP is slightly better (0.6 vs 1.2 cm
  at 9 s) because the gyro rotation adds its own error. Question: how many of scan_009's unplaced frames does it place,
  and is the path cleaner?
- **Start → end:** 01:2x → 01:3x (export only, ~1.5 min per attempt)
- **Errors during the run:**
  1. `FileNotFoundError: …\work_v9pfp_sfm\undist\images\frame_00001.jpg`. Cause: R-046's undistorted images are in
     `<sfm>/images`, `undist/images` no longer exists there, and the new code wrote the placed frames' undistorted
     images into `undist/images`. Fix: placed frames are undistorted straight into `<sfm>/images`; the 761 images
     copied into the test folder. Resolved: yes.
- **Result (export):** gyro check dropped 330; **placed 157 of 442** unplaced frames (>= 4 inliers, >= 50% inlier ratio,
  within 15 s of an accepted frame); then the jump filter dropped 112 → 476 frames, of which 90 are newly placed
  (R-047: 370). Path: steps > 5× median speed 40 (R-047: 21, R-046: 51); keyframes per 15 s [48, 34, 68, 26, 16, 34,
  10, 54, 54, 63, 24, 16]. Sim3 26 inliers, scale 0.845 (unreliable).
- **Verdict:** inconclusive, not trained. More of the walk is covered but the path is less clean than R-047: on this
  capture the 3D points the frames are matched to were partly built from misplaced cameras. Next: stricter acceptance
  (more inliers, position bounded by the IMU-bridged motion from the neighbours) and a cleaner base model (R-048).

### R-050 · 2026-11-18 · scan_009_057ed3beb4fc: why SfM fails locally (diagnosis, no training)

- **Who / machine:** Tayyab (agent, night session) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 1ccc414 (uncommitted: `imu_scale.py`, `gyro_pairs.py`)
- **Dataset:** scan_009 (R-046 GLOMAP model, R-048 incremental model, their ALIKED databases)
- **Command(s):** `imu_scale.py` (pre-integrated accelerometer scale, per-window scale in scratchpad `local_scale.py`);
  `gyro_pairs.py dataset/scan_009… work_v9pfm work_v9pfm_sfm --write work_v9pfx_sfm`; short-range-only mapping
  (pairs < 5 s apart, `work_v9pft_sfm`, `sfm_colmap.py --stage map --bridge 0`); 1-s displacement ratio SfM / ARCore
  (scratchpad `comp_check.py`); `fallback.calibrate` (gyro vs ARCore at 30 Hz)
- **Goal:** find why R-046 – R-048 are locally wrong, before choosing a fix.
- **Start → end:** 02:00 → 02:55
- **Errors during the run:** none (findings below).
- **Result:**
  1. Accelerometer scale per 15 s window: newRoom 0.48 – 0.93 (mostly 0.6 – 0.7); scan_009 GLOMAP −4.5 … 24,
     incremental −0.26 … 78. 1-s displacement ratio SfM / ARCore: newRoom spread p90/p10 1.3×; scan_009 ~800 – 1,500×.
  2. Gyro pair test (`gyro_pairs.py`): newRoom rejects 0.2% of 23,834 verified pairs; scan_009 only 0.6% of 12,681.
     Wrong matches between look-alike places are NOT the main cause.
  3. Short-range matches only (< 5 s): 13 components (11 – 127 frames), still inconsistent with ARCore.
  4. ARCore itself on scan_009: gyro vs ARCore angular velocity correlation **0.343** (bedroom 0.994), its own
     keyframe poses fail the accelerometer test (scale 0.014; bedroom 1.01, newRoom 0.94). The IMU data is clean
     (201 Hz, monotonic, |a| 9.84); ARCore barely tracked this room, so ARCore poses are not a usable reference here.
  5. `check_capture.py`: video ↔ pose sync PASS (offset +0.05 s, correlation 0.45), 1.5% dropped video frames.
- **Verdict:** diagnosis. The IMU is the only trustworthy signal on scan_009; image-based SfM (blur 21.7 px median,
  plain / repeated surfaces) gets rotations roughly right (0.85 – 1.4° vs gyro) but positions locally wrong. Next:
  rotations from the gyro + positions from image directions and the accelerometer together (`rot_sfm.py`, R-051).
  Also tried: VGGT (learned poses, plan step 2) code and weights fetched to `C:\Users\tyb\.cache\buildscan` (outside
  the repo), but running downloaded third-party code was blocked by the session's permission check: needs Tayyab's OK.

### R-051 · 2026-11-18 · scan_009_057ed3beb4fc: gyro-rotation + accelerometer SfM (`rot_sfm.py`, `v9pfr`)

- **Who / machine:** Tayyab (agent, night session) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 1ccc414 (uncommitted: `rot_sfm.py`, gyro bias in
  `gyro_check.py`, `Orientation(bg=…)` in `gyro_pairs.py`, `sfm_colmap.py --sim3 none`)
- **Dataset:** scan_009, 894 pose-free keyframes (`work_v9pfm` copied to `work_v9pfr`), R-048's ALIKED database
- **Command(s):** `python src/arcore3dgs/rot_sfm.py dataset/scan_009… …/work_v9pfm …/work_v9pfm_sfm …/work_v9pfr_sfm
  --triangulate_only`; `sfm_colmap.py --work …/work_v9pfr --out …/work_v9pfr_sfm --feature aliked --sim3 none --stage
  {undistort, export}`; `run_v8.py --dataset dataset/scan_009… --tag v9pfr --from_stage export --pose_free --init mono
  --planar 0.2 --blur 0.0222 --pgsr`
- **Goal:** a locally correct camera path for scan_009 from the phone's sensors: rotations from the gyro (bias
  removed, 0.134°/s on this capture), positions from pair directions (fixed rotation, 2-point RANSAC) + the
  pre-integrated accelerometer in one linear system (metric, gravity per 15 s segment), then COLMAP triangulation with
  the poses fixed. Validation on newRoom first (below).
- **Validation on newRoom (trusted SfM model, metric via ARCore 0.668):** gyro bias 0.055°/s; accelerometer-only
  1-s steps 1.16× true (p10–p90 1.01–1.33), |g| 9.79. Development history: homogeneous direction equations collapsed
  the path (steps 0.02 – 0.07× true); fixed-length direction equations fixed it. Final: Sim3 scale 0.936 (1.0 =
  exact), 1-s step ratio median 0.98 (spread p90/p10 7×), position error median 63 cm; after COLMAP BA 71 cm, spread
  5.5×. Much less accurate than normal SfM where normal SfM works (newRoom); meant only for captures where it fails.
- **scan_009 solve:** 6,765 pair directions (dt ≤ 20 s, parallax ≥ 1°) from 12,681 verified pairs; all 894 keyframes
  connected (accelerometer links up to 2 s); direction residual median 2.9°, p90 40°; |g| 9.85; 706 cameras with
  median edge residual < 10°. Triangulation with the poses fixed: **23,508 points, reprojection error median 1.76 px**
  (R-046 GLOMAP model: 9,349 points): the images agree with these poses.
- **Export (`--sim3 none`):** 698 frames (only 8 dropped by the 30 cm jump filter; R-047: 61).
- **Start → end:** 03:27 → 04:41; export 0.01, prior 4.41 (698 frames, Metric3D aligned median error 7.4%), init
  (fast_mvs) 2.19, train 22.78, ply 0.58 min (30.0 from export)
- **Errors during the run:**
  1. Not a crash: **metric scale probably 2 – 3× too large.** Model depth ÷ Metric3D depth per frame median 3.03
     (p10–p90 1.22 – 4.82; on the good rooms Metric3D reads 7 – 17% low, i.e. ~1.1 – 1.2 expected); cameras spread
     7.5 × 7.0 m horizontally and 1.7 m vertically (p5–p95), too large for a bedroom. The accelerometer alone ran 16%
     long on newRoom; with scan_009's weaker image directions the drift is larger. Training continues (it depends on
     consistent poses more than on absolute scale); the scale needs another source (open).
- **Result:** `dataset/scan_009_057ed3beb4fc/work_v9pfr_sfm/gs_v9pfr/splat.ply` (457,058 Gaussians; opaque extent
  p1–p99 22.6 × 31.8 m: the inflated scale). Training-view PSNR on shared keyframes, each model against its own
  undistorted photos (scratchpad `render_compare.py`): vs R-047 on 311 frames 18.38 vs **19.90 dB** (−1.92, better on
  33%); vs R-046 on 440 frames 18.53 vs 18.86 (−0.28). Photo | R-047 | R-051 sheet: R-051 visibly blurrier (curtain,
  door at 0 s, AC unit).
- **Verdict:** rejected. The gyro + accelerometer positions connect the whole walk and the images triangulate with
  them, but they are not accurate enough for sharp splats, and the scale is ~2 – 3× off. R-047 stays the best
  scan_009 model. `rot_sfm.py` kept as an experiment (not in the pipeline).

### R-052 · 2026-11-19 · scan_009_057ed3beb4fc: R-051's gyro + accelerometer poses refined by bundle adjustment (`v9pfb`)

- **Who / machine:** Tayyab (agent, night session, asked: "work on featureless overnight") · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 57db57a
- **Dataset:** scan_009, R-051's triangulated model (`work_v9pfr_sfm/sparse/0`, 706 cameras, 23,508 points) and its
  ALIKED database, copied to `work_v9pfb_sfm`; keyframes `work_v9pfr` copied to `work_v9pfb`
- **Command(s):** (1) `COLMAP bundle_adjuster` on the copy (free BA; kept as `work_v9pfb_sfm/sparse_freeba`, log
  `ba_v9pfb.log`); (2) new `python src/arcore3dgs/prior_ba.py work_v9pfr_sfm/sparse/0 work_v9pfb work_v9pfb_sfm/sparse/0
  --colmap …COLMAP.bat` (defaults: relative rotation sigma 0.1° + 0.1°/s, relative position sigma 0.02 + 30% of the
  step, Huber 2 px; log `prior_ba_v9pfb.log`); checks `gyro_check.py`, `imu_scale.py`; then
  `dataset/scan_009…/r052.sh`: `sfm_colmap.py --work …/work_v9pfb --out …/work_v9pfb_sfm --feature aliked --sim3 none
  --stage {undistort, export}` and `run_v8.py --dataset … --tag v9pfb --from_stage export --pose_free --init mono
  --planar 0.2 --blur 0.0222 --pgsr` (log `run_v9pfb.log`)
- **Goal:** R-051's poses connect the whole walk and the images triangulate with them (1.76 px), but the splats were
  blurrier than R-047: the poses were kept fixed. Does letting the images refine them (starting from the sensor
  solution instead of SfM's own) give sharper splats without falling back into R-046 – R-048's locally wrong path?
  Checked by the gyro agreement, the accelerometer test and training-view PSNR against R-047.
- **Start → end:** 01:33 →
- **Errors during the run:**
  1. 01:33 first free BA: `NO_CONVERGENCE` after 100 iterations (cost 1.03 → 0.886 px); a retry with
     `--BundleAdjustment.max_num_iterations` failed: `unrecognised option` (COLMAP 4.2 calls it
     `--BundleAdjustmentCeres.max_num_iterations`). Redone from R-051 with 1,000 iterations and intrinsics fixed: same
     0.886 px, still NO_CONVERGENCE (flat). Not a failure of the run, see the result.
- **Result so far (01:45):**
  - Free COLMAP BA pulls the rotations away from the gyro: `gyro_check` pair error median 0.27°, p90 3.08°, **106 of 706
    frames over 2°** (R-051 as solved: 0.07° / 0.13°, 2 frames). The images alone drag the path back toward the locally
    wrong SfM solution, so a free BA is not usable here.
  - **`prior_ba.py`** (BA with the gyro / accelerometer solution as soft relative priors): reprojection median
    1.77 → **1.22 px** (p90 2.76 px), 2,945 of 125,228 observations > 4 px dropped after round 1; the relative
    rotations stay within 0.11° (median, p95 0.38°) of the gyro; positions moved median 0.18, p95 0.33 model units;
    path length ×0.968. `gyro_check`: pair error median 0.22°, p90 0.50°, **2 frames over 2°**. 111 s on the 3070.
  - Accelerometer test (`imu_scale.py`, 1 s, frames passing the gyro check), metres per model unit (1.0 = metric, as
    R-051 claims): R-051 0.548 (bootstrap p5–p95 0.21–0.50), prior BA 0.405 (0.05–0.49), free BA 0.111 (0.06–0.36,
    |g| 9.40). All say the model is larger than metric (agrees with R-051's Metric3D ratio 3.0), but the bootstrap
    ranges are wide: no reliable scale.
  - Looser priors change nothing: position sigma 0.05 + 100% or 0.1 + 300% of the step, rotation sigma 0.3 or 1.0°
    (+ same per s): reprojection median 1.21 – 1.22 px every time; the rotation-loose ones drift from the gyro (1.0°:
    p90 1.11°, 5 frames over 2°). The floor is the keypoints (blur), not the priors. Defaults kept.
  - Training 1 (`--init mono`, as R-051's TRAINING entry says; but R-051's log shows `fast_mvs`, so that entry's
    command line is wrong): export 698 frames (8 dropped by the jump filter), prior 4.1, init 0.1, train 22.0, ply 0.7
    min. Kept as `gs_v9pfb_mono`. PSNR (scratchpad `render_compare.py`, training views, half res): vs R-051 on 698
    frames 18.89 → 19.36 (+0.20 median diff); vs R-047 on its 311 frames 19.90 vs 19.36 (−0.73).
  - **Training 2 (`--from_stage init --init fmvs`, same as R-047 / R-051 in practice):** init 2.0 (22,491 points), train
    22.7, ply 0.8 min → `work_v9pfb_sfm/gs_v9pfb/splat.ply`. vs R-051 on 698 frames: median 18.89 → **19.54** (better
    on 65%, +0.49 dB median diff); vs R-047 on the 311 frames R-047 kept: median 19.90 vs 19.25, **mean 19.31 vs 19.30**
    (better on 37%). Not held out; R-047 fits fewer frames. Photo | R-047 | R-052 sheet: R-052 cleaner on the plain
    walls (34 s, 57 s, 109 s) and the bathroom door (125 s, no green / black smear); worse at 0 s (wall lamp missing)
    and 187 s (curtain and AC blurred). 0 s and 187 s show the same wall at the start and end of the walk: the loop
    does not close (rot_sfm only uses pairs < 20 s apart, so drift accumulates over the 3-min walk).
- **End:** 02:51
- **Verdict:** kept as the scan_009 model with the most coverage (698 frames vs 370); quality about equal to R-047
  (better in the middle of the walk, worse where the loop meets). `prior_ba.py` kept. Next: close the loop (R-071).


### R-071 · 2026-11-19 · scan_009_057ed3beb4fc: loop closure: gyro bias from far-apart image pairs, rot_sfm with all pairs, prior BA (`v9pfl`)

- **Who / machine:** Tayyab (agent, night session) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 57db57a (uncommitted: `prior_ba.py`, `gyro_loop_bias.py`,
  `rot_sfm.py --bg_json`)
- **Dataset:** scan_009, 894 pose-free keyframes (`work_v9pfm` copied to `work_v9pfl`), R-048's ALIKED database and
  calibration model (`work_v9pfm_sfm`)
- **Command(s):** `python src/arcore3dgs/gyro_loop_bias.py dataset/scan_009… …/work_v9pfm …/work_v9pfm_sfm --out
  …/gyro_loop_bias.json` (also `--linear`); `python src/arcore3dgs/rot_sfm.py dataset/scan_009… …/work_v9pfl
  …/work_v9pfm_sfm …/work_v9pfl_sfm --max_dt 300 --bg_json …/gyro_loop_bias.json --triangulate_only`; `prior_ba.py`
  (defaults); `sfm_colmap.py --sim3 none --stage {undistort, export}`; `run_v8.py --tag v9pfl --from_stage export
  --pose_free --init fmvs --planar 0.2 --blur 0.0222 --pgsr`
- **Goal:** R-052 does not close the loop: the start (0 s) and end (187 s) views of the same wall disagree. Check
  (scratchpad `loop_rot2.py`): each verified image pair's own rotation (5-point, essential matrix) against the gyro
  chain. Pairs < 5 s apart: 3.3° median (the noise of 5-point on these blurred images); pairs > 120 s apart: 14.7°
  median, all with nearly the same world error vector (yaw −14.2°, MAD under 2°): a **heading drift of the gyro**, i.e.
  the bias from `gyro_check` (fitted against the locally wrong SfM model) is off by ~0.08°/s. Fit the bias from all
  pairs, then let rot_sfm use far-apart pairs too (it used dt ≤ 20 s), so the walk closes on itself.
- **Start → end:** 02:55 → 03:50 (rot_sfm ~17 min, prior BA 1.7 min, export 03:16, prior 4.0, init 3.2, train 22.5,
  ply 0.5 min, done 03:47)
- **Errors during the run:** none.
- **Result:** `gyro_loop_bias.py`: 6,036 pairs with a 5-point rotation (4.6 min, cached in
  `work_v9pfm_sfm/five_point_pairs.npz`). Median residual per time gap, before → after (constant bias, Cauchy loss
  3°): 0–5 s 2.97 → 2.96°; 5–20 s 5.94 → 5.92°; 20–60 s 11.17 → 9.86°; 60–120 s 8.85 → 6.64°; **> 120 s 14.64 →
  3.52°**. Bias (deg/s, IMU frame) [−0.009, 0.088, −0.101] → [−0.032, 0.006, −0.090]. A bias linear in time gives the
  same (> 120 s: 3.54°), so the constant one is used. The 20–60 s pairs that still disagree (316, median 9.9°) are
  likely look-alike matches (not checked).
  - `rot_sfm.py --max_dt 300 --bg_json` (log `rot_sfm_v9pfl.log`): bias 0.095°/s removed; **9,015 pair directions**
    (R-051: 6,765 with dt ≤ 20 s); all 894 keyframes connected; direction residual median 3.47°, p90 39.2° after 15
    iterations; 698 cameras with median edge residual < 10°; triangulation (poses fixed) 23,490 points.
  - `prior_ba.py` (log `prior_ba_v9pfl.log`): 138,270 observations (R-052: 125,228: the far-apart pairs now share
    tracks), reprojection median 1.88 → **1.27 px** (p90 2.81); relative rotation vs the gyro prior median 0.10°,
    p95 0.33°. `gyro_check`: pair error median 0.19°, p90 0.47°, 1 frame over 2°.
  - **Loop check** (5-point rotation of each verified pair vs the model, scratchpad `loop_rot2.py`), median error,
    R-052 → R-071: pairs > 120 s apart **15.6° → 3.5°** (world error vector [0.4, −15.2, 1.4]° → [−0.2, −0.9, 0.3]°:
    the heading drift is gone); 60–120 s 8.6 → 7.4°; 20–60 s 11.8 → 9.5°; 0–5 s 3.2 → 3.2° (noise floor);
    5–20 s 7.8 → 13.6° on 53 pairs (worse; not explained yet).
  - Export: 680 frames (jump filter dropped 18). `sfm_scale_check`: ratio median 2.25 model units per Metric3D metre,
    **verdict "ok"**: the first scan_009 model without a shrunken block (R-046 – R-052 all "PART OF THE MODEL
    SHRUNKEN").
  - Points seen after 165 s that are also seen before 40 s (same wall at the start and end of the walk): **3,625 of
    5,603** (R-052: 115 of 2,268). Per 15-s window, every stretch reprojects at 0.75 – 1.33 px median per camera, but
    45 – 60 s and 90 – 105 s have a median of 0 and 3 3D points per camera: those cameras rest on the gyro +
    accelerometer only.
  - `→ work_v9pfl_sfm/gs_v9pfl/splat.ply`. Training-view PSNR (half res, scratchpad `render_compare.py`): vs R-047 on
    the 303 frames both kept: median 19.95 vs 19.08, mean 19.49 vs 19.32, better on 45%; vs R-052 on 625 frames:
    19.71 vs 19.70 (equal). Photo | R-047 | R-071 sheet: the start (0 s: wall lamp and door) now as sharp as R-047 (R-052
    lost the lamp); 45 s (wardrobe door) and 125 s (bathroom door) cleaner than R-047; 32 s, 95 s (door), 140 s and 187 s
    (curtain / AC) smeared. Not held out.
  - Scale (metres per model unit, none reliable): accelerometer (`imu_scale.py`) 0.368 at 1 s (bootstrap 0.16 – 0.48),
    0.477 at 2 s (0.25 – 0.61); Metric3D 1 / 2.25 = 0.44 (Metric3D read 7 – 17% low on the good rooms, so ~0.47 –
    0.53); `layout.py` room height 4.67 units → 0.56 – 0.64 if the ceiling is 2.6 – 3.0 m (not measured). The
    model is about 2× too large; no scale applied.
  - `layout.py` (`work_v9pfl_sfm/layout/`): 6 walls, corners at 40°, 73° and 45°: the room is not recovered as a
    clean rectangle (floaters and the partly IMU-only stretches), so the layout is not usable for measurements yet.
- **Verdict:** kept: **the most complete and consistent scan_009 model so far** (680 frames, loop closed, scale check
  ok), training-view quality about equal to R-047 (370 frames). Scale still unknown. `gyro_loop_bias.py` +
  `rot_sfm.py --bg_json --max_dt 300` + `prior_ba.py` is the recipe for captures where SfM fails.


### R-072 · 2026-11-19 · newRoomAttemptSadness: validation of the R-071 recipe against a trusted SfM path (no training)

- **Who / machine:** Tayyab (agent, night session) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 57db57a (uncommitted: `prior_ba.py`, `gyro_loop_bias.py`,
  `rot_sfm.py --bg_json`)
- **Dataset:** newRoomAttemptSadness, keyframes `work_v9e2e`, trusted model `work_v9e2e_sfm/sparse/0` (normal SfM,
  metric via the ARCore Sim3 0.668 m per unit)
- **Command(s):** `dataset/newRoomAttemptSadness/r054.sh` (log `r054.log`): `gyro_loop_bias.py`; `rot_sfm.py
  --triangulate_only` (dt ≤ 20 s, R-051 setting; pair directions from the cache in `work_rotsfm_vio`) →
  `work_rotsfm_tri`; `rot_sfm.py --max_dt 300 --bg_json … --triangulate_only` → `work_rotsfm_loop`; `prior_ba.py` on
  both (`sparse_pba`); evaluation scratchpad `eval_rot.py` (Sim3 to the trusted path, position error in metres)
- **Goal:** how much do the R-071 steps (bias from far-apart pairs, far-apart pairs in rot_sfm, BA with sensor priors)
  improve the camera path where the truth is known?
- **Start → end:** 03:50 → 04:24 (bias fit 5.0 min, rot_sfm 3.3 + 9.4 min, prior BA 7.7 + 7.0 min)
- **Errors during the run:** none.
- **Result:**
  - Bias fit: 15,242 pairs; correction small on this capture ([−0.033, 0.021, −0.038] → [−0.026, 0.017, −0.035]
    deg/s); pairs > 120 s apart 1.49 → 1.19° median (scan_009: 14.6 → 3.5°). The 5-point noise is much lower here
    (0–5 s pairs 0.61°; scan_009 2.97°).
  - Position error vs the trusted path (Sim3 fitted, median / p90), 1-s step ratio spread p90/p10, Sim3 scale (1.0 =
    exactly metric):

    | Camera path | Frames | Median | p90 | Step spread | Scale |
    |---|---|---|---|---|---|
    | rot_sfm, pairs ≤ 20 s, poses fixed (R-051 setting) | 1,075 | 72.2 cm | 166.0 cm | 5.16× | 0.684 |
    | same + `prior_ba.py` | 1,075 | 62.3 cm | 153.8 cm | 3.00× | 0.679 |
    | rot_sfm, all pairs + loop bias, poses fixed | 1,022 | 55.2 cm | 101.9 cm | 5.02× | 0.918 |
    | **same + `prior_ba.py` (R-071 recipe)** | 1,022 | **31.1 cm** | **68.4 cm** | **1.89×** | 0.893 |

    `prior_ba.py` reprojection median 0.67 / 0.66 px. R-051's validation recorded Sim3 scale 0.936 and 63 cm for the
    first row; today's re-run gives 0.684 and 72 cm (same code path except the bias / cache; not explained).
- **Verdict:** the R-071 recipe more than halves the position error of the sensor-based path (72 → 31 cm median) and
  makes the steps far more regular, but it is still much worse than normal SfM where normal SfM works (the trusted
  path). Use only for captures where SfM fails. One capture only; tuned settings are the defaults.
