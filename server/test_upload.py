"""
Quick test: upload an existing dataset to the local server and poll status.

Usage:
  1. Start the server:  python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
  2. Run this:           python server/test_upload.py dataset/newRoomAttemptSadness
"""

import sys
import time
import requests

SERVER = "http://localhost:8000"


def main():
    dataset = sys.argv[1] if len(sys.argv) > 1 else "dataset/newRoomAttemptSadness"
    print(f"Uploading from {dataset} ...")

    files = {}
    for name in ["dataset.mp4", "poses.csv", "tracking.csv", "points.csv", "quality.csv", "meta.json"]:
        path = f"{dataset}/{name}"
        try:
            files[name.split(".")[0]] = (name, open(path, "rb"))
        except FileNotFoundError:
            print(f"  WARNING: {path} not found, sending empty")
            files[name.split(".")[0]] = (name, b"")

    # Rename keys to match the endpoint parameter names
    upload_files = {
        "video": files.get("dataset", ("dataset.mp4", b"")),
        "poses": files.get("poses", ("poses.csv", b"")),
        "tracking": files.get("tracking", ("tracking.csv", b"")),
        "points": files.get("points", ("points.csv", b"")),
        "quality": files.get("quality", ("quality.csv", b"")),
        "meta": files.get("meta", ("meta.json", b"")),
    }

    resp = requests.post(f"{SERVER}/upload", files=upload_files, data={"iterations": 30000})
    resp.raise_for_status()
    result = resp.json()
    job_id = result["job_id"]
    print(f"Job created: {job_id}")
    print(f"Poll URL: {SERVER}/status/{job_id}")
    print()

    # Poll until done
    while True:
        status = requests.get(f"{SERVER}/status/{job_id}").json()
        pct = status["progress_pct"]
        step = status["current_step_label"] or "waiting"
        elapsed = status["elapsed_sec"]
        print(f"  [{pct:3d}%] {step} ({elapsed}s elapsed)")

        if status["status"] in ("completed", "failed"):
            print()
            if status["status"] == "completed":
                print(f"Done! Output: {status['output_path']}")
                print(f"Download: {SERVER}/download/{job_id}")
            else:
                print(f"FAILED: {status['error']}")
            break

        time.sleep(5)


if __name__ == "__main__":
    main()
