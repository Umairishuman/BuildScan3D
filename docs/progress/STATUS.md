# BuildScan3D: Project Status

Last updated: 2026-11-13 by Tayyab (agent): merged `origin/master` into `exp/fast-pipeline`; speed-up runs R-032 – R-038 (renumbered from R-029 – R-035 at the merge), mini-room diagnosis, OD-10, OD-11, new 7.2 items. Before that: 2026-11-12 by Umair (recordings table in §2 "Which recording is which"; NFR1 re-measured on scan #3, NFR2 timing in the app, 1.7 closed D-067, update prompts + changelog D-068, readable `buildscan watch`, quality banner only at the top; earlier the same day: D-062 – D-066).

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
| **scan #3** | `dataset/scan_003_6de634cbb8b2` | 2026-11-12 (uploaded 14:53 over USB) | Umair, Infinix X6833B, **v0.3.6** | Classroom: rows of wooden desks with red seats, projector screen, wooden door, blue curtains, ceiling AC units; room number to fill in | 185 s | R-031 (running) |
| newRoomAttemptSadness | 3070 PC: `dataset/newRoomAttemptSadness` | by 2026-10-10 (first run R-007) | realme RMX5111; who recorded it not written down | Room of the best model (R-023) and semantics v10 | 240 s | R-007 … R-025 |
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
| Room layout | Done on one room | `layout.py` (v9), `structure.py` (older) | Walls (any number), floor, ceiling, corners, dimensions, `plan.png` |
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
- [x] **[new] 1g. All of 1b–1f as one script** — done 2026-11-06: `scripts/setup_linux.sh` (+ `--check`); run here OK, fresh-machine run not yet tested. (`scripts/setup_linux.sh` + env files), so step 2 and the friend's PC reuse it (D-048).
- [x] **[new] 1h(a). First complete run here** — done 2026-11-06 (R-029): Umair's corridor-end recording
      `scan_056fe94d3399` through `scripts/run_full.sh`, all 15 stages, 34.7 min, no errors after the `imu.npz` fix (R-028).
- [ ] **[new] 1h(b). Machine agreement:** copy `newRoomAttemptSadness` from the RTX 3070 PC, run the v9 pipeline, log it in
      TRAINING.md (every setup and run error), and compare with R-020 / R-023 to confirm the machines agree.

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

- [ ] **[new] Optimise the processing pipeline** end to end; measure each change with `run_v8.py`'s stage times and log it.
  - **2026-11-12 (Tayyab's session, branch `exp/fast-pipeline`):** training 42.5 → 28.2 min and dense init 20.1 → 7.5 min
    at equal quality on newRoom (TRAINING R-032, R-033); Metric3D 8.1 → 6.8 min (identical output). Normal SfM + these:
    ~67 min end to end on newRoom (estimate from the measured stages), 48.8 min on the new lecture hall (R-036). The SfM
    shortcut `--skip_retriangulation` lost quality (R-035, rejected). Adoption: DECISIONS OD-10.
  - **[new 2026-11-12] SfM can shrink part of a room (GLOMAP).** R-036's lecture-hall model had a "mini room": ~175
    frames (ARCore lost after frame ~2200, so `--pairs arcore` matched the wrong neighbours) were placed by GLOMAP at
    ~0.38× scale. The incremental mapper (`--mapper mapper`, R-037) keeps the main part correct (581/842 frames) and
    splits off the rest; R-038 trained on it (no mini room, right-side walk missing). To do: a per-frame scale check
    after SfM (SfM depth / Metric3D depth, a block of frames < 0.5× = shrunken part) that warns or falls back to the
    incremental mapper; and do not trust ARCore neighbours after tracking loss. Adoption: DECISIONS OD-11.
- [ ] **[new 2026-11-13] Speed-ups not tested with `--pgsr`** (the best model's recipe, R-023, now a `run_v8.py` flag
      from master) **nor on Linux**: one run of each before adopting OD-10.
- [ ] **[new 2026-11-13] Batched Grounding DINO tiles in `semantic2d.py`** are committed but have never run: compare the
      2D labels with the unbatched output on newRoom and time it (the 38-min semantics stage is the next big cost).
- [ ] **[new 2026-11-13] Fast recipe vs v9e2e on the lecture hall is not known** (R-036/R-038 have no baseline; Tayyab
      is not sure R-038 is better than v9e2e). Umair's R-031 (scan #3, Ubuntu PC, old recipe + PGSR) looks like the
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

- [ ] **[new 2026-11-12] R-030 (`scan_646070948603`, lab room): room height 1.50 m cannot be right.** View the model,
      check which plane the layout took as the ceiling and whether the scale is off; measure one length with a tape.

- [ ] **Second room** (roomAttemptSadness2): full v9 pipeline + semantics (~2 h GPU), then a room check by the user. The
      real test of v9/v10. *(from TODO 2026-10-24 / 2026-10-27)*
- [ ] Full PGSR multi-view geometric + photometric consistency (1–2 days, ~2× training time); removes the faint vertical
      stripes on plain walls. *(from TODO 2026-10-27)*
- [ ] Rolling-shutter modelling and per-frame exposure from `camera.csv` in the blur model (v9 uses a fixed 1/45 s).
      Check whether "Gaussian Splatting on the Move" code ports to nerfstudio 1.1.5 / gsplat 1.4. *(from TODO step 3, 2026-10-12)*
- [ ] Planar + blur together on v6's SfM (only tested together inside the e2e run). *(from TODO 2026-10-26)*
- [ ] Repeat runs to measure run-to-run noise on the hardest off-path frame (one run per setting so far). *(from TODO 2026-10-26)*
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

- [ ] Test v10 semantics on a second room (the real test); the user confirms the 3 new detections (`door_1`, `door_6`, `tube_light_1`). *(from TODO 2026-11-03)*
- [ ] Open doorways (no door leaf) from gaps in the layout walls; windows on room 2. *(from TODO 2026-10-27)*
- [ ] Still missed on newRoom: the socket under the ironing table (never a good candidate) and round light #14 (the
      "clock" decoy wins its votes). [P&S §4.18]
- [ ] Thin margins: false sockets scored 0.45–0.47 in the CLIP check against a 0.5 threshold (real plates 0.69–0.88);
      the 25% switchboard rule rests on 3 plates. [P&S §4.18]
- [ ] Switch plates (8–14 cm) need ~30 confirming frames, so a fast walk past a switch can miss it. [P&S §4.17]
- [ ] Rules were tuned on the same room they are scored on: get an independent score (room 2, then precision / recall
      as in proposal contribution 3). [P&S §4.17–4.18]
- [ ] Per-element dimensions for fixtures in the viewer (FR10). [proposal v4]

### 7.6 Room layout, structure and mesh

- [ ] Edge-based corner / blank-wall detection (gravity-aware lines; the wall–floor boundary + floor plane gives a plain
      wall's position). *(from TODO 2026-10-23)*
- [ ] Right-angle priors and an as-built floor plan export (layout.py has walls, corners, `plan.png`; no right-angle
      snapping or plan export format yet). *(from TODO, Novelty)*
- [ ] `structure.py` ceiling height (2.555 m was probably cupboard tops); `layout.py` supersedes it. *(from TODO, Parked)*
- [ ] Wall 3 and the ceiling stay rough in the mesh (> 2.5 cm, untouched by shell denoising). [P&S §4.17]

### 7.7 Android app

- [ ] **[new 2026-11-12] Ask Tayyab whether he has unpushed app changes.** GitHub shows none after `6d0cab5`
      (2026-10-26); work only on his PC cannot be seen.
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

- [ ] Tune BA pass 2 so it keeps PnP accuracy (8.2 px → 15.1 px after BA): weaker within-segment ARCore priors after a gap. *(from TODO 2026-10-10)*
- [ ] Use bridged fallback frames in training with per-frame pose refinement (only re-aligned segments are used now). *(from TODO)*
- [ ] Decide whether the v9 pipeline (`run_v8.py`) should use the fallback at all, now that SfM registers 1165/1166 frames.

### 7.10 Web viewer and delivery

- [ ] `.spz` (in use) vs `.ksplat` (proposal, Zaid's branch): team decision. If `.ksplat` stays: finish v2-B/v2-C/scan-2
      renders, quality vs photos, FPS on the target laptop. [feat/splat-compress README]
- [ ] Adaptive splat budget / level of detail (FR9, NFR5). [proposal v4]
- [ ] Web-UI step 8 (S9 empty and error states) and the known issues in `prototype/web-ui/STATUS.md` §6 (list view toggle,
      `globals.css` conflicts, stub buttons, every floor-plan room opens the same model, inert measurement types, missing thumbnails).

### 7.11 Reports and evaluation with users

- [ ] FYP-2 / final report (start a `report/final-eval/`).
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
