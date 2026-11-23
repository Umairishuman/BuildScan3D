# BuildScan3D: Project Log

Dated record of what was done, by whom, and where the details are. Newest day at the **end**. One block per working
day (or per session if several people worked that day). Runs get a one-line mention here and a full entry in
[TRAINING.md](TRAINING.md); decisions get a line here and an entry in [DECISIONS.md](DECISIONS.md). Rules:
[CLAUDE.md](../../CLAUDE.md).

Entries up to 2026-11-05 were backfilled on 2026-11-06 from git history, Problems_and_Solutions.md (P&S), the old
TODO ([archive/TODO.md](archive/TODO.md)) and branch notes. Names: Umair = UmairisHuman, Tayyab = BlazingBeam
(confirmed by Umair on 2026-11-06), Zaid = Zaid Fareed.

Template:

```markdown
## YYYY-MM-DD · <name> · <branch>
- Did: <what changed, with files>
- Runs: R-NNN <name> (<result in a few words>)
- Decisions: D-NNN <short>
- Problems: <anything that went wrong and is not a run error>
- Next: <what the next session should pick up>
```

---

## 2026-08-20 → 08-24 · Umair · master
- Initial commit with research papers; workflow and all requirements; draft 1 of the requirements.
- File renames, `.gitignore`.

## 2026-08-21 · Zaid · master
- Proposal draft from the refined and merged documents.

## 2026-08-22 · team
- Proposal v4 dated 22 August 2026 (ownership: Umair capture, Tayyab orchestration + 3DGS, Zaid semantics + compression + web). D-001.

## 2026-08-28 · Tayyab · master
- App init: AR works in the app, but exports to the desktop don't work yet.

## 2026-09-01 · Umair · master
- More research on ARCore + 3DGS.

## 2026-09-05 · Zaid · master
- Initial draft of the proposal defence slides.

## 2026-09-07 → 09-10 · Umair · master / prototype
- POC requirements; folder layout; web UI prototype: layout, 3D scene builder + HUD, branding (AGENTS.md), mock data,
  dashboard redesigns, measurement panel, semantic layers and render modes, floor-plan route, comparison view, overview /
  files / report tabs, X-ray mode for MEP layers, new-project flow with OCR simulation, user-uploaded floor plans,
  `prototype/web-ui/STATUS.md`.

## 2026-09-14 · Tayyab · master
- Simple app with record / stop buttons that saves metrics + video.

## 2026-09-28 · Tayyab · master
- Fusion pipeline (Metric3D + ARCore poses → dense prior), interactive viewer, dataset processing, trajectory visualisation.

## 2026-09-29 · Umair · master
- Code-structure refactor.

## 2026-10-06 → 10-07 · Tayyab · master
- Metric ARCore → 3DGS pipeline: pose interpolation by timestamp, Metric3D preprocessing, own GPU BA, plane-sweep MVS,
  two-pass fusion, depth-supervised gsplat trainer, viewer fixes. D-002 – D-007. Runs: R-001.
- App: live capture-quality assessment (IQA).

## 2026-10-09 · Tayyab, Umair · master
- Tayyab: ARCore tracking and IQA fixes; `diagnose.py` shows the trainer underfits (wrong depth target). D-008, D-009, D-041. Runs: R-002, R-003.
- Umair: merged `prototype`; logo; `.gitignore` updates.

## 2026-10-10 · Tayyab, Zaid · master, `exp/trainer-arkitscenes`, `ci/github-actions`
- Tayyab: training-recipe analysis (Training_Analysis.md), splatfacto adopted, measured init, viewer FOV defaults,
  PocketGS-style prior, coverage overlay, `check_capture.py`, IMU featureless-tracking fallback. D-010 – D-013, D-016.
  Runs: R-004, R-005, R-007.
- Zaid: image-sequence input + ARKitScenes converter, trainer checkpoints / per-frame depth loss, `mvs.py` no-source fix,
  experiments on Kaggle (R-006, branch `exp/trainer-arkitscenes`); unit tests, ruff, CI and CD workflows, PR template, CI/CD notes. D-036.

## 2026-10-11 · Tayyab, Zaid · master
- Tayyab: root cause found (silent ARCore re-anchor, no lens distortion): COLMAP SfM poses + lens self-calibration,
  ARCore for scale; bilateral grid; tape-measure tests; README update. D-014, D-015, D-039, D-040. Runs: R-008 – R-011.
- Zaid: tests for IMU parsing, gap bridging, relocalisation and Sim3, capture fallback edge cases.

## 2026-10-12 · Tayyab, Umair, Zaid · master
- Tayyab: v6 (gyro-aware sharp frames + dense MVS init), structural-layer and flattening experiments; app logs camera
  metadata and anchors; blur prediction with real exposure. D-017, D-018, D-019, D-031, D-042. Runs: R-012.
- Umair: processing server (FastAPI), upload & process UI in the app, configurable server URL, recording performance fix,
  RunPod on-demand client, `start_server.bat`, default GPU RTX 3090; proposal guidelines, POC plans, stakeholder workflows;
  folder clean-up. D-034, D-043.
- Zaid: server API, pipeline and RunPod client tests; coverage gate, APK checks, shared signing key; latest-APK release.

## 2026-10-15 · Umair · master
- Mid-report table of contents and the assessment guidelines.

## 2026-10-18 · Umair · master
- Server dry-run mode; local-IP detection; in-app update checker (v0.2.0); auto-versioned APK builds in CD (v0.3.0 →
  v0.3.2); gallery overhaul, server auto-discovery, upload progress; job log retrieval, retry, pod lifetime watchdog;
  remote-GPU (SSH) mode; `.env` for the RunPod key.

## 2026-10-19 · Umair, Tayyab · master
- Umair: GitHub Actions workflow that builds the GPU Docker image (`umairishuman/buildscan-gpu:latest`). D-035.
- Tayyab: refactor.

## 2026-10-21 · Tayyab
- v7 fast pipeline (25 min) rejected on quality; ARCore-guided matching kept. D-020. Runs: R-013.
  (Committed on 2026-10-23 in `66fb668`: `sfm_colmap.py --pairs arcore`, pose-refined `fair_compare.py`.)

## 2026-10-22 · Umair · master, `claude/jolly-wozniak-42woyl`
- RunPod: GPU selection and existing-pod support; watchdog default raised above the measured run time; missing `time`
  import fixed. `.env` untracked, `.env.example` added.
- Mid report: fix brief (team decisions, D-033), correction pass (fabricated evidence removed, MEP and X-ray removed,
  TikZ diagrams, risk register), shortening 107 → 85 pages, chunked rewrites, compiled. Logs now in
  `report/mid-eval/report-fix-notes/`.

## 2026-10-23 · Tayyab · master
- Documentation and model-evaluation refinements (`66fb668`, merge `df5bf1e`).
- App capture-quality audit (predicted-blur IQA, HDR off, pawn removed, dropped-frame reporting); surface map, room
  overlay, autofocus toggle built and then reverted at the user's request. D-032. The kept app changes were committed
  on 2026-10-26 inside `6d0cab5`.

## 2026-10-24 · Tayyab
- v8: DashGaussian + SfM-anchored priors, off-path evaluation, Metric3D fp16; Spark web viewer with `.spz`. Research notes.
  D-021, D-030. Runs: R-014 – R-017. Committed on 2026-10-26 inside the v9 commit `6d0cab5`.

## 2026-10-26 · Tayyab · `feature/processing-v9`
- v9: retrieval SfM, fast MVS init, planar and motion-blur priors, room layout; 96 min end to end. D-022 – D-024. Runs: R-018 – R-020.

## 2026-10-27 · Tayyab · `feature/semantics-mesh`
- Semantic labelling, PGSR-lite, meshing, scan layers in the web viewer; prior-alignment bug fixed; checkpoints + resume
  after a power cut; final all-frames model. D-025, D-026, D-028, D-029. Runs: R-021 – R-024.

## 2026-11-02 · user room check
- Fixtures checked in the real room: 13/15 correct, recall 13/17 (`gs_v9final/semantic/audit_ground_truth.json`).

## 2026-11-03 · Tayyab, Zaid · `feature/semantics-mesh`, `feat/splat-compress`
- Tayyab: semantics v10 (tiled small-object pass, CLIP crop check, door merging). D-027. Runs: R-025.
- Zaid: splat analysis + pruning / SH reduction scripts, `.ksplat` v1 and v2 notes. Runs: R-026.

## 2026-11-06 · Tayyab · `feature/semantics-mesh`
- Requirements files per environment, README setup, PROCESSING_GUIDE and STATUS for v10. D-037.

## 2026-11-06 · Umair · `docs/project-organisation` (off `feature/semantics-mesh`)
- Did: project reorganisation. New records `DECISIONS.md`, `LOG.md`, `TRAINING.md` (all backfilled from history);
  `STATUS.md` rewritten to hold everything done and left (absorbs `TODO.md`); old `TODO.md`, `Training_Analysis.md` and
  two old `.docx` notes archived in `docs/progress/archive/` (pointers left for the two the mid report cites); mid-evaluation
  material moved to `report/mid-eval/`; `CLAUDE.md` now holds the logging workflow and per-member sections.
- Decisions: D-044 (records and folders), D-045 (target machines: this PC, friend's PC, RunPod; no Docker install here
  yet), D-046 (next focus: semantic labelling).
