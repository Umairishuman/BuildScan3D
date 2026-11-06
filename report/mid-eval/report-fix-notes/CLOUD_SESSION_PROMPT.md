# Cloud session prompt — paste everything below the line

---

You are fixing the FYP-1 mid-evaluation report for BuildScan 3D. The LaTeX sources are
in `F26_FYP1_Mid_Report_LaTeX_Complete/`. Supervisors flagged factual errors,
fabricated evidence and missing artefacts; your job is to correct all of it.

**Read `docs/report/REPORT_FIX_BRIEF.md` first.** It is authoritative. It contains the
team's final decisions and a Ground Truth table of every permitted figure, with
citations into `docs/progress/`. Follow it exactly.

## Absolute rules

1. **Never invent a measurement.** If a number is not in the brief's Ground Truth
   table or in `docs/progress/`, write "not yet measured". Do not interpolate, do not
   estimate, do not carry a number across from a different model or scene.
2. **Never invent process evidence** — no meeting dates, no supervisor approvals, no
   test result marked Pass that was not executed.
3. **Do not compile the document.** TeX Live is not installed and installing it wastes
   the whole session. Edit `.tex` sources only. Do not touch `main.aux`, `main.log`,
   `main.toc`, `main.pdf` or any build artefact.
4. **Do not touch** `scripts/`, `server/`, `src/` or `tests/` — there is unrelated
   uncommitted work there.
5. No AI-attribution trailers in commit messages (`AGENTS.md` section 4).
6. Preserve all existing `\label{}` keys so cross-references keep resolving.

## Work in phases, committing after each

### Phase 1 — Processing time (brief decisions 1, 2)

Measured truth: **~75 min on RTX 3070** (matching 23 + mapping 6 + training 45).
No 3090 run and no 4090 run has ever been performed. The FYP-2 target is
**under 35 min on RTX 4090**, and must be labelled a projection everywhere.

Fix every one of these:
- `chapter8_testing.tex:75` — **delete the entire "Processing time (3090)" table row.**
- `chapter8_testing.tex:86` and `:123` — remove the "under 15 minutes on RTX 3090" claims.
- `chapter10_fyp2_plan.tex:9`, `:27`, `:69` — "<5 min on RTX 4090" becomes "<35 min
  (projected, not yet measured)". Line 9 also wrongly says current time is 12-15 min;
  it is 75 min on the 3070.
- `chapter1_introduction.tex:22` and `:73` — "under 15 minutes" becomes the 35 min target.
- `chapter4_requirements.tex:83` (NFR-P1) and `:108` — restate against the 35 min target
  and name the RTX 4090; the acceptance row must say the measurement is outstanding.
- `appendix_requirements.tex:63` — same NFR-P1 change.
- `appendix_action_register.tex:16` — same.
- `chapter6_iteration1.tex:135` — keep the measured 75 min, change "expected <15 minutes"
  to the projected <35 min.
- `chapter9_development_evidence.tex:173` — "12-15 minutes on an RTX 3090" is false;
  it is ~75 min on the RTX 3070.
- `conclusion.tex:11` — remove "under 15 minutes on an RTX 3090".
- `06_executive_summary.tex:12` — pods are RTX 4090 by default per
  `server/runpod_client.py`; do not imply a measured 3090 result.

### Phase 2 — Reconstruction metrics (brief decisions 4, 5, 6)

The report conflates two different runs. **v6 is 26.52 dB / 0.8886** on a 42-frame
held-out set. **27.81 dB** is splatfacto on a different scene (`roomAttemptSadness2`)
and has no SSIM. They must never appear together as one result.

- `04_abstract.tex:8`, `06_executive_summary.tex:12`, `chapter6_iteration1.tex:133`,
  `appendix_test_cases.tex:32` (TC-13), `conclusion.tex:11` — replace
  "27.8 dB / 0.889" with **26.52 dB / 0.8886 (v6)**. It still clears the >=25 dB bar.
- `chapter8_testing.tex:71-72` — rebuild the results table from the real progression:
  v3 26.04/0.8756, v4_sharp 26.30/0.8849, v5 26.51/0.8879, **v6 26.52/0.8886**.
  **Delete the invented "Room B 26.4 dB / 0.862" column.** The real second-room
  evidence is **SSIM 0.91 and 1% badly-placed surfaces**, measured by Muhammad Tayyab.
  There is no second-room PSNR — do not supply one.
