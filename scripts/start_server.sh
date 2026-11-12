#!/usr/bin/env bash
# BuildScan3D: start the phone-upload server (FastAPI, port 8000) on Linux. Linux twin of start_server.bat.
#
#   scripts/start_server.sh            start in the foreground
#   screen -dmS bs-server scripts/start_server.sh   start detached; reattach with `screen -r bs-server`
#
# Runs in its own small micromamba env `bs-server` (Python 3.10 + server/requirements.txt), not in the pipeline envs.
# Create it once:
#   micromamba create -n bs-server -c conda-forge python=3.10 pip
#   micromamba run -n bs-server pip install -r server/requirements.txt
# Loads .env if present (PROCESSING_MODE, RUNPOD_API_KEY, ...). Mode defaults to dry_run: uploads are saved to
# dataset/scan_<id>/ and nothing is processed.
# Also starts scripts/usb_link.sh, so a phone on a USB cable (USB debugging on) uploads over the cable.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export MAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-$HOME/micromamba}"
MM="${BUILDSCAN_MAMBA:-$HOME/.local/bin/micromamba}"
export PORT="${PORT:-8000}"

if [[ -f .env ]]; then set -a; source .env; set +a; fi
export PROCESSING_MODE="${PROCESSING_MODE:-dry_run}"

echo
echo " BuildScan 3D Server"
echo " ==================="
echo " Mode:  $PROCESSING_MODE"
echo " Local: http://localhost:$PORT   (docs: /docs)"
for ip in $(hostname -I); do
  [[ "$ip" == *:* ]] && continue
  echo " Phone: http://$ip:$PORT   (Wi-Fi)"
done
echo " Phone: http://127.0.0.1:$PORT   (USB cable, automatic when plugged in)"
echo

# USB link: keeps `adb reverse` set while a phone is plugged in (scripts/usb_link.sh); stopped with the server.
"$ROOT/scripts/usb_link.sh" "$PORT" &
USB_PID=$!
trap 'kill "$USB_PID" 2>/dev/null' EXIT

"$MM" run -n bs-server python -m uvicorn server.main:app --host 0.0.0.0 --port "$PORT"
