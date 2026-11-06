# Cloud prompts — split the report into 200-word chunks, then apply rewrites

Two prompts. Run **Prompt A** now to produce the chunk files. Fill in the `rewrite:`
blocks yourself over time. Run **Prompt B** later to apply them.

---

# Prompt A — split the report prose into chunks

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

There are roughly 10,100 words of body prose, so expect **about 50 chunks**. If you
produce wildly more or fewer, something is wrong with your chunking — stop and say so.

## What counts as prose

**Include only running body text**: paragraphs, and the text of list items.

**Exclude completely** — do not chunk these, and do not emit placeholders or skip markers
for them either. They simply do not appear in the output:

- all headings (`\chapter`, `\section`, `\subsection`, `\paragraph`)
- every `table`, `longtable`, `figure` and `tikzpicture` environment, **including their
  captions**
- the preamble, `\label`-only lines, and comment lines

Headings are still used as the `section:` label on each chunk, so the reader knows where
they are. They are never chunk content.

## Output

**One single Markdown file: `docs/report/REPORT_CHUNKS.md`.** Do not create a directory
and do not split the output across files.

Structure it as:

1. A short header: total chunk count, total words, the date, and the commit the chunks
   were taken from.
2. A `## <filename>` heading before the first chunk of each source file, so the file is
   navigable — thirteen of these, in the reading order above.
3. All chunks, numbered continuously 001 upwards across the whole report.

## Chunking rules

- Target 200 words, accept 150–250 to land on a natural boundary.
- **Never split mid-sentence, mid-paragraph or mid-list-item.** Prefer a paragraph
  boundary. If a single paragraph exceeds 250 words, split at a sentence boundary.
- Chunks must be **contiguous and non-overlapping** within a file and cover all body prose
  in source order, with no gaps. Skipped tables and headings simply break the run; a chunk
  never spans across one, so start a new chunk after each.
- Start a new chunk at every heading even if the previous one is short.

## Chunk format

Use exactly this, with no extra commentary between chunks:

```
### CHUNK 007
- **file:** chapters/chapter2_research.tex
- **section:** Technical Challenges
- **lines:** 78-91
- **words:** 204

original:

ARCore silently corrects its world frame during SLAM loop closures, causing pose
discontinuities of up to 1 m and 28 degrees. These must be detected and handled to avoid
ghosting in the 3D model.

rewrite:


---
```

## Rules

- **`original:` is plain readable text.** Strip the LaTeX: no backslash commands, no
  braces. Render `\texttt{poses.csv}` as `poses.csv`, `\textbf{x}` as `x`, `\%` as `%`,
  `\&` as `&`, `~` as a space, `---` as an em dash, `$\geq$` as `>=`, `\\` as a line
  break. Replace a `\ref{}` or `\cite{}` with a readable placeholder such as
  `[see Figure 5.2]` or `[citation]`. The point is that it reads as normal English.
- **Do not reword, correct, summarise or improve the text while extracting.** Strip the
  markup and nothing else. The wording must be the report's wording.
- **`lines:` must be the true 1-indexed inclusive span** in the current `.tex` file, and
  must cover exactly the LaTeX that produced the plain text you printed. Verify each span
  by re-reading the file. This span is how the apply pass finds the text again — a wrong
  span makes the chunk unapplicable.
- Number chunks **continuously across the whole report**, starting at 001, in the reading
  order above — not restarting per file.
- Leave every `rewrite:` block empty. You are not rewriting anything in this pass.
- Do not compile. Do not touch `scripts/`, `server/`, `src/` or `tests/`.
- No AI-attribution trailers in commit messages (`AGENTS.md` section 4).

## Finish

Commit `docs/report/REPORT_CHUNKS.md` in one commit. In its header, state the total chunk
count, total words, and confirm explicitly that **no `.tex` file was modified**
(`git status` should show one added file and nothing else).

---
---

# Prompt B — apply the filled-in rewrites

Run this only after you have filled in some `rewrite:` blocks. Paste below the line.

---

Apply the filled-in rewrites in `docs/report/REPORT_CHUNKS.md` to the LaTeX sources in
`F26_FYP1_Mid_Report_LaTeX_Complete/chapters/`.

Read `docs/report/REPORT_FIX_BRIEF.md` first — its Ground Truth table is the authority on
every figure in this report.

## What to apply

- Process **only** chunks whose `rewrite:` block has real content. A block that is empty
  or whitespace is **unchanged — skip it silently.**
- For each one, open the chunk's `file`, read the LaTeX at its `lines` span, and replace
  that span with the rewritten wording.

## Formatting must be preserved exactly

The `rewrite:` text is plain English, because the `original:` shown to the author had its
markup stripped. **Your job is to put the markup back.** The rewritten span must match the
original's formatting conventions in every respect:

- A filename, path, command, endpoint, class or identifier that was `\texttt{}` in the
  original stays `\texttt{}`. Apply the same treatment to any new one the rewrite
  introduces.
- Bold and italic emphasis, `\paragraph{}` lead-ins, `itemize`/`enumerate` structure and
  `\item` boundaries all stay as they were, unless the rewrite clearly restructures the
  passage.
- Every `\label{}` inside the span is preserved. Every `\ref{}` and `\cite{}` is restored
  in place of the readable placeholder it was rendered as — pointing at the **same** label
  or key as before.
- LaTeX escaping is reapplied: `%` becomes `\%`, `&` becomes `\&`, `_` becomes `\_`, `#`
  becomes `\#`, and maths such as `>=` returns to `$\geq$`.
- Units keep their thin spaces (`30\,FPS`, `26.52\,dB`, `0.2\,s`), and em dashes stay
  `---`.
- Indentation and line-wrapping style match the surrounding file.

If the rewrite does not clearly indicate how a piece of markup should be placed, keep what
the original had.

## Critical: apply bottom-up

Apply chunks in **descending line order within each file** (highest line number first).
Editing earlier lines shifts every later line number, so top-down application silently
corrupts spans. Before each replacement, verify the span still renders to the plain text
shown in `original:`; if it does not, **stop and report** rather than guessing.

## Rules that override the pasted text

1. **Never accept an invented measurement.** If a rewrite contains a number that is not in
   the chunk's `original:`, not in `docs/progress/`, and not in the brief's Ground Truth
   table, **keep the original number** and record the refusal. Do not silently adopt it.
2. **Never weaken an honesty marker.** "Not yet measured", "Not yet executed", "Not yet
   automated", "Partial", "projected" and "not yet scheduled" must survive. If a rewrite
   turns one into a pass or a measured result, **do not apply that part** — record it.
3. Keep section headings as they are; they were never part of the chunks.
4. Do not compile. Do not touch `scripts/`, `server/`, `src/` or `tests/`.
5. No AI-attribution trailers in commits.

## Finish

Commit per source file, not per chunk. Then write `docs/report/APPLY_LOG.md`
recording: which chunks were applied, which were skipped as empty, every number or honesty
marker you refused and why, every `\ref`/`\cite` you restored, and any span that no longer
matched.
