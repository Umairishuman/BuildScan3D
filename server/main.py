"""
BuildScan 3D — Processing Server

Endpoints:
  POST /upload          Upload a dataset (multipart: dataset.mp4 + sidecar files)
  GET  /status/{job_id} Poll job progress
  GET  /jobs            List all jobs
  GET  /download/{job_id}  Download the finished splat.ply
  GET  /config          Show current processing mode
  POST /config          Switch between local and RunPod processing

Run (local):   python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
Run (RunPod):  RUNPOD_API_KEY=your_key python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
"""

import os
import time
import shutil
import uuid
import logging
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .pipeline import Job, JobStatus, start_pipeline_thread
from .runpod_client import start_runpod_pipeline_thread, start_existing_pod_pipeline_thread
from .remote_gpu import start_remote_pipeline_thread

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_ROOT = PROJECT_ROOT / "dataset"


class UploadProgressLogger:
    """ASGI middleware: logs POST /upload while its body is still arriving (start, progress, done or cut off).

    FastAPI only calls the /upload handler after the whole multipart body is received, so without this the
    server is silent for the whole network transfer of the video.
    """

    def __init__(self, app, every_s: float = 5.0):
        self.app = app
        self.every_s = every_s

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"] != "/upload":
            return await self.app(scope, receive, send)

        headers = dict(scope.get("headers") or [])
        total = int(headers.get(b"content-length", b"0") or 0)
        client = (scope.get("client") or ("?",))[0]
        mb = 1024 * 1024
        state = {"got": 0, "t0": time.monotonic(), "last": time.monotonic(), "done": False}
        log.info("Upload started from %s: %s", client, f"{total / mb:.1f} MB" if total else "size unknown")

        def line():
            el = max(time.monotonic() - state["t0"], 1e-6)
            pct = f" ({100 * state['got'] / total:.0f}%)" if total else ""
            return f"{state['got'] / mb:.1f}{f' / {total / mb:.1f}' if total else ''} MB{pct}, " \
                   f"{state['got'] / mb / el:.2f} MB/s, {el:.0f} s"

        async def logged_receive():
            msg = await receive()
            if msg["type"] == "http.request":
                state["got"] += len(msg.get("body", b""))
                now = time.monotonic()
                if not msg.get("more_body", False):
                    state["done"] = True
                    log.info("Upload received from %s: %s", client, line())
                elif now - state["last"] >= self.every_s:
                    state["last"] = now
                    log.info("Upload receiving: %s", line())
            elif msg["type"] == "http.disconnect" and not state["done"]:
                log.warning("Upload from %s cut off: %s", client, line())
            return msg

        await self.app(scope, logged_receive, send)


class ErrorLogger:
    """ASGI middleware: logs when a device first talks to the server (or comes back after 5 min of silence), and
    every request that fails (status >= 400 or a crash) with the client, the path and the reason the server sent
    back, so an app-side failure is visible in the server terminal."""

    def __init__(self, app, quiet_s: float = 300.0):
        self.app = app
        self.quiet_s = quiet_s
        self.seen: dict[str, float] = {}

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        client = (scope.get("client") or ("?",))[0]
        what = f"{scope['method']} {scope['path']} from {client}"
        state = {"status": 0, "body": b""}
        now = time.monotonic()
        last = self.seen.get(client)
        if last is None or now - last > self.quiet_s:
            ua = dict(scope.get("headers") or []).get(b"user-agent", b"?").decode("utf-8", "replace")
            log.info("DEVICE %s %s (%s, first request: %s %s)", client,
                     "connected" if last is None else "back after a pause", ua, scope["method"], scope["path"])
        self.seen[client] = now

        async def logged_send(msg):
            if msg["type"] == "http.response.start":
                state["status"] = msg["status"]
            elif msg["type"] == "http.response.body" and state["status"] >= 400 and len(state["body"]) < 1000:
                state["body"] += msg.get("body", b"")
                if not msg.get("more_body", False):
                    level = logging.ERROR if state["status"] >= 500 else logging.WARNING
                    log.log(level, "FAILED %s -> %d: %s", what, state["status"],
                            state["body"][:1000].decode("utf-8", "replace"))
            await send(msg)

        try:
            await self.app(scope, receive, logged_send)
        except Exception:
            log.exception("CRASH while handling %s", what)
            raise


