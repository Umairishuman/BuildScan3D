"""Triangle mesh from a 3DGS model: TSDF fusion of rendered depth (the mesh extraction of PGSR / 2DGS / GOF).

Every --every-th training view is rendered (colour + depth + alpha) at --scale of full resolution and fused
into a TSDF volume (Open3D 0.19 -- the system Python's Open3D 0.20 TSDF returns empty meshes on this machine,
so run this with nerfstudio-env); marching cubes gives the mesh, small disconnected pieces (floaters) are
removed. Depth:
  expected   alpha-blended depth (any 3DGS model; fuzzy surfaces give bumpy, thick walls)
  unbiased   PGSR's plane depth: every Gaussian is treated as a flat disc (normal = its shortest axis); the
             normal and the camera-to-plane distance are alpha-blended and the depth is the ray / plane
             intersection, which lies ON the surface (meant for models trained with --pgsr)
Evaluation (--layout): flatness of the room shell -- for the floor, the ceiling and every wall of layout.json,
the mesh vertices on it (near the plane, normal agreeing) are fitted with their own best plane; reported are
the median deviation and the share of vertices within 1 cm of it (furniture in front of a wall has the wrong
normal / distance and is left out). Plus renders of the mesh (colour and shaded geometry) next to the splat
render from training and room-centre views. --eval_only re-scores an existing <out>/mesh.ply on the CPU.

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/mesh.py --ply <splat.ply> --work <work_sfm> --out <dir>
      [--depth unbiased] [--layout <layout.json>]
"""
import os, json, argparse, time
import numpy as np, cv2, torch, torch.nn.functional as F
import open3d as o3d
from plyfile import PlyData
from gsplat import rasterization

ap = argparse.ArgumentParser()
ap.add_argument("--ply", required=True); ap.add_argument("--work", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--depth", default="expected", choices=["expected", "unbiased"])
ap.add_argument("--every", type=int, default=2); ap.add_argument("--scale", type=float, default=0.5)
ap.add_argument("--voxel", type=float, default=0.015); ap.add_argument("--trunc", type=float, default=0.06)
ap.add_argument("--max_depth", type=float, default=6.0); ap.add_argument("--min_alpha", type=float, default=0.8)
ap.add_argument("--min_piece", type=float, default=0.002, help="drop connected pieces with fewer triangles than this fraction")
ap.add_argument("--layout", default="")
ap.add_argument("--eval_only", action="store_true", help="only re-score <out>/mesh.ply (CPU, no renders)")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)


def shell_flatness(V, Nv, lay):
    """per room-shell plane: median |deviation| (cm) and % of its vertices within 1 cm of their own best plane"""
    out = {}
    def stats(Q):
        if len(Q) < 200:
            return None
        c = Q.mean(0); kp = np.ones(len(Q), bool)
        for _ in range(5):                                    # robust plane fit
            c = Q[kp].mean(0); _, _, Vt = np.linalg.svd(Q[kp] - c, full_matrices=False); n = Vt[2]
            r = np.abs((Q - c) @ n); kp = r < max(0.01, 3 * np.median(r[kp]))
        r = r[r < 0.10]
        return dict(median_cm=round(float(np.median(r)) * 100, 2), within_1cm=round(float((r < 0.01).mean()) * 100, 1), vertices=int(len(r)))
    hor = np.abs(Nv[:, 1]) > 0.8
    out["floor"] = stats(V[hor & (np.abs(V[:, 1] - lay["floor_y"]) < 0.10)])
    if np.isfinite(lay["ceiling_y"]):
        out["ceiling"] = stats(V[hor & (np.abs(V[:, 1] - lay["ceiling_y"]) < 0.20)])
    for k, w in enumerate(lay["walls"]):
        p0, p1 = np.array(w["p0"]), np.array(w["p1"]); dd = (p1 - p0) / np.linalg.norm(p1 - p0)
        n2 = np.array(w["normal"]) / np.linalg.norm(w["normal"]); rel = V[:, [0, 2]] - p0; t = rel @ dd
        m = (np.abs(rel @ n2) < 0.10) & (t > 0.1) & (t < w["length"] - 0.1) & (np.abs(Nv[:, [0, 2]] @ n2) > 0.8) &             (V[:, 1] > lay["floor_y"] + 0.15)
        out[f"wall_{k}"] = stats(V[m])
    return out


if args.eval_only:
    mesh = o3d.io.read_triangle_mesh(os.path.join(args.out, "mesh.ply")); mesh.compute_vertex_normals()
    fl = shell_flatness(np.asarray(mesh.vertices), np.asarray(mesh.vertex_normals), json.load(open(args.layout)))
    rp = os.path.join(args.out, "mesh_report.json"); rep = json.load(open(rp)) if os.path.exists(rp) else {}
    rep["shell_flatness"] = fl; json.dump(rep, open(rp, "w"), indent=1)
    for k, v_ in fl.items():
        print(f"{k:8s} {v_}")
    raise SystemExit
