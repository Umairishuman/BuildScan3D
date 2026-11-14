# Installed into $CONDA_PREFIX/etc/conda/activate.d/ of bs-ns (by scripts/setup_linux.sh). Runs on every activation,
# including `micromamba run -n bs-ns`. Lets torch 2.1.2's cpp_extension (gsplat's CUDA JIT build) find conda's CUDA 12.1:
# its headers are under targets/x86_64-linux/include and there is no lib64/ (R-027).
export CUDA_HOME="$CONDA_PREFIX"
export CPATH="$CONDA_PREFIX/targets/x86_64-linux/include${CPATH:+:$CPATH}"
export LIBRARY_PATH="$CONDA_PREFIX/lib:$CONDA_PREFIX/targets/x86_64-linux/lib${LIBRARY_PATH:+:$LIBRARY_PATH}"
# Ada (RTX 4000 Ada) = 8.9. Override before activating for another GPU (e.g. 8.6 for an RTX 3070, 8.9 for a 4090).
export TORCH_CUDA_ARCH_LIST="${BUILDSCAN_CUDA_ARCH:-8.9}"
