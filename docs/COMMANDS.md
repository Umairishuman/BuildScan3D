# BuildScan commands: cheat sheet

Every command for the Linux PC, with what to type for each argument. Run them from the repository folder:

```bash
cd ~/Desktop/BuildScan3D
```

**You can leave arguments out.** Then `scripts/buildscan` asks: it shows a numbered list of your recordings, runs or
running sessions, and you type the number. A new run suggests a name you can accept with Enter.

The longer guide (what each stage does, where the outputs are, problems met): [RUN_PIPELINE.md](RUN_PIPELINE.md).

## The arguments

| Argument | What it is | Where to find it | Example |
|---|---|---|---|
| `<scan>` | a recording: its **number** (recordings are numbered 1, 2, 3 in the order they arrived), `latest`, or its folder in `dataset/` | `scripts/buildscan datasets` (newest first, with the numbers); the app shows the number after an upload | `4`, `latest`, `scan_004_6de634cbb8b2` |
| `<tag>` | the **name of one run** of a recording; names its output folders `work_<tag>_sfm/gs_<tag>/`. Any short name: letters, digits, `_`, `-` | for an existing run: `scripts/buildscan datasets` lists each recording's runs | `umair`, `r1106`, `test2` |
| `<session>` | a background program started by buildscan | `scripts/buildscan status` | `bs-server`, `run-umair`, `viewer`, `web` |
| `<stage>` | where to restart a run (see the list below) | `run_full.log` shows which stage failed | `sem2d` |

Pick a **new** tag for every new run (the old run stays untouched). Reuse a tag only with `--from` to continue it.

## Everyday commands

| I want to ... | Type | Notes |
|---|---|---|
| see what is running, the phone URL, GPU, newest recordings | `scripts/buildscan status` | start here |
| start the upload server for the phone | `scripts/buildscan server start` | the phone URL is in `status`; phone on the same network |
| watch uploads arrive | `scripts/buildscan server log` | leave with **Ctrl+A then D** |
| upload over the USB cable (fastest) | start the server, plug the phone in (USB debugging on, tap Allow) | the server links it by itself; `status` shows the phone; one-time setup: [PROCESSING_GUIDE.md](PROCESSING_GUIDE.md#upload-over-a-usb-cable-fastest-no-wi-fi-needed) |
| stop the upload server | `scripts/buildscan server stop` | |
| list my recordings and their runs | `scripts/buildscan datasets` | |
| check a recording before processing | `scripts/buildscan check latest` | must end with `READY TO PROCESS` |
| process a recording (everything, best recipe) | `scripts/buildscan run latest mytag` | or just `scripts/buildscan run` and answer the questions |
| follow a run's progress | `scripts/buildscan watch latest mytag` | **Ctrl+C** stops watching only, not the run |
| see the full run screen | `scripts/buildscan attach run-mytag` | leave with **Ctrl+A then D** (Ctrl+C would stop the run) |
| see where the results are + stage times | `scripts/buildscan results latest mytag` | |
| look at the 3D model | `scripts/buildscan view latest mytag` | then open http://localhost:7010 |
| open the web dashboard | `scripts/buildscan web` | http://localhost:3000; a scan shows only with an entry in `prototype/web-ui/src/lib/mockData.ts` |
| stop something | `scripts/buildscan stop run-mytag` | or `stop viewer`, `stop web`, `stop bs-server`; or just `stop` to choose |
| GPU use / temperature live | `scripts/buildscan gpu` | Ctrl+C to leave |
| this PC's addresses | `scripts/buildscan ip` | |
| all commands | `scripts/buildscan help` | |

## Less common

**Continue a run that stopped** (crash, power cut, you stopped it). Find the failed stage at the end of `run_full.log`
(`scripts/buildscan watch latest mytag`), then:

```bash
scripts/buildscan run latest mytag --from sem2d
```

Stages, in order: `select sfm export prior init train ply layout sem2d sem3d verify sem3d2 mesh meshlabels web`.

**A different recipe** (anything after `--` replaces the default recipe and goes to `run_v8.py`):

```bash
scripts/buildscan run latest quicktest -- --init fmvs                 # plain v9, no planar / blur / PGSR: faster check
scripts/buildscan run latest myrun -- --sfm_args "--retrieval 20" --init fmvs --planar 0.2 --blur 0.0222 --pgsr   # = the default
```

The default recipe is the best model's (R-023): retrieval SfM, fast dense init, planar prior 0.2, blur model with
exposure 1/45 s (0.0222), PGSR-lite.

## Rules that matter

- One run at a time on the GPU (buildscan refuses a second one).
- Every run gets an entry in [TRAINING.md](progress/TRAINING.md): before it starts, every error, and the result.
- `<...>` in these docs means "put your value here": type `latest` or `scan_056fe94d3399`, never `<scan>`.
