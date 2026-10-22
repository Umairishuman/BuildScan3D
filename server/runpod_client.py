"""
RunPod on-demand pod management — create, monitor, execute, and terminate GPU pods.

Flow:
  1. create_pod()     — spin up a GPU pod from a template
  2. wait_for_ready()  — poll until SSH is available
  3. upload_dataset()  — SCP the dataset folder to the pod
  4. run_pipeline()    — SSH and run the processing pipeline with live progress
  5. download_result() — SCP the splat.ply back
  6. terminate_pod()   — destroy the pod (stops billing)
"""

import io
import json
import os
import time
import logging
import subprocess
import threading
from dataclasses import dataclass
from typing import Optional

import requests

log = logging.getLogger(__name__)

RUNPOD_API = "https://api.runpod.io/graphql"


@dataclass
class PodInfo:
    pod_id: str
    status: str
    ssh_host: Optional[str] = None
    ssh_port: Optional[int] = None
    gpu_type: Optional[str] = None


class RunPodClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        self.params = {"api_key": api_key}

    def _query(self, query: str, variables: dict = None) -> dict:
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        resp = requests.post(RUNPOD_API, json=payload, params=self.params, headers=self.headers)
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            raise RuntimeError(f"RunPod API error: {data['errors']}")
        return data.get("data", {})

    def list_gpu_types(self) -> list:
        """List available GPU types with pricing and real-time stock status."""
        query = """
        query GpuTypes {
          gpuTypes {
            id
            displayName
            memoryInGb
            secureCloud
            communityCloud
            lowestPrice(input: { gpuCount: 1 }) {
              minimumBidPrice
              uninterruptablePrice
              stockStatus
            }
          }
        }
        """
        data = self._query(query)
        gpus = data.get("gpuTypes", [])
        result = []
        for g in gpus:
            price = g.get("lowestPrice") or {}
            result.append({
                "id": g["id"],
                "name": g.get("displayName", g["id"]),
                "vram_gb": g.get("memoryInGb", 0),
                "secure": g.get("secureCloud", False),
                "community": g.get("communityCloud", False),
                "price_on_demand": price.get("uninterruptablePrice"),
                "price_spot": price.get("minimumBidPrice"),
                "stock_status": price.get("stockStatus", "None"),
            })
        result.sort(key=lambda x: x.get("price_on_demand") or 999)
        return result

    def resolve_gpu_type(self, gpu_type: str) -> str:
        """Resolve a short/display GPU name to the actual API id."""
        try:
            gpus = self.list_gpu_types()
        except Exception:
            return gpu_type
        for g in gpus:
            if gpu_type in (g["id"], g["name"]):
                return g["id"]
        needle = gpu_type.lower()
        for g in gpus:
            if needle in g["id"].lower() or needle in g["name"].lower():
                return g["id"]
        return gpu_type

    def create_pod(
        self,
        name: str = "buildscan-3dgs",
        gpu_type: str = "RTX 4090",
        image: str = "umairishuman/buildscan-gpu:latest",
        disk_gb: int = 40,
        cloud_type: str = "SECURE",
        retry_interval: int = 15,
        max_retries: int = 6,
        job=None,
    ) -> PodInfo:
        """Create an on-demand GPU pod. Resolves short names, retries on supply constraints."""
        resolved = self.resolve_gpu_type(gpu_type)
        if resolved != gpu_type:
            log.info("Resolved GPU '%s' → '%s'", gpu_type, resolved)
            if job:
                job._append_log(f"Resolved GPU '{gpu_type}' → '{resolved}'")
            gpu_type = resolved

        query = """
        mutation createPod($input: PodFindAndDeployOnDemandInput!) {
          podFindAndDeployOnDemand(input: $input) {
            id
            desiredStatus
            imageName
            machine { gpuDisplayName }
          }
        }
        """
        pod_input = {
            "name": name,
            "imageName": image,
            "gpuTypeId": gpu_type,
            "gpuCount": 1,
            "cloudType": cloud_type,
            "containerDiskInGb": disk_gb,
            "startSsh": True,
        }

        cloud_types = ["SECURE", "COMMUNITY"] if cloud_type == "SECURE" else [cloud_type]
        for ct in cloud_types:
            pod_input["cloudType"] = ct
            for attempt in range(max_retries + 1):
                try:
                    data = self._query(query, {"input": pod_input})
                    pod = data["podFindAndDeployOnDemand"]
                    log.info("Created pod %s (%s) on %s cloud", pod["id"],
                             pod.get("machine", {}).get("gpuDisplayName", "?"), ct)
                    if job:
                        job._append_log(f"Pod created: {pod['id']} ({ct} cloud)")
                    return PodInfo(
                        pod_id=pod["id"],
                        status=pod.get("desiredStatus", "RUNNING"),
                        gpu_type=pod.get("machine", {}).get("gpuDisplayName"),
                    )
                except RuntimeError as e:
                    if "SUPPLY_CONSTRAINT" not in str(e):
                        raise
                    msg = f"No {gpu_type} on {ct} cloud (attempt {attempt+1}/{max_retries+1})"
                    log.warning(msg)
                    if job:
                        job._append_log(msg)

                if attempt < max_retries:
                    wait_msg = f"Waiting {retry_interval}s before retrying..."
                    log.info(wait_msg)
                    if job:
                        job._append_log(wait_msg)
                    time.sleep(retry_interval)

            if job:
                job._append_log(f"Exhausted {ct} cloud, trying next...")

        raise RuntimeError(
            f"No {gpu_type} available on any cloud after all attempts. "
            "Try a different GPU via the job manager (option 8 to browse)."
        )

    def get_pod(self, pod_id: str) -> PodInfo:
        query = """
        query getPod($podId: String!) {
          pod(input: { podId: $podId }) {
            id
            desiredStatus
            runtime { uptimeInSeconds ports { ip isIpPublic privatePort publicPort type } }
            machine { gpuDisplayName }
          }
        }
        """
        data = self._query(query, {"podId": pod_id})
        pod = data.get("pod")
        if not pod:
            raise RuntimeError(f"Pod {pod_id} not found")

        info = PodInfo(
            pod_id=pod["id"],
            status=pod.get("desiredStatus", "UNKNOWN"),
            gpu_type=pod.get("machine", {}).get("gpuDisplayName"),
        )

        runtime = pod.get("runtime")
        if runtime and runtime.get("ports"):
            for port in runtime["ports"]:
                if port.get("privatePort") == 22:
                    info.ssh_host = port.get("ip")
                    info.ssh_port = port.get("publicPort")
                    break

        return info

    def wait_for_ready(self, pod_id: str, timeout_sec: int = 300) -> PodInfo:
        """Poll until the pod has SSH access. Raises on timeout."""
        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            info = self.get_pod(pod_id)
            if info.ssh_host and info.ssh_port:
                log.info("Pod %s ready: SSH at %s:%d", pod_id, info.ssh_host, info.ssh_port)
                return info
            log.info("Pod %s: waiting for SSH (status=%s)...", pod_id, info.status)
            time.sleep(10)
        raise TimeoutError(f"Pod {pod_id} not ready after {timeout_sec}s")

    def terminate_pod(self, pod_id: str):
        query = """
        mutation terminatePod($input: PodTerminateInput!) {
          podTerminate(input: $input)
        }
        """
        self._query(query, {"input": {"podId": pod_id}})
        log.info("Terminated pod %s", pod_id)


