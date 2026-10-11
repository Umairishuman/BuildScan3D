@echo off
REM LEGACY (ARCore-pose pipeline, superseded 2026-10-11 by run_arcore3dgs.bat / sfm_colmap.py). Usage: run_arcore3dgs_legacy.bat <dataset_dir> [steps]
REM   ARCore capture -> metric 3DGS, PocketGS-style (see docs/Problems_and_Solutions.md 4.7, 4.10):
REM   fallback (IMU-bridged tracking gaps, ARCore frame-jump correction) -> prepare (keyframes + Metric3D)
REM   -> ba -> relocalize_pnp (re-align post-gap segments to the map) -> ba again (from relocalised poses)
REM   -> mvs (stereo + ARCore-anchored depth) -> pocket_prior (movement-gated keyframes +
REM   multi-view-consistent dense prior) -> short photometric training from the prior
REM   Output: <dataset>\work\gs_pocket\splat.ply   (~13 min training for a 5 min recording)
setlocal
set DATA=%~1
if "%DATA%"=="" set DATA=dataset\roomAttemptSadness2
set STEPS=%~2
if "%STEPS%"=="" set STEPS=8000
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set NS=nerfstudio-env\Scripts\python.exe -W ignore -u
cd /d %~dp0
python src\arcore3dgs\fallback.py "%DATA%" || exit /b 1
if not exist "%DATA%\work\frames.json" python src\arcore3dgs\prepare.py --dataset "%DATA%" --out "%DATA%\work" || exit /b 1
%NS% src\arcore3dgs\ba.py --work "%DATA%\work" || exit /b 1
%NS% src\arcore3dgs\relocalize_pnp.py --work "%DATA%\work" || exit /b 1
del /q "%DATA%\work\ba_tracks.npz" 2>nul
%NS% src\arcore3dgs\ba.py --work "%DATA%\work" || exit /b 1
%NS% src\arcore3dgs\mvs.py --work "%DATA%\work" || exit /b 1
%NS% src\arcore3dgs\pocket_prior.py --work "%DATA%\work" || exit /b 1
%NS% src\arcore3dgs\train.py --work "%DATA%\work" --out "%DATA%\work\gs_pocket" --frames_file frames_pocket.json --init_ply prior_points.ply --steps %STEPS% --fullres_frac 0.3 --sh_degree 3 || exit /b 1
echo Done: %DATA%\work\gs_pocket\splat.ply   (view with: view_splat.bat %DATA%\work\gs_pocket\splat.ply)
