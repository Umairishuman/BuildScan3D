# BuildScan 3D — Processing Guide

End-to-end guide for scanning on the phone, processing on a GPU, and viewing the 3D result.

---

## Prerequisites

| Component | What you need |
|-----------|--------------|
| **Phone** | Android device with ARCore support |
| **App** | BuildScan 3D APK installed (download from [GitHub Releases](../../releases)) |
| **Server PC** | Python 3.10+, on the same WiFi as the phone |
| **GPU** | One of: RunPod account, local NVIDIA GPU, or a friend's GPU machine |

### Install server dependencies

```bash
cd FYP
pip install fastapi uvicorn python-multipart requests
```

For **local GPU** processing (your partner's machine), also install:

```bash
pip install nerfstudio==1.1.5 open3d pyquaternion scipy opencv-python-headless plyfile
# Also install COLMAP: https://colmap.github.io/install.html
```

---

## Quick Start

### 1. Start the server

```bash
scripts\start_server.bat
```

This will show:
- The processing mode (Dry Run / RunPod / Local)
- The IP address to enter in the phone app

### 2. Choose processing mode

Open the **Job Manager** in another terminal:

```bash
scripts\jobs.bat
```

Pick option **7) Processing mode**, then choose:

| Mode | When to use |
|------|-------------|
| **local** | Your machine has an NVIDIA GPU with COLMAP + Nerfstudio installed |
| **runpod** | Use RunPod cloud GPUs (costs credits, needs `RUNPOD_API_KEY` in `.env`) |
| **remote** | SSH into a friend's GPU machine (prompts for IP, port, user) |
| **dry_run** | Just save uploads, don't process (for testing the app) |

### 3. Record a scan

1. Open BuildScan 3D on your phone
2. The app will auto-discover the server on your network, or enter the IP manually
3. Point the camera at the area you want to scan
4. Tap **Record** — slowly walk around the subject (30-60 seconds is usually enough)
5. Tap **Stop** — choose **Upload & Process** to send it to the server

### 4. Monitor processing

In the Job Manager (`scripts\jobs.bat`):

- **1) List jobs** — see all jobs and their status
- **3) Watch job** — live-tail the logs as processing happens
- **5) Full logs** — dump everything if something went wrong

### 5. View the result

Once complete, the output `splat.ply` is saved in `dataset/scan_<id>/splat.ply`. Load it in the web viewer or any 3D Gaussian Splatting viewer.

---

## Reprocessing Existing Scans

Don't want to re-record every time? You don't have to.

In the Job Manager (`scripts\jobs.bat`), pick option **6) Reprocess existing scan**. It lists all scan datasets already on disk and lets you queue one for processing without re-uploading from the phone.

You can also hit the API directly:

```bash
curl -X POST http://localhost:8000/reprocess -d "dataset_name=scan_1750266764fa&iterations=30000"
```

---

## Processing Pipeline

The pipeline runs these steps in order:

| Step | What it does | Typical time |
|------|-------------|-------------|
| **1. Fallback** | Bridges IMU gaps in pose data | ~5s |
| **2. Prepare** | Extracts video keyframes + camera intrinsics | ~30s |
| **3. COLMAP SfM** | Feature matching & sparse reconstruction | 2-10 min |
| **4. Export** | Converts to Nerfstudio format | ~10s |
| **5. Train** | 3D Gaussian Splatting (splatfacto) | 3-5 min on RTX 4090 |
| **6. Export Splat** | Saves final `splat.ply` | ~15s |

---

## Job Manager Reference

Run `scripts\jobs.bat` for the interactive menu, or use direct commands:

```
scripts\jobs.bat                    Interactive menu
scripts\jobs.bat list               List all jobs
scripts\jobs.bat status <job_id>    Show status + recent logs
scripts\jobs.bat logs <job_id>      Full log dump
scripts\jobs.bat watch <job_id>     Live-tail a job
scripts\jobs.bat retry <job_id>     Retry a failed job
scripts\jobs.bat mode               Show current processing mode
```

---

## Server API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Server status + current mode |
| `GET` | `/config` | Full configuration |
| `POST` | `/config` | Update mode, API keys, remote GPU settings |
| `POST` | `/upload` | Upload a new scan (multipart form) |
| `GET` | `/jobs` | List all jobs |
| `GET` | `/status/<id>` | Job status + recent logs |
| `GET` | `/logs/<id>` | Full log output |
| `POST` | `/retry/<id>` | Retry a failed job |
| `GET` | `/datasets` | List scan datasets on disk |
| `POST` | `/reprocess` | Queue an existing dataset for processing |
| `GET` | `/download/<id>` | Download the finished `splat.ply` |

Interactive API docs: http://localhost:8000/docs

---

## Environment Variables

Set these in `.env` (loaded automatically by `start_server.bat`):

```env
PROCESSING_MODE=dry_run          # dry_run, local, runpod, or remote
RUNPOD_API_KEY=rpa_xxxxx         # Required for runpod mode
RUNPOD_GPU_TYPE=NVIDIA RTX 3090  # GPU to request from RunPod
REMOTE_GPU_HOST=192.168.1.50     # Friend's GPU machine IP (for remote mode)
REMOTE_GPU_PORT=22               # SSH port
REMOTE_GPU_USER=root             # SSH user
REMOTE_SKIP_SETUP=false          # Skip installing deps on remote (if already done)
MAX_POD_LIFETIME=7200            # Safety: kill RunPod pod after this many seconds (default 2 h)
```

---

## Safety Features

- **Pod watchdog**: RunPod pods are automatically terminated after `MAX_POD_LIFETIME` seconds (default 2 h), even if a step hangs
- **Per-step timeouts**: Each pipeline step has its own timeout (e.g., training: 60 min, COLMAP: 40 min)
- **Always-terminate**: RunPod pods are killed in a `finally` block — errors, crashes, timeouts all trigger cleanup
- **Dry run mode**: Default mode saves uploads without spending GPU credits

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Phone can't find server | Make sure phone and PC are on the same WiFi. Check the IP shown by `start_server.bat` |
| Upload stuck / slow | Check firewall isn't blocking port 8000. Try `curl http://localhost:8000/health` |
| Job failed at COLMAP | Usually means not enough visual overlap in the scan. Re-record with slower movement |
| Job failed at training | Check GPU memory. Reduce iterations (`iterations=10000`) for testing |
| RunPod pod still running | Check RunPod dashboard. The watchdog should have killed it, but verify manually |
| "SSH connection failed" (remote mode) | Set up SSH key auth: `ssh-copy-id user@remote-ip` |

---

## For Your Partner (Local GPU Setup)

If your partner has their own NVIDIA GPU:

1. Clone the repo on their machine
2. Install dependencies: `pip install -r requirements.txt` + COLMAP + Nerfstudio
3. Run `scripts\start_server.bat`
4. In another terminal: `scripts\jobs.bat` → option **7** → pick **local**
5. Upload from the phone to their server IP
6. Processing runs on their GPU — no cloud costs
