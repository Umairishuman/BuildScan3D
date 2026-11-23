# Notice for Tayyab and any agent working for him (2026-11-23)

From Umair (written by an agent for him). Read this before your next run, your next new R- or D- number, or your next
merge of `docs/featureless-tracking-plan` (or any other branch) with `master`. When you have acted on it, tell
Tayyab what changed, add a line to LOG.md, and mark this notice done in MAP.md (archive it, D-049).

## 1. Run / decision numbers clashed again; Umair's side was renumbered (D-091)

Your pushed branch `docs/featureless-tracking-plan` uses R-047 – R-052, R-071 – R-100 and D-080 / D-081. Umair's
sessions had used some of the same numbers on this PC. **Your numbers stay as they are.** Umair's moved:

| Old (Umair, this PC) | New | What |
|---|---|---|
| R-071 | **R-101** | scan #6 full pipeline on the GPU (cuDSS) COLMAP, tag `r071g6` (on `exp/colmap-cudss`) |
| R-072 | **R-102** | stopped scan #3 speed series (on `exp/colmap-cudss`) |
| R-085 / R-086 | **R-103 / R-104** | scan #6 fixture check sheet / wall roughness in the mesh (on `master`) |
| D-080 (pending) | **D-082** | switch to the GPU COLMAP or not (on `exp/colmap-cudss`) |

Next free: **R-105, D-092** (Umair's speed session takes R-105 and up next; check before you take one).
**New rule (D-091):** before taking a number, check every branch, local and remote, not only `origin/master`:

```bash
git fetch origin
for b in $(git branch -a --format='%(refname:short)' | grep -v HEAD); do
  git show $b:docs/progress/TRAINING.md 2>/dev/null | grep -oE '^### R-[0-9]+'; done | sort -u | tail -3
```

(Same for `^## D-[0-9]+` in DECISIONS.md.) Details: DECISIONS.md D-091, TRAINING.md note above the run index.

## 2. Runs are always closed; run times are in `docs/progress/runs.tsv` (D-090)

- CLAUDE.md §6 (Umair): every TRAINING.md entry gets end time, stage times, result and verdict as soon as the run ends
  (failed / stopped / never started too); never leave "(running)", "(pending)", "none so far" or "waiting" on a run that
  is over. Umair asks that your runs follow the same rule.
- `docs/progress/runs.tsv` has one row per run and room, with the times. `python3 scripts/run_times.py update` fills a
  row's times from the run's `timing.json` / `stages.tsv` / `global_mapper.log` when its `folder` column points at the
  run folder; `python3 scripts/run_times.py check` must end with 0 FAIL. Standard library only (not yet run on Windows).
- **Your 36 runs on `docs/featureless-tracking-plan` already have rows**, written from your index's time column (text
  in `note`, `source` = TRAINING). On the RTX 3070 PC you can make them exact: set each row's `folder` to the run's model
  folder (e.g. `dataset/scan_009_057ed3beb4fc/work_v9pfh_sfm/gs_v9pfh`), run `update`, then `check`.
- On `master` these finished runs of yours were closed on 2026-11-23 ("none so far" → "none", result filled in):
  R-039, R-041 – R-044, R-064 (result copied from R-065's text; its end time was never recorded), R-067, R-068, R-070.
  Your branch still has the old open copies: **when you merge `master` into your branch, keep `master`'s version of
  those entries.** Afterwards run (master last, it wins):
  `python3 scripts/run_times.py check --training git:<your branch> --training git:origin/master`

## 3. Known CI failure on `master`

`tests/test_changelog.py::test_repo_changelog_has_unreleased_and_current_version` fails on `master`: the v0.3.9 app
release has no line in `android/CHANGELOG.md`. Umair chose not to fix it alone, because any change under `android/`
makes CD publish a new app release. If your next pull request changes the app anyway, add under `## v0.3.9 · 2026-11-19`:
`- Nothing you will notice: this release only renamed run numbers in a code comment (D-079).` (STATUS §7.7).

## 4. Where Umair's side stands (for context)

- Step 4: `docs/progress/CHECKS_FOR_UMAIR.md` lists the checks only Umair can do; R-059 (scan #6, CPU COLMAP) written
  up; R-101 (scan #6, GPU COLMAP) running on 2026-11-23; the GPU COLMAP switch waits for Umair (D-082).
- `exp/colmap-cudss` (cuDSS / GPU COLMAP work) is not merged yet: Umair holds it.
