# Mid-Report Fix Log

Record of the correction pass on `F26_FYP1_Mid_Report_LaTeX_Complete/`, done against
`docs/report/REPORT_FIX_BRIEF.md` (authoritative) following `docs/report/CLOUD_SESSION_PROMPT.md`.
One commit per phase on branch `claude/jolly-wozniak-42woyl`. **The document was not compiled**
(TeX Live is not installed in the session); see "Check on first local build" at the end.

All chapter files are under `F26_FYP1_Mid_Report_LaTeX_Complete/chapters/`. Reminder: `chapter8_testing.tex`
renders as Chapter 7 and `chapter9_development_evidence.tex` as Chapter 8. New cross-references use `\ref`.

---

## Per decision

### 1. Processing time (phase 1)
- **Changed:** every "<15 min" / "<5 min" claim now says: measured ~75 min on the RTX 3070 (matching 23,
  mapping 6, training 45). The FYP-2 target is under 35 min on an RTX 4090, labelled as a projection
  everywhere. NFR-P1 and its acceptance row say the measurement is outstanding. Success criterion and
  objective updated. RunPod pods are described as RTX 4090 by default, selectable at runtime (`server/main.py`,
  `server/runpod_client.py`).
- **Files:** `chapter1_introduction`, `chapter2_research`, `chapter3_iteration_plan`, `chapter4_requirements`,
  `chapter5_design`, `chapter6_iteration1`, `chapter8_testing`, `chapter9_development_evidence`,
  `chapter10_fyp2_plan`, `conclusion`, `06_executive_summary`, `appendix_requirements`, `appendix_action_register`.
- Also: `AGENTS.md` Stage 3 claimed "< 5 minutes on RTX 4090"; corrected in phase 5.

### 2. Delete the 3090 row (phase 1)
- **Changed:** the "Processing time (3090) 12 / 14 min" row is gone from the results table; every other
  RTX 3090 timing claim is gone (risk table, limitations, action register, summaries).

### 3. Accuracy target = 5% (phase 3)
- **Changed:** every "<1%" target is now 5%. The measured 0.19% mean / 0.29% worst case is reported as far
  better than the target. The full tape-measure table is in the testing chapter (`tab:tape`). Invented
  "<2 cm wall-to-wall" / "1.2 cm" / "0.5%" figures are removed. The "Sim3 scale 1.000-1.003" claim was
  really the old bundle adjustment's trajectory-length check, so it was removed as a Sim3 claim.
- **Files:** `04_abstract`, `06_executive_summary`, `chapter1_introduction`, `chapter3_iteration_plan`,
  `chapter4_requirements`, `chapter6_iteration1`, `chapter8_testing`, `chapter10_fyp2_plan`, `conclusion`,
  `appendix_action_register`.

### 4. Headline v6 = 26.52 dB / 0.8886 (phase 2)
- **Changed:** abstract, executive summary, iteration outcome, TC-13 and conclusion now give v6 on the
  42-frame held-out set. The results table (`tab:quality`) is rebuilt from v3 -> v4_sharp -> v5 -> v6.
  A before/after table of the pose fix (`tab:posefix`) is added.

### 5. 27.81 dB is a separate result (phase 2)
- **Changed:** 27.81 dB (and 28.08 dB training) appears only as splatfacto vs. our own trainer (24.70 dB)
  on `roomAttemptSadness2`, in `chapter2_research`, `chapter5_design` and `chapter8_testing`, never with an SSIM.
- The misattributed "22.7 -> 27.8 dB" story is rewritten: 22.67 dB / 0.782 is `gs_colmap_nc` (our trainer
  with COLMAP depth); the pose fix is described with the summary's before/after (21.9 -> ~28 dB training
  fit, SSIM 0.78 -> 0.86, badly placed surfaces 7-23% -> 3%). 2.32 -> 0.62 px is kept and attributed to
  bundle adjustment (626k observations). Lens distortion corrected to k1 ~ 0.09, k2 ~ -0.22.

### 6. Second room (phase 2)
- **Changed:** "Room B 26.4 dB / 0.862" deleted. Second room = SSIM 0.91, 1% badly placed surfaces,
  measured by Muhammad Tayyab. **No second-room PSNR anywhere**; it is written as "not yet measured".
- Invented room dimensions (Room A 4.2 x 3.1 m, Room B 5.0 x 3.5 m) are removed; the reference recordings
  are named (`newRoomAttemptSadness`, `roomAttemptSadness2`).

### 7. MEP out, structural layer in (phase 5)
- **Changed:** all YOLOv8-Seg / MEP / pipes / conduits / HVAC / semantic text removed from scope,
  objectives, modules, success criteria (mIoU criterion removed), comparison table, gaps, work breakdown,
  test plan, FYP-2 plan (chapter 10 rewritten), limitations, conclusion and abbreviations (MEP, HVAC).
  Replaced with the structural layer (`structure.py`): wall planes, corners, wall lengths
  6.65-6.68 x 4.45-4.48 m, 5 doors detected automatically, floor plans, 1:1 measurement.
