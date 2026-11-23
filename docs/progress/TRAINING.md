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

**Renumbered runs (2026-11-19, D-079).** Tayyab's runs on the RTX 3070 PC (2026-11-12 / 14) and Umair's runs on the
Ubuntu PC were both numbered R-032 – R-040 in parallel branches. When they met on `master`, Tayyab's nine got the next
free numbers; every reference in the records and code comments was changed with them. Older commit messages, issues
and file names on the 3070 PC (e.g. `gs_v10inc/topdown_vs_R-036.jpg`) still use the old numbers:

| Old (3070 PC, before 2026-11-19) | R-032 | R-033 | R-034 | R-035 | R-036 | R-037 | R-038 | R-039 | R-040 |
|---|---|---|---|---|---|---|---|---|---|
| **New** | R-062 | R-063 | R-064 | R-065 | R-066 | R-067 | R-068 | R-069 | R-070 |

R-032 – R-040 now always mean Umair's runs on the Ubuntu PC; R-041 – R-046 (Tayyab) did not collide and are unchanged.

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
| R-031 | 2026-11-12 | scan #3 `scan_003_6de634cbb8b2` (classroom, first v0.3.6 recording, 185 s), full pipeline (`--tag r1112`) | this PC (Ubuntu, RTX 4000 Ada) | 81.0 min (run_v8 64.7) | ran clean; 875/885 frames; **height 2.74 m** (plausible); 2 walls, 0 corners, 21 fixtures | Kept (`saved_models/2026-11-12_r1112_scan003/`); baseline stage times; quality and tape not measured |
| R-032 | 2026-11-12 | Layout diagnostics on scan #2 / #3 (read-only, plan 4.1) | this PC (Ubuntu, RTX 4000 Ada) | seconds per pass | models tilted 9.1° / 12.1° from ARCore gravity (Sim3 from camera centres only); levelled prototype: scan #3 4 walls, 3 corners ~90°, 2.52 m | Diagnosis
| R-033 | 2026-11-12 | `sfm_colmap.py --stage export` with ARCore gravity (D-071), scan #2 / #3, scratch output | this PC (CPU) | seconds | models level (0.06° / 0.00°); scale 0.0937 / 0.9521 (+0.45% on scan #3) | Kept
| R-034 | 2026-11-12 | `level_model.py`: levelled copies of scan #2 / #3 models (tags `r1106lev`, `r1112lev`) | this PC | seconds | rotated 9.09° / 12.10°; renders match the source at 85–98 dB (after an SH transpose bug, fixed) | Kept
| R-035 | 2026-11-12 | scan #3 levelled (`r1112lev`), layout → web | this PC | 18.0 min | 4 walls, 3 corners ~90°, height 2.52 m, floor 32.27 m², 18 fixtures | Kept (Step 4 layout / semantics of scan #3); tape pending |
| R-036 | 2026-11-12 | scan #2 levelled (`r1106lev`), layout → web | this PC | 8.5 min | height 1.50 → 2.41 m (wall-top rule), 1 wall, 10 fixtures | Inconclusive: weak capture (camera in 0.8 × 0.7 m); re-record |
| R-037 | 2026-11-12 | newRoomAttemptSadness, R-023 recipe, full pipeline (`r1112nr`), first run with D-071 / D-072 | this PC (Ubuntu, RTX 4000 Ada) | 103.0 min (run_v8 81.4) | 1157/1166 frames; gravity 0.00°; 6.63 × 4.37 m (R-023 6.60 × 4.36); height 2.81 m (R-023 2.72, via D-072); 18 fixtures (15) | Kept (machine agreement on size); height and PSNR not settled |
| R-038 | 2026-11-16 | scan_008_7b486c855ed6, R-023 recipe, full pipeline (`r1116`), first Infinix X6833B capture | this PC (Ubuntu, RTX 4000 Ada) | 49.7 min, did not finish | 1639 of 10255 frames; COLMAP `global_mapper` killed by OOM (26.1 GB) at 13:16 | Failed (OOM in SfM) |
| R-039 | 2026-11-16 | scan_008 re-run with `--window 9` (`r1116w9`, D-073), R-023 recipe otherwise | this PC (Ubuntu, RTX 4000 Ada) | 166.7 min (run_v8 145.4) | 1118/1118 frames; gravity 0.00°; 5 walls, floor 21.26 m², ceiling 3.19 m; 11 fixtures (unchecked) | Kept for now (in the web UI) |
| R-040 | 2026-11-18 | scan #7 `scan_007_e6d4f090f88e` (269 s), R-023 recipe, default window 6 (`r1118`) | this PC (Ubuntu, RTX 4000 Ada) | 200.6 min (run_v8 175.4) | 1159/1160 frames; gravity 0.00°; 6 walls, floor 19.66 m², ceiling 3.40 m; **0 fixtures (29 rejected)** | Inconclusive (fixtures) |
| R-041 | 2026-11-14 | newRoom: Fast training + PGSR-lite on newRoom (`pgsrfast`) | 3070 | 33.0 min train (R-021: 46) | 25.02 / 0.8232, sharpness 0.87 | Speed-ups OK with PGSR (R-021 flatness 1.27 vs 1.34 cm) |
| R-042 | 2026-11-14 | newRoom: MCMC with a larger budget (`mcmc1m`) | 3070 | 40.4 min train | 24.74 / 0.8200, sharpness 0.69 | Rejected |
| R-043 | 2026-11-14 | newRoom: revised opacity on clone / split (`revop`) | 3070 | 28.5 min train | 25.02 / 0.8244, flat 0.73 cm, −10% size | Inconclusive |
| R-044 | 2026-11-14 | newRoom: lower densification threshold (`dg4`) | 3070 | 30.8 min train | 25.07 / 0.8243, sharpness 0.85, +40% size | Inconclusive |
| R-045 | 2026-11-15 | scan_009_057ed3beb4fc: full v9 + PGSR pipeline (`v9pgsr`), capture failed check_capture | 3070 | 32.4 min to the model; layout crashed | 87 / 5,629 frames registered, partial, scale unreliable | Rejected (record again) |
| R-046 | 2026-11-15 | scan_009_057ed3beb4fc: pose-free keyframes + SfM tests; ALIKED SfM model (`v9pf`) | 3070 | 34.0 min from export (train 25.1) | 535 frames over the whole walk (R-045: 87); misplaced cameras remain, scale unreliable | Inconclusive |
| R-053 | 2026-11-19 | Layout re-runs on six rooms, no-roof check (#8), scratch output | this PC (Ubuntu, RTX 4000 Ada) | 8.8 min | scan #7: no roof, walls 3.12 m (was ceiling 3.435 m); 5 other rooms unchanged | Kept (#8) |
| R-054 | 2026-11-19 | scans #7 / #3: layout (#8 #9 #10) → semantics → mesh labels → web, tag `r1119a` | this PC (Ubuntu, RTX 4000 Ada) | 8.1 min | #7 no roof, 1 doorway + 3 window openings, open outline; #3 open outline flagged, triangle area gone, 4 false openings | Superseded (#9 fixed after it) |
| R-055 | 2026-11-19 | Layout on six rooms, `--debug`, default vs `--raised_max 1.5 --infer_gap 6` | this PC (Ubuntu, RTX 4000 Ada) | 16.9 min | scan #3 no false openings; `--raised_max` closes #7 and #8 (4 walls, 88–90°), drops nothing real | Kept (findings) |
| R-056 | 2026-11-19 | Four rooms, layout → web → plan with the 2026-11-19 defaults, tag `r1119b` | this PC (Ubuntu, RTX 4000 Ada) | 15.6 min | #7 no roof + 2 openings; #3 no false openings; newRoom closed, 29.41 m²; #8 open, 2 doorways | Kept (for Umair's checks) |
| R-057 | 2026-11-19 | Four rooms, layout → web → plan with the D-075 defaults, tag `r1119c` | this PC (Ubuntu, RTX 4000 Ada) | 16.7 min | #7 / #8 closed rectangles (17.99 / 26.44 m²); #3 tilt 0.29°; ceilings 4.3 → 0.04 cm; #8 lost a switch + socket | Kept (scan #8 corner = furniture, Umair) |
| R-058 | 2026-11-19 | scan #6 `scan_006_1e457a214ce1` (259.8 s), full pipeline, R-023 recipe + D-075 (`r1119`) | this PC (Ubuntu, RTX 4000 Ada) | 45.5 min, did not finish | 1159 frames, 12.56 M observations; COLMAP `global_mapper` killed by OOM (26.4 GB) at 16:14:39 while the agent ran web work | Failed (OOM in SfM) |
| R-059 | 2026-11-19 | scan #6 rerun after R-058, same recipe, PC kept quiet (`r1119b6`) | this PC (Ubuntu, RTX 4000 Ada) | 162.5 + 21.4 min | 1159/1159 frames; height 3.05 m, closed, 7 walls; 11 fixtures, 84 rejected | Kept (not checked by a person) |
| R-085 | 2026-11-23 | scan #6 fixture check sheet from R-059 (`fixture_checklist.py --rejected`, no GPU) | this PC (Ubuntu, RTX 4000 Ada) | (running) | — | — |
| R-062 | 2026-11-12 | Training speed-up: exact TV-loss / colour-affine fixes, blur colour grid once (`fast_t1`) | 3070 | 28.2 min train (was 42.5) | 25.14 / 0.8251, sharp 0.80, flat 0.81 | Kept (proposed) |
| R-063 | 2026-11-12 | Photometric-only fast-MVS init (`fast_t2_photo`) | 3070 | init 7.5 min (was 20.1) | 25.16 / 0.8240, flat 0.78 | Kept (proposed) |
| R-064 | 2026-11-12 | Global mapper settings (`ba1`, `noretri`, default rerun) | 3070 | mapper 9.4 – 14.5 min | default runs differ by ~16 cameras | Inputs to R-065 |
| R-065 | 2026-11-12 | Fast pipeline end to end incl. `--skip_retriangulation` (`v10fast`) | 3070 | 61.6 min (was 96.2) | 24.56 / 0.8078, visible smears | Rejected (SfM shortcut) |
| R-066 | 2026-11-12 | New room `scan_3028a4de8fa0` (tiered lecture hall), normal SfM + speed-ups | 3070 | 48.8 min | fits training views; mini room inside the room (SfM scale collapse, see R-067) | Rejected |
| R-067 | 2026-11-12 | `scan_3028a4de8fa0`: incremental mapper instead of GLOMAP (fix R-066 mini room) | 3070 (CPU) | map 25.4 min | 581/842 frames in one correctly scaled model; front of room split off | Diagnosis confirmed |
| R-068 | 2026-11-12 | `scan_3028a4de8fa0`: fast recipe on R-067's 581-frame SfM (`v10inc`) | 3070 | 35.8 min (+ map 25.4, R-067) | no mini room; right-side walk missing | Kept |
| R-069 | 2026-11-14 | roomAttemptSadness2: full v9 + PGSR → semantics → mesh → web (`v9pgsr8`) | 3070 | 87.7 min to the model + 32 min after | height 2.78 m; 22 fixtures (unchecked) | Kept (fixtures to check) |
| R-070 | 2026-11-14 | newRoom: MCMC densification at the baseline budget (`mcmc620`) | 3070 | 35.0 min train | 24.65 / 0.8216, sharpness 0.64 (softer) | Rejected |

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
- **Start → end:** 15:04:02 → 16:25:03 (81.0 min). run_v8 64.7 min (`timing.json`): select 0.37, SfM 12.11, export
  0.01, prior 3.56, init 14.76 (PatchMatch 14.5, fusion 0.2), train 33.57, ply 0.28. Then (`stages.tsv`) layout 0.4,
  sem2d 13.7, sem3d 0.1, verify 0.2, sem3d2 0.1, mesh 0.3, meshlabels 1.5, web 0.1. GPU (`gpu.csv`, every 30 s): up
  to 4.8 of 20.5 GB, 38–77 °C. Compared with R-030 (482 frames): run_v8 64.7 vs 41.7 min, train 33.6 vs 27.8, init
  14.8 vs 6.6, SfM 12.1 vs 4.9, sem2d 13.7 vs 7.7.
- **Errors during the run:** none (`run_full.log` has no tracebacks or errors).
- **Capture facts measured on 2026-11-12 (agent, from the dataset files, for COMPLETION_PLAN 1.6 / 1.7):**
  `check_capture.py`: READY TO PROCESS; **video 28.9 fps average, 176 dropped-frame gaps in 5,346 frames (3.3%),
  longest 99 ms** (NFR1 not met); poses 28.9 Hz, tracking lost 0.0%; predicted blur median 6.7 px (> 5 px on 75% of
  frames, > 10 px on 21%); exposure median 30.0 ms (range 10–30 ms), ISO median 842; rolling-shutter readout 28.2 ms;
  ARCore world corrections at 22.3 s (123 cm, 6.0°), 31.5 s (26 cm) and six smaller ones; video ↔ pose sync +0.05 s,
  r = 0.89. (A first count from `poses.csv` gaps gave 0.24% dropped; that count used a 1.5 × median threshold on pose
  timestamps and missed most gaps, so the video count is the one to use.) ARCore depth: 782 maps
  (160 × 90), all 782 different, median valid fraction 0.86, median depth 0–5.5 m across maps, mean confidence
  0–81: **not stale** in this recording. IQA levels in `quality.csv`: GOOD 1,279, WARN 2,894, BAD 1,164.
- **Result:** `dataset/scan_003_6de634cbb8b2/work_r1112_sfm/gs_r1112/` (`splat.ply` 124 MB, 522,615 splats), copied to `saved_models/2026-11-12_r1112_scan003/` with README.txt; web bundle
  `prototype/web-ui/public/scans/scan_003_6de634cbb8b2_r1112/` (18 MB). SfM (`report.json`): 875 / 885 frames
  registered, 114,929 points, Sim3 to ARCore scale 0.9478, 268 inliers, median 4.0 cm. Metric3D prior aligned median
  error 3.7% (raw 32.6%). Dense init: 472,582 points at 1 cm.
  **Layout:** floor y −8.329, ceiling y −5.588 → **height 2.741 m**; 2 walls (6.39 m, 2.57 m), 9.03 m apart, 0
  corners. **Semantics v10:** floor tilt 0.28° (median residual 7.2 cm); ceiling plane fit rejected (tilt 8.06°), so
  the ceiling was set level at the layout height (2.73 m); 21 fixtures accepted (1 door, 2 windows, 2 light switches,
  4 power sockets, 4 ceiling lights, 1 tube light, 3 lamps, 4 ceiling fans), 34 rejected; CLIP check kept all 6
  switches / sockets. Mesh 2,986,324 → 2,884,227 triangles; area by class (m²) other 161.47, ceiling 62.27, wall_0
  10.09, wall_1 3.40, floor 2.19, door 1.73; `mesh_web.glb` 400k triangles, 8.5 MB.
  **Height check (agent, 2026-11-12):** `analyze.py` (`feat/splat-compress`): model extent
  p1–p99 7.88 × 3.90 × 9.74 m. Splats with opacity > 0.5 span y −9.14 … −5.06 (p0.5–p99.5); the part below the floor
  is probably reflection of the glossy floor (3.13); the densest top band is −5.5 … −5.2, slightly above the layout
  ceiling, so the true height may be somewhat more than 2.74 m. Median camera height 1.74 m above the layout floor.
  Ceiling fans sit 2.34–2.58 m above the floor; `window_1` at 2.72 m (at the ceiling) is probably a wrong placement.
  **Not measured:** model quality (no held-out split; this run trains on all frames), tape lengths (Umair will measure
  the room, expected within a few days of 2026-11-12), room number.
- **Verdict:** **kept** as the first v0.3.6 room and as the stage-time baseline for COMPLETION_PLAN 3.3 / 3.4
  (D-069). The height is plausible (unlike R-030's 1.50 m) but unconfirmed until the tape; the layout found only 2 of
  the walls and no corners. To do: tape check; view the model (`scripts/buildscan view 3 r1112`).

### R-032 · 2026-11-12 · Layout diagnostics on scan #2 and scan #3 (read-only, COMPLETION_PLAN 4.1)
- **Who / machine:** Umair (agent) · this PC (Ubuntu, RTX 4000 Ada)
- **Branch / commit:** `feature/step4-layout` @ `99f8efe` (uncommitted changes: no; the script is a copy of
  `layout.py` steps 1–2 plus prints, kept in the agent's scratchpad, not in the repo)
- **Dataset:** scan #2 (`scan_002_646070948603`, R-030 model `gs_r1106`), scan #3 (`scan_003_6de634cbb8b2`, R-031
  model `gs_r1112`)
- **Command(s):** `micromamba run -n bs-ns python diag_layout.py --ply <gs>/splat.ply --work <work_sfm> --out <scratch>`
  (same defaults as `layout.py`; writes nothing into `dataset/`)
- **Goal:** find why R-030's layout took a plane at 1.50 m as the ceiling: the horizontal plane candidates (height
  histogram), the camera heights that bound the floor / ceiling search, and the splat height histogram.
- **Start → end:** 17:59 → before 18:20 (exact end not recorded); several diagnostic passes of a few seconds of GPU
  rendering each, the time in between was analysis.
- **Errors during the run:** none (one diagnostic script was first run with the system `python3`, which has no numpy;
  re-run in `bs-ns`).
- **Result:** the 1.50 m ceiling and the 2-wall classroom have **one root cause: the models are not level.** The
  Sim3 to ARCore in `sfm_colmap.py` (export) takes its rotation from camera centres only. ARCore's own gravity
  (each frame's `c2w_arcore` orientation) expressed in the model world is **9.11° off +Y in scan #2 and 12.10° in
  scan #3**, the same in every frame (per-frame angle median 9.26° / 12.09°, spread < 1°). The planes agree: in
  scan #3 the floor, desk-top and ceiling regions are all tilted 11.8–12.5° the same way; in scan #2 6.6–8.2°.
  Scan #2's camera centres span only 0.8 × 0.7 m (the walk was mostly turning on the spot), so centres cannot fix
  the rotation; in scan #3 the RANSAC inliers are 268 / 885 frames.
  Consequences in `layout.py` (which assumes +Y is up): (1) scan #3: 807 of 3,982 flat regions (more pixel weight than
  all vertical ones) have |n·up| ≈ 0.21 and are dropped as neither wall nor floor: these are the two long side
  walls, hence 2 walls / 0 corners; (2) heights are measured along a tilted axis (12° over 9 m ≈ 1.9 m of height
  change across the floor), so 2.74 m was not a real height; semantics' "floor tilt 0.28°" only fits a ±15 cm band
  and so sees a level patch.
  Scan #2 has a second, model problem: the white tiled ceiling appears at three heights in different frames
  (0.3–0.5 m above the cameras when seen overhead, y ≈ 0.9 partly as a **reflection in the door glass**, y ≈ 1.6 when
  seen across the room); the layout took the strongest, lowest one (1.50 m). Its walls reach 2.28–2.65 m.
  **Prototype (scratchpad copy of `layout.py`, world levelled with ARCore gravity, same model, no retraining):**
  scan #3 → **4 walls, 3 corners at 89.5°, 89.8°, 88.9°, walls 7.23 m and 9.05 m apart, one clean ceiling peak at
  2.52 m** (walls reach 2.36–2.44 m; splat top p99 2.70 m); scan #2 → 1 wall, ceiling still 1.79 m (0.4 m above the
  cameras: impossible); with "the ceiling may not lie below the top of the walls" 2.41 m. Without levelling that
  rule alone gives scan #2 2.78 m, scan #3 2.83 m (tilted axis, so not trustworthy).
