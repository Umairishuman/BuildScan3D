# BuildScan3D: Map of the repository

**What is where, and what each file does.** Read this first in a new session (human or agent), then
[CLAUDE.md](CLAUDE.md) (how we work) and [docs/progress/STATUS.md](docs/progress/STATUS.md) (where the project stands).
Last checked against the code: 2026-11-19 (online site: `publish_scan.py`, `remoteBundles.ts`, D-076, branch `feature/vercel-deploy`; web UI: `/api/scans` lists every scan bundle, D-074; earlier 2026-11-12: branch `feature/iqa-timing`: app changelog `android/CHANGELOG.md`, update checks on start and return, `iqa_ms`; earlier: app moved to `android/` §6, USB upload, light UI).
When you add, move, retire or repurpose a file, update this map in the same commit.

Markers: **[v9]** = part of the current best pipeline (v9 processing + v10 semantics) · [eval] = evaluation /
diagnostics · [v3] = the older SfM pipeline the server still runs · [legacy] = the ARCore-pose pipeline from before
2026-10-11, kept for the record · [exp] = experiment, not used by any pipeline · [dead] = backup copy, unused.

## 0. Where is ...? (quick finder)

| Looking for | Folder | Section |
|---|---|---|
| **Mobile app UI** (screens, buttons, menus, colours) | `android/app/src/main/` → screens in `java/com/buildscan3d/app/*Activity.java`, layouts in `res/layout/`, colours in `res/values/colors.xml`, logo `res/drawable-nodpi/logo.png` | 6 |
| Mobile app logic (recording, IQA, coverage, upload, USB / Wi-Fi link, updates) | same `java/com/buildscan3d/app/` folder | 6 |
| Reconstruction pipeline + "models" code (SfM, priors, 3DGS training, semantics, mesh) | `src/arcore3dgs/` | 2, 3 |
| AI model weights (Metric3D, Grounding DINO, SAM, CLIP) | not in git: `~/.cache/torch/hub`, `~/.cache/huggingface` (downloaded on first use) | 9 |
| Trained 3D models (results) | not in git: `saved_models/`, `dataset/<capture>/work_*` | 9 |
| Phone-upload server | `server/` (start: `scripts/start_server.sh`) | 4, 5 |
| Web dashboard + 3D viewer | `prototype/web-ui/` | 7 |
| **One command for everything** (server, runs, viewers, status) | `scripts/buildscan` (`scripts/buildscan help`) | 5 |
| **Which command, which arguments** (cheat sheet) | [docs/COMMANDS.md](docs/COMMANDS.md) | 8 |
| **How to run the full pipeline** | [docs/RUN_PIPELINE.md](docs/RUN_PIPELINE.md) | 8 |
| Launch / setup scripts | `scripts/` | 5 |
| Python environments | `envs/linux/` (Linux), `requirements*.txt` (Windows) | 1 |
| Tests | `tests/` | 11 |
| CI/CD (GitHub Actions) and APK checks | `.github/` | 11 |
| Project records (status, decisions, log, runs) | `docs/progress/` | 8 |
| Reports for evaluations | `report/` | 1 |

## 1. Top level

| Path | What it is |
|---|---|
| `MAP.md` | This file |
| `CLAUDE.md` | Team workflow, logging rules, git rules, per-member preferences |
| `AGENTS.md` | Brand assets, UI theme, five-stage architecture, commit conventions |
| `README.md` | Overview and setup (its folder tree is out of date, STATUS §7.1) |
| `src/arcore3dgs/` | **The reconstruction pipeline** (all Python stages, section 3) |
| `src/Metric3D_v2/`, `src/process_dataset.py`, `src/visualize_trajectory.py` | First prototype (Sept 2026): Metric3D depth + ARCore poses → dense cloud. Superseded; `process_dataset.py` still has a test |
| `server/` | Phone-upload processing server (FastAPI) + RunPod / remote-GPU runners (section 4) |
| `scripts/` | Windows `.bat` launchers + the job-manager CLI (section 5) |
| `android/` | **The capture app** (Android, our code; moved here from `googleARCore/samples/hello_ar_java/` on 2026-11-12, D-063), section 6 |
| `googleARCore/` | Google's ARCore SDK and samples, vendored and unused (`samples/hello_ar_java/MOVED.md` points to `android/`) |
| `prototype/web-ui/` | Next.js dashboard + 3D scan viewer (section 7) |
| `prototype/requirements.md`, `prototype/POC_requirements.md` | Early product / POC requirements |
| `tests/` | pytest suite (CPU-only logic, runs in CI) |
| `docker/Dockerfile.gpu` | GPU image for RunPod (`umairishuman/buildscan-gpu:latest`); **out of date** (STATUS §6) |
| `.github/` | CI (`ci.yml`), CD (`cd.yml`), Docker build (`docker-gpu.yml`), APK checks (`android/`), PR template |
| `docs/` | Records, guides, proposal, papers (section 8) |
| `report/mid-eval/` | Everything submitted for the FYP-1 mid evaluation (frozen) |
| `UI designs/` | Two design reference images for the web UI |
| `scratch/` | One-off Python scripts that once patched web-UI files (dashboard, logo, login image). Not used; to be archived once the owner agrees (D-049) |
| `envs/linux/` | Linux micromamba env files (`colmap.yml` → `bs-colmap`, `nerfstudio.yml` → `bs-ns`, `system.yml` → `bs-system`) `requirements-nerfstudio.txt` (the Windows freeze minus Windows-only packages) and `bs-ns-activate.sh` (CUDA paths for gsplat's JIT build, copied into the env's `activate.d`). Used by this PC and, later, the Docker image (D-047, D-048) |
| `requirements.txt` | `nerfstudio-env` (Windows `pip freeze`) |
| `requirements-system.txt` | System Python 3.10: `run_v8.py`, COLMAP wrappers, Metric3D |
| `requirements-semantic.txt` | `semantic-env`: Grounding DINO, SAM, CLIP |
| `pytest.ini`, `.coveragerc`, `ruff.toml` | Test / lint config |
| `.env.example` | Template for `.env` (RunPod key, processing mode); `.env` is never committed |

