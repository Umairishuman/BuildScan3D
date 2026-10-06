@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"
set PATH=%~dp0nerfstudio-env\Scripts;%PATH%
set CL=/Zc:preprocessor
set TORCH_CUDA_ARCH_LIST=8.6
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d %~dp0
ns-viewer --load-config outputs\roomAttemptSadness_fast\splatfacto\run2\config.yml
