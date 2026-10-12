"""
BuildScan 3D — Processing Server

Endpoints:
  POST /upload          Upload a dataset (multipart: dataset.mp4 + sidecar files)
  GET  /status/{job_id} Poll job progress
  GET  /jobs            List all jobs
  GET  /download/{job_id}  Download the finished splat.ply

Run:  python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
"""

import os
import shutil
import uuid
import logging
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from .pipeline import Job, JobStatus, start_pipeline_thread

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_ROOT = PROJECT_ROOT / "dataset"

app = FastAPI(title="BuildScan 3D Processing Server")

# In-memory job store (single-server; swap for Redis/DB on RunPod if needed)
jobs: dict[str, Job] = {}


@app.post("/upload")
async def upload_dataset(
    video: UploadFile = File(..., description="dataset.mp4"),
    poses: UploadFile = File(..., description="poses.csv"),
    tracking: UploadFile = File(..., description="tracking.csv"),
    points: UploadFile = File(..., description="points.csv"),
    quality: UploadFile = File(..., description="quality.csv"),
    meta: UploadFile = File(..., description="meta.json"),
    depth_zip: UploadFile = File(None, description="depth.zip — zipped depth/ folder"),
    iterations: int = Form(30000),
):
    job_id = uuid.uuid4().hex[:12]
    dataset_dir = DATASET_ROOT / f"scan_{job_id}"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    depth_dir = dataset_dir / "depth"
    depth_dir.mkdir(exist_ok=True)

    try:
        # Save sidecar CSV/JSON files
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
                while chunk := await upload.read(1024 * 1024):
                    f.write(chunk)
            log.info("Saved %s (%d bytes)", dst.name, dst.stat().st_size)

        # Unzip depth folder if provided
        if depth_zip and depth_zip.filename:
            zip_path = dataset_dir / "depth.zip"
            with open(zip_path, "wb") as f:
                while chunk := await depth_zip.read(1024 * 1024):
                    f.write(chunk)
            shutil.unpack_archive(zip_path, dataset_dir)
            zip_path.unlink()
            log.info("Extracted depth.zip")

    except Exception as e:
        shutil.rmtree(dataset_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

    # Create job and start processing
    job = Job(job_id=job_id, dataset_dir=str(dataset_dir))
    jobs[job_id] = job
    start_pipeline_thread(job, iterations=iterations)

    return {"job_id": job_id, "status": "processing", "poll": f"/status/{job_id}"}


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
    return {"status": "ok"}