dev = "cuda"; G = np.diag([1, -1, -1, 1.0]); t0 = time.time(); SH0 = 0.28209479177387814

v = PlyData.read(args.ply)["vertex"]; c = lambda n: torch.tensor(np.asarray(v[n]), dtype=torch.float32, device=dev)
means = torch.stack([c("x"), c("y"), c("z")], 1)
quats = F.normalize(torch.stack([c(f"rot_{i}") for i in range(4)], 1), dim=-1)
scales = torch.exp(torch.stack([c(f"scale_{i}") for i in range(3)], 1)); opac = torch.sigmoid(c("opacity"))
nr = len([n for n in v.data.dtype.names if n.startswith("f_rest")])
col = torch.stack([c(f"f_dc_{i}") for i in range(3)], 1)[:, None]
if nr:
    col = torch.cat([col, torch.stack([c(f"f_rest_{i}") for i in range(nr)], 1).reshape(len(means), 3, -1).transpose(1, 2)], 1)
shd = int(round(np.sqrt(col.shape[1]))) - 1


def quat_to_rot(q):                                          # wxyz
    w, x, y, z = q.unbind(1)
    return torch.stack([1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y),
                        2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x),
                        2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)], 1).reshape(-1, 3, 3)


Rg = quat_to_rot(quats)
nrm_w = torch.gather(Rg, 2, scales.argmin(1)[:, None, None].expand(-1, 3, 1)).squeeze(2)   # shortest axis = disc normal
meta = json.load(open(os.path.join(args.work, "frames.json")))
W, H = int(meta["W"] * args.scale), int(meta["H"] * args.scale)
K = np.array([[meta["fx"] * args.scale, 0, meta["cx"] * args.scale], [0, meta["fy"] * args.scale, meta["cy"] * args.scale], [0, 0, 1]])
Kt = torch.tensor(K[None], dtype=torch.float32, device=dev)
vv, uu = torch.meshgrid(torch.arange(H, device=dev) + 0.5, torch.arange(W, device=dev) + 0.5, indexing="ij")
RAY = torch.stack([(uu - K[0, 2]) / K[0, 0], (vv - K[1, 2]) / K[1, 1], torch.ones_like(uu)], -1)


@torch.no_grad()
def render(c2w_cv):
    w2c = torch.tensor(np.linalg.inv(c2w_cv), dtype=torch.float32, device=dev)
    out, alpha, _ = rasterization(means, quats, scales, opac, col, w2c[None], Kt, W, H, sh_degree=shd, render_mode="RGB+ED")
    rgb = out[0, ..., :3].clamp(0, 1); A = alpha[0, ..., 0]; D = out[0, ..., 3]
    if args.depth == "unbiased":
        mc = means @ w2c[:3, :3].T + w2c[:3, 3]; nc = nrm_w @ w2c[:3, :3].T
        nc = torch.where(((nc * mc).sum(1, keepdim=True) > 0), -nc, nc)          # face the camera
        geo = torch.cat([nc, (nc * mc).sum(1, keepdim=True)], 1)                 # normal, plane offset (< 0)
        g, _, _ = rasterization(means, quats, scales, opac, geo, w2c[None], Kt, W, H)
        n_ = g[0, ..., :3]; d_ = g[0, ..., 3]
        D = d_ / (n_ * RAY).sum(-1).clamp(max=-1e-4)
    return rgb, D, A


vol = o3d.pipelines.integration.ScalableTSDFVolume(voxel_length=args.voxel, sdf_trunc=args.trunc,
                                                   color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8)
intr = o3d.camera.PinholeCameraIntrinsic(W, H, K[0, 0], K[1, 1], K[0, 2], K[1, 2])
frames = meta["frames"][:: args.every]
for i, f in enumerate(frames):
    c2w = np.array(f["c2w"]) @ G
    rgb, D, A = render(c2w)
    D = torch.where((A > args.min_alpha) & (D > 0.1) & (D < args.max_depth), D, torch.zeros_like(D))
    rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
        o3d.geometry.Image((rgb.cpu().numpy() * 255).astype(np.uint8)), o3d.geometry.Image(D.cpu().numpy().astype(np.float32)),
        depth_scale=1.0, depth_trunc=args.max_depth, convert_rgb_to_intensity=False)
    vol.integrate(rgbd, intr, np.linalg.inv(c2w))
    if i % 100 == 0:
        print(f"{i}/{len(frames)} fused", flush=True)
t1 = time.time()
mesh = vol.extract_triangle_mesh()
ntri0 = len(mesh.triangles)
cl, n_cl, _ = mesh.cluster_connected_triangles(); cl = np.asarray(cl); n_cl = np.asarray(n_cl)
mesh.remove_triangles_by_mask(n_cl[cl] < args.min_piece * ntri0)
mesh.remove_unreferenced_vertices(); mesh.compute_vertex_normals()
o3d.io.write_triangle_mesh(os.path.join(args.out, "mesh.ply"), mesh)
rep = dict(model=os.path.abspath(args.ply), depth=args.depth, frames=len(frames), voxel=args.voxel,
           triangles=len(mesh.triangles), vertices=len(mesh.vertices), triangles_before_cleanup=ntri0,
           fuse_min=round((t1 - t0) / 60, 2))
