"""Web-viewer assets for a labelled scan: class-group splat files, a compact semantics JSON, the mesh.

The splat model is split by semantic3d.py's per-Gaussian labels into groups the viewer can show / hide / tint
(Spark SplatMesh.visible / .recolor): floor, ceiling, walls, openings (doors, windows), electrical (switches,
sockets, lights, fans, AC) and other (furniture, clutter). Every group is written as a PLY and compressed to
.spz with Spark's own encoder (node, prototype/web-ui/node_modules), so the groups together are about the size
of the whole model. scan.json carries the room summary (floor area, ceiling height, walls with gross / net
areas) and the fixtures (class, position, height above floor, wall, size). The mesh .glb (mesh_labels.py
--glb) is copied as mesh.glb.

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/export_web.py --ply <splat.ply> --semantic <dir>
      --glb <mesh_web.glb> --out prototype/web-ui/public/scans/<name>
"""
import os, json, shutil, argparse, subprocess
import numpy as np
from plyfile import PlyData, PlyElement

ap = argparse.ArgumentParser()
ap.add_argument("--ply", required=True); ap.add_argument("--semantic", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--glb", default="")
args = ap.parse_args()
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WEB = os.path.join(ROOT, "prototype", "web-ui")
args.out = os.path.abspath(args.out); os.makedirs(args.out, exist_ok=True)
sem = json.load(open(os.path.join(args.semantic, "semantic.json"))); names = sem["classes"]
lab = np.load(os.path.join(args.semantic, "labels.npy"))
GROUPS = {"floor": ["floor"], "ceiling": ["ceiling"], "walls": [n for n in names if n.startswith("wall_")],
          "openings": ["door", "window"],
          "electrical": ["light switch", "power socket", "ceiling light", "lamp", "air conditioner", "ceiling fan"],
          "other": ["other"]}
COLORS = {"floor": "#8c5a32", "ceiling": "#ebebeb", "walls": "#78c878", "openings": "#285aff", "electrical": "#ff00c8", "other": "#969696"}
D = PlyData.read(args.ply)["vertex"].data
spz_js = os.path.join(os.path.dirname(os.path.abspath(__file__)), "to_spz.mjs")
groups = []
for g, members in GROUPS.items():
    ids = [names.index(m) for m in members if m in names]
    sel = np.isin(lab, ids)
    if not sel.any():
        continue
    tmp = os.path.join(args.out, f"_{g}.ply")
    PlyData([PlyElement.describe(D[sel], "vertex")]).write(tmp)
    subprocess.run(["node", spz_js, tmp, os.path.join(args.out, f"{g}.spz")], cwd=WEB, check=True)
    os.remove(tmp)
    groups.append(dict(key=g, url=f"{g}.spz", splats=int(sel.sum()), color=COLORS[g], classes=members))
    print(f"{g}: {int(sel.sum())} splats")
if args.glb:
    shutil.copy(args.glb, os.path.join(args.out, "mesh.glb"))
keep = ("id", "cls", "position", "height_above_floor", "wall", "along_wall", "width", "height", "views")
scan = dict(floor_area=sem["floor_area"], ceiling_height=sem["ceiling_height"],
            walls=[{k: w[k] for k in ("id", "length", "height", "gross_area", "openings_area", "net_area", "openings", "fixtures")}
                   for w in sem["walls"]],
            fixtures=[{k: f[k] for k in keep} for f in sem["fixtures"]],
            groups=groups, mesh="mesh.glb" if args.glb else None)
json.dump(scan, open(os.path.join(args.out, "scan.json"), "w"), indent=1)
total = sum(os.path.getsize(os.path.join(args.out, f)) for f in os.listdir(args.out)) / 1e6
print(f"-> {args.out} ({total:.1f} MB)")
