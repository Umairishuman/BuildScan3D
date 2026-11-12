# BuildScan 3D completion plan

2026-11-12 · Muhammad Umair

Every open task, grouped by pipeline step, so the product and the final evaluation are complete by **2026-12-04**.
Nothing is cut: Must = needed for a complete product and evaluation, Should = strengthens it, Could = done if time
allows. Owners are left blank for the team to fill in.

**Live copy:** the shared doc [BuildScan 3D Completion Plan](https://claude.ai/artifact/1V2YG8GSfBEpLXmnTJdctC) holds
the Owner and Status dropdowns the team edits. This file is a snapshot of that doc taken on 2026-11-12 (written into the
repo the same day, see LOG.md); when owners or statuses change there, update this file in the same session.

## Weeks and gates

| Week | Dates | Main work | Gate at the end |
|---|---|---|---|
| Week 1 | 2026-11-13 → 11-19 | Record + process new rooms; server runs the v9/v10 pipeline; fix the layout ceiling (R-030); owners + OD-1/4/6/7 decided | **G1 · 2026-11-19:** new rooms processed on the server |
| Week 2 | 2026-11-20 → 11-26 | Evaluations E1–E9 measured; speed work with before / after; web: real scans, states, fixes; final report draft | **G2 · 2026-11-26:** every evaluation number measured |
| Week 3 | 2026-11-27 → 12-04 | UAT walkthrough; report, poster, demo video; Should and Could rows; freeze: tag `master` + APK | **G3 · 2026-12-04:** report, demo and UAT done |

Each gate is checked by all three of us; a Must row that misses its gate moves the rows that need it (see the Needs
column).

## Step 1 · Capture app (Android)

The app works and v0.3.5 is released (2026-11-12), but nothing since v0.3.4 has been tested on a phone, and the
evaluation needs new rooms recorded with tape measurements.

| # | Task | Done when | Needs | Priority | Week | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1.1 | Ask Tayyab whether he has app changes that are not pushed | Answer recorded in LOG; any changes on a branch | — | Must | W1 |  |  |
| 1.2 | Install v0.3.5 on the phone: Play Protect warning, server search finds the PC, "Check for updates" works | All three checked on the Infinix, noted in STATUS 7.7 | 2.1 | Must | W1 |  |  |
| 1.3 | Upload one recording from v0.3.5 | `camera.csv`, `anchors.csv` and the lens files arrive on the server | 2.1 | Must | W1 |  |  |
| 1.4 | Record 2–3 real rooms with the capture protocol (two loops at chest and knee height, 360° turns from 2–3 points, every wall at two heights, close passes, all lights on) | Rooms on the PC, each checked READY by `buildscan check` | 1.2 | Must | W1 |  |  |
| 1.5 | Tape-measure every recorded room: lengths, room height, doors, one switch and one socket height, 3 repeated readings each | Tape sheet per room saved next to the dataset | 1.4 | Must | W1 |  |  |
| 1.6 | Re-measure dropped frames (NFR1, ≥ 30 FPS) and the quality-check time per frame (NFR2, < 16 ms) | Both numbers measured on the phone, in STATUS §4 | 1.2 | Should | W2 |  |  |
| 1.7 | Find out why ARCore depth was stale in newRoomAttemptSadness (all maps identical, confidence ≈ 0) | Cause found and fixed, or depth turned off (1.12) | — | Should | W2 |  |  |
| 1.8 | Tune the quality thresholds on the phone (predicted blur warn > 5 px, bad > 10 px) | Thresholds checked on a test walk, values recorded | 1.2 | Should | W2 |  |  |
| 1.9 | Coverage overlay and tier-2 guidance: show what is left to scan (ceiling, floor, depth holes, blur, dark, tracking) | Overlay tested on the phone | — | Should | W2 |  |  |
| 1.10 | Download and preview the finished model on the phone | A processed scan opens on the phone | 2.4 | Should | W2 |  |  |
| 1.11 | Decide on and redo any of the features reverted on 2026-10-23: surface + edge map, live layout overlay, autofocus toggle, feature-starvation warning, vertical planes (OD-5) | Team decision recorded; chosen ones built | OD-5 | Could | W3 |  |  |
| 1.12 | Turn ARCore depth off if dropped frames persist (160×90, ~25% valid, only feeds the coverage overlay) | Decision from the 1.6 numbers | 1.6 | Could | W3 |  |  |
| 1.13 | Lock exposure and white balance (needs the Shared Camera API refactor) | Works on the phone, or recorded as not done | — | Could | W3 |  |  |
| 1.14 | Move the app code out of `hello_ar_java` into its own folder and package; note the JDK 21 build requirement | App builds in CI from the new path, MAP updated | — | Could | W3 |  |  |

## Step 2 · Upload, server and cloud processing

The phone uploads to the FastAPI server, but the server and RunPod still run the old v3 recipe; the v9/v10 pipeline
only runs from the command line.

| # | Task | Done when | Needs | Priority | Week | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2.1 | Run the upload server from a checkout that includes PR #4 (local `master` is behind; the server runs from `exp/first-linux-run`) | `/health` answers from the updated code; a v0.3.5 upload keeps all files | — | Must | W1 |  |  |
| 2.2 | Port `server/pipeline.py` to Linux (last part of STATUS 7.1 1f) | Server starts a job on this PC without Windows paths | — | Must | W1 |  |  |
| 2.3 | Server jobs run the v9/v10 pipeline (`scripts/run_full.sh`) instead of v3 (OD-7) | An uploaded recording produces splat, layout, semantics, mesh and web bundle | 2.2, OD-7 | Must | W1 |  |  |
| 2.4 | Job progress and results go back to the app and the dashboard (stage, percent, model link) | App shows progress; the finished scan opens in the dashboard | 2.3, 5.3 | Must | W2 |  |  |
| 2.5 | Final-1 exit gate (a): a 60 s capture uploads and triggers processing end to end | One logged run (TRAINING R-NNN) from phone to model | 2.3, 1.3 | Must | W2 |  |  |
| 2.6 | Back up the release signing key `~/.buildscan3d-keys/` off this PC | Copy stored in an agreed safe place | — | Should | W1 |  |  |
| 2.7 | Docker image from `scripts/setup_linux.sh` (2a), built on GitHub Actions (2b), tested (2c) | Image runs the v9 pipeline on RunPod | 2.3 | Should | W2 |  |  |
| 2.8 | RunPod end to end: create pod, process, download, terminate; find why it works poorly | One logged RunPod run with every error | 2.7 | Should | W2 |  |  |
| 2.9 | Run the pipeline on the friend's PC (owner, GPU, OS in STATUS §6) | One logged run there | — | Could | W2 |  |  |
| 2.10 | Dockerise the upload server so it runs the same on Windows and Linux | Server container starts on both | 2.7 | Could | W3 |  |  |
| 2.11 | Proposal FR3 / FR4: object storage and the Redis / Node job queue, or a written reason for the FastAPI design (OD-2) | Built, or the decision recorded for the report | OD-2 | Could | W3 |  |  |
| 2.12 | Always-on server (cheap VPS) so uploads work without the lab PC | Phone uploads to the VPS | 2.10 | Could | W3 |  |  |

## Step 3 · Reconstruction (SfM + 3DGS)

The v9 recipe gives the best model (R-023) but has been tested on one room only and takes 96 min on the RTX 3070 and
41.7 min on this PC for a 97 s video (R-030); the proposal target is 15 min for a 60 s video on a 4090.

| # | Task | Done when | Needs | Priority | Week | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3.1 | Machine agreement: copy newRoomAttemptSadness here, run v9, compare with R-020 / R-023 | Logged run; PSNR / SSIM / scale within run-to-run noise of the 3070 | — | Must | W1 |  |  |
| 3.2 | Process roomAttemptSadness2 and every new room (1.4) with the full v9 pipeline | One logged run per room, models kept in `saved_models/` | 1.4 | Must | W1 |  |  |
| 3.3 | Optimise the processing time end to end; measure every change with the stage times | Before / after stage table for each change in TRAINING | 3.1 | Must | W2 |  |  |
| 3.4 | Speed ideas to test in 3.3: blur only in the last third, photometric-only PatchMatch, ViT-S depth prior, faster `fast_mvs` (photometric or every 10th frame), faster `plane_seg` (~11 min CPU) | Each tried and kept or rejected with numbers | 3.3 | Must | W2 |  |  |
| 3.5 | Time the pipeline on a cloud RTX 4090 (NFR3 is stated for a 4090) | Measured total and stage times on a 4090 | 2.8 | Should | W2 |  |  |
| 3.6 | Repeat runs of one setting to measure run-to-run noise | ≥ 3 runs, spread of PSNR / SSIM / scale reported | 3.1 | Should | W2 |  |  |
| 3.7 | Ceiling and upper walls are the weakest surfaces: capture guidance to look up, or stronger planar priors | Ceiling quality improved on one room, measured | 3.2 | Should | W2 |  |  |
| 3.8 | IMU fallback (the stated novelty): decide whether v9 uses it (OD-6) | Decision recorded with a reason for the report | OD-6 | Should | W1 |  |  |
| 3.9 | IMU fallback: tune BA pass 2 so it keeps PnP accuracy (8.2 → 15.1 px today); use bridged frames with per-frame pose refinement | Accuracy kept after BA; bridged frames used in training | 3.8 | Should | W2 |  |  |
| 3.10 | Rolling-shutter model and per-frame exposure from `camera.csv` (v0.3.5 now uploads it) instead of the fixed 1/45 s | Tested on one v0.3.5 room against the fixed value | 1.3 | Could | W3 |  |  |
| 3.11 | Full PGSR multi-view geometric + photometric consistency (removes the faint stripes on plain walls; ~2× training time) | Tested on one room, kept or rejected | — | Could | W3 |  |  |
| 3.12 | Planar + blur together on v6's SfM | Run logged | — | Could | W3 |  |  |
| 3.13 | Mask reflective surfaces (glossy floor, glass) out of SfM, depth and evaluation | Mask applied on one room, effect measured | — | Could | W3 |  |  |
| 3.14 | Free-space-aware training: `consistency.py` as a loss (novelty idea) | Tested on one room | — | Could | W3 |  |  |
| 3.15 | Anti-aliasing (Mip-Splatting idea, gsplat `antialiased`) with an antialiased-aware viewer | Zoomed views compared | 5.10 | Could | W3 |  |  |
| 3.16 | Faster 3DGS methods with their own CUDA rasterizer (FastGS, Taming-3DGS budget), cloud only | Tried on RunPod, or recorded as future work | 2.8 | Could | W3 |  |  |
| 3.17 | Legacy own-trainer items (block-wise training, `diagnose.py`, Census + SGM, PocketGS, `--near_cam`, 7.4% floaters): confirm obsolete | Each marked obsolete in STATUS with the reason | — | Could | W3 |  |  |

## Step 4 · Room layout, semantics and mesh

Semantics v10 found 15 of 17 fixtures on newRoomAttemptSadness, but its rules were tuned on that same room, and the
layout picked a wrong ceiling in R-030 (1.50 m in a room ~3.1 m tall).

| # | Task | Done when | Needs | Priority | Week | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4.1 | Fix the ceiling detection in `layout.py` (R-030: 1.50 m; model extent 3.08 m) | R-030 and the new rooms give the right height against tape | 1.5 | Must | W1 |  |  |
| 4.2 | Run semantics v10 on roomAttemptSadness2 and every new room; a person checks each fixture | Per-room table of found / missed / false fixtures | 3.2 | Must | W2 |  |  |
| 4.3 | Fixture dimensions in the viewer (width, height, height above floor, area) (FR10) | Clicking a fixture shows its size; checked against tape on one room | 4.2 | Must | W2 |  |  |
| 4.4 | Confirm the three new v10 detections on newRoom (`door_1`, `door_6`, `tube_light_1`) | Checked by the person who knows the room | — | Should | W1 |  |  |
| 4.5 | Open doorways (no door leaf) from gaps in the layout walls; windows on room 2 | Doorways found on one room | 4.1 | Should | W2 |  |  |
| 4.6 | Fix the two misses on newRoom: socket under the ironing table, round light #14 (the "clock" decoy wins) | Both found without new false positives | — | Should | W2 |  |  |
| 4.7 | Widen the thin CLIP margins (false sockets 0.45–0.47 vs threshold 0.5) and re-check the 25% switchboard rule (3 plates) | Rule checked on the new rooms | 4.2 | Should | W2 |  |  |
| 4.8 | Small switch plates need ~30 confirming frames: lower the need or add capture guidance | A fast walk past a switch still finds it | 4.2 | Should | W3 |  |  |
| 4.9 | Right-angle priors and an as-built floor-plan export (format agreed) | Plan exported for each room | 4.1 | Should | W2 |  |  |
| 4.10 | Layout for spaces that are not rooms (R-029 corridor end: 1 wall, 0 corners) | Corridor gives sensible walls or a clear warning | 4.1 | Could | W3 |  |  |
| 4.11 | Edge-based corner and blank-wall detection (gravity-aware lines, wall–floor boundary) | Plain walls found on one room | 4.1 | Could | W3 |  |  |
| 4.12 | Mesh: wall 3 and the ceiling stay rough (> 2.5 cm); mark `structure.py` superseded by `layout.py` | Roughness reduced and measured; STATUS updated | — | Could | W3 |  |  |

## Step 5 · Compression and web delivery

The viewer loads `.spz` groups through Spark (R-030 bundle: 20.4 MB with an 8.3 MB mesh). Zaid's `feat/splat-compress`
adds pruning + colour reduction (162 → 54 MB on R-030) and `.ksplat` settings (18.4 MB with a small loss, 40.2 MB
visually lossless); the `.ksplat` converter itself is not in the repo.

| # | Task | Done when | Needs | Priority | Week | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5.1 | Decide `.spz` (in use) or `.ksplat` (proposal) for delivery (OD-1) | Decision in DECISIONS.md with sizes and quality of both | 5.4 | Must | W1 |  |  |
| 5.2 | Merge or close `feat/splat-compress` and `exp/trainer-arkitscenes` (OD-4); if kept, add the `.ksplat` converter or its install step | Branches merged through a PR or closed with a note | 5.1 | Must | W1 |  |  |
| 5.3 | Every processed scan appears in the dashboard without hand-editing `mockData.ts` | A new run's bundle shows up and opens | 2.3 | Must | W2 |  |  |
| 5.4 | Measure compression quality: render original and compressed at the same views (PSNR / SSIM) on a real GPU, for `.spz` and `.ksplat` | Table of size and quality for both formats on 2 scans | — | Must | W1 |  |  |
| 5.5 | Web UI step 8: empty and error states (S9) | All pages handle no data and failed loads | — | Must | W2 |  |  |
| 5.6 | Fix the web UI known issues: list view toggle, `globals.css` conflicts, stub buttons, every floor-plan room opens the same model, inert measurement types, missing thumbnails | Each issue closed in `prototype/web-ui/STATUS.md` §6 | — | Should | W2 |  |  |
| 5.7 | Try Zaid's opacity pruning + colour reduction before the `.spz` export; check quality (D-040 found floater pruning hurt) | Kept or rejected with numbers | 5.4 | Should | W2 |  |  |
| 5.8 | Adaptive splat budget / level of detail for weak devices (FR9, NFR5) | Viewer holds ≥ 30 FPS on the target phone | E5 | Should | W2 |  |  |
| 5.9 | Measuring: snap clicks to corners and edges (removes the endpoint bias) | Snapping on; tape comparison repeated | 4.1 | Should | W2 |  |  |
| 5.10 | Antialiased-aware viewer (pairs with 3.15) | Viewer renders an antialiased model correctly | — | Could | W3 |  |  |

## Evaluation

These are the numbers the proposal (v4) promises and the examiners will ask for; today only NFR4 (compression) and
NFR6 (accuracy, on v3) are met with measurements.

| # | Task | Done when | Needs | Priority | Week | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | Final-1 exit gate (d) / contribution 1: COLMAP with vs without ARCore priors on low-texture captures (ATE, track completion) | Table for ≥ 2 rooms in the report | 3.2 | Must | W2 |  |  |
| E2 | Accuracy vs tape (NFR6 ≤ 5%): script that compares model measurements with tape, mean / max error in cm, on ≥ 2 rooms with v9 | Script in repo; numbers per room | 1.5, 3.2, 4.1 | Must | W2 |  |  |
| E3 | Semantic precision / recall / mIoU on rooms the rules were not tuned on (contribution 3) | Per-class table on ≥ 2 rooms | 4.2 | Must | W2 |  |  |
| E4 | Pipeline time per stage, per machine (NFR3: 60 s video in 15 min on a 4090) | Table: this PC, 3070, 4090 if available | 3.3, 3.5 | Must | W2 |  |  |
| E5 | Viewer FPS, GPU memory and load time on a mid-range Android browser vs an unoptimised viewer (NFR5 ≥ 30 FPS, contribution 4) | Measured table for 2 scans | 5.3 | Must | W2 |  |  |
| E6 | Compression size and quality (NFR4 ≥ 60%) for the chosen format | From 5.4, in the report | 5.4 | Must | W2 |  |  |
| E7 | Metric scale: a more robust Sim3 to ARCore (several segments, `anchors.csv` corrections; fast SfM is 1.5–1.9% off) | Scale error reduced, measured on tape rooms | E2 | Should | W2 |  |  |
| E8 | Thesis metrics per room: reprojection error before / after BA, MVS coverage, PSNR / SSIM on held-out views, free-space violation ratio | Table per room | 3.2 | Should | W2 |  |  |
| E9 | Capture metrics on the phone: NFR1 dropped frames, NFR2 quality-check time | From 1.6, in the report | 1.6 | Should | W2 |  |  |
| E10 | Certified measurements (novelty idea): every measurement with an error bound from pose, depth and multi-view agreement, validated against tape | Bounds shown in the viewer and checked on one room | E2 | Could | W3 |  |  |

## Infrastructure and repository

`master` must hold everything that is shown at the final evaluation, with records up to date and CI green.

| # | Task | Done when | Needs | Priority | Week | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| I1 | Merge `exp/first-linux-run` (Linux scripts, `buildscan`, records) into `master` through a PR | PR merged with CI green | — | Must | W1 |  |  |
| I2 | Write the missing tests; raise the coverage gate back to 40% (D-054; now 35%, measured 37.4%) | CI passes at 40% | — | Must | W3 |  |  |
| I3 | Update README and AGENTS.md: folder tree, dropped MEP / YOLOv8 layers, ~75 min, `structure.py` (OD-9) | Both match the current pipeline | OD-9 | Must | W3 |  |  |
| I4 | Keep the records current: a TRAINING entry for every run, LOG per session, STATUS at the end of each session | Checked at each weekly gate | — | Must | W1–W3 |  |  |
| I5 | Archive the dead files with their owners' agreement: `train_fixed2_backup.py`, `train_v3_backup.py`, old `run_*.bat`, `scratch/`, `ViewerHUD.tsx` (OD-8) | Moved to archive folders, MAP updated | OD-8 | Should | W3 |  |  |
| I6 | GitHub settings from CI_CD.md §6: branch protection on `master` requiring `CI passed`, release permissions | Settings checked and recorded | — | Should | W1 |  |  |
| I7 | Tailscale: Umair's laptop in the tailnet, SSH tested, key expiry off; lab Wi-Fi block (wired or ask IT); login-screen suspend | Laptop reaches this PC over SSH | — | Should | W1 |  |  |
| I8 | Update STATUS items that no longer apply (e.g. "merge `feature/semantics-mesh`", settled by D-051) | Marked obsolete with the reason | — | Should | W1 |  |  |
| I9 | Code reorganisation step 2: regroup `src/arcore3dgs/` by stage (MAP §10), checked with a real run | Moves done on a branch, one run passes | 3.1 | Could | W3 |  |  |
| I10 | Moving to another lab PC: `scripts/sync_to_pc.sh` + a new-PC checklist | Script and checklist in the repo | — | Could | W3 |  |  |
| I11 | CI gaps: top-level script logic untested, no Android unit tests, no GPU stages | At least Android unit tests added | I2 | Could | W3 |  |  |
| I12 | Remove the revoked RunPod key from git history (`00bc021`; needs a history rewrite + force-push) | Team decision recorded; done or declined | team | Could | W3 |  |  |

## Final report, UAT, poster and demo

The final submission needs a report, a user acceptance test, a poster and a working demo; none of them is started
except the poster guide (Tayyab, 2026-11-11).

| # | Task | Done when | Needs | Priority | Week | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | Book the UAT with the construction stakeholder (proposal v4 §10) | Date agreed | — | Must | W1 |  |  |
| R2 | Run the UAT: supervised walkthrough, capture → model → measurement, feedback form | Notes and feedback recorded in `report/final-eval/` | 2.5, 5.3 | Must | W3 |  |  |
| R3 | Final report in `report/final-eval/`: changes of plan (D-014, D-033), method, every evaluation table, limits | Draft by W2 end, final by 2026-12-04 | E1–E9 | Must | W2–W3 |  |  |
| R4 | Poster from `docs/poster/Poster_Content_Guide.md` | Poster printed / submitted | E2, E3 | Must | W3 |  |  |
| R5 | Demo video (capture on the phone → processed model → web viewer with labels and measurement) | Video recorded and saved | 2.5 | Must | W3 |  |  |
| R6 | Final slides and a live-demo script with a fallback (pre-processed scan) | Rehearsed once by all three | R5 | Must | W3 |  |  |
| R7 | Freeze: tag `master`, final APK release, every record updated | Tag and release exist; STATUS §7 reviewed | all Musts | Must | W3 |  |  |

## Decisions the team must make first

These block tasks above; each answer goes in DECISIONS.md with the names of who decided. Recommendations are a
starting point, not a decision.

| Decision | Blocks | Options | Recommendation |
| --- | --- | --- | --- |
| Who owns which task | everything | Split by proposal ownership (Umair: capture + upload, Tayyab: orchestration + 3DGS, Zaid: semantics + compression + web) or by load | Start from proposal ownership, then balance the Must rows |
| OD-7: server runs v9/v10 | 2.3, 2.5, 5.3 | Wire `run_full.sh` into the server; or keep v3 on the server | Wire in v9/v10: exit gate (a) and the demo need it |
| OD-1: `.spz` or `.ksplat` | 5.1, 5.2, E6 | `.spz` (in use, Spark); `.ksplat` (proposal, Zaid) | Decide on the 5.4 numbers; the `.spz` splats are already smaller (~12 MB vs 18.4 / 40.2 MB), but their quality is not measured |
| OD-4: Zaid's branches | 5.2 | Merge `feat/splat-compress` tools as a pre-export step; keep as notes; close | Merge the analysis + pruning scripts; record results for the report |
| OD-6: IMU fallback in v9 | 3.8, 3.9 | Use it; keep it as a separate novelty result | Keep it as a measured novelty result, since SfM registers 1165/1166 frames |
| OD-2: queue design | 2.11 | Build Redis / Node queue; keep FastAPI + threads with a written reason | Decide early; it changes the report's architecture chapter |
| OD-5: reverted app features | 1.11 | Redo some; leave out | Decide after the 1.6 frame-drop numbers |
| OD-8 / OD-9: archive dead files; fix README / AGENTS.md | I3, I5 | Yes / no, and where | Yes, in week 3 |
| Which rooms to record | 1.4, E1–E3 | Number of rooms, which buildings | ≥ 2 real rooms plus roomAttemptSadness2 |

## Sources

Built from the repository records on branch `exp/first-linux-run`: `docs/progress/STATUS.md` §4 and §7 (every open
item is in a row above), `DECISIONS.md` (open decisions OD-1 to OD-9, D-014, D-033, D-040, D-051, D-054, D-061),
`TRAINING.md` (R-020, R-023, R-029, R-030), `prototype/web-ui/STATUS.md` §6, proposal v4, and Zaid's
`feat/splat-compress` notes, with its scripts run on R-030 on 2026-11-12.
