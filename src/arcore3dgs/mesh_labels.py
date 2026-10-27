"""Carry the semantic labels of a 3DGS model (semantic3d.py) onto its mesh (mesh.py) -- CPU only.

Structure is labelled on the mesh surface itself (--layout): a vertex is floor / ceiling / wall_k when it lies
within a few cm of that plane (floor and ceiling refit on the mesh, tilt allowed) AND its normal agrees with
the plane's. Fixtures come from the accepted fixture Gaussians of semantic3d.py (vertex within --max_dist of
one). Everything else is "other" (furniture, clutter). Without --layout every vertex simply takes the label of
the nearest opaque Gaussian. A triangle's class is the majority of its 3 vertices. Writes:
  mesh_labels.npy        per-vertex class id (index into semantic.json "classes")
  mesh_semantic.ply      the mesh coloured by class
  mesh_areas.json        surface area per class (m2) -- the paintable wall area, measured on the surface
  mesh_web.glb (--glb)   decimated, vertex-coloured mesh for the web viewer (real colours) + mesh_web_semantic.glb
  mesh_clean.ply (--clean, needs --layout)  planar denoising of the room shell: every floor / ceiling / wall
                         vertex is pulled onto its surface's best-fit plane, fully within --clean (m) and fading
                         to nothing at 2.5x that, so ~1 cm fusion stripes go while door frames, skirting and
                         switch plates (2+ cm proud) keep their relief. Only the mesh copy changes, never the
                         splat model (snapping splats killed reflections and door frames, see 4.11-4.13).

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/mesh_labels.py --mesh <mesh.ply> --ply <splat.ply>
      --semantic <semantic dir> [--layout <layout.json>] [--glb 400000]
"""
import os, json, argparse, time
import numpy as np
import open3d as o3d
from plyfile import PlyData
from scipy.spatial import cKDTree

ap = argparse.ArgumentParser()
ap.add_argument("--mesh", required=True); ap.add_argument("--ply", required=True); ap.add_argument("--semantic", required=True)
ap.add_argument("--max_dist", type=float, default=0.05)
ap.add_argument("--layout", default="")
ap.add_argument("--clean", type=float, default=0.0, help="> 0 (m): also write mesh_clean.ply, see above (e.g. 0.01)")
ap.add_argument("--glb", type=int, default=0, help="> 0: also write decimated .glb meshes with about this many triangles")
args = ap.parse_args()
t0 = time.time()
sem = json.load(open(os.path.join(args.semantic, "semantic.json"))); names = sem["classes"]
lab = np.load(os.path.join(args.semantic, "labels.npy"))
v = PlyData.read(args.ply)["vertex"].data
P = np.stack([v["x"], v["y"], v["z"]], 1); op = 1 / (1 + np.exp(-v["opacity"]))
keep = op > 0.3
tree = cKDTree(P[keep]); L = lab[keep]
mesh = o3d.io.read_triangle_mesh(args.mesh)
V = np.asarray(mesh.vertices); T = np.asarray(mesh.triangles)
d, i = tree.query(V, k=1, workers=-1)
vl = np.where(d < args.max_dist, L[i], 0).astype(np.int16)
if args.layout:
    lay = json.load(open(args.layout)); mesh.compute_vertex_normals(); Nv = np.asarray(mesh.vertex_normals)
    idx = {nm: k for k, nm in enumerate(names)}
    def fit_level(sel):
        Q = V[sel]; A = np.c_[Q[:, 0], Q[:, 2], np.ones(len(Q))]; kp = np.ones(len(Q), bool)
        for _ in range(6):
            cf = np.linalg.lstsq(A[kp], Q[kp, 1], rcond=None)[0]; r = Q[:, 1] - A @ cf
            kp = np.abs(r) < max(0.01, 2.5 * np.median(np.abs(r[kp])))
        return cf
    hor = np.abs(Nv[:, 1]) > 0.8
    fl = fit_level(hor & (np.abs(V[:, 1] - lay["floor_y"]) < 0.1))
    dfl = V[:, 1] - (fl[0] * V[:, 0] + fl[1] * V[:, 2] + fl[2])
    st = np.zeros(len(V), np.int16); best = np.full(len(V), np.inf)
    m = hor & (np.abs(dfl) < 0.04); st[m] = idx["floor"]; best[m] = np.abs(dfl[m])
    if np.isfinite(lay["ceiling_y"]):
        ce = fit_level(hor & (np.abs(V[:, 1] - lay["ceiling_y"]) < 0.2))
        dce = V[:, 1] - (ce[0] * V[:, 0] + ce[1] * V[:, 2] + ce[2])
        m = hor & (np.abs(dce) < 0.06) & (np.abs(dce) < best); st[m] = idx["ceiling"]; best[m] = np.abs(dce[m])
    for k, w in enumerate(lay["walls"]):
        p0, p1 = np.array(w["p0"]), np.array(w["p1"]); dd = (p1 - p0) / np.linalg.norm(p1 - p0)
        n2 = np.array(w["normal"]) / np.linalg.norm(w["normal"]); rel = V[:, [0, 2]] - p0
        sd = rel @ n2; t = rel @ dd
        m = (np.abs(sd) < 0.05) & (t > -0.1) & (t < w["length"] + 0.1) & (np.abs(Nv[:, [0, 2]] @ n2) > 0.8) & (np.abs(sd) < best)
        st[m] = idx[f"wall_{k}"]; best[m] = np.abs(sd[m])
    fix = np.array([nm not in ("other", "floor", "ceiling") and not nm.startswith("wall_") for nm in names])
    vl = np.where(fix[vl] & (d < 0.03), vl, st).astype(np.int16)
