@echo off
REM Usage: view_splat.bat [path\to\splat.ply]   then open http://localhost:7010
set PLY=%~1
if "%PLY%"=="" set PLY=saved_models\2026-10-12_sharp_mvs_v6\newRoomAttemptSadness\splat.ply
cd /d %~dp0
nerfstudio-env\Scripts\python.exe -W ignore src\arcore3dgs\view.py --ply "%PLY%"
