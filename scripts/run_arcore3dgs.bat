@echo off
REM Usage: run_arcore3dgs.bat <dataset_dir> [iterations]
REM   ARCore capture -> metric 3DGS (see docs/Problems_and_Solutions.md 4.11):
REM   prepare (sharp keyframes from the video, no depth) -> sfm_colmap (COLMAP SIFT + exhaustive matching +
REM   global mapper: poses AND lens distortion from the images; undistort; Sim3 to ARCore for metric scale +
REM   gravity; drop mis-registered frames) -> splatfacto at full resolution with per-image colour correction
REM   (bilateral grid), camera refinement and scale regularisation.
REM   Output: <dataset>\work_sfm\gs_sfm\splat.ply   (metric, ARCore world, +Y up)
REM   Needs: COLMAP 4.2 CUDA in tools\colmap_dl\ (see TODO.md), nerfstudio-env.
REM   Time on an RTX 3070 for ~600 keyframes: matching ~25 min, mapping ~6 min, training ~45 min.
setlocal
set DATA=%~1
if "%DATA%"=="" set DATA=dataset\newRoomAttemptSadness
set ITERS=%~2
if "%ITERS%"=="" set ITERS=30000
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set NS=nerfstudio-env\Scripts
cd /d %~dp0..
python src\arcore3dgs\fallback.py "%DATA%" || exit /b 1
if not exist "%DATA%\work\frames.json" python src\arcore3dgs\prepare.py --dataset "%DATA%" --out "%DATA%\work" --depth 0 || exit /b 1
python src\arcore3dgs\sfm_colmap.py --work "%DATA%\work" --out "%DATA%\work_sfm" || exit /b 1
%NS%\python.exe src\arcore3dgs\export_nerfstudio.py --work "%DATA%\work_sfm" --downscale 1 || exit /b 1
%NS%\ns-train.exe splatfacto --data "%DATA%\work_sfm" --output-dir "%DATA%\work_sfm\ns" --experiment-name gs --timestamp run ^
  --max-num-iterations %ITERS% --steps-per-save 5000 --vis tensorboard --viewer.quit-on-train-completion True ^
  --pipeline.model.random-init False ^
  --pipeline.model.use-bilateral-grid True --pipeline.model.use-scale-regularization True ^
  --pipeline.model.camera-optimizer.mode off ^
  --pipeline.datamanager.cache-images cpu --pipeline.datamanager.cache-images-type uint8 ^
  nerfstudio-data --auto-scale-poses False --center-method none --orientation-method none --downscale-factor 1 --load-3D-points True || exit /b 1
%NS%\ns-export.exe gaussian-splat --load-config "%DATA%\work_sfm\ns\gs\splatfacto\run\config.yml" --output-dir "%DATA%\work_sfm\gs_sfm" || exit /b 1
echo Done: %DATA%\work_sfm\gs_sfm\splat.ply   (view with: scripts\view_splat.bat %DATA%\work_sfm\gs_sfm\splat.ply)