# ---------- SSH helpers ----------

SSH_OPTS = [
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "LogLevel=ERROR",
    "-o", "ConnectTimeout=15",
]


def ssh_cmd(host: str, port: int, command: str, timeout: int = 3600) -> subprocess.CompletedProcess:
    """Run a command on the pod via SSH. Returns CompletedProcess."""
    cmd = ["ssh", *SSH_OPTS, "-p", str(port), f"root@{host}", command]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def ssh_stream(host: str, port: int, command: str, job, step_label: str, timeout: int = 3600) -> int:
    """Run a command on the pod via SSH, streaming stdout to job.log_lines. Returns exit code."""
    cmd = ["ssh", *SSH_OPTS, "-p", str(port), f"root@{host}", command]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    deadline = time.time() + timeout
    while True:
        if time.time() > deadline:
            proc.kill()
            proc.wait()
            raise TimeoutError(f"Step '{step_label}' timed out after {timeout}s")
        line = proc.stdout.readline()
        if line:
            job._append_log(line)
        elif proc.poll() is not None:
            break
    return proc.returncode


def scp_upload(host: str, port: int, local_path: str, remote_path: str, timeout: int = 600):
    """Upload a file or directory to the pod."""
    cmd = ["scp", *SSH_OPTS, "-P", str(port), "-r", local_path, f"root@{host}:{remote_path}"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"SCP upload failed: {result.stderr}")


