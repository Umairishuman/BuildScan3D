"""scripts/publish_scan.py against a local folder bucket (--target dir:), on a synthetic repo (D-076, #29)."""
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "publish_scan.py"


def make_repo(root: Path):
    (root / "dataset").mkdir(parents=True)
    (root / "dataset" / ".scan_numbers.tsv").write_text("7\tscan_007_abc\n", encoding="utf-8")
    b = root / "prototype" / "web-ui" / "public" / "scans" / "scan_007_abc_t2"
    b.mkdir(parents=True)
    (b / "scan.json").write_text(json.dumps({"walls": [], "fixtures": [], "groups": [], "floor_area": 17.99}))
    (b / "walls.spz").write_bytes(b"x" * 1000)
    plan = root / "dataset" / "scan_007_abc" / "work_t1_sfm" / "gs_t2" / "layout"  # re-run on model t1
    plan.mkdir(parents=True)
    (plan / "plan.png").write_bytes(b"png")
    (root / "docs" / "progress").mkdir(parents=True)
    (root / "docs" / "progress" / "TRAINING.md").write_text("### R-099 · 2026-11-19 · test run (tag `t2`)\n", encoding="utf-8")


def run(root, bucket, *args):
    env = {**os.environ, "BUILDSCAN_ROOT": str(root)}
    env.pop("PUBLISH_OWNER", None)
    return subprocess.run([sys.executable, str(SCRIPT), *args, "--target", f"dir:{bucket}"],
                          env=env, capture_output=True, text=True)


def test_publish_list_unpublish(tmp_path):
    root, bucket = tmp_path / "repo", tmp_path / "bucket"
    make_repo(root)
    r = run(root, bucket, "publish", "7", "t2", "--owner", "umair", "--owner-name", "Umair", "--room", "Office")
    assert r.returncode == 0, r.stderr
    idx = json.loads((bucket / "scans" / "umair" / "index.json").read_text())
    (e,) = idx["bundles"]
    assert (e["folder"], e["scan_number"], e["run_id"], e["date"], e["room"], e["plan"]) == \
        ("scan_007_abc_t2", 7, "R-099", "2026-11-19", "Office", "plan.png")
    assert e["scan"]["floor_area"] == 17.99
    assert (bucket / "scans" / "umair" / "scan_007_abc_t2" / "walls.spz").stat().st_size == 1000
    assert (bucket / "scans" / "umair" / "scan_007_abc_t2" / "plan.png").exists()
    # a second person: own prefix and index, both listed in owners.json
    assert run(root, bucket, "publish", "7", "t2", "--owner", "tayyab").returncode == 0
    owners = json.loads((bucket / "owners.json").read_text())["owners"]
    assert [o["id"] for o in owners] == ["umair", "tayyab"]
    assert len(json.loads((bucket / "scans" / "umair" / "index.json").read_text())["bundles"]) == 1
    # republish replaces, never duplicates
    assert run(root, bucket, "publish", "7", "t2", "--owner", "umair").returncode == 0
    assert len(json.loads((bucket / "scans" / "umair" / "index.json").read_text())["bundles"]) == 1
    # unpublish: off the index, files archived (not deleted)
    assert run(root, bucket, "unpublish", "7", "t2", "--owner", "umair").returncode == 0
    assert json.loads((bucket / "scans" / "umair" / "index.json").read_text())["bundles"] == []
    assert not (bucket / "scans" / "umair" / "scan_007_abc_t2").exists() or \
        not any((bucket / "scans" / "umair" / "scan_007_abc_t2").iterdir())
    assert list((bucket / "archive" / "scans" / "umair" / "scan_007_abc_t2").rglob("walls.spz"))


def test_refuses_bad_owner_and_missing_bundle(tmp_path):
    root, bucket = tmp_path / "repo", tmp_path / "bucket"
    make_repo(root)
    assert run(root, bucket, "publish", "7", "t2", "--owner", "../x").returncode != 0
    assert run(root, bucket, "publish", "7", "nope", "--owner", "umair").returncode != 0
    assert run(root, bucket, "publish", "9", "t2", "--owner", "umair").returncode != 0
    assert not (bucket / "owners.json").exists()


def test_storage_cap(tmp_path):
    """D-077: nothing is uploaded when the bucket would pass the cap; the cap never goes above 10 GB."""
    root, bucket = tmp_path / "repo", tmp_path / "bucket"
    make_repo(root)
    env = {**os.environ, "BUILDSCAN_ROOT": str(root), "R2_MAX_BYTES": "1002000"}  # one ~1.1 KB bundle + indexes + 1 MB headroom fit, two do not
    cmd = [sys.executable, str(SCRIPT), "publish", "7", "t2", "--owner", "umair", "--target", f"dir:{bucket}"]
    assert subprocess.run(cmd, env=env, capture_output=True, text=True).returncode == 0
    # republishing the same run replaces its files, so it still fits
    assert subprocess.run(cmd, env=env, capture_output=True, text=True).returncode == 0
    # a second copy under another owner would not fit: refused, nothing written for it
    r = subprocess.run(cmd[:6] + ["tayyab", "--target", f"dir:{bucket}"], env=env, capture_output=True, text=True)
    assert r.returncode != 0 and "NOT published" in r.stderr
    assert not (bucket / "scans" / "tayyab").exists()
    # a cap above the free tier is clamped to 10 GB
    sys.path.insert(0, str(SCRIPT.parent))
    import publish_scan
    assert publish_scan.storage_cap({"R2_MAX_BYTES": "5e10"}) == 10_000_000_000
    assert publish_scan.storage_cap({}) == 9_500_000_000
