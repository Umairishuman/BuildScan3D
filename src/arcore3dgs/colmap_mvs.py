"""Dense depth with COLMAP PatchMatch stereo from our fixed, metric BA poses.

Our poses (ba.py, ~0.6 px) are kept as-is; COLMAP only matches features between co-visible keyframes
(pairs taken from the BA tracks), triangulates with the poses held fixed, then runs PatchMatch stereo
(per-pixel depth + normal, geometric consistency) and fusion. Metric scale is preserved because the poses
are never re-estimated.

  nerfstudio-env\Scripts\python.exe src/arcore3dgs/colmap_mvs.py --work <dataset>/work [--max_image_size 960] [--num_src 12] [--stage all]

Outputs in <work>/colmap/: sparse/ (triangulated model), dense/stereo/depth_maps/*.geometric.bin,
dense/fused.ply, and <work>/depth_colmap/<name>.npy (metric depth, depth_scale resolution, 0 = no depth).
"""
import os, json, argparse, sqlite3, subprocess, warnings
import numpy as np, cv2
from scipy.spatial.transform import Rotation as R

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--colmap", default=os.path.join(os.path.dirname(__file__), "..", "..", "tools", "colmap_dl",
                                                 "colmap-4.2.0", "COLMAP.bat"))
ap.add_argument("--frames_file", default="frames.json")
ap.add_argument("--pairs_per_image", type=int, default=25)
ap.add_argument("--min_shared", type=int, default=15, help="min shared BA points for a matching pair")
ap.add_argument("--max_image_size", type=int, default=960, help="960 = our depth resolution (depth_scale 0.5)")
ap.add_argument("--num_src", type=int, default=12, help="source views per reference view in PatchMatch")
ap.add_argument("--median", type=int, default=5, help="hole-aware median filter size on the depth maps (1 = off)")
ap.add_argument("--voxel", type=float, default=0.01, help="voxel size (m) for colmap_points.ply")
ap.add_argument("--stage",default="all", choices=["all", "sparse", "dense", "convert"])
args = ap.parse_args()
warnings.filterwarnings("ignore", "All-NaN slice")

W_ = os.path.abspath(args.work); CM = os.path.abspath(args.colmap)
root = os.path.join(W_, "colmap"); os.makedirs(root, exist_ok=True)
db = os.path.join(root, "database.db")
meta = json.load(open(os.path.join(W_, args.frames_file)))
fr = [f for f in meta["frames"] if not f.get("fallback_unverified")]
names = [f["name"] + ".jpg" for f in fr]
G = np.diag([1.0, -1.0, -1.0, 1.0])


def colmap(*a):
    cmd = [CM] + [str(x) for x in a]
    print(">", " ".join(cmd[1:3]), flush=True)
    subprocess.run(cmd, check=True)


def sparse():
    if os.path.exists(db):
        os.remove(db)
    with open(os.path.join(root, "image_list.txt"), "w") as f:
        f.write("\n".join(names))
    colmap("feature_extractor", "--database_path", db, "--image_path", os.path.join(W_, "images"),
           "--image_list_path", os.path.join(root, "image_list.txt"),
           "--ImageReader.single_camera", 1, "--ImageReader.camera_model", "PINHOLE",
           "--ImageReader.camera_params", f"{meta['fx']},{meta['fy']},{meta['cx']},{meta['cy']}",
           "--FeatureExtraction.use_gpu", 1, "--SiftExtraction.max_num_features", 8192)

    # matching pairs = keyframes that share BA points (co-visibility from our own tracks)
    full = [f["name"] for f in json.load(open(os.path.join(W_, "frames.json")))["frames"]]
    sp = np.load(os.path.join(W_, "sparse.npz")); cam, pt = sp["cam"], sp["pt"]
    keep = {full.index(f["name"]): k for k, f in enumerate(fr)}
    m = np.isin(cam, list(keep)); cam, pt = np.array([keep[c] for c in cam[m]]), pt[m]
    n = len(fr); A = np.zeros((n, n), np.int32)
    order = np.argsort(pt); cam, pt = cam[order], pt[order]
    starts = np.r_[0, np.flatnonzero(np.diff(pt)) + 1, len(pt)]
    for a, b in zip(starts[:-1], starts[1:]):
        c = np.unique(cam[a:b])
        A[np.ix_(c, c)] += 1
    np.fill_diagonal(A, 0)
    pairs = set()
    for i in range(n):
        for j in np.argsort(-A[i])[: args.pairs_per_image]:
            if A[i, j] >= args.min_shared:
                pairs.add((min(i, j), max(i, j)))
        for j in range(i + 1, min(n, i + 4)):                       # always match close neighbours in time
            pairs.add((i, j))
    with open(os.path.join(root, "pairs.txt"), "w") as f:
        f.write("\n".join(f"{names[i]} {names[j]}" for i, j in sorted(pairs)))
    print(f"{len(pairs)} matching pairs for {n} images")
    colmap("matches_importer", "--database_path", db, "--match_list_path", os.path.join(root, "pairs.txt"),
           "--match_type", "pairs", "--FeatureMatching.use_gpu", 1)

    # known-pose model with the database's own image / camera ids
    con = sqlite3.connect(db)
    ids = {nm: (iid, cid) for iid, nm, cid in con.execute("SELECT image_id, name, camera_id FROM images")}
    con.close()
    known = os.path.join(root, "known"); os.makedirs(known, exist_ok=True)
    cid = next(iter(ids.values()))[1]
    with open(os.path.join(known, "cameras.txt"), "w") as f:
        f.write(f"{cid} PINHOLE {meta['W']} {meta['H']} {meta['fx']} {meta['fy']} {meta['cx']} {meta['cy']}\n")
    with open(os.path.join(known, "images.txt"), "w") as f:
        for fm, nm in zip(fr, names):
            w2c = np.linalg.inv(np.array(fm["c2w"]) @ G)
            qx, qy, qz, qw = R.from_matrix(w2c[:3, :3]).as_quat()
            t = w2c[:3, 3]
            f.write(f"{ids[nm][0]} {qw} {qx} {qy} {qz} {t[0]} {t[1]} {t[2]} {ids[nm][1]} {nm}\n\n")
    open(os.path.join(known, "points3D.txt"), "w").close()
    out = os.path.join(root, "sparse"); os.makedirs(out, exist_ok=True)
    colmap("point_triangulator", "--database_path", db, "--image_path", os.path.join(W_, "images"),
           "--input_path", known, "--output_path", out,
           "--Mapper.ba_refine_focal_length", 0, "--Mapper.ba_refine_principal_point", 0,
           "--Mapper.ba_refine_extra_params", 0)


