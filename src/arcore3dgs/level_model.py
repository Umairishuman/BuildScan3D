"""Level an already trained model with ARCore's gravity (D-071), without retraining.

Models exported before 2026-11-12 took the Sim3 rotation from camera centres only and can be tilted (R-032: scan #2
9.1 deg, scan #3 12.1 deg), which breaks every stage that assumes +Y is up (layout, semantics, mesh labels, web).
`sfm_colmap.py` now levels new runs itself; this script levels an existing one by a rigid rotation of the trained
splats (positions, orientations, normals and the view-dependent colour coefficients) and of the camera poses:

  <dataset>/work_<tag>_sfm/            (source, not changed)
  <dataset>/work_<new_tag>_sfm/        frames.json (levelled poses), level.json, links to images/ and planes/
                          gs_<new_tag>/splat.ply (levelled)

Then the rest of the pipeline runs on the copy:  scripts/run_full.sh <dataset> <new_tag> --from layout -- --pgsr
(--pgsr only if the source model was trained with it; it selects the unbiased depth for the mesh).

  micromamba run -n bs-ns python src/arcore3dgs/level_model.py --dataset dataset/scan_003_6de634cbb8b2 --tag r1112 \
      --new_tag r1112lev [--check 3]

--check N renders N frames from the source model and from the levelled one (levelled cameras) and prints the PSNR
between them: a correct rotation gives the same images (PSNR > 40 dB).
"""
import os, json, argparse
import numpy as np, torch
from plyfile import PlyData, PlyElement

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", required=True); ap.add_argument("--tag", required=True); ap.add_argument("--new_tag", required=True)
ap.add_argument("--check", type=int, default=3, help="frames rendered from both models to compare (0 = skip)")
args = ap.parse_args()
D = os.path.abspath(args.dataset)
SRC = os.path.join(D, f"work_{args.tag}_sfm"); DST = os.path.join(D, f"work_{args.new_tag}_sfm")
M_SRC = os.path.join(SRC, f"gs_{args.tag}"); M_DST = os.path.join(DST, f"gs_{args.new_tag}")
if os.path.exists(os.path.join(M_DST, "splat.ply")):
    raise SystemExit(f"{M_DST}/splat.ply exists already; pick another --new_tag (nothing is overwritten)")
Y = np.array([0.0, 1.0, 0.0])

# ---------------- gravity: ARCore's up in the model world (same as sfm_colmap.arcore_up) ----------------
meta = json.load(open(os.path.join(SRC, "frames.json")))
U = np.array([np.array(f["c2w"])[:3, :3] @ (np.array(f["c2w_arcore"])[:3, :3].T @ Y) for f in meta["frames"]])
U /= np.linalg.norm(U, axis=1, keepdims=True); keep = np.ones(len(U), bool)
for _ in range(3):
    u = U[keep].mean(0); u /= np.linalg.norm(u)
    dev = np.degrees(np.arccos(np.clip(U @ u, -1, 1))); keep = dev < max(2.0, 3 * np.median(dev))
tilt = float(np.degrees(np.arccos(np.clip(u @ Y, -1, 1))))
v = np.cross(u, Y); s_, c_ = np.linalg.norm(v), float(u @ Y)
K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
Rg = np.eye(3) + K + K @ K * ((1 - c_) / s_ ** 2) if s_ > 1e-9 else np.eye(3)
print(f"ARCore gravity is {tilt:.2f} deg from the model's +Y (per-frame spread {np.median(dev):.2f} deg, "
      f"{keep.sum()} / {len(U)} frames): rotating the model by {tilt:.2f} deg")

# ---------------- poses ----------------
os.makedirs(M_DST, exist_ok=True)
meta2 = json.loads(json.dumps(meta))
for f in meta2["frames"]:
    c2w = np.array(f["c2w"]); c2w[:3] = Rg @ c2w[:3]; f["c2w"] = c2w.tolist()
meta2.setdefault("sfm", {})["levelled"] = dict(source=f"work_{args.tag}_sfm", tilt_deg=tilt, spread_deg=float(np.median(dev)))
json.dump(meta2, open(os.path.join(DST, "frames.json"), "w"), indent=1)
for d in ("images", "planes"):                               # camera-frame data: unchanged by a world rotation
    if os.path.exists(os.path.join(SRC, d)) and not os.path.exists(os.path.join(DST, d)):
        os.symlink(os.path.join("..", f"work_{args.tag}_sfm", d), os.path.join(DST, d))
json.dump(dict(source_work=SRC, source_model=os.path.join(M_SRC, "splat.ply"), tilt_deg=tilt,
               spread_deg=float(np.median(dev)), frames_used=int(keep.sum()), R=Rg.tolist(),
               note="new = R @ old (positions and camera poses); D-071, R-032"),
          open(os.path.join(DST, "level.json"), "w"), indent=1)

# ---------------- splats ----------------
ply = PlyData.read(os.path.join(M_SRC, "splat.ply")); vx = ply["vertex"].data.copy()
names = vx.dtype.names
P = np.stack([vx["x"], vx["y"], vx["z"]], 1).astype(np.float64) @ Rg.T
vx["x"], vx["y"], vx["z"] = P.T
if "nx" in names:
    Nn = np.stack([vx["nx"], vx["ny"], vx["nz"]], 1) @ Rg.T; vx["nx"], vx["ny"], vx["nz"] = Nn.T
