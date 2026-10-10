@echo off
REM Usage: view_splat.bat [path\to\splat.ply]   then open http://localhost:7010
set PLY=%~1
if "%PLY%"=="" set PLY=dataset\roomAttemptSadness2\work\gs_pocket8k\splat.ply
cd /d %~dp0
nerfstudio-env\Scripts\python.exe -W ignore src\arcore3dgs\view.py --ply "%PLY%"
