"""Where the external tools live: Windows (RTX 3070 PC) or Linux (micromamba envs, envs/linux/).

Windows keeps the old layout: tools/colmap_dl/colmap-4.2.0/COLMAP.bat and nerfstudio-env/Scripts/*.exe.
Linux uses the micromamba envs bs-colmap and bs-ns under ~/micromamba (D-047). Override either with
  BUILDSCAN_COLMAP   path to the colmap executable
  BUILDSCAN_NS_ENV   root of the nerfstudio env (the folder that holds bin/ or Scripts/)
  BUILDSCAN_MAMBA    micromamba executable (default ~/.local/bin/micromamba, else on PATH)
On Linux nerfstudio programs must run inside the ACTIVATED bs-ns env: its activation sets CUDA_HOME, the CUDA paths and
the compilers, without which gsplat's compiled CUDA module does not load (R-027). Use ns_cmd(), not ns_tool().
No heavy imports here: scripts import this before argparse.
"""
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
WINDOWS = os.name == "nt"
MAMBA = os.environ.get("MAMBA_ROOT_PREFIX", os.path.expanduser("~/micromamba"))


def colmap():
    """COLMAP 4.2 executable."""
    if os.environ.get("BUILDSCAN_COLMAP"):
        return os.environ["BUILDSCAN_COLMAP"]
    if WINDOWS:
        return os.path.join(ROOT, "tools", "colmap_dl", "colmap-4.2.0", "COLMAP.bat")
    env = os.path.join(MAMBA, "envs", "bs-colmap", "bin", "colmap")
    return env if os.path.exists(env) else (shutil.which("colmap") or env)


def ns_tool(name):
    """A program of the nerfstudio env, e.g. ns_tool("python") or ns_tool("ns-export")."""
    if WINDOWS:
        root = os.environ.get("BUILDSCAN_NS_ENV", os.path.join(ROOT, "nerfstudio-env"))
        return os.path.join(root, "Scripts", name + ".exe")
    root = os.environ.get("BUILDSCAN_NS_ENV", os.path.join(MAMBA, "envs", "bs-ns"))
    return os.path.join(root, "bin", name)


def ns_cmd(name):
    """Command list that runs a program of the nerfstudio env, e.g. ns_cmd("python") + ["script.py", ...].
    Windows: the program itself. Linux: `micromamba run -n bs-ns <name>` (activated env), unless BUILDSCAN_NS_ENV
    points at an env that is already set up (then the program path, as on Windows)."""
    if WINDOWS or os.environ.get("BUILDSCAN_NS_ENV"):
        return [ns_tool(name)]
    mamba = os.environ.get("BUILDSCAN_MAMBA") or (os.path.expanduser("~/.local/bin/micromamba")
                                                  if os.path.exists(os.path.expanduser("~/.local/bin/micromamba"))
                                                  else shutil.which("micromamba") or "micromamba")
    return [mamba, "run", "-r", MAMBA, "-n", "bs-ns", name]


def link_dir(target, link):
    """Directory link without copying: a junction on Windows, a symlink elsewhere."""
    if WINDOWS:
        import subprocess
        subprocess.run(["cmd", "/c", "mklink", "/J", link, target], check=True, capture_output=True)
    else:
        os.symlink(target, link, target_is_directory=True)


def unlink_dir(link):
    """Remove a link made by link_dir (never the folder it points to)."""
    if os.path.islink(link):
        os.unlink(link)
    elif os.path.exists(link):
        os.rmdir(link)  # a Windows junction; fails safely on a real, non-empty folder