- Problems: git has no user identity on this PC (commits made with `-c user.name/user.email`); this PC has no NVIDIA
  driver loaded, no Docker / COLMAP / Node.js, and Python 3.14 (STATUS §6).
- Next: Tayyab and Zaid fill in their CLAUDE.md sections; team settles the open decisions (DECISIONS OD-1 – OD-9); set up
  this PC (driver, Python 3.10); then semantic labelling.

## 2026-11-06 (second session) · Umair · `docs/project-organisation`
- Did: `MAP.md` at the repo root: what is where and what every file does, with status markers (v9 / eval / v3 / legacy /
  exp / dead), the v9 pipeline in order, data folders, and the two-step reorganisation plan. CLAUDE.md: read MAP.md
  first; never delete files, archive them. Checked this PC (STATUS §6): GPU on `nouveau`, Secure Boot on,
  `nvidia-driver-595-open` recommended, no compiler / ffmpeg / Node / conda, Python 3.14 only. STATUS §7.1 now has the
  ordered plan: step 1 this PC, step 2 Docker image, step 3 RunPod and the friend's PC.
- Confirmed: BlazingBeam = Tayyab.
- Decisions: D-047 (this PC first, same versions, conda envs), D-048 (one setup script for PC + Docker), D-049 (two-step
  reorganisation; never delete, archive), D-050 (MAP.md first).
- Next: Umair installs the NVIDIA driver (`sudo ubuntu-drivers install nvidia-driver-595-open`, reboot, `nvidia-smi`);
  then micromamba, the envs and `scripts/setup_linux.sh` (STATUS §7.1 1b–1h).

## 2026-11-06 (third session) · Umair · `feature/linux-port`
- Did: this PC set up (R-027, ~2.5 h): driver, micromamba, envs `bs-colmap` / `bs-ns` / `bs-system`, `semantic-env`,
  model weights, vocabulary tree; gsplat compiled; tests pass. Code port (`toolpaths.py`, `run_v8.py` and the COLMAP
  scripts) and `scripts/setup_linux.sh`. Auto-suspend off; `gh` installed in `~/.local/bin`.
- Decisions: D-051 (merge everything into `master` by PR; Tayyab informed), D-052 (delete only fully merged branches),
  D-053 (PC stays awake; Tailscale remote access).
- Problems: stalled conda download, COLMAP's undeclared OpenImageIO, setuptools too new, gsplat needing the activated
  env — all in R-027.
- Next: Umair runs `gh auth login`; PR → CI → merge → delete merged branches. Then Tailscale (sudo), the server port,
  and the first run when Tayyab's data arrives.

## 2026-11-06 (fourth session) · Umair · `feature/linux-port` → `master`
- Did: Tailscale up on this PC (`gpu-lab-precision-3680`, 100.102.13.24, Tailscale SSH on); `gh` logged in. PR #1
  (`feature/linux-port` → `master`). CI first failed on two things: coverage 37.4% < 40% (already failing on `master`
  since 2026-10-19 at 38%) and the 12.5 MB `newroom_v6.spz` over the 10 MB limit. Gate lowered to 35% (D-054); the
  unused `.spz` taken out of git, local copy in `saved_models/web/` (D-055). Then all 9 checks green.
- Found: the repository is **public**, and commit `00bc021` contains `.env` with a real RunPod API key → Umair to revoke it
  (STATUS §7.1).
- Decisions: D-054, D-055.
- Next: merge PR #1 (merge commit), delete the fully merged branches, keep Zaid's unmerged ones.

## 2026-11-06 (fifth session) · Umair · `docs/repo-public`
- Did: PR #1 merged into `master` (`9ce4d68`); the 8 fully merged branches deleted on GitHub and locally (Zaid's two
  unmerged branches kept); first green `master` CD since 2026-10-19 (APK + web bundle + "latest" release published).
- Umair revoked the leaked RunPod key; the repo stays public (D-056). Screen "sleep" checked: the PC never suspended,
  it only locks after 5 min idle; lock kept.
- Next: the server port and `.sh` launchers (STATUS 7.1 1f); the first run when Tayyab's data arrives.

## 2026-11-06 (sixth session) · Umair · `exp/first-linux-run`, `fix/android-app`
- Did: plan for STATUS 7.1 step 1h with Umair's own new recording (not yet uploaded). Tailscale checked: running,
  SSH on, key expires 2027-05-05; laptop not yet in the tailnet. Upload server on Linux: env `bs-server`,
  `scripts/start_server.sh` (`dry_run`); the server now logs devices that connect, uploads as they arrive, failed
  requests, and answers a UDP server search on port 8001 (all tested on a copy on ports 8010/8011). App: server list
  failed because it only swept the phone's /24 while the lab Wi-Fi is a /19 → UDP search + saved servers; update
  checker fixed (repo name, menu item, in-app install, errors shown); package name `com.buildscan3d.app`; CD builds a
  release APK signed with a new private key (`~/.buildscan3d-keys/`, GitHub secrets). Python tests: 212 passed.
- Decisions: D-057 (server env), D-058 (package name), D-059 (release key), D-060 (PR → merge → CD).
- Problems: system Python has no `ensurepip` (no venv without sudo) → micromamba env; conda download of `openjdk`
  stalled (as in R-027) → key made with `openssl`; `ufw` is active (phone access untested).
- Next: CI on the PR, merge, CD release v0.3.4; Umair uploads today's recording, then installs v0.3.4 (next to the old app,
  a separate package); ufw rules; then `check_capture.py` and the R-028 run options.

## 2026-11-06 (seventh session) · Umair · `fix/upload-all-files`
- Did: the app's upload left out `camera.csv`, `anchors.csv`, `lens_metadata.json`, `camera_characteristics.json` (found
  on `scan_056fe94d3399`, R-028). Both upload screens now send them; the server saves them as optional files and warns
  when an older app does not send them. Tests: 214 passed (2 new).
- Next: PR → CI → merge → CD release; record a new room with the new app to get `camera.csv` (exposure) for `--blur`.