print(f"mesh: {ntri0} triangles -> {len(mesh.triangles)} after removing small pieces, fused in {(t1 - t0) / 60:.1f} min")

# ---------------- flatness of the room shell ----------------
if args.layout:
    rep["shell_flatness"] = shell_flatness(np.asarray(mesh.vertices), np.asarray(mesh.vertex_normals), json.load(open(args.layout)))
    for k, v_ in rep["shell_flatness"].items():
        print(f"{k:8s} {v_}")
json.dump(rep, open(os.path.join(args.out, "mesh_report.json"), "w"), indent=1)

# ---------------- renders: splat | mesh colour | mesh shaded ----------------
tm = o3d.t.geometry.TriangleMesh.from_legacy(mesh)
scene = o3d.t.geometry.RaycastingScene(); scene.add_triangles(tm)
mesh.compute_triangle_normals()
VC = np.asarray(mesh.vertex_colors); TRI = np.asarray(mesh.triangles); TN = np.asarray(mesh.triangle_normals)
Wr, Hr = W // 2, H // 2
Kr = K / 2; Kr[2, 2] = 1


def ray_render(c2w_cv):
    vv_, uu_ = np.mgrid[0:Hr, 0:Wr] + 0.5
    d = np.stack([(uu_ - Kr[0, 2]) / Kr[0, 0], (vv_ - Kr[1, 2]) / Kr[1, 1], np.ones_like(uu_)], -1) @ c2w_cv[:3, :3].T
    d /= np.linalg.norm(d, axis=-1, keepdims=True)
    rays = np.concatenate([np.broadcast_to(c2w_cv[:3, 3], d.shape), d], -1).astype(np.float32)
    r = scene.cast_rays(o3d.core.Tensor(rays))
    pid = r["primitive_ids"].numpy(); hit = pid != o3d.t.geometry.RaycastingScene.INVALID_ID
    uv = r["primitive_uvs"].numpy()
    colr = np.zeros((Hr, Wr, 3)); shade = np.zeros((Hr, Wr, 3))
    t_ = TRI[pid[hit]]; b1, b2 = uv[hit][:, 0:1], uv[hit][:, 1:2]
    colr[hit] = VC[t_[:, 0]] * (1 - b1 - b2) + VC[t_[:, 1]] * b1 + VC[t_[:, 2]] * b2
    lam = np.abs((TN[pid[hit]] * -d[hit]).sum(1, keepdims=True))
    shade[hit] = 0.15 + 0.85 * lam * np.array([0.85, 0.9, 1.0])
    return (colr[..., ::-1] * 255).astype(np.uint8), (shade[..., ::-1] * 255).astype(np.uint8)


UP = np.array([0.0, 1, 0]); ctr = np.array([np.array(f["c2w"])[:3, 3] for f in meta["frames"]]).mean(0)
def look(pos, tgt):
    fw = tgt - pos; fw /= np.linalg.norm(fw); r_ = np.cross(fw, UP); r_ /= np.linalg.norm(r_); u_ = np.cross(r_, fw)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = r_, -u_, fw, pos       # OpenCV camera
    return m


cams = [("frame", np.array(f["c2w"]) @ G) for f in meta["frames"][:: max(1, len(meta["frames"]) // 3)][:3]]
cams += [(f"centre {a}", look(ctr, ctr + np.array([np.cos(np.radians(a)), -0.35, np.sin(np.radians(a))]))) for a in (0, 90, 180, 270)]
rows = []
for nm, c2w in cams:
    w2c = torch.tensor(np.linalg.inv(c2w), dtype=torch.float32, device=dev)
    with torch.no_grad():
        o_, _, _ = rasterization(means, quats, scales, opac, col, w2c[None], torch.tensor(Kr[None], dtype=torch.float32, device=dev),
                                 Wr, Hr, sh_degree=shd)
    sp = (o_[0].clamp(0, 1).cpu().numpy()[..., ::-1] * 255).astype(np.uint8)
    mc, ms = ray_render(c2w)
    row = np.hstack([sp, mc, ms])
    cv2.putText(row, f"{nm}: splat | mesh colour | mesh geometry", (8, 24), 0, 0.6, (0, 0, 0), 3)
    cv2.putText(row, f"{nm}: splat | mesh colour | mesh geometry", (8, 24), 0, 0.6, (255, 255, 255), 1)
    rows.append(row)
cv2.imwrite(os.path.join(args.out, "mesh_views.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])
print(f"done in {(time.time() - t0) / 60:.1f} min -> {args.out}")
