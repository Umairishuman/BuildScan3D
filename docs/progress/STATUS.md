# BuildScan3D: Project Status

Last updated: 2026-11-28 afternoon by Tayyab (agent): usability (docs/HCI.md) and security (docs/SECURITY.md, D-100, OD-20) pass on web viewer and app, branch `feature/ux-security`; `SEMANTICS=0` in run_full.sh; R-146 resumed. Before that: 2026-11-28 by Tayyab (agent, night; Umair and Zaid away until 2026-11-30): FINAL_PLAN.md to the 2026-12-06 submission; R-134 – R-136 automatic pipeline test bench (bedroom kept, scan_009 inconclusive, tape room kept: 25.33 dB aligned, -1.86 %), layout fallback (R-137), `.spz` quality tool (R-139 queued), `sensor_path.py --track_dirs` (R-140 queued), ARCore vs our cameras (R-141), final report draft in `report/final-eval/`. Before that: 2026-11-27 by Tayyab (agent, night): R-131 – R-133 (Apache DA3 depth priors, R-133 = best score with commercial-use models, D-098), viewer lag fixed (`fix/viewer-perf`), automatic pipeline `--auto` (D-099, `feature/auto-pipeline`, test bench R-134 on). Before that: 2026-11-25 by Tayyab (agent, `exp/featureless-holes`): R-123 – R-130 (best scan_009 model now R-128, denser frames in weak windows, 24.25 dB), analyzer (R-124), plane anchoring (R-125 / R-126), hole filling (R-127, rejected), learnable blur (R-129), Depth Anything 3 test (R-130); records corrected (R-121). Before that: 2026-11-23 (merge of `master`) and 2026-11-22 by Tayyab (agent, night on `docs/featureless-tracking-plan`): §11.d loop closure (R-096, +0.96 dB, first clear gain), R-097 (rejected), R-098 (inconclusive), R-099 (all frames, viewer), `loop_path.py`, `loop_match.py`, `prior_consistency.py`, `offpath_views.py`, `prior_ba.py --pair_priors`. Before that: 2026-11-20 by Tayyab (agent, on `docs/featureless-tracking-plan`): R-082 (§10.a held-out baseline, 20.80 dB), R-083 (§10.f gyro blur, inconclusive), R-084 (§10.d pose refinement, rejected), `eval_align.py`, R-085 (§10.c track loop, rejected); 2026-11-21: disk cleanup, R-086 – R-088 (10.e part 1, 10.b-1, noise repeat), `--path_prune` with R-089 / R-090, R-091 (10.b-2, rejected), R-092 (`--fill_scale`), §11 plan, D-081 + R-093 (VGGT test), R-094 (scale drift), R-095 (plane priors, rejected); before that, code for featureless §10.a – 10.f (rolling shutter, track loop, still frames, pose refinement, gyro blur; not trained); earlier the same day: video point tracks and adaptive priors, runs R-073 – R-081, `scan-009-tracks` in the viewer, featureless plan §10. Before that: 2026-11-19 by Tayyab (agent, on `docs/featureless-tracking-plan`): `master` merged in, clashing IDs renumbered (R-071, R-072, D-080, OD-14, OD-15), featureless plan §9. Night before: scan_009 runs R-052, R-071, R-072, `prior_ba.py`, `gyro_loop_bias.py`, loop-closed `scan-009-loop` in the viewer. Before that: 2026-11-18 by Tayyab (agent, night on `docs/featureless-tracking-plan`): scan_009 runs R-048 – R-051, IMU scale / gyro tools, `scan-009-gyro` in the viewer. Earlier: featureless tracking plan, D-080 (option 1 then continue), `gyro_check.py` / `--gyro_thr`, `gap_test.py`, R-047, app low-texture prompts. Before that: 2026-11-15 by Tayyab (agent, on `exp/overnight-2026-11-14`): scan_009 runs R-045 / R-046, `--pose_free` keyframes, layout no-floor fix, app feature-point map + coverage dots per frame + depth/pose pairing, 7 real models in the web viewer. Before that: 2026-11-14 by Tayyab (agent, overnight session on `exp/overnight-2026-11-14`): roomAttemptSadness2 v9 run (R-069), newRoom technique tests (R-070 – R-043), layout ceiling fix, server v9 option, tape script, capture checks in the app and on the PC, coverage 45%. Before that: 2026-11-13 by Tayyab (agent): merged `origin/master` into `exp/fast-pipeline`; speed-up runs R-062 – R-068 (renumbered from R-029 – R-065 at the merge), mini-room diagnosis, OD-10, OD-11, new 7.2 items. Before that: 2026-11-12 by Umair (recordings table in §2 "Which recording is which"; NFR1 re-measured on scan #3, NFR2 timing in the app, 1.7 closed D-067, update prompts + changelog D-068, readable `buildscan watch`, quality banner only at the top; earlier the same day: D-062 – D-066). Merged with `master` the same day; before that: 2026-11-19 by Umair (merged with `master`: Tayyab's records to 2026-11-15, his runs renumbered R-062 – R-070, D-079; R-058 scan #6 OOM in SfM, R-059 rerun running; issues #31 – #38 for the next steps; feature/vercel-deploy pushed; R-057: D-075 defaults on four rooms; R-058 scan #6 running; D-076 online site on Vercel + R2, issues #26 – #30, code on `feature/vercel-deploy`; earlier D-075: Step 4 options on in run_full.sh, older web bundles moved to prototype/web-ui/scans_archive/; before that Step 4 issues #8 – #25, runs R-053 – R-056)
Before that on `master`: 2026-11-23 by Umair (agent, `feature/run-times`: runs.tsv + `scripts/run_times.py`, D-090; `feature/step4-triage`: R-059 written up, scan #6 fixture sheet R-103, wall roughness R-104, `CHECKS_FOR_UMAIR.md` with every Step 4 check only Umair can do; R-061 / R-101 speed work on `exp/colmap-cudss`). Before that: 2026-11-19 by Umair (merged with `master`: Tayyab's records to 2026-11-15, his runs renumbered R-062 – R-070, D-079; R-058 scan #6 OOM in SfM, R-059 rerun running; issues #31 – #38 for the next steps; feature/vercel-deploy pushed; R-057: D-075 defaults on four rooms; R-058 scan #6 running; D-076 online site on Vercel + R2, issues #26 – #30, code on `feature/vercel-deploy`; earlier D-075: Step 4 options on in run_full.sh, older web bundles moved to prototype/web-ui/scans_archive/; before that Step 4 issues #8 – #25, runs R-053 – R-056)
Before that on `master`: 2026-11-15 by Tayyab (agent, on `exp/overnight-2026-11-14`): scan_009 runs R-045 / R-046, `--pose_free` keyframes, layout no-floor fix, app feature-point map + coverage dots per frame + depth/pose pairing, 7 real models in the web viewer. Before that: 2026-11-14 by Tayyab (agent, overnight session on `exp/overnight-2026-11-14`): roomAttemptSadness2 v9 run (R-069), newRoom technique tests (R-070 – R-043), layout ceiling fix, server v9 option, tape script, capture checks in the app and on the PC, coverage 45%. Before that: 2026-11-13 by Tayyab (agent): merged `origin/master` into `exp/fast-pipeline`; speed-up runs R-062 – R-068 (renumbered from R-029 – R-065 at the merge), mini-room diagnosis, OD-10, OD-11, new 7.2 items. Before that: 2026-11-12 by Umair (recordings table in §2 "Which recording is which"; NFR1 re-measured on scan #3, NFR2 timing in the app, 1.7 closed D-067, update prompts + changelog D-068, readable `buildscan watch`, quality banner only at the top; earlier the same day: D-062 – D-066).


This file is the single place for **where the project stands: what is done and what is left**. It absorbed the old
`TODO.md` on 2026-11-06 (archived unchanged in [archive/TODO.md](archive/TODO.md)); every open item from it is in
section 7, every finished one in section 8. How to keep this file up to date: [CLAUDE.md](../../CLAUDE.md).

| Other record | What it holds |
|---|---|
| [MAP.md](../../MAP.md) | What is where and what every file does (read first) |
| [DECISIONS.md](DECISIONS.md) | Every decision: what, why, evidence, alternatives rejected, who |
| [LOG.md](LOG.md) | Dated project log: what was done on each day, by whom |
| [TRAINING.md](TRAINING.md) | One entry per processing / training run: command, machine, errors hit, result |
| [Problems_and_Solutions.md](Problems_and_Solutions.md) | Full technical evidence (symptom → root cause → fix → numbers), cited as P&S §x |
| [Research_Notes_2026-10-24.md](Research_Notes_2026-10-24.md) | Literature behind the v8/v9 ideas (DashGaussian, PGSR, PlanarGS, LIMAP, ...) |
| [prototype/web-ui/STATUS.md](../../prototype/web-ui/STATUS.md) | Web viewer / dashboard build status and its own known issues |
| [docs/CI_CD.md](../CI_CD.md), [docs/PROCESSING_GUIDE.md](../PROCESSING_GUIDE.md), [docs/Flow.md](../Flow.md) | CI/CD, phone-upload server, system flow |

---

## 1. Summary

- **Goal (proposal v4):** turn a phone video of a built room into a metric, measurable 3D Gaussian Splatting model,
  delivered to a browser, with semantic labels. Commodity Android phone (realme RMX5111), no LiDAR.
- **Biggest change of plan:** ARCore poses are not good enough for 3DGS (silent re-anchor of ~1 m / 28°, no lens
  distortion). Poses now come from COLMAP SfM with lens self-calibration; ARCore gives metric scale, gravity, live
  guidance and a tracking fallback (P&S §4.11, DECISIONS D-014).
- **Where we are:** a full v9/v10 command-line pipeline works on one room (newRoomAttemptSadness): metric 3DGS,
  room layout, semantic labels (walls / floor / ceiling + 15 fixtures), mesh, and a web viewer with scan layers.
  It takes ~96 min + ~40 min semantics on the RTX 3070, has only been tested on one room, and runs only on the
  Windows RTX 3070 PC. The phone-upload server and RunPod still run the older v3 recipe.
- **FYP-1 mid evaluation:** submitted (material in [report/mid-eval/](../../report/mid-eval/)).
- **Current focus (Umair):** set up this Ubuntu PC (7.1 step 1), then rebuild the Docker image from the same setup
  script (step 2), then **semantic labelling**. What each file does: [MAP.md](../../MAP.md).

## 2. Best model and results

`saved_models/2026-10-27_v9_semantic_pgsr/newRoomAttemptSadness/` (see its `README.txt`). `saved_models/` is
gitignored and lives on the RTX 3070 PC only.

| Item | Value |
|---|---|
| Capture | newRoomAttemptSadness, realme RMX5111, ARCore app, slow walk (240 s) |
| Model | 605,481 Gaussians, metric, +Y up; `splat.ply` 150 MB, `splat.spz` 11.6 MB |
| Recipe | v9 pipeline + PGSR-lite, trained on all 1165 frames, 15k steps, 46 min |
| Labels | `semantic_v10/` (newest), `semantic/` (v9) |
| Mesh, layout | `mesh/` (TSDF, shell denoised, `.glb` for the web), `layout/` |
| Web demo | `prototype/web-ui/public/scans/newroom/`, page `/viewer/newroom-scan` |

`saved_models/2026-10-26_v9_e2e/` is the same recipe with 79 frames held out, used for the numbers below.
`saved_models/2026-10-24_v8_geofast15` has a training bug (priors on the wrong images, P&S §4.17); don't use it.
Older saved models: `2026-10-11_sfm_v3/` (v3, tape-validated scale), `2026-10-12_sharp_mvs_v6/` (v6, mid-report headline).

| Goal | Result | Verdict |
|---|---|---|
| Image quality (79 held-out frames) | PSNR 25.16, SSIM 0.825, sharpness 0.80 (PGSR-lite: 0.88) | Best so far; the hardest off-path view is complete for the first time |
| Processing time | 96 min end to end on the RTX 3070 (SfM 22, priors 8, init 20, training 43) | Was ~4 h (v6); proposal goal (< 15 min on a 4090) and FYP-2 target (< 35 min on a 4090, a projection) not reached |
| Metric scale | Room length 6.60 m (tape 6.70 m), −1.5% | Open: the Sim3-to-ARCore scale varies between SfM runs. v3 was −0.12% (table below) |
| Flat walls | Off-path flatness 0.77 cm; mesh walls 0.03–0.78 cm after shell denoising | Good; wall 3 and the ceiling stay rough (ceiling seen only at grazing angles) |
| Room measurements | 4 walls with gross / opening / net areas, floor 28.8 m², ceiling 2.73 m | Works on one room |
| Fixtures (v10) | 15/15 detections correct, 15/17 visible fixtures found | Tuned and scored on the same room: not a general accuracy figure |

v10 still misses the socket under the ironing table and one round light (taken by the "clock" decoy). The three new
v10 detections (`door_1`, `door_6`, `tube_light_1`) still need the user's confirmation.

**Tape measure vs model (v3 model, viewer measure tool, 2026-10-11):** table 0.458/0.459 m (−1 mm), chair 0.361/0.368
(−7 mm, soft edge), rug 0.858/0.870 (−12 mm, soft edge), table long side 1.748/1.750 (−2 mm), wall 2.792/2.800
(−8 mm), room 6.692/6.700 (−8 mm). Rigid objects: mean 4.8 mm / 0.19%, worst 0.29%. The error does not grow with
length; the small negative offset is most likely where the clicks land.

**Mid-report headline numbers (v3 → v6, 42 frames no model trained on):** v3 26.04 dB / 0.8756, v4_sharp 26.30 /
0.8849, v5 26.51 / 0.8879, **v6 26.52 / 0.8886**. Second room (roomAttemptSadness2, v3): SSIM 0.91, 1% badly placed
surfaces. Splatfacto vs our own trainer (roomAttemptSadness2): held-out 27.81 vs 24.70 dB.

### Which recording is which

Recordings on this PC are numbered in the order they arrived (D-065); "scan #3" in the records means the row below.
Older recordings (before numbering) are on the RTX 3070 PC and keep their names. Room names and numbers that are
"to fill in" were not recorded; whoever knows them, please add them.

| Name in the records | Folder | Recorded | By, phone, app | Place | Length | Runs |
|---|---|---|---|---|---|---|
| **scan #1** | `dataset/scan_001_056fe94d3399` | 2026-11-06 | Umair, Infinix X6833B, app ≤ v0.3.4 | Umair's first Linux test (LOG 2026-11-06: "Umair's room"; the layout found only 1 wall, like a corridor end, plan 4.10); room to fill in | 46 s | R-028 (stopped), R-029 |
| **scan #2** | `dataset/scan_002_646070948603` | 2026-11-06 | Umair, Infinix X6833B, app ≤ v0.3.4 | Computer lab: desks, red chairs, glass partition; room number to fill in | 97 s | R-030 (ceiling 1.50 m, wrong) |
| **scan #3** | `dataset/scan_003_6de634cbb8b2` | 2026-11-12 (uploaded 14:53 over USB) | Umair, Infinix X6833B, **v0.3.6** | Classroom: rows of wooden desks with red seats, projector screen, wooden door, blue curtains, ceiling AC units; room number to fill in | 185 s | R-031 (2.74 m, kept; `saved_models/2026-11-12_r1112_scan003/`) |
| scan #4 | (number 4 = `newRoomAttemptSadness`, registered when it was copied here, `dataset/.scan_numbers.tsv`) | | | | | |
| **scan #5** | `dataset/scan_005_4aadb16181d9` | on this PC 2026-11-16 (folder 12:05) | Umair, Infinix X6833B | room to fill in | 352.5 s | not processed yet (planned as R-060, `--window 9`; GPU slot needed) |
| **scan #6** | `dataset/scan_006_1e457a214ce1` | on this PC 2026-11-16 (folder 12:06) | Umair, Infinix X6833B | room to fill in (L-shaped, 7 walls) | 259.8 s | R-058 (OOM in SfM); **R-059** `r1119b6` (kept: 3.05 m, closed, 11 fixtures; check sheet R-103); R-061 / R-101 GPU-COLMAP copies (speed tests) |
| **scan #7** | `dataset/scan_007_e6d4f090f88e` | on this PC 2026-11-16 (folder 12:06) | Umair, Infinix X6833B | room to fill in | 269.2 s | R-040 (finished 2026-11-18; 0 fixtures); a building under construction (no roof); R-057 `r1119c`: 4 walls, closed, 17.99 m² |
| **scan #8** | `dataset/scan_008_7b486c855ed6` | on this PC 2026-11-16 (folder 12:27) | Umair, Infinix X6833B | room to fill in | 366.5 s | R-038 (OOM in SfM), R-039 (window 9, finished, 11 fixtures); R-057 `r1119c`: 4 walls, closed, 26.44 m² (corner furniture dropped, Umair) |
| newRoomAttemptSadness | 3070 PC; **this PC since 2026-11-12** (raw recording only): `dataset/newRoomAttemptSadness` | by 2026-10-10 (first run R-007) | realme RMX5111; who recorded it not written down | Room of the best model (R-023) and semantics v10 | 240 s | R-007 … R-025; here R-037 |
| roomAttemptSadness2 | 3070 PC | by 2026-10-09 (first run R-002) | realme RMX5111; who recorded it not written down | Second room of the mid report | not recorded here | R-002, R-004, R-010 |

## 3. Module status

| Module | State | Where | Notes |
|---|---|---|---|
| Android capture app | Working, used for all recordings | `googleARCore/samples/hello_ar_java` | ARCore video + poses + IMU + depth + IQA + coverage overlay + upload UI + in-app update checker. Predicted-blur IQA. Not tuned on device; no unit tests |
| Capture checks | Done | `check_capture.py` | Files, sync, tracking, dropped frames, predicted blur, exposure, re-anchor events |
| IMU featureless-tracking fallback (novelty) | Done, validated on simulated gaps | `imu.py`, `fallback.py`, `relocalize_pnp.py` | In `run_arcore3dgs.bat` and the server pipeline; **not used by `run_v8.py`** (v9) |
| Poses (SfM) | Done | `sfm_colmap.py` | COLMAP 4.2, ARCore-guided pairs + `--retrieval 20`, lens self-calibration, Sim3 to ARCore. Scale not stable between runs |
| Dense init | Done | `fast_mvs.py` (v9), `mvs_init.py` (v6) | 19 min fast PatchMatch vs 2 h 15 min full |
| Priors | Done | `mono_prior.py`, `plane_seg.py`, `blur_motion.py` | Metric3D depth/normals aligned to SfM points, planar masks, motion-blur model |
| 3DGS training | Done | `geo_splatfacto.py` (splatfacto subclass) | DashGaussian schedule, priors, planar, blur, PGSR-lite, checkpoints + resume. `train.py` (own trainer) kept for experiments |
| End-to-end driver | Done | `run_v8.py` | Times every stage; v9 flags in section 5 |
| Evaluation tools | Done | `eval_offpath.py`, `fair_compare.py`, `compare_models.py`, `fit_diag.py`, `diagnose.py` | Off-path split, pose-refined comparison, flatness metric |
| Room layout | Done; needs a levelled model (D-071) | `layout.py` (v9), `structure.py` (older) | Walls (any number), floor, ceiling, corners, dimensions, `plan.png` |
| Semantic labelling | v10 done on one room | `semantic2d.py`, `semantic3d.py`, `verify_fixtures.py` | Grounding DINO + SAM + decoys, 3D votes + class geometry rules, CLIP crop check. Needs room 2. **Umair's next focus** |
| Mesh | Done | `mesh.py`, `mesh_labels.py` | TSDF of rendered depth, PGSR unbiased depth, shell denoising, labelled `.glb` |
| Web viewer / dashboard | Working with a real scan | `prototype/web-ui` | Spark splat rendering, `.spz`, Scan Layers panel, mesh mode, measure tool. Many dashboard screens are mock data (see its STATUS) |
| Web export | Done | `export_web.py`, `to_spz.mjs` | 6 label groups as `.spz` + `scan.json` + mesh |
| Compression (`.ksplat`) | Experiments on an unmerged branch | `origin/feat/splat-compress` (Zaid) | v1 88% smaller, v2-A 73% smaller and visually lossless. The web viewer uses `.spz` instead (open decision, DECISIONS) |
| Phone-upload server | Works, but runs the old v3 recipe | `server/` | FastAPI, modes local / runpod / remote / dry_run, job manager `scripts/jobs.bat`. Windows paths hard-coded |
| RunPod cloud processing | Integrated, unreliable | `server/runpod_client.py`, `docker/Dockerfile.gpu` | User reports it does not work well; no end-to-end test recorded. Image out of date (section 6) |
| CI/CD | Working | `.github/workflows/` | Lint + tests (CPU only), web build, APK build/sign/check, releases, Docker image build |
| Reports | FYP-1 mid submitted | `report/mid-eval/` | FYP-2 / final report not started |

## 4. Proposal (v4) requirements against the current state

The proposal is `docs/proposal/BuildScan3D_FYP_Proposal_v4.docx`. Several parts were changed on purpose
(DECISIONS D-033); this table shows where each requirement stands.

| Req | Proposal | Now |
|---|---|---|
| FR1 telemetry | 1080p video + 6-DoF ARCore anchors + IMU | Done (video, poses, IMU in the MP4, anchors, camera metadata, depth) |
| FR2 live IQA | Laplacian + lux, on-screen guidance | Done, upgraded to predicted blur from motion × exposure; thresholds not tuned on device |
| FR3 async upload | Background upload to object storage | Upload to our FastAPI server (multipart). No object storage (R2) |
| FR4 job queue | Redis queue, Node/Express, Docker GPU workers | Not as proposed: FastAPI with threads and subprocesses. No Redis / Node |
| FR5 spatial anchoring | ARCore + COLMAP fusion | Done (COLMAP SfM + Sim3 to ARCore); scale not stable between runs |
| FR6 3DGS | GPU worker trains 3DGS | Done locally; cloud path runs only the v3 recipe |
| FR7 semantics | 2D CNN materials (drywall, wiring) → 3D | Changed: walls / floor / ceiling + fixtures (doors, windows, switches, sockets, lights) with Grounding DINO + SAM; MEP / material segmentation dropped (D-033) |
| FR8 pruning + compression | `.ksplat`, ≥ 60% smaller | `.spz` in the viewer (148 → 12.5 MB, ~92%). `.ksplat` on Zaid's branch. No floater pruning by default (it made models worse, D-040) |
| FR9 web rendering | `.ksplat` in Three.js, first-person navigation | Done with `.spz` + Spark (Three.js). No adaptive splat budget |
| FR10 dimensions | Area / length of a labelled element | Wall gross / opening / net areas and point-to-point measure. Per-element area for fixtures not done |
| FR11 X-ray overlay | Planned FYP-2 | Dropped by the team (D-033) |
| NFR1 capture 30 FPS | ≥ 30 FPS | **Not met.** Re-measured 2026-11-12 on scan #3 (classroom, `scan_003_6de634cbb8b2`, Infinix, v0.3.6, 185 s): 28.9 fps average, 3.3% dropped-frame gaps, longest 99 ms (R-031). Before the 2026-10-23 fixes: 0.7–3.6% |
| NFR2 IQA latency | < 16 ms per frame | Not measured. The app now logs it per frame (`quality.csv` `iqa_ms`, `feature/iqa-timing`, not yet on a phone); `check_capture.py` reports it |
| NFR3 pipeline time | 60 s video in 15 min on a 4090 | Not met: 96 min on a 3070 (240 s video). FYP-2 target < 35 min on a 4090 (projection) |
| NFR4 compression | ≥ 60% | Met (`.spz` ~92%, `.ksplat` 73–88%) |
| NFR5 viewer FPS | ≥ 30 FPS mid-range browser | Not measured |
| NFR6 accuracy | ≤ 5% vs tape | Met: 0.19% mean / 0.29% worst (v3); v9 room length −1.5% |
| Final-1 exit gate (a) | 60 s capture uploads and triggers the cloud pipeline | Upload → local server works; RunPod unreliable |
| Final-1 exit gate (b) | ARCore-assisted COLMAP → 3DGS | Done |
| Final-1 exit gate (c) | Compressed and rendered in a browser | Done (manual `export_web.py` step) |
| Final-1 exit gate (d) | Visual-only vs ARCore-assisted COLMAP baseline, ATE + track completion | **Not done** |
| Evaluation: contribution 3 | Semantic precision / recall (mIoU) on held-out keyframes | Only a room check on one room |
| Evaluation: contribution 4 | Viewer FPS / GPU memory / load time vs unoptimised | Not done |
| UAT | Supervised walkthrough with the construction stakeholder, semester 2 | Not started |

## 5. How to run (v9 / v10, Windows RTX 3070 PC)

Setup: three Python environments, see the README "Quick Start Guide" and `requirements*.txt`.
From the repo root, `S` = `dataset/<capture>/work_v9_sfm`, `M` = `$S/gs_v9`:

```powershell
# 1. Capture -> metric 3DGS (96 min). System Python; nerfstudio steps switch to nerfstudio-env themselves.
python src/arcore3dgs/run_v8.py --dataset dataset/<capture> --tag v9 --sfm_args "--retrieval 20" --init fmvs --planar 0.2 --blur 0.0222
#    The best model adds --pgsr: rerun the train stage with geo_splatfacto.py --pgsr (same arguments run_v8.py prints).

# 2. Room layout (walls, corners, dimensions)
nerfstudio-env\Scripts\python.exe src/arcore3dgs/layout.py --ply $M/splat.ply --work $S --out $M/layout

# 3. Semantics: 2D proposals (38 min), 3D labels, CLIP check of switches / sockets, then 3D labels again
semantic-env\Scripts\python.exe -W ignore src/arcore3dgs/semantic2d.py --work $S --every 2 --box_thr 0.28 --tiles 640 --out semantic2d_v10
nerfstudio-env\Scripts\python.exe -W ignore src/arcore3dgs/semantic3d.py --ply $M/splat.ply --work $S --layout $M/layout/layout.json --out $M/semantic_v10 --sem2d semantic2d_v10
semantic-env\Scripts\python.exe src/arcore3dgs/verify_fixtures.py --work $S --sem2d semantic2d_v10 --semantic $M/semantic_v10
nerfstudio-env\Scripts\python.exe -W ignore src/arcore3dgs/semantic3d.py --ply $M/splat.ply --work $S --layout $M/layout/layout.json --out $M/semantic_v10 --sem2d semantic2d_v10 --verdicts $M/semantic_v10/verdicts.json

# 4. Mesh (PGSR models: --depth unbiased), labelled mesh, web bundle
nerfstudio-env\Scripts\python.exe src/arcore3dgs/mesh.py --ply $M/splat.ply --work $S --out $M/mesh --depth unbiased
nerfstudio-env\Scripts\python.exe src/arcore3dgs/mesh_labels.py --mesh $M/mesh/mesh.ply --ply $M/splat.ply --semantic $M/semantic_v10 --layout $M/layout/layout.json --clean 0.01 --glb 400000
nerfstudio-env\Scripts\python.exe src/arcore3dgs/export_web.py --ply $M/splat.ply --semantic $M/semantic_v10 --glb $M/mesh/mesh_web.glb --out prototype/web-ui/public/scans/<name>
```

Check each script's docstring for its full options. Don't run other GPU jobs while training with `--blur` (OOM on 8 GB).
Log every run in [TRAINING.md](TRAINING.md).

Older pipelines: `scripts/run_arcore3dgs.bat <dataset>` (v3: COLMAP + splatfacto, ~75 min, what the server runs) and
`scripts/run_arcore3dgs_legacy.bat` (ARCore poses + own BA / MVS / PocketGS prior). Viewer: `scripts/view_splat.bat`
(port 7010). Phone-upload server: `scripts/start_server.bat` + `scripts/jobs.bat` ([PROCESSING_GUIDE.md](../PROCESSING_GUIDE.md)).
On Linux (this PC): `screen -dmS bs-server scripts/start_server.sh` (reattach `screen -r bs-server`; env `bs-server`,
created once with `micromamba create -n bs-server -c conda-forge python=3.10 pip` + `pip install -r server/requirements.txt`).
Mode defaults to `dry_run` (uploads saved to `dataset/scan_<id>/`, nothing processed). Phone URL: this PC's LAN IP, port 8000.

## 6. Machines and environments

The goal is that the full pipeline runs the same way on three places: **this PC, a friend's PC and RunPod**
(Umair, 2026-11-06). Today it runs only on the RTX 3070 PC.

| Machine | Hardware / OS | State (2026-11-06) |
|---|---|---|
| RTX 3070 PC | Windows, RTX 3070 8 GB VRAM, 16 GB RAM | Every run so far. Holds `dataset/`, `saved_models/`, `tools/colmap_dl/` (COLMAP 4.2 CUDA), `tools/cudnn9/`, the three envs (all gitignored) |
| This PC (`gpu-lab-Precision-3680`) | Ubuntu 26.04.1 LTS (kernel 7.0.0-43), NVIDIA RTX 4000 Ada (20 GB), 28 threads, 30 GB RAM, 366 GB free | Setup in progress (R-027). **NVIDIA driver 595.99.02 working** (installed 2026-11-06, was `nouveau`), Secure Boot enabled; micromamba 2.10.0 in `~/.local/bin`; conda envs `bs-colmap` (COLMAP 4.2.0 CUDA, starts), `bs-ns` (Python 3.10, CUDA 12.1, gcc 11.4, Node 22, ffmpeg) and `bs-system` (Python 3.10, ffmpeg) built 2026-11-06; pip packages not installed yet. Still missing system-wide (by design, provided by the envs): no gcc / make / cmake / ninja, no ffmpeg / ffprobe, no Node.js, no Docker, no COLMAP, no conda; system Python 3.14.4 only (torch 2.1.2 needs ≤ 3.11); `sudo` needs Umair's password; git identity configured and GitHub over SSH, `gh` 2.103.3 in `~/.local/bin`, auto-suspend off (2026-11-06); no Tailscale / SSH server yet; no datasets or models |
| Friend's PC | Not recorded yet | Fill in: owner, GPU, OS, what is installed |
| RunPod | On-demand pod (default "RTX 4090"; an earlier commit set RTX 3090), image `umairishuman/buildscan-gpu:latest` | Integrated in `server/`, works poorly per the user; no recorded end-to-end run |

Portability problems found while reading the code (not yet tested on Linux):

- `server/pipeline.py` and every `scripts/*.bat` call `nerfstudio-env\Scripts\python.exe` / `.exe` tools: Windows-only paths.
- `requirements.txt` is a Windows `pip freeze`: it contains `msvc_runtime` and `pywinpty`, and gsplat is loaded through a
  prebuilt Windows `.pyd` shim (`gsplat/csrc.py`, section 10). On Linux gsplat 1.4 must be built or installed for the local CUDA.
- COLMAP 4.2 CUDA is a Windows download in `tools/colmap_dl/`; Linux needs its own build or package of ≥ 4.2
  (`global_mapper`, faiss vocabulary trees). ALIKED needs `tools/cudnn9` DLLs (only for the rejected ALIKED path).
- `semantic-env` relies on the system Python's torch 2.1.2 (`--system-site-packages`); `truststore` is there for the
  TLS-intercepting network.

**Docker image (`docker/Dockerfile.gpu`, built by `.github/workflows/docker-gpu.yml` and pushed to Docker Hub as
`umairishuman/buildscan-gpu:latest`).** Out of date against the current pipeline:

- base `runpod/pytorch:2.4.0-py3.11-cuda12.4.1` (torch 2.4) while the local envs use torch 2.1.2 + cu121;
- COLMAP from Ubuntu 22.04's `apt` (an old 3.x release, to be checked), not 4.2 with `global_mapper`;
- only `nerfstudio==1.1.5 open3d==0.19.0 pyquaternion scipy opencv-python-headless plyfile`: no Metric3D deps
  (`timm`, `mmengine`), no semantic stack (`transformers`, SAM / Grounding DINO weights), no Node.js for the `.spz` export,
  no pinned `gsplat`;
- the RunPod setup script skips installing anything if nerfstudio is present, so a stale image is used silently.

## 7. Open work (everything left)

Tags: **[new]** added 2026-11-06; *(from TODO, date)* carried over from the old TODO.md. Sources in brackets.

**Plan to finish by 2026-12-04:** [COMPLETION_PLAN.md](COMPLETION_PLAN.md) puts every item below into one task table per
pipeline step, with done-when, dependencies, priority (Must / Should / Could), target week and gates (2026-11-19,
11-26, 12-04). Owners are still to be agreed by the team.

### 7.1 Organisation, environments and infrastructure

- [ ] **[new 2026-11-28] Security framework follow-ups** ([docs/SECURITY.md](../SECURITY.md), D-100): upload-server
      controls S1 – S4 (shared token, `/config` from the PC only, `/reprocess` name check, upload size limits) for Umair
      (OD-20); the app's token field (A8) with S1; privacy rules PR1 / PR2 (consent to record and to publish) in the
      capture protocol; `npm audit` / `pip-audit` as an informational CI step (C3).
- [ ] **[new 2026-11-28] Push `feature/ux-security` and open its PR** (web viewer usability + security headers, app
      usability + network security config, docs/SECURITY.md, docs/HCI.md; 7 commits on `fix/viewer-perf`, so merge
      that one first). App part not compiled on the 3070 PC yet (to do after R-146; CI compiles on push).
- [ ] **[new 2026-11-19] Merge `origin/master` into the Step 4 work (OD-12).** `origin/master` has 43 commits that
      `feature/step4-layout` does not (Tayyab's PR #7: fast pipeline, `tape_check.py`, server v9 runner, layout ceiling
      rule `d052301`, plan.png fix `a098711`, real models in `mockData.ts`, app v0.3.8). A dry run conflicts in MAP,
      COMPLETION_PLAN, LOG, STATUS, TRAINING, web-ui `.gitignore` / STATUS / `mockData.ts` and `sfm_colmap.py`;
      `layout.py` merges as text but has two ceiling rules. Run IDs R-032 … R-040 and D-069 mean different things on
      the two sides; `origin/docs/featureless-tracking-plan` goes on to R-051. Team decision on the numbering first.
- [x] **[new 2026-11-12] Update the server checkout on this PC** — done 2026-11-12: `origin/master` (PR #4) merged into `exp/first-linux-run`. Was: run the server from a branch that includes PR #4 (local `master` is
      behind `origin/master`; the server runs from `exp/first-linux-run`), so v0.3.5 uploads keep the new files.

**Order agreed on 2026-11-06 (Umair, D-047 – D-049): step 1 this PC, step 2 the Docker image from the same setup
script, step 3 RunPod and the friend's PC.**

**Step 1: set up this PC** (same versions as the RTX 3070 PC, in conda/micromamba envs; D-047)

- [x] **[new] 1a. NVIDIA driver (Umair, needs sudo)** — done 2026-11-06: driver 595.99.02, `nvidia-smi` sees the RTX 4000 Ada (R-027). `sudo ubuntu-drivers install nvidia-driver-595-open`, reboot,
      check `nvidia-smi` lists the RTX 4000 Ada. Secure Boot is on: if the installer asks for a MOK password, enrol it on
      the blue MOK screen at the next boot, otherwise the driver will not load.
- [x] **[new] 1b. micromamba** in the user's home (no sudo), and set the git identity — done 2026-11-06 (micromamba 2.10.0; Umair set `git config --global user.name/user.email`).
- [x] **[new] 1b2. GitHub access from this PC** — done 2026-11-06: Umair added an SSH key (`~/.ssh/id_ed25519`), remote switched to `git@github.com:Umairishuman/BuildScan3D.git`, `docs/project-organisation` pushed. Before: no `gh`, no SSH key, no credential helper, so `git push` fails with
      `could not read Username for 'https://github.com'` (2026-11-06). Set up an SSH key (or a personal access token).
- [x] **[new] 1c. Three envs mirroring the Windows ones** — done 2026-11-06 (`bs-colmap`, `bs-ns`, `bs-system` + `semantic-env`; R-027). (timm 0.6.7 for nerfstudio vs timm 1.0.30 for Metric3D, and
      transformers 4.46.3, can't share one env): system-equivalent, nerfstudio, semantic. Each: Python 3.10, and where
      CUDA code is compiled (gsplat 1.4.0, tiny-cuda-nn) CUDA toolkit 12.1 + gcc 11 from conda; then pip
      `torch==2.1.2+cu121 torchvision==0.16.2+cu121` and the pinned packages; `TORCH_CUDA_ARCH_LIST=8.9` (Ada).
      ffmpeg / ffprobe and Node.js from conda too, so nothing else needs sudo.
- [x] **[new] 1d. Linux requirement files** — done 2026-11-06 (`envs/linux/`; versions equal to Windows; setuptools < 70 added; tiny-cuda-nn left out, unused). the Windows `requirements.txt` is a `pip freeze` with Windows-only
      packages (`msvc_runtime`, `pywinpty`); make Linux pins (env `.yml` + requirement files) and keep the versions equal.
- [x] **[new] 1e. COLMAP ≥ 4.2 with CUDA on Linux** — done 2026-11-06: conda-forge 4.2.0 `cuda_129` + OpenImageIO 3.1; GPU SIFT / matching / vocab tree tested; mapper and PatchMatch wait for real data. (check whether conda-forge has 4.2 with CUDA, else build from source
      in the env) + the faiss vocabulary trees (from the COLMAP 3.11.1 / 3.13.0 releases), as on Windows.
- [ ] **[new] 1f. Port the Windows-only paths in code** — partly done 2026-11-06 on `feature/linux-port`: `toolpaths.py`, `run_v8.py`, `sfm_colmap.py`, `fast_mvs.py`, `mvs_init.py`, `colmap_mvs.py`. Still open: `server/pipeline.py`, `.sh` launchers (`scripts/start_server.sh` done 2026-11-06, D-057). `run_v8.py` (`nerfstudio-env/Scripts/python.exe`,
      `ns-export.exe`), `sfm_colmap.py` (`tools/colmap_dl/.../COLMAP.bat`, `tools/cudnn9` DLL path), `server/pipeline.py`;
      the `.bat` launchers need `.sh` equivalents.
  - **2026-11-14:** `server/pipeline.py` now finds the nerfstudio programs through `toolpaths.ns_cmd` (no hard-coded
    `Scripts/*.exe`), and `scripts/run_full.sh` runs on Windows Git Bash too. Not yet started on Linux through the server.
- [ ] **[new 2026-11-14] Server jobs can run v9/v10** (COMPLETION_PLAN 2.3): `BUILDSCAN_PIPELINE=v9` makes a job run
      `scripts/run_full.sh` (R-023/R-031 recipe, `BUILDSCAN_V9_ARGS` to override), with the 15 stages as job progress;
      default still v3 until OD-7 is decided. To do: one upload end to end with it (2.5), then OD-7.
- [x] **[new] 1g. All of 1b–1f as one script** — done 2026-11-06: `scripts/setup_linux.sh` (+ `--check`); run here OK, fresh-machine run not yet tested. (`scripts/setup_linux.sh` + env files), so step 2 and the friend's PC reuse it (D-048).
- [x] **[new] 1h(a). First complete run here** — done 2026-11-06 (R-029): Umair's corridor-end recording
      `scan_056fe94d3399` through `scripts/run_full.sh`, all 15 stages, 34.7 min, no errors after the `imu.npz` fix (R-028).
- [ ] **[new] 1h(b). Machine agreement:** copy `newRoomAttemptSadness` from the RTX 3070 PC, run the v9 pipeline, log it in
      TRAINING.md (every setup and run error), and compare with R-020 / R-023 to confirm the machines agree.
      **2026-11-12: R-037 done** (R-023 recipe, 103.0 min, no errors): room 6.63 × 4.37 m vs R-023 6.60 × 4.36 m, so
      the size agrees. Still open: PSNR / SSIM (needs the R-014 split from Tayyab), scale vs R-023 (R-023's scale is
      not on this PC), 18 vs 15 fixtures (sheet for Umair), height 2.81 vs 2.72 m (next item).
- [ ] **[new 2026-11-12] D-072 may overshoot the ceiling on newRoom (R-037):** the strongest horizontal plane was 2.69 m
      above the floor but below the wall tops, so the rule took 2.81 m (R-023: 2.72 m). Tape the newRoom height, or
      look at what sits above 2.69 m in the model (floaters above the ceiling?), before keeping or changing D-072
      (Umair's decision).

**Remote access and moving between lab PCs** (D-053)

- [x] **[new] Auto-suspend off** on this PC (2026-11-06, GNOME `sleep-inactive-ac-type 'nothing'`). Checked later the
      same day: no suspend since boot (journal). The screen still **locks** after 5 min idle (and on Win + L); locking
      is not sleep, runs and Tailscale continue. Lock kept on purpose (Umair, D-053).
- [ ] **[new] Login-screen suspend** (applies when nobody is logged in, e.g. after a reboot; needs sudo): GDM's own
      power setting, or `sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target` (lab policy?).
- [x] **[new] Tailscale on this PC** — done 2026-11-06: `gpu-lab-precision-3680`, 100.102.13.24, Tailscale SSH on,
      starts at boot, MagicDNS on. Used **only** for Umair's laptop → this PC (the phone uploads over the Wi-Fi).
- [ ] **[new] Tailscale: Umair's laptop** joins the tailnet and `ssh i230662@gpu-lab-precision-3680` is tested (the
      only other own device, `desktop-hnumpvk`, was last seen 2026-09-30); then VS Code Remote-SSH.
- [ ] **[new] Tailscale offline on the lab Wi-Fi** (found 2026-11-06 18:02): `tailscale status` says this PC is
      offline, "Unable to connect to the Tailscale coordination server". UDP / DERP work (netcheck: Singapore 131 ms) and
      the TLS handshake with `controlplane.tailscale.com` succeeds (Let's Encrypt cert, so no TLS interception), but
      the HTTPS requests time out / are closed (`tailscaled`: "read tcp 172.15.40.53 → 192.200.0.x:443: use of closed
      network connection"). It worked earlier on the wired network (172.17.170.120). Likely the lab Wi-Fi cuts these
      connections. Options: wired network, or ask lab IT whether Tailscale is blocked on the Wi-Fi.
- [ ] **[new] Tailscale: disable key expiry** for this PC in the admin console (key expires 2027-05-05).
- [x] **[new] Firewall (`ufw` is active) for phone uploads** — done 2026-11-06 by Umair: TCP 8000 and UDP 8001 (server
      search) allowed on the Wi-Fi card, so they work on the lab Wi-Fi and on the phone's hotspot:
      `sudo ufw allow in on wlp0s20f3 to any port 8000 proto tcp` and the same with `port 8001 proto udp`.
      Phone access not yet tested. The PC is on Wi-Fi (`wlp0s20f3`, 172.15.40.53/19 on the lab Wi-Fi); the wired card had no address.
- [ ] **[new] SSH into this PC from the laptop: test.** No OpenSSH server is installed (no `sshd`, nothing on port 22);
      remote login is **Tailscale SSH** only (`RunSSH` on, ssh capability granted, 2026-11-06). A test from this PC to its
      own address is not possible (local traffic bypasses Tailscale); test from the laptop once it is in the tailnet.
- [ ] **[new] Back up the release signing key** `~/.buildscan3d-keys/` (D-059) somewhere other than this PC.
- [ ] **[new] Dockerise the upload server** so it runs the same on Windows and Linux (asked by Umair 2026-11-06;
      deferred with step 2, Docker not on this PC for now, D-045 / D-057).
- [x] **[new] Remote power-on — not needed (2026-11-06, D-053):** Umair has no BIOS access, and the lab agreed to leave
      the PC on. Notes kept in case that changes: wired NIC `enp0s31f6` (Intel I219-LM, MAC `ac:b4:80:3b:91:2e`, LAN
      172.17.170.120/24) has device wake-up enabled; Wake-on-LAN also needs the BIOS setting and `sudo ethtool -s
      enp0s31f6 wol g`, plus an always-on device **on the same LAN** to send the packet (WoL does not cross Tailscale).
      Alternatives: Intel AMT (Intel ME present; needs lab provisioning), BIOS "Auto On" schedule, or asking the lab to
      keep it on.
- [ ] **[new] Moving to another lab PC** (same `/home/i230662`): run `scripts/setup_linux.sh` (needs the driver first), or
      copy `~/micromamba`, `~/.local/bin`, the model caches and the repo extras with `rsync` (~27 GB, works because the
      path is the same); then `setup_linux.sh --check`. Data (datasets, saved models) is copied either way; where its
      master copy lives is still open. Proposed: `scripts/sync_to_pc.sh` + a new-PC checklist.

**Step 2: rebuild the Docker image** (after step 1 works)

- [ ] **[new] 2a. New `docker/Dockerfile.gpu` that runs the same setup script** (D-048), from a CUDA 12.1 base, with
      COLMAP 4.2, all three envs, Node.js and the model weights it needs (Metric3D, Grounding DINO, SAM, CLIP) or a
      download step. The current image's problems are listed in section 6.
- [ ] **[new] 2b. Build it.** Docker is **not installed on this PC and should not be installed yet** (Umair, 2026-11-06,
      D-045). `.github/workflows/docker-gpu.yml` builds and pushes on GitHub without local Docker; check the runner's disk
      is big enough for a CUDA + torch + COLMAP image. Consider dated / commit tags next to `:latest`.
- [ ] **[new] 2c. Test the image** on RunPod (or here, once Docker is allowed), and make the RunPod setup script stop
      silently skipping installs on a stale image.

**Step 3: RunPod and the friend's PC**

- [ ] **[new] Make the pipeline run the same on this PC, the friend's PC and RunPod;** one recorded run per machine in TRAINING.md.
- [ ] **[new] RunPod: find out why it works poorly.** Run one end-to-end job (create pod → process → download →
      terminate) and log every error in TRAINING.md. *(from TODO 2026-10-12: "End-to-end test of RunPod flow")*
- [ ] **[new] Friend's PC:** record owner, GPU, OS in section 6; run `setup_linux.sh` (or a Windows equivalent).

**Other organisation items**

- [ ] **[new] Upload server exposed to the internet on the RTX 3070 PC's network (found 2026-11-12, Tayyab's session).**
      With the server on port 8000 (dry-run mode, 17:45 – 18:25), ~30 public IP addresses (internet scanners, e.g.
      Infrawatch, a WinRM probe on `/wsman`) reached it within minutes, so the router forwards port 8000 to this PC (port
      forwarding / DMZ / UPnP). All of their requests got 404; the phone upload (`scan_3028a4de8fa0`) was the only
      successful POST. The server has no authentication (`/upload`, `/config`). Before running it on that network again:
      remove the router forwarding (or run on the PC's own hotspot, 192.168.137.1), and/or add a token to the server.

- [x] **[new] Revoke the leaked RunPod API key** — done 2026-11-06 by Umair (the old key no longer works; the new one is
      only in the local `.env`). History:  commit `00bc021` (2026-10-18) committed `.env` with a
      real `RUNPOD_API_KEY`; untracking it on 2026-10-22 did not remove it from history, and the repository is
      **public**. Revoke it in the RunPod console and make a new one (local `.env` only). Removing it from git history
      as well needs a history rewrite + force-push: to be discussed with the team.
- [x] **[new] Repository visibility** — stays **public** (Umair, 2026-11-06, D-056); docs/CI_CD.md §9 corrected.
- [ ] Optional: remove the revoked key from git history (`00bc021`); needs a history rewrite + force-push, team decision.
      Not urgent now that the key is revoked.
- [ ] **[new] Raise the coverage gate back to 40%** when the tests are written (D-054; now 35%, measured 37.4%).
  - **2026-11-14 (Tayyab's overnight session, `exp/overnight-2026-11-14`):** with the new tests (`test_tape_check.py`,
    v9 server tests) line coverage is **45%** locally (Windows, Python 3.10; CI on Linux not run yet). D-054 can be
    flipped back to 40% once CI confirms it on the branch (Umair's decision).

- [ ] **[new] Code reorganisation, step 2 of D-049:** regroup `src/arcore3dgs/` by stage (proposal in
      [MAP.md](../../MAP.md) §10) on its own branch, **after** step 1 works so every move can be checked with a real run.
- [ ] Wire the v9 / v10 pipeline into the server and RunPod (they still run the v3 recipe). [PROCESSING_GUIDE]
- [ ] Merge `feature/semantics-mesh` (v9, v10, docs; 5 commits ahead) into `master` through a PR. Needs a team decision.
- [ ] Decide what to do with the unmerged branches `origin/feat/splat-compress` (Zaid, `.ksplat`) and
      `origin/exp/trainer-arkitscenes` (Zaid, ARKitScenes trainer experiments on Kaggle).
- [ ] Move the server to a cheap always-on VPS so the phone can upload without the PC running. *(from TODO 2026-10-12)*
- [ ] GitHub one-time settings from CI_CD.md §6 (branch protection on `master` requiring `CI passed`, workflow
      permissions for releases): not recorded whether they were made.
- [ ] README is out of date: folder tree (`d:/FYP/`, `docs/Proposal Slides/`, `mobile-ui/`, `FloorPlanView.tsx`), and it
      still advertises YOLOv8-Seg MEP layers, which were dropped. AGENTS.md §3 still says ~75 min (v3) and names only
      `structure.py` for Stage 4.
- [ ] Archive (never delete, D-049) the unused files once their owners agree: `src/arcore3dgs/train_fixed2_backup.py`,
      `train_v3_backup.py`, the five old `scripts/run_train*.bat` / `run_post*.bat` / `run_viewer.bat`, `scratch/`,
      `ViewerHUD.tsx` (the user declined its deletion once). Marked `[dead]` in MAP.md.
- [ ] CI limits (CI_CD.md §7): coverage counts only imported files; most `src/arcore3dgs` logic runs at script top level
      and is untested; no Android unit tests; no GPU stages in CI.

### 7.2 Processing speed (optimise the processing) **[new priority]**

Now: 96 min on the RTX 3070 (select 1.9, SfM 22.4, priors 8.1, fast init 20.4, training 42.5, export 0.7) plus ~40 min
of semantics (2D stage 38 min since the v10 tile pass, was 8 min). Proposal NFR3: 15 min on a 4090; FYP-2 target
< 35 min on a 4090 (projection).

- [ ] **[new 2026-11-12] Speed baseline on this PC (R-031, scan #3, 885 frames):** run_v8 64.7 min (SfM 12.1, prior 3.6,
      init 14.8, train 33.6) + sem2d 13.7 min; 81.0 min in total. Tayyab is doing the speed work on the RTX 3070 PC
      (2026-11-12: SfM without retriangulation, threaded priors I/O, photometric PatchMatch, training loss / colour-grid
      fixes; expected ~65 min vs 96 on newRoom, not yet measured; LOG 2026-11-12). Check his recipe on scan #3 vs R-031.
- [ ] **[new 2026-11-16] SfM memory and time on long recordings (plan 3.18, Thursday 2026-11-19):** scan #8 (366.5 s,
      10,255 frames) ran out of RAM in COLMAP `global_mapper` with 1,639 frames (R-038, 26.1 GB, OOM kill); with
      `--window 9` (1,118 frames, D-073) it passed with ~2 GB to spare and global positioning took 28.3 min (R-037:
      1.7 min). Test `hierarchical_mapper` and `--max_features 4096` against R-037; consider a RAM line / low-memory
      warning in `run_full.sh` and a clear "killed: out of memory" message in `buildscan watch` (today the cause is only in
      `journalctl -k`). Ceres here has no cuDSS, so bundle adjustment runs on the CPU.
- [ ] **[new] Optimise the processing pipeline** end to end; measure each change with `run_v8.py`'s stage times and log it.
  - **2026-11-12 (Tayyab's session, branch `exp/fast-pipeline`):** training 42.5 → 28.2 min and dense init 20.1 → 7.5 min
    at equal quality on newRoom (TRAINING R-062, R-063); Metric3D 8.1 → 6.8 min (identical output). Normal SfM + these:
    ~67 min end to end on newRoom (estimate from the measured stages), 48.8 min on the new lecture hall (R-066). The SfM
    shortcut `--skip_retriangulation` lost quality (R-065, rejected). Adoption: DECISIONS OD-10.
  - **[new 2026-11-12] SfM can shrink part of a room (GLOMAP).** R-066's lecture-hall model had a "mini room": ~175
    frames (ARCore lost after frame ~2200, so `--pairs arcore` matched the wrong neighbours) were placed by GLOMAP at
    ~0.38× scale. The incremental mapper (`--mapper mapper`, R-067) keeps the main part correct (581/842 frames) and
    splits off the rest; R-068 trained on it (no mini room, right-side walk missing). To do: a per-frame scale check
    after SfM (SfM depth / Metric3D depth, a block of frames < 0.5× = shrunken part) that warns or falls back to the
    incremental mapper; and do not trust ARCore neighbours after tracking loss. Adoption: DECISIONS OD-11.
- [ ] **[new 2026-11-13] Speed-ups not tested with `--pgsr`** (the best model's recipe, R-023, now a `run_v8.py` flag
      from master) **nor on Linux**: one run of each before adopting OD-10.
  - **2026-11-14:** tested on newRoom (R-041): training 33.0 min vs R-021's 46 min, PSNR 25.02 / SSIM 0.8232 /
    sharpness 0.87 vs 25.09 / 0.8254 / 0.88 (one run each); off-path flatness of R-021 still to measure. Also used in
    R-069 (roomAttemptSadness2, 36.2 min). Linux still not tested.
- [ ] **[new 2026-11-13] Batched Grounding DINO tiles in `semantic2d.py`** are committed but have never run: compare the
      2D labels with the unbatched output on newRoom and time it (the 38-min semantics stage is the next big cost).
  - **2026-11-14:** first real run (R-069, roomAttemptSadness2) was ~3× slower (~12 s per frame): batching all tiles
    filled the 8 GB GPU and Windows spilled GPU memory to RAM. Now `--tile_batch` (default 1 = the old per-tile calls).
    Batching only helps on a larger GPU; not measured there.
- [ ] **[new 2026-11-13] Fast recipe vs v9e2e on the lecture hall is not known** (R-066/R-068 have no baseline; Tayyab
      is not sure R-068 is better than v9e2e). Umair's R-031 (scan #3, Ubuntu PC, old recipe + PGSR) looks like the
      same hall with a steadier capture (6.7 px vs 25 px blur): compare the two models side by side once R-031 has a result
      (not checked that it is the same room).
- [ ] **[new 2026-11-13] Clean up the speed-up experiment folders on the 3070 PC** (`work_v9e2e_sfm/_mapper_exp`,
      `undist_fast_it3`, `undist_fast_photo`, `gs_fast_t1`, `gs_fast_t2_photo`, `work_v10fast*` in newRoomAttemptSadness;
      `work_v10_sfm` of `scan_3028a4de8fa0` holds the rejected mini-room model). Ask Tayyab first; disk 93% full (70 GB free).
- [ ] **[new 2026-11-13] `scan_3028a4de8fa0` has no recording number** (D-065 numbers the recordings on the Ubuntu PC;
      this one was uploaded to the 3070 PC on 2026-11-12 with an older app, no `camera.csv`). Decide whether recordings
      on the 3070 PC get numbers too.
- [ ] Training 42 min (blur ×1.4) and SfM 22 min dominate; fast_mvs 20 min. Ideas: blur only in the last third,
      photometric-only PatchMatch, ViT-S prior. *(from TODO 2026-10-26)*
- [ ] Faster `fast_mvs` (photometric only or every 10th frame) and `plane_seg` (~11 min CPU). *(from TODO 2026-10-26)*
- [ ] Semantics 2D stage: the tile pass made it 5× slower (8 → 38 min). [STATUS 2026-11-06]
- [ ] Faster 3DGS methods that need their own CUDA rasterizer (FastGS, Taming-3DGS budget) — later / cloud, since our
      gsplat is a prebuilt binary. [Research_Notes §1]
- [ ] Cloud RTX 3090/4090 roughly halves training (not measured). *(from TODO 2026-10-21)*
- [ ] Legacy: `--near_cam` in the own trainer is slow (CPU KD-tree every 100 steps). *(from TODO 2026-10-11)*

### 7.3 Reconstruction quality

- [ ] **[new 2026-11-12] scan #3 (classroom): check the levelled layout against the tape.** R-031's 2.74 m / 2 walls
      came from a model tilted 12.1° from gravity (R-032). Levelled (R-034 / R-035): **2.52 m, 4 walls, 3 corners at
      89–90°, 7.23 × 9.05 m, floor 32.27 m², 18 fixtures**. Tape not measured yet; Umair checks the 18 fixtures with
      `gs_r1112lev/semantic_v10/fixture_check.md` (COMPLETION_PLAN 4.2).
- [x] ~~R-030 (scan #2, lab): room height 1.50 m cannot be right.~~ **Cause found 2026-11-12 (R-032):** the model was
      9.1° off gravity and its white ceiling was reconstructed 0.4 m above the camera (plus a reflection in the door
      glass). Levelled + D-072: 2.41 m (R-036), still 1 wall. See the next item.
  - [ ] (from `master`, Tayyab's open copy of this item, merged here 2026-11-19)
      check which plane the layout took as the ceiling and whether the scale is off; measure one length with a tape.
  - **2026-11-14:** `layout.py` fix (`exp/overnight-2026-11-14`): the ceiling is now the strongest horizontal cluster
    above the cameras with < 3% of the opaque splats above it, not just the strongest one (an AC unit or cabinet
    underside can win). newRoom unchanged (2.72 m); roomAttemptSadness2 2.78 m (R-069). **To do (Umair, Linux PC):**
    rerun `layout` on R-030 (`buildscan`, `--from layout`) and check the height against the tape.
    Both ceiling rules now run in sequence (D-072 after `--above_frac`, OD-12): rerun the four R-057 rooms and R-030.
- [ ] **[new 2026-11-12] Re-record the computer lab (scan #2) with the capture protocol** (§7.8): the camera stayed
      within 0.8 × 0.7 m, so the ceiling and most walls never got a baseline (R-032 / R-036).
- [ ] **[new 2026-11-15] Frames without an ARCore pose (`--pose_free`) and ALIKED SfM** (R-045, R-046,
      `exp/overnight-2026-11-14`): on scan_009 (ARCore lost tracking 63.7% of the time) the default recipe kept 87 frames
      (R-045); `select_sharp.py --pose_free` keeps frames without a pose (894 vs 238), and `--feature aliked` joined 761 of
      them in one SfM component (SIFT: largest 234 / 409). After the jump filter 535 frames trained (R-046, inconclusive):
      misplaced cameras remain, scale unreliable (26 ARCore inliers). **Re-opens D-022 (ALIKED rejected 2026-10-26) with
      new evidence on another capture: Tayyab's call.** To do: run `--pose_free` + ALIKED on newRoom against R-062 before
      any default change; a stricter mis-registration filter (only jumps > 30 cm are dropped now).
- [ ] **[new 2026-11-15] Scale fallback when ARCore poses are poor:** Metric3D ÷ ARCore scale measured 0.83 (newRoom),
      0.93 (room2), 0.52 (lecture hall), so Metric3D is not a usable fallback; ARCore depth on scan_009: 17 maps, mutually
      inconsistent (possibly the depth/pose pairing bug fixed in the app on 2026-11-15, 7.7). Unsolved.
- [ ] **[new 2026-11-15] Re-record scan_009's room** (bedroom with cabinets / AC / curtains): `check_capture.py` FAIL on
      tracking lost 63.7% and median blur 21.7 px; the walk looked mostly at upper walls, the floor is barely in view.

- [ ] **[new 2026-11-14] Techniques tried on newRoom** (one run each, off-path 79 frames, baseline R-062 25.14 / 0.8251):
      MCMC densification 620k / 1M (R-070, R-042: 24.65 / 24.74, visibly softer, **rejected**), revised opacity (R-043:
      25.02, −10% size, inconclusive), lower densify threshold 0.0004 (R-044: 25.07, sharper score, +40% size,
      inconclusive). None beats the current recipe; the off-path softness is more likely the capture (motion blur,
      coverage) than densification. Untried: residual camera-pose refinement and exposure correction (LighthouseGS,
      WACV 2026), longer training, measuring run-to-run noise first (3.6).


- [ ] **Second room** (roomAttemptSadness2): full v9 pipeline + semantics (~2 h GPU), then a room check by the user. The
      real test of v9/v10. *(from TODO 2026-10-24 / 2026-10-27)*
- [ ] Full PGSR multi-view geometric + photometric consistency (1–2 days, ~2× training time); removes the faint vertical
      stripes on plain walls. *(from TODO 2026-10-27)*
- [ ] Rolling-shutter modelling and per-frame exposure from `camera.csv` in the blur model (v9 uses a fixed 1/45 s).
      Check whether "Gaussian Splatting on the Move" code ports to nerfstudio 1.1.5 / gsplat 1.4. *(from TODO step 3, 2026-10-12)*
- [ ] Planar + blur together on v6's SfM (only tested together inside the e2e run). *(from TODO 2026-10-26)*
- [ ] Repeat runs to measure run-to-run noise on the hardest off-path frame (one run per setting so far). *(from TODO 2026-10-26)*
      [2026-11-12] For new rooms: 3 repeats of the default recipe on scan #3 with the held-out split (D-069, D-070);
      `dataset/scan_003_6de634cbb8b2/offpath_test.txt` (87 / 875 frames) is ready, runs not started.
- [ ] Anti-aliasing (Mip-Splatting idea / gsplat `antialiased`) for zooming in the viewer; needs an antialiased-aware viewer. *(from TODO step 5)*
- [ ] Reflective surfaces (glossy floor, glass): mask them out of SfM / depth / evaluation, e.g. points below the floor plane. *(from TODO 2026-10-11)*
- [ ] Ceiling and upper walls are the weakest surfaces: capture guidance to look up, or stronger planar priors. *(from TODO 2026-10-10 / 2026-10-27)*
- [ ] Free-space-aware training: penalise Gaussians in space cameras saw through (`consistency.py` as a loss). *(Novelty, from TODO)*
- [ ] Legacy, own trainer only (probably obsolete since splatfacto is the trainer; confirm before dropping): block-wise
      training; splatfacto densification in `train.py`; re-run `diagnose.py` targets; Census + SGM MVS; PocketGS 5k-step
      speed and weak depth term; the remaining 7.4% free-space floaters on roomAttemptSadness. *(from TODO 2026-10-06…10)*

### 7.4 Metric accuracy and evaluation

- [ ] **Metric scale:** a more robust Sim3 to ARCore (several segments, `anchors.csv` corrections), checked against the
      tape. The fast SfM is 1.5–1.9% off. *(from TODO 2026-10-26)*
- [ ] **[new 2026-11-14] Tape comparison script** `src/arcore3dgs/tape_check.py` (COMPLETION_PLAN E2): fill a
      `tape.csv` per room (template in its docstring) and run it on each room's `layout.json`. newRoom with the
      2026-10-11 readings: v9 layout room length 6.600 vs 6.700 m (−10 cm, −1.49%; the v3 model measured in the viewer
      was −0.8 cm). Check why the layout's wall-to-wall distance is 10 cm short (wall planes inside the wall surface?).
- [ ] Use `anchors.csv` corrections in the pipeline: re-align pre-correction ARCore poses (better Sim3 inliers, a COLMAP-free fallback). *(from TODO 2026-10-12)*
- [ ] More tape references (room 2, room height, doors) with 3 repeated clicks each, to quantify clicking error. *(from TODO)*
- [ ] Tape-measure check on roomAttemptSadness2. *(from TODO 2026-10-10)*
- [ ] Tape a switch and a socket height (semantics check). *(from TODO 2026-10-27)*
- [ ] Viewer: snap measure clicks to corners / edges (removes the endpoint bias). *(from TODO)*
- [ ] Script: model measurements vs tape → mean / max error in cm. *(from TODO)*
- [ ] Thesis metrics alongside: reprojection error before/after BA, MVS coverage, PSNR/SSIM, free-space violation ratio. *(from TODO)*
- [ ] Proposal contribution 1: COLMAP with vs without ARCore priors on low-texture captures (ATE, track completion).
      This was Final-1 exit gate (d). [proposal v4 §10, §11.1]
- [ ] Proposal contribution 4: viewer FPS / GPU memory / load time on a mid-range Android browser vs an unoptimised viewer. [proposal v4 §10]
- [ ] **Certified measurements (headline novelty idea):** every measurement with an error bound (e.g. 3.42 m ± 1.1 cm)
      from pose uncertainty, depth agreement and multi-view agreement, validated against the tape. *(from TODO, Novelty)*

### 7.5 Semantic labelling (Umair's next focus)

- [ ] **[new 2026-11-19] scan #7 (R-040): 0 fixtures accepted, all 29 candidates rejected by the geometry rules**
      (14 sockets "small, on a wall", 6 doors, 6 windows, 3 ceiling lights), while the layout found 6 walls and a
      3.40 m ceiling. Not investigated: look at the model and `semantic_v10/semantic.json` `rejected` (wrong walls?
      scale? a real room without fixtures?). Needs Umair to say what is in the room.
      2026-11-19: scan #7 is a building under construction (bare brick, no roof, empty openings, planks): 0 fixtures is most likely right; candidates listed in `gs_r1118/semantic_v10/fixture_check.md` (`--rejected`, #13) for Umair to confirm (#21). The layout bugs it showed: #8 (no roof, fixed), #9 (openings), #11 (plank faces).
- [ ] Test v10 semantics on a second room (the real test); the user confirms the 3 new detections (`door_1`, `door_6`, `tube_light_1`). *(from TODO 2026-11-03)*
- [ ] Open doorways (no door leaf) from gaps in the layout walls; windows on room 2. *(from TODO 2026-10-27)*
      **2026-11-19 (#9):** `openings.py` + `layout.py`: gaps in a wall's surface with ≥ 10 Gaussians seen behind per open cell → doorway / window opening; in `semantic.json`, net wall area, viewer, plan export. R-054 / R-055; not checked against the real rooms (#21).
- [ ] Still missed on newRoom: the socket under the ironing table (never a good candidate) and round light #14 (the
      "clock" decoy wins its votes). [P&S §4.18]
      **2026-11-19 (#16):** blocked: their positions are in `audit_ground_truth.json` on the 3070 PC.
- [ ] Thin margins: false sockets scored 0.45–0.47 in the CLIP check against a 0.5 threshold (real plates 0.69–0.88);
      the 25% switchboard rule rests on 3 plates. [P&S §4.18]
      **2026-11-19 (#14):** 17 of 80 crop-check candidates on 5 rooms score within ±0.1 of 0.5; blocked on the filled check sheets (#21) to choose a threshold.
      2026-11-23: scan #6 (R-059) adds 19 candidates, 8 dropped / 11 kept, 5 within 0.40–0.60 (0.421, 0.458 dropped; 0.544, 0.567, 0.598 kept): 22 of 99 on 6 rooms.
- [ ] Switch plates (8–14 cm) need ~30 confirming frames, so a fast walk past a switch can miss it. [P&S §4.17]
      **2026-11-19 (#15):** accepted switches / sockets have 19–82 confirming frames on 4 rooms; only 2 candidates (scan #8) were dropped for < 6 frames. The frame minimum is not the limit; blocked on #21 for `--min_views 4`.
      2026-11-23: scan #6 (R-059): accepted 12, 18, 23, 43, 56, 69 frames; none dropped for too few frames.
- [ ] Rules were tuned on the same room they are scored on: get an independent score (room 2, then precision / recall
      as in proposal contribution 3). [P&S §4.17–4.18]
- [ ] Per-element dimensions for fixtures in the viewer (FR10). [proposal v4] **Built 2026-11-12:** a fixture row or marker opens a size card (width, height, area, centre / bottom / top above floor, wall); not checked in a browser or against tape yet (COMPLETION_PLAN 4.3).

### 7.6 Room layout, structure and mesh

- [ ] Edge-based corner / blank-wall detection (gravity-aware lines; the wall–floor boundary + floor plane gives a plain
      wall's position). *(from TODO 2026-10-23)*
- [ ] Right-angle priors and an as-built floor plan export (layout.py has walls, corners, `plan.png`; no right-angle
      snapping or plan export format yet). *(from TODO, Novelty)*
      **2026-11-19 (#12):** `plan_export.py` writes `plan.json` / `.svg` / `.dxf` (R12) per run (stage 16 `plan`); `--square` turns walls within 5° (off by default; moves wall ends 1–5 cm on newRoom). Format to be agreed by the team.
- [ ] `structure.py` ceiling height (2.555 m was probably cupboard tops); `layout.py` supersedes it. *(from TODO, Parked)*
      **2026-11-19 (#18): obsolete** — `layout.py` supersedes `structure.py` (MAP §3 marks it [exp]); its ceiling height is not used anywhere.
- [ ] Wall 3 and the ceiling stay rough in the mesh (> 2.5 cm, untouched by shell denoising). [P&S §4.17]
      **2026-11-19 (#18):** measured (`mesh.py --eval_only`): ceilings 4.28–4.34 cm (newRoom, scan #8), walls 2.86–4.98 cm (newRoom wall 3, scan #8 wall 4, scan #3 wall 2). `mesh_labels.py --clean_ceiling 0.04` brings the ceilings to 0.04 cm; on in `run_full.sh` (D-075). **Ceiling part done 2026-11-19 (R-057, #18 closed):** scan #8 4.35 → 0.04 cm, newRoom 4.31 → 0.04 cm. Rough walls not addressed (may be real relief): stays open for the walls.
      **2026-11-23 (R-104, read-only):** 16 of 20 walls on scans #6 / #7 / #8 / newRoom ≤ 0.26 cm. The rough ones are not noise on a flat wall: scan #8 wall 1 (1.55 cm) and scan #6's 0.74 m wall 5 (4.70 cm) are stretches at different depths joined into one layout wall; newRoom wall 3 (2.88 cm) is bowed / leaning (1.47° off vertical). Flattening them would move real surfaces; options with Umair.
- [ ] **[new 2026-11-12] Floor still fits 1.95° tilted on levelled scan #3** (1.57° on scan #2), while the ceiling fits
      0.05°: not explained (glossy floor reflection, or a bend in the model). Look at the floor residual map. (R-035)
      **2026-11-19 (#17): cause found:** not a tilt but a step: one half fits 0.30°, the far end is 8–14 cm higher over ~2 m (a raised platform?); 29 % as many Gaussians below the floor as on it (glossy floor). Umair to confirm the platform (#20).
      **2026-11-19 (R-057):** with `--floor_win 0.06` (on, D-075) scan #3 fits 0.29°, but `semantic.json` ceiling height goes 2.504 → 2.582 m while `layout.json` stays 2.525 m (5.7 cm apart): tape decides which floor level is the room's (#17, #20).
- [ ] **[new 2026-11-12] scan #3's fourth corner is missing:** walls 2 and 3 stop > 2.5 m short of each other (door /
      cupboards on that side?). Check in the model; then 4.5 (doorways from wall gaps). (R-035)
- [ ] **[new 2026-11-12] Merge note for Tayyab:** `sfm_colmap.py` export now levels with ARCore gravity (D-071,
      `--gravity centres` restores the old Sim3); his Step 3 changes are in the mapper part of the same file.
      2026-11-23: both sides are merged on `master` (PR #39, 2026-11-19); still to tell Tayyab.
- [ ] **[new 2026-11-12] Re-check older models for tilt:** any model exported before D-071 can be off gravity;
      `level_model.py` levels it without retraining (R-034). Not checked for newRoom (R-023); R-037 prints it.
      2026-11-12: newRoom was nearly level anyway (old export would have been 0.57° off, R-037); R-023 itself not checked.

### 7.7 Android app

- [ ] **[new 2026-11-28] Check the usability pass on a phone** (`feature/ux-security`, docs/HCI.md §3): record button
      double-tap guard, 48 dp buttons, TalkBack labels; and that updates still download (HTTPS-only GitHub, A2). The
      `test_changelog` failure below is fixed on that branch (v0.3.9 line).
- [ ] **[new 2026-11-28] First-run walkthrough** (three screens on how to record; docs/HCI.md §4).
- [ ] **[new 2026-11-23] `tests/test_changelog.py` fails on `master`:** the v0.3.9 release (`8338680`, `[skip ci]`) wrote "No
      changes listed" (only a code comment changed, D-079), and the test wants every current version to have a line.
      Not fixed in PR #40 because any `android/` change makes CD publish a new app release (Umair 2026-11-23: fix it with the
      next real app change). Fix: a v0.3.9 line ("Nothing you will notice: …") in `android/CHANGELOG.md` with that change.

- [ ] **[new 2026-11-15] Capture-screen dots fixed, test on the phone** (`exp/overnight-2026-11-14`; Tayyab reported lag,
      flicker, no dots and floating). Measured on the recordings: the app drew at 29.9 fps (scan_009, `tracking.csv`),
      IQA median 0.2 ms; ARCore's point cloud updates every 100 ms with 7 – 76 points (median per recording) and the same
      point id moves 1.3 – 19.4 cm (median per recording). Fixes: `FeatureMap.java` keeps a persistent smoothed map
      (replayed on the saved `points.csv`: 9,863 settled points at the end of roomAttemptSadness2 vs 41 per update);
      feature dots sized to the screen; coverage dots drawn every frame from world positions (were a 2 Hz Canvas
      snapshot), hidden while tracking is lost, voxel search off the GL thread; raw depth stored with the timestamp and
      pose of the frame it came from (`depth/timestamps.csv` records the pairing). Compiled locally (debug APK);
      **not tested on a phone**. On the next recording check `depth/timestamps.csv`: if depth_ts differs from frame_ts,
      the old depth files (named by the acquiring frame) were misaligned.

- [ ] **[new 2026-11-12] Ask Tayyab whether he has unpushed app changes.** GitHub shows none after `6d0cab5`
      (2026-10-26); work only on his PC cannot be seen.
- [ ] **[new 2026-11-14] End-of-recording warning and repeated buzz** (`exp/overnight-2026-11-14`, commit c0d6b07):
      the stop dialog says "Record again?" when the median predicted blur is > 15 px or > 50% of frames were bad, and the
      bad-quality vibration repeats every 3 s. Compiled locally; **not tested on a phone**. `check_capture.py` now FAILs
      the same 15 px case (scan_3028a4de8fa0 passed as READY before).
- [ ] **[new 2026-11-12] Test the new app on the phone** (USB upload D-062, light UI + bottom navigation + Server tab +
      upload checks and Stop D-064): install `adb` on this PC (docs/PROCESSING_GUIDE.md), USB debugging on the phone,
      then an upload over the cable and over Wi-Fi, pulling the cable mid-upload (WAITING → restart), Stop, the
      "not connected" and "upload over Wi-Fi?" dialogs, and every tab. Built by CI only; not seen on a device.
      **Partly done 2026-11-12:** `adb` installed (`~/.local/bin/adb`); scan #3 (classroom, `scan_003_6de634cbb8b2`) recorded with v0.3.6 and uploaded over
      the cable: 815 MB in 22 s at 37 MB/s (Wi-Fi ~1.4 MB/s), all files arrived (server log). Still to test: Wi-Fi
      upload, pulling the cable mid-upload, Stop, the dialogs, every tab.

- [x] **[new] Upload sends every recorded file** — fixed 2026-11-06 (branch `fix/upload-all-files`): the app recorded
      `camera.csv`, `anchors.csv`, `lens_metadata.json`, `camera_characteristics.json` but never uploaded them (found in
      R-028); the app now sends them and the server saves them (optional, so older apps still upload). Not tested on a device.
- [ ] **[new] Test the 2026-11-06 app fixes on the phone** (now **v0.3.5**, released 2026-11-12 with PR #4; D-058 – D-060; also check that an upload now brings `camera.csv`, `anchors.csv` and the lens files): install from GitHub Releases (it installs
      next to the old app; uninstall the old one only after its recordings are uploaded), check whether Play Protect still warns, the server list
      finds this PC, and "Check for updates" installs the next build. Not tested on a device.
- [x] **[new] Move the app code** out of `googleARCore/samples/hello_ar_java/` and Google's Java package — done
      2026-11-12: `android/`, package `com.buildscan3d.app`, `CaptureActivity` (D-063).
- [x] ~~App bug: ARCore depth was stale in newRoomAttemptSadness (every map identical, confidence ≈ 0). Investigate.~~ *(from TODO 2026-10-10)* Closed 2026-11-12: not reproduced on scan #3 (classroom, 2026-11-12) (D-067).
- [ ] **[new] NFR2 / NFR1 on the phone:** install the build with the `iqa_ms` column (`feature/iqa-timing`), record one
      walk of 1–2 min, upload, run `scripts/buildscan check` and copy the NFR1 / NFR2 lines into §4 (COMPLETION_PLAN 1.6).
- [ ] **[new] Test the update flow on the phone (D-068):** after merging, v0.3.6 offers the new build (old dialog);
      on the build after that: prompt with "What's new" at start and after returning, the permission screen continuing
      by itself, "Updated to vX" once after installing. Not tested on a device.
- [ ] **[new] Fill in the room names / numbers** of scans #1 – #3 in §2 "Which recording is which" (not recorded).
- [x] **[new] Quality message twice on the capture screen** (Umair, 2026-11-12): the ARCore sample's bottom snackbar
      repeated the tracking message and covered the bottom navigation; removed, the top banner shows it ("Starting
      tracking" added for the start-up case). Not seen on a device yet.
- [ ] **[new] NFR1 not met** (3.3% dropped, 28.9 fps on scan #3 (classroom, 2026-11-12)): find what drops frames (render thread, depth, IQA
      cost from the `iqa_ms` numbers); turning depth off (COMPLETION_PLAN 1.12) is one option.
- [ ] Tune the IQA thresholds on the phone (predicted-blur warn > 5 px / bad > 10 px is new and untested on device). *(from TODO)*
- [ ] Coverage overlay and tier-2 guidance: show what is left to scan (few viewpoints, ceiling / floor missing, depth
      holes), blur / dark / overexposed, degraded tracking, as an overlay or heatmap. Device test of the coverage overlay not recorded. *(from TODO)*
- [ ] Lock exposure / white balance: not possible through the normal ARCore API (needs the Shared Camera API, a larger
      refactor). Low priority, the bilateral grid absorbs it. *(from TODO 2026-10-12)*
- [ ] Download and preview the finished splat on the phone. *(from TODO)*
- [ ] Consider turning ARCore depth (AUTOMATIC) off if dropped frames persist: 160×90, ~25% valid on this phone, feeds
      only the coverage overlay. *(from TODO 2026-10-23)*
- [ ] Reverted 2026-10-23 at the user's request, notes kept for re-implementation (archive/TODO.md): persistent surface
      + edge map (`SurfaceMap`), live room-layout overlay, autofocus toggle + test, feature-starvation warning, vertical
      plane finding (`HORIZONTAL_AND_VERTICAL`). The backup patch was session-only and is lost. Decide whether to redo any.
- [ ] Build note: Android Studio's JBR is Java 25, which Gradle 8.13 cannot run; build with JDK 21. *(from TODO 2026-10-23)*

### 7.8 Capture protocol (record the next rooms this way)

- [ ] Loop 1 perimeter at chest height facing the centre; loop 2 at knee height tilted up; 360° turns from 2–3 points in
      the middle of the room (fixes room-centre views). *(from TODO 2026-10-10)*
- [ ] In plain rooms keep an edge, corner, light or furniture in frame on walls / ceiling; after a tracking loss go back
      to a tracked area and pause ~3 s. *(from TODO)*
- [ ] Every wall at two heights; slow movement; close passes (30–50 cm) where detail matters; sideways sway while
      turning (168/592 keyframes had no stereo neighbours); closer passes (≤ 3 m) in large rooms; all lights on. *(from TODO)*

### 7.9 IMU fallback (novelty)

- [ ] **[new 2026-11-18] Featureless tracking plan** ([FEATURELESS_TRACKING_PLAN.md](FEATURELESS_TRACKING_PLAN.md), draft):
      gyro rotation check and gap filling in `sfm_colmap.py`, lines / junctions and the `layout.py` room as a map for
      frames without corners, dense matchers / VGGT as quick tests, app guidance. Measured: scan_009's ARCore-lost
      frames have SIFT median 39 (bedroom 526) but as many long lines (6 vs 7) (`texture_probe.py`). **OD-14 open**
      (recommended: steps 0, 1, 6 first). Would answer OD-6.
  - **2026-11-18: option 1 chosen, then continue (D-080).** Built: `gyro_check.py` + `sfm_colmap.py --gyro_thr`
    (newRoom: 0.15° median, 3 of 1,166 frames flagged; scan_009: 330 of 761), `gap_test.py` (gyro rotation through
    cut gaps: 0.30° median at 15 s), app prompts. R-047 (scan_009 with the check): inconclusive, path jumps 51 → 21,
    remaining errors are position / scale. Next: step 4 (position from lines + layout) or the incremental mapper
    on scan_009 (OD-11); the app prompts are not tested on a phone. Progress table: plan §8.
  - **Night 2026-11-18 (scan_009, R-048 – R-051):** incremental mapper (R-048, rejected: locally wrong);
    diagnosis (R-050): SfM positions locally wrong in both mappers, not from wrong matches or timing; ARCore barely
    tracked (gyro correlation 0.34); the IMU is clean. New: `imu_scale.py` (accelerometer scale, VINS-style: newRoom
    −2.8%, bedroom +2.5%, hall −18.7% vs ARCore), `known_rot_pnp.py` + `--place_unplaced` (R-049, inconclusive),
    `gyro_pairs.py`, gyro bias estimate, `rot_sfm.py` (gyro rotation + accelerometer positions, R-051: rejected,
    blurrier, scale 2–3× off). **Best scan_009 model: R-047**, now in the viewer as `scan-009-gyro`. Open for Tayyab:
    allow VGGT (learned poses; code + weights in `C:\Users\tyb\.cache\buildscan`, running it needs his OK) or
    re-record the room (slower, more light, floor in view). Scale of scan_009 remains unknown.
  - **Night 2026-11-19 (scan_009, R-052, R-071, R-072):** `prior_ba.py` (BA of a sensor-based path with gyro /
    accelerometer relative priors; a free BA undid the gyro: 106 of 706 frames > 2°) → R-052 (698 frames, +0.5 dB vs
    R-051, ≈ R-047, loop not closed). Loop check: pairs > 120 s apart disagreed with the gyro by a consistent 14° yaw
    (gyro bias error). `gyro_loop_bias.py` (bias from all image pairs' 5-point rotations: 14.6 → 3.5°) +
    `rot_sfm.py --bg_json --max_dt 300` + `prior_ba.py` → **R-071: 680 frames, loop closed (3,625 of 5,603 end points
    shared with the start), first scan_009 model whose scale check says "ok"**; training-view PSNR ≈ R-047; in the viewer
    as `scan-009-loop`. Scale still unknown (estimates 0.37 – 0.64 m per unit: ~2× too large; not applied); layout not
    a clean rectangle. R-072 validation on newRoom: the recipe cuts the position error of the sensor path from 72 to
    31 cm median (normal SfM is far better where it works). Open: VGGT (needs Tayyab's OK), re-recording, a scale
    source, lines / layout for the IMU-only stretches (45 – 60 s, 90 – 105 s have ~0 matched points), cleanup of the
    scan_009 experiment folders (disk 9 GB free; ask).
  - **2026-11-19 (day): `master` merged into this branch; next steps planned** in
    [FEATURELESS_TRACKING_PLAN.md §9](FEATURELESS_TRACKING_PLAN.md):
    - [ ] 9.a E1 table: cut-gap ATE and frames placed for normal SfM, gyro check and the sensor-path recipe, on 3 rooms
          plus scan_009. Target 11-22. Needs an E1 owner.
    - [ ] 9.b scan_009 scale: `layout.py` height on R-071, a tape visit, `tape_check.py`.
    - [ ] 9.c sharp re-recording of scan_009's room.
    - [ ] 9.d pipeline fallback option, only if OD-15 = a.
    - [ ] 9.e lines / layout for the IMU-only stretches, shared with COMPLETION_PLAN 4.11. W3, only if G2 is met.
    - [ ] 9.f VGGT, if Tayyab approves.
    - [ ] 9.g ship the corner prompt in the next app release.
    - [ ] 9.h report section.
    - [ ] `sfm_colmap.py` after the merge (D-071 levelling + `--sim3 none`): re-run one export to check (only
          `py_compile` so far).
    - [ ] `tests/test_changelog.py` fails on `master` too: v0.3.9 was released with an empty "Unreleased", so its entry
          is "No changes listed". CI will be red on the next push. Fix: release notes for v0.3.9 (Umair's release).
  - **2026-11-20: video point tracks (R-073 – R-081); best scan_009 model so far (R-081, `scan-009-tracks` in the
    viewer, "much better than the old one" per Tayyab).** `video_tracks.py`, adaptive priors in `prior_ba.py`
    (newRoom 31.1 → 16.2 cm median, p90 68.4 → 29.6), track directions in `rot_sfm.py`; 90 – 105 s fixed, 45 – 60 s
    still without texture. Ranked next steps in [FEATURELESS_TRACKING_PLAN.md §10](FEATURELESS_TRACKING_PLAN.md):
    - [x] 10.a held-out baseline (2026-11-20, R-082): 69 of 622 frames held out (`s10_test.txt`: 6 stretches of 3 s +
      8 still frames); held-out PSNR 20.80, SSIM 0.874, flatness 8.18 cm (R-081, which saw those frames: 23.98 / 0.909 /
      5.98). The planned every-8th split was replaced by stretches + still frames (§10.5). Orbit sheet: `eval_offpath.py`
      room-centre views (`eval_r082/centre.jpg`) instead of a separate orbit.
    - [ ] 10.b rolling-shutter rectification from the gyro (shear median 8 px, p90 17 px), full re-run.
    - [x] 10.c iterate tracks ↔ path (2026-11-20, R-085): 647 → 676 → 656 cameras, support thinner, 45 – 60 s
      unchanged; oscillates, rejected; R-080's model stays best.
    - [x] 10.d `--pose_opt` on scan_009 (2026-11-20, R-084): held-out 20.20 vs 20.80; with test-pose alignment
      (`eval_align.py`) 22.39 vs R-082 22.64: no gain, rejected for now. Alignment shows held-out SfM poses ~2° off.
    - [x] Free disk on the 3070 PC (2026-11-21, Tayyab chose): all 19 `mono_prior/` folders under `dataset/` (17.9 GB;
      rebuilt by `run_v8.py`'s prior stage in ~3.5 min), the R-083 / R-084 work folders (evaluations kept in
      `scan_009_057ed3beb4fc/s10_eval/`), and the checkpoints + TensorBoard logs of the three `outputs/` runs that
      have an exported `export/splat.ply` (room2 baseline, roomAttemptSadness run1, roomAttemptSadness_fast run2).
      Freed 22.8 GB, 23.9 GB free. Kept: the 17 other `outputs/` checkpoints (no exported copy; ~8 GB of TensorBoard
      logs there too), older experiment folders.
    - [ ] `run_v8.py`: option to keep the checkpoint / write the refined poses when `--pose_opt` is on (R-084 lost them).
    - [ ] 10.e geometry for off-path views. First part done 2026-11-21 (R-086: planar 0.5, depth / normal 0.1):
      flatness 4.98 vs 8.18 cm, aligned PSNR 21.85 vs 22.65, a flat sheet blocks the 134 s view; inconclusive.
      Near-camera pruning coded and tested 2026-11-21 (`--path_prune 0.1`, R-089 / R-090: no cost, blocked views
      7 → 0) and the flatness guard (`eval_offpath.py` blocked views). Still to code: layout planes.
    - [ ] 10.b rolling shutter: 10.b-1 done 2026-11-21 (R-087, rectified keyframes on R-080's cameras): aligned 22.22
      vs 22.65, 51 – 53 s +1.6 dB, flatness 4.18 cm, blocked views at 134 / 186 s; inconclusive, most promising.
      R-089 (rectified + pruning): 51 – 53 s +2.6 dB, overall −0.4. 10.b-2 (R-091, SfM on rectified keyframes):
      rejected, 45 – 60 s still 0 – 1 obs per camera, fewer cameras than R-080; not trained.
    - [x] Run-to-run spread (2026-11-21, R-088, R-082 repeated): ~0.1 – 0.25 dB overall, ≤ 0.9 dB per stretch, 1.5 cm
      flatness.
    - [x] 10.f per-frame motion blur from the gyro (2026-11-20, R-083): held-out PSNR 20.86 vs 20.80, sharpness 0.43 vs
      0.28, flatness 9.85 vs 8.18 cm, +6 min training. Inconclusive; keep `--blur_gyro` or not: Tayyab.
    - [x] Depth priors for frames without SfM support (2026-11-21, R-092, `mono_prior.py --fill_scale`): 77 frames
      had no depth / normal prior at all; filled with a time-interpolated scale (5.3 % leave-one-out error).
      Flatness 9.92 → 6.77 cm, aligned PSNR −0.26 dB; kept for Tayyab's inspection.
    - [ ] §11 plan (2026-11-21, FEATURELESS_TRACKING_PLAN §11): one consistent room geometry first. 11.a VGGT test on
      45 – 60 s (needs Tayyab's OK to run the downloaded code), 11.b room planes, 11.c depth guidance rendered from one
      geometry, 11.d cameras placed against the planes, 11.e off-path judging (orbit renders, depth agreement, final
      models on all frames). Tayyab: R-092 looks almost worse than R-081 in the viewer.
      11.a done 2026-11-21 (R-093, D-081): VGGT cannot place the blank-wall frames (rotation 3.5 – 10° off per step
      on the blank wall, 0.6 – 0.9° on texture); its depth is ~3× more consistent across frames than the Metric3D
      priors (5.3 % vs 15.1 %). Next 11.b.
      11.b (2026-11-21): the sensor camera path's scale drifts ~2× along the walk (room height 8.3 → 4.6 units);
      `scale_drift.py` corrects it with the room height; R-094 trained on the corrected path, paused before its
      evaluation; evaluated later: aligned 22.59 = R-090 (22.63). 11.c (R-095, `plane_prior.py`): depth disagreement
      6.8 → 3.6 % but aligned 21.53 (−1.06 dB): rejected, the plane set still holds parallel copies of walls
      (horizontal drift). Next: 11.d (walls seen at different times made to coincide), then 11.c again.
      **11.d done 2026-11-22 (R-096): first clear gain.** R-094's model had almost no point tracks between distant
      times, so its BA never saw the loops; 852 verified pairs >= 60 s apart existed in rot_sfm's cache.
      `loop_path.py` re-solves the camera centres with them (held-out pairs >= 60 s: 7.0 → 2.5°), `prior_ba.py
      --pair_priors` keeps them in the BA. Aligned **22.67 → 23.63 dB** on the same 63 held-out frames, no stretch
      worse; off-path room-centre views coherent in 6 of 8 directions (`offpath_views.py`, 11.e). Walls still thick.
      R-097 (second matching round, `loop_match.py`): 134 – 137 s broken by new pairs, rejected; needs a stricter
      pair check. R-098 (11.c second form, `prior_consistency.py`): equal (23.61), not adopted. R-099: R-096's recipe
      on all frames for the viewer.
    - [x] Tayyab looked at R-099 (`scan-009-loops`) in the viewer (2026-11-22): "miles better ... MUCH more like the
      real room". Still wrong: off-angle views, splats detached from walls / doors, floating splats in the bathroom
      doorway blocking the view inside, missing floor splats in the middle of the room (maybe not filmed). Not
      measured: these are his visual findings.
    - [x] Plan step 1, floaters (2026-11-22, R-100): `clean_splats.py --mono` (depth priors + BA points as free-space
      evidence) on R-096. See-through rule alone: aligned 23.54 vs 23.63 (clears mid-air splats above head height);
      the camera-path radius rule removes real wall (−0.23 dB). The bathroom doorway (125 s) is a smear even from its
      own training pose and is unchanged: the 100 – 150 s stretch fits worst (cameras), not floaters. Not adopted.
    - [x] Plan step 4, pose refinement in training on R-096 (2026-11-22, R-120): aligned 23.96 vs 23.63, SSIM 0.896 vs
      0.888, +1.8 min training. Kept.
    - [x] Plan step 3, second loop round with a pair check (`loop_path.py --gate 10`, 2026-11-22, R-121): 30 – 90 s
      +1.6 – 1.8 dB but 134 – 140 s broken again (15.83, as R-097). Cause: the camera model has a hole at 125.4 – 133.2 s
      (35 keyframes, none placed: blur 12 – 42 px, no ARCore pose); the bathroom doorway (125 s) is at its start.
      **Corrected 2026-11-25:** ARCore tracked all of them and they are only mildly blurred (view into the bathroom,
      TRAINING R-121 correction); they look recoverable with ARCore's poses.
      Rejected. The doorway is a limit of the video there (fast blurred pan), not of the method.
    - [x] Plan step 5 (2026-11-23, R-122): R-120's recipe on all frames, 32.8 min, in the viewer as `scan-009-poseopt`.
    - [ ] Tayyab to decide: whether to try a hole-aware second loop round, or move to the analyzer (D-095) now.
    - [x] Disk on the RTX 3070 PC (2026-11-23, Tayyab "do whats best"): 4.2 → 7.0 GB free. Deleted R-121's bulk
      (`mono_prior/`, `images/`, `undist*/`), R-100's three cleaned copies (`splat_clean_r100*.ply`) and the input
      copies of `work_v9pfz` for rejected / inconclusive runs (`work_v9plg`, `plm`, `pcs`, `ppl`, `pfk`, `pfs`, `pfo`);
      list in `dataset/scan_009_057ed3beb4fc/cleanup_2026-11-22.txt`. Not touched: Windows Temp (3.4 GB), `outputs/`
      (14 GB of old checkpoints, kept on purpose 2026-11-21). The 13 → 4.2 GB drop on 2026-11-23 was not investigated. Analyzer must detect path
      holes (unplaced keyframes, blur, ARCore state; R-121 correction 2026-11-25).
    - [x] 2026-11-23 – 25 on `exp/featureless-holes` (TRAINING R-123 – R-130): R-123 hole-aware loop round rejected
      (holes not the cause of the 134 – 140 s break); R-124 analyzer first part (`analyze_recording.py`: labels and
      route agree with the four test recordings; thresholds untuned); R-125 / R-126 room-plane anchoring (flatter
      walls 6.1 → 3.8 cm, −1.9 dB; Tayyab: R-120 and R-126 "both suck"); R-127 hole frames placed from image
      directions + gyro (`direction_fill.py`; `arcore_fill.py` rejected: ARCore positions unreliable here, a 3.48 m
      jump at 127.5 s) rejected (−0.74 dB); **R-128 denser frames in weak windows (`densify_frames.py`): 24.25 vs
      23.96, +3.6 min, kept, best so far, in the viewer as `scan-009-dense`**; R-129 learnable blur (`--blur_learn`)
      no gain; R-130 Depth Anything 3 (D-097): fails on the blank wall like VGGT, tracks the doorway (2.6°), depth
      3 – 16× more consistent than the Metric3D priors.
    - [x] Next (Tayyab chose 2026-11-26): DA3 depth as the training priors, done (R-131 – R-133, TRAINING): DA3-LARGE
      is non-commercial, so only commercial-use weights (D-098; Metric3D is non-commercial too); DA3-BASE
      (Apache) depth 2 – 5× more consistent than Metric3D, doorway poses not usable alone (13° median); R-132
      (DA3 priors, unsupported frames filled) 23.76, blank wall at 55 – 60 s worse (Tayyab); **R-133 (DA3 +
      confidence cut-off 1.1) 24.25 = R-128, best 60 – 90 s so far, 2.6 min faster: the DA3 candidate**, in the
      viewer as `scan-009-conf` (Tayyab to look at the blank wall). Featureless work paused 2026-11-26 for the
      viewer and the automatic pipeline.
    - [ ] DA3 poses for the doorway frames (MapAnything Apache with ARCore poses, or BASE steps pinned to the gyro);
      the 134 – 140 s stretch is still the weakest (R-133 17.11 vs R-128 18.30).
    - [ ] **[in progress 2026-11-27] Automatic pipeline (D-099): `run_full.sh <rec> <tag> -- --auto`** on
      `feature/auto-pipeline`: recipe fixed, `analyze` + `densify` stages, DA3 priors with the cut-off, frame budget
      (window from the video length), sem2d frame step capped at ~300 frames, choices in `gs_<tag>/auto.json`. Test
      bench: R-134 bedroom (running), then scan_009 and newRoom. Not automated yet: the sensor-path camera chain for
      recordings SfM cannot place (reported as route "sensor path").
      - [x] 2026-11-27 / 28: sensor path automated (`sensor_path.py`, `sensor` stage). Test bench: **R-134 bedroom**
        end to end, no hand choice, kept (104.0 min of stages; 5 walls, 19 fixtures); **R-135 scan_009** end to end
        in 71.9 min, sensor path chosen by the analyzer (41 → 81 % placed), but 23.07 vs the hand chain's 24.46 dB
        (61 common frames) and layout 7.28 m: inconclusive. **R-136 newRoom** (tape room, kept): aligned 25.35 vs v9_e2e 25.51 on the same 49 held-out frames, closed room
        6.575 x 4.380 m, tape -1.86 %, 106.1 min.
      - [x] 2026-11-28: layout fallback for implausible floors / ceilings (R-137, `layout.py`): R-135 7.28 → 5.25 m (first pick 3.56, raised by D-072 on floater walls),
        textured rooms unchanged. R-138 queued: R-135's downstream again with it.
      - [x] 2026-11-28 **R-140 `--track_dirs`** (R-079's track-direction rot_sfm, left out of `sensor_path.py`):
        rejected, 21.81 vs R-135 23.03 on 56 common frames, blank wall 17.60 vs 22.21 (fewer cameras kept); opt-in only.
      - [x] 2026-11-28 **R-145 ALIKED matches** (`--auto --sfm_args "--feature aliked"`): **25.68 vs the best hand-made
        model 24.46 (R-128) / 24.47 (R-133) on 61 common held-out frames**, blank wall 28.66, 134 - 140 s 22.05 (every
        earlier run failed there); SfM placed 78 % (SIFT 41 %); 91.5 min; SfM 20.5 vs 3.9 min. Kept: best scan_009 model,
        automatic. OD-17 for Tayyab (ALIKED for the sensor route or for every recording).
      - [x] 2026-11-28 R-144 photometric init inside `--auto` (OD-10): init 17.5 → 7.5 min (7.1 net), -0.22 dB on the
        same 62 frames; inconclusive, Tayyab to decide.
      - [x] 2026-11-28 `run_full.sh` exited 1 after finished long runs (GPU monitor + EXIT trap under `set -e`): fixed
        (4beb0a3); the server reads that exit status.
      - [ ] Tayyab to decide: `--auto` as the recipe for new rooms / the server (after R-136); OD-10 in `--auto`.
    - [ ] Disk on the RTX 3070 PC: 1.9 GB free after R-130 (2026-11-25); candidates to slim (Tayyab's call): R-127
      (`work_v9plb*`, rejected), R-129 (`work_v9plk*`, not adopted), R-126 (`work_v9pla*`), R-123 (`work_v9plh*`),
      R-121 (`work_v9plg*`).
    - [ ] Analyzer-driven pipeline (D-095, [PIPELINE_ANALYZER_PLAN.md](PIPELINE_ANALYZER_PLAN.md)), after steps 4 / 3:
      analyzer `analysis.json` on the four test recordings; route decision and the sensor-path chain inside
      `run_v8.py` with per-step checks; test bench vs the reference results; frame weighting by camera trust.
      Processing time is a primary target: measure the sensor-path chain end to end (not measured yet).
    - [ ] Tayyab to decide: R-096's loop closure as part of the sensor-path recipe (OD-15); which scan_009 model the
      viewer shows (R-099 proposed); whether to retry the second loop round with a pair check (e.g. reject pairs whose
      direction disagrees with R-096's path by > 10° before solving).
    - [x] Free disk on the 3070 PC (2026-11-22, Tayyab chose option 1): 3.8 → 14 GB free (`df`). Deleted the
      regenerable bulk (`mono_prior/`, `images/`, `undist/`, `undist_fast/`) of six rejected / inconclusive scan_009
      runs (R-086 `v9pfk`, R-087 `v9pfs`, R-089 `v9pfo`, R-095 `v9ppl`, R-097 `v9plm`, R-098 `v9pcs`; their
      `splat.ply`, `sparse/`, eval folders and logs kept) and four rejected folders not used by later runs
      (`track_loop_r085`, `work_v9pfs2_sfm`, `work_v9pfv_sfm`, `work_v9pfw_sfm`). Exact list with sizes:
      `dataset/scan_009_057ed3beb4fc/cleanup_2026-11-22.txt`. Not touched: the other room datasets
      (newRoomAttemptSadness 36 GB, roomAttemptSadness2 17 GB, roomAttemptSadness 6.8 GB: could move to an external
      drive) and ~14 older scan_009 folders (~8 GB, verdicts not checked). The project uses ~110 GB of the 931 GB C:.
    - [ ] 10.g planes for 45 – 60 s (a re-recording is not possible: the site is far away, Tayyab 2026-11-21).
      Next candidates: layout planes from the tracked walls, and placing the featureless frames by matching their
      depth maps to those planes; or leaving the untrackable frames out of training (Tayyab's idea).
    - [x] Commit `video_tracks.py`, the `rot_sfm.py` / `prior_ba.py` options and the R-081 viewer entry, MAP.md entry
          (2026-11-20, `5b26db3`, `d8678ae`, `666c74a`).
    - [ ] Move `stretch_stats.py` / `track_dir_check.py` / `render_compare.py` from the agent's scratch folder into
          `src/arcore3dgs/` with 9.a's tools.
    - **Code for 10.a – 10.f written 2026-11-20, nothing trained** (§10.5 has the run order): `rs_rectify.py`,
      `track_loop.py`, `still_frames.py`, `--pose_opt`, `--blur_gyro`, `--train_args`. Not coded: floater pruning and
      layout-plane constraints (10.e). Found: scan_009's blur model had no motion for 398 of 622 frames (ARCore lost).
      Tayyab 2026-11-20: this week is not the evaluation week; §10 goes first.

- [ ] Tune BA pass 2 so it keeps PnP accuracy (8.2 px → 15.1 px after BA): weaker within-segment ARCore priors after a gap. *(from TODO 2026-10-10)*
- [ ] Use bridged fallback frames in training with per-frame pose refinement (only re-aligned segments are used now). *(from TODO)*
- [ ] Decide whether the v9 pipeline (`run_v8.py`) should use the fallback at all, now that SfM registers 1165/1166 frames.

### 7.10 Web viewer and delivery

- [ ] **[new 2026-11-28] Look at the usability pass in a browser and on a phone** (`feature/ux-security`,
      docs/HCI.md §2): progress bar, error card, Controls panel (`?`), Esc, measuring prompt, phone layout. Checked
      only headless (software rendering), not with a screen reader.
- [ ] **[new 2026-11-28] Usability test with 3 – 5 new users** (open a scan, measure a wall, find a socket; time and
      errors per task) for the report (docs/HCI.md §4, UAT).
- [ ] **[new 2026-11-15] 7 real models in the project list** (bedroom labelled, lecture hall, scan 009 R-045 and pose-free
      R-046, newRoom v9e2e / v6 / v3; prototype/web-ui/STATUS.md §4). Model files and thumbnails are git-ignored, so they
      exist only on Tayyab's PC. Not looked at in a browser; roomAttemptSadness2 v3 (359 MB PLY) not added.

- [ ] `.spz` (in use) vs `.ksplat` (proposal, Zaid's branch): team decision. If `.ksplat` stays: finish v2-B/v2-C/scan-2
      renders, quality vs photos, FPS on the target laptop. [feat/splat-compress README]
- [x] **[new 2026-11-16] Show every processed scan in the viewer with its semantics** — done 2026-11-19 (D-074, moved to §8):
      the Projects tab lists every bundle in `public/scans/` (`/api/scans`). The FR10 size card is still not checked in a browser.
- [ ] **[new 2026-11-19] Check an auto-listed scan in a real browser** (`/viewer/run-<folder>`): splats, Scan Layers,
      camera start (middle of the fixtures, 1.5 m above the floor; ARCore origin when there are no fixtures). Headless
      software rendering was still loading after 60 s.
- [ ] **[new 2026-11-19] Online site (D-076): web UI on Vercel (`https://build-scan-3d.vercel.app/`), bundles on Cloudflare R2**,
      one prefix and index per person so Tayyab can publish too. #26 Umair: bucket, public URL, keys in `.env`, Vercel
      env `SCANS_BASE_URL`, OK to push. #27 / #28 / #29 code done on `feature/vercel-deploy` (not pushed; tested with
      a local folder bucket only). #30: bucket CORS, first deploy, browser check on a second machine. Then: `pip install
      boto3` in `bs-server`; Tayyab's own token and `PUBLISH_OWNER=tayyab` on the 3070 PC (needs Tayyab).
- [ ] **[new 2026-11-19] Next steps as issues** (#31 – #38): server runs `run_full.sh` (#31, OD-7 for Umair), auto-publish
      finished jobs within the 10 GB cap (#32), job progress to app / dashboard (#33), signing key backup (#34, Umair),
      SfM memory on long recordings (#35, R-038 / R-058), processing-time table and repeat runs (#36), `.spz` vs
      `.ksplat` + unmerged branches (#37, team), web UI empty / error states and known issues (#38).
- [ ] **[new 2026-11-19] Hand-written `scan-008` card on Vercel** opens only once `scan_008_…_r1116w9` is published
      (or the card is retired for the auto-listed one): Umair's choice.
- [ ] **[new 2026-11-19] Room names on the auto-listed cards** (they say "Scan #N · tag"): e.g. a small names file next
      to the scan register, once the rooms are written down in "Which recording is which". Published cards take a room
      name already (`scripts/buildscan publish <scan> <tag> --room "<name>"`).
- [x] **[new 2026-11-26] Viewer lag on heavy scans** (Tayyab: brick room lags, flickers): done 2026-11-26 on
      `fix/viewer-perf` (not pushed: the agent's push is blocked; Tayyab to push + PR): the hover readout raycast
      froze the page 150 – 290 ms per call; scan #7 drag worst frame 195 → 15 ms, 168 → 1,174 frames in 6 s
      (prototype/web-ui/STATUS.md §4).
- [ ] Adaptive splat budget / level of detail (FR9, NFR5). [proposal v4] Spark 2.3.1 builds a LoD tree at load
      (`SplatMesh({lod: true})`, `SparkRenderer({enableLod})`): to measure on the brick room when the GPU is free.
- [x] **[new 2026-11-28] `.spz` quality against the `.ply`** (5.4 / E6, input to OD-1): done (R-139): 92.3 - 92.8 %
      smaller, render difference 35.8 - 36.5 dB PSNR, SSIM 0.98 - 0.99 on four models.
- [ ] Viewer times (E5, desktop): R-143 measured 3 scans (load 2.2 - 7.6 s, worst frame 15 ms); the 4 local bundles
      did not load through junctions in the test worktree: repeat with copies. Phone not measured.
      Smaller `.spz` (fewer SH bands / opacity cut) only −13 – 18 % (measured 2026-11-26).
- [ ] Web-UI step 8 (S9 empty and error states) and the known issues in `prototype/web-ui/STATUS.md` §6 (list view toggle,
      `globals.css` conflicts, stub buttons, every floor-plan room opens the same model, inert measurement types, missing thumbnails).

### 7.11 Reports and evaluation with users

- [ ] **Final report (due 2026-12-06, Tayyab)**: draft started 2026-11-28 in `report/final-eval/BuildScan3D_Final_Report/`
      (copy of the mid report source; new chapters Iteration 2 and Evaluation with `TODO(name)` markers; builds to
      123 pages). Plan to the deadline: [FINAL_PLAN.md](FINAL_PLAN.md).
- [x] E1 (2026-11-28): ARCore path vs our cameras (R-141: median 0.14 - 0.25 m on textured rooms, 26 % tracked on
      scan_009); visual-only vs ARCore-guided SfM (R-142, `--pairs visual`): same frames placed on both rooms, newRoom
      solutions 0.23 m apart. In the report draft.
- [ ] User acceptance test with the construction stakeholder in semester 2. [proposal v4 §10]

## 8. Done

Dated milestones; details in [LOG.md](LOG.md), reasons in [DECISIONS.md](DECISIONS.md), evidence in P&S.

- **2026-08-20 → 09-07: proposal and planning.** Requirements, workflow docs, proposal v1–v4, defence slides, POC requirements.
- **2026-09-07 → 09-10: web prototype** (Umair): Next.js dashboard, project detail, 3D viewer with mock MEP layers and X-ray,
  measurements, floor plans, comparison view, notifications, new-project flow (prototype/web-ui/STATUS.md).
- **2026-08-28 → 09-14: capture app v0** (record / stop, metrics + video).
- **2026-09-28: first fusion pipeline** (Metric3D depth + ARCore poses → dense prior, interactive viewer).
- **2026-10-07: metric ARCore → 3DGS pipeline** with own GPU bundle adjustment, plane-sweep MVS, two-pass fusion and a
  depth-supervised gsplat trainer; per-frame pose interpolation and sync checks (P&S §1–4.2). Live IQA in the app.
- **2026-10-09/10: baseline diagnosis.** Trainer underfit (wrong depth target, degenerate splats); new recipe; splatfacto
  became the trainer (P&S §4.4–4.5, archive/Training_Analysis.md). Tracking-loss filtering, low-texture IQA warning,
  coverage overlay, `check_capture.py`, PocketGS-style prior, viewer FOV fix, IMU fallback (P&S §4.3–4.10).
  Unit tests + CI/CD (Zaid). ARKitScenes experiments on Kaggle (Zaid, unmerged branch).
- **2026-10-11: root cause found, SfM v3** — COLMAP poses + lens, ARCore for scale; bilateral grid; validated on room 2;
  tape measurements (P&S §4.11–4.12). Rolling shutter and lens residual checked: negligible (P&S §4.8).
- **2026-10-12: v6** (gyro-aware sharp frames, dense MVS init, grad 0.0006) — mid-report headline. App logs exposure,
  rolling-shutter skew, anchors, lens metadata; recording performance fix; upload & process UI; configurable server URL.
  FastAPI processing server and RunPod client (Umair). Folder clean-up (`scripts/`, `docs/proposal/`, `docs/progress/`, `Flow.md`).
- **2026-10-15 → 10-19:** mid-report table of contents; server dry-run mode, auto-discovery, gallery, upload progress,
  in-app update checker, auto-versioned APK releases (v0.2.0 → v0.3.2), remote-GPU (SSH) mode, job logs / retry, pod
  watchdog, GPU Docker image workflow (Umair).
- **2026-10-21: v7 fast pipeline** (25 min) rejected on quality; ARCore-guided matching and pose-refined `fair_compare.py` kept.
- **2026-10-22: mid report** corrected, shortened (107 → 85 pages), rewritten, compiled (Umair); `.env` untracked;
  RunPod GPU selection, existing-pod support, watchdog default raised.
- **2026-10-23: app capture-quality audit** (predicted-blur IQA, HDR light estimation off, IQA stride 8, demo pawn
  removed, dropped-frame reporting); overlay features built and reverted the same day.
- **2026-10-24: v8** (DashGaussian + SfM-anchored priors, 30 min training), off-path evaluation, Metric3D fp16, Spark web
  viewer with `.spz` (P&S §4.15).
- **2026-10-26: v9** (retrieval SfM, fast MVS, planar prior, motion-blur model, `layout.py`), 96 min end to end (P&S §4.16).
  Also done from the old TODO: "register more frames in the fast SfM" (retrieval → 1164/1166), planar-region priors,
  the ALIKED + LightGlue test (rejected).
- **2026-10-27: semantics v9, PGSR-lite, meshing, scan layers in the viewer; final all-frames model** (P&S §4.17).
  Prior-alignment bug fixed; checkpoints + resume after a power cut. "Retrain the v9 recipe on all frames" from the old TODO is done.
- **2026-11-02: room check** of the fixtures by the user: 13/15 correct, recall 13/17.
- **2026-11-03: semantics v10** (15/15 correct, 15/17 found) (P&S §4.18). `.ksplat` compression experiments (Zaid, unmerged).
- **2026-11-06: PR #1 into `master`** (v9/v10 + records + Linux port, CI green after D-054 / D-055); fully merged
  branches deleted (D-052). Ubuntu PC set up (R-027), `scripts/setup_linux.sh`, Tailscale SSH, auto-suspend off.
- **2026-11-06: per-environment requirements files**, README setup, docs for v10. Project reorganisation: these logs,
  `report/mid-eval/`, archive, CLAUDE.md workflow and member sections.

- **2026-11-06 (evening): upload server on Linux and app fixes** (Umair): `scripts/start_server.sh` in env `bs-server`;
  server logs devices, upload progress, failures and answers a UDP server search (D-057). App: server search that
  works on the /19 lab Wi-Fi, in-app updates, own package name `com.buildscan3d.app`, release builds signed with a
  private key (D-058 – D-060). Branch `fix/android-app`.

- **2026-11-12: app v0.3.5** (Umair, PR #4): uploads `camera.csv`, `anchors.csv` and the lens files; server accepts
  them as optional. Per-run web bundles gitignored (D-061). R-030 (lab room, 50.2 min on Linux) logged.

- **2026-11-12: app restructured and restyled** (Umair): moved to `android/` with its own package (D-063); USB upload
  route with connection bar, speed, automatic restart (D-062); light theme from the logo, bottom navigation, Server
  tab, upload checks and Stop (D-064). `exp/first-linux-run` and `feature/usb-upload` merged to `master`.
- **2026-11-12: ARCore depth bug closed** (Umair, D-067): scan #3 (classroom, 2026-11-12) has 782 distinct depth maps, 87% valid; the stale
  maps of newRoomAttemptSadness (realme, older app) did not come back.
- **2026-11-12: app v0.3.7** (Umair, PR #6): update prompt at start and on return with the release notes, "What's new"
  after an update, changelog per release (D-068), numbered scans (D-065), `iqa_ms` (NFR2), single quality banner.
  Released by CD with the changelog as notes; not tested on a device.

- **2026-11-12: scan #3 processed** (Umair, R-031): first v0.3.6 room, full pipeline in 81.0 min on this PC, 875 / 885
  frames, layout height 2.74 m, 21 fixtures; model in `saved_models/2026-11-12_r1112_scan003/`. Held-out split tool
  `make_split.py` for scoring speed runs (D-070).
- **2026-11-12: layout fixed for tilted models** (Umair, Step 4 session): the Sim3 to ARCore took its rotation from camera
  centres only and left scans #2 / #3 9.1° / 12.1° off gravity (R-032). `sfm_colmap.py` now levels with ARCore gravity
  (D-071, R-033); `level_model.py` levels trained models (R-034); the ceiling may not lie below the wall tops (D-072).
  scan #3: 2 → 4 walls, 0 → 3 corners (89–90°), 2.74 → 2.52 m (R-035); scan #2: 1.50 → 2.41 m (R-036). Viewer:
  fixture size card (FR10). `fixture_checklist.py` for the per-room fixture check.

- **2026-11-19: every processed scan in the web Projects tab** (Umair, D-074): `/api/scans` lists the bundles in
  `public/scans/` with their numbers, run IDs and layout plans; `/viewer/run-<folder>` opens them. `feature/step4-layout`
  fast-forwarded to `feature/viewer-scan-008`; work on `feature/viewer-all-scans`. R-039 / R-040 written up.

- **2026-11-19: Step 4 issues** (Umair, agent; R-053 – R-056): no-roof detection (#8), doorways / window openings
  from wall gaps (#9), closed-room check and floor area only for a closed outline (#10), floor plan .svg / .dxf /
  .json as stage 16 (#12), check sheets with rejected candidates (#13); optional `--raised_max`, `--clean_ceiling`,
  `--floor_win`, `--infer_gap`, `--square`: **on in `run_full.sh` since 2026-11-19 (D-075, Umair)**; first full run with them: R-057 (next session).

- **2026-11-19: R-057, the D-075 defaults on four rooms** (agent for Umair, tag `r1119c`, 16.7 min, no errors):
  scans #7 and #8 become closed 4-wall rooms (17.99 / 26.44 m², corners 87.7–89.7°), scan #3 floor tilt 1.95° → 0.29°,
  ceilings 4.3 → 0.04 cm rough; newRoom unchanged. Scan #8 lost a switch + socket plate that sat on corner furniture
  (Umair: furniture, so right). `r1119b` bundles archived; #11 and #18 closed. With `--square` the plan files are
  `layout/plan_square.*`.
- **2026-11-23: run times in one table** (Umair, agent): `docs/progress/runs.tsv` (116 rows, R-001 – R-104, with Tayyab's R-047 – R-052 and R-071 – R-100 from `docs/featureless-tracking-plan`), `scripts/run_times.py update / check / show`, 12 tests; check over three branches 0 FAIL; open runs closed (R-059, R-061, R-064, R-102 …); rule in CLAUDE.md §6 (D-090).

## 9. Known limits

- **One room.** Every v9/v10 result is on newRoomAttemptSadness; the semantics rules were tuned on it.
- **Speed.** 96 min plus ~40 min for semantics; the v10 tile pass made the 2D stage 5× slower.
- **Metric scale** is 1.5–2% off on the fast SfM and not stable between SfM runs (v3 with exhaustive matching: 0.1%).
- **Semantics margins are thin** (CLIP 0.45–0.47 vs 0.5 threshold).
- **Open doorways without a door leaf** are found only when their frame strips merge; plain wall gaps aren't used yet.
- **Ceiling** is the weakest surface (seen at grazing angles from chest height).
- PGSR is single-view only ("lite"); the multi-view terms that remove faint wall stripes aren't implemented.
- Fine detail lost to motion blur in the source frames (printer vents) in every model.
- Off-path quality is limited by coverage: nothing reconstructs well where no camera went.
- Only runs on the Windows RTX 3070 PC (section 6).

## 10. Environment gotchas (RTX 3070 PC)

- gsplat's CUDA extension is prebuilt and loaded via `nerfstudio-env/Lib/site-packages/gsplat/csrc.py`; that file explains
  how to refresh it after a gsplat, torch or CUDA upgrade. Without it gsplat recompiles (~15 min) on most launches.
- Open3D 0.20 has broken TSDF fusion (empty meshes, also on Kaggle). Use Open3D 0.19 (`nerfstudio-env`).
- Steam uses port 8080, so the viewer runs on **7010**.
- Nerfstudio pins cached images in page-locked RAM; > 1000 full-res frames (~6.7 GB) fails on Windows with "CUDA out of
  memory". nerfstudio-env is patched to skip pinning above 4 GB.
- COLMAP PatchMatch caches ~7 GB of RAM: never train alongside it on the 16 GB machine. COLMAP writes PLY headers with `\r\n`.
- Never share the GPU with a `--blur` run (up to 5 sub-renders per step), and close the viewer before training (8 GB VRAM).
- `splatfacto-big` thresholds run out of 8 GB VRAM at full resolution (~step 12.5k).
- COLMAP's ONNX models (ALIKED) need cuBLAS 12 + cuDNN 9 DLLs (`tools/cudnn9`); COLMAP ≥ 3.12 needs faiss vocabulary trees (`tools/colmap_dl/vocab/`).
- Windows console: `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8` (Rich cp1252 errors); run Python with `-u` for live logs.
- Power cuts: `geo_splatfacto.py --save_every 2500` + `--resume`; a resumed nerfstudio run is given only the remaining steps.
- `transformers` is pinned to 4.46.3 in semantic-env (newer versions need torch ≥ 2.4 and silently disable PyTorch on 2.1.2).
