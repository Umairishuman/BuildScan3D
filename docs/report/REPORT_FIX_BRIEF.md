# Mid-Report Fix Brief — authoritative decisions

Scope: `F26_FYP1_Mid_Report_LaTeX_Complete/`. Every decision below is FINAL and was
made by the team. Do not re-litigate them, do not "improve" on them, and do not
invent any number that is not in the Ground Truth table.

## Hard rules

1. **Never invent a measurement.** If a number is not in Ground Truth below or in
   `docs/progress/`, it does not go in the report. Write "not yet measured".
2. **No fabricated process evidence.** No invented meeting dates, no claimed
   supervisor approvals, no test marked Pass that was not executed.
3. No AI-attribution trailers in commits (see `AGENTS.md` section 4).

## Ground truth (the ONLY permitted figures)

| Claim | Correct value | Source |
|---|---|---|
| Current best model | **v6 = 26.52 dB PSNR / 0.8886 SSIM**, 42 held-out frames | `Problems_and_Solutions.md:387`, `TODO.md:9` |
| v3 / v4_sharp / v5 | 26.04/0.8756, 26.30/0.8849, 26.51/0.8879 | same |
| Splatfacto vs custom trainer (DIFFERENT scene, `roomAttemptSadness2`) | held-out 27.81 dB, train 28.08 dB | `Training_Analysis.md:82-83` |
| Before/after pose fix | train 21.9 to ~28 dB; held-out SSIM 0.78 to 0.86 | MidEvaluation_Summary section 6 |
| Second room | **SSIM 0.91, badly-placed surfaces 1%** | MidEvaluation_Summary section 6 |
| Best previous custom trainer (`gs_colmap_nc`) | 22.67 dB / 0.782 | `Problems_and_Solutions.md:325` |
| Processing time, measured | **~75 min on RTX 3070** (matching 23, mapping 6, training 45) | `TODO.md:53` |
| Lens distortion | k1 approx 0.09, k2 approx -0.22 | MidEvaluation_Summary section 5 |
| Reprojection error | 2.32 px median (ARCore) to 0.62 px (BA, 626k obs) | `Problems_and_Solutions.md:74,245` |
| Bundle adjustment | global BA 0.97 to 0.88 px | `TODO.md:17` |
| IMU fallback, 9 s gap | **3.8 cm error vs 30.6 cm for interpolation** | MidEvaluation_Summary section 3 |
| IMU fallback, re-alignment | **49.7 px to 8.2 px** on post-gap frames | same |
| Tape measure | table 0.458/0.459 (-1 mm), long 1.748/1.750 (-2 mm), wall 2.792/2.800 (-8 mm), room 6.692/6.700 (-8 mm); **mean 4.8 mm = 0.19%**, worst 0.29% | MidEvaluation_Summary section 7 |
| Structural layer | wall planes 6.65-6.68 x 4.45-4.48 m, **5 doors auto-detected** | MidEvaluation_Summary section 9 |
| Frame counts | v3 574 frames; gyro selection 1166 to **1108 kept**; 7,177 total video frames | `TODO.md:17` |
| Dense MVS init | 1.15M fused to ~460k points at 1 cm; +0.21 dB / +0.003 SSIM | `TODO.md:13` |
| Gyro frame selection gain | +0.26 dB / +0.009 SSIM | `TODO.md:17` |
| Commits | Umair 85, Zaid 26, Tayyab ("BlazingBeam") 20 — total 133 | `git shortlog -sne --all` |
| Device | commodity Android (realme), no LiDAR | MidEvaluation_Summary section 1 |

## Decisions

1. **Processing time.** Measured: 75 min on RTX 3070. FYP-2 target: **under 35 min on
   RTX 4090**, explicitly labelled a projection, not a measurement. Replace every
   "<5 min" and "<15 min" claim. Update NFR-P1 and the success criteria to 35 min.
2. **Delete** the "Processing time (3090) 12-14 min" row from the results table in
   `chapter8_testing.tex`. Remove the 3090 timing claim everywhere it appears.
3. **Accuracy target = 5%** (what was actually presented). Report measured 0.29%
   worst case / 0.19% mean as substantially exceeding it. Replace all "<1%" targets.
4. **Headline v6: 26.52 dB / 0.8886.** It still clears the >=25 dB acceptance bar.
5. **27.81 dB is a separate result** on a different scene — present it only as the
   splatfacto-vs-custom-trainer comparison, never as v6's score, never alongside 0.889.
6. **Second room = SSIM 0.91, 1% badly-placed surfaces**, measured by Muhammad Tayyab.
   Delete the invented "Room B 26.4 dB / 0.862". Do not invent a second-room PSNR.
