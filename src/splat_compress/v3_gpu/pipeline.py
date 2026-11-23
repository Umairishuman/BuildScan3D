"""Run the configured stages on one PLY and write outputs + report.json."""
import json
import os
import subprocess
import time

import torch

from .splat_io import raw_bytes, read_ply, resolve_device, sh_degree_of
from .stages import MUST_BE_LAST, STAGES
from .writers import write_all


def _sync(dev):
    if dev.type == "cuda":
        torch.cuda.synchronize()


def _git_commit():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=os.path.dirname(os.path.abspath(__file__))).stdout.strip() or None
    except OSError:
        return None


def validate(cfg):
    names = cfg["pipeline"]
    bad = [n for n in names if n not in STAGES]
    if bad:
        raise ValueError(f"unknown stage(s) {bad}; known: {sorted(STAGES)}")
    for i, n in enumerate(names):
        if n in MUST_BE_LAST and i != len(names) - 1:
            raise ValueError(f"stage '{n}' must be the last stage (it stores per-splat indices)")


def run(cfg, src, out_dir):
    validate(cfg)
    dev = resolve_device(cfg["device"])
    ctx = dict(device=dev, seed=cfg["seed"], cfg=cfg)
    t0 = time.perf_counter()
    splats = read_ply(src, dev)
    _sync(dev)
    input_bytes = os.path.getsize(src)
    report = dict(input=os.path.abspath(src), device=str(dev), git_commit=_git_commit(), config=cfg,
                  input_file_bytes=input_bytes, input_splats=len(splats["xyz"]), input_sh_degree=sh_degree_of(splats),
                  load_seconds=round(time.perf_counter() - t0, 3), stages=[])
    for name in cfg["pipeline"]:
        t = time.perf_counter()
        splats, stats = STAGES[name](splats, cfg[name], ctx)
        _sync(dev)
        stats.update(stage=name, seconds=round(time.perf_counter() - t, 3), raw_bytes_after=raw_bytes(splats))
        report["stages"].append(stats)
    t = time.perf_counter()
    report["outputs"] = write_all(splats, out_dir, cfg["write"], ctx)
    report["write_seconds"] = round(time.perf_counter() - t, 3)
    for o in report["outputs"].values():
        o["smaller_percent"] = round(100 * (1 - o["bytes"] / input_bytes), 1)
    report["output_splats"] = len(splats["xyz"])
    with open(os.path.join(out_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
    return report, splats
