#!/usr/bin/env bash
# BuildScan3D: the whole v9 / v10 pipeline on Linux, capture -> 3DGS -> layout -> semantics -> mesh -> web bundle.
# Same commands as STATUS §5 (the Windows recipe), each stage in its own env (envs/linux/, scripts/setup_linux.sh).
#
#   scripts/run_full.sh <dataset_dir> <tag> [--from STAGE] [-- extra run_v8.py args]
#
#   screen -dmS r028 bash -c 'scripts/run_full.sh dataset/scan_x v9 -- --sfm_args "--retrieval 20" --init fmvs \
#       --planar 0.2 --blur 0.0222 --pgsr'          # detached; watch with `screen -r r028`
#
# Stages, in order (--from restarts at one; earlier outputs are reused):
#   select sfm export prior init train ply   run_v8.py (bs-system; nerfstudio parts in bs-ns via toolpaths.ns_cmd)
#   layout                                   layout.py                         (bs-ns)
#   sem2d                                    semantic2d.py, 2D masks           (semantic-env)
#   sem3d                                    semantic3d.py, labels on Gaussians (bs-ns)
#   verify                                   verify_fixtures.py, CLIP check    (semantic-env)
#   sem3d2                                   semantic3d.py again with verdicts (bs-ns)
#   mesh meshlabels web                      mesh.py, mesh_labels.py, export_web.py (bs-ns; Node for .spz)
# Every GPU_EVERY seconds (default 30) a status line shows GPU use, memory, temperature, power and, while training,
# the step and time left (training itself writes only to train.log); also saved to gpu.csv. GPU_EVERY=0 turns it off.
# A run that dies in training continues with: --from train (geo_splatfacto checkpoints every 2500 steps; see R-023
# for --resume). Output: <dataset>/work_<tag>_sfm/gs_<tag>/ (+ run_full.log, stages.tsv), web bundle in
# prototype/web-ui/public/scans/<capture>_<tag>/.
set -euo pipefail

