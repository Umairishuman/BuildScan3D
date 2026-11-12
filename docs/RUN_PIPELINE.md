# Running the full pipeline (Linux)

How to turn a phone recording into a labelled 3D model on a Linux GPU machine (this Ubuntu PC today; the Docker
image and the friend's PC later). One command, `scripts/run_full.sh`, runs every stage from the raw recording to the
web viewer bundle. The Windows commands are in [STATUS §5](progress/STATUS.md); what each script does is in
[MAP.md](../MAP.md) §2–3.

Last checked: 2026-11-06 on this PC (RTX 4000 Ada 20 GB), first full runs R-028 / R-029 in
[TRAINING.md](progress/TRAINING.md).

## 0. Short version: `scripts/buildscan` (one command for everything)

```bash
scripts/buildscan status                    # what is running, upload server + phone URL, GPU, newest recordings
scripts/buildscan server start              # phone-upload server (stop: server stop, see it: server log)
scripts/buildscan datasets                  # recordings, newest first, with their runs
scripts/buildscan check latest              # capture check of the newest recording
scripts/buildscan run latest mytag          # full pipeline, best recipe, in screen session run-mytag
scripts/buildscan watch latest mytag        # live view: stage n of 15, training step, GPU (--raw: raw logs; Ctrl+C stops watching only)
scripts/buildscan results latest mytag      # where the outputs are + stage times
scripts/buildscan view latest mytag         # 3D viewer, http://localhost:7010
scripts/buildscan web                       # web dashboard, http://localhost:3000
scripts/buildscan stop <session>            # bs-server, run-<tag>, viewer, web
scripts/buildscan help                      # everything else (attach, ip, gpu, --from, custom recipe)
```

Leave arguments out and it asks (numbered lists). Cheat sheet: [COMMANDS.md](COMMANDS.md).
`latest` = the newest recording; or give its folder name (`scan_001_056fe94d3399`). Everything long-running is in a
named `screen` session, so it keeps running when the terminal or SSH closes. The sections below explain the steps and
the scripts underneath (`start_server.sh`, `run_full.sh`).

## 1. Once per machine

```bash
scripts/setup_linux.sh            # installs the envs bs-colmap, bs-ns, bs-system, semantic-env (no sudo, ~25 GB)
scripts/setup_linux.sh --check    # GPU, COLMAP, gsplat, Open3D, models: must end with "All checks passed"
```

The NVIDIA driver must already work (`nvidia-smi`). Details and every set-up problem met so far: TRAINING.md R-027.

## 2. Get a recording onto the PC

**From the phone (normal way).** Start the upload server, then upload from the app's gallery:

```bash
screen -dmS bs-server scripts/start_server.sh      # or scripts/start_server.sh to see it in the foreground
screen -r bs-server                                # watch it; leave with Ctrl+A then D
```

- The server prints the URL for the phone (`http://<this PC's IP>:8000`). In the app: ⋮ → Server URL → it searches
  for the server, or type the URL. The phone must be on the same network as the PC.
- The firewall must allow TCP 8000 and UDP 8001 on the network card in use (STATUS §7.1):
  `sudo ufw allow in on <card> to any port 8000 proto tcp` and `... port 8001 proto udp`
  (`wlp0s20f3` = Wi-Fi, `enp0s31f6` = cable; `ip -br addr` shows which has an address).
- The terminal shows `DEVICE ... connected`, upload progress and `Upload complete: .../dataset/scan_<id>`.
- The recording lands in `dataset/scan_<id>/`. Find the newest with `ls -t dataset/`.
- App v0.3.5+ also sends `camera.csv` (exposure), `anchors.csv` and the lens files; older apps do not.

**Copied by hand** (e.g. from the RTX 3070 PC): put the whole recording folder in `dataset/<name>/`.

## 3. Check the recording

```bash
~/.local/bin/micromamba run -n bs-system python src/arcore3dgs/check_capture.py dataset/scan_<id>
```

It must end with `OVERALL: READY TO PROCESS`. Warnings (short video, bad IQA, missing `camera.csv`) do not stop a run
but explain weak results. Always use `micromamba run` (it activates the env, which puts ffmpeg / ffprobe on the PATH).

## 4. Run everything

Replace `scan_<id>` with the real folder name and `<tag>` with a short name for this run (it names the output
folders, so a new tag never mixes with an older run):

```bash
cd ~/Desktop/BuildScan3D
screen -dmS run1 bash -c 'scripts/run_full.sh dataset/scan_<id> <tag> -- --sfm_args "--retrieval 20" --init fmvs --planar 0.2 --blur 0.0222 --pgsr'
screen -r run1          # watch it; leave with Ctrl+A then D (Ctrl+C would stop the run)
```

- Everything after `--` goes to `run_v8.py`. The options above are the best recipe (v9 + PGSR-lite, R-023).
  `--blur 0.0222` = 1/45 s, the assumed exposure (ARCore does not record it).
- Without `screen` it runs in the terminal, and closing the terminal stops it.
- One run at a time on one GPU.

**Stages, in order** (each runs in its own environment; `--from <stage>` restarts at one and reuses the earlier output):

| Stage | Script | What it makes |
|---|---|---|
| `select` | `select_sharp.py` | sharpest frame per 0.2 s (gyro-aware) → `work_<tag>/` |
| `sfm` | `sfm_colmap.py` | COLMAP camera poses, lens calibration, metric scale from ARCore → `work_<tag>_sfm/` |
| `export` | `export_nerfstudio.py` | `transforms.json` for training |
| `prior` | `mono_prior.py` | Metric3D depth + normals per frame |
| `init` | `fast_mvs.py` (+ `plane_seg.py`, `blur_motion.py` on the CPU) | dense starting point cloud |
| `train` | `geo_splatfacto.py` | the 3D Gaussian Splatting model (longest stage; output only in `train.log`) |
| `ply` | `ns-export` | `gs_<tag>/splat.ply` |
| `layout` | `layout.py` | walls, floor, ceiling, corners, room size → `gs_<tag>/layout/` |
| `sem2d` | `semantic2d.py` | 2D masks of doors, switches, sockets, lights (Grounding DINO + SAM) |
| `sem3d` | `semantic3d.py` | labels on the 3D model → `gs_<tag>/semantic_v10/` |
| `verify` | `verify_fixtures.py` | CLIP check of switches / sockets → `verdicts.json` |
| `sem3d2` | `semantic3d.py` | labels again, with the verdicts |
| `mesh` | `mesh.py` | surface mesh → `gs_<tag>/mesh/` |
| `meshlabels` | `mesh_labels.py` | labels and areas on the mesh, `.glb` files |
| `web` | `export_web.py` | viewer bundle → `prototype/web-ui/public/scans/<capture>_<tag>/` |

**Restart after a crash or a stop:**

```bash
scripts/run_full.sh dataset/scan_<id> <tag> --from sem2d                      # a stage after training: no run_v8 args needed
scripts/run_full.sh dataset/scan_<id> <tag> --from train -- <same run_v8 args>   # training or earlier: repeat the args
```

## 5. Watching a run

All files are in `dataset/scan_<id>/work_<tag>_sfm/gs_<tag>/`:

| File | What |
|---|---|
| `run_full.log` | everything the terminal shows: stage start / end, outputs, errors, GPU lines |
| `train.log` | training progress (step, %, time left). The terminal is otherwise quiet during training |
| `gpu.csv` | GPU use %, memory, temperature °C, power W every 30 s |
| `timing.json`, `stages.tsv` | minutes per stage |
| `plane_seg.log`, `blur_motion.log` | the two CPU side jobs of the init stage |

Every 30 s the run prints a line like
`[gpu 18:29:12] 97% | 4622 / 20475 MiB | 76 C | 101 W | train step 13980 (93.20%), ETA 2 m, 53 s`
(`<< HOT` from 85 °C). Change the interval with `GPU_EVERY=60 scripts/run_full.sh ...`, turn it off with `GPU_EVERY=0`.

From another terminal or over SSH (Tailscale, `ssh i230662@gpu-lab-precision-3680`):

```bash
tail -F dataset/scan_<id>/work_<tag>_sfm/gs_<tag>/{run_full.log,train.log}
watch -n 2 nvidia-smi
```

## 6. Results

- Model: `gs_<tag>/splat.ply`; layout `gs_<tag>/layout/` (`layout.json`, `plan.png`); labels `gs_<tag>/semantic_v10/`;
  mesh `gs_<tag>/mesh/`.
- Web bundle: `prototype/web-ui/public/scans/<capture>_<tag>/`. The viewer only shows bundles that have a project
  entry in `prototype/web-ui/src/lib/mockData.ts` (copy the `newroom-scan` entry, change `scanUrl`); then
  `cd prototype/web-ui && npm run dev` (Node from the `bs-ns` env).
- Keep a good model in `saved_models/YYYY-MM-DD_<tag>/` with a `README.txt` (CLAUDE.md §3).

## 7. Record the run

Every run gets an entry in [TRAINING.md](progress/TRAINING.md) (CLAUDE.md §2): before starting (run ID, command,
dataset, goal), every error as it happens, and at the end the stage times (`timing.json`, `stages.tsv`), results and a
verdict.

## 8. Problems met so far

| Symptom | Cause / fix |
|---|---|
| `FileNotFoundError: 'ffprobe'` | env not activated: use `micromamba run -n <env>` (R-028) |
| `FileNotFoundError: .../imu.npz` | fresh recording; fixed: `select_sharp.py` extracts it (R-028) |
| Terminal silent for 20+ min after `== train:` | normal: training writes only to `train.log`; the GPU line shows the step |
| `bash: new: No such file or directory` | `<...>` in a command is a placeholder; type the real folder name |
| `camera.csv missing` warning | recorded with an app before v0.3.5 (the upload dropped it); the run still works |
| Tailscale "offline", cannot reach the coordination server | the lab Wi-Fi cuts it; use the cable (STATUS §7.1) |
