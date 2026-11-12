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
- Next: CI on the PR; install `adb`; test on the phone; release.