def scp_download(host: str, port: int, remote_path: str, local_path: str, timeout: int = 600):
    """Download a file from the pod."""
    cmd = ["scp", *SSH_OPTS, "-P", str(port), f"root@{host}:{remote_path}", local_path]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"SCP download failed: {result.stderr}")


# ---------- Pipeline on RunPod ----------

SETUP_SCRIPT = r"""#!/bin/bash
set -e

# Skip setup if nerfstudio is already installed (custom Docker image)
if python -c "import nerfstudio" 2>/dev/null && command -v colmap &>/dev/null; then
    echo "=== Dependencies already installed (custom image) — skipping setup ==="
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    exit 0
fi

echo "=== Installing COLMAP ==="
apt-get update -qq && apt-get install -y colmap
echo "  COLMAP installed"

echo "=== Installing Python dependencies ==="
pip install nerfstudio==1.1.5 open3d==0.19.0 pyquaternion scipy opencv-python-headless plyfile
echo "  Python deps installed"

echo "=== Setup complete ==="
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
"""

# Pipeline steps to run on the pod (mirrors run_arcore3dgs.bat)
PIPELINE_COMMANDS = [
    ("fallback", "IMU fallback bridging", 120,
     "cd /workspace/project && python src/arcore3dgs/fallback.py {dataset}"),
    ("prepare", "Extracting keyframes", 300,
     "cd /workspace/project && python src/arcore3dgs/prepare.py --dataset {dataset} --out {dataset}/work --depth 0"),
    ("sfm_colmap", "COLMAP matching & mapping", 2400,
     "cd /workspace/project && python src/arcore3dgs/sfm_colmap.py --work {dataset}/work --out {dataset}/work_sfm"),
    ("export_ns", "Exporting to Nerfstudio", 120,
     "cd /workspace/project && python src/arcore3dgs/export_nerfstudio.py --work {dataset}/work_sfm --downscale 1"),
    ("train", "Training 3D Gaussian Splatting", 3600,
     "cd /workspace/project && ns-train splatfacto --data {dataset}/work_sfm --output-dir {dataset}/work_sfm/ns "
     "--experiment-name gs --timestamp run --max-num-iterations {iters} --steps-per-save 5000 "
     "--vis tensorboard --viewer.quit-on-train-completion True "
     "--pipeline.model.random-init False --pipeline.model.use-bilateral-grid True "
     "--pipeline.model.use-scale-regularization True --pipeline.model.camera-optimizer.mode off "
     "--pipeline.datamanager.cache-images cpu --pipeline.datamanager.cache-images-type uint8 "
     "nerfstudio-data --auto-scale-poses False --center-method none --orientation-method none "
     "--downscale-factor 1 --load-3D-points True"),
    ("export_splat", "Exporting final model", 300,
     "cd /workspace/project && ns-export gaussian-splat "
     "--load-config {dataset}/work_sfm/ns/gs/splatfacto/run/config.yml "
     "--output-dir {dataset}/work_sfm/gs_sfm"),
]


MAX_POD_LIFETIME_SEC = int(os.environ.get("MAX_POD_LIFETIME", 3600))  # 60 min default


def _pod_watchdog(client: RunPodClient, pod_id: str, job, max_sec: int):
    """Kill the pod if it runs longer than max_sec. Runs as a daemon thread."""
    time.sleep(max_sec)
    if job.status.value in ("processing", "uploading", "queued"):
        log.error("WATCHDOG: pod %s exceeded %ds lifetime — terminating", pod_id, max_sec)
        job._append_log(f"WATCHDOG: max pod lifetime ({max_sec}s) exceeded — terminating pod")
        try:
            client.terminate_pod(pod_id)
        except Exception as e:
            log.error("WATCHDOG: failed to terminate pod %s: %s", pod_id, e)