[[ $# -ge 2 ]] || { sed -n 2,22p "$0"; exit 1; }
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
D="$(cd "$1" && pwd)"; TAG="$2"; shift 2
FROM=select
if [[ "${1:-}" == "--from" ]]; then FROM="$2"; shift 2; fi
[[ "${1:-}" == "--" ]] && shift
V8_ARGS=("$@")

export MAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-$HOME/micromamba}"
MM="${BUILDSCAN_MAMBA:-$HOME/.local/bin/micromamba}"
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
HERE=src/arcore3dgs
S="$D/work_${TAG}_sfm"; M="$S/gs_${TAG}"
NAME="$(basename "$D")_${TAG}"
WEB_OUT="prototype/web-ui/public/scans/$NAME"

ALL=(select sfm export prior init train ply layout sem2d sem3d verify sem3d2 mesh meshlabels web)
idx() { local i; for i in "${!ALL[@]}"; do [[ "${ALL[$i]}" == "$1" ]] && { echo "$i"; return; }; done; echo "unknown stage: $1" >&2; exit 1; }
FROM_I=$(idx "$FROM")

mkdir -p "$M"
LOG="$M/run_full.log"
exec > >(tee -a "$LOG") 2>&1
echo "=== run_full.sh $(date '+%F %T')  dataset=$D tag=$TAG from=$FROM  commit=$(git rev-parse --short HEAD)"
echo "    run_v8 args: ${V8_ARGS[*]:-(none)}"

ns()  { "$MM" run -n bs-ns python -u -W ignore "$@"; }
sem() { "$MM" run -n bs-system "$ROOT/semantic-env/bin/python" -u -W ignore "$@"; }

gpu_monitor() {   # one status line every GPU_EVERY s: GPU use / memory / temperature / power (+ training step)
  local every=${GPU_EVERY:-30} q u mu mt t p tr warn
  [[ -f "$M/gpu.csv" ]] || echo "time,util_pct,mem_used_mib,mem_total_mib,temp_c,power_w" > "$M/gpu.csv"
  while sleep "$every"; do
    q=$(nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw \
        --format=csv,noheader,nounits 2>/dev/null | head -1) || continue
    IFS=', ' read -r u mu mt t p <<< "$q"
    echo "$(date '+%F %T'),$u,$mu,$mt,$t,$p" >> "$M/gpu.csv"
    tr=""
    if [[ -n "$(find "$M/train.log" -mmin -1 2>/dev/null)" ]]; then   # training is writing its log
      tr=$(tail -c 4000 "$M/train.log" | tr '\r' '\n' | grep -aE '^[0-9]+ \([0-9.]+%\)' | tail -1 |
           awk '{printf " | train step %s %s, ETA %s %s %s %s", $1, $2, $5, $6, $7, $8}')
    fi
    warn=""; [[ "${t:-0}" =~ ^[0-9]+$ && $t -ge 85 ]] && warn="  << HOT"
    printf '  [gpu %s] %s%% | %s / %s MiB | %s C | %s W%s%s\n' "$(date '+%T')" "$u" "$mu" "$mt" "$t" "${p%.*}" "$tr" "$warn"
  done
}
if [[ "${GPU_EVERY:-30}" != 0 ]]; then
  gpu_monitor & MON=$!
  trap 'kill $MON 2>/dev/null' EXIT
fi

stage() {   # stage <name> <command...>: skipped before --from, timed, recorded in stages.tsv
  local name=$1; shift
  [[ $(idx "$name") -lt $FROM_I ]] && return 0
  echo; echo "=== [$(date '+%T')] $name"
  local t0=$SECONDS
  "$@"
  local dt=$((SECONDS - t0))
  awk -v d="$(date '+%F %T')" -v n="$name" -v t="$dt" 'BEGIN{printf "%s\t%s\t%.1f min\n", d, n, t/60}' >> "$M/stages.tsv"
  echo "=== [$(date '+%T')] $name done in $((dt / 60)) min $((dt % 60)) s"
}

# 1. capture -> 3DGS (run_v8.py runs its own stages and resumes with --from_stage)
if [[ $FROM_I -le $(idx ply) ]]; then
  echo; echo "=== [$(date '+%T')] run_v8.py: $FROM -> ply (its own stage times: $M/timing.json)"
  t0=$SECONDS
  "$MM" run -n bs-system python -u "$HERE/run_v8.py" --dataset "$D" --tag "$TAG" --from_stage "$FROM" "${V8_ARGS[@]}"
  awk -v d="$(date '+%F %T')" -v n="run_v8 ($FROM-ply)" -v t="$((SECONDS - t0))" 'BEGIN{printf "%s\t%s\t%.1f min\n", d, n, t/60}' >> "$M/stages.tsv"
  FROM_I=$(( $(idx ply) + 1 ))
fi

# 2. room layout, 3. semantics, 4. mesh + web bundle (STATUS §5)
stage layout     ns  "$HERE/layout.py" --ply "$M/splat.ply" --work "$S" --out "$M/layout"
stage sem2d      sem "$HERE/semantic2d.py" --work "$S" --every 2 --box_thr 0.28 --tiles 640 --out semantic2d_v10
stage sem3d      ns  "$HERE/semantic3d.py" --ply "$M/splat.ply" --work "$S" --layout "$M/layout/layout.json" --out "$M/semantic_v10" --sem2d semantic2d_v10
stage verify     sem "$HERE/verify_fixtures.py" --work "$S" --sem2d semantic2d_v10 --semantic "$M/semantic_v10"
stage sem3d2     ns  "$HERE/semantic3d.py" --ply "$M/splat.ply" --work "$S" --layout "$M/layout/layout.json" --out "$M/semantic_v10" --sem2d semantic2d_v10 --verdicts "$M/semantic_v10/verdicts.json"
DEPTH=(); [[ " ${V8_ARGS[*]} " == *" --pgsr "* ]] && DEPTH=(--depth unbiased)
stage mesh       ns  "$HERE/mesh.py" --ply "$M/splat.ply" --work "$S" --out "$M/mesh" "${DEPTH[@]}"
stage meshlabels ns  "$HERE/mesh_labels.py" --mesh "$M/mesh/mesh.ply" --ply "$M/splat.ply" --semantic "$M/semantic_v10" --layout "$M/layout/layout.json" --clean 0.01 --glb 400000
stage web        ns  "$HERE/export_web.py" --ply "$M/splat.ply" --semantic "$M/semantic_v10" --glb "$M/mesh/mesh_web.glb" --out "$WEB_OUT"

echo; echo "=== all done $(date '+%F %T'): model $M, web bundle $WEB_OUT"
cat "$M/stages.tsv"
