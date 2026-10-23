"""HTTP tests of the processing server (server/main.py): upload, status, download, config, health.

No GPU, RunPod account or network is needed. The two functions that would start a real processing job are
replaced by recorders, and uploads go to a temporary folder."""
import io
import types
import zipfile

import pytest
from fastapi.testclient import TestClient

import server.main as m
from server.pipeline import Job, JobStatus

FILES = {
    "video": ("dataset.mp4", b"not really a video"),
    "poses": ("poses.csv", b"1,2,3\n"),
    "tracking": ("tracking.csv", b"1,TRACKING,NONE\n"),
    "points": ("points.csv", b"1,0,0,0,1,0.9\n"),
    "quality": ("quality.csv", b"timestamp_ns,level\n"),
    "meta": ("meta.json", b"{}"),
}


@pytest.fixture
def api(tmp_path, monkeypatch):
    started = types.SimpleNamespace(local=[], runpod=[])
    monkeypatch.setattr(m, "DATASET_ROOT", tmp_path / "dataset")
    monkeypatch.setattr(m, "jobs", {})
    monkeypatch.setattr(m, "processing_config",
                        {"mode": "local", "runpod_api_key": "", "runpod_gpu_type": "NVIDIA RTX 3090",
                         "remote_host": "", "remote_port": 22, "remote_user": "root",
                         "remote_skip_setup": False})
    monkeypatch.setattr(m, "start_pipeline_thread",
                        lambda job, iterations=30000: started.local.append((job.job_id, iterations)))
    monkeypatch.setattr(m, "start_runpod_pipeline_thread",
                        lambda job, api_key, gpu_type, iterations: started.runpod.append(
                            (job.job_id, api_key, gpu_type, iterations)))
    return types.SimpleNamespace(client=TestClient(m.app), started=started, root=tmp_path)


def upload(api, files=None, **data):
    return api.client.post("/upload", files=files or FILES, data=data)


# ------------------------------------------------------------------ health and config
def test_health_reports_ok_and_mode(api):
    r = api.client.get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok", "mode": "local"}


def test_config_never_returns_the_api_key(api):
    api.client.post("/config", json={"runpod_api_key": "super-secret-key"})
    r = api.client.get("/config")
    assert r.json()["runpod_api_key_set"] is True
    assert "super-secret-key" not in r.text


def test_config_can_switch_mode_and_gpu(api):
    r = api.client.post("/config", json={"mode": "runpod", "runpod_gpu_type": "NVIDIA RTX 4090"})
    assert r.status_code == 200
    assert r.json()["mode"] == "runpod" and r.json()["runpod_gpu_type"] == "NVIDIA RTX 4090"


def test_config_ignores_an_unknown_mode(api):
    r = api.client.post("/config", json={"mode": "banana"})
    assert r.json()["mode"] == "local"


# ------------------------------------------------------------------ upload
def test_upload_saves_every_file_and_starts_a_local_job(api):
    r = upload(api, iterations="1234")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "processing" and body["mode"] == "local"
    job_id = body["job_id"]
    assert len(job_id) == 12 and body["poll"] == f"/status/{job_id}"

    folder = api.root / "dataset" / f"scan_{job_id}"
    for field, (name, content) in FILES.items():
        assert (folder / name).read_bytes() == content
    assert api.started.local == [(job_id, 1234)]
    assert api.started.runpod == []


def test_upload_default_iterations_is_30000(api):
    upload(api)
    assert api.started.local[0][1] == 30000


def test_upload_missing_a_required_file_is_rejected_and_starts_nothing(api):
    files = {k: v for k, v in FILES.items() if k != "poses"}
    r = upload(api, files=files)
    assert r.status_code == 422
    assert api.started.local == [] and api.client.get("/jobs").json() == []


def test_upload_unpacks_the_optional_depth_zip(api):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("depth/100.depth", b"\x00\x01")
        z.writestr("depth/size.txt", "160 90\n")
    files = dict(FILES, depth_zip=("depth.zip", buf.getvalue()))
    job_id = upload(api, files=files).json()["job_id"]
    folder = api.root / "dataset" / f"scan_{job_id}"
    assert (folder / "depth" / "100.depth").read_bytes() == b"\x00\x01"
    assert (folder / "depth" / "size.txt").exists()
    assert not (folder / "depth.zip").exists()                      # the archive is removed after unpacking


