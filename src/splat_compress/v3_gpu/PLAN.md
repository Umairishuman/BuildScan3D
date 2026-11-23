# v3: GPU compression engine, plan

Status: **draft, code written 2026-11-23, not yet run on a GPU** (no GPU on the machine it was written on; the unit
tests run on CPU torch only). Owner: Zaid. Nothing here decides OD-1 (`.spz` or `.ksplat`); the delivery format is a
plug-in, chosen in the config.

## Why v3

v1 and v2 (`../v1_ply_prune_sh_ksplat`, `../v2_ksplat_high_fidelity`) are single-use scripts:
- compress.py is numpy on the CPU, with settings fixed in argparse defaults and no config file.
- The `.ksplat` step is a manual `node create-ksplat.js` call whose converter is not in the repo (COMPLETION_PLAN 5.2).
- Quality was measured by rendering in a software viewer, once, by hand (v2 README, "Not done yet"). There is no
  repeatable PSNR / SSIM measurement (COMPLETION_PLAN 5.4).
- Pruning only looks at opacity and scale; it never asks whether a splat matters for the rendered images.

v3 turns this into one repeatable, configurable run: input PLY, stages, outputs, size table and (on a GPU) quality table.

## Design rules

1. **No hard-coded values.** Every threshold, SH degree, codebook size, path, view count and output format comes from
   a JSON config (`config.default.json`) and can be overridden on the command line (`--set stages.prune.min_opacity=0.02`).
   The defaults are the v1 values, so v3 with defaults reproduces v1 numbers (check on GPU).
2. **Device is a parameter**: `device: auto` uses CUDA when present, else CPU. The stages are plain torch, so the
   same code runs on both; the tests run on CPU.
3. **Stages are small functions** `stage(splats, cfg) -> (splats, stats)` and are listed in the config in order, so a
   run can drop or reorder them.
4. **Every run writes `report.json`** (splat counts, bytes and time per stage, config used, git commit). Numbers come
   from that file only, never typed by hand (CLAUDE.md §2).
5. **Nothing decided for the team.** `.spz` vs `.ksplat`, default thresholds and the merge of the branch stay open
   decisions (OD-1, OD-4); this code gives the numbers to decide with.

## Stages

| # | Stage | What | GPU benefit | Status |
|---|---|---|---|---|
| 1 | `load` | PLY to tensors; infers SH degree from the `f_rest_*` columns | I/O only | written, CPU-tested |
| 2 | `prune` | drop by opacity, scale outliers (off by default), and an importance score (opacity x volume) quantile | vectorised over millions of splats | written, CPU-tested |
| 3 | `prune_render` | render-based importance: accumulate each splat's contribution over the training views with gsplat and drop the lowest | needs gsplat on CUDA | **not written** (needs the GPU to design against) |
| 4 | `sh_reduce` | cut SH to degree N, drop normals | cheap | written, CPU-tested |
| 5 | `vq_sh` | k-means codebook for the SH "rest" coefficients, index per splat | k-means on the GPU is the point of the whole stage | written, CPU-tested on small data; speed not measured |
| 6 | `write` | `ply` (dequantised, standard 3DGS PLY) always; then converters: `spz` (existing `src/arcore3dgs/to_spz.mjs`) and `ksplat` (node converter path from config) | no | `ply` written; converters written as wrappers, never run |
| 7 | `evaluate` | render original and compressed at the same views with gsplat, PSNR / SSIM, size, render time | the renderer needs CUDA | written, **never run** |

Honest caveat on stage 5: a VQ codebook only shrinks the delivered file if the container stores codebook + indices.
`ply`, `.spz` and `.ksplat` do not, so after `vq_sh` the PLY is dequantised and the saving comes only from what the
delivery format's own quantiser then does with fewer distinct values. The stage is therefore **experimental**: its
value is measured in step 3 of the test plan below, and it is off in the default config.

## Test plan for tomorrow (needs the lab GPU)

Setup first (not done, waiting for the SSH username and key install): `ssh gpu-lab`, `nvidia-smi`, check
`python -c "import torch, gsplat"` in the environment the pipeline uses (STATUS §6), copy or locate the R-030 scan and
its `frames.json`. Log it as a run in TRAINING.md before starting (CLAUDE.md §2).

1. `pytest tests/test_splat_compress_v3.py` on the GPU machine (the same tests, now with `device: cuda` too).
2. Reproduce v1: defaults on the R-030 `splat.ply` should give about 51.3 MB pruned PLY (v1 README). If not, v3 is wrong.
3. Run `vq_sh` with a few codebook sizes; record time on CPU vs GPU and PSNR / SSIM vs the original.
4. `evaluate` on 2 scans for the PLY, `.spz` and `.ksplat` outputs: this fills COMPLETION_PLAN 5.4 / E6.
5. Write the results in TRAINING.md (run ID), DECISIONS.md only after Zaid decides, then the stage-3 design.

## Open questions

- What did the teammate find wrong in the existing compression code? Not yet told; this plan is built from reading v1/v2.
- Where is the `.ksplat` converter (`create-ksplat.js`) to be installed from (GaussianSplats3D), and is it kept in the repo?
- Which held-out views does `evaluate` use? Default: the same every-10th split as `compare_models.py` (frames.json).
