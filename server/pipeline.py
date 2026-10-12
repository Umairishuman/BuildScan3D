"""
Pipeline runner — executes the 3DGS processing steps as subprocesses
with per-step timeouts and progress reporting.
"""

import os
import subprocess
import threading
import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

log = logging.getLogger(__name__)

# ---------- configuration ----------

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PYTHON = "python"
NS_PYTHON = os.path.join(PROJECT_ROOT, "nerfstudio-env", "Scripts", "python.exe")
NS_TRAIN = os.path.join(PROJECT_ROOT, "nerfstudio-env", "Scripts", "ns-train.exe")
NS_EXPORT = os.path.join(PROJECT_ROOT, "nerfstudio-env", "Scripts", "ns-export.exe")


class StepName(str, Enum):
    UPLOAD = "upload"
    FALLBACK = "fallback"
    PREPARE = "prepare"
    SFM_COLMAP = "sfm_colmap"
    EXPORT_NS = "export_nerfstudio"
    TRAIN = "train"
    EXPORT_SPLAT = "export_splat"


@dataclass
class StepConfig:
    name: StepName
    label: str
    timeout_sec: int  # max wall-clock seconds for this step


STEPS = [
    StepConfig(StepName.FALLBACK, "IMU fallback bridging", timeout_sec=120),
    StepConfig(StepName.PREPARE, "Extracting keyframes from video", timeout_sec=300),
    StepConfig(StepName.SFM_COLMAP, "COLMAP feature matching & mapping", timeout_sec=2400),
    StepConfig(StepName.EXPORT_NS, "Exporting to Nerfstudio format", timeout_sec=120),
    StepConfig(StepName.TRAIN, "Training 3D Gaussian Splatting", timeout_sec=3600),
    StepConfig(StepName.EXPORT_SPLAT, "Exporting final splat model", timeout_sec=300),
]


class JobStatus(str, Enum):
    QUEUED = "queued"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    job_id: str
    dataset_dir: str
    status: JobStatus = JobStatus.QUEUED
    current_step: Optional[str] = None
    current_step_label: Optional[str] = None
    step_index: int = 0
    total_steps: int = len(STEPS)
    progress_pct: int = 0
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    output_path: Optional[str] = None
    log_lines: list = field(default_factory=list)

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "current_step": self.current_step,
            "current_step_label": self.current_step_label,
            "step_index": self.step_index,
            "total_steps": self.total_steps,
            "progress_pct": self.progress_pct,
            "error": self.error,
            "elapsed_sec": round(time.time() - self.started_at) if self.started_at else 0,
            "output_path": self.output_path,
            "recent_logs": self.log_lines[-20:],
        }

    def _append_log(self, line: str):
        self.log_lines.append(line.rstrip())
        if len(self.log_lines) > 200:
            self.log_lines = self.log_lines[-200:]