def dense():
    dn = os.path.join(root, "dense")
    colmap("image_undistorter", "--image_path", os.path.join(W_, "images"), "--input_path", os.path.join(root, "sparse"),
           "--output_path", dn, "--output_type", "COLMAP", "--max_image_size", args.max_image_size)
    cfg = os.path.join(dn, "stereo", "patch-match.cfg")               # fewer auto-selected sources = faster
    txt = open(cfg).read().replace("__auto__, 20", f"__auto__, {args.num_src}")
    open(cfg, "w").write(txt)
    colmap("patch_match_stereo", "--workspace_path", dn, "--workspace_format", "COLMAP",
           "--PatchMatchStereo.geom_consistency", 1, "--PatchMatchStereo.depth_min", 0.15,
           "--PatchMatchStereo.depth_max", 15)
    colmap("stereo_fusion", "--workspace_path", dn, "--workspace_format", "COLMAP", "--input_type", "geometric",
           "--output_path", os.path.join(dn, "fused.ply"))


def read_bin(p):
    with open(p, "rb") as f:
        hdr = b""
        while hdr.count(b"&") < 3:
            hdr += f.read(1)
        w, h, c = map(int, hdr.decode().split("&")[:3])
        return np.fromfile(f, np.float32).reshape(c, h, w).transpose(1, 2, 0).squeeze()


def masked_median(d, k):
    """k x k median over measured pixels only; holes stay holes (removes isolated wrong depths)."""
    if k <= 1:
        return d
    h, w = d.shape; x = np.where(d > 0, d, np.nan); p = k // 2
    xp = np.pad(x, p, constant_values=np.nan)
    with np.errstate(all="ignore"):
        m = np.nanmedian(np.stack([xp[dy:dy + h, dx:dx + w] for dy in range(k) for dx in range(k)]), 0)
    m[np.isnan(m) | (d <= 0)] = 0
    return m.astype(np.float32)


def convert():
    """COLMAP geometric depth -> <work>/depth_colmap/<name>.npy at our depth resolution (0 = unmeasured),
    hole-aware median filtered; fused.ply -> colmap_points.ply (voxel-downsampled training init)."""
    dm = os.path.join(root, "dense", "stereo", "depth_maps"); out = os.path.join(W_, "depth_colmap")
    os.makedirs(out, exist_ok=True)
    s = meta.get("depth_scale", 0.5); w, h = int(meta["W"] * s), int(meta["H"] * s)
    cov = []
    for nm in names:
        p = os.path.join(dm, nm + ".geometric.bin")
        if not os.path.exists(p):
            continue
        d = read_bin(p); d[~np.isfinite(d)] = 0
        d = masked_median(cv2.resize(d, (w, h), interpolation=cv2.INTER_NEAREST), args.median)
        np.save(os.path.join(out, nm[:-4] + ".npy"), d.astype(np.float32))
        cov.append((d > 0).mean())
    print(f"depth_colmap: {len(cov)} maps, mean coverage {100 * np.mean(cov):.1f}% of pixels")

    fp = os.path.join(root, "dense", "fused.ply")
    if os.path.exists(fp):
        from plyfile import PlyData, PlyElement
        v = PlyData.read(fp)["vertex"]
        P = np.stack([v["x"], v["y"], v["z"]], 1); Cl = np.stack([v["red"], v["green"], v["blue"]], 1)
        key = np.floor(P / args.voxel).astype(np.int64)
        _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True); inv = inv.ravel()
        Pm = np.zeros((len(cnt), 3)); Cm = np.zeros((len(cnt), 3))
        np.add.at(Pm, inv, P); np.add.at(Cm, inv, Cl)
        Pm /= cnt[:, None]; Cm /= cnt[:, None]
        el = np.empty(len(Pm), [("x", "f4"), ("y", "f4"), ("z", "f4"), ("red", "u1"), ("green", "u1"), ("blue", "u1")])
        el["x"], el["y"], el["z"] = Pm.T; el["red"], el["green"], el["blue"] = np.clip(Cm, 0, 255).T
        PlyData([PlyElement.describe(el, "vertex")]).write(os.path.join(W_, "colmap_points.ply"))
        print(f"colmap_points.ply: {len(P)} fused points -> {len(Pm)} at {args.voxel * 100:.0f} cm voxels")


if args.stage in ("all", "sparse"):
    sparse()
if args.stage in ("all", "dense"):
    dense()
if args.stage in ("all", "convert"):
    convert()