def run_pipeline_on_runpod(job, api_key: str, gpu_type: str = "RTX 4090",
                            iterations: int = 30000):
    """
    Full pipeline: create pod → setup → upload → process → download → terminate.
    Called from a background thread. Updates job status throughout.
    """
    from .pipeline import JobStatus, StepName

    client = RunPodClient(api_key)
    pod_info = None
    dataset_name = os.path.basename(job.dataset_dir)
    remote_dataset = f"/workspace/project/dataset/{dataset_name}"

    try:
        # Step 1: Create pod
        job.status = JobStatus.PROCESSING
        job.started_at = time.time()
        job.current_step = "creating_pod"
        job.current_step_label = "Creating GPU pod..."
        job.progress_pct = 0
        job._append_log(f"Requesting {gpu_type} pod...")

        pod_info = client.create_pod(gpu_type=gpu_type, job=job)
        job._append_log(f"Pod created: {pod_info.pod_id}")

        # Safety watchdog — terminates pod if total time exceeds limit
        watchdog = threading.Thread(
            target=_pod_watchdog,
            args=(client, pod_info.pod_id, job, MAX_POD_LIFETIME_SEC),
            daemon=True,
        )
        watchdog.start()
        job._append_log(f"Watchdog armed: pod will be killed after {MAX_POD_LIFETIME_SEC}s")

        # Step 2: Wait for SSH
        job.current_step_label = "Waiting for pod to start..."
        job.progress_pct = 5
        pod_info = client.wait_for_ready(pod_info.pod_id, timeout_sec=300)
        host, port = pod_info.ssh_host, pod_info.ssh_port
        job._append_log(f"Pod ready: SSH at {host}:{port}")

        # Give SSH daemon a moment to fully initialize
        time.sleep(5)

        # Step 3: Setup environment
        job.current_step = "setup"
        job.current_step_label = "Installing dependencies on GPU..."
        job.progress_pct = 8
        job._append_log("Running setup script...")
        rc = ssh_stream(host, port, SETUP_SCRIPT, job, "setup", timeout=600)
        if rc != 0:
            raise RuntimeError(f"Setup failed with exit code {rc}")

        # Step 4: Upload project code + dataset
        job.current_step = "upload"
        job.current_step_label = "Uploading project code & dataset..."
        job.progress_pct = 12
        job._append_log("Creating remote directories...")
        ssh_cmd(host, port, "mkdir -p /workspace/project/src/arcore3dgs /workspace/project/dataset")

        # Upload pipeline code
        job._append_log("Uploading pipeline code...")
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        scp_upload(host, port, os.path.join(project_root, "src", "arcore3dgs") + "/",
                   "/workspace/project/src/arcore3dgs/", timeout=120)

        # Upload dataset
        job._append_log(f"Uploading dataset ({dataset_name})...")
        scp_upload(host, port, job.dataset_dir, remote_dataset, timeout=600)
        job._append_log("Upload complete")

        # Step 5: Run pipeline steps
        total_steps = len(PIPELINE_COMMANDS)
        for i, (step_name, step_label, timeout, cmd_template) in enumerate(PIPELINE_COMMANDS):
            job.step_index = i
            job.current_step = step_name
            job.current_step_label = step_label
            job.progress_pct = 15 + int((i / total_steps) * 80)
            job.total_steps = total_steps
            job._append_log(f"[step {i+1}/{total_steps}] {step_label}")

            # Skip prepare if frames.json already exists
            if step_name == "prepare":
                check = ssh_cmd(host, port, f"test -f {remote_dataset}/work/frames.json && echo EXISTS")
                if "EXISTS" in (check.stdout or ""):
                    job._append_log("  frames.json exists, skipping")
                    continue

            cmd = cmd_template.format(dataset=remote_dataset, iters=iterations)
            rc = ssh_stream(host, port, cmd, job, step_label, timeout=timeout)
            if rc != 0:
                raise RuntimeError(f"Step '{step_name}' failed with exit code {rc}")
            job._append_log(f"  step complete")

        # Step 6: Download result
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
        log.info("Job %s completed on RunPod in %.0fs", job.job_id, job.finished_at - job.started_at)

    except Exception as e:
        job.status = JobStatus.FAILED
        job.error = str(e)
        job.finished_at = time.time()
        job._append_log(f"FAILED: {e}")
        log.error("Job %s failed on RunPod: %s", job.job_id, e)

    finally:
        # Always terminate the pod to stop billing
        if pod_info and pod_info.pod_id:
            try:
                job._append_log("Terminating pod...")
                client.terminate_pod(pod_info.pod_id)
                job._append_log("Pod terminated (billing stopped)")
            except Exception as e:
                job._append_log(f"WARNING: Failed to terminate pod {pod_info.pod_id}: {e}")
                log.error("Failed to terminate pod %s: %s", pod_info.pod_id, e)