## 2026-11-06 (eighth session) · Umair · `exp/first-linux-run`
- Did: `scan_056fe94d3399` (Umair's room, Infinix X6833B, 46 s) checked: READY with warnings; the upload had dropped
  `camera.csv`, `anchors.csv` and the lens files (fixed on `fix/upload-all-files`, not pushed). `scripts/run_full.sh`
  (whole pipeline, one command) + `run_v8.py --pgsr --save_every`; `select_sharp.py` now extracts `imu.npz`. R-028
  (agent) stopped by Umair after ~5 min; R-029 is his own run (tag `umair`). `run_full.sh` prints GPU use /
  temperature / training progress every 30 s; guide `docs/RUN_PIPELINE.md`; MAP quick finder + app UI files.
  Tailscale: offline on the lab Wi-Fi (cannot reach the coordination server), works on the cable; Umair's laptop
  connects (direct). VS Code Remote-SSH steps given.
- Runs: R-028 (abandoned), R-029 (running).
- Problems: `ffprobe` not on PATH without env activation; `imu.npz` missing on fresh recordings; terminal silent
  during training; placeholder `<new id>` typed literally; Tailscale blocked on the lab Wi-Fi.
- Next: finish R-029 (results, verdict); push + release `fix/upload-all-files` (v0.3.5) when Umair agrees; firewall
  rules for the wired card `enp0s31f6`; disable Tailscale key expiry; record a room with v0.3.5 (`camera.csv`).

## 2026-11-06 (ninth session, backfilled 2026-11-12) · Umair · `exp/first-linux-run`
- Did: `scripts/buildscan` (one command for server, runs, viewers, status; asks for missing arguments) and
  `docs/COMMANDS.md` cheat sheet (`908ef6f`, `60c6611`, `718f884`). Recorded `scan_646070948603` (lab room, 97 s) and
  processed it with `scripts/buildscan run` (tag `r1106`).
- Runs: R-030 (50.2 min, no errors; room height 1.50 m looks wrong). Not logged at the time.

## 2026-11-12 · Umair · `exp/first-linux-run`, `fix/upload-all-files`
- Did: reviewed the records and listed everything still open in STATUS §7 for the end-of-month deadline
  (2026-11-30). Found why `prototype/web-ui/public/scans/` held two untracked folders: the `web` stage of every run
  writes `<scan>_<tag>/` there (R-029, R-030) → gitignored (D-061, `56d7517`), MAP.md row added. Wrote the missing
  R-030 entry. Checked whether Tayyab changed the app: his last app commit is `6d0cab5` (2026-10-26, shipped in
  v0.3.3: demo pawn / Instant Placement removed, motion-blur IQA messages); his only push since is the poster guide
  (`f33aeaf`, 2026-11-11). Unpushed work on his PC cannot be seen. v0.3.3 → v0.3.4 changed only server search,
  updates, package name and key (no ARCore / recording code). Confirmed the ARCore point-cloud dots are drawn on
  screen only and never while recording; the MP4 is ARCore's raw camera stream (a frame of R-030 checked, clean).
  ARCore is still used for metric scale / gravity (R-030: Sim3 with 242 inliers, median 5.25 cm), poses come from
  COLMAP (D-014). Pushed `fix/upload-all-files`, PR #4 (CI green: app build, Python 3.10–3.12), merged; CD published
  **v0.3.5** (`BuildScan3D-v0.3.5.apk`, 5.7 MB, 2026-11-12 08:16 UTC).
- Runs: R-030 entry backfilled.
- Decisions: D-061 (per-run web bundles out of git).
- Problems: no local env has pytest + FastAPI, so the server tests ran only in CI. Local `master` is 12+ commits
  behind `origin/master`; the upload server on this PC runs from `exp/first-linux-run`, which lacks the PR #4 server
  change.
- Next: install v0.3.5 on the phone (not tested on a device) and record a room with it (`camera.csv` must arrive);
  update the server checkout to include PR #4; check R-030's room height; ask Tayyab about unpushed app work.
- Later the same day: checked Zaid's `feat/splat-compress` (2026-11-03): `analyze.py` + `compress.py` (opacity pruning,
  normals dropped, SH 3 → 1) run on R-030's `splat.ply` in the `bs-ns` env: 162 MB → 54 MB (66% smaller, 90.4% of
  652,392 splats kept) in 0.3 s; its analysis showed the R-030 model is 3.08 m tall (TRAINING R-030 follow-up). The
  `.ksplat` converter it relies on is not in the repo; quality only compared on software renders. OD-1 / OD-4 stay open.
  Made the completion plan for 2026-12-04 with Umair: 94 tasks by step (14 capture, 12 server, 17 reconstruction,
  12 layout / semantics, 10 compression / web, 10 evaluation, 12 infrastructure, 7 report / UAT / demo), three weekly
  gates, nine decisions to take first; nothing cut (Umair). Shared doc
  [BuildScan 3D Completion Plan](https://claude.ai/artifact/1V2YG8GSfBEpLXmnTJdctC) (private until shared), repo copy
  `docs/progress/COMPLETION_PLAN.md`; MAP and STATUS §7 point to it.
- Next (plan): the team assigns owners in the shared doc and takes the first decisions (owners, OD-7, OD-1, OD-4,
  OD-6); keep the repo copy in step with the doc.

## 2026-11-12 · Umair · `feature/usb-upload`
- Did: uploads were slow (~1.4 MB/s lab Wi-Fi, ~1 MB/s hotspot; PC Wi-Fi signal −76 dBm on the hotspot, link
  26 Mbit/s PC → phone) and the PC's address kept changing. Added a USB upload route (D-062):
  `scripts/usb_link.sh` + `start_server.sh` (adb reverse while the server runs), server log labels USB requests;
  app `ServerLink.java` (USB first, then saved / recent Wi-Fi, plain reason when none answers), connection bar on the
  Scans screen, upload speed and time left, 30 s write timeout (was 10 min), automatic restart up to 3 times, screen
  kept on during uploads, USB entry in the server dialog. Guide: docs/PROCESSING_GUIDE.md "Upload over a USB cable".
- Problems: installing `adb` from this session was blocked by the permission check, so Umair installs it (commands
  in the guide). No Android SDK / JDK on this PC, so the app was not compiled locally; CI builds it.
- Then (same day): moved the app to `android/` with package `com.buildscan3d.app`, `CaptureActivity` (D-063); light
  theme from the logo, logo in headers and on the capture screen, bottom navigation Capture / Scans / Server, new
  Server tab (`ServerActivity`, search moved to `ServerDiscovery`), upload checks before the progress bar (files, then
  USB / Wi-Fi, with dialogs asking to connect), Stop on the Scans tab and the processing screen, progress with MB/s on
  the processing screen too (D-064). Merged `exp/first-linux-run` into this branch; `buildscan status` shows the USB
  link. CI: first UI build failed (`R.id.btn_gallery` left in `CaptureActivity`), fixed; lint's one error was a
  missing `ACCESS_NETWORK_STATE` permission (fixed); remaining lint items are old warnings (hard-coded strings etc.).
- Problems: no Android SDK here, so every compile check ran in CI; the UI was not seen on a device or emulator.
- Next: PR to `master`, CD release; install `adb`; test the new UI and the USB upload on the phone.

## 2026-11-12 (later) · Umair · `feature/numbered-scans`
- Did: recordings numbered 1, 2, 3 in arrival order (D-065): `server/scan_numbers.py` (register
  `dataset/.scan_numbers.tsv`), uploads saved as `scan_<NNN>_<id>` with the number in the server's answer, `/datasets`
  sorted by number, `scripts/buildscan` datasets / status / picker / `<scan>` arguments use the numbers, the app shows
  "Saved on the PC as scan #N" and "UPLOADED #N". Current recordings: #1 `scan_056fe94d3399`, #2 `scan_646070948603`,
  #3 `scan_6de634cbb8b2` (uploaded 2026-11-12 14:53 with `camera.csv` / `anchors.csv`, so the v0.3.5 upload fix works).
  Found on the way: `buildscan latest` used folder dates, which processing runs change.
- Tests: `tests/test_scan_numbers.py` (6) + `tests/test_server_api.py` (21) pass locally (pytest in a temporary path).
- Then renamed the three earlier recordings with their numbers (D-066): `scan_001_056fe94d3399`,
  `scan_002_646070948603`, `scan_003_6de634cbb8b2`; stored paths in `frames.json` / `project.ini` / `semantic.json` /
  `mesh_*.json` updated, logs left as written, web bundles renamed, examples in COMMANDS.md / RUN_PIPELINE.md /
  buildscan updated. Wrote the hand-over prompt for the next session (end of this block).
- Next: PR, CI, merge and release (app shows the number from the next version on).

## 2026-11-12 (evening) · Umair · `feature/numbered-scans`, `feature/iqa-timing`
- Did: COMPLETION_PLAN Step 1 review with Umair: 1.1 (asked Tayyab), 1.2 and 1.3 done; 1.4 in progress (scan #3 (classroom, 2026-11-12)
  processing as R-031, started by Umair 15:04, tag `r1112`); 1.5 tape measured (sheet not yet saved next to a
  dataset). Checked scan #3 (classroom, 2026-11-12) for 1.6 / 1.7: `check_capture.py` READY; NFR1 **not met** (28.9 fps, 3.3% dropped-frame
  gaps, longest 99 ms); ARCore depth live (782 distinct maps) → 1.7 closed (D-067). NFR2 could not be measured (the
  app never timed the quality check): `feature/iqa-timing` times `QualityMonitor.update()` per frame and writes it as
  the last `quality.csv` column `iqa_ms`; `check_capture.py` prints NFR1 / NFR2 lines.
- Runs: R-031 (header and capture facts written while it runs).
- Decisions: D-067.
- Problems: a first dropped-frame count from `poses.csv` gaps (0.24%) was wrong (threshold missed most gaps); the video
  count (3.3%) replaced it in R-031 and the plan. No Android SDK here, so the app change is compiled by CI only.
- Next: push `feature/iqa-timing` + PR when Umair agrees (CI builds the APK); install, record 1–2 min, upload,
  `scripts/buildscan check` → NFR2 numbers into STATUS §4; finish R-031 (result, verdict, ceiling height vs tape);
  save the tape sheets next to the datasets; then 1.8 (scan #3 (classroom, 2026-11-12): blur > 5 px on 75% of frames at 30 ms exposure) and 1.9.
- Correction (same evening, Umair): scan #3 (classroom, 2026-11-12) is from **v0.3.6**, not v0.3.5: the server log shows it came over the USB
  cable (14:53:06, 815 MB in 22 s at 37 MB/s), which only v0.3.6 can do. So the USB upload (D-062) works on the phone,
  and `adb` is installed (`~/.local/bin/adb`). Records updated (R-031, D-067, STATUS §4 / §7.7, plan 1.3).
- Then (same evening, `feature/iqa-timing`): update checks on start and on return to the app (at most every 6 h, not
  while recording), release notes in the update dialog, "Updated to vX" once after an update, install continues after
  the permission screen (`UpdateChecker.java`, `CaptureActivity`, `ServerActivity`). App changelog
  `android/CHANGELOG.md` (v0.3.3 – v0.3.6 written from git history + "Unreleased"); `.github/android/changelog.py` +
  `cd.yml` turn "Unreleased" into each release's entry and notes; `tests/test_changelog.py` (6, pass locally without
  pytest). MAP, CI_CD.md updated. Decision D-068 (Umair). Java not compiled here (no JDK); CI compiles it. Pushed both
  branches and opened one PR at Umair's request.
- Then (same evening, Umair's requests): STATUS §2 "Which recording is which" (scans #1 – #3 with folder, date, phone,
  app, place, runs; room numbers not recorded) and every "scan #3" in the records labelled (classroom, 2026-11-12).
  `scripts/buildscan watch` rewritten as a live view (`scripts/watch_run.py`): run and scan, stage n of 15 with what it
  does, time in the stage vs R-030, training step / time left, GPU use labelled as GPU use, last message without
  paths, STOPPED / FINISHED; `--raw` keeps the old log tail; `watch latest` picks the only or the running run. App:
  the bottom snackbar that repeated the tracking message and covered the bottom navigation removed (top banner only).
  Merged PR #6 to `master` at Umair's request after CI.
- CD after the merge: CI gate, APK build and release all green; **v0.3.7** released (`5ac8e54`,
  `BuildScan3D-v0.3.7.apk`) with the changelog text as its release notes: the new CD step (D-068) worked on its first
  run. Not yet installed on the phone.
