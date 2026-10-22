# Cloud prompts — split the report into 200-word chunks, then apply rewrites

Two prompts. Run **Prompt A** now to produce the chunk files. Fill in the `rewrite:`
blocks yourself over time. Run **Prompt B** later to apply them.

---

# Prompt A — split the report into chunks

Paste everything in this section below the line.

---

Split the prose of the FYP-1 mid report into ~200-word chunks for review, writing the
result as Markdown files. **This is an extraction task: do not change a single character
of the report itself.** No `.tex` file may be modified by this pass.

## Source

`F26_FYP1_Mid_Report_LaTeX_Complete/chapters/`, in this reading order:

```
04_abstract.tex
06_executive_summary.tex
chapter1_introduction.tex
chapter2_research.tex
chapter3_iteration_plan.tex
chapter4_requirements.tex
chapter5_design.tex
chapter6_iteration1.tex
chapter8_testing.tex
chapter9_development_evidence.tex
chapter10_fyp2_plan.tex
conclusion.tex
appendix_meetings.tex
```

Note `chapter8_testing.tex` renders as Chapter 7 and `chapter9_development_evidence.tex`
as Chapter 8. Label chunks by **filename**, not by rendered chapter number.

There are roughly 11,150 prose words, so expect **about 56 chunks**. If you produce
wildly more or fewer, something is wrong with your chunking — stop and say so.

## Output

One Markdown file per source file, in a new directory `docs/report/rewrite/`, named after
the source: `04_abstract.md`, `chapter1_introduction.md`, and so on. Also write
`docs/report/rewrite/INDEX.md` listing every file with its chunk count and word count.

## Chunking rules

- Chunk **prose only**. Target 200 words, accept 150–250 to land on a natural boundary.
- **Never split mid-sentence, mid-paragraph or mid-list-item.** Prefer a paragraph
  boundary. If a single paragraph exceeds 250 words, split it at a sentence boundary.
- Chunks must be **contiguous and non-overlapping**, and together must cover all prose in
  the file in source order. No gaps.
- **Do not chunk** `tikzpicture` environments, `tabular`/`longtable` bodies, the
  `\begin{document}` preamble, or `\label`-only lines. Where one of these sits between
  two prose chunks, emit a skip marker (format below) so the reader knows content lives
  there. A table's **caption** is prose and belongs in a chunk; its **rows** do not.
- Section headings (`\section{}`, `\subsection{}`) are not prose; use them to label
  chunks, and start a new chunk at every heading even if the previous one is short.

## Chunk format

Use exactly this, with no extra commentary between chunks:

```
### CHUNK 007
- **file:** chapters/chapter2_research.tex
- **section:** Technical Challenges
- **lines:** 78-91
- **words:** 204

original:

> <the raw LaTeX of this span, verbatim, every line prefixed with "> ">

rewrite:

<!-- leave empty to keep the original unchanged -->

---
```

Skip markers look like this and carry no `rewrite:` block:

```
### SKIP — table `tab:comparison` (chapters/chapter2_research.tex lines 24-45)
Comparison of existing 3D scanning solutions. 9 rows, 6 columns.

---
```

## Rules

- **`original:` is the raw LaTeX, copied exactly**, including `\texttt{}`, `\ref{}`,
  `\cite{}`, maths and escapes. Do not clean it up, do not reflow it, do not "fix"
  anything you think is wrong. It is the key the apply pass matches on.
- **`lines:` must be the true 1-indexed inclusive span** in the current file. Verify each
  one by re-reading the file; a wrong span makes the chunk unapplicable.
- Number chunks **continuously across the whole report**, starting at 001, in the reading
  order above — not restarting per file.
- Leave every `rewrite:` block empty. You are not rewriting anything in this pass.
- Do not compile. Do not touch `scripts/`, `server/`, `src/` or `tests/`.
- No AI-attribution trailers in commit messages (`AGENTS.md` section 4).

## Finish

Commit the new `docs/report/rewrite/` directory in one commit. In `INDEX.md`, state the
total chunk count, total words, and confirm explicitly that **no `.tex` file was modified**
(`git status` should show only additions under `docs/report/rewrite/`).

---
---

# Prompt B — apply the filled-in rewrites

Run this only after you have filled in some `rewrite:` blocks. Paste below the line.

---

Apply the filled-in rewrites in `docs/report/rewrite/` to the LaTeX sources in
`F26_FYP1_Mid_Report_LaTeX_Complete/chapters/`.

Read `docs/report/REPORT_FIX_BRIEF.md` first — its Ground Truth table is the authority on
every figure in this report.

## What to apply

- Process **only** chunks whose `rewrite:` block has real content. A block that is empty,
  whitespace, or still holds the HTML comment is **unchanged — skip it silently.**
- For each one, replace the source span given by that chunk's `file` and `lines` with the
  rewritten text, converted to LaTeX in the style of the surrounding document.
- The `rewrite:` text is plain English. Restore markup by reference to the chunk's
  `original:` — if a filename was `\texttt{}` there, it stays `\texttt{}`; if a figure was
  cited with `\ref{}`, keep the same `\ref{}`.

## Critical: apply bottom-up

Apply chunks in **descending line order within each file** (highest line number first).
Editing earlier lines shifts every later line number, so top-down application silently
corrupts spans. Before each replacement, verify the span still begins and ends with the
text shown in `original:`; if it does not, **stop and report** rather than guessing.

## Rules that override the pasted text

1. **Never accept an invented measurement.** If a rewrite contains a number that is not in
   the chunk's `original:`, not in `docs/progress/`, and not in the brief's Ground Truth
   table, **keep the original number** and record the refusal. Do not silently adopt it.
2. **Never weaken an honesty marker.** "Not yet measured", "Not yet executed", "Not yet
   automated", "Partial", "projected" and "not yet scheduled" must survive. If a rewrite
   turns one into a pass or a measured result, **do not apply that part** — record it.
3. **Preserve every `\label{}`** inside the replaced span, and keep all `\ref`s resolving.
4. Keep section headings unless the rewrite clearly supplies a new title.
5. Do not compile. Do not touch `scripts/`, `server/`, `src/` or `tests/`.
6. No AI-attribution trailers in commits.

## Finish

Commit per source file, not per chunk. Then write
`docs/report/rewrite/APPLY_LOG.md` recording: which chunks were applied, which were
skipped as empty, every number or honesty marker you refused and why, any `\ref` you
repointed, and any span that no longer matched.
