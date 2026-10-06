@echo off
REM Usage: run_arcore3dgs.bat <dataset_dir> [steps]
REM   ARCore capture -> metric 3DGS:
REM   prepare (keyframes + Metric3D) -> ba (bundle adjustment on ARCore poses) -> mvs (multi-view depth)
REM   -> align_fuse (TSDF fusion) -> train (depth-supervised gsplat). Output: <dataset>\work\gs\splat.ply
setlocal
set DATA=%~1
if "%DATA%"=="" set DATA=dataset\roomAttemptSadness
set STEPS=%~2
if "%STEPS%"=="" set STEPS=7000
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set NS=nerfstudio-env\Scripts\python.exe -W ignore -u
cd /d %~dp0
if not exist "%DATA%\work\frames.json" python src\arcore3dgs\prepare.py --dataset "%DATA%" --out "%DATA%\work" || exit /b 1
%NS% src\arcore3dgs\ba.py --work "%DATA%\work" || exit /b 1
%NS% src\arcore3dgs\mvs.py --work "%DATA%\work" || exit /b 1
%NS% src\arcore3dgs\align_fuse.py --work "%DATA%\work" --depth_dir depth_mvs || exit /b 1
%NS% src\arcore3dgs\train.py --work "%DATA%\work" --steps %STEPS% || exit /b 1
