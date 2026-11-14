#!/usr/bin/env bash
# BuildScan3D: set up the processing environments on a Linux machine with an NVIDIA GPU (no sudo needed).
#
#   scripts/setup_linux.sh            install / complete everything (safe to run again: finished steps are skipped)
#   scripts/setup_linux.sh --check    only run the checks (GPU, COLMAP, gsplat, Open3D, models)
#
# Same versions as the Windows RTX 3070 PC (D-047), one script for every Linux machine and the Docker image (D-048).
# Every problem met while writing it is in docs/progress/TRAINING.md R-027.
#
# Needs beforehand: the NVIDIA driver (`nvidia-smi` works; 595 tested), curl, python3 (any version, only to unpack
# micromamba), ~25 GB of disk. Installs:
#   ~/.local/bin/micromamba, envs under ~/micromamba (or $MAMBA_ROOT_PREFIX):
#     bs-colmap  COLMAP 4.2.0 + CUDA            (envs/linux/colmap.yml)
#     bs-ns      nerfstudio 1.1.5, gsplat 1.4.0, torch 2.1.2+cu121, CUDA 12.1 + gcc 11, Node, ffmpeg
#                (envs/linux/nerfstudio.yml + requirements-nerfstudio.txt + bs-ns-activate.sh)
#     bs-system  Metric3D side: torch 2.1.2+cu121, timm, mmengine, xformers   (envs/linux/system.yml + requirements-system.txt)
#   semantic-env/  venv on bs-system: transformers 4.46.3 (requirements-semantic.txt)
#   tools/colmap_dl/vocab/vocab_tree_faiss_flickr100K_words32K.bin   (COLMAP 3.11.1 release)
#   prototype/web-ui/node_modules (npm ci from package-lock.json, for the .spz export)
# GPU architecture for gsplat's CUDA build: BUILDSCAN_CUDA_ARCH (default 8.9 = RTX 4000 Ada / 4090; 8.6 = RTX 30xx).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export MAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-$HOME/micromamba}"
MM="${BUILDSCAN_MAMBA:-$HOME/.local/bin/micromamba}"
TORCH_IDX="https://download.pytorch.org/whl/cu121"
VOCAB_URL="https://github.com/colmap/colmap/releases/download/3.11.1/vocab_tree_faiss_flickr100K_words32K.bin"
VOCAB_SIZE=9477067
ONLY_CHECK=0; [[ "${1:-}" == "--check" ]] && ONLY_CHECK=1

say() { printf '\n== %s\n' "$*"; }
run_in() { local env=$1; shift; "$MM" run -n "$env" "$@"; }   # always inside the ACTIVATED env (R-027 steps 13, 20)
have_env() { [[ -d "$MAMBA_ROOT_PREFIX/envs/$1/conda-meta" ]]; }

setup() {
  say "0. NVIDIA driver"
  command -v nvidia-smi >/dev/null || { echo "nvidia-smi not found: install the NVIDIA driver first"; exit 1; }
  nvidia-smi --query-gpu=name,driver_version,memory.total,compute_cap --format=csv,noheader

  say "1. micromamba"
  if [[ ! -x "$MM" ]]; then
    mkdir -p "$(dirname "$MM")"; tmp="$(mktemp -d)"
    curl -fsSL https://micro.mamba.pm/api/micromamba/linux-64/latest -o "$tmp/mm.tar.bz2"
    # python's tarfile instead of tar -j: bzip2 may be missing (R-027 step 2)
    python3 -c 'import sys,tarfile; t=tarfile.open(sys.argv[1],"r:bz2"); t.extractall(sys.argv[2], members=[t.getmember("bin/micromamba")], filter="data")' "$tmp/mm.tar.bz2" "$tmp"
    install -m 755 "$tmp/bin/micromamba" "$MM"; rm -rf "$tmp"
  fi
  "$MM" --version

  say "2. conda envs"
  for pair in colmap:bs-colmap nerfstudio:bs-ns system:bs-system; do
    yml="${pair%%:*}"; env="${pair##*:}"
    if have_env "$env"; then echo "$env exists, updating from $yml.yml"; "$MM" install -y -n "$env" -f "$ROOT/envs/linux/$yml.yml"
    else "$MM" create -y -f "$ROOT/envs/linux/$yml.yml"; fi
  done
  # if a package download stalls (R-027 step 6): stop, fetch the .conda with curl, check its sha256 from
  # `micromamba search --json`, put it in $MAMBA_ROOT_PREFIX/pkgs/ and run this script again.

  say "3. bs-ns activation script (CUDA paths for gsplat's JIT build)"
  mkdir -p "$MAMBA_ROOT_PREFIX/envs/bs-ns/etc/conda/activate.d"
  cp "$ROOT/envs/linux/bs-ns-activate.sh" "$MAMBA_ROOT_PREFIX/envs/bs-ns/etc/conda/activate.d/zz-buildscan.sh"

  say "4. pip: bs-ns"
  run_in bs-ns python -m pip install --progress-bar off torch==2.1.2+cu121 torchvision==0.16.2+cu121 --index-url "$TORCH_IDX"
  run_in bs-ns bash -c "cd '$ROOT' && python -m pip install --progress-bar off -r envs/linux/requirements-nerfstudio.txt --extra-index-url $TORCH_IDX"
  run_in bs-ns python -m pip check

  say "5. pip: bs-system"
  run_in bs-system bash -c "cd '$ROOT' && python -m pip install --progress-bar off -r requirements-system.txt --extra-index-url $TORCH_IDX"

  say "6. semantic-env (venv on bs-system, as on Windows)"
  [[ -x "$ROOT/semantic-env/bin/python" ]] || "$MAMBA_ROOT_PREFIX/envs/bs-system/bin/python" -m venv "$ROOT/semantic-env" --system-site-packages
  "$ROOT/semantic-env/bin/python" -m pip install --progress-bar off -r "$ROOT/requirements-semantic.txt"

  say "7. COLMAP vocabulary tree (retrieval, sfm_colmap.py --retrieval)"
  v="$ROOT/tools/colmap_dl/vocab/vocab_tree_faiss_flickr100K_words32K.bin"
  if [[ "$(stat -c %s "$v" 2>/dev/null || echo 0)" != "$VOCAB_SIZE" ]]; then
    mkdir -p "$(dirname "$v")"; curl -fsSL -o "$v" "$VOCAB_URL"
  fi
  [[ "$(stat -c %s "$v")" == "$VOCAB_SIZE" ]] && echo "ok ($VOCAB_SIZE bytes)"

  say "8. web viewer packages (Node, for to_spz.mjs)"
  run_in bs-ns bash -c "cd '$ROOT/prototype/web-ui' && npm ci --no-audit --no-fund"
}