- Next: Umair installs v0.3.7 (v0.3.6 offers it with the old dialog), records 1–2 min, uploads → NFR2 from
  `scripts/buildscan check`; R-031 result. Hand-over prompt for the Step 3 session below.

Hand-over prompt (2026-11-12, for the next session):

    Read MAP.md, CLAUDE.md (I am Umair) and docs/progress/STATUS.md (§2 "Which recording is which", §4, §7.2, §7.3),
    then the 2026-11-12 LOG.md blocks, docs/progress/COMPLETION_PLAN.md Step 3, and TRAINING.md R-020, R-023, R-030,
    R-031. Deadline 2026-12-04; week-1 gate G1 on 2026-11-19 (new rooms processed).

    State at the end of 2026-11-12:
    - master = v0.3.7 (PR #6 merged; CD released it with the changelog as release notes, D-068). Not yet tested on the phone:
      update prompt, "What's new", single quality banner, `iqa_ms` column (NFR2).
    - Recordings on this PC (STATUS §2): scan #1 (`scan_001_056fe94d3399`, 46 s, R-029), scan #2 (`scan_002_646070948603`,
      computer lab, 97 s, R-030: layout ceiling 1.50 m, wrong; model is ~3.1 m tall), scan #3 (`scan_003_6de634cbb8b2`,
      classroom, 185 s, v0.3.6, R-031 started 15:04 with the default recipe, tag `r1112`; at 15:37 it was training, after
      select 0.4 / SfM 12.1 / prior 3.6 / init 14.8 min). Room numbers not recorded.
    - `scripts/buildscan watch latest` now shows stage n of 15, training step and GPU in plain words (`--raw` for logs).
    - Uploading / server work (Step 2) is parked: Umair deals with it later. Do not work on Step 2 this session.

    This session: COMPLETION_PLAN Step 3 (reconstruction), on a new branch (e.g. `exp/step3-speed`), committing after each
    logical step, never pushing or merging without asking.
    1. Finish R-031: result, stage times (`stages.tsv`, `timing.json`), verdict, index row; check the layout height
       against the model and against Umair's tape numbers (ask him which rooms he measured and where the sheets are).
    2. 3.2: one logged run per new room as Umair records them; models into `saved_models/YYYY-MM-DD_<tag>/` with README.txt.
    3. 3.1 machine agreement: newRoomAttemptSadness lives on Tayyab's RTX 3070 PC. Ask Umair whether Tayyab can copy it
       here (how: USB disk / scp over Tailscale); then run v9 and compare PSNR / SSIM / scale with R-020 / R-023.
    4. 3.3 / 3.4 speed (Must): the stage times are the baseline (R-030: 41.7 min run_v8 + 8 min semantics; R-031: init
       took 14.8 min for 885 frames, CPU-bound PatchMatch). Try one change at a time on the same scan and log each as its
       own R-NNN with a before / after stage table: photometric-only PatchMatch or every-10th-frame `fast_mvs`, blur only
       in the last third of training, ViT-S depth prior, faster `plane_seg`. Kept / rejected with numbers.
    5. 3.6 run-to-run noise: 3 repeats of one setting, so a speed change can be told apart from noise.
    6. 3.8 / OD-6 (IMU fallback in v9) is a team decision: prepare the options with a recommendation, let Umair decide.

    Rules: every run gets a TRAINING.md entry before it starts, errors as they happen; never invent a number; decisions
    (recipe changes, what to keep) are Umair's: bring options with a recommendation and record his answer in
    DECISIONS.md; one run on the GPU at a time (check `scripts/buildscan status` first); update STATUS, LOG and the
    COMPLETION_PLAN rows at the end of the session; no AI attribution in commits.

## 2026-11-12 (Step 3 session) · Umair · `exp/step3-speed`
- Did: branch `exp/step3-speed` (from `docs/handover-step3`, which holds v0.3.7; local `master` was behind). R-031
  (scan #3, classroom) finished 16:25 without errors: 81.0 min (run_v8 64.7: SfM 12.1, prior 3.6, init 14.8, train
  33.6; sem2d 13.7); layout height 2.74 m, 2 walls / 0 corners, 21 fixtures; height checked against the model's splat
  heights and camera heights (plausible, maybe slightly low; not against tape). Model saved to
  `saved_models/2026-11-12_r1112_scan003/` with README.txt. New `src/arcore3dgs/make_split.py` (6 × 3 s held-out
  stretches) → `dataset/scan_003_6de634cbb8b2/offpath_test.txt`, 87 / 875 frames, for scoring speed runs.
- Runs: R-031 (finished, kept).
- Decisions: D-069 (speed and noise runs on scan #3, not scan #2; Umair), D-070 (fixed held-out split, scored with
  `eval_offpath.py`; Umair on the agent's recommendation).
- Correction (Umair): the classroom has **not** been tape-measured yet (a class was about to start); the earlier
  block's "1.5 tape measured" is wrong. Expected within a few days. Plan row 1.5 corrected.
- Team: Umair asked Tayyab for newRoomAttemptSadness (3.1). Tayyab says he is reducing the computation time; which
  stage is not known (nothing pushed: his last commits are the poster guide 2026-11-11 and semantics v10 2026-11-03).
  So Step 3 speed (3.3 / 3.4) waits for his answer; the 3 noise repeats (3.6) are prepared but not started.
- Problems: one commit was first written with an AI co-author trailer; amended before any push (CLAUDE.md forbids it).
- Later (Umair forwarded Tayyab's message): Tayyab is doing the Step 3 speed work on the RTX 3070 PC with
  newRoomAttemptSadness and the R-014 split (79 held-out frames), a full end-to-end run started 17:28. His changes
  and **expected** (not yet measured) times against R-020's v9e2e: SfM mapper skips retriangulation (22.4 → ~17 min),
  threaded I/O in the Metric3D priors (8.1 → ~7), photometric PatchMatch in the dense init (20.4 → ~8), exact loss
  and colour-grid fixes in training (42.5 → ~28); ~65 min in total with evaluation. His quality numbers were not in
  the forwarded part. So 3.3 / 3.4 are Tayyab's; on this PC the job becomes checking his recipe on scan #3 against
  R-031 once he pushes it (3.1 / 3.2). Not yet recorded as a decision (ownership split is a team decision).
- Next: Step 4 (prompt below). New rooms will be recorded on 2026-11-13 → one logged run each (3.2), they take the
  GPU first (G1 gate 2026-11-19). Ask Tayyab which stage he is optimising and split Step 3 ownership.

Hand-over prompt (2026-11-12, for the Step 4 session):

    Read MAP.md, CLAUDE.md (I am Umair) and docs/progress/STATUS.md (§2 "Which recording is which", §7.3, §7.5, §7.6),
    then the 2026-11-12 LOG.md blocks (the last one first), docs/progress/COMPLETION_PLAN.md Step 4, TRAINING.md R-030
    and R-031, DECISIONS.md D-069 / D-070, and P&S §4.17–4.18 (semantics v10). Deadline 2026-12-04; week-1 gate G1 on
    2026-11-19 (new rooms processed).

    State at the end of 2026-11-12:
    - Branch `exp/step3-speed` (not pushed) holds D-069, D-070, `make_split.py` and R-031's result. Step 3 is now
      Tayyab's: Umair told him what this branch contains and Tayyab will merge it later. Do not continue Step 3 work
      and do not add Step 4 work to `exp/step3-speed`.
    - Make a **new branch for Step 4** (e.g. `feature/step4-layout`) from `exp/step3-speed`, so the records above
      are on it; commit after each logical step, never push or merge without asking. Local `master` is behind
      `origin/master` (v0.3.7).
    - scan #2 (`scan_002_646070948603`, computer lab, R-030): layout height 1.50 m, wrong; splats span ~3.1 m vertically.
      Outputs in `dataset/scan_002_646070948603/work_r1106_sfm/gs_r1106/`.
    - scan #3 (`scan_003_6de634cbb8b2`, classroom, R-031): layout height 2.74 m (plausible; densest top splats slightly
      above the layout ceiling, so maybe a bit low), only 2 walls (6.39 m and 2.57 m, 9.03 m apart) and 0 corners;
      semantics v10 rejected the ceiling plane fit (tilt 8.06°) and levelled it at the layout height; floor tilt 0.28°;
      21 fixtures accepted (door, 2 windows, 2 switches, 4 sockets, 4 ceiling lights, tube light, 3 lamps, 4 ceiling
      fans), `window_1` sits at 2.72 m (at the ceiling, probably wrong). Model: `saved_models/2026-11-12_r1112_scan003/`
      (also in `dataset/scan_003_6de634cbb8b2/work_r1112_sfm/gs_r1112/`). View: `scripts/buildscan view 3 r1112`.
    - No tape measurements yet (Umair measures the classroom in the next days). New rooms recorded on 2026-11-13: each
      gets a logged full-pipeline run first (3.2), they take the GPU before anything else.
    - Tayyab does the Step 3 speed work on his PC (SfM without retriangulation, threaded priors I/O, photometric
      PatchMatch, training loss / colour-grid fixes; expected ~65 min vs 96, not yet measured; see the last LOG
      block). When he pushes it, run his recipe on scan #3 and compare with R-031 (this PC, same room). Step 2 (upload / server) is
      parked: do not work on it.

    This session: COMPLETION_PLAN Step 4 (layout, semantics, mesh), Must items first.
    1. 4.1 ceiling detection in `layout.py`: find out why R-030 took a plane at 1.50 m as the ceiling (look at its
       candidate planes and the splat height histogram), fix it, re-run only the layout stage on scan #2 and scan #3
       (`layout.py` directly takes seconds; `run_full.sh <scan> <tag> --from layout` also re-runs semantics, ~14 min) and compare heights before /
       after. Also look at why scan #3 found only 2 walls and no corners. Each re-run gets an R-NNN entry.
    2. 4.2 fixture check on scan #3 with Umair: give him a short checklist of the 21 fixtures (name, height above floor,
       size, which wall) to tick real / wrong while viewing the model, and ask what was missed; record a per-room
       found / missed / false table. Repeat for each new room after its run.
    3. 4.3 (FR10) fixture sizes in the web viewer: clicking a fixture shows width, height, height above floor (the
       values are already in `semantic_v10`); check one against tape when the tape numbers come.
    4. Should items if time is left: 4.5 doorways from wall gaps, 4.7 CLIP margins on the new rooms, 4.9 right-angle
       priors / floor-plan export.

    Rules: every run (including layout-only and semantics-only re-runs) gets a TRAINING.md entry before it starts,
    errors as they happen; never invent a number; rule / threshold changes that alter results are Umair's decision:
    bring options with a recommendation and record his answer in DECISIONS.md; one run on the GPU at a time (check
    `scripts/buildscan status` first); update STATUS, LOG and the COMPLETION_PLAN rows at the end of the session; no AI
    attribution in commits.