**Not in git (gitignored), on the RTX 3070 PC only:** `dataset/`, `saved_models/`, `outputs/`, `tools/colmap_dl/`
(COLMAP 4.2 CUDA + vocabulary trees), `tools/cudnn9/`, `nerfstudio-env/`, `semantic-env/` (section 9).

## 2. The current pipeline (v9 processing + v10 semantics), in order

Commands with all flags: STATUS §5. Python environment in brackets.

```
phone app (android/) ──── dataset/<capture>/  (dataset.mp4, poses.csv, ...)
   │  check_capture.py                                  [system]  sanity check before processing
   ▼
run_v8.py  [system Python; calls nerfstudio-env for export/train]
   select   select_sharp.py      gyro-aware sharpest frame per 0.2 s            -> dataset/<c>/work_v9/
   sfm      sfm_colmap.py        COLMAP 4.2 SfM, lens, undistort, Sim3 to ARCore -> dataset/<c>/work_v9_sfm/
   export   export_nerfstudio.py transforms.json for nerfstudio
   prior    mono_prior.py        Metric3D depth + normals aligned to SfM points
            plane_seg.py         planar regions (CPU, in parallel)               (--planar)
            blur_motion.py       camera motion during exposure (in parallel)     (--blur)
   init     fast_mvs.py          fast PatchMatch dense init (or mono_init.py)    (--init fmvs)
   train    geo_splatfacto.py    splatfacto + DashGaussian + priors (+ --pgsr)   [nerfstudio-env]
   ply      ns-export            -> work_v9_sfm/gs_v9/splat.ply, timing.json
   ▼
layout.py          walls / floor / ceiling / corners / dimensions          [nerfstudio-env] -> gs_v9/layout/
semantic2d.py      2D fixture masks (Grounding DINO + SAM)                  [semantic-env]   -> work_v9_sfm/semantic2d_v10/
semantic3d.py      labels on the Gaussians, walls with areas, fixtures      [nerfstudio-env] -> gs_v9/semantic_v10/
verify_fixtures.py CLIP check of switches / sockets -> verdicts.json        [semantic-env]
semantic3d.py      again with --verdicts
mesh.py            TSDF mesh of rendered depth                              [nerfstudio-env] -> gs_v9/mesh/
mesh_labels.py     labels onto the mesh, areas, .glb                        [nerfstudio-env]
export_web.py      .spz groups + scan.json + mesh for the viewer (to_spz.mjs, Node) -> prototype/web-ui/public/scans/<name>/
```

## 3. `src/arcore3dgs/`, file by file

Scripts call each other by path from `run_v8.py` (`HERE = src/arcore3dgs`); the shared modules are `common.py`
(imported by 7 scripts), `imu.py` and `toolpaths.py` (tool locations per OS). Each script's docstring has its full usage.

**Capture loading and frame selection**

| File | Does | Status |
|---|---|---|
| `toolpaths.py` | Where COLMAP and the nerfstudio env live on Windows (old layout) or Linux (micromamba envs); `BUILDSCAN_COLMAP` / `BUILDSCAN_NS_ENV` / `BUILDSCAN_MAMBA` override; `ns_cmd()` runs nerfstudio programs inside the activated `bs-ns` env on Linux (needed for gsplat); directory link helpers. Used by `run_v8.py`, `sfm_colmap.py`, `fast_mvs.py`, `mvs_init.py`, `colmap_mvs.py` | **[v9]** shared |
| `common.py` | Loads a capture (video + poses + points), pose interpolation at frame time, intrinsics, OpenGL→OpenCV, tracking gaps | **[v9]** shared |
| `check_capture.py` | Validates a recording before processing (files, sync, tracking, dropped frames, blur, exposure, re-anchors) | **[v9]** |
| `select_sharp.py` | Gyro-aware keyframes: least predicted blur per window, uses `camera.csv` exposure | **[v9]** |
| `prepare.py` | Laplacian keyframes + Metric3D depth cache, tracking-loss settle | [v3] [legacy] |
| `filter_frames.py` | Drops post-tracking-loss frames from an existing work dir | [legacy] |
| `imu.py` | Extracts gyro + accelerometer from the ARCore MP4's protobuf tracks | used by fallback / select |

**Camera poses**

| File | Does | Status |
|---|---|---|
| `sfm_colmap.py` | COLMAP 4.2: features, ARCore-guided / retrieval pairs, global mapper, lens self-calibration, undistortion, Sim3 to ARCore (levelled with ARCore gravity since D-071), mis-registration filter. COLMAP path from `toolpaths.py`; `tools/cudnn9` only for the rejected ALIKED path | **[v9]** [v3] |
| `fallback.py` | IMU featureless-tracking fallback: bridge tracking gaps, detect heading jumps | [v3] [legacy]; not in `run_v8.py` (OD-6) |
| `relocalize_pnp.py` | Re-aligns post-gap segments to the map with PnP | [legacy] |
| `relocalize.py` | Earlier image-content relocalisation of post-gap segments | [legacy] |
| `validate_realign.py` | Checks the re-alignment with independent SIFT matches | [eval] [legacy] |
| `ba.py` | Own GPU bundle adjustment (Schur LM) with ARCore priors | [legacy] |