def run_pipeline_on_existing_pod(job, api_key: str, pod_id: str,
                                  iterations: int = 30000):
    """
    Run pipeline on a pod the user already created (e.g. via RunPod website).
    Waits for SSH, runs the full pipeline, then terminates the pod.
    """
    from .pipeline import JobStatus

    client = RunPodClient(api_key)
    dataset_name = os.path.basename(job.dataset_dir)
    remote_dataset = f"/workspace/project/dataset/{dataset_name}"

    try:
        job.status = JobStatus.PROCESSING
        job.started_at = time.time()
        job.current_step = "connecting"
        job.current_step_label = "Connecting to existing pod..."
        job.progress_pct = 0
        job._append_log(f"Connecting to pod {pod_id}...")

        watchdog = threading.Thread(
            target=_pod_watchdog,
            args=(client, pod_id, job, MAX_POD_LIFETIME_SEC),
            daemon=True,
        )
        watchdog.start()
        job._append_log(f"Watchdog armed: pod will be killed after {MAX_POD_LIFETIME_SEC}s")

        pod_info = client.wait_for_ready(pod_id, timeout_sec=300)
        host, port = pod_info.ssh_host, pod_info.ssh_port
        job._append_log(f"Pod ready: SSH at {host}:{port} (GPU: {pod_info.gpu_type})")
        time.sleep(5)

        job.current_step = "setup"
        job.current_step_label = "Installing dependencies on GPU..."
        job.progress_pct = 8
        job._append_log("Running setup script...")
        rc = ssh_stream(host, port, SETUP_SCRIPT, job, "setup", timeout=600)
        if rc != 0:
            raise RuntimeError(f"Setup failed with exit code {rc}")

        job.current_step = "upload"
        job.current_step_label = "Uploading project code & dataset..."
        job.progress_pct = 12
        job._append_log("Creating remote directories...")
        ssh_cmd(host, port, "mkdir -p /workspace/project/src/arcore3dgs /workspace/project/dataset")

        job._append_log("Uploading pipeline code...")
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        scp_upload(host, port, os.path.join(project_root, "src", "arcore3dgs") + "/",
                   "/workspace/project/src/arcore3dgs/", timeout=120)

        job._append_log(f"Uploading dataset ({dataset_name})...")
        scp_upload(host, port, job.dataset_dir, remote_dataset, timeout=600)
        job._append_log("Upload complete")

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
            job._append_log(f"  step complete")

        job.current_step = "download"
        job.current_step_label = "Downloading result..."
        job.progress_pct = 95
        remote_splat = f"{remote_dataset}/work_sfm/gs_sfm/splat.ply"
        local_splat = os.path.join(job.dataset_dir, "splat.ply")
        job._append_log("Downloading splat.ply...")
        scp_download(host, port, remote_splat, local_splat, timeout=300)

        job.status = JobStatus.COMPLETED
        job.progress_pct = 100
        job.current_step_label = "Done"
        job.output_path = local_splat if os.path.exists(local_splat) else None
        job.finished_at = time.time()
        job._append_log(f"Completed in {int(job.finished_at - job.started_at)}s")

    except Exception as e:
        job.status = JobStatus.FAILED
        job.error = str(e)
        job.finished_at = time.time()
        job._append_log(f"FAILED: {e}")
        log.error("Job %s failed on pod %s: %s", job.job_id, pod_id, e)

    finally:
        try:
            job._append_log("Terminating pod...")
            client.terminate_pod(pod_id)
            job._append_log("Pod terminated (billing stopped)")
        except Exception as e:
            job._append_log(f"WARNING: Failed to terminate pod {pod_id}: {e}")
            log.error("Failed to terminate pod %s: %s", pod_id, e)


def start_runpod_pipeline_thread(job, api_key: str, gpu_type: str = "RTX 4090",
                                  iterations: int = 30000) -> threading.Thread:
    t = threading.Thread(
        target=run_pipeline_on_runpod,
        args=(job, api_key, gpu_type, iterations),
        daemon=True,
    )
    t.start()
    return t


def start_existing_pod_pipeline_thread(job, api_key: str, pod_id: str,
                                        iterations: int = 30000) -> threading.Thread:
    t = threading.Thread(
        target=run_pipeline_on_existing_pod,
        args=(job, api_key, pod_id, iterations),
        daemon=True,
    )
    t.start()
    return t
