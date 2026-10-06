# BuildScan3D — To Do

Status as of 2026-10-06. Pipeline lives in `src/arcore3dgs/`:
`prepare.py → ba.py → mvs.py → align_fuse.py --depth_dir depth_mvs → train.py`
(one command: `run_arcore3dgs.bat <dataset_dir>`, view with `view_splat.bat`, evaluate with `compare.py`).

## Now — finish the current capture (roomAttemptSadness)

- [ ] **Train v3 on the cleaned two-pass fusion** (paused to free the PC). Close the viewer first; 8 GB VRAM overflows otherwise.
      `nerfstudio-env\Scripts\python.exe -W ignore -u src/arcore3dgs/train.py --work dataset/roomAttemptSadness/work --out dataset/roomAttemptSadness/work/gs_v3 --steps 7000`
- [ ] Check that the floating curtain/cupboard copies above the bed are gone (anti-aliasing + 10 cm prune are new and untested).
- [ ] Run `compare.py` on v1 / v2 / v3, then point `view_splat.bat` at `gs_v3`.
- [ ] Commit `src/arcore3dgs/`, the app changes (`CaptureLogger.java`) and the `.bat` launchers. Nothing is committed yet.

## Next — new capture with the updated app

- [ ] Install the updated app on the phone and test a short recording: confirm `tracking.csv`, `points.csv` (with ids/confidence), `depth/` and `meta.json` are written.
- [ ] Record one room using the capture protocol:
  - [ ] ceiling and floor sweeps
  - [ ] every wall at two heights (chest and knee)
  - [ ] slow movement (about half the speed of roomAttemptSadness)
  - [ ] close passes (30–50 cm) over anything that must look sharp up close
  - [ ] lock exposure if possible (add to app)
- [ ] Add ARCore raw depth to the pipeline as a third depth source next to MVS and Metric3D. It is metric depth for plain walls, where MVS fails.
- [ ] Full-quality run on the new capture: full resolution, 15–30k steps.

## Evaluation (thesis numbers)

- [ ] Tape-measure 10–15 references in the new room: wall lengths, room height, door width/height, desk, bed.
- [ ] Script: compare model measurements against tape measurements → mean / max dimensional error (cm).
- [ ] Report alongside: reprojection error before/after BA, MVS coverage, colour-fit PSNR/SSIM, free-space violation ratio.

## Novelty (after the optimisations above)

- [ ] **Certified measurements (headline):** every measurement comes with an error bound (e.g. 3.42 m ± 1.1 cm), built from BA pose uncertainty, measured-vs-predicted depth (`mvs_mask`) and multi-view agreement. Validate the bounds against tape-measure error.
- [ ] **Planar / right-angle priors → as-built floor plan:**
  - detect walls, floor and ceiling as planes;
  - snap Gaussians onto them and enforce right angles between near-perpendicular walls;
  - export room dimensions and a floor plan.
- [ ] **Free-space-aware training:** a loss that penalises Gaussians in space that cameras saw through (turns `consistency.py` into a training term).

## Android app

- [ ] **Live IQA + coverage guidance:** on-device image quality assessment while recording, which tells the user live:
  - which sections are left to record or need further scanning (surfaces seen from too few viewpoints or angles, ceiling or floor missing, holes in ARCore depth coverage);
  - when frames are too blurry, too dark or overexposed, or the camera is moving too fast;
  - when tracking is degraded or lost (from `tracking.csv` state and failure reason).

  Show this as an overlay or heatmap on the camera view, so missed areas are fixed during capture instead of after processing.
- [ ] Lock exposure / white balance during recording (cuts the per-image colour drift that training compensates for).

## Known environment notes

- gsplat CUDA extension is prebuilt and loaded via `nerfstudio-env/Lib/site-packages/gsplat/csrc.py`. That file explains how to refresh it after a gsplat, torch or CUDA upgrade.
- Open3D 0.20 (system Python) has broken TSDF fusion. Run fusion with `nerfstudio-env` (Open3D 0.19).
- Steam uses port 8080, so the viewer runs on **7010**.
