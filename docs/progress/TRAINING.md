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

Second clash, same rule (2026-11-19, merge of `master` into `docs/featureless-tracking-plan`): Tayyab's night runs
**R-053 → R-071** (scan_009 loop closure) and **R-054 → R-072** (newRoom validation); his decision **D-069 → D-080**
(featureless tracking, option 1) and open decisions **OD-12 → OD-14**, **OD-13 → OD-15**. Commit messages `c1b2b8f`,
`113e7a5` and the scripts `r053.sh` / `r054.sh` in the dataset folders keep the old numbers.

R-032 – R-040 now always mean Umair's runs on the Ubuntu PC; R-041 – R-046 (Tayyab) did not collide and are unchanged.

**Renumbered runs (2026-11-23, D-091).** Tayyab's branch `docs/featureless-tracking-plan` (pushed 2026-11-18 – 22) already
used R-047 – R-052, R-071 – R-100 and D-080 / D-081. Umair chose to renumber ours: **R-071 → R-101** (scan #6 GPU COLMAP;
tag `r071g6` and screen `run-r071g6` keep the old name), **R-072 → R-102**, the Step 4 session's **R-085 / R-086 → R-103 /
R-104**, the pending GPU-COLMAP decision **D-080 → D-082**. A comment in `sfm_colmap.py` keeps "R-072" (not edited while
R-101 runs). Next free: R-105, D-092.

