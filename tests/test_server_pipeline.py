"""server/pipeline.py (local processing) and the RunPod command list in server/runpod_client.py.

These are consistency tests: the two copies of the pipeline must stay in sync with each other and with the
scripts they call. If someone renames or deletes a script, or changes one list but not the other, a test fails
here instead of a RunPod job failing an hour into a run."""
import os
import re

import pytest

import server.pipeline as pl
import server.runpod_client as rc

REPO = pl.PROJECT_ROOT


# ------------------------------------------------------------------ local pipeline
def test_local_pipeline_has_six_steps_in_order():
    cmds = pl._build_commands("/data/scan_1")
    assert [step.name for step, _ in cmds] == [s.name for s in pl.STEPS]
    assert len(cmds) == len(pl.STEPS) == 6
    assert [s.name.value for s in pl.STEPS] == ["fallback", "prepare", "sfm_colmap",
                                                "export_nerfstudio", "train", "export_splat"]


def test_every_step_has_a_label_and_a_positive_timeout():
    for step in pl.STEPS:
        assert step.label and step.timeout_sec > 0


def test_iterations_reach_the_training_command():
    cmds = pl._build_commands("/data/scan_1", iterations=1234)
    train = next(cmd for step, cmd in cmds if step.name == pl.StepName.TRAIN)
    assert train[train.index("--max-num-iterations") + 1] == "1234"


def test_default_iterations_is_30000():
    train = next(cmd for step, cmd in pl._build_commands("/d") if step.name == pl.StepName.TRAIN)
    assert train[train.index("--max-num-iterations") + 1] == "30000"


def test_commands_point_at_the_dataset_folder():
    for step, cmd in pl._build_commands("/data/scan_9")[:4]:
        assert any("/data/scan_9" in str(part) or "scan_9" in str(part) for part in cmd), step.name


def test_every_script_the_local_pipeline_runs_exists_in_the_repo():
    for step, cmd in pl._build_commands("/d"):
        for part in cmd:
            if str(part).endswith(".py") and os.path.normpath(REPO) in os.path.normpath(str(part)) \
                    and "nerfstudio-env" not in str(part):
                assert os.path.exists(part), f"{step.name}: {part} is missing"


# ------------------------------------------------------------------ job object
def test_job_to_dict_has_the_fields_the_app_reads():
    job = pl.Job(job_id="j1", dataset_dir="/d")
    d = job.to_dict()
    assert d["job_id"] == "j1" and d["status"] == "queued"
    assert d["total_steps"] == len(pl.STEPS) and d["progress_pct"] == 0 and d["elapsed_sec"] == 0
    assert d["recent_logs"] == []


def test_job_log_keeps_only_the_last_200_lines_and_strips_newlines():
    job = pl.Job(job_id="j", dataset_dir="/d")
    for i in range(250):
        job._append_log(f"line {i}\n")
    assert len(job.log_lines) == 200
    assert job.log_lines[0] == "line 50" and job.log_lines[-1] == "line 249"
    assert len(job.to_dict()["recent_logs"]) == 20


# ------------------------------------------------------------------ RunPod pipeline copy
def test_runpod_pipeline_matches_the_local_pipeline_step_for_step():
    assert len(rc.PIPELINE_COMMANDS) == len(pl.STEPS)
    for (name, _label, timeout, _cmd), step in zip(rc.PIPELINE_COMMANDS, pl.STEPS):
        assert timeout == step.timeout_sec, f"timeout differs for {name}"


def test_runpod_commands_format_with_dataset_and_iterations():
    for _name, _label, _timeout, template in rc.PIPELINE_COMMANDS:
        text = template.format(dataset="/workspace/scan_x", iters=777)        # an unknown placeholder would raise KeyError
        assert "{dataset}" not in text and "{iters}" not in text
        assert "/workspace/scan_x" in text or "{dataset}" not in template      # the dataset path was substituted
    train = next(t for n, _, _, t in rc.PIPELINE_COMMANDS if n == "train")
    assert "--max-num-iterations 777" in train.format(dataset="/d", iters=777)


@pytest.mark.parametrize("template", [t for *_, t in rc.PIPELINE_COMMANDS])
def test_scripts_called_on_the_pod_exist_in_the_repo(template):
    for script in re.findall(r"src/arcore3dgs/(\w+\.py)", template):
        assert os.path.exists(os.path.join(REPO, "src", "arcore3dgs", script)), script


def test_setup_script_installs_what_the_pipeline_needs():
    assert "colmap" in rc.SETUP_SCRIPT and "nerfstudio" in rc.SETUP_SCRIPT


# ---------------------------------------------------------------- BUILDSCAN_PIPELINE=v9 (scripts/run_full.sh)
def test_default_recipe_is_still_v3(monkeypatch):
    monkeypatch.delenv("BUILDSCAN_PIPELINE", raising=False)
    assert pl.pipeline_recipe() == "v3"
    monkeypatch.setenv("BUILDSCAN_PIPELINE", "v9")
    assert pl.pipeline_recipe() == "v9"


def test_v9_command_runs_run_full_with_the_default_recipe(monkeypatch):
    monkeypatch.delenv("BUILDSCAN_V9_ARGS", raising=False)
    cmd = pl.build_v9_command("/data/scan_7")
    assert cmd[1].endswith(os.path.join("scripts", "run_full.sh")) and os.path.exists(cmd[1])
    assert cmd[2:5] == ["/data/scan_7", pl.V9_TAG, "--"]
    assert cmd[5:7] == ["--sfm_args", "--retrieval 20"]          # one argument with a space, as run_v8 expects
    assert "--pgsr" in cmd


def test_v9_args_can_be_overridden(monkeypatch):
    monkeypatch.setenv("BUILDSCAN_V9_ARGS", "--init fmvs --init_args=--photometric")
    assert pl.build_v9_command("/d")[5:] == ["--init", "fmvs", "--init_args=--photometric"]


@pytest.mark.parametrize("line,stage", [
    ("=== [01:30:42] layout", "layout"),
    ("=== [01:31:00] layout done in 0 min 6 s", "layout"),
    ("== train: C:/x/python.exe geo_splatfacto.py", "train"),
    ("== select: python select_sharp.py", "select"),
    ("=== [01:30:42] run_v8.py: select -> ply", None),
    ("  [gpu 01:32:43] 11% | 1943 / 8192 MiB", None),
    ("=== run_full.sh 2026-11-14 01:30:42  dataset=x", None),
])
def test_v9_stage_lines_are_recognised(line, stage):
    assert pl.v9_stage_of(line) == stage


def test_v9_stages_match_run_full_sh():
    src = open(os.path.join(pl.PROJECT_ROOT, "scripts", "run_full.sh"), encoding="utf-8").read()
    assert "ALL=(" + " ".join(pl.V9_STAGES) + ")" in src
    assert set(pl.V9_LABELS) == set(pl.V9_STAGES)