- **Verdict:** diagnosis (no model changed). Cause found; fix options for Umair (DECISIONS). Heights still need the tape.

### R-033 · 2026-11-12 · `sfm_colmap.py --stage export` with ARCore gravity (D-071) on scan #2 / #3, into scratch folders
- **Who / machine:** Umair (agent) · this PC (Ubuntu, RTX 4000 Ada); CPU only
- **Branch / commit:** `feature/step4-layout` @ `8f8e605` + uncommitted `sfm_colmap.py` change (the D-071 export)
- **Dataset:** scan #2 (`work_r1106_sfm`, R-030's COLMAP model), scan #3 (`work_r1112_sfm`, R-031's)
- **Command(s):** `micromamba run -n bs-system python src/arcore3dgs/sfm_colmap.py --work dataset/<scan>/work_<tag>
  --out <scratch>/exp_<tag> --stage export` with `<scratch>/exp_<tag>/{sparse,undist,images}` linked to the existing
  `work_<tag>_sfm/` (nothing written into `dataset/`)
- **Goal:** check the new export: the printed tilt a centre-only Sim3 would leave must match R-032 (9.1° / 12.1°),
  the new frames.json must be level (ARCore gravity on +Y), scale and inliers comparable with R-030 / R-031.
- **Start → end:** start not recorded (after R-032) → 18:22 (export only, seconds per scan)
- **Errors during the run:** none. One wrong reading of my own diagnostic, corrected before commit: the first version
  printed "centre-only Sim3 would leave the model X deg off gravity" computed on the **new** inlier set (scan #3:
  0.74°), which is not what R-031's RANSAC did (it picked a different 268-frame set that absorbed 12.1°). Renamed
  to `gravity_tilt_full_sim3_same_inliers_deg`, "for comparison" only.