- `chapter2_research.tex:94` and `chapter5_design.tex:76` — the "22.7 to 27.8 dB"
  story is misattributed. 22.67 dB is `gs_colmap_nc`, the team's *own trainer with
  COLMAP depth*, not raw ARCore poses. Reframe using the mid-eval summary's own
  before/after: training 21.9 to ~28 dB, held-out SSIM 0.78 to 0.86 (second room 0.91),
  badly-placed surfaces 7-23% down to 3% (1% second room). Keep the reprojection
  figures (2.32 px to 0.62 px) — those are correct.
- `appendix_meetings.tex:35` — same misattribution in the progress log.
- Correct lens distortion to **k1 ~ 0.09, k2 ~ -0.22** wherever it appears
  (`chapter2_research.tex` currently says 0.08 / -0.2).

### Phase 3 — Accuracy target (brief decision 3)

The committed target as presented was **5%**, not 1%. Measured accuracy is far better:
mean 4.8 mm (0.19%), worst case 0.29%.

- `chapter1_introduction.tex:23` and `:71` — target becomes 5%.
- `chapter4_requirements.tex` acceptance table, `appendix_action_register.tex:16`,
  `conclusion.tex:11` — replace "<1%" with the 5% target, and report the measured
  0.19% mean / 0.29% worst case as exceeding it.

### Phase 4 — X-ray removal (brief decision 10)

The team dropped X-ray themselves. **The panel was never told about it**, so any claim
of panel feedback about it is false and must go. Delete all five occurrences:
- `chapter1_introduction.tex:48` — remove the "Out of scope" bullet entirely.
- `chapter3_iteration_plan.tex:8` — remove the panel-feedback bullet.
- `chapter3_iteration_plan.tex:20` — remove action register row 3 and renumber.
- `chapter3_iteration_plan.tex:88` — remove the deviation entry.
- `chapter5_design.tex:87` — remove from design evolution.
- `appendix_action_register.tex:14` — remove row 3 and renumber.

### Phase 5 — MEP removal, structural layer in (brief decision 7)

Remove **all** YOLOv8-Seg / MEP / pipes / conduits / HVAC content and replace it with
the structural layer, which is real and already built: automatic wall planes, corners,
wall lengths (**6.65-6.68 x 4.45-4.48 m**), **5 doors detected automatically**, and
1:1 metric measurement. This is the basis for automatic floor plans.

Occurrence counts to clear: `chapter10_fyp2_plan.tex` (16 — effectively a rewrite),
`chapter3_iteration_plan.tex` (7), `chapter1_introduction.tex` (6),
`06_executive_summary.tex` (3), `chapter2_research.tex` (3),
`chapter9_development_evidence.tex` (3), `04_abstract.tex` (2),
`07_abbreviations.tex` (2), `chapter8_testing.tex` (1), `conclusion.tex` (1),
`appendix_action_register.tex` (1).

Also update `AGENTS.md` section 3, Stage 4 — it still names YOLOv8-Seg for MEP.
Remove the mIoU >= 0.6 semantic success criterion from `chapter1_introduction.tex`.

### Phase 6 — Honest status (brief decisions 8, 9)

- Iteration 1 is **"core pipeline complete, refinement ongoing"**, never "complete".
  Fix `04_abstract.tex`, `06_executive_summary.tex` (heading included),
  `chapter6_iteration1.tex` "Iteration Outcome", `chapter3_iteration_plan.tex`
  ("All Iteration 1 milestones have been met" and "No recovery plan needed"),
  and `chapter8_testing.tex` "Current Validation Status".
- State the honest open items: 3DGS refinement, **3D mesh creation**, structural layer
  completion, and the web workspace.
- **3D mesh creation is in scope.** Add it as planned work, but do **not** assign it to
  any specific iteration anywhere in the document.

### Phase 7 — Meetings and test evidence (brief decisions 11, 12)

