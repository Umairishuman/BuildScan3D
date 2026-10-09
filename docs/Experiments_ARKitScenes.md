# Testing the trainer fix on a public room (ARKitScenes) with Kaggle

Branch: `feature/trainer-baseline-fix`. This note records what we tried while the capture phone and the 3070 PC were not available, what we measured, and what we still do not know.

## 1. Why this experiment

`diagnose.py` on our own rooms (see `Problems_and_Solutions.md` §4.4) suggested that the trainer underfits: colour-fit PSNR on its own training views was only 21–22 dB and the renders looked like cotton. My explanation was that the depth loss uses the fused TSDF mesh as its target and that this target is wrong in many places. I rewrote the trainer to test that explanation, but I had no GPU and no access to the room captures, so I needed another scene with ARCore-like data (metric camera poses from a phone/tablet tracker, handheld video).

The aim was to answer three questions on one scene, changing one thing at a time:

1. Does supervising depth with each frame's own stereo depth (`depth_mvs`, weighted by `mvs_mask`) instead of the fused-mesh render help?
2. Does a longer schedule help?
3. Do the weaker/fading depth and flatness losses help?

## 2. Data

- Scene: ARKitScenes (Apple), raw dataset, Training split, video id `47333462`. One furnished bedroom, handheld, about 60 s.
- Assets used: `vga_wide` (RGB, 640×480, about 30 fps, 1805 frames), `vga_wide_intrinsics` (per-frame intrinsics) and `lowres_wide.traj` (camera poses, 10 Hz, 596 rows).
- Licence: Apple's licence file allows personal, non-commercial use. The data is only used for this coursework, kept private (private Kaggle dataset) and not redistributed. Reference: Baruch et al., *ARKitScenes – A Diverse Real-World Dataset for 3D Indoor Scene Understanding Using Mobile RGB-D Data*, NeurIPS 2021 Datasets and Benchmarks.

### Converting it to the format the pipeline reads

Our pipeline expects what the Android app writes (`poses.csv` in ARCore layout plus a video). For this scene I converted the data with `src/arcore3dgs/arkit_to_scan.py` to a folder with `poses.csv`, a `frames/` image sequence and `pts.txt` (frame times). The conventions that mattered:

