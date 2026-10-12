# BuildScan 3D — System Flow

## End-to-End Pipeline

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐     ┌──────────────┐
│  Android App │────>│ Local Server │────>│ RunPod GPU Pod │────>│  3D Model    │
│  (Capture)   │     │  (FastAPI)   │     │ (RTX 4090)     │     │  (splat.ply) │
└─────────────┘     └──────────────┘     └────────────────┘     └──────────────┘
```

## Stage 1: Mobile Capture (Android App)

**Code**: `googleARCore/samples/hello_ar_java/`

1. User opens app → ARCore initializes camera + tracking
2. User taps record → `CaptureLogger` starts writing:
   - `dataset.mp4` — ARCore-recorded video (30 FPS)
   - `poses.csv` — camera pose per frame (position + quaternion + intrinsics)
   - `tracking.csv` — tracking state + failure reason per frame
   - `points.csv` — ARCore feature points (world-space)
   - `quality.csv` — live IQA metrics (sharpness, brightness, motion speed)
   - `depth/` — ARCore raw depth maps at 5 Hz (uint16 mm + confidence)
   - `meta.json` — device info, camera config, resolution
3. `QualityMonitor` gives live feedback (too fast, too dark, blurry, low texture)
4. `CoverageMap` shows which surfaces need more views (red/yellow/green dots)
5. User taps stop → quality summary dialog → **"Upload & Process"** button

**Performance**: During recording, all demo rendering (planes, virtual objects, PBR lighting) is disabled. Only camera feed + capture logging + quality overlay runs.

## Stage 2: Upload to Server

**Code**: `ProcessingActivity.java` → `server/main.py`

1. App zips the `depth/` folder
2. Uploads all files via multipart POST to `/upload`
3. Server saves to `dataset/scan_{job_id}/`
4. Server returns `job_id`
5. App polls `GET /status/{job_id}` every 3 seconds
6. Progress screen shows: step name, percentage, elapsed time, recent logs

**Server URL** is configurable in the app settings menu (persisted in SharedPreferences).

## Stage 3: Processing (Local or RunPod)

**Code**: `server/pipeline.py` (local) or `server/runpod_client.py` (cloud)

### Local Mode
Runs the pipeline directly on the PC's GPU as subprocesses.

### RunPod Mode
1. Creates an on-demand GPU pod (RTX 4090) via RunPod API
2. Installs dependencies (COLMAP, nerfstudio) via SSH
3. Uploads project code + dataset via SCP
4. Runs pipeline steps remotely via SSH
5. Downloads `splat.ply` back
6. **Terminates pod** (always, even on error — prevents billing leaks)

### Pipeline Steps

| Step | Script | What it does | Timeout |
|---|---|---|---|
| 1. Fallback | `fallback.py` | IMU-bridged tracking gap recovery | 2 min |
| 2. Prepare | `prepare.py` | Extract sharp keyframes from video | 5 min |
| 3. SfM | `sfm_colmap.py` | COLMAP SIFT matching + global mapper + Sim3 alignment to ARCore | 40 min |
| 4. Export | `export_nerfstudio.py` | Convert to Nerfstudio data format | 2 min |
| 5. Train | `ns-train splatfacto` | 3D Gaussian Splatting training (30k iterations) | 60 min |
| 6. Export | `ns-export` | Export final `splat.ply` model | 5 min |

**Output**: `dataset/scan_{job_id}/work_sfm/gs_sfm/splat.ply`

Each step has a watchdog timeout. If exceeded, the process is killed and the job is marked failed.

## Stage 4: Result

- `GET /download/{job_id}` returns the finished `splat.ply`
- Model is metric-scale (aligned to ARCore world coordinates, +Y up)
- Viewable with `scripts/view_splat.bat` on localhost:7010

## Project Structure

```
D:\FYP\
├── AGENTS.md              — Agent instructions & design guidelines
├── README.md              — Project overview
├── requirements.txt       — Python dependencies
│
├── googleARCore/          — Android capture app (hello_ar_java)
│   └── samples/hello_ar_java/
│       └── app/src/main/java/.../helloar/
│           ├── HelloArActivity.java      — Main AR camera + recording
│           ├── CaptureLogger.java        — Writes poses, points, depth, quality
│           ├── QualityMonitor.java       — Live IQA feedback
│           ├── CoverageMap.java          — Voxel coverage tracking
│           ├── CoverageOverlayView.java  — Coverage dot overlay
│           ├── GalleryActivity.java      — Video preview + trimming
│           └── ProcessingActivity.java   — Upload + progress UI
│
├── server/                — Processing backend (FastAPI)
│   ├── main.py            — API endpoints (/upload, /status, /config, etc.)
│   ├── pipeline.py        — Local pipeline runner with per-step timeouts
│   ├── runpod_client.py   — RunPod pod management + remote execution
│   ├── test_upload.py     — Test script
│   └── requirements.txt
│
├── src/arcore3dgs/        — Processing pipeline scripts
│   ├── prepare.py         — Keyframe extraction from video
│   ├── sfm_colmap.py      — COLMAP SfM + Sim3 alignment
│   ├── export_nerfstudio.py — Nerfstudio format export
│   ├── fallback.py        — IMU tracking gap bridging
│   ├── ba.py, mvs.py, ... — Legacy pipeline steps
│   └── view.py            — Splat viewer (localhost:7010)
│
├── scripts/               — Batch launchers
│   ├── run_arcore3dgs.bat — Main pipeline launcher
│   ├── view_splat.bat     — Splat viewer launcher
│   └── ...                — Legacy/utility scripts
│
├── docs/
│   ├── Flow.md            — This file
│   ├── progress/          — Development progress & analysis
│   │   ├── TODO.md
│   │   ├── Problems_and_Solutions.md
│   │   └── Training_Analysis.md
│   ├── proposal/          — FYP proposal documents & slides
│   └── Research Papers/   — Reference papers
│
└── dataset/               — Captured scan datasets
```

## Server Configuration

| Env Variable | Default | Purpose |
|---|---|---|
| `RUNPOD_API_KEY` | (none) | RunPod API key — enables RunPod mode |
| `RUNPOD_GPU_TYPE` | `NVIDIA RTX 4090` | GPU to request |

Switch modes at runtime: `POST /config {"mode": "local"}` or `POST /config {"mode": "runpod"}`
