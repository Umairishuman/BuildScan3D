@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"
set PATH=%~dp0..\nerfstudio-env\Scripts;%PATH%
set CL=/Zc:preprocessor
set TORCH_CUDA_ARCH_LIST=8.6
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d %~dp0..
set RUN=outputs\roomAttemptSadness\splatfacto\2026-10-05_run1
ns-eval --load-config %RUN%\config.yml --output-path %RUN%\eval.json
ns-export gaussian-splat --load-config %RUN%\config.yml --output-dir %RUN%\export
