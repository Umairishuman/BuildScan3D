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
- Next: CI on the PR, merge, CD release v0.3.4; Umair uploads today's recording, then uninstalls the old app and installs
  v0.3.4; ufw rules; then `check_capture.py` and the R-028 run options.
