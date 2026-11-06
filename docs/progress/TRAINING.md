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
| R-028 | 2026-11-06 | First Linux run: Umair's room, full v9 + PGSR → semantics → mesh → web | this PC (Ubuntu, RTX 4000 Ada) | running | — | — |

## Runs

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
- **Start → end:** 17:53 → (running)
- **Errors during the run:**
  1. 17:53 check_capture — `FileNotFoundError: 'ffprobe'` when run with the env's python directly: ffmpeg is in the
     env but only on `PATH` when the env is activated → run through `micromamba run -n bs-system` (resolved: yes;
     `run_full.sh` always uses `micromamba run`).
  2. 17:53 select — `FileNotFoundError: .../scan_056fe94d3399/imu.npz`: `select_sharp.py` loads the IMU cache but nothing
     in `run_v8.py` creates it (on Windows an earlier script had made it for every capture) → `select_sharp.py` now
     calls `imu.extract_imu()` when the cache is missing; restarted from `select` (resolved: see below).
- **Result:** (pending)
- **Verdict:** (pending)
