"""
Remote GPU processing — run the 3DGS pipeline on a friend's GPU machine via SSH.

Same flow as RunPod but without pod creation/termination (the machine is always on).
Requires SSH key-based auth to be set up between this machine and the remote GPU.
"""

import os
import threading
import time
import logging

from .runpod_client import (
    ssh_cmd, ssh_stream, scp_upload, scp_download, SETUP_SCRIPT, PIPELINE_COMMANDS,
)

log = logging.getLogger(__name__)


def run_pipeline_on_remote(job, host: str, port: int = 22, user: str = "root",
                           iterations: int = 30000, skip_setup: bool = False):
    from .pipeline import JobStatus

    dataset_name = os.path.basename(job.dataset_dir)
    remote_dataset = f"/workspace/project/dataset/{dataset_name}"

    try:
        job.status = JobStatus.PROCESSING
        job.started_at = time.time()
        job.progress_pct = 0

        # Test SSH connection
        job.current_step = "connecting"
        job.current_step_label = f"Connecting to {host}:{port}..."
        job._append_log(f"Connecting to {user}@{host}:{port}...")

        check = ssh_cmd(host, port, "echo OK && nvidia-smi --query-gpu=name,memory.total --format=csv,noheader", timeout=30)
        if check.returncode != 0:
            raise RuntimeError(f"SSH connection failed: {check.stderr}")
        job._append_log(f"Connected: {check.stdout.strip()}")

        # Setup (install deps — skip if already done)
        if not skip_setup:
            job.current_step = "setup"
            job.current_step_label = "Installing dependencies on remote GPU..."
            job.progress_pct = 5
            job._append_log("Running setup script...")
            rc = ssh_stream(host, port, SETUP_SCRIPT, job, "setup", timeout=600)
            if rc != 0:
                raise RuntimeError(f"Setup failed with exit code {rc}")
        else:
            job._append_log("Skipping setup (already configured)")
            job.progress_pct = 8

        # Upload project code + dataset
        job.current_step = "upload"
        job.current_step_label = "Uploading project code & dataset..."
        job.progress_pct = 10
        job._append_log("Creating remote directories...")
        ssh_cmd(host, port, "mkdir -p /workspace/project/src/arcore3dgs /workspace/project/dataset")

        job._append_log("Uploading pipeline code...")
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        scp_upload(host, port, os.path.join(project_root, "src", "arcore3dgs") + "/",
                   "/workspace/project/src/arcore3dgs/", timeout=120)

        job._append_log(f"Uploading dataset ({dataset_name})...")
        scp_upload(host, port, job.dataset_dir, remote_dataset, timeout=600)
        job._append_log("Upload complete")

        # Run pipeline steps
        total_steps = len(PIPELINE_COMMANDS)
        for i, (step_name, step_label, timeout, cmd_template) in enumerate(PIPELINE_COMMANDS):
            job.step_index = i
            job.current_step = step_name
            job.current_step_label = step_label
            job.progress_pct = 15 + int((i / total_steps) * 80)
            job.total_steps = total_steps
            job._append_log(f"[step {i+1}/{total_steps}] {step_label}")

            if step_name == "prepare":
                check = ssh_cmd(host, port, f"test -f {remote_dataset}/work/frames.json && echo EXISTS")
                if "EXISTS" in (check.stdout or ""):
                    job._append_log("  frames.json exists, skipping")
                    continue

            cmd = cmd_template.format(dataset=remote_dataset, iters=iterations)
            rc = ssh_stream(host, port, cmd, job, step_label, timeout=timeout)
            if rc != 0:
                raise RuntimeError(f"Step '{step_name}' failed with exit code {rc}")
            job._append_log("  step complete")

        # Download result
        job.current_step = "download"
        job.current_step_label = "Downloading result..."
        job.progress_pct = 95
        remote_splat = f"{remote_dataset}/work_sfm/gs_sfm/splat.ply"
        local_splat = os.path.join(job.dataset_dir, "splat.ply")
        job._append_log("Downloading splat.ply...")
        scp_download(host, port, remote_splat, local_splat, timeout=300)

        # Done
        job.status = JobStatus.COMPLETED
        job.progress_pct = 100
        job.current_step_label = "Done"
        job.output_path = local_splat if os.path.exists(local_splat) else None
        job.finished_at = time.time()
        job._append_log(f"Completed in {int(job.finished_at - job.started_at)}s")
        log.info("Job %s completed on remote GPU in %.0fs", job.job_id, job.finished_at - job.started_at)

    except Exception as e:
        job.status = JobStatus.FAILED
        job.error = str(e)
        job.finished_at = time.time()
        job._append_log(f"FAILED: {e}")
        log.error("Job %s failed on remote GPU: %s", job.job_id, e)


def start_remote_pipeline_thread(job, host: str, port: int = 22, user: str = "root",
                                  iterations: int = 30000, skip_setup: bool = False) -> threading.Thread:
    t = threading.Thread(
        target=run_pipeline_on_remote,
        args=(job, host, port, user, iterations, skip_setup),
        daemon=True,
    )
    t.start()
    return t
