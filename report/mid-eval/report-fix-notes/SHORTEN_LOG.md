# Mid-Report Shortening Log

Shortening pass on `F26_FYP1_Mid_Report_LaTeX_Complete/`, following `docs/report/CLOUD_PROMPT_SHORTEN.md`.
Starting point: master at `cb3fa01` (107 pages, `main.pdf`). **The document was not compiled**, so the
"after" page counts are estimates. They come from the old PDF's real per-chapter page counts, scaled by
each chapter's text volume after the pass, with figures counted separately and an allowance for the
smaller table fonts and the fixed float placement. Expect roughly +/-1 page per chapter.

## Result

**Estimated final length: about 86-90 pages (central estimate ~88), down from 107.**
That is **above the 70-75 target**, and this pass stopped there on purpose, as the prompt instructs.
All duplication between chapters and appendices is gone, and the remaining length is content the rubric
scores. Getting below ~85 pages would require cutting protected material: the per-requirement acceptance
checks, the 20 test cases, the evidence paragraphs, the risk register, the parked-techniques table, the nine
figures, or the FYP-2 schedule. See "Decided not to cut" below.

## Per section

| Section | Before (pp.) | After (est.) | What changed |
|---|---|---|---|
| Front matter (title, contents, LoF, LoT, mandated pages) | 17 | ~16 | Contents loses five appendix chapters; LoT loses the duplicate "Test cases" and "Risk register" entries. Mandated pages untouched. |
| Ch1 Introduction | 6 | ~5 | Problem statement no longer restates Ch2's analysis of existing tools; points to Section `sec:gaps`. Out-of-scope, stakeholders and constraints lists became prose. |
| Ch2 Research | 7 | ~6.5 | Parked-techniques table in `\footnotesize`, with a first-page-only caption. No content cut. |
| Ch3 Proposal Feedback and Iteration Plan | 5 | ~5 | **Absorbed Appendix A.** One action register (`tab:actionregister`) with the panel's wording, all five rows (the appendix's fifth row, cloud GPU cost, was missing from the chapter), and `\ref`s replacing stale hard-coded "Table 4.3" / "Section 6.6". Feedback bullets folded into one sentence; Iteration 2 features point to the FYP-2 chapter. |
| Ch4 Software Requirements | 6 | ~6.5 | **Absorbed Appendix B.** Two tables: FRs (`tab:fr`) with priority, dependency, status, a verifiable acceptance check for every FR, and the implementing file and test case (the full traceability matrix); NFRs (`tab:nfr`) with measurement and status. The old acceptance table and "selected" traceability table were folded in; a short acceptance-criteria section (`sec:acceptance`) keeps the project-level thresholds. |
| Ch5 System Design | 9 | ~10.5 | **Gained two Appendix E figures:** Android architecture (after the component list) and pipeline steps with timeouts (after the six-step process). Dependency list became prose. |
| Ch6 Iteration 1 | 8 | ~9 | **Gained two Appendix E figures:** Sim3 alignment and coverage map. Server, pipeline and CI/CD lists now refer to Ch5 (`sec:components`, `sec:process`, `fig:pipelinesteps`) and Ch8 instead of repeating them; the Android feature list became prose. |
| Ch7 Testing (`chapter8_testing.tex`) | 9 | ~11 | **Absorbed Appendix C.** One TC-1..TC-20 table (`tab:testcases`) carrying every column of both versions; per-file coverage table (`tab:testfiles`); the suite description, "Where Pass (CI) comes from" and "Faults found by that re-run" paragraphs moved verbatim. The test-results paragraph lost only the sentences that repeated them. Defects table in `\footnotesize`. |
| Ch8 Project Mgmt and Evidence (`chapter9_development_evidence.tex`) | 10 | ~9 | **Absorbed Appendix D:** repository-structure table (`tab:repo`), CI/CD job list, CD triggers and task tracking. Risk register: owner column dropped, one-line mitigations, `\footnotesize`. Work completed/remaining and tools lists became prose. `[h]` to `[htbp]` should stop the three tables that drifted onto pp. 75-77. |
| Ch9 Remaining FYP Plan | 5 | ~5 | Unchanged apart from a `\label{ch:plan}` and `\small` on the timeline table. |
| Ch10 Conclusion | 2 | ~1 | Rewritten to about one page; every finding, figure and status marker kept. |
| Appendix A Action Register | 3 | 0 | Merged into Ch3 (see above). |
| Appendix B Detailed Requirements | 4 | 0 | Merged into Ch4. |
| Appendix C Detailed Test Cases | 6 | 0 | Merged into Ch7. |
| Appendix D Repository Evidence | 3 | 0 | Merged into Ch8. The per-member "commit categories" list repeated the owned-modules table and was dropped. |
| Appendix E Additional Diagrams | 4 | 0 | All four figures moved into Ch5/Ch6; appendix shell deleted. |
| Appendix F Meetings | 2 | 2 | Kept unchanged (Form 2 criterion 6 evidence). It is now the only appendix. |
| Bibliography | 1 | 1 | Unchanged. |
| **Total** | **107** | **~86-90** | |