# orientation quaternions (w, x, y, z): q_new = q_R * q
from scipy.spatial.transform import Rotation as Rot
qr = Rot.from_matrix(Rg).as_quat()                           # x, y, z, w
q = np.stack([vx["rot_1"], vx["rot_2"], vx["rot_3"], vx["rot_0"]], 1).astype(np.float64)
nq = np.linalg.norm(q, axis=1, keepdims=True); qn = (Rot.from_quat(qr) * Rot.from_quat(q / nq)).as_quat() * nq
vx["rot_1"], vx["rot_2"], vx["rot_3"], vx["rot_0"] = qn.T
# view-dependent colour: f_rest_{c * K + k} = channel c, coefficient k (INRIA / nerfstudio layout)
rest = sorted([n for n in names if n.startswith("f_rest_")], key=lambda n: int(n[7:]))
from gsplat import spherical_harmonics


def sh_basis(dirs, nk):                                      # (M, nk) values of gsplat's real SH basis
    dev_ = torch.device("cuda"); d = torch.tensor(dirs, dtype=torch.float32, device=dev_)
    out = []
    for k in range(nk):
        cf = torch.zeros(len(d), nk, 3, device=dev_); cf[:, k, 0] = 1
        out.append(spherical_harmonics(int(np.sqrt(nk)) - 1, d, cf)[:, 0])
    return torch.stack(out, 1).double().cpu().numpy()


if rest:
    nk = len(rest) // 3 + 1                                  # coefficients per channel incl. DC (16 for degree 3)
    rng = np.random.default_rng(0); dirs = rng.normal(size=(4000, 3)); dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    # colour'(d) = colour(Rg^T d)  =>  B(d) c' = B(Rg^T d) c  =>  c' = Mx c, Mx = lstsq(B(d), B(Rg^T d))
    Bd, Bt = sh_basis(dirs, nk), sh_basis(dirs @ Rg, nk)
    Mx = np.linalg.lstsq(Bd, Bt, rcond=None)[0]              # (nk, nk); row 0 / column 0 = DC, unchanged
    err = np.abs(Bd @ Mx - Bt).max()
    print(f"colour coefficients: degree {int(np.sqrt(nk)) - 1}, rotation fit max error {err:.2e}")
    assert err < 1e-4, "SH rotation fit failed"
    Mr = Mx[1:, 1:]
    F_ = np.stack([vx[n] for n in rest], 1).astype(np.float64).reshape(len(vx), 3, nk - 1)   # (N, channel, k)
    F2 = np.einsum("jk,nck->ncj", Mr, F_).reshape(len(vx), -1)                                  # c'_j = sum_k Mr[j, k] c_k
    for i, n in enumerate(rest):
        vx[n] = F2[:, i]
PlyData([PlyElement.describe(vx, "vertex")], text=False).write(os.path.join(M_DST, "splat.ply"))
print(f"-> {M_DST}/splat.ply ({len(vx)} splats), {DST}/frames.json")

# ---------------- check: same images from both models ----------------
if args.check:
    from gsplat import rasterization
    import torch.nn.functional as F

    def load(path):
        v_ = PlyData.read(path)["vertex"]; t = lambda n: torch.tensor(np.asarray(v_[n]), dtype=torch.float32, device="cuda")
        means = torch.stack([t("x"), t("y"), t("z")], 1)
        quats = F.normalize(torch.stack([t(f"rot_{i}") for i in range(4)], 1), dim=-1)
        scales = torch.exp(torch.stack([t(f"scale_{i}") for i in range(3)], 1)); op = torch.sigmoid(t("opacity"))
        dc = torch.stack([t(f"f_dc_{i}") for i in range(3)], 1)[:, None]
        rs = torch.stack([t(n) for n in rest], 1).reshape(len(means), 3, -1).transpose(1, 2) if rest else dc[:, :0]
        return means, quats, scales, op, torch.cat([dc, rs], 1)

    a, b = load(os.path.join(M_SRC, "splat.ply")), load(os.path.join(M_DST, "splat.ply"))
    Gm = np.diag([1, -1, -1, 1.0]); dn = 4; W, H = meta["W"] // dn, meta["H"] // dn
    Kt = torch.tensor([[[meta["fx"] / dn, 0, meta["cx"] / dn], [0, meta["fy"] / dn, meta["cy"] / dn], [0, 0, 1]]],
                      dtype=torch.float32, device="cuda")
    sh_deg = int(np.sqrt(a[4].shape[1])) - 1
    for f1, f2 in list(zip(meta["frames"], meta2["frames"]))[:: max(1, len(meta["frames"]) // args.check)][: args.check]:
        imgs = []
        for mdl, f in ((a, f1), (b, f2)):
            w2c = torch.tensor(np.linalg.inv(np.array(f["c2w"]) @ Gm)[None], dtype=torch.float32, device="cuda")
            with torch.no_grad():
                im, _, _ = rasterization(*mdl, w2c, Kt, W, H, sh_degree=sh_deg)
            imgs.append(im[0].clamp(0, 1))
        mse = float(((imgs[0] - imgs[1]) ** 2).mean())
        print(f"check {f1['name']}: PSNR source vs levelled {10 * np.log10(1 / max(mse, 1e-12)):.1f} dB")