**Tayyab's runs after D-091 (2026-11-23, D-096).** Tayyab's unpushed session had also taken R-101 – R-103 and D-082;
they became **R-120** (pose refinement), **R-121** (gated second loop round), **R-122** (viewer model) and **D-095**
(analyzer plan). Scripts / logs in the dataset folder keep `r101` – `r103`. Next free on Tayyab's side: R-123, D-097;
Umair's side continues at R-105.

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
| R-047 | 2026-11-18 | scan_009: R-046's ALIKED model with the gyro rotation check (`--gyro_thr 2`, `v9pfg`) | 3070 | 32.2 min from export (train 25.3) | 370 frames; path jumps 51 → 21; +1.0 dB on common training views (not held out); jumps and shrunken blocks remain | Inconclusive |
| R-048 | 2026-11-18 | scan_009: incremental mapper on R-046's ALIKED matches + gyro check (`v9pfm`) | 3070 | 73 min SfM (stopped before training) | 684 frames in one component but locally wrong (IMU \|g\| 1.9); ARCore Sim3 182 broke the jump filter | Rejected |
| R-049 | 2026-11-18 | scan_009: SfM export only, gyro check + placing unplaced frames with gyro rotation + known-rotation fit (`v9pfp`) | 3070 (CPU) | ~1.5 min | 157 of 442 placed, 90 kept; 476 frames; path jumps 40 (R-047: 21) | Inconclusive |
| R-050 | 2026-11-18 | scan_009: diagnosis of the SfM failure (IMU scale per window, gyro pair test, short-range mapping, ARCore vs gyro) | 3070 | ~55 min | SfM locally wrong in both mappers; not wrong matches, not timing; ARCore poor (gyro corr 0.34); IMU clean | Diagnosis |
| R-051 | 2026-11-18 | scan_009: gyro-rotation + accelerometer SfM (`rot_sfm.py`, `v9pfr`) | 3070 | 30.0 min from export (train 22.8) | 698 frames, 23,508 points at 1.76 px; −1.9 dB vs R-047, blurrier; scale ~2–3× too large | Rejected |
| R-052 | 2026-11-19 | scan_009: R-051's poses refined by BA with gyro / accelerometer priors (`prior_ba.py`, `v9pfb`) | 3070 | ~78 min (two trainings) | 698 frames, reprojection 1.77 → 1.22 px, gyro kept (2 frames > 2°); +0.49 dB vs R-051; ≈ R-047 (mean 19.30 vs 19.31), loop not closed | Kept (coverage) |
| R-053 | 2026-11-19 | Layout re-runs on six rooms, no-roof check (#8), scratch output | this PC (Ubuntu, RTX 4000 Ada) | 8.8 min | scan #7: no roof, walls 3.12 m (was ceiling 3.435 m); 5 other rooms unchanged | Kept (#8) |
| R-054 | 2026-11-19 | scans #7 / #3: layout (#8 #9 #10) → semantics → mesh labels → web, tag `r1119a` | this PC (Ubuntu, RTX 4000 Ada) | 8.1 min | #7 no roof, 1 doorway + 3 window openings, open outline; #3 open outline flagged, triangle area gone, 4 false openings | Superseded (#9 fixed after it) |
| R-055 | 2026-11-19 | Layout on six rooms, `--debug`, default vs `--raised_max 1.5 --infer_gap 6` | this PC (Ubuntu, RTX 4000 Ada) | 16.9 min | scan #3 no false openings; `--raised_max` closes #7 and #8 (4 walls, 88–90°), drops nothing real | Kept (findings) |
| R-056 | 2026-11-19 | Four rooms, layout → web → plan with the 2026-11-19 defaults, tag `r1119b` | this PC (Ubuntu, RTX 4000 Ada) | 15.6 min | #7 no roof + 2 openings; #3 no false openings; newRoom closed, 29.41 m²; #8 open, 2 doorways | Kept (for Umair's checks) |
| R-057 | 2026-11-19 | Four rooms, layout → web → plan with the D-075 defaults, tag `r1119c` | this PC (Ubuntu, RTX 4000 Ada) | 16.7 min | #7 / #8 closed rectangles (17.99 / 26.44 m²); #3 tilt 0.29°; ceilings 4.3 → 0.04 cm; #8 lost a switch + socket | Kept (scan #8 corner = furniture, Umair) |
| R-058 | 2026-11-19 | scan #6 `scan_006_1e457a214ce1` (259.8 s), full pipeline, R-023 recipe + D-075 (`r1119`) | this PC (Ubuntu, RTX 4000 Ada) | 45.5 min, did not finish | 1159 frames, 12.56 M observations; COLMAP `global_mapper` killed by OOM (26.4 GB) at 16:14:39 while the agent ran web work | Failed (OOM in SfM) |
| R-059 | 2026-11-19 | scan #6 rerun after R-058, same recipe, PC kept quiet (`r1119b6`) | this PC (Ubuntu, RTX 4000 Ada) | 183.8 min (run_v8 162.5) | 1159/1159 frames; height 3.05 m, closed, 7 walls; 11 fixtures, 84 rejected | Kept (not checked by a person) |
| R-103 | 2026-11-23 | scan #6 fixture check sheet from R-059 (`fixture_checklist.py --rejected`, no GPU) | this PC (Ubuntu, RTX 4000 Ada) | < 1 s | `scan_006…/checks_r085/fixture_check.md`: 11 fixtures + 84 rejected; switches 2 / 5 maybe one plate | Kept (for Umair, #21) |
| R-104 | 2026-11-23 | Wall roughness in the mesh, where it sits (4.12, #18), four rooms, read-only, CPU | this PC (Ubuntu, RTX 4000 Ada) | 3.4 s | 16 of 20 walls ≤ 0.26 cm; rough: newRoom wall 3 (2.88, bowed), scan #8 wall 1 (1.55, offset stretches), scan #6 wall 5 (4.70, two surfaces) | Inconclusive (look in the viewer) |
| R-062 | 2026-11-12 | Training speed-up: exact TV-loss / colour-affine fixes, blur colour grid once (`fast_t1`) | 3070 | 28.2 min train (was 42.5) | 25.14 / 0.8251, sharp 0.80, flat 0.81 | Kept (proposed) |
| R-063 | 2026-11-12 | Photometric-only fast-MVS init (`fast_t2_photo`) | 3070 | init 7.5 min (was 20.1) | 25.16 / 0.8240, flat 0.78 | Kept (proposed) |
| R-064 | 2026-11-12 | Global mapper settings (`ba1`, `noretri`, default rerun) | 3070 | mapper 9.4 – 14.5 min | default runs differ by ~16 cameras | Inputs to R-065 |
| R-065 | 2026-11-12 | Fast pipeline end to end incl. `--skip_retriangulation` (`v10fast`) | 3070 | 61.6 min (was 96.2) | 24.56 / 0.8078, visible smears | Rejected (SfM shortcut) |
| R-066 | 2026-11-12 | New room `scan_3028a4de8fa0` (tiered lecture hall), normal SfM + speed-ups | 3070 | 48.8 min | fits training views; mini room inside the room (SfM scale collapse, see R-067) | Rejected |
| R-067 | 2026-11-12 | `scan_3028a4de8fa0`: incremental mapper instead of GLOMAP (fix R-066 mini room) | 3070 (CPU) | map 25.4 min | 581/842 frames in one correctly scaled model; front of room split off | Diagnosis confirmed |
| R-068 | 2026-11-12 | `scan_3028a4de8fa0`: fast recipe on R-067's 581-frame SfM (`v10inc`) | 3070 | 35.8 min (+ map 25.4, R-067) | no mini room; right-side walk missing | Kept |
| R-069 | 2026-11-14 | roomAttemptSadness2: full v9 + PGSR → semantics → mesh → web (`v9pgsr8`) | 3070 | 87.7 min to the model + 32 min after | height 2.78 m; 22 fixtures (unchecked) | Kept (fixtures to check) |
| R-070 | 2026-11-14 | newRoom: MCMC densification at the baseline budget (`mcmc620`) | 3070 | 35.0 min train | 24.65 / 0.8216, sharpness 0.64 (softer) | Rejected |
| R-071 | 2026-11-19 | scan_009: loop closure (gyro bias from far-apart pairs, rot_sfm with all pairs, prior BA; `v9pfl`) | 3070 | 55 min | 680 frames, loop closed (> 120 s pairs 15.6° → 3.5°), scale check ok; PSNR ≈ R-047 / R-052; scale ~2× too large (not applied) | Kept (most complete) |
| R-072 | 2026-11-19 | newRoom: validation of the R-071 recipe against the trusted SfM path | 3070 | 34 min | position error median 72 → 31 cm (p90 166 → 68 cm), scale 0.89; still far worse than normal SfM | Validation |
| R-073 | 2026-11-19 | newRoom: video point tracks (`video_tracks.py`) added to the R-071 recipe, against the trusted SfM path | 3070 | 11.6 min | position error median 31.1 → 37.5 cm (p90 68.4 → 74.2); 3D obs per image 370 → 682 | Rejected (as is) |
| R-074 | 2026-11-19 | newRoom: prior BA with loose position priors, with and without video tracks (are the priors the bottleneck?) | 3070 | 28 min | loose priors: 31.1 → 21.9 cm median (p90 68.4 → 48.3); with video tracks 22.9 cm | Kept (finding) |
| R-075 | 2026-11-19 | newRoom: prior BA with position priors nearly off (`--s_t1 30`), 150 iterations | 3070 | 20 min | **14.8 cm median, p90 35.9** (R-072: 31.1 / 68.4); cost still falling slowly at 142 iterations | Kept (finding) |
| R-076 | 2026-11-20 | scan_009: video tracks + prior BA with default / loose / nearly-off position priors (no training) | 3070 | 10 min | tracks fill little: 45 – 60 s still 0 points per camera; cameras < 10 points 202 → 173; priors nearly off → path jumps (max step 69× median) | Rejected (finding) |
| R-077 | 2026-11-20 | scan_009: video-track pair directions into `rot_sfm.py` (`--extra_pairs`), then prior BA (`v9pfv`, no training yet) | 3070 | 4 min | +1,321 directions from tracks, but 641 cameras kept (R-071: 698); 45 – 60 s: 36 cameras, still 0 points median | Rejected (as is) |
| R-078 | 2026-11-20 | Adaptive position priors in `prior_ba.py` (`--adapt_n 150`): tight where a keyframe pair has few 3D observations, loose where it has many; newRoom + scan_009 | 3070 | 21 min | newRoom 16.2 cm median, p90 29.6 (R-075 free: 14.8 / 35.9; R-071 recipe 31.1 / 68.4); scan_009 no jumps (max step 9.2× median), empty stretches unchanged | Kept (recipe for the BA step) |
| R-079 | 2026-11-20 | scan_009: track directions with more weight (`--extra_w 10` / `30`, `--extra_min_inliers 8`) into `rot_sfm.py`, then the R-078 adaptive BA (`v9pfw`, `v9pfy`, no training yet) | 3070 | 11 min | path now agrees with the tracks in 45 – 60 s (4.3° vs 46.9°); 647 cameras (×30), empty stretches still 0 points median | Kept as input for R-080 (×30) |
| R-080 | 2026-11-20 | scan_009: video tracks re-triangulated on R-079's path (`v9pfy`), then the adaptive BA (no training yet) | 3070 | 3.5 min | 7,263 track points; 90 – 105 s median 3D obs 3 → 23; 45 – 60 s still 1 (video has no trackable texture there); reprojection 1.13 px | Kept (best scan_009 SfM so far, not trained) |
| R-081 | 2026-11-20 | scan_009: train on R-080's camera model (`v9pfz`, R-071's training recipe) for the web viewer | 3070 | 28.8 min | 622 frames, 542,469 splats; training-view PSNR median 19.59 vs R-071 19.52 on 607 common frames, better on 61%; scale check ok | Kept (best scan_009 model so far, in the web viewer) |
| R-082 | 2026-11-20 | scan_009: plan 10.a baseline, R-081 recipe with 69 frames held out (`v9pfh`) | 3070 | 28.3 min | held-out (69 frames) PSNR 20.80, SSIM 0.874, flatness 8.18 cm, 573,257 splats; R-081 on the same frames (seen in training) 23.98 / 0.909 / 5.98 cm | Kept as the §10 baseline |
| R-083 | 2026-11-20 | scan_009: plan 10.f, R-082 plus gyro motion blur (`v9pfi`) | 3070 | 34.4 min | held-out PSNR 20.86 (R-082 20.80), SSIM 0.871 (0.874), sharpness 0.43 (0.28), flatness 9.85 cm (8.18), 586,509 splats; train 28.0 min (21.9) | Inconclusive |
| R-084 | 2026-11-20 | scan_009: plan 10.d, R-082 plus pose refinement in training (`v9pfj`) | 3070 | 29.3 min | held-out PSNR 20.20 (R-082 20.80), flatness 7.40 cm (8.18); after test-pose alignment (`eval_align.py`) 22.39 vs R-082 22.64, R-083 22.51 | Rejected (no gain once poses are aligned) |
| R-085 | 2026-11-20 | scan_009: plan 10.c, tracks ↔ path loop from R-080's model (`track_loop_r085`) | 3070 | 18.2 min | cameras 647 → 676 → 656, 3D obs median 120 → 91 → 109, < 10 obs 110 → 144 → 123; stopped after round 2 | Rejected (R-080 stays the best model) |
| R-086 | 2026-11-21 | scan_009: plan 10.e, R-082 with stronger geometry weights (`v9pfk`) | 3070 | 30.5 min | held-out PSNR 20.75 (R-082 20.80), **flatness 4.98 cm (8.18)**; aligned PSNR 21.85 (22.64); a flat sheet blocks the 134 s view | Inconclusive (flatter walls, lower PSNR) |
| R-087 | 2026-11-21 | scan_009: plan 10.b-1, rolling-shutter-rectified keyframes on R-080's cameras (`v9pfs`) | 3070 | 29.7 min | held-out PSNR 20.69 vs R-082 20.81 (rectified photos), flatness 3.55 vs 8.87 cm; aligned 22.22 vs 22.66; 51 – 53 s +1.6 dB aligned; views at 134 s and 186 s blocked | Inconclusive (run-to-run spread not known) |
| R-088 | 2026-11-21 | scan_009: R-082 repeated unchanged, run-to-run spread (`v9pfn`) | 3070 | 28.8 min | vs R-082: held-out PSNR 21.05 vs 20.80, flatness 6.65 vs 8.18 cm, aligned 22.55 vs 22.65; per stretch up to ±0.9 dB, per frame median 0.70 dB | Kept (noise reference) |
| R-089 | 2026-11-21 | scan_009: R-087 (rectified keyframes) plus path pruning in training (`v9pfo`) | 3070 | 29.4 min | blocked views 1 (R-087 16, R-082 7); PSNR 20.68, aligned 22.21 (R-087 22.18, R-082 22.64); 51 – 53 s aligned 24.18 (R-082 21.59) | Inconclusive (best in 51 – 53 s, not overall) |
| R-090 | 2026-11-21 | scan_009: R-082 plus path pruning in training (`v9pfq`) | 3070 | 28.2 min | blocked views 0 (R-082 7); PSNR 21.10, aligned 22.52 (R-082 22.64, R-088 22.54) | Kept: pruning costs nothing and removes the blocked views |
| R-091 | 2026-11-21 | scan_009: plan 10.b-2, SfM chain (features, rot_sfm, adaptive BA, one track round) on the rectified keyframes (`v9pfs2`) | 3070 | ~1 h 40 min of work (plus a pause) | final 647 cameras, 3D obs median 100 (R-080 120); 45 – 60 s: 30 cameras, obs median 0 (R-080 41, 1) | Rejected (not trained) |
| R-092 | 2026-11-21 | scan_009: R-090 plus depth priors for frames without SfM support (`--fill_scale`, `v9pfu`) | 3070 | 29.9 min | flatness 6.77 vs 9.92 cm (R-090), 0 blocked; aligned PSNR 22.26 vs 22.52, SSIM 0.880 vs 0.878; held-out pose correction 1.62° vs 2.02° | Kept for inspection (flatter, PSNR −0.26) |
| R-093 | 2026-11-21 | scan_009: plan 11.a, VGGT on keyframes (42 – 63 s) and dense video frames (44 – 60 s) (feasibility, no training) | 3070 | 22 – 43 s per chunk | textured part: rotation steps within 0.6 – 0.9° of the gyro, depth consistent across frames (2.5 – 5.3 % vs Metric3D priors 15.1 %); blank wall (48 – 60 s): steps 3.5 – 10° off (max 92°), confidence at its floor | VGGT cannot place the blank-wall frames; its depth is far more consistent than the per-frame Metric3D priors |
| R-094 | 2026-11-21 | scan_009: plan 11.b, camera path scale drift corrected with the room height, then R-090's recipe (`v9psc`) | 3070 | 29.2 min | room height along the walk 5.0 – 6.0 units (before 4.6 – 7.6); aligned PSNR 22.59 vs R-090 22.63 on 66 common held-out frames (late walk +1.1 – 1.2 dB, 51 – 53 s −2.1 dB) | Kept (cameras for 11.c); no image gain by itself |
| R-095 | 2026-11-21 | scan_009: plan 11.c, depth / normal priors rewritten from the room planes (`plane_prior.py`) on R-094's cameras (`v9ppl`) | 3070 | 24.8 min | neighbouring-frame depth disagreement 6.8 → 3.6 %; held-out PSNR 19.94 vs R-094 20.85, aligned 21.53 vs 22.59 (66 frames) | Rejected (the plane set is still fragmented) |
| R-096 | 2026-11-22 | scan_009: plan 11.d, loops closed with the long-range image pairs (`loop_path.py`, `prior_ba.py --pair_priors`) on R-094's cameras (`v9plp`) | 3070 | 28.3 min (+7 min solve / BA) | held-out loop pairs >= 60 s: 7.0 → 2.5° median; **aligned 22.67 → 23.63 on the 63 common held-out frames**, every stretch equal or better; off-path views more coherent | **Kept** (first clear gain) |
| R-097 | 2026-11-22 | scan_009: 11.d second round, loop pairs chosen with R-096's cameras and matched (`loop_match.py`, `v9plm`) | 3070 | 28.7 min (+3 min matching / solve) | aligned 22.93 vs R-096 23.63 (63 frames): four stretches better, 134 – 137 s broken (20.10 → 15.81) | Rejected (new pairs need a stricter check) |
| R-098 | 2026-11-22 | scan_009: 11.c second form, prior pixels contradicted by other views dropped (`prior_consistency.py`) on R-096's cameras (`v9pcs`) | 3070 | 24.0 min | loop-partner depth disagreement 12.4 → 9.1 %; aligned 23.61 vs R-096 23.63 (63 frames), SSIM 0.892 vs 0.888, flatness 8.54 vs 6.57 | Inconclusive, not adopted |
| R-099 | 2026-11-22 | scan_009: R-096's recipe on all frames, for the viewer (`v9plf`, `scan-009-loops`) | 3070 | 27.9 min | no held-out score (all frames); off-path views as R-096 | Kept (viewer) |
| R-100 | 2026-11-22 | scan_009: floater clean-up (`clean_splats.py --mono`) on R-096's model, no retraining | 3070 | 37 min (3 cleanings 20 s, evaluations 36 min) | aligned on 63 held-out frames: both rules 23.31, see-through rule only 23.54, camera-path rule only 23.40 (R-096 23.63); bathroom doorway (125 s) unchanged | Rejected as the doorway fix; see-through rule neutral, camera-path rule harmful |
| R-120 | 2026-11-22 | scan_009: R-096 plus camera refinement in training (`--pose_opt`, `v9plo`) | 3070 | 30.4 min (train 24.3, R-096 22.5) | aligned 23.96 vs R-096 23.63 (63 frames), SSIM 0.896 vs 0.888; 35 frames > 0.5 dB better, 13 worse; doorway (125 s) unchanged | Kept (modest gain, +1.8 min training) |
| R-121 | 2026-11-22 | scan_009: second loop round with a pair check (`loop_path.py --gate 10`), R-096's recipe (`v9plg`) | 3070 | 28.5 min + 1.5 min solve / BA | aligned 22.91 vs R-096 23.58 on 60 common frames; 30 – 90 s +1.6 – 1.8 dB, 134 – 140 s broken again (20.10 → 15.83); path hole 125.4 – 133.2 s found | Rejected (the hole, not the pairs, breaks 134 – 140 s) |
| R-122 | 2026-11-23 | scan_009: R-120's recipe (R-096 cameras + `--pose_opt`) on all frames, for the viewer (`v9plq`) | 3070 | 32.8 min (train 25.95) | no held-out score (all frames); 521,715 splats | Kept (viewer `scan-009-poseopt`) |
| R-123 | 2026-11-23 | scan_009: R-121's gated loop round with path holes held (`loop_path.py --hole_dt 2.5`), R-120's recipe (`v9plh`) | 3070 | 35.1 min (train 28.66) + 2 min solve / BA | aligned 22.83 vs R-120 23.97 (60 frames); 134 – 140 s still broken (15.52); R-121's 30 – 90 s gains lost | Rejected (the holes are not why 134 – 140 s breaks) |
| R-124 | 2026-11-23 | Analyzer, first part (`analyze_recording.py`) on the four test recordings (read-only, CPU) | 3070 | < 10 s per recording | newRoom / bedroom textured → normal SfM; lecture hall 68 % placed, 34 % holes → sensor path; scan_009 normal SfM 37 % placed → sensor path; labels match the known stretches | Kept (first thresholds by hand, not tuned) |
| R-125 | 2026-11-24 | scan_009: room-plane anchoring preview, splats near one shared plane per wall / floor snapped onto it (`plane_snap.py`) on R-120's model, no training | 3070 | snap 8 s, evaluation 11 min | aligned 20.32 vs R-120 23.96 (63 frames); 20 % of splats snapped onto 68 planes; planes form the room outline; glittery walls; two floor levels 0.56 units apart | Preview only: snapping must happen in training |
| R-126 | 2026-11-24 | scan_009: R-120's recipe with room-plane anchoring in training (`--plane_anchor`, `v9pla`) | 3070 | 31.5 min (train 24.93) | aligned 22.07 vs R-120 23.96 (63 frames); flatness 3.81 vs 6.12 cm; straight walls from above; 134 – 140 s broken (15.87); ~95 % of splats moved | Inconclusive: flatter walls, −1.9 dB; anchoring too broad |
| R-127 | 2026-11-25 | scan_009: unplaced keyframes in path holes placed from image directions + gyro (`direction_fill.py`; `arcore_fill.py` rejected), R-120's recipe (`v9plb`) | 3070 | 33.4 min (train 26.46) + fill 1 min | aligned 23.22 vs R-120 23.96 (63 frames); 60 – 90 s −1.1, 134 – 140 s −2.1, 30 – 60 s +1.1 dB; 19 of 29 added frames survived the export jump filter | Rejected (added frames conflict) |
| R-128 | 2026-11-25 | scan_009: R-120 plus extra video frames between keyframes in weak / featureless windows (`densify_frames.py`, `v9pld`) | 3070 | 34.0 min (R-120 30.4; prior +2.1, init +1.0, train +0.8) | **aligned 24.25 vs R-120 23.96**, SSIM 0.898; 30 – 60 s +4.7 dB (4 frames), 0 – 30 s +0.9, 134 – 140 s −1.5; 266 frames added | **Kept** (new best, +3.6 min) |
| R-129 | 2026-11-25 | scan_009: R-128 plus learnable blur motion (`--blur_learn`, `v9plk`) | 3070 | running | | |
| R-130 | 2026-11-25 | scan_009: Depth Anything 3 (DA3-LARGE) feasibility on four chunks, same checks as VGGT in R-093 (no training) | 3070 | planned (after R-129) | | |

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
- **Errors during the run:** none (memory came within ~2 GB of running out at 13:50, see above).
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
- **Errors during the run:** none
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
- **Errors during the run:** none
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
- **Errors during the run:** none
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
- **Errors during the run:** none
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
  Does COLMAP's incremental mapper (correct but partial on the lecture hall, R-068; OD-11) give a cleaner model of
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
- **Start → end:** 16:33:50 → 19:37:41 = **183.8 min** ("all done" in `gs_r1119b6/run_full.log`). Stage times (`timing.json`,
  `stages.tsv`): run_v8 162.5 min = select 0.53, SfM 86.07, export 0.01, prior 5.23, init 19.41, train 50.53, ply
  0.73; then layout 1.4, sem2d 17.6, sem3d 0.2, verify 0.2, sem3d2 0.2, mesh 0.3, meshlabels 1.5, web 0.1, plan 0.0 min.
  Inside SfM (`global_mapper.log`, as quoted in R-101): global positioning 2,240.92 s, iterative BA 1,528.52 s,
  retriangulation + refinement 733.86 s, reconstruction 4,535.88 s.
- **Errors during the run:** none (no traceback in `run_full.log`; only timm `FutureWarning`s). SfM passed in RAM with
  the PC kept quiet (R-058's failure did not repeat).
- **Result** (written up 2026-11-23 from the run's files, R-103): `work_r1119b6_sfm/gs_r1119b6/` (`splat.ply`
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
  (check sheet: R-103), render quality (no held-out split).
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
- **Start → end:** first attempt 02:18 → stopped during `ba1`'s retriangulation (~02:45, see R-063 error 1); restarted 16:45 → end not recorded (finished before 17:28, when R-065 started with its result)
- **Errors during the run:**
  1. ~02:45 — stopped with exit code 4 together with R-063 (no COLMAP error in the log). Restarted at 16:45. (resolved: restarted)
- **Result:** written up in R-065 ("R-064 result", closed 2026-11-23 from that text): two default mapper runs on the same
  matches differ by median 0.48 cm (16 cameras > 10 cm); `skip_retriangulation` 9.4 vs 14.3 min, median 0.90 cm, within that
  spread; `ba_num_iterations 1` 14.2 min, 51 cameras > 10 cm.
- **Verdict:** `skip_retriangulation` kept for R-065, whose recipe was then rejected (the loss may come from it or from the mapper's run-to-run randomness, R-065); `ba_num_iterations 1` rejected.

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
- **Errors during the run:** none (many Ceres `CHOLMOD warning: Matrix not positive definite` lines in
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
- **Errors during the run:** none
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
- **Errors during the run:** none
- **Result:** `work_v9e2e_sfm/gs_mcmc620/` (eval sheets in `eval/`). MCMC grew from the 258k-point init by 5% per 100
  steps as expected (e.g. step 900: 15,352 relocated, 14,954 added, 314,042 total); the exported `splat.ply` has
  402,989 Gaussians (why fewer than the cap was not investigated). Off-path, 79 frames: **PSNR(cf) 24.65 / SSIM 0.8216 /
  sharpness 0.64 / flatness 0.98 cm** vs v9e2e 25.16 / 0.8247 / 0.80 / 0.77 and R-062 25.14 / 0.8251 / 0.80 / 0.81.
  Full-resolution steps ~209 ms (R-062 ~160 ms). Crops: printer edges, plant leaves and floor grain visibly softer.
- **Verdict:** **rejected** (one setting). Possible reasons, not tested: relocation stops at step 7,500 (half of
  training; gsplat's default keeps it to 25k of 30k), interaction with the DashGaussian low-resolution phase and the
  depth / normal priors, the opacity regulariser pushing opacities down.


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

### R-073 · 2026-11-19 · newRoomAttemptSadness: video point tracks added to the R-071 recipe (no training)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 45de8b5 (uncommitted: new `src/arcore3dgs/video_tracks.py`)
- **Dataset:** newRoomAttemptSadness, keyframes `work_v9e2e`, input model `work_rotsfm_loop/sparse/0` (R-072's
  rot_sfm with loop bias, before prior BA); trusted path `work_v9e2e_sfm/sparse/0` (0.668 m per unit)
- **Command(s):** `dataset/newRoomAttemptSadness/r073.sh` (log `r073.log`): `video_tracks.py` → `work_rotsfm_loop/
  sparse_vt`; `prior_ba.py` → `sparse_vt_pba`; scratchpad `eval_rot.py` against the trusted path, next to R-072's
  `sparse_pba` (31.1 cm median)
- **Goal:** FEATURELESS_TRACKING_PLAN §10 technique 1: do KLT tracks through every video frame lower the position
  error of the sensor-based path? Must be checked here before scan_009.
- **Start → end:** 23:00 → 23:12 (tracking 100 s for 7,177 video frames; RANSAC + triangulation ~1.5 min; prior BA
  593 s; eval 10 s)
- **Errors during the run:** none. Before it: seeking in the mp4 (`CAP_PROP_POS_FRAMES`) is not frame-exact (keyframe
  vs sought frame mean difference 14 – 48 grey levels); decoding in order matches `video_index` exactly (0.12 – 0.19).
  `video_tracks.py` decodes in order.
- **Result:**
  - Tracks: 305,892 started (≤ 300 new corners per keyframe, half resolution, CLAHE, forward-backward < 0.7 px);
    994,328 keyframe observations; rotation-fixed RANSAC rejected 40,954 of 688,431 tested pair observations (5.9%).
    Triangulated 47,240 new points (308,429 observations); rejected: 168,196 seen in one keyframe only, 72,843 parallax
    < 1°, 17,023 reprojection > 10 px, 590 behind a camera.
  - 3D observations per image: median 370 → 682; images with < 20: 94 → 74; < 50: 149 → 106.
  - `prior_ba.py`: 858,595 observations; reprojection median 0.73 px (p90 1.85); position change median 0.288 units.
  - Against the trusted path (Sim3 fitted): R-072's `sparse_pba` 31.1 cm median / 68.4 cm p90 / step spread 1.89×;
    **with video tracks 37.5 / 74.2 cm / 2.24×** (scale 0.901).
- **Verdict:** rejected as is: more local observations made the path slightly worse. newRoom already had 370 points
  per frame and fits them at 0.73 px, so its 31 cm error is not missing matches but a smooth bend of the whole path.
  Suspected cause: the relative position priors (`--s_t1 0.3` of the sensor step) hold the path near the noisy sensor
  solution. Checked next in R-074. One capture only; scan_009 not run.

### R-074 · 2026-11-19 · newRoomAttemptSadness: prior BA with loose position priors (no training)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 45de8b5 (uncommitted: `video_tracks.py`)
- **Dataset:** as R-073 (input `work_rotsfm_loop/sparse/0` and R-073's `sparse_vt`)
- **Command(s):** `dataset/newRoomAttemptSadness/r074.sh` (log `r074.log`): `prior_ba.py --s_t0 0.2 --s_t1 3.0
  --iters 60` (position priors 10× looser) on both models; scratchpad `eval_rot.py`
- **Goal:** is R-072's 31 cm error held in place by the sensor position priors? If yes, loosening them moves the path
  toward the trusted one, and the video tracks may help after all.
- **Start → end:** 23:12 → 23:40 (820 s + 836 s; eval 15 s)
- **Errors during the run:** none. The log filter dropped the per-iteration lines, so whether 60 iterations were all
  used is not known (round 1 took ~580 s, consistent with all 60).
- **Result:** against the trusted path, median / p90 / step spread:

  | Model | Default priors (R-072 / R-073) | Loose priors (`--s_t0 0.2 --s_t1 3.0`) |
  |---|---|---|
  | rot_sfm with loop bias | 31.1 / 68.4 cm / 1.89× | **21.9 / 48.3 cm / 1.63×** (scale 0.912) |
  | same + video tracks | 37.5 / 74.2 cm / 2.24× | 22.9 / 50.4 cm / 1.71× |

  Reprojection 0.66 / 0.73 px; relative rotation vs the gyro prior still 0.09 – 0.11° median.
- **Verdict:** the position priors were holding the path near the noisy sensor solution: loosening them cuts the error
  by 30%. The video tracks still add nothing on newRoom (it is not short of matches). Next: priors almost off and more
  iterations (R-075).

### R-075 · 2026-11-19 · newRoomAttemptSadness: prior BA with position priors nearly off (no training)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 45de8b5 (uncommitted: `video_tracks.py`)
- **Dataset:** as R-074, input `work_rotsfm_loop/sparse/0` only
- **Command(s):** `dataset/newRoomAttemptSadness/r075.sh` (log `r075.log`, iterations kept): `prior_ba.py --s_t0 2
  --s_t1 30 --iters 150` → `sparse_pba_free_t`; scratchpad `eval_rot.py`
- **Goal:** how far do the images alone (rotations still tied to the gyro) move the path toward the trusted one, and
  does the solver stop by convergence or by the iteration limit?
- **Start → end:** 2026-11-19 23:41 → 2026-11-20 00:01 (round 1: 142 iterations, 982 s; round 2: 13, 186 s)
- **Errors during the run:** none.
- **Result:** round 1 cost 797,683 → 333,113 (iteration 100: 333,202; 140: 333,113: still falling slowly, a flat
  valley, so not fully converged); reprojection 0.66 px median after round 2; rotations stay with the gyro (relative
  rotation vs prior 0.097° median); position change median 0.581 units. Against the trusted path: **14.8 cm median,
  35.9 cm p90**, step spread 1.65×, Sim3 scale 0.946 (R-074 loose: 21.9 / 48.3; R-072: 31.1 / 68.4).
- **Verdict:** on a capture with enough matches the images alone (rotation tied to the gyro) bring the sensor path to
  ~15 cm; the default position priors (`--s_t1 0.3`) were the main limit of the R-071 recipe. Not yet tested on
  scan_009, where two stretches have no image points and only the priors hold the cameras: there the video tracks
  (R-073) should take over. One capture only.

### R-076 · 2026-11-20 · scan_009_057ed3beb4fc: video tracks + prior BA with looser position priors (no training)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 45de8b5 (uncommitted: `video_tracks.py`)
- **Dataset:** scan_009, keyframes `work_v9pfl`, input `work_v9pfl_sfm/sparse_tri` (R-071's rot_sfm model before
  prior BA: 698 cameras, 23,490 points, 138,270 observations)
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r076.sh` (log `r076.log`): `video_tracks.py` → `sparse_vt`;
  `prior_ba.py` on `sparse_vt` with default priors (`sparse_vt_pba`), `--s_t0 0.2 --s_t1 3` (`sparse_vt_pba_loose`),
  `--s_t0 2 --s_t1 30 --iters 150` (`sparse_vt_pba_free`), and on `sparse_tri` with `--s_t0 0.2 --s_t1 3`
  (`sparse_pba_loose`); scratchpad `loop_rot2.py` (start / end rotation check) and `cam_reproj.py` (points per camera)
- **Goal:** R-073 – R-075 on scan_009: do the video tracks fill the two stretches without image points
  (45 – 60 s, 90 – 105 s), and can the position priors be loosened there without the cameras floating?
- **Start → end:** 00:02 → 00:12 (tracking 57 s; prior BA 97 / 100 / 207 / 84 s)
- **Errors during the run:** none.
- **Result:** tracks: 209,330 started, 320,229 keyframe observations, 13,610 of 110,772 tested rejected by the
  rotation RANSAC; only 6,398 triangulated (174,624 reach one keyframe only, 24,225 parallax < 1°); 3D observations per
  image median 56 → 82, images < 20: 244 → 206. Per model (scratchpad `stretch_stats.py`; cameras with < 10 3D points;
  fastest step / median step):

  | Model | All 698 cams: < 10 pts, max step | 45 – 60 s (50 cams): pts median, < 10 | 90 – 105 s (45 cams): pts median, < 10 |
  |---|---|---|---|
  | R-071 `sparse/0` | 202, 8.7× | 0, 43 | 3, 29 |
  | tracks + default priors | 173, 9.1× | 0, 37 | 4, 28 |
  | tracks + loose (`0.2 / 3`) | 173, 10.2× | 0, 37 | 4, 28 |
  | tracks + nearly off (`2 / 30`, 150 it) | 173, **69.1×** | 0, 37 | 4, 28 |
  | no tracks + loose | 201, 10.5× | 0, 43 | 3, 29 |

  Per-stage count (`--debug_window`) for tracks starting in the window: 45 – 60 s: 15,000 started → 1,286 reach a
  second keyframe → 875 pass the RANSAC → **95 triangulated**; 90 – 105 s: 13,500 → 2,009 → 1,630 → **6**;
  120 – 140 s (has matches): 21,000 → 4,721 → 3,726 → 1,029. Keyframes 0.20 s apart (median) in all three.
- **Verdict:** the tracks survive and agree with the gyro in the empty stretches but are lost at triangulation with
  the current (wrong) positions there. With the position priors nearly off the path jumps (69× max step): on scan_009
  the priors are what holds the empty stretches. Not trained. Next: give the tracks to `rot_sfm.py` as directions
  (R-077).

### R-077 · 2026-11-20 · scan_009_057ed3beb4fc: video-track pair directions into rot_sfm (`v9pfv`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 45de8b5 (uncommitted: `video_tracks.py --pairs_out`,
  `rot_sfm.py --extra_pairs / --extra_w`)
- **Dataset:** scan_009, keyframes `work_v9pfl`, calibration `work_v9pfm_sfm` (as R-071), tracks on R-071's
  `sparse_tri` (698 cameras)
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r077.sh` (log `r077.log`): `video_tracks.py … --pairs_out
  work_v9pfv_sfm/vt_pairs.npz`; R-071's pair-direction cache copied; `rot_sfm.py … work_v9pfv_sfm --max_dt 300
  --bg_json gyro_loop_bias.json --triangulate_only --extra_pairs vt_pairs.npz`; `prior_ba.py` (defaults) →
  `work_v9pfv_sfm/sparse_pba`; scratchpad `stretch_stats.py` against R-071's `sparse/0`
- **Goal:** R-076 showed the tracks in the empty stretches pass the gyro check (875 at 45 – 60 s, 1,630 at 90 – 105 s)
  but cannot be triangulated with the wrong positions there (95 and 6 points). With the rotation fixed they give the
  direction of travel between keyframes directly, which is what `rot_sfm.py` solves positions from.
- **Start → end:** 00:17 → 00:22 (tracking 62 s; rot_sfm 2.3 min; prior BA 84 s)
- **Errors during the run:** none.
- **Result:** `vt_pairs.npz`: 4,124 keyframe pairs, median 27 correspondences, 2,688 with ≥ 15. `rot_sfm.py`: 9,015
  image directions (R-071's cache) + **1,321 from tracks**; all 894 keyframes connected; **641 kept** with median edge
  residual < 10° (R-071: 698). After `prior_ba.py`: reprojection 1.27 px; 45 – 60 s: 36 cameras (R-071: 50), 3D points
  median 0, 28 with < 10; 90 – 105 s: 37 cameras (45), median 7, 21 with < 10; max step 9.6× median (R-071 8.7×).
- **Verdict:** rejected as is: the track directions disagree with the rest of the path often enough that more cameras
  fail the 10° consistency test, and the empty stretches lose cameras instead of gaining points. Not looked into yet:
  whether the track directions are noisy (short 0.2 s baselines, parallax near the 1° limit) or the sensor path is
  wrong there (then the 10° test drops the right cameras). Not trained. Paused here at Tayyab's request. **Answered in
  R-078 (side check): the path is wrong there, the tracks are accurate.**

### R-078 · 2026-11-20 · Adaptive position priors (`prior_ba.py --adapt_n`), newRoom + scan_009

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 45de8b5 (uncommitted: `prior_ba.py --adapt_n / --loose_t0 /
  --loose_t1`, plus the R-076/R-077 tools)
- **Dataset:** newRoomAttemptSadness (`work_rotsfm_loop/sparse/0`, truth `work_v9e2e_sfm`, as R-075) and scan_009
  (R-071's `work_v9pfl_sfm/sparse_tri`)
- **Command(s):** `dataset/newRoomAttemptSadness/r078.sh` and `dataset/scan_009_057ed3beb4fc/r078.sh` (logs
  `r078.log`): `prior_ba.py … --adapt_n 150 --loose_t0 2 --loose_t1 30 --iters 150` (tight end = defaults
  0.02 / 0.3); newRoom scored with scratchpad `eval_rot.py`, scan_009 with `stretch_stats.py` against R-071's `sparse/0`
- **Goal:** R-075 showed the position priors limit newRoom (31.1 → 14.8 cm with priors nearly off), R-076 that scan_009
  needs them in its empty stretches (path jumps without). Support per camera (3D observations) before the run: newRoom
  median 370, 122 of 1,022 under 30; scan_009 median 56, 277 of 698 under 30. A prior strength that follows the
  support should keep both gains.
- **Start → end:** 02:02 → 02:23 (newRoom BA 18.5 min for 2 × 150 iterations; scan_009 BA 2.8 min)
- **Errors during the run:** none.
- **Result:** newRoom: 704 of 1,021 pairs fully loose, 95 tight; reprojection 0.66 px. Against the truth
  (`eval_rot.py`): **16.2 cm median, p90 29.6 cm**, Sim3 scale 0.941 (R-075 priors nearly off: 14.8 / 35.9; R-074
  loose: 21.9 / 48.3; R-071 recipe: 31.1 / 68.4). scan_009: 192 of 697 pairs fully loose, 247 tight; reprojection
  1.27 px; path as smooth as R-071 (max step 9.2× median, R-071 8.7×, R-076 priors off 69×); cameras moved median 0.010
  units against R-071; 45 – 60 s and 90 – 105 s unchanged (3D points median 0 and 3, a BA adds no points).
- **Verdict:** kept as the BA recipe: on newRoom it keeps most of the R-075 gain (median 16.2 vs 14.8 cm) with a
  better p90 (29.6 vs 35.9 cm), and on scan_009 it does not make the path jump. Not measured: whether scan_009's
  textured parts got more accurate (no truth for scan_009). Tuned on these two scans only (`adapt_n` 150 not swept).
- **Side check (same day, CPU, scratchpad `track_dir_check.py`):** the R-077 track directions against R-071's path
  (`sparse/0`), 1,254 pairs with ≥ 15 inliers and ≥ 1° parallax. Pairs whose cameras have ≥ 50 3D observations:
  angle median 2.4 – 2.9°, about 90 % under 10°; with only 1 – 2° parallax still 3.6°. 45 – 60 s: 23 pairs, median
  46.9°, 43 % reversed; 90 – 105 s: 10 pairs, median 72.9°. So the tracks are accurate and the sensor-held path in the
  empty stretches is wrong: R-077's 10° test removed the right directions. Few track pairs reach those stretches.

### R-079 · 2026-11-20 · scan_009_057ed3beb4fc: track directions weighted up in rot_sfm (`v9pfw`, `v9pfy`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 45de8b5 (uncommitted: as R-078, plus `rot_sfm.py
  --extra_min_inliers`)
- **Dataset:** scan_009, keyframes `work_v9pfl`, calibration `work_v9pfm_sfm`, track pairs from R-077
  (`work_v9pfv_sfm/vt_pairs.npz`, tracks on R-071's `sparse_tri`)
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r079.sh` (log `r079.log`): for `extra_w` 10 (`work_v9pfw_sfm`) and 30
  (`work_v9pfy_sfm`): R-071's pair-direction cache copied; `rot_sfm.py … --max_dt 300 --bg_json gyro_loop_bias.json
  --triangulate_only --extra_pairs vt_pairs.npz --extra_w W --extra_min_inliers 8`; `prior_ba.py … --adapt_n 150
  --loose_t0 2 --loose_t1 30 --iters 150` → `sparse_pba_adapt`; scratchpad `stretch_stats.py` against R-071's
  `sparse/0` and `track_dir_check.py` on the result
- **Goal:** R-078's side check showed the track directions are accurate (2.4 – 2.9° against the path where the images
  support it) and the path in the empty stretches is wrong. In R-077 they entered with weight inliers × parallax / 10
  (small at 1.5° parallax) against the accelerometer term, and were outvoted. With more weight they should pull the path
  there into line, so that the cameras survive and points can be triangulated.
- **Start → end:** 02:25 → 02:36 (per variant: rot_sfm 2.8 min, prior BA 1.2 – 1.5 min, checks 1.3 min)
- **Errors during the run:** none.
- **Result:** 1,734 track directions (R-077: 1,321 at 15 inliers); all 894 keyframes connected.

  | | R-071 | ×10 (`v9pfw`) | ×30 (`v9pfy`) |
  |---|---|---|---|
  | cameras kept (median edge residual < 10°) | 698 | 619 | 647 |
  | 3D observations per camera, median | 54 | 72 | 70 |
  | 45 – 60 s: cameras, 3D obs median | 50, 0 | 35, 0 | 41, 0 |
  | 90 – 105 s: cameras, 3D obs median | 45, 3 | 36, 10 | 37, 10 |
  | max step / median step | 8.7 | 10.7 | 9.4 |
  | track direction vs path, 45 – 60 s (median) | 46.9° (23 pairs) | 4.2° (18) | 4.3° (17) |
  | track direction vs path, 90 – 105 s | 72.9° (10) | 8.7° (4) | 4.6° (8) |
  | track direction vs path, support ≥ 150 | 2.9° | 2.2° | 1.9° |

  (after `prior_ba.py --adapt_n 150`; reprojection 1.27 px in both). Cameras in 45 – 60 s moved 0.85 units median
  against R-071 (×30).
- **Verdict:** ×30 kept as the input for R-080: the path in the empty stretches now follows the tracks, and the
  agreement also improved where the images support the path (1.9° vs 2.9°), which the tracks did not force by
  themselves. Caveat: the agreement inside the empty stretches is partly circular (the tracks were weighted in);
  the independent test is whether the tracks now triangulate there (R-080). Still fewer cameras than R-071 (647 vs 698)
  and no points in 45 – 60 s, because `--triangulate_only` uses the image matches only.

### R-080 · 2026-11-20 · scan_009_057ed3beb4fc: video tracks on R-079's path (`v9pfy`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 45de8b5 (uncommitted, as R-079)
- **Dataset:** scan_009, keyframes `work_v9pfl`; model `work_v9pfy_sfm/sparse_pba_adapt` (R-079, ×30, 647 cameras)
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r080.sh` (log `r080.log`): `video_tracks.py … work_v9pfy_sfm/sparse_pba_adapt
  work_v9pfy_sfm/sparse_vt` (defaults, as R-076); `prior_ba.py … --adapt_n 150 --loose_t0 2 --loose_t1 30 --iters 150`
  → `sparse_vt_pba_adapt`; scratchpad `stretch_stats.py` against R-071's `sparse/0`
- **Goal:** R-076 found the tracks in 45 – 60 s and 90 – 105 s survive the gyro check but do not triangulate (95 and
  6 points) because the positions there were wrong. R-079 moved those positions to agree with the tracks; if they are
  now right, the tracks should triangulate within the 10 px reprojection limit and give those cameras points.
- **Start → end:** 02:36 → 02:40 (tracking 77 s, prior BA 2.0 min)
- **Errors during the run:** none.
- **Result:** `video_tracks.py`: 194,030 tracks, 281,760 of 302,947 keyframe observations kept by the rotation-fixed
  RANSAC; **7,263 new points** (R-076 on R-071's path: 6,398); rejected: 159,848 seen in one keyframe only, 24,613
  parallax, 1,785 reprojection (R-076's main loss), 521 behind. Live tracks at video frames 2,000 and 3,000 (≈ 67 and 100 s, 30 fps): 1 and 0. After `prior_ba.py --adapt_n 150`: reprojection median **1.13 px** (R-071 1.27), p90 2.60.

  | | R-071 | R-079 ×30 | R-080 |
  |---|---|---|---|
  | cameras | 698 | 647 | 647 |
  | 3D observations per camera, median | 54 | 70 | **120** |
  | cameras with < 10 | 202 | 162 | **110** |
  | 45 – 60 s: cameras, median, < 10 | 50, 0, 43 | 41, 0, 33 | 41, 1, 23 |
  | 90 – 105 s: cameras, median, < 10 | 45, 3, 29 | 37, 10, 18 | 37, **23**, 12 |
  | max step / median step | 8.7 | 9.4 | 9.3 |
- **Verdict:** kept, best scan_009 SfM so far by these counts: the reprojection limit no longer throws the tracks away
  (1,785 rejected), so R-079's path agrees with the images it was not fitted on. 90 – 105 s now has points; 45 – 60 s
  does not, and the reason is the video itself: most tracks die before reaching the next keyframe (159,848 single-keyframe
  tracks overall; the live-track counts are snapshots at frames 2,000 / 3,000 ≈ 67 / 100 s, not inside 45 – 60 s;
  R-076's per-stretch count: 1,286 of 15,000 started tracks reach a second keyframe in 45 – 60 s). Point-based methods cannot fill that stretch; it needs
  texture-free constraints (planes from depth) or a new recording. Not trained, no render check yet; no truth for
  scan_009, so accuracy is not measured.

### R-081 · 2026-11-20 · scan_009_057ed3beb4fc: training on R-080's cameras (`v9pfz`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 45de8b5 (uncommitted, as R-079)
- **Dataset:** scan_009; keyframes `work_v9pfl` copied to `work_v9pfz`; R-080's `work_v9pfy_sfm/sparse_vt_pba_adapt`
  (647 cameras, 31,331 points) copied to `work_v9pfz_sfm/sparse/0`
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r081.sh` (log `r081.log`): as R-071: `sfm_colmap.py --work … work_v9pfz
  --out … work_v9pfz_sfm --feature aliked --sim3 none --stage {undistort, export}`; `run_v8.py --tag v9pfz --from_stage
  export --pose_free --init fmvs --planar 0.2 --blur 0.0222 --pgsr`; then `to_spz.mjs` for the web viewer
- **Goal:** Tayyab asked to see R-080 in the web viewer (`npm run dev`), which needs a trained model. Same recipe as
  R-071, so the two can be compared directly.
- **Start → end:** 12:38 → 13:07 (export 0.02, prior 3.8, init 2.2, train 22.2, ply 0.6 min)
- **Errors during the run:** none fatal. `Error caught was: No module named 'triton'` printed during the prior stage
  (also in R-071's log; the stage finished normally).
- **Result:** export: 25 frames dropped by the jump filter (> 30 cm from temporal neighbours), 622 frames; Sim3 to
  ARCore not applied (`--sim3 none`; for reference scale 0.4824, 23 / 157 inliers). `sfm_scale_check`: ratio median
  2.134 model units per Metric3D metre, **verdict "ok"** (R-071: 2.25). `→ work_v9pfz_sfm/gs_v9pfz/splat.ply`, 542,469
  splats. Training-view PSNR (half res, scratchpad `render_compare.py`, R-071 vs R-081 on the 607 frames both kept):
  median 19.52 → **19.59**, mean 19.65 → **19.90**, R-081 better on **61 %** of frames (median +0.54 dB on those).
  Photo | R-071 | R-081 sheet (scratchpad `cmp_r071_r081_compare.jpg`): sharper at 0 s and 23 s (door, lamp), 44 s (less
  colour noise), 106 s (wall corner line visible), 187 s (AC unit and curtain much cleaner); worse at 137 s (white
  smear over a door corner); 160 s about equal. Not held out. Web viewer: `scan-009-tracks`
  (`prototype/web-ui/public/splats/scan009_v9pfz.spz`, 10.3 MB).
- **Verdict:** kept: the best scan_009 model so far (slightly better than R-071 on training views, scale check ok).
  45 – 60 s still rests on the sensors (R-080). Scale still ~2× too large (not corrected). Training-view PSNR only;
  not held out.

### R-082 · 2026-11-20 · scan_009_057ed3beb4fc: 10.a baseline with held-out frames (`v9pfh`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 04b9522
- **Dataset:** scan_009; `work_v9pfz` copied to `work_v9pfh`, `work_v9pfz_sfm` (without `gs_v9pfz`) copied to
  `work_v9pfh_sfm`, so the cameras are R-081's (R-080's model)
- **Held-out list** `s10_test.txt`: `still_frames.py … work_v9pfz_sfm --bg_json gyro_loop_bias.json --split_out
  still_test.txt --json_out still_frames.json` found 9 still stretches (< 6°/s for >= 0.4 s, 6.7 s of 187 s; one at
  1.8 – 2.4 s has no keyframe), 8 held-out keyframes; 7 of the 9 stretches are in the first 17.6 s, one at 79.5 s, one
  at 186.3 s. `make_split.py --work … work_v9pfz_sfm --out s10_test.txt --add still_test.txt`: 6 stretches of 3 s
  plus the 8 still frames, **69 of 622 frames held out (11.1 %)**. Every later §10 model uses this list.
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r082.sh` (log `r082.log`): `sfm_colmap.py --work … work_v9pfh --out
  … work_v9pfh_sfm --feature aliked --sim3 none --stage {undistort, export}`; `run_v8.py --tag v9pfh --from_stage
  export --pose_free --init fmvs --planar 0.2 --blur 0.0222 --pgsr --split s10_test.txt`; then `eval_offpath.py`
- **Goal:** plan §10.a: the held-out number every later step (10.f, 10.b, 10.c, 10.d, 10.e) is judged against. Same
  recipe as R-081, only the split differs.
- **Start → end:** 17:16 → 17:20 (copy, undistort, export, prior; failed at init, below); resumed 17:20 → 17:45
  (export 0.01, prior 3.55, init 2.21, train 21.93, ply 0.59 min; `timing.json` total 28.3 min)
- **Errors during the run:**
  - 17:16 – 17:20, init stage (`fast_mvs.py`): `OSError: [WinError 145] The directory is not empty: …work_v9pfh_sfm\undist_fast\images`, `stage init failed (1)`. Cause: `r082.sh` copied `work_v9pfz_sfm` with `cp -r`, which followed the Windows junction `undist_fast/images` (→ `work_v9pfz_sfm/images`) and wrote a real 647-file folder; `fast_mvs.py` only unlinks junctions. Checked the original is still a junction (untouched). Fix: removed the copied real folder in `work_v9pfh_sfm/undist_fast/images` (a duplicate of `work_v9pfh_sfm/images`) and resumed with `run_v8.py … --from_stage init` (`r082b.sh`); export (split 553 train / 69 held out), prior (3.5 min, scale check ok, ratio 2.134) and blur were already done. Resolved: the resume ran to the end. Copy scripts should skip `undist_fast/images` from now on.
- **Result:** split 553 train / 69 held out; scale check verdict "ok", ratio 2.134 (as R-081). `→
  work_v9pfh_sfm/gs_v9pfh/splat.ply`, 573,257 splats. `eval_offpath.py --work work_v9pfh_sfm --out
  work_v9pfh_sfm/eval_r082 --models r082=… r081_seen=work_v9pfz_sfm/gs_v9pfz/splat.ply` (69 frames, half res):

  | Model | Splats | PSNR (colour-fit) | SSIM | Sharpness | Flatness cm |
  |---|---|---|---|---|---|
  | R-082 (frames held out) | 573,257 | **20.80** | **0.874** | 0.28 | **8.18** |
  | R-081 (same frames, seen in training) | 542,469 | 23.98 | 0.909 | 0.32 | 5.98 |

  The R-081 row is not a held-out score (it trained on these frames); it shows how much is lost when a view is not
  seen: 3.2 dB PSNR, 0.035 SSIM, 2.2 cm flatness. Sheet `eval_r082/offpath_frames.jpg` (one frame per stretch plus
  the still frames): the early door / AC views (0 – 17 s) are close to R-081; held-out views fail near the room
  entrance (a red smear across the door frame), a door seen from further back (the wall around it breaks into
  floaters) and a blank wall (rainbow-coloured floaters); the last frame (curtain, 186 s) is smeared in both models.
  Sheets `crops.jpg`, `centre.jpg` in the same folder. One scan, one split; the per-stretch and still-frame-only
  numbers were not computed separately.
- **Verdict:** kept as the §10.a baseline: 10.f, 10.b, 10.c, 10.d and 10.e are scored on the same `s10_test.txt` with
  `eval_offpath.py` against R-082 (20.80 dB / 0.874 / 8.18 cm).

### R-083 · 2026-11-20 · scan_009_057ed3beb4fc: 10.f gyro motion blur (`v9pfi`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ d013674
- **Dataset:** scan_009; `work_v9pfz` copied to `work_v9pfi`; `work_v9pfh_sfm` copied to `work_v9pfi_sfm` without
  `gs_v9pfh`, `eval_r082` and the `undist_fast/images` junction (R-082's copy problem), so cameras and split are R-082's
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r083.sh` (log `r083.log`): `sfm_colmap.py … --stage {undistort,
  export}` as R-082; `run_v8.py --tag v9pfi --from_stage export --pose_free --init fmvs --planar 0.2 --blur 0.0222
  --pgsr --split s10_test.txt --blur_gyro gyro_loop_bias.json`; then `eval_offpath.py` with R-082
- **Goal:** plan §10.f, one change against R-082: the blur model gets camera motion from the gyro for every frame
  (before: 398 of 622 frames had none, ARCore lost). Compared on the same 69 held-out frames.
- **Start → end:** 18:52 → 19:27 (export 0.01, prior 3.65, init 2.15, train 27.96, ply 0.6 min; total 34.4 min)
- **Errors during the run:** none. (At 18:56 the copied `blur_motion.json` still showed R-082's ARCore motion; that was
  the copy, `blur_motion.py` runs beside the init stage and rewrote it before training.)
- **Result:** `blur_motion.log`: 622 frames, motion from ARCore 0, gyro 622, none 0 (3 frames zero), rotational blur
  median 8.7 px, p90 17.6 px. Split 553 / 69 as R-082. `→ work_v9pfi_sfm/gs_v9pfi/splat.ply`, 586,509 splats.
  `eval_offpath.py --work work_v9pfi_sfm --out work_v9pfi_sfm/eval_r083 --models r082=… r083_gyroblur=…` (69 frames):

  | Model | Splats | PSNR (colour-fit) | SSIM | Sharpness | Flatness cm | Train min |
  |---|---|---|---|---|---|---|
  | R-082 (baseline) | 573,257 | 20.80 | 0.874 | 0.28 | 8.18 | 21.9 |
  | R-083 (gyro blur) | 586,509 | 20.86 | 0.871 | **0.43** | 9.85 | 28.0 |

  Sheet `eval_r083/offpath_frames.jpg`: the curtain / AC view at 186 s has visibly more detail (R-082 smeared it), the
  blank-wall view has fewer coloured floaters; the far door view and the entrance red smear are as bad as in R-082.
  PSNR +0.06 dB and SSIM −0.004 are within what one rerun could change (run-to-run spread not measured); sharpness
  rose clearly; wall flatness got worse by 1.7 cm; training took 6 min longer (blur sub-renders on every frame).
- **Verdict:** inconclusive: sharper held-out renders but no PSNR gain and less flat walls. The blur fix does not
  address the main held-out failures (entrance, far door), which look like pose / geometry errors. Whether to keep
  `--blur_gyro` in the next steps is Tayyab's choice.
- **Cleanup 2026-11-21 (Tayyab):** the work folders `work_v9pfi` / `work_v9pfi_sfm` and the model were deleted to free disk; the evaluation folder moved to `dataset/scan_009_057ed3beb4fc/s10_eval/eval_r083/` (with `timing_r083.json`, `blur_motion_r083.log`).

### R-084 · 2026-11-20 · scan_009_057ed3beb4fc: 10.d pose refinement in training (`v9pfj`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 7b56e5c
- **Dataset:** scan_009; copies `work_v9pfj` / `work_v9pfj_sfm` made as in R-083 (from `work_v9pfz` and
  `work_v9pfh_sfm`, without the model, the eval folder and the `undist_fast/images` junction)
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r084.sh` (log `r084.log`): as R-082 plus `--pose_opt` (nerfstudio
  SO3xR3 camera optimizer); no `--blur_gyro` (R-083 inconclusive, so 10.d is compared with R-082 alone); then
  `eval_offpath.py` and the per-frame check (scratchpad `perframe.py`)
- **Goal:** plan §10.d. Why now: the per-frame check of R-082 (`work_v9pfh_sfm/eval_r082/perframe.csv`, below)
  points at pose error in 22 – 25 s and 51 – 53 s and at frames that do not fit even when trained on (134 – 137 s).
  Caveat: held-out frames keep their unrefined SfM poses, so if refinement moves the training cameras as a whole the
  held-out score can drop even when the model is better; the sheet is checked as well.
- **Per-frame check of R-082 / R-083 (before this run):** mean colour-fit PSNR per held-out stretch; "seen" = R-081,
  which trained on these frames:

  | Stretch | Frames | 3D obs median | R-082 held | R-083 held | R-081 seen | Gap seen − R-082 |
  |---|---|---|---|---|---|---|
  | still 0 – 17 s | 6 | 521 | 24.55 | 24.22 | 24.58 | 0.03 |
  | 22 – 25 s | 14 | 144 | 23.87 | 24.27 | 26.67 | 2.80 |
  | 51 – 53 s | 6 | 0 | 20.01 | 19.75 | 24.52 | 4.51 |
  | 78 – 81 s | 14 | 746 | 21.63 | 22.27 | 27.56 | 5.93 |
  | 106 – 107 s | 2 | 4 | 28.37 | 26.27 | 27.83 | −0.54 |
  | 134 – 137 s | 15 | 171 | 15.73 | 15.63 | 18.93 | 3.20 |
  | 162 – 165 s | 11 | 75 | 20.41 | 20.28 | 22.28 | 1.87 |
  | 186 s | 1 | 1094 | 13.90 | 14.28 | 16.40 | 2.50 |

  Reading (not proven): still frames with good support generalise (gap 0); 51 – 53 s has no image support (pose from
  sensors); 78 – 81 s has good support but the largest gap; the stretch contains the whole 79.5 – 80.7 s still hold, so
  that view direction is in no training frame (coverage / geometry, not pose); 134 – 137 s is poor even when trained
  on (frames inconsistent with their neighbours: pose or blur; gyro blur did not change it). An ECC homography warp of
  render onto photo was also tried as a rotation-error measure; it is unreliable on blank walls (fitted shifts of
  thousands of px), so it is not used.
- **Start → end:** 19:52 → 20:21 (export 0.01, prior 3.56, init 2.13, train 23.09, ply 0.54 min; total 29.3 min)
- **Errors during the run:** none. Training log shows `CameraOptimizerConfig(mode='SO3xR3')`. Not an error but a
  gap: `run_v8.py` deletes `nerfstudio_models/` after the export (disk), so the refined poses are lost and how far
  they moved was not measured.
- **Disk:** 2.7 GB free on C: after this run (each §10 training copy is ~2.3 GB: `work_v9pfh_sfm` 1.8 GB,
  `work_v9pfi_sfm` 2.2 GB, mostly `mono_prior` 1.2 GB). No further training fits without freeing space; nothing was
  deleted (Tayyab's choice).
- **Result:** split 553 / 69; `→ work_v9pfj_sfm/gs_v9pfj/splat.ply`, 555,219 splats. `eval_offpath.py` (`eval_r084/`):
  R-082 20.80 / 0.874 / sharpness 0.28 / flatness 8.18 cm; **R-084 20.20 / 0.861 / 0.30 / 7.40 cm**. Per stretch
  (`perframe.csv`) R-084 is lower on 6 of 8, including the still frames at 0 – 17 s (24.55 → 22.97), which have good
  support: the pattern expected when the training cameras move and the held-out poses do not. Sheet: the far-door
  edge and the entrance smear look cleaner, other views similar.
  New `src/arcore3dgs/eval_align.py` (test-pose alignment: per held-out frame, model frozen, 6-DoF correction plus
  colour gain / bias by L1, 1/8 → 1/4 → 1/2 res, 150 / 75 / 50 iterations; the correction is dropped if it lowers
  PSNR), same 69 frames, 23.7 min for three models (`eval_r084/aligned.csv`):

  | Model | PSNR | PSNR aligned | SSIM | SSIM aligned | Correction median |
  |---|---|---|---|---|---|
  | R-082 baseline | 20.80 | **22.64** | 0.874 | 0.885 | 2.02°, 0.154 units |
  | R-083 gyro blur | 20.86 | 22.51 | 0.871 | 0.876 | 2.11°, 0.149 units |
  | R-084 pose refinement | 20.20 | 22.39 | 0.861 | **0.888** | 1.60°, 0.159 units |

  Aligned PSNR per stretch (R-082 / R-083 / R-084; median correction R-082): still 0 – 17 s 24.89 / 24.64 / 25.13
  (0.12°); 22 – 25 s 26.44 / 26.13 / 26.44 (1.81°); 51 – 53 s 21.59 / 22.06 / 22.47 (15.9°); 78 – 81 s 23.63 / 23.90 /
  23.90 (1.10°); 106 – 107 s 29.12 / 28.23 / 27.65; 134 – 137 s 17.53 / 17.37 / 16.66 (2.61°); 162 – 165 s 22.38 /
  21.82 / 21.32; 186 s 14.88 / 15.45 / 14.92. Corrections above ~5° are on blank walls (51 – 53 s, 106 s, 162 s), where
  the alignment can slide along a featureless surface; not trusted.
- **Verdict:** rejected for now: once each model gets its best held-out pose, the three models are within 0.25 dB, so
  pose refinement in training does not make a better model here (one run, one split). What the alignment shows:
  (1) held-out SfM poses are off by about 2° on textured stretches (aligning gains 1.8 dB on average, 2.6 dB at
  22 – 25 s), so pose error is real but has to be fixed in SfM (10.c / 10.b), not in training; (2) at 78 – 81 s the
  pose is nearly right (1.1°) yet aligned PSNR stays 4 dB below the seen model (27.56), a coverage / geometry gap
  (10.e); (3) 134 – 137 s stays poor even aligned (17.5) and even when trained on (18.9).
- **Cleanup 2026-11-21 (Tayyab):** the work folders `work_v9pfj` / `work_v9pfj_sfm` and the model were deleted to free disk; the evaluation folder moved to `dataset/scan_009_057ed3beb4fc/s10_eval/eval_r084/` (with `timing_r084.json`).

### R-085 · 2026-11-20 · scan_009_057ed3beb4fc: 10.c tracks ↔ path loop (`track_loop_r085`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 5765e1d
- **Dataset:** scan_009; keyframes `work_v9pfl`, calibration `work_v9pfm_sfm`, start model R-080's
  `work_v9pfy_sfm/sparse_vt_pba_adapt` (647 cameras), pair-direction cache `work_v9pfl_sfm/pair_directions_dt300_par1_bg.json`
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r085.sh` (log `r085.log`): `track_loop.py $S $S/work_v9pfl
  $S/work_v9pfm_sfm $S/work_v9pfy_sfm/sparse_vt_pba_adapt $S/track_loop_r085 --pair_cache … --bg_json
  gyro_loop_bias.json --rounds 3 --colmap COLMAP.bat` (defaults: `--extra_w 30 --extra_min_inliers 8 --adapt_n 150`,
  BA `--loose_t0 2 --loose_t1 30 --iters 150`, stop when kept cameras rise by < 5)
- **Goal:** plan §10.c: repeat R-079 / R-080 (tracks → `rot_sfm.py` → adaptive BA → tracks → BA) until the kept
  cameras stop rising. R-084's alignment showed held-out SfM poses ~2° off, so the pose fix has to come from SfM.
  No training in this run (disk 2.7 GB).
- **Start → end:** 20:50 → 21:08 (7.8 min per round)
- **Errors during the run:** none.
- **Result:** `track_loop.json`; per-stretch numbers from scratchpad `stretch_stats.py` (cameras, 3D obs median, cameras
  with < 10 obs):

  | Model | All | 45 – 60 s | 90 – 105 s | Reprojection |
  |---|---|---|---|---|
  | start (R-080) | 647, 120, 110 | 41, 1, 23 | 37, 23, 12 | 1.13 px |
  | round 1 | 676, 91, 144 | 48, 3, 30 | 43, 16, 17 | 1.13 px |
  | round 2 | 656, 109, 123 | 38, 1, 22 | 37, 21, 13 | 1.12 px |

  Round 1 brought back 29 cameras (7 of them in 45 – 60 s) but with thinner support everywhere; round 2 dropped 20 of
  them again and support went back towards the start; `--min_gain 5` stopped the loop. The loop oscillates instead
  of converging: the extra cameras are the weakly supported ones, kept or dropped by small changes in the path.
- **Verdict:** rejected: no round beats R-080's model on support, and 45 – 60 s is unchanged (median 1 → 3 → 1). Not
  trained (no gain to test, and 2.7 GB disk). R-080 (`work_v9pfy_sfm/sparse_vt_pba_adapt`) stays the best scan_009
  camera model. Output `dataset/scan_009_057ed3beb4fc/track_loop_r085/` (two rounds) kept.

### R-086 · 2026-11-21 · scan_009_057ed3beb4fc: 10.e stronger geometry weights (`v9pfk`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ a008f5b
- **Dataset:** scan_009; `work_v9pfz` copied to `work_v9pfk`; `work_v9pfh_sfm` copied to `work_v9pfk_sfm` without
  `gs_v9pfh`, `eval_r082` and the `undist_fast/images` junction (R-082's cameras and split; `mono_prior/` was
  deleted on 2026-11-21 and is rebuilt by the prior stage)
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r086.sh` (log `r086.log`): as R-082 with `--planar 0.5`
  (R-082: 0.2) and `--train_args "--depth_lambda 0.1 --normal_lambda 0.1"` (defaults 0.05 / 0.05); no gyro blur, no
  pose refinement; then `eval_offpath.py` and `eval_align.py` against R-082
- **Goal:** plan §10.e, first part: the per-frame check found the largest held-out gap at 78 – 81 s with the pose
  nearly right (R-084's alignment: 1.1°), plus floaters on blank walls, which points at geometry. Stronger
  depth / normal / planar priors should hold the surfaces in place for views the training did not see. The three
  weights change together (the plan's 10.e setting); if it helps, a later run can separate them.
- **Start → end:** 01:09 → 02:01 (training 01:09 → 01:40: export 0.02, prior 3.82, init 2.24, train 23.73, ply 0.71 min,
  total 30.5 min; then both evaluations 21 min)
- **Errors during the run:** none.
- **Result:** `→ work_v9pfk_sfm/gs_v9pfk/splat.ply`, 588,175 splats. `eval_offpath.py` (`eval_r086/`):

  | Model | PSNR | SSIM | Sharpness | Flatness cm | PSNR aligned | SSIM aligned | Correction median |
  |---|---|---|---|---|---|---|---|
  | R-082 | 20.80 | 0.874 | 0.28 | 8.18 | **22.64** | **0.884** | 2.02° |
  | R-086 | 20.75 | 0.871 | 0.22 | **4.98** | 21.85 | 0.877 | 1.32° |

  Aligned PSNR per stretch (R-082 → R-086, `eval_r086/aligned.csv`): still 0 – 17 s 24.89 → 24.17; 22 – 25 s 26.44 →
  24.98; 51 – 53 s 21.59 → 21.52; **78 – 81 s 23.63 → 24.10**; 106 s 29.17 → 27.25; 134 – 137 s 17.55 → 16.13;
  162 – 165 s 22.39 → 21.41; 186 s 14.88 → 14.46. Sheet `eval_r086/offpath_frames.jpg`: the blank-wall view has no
  rainbow floaters; at 134 s (the far door) the render is one flat brown surface: a flattened sheet of Gaussians
  sits in front of that camera; the entrance smear is narrower but still there.
- **Verdict:** inconclusive: the walls are 39 % flatter and the 78 – 81 s coverage gap improves a little, but
  aligned PSNR drops 0.8 dB and one view is blocked. The planar weight 0.5 is the likely cause of the sheet (not
  separated: the three weights changed together). Next if pursued: depth / normal 0.1 with planar back at 0.2, or
  planar 0.35.

### R-087 · 2026-11-21 · scan_009_057ed3beb4fc: 10.b-1 rolling-shutter rectified keyframes (`v9pfs`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ a008f5b (records for R-086 / R-087 uncommitted at start)
- **Dataset:** scan_009; keyframes `work_v9pfz` rectified into `work_v9pfs`; R-080's model (`work_v9pfz_sfm/sparse/0`)
  copied to `work_v9pfs_sfm/sparse/0` (only that, so the export takes the rectified images); split `s10_test.txt`
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r087.sh` (log `r087.log`): `rs_rectify.py $S work_v9pfz work_v9pfz_sfm
  work_v9pfs --bg_json gyro_loop_bias.json --axis cols --sign 1` (the probe's choice, plan §10.5); `sfm_colmap.py …
  --stage {undistort, export}`; `run_v8.py --tag v9pfs` with R-082's recipe; `eval_offpath.py` twice (ground truth =
  rectified photos `work_v9pfs_sfm`, and raw photos `work_v9pfh_sfm`, both models each time) and `eval_align.py` on
  the rectified photos
- **Goal:** plan §10.b, first part: same cameras as R-082, only the images change (rolling-shutter shear removed with
  the gyro). The full 10.b-2 (features, matching and SfM on rectified keyframes) only if this helps.
- **Start → end:** 02:01 → 02:59 (rectify + undistort + export 10 min; export 0.01, prior 3.81, init 2.28, train 22.92,
  ply 0.63 min, total 29.7; evaluations 17 min)
- **Errors during the run:** none.
- **Result:** `rs_rectify.py`: 894 keyframes rectified (readout along columns, sign +1), per-frame shift (p95 of the
  pixels) median 4.6 px, max 21.5 px. Split 553 / 69 (same 622 frames as R-082). `→ work_v9pfs_sfm/gs_v9pfs/splat.ply`,
  596,688 splats.

  | Ground truth | Model | PSNR | SSIM | Sharpness | Flatness cm |
  |---|---|---|---|---|---|
  | rectified photos (`eval_r087_gt_pfs/`) | R-082 | 20.81 | 0.875 | 0.32 | 8.87 |
  | | R-087 | 20.69 | 0.867 | 0.28 | **3.55** |
  | raw photos (`eval_r087_gt_pfh/`) | R-082 | 20.80 | 0.874 | 0.28 | 8.18 |
  | | R-087 | 20.67 | 0.866 | 0.25 | **4.18** |

  Aligned (`eval_align.py`, rectified photos): R-082 22.66 / 0.885, R-087 22.22 / 0.878 (correction medians 2.01° /
  2.28°). Per stretch R-082 → R-087: still 0 – 17 s 24.93 → 25.27; 22 – 25 s 26.46 → 26.26; **51 – 53 s 21.74 →
  23.33**; 78 – 81 s 23.64 → 23.51; 106 s 29.14 → 28.45; 134 – 137 s 17.52 → 15.87; 162 – 165 s 22.40 → 21.29;
  186 s 14.87 → 15.40. Sheet: at 134 s a flat surface fills the view (as in R-086), the 186 s view is blank, the 162 s
  view shows ceiling and AC structure that R-082 lost, the blank-wall floaters remain.
- **Caution on flatness:** the metric is the rms around a fitted plane wherever the render is opaque; a sheet of
  Gaussians filling a view (134 s here and in R-086) scores as perfectly flat, so part of the flatness gain in
  R-086 / R-087 may be such sheets. Not separated.
- **Verdict:** inconclusive: flatter (with the caveat above), better in the 51 – 53 s stretch with no image support,
  worse aligned PSNR overall, blocked views. Differences of 0.4 – 0.8 dB cannot be judged until the run-to-run spread
  of identical trainings is known (R-088).

### R-088 · 2026-11-21 · scan_009_057ed3beb4fc: R-082 repeated, run-to-run spread (`v9pfn`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ a008f5b (R-086 – R-088 records uncommitted at start)
- **Dataset:** as R-082: `work_v9pfz` → `work_v9pfn`, `work_v9pfh_sfm` → `work_v9pfn_sfm` (without the model, eval and
  the `undist_fast/images` junction)
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r088.sh` (log `r088.log`): R-082's exact command with tag `v9pfn`;
  then `eval_offpath.py` and `eval_align.py` with R-082
- **Goal:** R-083 – R-087 differ from R-082 by 0.1 – 0.8 dB and in single blocked views; without knowing how much two
  identical trainings differ none of that can be judged. Nerfstudio's seed is fixed (42), so this measures the
  spread from GPU non-determinism with identical inputs (a lower bound of the seed-to-seed spread).
- **Start → end:** 02:59 → 03:45 (export 0.0, prior 3.61, init 2.12, train 22.45, ply 0.61 min, total 28.8; evaluations 16 min)
- **Errors during the run:** none.
- **Result:** `→ work_v9pfn_sfm/gs_v9pfn/splat.ply`, 620,419 splats (R-082: 573,257). Same inputs, same command:

  | | PSNR | SSIM | Sharpness | Flatness cm | PSNR aligned | SSIM aligned |
  |---|---|---|---|---|---|---|
  | R-082 | 20.80 | 0.874 | 0.28 | 8.18 | 22.65 | 0.885 |
  | R-088 (repeat) | 21.05 | 0.873 | 0.27 | 6.65 | 22.55 | 0.880 |
  | difference | +0.25 | −0.001 | −0.01 | **−1.53** | −0.10 | −0.004 |

  Aligned per stretch (R-088 − R-082): still 0 – 17 s 0.00; 22 – 25 s −0.81; 51 – 53 s −0.13; 78 – 81 s +0.79;
  106 s −0.22; 134 – 137 s +0.04; 162 – 165 s −0.61; 186 s +0.88. Per frame |difference| median 0.70 dB, p90 1.58,
  max 3.89 (`eval_r088/aligned.csv`).
- **Verdict:** kept as the noise reference (one repeat, so a rough estimate). Two identical trainings differ by ~0.1 –
  0.25 dB overall, up to ~0.9 dB on a stretch and 1.5 cm in flatness. Against that: R-083 (+0.06 PSNR, −0.13 aligned)
  and R-084 (−0.25 aligned) are within the noise; R-086 (−0.79 aligned) and R-087 (−0.44 aligned) are probably real
  losses; R-086's and R-087's 134 – 137 s losses (−1.4, −1.65 dB; the repeat: +0.04) are real (the blocking sheet);
  R-087's 51 – 53 s gain (+1.6 dB; repeat −0.13) is probably real; flatness gains of 3.2 cm (R-086) and 4.0 cm (R-087)
  exceed the 1.5 cm spread but may partly be the sheets (R-087 caution).

### R-089 · 2026-11-21 · scan_009_057ed3beb4fc: rectified keyframes + path pruning (`v9pfo`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 84c4b4c plus uncommitted `geo_splatfacto.py --path_prune`,
  `prune_near_path.py`, `eval_offpath.py` blocked-view guard
- **Before this run (no training):** in R-087 the blocked held-out views had median rendered depth 0.01 – 0.04 model
  units (R-082 / R-088 at the same frames 0.7 – 2.4). New `prune_near_path.py` removes Gaussians whose extent
  (centre distance − 2 × largest scale) comes within 0.1 units (~5 cm) of the camera path (all keyframe centres, gaps
  > 0.5 units skipped). On the trained models: R-082 −4.15 %, R-087 −2.62 %, R-088 −4.34 % of the Gaussians.
  `eval_offpath.py` now counts views with median rendered depth < 0.2 units as blocked and leaves them out of
  flatness (`s10_eval/eval_blocked/`):

  | Model | PSNR | SSIM | Flatness cm (unblocked) | Blocked views of 69 |
  |---|---|---|---|---|
  | R-082 | 20.80 | 0.874 | 9.59 | 7 |
  | R-082 pruned after training | 20.53 | 0.868 | 9.43 | 1 |
  | R-088 (repeat of R-082) | 21.05 | 0.873 | 6.75 | 5 |
  | R-086 | 20.75 | 0.871 | 7.73 | 13 |
  | R-087 | 20.67 | 0.866 | 9.01 | 16 |
  | R-087 pruned after training | 20.63 | 0.866 | 9.28 | 1 |

  Pruning after training opens the blocked views (sheet `s10_eval/eval_prune/offpath_frames.jpg`: the 134 s door
  view, the 162 s AC view and the 186 s curtain reappear) but the geometry behind the sheets is messy, and a flat
  beige sheet matches the beige walls well under colour-fit PSNR, so PSNR drops. Hence pruning during training.
- **Dataset:** `work_v9pfs` (rectified keyframes, R-087) copied to `work_v9pfo`; `work_v9pfs_sfm` copied to
  `work_v9pfo_sfm` without the model, evaluations and the `undist_fast/images` junction
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r089.sh` (log `r089.log`): R-087's command with tag `v9pfo` plus
  `--train_args "--path_prune 0.1"` (every 500 steps); then `eval_offpath.py` (raw photos, `work_v9pfh_sfm`) and
  `eval_align.py` with R-082 and R-087
- **Goal:** keep R-087's gain in 51 – 53 s without the blocked views; make the model explain those views with real
  geometry instead of a sheet in front of the lens.
- **Start → end:** 13:14 → 14:09 (export 0.01, prior 3.89, init 2.16, train 22.7, ply 0.68 min, total 29.4; evaluations 25 min)
- **Errors during the run:** none. Pruning log (`gs_v9pfo/train.log`): 660 removed at step 500, 100 at 1000, 244 at
  1500, 491 at 2000, …, 496 at 7500, 390 at 14500; 14,050 in total (2.4 % of the final 581,354).
- **Result:** raw photos (`work_v9pfh_sfm`), `eval_r089/`:

  | Model | PSNR | SSIM | Flatness cm (unblocked) | Blocked of 69 | PSNR aligned | SSIM aligned |
  |---|---|---|---|---|---|---|
  | R-082 | 20.80 | 0.874 | 9.59 | 7 | **22.64** | **0.884** |
  | R-087 | 20.67 | 0.866 | 9.01 | 16 | 22.18 | 0.877 |
  | R-089 | 20.68 | 0.870 | 8.92 | **1** | 22.21 | 0.875 |

  Aligned per stretch R-082 / R-087 / R-089: still 0 – 17 s 24.89 / 25.24 / 23.73; 22 – 25 s 26.44 / 26.25 / 25.59;
  **51 – 53 s 21.59 / 23.23 / 24.18**; 78 – 81 s 23.63 / 23.52 / 22.73; 106 s 29.17 / 28.47 / 28.87; **134 – 137 s
  17.54 / 15.66 / 17.39**; 162 – 165 s 22.38 / 21.41 / 21.31; 186 s 14.88 / 15.57 / 15.72.
- **Verdict:** inconclusive. Pruning during training removes the blocked views without the PSNR drop of pruning
  afterwards (R-087 → R-089: 16 → 1 blocked, 134 – 137 s back to R-082's level) and the 51 – 53 s gain grows to
  +2.6 dB over R-082 (noise ≤ 0.9 dB per stretch, R-088); but the still frames (−1.2 dB), 22 – 25 s and 78 – 81 s are
  lower and the overall aligned score stays 0.4 dB below R-082. R-090 (pruning without rectification) separates
  the two changes.

### R-090 · 2026-11-21 · scan_009_057ed3beb4fc: R-082 plus path pruning (`v9pfq`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 84c4b4c plus uncommitted `--path_prune` code (as R-089)
- **Dataset:** as R-088 (`work_v9pfz` → `work_v9pfq`, `work_v9pfh_sfm` → `work_v9pfq_sfm`, unrectified keyframes)
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r090.sh` (log `r090.log`): R-082's command with tag `v9pfq` and
  `--train_args "--path_prune 0.1"`; then `eval_offpath.py` and `eval_align.py` with R-082 and R-088
- **Goal:** separate R-089's two changes: pruning alone on R-082's images.
- **Start → end:** 14:09 → 15:03 (export 0.01, prior 3.58, init 2.12, train 21.96, ply 0.55 min, total 28.2; evaluations 25 min)
- **Errors during the run:** none. 11,052 Gaussians pruned over the run (29 pruning steps; 285 at step 14500).
- **Result:** `eval_r090/` (raw photos):

  | Model | PSNR | SSIM | Flatness cm (unblocked) | Blocked of 69 | PSNR aligned | SSIM aligned |
  |---|---|---|---|---|---|---|
  | R-082 | 20.80 | 0.874 | 9.59 | 7 | 22.64 | 0.884 |
  | R-088 (repeat) | 21.05 | 0.873 | 6.75 | 5 | 22.54 | 0.880 |
  | R-090 (pruned) | 21.10 | 0.868 | 9.41 | **0** | 22.52 | 0.878 |

  Aligned per stretch R-082 / R-088 / R-090: still 24.89 / 24.89 / 24.87; 22 – 25 s 26.44 / 25.63 / 26.47; 51 – 53 s
  21.59 / 21.46 / 22.72; 78 – 81 s 23.63 / 24.42 / 23.96; 106 s 29.17 / 28.95 / 28.49; 134 – 137 s 17.51 / 17.57 / 17.07;
  162 – 165 s 22.40 / 21.78 / 21.21; 186 s 14.88 / 15.77 / 15.75.
- **Verdict:** kept. Pruning alone is within the run-to-run spread on every score (R-088) and removes all blocked
  views, so it can stay on. Separating R-089: the 51 – 53 s gain is mostly the rectification (pruning alone +1.1 dB,
  rectification alone +1.6, both +2.6); R-089's lower still-frame score (23.73) appears with neither change alone
  (R-087 25.24, R-090 24.87); not explained, one run each.

### R-091 · 2026-11-21 · scan_009_057ed3beb4fc: 10.b-2 SfM chain on rectified keyframes (`work_v9pfs_cal`, `work_v9pfs2_sfm`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 1627653
- **Dataset:** scan_009, the 894 rectified keyframes of R-087 (`work_v9pfs`); calibration model of R-048
  (`work_v9pfm_sfm/sparse/0`, copied into `work_v9pfs_cal`); gyro bias `gyro_loop_bias.json` (R-071, reused)
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r091.sh` (log `r091.log`): `sfm_colmap.py --work work_v9pfs --out
  work_v9pfs_cal --feature aliked --pairs arcore --temporal 30 --retrieval 30 --stage {extract, match}`; R-048's
  bridge pairs (`pairs_bridge0.txt`) imported with `matches_importer`; `rot_sfm.py … --max_dt 300 --bg_json
  --triangulate_only` → `work_v9pfs2_sfm`; `prior_ba.py --adapt_n 150 --loose_t0 2 --loose_t1 30 --iters 150`;
  `track_loop.py … --rounds 1 --rs 1` (= R-079 + R-080 on the rectified images); `stretch_stats.py` against R-080
- **Goal:** plan §10.b-2: the whole camera solve on rolling-shutter-free images (R-087 only swapped the images under
  R-080's cameras). R-084's alignment says the held-out SfM poses are ~2° off; less shear should give cleaner
  matches and pair directions. Training afterwards (R-092) only if the camera model is at least as complete as R-080
  (647 cameras, 3D obs median 120).
- **Start → end:** 15:03 → 16:42 (extraction + matching 15:03 → 15:24; `r091b.sh` 15:25 → 16:42, including the pause in the
  first `prior_ba.py`)
- **Errors during the run:**
  - 15:24, bridge-pair import (`r091.sh` step 1): `matches_importer` exited 3221226505 (0xC0000409);
    `matches_importer_bridge.log`: `Error loading "…\colmap-4.2.0in\onnxruntime_providers_cuda.dll" which
    depends on "cublasLt64_12.dll" which is missing`. Cause: the script called COLMAP directly, without the PATH
    entries (`tools/cudnn9`, torch's `lib`) that `sfm_colmap.py` adds for the ALIKED / LightGlue ONNX models.
    Extraction and the 29,186 guided + retrieval matches had finished. Fix: `r091b.sh` repeats the import with that
    PATH and continues the chain. Resolved: the import ran (15:25) and the chain continued.
  - Paused at Tayyab's request (2026-11-21, "can you pause it") during the first `prior_ba.py` (iteration 9 of 150,
    reprojection 1.89 → 1.35 px): the processes (`bash r091b.sh` ×2, `python prior_ba.py`) were suspended with
    `NtSuspendProcess`, not killed; their PIDs are in `%TEMP%
091_paused_pids.txt`. Resume with `NtResumeProcess` on
    the same PIDs (or rerun `r091b.sh` from the `prior_ba.py` line if the PC restarts). Resumed the same day (`NtResumeProcess`, all three processes found). Progress so far: rot_sfm on the
    rectified keyframes kept **695 cameras**, 23,494 points, 135,406 observations (R-071 on raw keyframes: 698
    cameras, 23,490 points).
- **Result:** (`r091.log`, `r091b.log`; per-stretch numbers from `stretch_stats.py`: cameras, 3D obs median, cameras
  with < 10 obs)

  | Model | All | 45 – 60 s | 90 – 105 s | Reprojection |
  |---|---|---|---|---|
  | R-071 raw keyframes, `rot_sfm` | 698, 54, 202 | 50, 0, 43 | 45, 3, 29 | |
  | R-080 (best so far) | 647, 120, 110 | 41, 1, 23 | 37, 23, 12 | 1.13 px |
  | R-091 `rot_sfm` + adaptive BA (rectified) | 695, 53, 211 | 45, 0, 42 | 41, 5, – | 1.27 px |
  | R-091 + one track round (`--rs 1`) | 647, 100, 115 | 30, 0, 17 | 37, 22, – | 1.13 px |

  `rot_sfm` on the rectified keyframes: 695 cameras, 23,494 points (R-071 on raw keyframes: 698, 23,490), so the
  rectified images match about as well as the raw ones; the adaptive BA moved positions by a median 0.17 units. The
  track round kept 647 cameras (−48) and fewer in 45 – 60 s (30 vs R-080's 41).
- **Verdict:** rejected; not trained (R-092 not run). Removing the rolling-shutter shear does not give more matches
  or tracks in the textureless stretch: 45 – 60 s stays at a median of 0 – 1 3D observations per camera. R-080
  stays the best camera model. Folders kept: `work_v9pfs_cal` (database), `work_v9pfs2_sfm`.

### R-092 · 2026-11-21 · scan_009_057ed3beb4fc: depth priors for unsupported frames (`--fill_scale`, `v9pfu`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ b4949cb plus uncommitted `mono_prior.py --fill_scale`,
  `run_v8.py --prior_args`
- **Why:** Tayyab inspected R-081 in the viewer: coherent only from the recorded angles, off-path the splat depth
  looks wrong. `mono_prior.py` aligns Metric3D to each frame's SfM points and gives frames with < 5 points **no**
  depth / normal prior (`valid` all false): 77 of 622 training frames of `work_v9pfq_sfm`, 19 of 37 at 45 – 60 s, 25
  of 104 at 60 – 90 s, 17 of 132 at 150 – 190 s, i.e. no geometry guidance exactly where tracking failed. Plan step
  chosen by Tayyab ("ok try 1."): give those frames a scale interpolated in time from well-fitted neighbours.
- **Code:** `mono_prior.py --fill_scale`: after the normal pass, frames with < 5 SfM points get scale =
  exp(interp over time of log median(z_sfm / z_mono) of frames with >= 20 inliers and residual < 15 %), shift 0,
  normals from that depth, `valid` set; the leave-one-out error of the interpolation is printed. `run_v8.py
  --prior_args` passes it.
- **Dataset:** as R-090 (`work_v9pfz` → `work_v9pfu`, `work_v9pfh_sfm` → `work_v9pfu_sfm`, raw keyframes, split
  `s10_test.txt`)
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r092.sh` (log `r092.log`): R-090's command with tag `v9pfu` and
  `--prior_args "--fill_scale"`; then `eval_offpath.py` and `eval_align.py` with R-082 and R-090
- **Goal:** better depth off-path (Tayyab's observation) without losing the training views; judged by aligned
  held-out PSNR, the blocked-view count and the room-centre sheet (`centre.jpg`), plus Tayyab in the viewer.
- **Start → end:** 16:55 → 17:50 (`r092b.sh`: export 0.01, prior 3.66, init 2.18, train 23.33, ply 0.67 min, total 29.9;
  evaluations 25 min)
- **Errors during the run:**
  - First start: `run_v8.py: error: argument --prior_args: expected one argument`: argparse takes a value that starts
    with `--` and has no space (`--fill_scale`) for an option (`--train_args "--path_prune 0.1"` passes because of
    the space). Failed before any processing (copies done). Fix: `--prior_args=--fill_scale`, rerun from the
    undistort step (`r092b.sh`). Resolved: `r092b.sh` ran to the end.
- **Result:** `fill_scale: 77 frames without SfM support got a time-interpolated scale from 434 well-fitted frames;
  leave-one-out scale error on those: median 5.3 %, p90 16.9 %` (the fitted frames' own alignment error: median
  5.9 %). 14,477 Gaussians path-pruned; `→ work_v9pfu_sfm/gs_v9pfu/splat.ply`, 591,387 splats. `eval_r092/`:

  | Model | PSNR | SSIM | Flatness cm (unblocked) | Blocked | PSNR aligned | SSIM aligned | Correction median |
  |---|---|---|---|---|---|---|---|
  | R-082 | 20.80 | 0.874 | 9.65 | 7 | 22.65 | 0.885 | 2.02° |
  | R-090 (pruning) | 21.10 | 0.868 | 9.92 | 0 | 22.52 | 0.878 | 2.02° |
  | R-092 (pruning + fill) | 20.64 | 0.872 | **6.77** | 0 | 22.26 | 0.880 | **1.62°** |

  Aligned per stretch R-082 / R-090 / R-092: still 24.90 / 24.87 / 24.35; 22 – 25 s 26.44 / 26.47 / 25.91; 51 – 53 s
  21.59 / 22.72 / 21.97; 78 – 81 s 23.63 / 23.96 / 23.81; 106 s 29.12 / 28.49 / 28.79; 134 – 137 s 17.55 / 17.07 /
  16.91; 162 – 165 s 22.40 / 21.20 / 21.50; 186 s 14.88 / 15.75 / 14.15. Room-centre views (`eval_r092/centre.jpg`,
  never visited by the camera): at 90° and 180° R-092's walls have fewer streaks / floaters and a straighter door
  edge than R-082 / R-090; the 0° and 270° views are a plain wall in all three.
- **Verdict:** kept for Tayyab's inspection. Flatness improves by 3.1 cm with no blocked views (twice the 1.5 cm
  run-to-run spread, and not a sheet artefact this time), held-out views need a smaller pose correction (1.62° vs
  2.02°), aligned SSIM is level, aligned PSNR is 0.26 dB lower (about the run-to-run spread). The geometry is better;
  the colour fit is not. One run.

### R-093 · 2026-11-21 · scan_009_057ed3beb4fc: 11.a VGGT feasibility test (42 – 63 s)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC (8 GB)
- **Branch / commit:** `docs/featureless-tracking-plan` @ cd1b566 plus uncommitted `src/arcore3dgs/vggt_chunk.py`,
  D-081
- **Software:** VGGT (`facebookresearch/vggt` @ a288dd0, weights `model.pt` 4.7 GB) from
  `C:/Users/tyb/.cache/buildscan/` (outside the repo; D-081), run in `nerfstudio-env` (torch 2.1.2+cu121; VGGT lists
  2.3.1) with its small helper packages from `vggt_deps`; bf16 autocast; weights loaded with `weights_only=True`.
- **Dataset:** scan_009, undistorted training images of `work_v9pfu_sfm` (R-080's cameras), 32 of the 65 keyframes
  between 42 and 63 s (37 lie in 45 – 60 s); reference model R-080 (`work_v9pfy_sfm/sparse_vt_pba_adapt`); Metric3D
  priors of R-092 (`work_v9pfu_sfm/mono_prior`, filled scales)
- **Command(s):** `nerfstudio-env/Scripts/python.exe src/arcore3dgs/vggt_chunk.py $S $S/work_v9pfu_sfm
  $S/work_v9pfy_sfm/sparse_vt_pba_adapt $S/vggt_r093 --vggt_dir …/vggt --weights …/vggt_weights/model.pt --t0 42 --t1
  63 --n 32 --bg_json $S/gyro_loop_bias.json --calib $S/work_v9pfz_sfm` (log `dataset/…/vggt_r093.log`)
- **Goal:** plan §11.a: can VGGT place the textureless frames? Checks: its relative rotations against the gyro, its
  camera centres against R-080 where R-080 has image support, and whether its depth maps agree across frames better
  than the per-frame Metric3D priors (the suspected cause of the wrong off-path depth).
- **Start → end:** start of the first try not recorded (stopped after > 10 min, see errors); the working runs finished at
  18:17 (8 frames, 26 s), 18:18 (32 keyframes, 22 s) and 18:21 (65 video frames, 43 s) (file times)
- **Errors during the run:**
  - First try (32 keyframes): after > 10 min the GPU sat at 7.8 of 8 GB, 100 % busy, no output: the model was moved to
    the GPU in fp32 (1.26 B parameters, ~5 GB of weights), so with the activations the Windows driver spilled into
    system RAM. Stopped (TaskStop + the python process). Fix in `vggt_chunk.py`: weights in bf16, the unused point
    and track heads dropped. Then 8 frames: 26 s, peak 3.3 GB; 32 frames: 22 s, 4.0 GB; 65 frames: 43 s, 5.7 GB.
- **Result 1, 32 keyframes 42 – 63 s** (`vggt_r093/`, log `vggt_r093.log`):
  - Per step against R-080 (whose rotations follow the gyro): 42 – 47.5 s (30 – 520 SfM observations per frame)
    VGGT's step rotation is within 0.4 – 3.5° (confidence ~2.1); from 51 s (0 – 3 observations) 20 – 75° off per step
    (confidence 1.0, its lowest) and the chunk never recovers (110 – 179° off frame 0 by the end). The keyframes are
    sparse exactly in the blank stretch: 3.5 s gaps (47.5 → 51.0 s, 55.2 → 57.8 s) with 64° and 51° of turning
    between neighbours, so this part was unfair to VGGT (hence result 2).
  - Positions: Sim3 on 19 frames with ≥ 20 observations, residual median 0.52 units (R-080's step between these
    frames 0.12): VGGT and R-080 do not agree well even where both have image support; on the 13 weak frames 2.0
    units apart (not meaningful given result 2).
  - **Depth consistency** (frame i's depth moved into frame j, 90 pairs 1 – 3 apart, median relative error): **VGGT
    5.3 %** with its own poses; **Metric3D priors (R-092, per-frame scales) with R-080's poses 15.1 %** (75 pairs with
    valid priors). Supports §11's diagnosis that the current depth guidance contradicts itself between frames.
- **Result 2, 65 video frames every 0.25 s, 44 – 60 s** (`--video_step 0.25`, `vggt_r093_video/`, raw video frames):
  VGGT step rotation vs the gyro, median / max per 2 s bin (gyro step ~4 – 7°): 44 – 46 s 0.63 / 1.2° (confidence
  3.28); 46 – 48 s 0.91 / 1.5° (3.22); 48 – 50 s 3.50 / 8.6° (1.93); 50 – 52 s 3.55 / 6.6° (1.50); 52 – 54 s 4.16 /
  10.2° (1.61); 54 – 56 s 4.87 / 61.4° (1.38); 56 – 58 s 9.90 / 18.0° (1.11); 58 – 60 s 10.00 / 91.8° (1.02). Depth
  consistency 2.5 % (189 pairs). Even with dense, overlapping frames VGGT stops following the camera on the blank
  wall (errors as large as the steps themselves) and says so (confidence at its floor).
- **Verdict:** answers §11.a: **VGGT cannot place the blank-wall frames** (at 518 px on the 8 GB card): rotation is
  better from the gyro, and nothing here supports its positions there. What it does give: depth maps that agree
  across frames about 3× better than the per-frame Metric3D priors on the textured parts. So §11.d uses the room
  planes only; §11.c can use VGGT depth (chunk-wise, scaled to the SfM points) where its confidence is high and the
  planes elsewhere. Extra folder: `vggt_r093_try8/` (the 8-frame memory test).

### R-094 · 2026-11-21 · scan_009_057ed3beb4fc: scale drift corrected with the room height (`v9psc`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 68b12e7 plus uncommitted `room_planes.py`, `scale_drift.py`
- **Found while fitting the room planes (11.b, first try `room_planes_v1/`):** `room_planes.py` on `work_v9pfu_sfm`
  gave 60 planes, among them 5 "floors" between −1.7 and −3.5 and ceilings between 0.3 and 4.1 units. Per 10 s
  of the walk the camera's height in the model stays ~0.1 units, but its distance to the floor (from the depth
  priors, scaled to the SfM points) falls from 4.85 (0 – 10 s) to 3.5 (30 – 40 s), 3.1 (70 – 80 s) and 2.3
  (130 – 140 s); to the ceiling from 3.8 – 4.5 (0 – 40 s) to 2.0 – 2.7 (60 – 140 s). Floor + ceiling seen in the
  same frame (room height): 8.3 / 7.6 units at 20 – 40 s, 4.6 at 130 – 140 s. Model units per Metric3D metre (raw
  Metric3D depth is roughly metric): ~2.7 – 5.3 at 20 – 50 s, ~1.4 – 2.7 after 60 s (10 – 20 s and 180 – 190 s are
  close-ups where Metric3D is known to fail). **The camera path's scale drifts ~2× along the walk** (positions from
  the accelerometer + pair directions, R-071 → R-080), so each part of the room is built at its own size: views
  agree only near where they were taken. This is a more direct explanation of the off-path look than §11's
  per-frame depth-scale point.
- **Code:** `scale_drift.py`: per well-fitted frame (>= 20 SfM inliers, prior residual < 15 %) the distances to its
  horizontal planes (floor / ceiling); fit log distance = constant (floor or ceiling) + log s(t), s piecewise linear
  (knots 10 s, smoothness 3, Huber); rescale every path step by 1 / s(t); re-triangulate every point; check the
  model-units-per-Metric3D-metre ratio per 10 s bin before / after.
- **Command(s):** `python src/arcore3dgs/scale_drift.py $S/work_v9pfy_sfm/sparse_vt_pba_adapt $S/work_v9pfu_sfm
  $S/work_v9pfy_sfm/sparse_scalefix` (12 s); `prior_ba.py $S/work_v9pfy_sfm/sparse_scalefix $S/work_v9pfl
  …/sparse_scalefix_pba --adapt_n 150 --loose_t0 2 --loose_t1 30 --iters 150 --colmap …` (as R-080, 2.1 min); then
  `dataset/scan_009_057ed3beb4fc/r094.sh` (log `r094.log`): `work_v9pfz` → `work_v9psc`, `sparse_scalefix_pba` →
  `work_v9psc_sfm/sparse/0`, `sfm_colmap.py --stage {undistort, export} --sim3 none`, `run_v8.py --tag v9psc
  --from_stage export --pose_free --init fmvs --planar 0.2 --blur 0.0222 --pgsr --split s10_test.txt --train_args
  "--path_prune 0.1"` (= R-090 on the corrected cameras); evaluations with R-082 and R-090; `room_planes.py` on the
  new priors
- **Scale correction result:** 339 floor / ceiling distances (149 / 190); s(t) at the knots 0 s 1.66, 10 s 1.55,
  20 s 1.49, 30 s 1.39, 40 s 1.24, 50 s 1.10, 60 s 0.96, 70 s 0.98, 80 s 1.06, 90 s 1.03, 100 s 0.94, 110 s 0.83,
  120 s 0.78, 130 s 0.82, 140 s 0.87, 150 s 0.80, 160 s 0.66, 170 s 0.69, 180 s 0.84, 190 s 1.00; residual median
  16.2 % (log distance; includes the hand height changing). Path length 57.9 → 62.7 units. 29,587 points
  re-triangulated, 1,541 dropped. Model units per Metric3D metre per 10 s bin, before → after: 0 – 10 s 2.77 → 1.90;
  20 – 30 s 2.68 → 1.88; 30 – 40 s 5.13 → 3.83; 40 – 50 s 5.29 → 4.42; 60 – 70 s 1.79 → 1.84; 70 – 80 s 2.11 → 2.03;
  80 – 90 s 1.34 → 1.28; 90 – 100 s 2.18 → 2.13; 100 – 110 s 2.67 → 3.07; 110 – 120 s 2.41 → 2.92; 120 – 130 s 1.48 →
  1.85; 130 – 140 s 1.79 → 2.10; 140 – 150 s 2.06 → 2.44; 150 – 160 s 1.40 → 2.10; 160 – 170 s 1.36 → 2.02; 170 – 180 s
  2.09 → 2.61; 180 – 190 s 1.79 → 1.97 (10 – 20 s 14.18 → 23.17 and 50 – 60 s 0.16 → 0.17: Metric3D unreliable there);
  spread across bins (p90 / p10) **3.81 → 2.29**. 30 – 50 s stays high (3.8 – 4.4): not explained. Prior BA:
  reprojection 1.11 → 1.10 px (R-080: 1.13), relative rotation vs the gyro prior median 0.062°, 622 cameras (3D obs
  median 108; 45 – 60 s: 36 cameras, median 1).
- **Goal:** one room size along the whole walk; then one set of room planes (11.b) and consistent depth (11.c).
- **Start → end:** 18:37 → 19:06 (export 0.01, prior 3.56, init 1.43, train 23.05, ply 0.58 min, total 29.2);
  `→ work_v9psc_sfm/gs_v9psc/splat.ply` (129 MB). Export kept 600 frames (R-090: 622). sfm_scale_check: ratio median
  2.381 units per Metric3D metre, verdict "ok", close-up blocks frame_00395 (5.07×) and frame_05554 (7.30×).
- **Paused** at Tayyab's request ("pause at the next stopping point") right after the export: the script was stopped
  as `eval_offpath.py` started (19:06), so **no evaluation yet**. Not run: `eval_offpath.py` / `eval_align.py`
  (note: the script compared R-082 / R-090 on R-094's corrected poses, which is wrong, since those models live in the
  uncorrected coordinates; when resumed, R-094 is scored on its own and against R-090's own numbers: 21.10 / aligned
  22.52) and `room_planes.py` on `work_v9psc_sfm`. Then 11.c (`plane_prior.py`, written, not run).
- **Errors during the run:** `prior_ba.py` first stopped at the end (`FileNotFoundError: …sparse_scalefix
igs.txt`):
  `scale_drift.py` wrote only cameras / images / points; fixed (it now copies `rigs.txt` and `frames.txt`), files
  copied by hand, rerun ok.
- **Resumed 2026-11-21 (Tayyab: "ok claude you can resume").** Errors: `eval_offpath.py` and `eval_align.py` stopped
  with `KeyError: 'frame_01537'`: the export dropped 3 held-out frames (jump filter); both tools now skip held-out
  names not in the model and say how many.
- **Result:** `eval_offpath.py` (own poses, 66 of 69 held-out frames): PSNR 20.85, SSIM 0.865, 0 blocked, flatness
  11.98 "cm" (model units × 100: not comparable with the uncorrected models, whose scale differs); `eval_align.py`:
  aligned **22.59**, SSIM 0.874, correction median 2.36°. R-090 on the same 66 frames (its own poses): aligned 22.63.
  Per stretch R-090 → R-094: still 0 – 17 s 24.87 → 25.09; 22 – 25 s 26.47 → 25.75; 51 – 53 s 22.99 → 20.84; 78 – 81 s
  23.96 → 23.23; 106 s 28.49 → 27.73; 134 – 137 s 17.07 → 18.29; 162 – 165 s 21.65 → 22.76; 186 s 15.75 → 15.85.
  `room_planes.py` on `work_v9psc_sfm` (`room_planes_v9psc/`): 57 planes; floor / ceiling height per 20 s: floor
  −2.35 … −3.39 and ceiling 2.6 … 3.4 for 20 – 160 s (before: floor −2.2 … −3.4, ceiling 2.0 … 4.2; room height
  5.0 – 6.0 units instead of 4.6 – 7.6); 0 – 20 s still large (floor −4.63, only 7 floor measurements) and 40 – 60 s
  meaningless (floor −10); walls still split into parallel copies (horizontal drift, which the room height cannot see).
- **Verdict:** kept as the camera model for 11.c; the vertical scale is more uniform, the image scores are unchanged
  overall (better late in the walk, worse in 22 – 25 s / 51 – 53 s / 78 – 81 s). One run.

### R-095 · 2026-11-21 · scan_009_057ed3beb4fc: 11.c priors from the room planes (`v9ppl`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 6408fae plus uncommitted eval fixes and `plane_prior.py`
  (ghost-plane guard)
- **Dataset:** `work_v9psc` → `work_v9ppl`, `work_v9psc_sfm` → `work_v9ppl_sfm` (without the model, eval and the
  `undist_fast/images` junction); R-094's cameras, split, Metric3D priors; room planes `room_planes_v9psc/room_planes.json`
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r095.sh` (log `r095.log`): `plane_prior.py --work …/work_v9ppl_sfm
  --planes …/room_planes_v9psc/room_planes.json --min_frames 15`; `run_v8.py --tag v9ppl --from_stage init` with
  R-094's recipe (so the rewritten priors are not recomputed); `eval_offpath.py`, `eval_align.py` on its own poses
- **Goal:** plan §11.c: depth guidance that agrees across frames (R-093: neighbouring Metric3D priors disagree by
  15.1 %); compared with R-094 (same cameras, per-frame priors).
- **Start → end:** 20:00 → 20:36 (plane priors 1.8 min; init 1.39, train 22.23, ply 0.55 min; evaluations 17 min)
- **Errors during the run:** none.
- **Result:** `plane_prior.py`: 31 planes with >= 15 frames; 600 frames; scale change median 0.866 (p10 0.346, p90
  1.005); trusted (plane) pixels median 21 %; no frame without a prior gained one. **Depth disagreement between
  neighbouring frames (every 3rd frame, 1 – 2 apart, median): 6.8 % → 3.6 %.** Scale change per 20 s (median / p10):
  0 – 20 s 0.74 / 0.56; 20 – 40 s 0.70 / 0.37; **40 – 60 s 0.14 / 0.05**; 60 – 80 s 0.80 / 0.45; 80 – 100 s 1.00 / 0.77
  (0 % trusted); 100 – 120 s 0.85 / 0.58; 120 – 140 s 0.66 / 0.26; 140 – 160 s 1.00 / 0.77; 160 – 180 s 0.99 / 0.80;
  180 – 200 s 1.00 / 0.96. `→ work_v9ppl_sfm/gs_v9ppl/splat.ply`, 542,994 splats. `eval_r095/`: PSNR 19.94 (R-094
  20.85), SSIM 0.850 (0.865), 0 blocked; aligned **21.53** (R-094 22.59 on the same 66 frames), SSIM 0.869.
  Aligned per stretch R-094 → R-095: still 25.09 → 25.09; 22 – 25 s 25.75 → 24.01; **51 – 53 s 20.84 → 22.90**;
  78 – 81 s 23.23 → 20.75; 106 s 27.73 → 28.46; 134 – 137 s 18.29 → 17.12; 162 – 165 s 22.76 → 22.21; 186 s 15.85 →
  15.59.
- **Verdict:** rejected. The priors agree better between frames, but with a fragmented plane set: R-094's model
  still has parallel copies of walls (horizontal drift), each frame takes the nearest plane its rays hit, and many
  frames were shrunk towards planes in front of the real wall (40 – 60 s by 0.14, where the poses rest on the
  sensors; 20 – 40 s and 120 – 140 s by ~0.7). Consistent guidance only helps once the room is one room: 11.c needs
  the horizontal drift fixed first (11.d).


### R-096 · 2026-11-22 · scan_009_057ed3beb4fc: 11.d loops closed with the long-range image pairs (`v9plp`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ a0a6c7f plus uncommitted `loop_path.py` and
  `scale_drift.py` (re-triangulation moved into `read_model` / `write_model`; output on R-094's input checked
  byte-identical)
- **Found before the run (2026-11-22):** R-094's camera model has almost no point tracks between distant times: of
  29,207 points, 1,327 span >= 60 s (1,198 of them 0 – 20 s ↔ 180 – 200 s, the start / end loop), 262 span 20 – 60 s.
  The bundle adjustment never sees the places the walk revisits. The evidence exists in rot_sfm's pair-direction
  cache (`work_v9pfy_sfm/pair_directions_dt300_par1_bg.json`): 6,148 pairs in the model, of them 905 at 5 – 20 s,
  432 at 20 – 60 s and 852 at >= 60 s apart (e.g. 142 pairs 100 – 120 s ↔ 140 – 160 s). Angle between each pair's
  direction and the camera path, dt >= 60 s (median / p75): R-080's path 5.17 / 11.39°, **R-094's path 7.20 /
  28.56°** (the room-height correction bent the path against the loops), rot_sfm's initial path 5.65 / 15.75°
  (scratchpad `loop_resid.py`). The wall planes (`room_planes.py`) were tried first as the drift signal and judged
  too noisy: plane normals of one frame scatter by 6.6° (median, 303 frames with >= 2 walls).
- **Code:** `loop_path.py`: camera centres solved again (rotations kept) with the input path's steps as the shape
  (sigma 0.01 + 0.05 × step), the pairs >= 5 s apart as direction constraints (sigma 5°, Cauchy), a rotation from
  rot_sfm's world to the model's fitted on the < 5 s pairs; 20 % of the loop pairs held out for a validation solve;
  points re-triangulated.
- **Command(s):** `python src/arcore3dgs/loop_path.py $S/work_v9pfy_sfm/sparse_scalefix_pba $S/work_v9psc_sfm
  $S/work_v9pfy_sfm/pair_directions_dt300_par1_bg.json $S/work_v9pfy_sfm/sparse_loop2`; `prior_ba.py
  $S/work_v9pfy_sfm/sparse_loop2 $S/work_v9pfl $S/work_v9pfy_sfm/sparse_loop2_pba --pair_priors …/sparse_loop2/loop_pairs.json --adapt_n 150 --loose_t0 2
  --loose_t1 30 --iters 150 --colmap …` (as R-080 / R-094); then `dataset/scan_009_057ed3beb4fc/r096.sh` (log
  `r096.log`): `work_v9pfz` → `work_v9plp`, `sparse_loop2_pba` (see below) → `work_v9plp_sfm/sparse/0`, `sfm_colmap.py --stage
  {undistort, export} --sim3 none`, `run_v8.py --tag v9plp` with R-094's recipe; `eval_offpath.py`, `eval_align.py`
  (own poses), `room_planes.py`
- **Goal:** plan §11.d: the walls seen at different times coincide (one room instead of parallel copies); compared
  with R-094 (aligned 22.59) and R-090 (22.63) on the same held-out frames.
- **Start → end:** 01:43 (loop solve) → 02:30 (loop solve + BA 7 min incl. the failed first BA; copy / undistort /
  export 01:52 – 01:53; prior 3.45, init 1.67, train 22.46, ply 0.63 min, total 28.3; evaluations + room planes 9 min)
- **Errors / changes during the run:**
  1. 01:45 prior BA: no error, but it **undid most of the loop closure**: `sparse_loop` → `sparse_loop_pba`, angle of
     the >= 60 s pairs median 1.96 → 5.96°, p75 4.50 → 13.03° (it sees only short tracks and drifts again). Fix:
     `prior_ba.py --pair_priors` (new): the loop pairs the solved path agrees with (< 15°, 2,036 of 2,189, written by
     `loop_path.py` as `loop_pairs.json`) keep their relative position as a prior, sigma 0.02 + 0.1 × distance.
     Rerun as `sparse_loop2` (same solve) → `sparse_loop2_pba` (2.9 min). Also tried `--loop_s1 0.05`
     (`sparse_loop2_pba05`): about the same (median 3.22°, p75 7.16°), rotations moved more (median 1.55° vs 1.17°);
     not used. Logs `r096_loop.log`, `r096_pba.log`, `r096_loop2.log`, `r096_pba2.log`, `r096_pba3.log`.
- **Loop solve result (`loop_path.py`, 10 s):** rotation rot_sfm world → model 90.57° (fitted on 3,940 short
  pairs); 2,189 pairs >= 5 s apart. Validation (20 % of them held out of the solve, never fitted), held-out pairs
  input → solved, median / p75: 5 – 20 s 6.47 / 10.47 → 2.88 / 5.66°; 20 – 60 s 3.28 / 7.77 → 2.07 / 3.90°;
  **>= 60 s 7.02 / 30.29 → 2.49 / 4.63°** (pairs < 5°: 42 → 78 %). Cameras moved median 0.51, p90 1.03, max 1.48
  units; path length 61.1 → 56.2; largest shifts at 10 – 40 s (z −0.5 … −0.9) and 110 – 120 s / 150 – 160 s (z +0.7 …
  +1.0). 26,997 points re-triangulated, 2,571 dropped.
- **After the prior BA with loop priors (`sparse_loop2_pba`):** reprojection median 1.08 px, p90 2.51 (R-094's BA
  1.10 px); pose change vs the solve: position median 0.159, p95 0.232; rotation median 1.17° (relative rotation vs
  the gyro prior median 0.050°); angle of all pairs, median / p75 (R-094 → R-096): 5 – 20 s 6.34 / 12.10 → 4.31 /
  9.05°; 20 – 60 s 3.33 / 8.50 → 2.21 / 4.69°; **>= 60 s 7.20 / 28.56 → 3.49 / 7.05°** (scratchpad `loop_resid.py`,
  one global rotation fitted on the short pairs per model).

- **Result:** `→ work_v9plp_sfm/gs_v9plp/splat.ply`, 544,401 splats. Export kept 581 frames (19 dropped by the
  jump filter, spread over 47 – 176 s; the loop solve used R-094's 600). `eval_offpath.py` (own poses, 63 of 69
  held-out frames; 6 dropped by the export): PSNR 21.27, SSIM 0.871, sharpness 0.34, flatness 6.57 "cm" (model
  units × 100; R-094 11.98, path ~15 % shorter in R-096), 0 blocked. `eval_align.py`: **aligned 23.63**, SSIM 0.888,
  correction median **1.57°** (R-094 2.36°: the held-out poses fit the model better). **On the 63 held-out frames
  both models have** (each on its own poses): raw PSNR 20.93 → 21.27, **aligned 22.67 → 23.63 (+0.96 dB)**,
  correction median 2.31 → 1.57°. Per stretch, aligned R-094 → R-096: still 0 – 17 s 25.09 → 25.79; 22 – 25 s
  25.75 → 25.76; 51 – 53 s 21.18 → 21.56; 78 – 81 s 23.23 → 23.47; 106 s 27.73 → 30.36; **134 – 137 s 18.29 →
  20.10; 162 – 165 s 23.12 → 25.13**; 186 s 15.85 → 20.12 (1 frame). No stretch worse. Run-to-run noise (R-088)
  ~0.1 – 0.25 dB overall, so the gain is well beyond it (one run).
  Wall offsets (scratchpad `wall_obs.py` / `plot_obs.py`, per axis / side the number of 0.15-unit offset bins that
  hold 80 % of the trusted wall pixels, R-094 → R-096): X+ 12 → 9, X- 13 → 16, Z+ 14 → 11, Z- 24 → 17, floor 8 → 9,
  ceiling 7 → 8. The far Z- wall seen at 0 – 25 s moved from 5.3 – 7.7 to 3.3 – 4.3 units, matching the later views
  (3.8 – 4.8); 40 – 47 s still 5.5 – 7.3. `room_planes.py` (`room_planes_v9plp/`): 54 planes (R-094 57). Residual
  scale drift (`scale_drift.py` measurement only, nothing written into the run): s(t) 0.85 – 1.18 over 0 – 180 s
  (R-094's own: 0.83 – 1.46), model units per Metric3D metre spread across 10 s bins 2.04 (R-094 2.42); applying
  the room-height correction again would raise it to 2.58, so it was not applied.
  Off-path views (new `offpath_views.py`, `offpath_views_r096/`: 8 views from the room centre + a top view of the
  slice camera height −1 … +0.5): R-096 shows a coherent room in 6 of 8 directions (doors, walls, corridor), R-094 /
  R-090 mostly blank close walls there (each model's own centre, so not the identical point); in the top view the
  walked area of R-090 / R-094 is crossed by wall slabs (ghost copies), R-096's is mostly clear; walls still thick.
- **Verdict:** **kept: first clear gain of the featureless work** (+0.96 dB aligned on the same frames, every stretch
  equal or better, off-path views more coherent). Not yet in the viewer. Next: a second matching round with these
  cameras (R-097).

### R-097 · 2026-11-22 · scan_009_057ed3beb4fc: 11.d second round, loop pairs chosen and matched with R-096's cameras (`v9plm`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ a0a6c7f plus uncommitted R-096 code and new `loop_match.py`,
  `loop_path.py --model_frame`
- **Dataset:** R-096's cameras (`work_v9pfy_sfm/sparse_loop2_pba`) and depth priors (`work_v9plp_sfm/mono_prior`);
  ALIKED database of the keyframes `work_v9pfm_sfm/database.db` (copied, not changed)
- **Command(s):** `python src/arcore3dgs/loop_match.py $S/work_v9pfy_sfm/sparse_loop2_pba $S/work_v9plp_sfm
  $S/work_v9pfm_sfm/database.db $S/work_v9pfy_sfm/loop_match2` (pairs >= 5 s apart whose depth-prior cells overlap
  >= 30 %, viewing directions within 60°, not matched before, <= 8 per keyframe, <= 4,000; ALIKED + LightGlue with
  `matches_importer`; directions of all verified pairs in the model's world); `loop_path.py
  …/sparse_loop2_pba $S/work_v9plp_sfm …/loop_match2/pair_directions.json …/sparse_loop3 --model_frame`; `prior_ba.py
  … --pair_priors …/sparse_loop3/loop_pairs.json` → `sparse_loop3_pba`; then `r097.sh` as R-096 with tag `v9plm`
- **Goal:** walls still thick in R-096 (several Z- wall offsets 3.1 – 4.8); more loop pairs where the walk revisits
  a surface; compared with R-096 (aligned 23.63 on 63 held-out frames).
- **Start → end:** 02:34 (matching) → 03:17 (matching + directions 1.6 min; loop solve 10 s; BA 1.1 min; copy /
  export 02:38; prior 3.55, init 1.38, train 22.64, ply 0.57 min, total 28.7; evaluations / views 10 min)
- **Errors during the run:**
  1. 02:34 `loop_match.py` stopped after matching: `TypeError: a bytes-like object is required, not 'NoneType'`
     (keypoint rows without data for images with no keypoints) → skipped such rows; rerun (the first 482 pairs had
     already been matched into the copy, so the second call chose 1,570 more with `--min_overlap 0.2 --voxel 0.4
     --per_frame 12`). Logs `r097_match.log`, `r097_match2.log`.
  2. 02:36 `loop_path.py --model_frame` stopped (`AxisError`: no short pairs to fit the rotation on) → the rotation
     fit is skipped with `--model_frame`; rerun.
- **Matching / solve result:** 3,425 candidate pairs not matched before; 482 + 1,570 matched; of the second call's
  1,570, 1,095 verified, 1,031 with a direction. Directions >= 5 s in total (old + new, recomputed with R-096's
  rotations): 3,161 (5 – 20 s 1,101; 20 – 60 s 696; >= 60 s 1,364). Loop solve on R-096's cameras: held-out pairs
  >= 60 s median 2.35 → 0.94°, p75 5.22 → 1.91°; cameras moved median 0.114, max 0.267 units; 3,037 of 3,161 pairs
  agree (< 15°). Prior BA: reprojection 1.07 px; position change median 0.059.
- **Result:** `→ work_v9plm_sfm/gs_v9plm/splat.ply`, 568,732 splats; export 581 frames; 63 of 69 held-out frames.
  `eval_offpath.py`: PSNR 20.80, SSIM 0.863, flatness 6.07, 0 blocked; `eval_align.py`: aligned **22.93**, SSIM
  0.878, correction median 2.21°. On the 63 common frames, aligned R-094 / R-096 / R-097: 22.67 / **23.63** / 22.93.
  Per stretch R-096 → R-097: still 25.79 → 25.75; 22 – 25 s 25.76 → 26.86; 51 – 53 s 21.56 → 22.11; 78 – 81 s 23.47 →
  23.48; 106 s 30.36 → 28.80; **134 – 137 s 20.10 → 15.81** (corrections up to 12.4°, still 15 – 16 dB after
  alignment: the area is built wrongly); 162 – 165 s 25.13 → 26.04; 186 s 20.12 → 19.65. 91 of the new pairs touch
  125 – 145 s, 38 of them linked to 140 – 160 s. `room_planes.py`: 58 planes. Off-path views in
  `offpath_views_r097/`.
- **Verdict:** rejected. Better in four stretches but one stretch broken, most likely by wrong matches among the new
  pairs (the loop pairs are not checked against anything but their own agreement); the second round needs a
  stricter pair check before it can be used. R-096's cameras stay.

### R-098 · 2026-11-22 · scan_009_057ed3beb4fc: 11.c second form, contradicted prior pixels dropped, on R-096's cameras (`v9pcs`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 7fdfc92 plus uncommitted `prior_consistency.py`
- **Dataset:** `work_v9plp` → `work_v9pcs`, `work_v9plp_sfm` → `work_v9pcs_sfm` (without the model, eval and the
  `undist_fast/images` junction): R-096's cameras, split and Metric3D priors
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r098.sh` (log `r098.log`): `prior_consistency.py --work
  …/work_v9pcs_sfm --pairs …/work_v9pfy_sfm/sparse_loop2/loop_pairs.json` (3 time neighbours each side + up to 6 loop
  partners; a prior pixel is switched off when other views see free space in front of it at least as often as they
  agree, tolerance 10 %); `run_v8.py --tag v9pcs --from_stage init` with R-096's recipe; `eval_offpath.py`,
  `eval_align.py` (own poses), `offpath_views.py` with R-096
- **Goal:** depth guidance that does not contradict itself across time without forcing it onto planes (R-095).
  Dry run on R-096's priors: depth disagreement loop partners 12.4 → 9.1 % median, time neighbours 3.5 → 2.9 %;
  18.9 % of the valid prior pixels dropped (some frames ~50 – 58 %). Compared with R-096 (aligned 23.63, 63 frames).
- **Start → end:** 03:17 → 03:51 (copy + consistency filter 1.2 min; init 1.63, train 21.81, ply 0.56 min, total
  24.0; evaluations / views 8 min)
- **Errors during the run:** none.
- **Result:** filter as the dry run: 11,597,123 of 61,268,191 valid prior pixels dropped (18.9 %); disagreement
  time neighbours 3.5 → 2.9 %, loop partners 12.4 → 9.1 %. `→ work_v9pcs_sfm/gs_v9pcs/splat.ply`, 521,335 splats.
  `eval_offpath.py` (63 frames): PSNR 21.59 (R-096 21.27), SSIM 0.871 (0.871), sharpness 0.41 (0.34), flatness 8.54
  (6.57), 0 blocked. `eval_align.py`: aligned **23.61** (R-096 23.63 on the same 63 frames), SSIM 0.892 (0.888),
  correction median 1.22° (1.57°). Per stretch R-096 → R-098: still 25.79 → 25.85; 22 – 25 s 25.76 → 26.27; 51 – 53 s
  21.56 → 21.86; 78 – 81 s 23.47 → 23.76; 106 s 30.36 → 29.69; 134 – 137 s 20.10 → 19.82; 162 – 165 s 25.13 → 24.02;
  186 s 20.12 → 19.54. Off-path views (`offpath_views_r098/`): nearly the same as R-096.
- **Verdict:** inconclusive, not adopted: aligned PSNR equal within noise, small gains in raw PSNR / SSIM, flatter
  walls lost; R-096's recipe (no filter) stays the simpler one. One run.

### R-099 · 2026-11-22 · scan_009_057ed3beb4fc: R-096's recipe on all frames, for the viewer (`v9plf`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 6f4a003 (records uncommitted)
- **Dataset:** `work_v9pfz` → `work_v9plf`; R-096's cameras `work_v9pfy_sfm/sparse_loop2_pba` → `work_v9plf_sfm/sparse/0`
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r099.sh` (log `r099.log`): as `r096.sh` with tag `v9plf` and **no
  `--split`** (no held-out frames); `offpath_views.py` with R-096
- **Goal:** the model Tayyab looks at in the viewer: R-096's cameras and recipe with every frame in training
  (R-096 held out 69 frames). No held-out score possible.
- **Start → end:** 03:51 → 04:20 (copy / undistort / export 03:51 – 03:52; prior 3.36, init 1.64, train 22.16, ply
  0.58 min, total 27.9; views 4 s)
- **Errors during the run:** none.
- **Result:** `→ work_v9plf_sfm/gs_v9plf/splat.ply`, 513,603 splats; export 581 frames (19 dropped by the jump filter,
  as R-096), all used for training. No held-out score (no split). Off-path views (`offpath_views_r099/`): the same
  room-centre views as R-096. In the viewer as `scan-009-loops` (`prototype/web-ui/public/splats/scan009_v9plf.spz`,
  9.8 MB, local only). Free disk on C: after the run: 4.2 GB (`df`).
- **Verdict:** kept as the scan_009 model to look at; not yet inspected by Tayyab.

### R-100 · 2026-11-22 · scan_009_057ed3beb4fc: floaters removed from R-096's model with free-space evidence (no retraining)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 9f59d9e (`clean_splats.py` changes committed after the run)
- **Dataset:** `work_v9plp_sfm` (R-096), its `splat.ply` (not changed; output `gs_v9plp/splat_clean_r100.ply`)
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r100.sh` (log `r100.log`): `clean_splats.py --mono 1 --mono_tol 0.2
  --exclude offpath_test.txt --max_depth 20` (evidence: depth priors and BA points of every 2nd training frame,
  the 69 held-out frames left out; a splat is dropped when >= 3 views see through it and none sees it as a surface,
  or no view sees it, or it is < 0.2 units from the camera path); then `eval_align.py` (R-096 vs cleaned, the same
  held-out frames) and `offpath_views.py`
- **Goal:** plan step 1 after Tayyab's look at R-099 (2026-11-22): floating splats in the bathroom doorway block the
  view inside. Remove splats in space the cameras looked through, without losing held-out quality.
- **Start → end:** 13:16 → 13:54 (cleaning 10 s each; `eval_align.py` 17 min for two models; off-path views 5 s;
  variants `r100b.sh` / `r100b.log` 13:34 → 13:54)
- **Errors during the run:** none. Planned run changed before it started: `clean_splats.py` needed stereo depth
  (`depth_mvs/`, `mvs_mask/`, `depth_scale`), which sensor-path models do not have; with no stereo views its "never
  in view" test would have dropped every splat. Added `--mono`, `--exclude`, `--max_depth`, BA points projected with
  the frame camera (stored uv belong to a 1080-px-high image, frames are 1048). A numpy RuntimeWarning (cast of
  points behind the camera to int) is harmless: those points are masked by z > 0.1.
- **Result:** evidence from 260 prior views and 409 BA views (69 held-out frames excluded). Both rules: 21,000 of
  544,401 splats dropped (see-through 10,485, < 0.2 units from the camera path 9,948, never in view 566). Where
  (`offpath_views_r100/dropped_plan.png`, scratch `plot_dropped.py`): the see-through splats sit in the middle of the
  room at y 0.5 – 2.5 (cameras at y 0.15 median, floor near y −2, ceiling near y 2.8), i.e. in the air above head
  height; 533 of ~12,900 floor splats in the room centre (y −2.5 – −1.5) were dropped too. Aligned PSNR, the same 63
  held-out frames (`work_v9plp_sfm/eval_r096/aligned_r100.csv`, `aligned_r100b.csv`):

  | Model | Aligned PSNR | SSIM | 0 – 5 s (3) | 20 – 25 s (14) | 134 – 138 s (15) | 160 – 166 s (7) |
  |---|---|---|---|---|---|---|
  | R-096 | 23.63 | 0.8881 | 28.25 | 25.76 | 20.10 | 25.12 |
  | both rules | 23.31 | 0.8832 | 27.16 | 24.99 | 20.28 | 24.46 |
  | see-through only (`_fl`) | 23.54 | 0.8859 | 28.25 | 25.76 | 20.08 | 24.51 |
  | camera-path radius only (`_near`) | 23.40 | 0.8855 | 27.16 | 24.99 | 20.32 | 25.08 |

  The camera-path rule removes real surface where the camera came close to a wall (0 – 5 s, 20 – 25 s). The
  see-through rule costs 0.09 dB (3 frames > 0.5 dB worse, 160 – 166 s). Room-centre ring (`compare_ring.jpg`): the
  flat near surface seen at yaw 135 – 225 from the room centre gets holes (white: nothing behind it), it is not
  replaced by the far wall. **Bathroom doorway** (frame_03753, 125.1 s, a training frame; scratch `door_views.py`,
  `offpath_views_r100/door_125s.jpg`): R-096 renders the open doorway as a smear even from the frame's own pose, and
  from 0.7 units to the side; the cleaned model looks the same. Training-frame PSNR per 10 s (R-096, raw `images/`, no
  exposure correction, so only the relative values mean anything): 100 – 150 s median 16.8 – 18.0, elsewhere mostly
  19.3 – 24.5: the doorway stretch is the worst-fitting part of the walk, even on the frames trained on. Outputs:
  `work_v9plp_sfm/gs_v9plp/splat_clean_r100{,_fl,_near}.ply` (+ `_dropped.npz`), `offpath_views_r100/`.
- **Verdict:** rejected as the fix for the doorway: the doorway smear is not free-space floaters but the 100 – 150 s
  stretch fitting badly (cameras); the camera-path rule is harmful (−0.23 dB); the see-through rule alone is close to
  neutral (−0.09 dB) and only clears mid-air splats; not adopted. `clean_splats.py --mono` kept as a tool.

### R-103 · 2026-11-23 · (numbered R-085 until 2026-11-23, D-091) scan #6 fixture check sheet from R-059 (`r1119b6`), CPU only
- **Who / machine:** agent for Umair · this PC (Ubuntu, RTX 4000 Ada), while R-101 (`run-r071g6`, speed session) runs
  `patch_match_stereo` on the GPU; this run uses no GPU and a few MB of RAM (standard-library script).
- **Branch / commit:** `feature/step4-triage` (worktree `../BuildScan3D-step4`, from `origin/master` `8338680`)
- **Dataset:** R-059's `dataset/scan_006_1e457a214ce1/work_r1119b6_sfm/gs_r1119b6/semantic_v10/semantic.json` and
  `layout/layout.json` (read only). The sheet goes to a new folder `dataset/scan_006_1e457a214ce1/checks_r085/`, so
  R-059's run folder is not written.
- **Command(s):** `python3 src/arcore3dgs/fixture_checklist.py --semantic <gs_r1119b6>/semantic_v10/semantic.json
  --layout <gs_r1119b6>/layout/layout.json --out dataset/scan_006_1e457a214ce1/checks_r085/fixture_check.md
  --title "scan #6 (R-059, r1119b6)" --rejected`
- **Goal:** the scan #6 sheet for Umair (#21, plan 4.2), like the other rooms' sheets.
- **Start → end:** 11:22:41 → 11:22:41 (< 1 s)
- **Errors during the run:** none (exit 0).
- **Result:** `dataset/scan_006_1e457a214ce1/checks_r085/fixture_check.md` (137 lines): 11 fixtures, empty "missed"
  table, summary per class, and the 84 rejected candidates with their failed rule. Seen while reading it (not
  checked against the room): `light_switch_2` and `light_switch_5` are both on wall 0 at 1.00 m along, 0.76 / 0.75 m
  up (8 × 8 and 6 × 7 cm), so they may be one plate found twice; `power_socket_1` is at 1.88 m and `light_switch_4`
  at 0.49 m, unusual heights; `doorway_1` (wall gap) has 0 frames because it comes from the layout, not from 2D
  detections.
- **Verdict:** kept: the sheet is ready for Umair (#21).

### R-104 · 2026-11-23 · (numbered R-086 until 2026-11-23, D-091) Wall roughness in the mesh: how much and where (plan 4.12, #18), four rooms, CPU only
- **Who / machine:** agent for Umair · this PC (Ubuntu, RTX 4000 Ada); R-101 runs `patch_match_stereo` on the GPU
  meanwhile (no SfM running; ~23 GB RAM available). This run is CPU only (open3d + numpy, one mesh at a time, < 1 GB).
- **Branch / commit:** `feature/step4-triage` (worktree `../BuildScan3D-step4`)
- **Dataset:** `mesh/mesh_clean.ply` + `layout/layout.json` of scan #6 `gs_r1119b6` (R-059), scans #7 / #8 and
  newRoom `gs_r1119c` (R-057). Read only; scan #3 left out (Umair: poor recording).
- **Command(s):** `micromamba run -n bs-ns python <scratchpad>/r086_walls.py`: `mesh.py`'s `shell_flatness` (copied
  unchanged: robust plane per wall, median |deviation|, % within 1 cm), plus, for each wall, the share of its vertices
  > 2 cm off the plane per height band (0.15–1.0 m, 1.0–2.0 m, > 2.0 m) and per third along the wall, and the sign
  of the large deviations (into the room = something in front of the wall; behind = a recess or noise behind it).
- **Goal:** 4.12's open part: are rough walls rough everywhere (noise / real relief) or only in a band or stretch
  (furniture against the wall, a window, a board)? No ground truth needed; options for Umair afterwards.
- **Start → end:** 11:25:32 → 11:25:36 (3.4 s, peak RSS 0.79 GB); part 2 (`<scratchpad>/r086_hist.py`: signed
  deviation histogram in 1 cm bins and median offset per third, for six walls) a few seconds after.
- **Errors during the run:** none (exit 0).
- **Result:** the measure agrees with the earlier ones (scan #8 wall 1 1.55 cm = R-057; newRoom wall 3 2.88 cm, #18:
  2.86). 20 walls; median |deviation| ≤ 0.26 cm on 16 of them. The four rough ones:

  | Wall | Length | Median cm | > 2 cm off | in front / behind | Where | Shape |
  |---|---|---|---|---|---|---|
  | newRoom wall 3 | 4.57 m | 2.88 | 64.8 % | 32.4 / 32.4 % | every height band (79.7 / 68.6 / 48.1 %), every third | broad spread ±5 cm, no peak; median offset per third −0.45 / +1.10 / +1.59 cm; plane 1.47° off vertical (other walls 0.1–0.4°) |
  | scan #8 wall 1 | 6.03 m | 1.55 | 44.8 % | 24.2 / 20.6 % | every band, every third | several peaks (−3, 0, +4 cm); median offset per third −1.31 / **+2.45** / −0.27 cm: stretches at different depths |
  | scan #6 wall 5 | 0.74 m | 4.70 | 73.9 % | 33.2 / 40.7 % | every band; first two thirds | flat ±8 cm spread with a gap at +1 cm: two surfaces, not one plane |
  | newRoom wall 4 | 0.78 m | 1.23 | 24.8 % | 12.5 / 12.3 % | every band | (short jog, not histogrammed) |

  Walls with a little roughness have it in one place and mostly in front of the wall (things against it): e.g. scan #6
  wall 4 (2.32 m) 21 % in its first third, 19.9 % above 2 m, 7.6 of 8.6 % in front; newRoom wall 0 48.3 % below 1 m in
  its last third, 17.3 of 21.2 % in front, while its histogram keeps a sharp peak (62.6 % within ±1 cm).
- **Reading (not checked in the room):** the rough walls are not "noise on a flat wall" that a clean-up should flatten:
  scan #8 wall 1 and scan #6 wall 5 are stretches at different depths joined into one layout wall (scan #8 wall 1 got
  longer in R-057 when `--raised_max` dropped the corner furniture, 0.06 → 1.55 cm); newRoom wall 3 is bowed or
  leaning (offset rising 2 cm along it, 1.47° off vertical) with broad scatter, which may be real (curtain, cupboard
  fronts) or a poorly seen wall. Flattening these like `--clean_ceiling` would move real surfaces by several cm.
- **Verdict:** inconclusive on cause (needs a look at the three walls in the viewer); options to Umair (4.12).

### R-120 · 2026-11-22 · (numbered R-101 until 2026-11-23, D-096; script and log names keep `r101`) scan_009_057ed3beb4fc: R-096 plus camera refinement in training (`v9plo`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 61655ce
- **Dataset:** `work_v9pfz` → `work_v9plo`; R-096's cameras `work_v9pfy_sfm/sparse_loop2_pba` → `work_v9plo_sfm/sparse/0`
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r101.sh` (log `r101.log`): `r096.sh` with tag `v9plo` plus `--pose_opt`
  (nerfstudio SO3xR3 camera optimiser, as R-084); `eval_offpath.py`, `eval_align.py` (63 common held-out frames),
  `offpath_views.py` with R-096
- **Goal:** plan step 4 (Tayyab 2026-11-22: "continue the step 4 and then 3"). R-100 showed the bathroom doorway
  (125 s) is a smear even from its own training pose and the 100 – 150 s stretch fits worst: per-frame camera error.
  R-084 tried `--pose_opt` on R-080's cameras (no gain after alignment); R-096's cameras are closer, the case pose
  refinement is made for. Processing time is recorded too (Tayyab: total processing time matters).
- **Start → end:** 14:13 → 14:52 (copy / undistort / export 14:13 – 14:14; export 0.01, prior 3.61, init 1.72, train
  24.26, ply 0.56 min, total 30.4; evaluations 8 min, views 4 s). R-096: train 22.46, total 28.3.
- **Errors during the run:** none ("No module named 'triton'" is printed and caught, as in R-096).
- **Result:** `work_v9plo_sfm/gs_v9plo/splat.ply`, 521,417 splats. `eval_offpath.py` (held-out frames on their
  unrefined poses): PSNR 20.14 vs R-096 21.27, SSIM 0.853 vs 0.871, flatness 6.12 vs 6.57 cm, 0 blocked views (the raw
  score drops because refinement moves the training cameras, as in R-084). `eval_align.py` on the 63 common held-out
  frames: **aligned 23.96 vs 23.63, SSIM 0.8957 vs 0.8881**, pose correction median 1.25° / 0.089 units (R-096
  1.57° / 0.166). Per frame: median +0.77 dB, 35 frames > 0.5 dB better, 13 worse. Per stretch (R-096 → R-120):
  0 – 10 s 28.25 → 28.39, 10 – 30 s 25.33 → 26.12, 30 – 60 s 21.56 → 20.22, 60 – 90 s 23.47 → 24.94, 90 – 120 s
  30.36 → 30.30, 134 – 140 s 20.10 → 19.76, 160 – 170 s 25.12 → 24.74. Off-path ring (`offpath_views_r101/`): the
  same room-centre views. Bathroom doorway (`offpath_views_r101/door_125s.jpg`, rendered on the unrefined pose): still
  a smear. Run-to-run spread for comparison (R-088): aligned ±0.1 overall, up to ±0.9 per stretch.
- **Verdict:** kept: +0.33 dB aligned and better SSIM for +1.8 min of training; gains in 10 – 30 s and 60 – 90 s,
  not in the doorway stretch (134 – 140 s −0.34, featureless 30 – 60 s −1.3 on 4 frames). Refined poses are not
  exported (they stay in the checkpoint); the splats are in the world frame, so the viewer is unaffected.

### R-121 · 2026-11-22 · (numbered R-102 until 2026-11-23, D-096; script and log names keep `r102`) scan_009_057ed3beb4fc: second loop round with a pair check against R-096's path (`v9plg`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` (`loop_path.py --gate`, committed before the run)
- **Dataset:** R-096's cameras `work_v9pfy_sfm/sparse_loop2_pba`; R-097's pair directions (old + new pairs, model
  world) `work_v9pfy_sfm/loop_match2/pair_directions.json` (no new matching); `work_v9pfz` → `work_v9plg`
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r102.sh` (log `r102.log`): `loop_path.py … --model_frame --gate 10`
  → `sparse_loop4`; `prior_ba.py … --pair_priors sparse_loop4/loop_pairs.json` (settings as R-096) →
  `sparse_loop4_pba`; R-096's recipe with tag `v9plg` (no `--pose_opt`, so the change is the cameras only);
  `eval_align.py`, `offpath_views.py` with R-096
- **Goal:** plan step 3 (Tayyab, D-095). R-097 used the extra pairs without a check: four stretches better, 134 – 137 s
  broken (20.10 → 15.81). Here pairs that disagree with R-096's path by > 10° are left out before solving (the check
  is meant to be generic: PIPELINE_ANALYZER_PLAN §2.3).
- **Start → end:** 14:52 → 15:32 (loop solve 9 s, prior BA 1.3 min, copy / export 14:54; export 0.01, prior 3.21,
  init 1.78, train 22.91, ply 0.60 min, total 28.5; evaluation 10 min)
- **Errors during the run:** none.
- **Result:** pair check: 322 of 3,161 pairs > 10° off R-096's path left out (their frames mostly at 0 – 30 s and
  130 – 190 s). Held-out pairs >= 60 s: median 2.14 → 0.94°; cameras moved median 0.096, max 0.229 units; 26,497
  points (484 dropped). Model `work_v9plg_sfm/gs_v9plg/splat.ply`. `eval_align.py` (60 frames common to R-096,
  R-120, R-121; the export dropped 3 more held-out frames): R-096 23.58 / R-120 23.97 / **R-121 22.91**, SSIM 0.876,
  pose correction median 2.98°. Per stretch (R-096 / R-120 / R-121): 0 – 10 s 28.25 / 28.39 / 28.17, 10 – 30 s
  25.33 / 26.12 / 25.87, 30 – 60 s 21.38 / 20.00 / 23.13, 60 – 90 s 23.47 / 24.94 / 25.09, 90 – 120 s 30.36 /
  30.30 / 27.91, **134 – 140 s 20.10 / 19.76 / 15.83** (corrections up to 12°, as R-097's 15.81), 160 – 170 s
  24.82 / 24.60 / 23.20.
  **Why 134 – 140 s breaks** (R-097 and R-121 alike): the camera model has two holes, 112.2 → 115.6 s (one step of
  1.54 units) and **125.4 → 133.2 s (one step of 1.40 units)**. The keyframe selection picked 35 frames in the second
  hole (`work_v9pfz/frames.json`); none is in the camera model: predicted blur 12 – 42 px (5 – 7 px after 133.7 s),
  no ARCore pose (ARCore "lost" from 133.7 s). The second round moves 115 – 125 s by 0.19 – 0.28 units while 133 – 142 s
  moves 0.03 – 0.06; the two sides are joined only by the loose step across the hole. The bathroom doorway (125 s) is
  at the start of this hole: the bathroom interior is seen almost only in the unplaceable blurred frames.
- **Verdict:** rejected as a model. The gated pairs help where the path is continuous (30 – 90 s +1.6 – 1.8 dB) and
  break the stretch after the 125 – 133 s hole. Finding for the analyzer (PIPELINE_ANALYZER_PLAN): detect path holes
  (unplaced keyframes, blur, no ARCore pose) and keep a loop correction from moving one side of a hole against the
  other unless pairs tie both sides.
- **Correction (2026-11-25, frames inspected by the agent and confirmed by Tayyab):** the 125.4 – 133.2 s frames DO
  have ARCore poses (all 39 keyframes 125 – 133.5 s tracked; the earlier check read `arcore_pose`, which is empty
  exactly when ARCore tracks). They are not heavily blurred either: 125 – 129.6 s look from the room through the
  bathroom doorway into the bathroom (door header close to the lens, open door, wall with a pipe, toilet; 130 –
  1,300 ORB keypoints, predicted blur 9 – 29 px); 130.7 – 132.8 s show a ceiling cornice with a wall light and the
  door header (blur 19 – 43 px). Why they are unplaced is not known; likely: the bathroom is seen nowhere else in
  the walk (no pairs to the rest), the header close to the lens, some blur. Frames and notes:
  `dataset/scan_009_057ed3beb4fc/inspect_blurry_125-133s/`. Also corrected: 45 – 60 s is not one blank wall (see
  `inspect_blank_wall_45-60s/`): 45 – 49 s wooden panel / ceiling light (textured), 49 – 55 s smooth surface with a
  lamp, 55 – 60 s a plain wall with an LED cove strip above (0 – 50 keypoints, the truly featureless part).

### R-122 · 2026-11-23 · (numbered R-103 until 2026-11-23, D-096; script and log names keep `r103`) scan_009_057ed3beb4fc: R-120's recipe on all frames, for the viewer (`v9plq`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `docs/featureless-tracking-plan` @ 0179ca3
- **Dataset:** `work_v9pfz` → `work_v9plq`; R-096's cameras `work_v9pfy_sfm/sparse_loop2_pba` → `work_v9plq_sfm/sparse/0`
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r103.sh` (log `r103.log`): as `r099.sh` with tag `v9plq` and
  `--pose_opt`, no `--split`; `offpath_views.py` with R-096
- **Goal:** plan step 5 (Tayyab "you can resume", 2026-11-23, after the agent recommended it): the best recipe so far
  (R-120, +0.33 dB aligned over R-096) on every frame, as the model for the viewer (replaces R-099 / `scan-009-loops`
  if Tayyab agrees). No held-out score possible.
- **Start → end:** 19:01 → 19:35 (export 0.02, prior 4.05, init 1.78, init wait 0.33, train 25.95, ply 0.65 min, total
  32.8; views 4 s). Training 3.5 min longer than R-099 (22.16) on the same frames: `--pose_opt` cost.
- **Errors during the run:** none. Free disk on C: fell from 13 GB (after R-121) to 4.2 GB at the end; this run's
  folders are ~1.4 GB, the rest was not written by these runs (not investigated; Tayyab's other work on the PC?).
- **Result:** `work_v9plq_sfm/gs_v9plq/splat.ply`, 521,715 splats; off-path views `offpath_views_r103/`. In the
  viewer as `scan-009-poseopt` (`prototype/web-ui/public/splats/scan009_v9plq.spz`, 9.9 MB, local only).
- **Verdict:** kept as the scan_009 model to look at (R-120's +0.33 dB recipe); not yet inspected by Tayyab.

### R-123 · 2026-11-23 · scan_009_057ed3beb4fc: gated second loop round with path holes held, R-120's recipe (`v9plh`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/featureless-holes` (from `docs/featureless-tracking-plan` @ cf8fdaa; `loop_path.py` hole
  options committed before the run)
- **Dataset:** R-096's cameras `work_v9pfy_sfm/sparse_loop2_pba`, R-097's pair directions
  `work_v9pfy_sfm/loop_match2/pair_directions.json`; `work_v9pfz` → `work_v9plh`
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r123.sh` (log `r123.log`): `loop_path.py … --model_frame --gate 10
  --hole_dt 2.5` → `sparse_loop5` (a gap >= 2.5 s or a step >= 15 × the median is a hole; held at R-096's offset,
  sigma 0.01 units, unless >= 5 pairs tie the 10 s on each side; cross-hole pairs added to `loop_pairs.json`);
  `prior_ba.py … --pair_priors` (as R-121) → `sparse_loop5_pba`; R-120's recipe (`--pose_opt`) with `--split`;
  `eval_align.py`; `offpath_views.py` with R-120
- **Goal:** Tayyab chose "1 then 2" (2026-11-23): keep R-121's gains where the path is continuous (30 – 90 s +1.6 –
  1.8 dB) without breaking 134 – 140 s at the 126 – 133 s hole. Compared with R-120 (aligned 23.96 / 23.97 on the
  60 common frames). Hole detection is the first piece of the analyzer (PIPELINE_ANALYZER_PLAN §2.1).
- **Start → end:** 20:01 → 20:52 (loop solve 12 s, prior BA 1.8 min, copy / undistort / export 20:03 – 20:04; export
  0.01, prior 3.66, init 2.09, train 28.66, ply 0.62 min, total 35.1; evaluation 13 min, views 4 s). Training 4.4 min
  longer than R-120's (24.26) with the same recipe: not explained (the PC was also running R-124's analysis, CPU only).
- **Errors during the run:** none.
- **Result:** holes found on R-096's path (>= 2.5 s or >= 15 × median step): 12; 11 held (0 or 1 tying pairs),
  95.7 – 100.5 s free (11 pairs). Pair check as R-121 (322 of 3,161 out). Held-out pairs >= 60 s: 2.14 → 0.97°
  (R-121 0.94°); cameras moved median 0.084, max 0.207 units. Model `work_v9plh_sfm/gs_v9plh/splat.ply`.
  `eval_align.py`, 60 frames common to R-096 / R-120 / R-121 / R-123: 23.58 / 23.97 / 22.91 / **22.83**; R-123 vs
  R-120 per frame median −0.47 dB (11 better, 30 worse by > 0.5). Per stretch (R-096 / R-120 / R-121 / R-123):
  0 – 10 s 28.25 / 28.39 / 28.17 / 29.14, 10 – 30 s 25.33 / 26.12 / 25.87 / 26.31, 30 – 60 s 21.38 / 20.00 / 23.13 /
  20.09, 60 – 90 s 23.47 / 24.94 / 25.09 / 24.00, 90 – 120 s 30.36 / 30.30 / 27.91 / 28.59, **134 – 140 s 20.10 /
  19.76 / 15.83 / 15.52**, 160 – 170 s 24.82 / 24.60 / 23.20 / 25.76.
  Camera change vs R-096 (median per stretch): the loop solve moves cameras but does not rotate them (133 – 140 s:
  0.025 units, 0°); the prior BA after it rotates 133 – 150 s by 0.76 – 0.81° (R-121's BA: 0.88 – 0.90°), the
  other stretches by 0.11 – 0.60°.
- **Verdict:** rejected. Holding the holes does not stop 134 – 140 s from breaking, so R-121's explanation (the 125 –
  133 s hole lets one side shift) is wrong or incomplete; and the 30 – 90 s gains of R-121 came from moving across the
  holes at 47 – 58 s and 68 – 72 s. What R-097 / R-121 / R-123 share and R-096 / R-120 do not: the second round's
  pair directions (`loop_match2`) and their pair priors in the BA, which rotates 133 – 150 s by ~0.8°. Not yet tested
  which of the two breaks 134 – 140 s. The `--hole_dt` option stays (off by default).

### R-124 · 2026-11-23 · Analyzer, first part: window labels and route on the four test recordings (read-only, CPU)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC (CPU only, while R-123 trains)
- **Branch / commit:** `exp/featureless-holes` (new `src/arcore3dgs/analyze_recording.py`, committed with the result)
- **Dataset:** selections and camera models already on disk: newRoomAttemptSadness `work_v9e2e` / `work_v9e2e_sfm`
  (R-020); roomAttemptSadness2 `work_v9pgsr8` / `_sfm` (R-069); scan_3028a4de8fa0 `work_v10` / `work_v10inc_sfm`
  (R-068); scan_009 normal SfM `work_v9pgsr` / `_sfm` (R-045) and sensor path `work_v9pfz` / `work_v9plp_sfm` (R-096)
- **Command(s):** `python src/arcore3dgs/analyze_recording.py --selection <work> --model <sfm> --out
  <sfm>/analysis.json` per recording (defaults: 5 s windows, hole >= 2.5 s or >= 15 × median step, first thresholds
  set by hand)
- **Goal:** plan step 2 (Tayyab "do 1 then 2", 2026-11-23): do the labels and the suggested route match what we know
  of each recording (newRoom / bedroom textured, normal SfM fine; lecture hall: 581 / 842 placed by the incremental
  mapper; scan_009: normal SfM fails, featureless 45 – 60 s, hole 125 – 133 s)?
- **Start → end:** 2026-11-23 evening, < 10 s per recording (CPU, while R-123 trained).
- **Errors during the run:** first pass showed "ARCore tracked 0 %" everywhere: the script read `arcore_pose`, which
  select_sharp.py only sets to "lost" / "unsettled" for frames WITHOUT a pose. Fixed (tracked = `c2w_arcore` present);
  rerun.
- **Result:** `analysis.json` in each model folder. Letters per 5 s window (T textured, w weak, f featureless,
  _ hole):

  | Recording (model) | Placed | Obs / camera | ARCore | Holes >= 2.5 s | Windows | Route |
  |---|---|---|---|---|---|---|
  | newRoom (`v9e2e`) | 1165 / 1166 | 715 | 100 % | 0 | 44 T, 4 w | normal SfM |
  | bedroom roomAttemptSadness2 (`v9pgsr8`) | 1000 / 1042 | 906 | 100 % | 2 (9 s, 3 %) | 55 T, 1 f, 3 _ | normal SfM |
  | lecture hall scan_3028 (`v10inc`) | 572 / 842 | 335 | 100 % | 2 (60 s, 34 %) | 15 T, 9 w, 11 _ | sensor path |
  | scan_009 normal SfM (`v9pgsr`) | 87 / 238 | 56 | 100 % | 2 (144 s, 89 %) | 3 w, 1 f, 12 _ | sensor path |
  | scan_009 sensor path R-096 (`v9plp`) | 581 / 894 | 105 | 26 % | 8 (38 s, 20 %) | 10 T, 11 w, 7 f, 10 _ | sensor path |

  scan_009 (R-096) per window: `wTTTwTTTw_f_wf_Tfff_f__ww__TTfwww__Tww`: featureless / holes at 45 – 60 s, 65 – 110 s
  (mixed), 125 – 133 s (blur 17 – 22 px) and 165 – 175 s, matching R-091 / R-093 (45 – 60 s) and R-121 (125 – 133 s).
  The lecture hall's route matches R-066 – R-068 (GLOMAP collapsed, the incremental mapper left the right-side walk
  out). The bedroom's two short holes at ~235 s and ~270 s were not known before (not checked).
- **Verdict:** kept as the analyzer's first part: the labels and routes agree with what each recording is known to be.
  Thresholds are hand-set first guesses (obs 30 / 100, blur 15 px, placed 95 %, holes 5 %), not tuned; four
  recordings only. Next: use the labels in the pipeline (route choice, hole-aware loop step R-123, frame weights).

### R-125 · 2026-11-24 · scan_009_057ed3beb4fc: room-plane anchoring preview on R-120's model (no training)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/featureless-holes` (new `src/arcore3dgs/plane_snap.py`, committed with the result)
- **Dataset:** R-120's model `work_v9plo_sfm/gs_v9plo/splat.ply` (not changed); output
  `work_v9plo_sfm/gs_v9plo/splat_snap_r125.ply`
- **Command(s):** `nerfstudio-env/Scripts/python.exe src/arcore3dgs/plane_snap.py --ply …/splat.ply --out
  …/splat_snap_r125.ply` (defaults: normal within 15° of an axis, flat splats vote, peaks within 0.35 units merged as
  copies, band 0.3 units); `eval_align.py` (R-120's held-out frames), `offpath_views.py`, scratch `door_views.py`
- **Goal:** Tayyab (2026-11-24): "the room still has major imperfections, floating splats that are supposed to be on
  the wall / floor are detached from them; we need some technique to bring major changes". Preview of one shared
  plane per surface: does a model with single, thin walls look better off-path, and how much photo match does it
  cost? Decides whether to build the anchoring into training.
- **Start → end:** 2026-11-24, snap 8 s (two passes), evaluation 17:07 → 17:18, views 17:18.
- **Errors during the run:** first pass merged only peaks within 0.35 units and kept copies 0.4 – 0.6 units apart
  as separate planes (61 planes, e.g. walls at z = 3.94 and 4.36); its layer thickness used the 25th percentile of
  the smallest scales, which is ~0 for PGSR's flat splats (printed 0.0000). Fixed: copies are peaks within 0.9 units
  whose footprints overlap >= 30 %; thin scale = median smallest scale of flat splats, >= 1e-4. Rerun.
- **Result:** 521,417 splats, 400,564 flat; 104,496 (20.0 %) snapped onto 68 planes (`splat_snap_r125_planes.json`).
  Strongest planes and the layers merged into them: wall z = 4.36 (26,894 splats, copies at 3.94 / 4.12 / 3.58 /
  4.98, layer thickness before 0.31 units), x = 2.36 (copies 2.12 – 3.18, 0.51), z = 1.00 (0.30 – 1.88, 0.45),
  x = −2.78 / −1.84, z = −0.60 / −1.22, ceiling y = 2.15 (copies 1.37 – 2.71, 0.38). **Floor: two levels, y = −2.47
  and −1.91 (0.56 units apart), over different areas** (footprints do not overlap): a stepped floor, i.e. height
  drift between parts of the walk, not stacked copies. `eval_align.py` (63 frames): **aligned 20.32 vs R-120 23.96**,
  SSIM 0.826 vs 0.896. Views (`offpath_views_r125/`): plan slice shows the snapped walls as thin straight lines
  forming the room's rectangle around the walk; the thick soft wall layers (non-flat splats) are untouched; ring views
  show glittery / speckled walls (colours and opacities fitted for the old positions). In the viewer (local only):
  `scan-009-planesnap` and the unsnapped R-120 as `scan-009-r120` (`public/splats/scan009_r125snap.spz` 9.7 MB,
  `scan009_v9plo.spz` 9.9 MB).
- **Verdict:** preview only, not a model to keep. The room's planes are found from the model, and merging copies by
  footprint works; snapping after training breaks appearance (−3.6 dB) and misses the non-flat splats that make
  the thick walls. The anchoring has to act during training (colours re-fit, all splats near a plane pulled in),
  and the floor needs a one-floor rule (stepped floor = height drift).

### R-126 · 2026-11-24 · scan_009_057ed3beb4fc: R-120's recipe with room-plane anchoring during training (`v9pla`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/featureless-holes` (new `plane_anchor.py`, `geo_splatfacto.py --plane_anchor`; committed
  before the run)
- **Dataset:** R-096's cameras `work_v9pfy_sfm/sparse_loop2_pba`; `work_v9pfz` → `work_v9pla`
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r126.sh` (log `r126.log`): as `r101.sh` (R-120) with tag `v9pla` and
  `--train_args "--path_prune 0.1 --plane_anchor"` (defaults: from step 5,000, planes refitted every 500 steps, splats
  moved half-way onto their plane every 100 steps, copies within 0.9 units with >= 30 % footprint overlap merged,
  one floor / one ceiling within 0.8 units, camera height from `frames.json`); `eval_offpath.py`, `eval_align.py`,
  `offpath_views.py` with R-120
- **Goal:** Tayyab (2026-11-24): floating splats detached from the walls / floor need a technique that brings major
  change. R-125 showed the planes can be found from the model but snapping after training costs 3.6 dB; here the
  anchoring acts during training so colours (and cameras, `--pose_opt`) re-fit. Judged on off-path views, wall layer
  thickness and held-out aligned PSNR vs R-120 (23.96).
- **Before the run (2026-11-24):** synthetic test (two copies of a wall 0.4 apart, a floor, random splats): copy pulled
  to the wall (2.4 → 2.007 after 6 moves), tilted splats turned to the wall normal, floor unchanged, float32 / float64,
  CPU / GPU; quaternion round trip error 7e-16. Smoke test: 400 training steps with anchoring from step 200
  (`smoke_plane_anchor.log`): runs to the end, 6 planes and 4,480 of 23,511 splats moved at step 300; checkpoint
  removed afterwards. First smoke attempt crashed on the Windows console encoding (nerfstudio output piped without
  UTF-8; run_v8.py already sets PYTHONUTF8): not a code error.
- **Start → end:** 17:36 → 18:16 (export 0.01, prior 3.90, init 1.99, train 24.93, ply 0.56 min, total 31.5; evaluations
  8 min, views 4 s). R-120's training: 24.26 min, so anchoring costs ~0.7 min.
- **Errors during the run:** none. The plane-anchor lines go to `gs_v9pla/train.log` (not `r126.log`). One fit (step
  6,000) found 0 planes (not investigated); the next one found 22 again.
- **Result:** `work_v9pla_sfm/gs_v9pla/splat.ply`, 413,544 splats (R-120: 521,417). Anchoring (train.log): step
  5,000: 54 planes, 41 copies merged, 689,814 of 721,628 splats moved, mean distance before 0.208 units; from step
  6,500 on 21 – 23 planes, 2 – 7 copies merged per fit, ~405,000 of ~428,000 splats moved per fit with mean distance
  before 0.006 – 0.011 units (held flat). The horizontal planes creep up over the run (floor −1.92 → −1.81,
  ceiling 2.08 → 2.21; not investigated, likely the whole model moving with `--pose_opt`). `eval_offpath.py`: PSNR
  19.65, SSIM 0.847, **flatness 3.81 cm** (R-120 6.12), 0 blocked views. `eval_align.py` (63 frames): **22.07 vs
  R-120 23.96**, SSIM 0.868 vs 0.896; per stretch (R-120 → R-126): 0 – 30 s 26.46 → 25.24, 30 – 90 s 23.89 → 21.82,
  90 – 134 s 30.30 → 29.39, 134 – 140 s 19.76 → 15.87, 140 – 200 s 24.15 → 24.50. Views (`offpath_views_r126/`):
  plan slice shows the walls as straight lines forming the room's rectangle (R-120: thick scattered bands), but
  large soft splats still sit on some wall lines; room-centre depth smoother. In the viewer as `scan-009-planes`
  (`public/splats/scan009_v9pla.spz`, 7.3 MB, local only).
- **Verdict:** inconclusive: the geometry is clearly more regular (flatness −38 %, straight walls), the photo match
  is 1.9 dB worse and 134 – 140 s breaks as in R-121 / R-123. The anchoring is too broad (~95 % of splats moved:
  the reach includes merged copies up to 0.9 units away, so objects near walls are pulled in too). Next if kept:
  narrower reach after the first merge, move only flat or wall-facing splats, smaller step. Tayyab to look.

### R-127 · 2026-11-25 · scan_009_057ed3beb4fc: ARCore-tracked keyframes placed in the holes of R-096's camera path, R-120's recipe (`v9plb`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/featureless-holes` (new `src/arcore3dgs/arcore_fill.py`, committed with the result)
- **Dataset:** R-096's cameras `work_v9pfy_sfm/sparse_loop2_pba`, selection `work_v9pfz/frames.json`, database
  `work_v9pfm_sfm/database.db` (read only); `work_v9pfz` → `work_v9plb`
- **Command(s):** `python src/arcore3dgs/arcore_fill.py …/sparse_loop2_pba …/work_v9pfz …/sparse_loop2_arc --database
  …/work_v9pfm_sfm/database.db` (holes >= 2.5 s; local Sim3 ARCore → model on tracked placed frames within 10 s on each
  side, >= 3 per side; accepted if rotation residual <= 5° and cross-side prediction <= 0.3 units; new frames with a
  median Sampson error > 4 px over their verified pairs dropped); then `dataset/scan_009_057ed3beb4fc/r127.sh`:
  R-120's recipe (`--pose_opt`, `--split`) on the filled model; `eval_align.py`, `offpath_views.py`, doorway views
- **Goal:** Tayyab "complete these" (2026-11-25), item 1: the bathroom doorway frames (125 – 133 s) are tracked by
  ARCore and textured but unplaced (R-121 correction); give the doorway real content. Compared with R-120.
- **Camera fill before training (2026-11-25):**
  1. `arcore_fill.py` (as in the command above): **rejected by its own checks**. ARCore's rotations agree with the
     model (relative rotation 0.80° median with the OpenGL→OpenCV flip), its positions do not: an ARCore jump of
     3.48 m in 0.11 s at 127.53 → 127.64 s (relocalisation), 1.3 – 2 m/s of motion logged at 114 – 120 s, scale
     0.27 – 0.29 model units per ARCore metre, centre residual 0.52 units on 42 frames before the hole; the one segment
     that fitted (130.7 – 132.7 s) failed the image check (Sampson 6 – 27 px, 10 of 11 dropped). First version also
     fitted the world rotation from the centres (174° residual): fixed (rotation from the orientations), and split
     at ARCore jumps / tracking gaps.
  2. New `direction_fill.py`: gyro rotations (`gyro_check.fill_rotations`; gyro check on the model: 0.32° pair error
     median) + directions of the verified pairs (1,201 touching hole frames) → centres by least squares, placed
     frames fixed; a frame is added with >= 2 pairs to placed frames and Sampson median <= 4 px. Result
     (`work_v9pfy_sfm/sparse_loop2_dir`, 44 s): **29 of 152 unplaced frames in 8 holes added**: 68.4 – 71.7 s (16),
     131.2 – 132.7 s (7, the top of the doorway), 48.2, 49.3, 97.4, 98.2, 98.9, 109.5, 115.3 s. Not placed: the
     bathroom interior frames 126.2 – 129.6 s (0 – 1 pairs to placed frames, Sampson 7 – 20 px: they match only each
     other, the bathroom is seen nowhere else) and the featureless frames (50 – 51, 55 – 58, 99 – 100, 107, 167 – 168 s:
     no usable pairs). Added frames moved up to 2.1 units from the straight interpolation across their hole (97 – 99 s).
  Training therefore uses `sparse_loop2_dir` (600 + 29 frames): `r127.sh` = `r101.sh` with tag `v9plb` and that model.
- **Start → end:** 18:37 → 19:23 (export 0.02, prior 4.22, init 1.54, train 26.46, ply 0.61 min, total 33.4; evaluation
  12 min). The export's jump filter (> 30 cm from temporal neighbours) dropped 28 frames (R-096: 19): 10 of the 29
  added (the single frames at 48.2, 49.3, 68.4, 71.7, 97.4, 98.2, 98.9, 109.5, 115.3, 131.2 s); kept 19 (68.5 – 71.3 s
  and 131.7 – 132.7 s); 601 frames exported, 538 train / 63 held out.
- **Errors during the run:** none.
- **Result:** `work_v9plb_sfm/gs_v9plb/splat.ply`, 532,713 splats. `eval_align.py`, the same 63 held-out frames:
  **23.22 vs R-120 23.96**, SSIM 0.891 vs 0.896; per frame median −0.37 dB (8 better, 26 worse by > 0.5). Per
  stretch (R-120 → R-127): 0 – 30 s 26.46 → 26.31, 30 – 60 s 20.22 → 21.34, 60 – 90 s 24.94 → 23.83, 90 – 134 s 30.30
  → 29.71, 134 – 140 s 19.76 → 17.70, 140 – 200 s 24.15 → 24.11. Flatness 6.01 cm (R-120 6.12).
- **Verdict:** rejected. The added frames pass the epipolar (Sampson) check but conflict in training: that check
  cannot see a wrong distance along the line of sight, and their centres moved up to ~1 unit from the interpolated
  path. The bathroom interior frames (126 – 129.6 s) could not be placed at all (they match only each other).
  `direction_fill.py` / `arcore_fill.py` kept as tools; R-128 / R-129 build on R-120's cameras instead.

### R-128 · 2026-11-25 · scan_009_057ed3beb4fc: R-120 plus extra video frames in weak windows (`v9pld`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/featureless-holes` @ 72f10fb (`densify_frames.py`)
- **Dataset:** R-096's cameras `work_v9pfy_sfm/sparse_loop2_pba`; `work_v9pfz` → `work_v9pld` (extra frames extracted
  from `dataset.mp4` into its `images/` and `frames.json`); windows from `work_v9plp_sfm/analysis.json` (R-124)
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r128.sh` (log `r128.log`): `densify_frames.py` (1 extra video frame
  between consecutive placed keyframes <= 0.5 s apart in windows labelled weak / featureless, at most 300; rotation
  from the gyro, position interpolated) → `sparse_loop2_dense`; R-120's recipe with `--split`; `eval_align.py`,
  `offpath_views.py` with R-120
- **Goal:** Tayyab "complete these", item 2: keyframe selection keeps 1 of 6 video frames; in fast pans the dropped
  frames carry coverage. Measure quality and the added processing time vs R-120 (23.96, 30.4 min).
- **Before the run:** `--blur_learn` smoke test (300 steps, R-120's data, `smoke_blur_learn.log`): runs, the
  per-frame parameters (518 × 7) are saved with their optimizer, 27 frames updated; checkpoint removed.
- **Start → end:** 19:25 → 20:08 (densify 54 s: 266 frames in 18 windows, gyro check 0.32° pair error; export
  0.01, prior 5.74, init 2.73, train 25.07, ply 0.48 min, total 34.0; evaluation 8 min). R-120: prior 3.61, init
  1.72, train 24.26, total 30.4. Exported 850 frames (16 dropped by the jump filter), 787 train / 63 held out.
- **Errors during the run:** none.
- **Result:** `work_v9pld_sfm/gs_v9pld/splat.ply`. `eval_align.py`, the same 63 held-out frames: **24.25 vs R-120
  23.96**, SSIM 0.898 vs 0.896, pose correction median 0.95° / 0.082 units; per frame median +0.34 dB (28 better, 22
  worse by > 0.5). Per stretch (R-120 → R-128): 0 – 30 s 26.46 → 27.39, 30 – 60 s 20.22 → 24.92, 60 – 90 s 24.94 →
  25.16, 90 – 134 s 30.30 → 28.50, 134 – 140 s 19.76 → 18.29, 140 – 200 s 24.15 → 24.62. Off-path views
  `offpath_views_r128/`.
- **Verdict:** kept: the best held-out score so far, the gain where frames were added (featureless 30 – 60 s), for
  +3.6 min (more depth priors and init points, training time nearly unchanged). 134 – 140 s still the weak spot.

### R-129 · 2026-11-25 · scan_009_057ed3beb4fc: R-128 plus learnable blur motion (`v9plk`)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/featureless-holes` @ 72f10fb (`geo_splatfacto.py --blur_learn`)
- **Dataset:** R-128's densified selection (`work_v9pld` → `work_v9plk`) and cameras (`sparse_loop2_dense`)
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r129.sh` (log `r129.log`): R-128's run with `--train_args
  "--path_prune 0.1 --blur_learn"` (per frame: log-scale on the gyro blur motion + rotation / translation velocity
  offsets, from 0, Adam lr 1e-3, L2 0.01); `eval_align.py`, `offpath_views.py` with R-128
- **Goal:** Tayyab "complete these", item 3: the gyro blur estimate is often off (100 % crops, 2026-11-25); learn it.
  Compared with R-128 (24.25).
- **Start → end:**
- **Errors during the run:**
- **Result:**
- **Verdict:**

### R-130 · 2026-11-25 · scan_009_057ed3beb4fc: Depth Anything 3 feasibility, same checks as R-093 (no training)

- **Who / machine:** Tayyab (agent) · RTX 3070 PC
- **Branch / commit:** `exp/featureless-holes` @ 72f10fb (`vggt_chunk.py --da3`, `da3_loader.py`; D-097)
- **Dataset:** as R-093: frames / priors `work_v9pfu_sfm`, SfM reference `work_v9pfy_sfm/sparse_vt_pba_adapt`, gyro
  bias `gyro_loop_bias.json`, calibration `work_v9pfz_sfm`; model `depth-anything/DA3-LARGE` (1,643,843,860 bytes,
  sha256 eaf2ae06…e421, verified; CC BY-NC 4.0) in `C:/Users/tyb/.cache/buildscan/da3_weights/`
- **Command(s):** `dataset/scan_009_057ed3beb4fc/r130.sh` (log `r130.log`): `vggt_chunk.py … --da3 <weights>` on
  (1) 32 keyframes 42 – 63 s (R-093's chunk), (2) video frames every 0.5 s 44 – 60 s, (3) video frames every 0.25 s
  124 – 134 s (bathroom doorway), (4) 32 keyframes 15 – 30 s (textured control)
- **Goal:** Tayyab "complete these", item 4: do DA3's rotations follow the gyro where VGGT's did not (blank wall,
  R-093: 3.5 – 10°, max 92°), and is its depth more consistent across frames than the Metric3D priors (R-093: VGGT
  2.5 – 5.3 % vs Metric3D 15.1 %)?
- **Setup (2026-11-25, D-097):** package from the PyPI wheel unpacked to `…/buildscan/da3`; einops, addict, omegaconf +
  antlr4 4.9.3, safetensors, huggingface_hub 0.25.2 (the newest needs `httpx2`) to `…/buildscan/da3_deps`; moviepy,
  pycolmap, evo replaced by empty stand-ins (export helpers only). Weights: first download stopped at 1.26 GB with a
  consistency error while the disk was being written by R-129; second download complete and checksum-verified.
- **Start → end:**
- **Errors during the run:**
- **Result:**
- **Verdict:**