- **Result:** scan #2: scale 0.0937 (R-030 0.0937), 244 / 482 centre inliers (242), median 5.4 cm (5.25); scan #3:
  scale **0.9521** (R-031 0.9478, +0.45%), 276 / 885 inliers (268), median 5.7 cm (4.0; higher because the old
  fit could tilt the model to absorb ARCore position noise). Checked independently (`gravcheck`): ARCore gravity
  now 0.06° (scan #2) and 0.00° (scan #3) from +Y; per-frame spread 0.85° / 0.98° (ARCore's own noise).
  Outputs only in the scratchpad; `dataset/` untouched (`work_r1112_sfm/frames.json` still 15:16).
- **Verdict:** kept: the export levels both models. Not yet run end to end on a new recording (the next new room is
  the first). The +0.45% scale change on scan #3 is within what the tape must decide.

### R-034 · 2026-11-12 · `level_model.py`: levelled copies of the scan #2 and scan #3 models (D-071)
- **Who / machine:** Umair (agent) · this PC (Ubuntu, RTX 4000 Ada)
- **Branch / commit:** `feature/step4-layout` @ `ec170c7` + uncommitted new `src/arcore3dgs/level_model.py`
- **Dataset:** scan #2 (`gs_r1106`, R-030) → tag `r1106lev`; scan #3 (`gs_r1112`, R-031) → tag `r1112lev`
- **Command(s):** `micromamba run -n bs-ns python src/arcore3dgs/level_model.py --dataset dataset/<scan> --tag <tag>
  --new_tag <tag>lev --check 3`
- **Goal:** rotate the trained models and poses onto ARCore's gravity without retraining; the check renders 3 frames
  from the source and the levelled model (levelled cameras) and must give the same images.
- **Start → end:** first attempt ended 18:24; second attempt ended before 18:26 (R-035 start); seconds per model
- **Errors during the run:**
  1. 18:24 colour check — first attempt rendered source vs levelled at only 35.9–44.6 dB → cause: the SH rotation
     matrix was applied transposed (`c'_j = Σ M[k, j] c_k` instead of `Σ M[j, k] c_k`); found by rendering at SH
     degree 0 (geometry exact, 88–96 dB) vs degree 3 (35–40 dB) → fix in `level_model.py`; the faulty outputs were
     moved out of `dataset/` into the agent's scratchpad (not used) and the script re-run (resolved: yes).
- **Result:** `dataset/scan_002_646070948603/work_r1106lev_sfm/gs_r1106lev/splat.ply` (rotated 9.09°, 469 / 482 frames
  agree, spread 0.83°) and `dataset/scan_003_6de634cbb8b2/work_r1112lev_sfm/gs_r1112lev/splat.ply` (12.10°, 875 / 875,
  0.98°), each with `frames.json`, `level.json` and links to the source `images/` and `planes/`. Check: source vs
  levelled renders **87.6–98.2 dB** (3 frames each; at SH degree 3 on scan #3 85.0–88.2 dB): the same model.
  The SH coefficient order (channel-major, `f_rest_{c·15+k}`) was confirmed against photos: 22.81 / 16.20 / 19.24 dB
  vs 21.71 / 15.14 / 17.04 dB for the other order.
- **Verdict:** kept: levelled copies for re-running layout → web (R-035, R-036). Originals unchanged.

### R-035 · 2026-11-12 · scan #3 levelled (`r1112lev`): layout → semantics → mesh → web
- **Who / machine:** Umair (agent) · this PC (Ubuntu, RTX 4000 Ada), `screen` session `run-r1112lev`
- **Branch / commit:** `feature/step4-layout` @ `0b9c882` (uncommitted changes: TRAINING.md only)
- **Dataset:** scan #3 (`scan_003_6de634cbb8b2`), R-031's model levelled by R-034 (12.10°)
- **Command(s):** `scripts/run_full.sh dataset/scan_003_6de634cbb8b2 r1112lev --from layout -- --pgsr` (`--pgsr` only
  selects the unbiased depth for the mesh, as in R-031)
- **Goal:** layout with D-071 + D-072 (expected from the prototype: 4 walls, 3 corners, 2.52 m), then semantics v10,
  mesh and web bundle on the levelled model; compare with R-031 (2 walls, 0 corners, 2.74 m, 21 fixtures).
- **Start → end:** 18:26:56 → 18:44:56 (18.0 min): layout 1.2, sem2d 13.7, sem3d 0.1, verify 0.2, sem3d2 0.1,
  mesh 0.3, meshlabels 2.4, web 0.1 (`stages.tsv`)
- **Errors during the run:** none (`run_full.log` has no tracebacks or errors).
- **Result:** `dataset/scan_003_6de634cbb8b2/work_r1112lev_sfm/gs_r1112lev/`; web bundle
  `prototype/web-ui/public/scans/scan_003_6de634cbb8b2_r1112lev/` (18 MB). **Layout:** 4 walls (8.97, 7.19, 7.68,
  3.69 m), walls 0 ↔ 2 7.23 m apart, 1 ↔ 3 9.05 m apart, 3 corners at 89.5°, 89.8°, 88.9°; height **2.525 m**
  (ceiling source: strongest plane above the cameras, already above the wall tops, so D-072 changed nothing here).
  **Semantics v10:** ceiling plane fit accepted, tilt 0.05°, residual 0.5 cm, ceiling 2.504 m (R-031: fit rejected at
  8.06°); floor plane tilt **1.95°**, residual 2.4 cm (R-031: 0.28° / 7.2 cm, an artefact of the ±15 cm band; the
  remaining 1.95° is not explained yet); **floor area 32.27 m²** (R-031: none); walls net 22.47 / 15.25 / 19.24 /
  9.24 m². **18 fixtures** (R-031: 21): 1 door (0.98 × 2.04 m, 0.12–2.17 m above floor; R-031's door ran from −0.58
  to 1.41 m), 2 windows (2.20–2.63 m, high), 2 light switches (0.67–0.68 m), 2 power sockets (0.68 / 0.81 m),
  7 ceiling lights, 1 lamp, 3 ceiling fans; 30 rejected. Mesh 2,720,768 triangles; area by class (m²) other 120.53,
  ceiling 62.1, floor 18.02, walls 14.97 / 12.74 / 6.12 / 4.22, ceiling fan 1.97, door 1.72.
  Fixture check sheet: `semantic_v10/fixture_check.md` (`fixture_checklist.py`), for Umair (plan 4.2).
  **Not measured:** tape (height, lengths), whether the fixtures are real (check pending).
- **Verdict:** **kept** as scan #3's current layout / semantics (replaces R-031's for Step 4; R-031's model stays the
  trained source and the Step 3 timing baseline). Height and lengths wait for the tape.

### R-036 · 2026-11-12 · scan #2 levelled (`r1106lev`): layout → semantics → mesh → web
- **Who / machine:** Umair (agent) · this PC (Ubuntu, RTX 4000 Ada), `screen` session `run-r1106lev`
- **Branch / commit:** `feature/step4-layout` @ `fc3d096` (uncommitted changes: TRAINING.md only)
- **Dataset:** scan #2 (`scan_002_646070948603`), R-030's model levelled by R-034 (9.09°)
- **Command(s):** `scripts/run_full.sh dataset/scan_002_646070948603 r1106lev --from layout -- --pgsr`
- **Goal:** layout with D-071 + D-072 (prototype: 1 wall, ceiling 2.41 m from "above the wall tops", with a warning),
  semantics, mesh, web on the levelled model; compare with R-030 (1.50 m, 2 walls, 8 fixtures).
- **Start → end:** 18:45:32 → 18:53:59 (8.5 min): layout 0.1, sem2d 7.8, the rest 0.1 each (`stages.tsv`)
- **Errors during the run:** none.
- **Result:** `dataset/scan_002_646070948603/work_r1106lev_sfm/gs_r1106lev/`; web bundle
  `prototype/web-ui/public/scans/scan_002_646070948603_r1106lev/`. **Layout:** strongest ceiling plane 1.790 m was
  below the wall top (2.274 m) → **2.408 m** ("strongest horizontal plane above the wall tops", D-072); 1 wall
  (3.74 m), 0 corners (R-030: 2 walls). **Semantics v10:** ceiling plane fit accepted (tilt 0.42°, residual 2.0 cm),
  ceiling 2.503 m; floor tilt 1.57°, residual 1.9 cm; floor area not computed (one wall); **10 fixtures** (window,
  2 light switches, 2 power sockets, 2 ceiling lights, 2 lamps, air conditioner), 45 rejected (R-030: 8 / 44).
- **Verdict:** **inconclusive.** The height is now plausible (1.50 → 2.41 m) but rests on the wall-top rule: this
  model's ceiling is wrong (R-032), and with the camera within 0.8 × 0.7 m the room cannot get more walls. Better
  fixed by a new recording of the lab with the capture protocol than by more rules. Not checked against tape.

### R-037 · 2026-11-12 · newRoomAttemptSadness on this PC, R-023 recipe, full pipeline (tag `r1112nr`)
- **Who / machine:** Umair (agent; Umair chose the recipe) · this PC (Ubuntu, RTX 4000 Ada), `screen` session `run-r1112nr`
- **Branch / commit:** `feature/step4-layout` @ `104a535` (uncommitted changes: TRAINING.md only)
- **Dataset:** `dataset/newRoomAttemptSadness`, copied from the RTX 3070 PC on 2026-11-12 by Umair (raw recording only:
  `dataset.mp4`, `poses.csv` 7,047 rows, `points.csv`, `depth/` 1,677 files, `quality.csv`, `tracking.csv`,
  `meta.json`; realme RMX5111; no `camera.csv` / `anchors.csv`); the R-014 held-out list is not on this PC
- **Command(s):** `scripts/run_full.sh dataset/newRoomAttemptSadness r1112nr -- --sfm_args "--retrieval 20" --init fmvs
  --planar 0.2 --blur 0.0222 --pgsr` (the R-023 recipe, all frames)
- **Goal:** COMPLETION_PLAN 3.1 machine agreement against R-023 (3070: 1165 frames, layout 6.60 × 4.36 m, ceiling
  2.72 m, tape 6.70 m, 15 v10 fixtures, 96 min for the R-020 run) and the first end-to-end run with D-071 (gravity
  in the export) and D-072 (ceiling rule) on a room whose layout was right. No PSNR comparison (no split here).
- **Errors during the run:** none (only `timm` FutureWarnings in the log).
- **Output:** `dataset/newRoomAttemptSadness/work_r1112nr_sfm/gs_r1112nr/` (606,881 splats), web bundle
  `prototype/web-ui/public/scans/newRoomAttemptSadness_r1112nr/` (19 MB, not committed, like the other local bundles).
- **Stage times** (`stages.tsv`, `timing.json`), 18:56:57 → 20:39:57 = **103.0 min**: select 0.5, SfM 12.4, export 0.0,
  prior 4.6 (1157 frames in 267 s), init (fast MVS) 18.4, train 45.2, ply 0.3 (run_v8 81.4) · layout 1.8 · sem2d 18.2 ·
  sem3d / verify / sem3d2 0.5 · mesh 0.3 · mesh labels 0.7 · web 0.1. For comparison: R-020 (v9e2e, 3070) 96 min,
  R-023 training 46 min on the 3070; R-031 (scan #3, 885 frames, this PC) 81.0 min. Not the same stage split, so the
  per-machine comparison is only rough.
- **SfM:** 1157 / 1166 frames registered (R-023: 1165 frames); Sim3 scale 0.6259, 898 / 1166 centre inliers, median
  3.3 cm. R-023's scale is not on this PC, so scale agreement is **not measured**.
- **Gravity (D-071):** ARCore gravity 0.00° from +Y after levelling (per-frame spread 0.31°, 1164 frames); a
  full-rotation Sim3 on the same inliers would have been 0.57° off, so this room was nearly level with the old export
  too (unlike scan #2 / #3).
- **Layout:** 5 walls 6.63 / 4.37 / 5.78 / 4.57 / 0.78 m, 4 corners 72.0 / 88.1 / 89.2 / 89.2°, no warnings. Main
  rectangle **6.63 × 4.37 m** vs R-023 6.60 × 4.36 m (+3 cm / +1 cm) and tape 6.70 m (−7 cm). The 0.78 m wall and the
  72° corner are not explained yet (look at `layout/plan.png`).
- **Height: 2.81 m** vs R-023 2.72 m (+9 cm). D-072 changed it: the strongest horizontal plane was at 2.69 m above
  the floor (ceiling_first_y 1.205), below the wall tops (1.301), so the rule took the plane above the wall tops
  (ceiling_y 1.320). Semantics rejected its own ceiling fit (tilt 0.49°, residual 4.7 cm) and used 2.822 m. Which of
  2.69 / 2.72 / 2.81 m is right is **not measured** (no tape height for this room); the wall tops may be floaters
  above the ceiling, in which case D-072 overshoots here.
- **Semantics v10:** floor tilt 0.25° (residual 0.5 cm), floor area 29.41 m² (R-023 bundle 28.81 m²), **18 fixtures**
  vs R-023's 15: door 7 (6), light switch 3 (2), power socket 2 (1), ceiling light 3 (3), window 1 (1), tube light 1
  (1), lamp 1 (1); 49 rejected. Which of the 3 extra ones are real is not checked: check sheet
  `gs_r1112nr/semantic_v10/fixture_check.md` for Umair.
- **Mesh:** unbiased depth, 579 frames, 1,858,737 triangles.
- **Verdict:** **kept** as the machine-agreement run for this PC: the pipeline runs end to end and the room size agrees
  with the 3070 within 3 cm. Not settled: height (+9 cm, D-072), 3 extra fixtures, PSNR / SSIM (needs the R-014 split
  from Tayyab). Whether the model goes to `saved_models/`: Umair to decide.

### R-038 · 2026-11-16 · scan_008 full pipeline, R-023 recipe (tag `r1116`)
- **Who / machine:** Umair (started the run himself; agent wrote the entry) · this PC (Ubuntu, RTX 4000 Ada), `screen`
  session `run-r1116`
- **Branch / commit:** `feature/step4-layout` @ `4f0f710` (uncommitted changes: none in code; `.gitignore` /
  DECISIONS.md edited during the run, no effect on the pipeline)
- **Dataset:** `dataset/scan_008_7b486c855ed6`, added by Umair on 2026-11-16 with scan_005 / 006 / 007 (not run yet).
  Phone INFINIX Infinix X6833B (the same phone as scans #1–#3; *corrected 2026-11-16: this entry first said it was the
  first Infinix capture, which was wrong*), 1920 × 1080 at 30 fps; **366.5 s video** (ffprobe from the `bs-system`
  env), 10,255 frames, `poses.csv` 10,172 rows, `depth/` 1,027 files (`imu.npz` is written by the pipeline at
  12:27:16, not recorded). The longest recording on this PC (scan #3: 185 s; newRoom: 240 s). Which room it is: not
  recorded yet (Umair to fill in).
- **Command(s):** `scripts/run_full.sh dataset/scan_008_7b486c855ed6 r1116 -- --sfm_args "--retrieval 20" --init fmvs
  --planar 0.2 --blur 0.0222 --pgsr` (the R-023 recipe, as in R-037)
- **Goal:** first new-room run for COMPLETION_PLAN Step 3/4: SfM on the new phone, layout + height with D-071 / D-072,
  semantics v10 on a room the rules were not tuned on (plan 4.1 / 4.2).
- **Start → end:** 12:27:13 → 13:16:55 (49.7 min, **did not finish**). select 0.7 min (1639 of 10255 frames, predicted
  blur median 4.2 px vs 5.2 px); SfM: feature extraction to 12:28:34; 37,345 ARCore-guided pairs (22.8 per frame),
  `matches_importer` 12:28 → 12:32:56; `vocab_tree_matcher` (retrieval 20) to 12:39:53; `global_mapper` from 12:39:54:
  37,250 matched pairs, 1 connected component with all 1639 images, rotation averaging 4.0 s, **1,265,512 tracks from
  16,188,709 observations** (track establishment 35.0 s), global positioning started 12:42:48 on the CPU (log: "Ceres
  was compiled without cuDSS support. Falling back to CPU-based sparse solvers").
- **Errors during the run:**
  1. 13:16:55 SfM (`global_mapper`, global positioning) — killed by the kernel OOM killer: `Out of memory: Killed process
     71833 (colmap) total-vm:46212272kB, anon-rss:26138352kB` (26.1 GB resident; this PC has 30 GB RAM + 7 GB swap).
     The `screen` session `run-r1116` ended, no `sparse/0` written. `scripts/buildscan watch` only showed "STOPPED ...
     did not finish" with the last message `> global_mapper`; the cause is only in the kernel log (`journalctl -k`).
     → cause: 1639 frames × 8192 SIFT features gives 16.2 M observations; GLOMAP's global positioning on the CPU did not
     fit in memory. R-037 (1166 frames) and R-031 (885 frames) fitted on the same PC; their peak memory was not
     measured. → fix / workaround: Umair chose fewer frames (`--window 9`, D-073) → re-run R-039 (resolved: in R-039).
- **Result:** none; partial output `dataset/scan_008_7b486c855ed6/work_r1116_sfm/` (database.db 4.3 GB, matcher logs),
  log `gs_r1116/run_full.log`.
- **Verdict:** **failed** (OOM in SfM); re-run as R-039 with fewer frames (D-073).

### R-039 · 2026-11-16 · scan_008 re-run with fewer frames (tag `r1116w9`)
- **Who / machine:** Umair (chose the fix, D-073; agent started the run) · this PC (Ubuntu, RTX 4000 Ada), `screen`
  session `run-r1116w9`
- **Branch / commit:** `feature/step4-layout` @ `3959d4d` (uncommitted changes: TRAINING.md / DECISIONS.md only)
- **Dataset:** `dataset/scan_008_7b486c855ed6` (as R-038)
- **Command(s):** `scripts/buildscan run scan_008_7b486c855ed6 r1116w9 -- --window 9 --sfm_args "--retrieval 20"
  --init fmvs --planar 0.2 --blur 0.0222 --pgsr`
- **Goal:** R-038's goal; SfM has to fit in memory with ~1,140 frames (R-037: 1,166 frames ran on this PC).
- **Start → end:** 13:21:30 → 16:08:11 (`stages.tsv`; written up by the agent on 2026-11-19). select 0.7 min: **1118 frames** (predicted blur median 3.9 px vs 5.2 px).
  SfM: 25,622 ARCore-guided pairs (22.9 per frame); `global_mapper` from ~13:30: **1,404,275 tracks from 10,774,946
  observations** (R-037: 289,543 tracks / 1.78 M observations for 1,166 frames, so ~6× more per frame);
  **global positioning 1699.9 s (28.3 min)** (R-037: 99.0 s), done 13:59:16; iterative bundle adjustment from 13:59:17.
- **Memory** (agent's watcher, every 10 s; ``ps`` RSS of colmap and ``MemAvailable``): colmap 12.6 GB at 13:50:36, then
  19.8 GB at 13:50:46 and **23.3 GB at 13:50:56 with 2.1 GB available** (the watcher stopped there, so the true peak
  is not measured); swap in use 4.0 of 8.0 GB at 14:02. No OOM kill. At 14:02 colmap 10.4 GB in bundle adjustment.
- **Errors during the run:** none so far (memory came within ~2 GB of running out at 13:50, see above).
- **Stage times (min, `timing.json` / `stages.tsv`):** select 0.71, SfM 63.6, export 0.01, prior 4.94, init 17.39,
  train 57.91, ply 0.87 → run_v8 145.4; layout 2.7, sem2d 16.6, sem3d 0.2, verify 0.1, sem3d2 0.2, mesh 0.3,
  meshlabels 1.0, web 0.1. Whole run 13:21:30 → 16:08:11 = 166.7 min.
- **Result:** 1118 of 1118 frames registered; ARCore gravity tilt 0.00° (spread 0.54°; full Sim3 on the same inliers
  1.11°), `work_r1116w9_sfm/report.json`. Mono prior aligned median error 1.5% (raw 13.8%). Layout / semantics
  (`semantic_v10/semantic.json`): 5 walls, floor 21.26 m², ceiling 3.194 m, floor tilt 0.22°, ceiling 0.63°;
  11 fixtures accepted (1 door, 2 windows, 4 switches, 3 sockets, 1 ceiling light), 56 rejected. Web bundle
  `prototype/web-ui/public/scans/scan_008_7b486c855ed6_r1116w9/` (2,506,236 splats), shown in the web UI as
  `scan-008` (2026-11-18). No `fixture_check.md` written yet; no tape; room not named. The plan also covers two
  small rooms next to the main one (web-ui STATUS §6).
- **Verdict:** kept as the scan #8 model for now (Umair put it in the web UI); fixtures not checked by a person.
  Output `dataset/scan_008_7b486c855ed6/work_r1116w9_sfm/gs_r1116w9/`.

### R-040 · 2026-11-18 · scan #7 full pipeline, R-023 recipe (tag `r1118`)
- **Who / machine:** Umair (started the run himself through the `scripts/buildscan` menu, recording 2) · this PC
  (Ubuntu, RTX 4000 Ada), `screen` session `run-r1118`. Before it, the agent closed the finished R-039 session
  `run-r1116w9` (it was waiting at "press Enter to close" and blocked the one-run-at-a-time check). The `viewer`
  session (`view.py` on scan #8's `splat.ply`, ~2.3 GB GPU) was still open when the run started.
- **Branch / commit:** `feature/viewer-scan-008` @ `b969f49` (uncommitted changes: `prototype/web-ui/next-env.d.ts`,
  `tsconfig.tsbuildinfo` from a `next build`; nothing in the pipeline)
- **Dataset:** `dataset/scan_007_e6d4f090f88e` (Umair, Infinix X6833B, 269.2 s, 7,243 frames; room not named yet)
- **Command(s):** `scripts/run_full.sh dataset/scan_007_e6d4f090f88e r1118 -- --sfm_args "--retrieval 20" --init fmvs
  --planar 0.2 --blur 0.0222 --pgsr` (started by `scripts/buildscan`; no `--window`, so `select_sharp` uses 6)
- **Goal:** first model of scan #7 (STATUS §7, scans #5–#7). The default window was kept; D-073's `--window 9` was
  needed for scan #8 (342 s). SfM has to fit in memory (R-037: 1,166 frames ran; R-038: 1,639 frames killed by OOM).
  Then check `report.json` gravity tilt, layout walls / height, fixtures and the check sheet.
- **Start → end:** 10:19:18 → 13:39:51 (`stages.tsv`; written up by the agent on 2026-11-19, the `screen` session was still open at "press Enter"). select 0.6 min: **1160 frames** of 7,243 (predicted blur median 0.6 px vs
  0.8 px over all frames). SfM started right after (`feature_extractor` running at 10:20:06; `vocab_tree_matcher` by the time of writing). At 10:20:06: 25 GB RAM available, swap 1 of 7 GB used.
- **Errors during the run:** none in `run_full.log` (only timm FutureWarnings).
- **Stage times (min, `timing.json` / `stages.tsv`):** select 0.57, SfM 96.38, export 0.01, prior 5.18, init 19.69,
  train 52.9, ply 0.68 → run_v8 175.4; layout 2.7, sem2d 17.7, sem3d 0.3, verify 0.2, sem3d2 0.3, mesh 2.6,
  meshlabels 1.1, web 0.2. Whole run 10:19:18 → 13:39:51 = 200.6 min.
- **Result:** SfM registered 1159 of 1160 frames; ARCore gravity tilt 0.00° (spread 0.83°; a full Sim3 on the same
  inliers would have been 1.72° off), `work_r1118_sfm/report.json`. Mono prior aligned median error 2.3% (raw
  Metric3D 12.9%). Web bundle groups hold 1,840,851 splats (`scan.json`). Layout /
  semantics (`semantic_v10/semantic.json`): 6 walls, floor 19.66 m², ceiling 3.401 m, floor tilt 0.98°, ceiling
  0.00°. **0 fixtures accepted, 29 rejected** by the geometry rules: 14 sockets ("small, on a wall"), 6 doors
  ("tall, from the floor, 0.45–2 m wide, in a wall"), 6 windows ("in a wall, sill ≥ 0.5 m, ≥ 0.3 m wide"),
  3 ceiling lights ("8 cm – 1.5 m, at the ceiling"). Why every candidate failed is not investigated yet (STATUS
  §7.5). Web bundle `prototype/web-ui/public/scans/scan_007_e6d4f090f88e_r1118/` (floor, ceiling, walls, other,
  mesh; no electrical / openings groups). No tape, room not named.
- **Verdict:** inconclusive until Umair has looked at the model and the rejected fixtures (the reconstruction itself
  finished without errors). Output `dataset/scan_007_e6d4f090f88e/work_r1118_sfm/gs_r1118/`.

### R-041 · 2026-11-14 · newRoom: Fast training + PGSR-lite on newRoom (`pgsrfast`)
- **Who / machine:** Tayyab (agent, overnight session) · RTX 3070 PC
- **Branch / commit:** `exp/overnight-2026-11-14` (uncommitted: the `--mcmc_cap` option in `geo_splatfacto.py` until it is tested)
- **Dataset:** newRoomAttemptSadness, `work_v9e2e_sfm` (R-020's SfM, prior, fast-MVS init and off-path split)
- **Command(s):** `train_eval.sh pgsrfast --pgsr` (scratchpad helper = R-062's commands: `geo_splatfacto.py --data work_v9e2e_sfm/transforms_fmvs.json --iters 15000 --dash_res_steps 7500 --stop_split_at 7500 --no_eval --prior mono_prior/train_v9e2e.npz --planar_lambda 0.2 --blur_exposure 0.0222 --pgsr`, `ns-export`, `eval_offpath.py` vs `gs_v9e2e` on the 79 off-path frames)
- **Goal:** The speed-ups (R-062) together with `--pgsr` (the best model's recipe, R-021 / R-023): same quality as R-021 v9pgsr (25.09 / 0.8254, 46 min training)?
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
- **Command(s):** `train_eval.sh mcmc1m --mcmc_cap 1000000` (scratchpad helper = R-062's commands: `geo_splatfacto.py --data work_v9e2e_sfm/transforms_fmvs.json --iters 15000 --dash_res_steps 7500 --stop_split_at 7500 --no_eval --prior mono_prior/train_v9e2e.npz --planar_lambda 0.2 --blur_exposure 0.0222 --mcmc_cap 1000000`, `ns-export`, `eval_offpath.py` vs `gs_v9e2e` on the 79 off-path frames)
- **Goal:** Does a 1M-Gaussian MCMC model improve off-path quality, and at what time / size cost?
- **Start → end:** 04:37 → 05:19 (train 40.4 min)
- **Errors during the run:** none so far
- **Result:** `work_v9e2e_sfm/gs_mcmc1m/` (601,002 Gaussians exported). Off-path, 79 frames: **PSNR(cf) 24.74 / SSIM
  0.8200 / sharpness 0.69 / flatness 0.93 cm**, 40.4 min training (v9e2e 25.16 / 0.8247 / 0.80 / 0.77, 42.5 min).
- **Verdict:** **rejected**: a larger budget helps MCMC a little over R-070 (+0.09 dB, sharpness 0.64 → 0.69) but it
  stays below splatfacto's densification on this pipeline. MCMC as wired here (relocation stopping at 7,500 steps,
  DashGaussian, depth / normal / planar priors) is not worth more runs without changing those first.

### R-043 · 2026-11-14 · newRoom: revised opacity on clone / split (`revop`)
- **Who / machine:** Tayyab (agent, overnight session) · RTX 3070 PC
- **Branch / commit:** `exp/overnight-2026-11-14` (new `--revised_opacity` option in `geo_splatfacto.py`, uncommitted until tested)
- **Dataset:** newRoomAttemptSadness, `work_v9e2e_sfm` (as R-070)
- **Command(s):** as R-070 with `--revised_opacity` (gsplat `DefaultStrategy(revised_opacity=True)`: Bulò et al. 2024,
  "Revising Densification in Gaussian Splatting"; splatfacto turns it off)
- **Goal:** cheaper floater / over-opacity fix than MCMC: does it beat R-062 (25.14 / 0.8251)?
- **Start → end:** 05:24 → 05:53 (train 28.5 min)
- **Errors during the run:** none so far
- **Result:** `work_v9e2e_sfm/gs_revop/` (561,425 Gaussians, −10% vs R-062's 621,430). Off-path, 79 frames: **PSNR(cf)
  25.02 / SSIM 0.8244 / sharpness 0.79 / flatness 0.73 cm**, 28.5 min, vs R-062 (same code without the option)
  25.14 / 0.8251 / 0.80 / 0.81 cm, 28.2 min.
- **Verdict:** **inconclusive, not adopted**: −0.12 dB PSNR, flatness 0.08 cm better, 10% smaller model; differences of
  this size are within what one run per setting can resolve (run-to-run noise not measured, STATUS 7.3).

### R-044 · 2026-11-14 · newRoom: lower densification threshold (`dg4`)
- **Who / machine:** Tayyab (agent, overnight session) · RTX 3070 PC
- **Branch / commit:** `exp/overnight-2026-11-14`
- **Dataset:** newRoomAttemptSadness, `work_v9e2e_sfm` (as R-070)
- **Command(s):** as R-070 with `--densify_grad 0.0004` (default 0.0006): more splitting / cloning where the image
  gradient is high
- **Goal:** do more Gaussians in detailed areas sharpen the off-path views (R-070 showed softness is the weak point),
  and at what size / time cost?
- **Start → end:** 06:21 → 06:53 (train 30.8 min); then the R-021 / R-041 flatness eval (06:53)
- **Errors during the run:** none so far
- **Result:** `work_v9e2e_sfm/gs_dg4/` (**868,556 Gaussians, +40%** vs R-062). Off-path, 79 frames: **PSNR(cf) 25.07 /
  SSIM 0.8243 / sharpness 0.85 / flatness 0.74 cm**, 30.8 min, vs R-062 25.14 / 0.8251 / 0.80 / 0.81 (28.2 min).
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
  "--retrieval 20" --init fmvs --planar 0.2 --blur 0.0222 --pgsr` (the R-069 recipe, default select window)
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

### R-053 · 2026-11-19 · Layout re-runs on six rooms for the no-roof check (#8), into scratch folders
- **Who / machine:** agent for Umair · this PC (Ubuntu, RTX 4000 Ada). Numbered R-053, not R-041: R-041 … R-051 are
  taken on `origin/master` / Tayyab's branches (OD-12).
- **Branch / commit:** `fix/8-open-ceiling` @ `fc816fb` (no uncommitted changes); a frozen copy of `layout.py` in the agent's
  scratch folder runs, so later edits do not leak in.
- **Dataset:** trained models of scan #1 (`umair`), #2 (`r1106lev`), #3 (`r1112lev`), #7 (`r1118`), #8 (`r1116w9`),
  newRoom (`r1112nr`); nothing in `dataset/` is written.
- **Command(s):** per room `micromamba run -n bs-ns python layout.py --ply <gs>/splat.ply --work <work_sfm> --out
  <scratch>/r053/<room>/layout`; before it, a read-only ceiling-evidence script on the same models (coverage of the
  floor outline, colour, Gaussian count).
- **Goal:** scan #7 (no roof) reports no ceiling and the wall-top height; the five rooms with ceilings keep the
  height, walls and corners of their last layout run.
- **Start → end:** 08:47:39 → 08:56:27 (8.8 min; scan #7 2.4 min, #3 1.3, #8 3.1, newRoom 1.8, #2 and #1 a few s each)
- **Errors during the run:** none (all six exit 0).
- **Result:** ceiling evidence (share of the floor outline under the ceiling plane / colour blue − red / opaque
  Gaussians at the plane): scan #7 **19.6 % / +0.253 / 2,919** → no roof, height = wall top **3.120 m** (was a 3.435 m
  "ceiling"); scan #3 95.6 % / −0.002 / 114,862; scan #8 51.3 % / −0.144 / 243,198; newRoom 63.1 % / −0.031 / 6,254;
  scan #2 47.0 % / −0.051 / 13,498; scan #1 15.8 % / −0.130 / 11,878 (low cover but not sky-coloured, so unchanged).
  The five rooms with a ceiling keep exactly their earlier height, walls, corners and wall lengths (2.525 / 3.161 /
  2.808 / 2.408 / 4.193 m). Outputs `<scratchpad>/r053/<room>/layout/` (not kept).
- **Verdict:** kept: the no-roof rule (#8) changes only the roofless room. Rule defaults (35 % cover, blue − red 0.15)
  are the agent's, from these six rooms; confirm or change (COMPLETION_PLAN Step 4, open for Umair).

### R-054 · 2026-11-19 · scans #7 and #3: layout with #8 / #9 / #10 → semantics → mesh labels → web (tag `r1119a`)
- **Who / machine:** agent for Umair · this PC (Ubuntu, RTX 4000 Ada).
- **Branch / commit:** `feature/9-wall-openings` @ `0a45f89` (stacked on `fix/10-room-closed`, `fix/8-open-ceiling`); no
  uncommitted changes in the pipeline.
- **Dataset:** trained models of scan #7 (`r1118`, R-040) and scan #3 (`r1112lev`, R-035), not retrained. New tag
  `r1119a` inside each run's work folder: `gs_r1119a/splat.ply` and `gs_r1119a/mesh/mesh.ply` are links to the
  originals; the 2D masks `semantic2d_v10` and the mesh are reused. R-040 / R-035 outputs are not touched.
- **Command(s):** the `run_full.sh` stages layout, sem3d, verify, sem3d2, meshlabels (`--clean 0.01 --glb 400000`),
  web, with the same arguments, through `<scratchpad>/r054.sh`; web bundles go to
  `prototype/web-ui/public/scans/<scan>_r1119a/` (gitignored, listed in the Projects tab by D-074).
- **Goal:** scan #7: no roof (#8), its empty doorways / window openings found from the wall gaps (#9), outline
  closed or a warning (#10); scan #3: the 4-walls-3-corners outline is flagged and the triangle floor area
  (32.27 m²) is no longer reported (#10); no false openings in a finished room (#9).
- **Start → end:** 08:57:17 → 09:05:25 (8.1 min; scan #7 08:57:17 → 09:01:06: layout 2.3, sem3d 0.2, verify 0.2, sem3d2 0.2,
  meshlabels 0.9, web 0.1 min; scan #3 09:01:06 → 09:05:25, `gs_r1119a/stages.tsv`)
- **Errors during the run:** none (exit 0).
- **Result:** scan #7: no roof, walls 3.12 m; outline flagged not closed (6 walls, 4 corners), floor area null;
  wall-gap openings: doorway 0.80 m (wall 1, 0.10–2.40 m), window openings 2.10 m (wall 4, 0.40–2.30 m), 0.50 m
  (wall 2, 2.30–3.20 m), 0.30 m (wall 0, 1.90–2.40 m); 4 fixtures, 29 rejected; net wall areas reduced by them;
  check sheet `gs_r1119a/semantic_v10/fixture_check.md`, plan `gs_r1119a/layout/plan.svg|dxf`. Scan #3: outline
  flagged not closed (4 walls, 3 corners), floor area null (was the 32.27 m² triangle), ceiling 2.504 m; **4 false
  "window openings"** in the finished classroom (0.3–0.6 m wide, 1–2 Gaussians seen behind per open cell, against 41 /
  19 for scan #7's doorway / big opening; scan #7's two small ones 1 and 4). Web bundles
  `public/scans/scan_007_e6d4f090f88e_r1119a/`, `scan_003_6de634cbb8b2_r1119a/`.
- **Verdict:** #8 and #10 behave as intended; #9 gave false openings on a finished room → fixed by a view-through
  minimum of 10 Gaussians per open cell (`f0e8bd7`); the `r1119a` bundles predate that fix and are superseded by
  the re-run after R-055.

### R-055 · 2026-11-19 · Layout on six rooms with `--debug`: default vs `--raised_max 1.5 --infer_gap 6` (#9, #10, #11)
- **Who / machine:** agent for Umair · this PC (Ubuntu, RTX 4000 Ada).
- **Branch / commit:** `fix/11-wall-behind-boards` @ `30315b9`; a frozen copy of `layout.py` runs from the scratch folder.
- **Dataset:** trained models of scans #1, #2, #3, #7, #8, newRoom (as R-053); nothing in `dataset/` written.
- **Command(s):** per room `layout.py --ply ... --work ... --out <scratch>/r055/<cfg>/<room>/layout --debug`, with
  cfg `default` and cfg `opts` = `--raised_max 1.5 --infer_gap 6`. Before it: one `--debug` run on scan #7 alone.
- **Goal:** (a) the view-through minimum leaves no openings on finished rooms and keeps scan #7's doorway / big
  window opening; (b) which real walls start > 0.5 m above the floor (would `--raised_max` drop them?); (c) what
  `--infer_gap 6` closes; (d) scan #7's plank faces gone with the options.
- **Start → end:** 09:07:45 → 09:24:41 (16.9 min, 12 layout runs; before it the scan #7 `--debug` run, ~2.5 min)
- **Errors during the run:** none (all exit 0).
- **Result (default):** heights / walls / corners as R-053. Wall-gap openings: scan #7 doorway 0.80 m (41 Gaussians
  behind per open cell) + window opening 2.10 m (19); scan #3 **none** (R-054's four false ones gone); scan #8 doorway
  1.0 m (13), window opening 2.0 m (23), doorway 1.3 m (365); newRoom doorway 0.8 m (24), window opening 0.4 m at
  0.5–0.9 m (17); scans #1 / #2 none. Closed outline: none of the six (#1 / #2 one wall; #3 / #7 / #8 a real gap;
  **newRoom wrongly**: its 0.78 m jog is 16° off its neighbour, no corner by design, ends 0.42 m apart → fixed in
  `8b7f7f2`, checked in R-056).
- **Result (`--raised_max 1.5 --infer_gap 6`):** scan #7: both plank faces dropped (1.06 m from 1.21 m up, 0.57 m from
  0.60 m up) → **4 walls, 4 corners 87.7–89.7°**, the real north wall now meets both neighbours (closed rectangle).
  Scan #8: one surface dropped (0.67 m from 0.58 m up; the slanted 1.88 m "wall" with a 70.6° corner) → **4 walls,
  corners 88.6–89.5°**, 6.03 × 4.48 m. newRoom / #2 / #1: nothing dropped (newRoom's only raised wall is 4.97 m long,
  0.62 m up; its 0.67 m jog starts 0.11 m up). Scan #3: `--infer_gap` infers nothing: the missing corner (gaps
  1.49 / 3.61 m) lies 3 m beyond the last reconstructed floor (z ≈ −7.6 vs −4.43), so the floor check refuses it.
- **Verdict:** view-through minimum kept (no openings on scan #3). `--raised_max 1.5` fixed scans #7 and #8 and
  touched no real wall on six rooms → recommended as default (Umair's decision, #11). `--infer_gap`: no effect on
  these rooms; stays off.

### R-056 · 2026-11-19 · Four rooms: layout → semantics → mesh labels → web → plan with the defaults of 2026-11-19 (tag `r1119b`)
- **Who / machine:** agent for Umair · this PC (Ubuntu, RTX 4000 Ada).
- **Branch / commit:** `fix/11-wall-behind-boards` @ `8b7f7f2` (defaults: no-roof rule, wall-gap openings with the
  view-through minimum, closed-room check with step joins, floor plan; `--raised_max`, `--infer_gap`,
  `--clean_ceiling`, `--square` off).
- **Dataset:** trained models of scans #7 (`r1118`), #3 (`r1112lev`), #8 (`r1116w9`), newRoom (`r1112nr`), not
  retrained; new tag `r1119b` as in R-054 (links to the model and mesh, 2D masks reused).
- **Command(s):** `<scratchpad>/r056.sh`: the `run_full.sh` stages layout, sem3d, verify, sem3d2, meshlabels, web,
  plan, then `fixture_checklist.py --rejected`; bundles in `prototype/web-ui/public/scans/<scan>_r1119b/`.
- **Goal:** final outputs for Umair to check (sheets, plans, web bundles); newRoom's outline closed again (`8b7f7f2`)
  with its floor area; no regressions in the semantics chain.
- **Start → end:** 09:25:07 → 09:40:45 (15.6 min; per room layout 1.8–2.9 min, sem3d / verify / sem3d2 ~0.2 min each,
  meshlabels ~0.9 min, web 0.1 min, plan < 0.1 min; `gs_r1119b/stages.tsv`)
- **Errors during the run:** none (exit 0).
- **Result:** scan #7: no roof, walls 3.12 m, outline open, openings doorway 0.80 m + window opening 2.10 m, 2
  fixtures (both openings). Scan #3: ceiling 2.504 m, outline open (floor area null, was the 32.27 m² triangle),
  **no wall-gap openings**, 18 fixtures (as R-035). Scan #8: ceiling 3.194 m, outline open (21° / 2.31 m gap; floor
  area null, was 21.26 m² from 4 of 5 corners), wall-gap doorways 1.0 m and 1.3 m, 13 fixtures (11 + 2). newRoom:
  **outline closed (step join), floor 29.41 m² (unchanged)**, ceiling 2.822 m, one wall-gap window opening 0.4 m,
  19 fixtures (18 + 1). Each room: `gs_r1119b/layout/plan.svg|dxf|json`, `semantic_v10/fixture_check.md`
  (`--rejected`), web bundle `public/scans/<scan>_r1119b/`.
- **Verdict:** kept as the current outputs for Umair's checks (#21, #24); whether the 5 wall-gap openings are real
  is not known yet.

### R-057 · 2026-11-19 · Four rooms: layout → semantics → mesh labels → web → plan with the D-075 defaults (tag `r1119c`)
- **Who / machine:** agent for Umair · this PC (Ubuntu, RTX 4000 Ada); the `viewer` screen session (~2.3 GB GPU)
  stays open, `run-r1118` is closed.
- **Branch / commit:** `feature/step4-layout` @ `8022277` (no uncommitted changes).
- **Dataset:** trained models of scans #7 (`r1118`), #3 (`r1112lev`), #8 (`r1116w9`), newRoom (`r1112nr`), not
  retrained; new tag `r1119c` as in R-056 (links to the model and mesh, 2D masks reused).
- **Command(s):** `<scratchpad>/r057.sh`: R-056's stages layout, sem3d, verify, sem3d2, meshlabels, web, plan, then
  `fixture_checklist.py --rejected`, with the flags `run_full.sh` passes since D-075: `layout.py --raised_max 1.5
  --infer_gap 6`, `semantic3d.py --floor_win 0.06` (both passes), `mesh_labels.py --clean_ceiling 0.04`,
  `plan_export.py --square`; bundles in `prototype/web-ui/public/scans/<scan>_r1119c/`.
- **Goal:** the five D-075 options together on four rooms, against R-056 (`r1119b`): walls, corners, closed outline,
  floor area, floor tilt, ceiling roughness, plan.svg. Expected from R-055 / #17 / #18: scans #7 and #8 closed with
  4 walls, scan #3 floor tilt ~0.3°, ceilings ~0 cm rough. Any room that gets worse goes to Umair before anything
  else.
- **Start → end:** 15:09:11 → 15:25:53 (16.7 min; per room layout 1.2–2.9 min, sem3d / verify / sem3d2 ~0.2 min each,
  meshlabels 0.9–3.5 min, web 0.1 min, plan < 0.1 min; `gs_r1119c/stages.tsv`)
- **Errors during the run:** none (exit 0). Not an error: with `--square`, `plan_export.py` writes
  `layout/plan_square.json|svg|dxf` and no `plan.svg`; `layout/plan.png` (thumbnail) is still written by `layout.py`.
- **Comparison script:** `<scratchpad>/compare.py` (layout.json, semantic.json, and `mesh.py`'s `shell_flatness` on
  `mesh_clean.ply`: median |deviation| cm, % within 1 cm). Run on `r1119b` first: it gives #18's numbers (scan #8
  ceiling 4.35 cm, newRoom 4.31 cm), so the measure is the same.
- **Result (R-056 `r1119b` → R-057 `r1119c`):**

  | Room | Walls | Corners | Closed | Floor area | Floor tilt | Ceiling rough (cm, % ≤ 1 cm) | Fixtures (rejected) | Wall-gap openings |
  |---|---|---|---|---|---|---|---|---|
  | scan #7 | 6 → **4** | 4 (one 63.5°) → 4 (87.7–89.7°) | no → **yes** | null → **17.99 m²** | 0.98° → 0.18° | no roof | 2 (29) → 3 (29) | doorway 0.8 + window 2.1 → **+ doorway 1.0 m** (wall 2, 0.1–2.4 m, the wall the planks hid) |
  | scan #3 | 4 → 4 | 3 → 3 | no → no | null → null | **1.95° → 0.29°** | 0.02 (89.4) → 0.00 (97.6) | 18 (30) → **20 (28)**: + socket at 0.59 m (45 views, no candidate before), + ceiling fan 3 (rejected before as "away from walls") | none → none |
  | scan #8 | 5 → **4** | 4 (one 70.6°) → 4 (88.6–89.5°) | no → **yes** | null → **26.44 m²** | 0.22° → 0.21° | **4.35 (19.6) → 0.04 (66.6)** | 13 (56) → **10 (58)** | doorways 1.0 + 1.3, window 2.0 → **doorway 1.3 m gone** |
  | newRoom | 5 → 5 | same | yes → yes | 29.41 → 29.41 | 0.25° → 0.24° | **4.31 (22.3) → 0.04 (61.2)** | 19 (49) → 19 (49) | same |

  Scan #3's semantic ceiling height 2.504 → **2.582 m** (floor fit on the lower level, `--floor_win`); `layout.json`
  height unchanged 2.525 m, so the two now differ by 5.7 cm; tape decides (#17, #20). Scan #8 lost **light switch 1
  and power socket 1** (one plate at 1.27 / 1.28 m, 23 / 35 views): they sat on the 1.88 m diagonal surface
  (0.58 m up, 0.67 m tall) that `--raised_max 1.5` dropped across the corner of walls 1 / 0; now 1.52 m from the
  nearest wall, so rejected "small, on a wall". The 1.3 m "doorway" lost with it was on the same surface (0.1–3.2 m,
  365 Gaussians seen through: the space behind the surface is open). Cutting the corner off would make the floor
  about 2.0 m² smaller (triangle of the three points, agent's estimate). `--square` turned walls by 0.02–2.35°
  (largest scan #7 wall 2: 2.35°, scan #8 wall 1: 1.91°). Wall flatness otherwise unchanged except where a wall got
  longer (scan #8 wall 1 0.06 → 1.55 cm, scan #7 wall 2 2.58 → 0.26 cm). Check sheets
  `gs_r1119c/semantic_v10/fixture_check.md` (`--rejected`); bundles `public/scans/<scan>_r1119c/`.
- **Verdict:** kept for scans #7, #3 and newRoom; **scan #8 waits for Umair**: closed rectangle and smooth ceiling,
  but a switch + socket plate lost. Is the diagonal surface in that corner a wall (then `--raised_max` is wrong here)
  or furniture with a plate on it? → **Umair (2026-11-19): furniture / a low board in that corner**, so
  `--raised_max 1.5` is right there and the lost plate was not on a wall; `r1119c` is current for all four rooms and
  the `r1119b` bundles moved to `scans_archive/`.

### R-058 · 2026-11-19 · scan #6 full pipeline, R-023 recipe, D-075 defaults (tag `r1119`)
- **Who / machine:** agent for Umair (Umair's command and go-ahead) · this PC (Ubuntu, RTX 4000 Ada), `screen`
  session `run-r1119`; the `viewer` session (~2.3 GB GPU) stays open.
- **Branch / commit:** `feature/step4-layout` @ `2e7bbb8` (no uncommitted changes in the pipeline)
- **Dataset:** `dataset/scan_006_1e457a214ce1` (Umair, Infinix X6833B, 259.8 s, 7,274 video frames; room not named yet)
- **Command(s):** `scripts/buildscan run 6 r1119 -- --sfm_args "--retrieval 20" --init fmvs --planar 0.2 --blur 0.0222
  --pgsr` (default window 6, like scan #7 at 269 s, R-040)
- **Goal:** first model of scan #6 (#19), with the post-training stages on the D-075 defaults; then gravity tilt,
  layout walls / height / closed outline, fixtures and the check sheet. SfM has to fit in RAM (R-040: 1,160 frames
  ran in 96 min).
- **Start → end:** 15:29:08 → killed 16:14:39 (45.5 min); select 0.6 min (**1159 frames** of 7,274, predicted blur
  median 3.9 px vs 5.0 px over all), SfM: feature extraction, 26,147 ARCore-guided pairs, vocabulary-tree matching,
  `global_mapper` from ~15:40 (12,557,723 observations; global positioning on the CPU, Ceres without CUDA).
- **Errors during the run:**
  1. 16:14:39 sfm (`global_mapper`) — kernel OOM killer: "Out of memory: Killed process 688507 (colmap)
     total-vm:43322560kB, anon-rss:26405116kB" (`journalctl -k`); the allocation that triggered it came from the
     agent's Claude process; VS Code helper processes and every `screen` session of the VS Code scope (`run-r1119`,
     `viewer`) were killed with it; no reboot. `run_full.log` just stops (no "all done", no `stages.tsv`). → cause:
     COLMAP needed ~26.4 GB of the 30 GB; scan #7 passed with 12,684,881 observations (R-040), so this recording is
     not too big by itself: during global positioning the agent ran web-UI work on the same PC (`next dev` servers,
     a `next build`, pytest, uploads to R2; `feature/vercel-deploy`), the `viewer` session was open, and swap was
     3 of 7 GB used. → fix: not resolved; rerun with nothing else heavy on the PC (agent does no builds / dev servers
     during SfM), or fewer frames (`--window 9`, D-073), or more swap (sudo, Umair). Choice is Umair's.
- **Result:** none (stopped in SfM). Work folder `dataset/scan_006_1e457a214ce1/work_r1119_sfm/` (database, partial).
- **Verdict:** failed (OOM in SfM, R-038's failure; the agent's parallel work is the likely tipping point).

### R-059 · 2026-11-19 · scan #6 rerun after R-058's OOM, same recipe, PC kept quiet (tag `r1119b6`)
- **Who / machine:** agent for Umair (Umair chose "same recipe, PC kept quiet" after R-058) · this PC (Ubuntu, RTX
  4000 Ada), `screen` session `run-r1119b6`; no `viewer`, no dev servers; the agent runs nothing heavy (builds, dev
  servers, tests, uploads) until SfM has finished, and logs free RAM every minute to its scratch folder.
- **Branch / commit:** `feature/step4-layout` @ `d6bb0ee` (no uncommitted changes)
- **Dataset:** `dataset/scan_006_1e457a214ce1` (259.8 s, 7,274 video frames)
- **Command(s):** `scripts/buildscan run 6 r1119b6 -- --sfm_args "--retrieval 20" --init fmvs --planar 0.2 --blur 0.0222 --pgsr`
- **Goal:** first model of scan #6 (#19); SfM must pass in RAM like scan #7 (12.68 M observations, R-040). Then
  layout / fixtures / check sheet, publish within the 10 GB cap (D-077).
- **Start → end:** 16:33:50 → 19:37:41 ("all done" in `gs_r1119b6/run_full.log`). Stage times (`timing.json`,
  `stages.tsv`): run_v8 162.5 min = select 0.53, SfM 86.07, export 0.01, prior 5.23, init 19.41, train 50.53, ply
  0.73; then layout 1.4, sem2d 17.6, sem3d 0.2, verify 0.2, sem3d2 0.2, mesh 0.3, meshlabels 1.5, web 0.1, plan 0.0 min.
  Inside SfM (`global_mapper.log`, as quoted in R-071): global positioning 2,240.92 s, iterative BA 1,528.52 s,
  retriangulation + refinement 733.86 s, reconstruction 4,535.88 s.
- **Errors during the run:** none (no traceback in `run_full.log`; only timm `FutureWarning`s). SfM passed in RAM with
  the PC kept quiet (R-058's failure did not repeat).
- **Result** (written up 2026-11-23 from the run's files, R-085): `work_r1119b6_sfm/gs_r1119b6/` (`splat.ply`
  506 MB); web bundle `prototype/web-ui/public/scans/scan_006_1e457a214ce1_r1119b6/`, published to R2 on 2026-11-19
  (LOG). SfM (`report.json`): 1,159 / 1,159 frames registered, 585,115 points, ARCore Sim3 174 inliers, median
  4.85 cm, gravity from ARCore (spread 0.70°; a full Sim3 on the same inliers would have tilted it 3.81°). Prior:
  aligned Metric3D median error 1.6 % (raw 15.5 %). **Layout** (`layout/layout.json`): height **3.05 m** (strongest
  horizontal plane above the cameras; wall tops 2.94 m above the floor), **room closed**, no warnings, 7 walls (5.26,
  4.39, 4.01, 2.32, 1.71, 0.98, 0.74 m), 6 corners (89.6, 89.8, 90.0, 83.0, 87.0, 89.3°), one wall-gap doorway 0.90 m
  on wall 2 (0.10–1.70 m, 5,011 Gaussians seen through). **Semantics v10** (`semantic_v10/semantic.json`): floor tilt
  0.21°, ceiling tilt 0.24°, ceiling height 3.076 m (2.6 cm above the layout's), floor area 19.79 m², **11 fixtures**
  (door 1, window 1, light switch 5, power socket 1, ceiling light 1, ceiling fan 1, doorway 1), **84 rejected**
  (62 windows "in a wall, sill ≥ 0.5 m, ≥ 0.3 m wide", 11 sockets "small, on a wall", 4 fans, 3 tube lights, 2
  switches, 1 crop check, 1 ceiling light). Not measured: tape (room height, wall lengths), fixture correctness
  (check sheet: R-085), render quality (no held-out split).
- **Verdict:** kept as the first model of scan #6 (#19); fixtures and dimensions not checked by a person yet.

### R-062 · 2026-11-12 · Training speed-up, phase 1: profiling + exact fixes + blur colour grid once (`fast_t1`)
*Runs R-062 – R-068 were numbered R-029 – R-065 on the unmerged branch (the chat of 2026-11-12 uses those numbers);
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

### R-063 · 2026-11-12 · Speed-up phase 2: photometric-only fast-MVS init (`fast_t2_photo`)
- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/fast-pipeline` @ f33aeaf (uncommitted changes: yes, R-062's + `fast_mvs.py --iters / --photometric / --suffix`)
- **Dataset:** newRoomAttemptSadness, `work_v9e2e_sfm` (as R-062).
- **Command(s):** init variants: `fast_mvs.py --work work_v9e2e_sfm --json transforms.json --out_json transforms_fmvs_it3.json
  --suffix _it3 --iters 3` and `... --suffix _photo --photometric`; then R-062's training on `transforms_fmvs_photo.json`.
- **Goal:** cut the 20 min dense init without losing quality (compared with R-062, same training code).
- **Init variants (PatchMatch time; cloud vs the current `init_fmvs.ply`, 258,364 points):**
  current 5 iterations + geometric pass 20.1 min (in R-020) · 3 iterations 12.1 min, 244,948 points, 94.3% of the
  current points within 2 cm, 96.1% of its points within 2 cm of the current cloud, 99.1% within 5 cm · photometric only
  **7.5 min**, 262,592 points, 93.2% / 90.9% / 99.1%.
- **Start → end:** first attempt 02:16 → stopped at step 8240 (~02:45); restarted 16:45 → 17:20 (training 30.6 min, slowed by R-064 running on the CPU at the same time)
- **Errors during the run:**
  1. ~02:45 training — the run stopped at step 8240 of 15000 with exit code 4 and no Python traceback, at the same moment
     as R-064's COLMAP process (both started from the agent's shell; likely the shell session was ended). Nothing else on
     the PC was affected. → restarted from scratch at 16:45 (partial outputs removed). (resolved: restarted)
- **Result:** `work_v9e2e_sfm/gs_fast_t2_photo/`. 79 off-path frames:

  | model | splats | PSNR(cf) | SSIM | sharpness | flatness cm |
  |---|---|---|---|---|---|
  | v9e2e (R-020) | 619,056 | 25.16 | 0.8247 | 0.80 | 0.77 |
  | fast_t1 (R-062, current init) | 621,430 | 25.14 | 0.8251 | 0.80 | 0.81 |
  | fast_t2_photo (photometric init) | 622,049 | 25.16 | 0.8240 | 0.80 | 0.78 |

  Room-centre and off-path views look the same as v9e2e (no new holes or floaters).
- **Verdict:** kept (proposed) — dense init 20.1 → 7.5 min (−12.6 min) at equal quality. The 3-iteration variant was not trained (slower, no reason to prefer it).

### R-064 · 2026-11-12 · Speed-up phase 2: COLMAP global mapper settings (CPU)
- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/fast-pipeline` @ f33aeaf (no code change; COLMAP options only)
- **Dataset:** newRoomAttemptSadness, a copy of `work_v9e2e_sfm/database.db` (R-020's matches), output in `work_v9e2e_sfm/_mapper_exp/`.
- **Command(s):** `COLMAP global_mapper --database_path db.db --image_path work_v9e2e/images --output_path <variant>`
  with `--GlobalMapper.ba_num_iterations 1` (`ba1`) and with `--GlobalMapper.skip_retriangulation 1` (`noretri`).
- **Goal:** the mapper took 14.3 min in R-020 (global positioning 3.0, bundle adjustment 4.8, retriangulation +
  refinement 6.5; Ceres has no CUDA in this COLMAP build, so all on the CPU). Compare poses (Sim3-aligned camera
  centres in cm, rotations), points and lens parameters with R-020's `sparse/0`.
- **Start → end:** first attempt 02:18 → stopped during `ba1`'s retriangulation (~02:45, see R-063 error 1); restarted 16:45 → (running)
- **Errors during the run:**
  1. ~02:45 — stopped with exit code 4 together with R-063 (no COLMAP error in the log). Restarted at 16:45. (resolved: restarted)
- **Result:** (pending)
- **Verdict:** (pending)

### R-065 · 2026-11-12 · Fast pipeline end to end (`v10fast`): all kept speed-ups from the raw capture
- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/fast-pipeline` @ f33aeaf (uncommitted changes: yes: R-062 training changes, threaded
  `mono_prior.py`, `fast_mvs.py --photometric`, `sfm_colmap.py --skip_retriangulation`, `run_v8.py --init_args`)
- **Dataset:** newRoomAttemptSadness raw capture (nothing reused), same 79-frame off-path split as R-020
  (`dataset/newRoomAttemptSadness/offpath_test.txt`, a copy of `work_v9e2e_sfm/offpath_test.txt`).
- **Command(s):** `python src/arcore3dgs/run_v8.py --dataset dataset/newRoomAttemptSadness --tag v10fast
  --split dataset/newRoomAttemptSadness/offpath_test.txt --sfm_args "--retrieval 20 --skip_retriangulation"
  --init fmvs --init_args=--photometric --planar 0.2 --blur 0.0222`, then
  `eval_offpath.py --work work_v10fast_sfm --models v10fast=gs_v10fast/splat.ply`.
- **Goal:** R-020 took 96.2 min end to end (select 1.9, SfM 22.4, prior 8.1, init 20.4, train 42.5, export 0.7) for
  PSNR 25.16 / SSIM 0.8247 / sharpness 0.80 / flatness 0.77 cm. Expected here: ~55–65 min at the same quality.
- **R-064 result (mapper settings, used here):** two runs of the **default** mapper on the same matches already differ:
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
- **Verdict:** rejected as a recipe. Training (R-062) and the photometric init (R-063) each held quality on R-020's SfM,
  so the loss comes from the SfM stage: `--skip_retriangulation` and/or the mapper's run-to-run randomness (R-064). One
  run cannot separate the two. Next: the same run with the default mapper.

### R-066 · 2026-11-12 · New room `scan_3028a4de8fa0` with the proposed fast recipe (normal SfM + R-062/R-063 speed-ups)
- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/fast-pipeline` @ f33aeaf (uncommitted changes: yes, as R-065)
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
  (R-067): part of the SfM model is rebuilt at a smaller scale. Metric3D-to-SfM depth ratio per frame (`mono_prior/stats.json`)
  is ~2.2 up to frame ~3100 but ~0.6 for frames ~3180–3700 and ~4170–4600 (3.5× smaller). ARCore poses are broken
  after frame ~2200 (ARCore path 15–71 m per 60 keyframes), so `--pairs arcore` picked wrong spatial neighbours there,
  those frames were only weakly linked, and GLOMAP's global positioning shrank them. **Verdict changed: rejected (broken SfM).**
  Scale check: a table measured in the viewer (`view.py` measure tool) in the main ("outer") room gives the real table
  length (reported by the user 2026-11-12; value not recorded), so the main model's metric scale is right despite only
  97 ARCore inliers. Metric3D reads ~1.3× short on this room (newRoom: SfM/Metric3D ratio 1.35, here 1.75): not a scale error.


### R-067 · 2026-11-12 · `scan_3028a4de8fa0`: incremental mapper instead of GLOMAP (fix for R-066's mini room)
- **Who / machine:** Tayyab (agent) · RTX 3070 PC (CPU only)
- **Branch / commit:** `exp/fast-pipeline` @ f33aeaf (uncommitted changes: yes, as R-066)
- **Dataset:** `dataset/scan_3028a4de8fa0`, R-066's keyframes and matches (`work_v10_sfm/database.db` copied to
  `work_v10inc_sfm/`)
- **Command(s):** `python src/arcore3dgs/sfm_colmap.py --work dataset/scan_3028a4de8fa0/work_v10 --out
  dataset/scan_3028a4de8fa0/work_v10inc_sfm --mapper mapper --stage map`, then `--stage undistort`, `--stage export`
- **Goal:** one consistently scaled model of the hall (no shrunken sub-model); compare camera path with R-066's.
- **Start → end:** 20:58 → 21:24 (map stage 25.4 min, two mapping rounds)
- **Progress:** started 20:58. Mapping round 0 (12 min): incremental mapper split the frames into 7 components
  [565, 162, 33, 21, 19, 12, 3] of 842: it refuses to join the weakly linked part instead of shrinking it (as GLOMAP did).
  Bridge round 0: 277 frames outside the main component matched against 81 of it (22,437 pairs), mapping round 1 from 21:12.
- **Errors during the run:** none so far (many Ceres `CHOLMOD warning: Matrix not positive definite` lines in
  `mapper.log` during round 1: a failed LM step that Ceres retries, not a crash)
- **Result:** round 1 components [581, 162, 33, 21, 20, 2] of 842: the bridge round joined only 16 more frames. The
  main component (`sparse/0`, 581 frames) has **no shrunken part**: SfM/Metric3D depth ratio per frame within 0.83–1.44×
  of its median, 0 frames < 0.5× (R-066 model: 175 frames at ~0.38×; newRoom v9e2e control: 0). Check:
  `src/arcore3dgs/sfm_scale_check.py` (per-frame median of SfM depth / Metric3D depth, R-066's `mono_prior`). Missing from it:
  video frames 2640–3875 (162-frame component 2: walking along the side wall past the seat rows, then the front with
  the teacher's desk and screen) and 4182–4734 (front of the room near the desk: white floor and walls, close range,
  blurred). These are the frames GLOMAP shrank into the "mini room": repeated seat rows, plain white surfaces, fast
  motion, and wrong ARCore neighbours give too few correct matches to tie them to the rest.
- **Verdict:** confirms the R-066 diagnosis; incremental mapping gives a correctly scaled model of ~69% of the frames,
  not the whole walk. Next step chosen by Tayyab 2026-11-12: train on the main component (R-068).

### R-068 · 2026-11-12 · `scan_3028a4de8fa0`: rest of the fast recipe on R-067's main SfM component
- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/fast-pipeline` @ f33aeaf (uncommitted changes: yes, as R-066)
- **Dataset:** `dataset/scan_3028a4de8fa0`, SfM = R-067 `work_v10inc_sfm/sparse/0` (581 / 842 keyframes)
- **Command(s):** `python src/arcore3dgs/sfm_colmap.py --work dataset/scan_3028a4de8fa0/work_v10 --out
  dataset/scan_3028a4de8fa0/work_v10inc_sfm --mapper mapper --stage undistort` (and `--stage export`), then
  `python src/arcore3dgs/run_v8.py --dataset dataset/scan_3028a4de8fa0 --tag v10inc --from_stage export --init fmvs
  --init_args=--photometric --planar 0.2 --blur 0.030`
- **Goal:** a model of the hall without R-066's shrunken "mini room" (front of the room expected thin or missing).
- **Start → end:** 21:27 → 22:03 (undistort + SfM export ~3 min; run_v8 35.8 min: export 0.01, prior 3.30, init 3.44, CPU wait 0.00, train 28.43, ply 0.60)
- **Errors during the run:** none so far
- **Result:** `dataset/scan_3028a4de8fa0/work_v10inc_sfm/gs_v10inc/splat.ply` (158 MB). SfM export: 572 frames (9 more
  dropped as pose jumps), 32,418 points, ARCore alignment 100 inliers, median 6.6 cm. Metric3D/SfM scale per frame: 5 of
  572 frames < 0.5× the median, 2 > 2× (R-066: 175 < 0.5×). Top-down splat density with camera path
  (`gs_v10inc/topdown_vs_R-036.jpg`): R-066 shows a tight camera cluster and a ghost copy of the seat rows in the middle
  of the hall; R-068 shows clean seat rows and no ghost; the right-hand walk (component 2) is missing from the camera
  path, but that side of the hall is still built from the opposite side. Not measured: off-path PSNR (no held-out
  split), table length in the viewer (asked the user to re-measure).
- **Verdict:** mini room gone; kept as the model of this room until a recapture.

### R-069 · 2026-11-14 · roomAttemptSadness2: full v9 + PGSR pipeline → layout → semantics v10 → mesh → web (COMPLETION_PLAN 3.2, 4.2)
- **Who / machine:** Tayyab (agent, overnight session) · RTX 3070 PC
- **Branch / commit:** `exp/overnight-2026-11-14` (from `exp/fast-pipeline` d936e66; uncommitted: `scripts/run_full.sh`
  made to run on Windows Git Bash too)
- **Dataset:** `dataset/roomAttemptSadness2` (realme RMX5111, recorded by 2026-10-09; the second room of the mid report,
  so far only v3 / splatfacto runs R-002, R-004, R-010)
- **Command(s):** first attempt `GPU_EVERY=120 bash scripts/run_full.sh dataset/roomAttemptSadness2 v9pgsr -- --sfm_args "--retrieval 20"
  --init fmvs --planar 0.2 --blur 0.0222 --pgsr` (the R-023 / R-031 recipe; training uses this branch's exact TV-loss
  speed-up and the blur colour grid applied once, R-062; first run of those together with `--pgsr`)
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

### R-070 · 2026-11-14 · newRoom: MCMC densification at the baseline budget (`mcmc620`)
- **Who / machine:** Tayyab (agent, overnight session) · RTX 3070 PC
- **Branch / commit:** `exp/overnight-2026-11-14` (uncommitted: the `--mcmc_cap` option in `geo_splatfacto.py` until it is tested)
- **Dataset:** newRoomAttemptSadness, `work_v9e2e_sfm` (R-020's SfM, prior, fast-MVS init and off-path split)
- **Command(s):** `train_eval.sh mcmc620 --mcmc_cap 620000` (scratchpad helper = R-062's commands: `geo_splatfacto.py --data work_v9e2e_sfm/transforms_fmvs.json --iters 15000 --dash_res_steps 7500 --stop_split_at 7500 --no_eval --prior mono_prior/train_v9e2e.npz --planar_lambda 0.2 --blur_exposure 0.0222 --mcmc_cap 620000`, `ns-export`, `eval_offpath.py` vs `gs_v9e2e` on the 79 off-path frames)
- **Goal:** gsplat `MCMCStrategy` (3DGS as MCMC, Kheradmand et al. 2024: relocation of dead Gaussians + position noise, opacity / scale regularisers 0.01) instead of splatfacto's split / clone / prune, capped at ~620k Gaussians (v9e2e has 619,056). New `--mcmc_cap` option in `geo_splatfacto.py`. Does it beat R-062 (25.14 / 0.8251) at the same size?
- **Start → end:** 03:27 → 04:03 (train 35.0 min)
- **Errors during the run:** none so far
- **Result:** `work_v9e2e_sfm/gs_mcmc620/` (eval sheets in `eval/`). MCMC grew from the 258k-point init by 5% per 100
  steps as expected (e.g. step 900: 15,352 relocated, 14,954 added, 314,042 total); the exported `splat.ply` has
  402,989 Gaussians (why fewer than the cap was not investigated). Off-path, 79 frames: **PSNR(cf) 24.65 / SSIM 0.8216 /
  sharpness 0.64 / flatness 0.98 cm** vs v9e2e 25.16 / 0.8247 / 0.80 / 0.77 and R-062 25.14 / 0.8251 / 0.80 / 0.81.
  Full-resolution steps ~209 ms (R-062 ~160 ms). Crops: printer edges, plant leaves and floor grain visibly softer.
- **Verdict:** **rejected** (one setting). Possible reasons, not tested: relocation stops at step 7,500 (half of
  training; gsplat's default keeps it to 25k of 30k), interaction with the DashGaussian low-resolution phase and the
  depth / normal priors, the opacity regulariser pushing opacities down.

### R-085 · 2026-11-23 · scan #6 fixture check sheet from R-059 (`r1119b6`), CPU only
- **Who / machine:** agent for Umair · this PC (Ubuntu, RTX 4000 Ada), while R-071 (`run-r071g6`, speed session) runs
  `patch_match_stereo` on the GPU; this run uses no GPU and a few MB of RAM (standard-library script).
- **Branch / commit:** `feature/step4-triage` (worktree `../BuildScan3D-step4`, from `origin/master` `8338680`)
- **Dataset:** R-059's `dataset/scan_006_1e457a214ce1/work_r1119b6_sfm/gs_r1119b6/semantic_v10/semantic.json` and
  `layout/layout.json` (read only). The sheet goes to a new folder `dataset/scan_006_1e457a214ce1/checks_r085/`, so
  R-059's run folder is not written.
- **Command(s):** `python3 src/arcore3dgs/fixture_checklist.py --semantic <gs_r1119b6>/semantic_v10/semantic.json
  --layout <gs_r1119b6>/layout/layout.json --out dataset/scan_006_1e457a214ce1/checks_r085/fixture_check.md
  --title "scan #6 (R-059, r1119b6)" --rejected`
- **Goal:** the scan #6 sheet for Umair (#21, plan 4.2), like the other rooms' sheets.
- **Start → end:** (running)
- **Errors during the run:** none so far.
