# BuildScan 3D: plan to the final submission (2026-12-06)

2026-11-28 · written by Tayyab's agent at Tayyab's request ("plan out what needs to be done and start working"; Umair
and Zaid are away until Monday 2026-11-30). It follows [COMPLETION_PLAN.md](COMPLETION_PLAN.md) (Umair, 2026-11-12;
its rows keep their numbers here) and lists only what is still open, who can do it, and when. **Nothing here is a
decision**: the choices at the end are Tayyab's (or the team's), recorded in DECISIONS.md once made.

**Finished product (Tayyab, 2026-11-26):** "the user inputs video -> gets web viewer output with splat and semantics
and mesh". Today that works from the command line on this PC (`run_full.sh <dataset> <tag> -- --auto`, D-099; R-134
textured room end to end with no hand choice). Missing: the server / phone path running it (2.3, 2.5), the newest
code on `master`, the evaluation numbers, the report, the demo.

## 1. Where each part stands (2026-11-28)

| Part | State | Open |
|---|---|---|
| Capture app | Works (v0.3.6), all recordings made with it | NFR1 not met (28.9 fps, R-031), NFR2 not measured on a phone (E9) |
| Upload + server | FastAPI server works, runs the **v3** recipe; v9 option built (`BUILDSCAN_PIPELINE=v9`) | Server runs `run_full.sh -- --auto` (2.3); phone → model run (2.5, exit gate a). Umair's area |
| Automatic pipeline | `--auto` on `feature/auto-pipeline` (unpushed): bedroom OK (R-134, 104 min); tape room 25.35 vs hand-set 25.51 dB, tape -1.86 % (R-136, 106 min); scan_009 with ALIKED 25.68, above every hand-made model (R-145, 91.5 min) | Merge to `master`; OD-16 / OD-17; scan_009 room height |
| Featureless (novelty) | Best model now automatic: R-145 (ALIKED, 25.68 vs hand-made 24.46 on 61 frames); DA3-BASE priors (Apache) | Room height (no floor reconstructed) |
| Semantics | v10, scored only on the room it was tuned on (15 / 17) | E3 on other rooms needs Umair's fixture sheets (#21) |
| Mesh, layout, plan | Working; layout fails on scan_009 (7.28 m) | Floater-robust floor / ceiling |
| Web viewer | Lag fixed on `fix/viewer-perf` (unpushed); loads 2.2 - 7.6 s, worst frame 15 ms (R-143, desktop) | Merge; local bundles and a phone not measured |
| Compression | `.spz` 92.3 - 92.8 % smaller at 35.8 - 36.5 dB vs the `.ply` render (R-139); Zaid's `.ksplat` branch unmerged | OD-1 with `.ksplat` numbers |
| Records / repo | Up to date on `feature/auto-pipeline` | 3 branches to push and merge (section 3) |
| Report, UAT, poster, demo | **Not started** (only the mid report) | R1 – R7 |

## 2. Work, by who and when

### Tonight (agent, 2026-11-28 night, GPU one job at a time)

| # | Work | Feeds | Done when |
|---|---|---|---|
| N1 | **R-136**: `--auto` on newRoomAttemptSadness with the v9_e2e split (mapped to its frames), eval vs v9_e2e, tape check | E2, E4, report "automatic vs hand-set" | Entry closed with PSNR, tape error, fixtures, stage times |
| N2 | Layout: floor / ceiling that cannot be right (camera path far above the floor, height > 4.5 m) fall back to a camera-height check; tested on R-135 (fails today) and R-134 / R-136 (must not change) | 4.1, product robustness | Change on `feature/auto-pipeline`, numbers before / after in TRAINING |
| N3 | Evaluation tables from what exists: E4 stage times per room (R-134 / R-135 / R-136), E5 viewer load time + frame times on this PC (desktop, not a phone), E6 `.spz` vs `.ply` render quality | E4, E5 (part), E6 | Numbers with their source in `report/final-eval/` |
| N4 | Final report: outline + method + results chapters drafted from the records (every number with its run / decision) | R3 | Draft in `report/final-eval/` for the team to edit |
| N5 | Records: STATUS, LOG, MAP for everything above | I4 | Committed |

### Saturday / Sunday (Tayyab)

| # | Work |
|---|---|
| T1 | Push `fix/viewer-perf`, `exp/featureless-holes`, `feature/auto-pipeline`; PRs into `master` (viewer first: it is small) |
| T2 | Look at R-134 / R-135 / R-136 in the viewer; answer the decisions in section 4 |
| T3 | Read the report draft (N4); own the reconstruction + featureless chapters (Workflow B) |
| T4 | If time: record one more room with the capture protocol (STATUS 7.8) and run `--auto` on it (a third test room for E2 / E3) |

### Monday 2026-11-30 onwards (Umair, Zaid back)

| # | Who | Work |
|---|---|---|
| M1 | Umair | Server runs `run_full.sh … -- --auto` (2.3); one phone → web-bundle run (2.5, exit gate a) |
| M2 | Umair | Tape sheets (#20) and fixture sheets (#21) → E2 / E3 on ≥ 2 rooms |
| M3 | Umair | UAT walkthrough (R1, R2) |
| M4 | Zaid | OD-1 `.spz` / `.ksplat` with the E6 numbers; E5 on a mid-range Android phone |
| M5 | all | Report chapters, poster (R4), demo video (R5), slides + live-demo fallback (R6) |
| M6 | all | Freeze by 2026-12-05: tag `master`, APK release, records (R7) |

## 3. Branches to merge (agents do not push or merge)

| Branch | On origin? | Ahead of `master` | Holds |
|---|---|---|---|
| `fix/viewer-perf` | no | 3 commits | viewer lag fix (SplatCanvas), web-ui STATUS |
| `exp/featureless-holes` | 8 commits behind local | 26 commits | DA3 priors (R-131 – R-133), D-098, scan_009 viewer entries |
| `feature/auto-pipeline` | no | 42 commits (includes `exp/featureless-holes`) | `--auto`, `sensor_path.py`, `run_full.sh` stages, R-134 – R-136, `run_times.py` fix |

## 4. Choices for Tayyab (recommendations, not decisions)

| Choice | Options | Recommendation |
|---|---|---|
| Make `--auto` the default recipe for new rooms (product path, server) | Yes after R-136; or keep the hand recipe | Yes if R-136 is within run-to-run noise of v9_e2e on PSNR and tape |
| scan_009 in the final demo | R-133 (hand chain, best) as the featureless showcase; or R-135 (automatic) | R-133 for the demo, R-135 reported honestly as the automatic result |
| OD-10 photometric init (19 → 7.5 min, R-063) | Adopt in `--auto`; or not | Adopt: same quality measured, saves ~12 min per room |
| Time on featureless vs finishing | Keep improving `sensor_path.py`; or freeze featureless and finish product + report | Freeze after one diagnosis pass (why R-135 < hand chain), then report |
| Report format | LaTeX like the mid report (`report/mid-eval/F26_FYP1_Mid_Report_LaTeX_Complete`); or Word | LaTeX, same template |
