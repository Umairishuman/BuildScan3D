@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"
set PATH=%~dp0nerfstudio-env\Scripts;%PATH%
set CL=/Zc:preprocessor
set TORCH_CUDA_ARCH_LIST=8.6
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d %~dp0
ns-train splatfacto --data dataset/roomAttemptSadness/nerf --output-dir outputs --experiment-name roomAttemptSadness_fast --timestamp run2 --max-num-iterations 10000 --steps-per-save 2000 --vis tensorboard --viewer.quit-on-train-completion True --pipeline.model.random-init False --pipeline.model.stop-split-at 7000 --pipeline.model.camera-optimizer.mode SO3xR3 nerfstudio-data --auto-scale-poses False --center-method none --orientation-method up --downscale-factor 2 --load-3D-points True
