# Cloud session prompt — shorten the mid report

Paste everything below the line.

---

Shorten the FYP-1 mid report in `F26_FYP1_Mid_Report_LaTeX_Complete/` from 107 pages
to **70-75 pages**, without losing evidence, numbers or any rubric-required section.

Read `docs/report/REPORT_FIX_BRIEF.md` and `docs/report/FIX_LOG.md` first. Those record
a correction pass that replaced fabricated claims with measured ones. **Everything they
established must survive this pass unchanged.** You are removing duplication and padding,
not content.

## The single most important rule

**Shorter is not automatically better.** The marking rubric
(`FYP-1-Mid-Assessment-Guidelines-and-Rubrics.pdf`) rewards depth, not brevity:
Problem Formulation and R&D is 15 marks, Requirements 15, Architecture 15,
Implementation Documentation 15, Testing and Risk 15. There is **no page limit**.
If a cut would weaken any of those, do not make it. Cutting evidence to hit a page
count is the worst possible outcome of this task.

## Where the pages are

| Section | Pages | Note |
|---|---|---|
| Front matter, title, contents/LoF/LoT | ~17 | mostly fixed by the class |
| Ch1 Introduction | 6 | |
| Ch2 Research | 7 | |
| Ch3 Proposal Feedback and Iteration Plan | 5 | duplicated by Appendix A |
| Ch4 Software Requirements | 6 | duplicated by Appendix B |
| Ch5 System Design | 9 | duplicated by Appendix E |
| Ch6 Iteration 1 | 8 | |
| Ch7 Testing and Early Validation | 9 | duplicated by Appendix C |
| Ch8 Project Management and Development Evidence | 10 | duplicated by Appendix D |
| Ch9 Remaining FYP Plan | 5 | |
| Ch10 Conclusion | 2 | |
| Appendices A-F | 22 | the main target |

## Priority 1 — de-duplicate chapters and appendices (~15 pages, zero content loss)

Five of the six appendices restate a chapter. For each pair, keep **one** authoritative
copy and delete the other, choosing by where the marks are given:

- **Appendix A (Proposal Action Register, 3 pp)** vs the action register table in
  `chapter3_iteration_plan.tex`. These are near-identical. Keep the chapter table
  (Form 2 criterion 1 is scored on the chapter), delete Appendix A, and redirect any
  `\ref` to the chapter table.
- **Appendix B (Detailed Requirements, 4 pp)** vs the FR/NFR lists and traceability
  matrix in `chapter4_requirements.tex`. Merge: the chapter keeps numbered FRs/NFRs
  **with their acceptance checks** (the SRS Gate requires testable acceptance criteria
  in the chapter), and Appendix B goes.
- **Appendix C (Detailed Test Cases, 6 pp)** vs the test table in `chapter8_testing.tex`
  (renders as Chapter 7). This is the biggest single win. Keep **one** table of TC-1..TC-20
  with ID, what it tests, level, and status, in the chapter. Move the "Where Pass (CI)
  comes from" and "Faults found by that re-run" paragraphs into the chapter verbatim --
  they are evidence and must not be lost. Delete Appendix C.
- **Appendix D (Repository and Contribution Evidence, 3 pp)** vs the contribution and
  milestone tables in `chapter9_development_evidence.tex` (renders as Chapter 8).
  Keep the chapter version, including the owned-modules table and the commit-granularity
  explanation. Delete Appendix D.
- **Appendix E (Additional Design Diagrams, 4 pp)**: the four TikZ figures here are
  genuinely additional (pipeline steps, Android architecture, Sim3 alignment, coverage
  map) and are **not** duplicates. Keep them, but move them into Chapters 5 and 6 beside
  the text that discusses them, and delete the appendix shell. Diagrams score under
  Architecture and Design (15 marks) in the chapters, not in an appendix.
- **Appendix F (Meeting and Progress Evidence, 2 pp)**: keep as is. It is short and is
  the process evidence for Form 2 criterion 6.

After this, the only appendix left should be F. That is fine.

## Priority 2 — tighten the long tables (~4-5 pages)

Several `longtable`s spill across pages and repeat their headers. The list of tables
shows "Test cases and their status" three times and "Risk register" three times.

- Use `\small` or `\footnotesize` inside the big tables.
- Rebalance `p{}` column widths so rows stop wrapping to three lines.
- Give continuation pages a `\caption*`-style header so they stop adding duplicate
  entries to the List of Tables.
- The 12-entry risk register in `chapter9_development_evidence.tex` can lose its
  "owner" column (every owner is the same three-person team) and shorten mitigation
  text to one line each.

## Priority 3 — prose tightening (~5 pages)

Only after the above. Cut padding, never facts:

- Remove sentences that restate the previous sentence, and introductory throat-clearing
  ("This chapter describes...", "It is important to note that...").
- Collapse bullet lists where every bullet is one short clause into running prose.
- Chapter 1 and Chapter 2 overlap on the problem statement and the limitations of
  existing tools; say it once.
- Chapter 6 and Chapter 5 both describe the six pipeline steps; keep the detailed version
  in Chapter 5 and have Chapter 6 reference it.
- Chapter 10 (Conclusion) restates the executive summary; keep it to one page.

## Never cut these

- Any measured number, or any "not yet measured" / "not yet executed" marker. The whole
  point of the previous pass was that these are honest. **Do not quietly upgrade a
  "not yet executed" to a pass to save a row.**
- The tape-measure accuracy table, the IMU fallback results (3.8 cm vs 30.6 cm;
  49.7 px to 8.2 px), the v3-to-v6 quality progression, or the techniques-explored-and-parked
  table. These are the project's actual contributions.
- The GenAI tool disclosure. The rubric sets tool-use marks to **zero** without it.
- The risk register (criterion 8 requires documented risks) -- shorten it, do not drop it.
- Any of the nine TikZ figures.
- Front matter: Students' Submission, Anti-Plagiarism, Authors' Declaration, Abstract,
  Acknowledgments, Executive Summary, Abbreviations. All are template-mandated and
  criterion 1 checks for them.
- The contributions/novelty section.

## Mechanics

- **Do not compile.** TeX Live is not installed in the session; the build is done locally.
- Preserve every `\label{}` that is still referenced. When you delete a table or section,
  repoint its `\ref`s rather than leaving them dangling -- a dangling reference prints
  "??" and is an instant formatting deduction.
- `chapter8_testing.tex` renders as Chapter 7 and `chapter9_development_evidence.tex`
  as Chapter 8. This is expected. Do not renumber files.
- Do not touch `scripts/`, `server/`, `src/` or `tests/`.
- Do not commit `main.aux`, `main.log`, `main.toc`, `main.lof` or `main.lot` -- they are
  gitignored now. `main.pdf` is tracked but you cannot rebuild it; leave it alone.
- Do not re-add `\tableofcontents`, `\listoffigures` or `\listoftables` to `main.tex`.
  The document class already emits all three; duplicating them printed three empty
  headings. There is a comment in `main.tex` explaining this.
- No AI-attribution trailers in commit messages (`AGENTS.md` section 4).

## Commit and report

Commit in stages: one commit per appendix merged, one for the table tightening, one for
the prose pass. Then write `docs/report/SHORTEN_LOG.md` recording, per section: the
before and after page estimate, what was merged or cut, where moved content now lives,
and anything you decided **not** to cut because it would have cost rubric marks.

Give an estimated final page count. If you cannot reach 70-75 pages without cutting
protected content, **stop at whatever length preserves the content** and say so in the
log. Overshooting the page target is the correct failure mode here.