## 2026-11-12 (Step 4 session) · Umair · `feature/step4-layout`
- Did: branch `feature/step4-layout` from `exp/step3-speed` (not pushed). COMPLETION_PLAN 4.1: found why R-030 had a
  1.50 m ceiling and R-031 only 2 walls: **both models were tilted against gravity** (9.1° / 12.1°), because the Sim3
  to ARCore in `sfm_colmap.py` took its rotation from camera centres only (R-032; confirmed by ARCore's own per-frame
  gravity and by the floor / desk / ceiling planes). Scan #2's ceiling is also reconstructed too close to the camera
  (and reflected in the door glass). Fixes (Umair's choice of options, D-071 / D-072): the SfM export now levels with
  ARCore gravity (`--gravity centres` = old behaviour; R-033); new `src/arcore3dgs/level_model.py` levels trained
  models incl. SH colours (R-034; renders match the source at 85–98 dB); `layout.py` ignores ceiling candidates
  below the wall tops and records `ceiling_source` / `warnings`. Re-runs from layout: scan #3 → 4 walls, 3 corners
  89–90°, 7.23 × 9.05 m, 2.52 m, floor 32.27 m², 18 fixtures (R-035, kept); scan #2 → 2.41 m, 1 wall, 10 fixtures
  (R-036, inconclusive: re-record). 4.2: new `src/arcore3dgs/fixture_checklist.py`; scan #3 sheet in
  `dataset/scan_003_6de634cbb8b2/work_r1112lev_sfm/gs_r1112lev/semantic_v10/fixture_check.md`. 4.3 (FR10): fixture
  size card + clickable markers in the web viewer (`ScanLayersPanel`, `SplatCanvas`, page, `scanTypes`), and
  `export_web.py` writes bottom / top (tsc / eslint / next build pass; not checked in a browser).
- Umair copied **newRoomAttemptSadness** here (raw recording only). He chose the R-023 recipe tonight: R-037 started
  18:56:57 (`run-r1112nr`), for 3.1 and as the first end-to-end run with D-071 / D-072 on a room whose layout was right.
- Runs: R-032, R-033, R-034, R-035, R-036, R-037 (running).
- Decisions: D-071 (levelling: SfM export + `level_model.py` for old models), D-072 (ceiling not below wall tops); both
  Umair on the agent's recommendation.
- Problems: SH rotation first applied transposed (caught by the render check, fixed before use, R-034); I first wrote
  run end times I had not measured (corrected in TRAINING); the web build changed `next-env.d.ts` (restored).
- Team: tell Tayyab that `sfm_colmap.py`'s export changed (D-071) next to his mapper changes; ask him for the R-014
  held-out list (`offpath_test.txt`, 79 frames) for a PSNR comparison on newRoom.
- Next: finish R-037 (stage times vs R-020's 96 min on the 3070, layout vs 6.60 × 4.36 m / 2.72 m, scale vs tape
  6.70 m, fixtures vs the 15 of v10, the tilt the export reports); Umair fills in scan #3's fixture sheet → per-room
  found / missed / false table (4.2, E3); tape the classroom → check 2.52 m and 7.23 × 9.05 m; new rooms recorded
  2026-11-13 go first on the GPU (they now come out level); re-record the lab (scan #2) with the protocol.

Hand-over prompt (2026-11-12, for the next session):

    Read MAP.md, CLAUDE.md (I am Umair) and docs/progress/STATUS.md (§2 "Which recording is which", §7.3, §7.5, §7.6),
    then the 2026-11-12 LOG.md blocks (the "Step 4 session" one first), docs/progress/COMPLETION_PLAN.md Steps 3 and 4,
    TRAINING.md R-031 and R-032 … R-037, DECISIONS.md D-069 … D-072. Deadline 2026-12-04; week-1 gate G1 on 2026-11-19
    (new rooms processed).

    State at the end of 2026-11-12:
    - Branch `feature/step4-layout` (from `exp/step3-speed`, not pushed) holds the Step 4 work. Keep working on it,
      commit after each logical step, never push or merge without asking. `exp/step3-speed` is Tayyab's to merge.
    - Models were tilted 9–12° against gravity (the Sim3 to ARCore used camera centres only), which caused R-030's
      1.50 m ceiling and R-031's 2 walls (R-032). Fixed: `sfm_colmap.py` export levels with ARCore gravity (D-071,
      `--gravity centres` = old; it prints the tilt and writes `gravity_*` into report.json); `level_model.py` levels an
      already trained model into a new tag (R-034); `layout.py` ignores ceiling candidates below the wall tops and
      writes `ceiling_source` / `warnings` (D-072). Tayyab edits the mapper part of `sfm_colmap.py` for Step 3: tell
      him about the export change for his merge.
    - scan #3 (classroom) levelled = tag `r1112lev` (R-035, kept): 4 walls, 3 corners 89–90°, 7.23 × 9.05 m, height
      2.52 m, floor 32.27 m², 18 fixtures. Unexplained: the floor still fits 1.95° tilted (ceiling 0.05°); the 4th
      corner is missing. View: `scripts/buildscan stop viewer; scripts/buildscan view 3 r1112lev`.
    - scan #2 (lab) levelled = `r1106lev` (R-036, inconclusive): 2.41 m from the wall-top rule, 1 wall; the camera
      stayed within 0.8 × 0.7 m, so it needs re-recording with the capture protocol.
    - newRoomAttemptSadness was copied here (raw recording only). R-037 (R-023 recipe, all frames, tag `r1112nr`,
      screen `run-r1112nr`) started 18:56:57 for COMPLETION_PLAN 3.1 and as the first end-to-end run with D-071 /
      D-072. The R-014 held-out list is not here (ask Tayyab) so there is no PSNR comparison yet.
      roomAttemptSadness2 is still on the 3070 PC: copy it and run it after the new rooms (3.2 / 4.2 / E3).
    - Web viewer: fixture size card + clickable markers (FR10, 4.3); tsc / eslint / build pass; not checked in a
      browser; `export_web.py` now writes bottom / top. New `fixture_checklist.py` writes a per-room check sheet.
    - No tape measurements yet. New rooms are recorded 2026-11-13: each gets a logged full run first (they now come
      out level). Step 2 (upload / server) stays parked.

    This session:
    1. Finish R-037: result, stage times vs R-020 (96 min on the 3070) and R-031, the gravity tilt the export
       printed, layout vs R-023 (6.60 × 4.36 m, 2.72 m; tape 6.70 m), scale, fixtures vs the 15 of v10 (4.4: Umair
       confirms door_1, door_6, tube_light_1 if he knows the room), verdict, index row; decide with Umair whether the
       model goes to `saved_models/`.
    2. New rooms (3.2): one logged full run each as Umair records them; then `fixture_checklist.py` for each, and
       check that `report.json` shows a small `gravity` tilt and the layout has sensible walls / height.
    3. 4.2: when Umair returns the filled scan #3 sheet (`gs_r1112lev/semantic_v10/fixture_check.md`), write the
       per-room found / missed / false table (STATUS §7.5 and the plan; P&S if it shows a pattern). Same per new room.
    4. Tape: when Umair's numbers come, compare scan #3's 2.52 m height and 7.23 × 9.05 m, and one fixture size from
       the viewer card (4.3), against the tape; record the error in cm.
    5. If time is left: the 1.95° floor tilt on scan #3 (residual map), the missing 4th corner and 4.5 doorways from
       wall gaps, 4.7 CLIP margins on the new rooms, 4.9 right-angle priors / floor-plan export.

    Rules: every run (including layout-only re-runs and level_model) gets a TRAINING.md entry before it starts, errors
    as they happen, and only times that were actually recorded; never invent a number; rule / threshold changes that
    alter results are Umair's decision: bring options with a recommendation and record his answer in DECISIONS.md;
    owners in the plan are the team's to fill in; one run on the GPU at a time (`scripts/buildscan status` first);
    Node for the web UI runs through `micromamba run -n bs-ns`; update STATUS, LOG and the COMPLETION_PLAN rows at the
    end of the session; no AI attribution in commits.

**Later on 2026-11-12 (Umair, agent):** R-037 finished at 20:39:57 (103.0 min, no errors) → step 1 of the hand-over
above is done. Room 6.63 × 4.37 m (R-023 6.60 × 4.36 m); ARCore gravity 0.00° (old export would have been 0.57° off);
height 2.81 m vs R-023's 2.72 m because D-072 skipped a plane at 2.69 m that lay below the wall tops (new STATUS item,
needs a tape height or a look at the model); 18 fixtures vs 15 (door 7, switch 3, socket 2 are one more each), check
sheet `dataset/newRoomAttemptSadness/work_r1112nr_sfm/gs_r1112nr/semantic_v10/fixture_check.md`. Open for Umair:
`saved_models/` or not, fill the sheet. Details: TRAINING.md R-037.

