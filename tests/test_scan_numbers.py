"""Scan numbers (server/scan_numbers.py, D-065): recordings in dataset/ are numbered 1, 2, 3 in arrival order."""
import importlib.util
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("scan_numbers", os.path.join(ROOT, "server", "scan_numbers.py"))
sn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sn)


def _old(root, *names):
    for n in names:
        (root / n).mkdir()
        time.sleep(0.02)


def test_old_folders_are_numbered_oldest_first(tmp_path):
    _old(tmp_path, "scan_bbb", "scan_aaa")
    assert sn.numbers(tmp_path) == [(1, "scan_bbb"), (2, "scan_aaa")]


def test_uploads_continue_the_sequence_with_the_number_in_the_name(tmp_path):
    _old(tmp_path, "scan_aaa", "scan_bbb", "scan_ccc")
    path, n, job = sn.new_scan_dir(tmp_path, "6de634cbb8b2")
    assert (n, path.name, job) == (4, "scan_004_6de634cbb8b2", "6de634cbb8b2") and path.is_dir()
    assert sn.new_scan_dir(tmp_path)[1] == 5


def test_numbers_do_not_change_when_an_old_folder_is_modified(tmp_path):
    _old(tmp_path, "scan_aaa", "scan_bbb")
    sn.new_scan_dir(tmp_path, "c" * 12)
    os.utime(tmp_path / "scan_aaa")                  # a processing run touches an old recording
    assert [n for n, _ in sn.numbers(tmp_path)] == [1, 2, 3]
    assert sn.resolve(tmp_path, "latest").endswith("scan_003_cccccccccccc")


def test_resolve_accepts_numbers_hash_names_and_latest(tmp_path):
    _old(tmp_path, "scan_aaa")
    sn.new_scan_dir(tmp_path, "d" * 12)
    assert sn.resolve(tmp_path, "1").endswith("scan_aaa")
    assert sn.resolve(tmp_path, "#2").endswith("scan_002_dddddddddddd")
    assert sn.resolve(tmp_path, "scan_aaa").endswith("scan_aaa")
    assert sn.resolve(tmp_path, "7") is None


def test_a_failed_upload_gives_its_number_back(tmp_path):
    path, n, _ = sn.new_scan_dir(tmp_path, "e" * 12)
    path.rmdir()
    sn.release(tmp_path, path.name)
    assert sn.new_scan_dir(tmp_path, "f" * 12)[1] == n


def test_job_id_of_old_and_new_names():
    assert sn.job_id_of("scan_004_6de634cbb8b2") == "6de634cbb8b2"
    assert sn.job_id_of("scan_056fe94d3399") == "056fe94d3399"