DISCOVERY_PORT = int(os.environ.get("DISCOVERY_PORT", "8001"))
DISCOVERY_MAGIC = b"BUILDSCAN_DISCOVER"


def _discovery_loop():
    """Answer the app's UDP broadcast "BUILDSCAN_DISCOVER" with this server's URL, so the app's server list finds it
    on any network size (the app's own address sweep only covers its /24)."""
    import json
    import socket
    port = int(os.environ.get("PORT", "8000"))
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", DISCOVERY_PORT))
    except OSError as e:
        log.warning("Discovery off: cannot listen on UDP %d (%s); the app can still use the URL typed in", DISCOVERY_PORT, e)
        return
    log.info("Discovery: answering the app's server search on UDP %d", DISCOVERY_PORT)
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if not data.startswith(DISCOVERY_MAGIC):
                continue
            probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            probe.connect((addr[0], addr[1]))           # no packet is sent: only picks the local address toward the phone
            ip = probe.getsockname()[0]
            probe.close()
            url = f"http://{ip}:{port}"
            reply = {"service": "buildscan3d", "url": url, "mode": processing_config["mode"], "host": socket.gethostname()}
            sock.sendto(json.dumps(reply).encode(), addr)
            log.info("DISCOVERY search from %s, answered %s", addr[0], url)
        except Exception as e:                              # never let one bad packet stop discovery
            log.warning("Discovery error: %s", e)


app = FastAPI(title="BuildScan 3D Processing Server")
app.add_middleware(UploadProgressLogger)
app.add_middleware(ErrorLogger)


@app.on_event("startup")
async def _start_discovery():
    import threading
    threading.Thread(target=_discovery_loop, name="discovery", daemon=True).start()

jobs: dict[str, Job] = {}

processing_config = {
    "mode": os.environ.get("PROCESSING_MODE", "dry_run"),
    "runpod_api_key": os.environ.get("RUNPOD_API_KEY", ""),
    "runpod_gpu_type": os.environ.get("RUNPOD_GPU_TYPE", "RTX 4090"),
    "remote_host": os.environ.get("REMOTE_GPU_HOST", ""),
    "remote_port": int(os.environ.get("REMOTE_GPU_PORT", "22")),
    "remote_user": os.environ.get("REMOTE_GPU_USER", "root"),
    "remote_skip_setup": os.environ.get("REMOTE_SKIP_SETUP", "").lower() in ("1", "true", "yes"),
}


class ConfigUpdate(BaseModel):
    mode: str = None
    runpod_api_key: str = None
    runpod_gpu_type: str = None
    remote_host: str = None
    remote_port: int = None
    remote_user: str = None
    remote_skip_setup: bool = None


@app.get("/config")
async def get_config():
    return {
        "mode": processing_config["mode"],
        "runpod_gpu_type": processing_config["runpod_gpu_type"],
        "runpod_api_key_set": bool(processing_config["runpod_api_key"]),
        "remote_host": processing_config["remote_host"],
        "remote_port": processing_config["remote_port"],
        "remote_user": processing_config["remote_user"],
        "remote_skip_setup": processing_config["remote_skip_setup"],
    }


@app.post("/config")
async def update_config(cfg: ConfigUpdate):
    if cfg.mode and cfg.mode in ("local", "runpod", "dry_run", "remote"):
        processing_config["mode"] = cfg.mode
    if cfg.runpod_api_key is not None:
        processing_config["runpod_api_key"] = cfg.runpod_api_key
    if cfg.runpod_gpu_type:
        processing_config["runpod_gpu_type"] = cfg.runpod_gpu_type
    if cfg.remote_host is not None:
        processing_config["remote_host"] = cfg.remote_host
    if cfg.remote_port is not None:
        processing_config["remote_port"] = cfg.remote_port
    if cfg.remote_user is not None:
        processing_config["remote_user"] = cfg.remote_user
    if cfg.remote_skip_setup is not None:
        processing_config["remote_skip_setup"] = cfg.remote_skip_setup
    return await get_config()