## Tables (Priority 2)
- Every `table` float changed from `[h]` to `[htbp]` (14 floats). A plain `[h]` that does not fit is deferred,
  which is what pushed Ch8's tables to its end.
- All captioned longtables now use `\endfirsthead`, so the caption (and its LoT entry) appears once.
- Long tables are set in `\footnotesize` with 3pt padding and widths rebalanced to fit the 15 cm text width;
  nine fixed tables are set in `\small`.

## Content corrections made along the way
These are not cuts. They were found while merging and are recorded so the team can check them:
- **`.env` is tracked in the repository and contains a RunPod API key** (committed 18 Oct 2026, `00bc021`).
  The report claimed it was gitignored. NFR-S2 is now marked "Not met", and the security section and the
  repository table say so. The CI hygiene job fails on a tracked `.env`, so the next CI run on master will
  fail. **Rotate the key and remove the file from version control.** This pass did not touch `.env` or
  `.gitignore`.
- Risk R6 said the pod watchdog default was 60 min; master raised it to 2 h (`1ca1e71`). Updated.
- Defect D-2 used an unsourced "5 dB" and attributed 0.62 px to COLMAP (it is the bundle-adjustment
  figure). Replaced with ground-truth figures (22.67 dB / 0.782; 2.32 px raw; SSIM 0.78 to 0.86).
- Two Appendix D claims were not carried over because they are not true as stated: "all merges go through
  pull requests", and "CI runs on every push" (CI skips direct pushes to master, which CD covers).
- New NFR statuses, from the code: NFR-R1 and NFR-P2 not yet measured, NFR-P3 implemented but not
  profiled, NFR-U2 and NFR-S1 implemented.

## Checks run (no compiler available)
- Static check on every `\input` file: balanced braces, matched `\begin`/`\end`, no duplicate labels, and
  every `\ref` resolves (59 refs, 0 missing). No `verbatim` anywhere. Nine TikZ figures present.
- Regression check against `cb3fa01`: every protected number (v3-v6, 27.81/28.08 split, 22.67/0.782,
  IMU 3.8/30.6 cm and 49.7/8.2 px, all tape rows, 0.19%/0.29%, structural-layer dimensions, 5 doors,
  0.91, frame counts, 75/35 min, commit counts, test-run figures) is still in the text.
- All 20 test-case statuses compared one by one: none changed. TC-11 and TC-12 still say "Partial", now
  with the appendix's detail on which part passed.

## Decided not to cut (would have cost rubric marks)
- **Per-FR acceptance checks and the full traceability** (Form 3 C4 SRS gate requires testable acceptance
  criteria in the chapter). The merged FR table is longer than the old chapter list but replaces three tables.
- **All 20 test cases with expected results, the per-file coverage table, and the "Where Pass (CI)" and
  "Faults found" paragraphs** (Testing and Risk, 15 marks; the honesty of the statuses is the point).
- **The risk register's twelve risks** (criterion 8). Shortened, not reduced.
- **The parked-techniques table, IMU fallback results, tape-measure table, v3-v6 progression, and the
  contributions/novelty section** (the project's actual contributions).
- **All nine TikZ figures** (Architecture and Design, 15 marks; Form 3 C6 artefact gate).
- **The GenAI disclosure table** (tool-use marks are zero without it).
- **The FYP-2 chapter's iteration list, implementation plan and timeline.** They overlap, but each is a
  template section, and the plan is scored under the remaining-plan criterion.
- **Chapter 6's week-by-week implementation and Chapter 3's progress-against-plan.** They cover the same
  weeks but answer different template sections (implementation documentation vs. progress tracking).
- **Edge cases (Ch7), current limitations (Ch8) and the risk register** all mention mirrors and glass. Each
  is a separate rubric item (failure cases, limitations, risks), so all three were kept.
- **All front matter** (template-mandated, checked under criterion 1).

## Check on first local build
- Confirm the page count and update the estimate above.
- Look at the merged longtables (`tab:fr`, `tab:nfr`, `tab:testfiles`, `tab:testcases`, `tab:risks`,
  `tab:repo`, `tab:parked`) for overfull boxes, and at the moved figures for placement.
- Confirm `main.tex` still has no `\tableofcontents` / `\listoffigures` / `\listoftables` (unchanged here).
