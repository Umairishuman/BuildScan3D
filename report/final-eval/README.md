# Final evaluation material (FYP-1 final, due 2026-12-06)

Started 2026-11-28 by Tayyab's agent (FINAL_PLAN.md N4). Not submitted yet; edit freely until submission, then freeze
this folder like `report/mid-eval/`.

| Item | What it is |
|---|---|
| `BuildScan3D_Final_Report/` | LaTeX source of the final report, copied from the mid report (`report/mid-eval/F26_FYP1_Mid_Report_LaTeX_Complete/`, unchanged there). New: `chapters/chapter7_iteration2.tex` (Iteration 2) and `chapters/chapter8b_evaluation.tex` (Evaluation), both drafts with `TODO(name)` markers; front matter says "final report", month December. The other chapters are still the mid report's text and need updating |
| `BuildScan3D_Final_Report/main.pdf` | Built draft (`pdflatex main; bibtex main; pdflatex main` twice) |

Every number in the new chapters comes from the records with its source (R-NNN, D-NNN, P&S). The build prints
`natbib Error: Bibliography not compatible with author-year citations` (the class loads natbib with both `numbers`
and `authoryear`, as in the mid report); the PDF is still written.