## 2026-11-12 · Tayyab (agent) · `exp/fast-pipeline`
- Did: profiled training (torch.profiler) and sped up the pipeline. `geo_splatfacto.py`: exact replacement of splatfacto's
  bilateral-grid total-variation loss (was ~30 ms of every step) and colour affine; with the blur model, the colour grid
  is applied once to the averaged render. `mono_prior.py`: image reading and saving in threads (identical output).
  `fast_mvs.py`: `--photometric`, `--iters`, `--suffix`. `sfm_colmap.py`: `--skip_retriangulation`. `run_v8.py`:
  `--init_args`. `semantic2d.py`: tile pass batched (not yet run). `select_sharp.py`: extracts `imu.npz` itself.
- Runs: R-062 (training 42.5 → 28.2 min, equal quality), R-063 (dense init 20.1 → 7.5 min, equal quality), R-064 (mapper
  settings; the default mapper is not deterministic), R-065 (everything incl. the SfM shortcut: 61.6 min but worse,
  rejected), R-066 (new room `scan_3028a4de8fa0`, a tiered lecture hall: 48.8 min end to end with normal SfM).
- Tried and dropped: parallel `plane_seg.py` (no gain on Windows: allocation-heavy numpy serialises across processes).
- Problems: two background runs stopped with exit code 4 (agent shell ended); `--init_args "--photometric"` parsed as an
  option; missing `imu.npz` on a fresh capture; port 8000 of the upload server reachable from the internet (STATUS 7.1).