7. **Remove all MEP semantic segmentation** (YOLOv8-Seg, pipes/conduits/HVAC) from
   the entire report, including scope, modules, success criteria and FYP-2 plan.
   Replace with the **structural layer**: wall planes, corners, wall lengths, door
   detection, floor plans, and 1:1 measurement. Also update `AGENTS.md` section 3 Stage 4.
8. **Iteration 1 = "core pipeline complete, refinement ongoing."** Not "complete".
   List honest open items: 3DGS refinement, mesh creation, structural layer
   completion, web workspace. Keep the FYP-1/FYP-2 split.
9. **3D mesh creation is in scope.** Mention it as planned work but do NOT assign it
   to a specific iteration anywhere.
10. **X-ray: delete every mention** (pp. 3, 11, 12, 14, 22, 52 of the old build),
    including the "Out of scope" line. The team dropped it themselves; the panel was
    never told. Remove the panel-feedback framing in `chapter3_iteration_plan.tex`
    action register row 3 and in `chapter5_design.tex` design evolution.
11. **Supervisor meetings: exactly two.** No dates were recorded, so write them
    without fabricated dates ("First meeting" / "Second meeting"). Agenda for both:
    showing work completed to date, the techniques used, and clarifying mid-evaluation
    expectations. **Remove every claim that the supervisor approved anything.**
12. **Rewrite the test appendix against the real pytest suite** in `tests/` (14 files:
    `test_fallback`, `test_imu`, `test_runpod_client`, `test_server_api`,
    `test_server_pipeline`, `test_common_capture`, `test_common_fallback`,
    `test_common_project`, `test_process_dataset`, `test_relocalize_and_sfm`,
    `test_apk_checks`, `test_sources_compile`, plus `conftest.py`).
    **There are ZERO Android/Java unit tests** — TC-1..TC-3 must not claim "Unit: Pass".
    TC-14 was never executed. Fix TC-5: real runs used 574/1108/1166 frames, not 150.
    Mark anything unexecuted as "Not yet executed", not "Pass".
13. **Contributions.** Document per-member owned modules as the evidence, and state
    plainly that commit counts (85/26/20) reflect differing commit granularity —
    Umair commits per small change, Tayyab works in large batches — not differing
    effort. Correct "40+ commits" to 133.
14. **Redraw every diagram in TikZ** (`tikz-uml` is already loaded in `main.tex`).
    No ASCII art in `verbatim`, no external images. Required: use case diagram
    (currently prose only in section 4.2), system architecture, sequence diagram for
    upload-process-download, data flow, and a Job state machine. Replace all five
    ASCII diagrams in `appendix_diagrams.tex`. Architecture reference material is in
    `docs/proposal/BuildScan3D_FYP_Proposal_v4.docx`.
15. **Add all missing content** from `docs/BuildScan3D_MidEvaluation_Summary.docx`:
    IMU fallback numbers (the team's stated novelty), the full tape-measure table,
    the structural layer, the "explored and parked" techniques (own GPU bundle
    adjustment, Metric3D monocular depth, own stereo matcher, depth supervision,
    floater pruning, median filtering, post-hoc flat-forcing — rejected because it
    destroyed glossy-floor reflections and crushed door frames), and the five-item
    contributions/novelty list.
16. **Add a risk register** (rubric Form 3 criterion 8 requires documented risks).

## Rubric gates to satisfy — `FYP-1-Mid-Assessment-Guidelines-and-Rubrics.pdf`

- **Form 3 C6 Artefact Gate**: generic or text diagrams force re-submission, see decision 14.
- **Form 2 C5**: "If Diagrams Only: cap design marks at 50%" — tie every diagram to real code.
- **Form 3 C4 SRS Gate**: FRs/NFRs must be numbered with *verifiable* acceptance checks.
- **Form 3 C8 Tool Disclosure Gate**: tool-use score = 0 without full GenAI disclosure.
  Verify `chapter9_development_evidence.tex` discloses Claude Code use completely.
- **Red flags**: "Dishonest Milestone Logging", "Uneven Team Contribution" (Form 11),
  "Ignored Proposal Panel Actions" (Form 10), "Generic/GenAI R&D Text".

## Note on file naming

`chapter8_testing.tex` renders as **Chapter 7** (there is no chapter 7 file); its
results table is "Table 7.3". This is expected, not a bug. Do not renumber.

## Build

TeX Live is likely unavailable in a cloud session. Edit the `.tex` sources; the PDF
is rebuilt locally. Do not commit regenerated `main.aux` / `main.log` churn.
