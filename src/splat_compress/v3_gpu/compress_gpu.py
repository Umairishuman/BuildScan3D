"""v3 compression engine CLI.

  python -m splat_compress.v3_gpu.compress_gpu in.ply out_dir [--config my.json] [--set prune.min_opacity=0.02 ...] [--device cuda]
  python -m splat_compress.v3_gpu.compress_gpu --print-config              # the effective config, nothing is run

With defaults this reproduces v1 (prune + SH degree 1, PLY out). Run from the src/ folder. See PLAN.md.
"""
import argparse
import json

from .config import load_config


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", nargs="?")
    ap.add_argument("out_dir", nargs="?")
    ap.add_argument("--config", help="JSON file merged over config.default.json")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="override, e.g. prune.min_opacity=0.02")
    ap.add_argument("--device", help="shortcut for --set device=...")
    ap.add_argument("--print-config", action="store_true")
    a = ap.parse_args(argv)
    over = list(a.set) + ([f"device={a.device}"] if a.device else [])
    cfg = load_config(a.config, over)
    if a.print_config:
        print(json.dumps(cfg, indent=2))
        return 0
    if not (a.src and a.out_dir):
        ap.error("src and out_dir are required")
    from .pipeline import run
    rep, _ = run(cfg, a.src, a.out_dir)
    print(f"device {rep['device']}: splats {rep['input_splats']:,} -> {rep['output_splats']:,}")
    for s in rep["stages"]:
        print(f"  {s['stage']:10s} {s['seconds']:7.2f}s")
    for f, o in rep["outputs"].items():
        print(f"  {f:7s} {o['bytes'] / 1e6:8.1f} MB  ({o['smaller_percent']}% smaller than input)  {o['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