@app.post("/upload")
async def upload_dataset(
    video: UploadFile = File(..., description="dataset.mp4"),
    poses: UploadFile = File(..., description="poses.csv"),
    tracking: UploadFile = File(..., description="tracking.csv"),
    points: UploadFile = File(..., description="points.csv"),
    quality: UploadFile = File(..., description="quality.csv"),
    meta: UploadFile = File(..., description="meta.json"),
    depth_zip: UploadFile = File(None, description="depth.zip — zipped depth/ folder"),
    camera: UploadFile = File(None, description="camera.csv — per-frame exposure / rolling shutter (app >= 2026-10-12)"),
    anchors: UploadFile = File(None, description="anchors.csv — anchor poses, shows ARCore re-anchors"),
    lens_metadata: UploadFile = File(None, description="lens_metadata.json — ARCore lens calibration"),
    camera_characteristics: UploadFile = File(None, description="camera_characteristics.json — Camera2 characteristics"),
    iterations: int = Form(30000),
):
    job_id = uuid.uuid4().hex[:12]
    dataset_dir = DATASET_ROOT / f"scan_{job_id}"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    depth_dir = dataset_dir / "depth"
    depth_dir.mkdir(exist_ok=True)

    try:
        for name, upload in [
            ("dataset.mp4", video),
            ("poses.csv", poses),
            ("tracking.csv", tracking),
            ("points.csv", points),
            ("quality.csv", quality),
            ("meta.json", meta),
        ]:
            dst = dataset_dir / name
            with open(dst, "wb") as f:
                while chunk := await upload.read(8 * 1024 * 1024):
                    f.write(chunk)
            log.info("Saved %s (%d bytes)", dst.name, dst.stat().st_size)

        for name, upload in [
            ("camera.csv", camera),
            ("anchors.csv", anchors),
            ("lens_metadata.json", lens_metadata),
            ("camera_characteristics.json", camera_characteristics),
        ]:
            if upload is None or not upload.filename:
                log.warning("Optional %s not in this upload (older app?)", name)
                continue
            dst = dataset_dir / name
            with open(dst, "wb") as f:
                while chunk := await upload.read(8 * 1024 * 1024):
                    f.write(chunk)
            log.info("Saved %s (%d bytes)", dst.name, dst.stat().st_size)

        if depth_zip and depth_zip.filename:
            zip_path = dataset_dir / "depth.zip"
            with open(zip_path, "wb") as f:
                while chunk := await depth_zip.read(1024 * 1024):
                    f.write(chunk)
            shutil.unpack_archive(zip_path, dataset_dir)
            zip_path.unlink()
            log.info("Extracted depth.zip (%d depth files)", sum(1 for _ in depth_dir.iterdir()))
        else:
            log.warning("No depth.zip in this upload")

        log.info("Upload complete: %s", dataset_dir)

    except Exception as e:
        log.error("Upload failed, %s removed: %s", dataset_dir.name, e)
        shutil.rmtree(dataset_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

    job = Job(job_id=job_id, dataset_dir=str(dataset_dir))
    jobs[job_id] = job

    mode = processing_config["mode"]
    if mode == "dry_run":
        job.status = JobStatus.QUEUED
        job.current_step_label = "Upload saved — processing disabled (dry_run mode)"
        log.info("Job %s saved in dry_run mode (no processing)", job_id)
    elif mode == "runpod":
        api_key = processing_config["runpod_api_key"]
        if not api_key:
            raise HTTPException(status_code=400, detail="RunPod API key not set. POST /config or set RUNPOD_API_KEY env var.")
        gpu_type = processing_config["runpod_gpu_type"]
        start_runpod_pipeline_thread(job, api_key=api_key, gpu_type=gpu_type, iterations=iterations)
        log.info("Job %s started on RunPod (%s)", job_id, gpu_type)
    elif mode == "remote":
        rhost = processing_config["remote_host"]
        if not rhost:
            raise HTTPException(status_code=400, detail="Remote GPU host not set. POST /config or set REMOTE_GPU_HOST env var.")
        start_remote_pipeline_thread(
            job, host=rhost,
            port=processing_config["remote_port"],
            user=processing_config["remote_user"],
            iterations=iterations,
            skip_setup=processing_config["remote_skip_setup"],
        )
        log.info("Job %s started on remote GPU (%s)", job_id, rhost)
    else:
        start_pipeline_thread(job, iterations=iterations)
        log.info("Job %s started locally", job_id)

    return {
        "job_id": job_id,
        "status": "queued" if mode == "dry_run" else "processing",
        "mode": mode,
        "poll": f"/status/{job_id}",
    }


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.to_dict()


@app.get("/jobs")
async def list_jobs():
    return [
        {
            "job_id": j.job_id,
            "status": j.status.value,
            "current_step_label": j.current_step_label,
            "progress_pct": j.progress_pct,
        }
        for j in jobs.values()
    ]


@app.get("/logs/{job_id}")
async def get_logs(job_id: str):
    """Full log output for a job — useful for debugging failures."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "error": job.error,
        "log_lines": job.log_lines,
    }


@app.post("/retry/{job_id}")
async def retry_job(job_id: str):
    """Re-run a failed job with the same dataset."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.FAILED:
        raise HTTPException(status_code=409, detail=f"Job is {job.status.value}, not failed — only failed jobs can be retried")
    if not os.path.isdir(job.dataset_dir):
        raise HTTPException(status_code=404, detail="Dataset directory no longer exists")

    # Reset job state
    job.status = JobStatus.QUEUED
    job.error = None
    job.current_step = None
    job.current_step_label = "Retrying..."
    job.step_index = 0
    job.progress_pct = 0
    job.started_at = None
    job.finished_at = None
    job.output_path = None
    job.log_lines = [f"=== RETRY at {__import__('datetime').datetime.now().isoformat()} ==="]

    mode = processing_config["mode"]
    if mode == "runpod":
        api_key = processing_config["runpod_api_key"]
        if not api_key:
            raise HTTPException(status_code=400, detail="RunPod API key not set")
        gpu_type = processing_config["runpod_gpu_type"]
        start_runpod_pipeline_thread(job, api_key=api_key, gpu_type=gpu_type)
        log.info("Retrying job %s on RunPod", job_id)
    elif mode == "remote":
        rhost = processing_config["remote_host"]
        if not rhost:
            raise HTTPException(status_code=400, detail="Remote GPU host not set")
        start_remote_pipeline_thread(
            job, host=rhost,
            port=processing_config["remote_port"],
            user=processing_config["remote_user"],
            skip_setup=processing_config["remote_skip_setup"],
        )
        log.info("Retrying job %s on remote GPU", job_id)
    elif mode == "dry_run":
        job.status = JobStatus.QUEUED
        job.current_step_label = "Upload saved — processing disabled (dry_run mode)"
    else:
        start_pipeline_thread(job)
        log.info("Retrying job %s locally", job_id)

    return {"job_id": job_id, "status": "retrying", "mode": mode}


@app.get("/gpus")
async def list_gpus():
    """List available RunPod GPU types with pricing."""
    api_key = processing_config["runpod_api_key"]
    if not api_key:
        raise HTTPException(status_code=400, detail="RunPod API key not set")
    from .runpod_client import RunPodClient
    client = RunPodClient(api_key)
    return client.list_gpu_types()


@app.get("/datasets")
async def list_datasets():
    """List all scan datasets on disk (uploaded or not)."""
    datasets = []
    if DATASET_ROOT.exists():
        for d in sorted(DATASET_ROOT.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if d.is_dir() and d.name.startswith("scan_"):
                video = d / "dataset.mp4"
                poses = d / "poses.csv"
                has_job = any(j.dataset_dir == str(d) for j in jobs.values())
                job_status = None
                job_id = None
                for j in jobs.values():
                    if j.dataset_dir == str(d):
                        job_status = j.status.value
                        job_id = j.job_id
                        break
                datasets.append({
                    "name": d.name,
                    "path": str(d),
                    "size_mb": round(video.stat().st_size / (1024 * 1024), 1) if video.exists() else 0,
                    "has_video": video.exists(),
                    "has_poses": poses.exists(),
                    "has_job": has_job,
                    "job_id": job_id,
                    "job_status": job_status,
                })
    return datasets


@app.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel/reset a stuck job so the dataset can be reprocessed."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    job = jobs[job_id]
    job.status = JobStatus.FAILED
    job.error = "Cancelled by user"
    job.finished_at = time.time()
    job._append_log("Job cancelled by user")
    return {"job_id": job_id, "status": "cancelled"}


@app.post("/run-on-pod")
async def run_on_existing_pod(dataset_name: str = Form(...), pod_id: str = Form(...),
                               iterations: int = Form(30000)):
    """Run pipeline on a pod the user created manually (e.g. via RunPod website)."""
    api_key = processing_config["runpod_api_key"]
    if not api_key:
        raise HTTPException(status_code=400, detail="RunPod API key not set")
    dataset_dir = DATASET_ROOT / dataset_name
    if not dataset_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found")
    if not (dataset_dir / "dataset.mp4").exists():
        raise HTTPException(status_code=400, detail="Dataset has no video file")

    job_id = dataset_name.replace("scan_", "")[:12]
    if job_id in jobs:
        job = jobs[job_id]
        if job.status.value in ("processing", "uploading"):
            raise HTTPException(status_code=409, detail="Job is already running")
    else:
        job = Job(job_id=job_id, dataset_dir=str(dataset_dir))
        jobs[job_id] = job

    job.status = JobStatus.QUEUED
    job.error = None
    job.current_step = None
    job.current_step_label = f"Connecting to pod {pod_id}..."
    job.step_index = 0
    job.progress_pct = 0
    job.started_at = None
    job.finished_at = None
    job.output_path = None
    job.log_lines = [f"=== RUN ON POD {pod_id} at {__import__('datetime').datetime.now().isoformat()} ==="]

    start_existing_pod_pipeline_thread(job, api_key=api_key, pod_id=pod_id, iterations=iterations)
    return {"job_id": job_id, "dataset": dataset_name, "pod_id": pod_id, "poll": f"/status/{job_id}"}


@app.post("/reprocess")
async def reprocess_dataset(dataset_name: str = Form(...), iterations: int = Form(30000)):
    """Queue processing for an existing dataset on disk — no re-upload needed."""
    dataset_dir = DATASET_ROOT / dataset_name
    if not dataset_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found in {DATASET_ROOT}")
    if not (dataset_dir / "dataset.mp4").exists():
        raise HTTPException(status_code=400, detail="Dataset has no video file")

    job_id = dataset_name.replace("scan_", "")[:12]
    # If a job already exists for this dataset, reset it
    if job_id in jobs:
        job = jobs[job_id]
        if job.status.value in ("processing", "uploading"):
            raise HTTPException(status_code=409, detail="Job is already running")
    else:
        job = Job(job_id=job_id, dataset_dir=str(dataset_dir))
        jobs[job_id] = job

    job.status = JobStatus.QUEUED
    job.error = None
    job.current_step = None
    job.current_step_label = "Reprocessing..."
    job.step_index = 0
    job.progress_pct = 0
    job.started_at = None
    job.finished_at = None
    job.output_path = None
    job.log_lines = [f"=== REPROCESS {dataset_name} at {__import__('datetime').datetime.now().isoformat()} ==="]

    mode = processing_config["mode"]
    if mode == "dry_run":
        job.current_step_label = "Upload saved — processing disabled (dry_run mode)"
    elif mode == "runpod":
        api_key = processing_config["runpod_api_key"]
        if not api_key:
            raise HTTPException(status_code=400, detail="RunPod API key not set")
        gpu_type = processing_config["runpod_gpu_type"]
        start_runpod_pipeline_thread(job, api_key=api_key, gpu_type=gpu_type, iterations=iterations)
    elif mode == "remote":
        rhost = processing_config["remote_host"]
        if not rhost:
            raise HTTPException(status_code=400, detail="Remote GPU host not set")
        start_remote_pipeline_thread(
            job, host=rhost,
            port=processing_config["remote_port"],
            user=processing_config["remote_user"],
            iterations=iterations,
            skip_setup=processing_config["remote_skip_setup"],
        )
    else:
        start_pipeline_thread(job, iterations=iterations)

    log.info("Reprocessing %s as job %s in %s mode", dataset_name, job_id, mode)
    return {"job_id": job_id, "dataset": dataset_name, "mode": mode, "poll": f"/status/{job_id}"}


@app.get("/download/{job_id}")
async def download_splat(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=409, detail=f"Job is {job.status.value}, not completed")
    if not job.output_path or not os.path.exists(job.output_path):
        raise HTTPException(status_code=404, detail="Output file not found")
    return FileResponse(
        job.output_path,
        media_type="application/octet-stream",
        filename=f"scan_{job_id}_splat.ply",
    )


@app.get("/health")
async def health():
    return {"status": "ok", "mode": processing_config["mode"]}
