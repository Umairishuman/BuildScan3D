#!/usr/bin/env bash
# BuildScan3D: keep the phone's USB link to the upload server alive.
#
#   scripts/usb_link.sh [port]        (start_server.sh runs this in the background; port defaults to 8000)
#
# With the phone on a USB cable (USB debugging on), `adb reverse tcp:<port> tcp:<port>` makes the phone's own
# http://127.0.0.1:<port> reach this PC's server through the cable: no Wi-Fi, no IP address, no firewall. The app
# tries that address first (ServerLink.java), so a plugged-in phone uploads over the cable without any setting.
# The reverse rule is lost when the cable is pulled or adb restarts, so this loop re-applies it every few seconds
# and prints a line only when something changes.
#
# adb: from PATH, ~/.local/bin/adb, or ~/Android/Sdk/platform-tools/adb. Without adb this prints how to get it and
# exits; the server keeps running over Wi-Fi.
set -uo pipefail

PORT="${1:-${PORT:-8000}}"
ADB="$(command -v adb || true)"
for c in "$HOME/.local/bin/adb" "$HOME/Android/Sdk/platform-tools/adb"; do
  [[ -z "$ADB" && -x "$c" ]] && ADB="$c"
done

say() { echo "$(date +%H:%M:%S) USB  $*"; }

if [[ -z "$ADB" ]]; then
  say "adb not found, USB uploads are off (Wi-Fi still works). Install it once, see docs/PROCESSING_GUIDE.md (Upload over a USB cable)."
  exit 0
fi

say "watching for a phone on the USB cable (adb: $ADB, port $PORT)"
declare -A last=()
while true; do
  declare -A now=()
  while read -r serial state _; do
    [[ -z "$serial" || "$serial" == "List" || "$serial" == "*" ]] && continue
    now[$serial]="$state"
    if [[ "$state" == "device" ]]; then
      if ! "$ADB" -s "$serial" reverse --list 2>/dev/null | grep -q "tcp:$PORT tcp:$PORT"; then
        if "$ADB" -s "$serial" reverse "tcp:$PORT" "tcp:$PORT" >/dev/null 2>&1; then
          state="linked"
        else
          state="reverse-failed"
        fi
      else
        state="linked"
      fi
      now[$serial]="$state"
    fi
    if [[ "${last[$serial]:-}" != "${now[$serial]}" ]]; then
      case "${now[$serial]}" in
        linked)         say "phone $serial connected: the app uploads over the cable (http://127.0.0.1:$PORT on the phone)" ;;
        unauthorized)   say "phone $serial: tap 'Allow' on the USB debugging prompt on the phone" ;;
        no*permissions*|no) say "phone $serial: no permission to use it (udev rule missing), see docs/PROCESSING_GUIDE.md (Upload over a USB cable)" ;;
        reverse-failed) say "phone $serial: adb reverse failed, unplug and plug the cable in again" ;;
        offline)        say "phone $serial is offline: unplug and plug the cable in again" ;;
        *)              say "phone $serial: ${now[$serial]}" ;;
      esac
    fi
  done < <("$ADB" devices 2>/dev/null)
  for serial in "${!last[@]}"; do
    [[ -z "${now[$serial]:-}" ]] && say "phone $serial unplugged: uploads fall back to Wi-Fi"
  done
  last=()
  for serial in "${!now[@]}"; do last[$serial]="${now[$serial]}"; done
  unset now
  sleep 3
done