- `.traj` rows are `timestamp, axis-angle rotation, translation` and describe **world → camera** (Apple's own loader inverts them). I inverted them to camera → world.
- ARKitScenes cameras use OpenCV axes (x right, y down, z forward). `poses.csv` uses OpenGL axes (x right, y up, −z forward), so each pose is multiplied by `diag(1, −1, −1)` on the camera side.
- The world frame is Z-up. I estimated the up direction as the direction perpendicular to all camera x-axes (a handheld camera barely rolls), got (−0.009, 0.011, 1.0), and rotated the world so that up is +Y like ARCore.
- Poses are at 10 Hz and frames at 30 fps, so frame poses are interpolated (linear position, slerp rotation) by the existing `Capture.pose_at`.
- To let the pipeline read an image folder without an `.mp4`, `common.py` now reads frame times from `pts.txt`, and `prepare.py` reads frames through a small `open_frames()` wrapper.

**Check that the conversion is right.** I repeated the test from `Problems_and_Solutions.md` §1.1: correlate the image motion between frames (phase correlation) with the rotation between the two poses. Image vertical motion vs rotation about camera X: r = 0.97. Image horizontal motion vs rotation about camera Y: r = 0.75. Both are positive, which is the same pattern we found for ARCore data. So the pose timing and the axes are consistent.

## 3. Setup on Kaggle

- GPU: Tesla T4, 15.6 GB, PyTorch 2.11 (CUDA 12.8). Only one of the two T4s is used.
- Code and data were uploaded as a private Kaggle dataset (two zip files) and run from a notebook.
- First-time problems and fixes:
  - `gsplat 1.4.0` compiles its CUDA extension on first use; this took about 25 minutes with the notebook's default job count and worked.
  - Open3D 0.20 is the only version Kaggle's Python can install, and its TSDF fusion returns an empty mesh (0 triangles on a synthetic plane), the same bug we had on Windows. Open3D 0.19 gives 31,752 triangles on the same test. I ran only `align_fuse.py` in a separate Python 3.12 environment with Open3D 0.19.
  - Metric3D's `torch.hub` loader asks interactively whether to trust the repository, which crashes a non-interactive run. It now loads with `trust_repo=True`. It also needs the `mmengine` package.
  - `mvs.py` crashed on this scene because five keyframes have no neighbouring views, so no raw depth file exists for them, but other frames still list them as stereo sources. A missing file now counts as "no depth".
  - The stage runner skipped `mvs` after it crashed, because the stage creates its output folder before it finishes. I had to delete the half-finished folders by hand. A better completion marker is still to do.

## 4. Preprocessing results on this scene

| Stage | Result | Time |
|---|---|---|
| Keyframes + Metric3D depth | 207 keyframes from 1805 frames | 8.6 min |
| Bundle adjustment | reprojection error 1.12 px → 0.33 px (p90 0.89 px); trajectory length ratio 0.9962; pose correction median 29.8 mm, rotation 1.40° | 1.3 min |
| Multi-view stereo | measured pixels per frame: median 11% (p10 3%, p90 32%); Metric3D vs stereo 0.8% | 0.8 min |
| TSDF fusion | 187 frames trusted, 17 dropped, 587,704 triangles, extent 10.1 × 3.5 × 5.9 m, per-frame depth vs fused depth 1.3% (p90 3.8%) | 0.5 min |

The extent of the fused mesh is larger than the camera path, probably because some geometry far outside the room (seen through the window) got fused.

## 5. Trainer changes (`train.py`)

- Depth loss uses each frame's own depth map. Pixels that stereo measured have weight 1, filled-in pixels 0.1, and filled-in pixels of the 17 frames that fusion rejected have weight 0. `--depth_src fused` keeps the old target.
- The depth loss fades from 0.1 to 0 over the first 35% of training; the flatness loss fades from 0.1 to 0 by 70%. Before they were 0.5 → 0.05 and a constant 1.0.
- Initial opacity 0.1 (was 0.5), densification stops at 60% of the steps (was 70%), the 10 cm mesh-distance prune is off by default.
- Optional low-resolution first phase and full-resolution last phase (`--ds_start`, `--ds_end`, `--hires_frac`).
- Resumable checkpoints (`--ckpt_every`, `--resume`) and a time budget (`--max_minutes`), so a Kaggle session that stops can be continued.
- It prints the PSNR on training views, which is what exposed the underfitting in the first place.
- My first default was 40 × frames steps (at least 15,000). The results below show this overfits a small capture, so the default is back to `max(7000, 15 × training frames)`.

## 6. Results

21 of the 207 keyframes (every 10th) are held out as test views, the other 186 are used for training. All runs used 640×480 images.

- *Test PSNR / SSIM* are on the held-out frames, rendered as they are (no colour correction).
- *Colour-fit PSNR* comes from `diagnose.py`: the render is first fitted to the photo with a per-image affine colour transform, so exposure differences do not count.
- *Sharpness* is the Laplacian variance of the render divided by that of the photo (1 = as sharp as the photo).

| Run | Steps | Train PSNR (with learned exposure) | Test PSNR | Test SSIM | Colour-fit PSNR train / test | Sharpness (test) | Splats | Train time |
|---|---|---|---|---|---|---|---|---|
| smoke test | 1,500 | 23.81 | 21.75 | 0.835 | 24.55 / 23.97 | 0.18 | 0.46 M | 0.8 min |
| old settings, 3,500 steps | 3,500 | 26.22 | 22.32 | 0.854 | 26.80 / 25.46 | 0.38 | 1.44 M | 4.0 min |
| **baseline** (old settings) | 7,000 | 27.16 | 22.31 | 0.849 | 26.53 / 25.34 | 0.45 | 2.70 M | 13.7 min |
| old settings + per-frame MVS depth target | 7,000 | 27.70 | 22.23 | 0.848 | 26.48 / 25.11 | 0.46 | 2.67 M | 13.5 min |
| **new settings** | 7,000 | 27.54 | 22.44 | 0.849 | **27.57 / 26.11** | 0.44 | 2.22 M | 11.2 min |
| old settings, 15,000 steps | 15,000 | 28.08 | 20.83 | 0.800 | 25.02 / 23.55 | 0.47 | 4.48 M | 50.6 min |
| new settings, 15,000 steps | 15,000 | 28.52 | 20.58 | 0.790 | 25.12 / 23.42 | 0.44 | 4.47 M | 44.4 min |

I also made side-by-side images (real photo | baseline | new settings at 7,000 steps): one set for the held-out test views and one set of full-resolution detail crops of two training frames. They are not in the repository (image files are git-ignored here); I can provide them on request. What they show: in the test views the two models look nearly identical, and both smear the window and the dark TV glass. In the detail crop of the plain wall next to the poster, the baseline has dark smudged patches, which are floating splats; the new run does not have them.

## 7. What I take from this

1. **More steps overfit.** Going from 7,000 to 15,000 steps raises the training PSNR but lowers the held-out numbers by 1.5–2 dB colour-fit and 0.05 SSIM, and the model grows from 2.7 M to 4.5 M splats. This happened with both the old and the new loss settings, so it is the schedule, not the losses. With only 186 training frames, 15,000 steps is about 80 passes over the data.
2. **The depth target alone makes no measurable difference here.** Swapping the fused-mesh depth for the per-frame MVS depth changed the held-out colour-fit PSNR by 0.2 dB (25.34 → 25.11), which is about the noise between two runs.
3. **The new loss settings help a little at the right step count.** `new settings` at 7,000 steps is about 0.8 dB better than the baseline in held-out colour-fit PSNR (26.11 vs 25.34), with 18% fewer splats and a shorter run. In the images, the baseline has dark smudged patches on the plain wall in the second detail crop; the new run does not have them.
4. **On this scene the old trainer did not underfit.** Its colour-fit PSNR on its own training views is 26.5 dB, not the 21–22 dB we saw on our own rooms. So I could not reproduce the underfitting here, and this experiment says nothing yet about our own 1080p captures, where the problem was observed.

## 8. Limits of these numbers

- Each setting was run once, and frame order is not seeded, so differences below roughly 0.3 dB should be treated as noise. A repeat of the best run would measure that properly.
- The 21 test frames are every 10th keyframe, so each one is close to training frames from the same pass. This tests interpolation between neighbouring views, not far-away viewpoints.
- The images are only 640×480 and the room is one scene; our own captures are 1920×1080.
- Both models still smear the window (the building outside is lost) and render the dark TV glass as a smudge.
- No distance was measured, so this says nothing yet about measurement accuracy.

## 9. Next steps

- Run the same comparison on our own recording, or on the processed `work` folder from the 3070 PC, which is the scene where the underfitting was observed.
- Repeat `new settings` and `baseline` with different random seeds to put numbers on the noise.
- Replace the stage-completion check in the Kaggle runner with a proper marker file.
- The Kaggle notebook is not part of the repository; it was only a stop-gap while there was no local GPU.
- Free-space and planar priors from `TODO.md` are still the next ideas for the floaters and the window.
