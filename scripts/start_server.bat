@echo off
setlocal enabledelayedexpansion
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

if "!PROCESSING_MODE!"=="dry_run" (
    echo  Mode: Dry Run  ^(uploads saved, no processing^)
) else if defined RUNPOD_API_KEY (
    echo  Mode: RunPod  ^(API key loaded^)
) else (
    echo  Mode: Local   ^(no RUNPOD_API_KEY found^)
)

REM Get WiFi IP (skip virtual adapters like vEthernet, Bluetooth, Loopback)
set "LOCAL_IP="
set "IN_WIFI=0"
for /f "usebackq tokens=*" %%L in (`ipconfig`) do (
    set "LINE=%%L"
    echo !LINE! | findstr /I /C:"Wi-Fi" /C:"Wireless" >nul 2>&1 && set "IN_WIFI=1"
    echo !LINE! | findstr /I /C:"vEthernet" /C:"Bluetooth" /C:"Loopback" /C:"Local Area Connection" >nul 2>&1 && set "IN_WIFI=0"
    if "!IN_WIFI!"=="1" (
        echo !LINE! | findstr /C:"IPv4" >nul 2>&1 && (
            for /f "tokens=2 delims=:" %%I in ("!LINE!") do (
                set "LOCAL_IP=%%I"
                set "LOCAL_IP=!LOCAL_IP: =!"
            )
        )
    )
)

echo  Local: http://localhost:8000
echo  Docs:  http://localhost:8000/docs
echo.
if defined LOCAL_IP (
    echo  Phone: http://!LOCAL_IP!:8000
    echo         ^^^^ Set this as server URL in the app
) else (
    echo  Phone: Could not detect WiFi IP. Run 'ipconfig' and use your WiFi IPv4 address.
)
echo.

python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
