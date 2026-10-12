"""Dense initial point cloud for splatfacto from a COLMAP dense fusion (PocketGS operator G / 3DGS-MVS baseline).

The fused cloud is in COLMAP's (arbitrary-scale) world. The Sim3 to the metric training world is recovered
exactly from the COLMAP camera centres vs. the metric poses in frames.json (both describe the same cameras).
Then: voxel-downsample (--voxel), merge with the SfM points already used as init, write a PLY and a copy of
transforms.json pointing at it (the original transforms.json is untouched).

  python src/arcore3dgs/mvs_init.py --work <work_sfm> --sparse <colmap sparse model dir> --fused <fused.ply>
      --out_ply init_mvs.ply --out_json transforms_mvs.json
"""
import os, json, argparse, subprocess
import numpy as np
from scipy.spatial.transform import Rotation as R

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True); ap.add_argument("--sparse", required=True); ap.add_argument("--fused", required=True)
ap.add_argument("--voxel", type=float, default=0.01)
ap.add_argument("--out_ply", default="init_mvs.ply"); ap.add_argument("--out_json", default="transforms_mvs.json")
ap.add_argument("--colmap", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools", "colmap_dl", "colmap-4.2.0", "COLMAP.bat"))
args = ap.parse_args()

txt = args.sparse.rstrip("/\\") + "_txt"; os.makedirs(txt, exist_ok=True)
subprocess.run([os.path.abspath(args.colmap), "model_converter", "--input_path", args.sparse, "--output_path", txt,
                "--output_type", "TXT"], check=True, capture_output=True)
cent = {}
L = [l for l in open(os.path.join(txt, "images.txt")) if l[0] != "#"]
for a in L[0::2]:
    p = a.split()
    if len(p) < 10:
        continue
    q = list(map(float, p[1:5])); t = np.array(list(map(float, p[5:8])))
    Rw = R.from_quat([q[1], q[2], q[3], q[0]]).as_matrix(); cent[p[9][:-4]] = -Rw.T @ t
meta = json.load(open(os.path.join(args.work, "frames.json")))
names = [f["name"] for f in meta["frames"] if f["name"] in cent]
A = np.array([cent[n] for n in names]); by = {f["name"]: f for f in meta["frames"]}
B = np.array([np.array(by[n]["c2w"])[:3, 3] for n in names])
def fit(A, B):
    ma, mb = A.mean(0), B.mean(0); s = np.sqrt(((B - mb) ** 2).sum() / ((A - ma) ** 2).sum())
    U, _, Vt = np.linalg.svd((B - mb).T @ (A - ma)); Rm = U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt
    return s, Rm, mb - s * Rm @ ma


keep = np.ones(len(A), bool)                                             # trimmed fit: drop cameras that one of
for _ in range(5):                                                       # the two models mis-registered
    s, Rm, t = fit(A[keep], B[keep]); res = np.linalg.norm((s * (Rm @ A.T)).T + t - B, axis=1)
    keep = res < max(0.02, 3 * np.median(res[keep]))
print(f"Sim3 from {keep.sum()}/{len(names)} cameras: scale {s:.5f}, inlier residual median {np.median(res[keep]) * 1000:.1f} mm, "
      f"max {res[keep].max() * 1000:.1f} mm")


def read_ply(path):
    with open(path, "rb") as f:
        hdr = b""
        while b"end_header" not in hdr:                                # COLMAP on Windows writes \r\n
            line = f.readline()
            if not line:
                raise ValueError("no PLY header end in " + path)
            hdr += line
        h = hdr.decode().replace("\r", "").splitlines(); n = int(next(l.split()[2] for l in h if l.startswith("element vertex")))
        tmap = {"float": "f4", "double": "f8", "uchar": "u1", "int": "i4"}
        dt = [(l.split()[2], tmap[l.split()[1]]) for l in h if l.startswith("property")]
        return np.frombuffer(f.read(n * np.dtype(dt).itemsize), dtype=dt, count=n)


v = read_ply(args.fused)
P = (s * (Rm @ np.stack([v["x"], v["y"], v["z"]], 1).astype(np.float64).T)).T + t
Cc = np.stack([v["red"], v["green"], v["blue"]], 1).astype(np.float64)
old = read_ply(os.path.join(args.work, "init_points.ply"))                       # SfM points (already metric)
P = np.concatenate([P, np.stack([old["x"], old["y"], old["z"]], 1)]); Cc = np.concatenate([Cc, np.stack([old["red"], old["green"], old["blue"]], 1)])
key = np.floor(P / args.voxel).astype(np.int64)
_, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True); inv = inv.ravel()
Pm = np.zeros((len(cnt), 3)); Cm = np.zeros((len(cnt), 3)); np.add.at(Pm, inv, P); np.add.at(Cm, inv, Cc)
Pm /= cnt[:, None]; Cm /= cnt[:, None]
el = np.zeros(len(Pm), [("x", "f4"), ("y", "f4"), ("z", "f4"), ("red", "u1"), ("green", "u1"), ("blue", "u1")])
el["x"], el["y"], el["z"] = Pm.T; el["red"], el["green"], el["blue"] = np.clip(Cm, 0, 255).T.astype(np.uint8)
with open(os.path.join(args.work, args.out_ply), "wb") as f:
    f.write((f"ply\nformat binary_little_endian 1.0\nelement vertex {len(el)}\nproperty float x\nproperty float y\n"
             "property float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n").encode())
    f.write(el.tobytes())
tj = json.load(open(os.path.join(args.work, "transforms.json"))); tj["ply_file_path"] = args.out_ply
json.dump(tj, open(os.path.join(args.work, args.out_json), "w"), indent=1)
print(f"{len(v)} fused + {len(old)} SfM points -> {len(Pm)} at {args.voxel * 100:.0f} cm -> {args.out_ply}, {args.out_json}")