def _build_commands(dataset_dir: str, iterations: int = 30000) -> list:
    """Return (StepConfig, cmd_list) pairs mirroring run_arcore3dgs.bat."""
    work = os.path.join(dataset_dir, "work")
    work_sfm = os.path.join(dataset_dir, "work_sfm")

    commands = []

    # 1. fallback
    commands.append((STEPS[0], [
        PYTHON, os.path.join(PROJECT_ROOT, "src", "arcore3dgs", "fallback.py"),
        dataset_dir,
    ]))

    # 2. prepare (only if work/frames.json doesn't exist yet)
    commands.append((STEPS[1], [
        PYTHON, os.path.join(PROJECT_ROOT, "src", "arcore3dgs", "prepare.py"),
        "--dataset", dataset_dir, "--out", work, "--depth", "0",
    ]))

    # 3. sfm_colmap
    commands.append((STEPS[2], [
        PYTHON, os.path.join(PROJECT_ROOT, "src", "arcore3dgs", "sfm_colmap.py"),
        "--work", work, "--out", work_sfm,
    ]))

    # 4. export_nerfstudio
    commands.append((STEPS[3], [
        NS_PYTHON, os.path.join(PROJECT_ROOT, "src", "arcore3dgs", "export_nerfstudio.py"),
        "--work", work_sfm, "--downscale", "1",
    ]))

    # 5. ns-train splatfacto
    commands.append((STEPS[4], [
        NS_TRAIN, "splatfacto",
        "--data", work_sfm,
        "--output-dir", os.path.join(work_sfm, "ns"),
        "--experiment-name", "gs", "--timestamp", "run",
        "--max-num-iterations", str(iterations),
        "--steps-per-save", "5000",
        "--vis", "tensorboard",
        "--viewer.quit-on-train-completion", "True",
        "--pipeline.model.random-init", "False",
        "--pipeline.model.use-bilateral-grid", "True",
        "--pipeline.model.use-scale-regularization", "True",
        "--pipeline.model.camera-optimizer.mode", "off",
        "--pipeline.datamanager.cache-images", "cpu",
        "--pipeline.datamanager.cache-images-type", "uint8",
        "nerfstudio-data",
        "--auto-scale-poses", "False",
        "--center-method", "none",
        "--orientation-method", "none",
        "--downscale-factor", "1",
        "--load-3D-points", "True",
    ]))

    # 6. ns-export
    config_yml = os.path.join(work_sfm, "ns", "gs", "splatfacto", "run", "config.yml")
    output_dir = os.path.join(work_sfm, "gs_sfm")
    commands.append((STEPS[5], [
        NS_EXPORT, "gaussian-splat",
        "--load-config", config_yml,
        "--output-dir", output_dir,
    ]))

    return commands


def run_pipeline(job: Job, iterations: int = 30000):
    """Run all pipeline steps sequentially. Called from a background thread."""
    job.status = JobStatus.PROCESSING
    job.started_at = time.time()

    commands = _build_commands(job.dataset_dir, iterations)

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    for i, (step_cfg, cmd) in enumerate(commands):
        job.step_index = i
        job.current_step = step_cfg.name.value
        job.current_step_label = step_cfg.label
        job.progress_pct = int((i / len(commands)) * 100)
        job._append_log(f"[step {i+1}/{len(commands)}] {step_cfg.label}")
        log.info("Job %s: starting step %s", job.job_id, step_cfg.name.value)

        # Skip prepare if frames.json already exists
        if step_cfg.name == StepName.PREPARE:
            frames_json = os.path.join(job.dataset_dir, "work", "frames.json")
            if os.path.exists(frames_json):
                job._append_log("  frames.json exists, skipping prepare")
                continue

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=PROJECT_ROOT,
                env=env,
                bufsize=1,
            )
        except FileNotFoundError as e:
            job.status = JobStatus.FAILED
            job.error = f"Step {step_cfg.name.value}: executable not found — {e}"
            job.finished_at = time.time()
            return

        deadline = time.time() + step_cfg.timeout_sec
        while True:
            # Check timeout
            if time.time() > deadline:
                proc.kill()
                proc.wait()
                job.status = JobStatus.FAILED
                job.error = (
                    f"Step {step_cfg.name.value} timed out after "
                    f"{step_cfg.timeout_sec}s"
                )
                job.finished_at = time.time()
                log.error("Job %s: %s", job.job_id, job.error)
                return

            line = proc.stdout.readline()
            if line:
                job._append_log(line)
            elif proc.poll() is not None:
                break

        rc = proc.returncode
        if rc != 0:
            job.status = JobStatus.FAILED
            job.error = f"Step {step_cfg.name.value} failed with exit code {rc}"
            job.finished_at = time.time()
            log.error("Job %s: %s", job.job_id, job.error)
            return

        job._append_log(f"  completed in {int(time.time() - deadline + step_cfg.timeout_sec)}s")

    # All steps done
    splat_path = os.path.join(job.dataset_dir, "work_sfm", "gs_sfm", "splat.ply")
    job.status = JobStatus.COMPLETED
    job.progress_pct = 100
    job.current_step_label = "Done"
    job.output_path = splat_path if os.path.exists(splat_path) else None
    job.finished_at = time.time()
    log.info("Job %s: completed in %.0fs", job.job_id, job.finished_at - job.started_at)


def start_pipeline_thread(job: Job, iterations: int = 30000) -> threading.Thread:
    t = threading.Thread(target=run_pipeline, args=(job, iterations), daemon=True)
    t.start()
    return t
