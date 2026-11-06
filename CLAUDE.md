# CLAUDE.md

Instructions for everyone working on BuildScan 3D: the three of us and any AI agent working for us.

**Start every session by reading [MAP.md](MAP.md)** (what is where, what every file does, which files are current),
then this file, then [docs/progress/STATUS.md](docs/progress/STATUS.md).

- [AGENTS.md](AGENTS.md): brand assets, UI theme, the five-stage FYP architecture, commit conventions. Read it.
- This file: **how we work**: the project records, when and how to write to them, the git workflow, and each member's
  personal preferences (section 6).

Key rule, repeated because it is easy to get wrong:

- **No AI attribution in commits.** Never add `Co-Authored-By: Claude ...`, `Generated with Claude Code`, or any
  similar trailer to a commit message or PR description in this repository.

---

## 1. The project records

All in `docs/progress/`. They are the project's memory: if it is not written there, the next person does not know it.

| File | Purpose | Who writes, when |
|---|---|---|
| [MAP.md](MAP.md) (repo root) | **What is where and what every file does**, with status markers (current v9 / eval / v3 / legacy / experiment / dead) | In the same commit that adds, moves, retires or repurposes a file |
| [STATUS.md](docs/progress/STATUS.md) | **Everything done and everything left.** Best model, module status, proposal requirements, machines, open work (§7), done (§8), known limits | Anyone, at the end of every session that changed something |
| [DECISIONS.md](docs/progress/DECISIONS.md) | **Every decision**: what, why, evidence, rejected alternatives, who decided, status. Open decisions (OD-x) at the end | Whenever a decision is made or an option is rejected |
| [LOG.md](docs/progress/LOG.md) | **Dated project log**: what each person did on each day, which runs and decisions it produced | Every working session, one block per day and person |
| [TRAINING.md](docs/progress/TRAINING.md) | **Every processing / training run and every error that happened during it** | During the run, as things happen |
| [Problems_and_Solutions.md](docs/progress/Problems_and_Solutions.md) | Deep technical evidence: symptom → root cause → how it was confirmed → fix → numbers | When an investigation finds a root cause |
| `docs/progress/archive/` | Files no longer maintained, kept unchanged | Only when retiring a file (section 3) |

Other status files: [prototype/web-ui/STATUS.md](prototype/web-ui/STATUS.md) (web UI build state),
[docs/CI_CD.md](docs/CI_CD.md), [docs/PROCESSING_GUIDE.md](docs/PROCESSING_GUIDE.md).

## 2. Logging rules

**Start of a session.** Read `MAP.md`, then `STATUS.md` (at least §1, §6 and the §7 part you will work on) and the
last few `LOG.md` blocks. Check `DECISIONS.md` before changing anything a decision covers; don't re-open an Active decision without new
evidence, and say so if you do.

**TRAINING.md: its purpose is the run log.** For every run of the pipeline or any stage of it (SfM, priors, training,
semantics, mesh, export, server / RunPod jobs, Kaggle), on any machine:

1. Before starting, add an entry from the template at the top of TRAINING.md: run ID `R-NNN` (next free number),
   who, machine, branch + commit, dataset, exact command, goal.
2. **Every error during the run goes in immediately:** time, stage, the exact error message or symptom, the cause once
   known, the fix or workaround, and whether it was resolved. OOMs, crashes, hangs, wrong outputs, environment and
   install problems, power cuts: all of them. A run that failed or was abandoned still gets its entry.
3. At the end: output folder, stage times, metrics, verdict (kept / rejected / inconclusive), and a row in the run index.
4. If the run led to a decision, write it in DECISIONS.md and link the run ID.

**DECISIONS.md.** Add an entry (`D-NNN`, next free number) for every decision: choosing a recipe, rejecting an option,
changing scope, choosing a tool, a folder or file convention. Fields: date, decision, why, evidence, rejected
alternatives, who decided, source. Never delete or rewrite an old decision: set its status to `Superseded by D-xxx`.
**Agents do not make project decisions.** When a choice is the team's (scope, recipe, what to delete, what to merge),
present the options with a recommendation, let the person decide, then record it with their name under "By". Unsettled
questions go in the Open decisions table.

**LOG.md.** One block per day and person (template at the top of LOG.md): what was done (with files), runs (`R-NNN`),
decisions (`D-NNN`), problems, and what the next session should pick up. Newest at the end.

**STATUS.md.** At the end of a session: tick finished items in §7 and move them into §8 (with the date), add every new
to-do in the right §7 group, and update §2–§6 if numbers, modules or machines changed. **Nothing is too small to record,
and nothing is removed because it looks unimportant**: an item that no longer applies is marked obsolete with the reason,
not deleted. Update the "Last updated" line.

**For everything:**

- Absolute dates (`YYYY-MM-DD`), never "today" or "last week". Names, not "I".
- **Never invent a number.** Only measured values, with their source (run ID, script output, P&S section). If something
  was not measured, write "not measured".