check() {
  say "check: torch + GPU (bs-ns, bs-system, semantic-env)"
  for env in bs-ns bs-system; do
    run_in "$env" python -c "import torch; assert torch.cuda.is_available(); print('$env torch', torch.__version__, torch.cuda.get_device_name(0))"
  done
  "$ROOT/semantic-env/bin/python" -c "import torch, transformers; from transformers import is_torch_available; assert is_torch_available(); print('semantic-env transformers', transformers.__version__)"

  say "check: COLMAP"
  "$MAMBA_ROOT_PREFIX/envs/bs-colmap/bin/colmap" help | head -1

  say "check: gsplat (first run compiles its CUDA code, ~2 min, cached in ~/.cache/torch_extensions)"
  run_in bs-ns python - <<'EOF'
import time, torch
from gsplat import rasterization
n = 100_000; d = "cuda"; t = time.time()
img, _, _ = rasterization(torch.randn(n, 3, device=d) * 0.5 + torch.tensor([0, 0, 3.0], device=d),
                          torch.nn.functional.normalize(torch.randn(n, 4, device=d), dim=-1),
                          torch.rand(n, 3, device=d) * 0.02, torch.rand(n, device=d), torch.rand(n, 3, device=d),
                          torch.eye(4, device=d)[None],
                          torch.tensor([[1000.0, 0, 960], [0, 1000.0, 540], [0, 0, 1]], device=d)[None], 1920, 1080)
torch.cuda.synchronize(); print(f"gsplat ok, {tuple(img.shape)}, {time.time() - t:.0f} s")
EOF

  say "check: Open3D TSDF (must not be empty)"
  run_in bs-ns python - <<'EOF'
import numpy as np, open3d as o3d
K = o3d.camera.PinholeCameraIntrinsic(640, 480, 500.0, 500.0, 320, 240)
v = o3d.pipelines.integration.ScalableTSDFVolume(voxel_length=0.01, sdf_trunc=0.04,
                                                 color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8)
for x in (-0.1, 0.0, 0.1):
    e = np.eye(4); e[0, 3] = x
    v.integrate(o3d.geometry.RGBDImage.create_from_color_and_depth(
        o3d.geometry.Image(np.full((480, 640, 3), 128, np.uint8)), o3d.geometry.Image(np.full((480, 640), 2.0, np.float32)),
        depth_scale=1.0, depth_trunc=5.0, convert_rgb_to_intensity=False), K, e)
n = len(v.extract_triangle_mesh().triangles); assert n > 0, "empty TSDF mesh"; print("open3d", o3d.__version__, "ok,", n, "triangles")
EOF
  echo; echo "All checks passed. Model weights (Metric3D, Grounding DINO, SAM, CLIP) download on first use."
}

[[ $ONLY_CHECK == 1 ]] || setup
check
