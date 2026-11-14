"""Dense initial point cloud from the SfM-anchored monocular depth (mono_prior.py) -- replaces the 2 h COLMAP
PatchMatch dense step for initialisation. Every --every-th frame's aligned depth (1/4 res, stride --stride) is
back-projected with the frame's metric pose, coloured from the image, merged with the SfM points, and voxelised.
Per-frame mono depths disagree slightly, which makes a thick noisy shell; a point is kept only when at least
--min_views different frames land in its coarse --agree_voxel cell (multi-view agreement; the aligned prior is
good to ~3 % of depth, i.e. several cm, so agreement is tested on a coarser grid than the output voxels). SfM points are always kept.

  python src/arcore3dgs/mono_init.py --work <work_sfm> --json transforms_offpath.json --out_json transforms_offpath_mono.json
"""
import os, json, argparse
import numpy as np, cv2

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True); ap.add_argument("--json", required=True); ap.add_argument("--out_json", required=True)
ap.add_argument("--every", type=int, default=4); ap.add_argument("--stride", type=int, default=3)
ap.add_argument("--voxel", type=float, default=0.01); ap.add_argument("--max_depth", type=float, default=8.0)
ap.add_argument("--down", type=int, default=4); ap.add_argument("--min_views", type=int, default=3)
ap.add_argument("--agree_voxel", type=float, default=0.06)
ap.add_argument("--base", default="init_points.ply", help="cloud the mono points are merged into (SfM or MVS points)")
ap.add_argument("--fill_only", type=float, default=0.0, help="> 0: add mono points only where the base cloud has no point within ~this many metres")
ap.add_argument("--out_ply", default="init_mono.ply")
args = ap.parse_args()
meta = json.load(open(os.path.join(args.work, "frames.json"))); d = args.down
fx, fy, cx, cy = meta["fx"] / d, meta["fy"] / d, meta["cx"] / d, meta["cy"] / d
G = np.diag([1.0, -1.0, -1.0, 1.0])
tj = json.load(open(os.path.join(args.work, args.json)))
train = set(tj.get("train_filenames", [f["file_path"] for f in tj["frames"]]))
by = {f["name"]: f for f in meta["frames"]}
names = [os.path.splitext(os.path.basename(f["file_path"]))[0] for f in tj["frames"] if f["file_path"] in train][:: args.every]
P, C, F = [], [], []
for i, n in enumerate(names):
    z = np.load(os.path.join(args.work, "mono_prior", n + ".npz"))
    D = z["depth"].astype(np.float32); V = z["valid"] & (D < args.max_depth)
    h, w = D.shape
    vv, uu = np.mgrid[0:h:args.stride, 0:w:args.stride]
    keep = V[vv, uu]; vv, uu = vv[keep], uu[keep]; zz = D[vv, uu]
    pc = np.stack([(uu + 0.5 - cx) / fx * zz, (vv + 0.5 - cy) / fy * zz, zz], 1)
    c2w = np.array(by[n]["c2w"]) @ G
    P.append(pc @ c2w[:3, :3].T + c2w[:3, 3])
    img = cv2.resize(cv2.imread(os.path.join(args.work, "images", n + ".jpg")), (w, h), interpolation=cv2.INTER_AREA)
    C.append(img[vv, uu][:, ::-1].astype(np.float64)); F.append(np.full(len(zz), i))


def read_ply(path):
    with open(path, "rb") as f:
        hdr = b""
        while b"end_header" not in hdr:
            hdr += f.readline()
        h_ = hdr.decode().replace("\r", "").splitlines(); n_ = int(next(l.split()[2] for l in h_ if l.startswith("element vertex")))
        tmap = {"float": "f4", "double": "f8", "uchar": "u1", "int": "i4"}
        dt = [(l.split()[2], tmap[l.split()[1]]) for l in h_ if l.startswith("property")]
        return np.frombuffer(f.read(n_ * np.dtype(dt).itemsize), dtype=dt, count=n_)


sfm = read_ply(os.path.join(args.work, args.base))
P.append(np.stack([sfm["x"], sfm["y"], sfm["z"]], 1).astype(np.float64)); C.append(np.stack([sfm["red"], sfm["green"], sfm["blue"]], 1).astype(np.float64))
F.append(np.full(len(sfm), -1))
P = np.concatenate(P); C = np.concatenate(C); F = np.concatenate(F); n_raw = len(P)
key = np.floor(P / args.voxel).astype(np.int64)
_, inv = np.unique(np.floor(P / args.agree_voxel).astype(np.int64), axis=0, return_inverse=True); inv = inv.ravel()
pair = np.unique(np.stack([inv, F], 1), axis=0)          # distinct (voxel, frame)
views = np.bincount(pair[:, 0], minlength=inv.max() + 1)
sfm_vox = np.zeros(len(views), bool); sfm_vox[inv[F < 0]] = True
ok = ((views >= args.min_views) | sfm_vox)[inv]
if args.fill_only > 0:                                       # hybrid: skip mono points next to existing base points
    cell = np.floor(P / args.fill_only).astype(np.int64)
    base_cells = {tuple(c) for c in cell[F < 0]}
    occupied = np.array([tuple(c) in base_cells for c in cell])
    ok &= (F < 0) | ~occupied
P, C = P[ok], C[ok]
_, inv, cnt = np.unique(key[ok], axis=0, return_inverse=True, return_counts=True); inv = inv.ravel()
Pm = np.zeros((len(cnt), 3)); Cm = np.zeros((len(cnt), 3)); np.add.at(Pm, inv, P); np.add.at(Cm, inv, C)
Pm /= cnt[:, None]; Cm /= cnt[:, None]
el = np.zeros(len(Pm), [("x", "f4"), ("y", "f4"), ("z", "f4"), ("red", "u1"), ("green", "u1"), ("blue", "u1")])
el["x"], el["y"], el["z"] = Pm.T; el["red"], el["green"], el["blue"] = np.clip(Cm, 0, 255).T.astype(np.uint8)
with open(os.path.join(args.work, args.out_ply), "wb") as f:
    f.write((f"ply\nformat binary_little_endian 1.0\nelement vertex {len(el)}\nproperty float x\nproperty float y\n"
             "property float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n").encode())
    f.write(el.tobytes())
tj["ply_file_path"] = args.out_ply
json.dump(tj, open(os.path.join(args.work, args.out_json), "w"), indent=1)
print(f"{len(names)} frames + {len(sfm)} SfM points -> {n_raw} points -> {len(Pm)} voxels at {args.voxel * 100:.1f} cm seen by >= {args.min_views} frames -> {args.out_ply}, {args.out_json}")