- Say what is verified and what is not ("not tested on a device", "one room only", "tuned on the same data").
- Link instead of copying: point to the run, decision or P&S section that holds the details.

## 3. Files and folders

- Records in `docs/progress/` (section 1). Proposals in `docs/proposal/`, papers in `docs/Research Papers/`.
- Evaluation material per milestone in `report/<milestone>/` (e.g. `report/mid-eval/`, later `report/final-eval/`).
  Once a milestone is submitted its folder is not edited.
- **Never delete a file: archive it** (D-049). Retiring a file means `git mv` into an archive folder
  (`docs/progress/archive/` for docs; a `legacy/` or `archive/` folder next to the code for code), a row in that
  folder's `README.md` (why, what replaces it), a one-line pointer at the old path if a report or document cites it,
  and the MAP.md entry updated. Ask the file's owner first.
- Datasets (`dataset/`), models (`saved_models/`, named `YYYY-MM-DD_<tag>/` with a `README.txt`), environments and
  `tools/` are gitignored and live on the machine that made them; STATUS §6 says which machine has what.
- Never commit `.env`, keys, datasets, `.ply` / `.mp4` / checkpoints (CI rejects them, see docs/CI_CD.md).

## 4. Git workflow (everyone)

- `master` is stable; nobody works on it directly. Work on short-lived branches: `feature/...`, `fix/...`, `exp/...`
  (experiments), `docs/...`, `ci/...`. Merge into `master` through a pull request with `CI passed` green.
- Commit messages: `type(scope): summary` (`feat`, `fix`, `docs`, `chore`, `test`, `ci`, `build`, `refactor`), e.g.
  `feat(semantics): ...`. A body explains why when it is not obvious. No AI attribution (top of this file).
- Pull before starting; don't rewrite history that others have pulled (no force-push to shared branches).
- Before a merge, update STATUS.md and LOG.md on the branch so `master` carries its own record.
- Agents: never push, merge, rebase, delete branches or touch `master` unless the member's section below allows it or
  the member asks in that session.

## 5. Machines

The pipeline has to work the same on the RTX 3070 PC, this Ubuntu PC (RTX 4000 Ada), a friend's PC and RunPod.
Current state of each, the Docker image and the known portability problems: STATUS.md §6. Record every set-up problem
in TRAINING.md (as part of the first run on that machine) and update §6.

## 6. Team members

Each member's preferences apply when that member is the one working (or the one the agent is working for). If it is
not clear who that is, ask at the start of the session. Members edit their own section; the rest of this file is shared
and changes need agreement.

### Muhammad Umair (23i-0662) · GitHub `UmairisHuman`
- **Proposal ownership:** mobile edge capture and validation (Workflow A). **Work so far:** web prototype, processing
  server, RunPod integration, CD / APK releases, GPU Docker image workflow, mid report, project organisation.
- **Current focus:** setting up this Ubuntu PC, then rebuilding the Docker image from the same setup script (STATUS §7.1),
  then semantic labelling; processing-time optimisation is a priority to-do.
- **Files:** never delete anything, archive it ("deleting never ends well").
- **Commits:** likes to commit often, in small logical steps, so he can revert to any point. Agents working for Umair
  commit automatically after each logical step **on a feature branch**, without asking each time; they never push,
  merge, rebase or touch `master` without asking.
- **Branches:** wants to use (and try out) the feature-branch flow: a new branch per piece of work, tested before it is
  merged.
- **Decisions:** do not decide for him. Bring every choice to him with options and a recommendation; record his answer in DECISIONS.md.
- **His machine:** this Ubuntu PC (`gpu-lab-Precision-3680`, RTX 4000 Ada). Git identity configured (2026-11-06); GitHub
  over SSH. Do not install Docker on this PC for now (2026-11-06).

### Muhammad Tayyab (23i-0636) · GitHub `BlazingBeam`
- **Proposal ownership:** cloud orchestration and 3DGS reconstruction engine (Workflow B). **Work so far:** capture app
  (ARCore logging, IQA, coverage), reconstruction pipeline v1 → v9, semantics v9 / v10, mesh, web scan viewer.
  Runs on the RTX 3070 PC. (`BlazingBeam` = Tayyab, confirmed by Umair 2026-11-06.)
- **Preferences:** *to be filled in by Tayyab* (commit style, branches, how agents should work for him). Noted in the
  report fix brief: works in large batches rather than many small commits.

### Zaid Fareed (23i-0829) · GitHub `Zaid Fareed`
- **Proposal ownership:** semantic AI, compression and web delivery (Workflows B and C). **Work so far:** unit tests,
  CI/CD, APK checks and signing, ARKitScenes trainer experiments on Kaggle (`exp/trainer-arkitscenes`), `.ksplat`
  compression (`feat/splat-compress`).
- **Preferences:** *to be filled in by Zaid*.
