@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"
set PATH=%CUDA_PATH%\bin;%~dp0..\nerfstudio-env\Scripts;%PATH%
set CL=/Zc:preprocessor
set TORCH_CUDA_ARCH_LIST=8.6
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d %~dp0..
ns-train splatfacto --data dataset/roomAttemptSadness/nerf --output-dir outputs --experiment-name roomAttemptSadness --max-num-iterations 30000 --steps-per-save 1000 --timestamp 2026-10-05_run1 --vis tensorboard --viewer.quit-on-train-completion True --pipeline.model.random-init False nerfstudio-data --auto-scale-poses False --center-method none --orientation-method none --downscale-factor 2 --load-3D-points True
