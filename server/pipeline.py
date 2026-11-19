"""
Pipeline runner — executes the 3DGS processing steps as subprocesses
with per-step timeouts and progress reporting.
"""

import os
import re
import shlex
import shutil
import subprocess
import sys
import threading
import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

log = logging.getLogger(__name__)

# ---------- configuration ----------

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PYTHON = sys.executable or "python"
# nerfstudio programs: the repo's venv on Windows, the micromamba env bs-ns on Linux (src/arcore3dgs/toolpaths.py)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src", "arcore3dgs"))
import toolpaths  # noqa: E402
NS_PYTHON = toolpaths.ns_cmd("python")
NS_TRAIN = toolpaths.ns_cmd("ns-train")
NS_EXPORT = toolpaths.ns_cmd("ns-export")

# Which recipe a job runs (OD-7 is open: the default stays the old v3 recipe).
#   BUILDSCAN_PIPELINE=v3  fallback -> prepare -> COLMAP -> splatfacto (_build_commands)
#   BUILDSCAN_PIPELINE=v9  scripts/run_full.sh: v9 3DGS -> layout -> semantics -> mesh -> web bundle
# BUILDSCAN_V9_ARGS overrides the run_v8.py arguments, BUILDSCAN_BASH the bash used for run_full.sh.
V9_STAGES = ["select", "sfm", "export", "prior", "init", "train", "ply", "layout", "sem2d", "sem3d", "verify",
             "sem3d2", "mesh", "meshlabels", "web", "plan"]
V9_LABELS = {"select": "Choosing sharp keyframes", "sfm": "COLMAP camera poses", "export": "Exporting cameras",
             "prior": "Depth / normal priors", "init": "Dense starting points", "train": "Training 3D Gaussian Splatting",
             "ply": "Exporting the model", "layout": "Room layout", "sem2d": "Finding fixtures in the images",
             "sem3d": "Labelling the model", "verify": "Checking fixtures", "sem3d2": "Final labels",
             "mesh": "Building the mesh", "meshlabels": "Labelling the mesh", "web": "Web viewer bundle",
             "plan": "Floor plan"}
V9_DEFAULT_ARGS = '--sfm_args "--retrieval 20" --init fmvs --planar 0.2 --blur 0.0222 --pgsr'   # R-023 / R-031 recipe
V9_TAG = "srv"
V9_TIMEOUT_SEC = 6 * 3600
_STAGE_LINE = re.compile(r"^==+ (?:\[[0-9:]+\] )?([a-z0-9]+)(?:[: ]|$)")


def pipeline_recipe() -> str:
    return "v9" if os.environ.get("BUILDSCAN_PIPELINE", "v3").lower() in ("v9", "v10") else "v3"


def _bash() -> str:
    if os.environ.get("BUILDSCAN_BASH"):
        return os.environ["BUILDSCAN_BASH"]
    if os.name == "nt":                     # Git Bash, not WSL's System32ash.exe
        for p in (r"C:\Program Files\Gitinash.exe", r"C:\Program Files (x86)\Gitinash.exe"):
            if os.path.exists(p):
                return p
    return shutil.which("bash") or "bash"


def build_v9_command(dataset_dir: str, tag: str = V9_TAG) -> list:
    """scripts/run_full.sh <dataset> <tag> -- <run_v8 args>; output in <dataset>/work_<tag>_sfm/gs_<tag>/."""
    args = shlex.split(os.environ.get("BUILDSCAN_V9_ARGS", V9_DEFAULT_ARGS))
    return [_bash(), os.path.join(PROJECT_ROOT, "scripts", "run_full.sh"), dataset_dir, tag, "--"] + args


def v9_stage_of(line: str) -> Optional[str]:
    """The run_full.sh / run_v8.py stage a log line starts ("=== [12:00:00] layout", "== train: ..."), else None."""
    m = _STAGE_LINE.match(line.strip())
    return m.group(1) if m and m.group(1) in V9_STAGES else None


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
        *NS_PYTHON, os.path.join(PROJECT_ROOT, "src", "arcore3dgs", "export_nerfstudio.py"),
        "--work", work_sfm, "--downscale", "1",
    ]))

    # 5. ns-train splatfacto
    commands.append((STEPS[4], [
        *NS_TRAIN, "splatfacto",
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
        *NS_EXPORT, "gaussian-splat",
        "--load-config", config_yml,
        "--output-dir", output_dir,
    ]))

    return commands


def run_v9_pipeline(job: Job):
    """BUILDSCAN_PIPELINE=v9: one run_full.sh process; its stage lines move the job's step / progress."""
    job.status = JobStatus.PROCESSING
    job.started_at = time.time()
    job.total_steps = len(V9_STAGES)
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env.setdefault("GPU_EVERY", "0")
    cmd = build_v9_command(job.dataset_dir)
    job._append_log("[v9] " + " ".join(cmd))
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=PROJECT_ROOT,
                                env=env, bufsize=1, encoding="utf-8", errors="replace")
    except FileNotFoundError as e:
        job.status = JobStatus.FAILED
        job.error = f"run_full.sh: executable not found — {e}"
        job.finished_at = time.time()
        return
    deadline = time.time() + V9_TIMEOUT_SEC
    for line in proc.stdout:                     # readline blocks; the timeout is checked per line
        job._append_log(line)
        st = v9_stage_of(line)
        if st:
            job.step_index = V9_STAGES.index(st)
            job.current_step = st
            job.current_step_label = V9_LABELS[st]
            job.progress_pct = int(100 * job.step_index / len(V9_STAGES))
        if time.time() > deadline:
            proc.kill()
            break
    proc.wait()
    job.finished_at = time.time()
    if time.time() > deadline:
        job.status = JobStatus.FAILED
        job.error = f"v9 pipeline timed out after {V9_TIMEOUT_SEC}s"
    elif proc.returncode != 0:
        job.status = JobStatus.FAILED
        job.error = f"v9 pipeline failed at stage {job.current_step} (exit code {proc.returncode})"
    else:
        splat = os.path.join(job.dataset_dir, f"work_{V9_TAG}_sfm", f"gs_{V9_TAG}", "splat.ply")
        job.status = JobStatus.COMPLETED
        job.progress_pct = 100
        job.current_step_label = "Done"
        job.output_path = splat if os.path.exists(splat) else None
    log.info("Job %s: v9 %s in %.0fs", job.job_id, job.status.value, job.finished_at - job.started_at)


def run_pipeline(job: Job, iterations: int = 30000):
    """Run all pipeline steps sequentially. Called from a background thread."""
    if pipeline_recipe() == "v9":
        return run_v9_pipeline(job)
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