def test_upload_with_a_corrupt_depth_zip_fails_cleanly(api):
    files = dict(FILES, depth_zip=("depth.zip", b"this is not a zip"))
    r = upload(api, files=files)
    assert r.status_code == 500 and "Upload failed" in r.json()["detail"]
    assert api.started.local == []
    assert not list((api.root / "dataset").glob("scan_*"))          # nothing half-written is left behind


def test_runpod_mode_without_api_key_is_rejected(api):
    api.client.post("/config", json={"mode": "runpod"})
    r = upload(api)
    assert r.status_code == 400 and "API key" in r.json()["detail"]
    assert api.started.runpod == [] and api.started.local == []


def test_runpod_mode_passes_key_gpu_and_iterations_to_the_runpod_starter(api):
    api.client.post("/config", json={"mode": "runpod", "runpod_api_key": "k-123", "runpod_gpu_type": "NVIDIA RTX 4090"})
    job_id = upload(api, iterations="500").json()["job_id"]
    assert api.started.runpod == [(job_id, "k-123", "NVIDIA RTX 4090", 500)]
    assert api.started.local == []


# ------------------------------------------------------------------ status and jobs
def test_status_of_an_uploaded_job_has_the_fields_the_app_reads(api):
    job_id = upload(api).json()["job_id"]
    r = api.client.get(f"/status/{job_id}")
    assert r.status_code == 200
    body = r.json()
    for key in ("job_id", "status", "current_step_label", "progress_pct", "elapsed_sec", "output_path", "error"):
        assert key in body                                          # ProcessingActivity polls these fields
    assert body["job_id"] == job_id and body["status"] == "queued" and body["progress_pct"] == 0


def test_status_of_an_unknown_job_is_404(api):
    assert api.client.get("/status/doesnotexist").status_code == 404


def test_jobs_list_starts_empty_then_lists_each_upload(api):
    assert api.client.get("/jobs").json() == []
    ids = {upload(api).json()["job_id"] for _ in range(2)}
    listed = api.client.get("/jobs").json()
    assert {j["job_id"] for j in listed} == ids and len(ids) == 2
    assert set(listed[0]) == {"job_id", "status", "current_step_label", "progress_pct"}


# ------------------------------------------------------------------ download
def test_download_of_an_unknown_job_is_404(api):
    assert api.client.get("/download/nope").status_code == 404


def test_download_before_the_job_is_finished_is_409(api):
    job_id = upload(api).json()["job_id"]
    r = api.client.get(f"/download/{job_id}")
    assert r.status_code == 409 and "queued" in r.json()["detail"]


def test_download_of_a_finished_job_returns_the_file(api, tmp_path):
    splat = tmp_path / "splat.ply"
    splat.write_bytes(b"ply\nformat binary_little_endian 1.0\n")
    m.jobs["abc123"] = Job(job_id="abc123", dataset_dir=str(tmp_path), status=JobStatus.COMPLETED,
                           output_path=str(splat))
    r = api.client.get("/download/abc123")
    assert r.status_code == 200 and r.content == splat.read_bytes()
    assert "scan_abc123_splat.ply" in r.headers["content-disposition"]


def test_download_when_the_output_file_has_vanished_is_404(api, tmp_path):
    m.jobs["gone"] = Job(job_id="gone", dataset_dir=str(tmp_path), status=JobStatus.COMPLETED,
                         output_path=str(tmp_path / "missing.ply"))
    assert api.client.get("/download/gone").status_code == 404


def test_download_of_a_failed_job_is_409(api, tmp_path):
    m.jobs["bad"] = Job(job_id="bad", dataset_dir=str(tmp_path), status=JobStatus.FAILED, error="colmap failed")
    r = api.client.get("/download/bad")
    assert r.status_code == 409 and "failed" in r.json()["detail"]