- `AGENTS.md` section 3 updated: Stage 4 is now the structural layer; Stage 5 no longer mentions semantic
  toggles; Stage 3 no longer claims "< 5 minutes".
- The unsourced "$0.30-0.70 per scan" cost in the executive summary was removed (cost not yet measured).

### 8. Iteration 1 status (phase 6)
- **Changed:** "core pipeline complete, refinement ongoing" in the abstract, executive summary heading,
  iteration plan, iteration outcome, validation status and conclusion. Open items listed everywhere:
  3DGS refinement, 3D mesh creation, structural layer completion, web workspace. "No recovery plan needed"
  replaced with an honest recovery plan. FYP-1/FYP-2 split kept.

### 9. 3D mesh creation (phase 6)
- **Changed:** added as in-scope planned work (scope list, work breakdown, work remaining, FYP-2 modules,
  summaries), always as "not yet scheduled"; it is not placed in any iteration, week or timeline row.

### 10. X-ray removed (phase 4)
- **Changed:** all mentions deleted: out-of-scope bullet, panel-feedback bullet, action register row 3
  (in `chapter3_iteration_plan` and `appendix_action_register`, rows renumbered), the deviation entry, and
  the design-evolution note. `grep -i "x-ray"` over the chapters returns nothing.

### 11. Supervisor meetings (phase 7)
- **Changed:** the eight-meeting table is replaced by "First meeting" / "Second meeting", no dates, with
  the agreed agenda (work completed to date, techniques used, mid-evaluation expectations). A sentence
  says no minutes were taken and nothing in the report is presented as supervisor-approved. All approval
  claims removed. Outcome column dropped because no outcomes were recorded.
- **File:** `appendix_meetings`.

### 12. Test appendix (phase 7)
- **Changed:** rewritten against the real pytest suite (12 files, 128 test functions, `conftest.py`). Each
  file's coverage is described from its contents. "Pass (CI)" is backed by GitHub Actions CI run #6
  (12 Oct 2026, commit `c3bfcc9`, branch `ci/pipeline-updates`): the unit-test step succeeded on Python 3.10,
  3.11 and 3.12; that commit's `tests/` folder is identical to today's.
- TC-1..TC-3: "Not yet automated" (no Android unit tests). TC-14: "Not yet executed". TC-5: real frame
  counts (574; 1166 registered, 1108 kept; BA 0.97 -> 0.88 px). TC-6/7/11/12 rewritten honestly; TC-15..TC-20
  added for the remaining test files. "All 14 test cases pass" replaced with an accurate summary.
- Also removed: the unverified "three users captured on first attempt" usability claim; NFR-U1 "user
  testing (3 users)".
- **Files:** `appendix_test_cases`, `chapter8_testing`, `appendix_requirements` (traceability).

### 13. Contributions (phase 8)
- **Changed:** "40+ commits" -> 133 (Umair 85, Zaid 26, Tayyab 20 as BlazingBeam, plus 2 bot commits).
  Owned modules are the primary evidence, with the granularity statement. GenAI disclosure expanded to cover
  Claude Code fully (coding, CI changes, documentation, report drafting, and this correction pass).
- **Needs team confirmation:** the owned-modules table follows the commit history of each file, which
  differs from the old report text. Git says Tayyab authored `src/arcore3dgs/` (fallback, SfM, select_sharp,
  structure, ...), `CaptureLogger` and `QualityMonitor`; Umair authored the server, RunPod client,
  `ProcessingActivity`, gallery/detail screens and the web UI prototype; Zaid authored the CI/CD, the whole
  test suite and the APK checker. The old text credited Umair with the SfM pipeline and `CaptureLogger`, and
  Zaid with ARCore-session co-development; git does not show this. If work was done by one member and
  committed by another, adjust `tab:responsibilities` and the paragraphs below it.
- **Files:** `chapter9_development_evidence`, `chapter3_iteration_plan`, `appendix_repository`, `chapter1_introduction`.

### 14. Diagrams in TikZ (phase 11)
- **Changed:** no `verbatim` remains in the report. Nine TikZ figures, each drawn from the code it names:
  use case (`fig:usecase`, chapter 4), architecture (`fig:architecture`), job state machine
  (`fig:jobstate`), data flow (`fig:dataflow`), sequence (`fig:sequence`) in chapter 5; pipeline steps,
  Android architecture, Sim3 alignment and coverage map in the appendix. The repository tree is now a table.
  `\listoffigures` added to `main.tex`. Only core TikZ and the libraries tikz-uml already loads are used
  (no `positioning` or TikZ `calc`): absolute coordinates, plain nodes and arrows. The UML is drawn in
  plain TikZ rather than with tikz-uml macros, because macros could not be test-compiled.
- The required diagrams are in chapter 5 (where the design marks are given), not in `appendix_diagrams.tex`;
  the appendix points to them.