**Depth, priors, initialisation**

| File | Does | Status |
|---|---|---|
| `mono_prior.py` | Metric3D depth + normals per frame, aligned to SfM points (fp16 default); `--fill_scale`: frames with < 5 SfM points get a time-interpolated scale instead of no prior (R-092) | **[v9]** |
| `plane_seg.py` | Per-frame planar regions for the planar prior | **[v9]** |
| `blur_motion.py` | Per-frame camera motion during exposure for the blur model; `--source gyro --gyro_calib --per_frame_exposure` for captures without ARCore (`run_v8.py --blur_gyro`, FEATURELESS 10.f) | **[v9]** |
| `fast_mvs.py` | Fast dense init: PatchMatch on every 7th frame at 640 px | **[v9]** |
| `mono_init.py` | Dense init from aligned mono depth (12 s, loses few-view detail) | [exp] option `--init mono` |
| `mvs_init.py` | Dense init from a full COLMAP PatchMatch (v6, 2 h 15 min) | [exp] v6 recipe |
| `colmap_mvs.py` | COLMAP PatchMatch on our fixed BA poses | [legacy] |
| `mvs.py` | Own plane-sweep MVS guided by Metric3D | [legacy] |
| `align_fuse.py` | Per-frame Metric3D scale + two-pass TSDF fusion | [legacy] |
| `pocket_prior.py` | PocketGS-style keyframes + dense consistent prior | [legacy] |
| `make_init.py` | Init from BA + MVS-measured points | [legacy] |

**Training**

| File | Does | Status |
|---|---|---|
| `run_v8.py` | One-command driver for the v9 pipeline, times every stage. Finds the nerfstudio env through `toolpaths.py`; `--pose_opt`, `--train_args`, `--blur_gyro`, `--prior_args` (FEATURELESS 10.d – 10.f) | **[v9]** |
| `geo_splatfacto.py` | Splatfacto subclass: DashGaussian, depth / normal / planar priors, blur model, PGSR-lite, checkpoints + `--resume`; `--pose_opt` (SO3xR3, applied once per view incl. blur / PGSR passes); `--path_prune <r>` (removes Gaussians reaching into the camera path every 500 steps) | **[v9]** |
| `export_nerfstudio.py` | Writes `transforms.json` for nerfstudio | **[v9]** [v3] |
| `train.py` | Own gsplat trainer (experiments only, D-010) | [exp] |
| `train_fixed2_backup.py`, `train_v3_backup.py` | Old copies of `train.py` | [dead] |

**Structure, semantics, mesh, export**