- `appendix_meetings.tex` — the 8-meeting table is fabricated. **There were exactly two
  meetings.** No dates were recorded, so label them "First meeting" and "Second
  meeting" with no dates. Both covered: work completed to date, techniques used, and
  mid-evaluation expectations. **Delete every claim that the supervisor approved
  anything** ("Approved switch to splatfacto", "CI/CD approved", "All acceptance
  criteria met", etc.).
- `appendix_test_cases.tex` and the test table in `chapter8_testing.tex` — rewrite
  against the real pytest suite in `tests/`: `test_fallback`, `test_imu`,
  `test_runpod_client`, `test_server_api`, `test_server_pipeline`,
  `test_common_capture`, `test_common_fallback`, `test_common_project`,
  `test_process_dataset`, `test_relocalize_and_sfm`, `test_apk_checks`,
  `test_sources_compile`. Read these files to describe what is genuinely covered.
  - **There are zero Android/Java unit tests** — TC-1, TC-2, TC-3 must not claim
    "Unit: Pass". Reclassify as manual/device verification or "Not yet automated".
  - **TC-14 was never executed** — mark "Not yet executed".
  - **TC-5 is wrong**: real runs used 574 / 1108 / 1166 frames, not 150.
  - Update the "All 14 test cases pass" claim in `chapter8_testing.tex` to match.

### Phase 8 — Contributions (brief decision 13)

`chapter9_development_evidence.tex`:
- "40+ commits" is wrong — the repository has **133** commits.
- Real split: **Umair 85, Zaid 26, Tayyab 20** (Tayyab commits as "BlazingBeam").
- Document per-member **owned modules** as the primary evidence of contribution, and
  state plainly that commit counts reflect differing commit granularity — Umair commits
  per small change, Tayyab works in large batches — not differing effort. This must
  answer the rubric's "Uneven Team Contribution" red flag honestly.
- Confirm the GenAI disclosure section fully discloses Claude Code usage. The rubric
  sets tool-use marks to **zero** without complete disclosure.

### Phase 9 — Missing content (brief decision 15)

Add from `docs/BuildScan3D_MidEvaluation_Summary.docx` (read it):
- **IMU fallback results** — the team's stated novelty, currently unquantified in the
  report: simulated 9 s gap gives **3.8 cm error vs 30.6 cm** for interpolation;
  re-alignment cuts post-gap frame error from **49.7 px to 8.2 px**.
- **The full tape-measure table**: table short side 0.458/0.459 (-1 mm), long side
  1.748/1.750 (-2 mm), wall 2.792/2.800 (-8 mm), room length 6.692/6.700 (-8 mm);
  mean 4.8 mm (0.19%). Put this in the testing chapter as acceptance evidence.
- **The structural layer** (see Phase 5).
- **Explored and parked techniques** — add to the research/design chapters: the team's
  own GPU bundle adjustment, Metric3D monocular depth, their own stereo matcher, depth
  supervision, floater pruning, median filtering, and post-hoc flat-forcing (rejected:
  it destroyed the glossy floor's reflections and crushed door frames). The supervisors
  want every technique attempted to be visible.
- **The five-item contributions/novelty list** from the summary — add as a dedicated
  section.
- Name the capture device: commodity Android (**realme**), no LiDAR.

### Phase 10 — Risk register (brief decision 16)

`chapter9_development_evidence.tex` already has a risk table around line 151. Extend it
into a proper register with likelihood, impact and mitigation per risk rather than
creating a second table. Cover at minimum: cloud GPU cost and availability, tracking
loss on featureless surfaces, mirrors and glass, large-room GPU memory limits,
unmeasured 4090 performance, and the remaining FYP-2 delivery scope.

### Phase 11 — Diagrams (brief decision 14) — do this LAST

All five diagrams in `appendix_diagrams.tex` are ASCII art inside `verbatim` with
broken box-drawing characters. The rubric's Artefact Gate forces re-submission for
text or generic diagrams, and Form 2 caps design marks at 50% for "diagrams only".

Redraw everything in **TikZ**. `tikz-uml` is already loaded in `main.tex`, so add no new
package that is not already there. No external image files.

Required diagrams:
1. **Use case diagram** — `chapter4_requirements.tex` section 4.2 is currently prose
   only. Actors: End User, Processing Server, Cloud GPU. Use cases: Record Scan, Upload
   Dataset, Monitor Progress, View Model, Take Measurement, Configure Server.
2. **System architecture** — the three tiers (Android client, FastAPI server, GPU
   compute), replacing the ASCII data-flow diagram.
3. **Sequence diagram** — upload to process to download, including the 3 s status
   polling loop and guaranteed pod termination.
4. **Data flow** — capture files (`poses.csv`, `tracking.csv`, `points.csv`,
   `quality.csv`, `depth/`, `meta.json`) through the six pipeline steps to `splat.ply`.
5. **Job state machine** — queued, processing, completed, failed, including the
   timeout-watchdog transition.
Also redraw the pipeline sequence, Android architecture, Sim3 alignment and coverage
map diagrams from `appendix_diagrams.tex` in TikZ.

Every diagram must reflect the real code in `src/arcore3dgs/`, `server/` and the
Android app — read those files rather than drawing from the existing prose.
Architecture reference material: `docs/proposal/BuildScan3D_FYP_Proposal_v4.docx`.

**Keep TikZ conservative** — basic nodes, arrows and positioning only, since you cannot
compile to verify. Prefer simple constructs over clever ones.

## Finishing

When all phases are done, write `docs/report/FIX_LOG.md` recording, per decision:
what you changed, which files, and anything you could not complete and why. Explicitly
list any place you had to write "not yet measured", so the team knows what still needs
a GPU run before submission.
