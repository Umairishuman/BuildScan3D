@echo off
REM BuildScan 3D — Job Manager (interactive menu)
cd /d %~dp0..
python scripts\jobs.py %*
