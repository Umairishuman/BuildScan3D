"""Output writers. `ply` is always the reference output; `spz` and `ksplat` call the existing external converters
(node), with every path and parameter taken from the config. A requested format that cannot be produced raises."""
import os
import subprocess

from .splat_io import write_ply


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def _abs(path, root):
    return path if os.path.isabs(path) else os.path.join(root, path)


def write_ply_out(ply_path, out_dir, cfg, ctx):
    return ply_path


def write_spz(ply_path, out_dir, cfg, ctx):
    root = repo_root()
    c = cfg["spz"]
    out = os.path.join(out_dir, cfg["name"] + ".spz")
    script = _abs(c["script"], root)
    if not os.path.exists(script):
        raise FileNotFoundError(f"spz converter script not found: {script}")
    subprocess.run([c["node"], script, os.path.abspath(ply_path), os.path.abspath(out)],
                   cwd=_abs(c["cwd"], root), check=True)
    return out


def write_ksplat(ply_path, out_dir, cfg, ctx):
    c = cfg["ksplat"]
    if not c["converter"]:
        raise ValueError("ksplat requested but write.ksplat.converter is not set "
                         "(path to GaussianSplats3D util/create-ksplat.js; it is not in the repo)")
    conv = _abs(c["converter"], repo_root())
    if not os.path.exists(conv):
        raise FileNotFoundError(f"ksplat converter not found: {conv}")
    out = os.path.join(out_dir, cfg["name"] + ".ksplat")
    cmd = [c["node"], conv, os.path.abspath(ply_path), os.path.abspath(out), str(c["level"]),
           str(c["alpha_threshold"]), c["center"], str(c["block_size"]), str(c["bucket_size"]), str(c["sh_degree"])]
    subprocess.run(cmd, check=True)
    return out


FORMATS = {"ply": write_ply_out, "spz": write_spz, "ksplat": write_ksplat}


def write_all(splats, out_dir, cfg, ctx):
    unknown = [f for f in cfg["formats"] if f not in FORMATS]
    if unknown:
        raise ValueError(f"unknown output format(s) {unknown}; known: {sorted(FORMATS)}")
    os.makedirs(out_dir, exist_ok=True)
    ply_path = os.path.join(out_dir, cfg["name"] + ".ply")
    write_ply(splats, ply_path)           # every converter reads this file, so it is always written
    files = {"ply": ply_path}
    for fmt in cfg["formats"]:
        files[fmt] = FORMATS[fmt](ply_path, out_dir, cfg, ctx)
    return {f: dict(path=p, bytes=os.path.getsize(p)) for f, p in files.items()}