- Shared the raw newRoomAttemptSadness capture with a friend as a zip (first version without `imu.npz`: run
  `python src/arcore3dgs/imu.py dataset/newRoomAttemptSadness` once, or use this branch's `select_sharp.py`).
- Later the same day: Tayyab saw a "mini room inside the room" in the lecture-hall model (R-066). Diagnosis: GLOMAP placed
  ~175 frames (after ARCore lost tracking) at ~0.38× scale; ARCore-guided matching had linked them weakly. Found with a
  per-frame SfM-vs-Metric3D depth ratio (`src/arcore3dgs/sfm_scale_check.py`; newRoom control: 0 bad frames). Tayyab measured a
  table in the outer room: real length, so the main scale is right. R-067: incremental mapper, 581/842 frames, correct
  scale, front/right-side walk split off. R-068 (Tayyab chose: train on the main part): 35.8 min, no mini room
  (`gs_v10inc/topdown_vs_R-036.jpg`). New open decision OD-11 (scale check + mapper fallback).
- Next: Tayyab decides on the fast recipe (DECISIONS OD-10) and the SfM fallback (OD-11); semantics speed (batched tiles) check; tape-measure the
  lecture hall; a second normal-SfM run of newRoom would show how much SfM randomness alone moves quality.

## 2026-11-13 · Tayyab (agent) · `exp/fast-pipeline`
- Did: committed the speed-up work in parts (training, init, prior, SfM option, semantics batching, scale check, records)
  and merged `origin/master` (48 commits: numbered scans D-065/D-066, USB upload, app v0.3.5–v0.3.7, R-028–R-031) into
  `exp/fast-pipeline`. Conflicts: `select_sharp.py` (Umair had fixed the same missing-`imu.npz` bug: master's version
  kept), `run_v8.py` (both sides added flags: `--init_args` and `--pgsr` / `--save_every` all kept), TRAINING.md and
  LOG.md (both added entries: master's first). My runs renumbered R-029–R-065 → **R-062–R-068**. New tool
  `src/arcore3dgs/sfm_scale_check.py` (MAP.md).
- Runs: none. Decisions: none (OD-10, OD-11 open for Tayyab).
- Problems: Tayyab is not sure the lecture-hall model (R-068) beats v9e2e; no baseline on that room.
- Next: OD-10 / OD-11; test the speed-ups with `--pgsr` and on Linux; run the batched semantics once; compare R-068
  with Umair's R-031 (probably the same hall); clean up experiment folders (ask first). Not pushed.

## 2026-11-14 · Tayyab (agent, overnight session) · `exp/overnight-2026-11-14`
Asked by Tayyab on 2026-11-13: work overnight on the Must tasks, improve the current output, check the app for capture
issues, use the existing datasets, try new techniques. Branch from `exp/fast-pipeline` (d936e66); nothing pushed.
- Did (code, each committed):
  - `scripts/run_full.sh` runs on Windows Git Bash too (repo venvs), so the 3070 PC runs the same full pipeline.
  - `layout.py`: ceiling = strongest horizontal candidate above the cameras with < 3% of the model above it (COMPLETION_PLAN
    4.1, R-030's 1.50 m); newRoom unchanged (2.72 m). R-030 itself is on the Linux PC: rerun its layout there.
  - `check_capture.py`: FAIL above a 15 px median predicted blur (scan_3028a4de8fa0 had 24.9 px and passed).
  - App (`android/`): the stop dialog says "Record again?" for such recordings, and the bad-quality buzz repeats every 3 s.
    Compiled locally with JDK 21; not tested on a phone.
  - `server/pipeline.py`: portable nerfstudio paths (2.2) and an optional v9 recipe `BUILDSCAN_PIPELINE=v9` running
    `run_full.sh` with stage progress (2.3); default still v3 (OD-7 open). Tests added.
  - `tape_check.py` (E2): model vs tape table; newRoom room length −10 cm / −1.49% from the v9 layout.
  - `sfm_scale_check.py` runs after the priors in `run_v8.py` (warning only, OD-11 open); flags shrunken blocks.
  - `semantic2d.py --tile_batch` (default 1): the batched tiles of `exp/fast-pipeline` were ~3× slower on the 8 GB GPU.
    Default output checked identical to the original code on 39 newRoom frames (detections.json equal).
  - `geo_splatfacto.py`: `--mcmc_cap` (gsplat MCMCStrategy) and `--revised_opacity` options.
  - Test coverage 45% locally (was 37.4%; gate 35%, D-054).
- Runs: R-069 roomAttemptSadness2 full v9 + PGSR (3.2: SfM 1,000 / 1,042 frames, 777 ARCore inliers; height 2.78 m;
  semantics resumed after the sem2d slowdown), R-070 MCMC 620k (rejected), R-041 speed-ups + PGSR (33 vs 46 min,
  25.02 / 0.8232), R-042 MCMC 1M (rejected), R-043 revised opacity (inconclusive), R-044 lower densify threshold.
- Decisions: none (agents do not decide). Open for Tayyab: OD-10, OD-11; for the team: OD-7; for Umair: the coverage gate.
- Problems: the PC has 16 GB RAM with ~9 GB free; a parallel test exhausted it and crashed COLMAP's matcher (R-069
  error 1): run one GPU job at a time. Disk 28 GB free at the start of the night.
- Next: see the end-of-night summary in the R-069 / R-044 entries and STATUS; rerun R-030's layout on Linux; tape sheets
  for the other rooms; test the app warning on a phone; OD-7 / OD-10 / OD-11.

## 2026-11-15 · Tayyab (agent) · `exp/overnight-2026-11-14`
- Did:
  - New recording `scan_009_057ed3beb4fc` uploaded over Wi-Fi (server on port 8010, dry_run, stopped after the upload);
    `check_capture.py`: FAIL (tracking lost 63.7%, median blur 21.7 px).
  - `select_sharp.py` / `run_v8.py --pose_free`: keep sharp frames without an ARCore pose; `sfm_colmap.py` handles
    them (temporal + retrieval pairs, left out of the Sim3); `layout.py` no longer crashes when no floor is found.
  - Web viewer (`prototype/web-ui`): 7 real models in the project list, local-only files (web-ui STATUS §4).
  - App (`android/`): persistent feature-point map (`FeatureMap.java`), coverage dots drawn every frame, raw depth paired
    with its own frame's pose, larger dots; debug APK built locally (JDK: Android Studio's JBR), not tested on a phone.
  - Corrected my own wrong claim in R-045 ("scale ~7× off": the ratio is against arbitrary COLMAP units).
- Runs: R-045 (v9 + PGSR on scan_009: 87 frames, rejected), R-046 (pose-free + ALIKED: 535 frames, inconclusive).
- Decisions: none. R-046 re-opens D-022 (ALIKED rejected) with new evidence: Tayyab's call, after a newRoom test.
- Problems: 16 GB RAM, so PLY→SPZ conversions waited for training to finish; disk ~98% full.
- Next: install the debug APK and check the dots + `depth/timestamps.csv`; `--pose_free` + ALIKED on newRoom; re-record
  scan_009's room; OD-7 / OD-10 / OD-11.

## 2026-11-16 · Umair · feature/step4-layout
- Did: Umair copied four new recordings onto this PC (scans #5–#8, all Infinix X6833B, 259.8–366.5 s; rooms not
  written down yet, STATUS "Which recording is which"). `prototype/web-ui/.gitignore` now ignores every per-run bundle
  in `public/scans/` except `newroom/` (D-061 addendum): `newRoomAttemptSadness_r1112nr/` from R-037 had shown as
  untracked because only `scan_*/` was ignored. Plan row 3.18 (optional, Thursday 2026-11-19): `hierarchical_mapper`
  and `--max_features 4096` against R-037 for SfM memory. Answered: where the stage times are (`gs_<tag>/stages.tsv`,
  `timing.json`, `scripts/buildscan results <scan> <tag>`, TRAINING.md entries); the web viewer already shows semantics
  for `newroom/` (Scan Layers: groups, tint, markers, size card, mesh), but no other scan is wired in.
- Runs: R-038 scan #8 full pipeline, R-023 recipe (tag `r1116`, started by Umair 12:27): 1,639 frames, killed by the
  kernel OOM killer in COLMAP `global_mapper` at 13:16:55 (26.1 GB, 16.2 M observations), failed. R-039 the same with
  `--window 9` (tag `r1116w9`, started 13:21:30): 1,118 frames, 10.8 M observations, global positioning 28.3 min with
  RAM down to ~2.1 GB available at 13:50 (swap 4 of 8 GB), passed; at 14:04 in bundle adjustment, run continuing.
- Decisions: D-061 addendum (ignore all bundles but `newroom/`, Umair); D-073 fewer frames for long recordings
  (`--window 9` for scan #8, Umair, chosen over fewer SIFT features and the incremental mapper).
- Problems: `buildscan watch` only said "STOPPED ... did not finish" for R-038; the OOM cause was only in
  `journalctl -k`. The agent's Bash permission check failed (no verdict) for part of the session, so two commits were
  made late. The agent first wrote in R-038 that scan #8 was the first Infinix capture and that it had ~10× more
  observations per frame: both wrong, corrected (same phone as scans #1–#3; ~4–6×).
  Not possible without sudo: more swap (Umair can add it: `sudo fallocate -l 24G /swap2.img && sudo chmod 600 /swap2.img && sudo mkswap /swap2.img && sudo swapon /swap2.img`; not done).
- Next: finish R-039 (stage times, gravity tilt, layout, height, fixtures, check sheet; Umair names the room); then
  scans #5–#7 (each a logged run; #5 is 352.5 s long, so use `--window 9` per D-073 and watch RAM). Umair to choose
  how new scans reach the viewer (scan picker or `mockData.ts`). Thursday 2026-11-19: plan 3.18. Tape heights and the
  fixture sheets (4.1, 4.2, 4.4) still wait for Umair (no tape today).

## 2026-11-19 · Umair · `feature/step4-layout` → `feature/viewer-all-scans`
- Did: read the records for Step 4. `feature/step4-layout` fast-forwarded to `feature/viewer-scan-008` (Umair's ask;
  it was 2 commits behind and nothing else: `b969f49` scan #8 project, `424ea4f` R-040 start). New branch
  `feature/viewer-all-scans` (not pushed): the web Projects tab lists every bundle in `public/scans/`
  (`/api/scans`, `src/lib/scanBundles.ts`, `src/lib/useAllProjects.ts`; opens at `/viewer/run-<folder>`), D-074.
  Wrote up R-039 (scan #8, finished 2026-11-16 16:08, 166.7 min, 11 fixtures) and R-040 (scan #7, finished 2026-11-18
  13:39:51, 200.6 min, 6 walls, ceiling 3.40 m, **0 fixtures: all 29 candidates rejected by the rules**), which were
  both still "running" in TRAINING.md.
- Found: `origin/master` has 43 commits the Step 4 branches do not (Tayyab's PR #7 and v0.3.8), including a second
  ceiling rule in `layout.py` (`d052301`), the plan.png crash fix (`a098711`) and `tape_check.py` (plan E2). A dry
  merge conflicts in 9 files; run IDs R-032 … R-040 and D-069 were used for different things on both sides (OD-12).
  Not merged: needs the team's choice on numbering.
- Runs: none started (R-039 / R-040 only written up). Decisions: D-074 (Umair's ask). Open: OD-12.
- Problems: my first `pkill -f "next start -p 3005"` matched its own shell and killed it (no harm; used the port's PID
  after). A placeholder splat count slipped into R-040 for one step and was replaced by the measured 1,840,851.
- Next: Umair looks at `/projects` in a browser (does an auto-listed scan render?); decide OD-12 with Tayyab, then
  merge `origin/master`; Step 4 Musts: tape (4.1), fixture sheets for scans #3, #8, #4 (4.2), why scan #7 has 0
  fixtures, FR10 size card vs tape (4.3); scans #5 / #6 still unprocessed.

## 2026-11-19 (Step 4 issues) · Umair · `feature/step4-layout` + one branch per issue
- Asked by Umair: turn every Step 4 item into an issue, work through the ones that do not need him, leave his for
  later, blockers into COMPLETION_PLAN. GitHub issues **#8 – #25** (labels `step-4`, `needs-umair` on #20 – #25).
- Branches (stacked, none pushed, none merged into `master`): `feature/13-fixture-sheets` (fast-forwarded into
  `feature/step4-layout`) → `fix/8-open-ceiling` → `feature/18-mesh-ceiling` → `fix/10-room-closed` →
  `feature/9-wall-openings` → `feature/12-plan-export` → `fix/11-wall-behind-boards` (tip; also carries the #9
  follow-up fixes and the records).
- Found: **scan #7 is a building under construction** (bare brick, no roof, empty openings, planks): its 0 fixtures
  (R-040) are most likely right; it exposed a false "ceiling" (sky), missing empty openings and plank faces taken
  as walls. Scan #3's 32.27 m² "floor area" was a triangle (4 walls, 3 corners), about half the room. Scan #3's
  1.95° floor tilt is a step (a raised platform?), not a tilt.
- Done: #13 (sheets with rejected candidates for scans #7 / #8), #8 (no-roof rule, R-053), #10 (closed-room check,
  floor area only for a closed outline, optional `--infer_gap`), #9 (wall-gap doorways / window openings, view-through
  minimum after R-054 showed 4 false ones on scan #3), #12 (plan.json / .svg / .dxf, stage 16), #18 (roughness
  measured, `--clean_ceiling` optional), #11 (`--debug`, optional `--raised_max`); measured and blocked on Umair's
  sheets: #14 (CLIP margins), #15 (switch frames); blocked: #16 (3070 PC file), #19 (`run-r1118` session open).
- Runs: R-053 (layout, six rooms, #8), R-054 (scans #7 / #3 layout → web, tag `r1119a`), R-055 (layout, six rooms,
  `--debug`, default vs options). Numbered from R-053: R-041 … R-051 exist on Tayyab's side (OD-12).
- Problems: the agent was not allowed to close the finished `run-r1118` screen session, so scans #5 / #6 could not
  start; twice wrote a guessed number into TRAINING (a splat count, an end time), both replaced by measured values
  before committing; `pkill -f` once matched its own shell; switched to an older stacked branch to commit and moved
  back (no rebase, per CLAUDE.md).
- Later the same day: R-055 (`--debug`, options) and R-056 (final defaults on scans #7, #3, #8, newRoom, tag
  `r1119b`: layout → semantics → mesh labels → web → plan, 15.6 min, no errors). #9 and #10 closed after R-056;
  newRoom's outline was wrongly flagged open in R-055 (a near-parallel step) and fixed (`8b7f7f2`). #17: the floor
  "tilt" is a step; `semantic3d.py --floor_win 0.06` fits scan #3 at 0.29° (default unchanged). New tests (openings,
  plan export) pass under pytest (92 passed with the compile check); ruff clean. Umair said "yes keep going":
  `feature/step4-layout` fast-forwarded to the tip.
- Issues: closed #8 #9 #10 #12 #13; open with a recommendation for Umair: #11 (`--raised_max 1.5`), #17
  (`--floor_win 0.06`, platform?), #18 (`--clean_ceiling 0.04`); blocked: #14 #15 (#21), #16 (3070 PC file), #19
  (`run-r1118` session). OD-13 lists the defaults to confirm.
- Next: Umair: close `run-r1118` and start scans #5 / #6 (#19), tape (#20), sheets (#21), browser check (#24), OD-13,
  OD-12 with Tayyab (#25). Agent, after that: the R-NNN for scans #5 / #6, per-room found / missed / false tables
  from the filled sheets, then the threshold work in #14 / #15.
- Later still (2026-11-19): Umair decided OD-13 → **D-075**: `run_full.sh` passes `--raised_max 1.5 --infer_gap 6`
  (layout), `--floor_win 0.06` (both sem3d passes), `--clean_ceiling 0.04` (mesh labels), `--square` (plan); script
  defaults unchanged. Seven older web bundles moved to `prototype/web-ui/scans_archive/` (gitignored, not served), so
  Projects shows the newest per scan (`newroom` and `scan_008_…_r1116w9` stay for the hand-written cards). Closing the
  finished `run-r1118` screen session was refused to the agent a second time: Umair closes it.
- Next: R-057 = the four rooms (scans #7, #3, #8, newRoom) layout → plan with the D-075 defaults (new tag), check the
  ceiling mesh and floor fits, then scans #6 and #5 (#19) once `run-r1118` is closed.

## 2026-11-19 (R-057, online site) · Umair · `feature/step4-layout`, `feature/vercel-deploy`
- Did: R-057 (the D-075 defaults on scans #7, #3, #8, newRoom, tag `r1119c`) compared with R-056 by a read-only script
  (layout / semantic JSON + `mesh.py`'s shell flatness on `mesh_clean.ply`). The `r1119b` bundles moved to
  `prototype/web-ui/scans_archive/` (README row). Closed #11 and #18 on GitHub; #17 stays open for the tape. Umair had
  closed `run-r1118`, so scan #6 started (R-058). Online site: Umair chose Vercel + Cloudflare R2 (D-076), deployed
  the Vercel project himself (`https://build-scan-3d.vercel.app/`, from `master`) and decided every scan so far may be
  public and that Tayyab may publish his too (D-076 addendum). Issues #26 (Umair: accounts) – #30. Code on the new
  branch `feature/vercel-deploy` (a git worktree at `../BuildScan3D-vercel`, so the running pipeline is not touched):
  `src/lib/remoteBundles.ts`, `mergeProjects.ts`, `scripts/publish_scan.py`, `buildscan publish|unpublish|published`,
  `tests/test_publish_scan.py`, `.env.example` keys; MAP and web-ui STATUS there.
- Runs: R-057 (16.7 min, no errors): scans #7 / #8 closed 4-wall rooms (17.99 / 26.44 m²), scan #3 tilt 1.95° → 0.29°,
  ceilings 4.3 → 0.04 cm; scan #8 lost a switch + socket plate on the dropped corner surface → asked Umair: furniture,
  so the option stays. R-058 scan #6 started 15:29:08 (`run-r1119`); R-059 scan #5 after it.
- Decisions: D-076 + addendum (Umair). Not a decision: scan #8's corner is furniture (Umair's answer, in R-057).
- Problems: with `--square`, `plan_export.py` writes `plan_square.*` and no `plan.svg` (by design; first read as missing
  output). The plan thumbnail of re-run tags (`work_r1118_sfm/gs_r1119c/`) was not found by `scanBundles.ts` (cards
  showed the logo) nor at first by `publish_scan.py`: both fixed on `feature/vercel-deploy`. `gh` from the scratch
  folder failed ("not a git repository"), rerun with `-R`. Turbopack refused a `node_modules` symlink in the worktree
  (hard-linked copy instead). No pytest / ruff in the project envs: the earlier session's scratch venv ran them (95
  passed on the relevant tests; 5 test files need `cv2` / `fastapi` / `requests` that venv lacks, as on the main checkout).
- Next: R-058 / R-059 write-ups and their check sheets; Umair: #26 (bucket, keys, `SCANS_BASE_URL` on Vercel, OK to
  push), then #30 (deploy, CORS, browser check); `pip install boto3` in `bs-server` before the first upload; ask
  Tayyab about publishing from the 3070 PC.
- Later (online site): Umair created the R2 bucket `build-scan-3d-scans` (public `https://pub-bb143f8a2567472b944c2c4f06f1f08c.r2.dev`) and an
  API token (later with admin read/write, needed to set CORS). The agent wrote the S3 keys into `.env` (new file,
  gitignored, mode 600; the Cloudflare API token value is not stored: not needed), installed boto3 in `bs-server`, set
  the bucket CORS (GET/HEAD, any origin) and published scan #7 `r1119c` as the first real upload (45.4 MB); the
  worktree site listed it from the bucket (3 of 3 requests). One `fetch failed` on the first try → one retry in
  `remoteBundles.ts` (`663f5d3`). Problem: `pkill -f "next dev -p 3006"` again matched the agent's own shell (as earlier
  on 2026-11-19); stopped by the port's PID afterwards. The keys were pasted into the chat: rolling the token later is
  Umair's choice.
- Later (Umair): "publish all always", never past 10 GB (**D-077**; cap 9.5 GB enforced in `publish_scan.py` `f948495`,
  rule in CLAUDE.md §6 Umair). Published: scans #4 (newRoom) `r1119c`, #1 `umair`, #2 `r1106lev`, #3 `r1119c`, #8
  `r1119c` and `r1116w9` (with #7: 7 bundles, 0.24 GB). Umair: deployed site lists only published scans, a local run
  lists local + published (`b7d3c86`); `prototype/web-ui/.env.local` holds `SCANS_BASE_URL` on this PC (gitignored).
  Umair allowed the agent to close `run-r1119` once its log says "all done", then start scan #5.
- Later still: **R-058 (scan #6) failed**: COLMAP `global_mapper` killed by the OOM killer at 16:14:39 (26.4 GB,
  12.56 M observations, the same size as scan #7 which passed alone); the agent's web work in parallel (dev servers,
  `next build`, tests, uploads) most likely tipped it; the OOM also killed VS Code helpers (ending that agent session)
  and the `run-r1119` / `viewer` screen sessions. Umair chose "same recipe, PC kept quiet": **R-059** (`r1119b6`)
  started 16:33:50; the agent logs free RAM each minute (`mem_r1119b6.log` in its scratch folder) and runs nothing
  heavy during SfM. Scan #5 becomes R-060. Umair added `SCANS_BASE_URL` in Vercel and allowed the push:
  `feature/vercel-deploy` pushed (86 commits ahead of `master`, CI passed); #26 closed. Umair keeps the R2 token for
  now. New issues **#31 – #38** for the next steps (STATUS §7.10, COMPLETION_PLAN rows 2.1 – 5.6); labels `step-2`,
  `step-3`.
- Next (agent): finish R-059 (close `run-r1119b6` once "all done", stage times, layout, fixtures, check sheet, publish
  within the cap), then R-060 scan #5 (`--window 9`, quiet PC); #30 Vercel preview check → PR to `master` only when
  Umair asks; #31 options for OD-7. Next free IDs: R-061, D-078. Umair: his items #16, #20 – #25 wait.
- Later (evening): R-059 (scan #6, `r1119b6`) finished, "all done" 19:37:41 (run_v8 162.5 min, SfM 86.1 of it; layout
  1.4, sem2d 17.6 min; `stages.tsv`); its write-up is still open. Umair asked to publish it and to merge everything
  except the cuDSS / COLMAP work into `master` so the deployed site shows it: scan #6 published (8 bundles, bucket
  0.28 GB of the 9.5 GB cap, D-077); `feature/step4-layout` up to `e74ee55` merged into `feature/vercel-deploy`
  (leaves out `e724252`, the cuDSS to-do), PR to `master`. The cuDSS work (D-078, R-061) stays on `exp/colmap-cudss`.

## 2026-11-23 (Step 4) · Umair · `feature/step4-triage`
- Done (agent for Umair, in the worktree `../BuildScan3D-step4`, from `origin/master` `8338680` because local `master`
  lacks PR #39; the main checkout stays on `exp/colmap-cudss` for R-071; `dataset/`, `saved_models/`, `tools/`,
  `semantic-env/` symlinked, hidden through `.git/info/exclude`): Step 4 triage table for Umair (done / blocked on Umair
  / agent-doable). R-059 (scan #6 `r1119b6`, finished 2026-11-19) written up in TRAINING from its files. Scan #6
  fixture check sheet (R-085) into a new folder `dataset/scan_006_1e457a214ce1/checks_r085/` (R-059's folder not
  written). `docs/progress/CHECKS_FOR_UMAIR.md` (MAP): room names, fixture sheets, newRoom's three detections, tape list
  with the pipeline values, browser check, scan #3 platform. Scan #6 added to the #14 / #15 numbers (STATUS §7.5, plan
  4.7 / 4.8). Wall roughness R-086 (read-only, CPU). STATUS recordings table: scan #5 not processed, scan #6 = R-059.
- Runs: R-085 (sheet, < 1 s), R-086 (wall roughness, 3.4 s). Nothing on the GPU: R-071 used it the whole session.
- Decisions: none. Waiting for Umair: 4.12 options for the rough walls; OD-12 layout re-run (GPU: `layout.py` renders
  with gsplat on CUDA) on scans #6 / #7 / #8 / newRoom, scan #3 in or out.
- Problems: `plan.png` labels walls by length, not number, so the check page names walls by length. `gh issue view`
  does not take `--comments` with `--json`.
- Next: OD-12 layout re-run in a GPU gap between speed tests (Umair's go); scan #6 `r071g6` layout / fixtures after
  R-071; Umair: `CHECKS_FOR_UMAIR.md`; scan #5 (R-060) needs a GPU slot.

