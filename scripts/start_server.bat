@echo off
REM Start the BuildScan 3D processing server
REM Loads .env for RUNPOD_API_KEY, then runs FastAPI on port 8000
cd /d %~dp0..

REM Load .env file
if exist .env (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        set "%%A=%%B"
    )
)

echo.
echo  BuildScan 3D Server
echo  ====================
if defined RUNPOD_API_KEY (
    echo  Mode: RunPod  (API key loaded)
) else (
    echo  Mode: Local   (no RUNPOD_API_KEY found)
)
echo  URL:  http://0.0.0.0:8000
echo  Docs: http://localhost:8000/docs
echo.

python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