np.save(os.path.join(os.path.dirname(args.mesh), "mesh_labels.npy"), vl)
web_src = mesh                                                # the .glb is made from the cleaned mesh if there is one
if args.clean > 0 and args.layout:
    Vc = V.copy(); moved = 0
    for k, nm in enumerate(names):
        if not (nm in ("floor", "ceiling") or nm.startswith("wall_")):
            continue
        sel = np.nonzero(st == k)[0]
        if len(sel) < 200:
            continue
        Q = V[sel]; kp = np.ones(len(Q), bool)
        for _ in range(5):                                    # robust plane of this surface
            c = Q[kp].mean(0); _, _, Vt_ = np.linalg.svd(Q[kp] - c, full_matrices=False); n = Vt_[2]
            r = (Q - c) @ n; kp = np.abs(r) < max(0.005, 3 * np.median(np.abs(r[kp])))
        w = np.clip((2.5 * args.clean - np.abs(r)) / (1.5 * args.clean), 0, 1)
        Vc[sel] -= (w * r)[:, None] * n; moved += int((w > 0).sum())
    cm = o3d.geometry.TriangleMesh(mesh); cm.vertices = o3d.utility.Vector3dVector(Vc); cm.compute_vertex_normals()
    o3d.io.write_triangle_mesh(os.path.join(os.path.dirname(args.mesh), "mesh_clean.ply"), cm)
    web_src = cm
    print(f"mesh_clean.ply: {moved} shell vertices pulled onto their planes (<= {args.clean * 100:.1f} cm fully, fading to {args.clean * 250:.1f} cm)")
# triangle class = majority of its vertices (ties -> first vertex)
tl = vl[T]; tri_lab = np.where((tl[:, 1] == tl[:, 2]) & (tl[:, 1] != tl[:, 0]), tl[:, 1], tl[:, 0])
a = V[T[:, 1]] - V[T[:, 0]]; b = V[T[:, 2]] - V[T[:, 0]]; area = 0.5 * np.linalg.norm(np.cross(a, b), axis=1)
areas = {names[k]: round(float(area[tri_lab == k].sum()), 2) for k in range(len(names)) if (tri_lab == k).any()}
json.dump(dict(mesh=os.path.abspath(args.mesh), total_area=round(float(area.sum()), 2), area_by_class=areas),
          open(os.path.join(os.path.dirname(args.mesh), "mesh_areas.json"), "w"), indent=1)
print("surface area by class (m2): " + ", ".join(f"{k} {a_}" for k, a_ in sorted(areas.items(), key=lambda x: -x[1])))
PAL = {"other": (150, 150, 150), "floor": (140, 90, 50), "ceiling": (235, 235, 235), "door": (40, 90, 255),
       "window": (0, 200, 255), "light switch": (255, 0, 200), "power socket": (255, 120, 0), "ceiling light": (255, 255, 0),
       "lamp": (255, 220, 120), "air conditioner": (0, 220, 120), "ceiling fan": (160, 80, 255)}
WALLC = [(120, 200, 120), (120, 160, 220), (220, 170, 120), (190, 120, 200), (120, 210, 210), (210, 210, 120)]
col = np.array([PAL.get(nm, WALLC[int(nm.split("_")[1]) % len(WALLC)] if nm.startswith("wall_") else (150, 150, 150))
                for nm in names], np.float64) / 255
sm = o3d.geometry.TriangleMesh(web_src)
sm.vertex_colors = o3d.utility.Vector3dVector(col[vl])
o3d.io.write_triangle_mesh(os.path.join(os.path.dirname(args.mesh), "mesh_semantic.ply"), sm)
if args.glb > 0:
    import trimesh
    for src, nm in ((web_src, "mesh_web.glb"), (sm, "mesh_web_semantic.glb")):
        dm = src.simplify_quadric_decimation(target_number_of_triangles=args.glb)
        tm = trimesh.Trimesh(np.asarray(dm.vertices), np.asarray(dm.triangles),
                             vertex_colors=(np.asarray(dm.vertex_colors) * 255).astype(np.uint8), process=False)
        tm.export(os.path.join(os.path.dirname(args.mesh), nm))
        print(f"{nm}: {len(dm.triangles)} triangles, {os.path.getsize(os.path.join(os.path.dirname(args.mesh), nm)) / 1e6:.1f} MB")
print(f"done in {time.time() - t0:.0f} s")