| File | Does | Status |
|---|---|---|
| `layout.py` | Room layout: any number of walls, floor, ceiling, corners, dimensions, `plan.png`; since 2026-11-19 also no-roof detection (`open_top`, #8), wall-gap openings (`openings.py`, #9), `room_closed` + warnings (#10); options `--debug`, `--raised_max`, `--infer_gap` (off) | **[v9]** |
| `openings.py` | Doorways and window openings without a leaf / frame from gaps in each wall's surface with the model seen through them; used by `layout.py` (#9) | **[v9]** shared |
| `plan_export.py` | As-built floor plan from `layout.json` (+ `semantic.json`): `plan.json`, `plan.svg`, `plan.dxf` (R12, layers WALLS / OPENINGS / FIXTURES / TEXT); `--square` turns near-right-angle walls and writes `plan_square.json|svg|dxf` instead (on in `run_full.sh` since D-075) (#12, plan 4.9) | **[v9]** stage `plan` of `run_full.sh` |
| `level_model.py` | Levels an already trained model with ARCore gravity (rotates splats incl. colour coefficients and poses) into a new tag, for models exported before D-071 (2026-11-12) | **[v9]** one-off tool |
| `semantic2d.py` | Grounding DINO + SAM fixture masks on upright frames, decoy classes, tile pass | **[v9]** semantic-env |
| `semantic3d.py` | Votes 2D labels onto Gaussians, structure from layout, fixture instances + geometry rules | **[v9]** |
| `verify_fixtures.py` | CLIP crop check of switch / socket candidates | **[v9]** semantic-env |
| `mesh.py` | TSDF mesh from rendered depth (Open3D 0.19), PGSR unbiased depth, shell flatness | **[v9]** |
| `mesh_labels.py` | Labels onto the mesh, shell denoising, areas, `.glb`; `--clean_ceiling` own radius for the ceiling (off, #18) | **[v9]** |
| `export_web.py` | Splits the model into label groups (`.spz`), `scan.json`, mesh for the viewer | **[v9]** |
| `to_spz.mjs` | PLY → `.spz` with Spark's encoder (run from `prototype/web-ui`, Node) | **[v9]** |
| `structure.py` | Older box-room structural layer (planes, walls, openings) | [exp] superseded by `layout.py` (its ceiling-height item marked obsolete 2026-11-19, #18) |
| `planarize.py` | Post-hoc snapping of splats to planes | [exp] rejected (D-017) |
| `clean_splats.py` | Floater pruning by measured free space; `--mono` uses the depth priors for sensor-path models, `--exclude` leaves held-out frames out (R-100) | [exp] not default (D-040) |

**Evaluation, diagnostics, viewing**

| File | Does | Status |
|---|---|---|
| `eval_offpath.py` | Off-path split metrics (PSNR, SSIM, sharpness, flatness, blocked views) + sheets | [eval] current |
| `eval_align.py` | Held-out PSNR / SSIM after test-pose alignment (model frozen, 6-DoF + colour per frame), for models trained with `--pose_opt` (R-084) | [eval] current |
| `prune_near_path.py` | Removes Gaussians reaching within a radius of the camera path from a trained `splat.ply` (blocked views, R-087 / R-089); `path_points()` is also used by `geo_splatfacto.py --path_prune` | [eval] current |
| `room_planes.py` | Room planes (walls / floor / ceiling) from plane_seg regions lifted with the depth priors + SfM points, before training; top-view `room_plan.png` (FEATURELESS §11.b, R-094) | [v9] experiment |
| `plane_prior.py` | Rewrites the depth / normal priors from the room planes: per-frame scale tied to the planes, plane depth + normal on agreeing planar pixels; before / after cross-frame consistency (FEATURELESS §11.c) | [v9] experiment |
| `prior_consistency.py` | Switches off depth-prior pixels that other views contradict (free space in front of them in time neighbours / loop partners); each frame keeps its own depth (FEATURELESS §11.c second form, R-098) | [v9] experiment |
| `scale_drift.py` | Corrects the scale drift of a sensor camera path with the room height (floor / ceiling distances per frame), re-triangulates the points (R-094); its `read_model` / `write_model` are used by loop_path.py | [v9] experiment |
| `loop_path.py` | Closes the loops of a camera path: camera centres solved again from the path's steps + the direction of verified image pairs >= 5 s apart (validation on held-out pairs), points re-triangulated, `loop_pairs.json` for `prior_ba.py --pair_priors` (FEATURELESS §11.d, R-096) | [v9] experiment |
| `loop_match.py` | Second loop round: picks pairs that see the same surfaces at different times with the corrected cameras + depth priors, matches them (ALIKED + LightGlue, copy of the database), pair directions in the model's world (R-097) | [v9] experiment |
| `offpath_views.py` | Fixed off-path views of trained splats: 8 views from the room centre (colour + depth) and a top view of a horizontal slice (walls as lines vs ghost copies) (FEATURELESS §11.e) | [eval] |
| `vggt_chunk.py` | VGGT (downloaded, outside the repo, D-081) on a chunk of keyframes or dense video frames: rotation vs the gyro / an SfM model, positions vs the model, depth consistency vs the Metric3D priors (R-093) | [experiment] |
| `eval_perframe.py` | Per held-out frame: PSNR of a held-out model vs a model that saw the frame, 3D support, time (R-084's per-stretch table) | [eval] current |
| `stretch_stats.py` | Per SfM model: 3D observations per camera, path smoothness, overall and in time stretches; movement vs a reference model | [eval] current |
| `track_dir_check.py` | Agreement of video-track pair directions with a model's path, by support and time stretch (R-077 – R-079) | [eval] current |
| `render_compare.py` | Two models on their common training views: PSNR per model and a photo / A / B sheet (R-081) | [eval] current |
| `fixture_checklist.py` | Fixture check sheet for one room from `semantic.json` (+ layout): every accepted fixture with height, size, wall, a real / wrong class / false column, a missed table and per-class summary; `--rejected` also lists the rule-rejected candidates (plan 4.2, E3) | [eval] current |
| `make_split.py` | Writes the held-out list for `run_v8.py --split` / `eval_offpath.py`: 6 × 3 s stretches of the walk (D-070); `--add` merges another held-out list (still frames) | [eval] current |
| `sfm_scale_check.py` | Finds parts of an SfM model rebuilt at the wrong scale ("mini room"): per-frame SfM depth / Metric3D depth from `mono_prior` (TRAINING R-066, R-067) | [eval] diagnostic |
| `texture_probe.py` | Per keyframe: SIFT keypoints, LSD long lines, faint / strong gradient share; grouped by ARCore pose state and by whether a model kept the frame (FEATURELESS_TRACKING_PLAN §1.1) | [eval] diagnostic |
| `gyro_check.py` | Gyro rotation check of an SfM model: IMU→camera rotation + time offset from the model, per-frame rotation disagreement with the gyroscope; `fill_rotations` gives rotations for frames SfM could not place. Used by `sfm_colmap.py --gyro_thr` (FEATURELESS_TRACKING_PLAN step 1, R-047) | **[v9]** option, default off |
| `known_rot_pnp.py` | Places a camera from >= 2 matched 3D points with its rotation fixed (gyro); cut-gap test vs PnP. Used by `sfm_colmap.py --place_unplaced` (R-049) | [experiment] option, default off |
| `imu_scale.py` | Metric scale of an SfM model from the accelerometer (pre-integrated over keyframe triplets, VINS-style), gravity and bias; `--gyro_orient` | [eval] diagnostic |
| `gyro_pairs.py` | Rejects image pairs whose matches contradict the gyro rotation; `Orientation` (gyro integrated once over a capture, bias removable) | [experiment] |
| `rot_sfm.py` | SfM with gyro rotations + positions from pair directions and the accelerometer (one linear system), then COLMAP triangulation / BA (R-051: rejected on scan_009); `--bg_json` (bias from `gyro_loop_bias.py`), `--max_dt 300` for loop pairs (R-071); `--extra_pairs` / `--extra_w` / `--extra_min_inliers`: pair directions from `video_tracks.py` (R-077, R-079) | [experiment] |
| `prior_ba.py` | Bundle adjustment of a COLMAP text model with soft gyro / accelerometer priors on consecutive keyframes (rotation 0.1° + 0.1°/s, position 0.02 + 30% of the step); same LM / Schur solver as `ba.py` (R-052, R-071, R-072); `--adapt_n`: position prior tight where a pair has few 3D observations, loose where it has many (R-078); `--pair_priors`: keeps the relative position of loop pairs from loop_path.py (R-096) | [experiment] |
| `video_tracks.py` | KLT point tracks through every video frame, checked against the gyro rotation (2-point RANSAC), triangulated into a COLMAP text model; `--pairs_out` writes keyframe-pair correspondences for `rot_sfm.py` (R-073 – R-080) | [experiment] |
| `rs_rectify.py` | Rolling-shutter rectification of keyframes with the gyro (per-row rotation, lens distortion kept); `--probe_only` finds the readout direction from the video; `rectify_points` used by `video_tracks.py --rs 1` (FEATURELESS 10.b, not trained yet) | [experiment] |
| `track_loop.py` | Rounds of video tracks → `rot_sfm.py` → adaptive `prior_ba.py` until the kept cameras stop rising (FEATURELESS 10.c, not run yet) | [experiment] |
| `still_frames.py` | Still stretches of a capture from the gyro; held-out list of sharp frames for `make_split.py --add` (FEATURELESS 10.a) | [experiment] |
| `gyro_loop_bias.py` | Gyro bias from the 5-point rotations of all verified image pairs (far-apart pairs see the drift); writes the bias for `rot_sfm.py --bg_json` (R-071, R-072) | [experiment] |
| `vggt_poses.py` | VGGT (learned poses) on chunks of keyframes, chained, checked against gyro / accelerometer / ARCore, written in the export layout. Needs VGGT outside the repo; **never run** (needs Tayyab's OK) | [experiment] not run |
| `gap_test.py` | Cut-gap test: removes windows of keyframes from a trusted model and predicts their rotation from the gyro (plan step 0 / 3) | [eval] |
| `tape_check.py` | Model vs tape table for a room (`<dataset>/tape.csv`: layout room length / width / height or values measured in the viewer), mean / max error, NFR6 (≤ 5%) check (COMPLETION_PLAN E2) | [eval] current |
| `fair_compare.py` | Compares models from different SfM runs (trimmed Sim3 + test-pose refinement) | [eval] current |
| `compare_models.py` | Photometric + geometric metrics and sheets on held-out frames | [eval] |
| `compare.py` | Older held-out comparison | [eval] [legacy] |
| `fit_diag.py` | Full-res fit on training views + optical-flow misalignment | [eval] |
| `diagnose.py` | Render-only "why is it blurry" check (train vs held-out, splat stats) | [eval] |
| `consistency.py` | Finds frames whose depth contradicts other views | [eval] [legacy] |
| `before_after.py`, `grazing_views.py` | Comparison image sheets | [eval] |
| `view.py` | gsplat browser viewer with measure tool, port 7010 | viewer |

## 4. `server/`

| File | Does |
|---|---|
| `main.py` | FastAPI app: `/upload`, `/status`, `/jobs`, `/logs`, `/retry`, `/datasets`, `/reprocess`, `/download`, `/config`, `/health`; modes local / runpod / remote / dry_run. Logs devices that connect, uploads while they arrive and every failed request; answers the app's server search on UDP 8001 (D-057). Saves uploads as `dataset/scan_<NNN>_<id>` and answers with the scan number (D-065) |
| `scan_numbers.py` | Scan numbers: every recording in `dataset/` numbered 1, 2, 3 in arrival order, register `dataset/.scan_numbers.tsv`; used by `main.py` and `scripts/buildscan` (D-065) |
| `pipeline.py` | Local runner: fallback → prepare → sfm_colmap → export_nerfstudio → ns-train splatfacto → ns-export (the **v3** recipe). Windows paths (`nerfstudio-env\Scripts\*.exe`) |
| `runpod_client.py` | RunPod API: create pod from `umairishuman/buildscan-gpu:latest`, setup script (skipped if nerfstudio exists), SCP up, run, SCP down, always terminate, watchdog |
| `remote_gpu.py` | Same flow over SSH to an always-on machine (a friend's GPU) |
| `test_upload.py` | Manual test: upload a dataset to a running server and poll |
| `requirements.txt` | Server-only deps (fastapi, uvicorn, ...) |

## 5. `scripts/` (Windows `.bat`, plus the Linux setup)

| File | Does |
|---|---|
| `buildscan` | **Linux: one command for everything**: `status`, `server start/stop/log`, `datasets`, `check`, `run` (calls `run_full.sh` in screen `run-<tag>`), `watch`, `results`, `view` (port 7010), `web` (port 3000), `publish` / `unpublish` / `published` (online site, D-076), `attach`, `stop`, `ip`, `gpu`. `latest` = newest recording |
| `watch_run.py` | Live view behind `buildscan watch`: stage n of 15 and what it does, time vs R-030, training step, GPU, last message without paths (reads `run_full.log` / `train.log`; standard library only) |
| `run_full.sh` | **Linux: the whole pipeline in one command**, recording → 3DGS → layout → semantics → mesh → web bundle, each stage in its env; `--from <stage>` restarts; prints GPU use / temperature / training progress every 30 s (`gpu.csv`). Guide: [docs/RUN_PIPELINE.md](docs/RUN_PIPELINE.md) |
| `setup_linux.sh` | **Linux setup** (no sudo): micromamba, envs `bs-colmap` / `bs-ns` / `bs-system`, `semantic-env`, vocabulary tree, web-ui packages, then checks (GPU, COLMAP, gsplat, Open3D). `--check` = checks only. Same script for the Docker image (D-048) |
| `run_arcore3dgs.bat` | [v3] pipeline: fallback → prepare → sfm_colmap → export_nerfstudio → ns-train → ns-export |
| `run_arcore3dgs_legacy.bat` | [legacy] ARCore-pose pipeline: fallback → prepare → ba → relocalize_pnp → ba → mvs → pocket_prior → train.py |
| `view_splat.bat` | Starts `view.py` (http://localhost:7010) |
| `start_server.bat` | Loads `.env`, starts the FastAPI server on port 8000, prints the IP for the phone |
| `start_server.sh` | Linux twin of `start_server.bat`: loads `.env`, mode defaults to `dry_run`, runs uvicorn on port 8000 in the small `bs-server` micromamba env (not the pipeline envs), prints the phone URLs. Detached: `screen -dmS bs-server scripts/start_server.sh` |
| `publish_scan.py` | Puts a run's web bundle + plan.png on the online site: R2 bucket `scans/<owner>/<capture>_<tag>/` + that owner's `index.json`; `unpublish` archives in the bucket, `list`; Python + boto3 (Linux and Windows), keys from `.env`; `--target dir:` for tests (D-076). Linux: `scripts/buildscan publish / unpublish / published` |
| `jobs.bat` / `jobs.py` | Job manager CLI (list, watch, logs, retry, reprocess, mode) |
| `release.bat` | Bumps the app version and tags a release |
| `run_train.bat`, `run_train_fast.bat`, `run_post.bat`, `run_post_fast.bat`, `run_viewer.bat` | [dead] first splatfacto runs on roomAttemptSadness (Sept/Oct 2026): ns-train / ns-eval / ns-export / ns-viewer with MSVC set up |

## 6. Android capture app: `android/`

Our app, built on Google's `hello_ar_java` sample; moved out of `googleARCore/` on 2026-11-12 with its own Java package
`com.buildscan3d.app` (D-063; `applicationId` unchanged since D-058, so installed apps update in place). Light theme
from the logo with bottom navigation Capture / Scans / Server (D-064). Code in
`app/src/main/java/com/buildscan3d/app/`:

| File | Does |
|---|---|
| `CaptureActivity.java` | Capture tab (was `HelloArActivity`, Google's sample heavily modified): ARCore session, recording, rendering, ⋮ menu |
| `GalleryActivity.java` | Scans tab: recordings, connection bar, upload with checks first (files, then USB / Wi-Fi), progress with MB/s and time left, Stop, automatic restart after a lost link |
| `ServerActivity.java` | Server tab: live connection, USB steps, Wi-Fi address (save and test, network search), app updates |
| `ProcessingActivity.java` | Upload & process screen after a recording: same checks, progress, Stop; then job status polling |
| `ScanDetailActivity.java` | One recording: video preview, trim |
| `ServerLink.java` | Which route reaches the server now: USB cable (`127.0.0.1:8000` via `adb reverse`) first, then saved / recent Wi-Fi servers; plain reason when none answers (D-062) |
| `ServerDiscovery.java` | Server search (USB, UDP broadcast, saved and recent servers, /24 sweep) and the recent-servers list |
| `BottomNav.java` | The bottom navigation bar (`res/layout/view_bottom_nav.xml`) |
| `CaptureLogger.java` | Writes poses, tracking, points, depth, `camera.csv`, `anchors.csv`, lens metadata on a background thread |
| `QualityMonitor.java` | Live IQA: predicted blur, dark / overexposed, low texture, tracking; `quality.csv` |
| `CoverageMap.java`, `CoverageOverlayView.java` | Live coverage map (red / yellow / green dots). Since 2026-11-15 the dots are drawn by the GL renderer every frame (`CaptureActivity.drawCoverage`, shader `assets/shaders/coverage_point.frag`); `CoverageOverlayView` only gets cleared |
| `FeatureMap.java` | Persistent, smoothed map of ARCore feature points for the camera preview (by point id, shown after 3 observations, reset on a > 15 cm jump); replaces drawing ARCore's per-update point set (2026-11-15) |
| `UpdateChecker.java` | Update check against GitHub Releases at start and on return to the app (at most every 6 h, not while recording) and from the Server tab / menu; the dialog shows the release notes ("What's new"), after an update the installed version's notes are shown once; downloads the APK and opens Android's installer (FileProvider `res/xml/update_paths.xml`), continuing by itself after the "install unknown apps" permission |
| `common/` | Google's helpers (rendering, camera permission, display rotation, ...), sample code, only the package renamed |

**App UI files** (`app/src/main/`):

| File | Screen / use |
|---|---|
| `res/values/colors.xml`, `res/values/styles.xml` | Light palette from the logo (`bs_*` colours) and `AppTheme` / `AppTheme.Capture` |
| `res/drawable-nodpi/logo.png` | The logo (cropped from `prototype/web-ui/public/images/logo-new-removebg-preview.png`); launcher icons in `res/mipmap-*` |
| `res/drawable/bg_card.xml`, `bg_button*.xml`, `bg_pill.xml`, `bg_bottom_nav.xml`, `ic_nav_*.xml` | Cards, buttons, badges, bottom bar and its icons |
| `res/layout/activity_main.xml` | Capture tab (`CaptureActivity`): camera view, logo badge, record button, IQA / coverage text, ⋮ menu, bottom bar |
| `res/layout/activity_gallery.xml`, `res/layout/item_scan.xml` | Scans tab (`GalleryActivity`) and one recording card |
| `res/layout/activity_server.xml` | Server tab (`ServerActivity`) |
| `res/layout/view_bottom_nav.xml` | Bottom navigation, included in the three tabs |
| `res/layout/activity_scan_detail.xml` | One recording's details (`ScanDetailActivity`) |
| `res/layout/activity_processing.xml` | Upload & processing status (`ProcessingActivity`) |
| `res/menu/settings_menu.xml` | ⋮ menu on the Capture tab: camera, depth, Server (opens the Server tab), Check for updates |
| `res/xml/update_paths.xml` | Folder shared with the installer for in-app updates |
| `assets/models/`, `assets/shaders/` | Google's sample 3D models and shaders for the AR rendering |
| `AndroidManifest.xml` | Screens, permissions, update file provider |

What changed in each release: [android/CHANGELOG.md](android/CHANGELOG.md); every PR that changes the app adds its
lines under "Unreleased" (D-068). Uploads send every recorded file since v0.3.5 (PR #4). Build: Android Studio (open `android/`) or
`./gradlew assembleDebug` in `android/` with JDK 21; CI builds it on every push (docs/CI_CD.md).

A recording (`dataset/<capture>/`): `dataset.mp4` (video + IMU tracks), `poses.csv`, `tracking.csv`, `points.csv`,
`quality.csv`, `camera.csv`, `anchors.csv`, `depth/` (5 Hz), `meta.json`, `lens_metadata.json`, `camera_characteristics.json`.

## 7. Web UI: `prototype/web-ui/`

Own status file: [prototype/web-ui/STATUS.md](prototype/web-ui/STATUS.md) (and its own AGENTS.md / CLAUDE.md).

| Path | What |
|---|---|
| `src/app/` | Routes: `/` login, `/dashboard`, `/projects`, `/projects/new`, `/viewer/[id]`, `/floorplan/[id]`, `/workspace/boiler-room` |
| `src/app/api/scans/route.ts`, `src/app/api/scans/[folder]/plan/route.ts` | Lists every bundle in `public/scans/` as a project (JSON) and serves each run's `layout/plan.png` as its thumbnail (D-074) |
| `src/lib/scanBundles.ts` | Server side: reads the bundles' `scan.json`, `dataset/.scan_numbers.tsv` and the TRAINING.md headings (run ID, date) into project cards |
| `src/lib/useAllProjects.ts`, `src/lib/mergeProjects.ts` | Client hook: `mockData.ts` projects + the listed bundles (no duplicates; a hand-written card opens the published copy when its folder is not on the server); used by `/projects` and `/viewer/run-<folder>` |
| `src/lib/remoteBundles.ts` | Server side: scans published to the R2 bucket (`SCANS_BASE_URL`: `owners.json`, `scans/<owner>/index.json`) as project cards, id `run-<owner>-<folder>` (D-076) |
| `src/components/Viewer3D/SplatCanvas.tsx` | **Real scan viewer** (Spark, `.spz`, label groups, mesh mode, measuring) |
| `src/components/Viewer3D/Canvas3D.tsx`, `SceneBuilder.ts`, `MeasurementTool.ts` | Mock 3D scene (procedural room) and measuring for mock projects |
| `src/components/ProjectDetail/ScanLayersPanel.tsx` | Scan Layers panel for real scans |
| `src/components/...` | Dashboard, projects, floor plan, notifications, modals (mostly mock data) |
| `src/lib/mockData.ts` | Mock projects and the hand-written real ones (`newroom-scan`, `scan-008`); other processed scans are listed automatically (`scanBundles.ts`) |
| `public/scans/newroom/` | The real labelled scan bundle (from `export_web.py`) |
| `public/scans/scan_<id>_<tag>/` | Per-run bundles written by every `run_full.sh` run; gitignored (D-061), live only on the machine that ran it; each one appears in the Projects tab by itself (D-074) |
| `scans_archive/` | Older per-run bundles moved out of `public/scans/` (not served, not listed in Projects); gitignored, this PC only (D-075) |
| `public/splats/` | Empty. The old v6 splat (`newroom_v6.spz`, 12.5 MB, unused since the labelled bundle) was taken out of git on 2026-11-06 (D-055); local copy in `saved_models/web/` on the Ubuntu PC |

## 8. `docs/`

| Path | What |
|---|---|
| `progress/STATUS.md`, `DECISIONS.md`, `LOG.md`, `TRAINING.md` | The four live project records (CLAUDE.md §1) |
| `progress/PIPELINE_ANALYZER_PLAN.md` | **current** · Plan (2026-11-22, D-082, not started): analyzer stage that labels a recording and picks the camera route, self-checking correction steps, four-recording test bench, processing-time rules |
| `progress/FEATURELESS_TRACKING_PLAN.md` | **current** · Draft plan (2026-11-18) for placing cameras in featureless stretches: gyro rotation, lines / junctions, the room layout as a map, dense matchers; measurements, steps, options (OD-14) |
| `progress/COMPLETION_PLAN.md` | **current** · Plan to finish by 2026-12-04: every open task by pipeline step, with done-when, dependencies, priority, week; snapshot of the shared doc (link inside) |
| `progress/Problems_and_Solutions.md` | Technical evidence for every problem and fix (P&S §x) |
| `progress/Research_Notes_2026-10-24.md` | Literature behind v8/v9 |
| `progress/archive/` | Retired files (old TODO, Training_Analysis, early notes) |
| `Flow.md` | System flow app → server → GPU → model |
| `COMMANDS.md` | **Cheat sheet**: every `scripts/buildscan` command, what to type for each argument, examples |
| `RUN_PIPELINE.md` | **How to run the full pipeline on Linux** (`scripts/run_full.sh`): setup, upload, check, run, watch, restart, results, known problems |
| `PROCESSING_GUIDE.md` | Using the phone-upload server and job manager |
| `CI_CD.md` | What CI/CD checks and how to run it locally |
| `proposal/` | Proposal v1–v4 (+ unversioned copy), defence slides, guidelines, POC plans, workflow docs |
| `Research Papers/` | 3DGS, PGSR, PocketGS, VIGS-SLAM papers and notes |

## 9. Data and outputs on disk (gitignored)

| Path | What |
|---|---|
| `dataset/<capture>/` | A recording (section 6). Captures: `roomAttemptSadness`, `roomAttemptSadness2`, `newRoomAttemptSadness` |
| `dataset/<c>/work/` | [legacy] work dir |
| `dataset/<c>/work_sfm/gs_sfm*` | [v3] SfM work dir and models |
| `dataset/<c>/work_sharp_sfm/` | v6 work dir; v8 / v9 experiments under it (`v8/`, `v9/`, `eval_v9/`, `layout_*`) |
| `dataset/<c>/work_<tag>/`, `work_<tag>_sfm/gs_<tag>/` | `run_v8.py --tag <tag>` output (e.g. `work_v9e2e_sfm/gs_v9e2e/`, `gs_v9final/`) |
| `outputs/v8/splatfacto/<name>/` | nerfstudio run folder (`config.yml`, checkpoints deleted after export) |
| `saved_models/YYYY-MM-DD_<tag>/` | Kept models with a `README.txt` (best: `2026-10-27_v9_semantic_pgsr/`) |
| `tools/colmap_dl/`, `tools/cudnn9/` | COLMAP 4.2 CUDA for Windows + vocabulary trees; cuDNN 9 DLLs |
| `nerfstudio-env/`, `semantic-env/` | Python venvs (Windows) |

## 10a. Tests, CI and other folders

| Path | What |
|---|---|
| `tests/conftest.py` | Shared fixtures (synthetic captures) |
| `tests/test_common_*.py`, `test_imu.py`, `test_fallback.py`, `test_relocalize_and_sfm.py` | Pipeline maths: capture loading, poses, IMU, fallback, SfM helpers |
| `tests/test_process_dataset.py` | First-prototype script |
| `tests/test_server_api.py`, `test_server_pipeline.py`, `test_runpod_client.py`, `test_scan_numbers.py` | Upload server, local runner, RunPod client, scan numbers |
| `tests/test_apk_checks.py` | APK / manifest checker and signing keys |
| `tests/test_openings.py`, `tests/test_plan_export.py` | Wall-gap openings and the floor-plan export on synthetic rooms (#9, #12) |
| `tests/test_publish_scan.py` | `publish_scan.py` against a folder bucket: index, owners, republish, unpublish to archive, refusals (D-076) |
| `tests/test_changelog.py` | App changelog tool (`.github/android/changelog.py`) and that `android/CHANGELOG.md` has the current version |
| `tests/test_sources_compile.py` | Every Python file compiles |
| `tests/requirements.txt` | Light test dependencies (no GPU) |
| `.github/workflows/ci.yml` | CI: lint, tests (Python 3.10–3.12), web build, Android debug + release build, repo hygiene |
| `.github/workflows/cd.yml` | CD on `master`: version bump + changelog entry (D-068), release APK signed with the private key (D-059), GitHub Release with the changelog as its notes |
| `.github/workflows/docker-gpu.yml` | Builds / pushes the RunPod GPU image |
| `.github/android/` | `check_apk.py` + `apk_expectations.json` (what a correct APK looks like), `debug.keystore` (CI builds only), `changelog.py` (CD: "Unreleased" in `android/CHANGELOG.md` → the new version's entry and the release notes) |
| `envs/linux/` | Linux env files (section 1) |
| `docker/` | `Dockerfile.gpu` (out of date, STATUS §6) |
| `report/mid-eval/` | FYP-1 mid evaluation: LaTeX report, fix notes (frozen) |
| `UI designs/`, `.vscode/`, `scratch/` | Design images, editor settings, old one-off scripts (section 1) |

## 10. Reorganisation plan (agreed 2026-11-06, DECISIONS D-049)

The flat `src/arcore3dgs/` mixes the current pipeline with legacy, experiments and backups, which is why it is hard to
tell what is current. **Nothing is ever deleted: retired files are archived** (`git mv` into an `archive/` or
`legacy/` folder, with a note of why). Two steps:

1. **Now, low risk:** this map plus the status markers. Archive the `[dead]` files (`train_*_backup.py`, the five old
   `run_*.bat`, `scratch/`) once their owners agree.
2. **After the pipeline runs on Linux** (STATUS §7.1 step 1, so every move can be checked with a real run): group the
   code by stage and move the legacy pipeline out of the way, e.g.

   ```
   src/arcore3dgs/
     capture/    common.py imu.py check_capture.py select_sharp.py
     poses/      sfm_colmap.py fallback.py relocalize_pnp.py
     priors/     mono_prior.py plane_seg.py blur_motion.py fast_mvs.py mono_init.py mvs_init.py
     train/      run_v8.py geo_splatfacto.py export_nerfstudio.py
     scene/      layout.py semantic2d.py semantic3d.py verify_fixtures.py mesh.py mesh_labels.py
     export/     export_web.py to_spz.mjs
     eval/       eval_offpath.py eval_align.py prune_near_path.py make_split.py sfm_scale_check.py tape_check.py fair_compare.py compare_models.py fit_diag.py diagnose.py view.py ...
     legacy/     ba.py mvs.py align_fuse.py pocket_prior.py make_init.py colmap_mvs.py train.py prepare.py ...
   ```

   This touches `run_v8.py` (script paths), the 7 `from common import` lines, `server/pipeline.py`, the `.bat`
   launchers, `tests/` and every command in STATUS / README, so it should be one dedicated branch and PR.
   Moving the capture app out of the vendored `googleARCore/` was done on 2026-11-12: it is in `android/` (D-063).