### 15. Missing content (phase 9; tape table in phase 3)
- **Added:** IMU fallback results (`tab:imufallback`, 2/5/9 s gaps; 3.8 vs 30.6 cm; 49.7 -> 8.2 px);
  the full tape-measure table (`tab:tape`); the structural layer description and results; a "Techniques
  explored and parked" section (`tab:parked`: own GPU BA, Metric3D, own stereo matcher, depth supervision,
  floater pruning, median filtering, post-hoc flat-forcing); a five-item "Contributions and Novelty"
  section (`sec:novelty`); the capture device (realme, no LiDAR).

### 16. Risk register (phase 10)
- **Changed:** the existing table (`tab:risks`) is now a 12-entry register with likelihood, impact,
  mitigation and owner: cloud GPU cost and availability, tracking loss, mirrors and glass, large-room GPU
  memory, unmeasured RTX 4090 performance, FYP-2 delivery scope, thin measurement evidence, single device,
  dependencies, ARCore, staffing.

---

## Other corrections found while checking the report against the code

- `prepare.py` was described as gyro-aware. It picks the sharpest frame by Laplacian variance per 8-frame
  window; gyro-aware selection is `select_sharp.py`, used for v4-v6 but **not yet in the one-command
  pipeline** (`server/pipeline.py`). FR-P1 status changed from "Done" to "Partial".
- Sim3 RANSAC uses a 10 cm inlier threshold (not 5 cm), 2,000 four-point samples, a Umeyama refit and a
  30 cm jump filter (`sfm_colmap.py`).
- RunPod SSH readiness: 300 s timeout, polling every 10 s (not 60 s, not exponential backoff).
- `fallback.py` reads the IMU from the MP4's own data tracks, not from `poses.csv`.
- `quality.csv`, `meta.json` and `depth/` are uploaded but not read by the six pipeline steps.
- The app never calls `/download`; the model is fetched by the desktop viewer.
- `JobStatus.UPLOADING` exists but no code path sets it.
- **The RunPod pod watchdog's default hard limit is 60 min (`MAX_POD_LIFETIME`), shorter than the only
  measured end-to-end run (~75 min on an RTX 3070).** Added to risk R6. Check it before the first full
  RunPod run.
- Silent re-anchoring was "solved via anchor logging and IMU fallback"; it was actually solved by
  image-based SfM poses (anchor logging only makes it detectable). Corrected in chapter 2 and defect D-3.
- Removed the uncited "$1.6 trillion annually on rework" statistic from chapter 1.
- "Chapter 9" references for the GenAI disclosure pointed at the wrong chapter number; now `\ref`.

---

## Written as "not yet measured" / "not yet executed": still needs work before submission

GPU or lab runs needed:
1. **End-to-end processing time on an RTX 4090** (NFR-P1; the < 35 min target is a projection).
2. **Cloud GPU cost per scan** (risk R1; the old "$0.30-0.70" was removed).
3. **Second-room held-out PSNR** (only SSIM 0.91 and 1% badly placed surfaces exist).
4. **Second-room tape measurements** (TC-12 is partial).
5. **Large-room behaviour on a 24 GB GPU** (limitations, risk R5).

Tests not executed or not automated:
6. **TC-14 processing timeout**: never exercised.
7. **TC-7 live RunPod run**, including termination on failure: only unit-tested with a faked API.
8. **TC-11 full app -> server -> RunPod -> download path**: not run as a recorded test (local pipeline only).
9. **TC-1..TC-3**: no Android unit tests exist.
10. **Usability testing** (NFR-U1): not done.
11. **Structural-layer wall lengths vs. tape measure**: not done.
12. **The pytest suite on the current `master` head**: CI last ran on `c3bfcc9`; `server/` has changed since.

## Not verified (left as the team wrote them)
- Implementation week numbers in chapters 3 and 6 (no dated evidence checked).
- Market prices in chapters 1-2 (Matterport "$6,000+", LiDAR "$10,000+"), the Copilot/ChatGPT rows of the
  GenAI table, and "Postman / NVIDIA Nsight" in the tools list.
- Acknowledgements wording.

## Check on first local build
The TikZ was written without a compiler. On the first `pdflatex` run, check:
- figures `fig:usecase`, `fig:architecture`, `fig:jobstate`, `fig:dataflow`, `fig:sequence` (full page,
  `[p]`) and the four appendix figures for overlapping labels; adjust coordinates if needed;
- the new long tables (`tab:testcases`, test appendix, `tab:risks`, `tab:parked`) for overfull boxes;
- that `main.aux` / `main.log` churn is not committed.

## Process notes
- `CLOUD_SESSION_PROMPT.md` was not on the remote when the session started; work began once it was pushed.
- The session's default git identity was "Claude <noreply@anthropic.com>". To follow `AGENTS.md`
  ("commits are authored by the student team only"), the repository-local identity was set to
  `UmairisHuman <muhammadumair19925@gmail.com>` (matching existing commits) and no AI trailers were added.
- Nothing in `scripts/`, `server/`, `src/` or `tests/` was modified, and pytest was not run locally.
