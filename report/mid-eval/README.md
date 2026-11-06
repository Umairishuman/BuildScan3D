# FYP-1 mid-evaluation material

Everything submitted for, or written while preparing, the FYP-1 mid evaluation (October 2026).
Moved here from the repository root and `docs/` on 2026-11-06. Nothing in this folder is edited any more;
it is the record of what was submitted.

| Item | What it is |
|---|---|
| `F26_FYP1_Mid_Report_LaTeX_Complete/` | LaTeX source of the mid report (`main.tex`, `chapters/`, `ThesisFigs/`) and its built `main.pdf` |
| `F26_FYP1_Mid_Report_LaTeX_Complete.pdf` | Earlier build of the report, as it was at the repository root |
| `FYP-1-Mid-Assessment-Guidelines-and-Rubrics.pdf` | The department's mid-assessment guidelines and marking rubrics |
| `BuildScan3D_MidEvaluation_Summary.docx` | Short progress summary used for the mid evaluation (the source for many report figures) |
| `report-fix-notes/` | Prompts and logs of the report correction, shortening and rewrite passes (formerly `docs/report/`). `REPORT_FIX_BRIEF.md` holds the team's final report decisions and the ground-truth numbers |

Paths inside these files still name the old locations (`F26_FYP1_Mid_Report_LaTeX_Complete/`, `docs/report/`,
`docs/progress/TODO.md`). They are historical and are not rewritten. `docs/progress/TODO.md` and
`docs/progress/Training_Analysis.md`, which the report cites, are now short pointers to their archived copies.

To rebuild the PDF, run `pdflatex` / `bibtex` inside `F26_FYP1_Mid_Report_LaTeX_Complete/`; the relative paths
inside the LaTeX source did not change.
