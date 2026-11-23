"""Run-time table (scripts/run_times.py, D-090): times come from the run's files and are checked against TRAINING.md."""
import importlib.util
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("run_times", os.path.join(ROOT, "scripts", "run_times.py"))
rt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt)

FOLDER = "dataset/scan_x/work_t1_sfm/gs_t1"
TIMING = {"select": 0.5, "sfm": 10.0, "export": 0.01, "prior": 2.0, "init": 5.0, "init_wait_cpu": 0.0, "train": 20.0,
          "ply": 0.49, "total": 38.0}
STAGES = ("2026-11-19 10:38:00\trun_v8 (select-ply)\t38.0 min\n2026-11-19 10:40:00\tlayout\t2.0 min\n"
          "2026-11-19 10:58:00\tsem2d\t18.0 min\n2026-11-19 10:58:06\tweb\t0.1 min\n")
LOG = ("I1 Global positioning done in 30.5 seconds\nI2 Iterative bundle adjustment done in 40.25 seconds\n"
       "I3 Iterative retriangulation and refinement done in 20 seconds\nI4 Reconstruction done in 95.75 seconds\n")
ENTRY = ("### R-101 · 2026-11-19 · test run\n- **Start → end:** 10:00 → 10:58 = 58.1 min (run_v8 38.0)\n"
         "- **Errors during the run:** none.\n- **Verdict:** kept.\n")
INDEX = "| R-101 | 2026-11-19 | test run | this PC | 58.1 min | ok | Kept |\n"


def make(tmp_path, timing=TIMING, stages=STAGES, entry=ENTRY, index=INDEX):
    d = tmp_path / FOLDER
    d.mkdir(parents=True)
    (d / "timing.json").write_text(json.dumps(timing))
    (d / "stages.tsv").write_text(stages)
    (d.parent / "global_mapper.log").write_text(LOG)
    (tmp_path / "TRAINING.md").write_text("## Run index\n\n" + index + "\n## Runs\n\n" + entry)
    row = {c: "" for c in rt.COLS}
    row.update(run="R-101", scan="scan_x", tag="t1", date="2026-11-19", state="done", folder=FOLDER)
    return row


def test_update_fills_times_from_the_files(tmp_path):
    row = make(tmp_path)
    rt.update([row], root=str(tmp_path))
    assert row["model_min"] == "38.0" and row["sfm"] == "10.00" and row["train"] == "20.00"
    assert row["start"] == "2026-11-19 10:00" and row["end"] == "2026-11-19 10:58"
    assert row["wall_min"] == "58.1"                       # 10:00:00 -> 10:58:06
    assert row["after_min"] == "20.1" and row["sem2d"] == "18.0" and row["web"] == "0.1"
    assert row["map_gp_s"] == "30.50" and row["map_total_s"] == "95.75"
    assert row["source"] == "files"


def test_map_log_of_another_tag_is_not_taken(tmp_path):
    row = make(tmp_path)
    other = tmp_path / "dataset/scan_x/work_t1_sfm/gs_retag"
    other.mkdir()
    (other / "stages.tsv").write_text("2026-11-19 11:00:00\tlayout\t1.0 min\n")
    row.update(tag="retag", folder="dataset/scan_x/work_t1_sfm/gs_retag")
    rt.update([row], root=str(tmp_path))
    assert row["layout"] == "1.0" and row["map_total_s"] == ""   # the SfM belongs to t1, not to this re-run


def test_hand_values_survive_update(tmp_path):
    row = make(tmp_path)
    row.update(note="kept by hand", who="Umair")
    rt.update([row], root=str(tmp_path))
    assert row["note"] == "kept by hand" and row["who"] == "Umair"


def run_check(tmp_path, row):
    rt.update([row], root=str(tmp_path))
    tr = rt.load_training([str(tmp_path / "TRAINING.md")])
    return rt.check([row], tr, root=str(tmp_path))


def test_clean_run_passes(tmp_path):
    fails, warns = run_check(tmp_path, make(tmp_path))
    assert fails == [] and warns == []


def test_timing_total_that_does_not_add_up_fails(tmp_path):
    fails, _ = run_check(tmp_path, make(tmp_path, timing=dict(TIMING, total=45.0),
                                       stages=STAGES.replace("38.0 min", "45.0 min")))
    assert any("add up" in f for f in fails)


def test_run_v8_line_must_match_timing(tmp_path):
    fails, _ = run_check(tmp_path, make(tmp_path, stages=STAGES.replace("38.0 min", "39.0 min")))
    assert any("stages.tsv run_v8" in f for f in fails)


def test_finished_run_left_open_in_training_fails(tmp_path):
    fails, _ = run_check(tmp_path, make(tmp_path, entry=ENTRY.replace("none.", "none so far.")))
    assert any("still open" in f for f in fails)
    fails, _ = run_check(tmp_path / "b", make(tmp_path / "b", index=INDEX.replace("58.1 min", "running")))
    assert any("index row still says" in f for f in fails)


def test_row_marked_running_whose_files_finished_fails(tmp_path):
    row = make(tmp_path)
    row["state"] = "running"
    fails, _ = run_check(tmp_path, row)
    assert any("close it" in f for f in fails)


def test_missing_rows_and_unrecorded_folders_are_reported(tmp_path):
    row = make(tmp_path)
    (tmp_path / "TRAINING.md").write_text((tmp_path / "TRAINING.md").read_text() + INDEX.replace("R-101", "R-102"))
    extra = tmp_path / "dataset/scan_x/work_t2_sfm/gs_t2"
    extra.mkdir(parents=True)
    (extra / "timing.json").write_text(json.dumps({"select": 0.5}))
    fails, warns = run_check(tmp_path, row)
    assert any("R-102: in TRAINING.md but no row" in f for f in fails)
    assert any("gs_t2: has timing files but no row" in w for w in warns)


def test_unquoted_measured_time_warns(tmp_path):
    _, warns = run_check(tmp_path, make(tmp_path, entry=ENTRY.replace("58.1", "57"), index=INDEX.replace("58.1", "57")))
    assert any("wall time 58.1" in w for w in warns)


def test_done_row_without_any_time_fails_unless_note_says_so(tmp_path):
    (tmp_path / "TRAINING.md").write_text(INDEX + ENTRY)
    row = {c: "" for c in rt.COLS}
    row.update(run="R-101", state="done")
    tr = rt.load_training([str(tmp_path / "TRAINING.md")])
    assert any("no time at all" in f for f in rt.check([row], tr, root=str(tmp_path))[0])
    row["note"] = "time not recorded"
    assert not any("no time at all" in f for f in rt.check([row], tr, root=str(tmp_path))[0])


def test_tsv_round_trip(tmp_path):
    row = make(tmp_path)
    rt.update([row], root=str(tmp_path))
    p = str(tmp_path / "runs.tsv")
    rt.write_rows([row], p)
    assert rt.read_rows(p) == [row]
