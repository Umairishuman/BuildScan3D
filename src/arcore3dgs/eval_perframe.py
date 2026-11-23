"""Per-frame held-out diagnosis (FEATURELESS_TRACKING_PLAN §10, after R-082 / R-083; moved here from a scratchpad
2026-11-21).

For every held-out frame: colour-fit PSNR of a held-out model; the same after an ECC homography warp of the render onto
the photo (meant as a rotation-error measure; unreliable on blank walls, TRAINING R-084: use eval_align.py); PSNR of a model that trained on the frame (seen);
3D observations of the frame in the SfM model (image support); time in the walk.

  nerfstudio-env/Scripts/python.exe src/arcore3dgs/eval_perframe.py --work <sfm dir with frames.json, offpath_test.txt, sparse/0, images>
      --held <ply> --seen <ply> --out <csv>
"""
import argparse, json, os
import numpy as np, cv2, torch, torch.nn.functional as F
from plyfile import PlyData
from gsplat import rasterization

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True); ap.add_argument("--held", required=True); ap.add_argument("--seen", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
dev = "cuda"; G = np.diag([1, -1, -1, 1.0])
meta = json.load(open(os.path.join(a.work, "frames.json"))); by = {f["name"]: f for f in meta["frames"]}
test = open(os.path.join(a.work, "offpath_test.txt")).read().split()
W, H = meta["W"], meta["H"]
Kh = torch.tensor([[[meta["fx"] / 2, 0, meta["cx"] / 2], [0, meta["fy"] / 2, meta["cy"] / 2], [0, 0, 1]]], dtype=torch.float32, device=dev)


def load(path):
    v = PlyData.read(path)["vertex"]; c = lambda n: torch.tensor(np.asarray(v[n]), dtype=torch.float32, device=dev)
    m = torch.stack([c("x"), c("y"), c("z")], 1); nr = len([n for n in v.data.dtype.names if n.startswith("f_rest")])
    col = torch.stack([c(f"f_dc_{i}") for i in range(3)], 1)[:, None]
    if nr:
        col = torch.cat([col, torch.stack([c(f"f_rest_{i}") for i in range(nr)], 1).reshape(len(m), 3, -1).transpose(1, 2)], 1)
    return dict(means=m, quats=F.normalize(torch.stack([c(f"rot_{i}") for i in range(4)], 1), dim=-1),
                scales=torch.exp(torch.stack([c(f"scale_{i}") for i in range(3)], 1)), opac=torch.sigmoid(c("opacity")),
                col=col, sh=int(round(np.sqrt(col.shape[1]))) - 1)


@torch.no_grad()
def render(g, c2w):
    w2c = torch.tensor(np.linalg.inv(np.array(c2w) @ G), dtype=torch.float32, device=dev)[None]
    out, _, _ = rasterization(g["means"], g["quats"], g["scales"], g["opac"], g["col"], w2c, Kh, W // 2, H // 2, sh_degree=g["sh"])
    return out[0].clamp(0, 1).cpu().numpy()


def photo(n):
    im = cv2.resize(cv2.imread(os.path.join(a.work, "images", n + ".jpg")), (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(im, cv2.COLOR_BGR2RGB).astype(np.float32) / 255


def psnr_cf(r, gt, mask=None):
    m = np.ones(gt.shape[:2], bool) if mask is None else mask
    A = np.c_[r[m].reshape(-1, 3), np.ones(m.sum())]
    ra = np.clip(A @ np.linalg.lstsq(A, gt[m].reshape(-1, 3), rcond=None)[0], 0, 1)
    return float(-10 * np.log10(((ra - gt[m].reshape(-1, 3)) ** 2).mean()))


def warp(r, gt):
    """ECC homography render -> photo; returns warped render, valid mask, corner shift (px, half res)"""
    g1 = cv2.cvtColor((r * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    g2 = cv2.cvtColor((gt * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    Hm = np.eye(3, dtype=np.float32)
    try:
        _, Hm = cv2.findTransformECC(g2, g1, Hm, cv2.MOTION_HOMOGRAPHY,
                                     (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-5), None, 5)
    except cv2.error:
        return r, np.ones(gt.shape[:2], bool), float("nan")
    h, w = gt.shape[:2]
    rw = cv2.warpPerspective(r, Hm, (w, h), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    m = cv2.warpPerspective(np.ones((h, w), np.uint8), Hm, (w, h), flags=cv2.INTER_NEAREST + cv2.WARP_INVERSE_MAP) > 0
    cn = np.array([[0, 0, 1], [w, 0, 1], [0, h, 1], [w, h, 1]], np.float32).T
    q = Hm @ cn; q = q[:2] / q[2]
    return rw, m, float(np.linalg.norm(q - cn[:2], axis=0).max())


# 3D observations per image in the SfM model
L = [l for l in open(os.path.join(a.work, "sparse", "0", "images.txt")) if not l.startswith("#")]
n3d = {}
for hdr, pts in zip(L[0::2], L[1::2]):
    name = os.path.splitext(hdr.split()[9])[0]
    n3d[name] = sum(1 for t in pts.split()[2::3] if t != "-1")

gh, gs = load(a.held), load(a.seen)
rows = []
for n in sorted(test, key=lambda n: by[n]["pts"]):
    gt = photo(n); rh = render(gh, by[n]["c2w"]); rs = render(gs, by[n]["c2w"])
    rw, m, shift = warp(rh, gt)
    rows.append((n, by[n]["pts"], n3d.get(n, -1), psnr_cf(rh, gt), psnr_cf(rw, gt, m),
                 shift, psnr_cf(rs, gt)))
t0 = min(f["pts"] for f in meta["frames"])
with open(a.out, "w") as f:
    f.write("name,t_s,obs3d,psnr_held,psnr_held_warped,warp_shift_px,psnr_seen\n")
    for r in rows:
        f.write(f"{r[0]},{r[1] - t0:.2f},{r[2]},{r[3]:.2f},{r[4]:.2f},{r[5]:.1f},{r[6]:.2f}\n")
R = np.array([r[2:] for r in rows], float)
print(f"{len(rows)} frames; held {R[:,1].mean():.2f}, held+warp {R[:,2].mean():.2f}, seen {R[:,4].mean():.2f}; "
      f"warp shift median {np.nanmedian(R[:,3]):.1f} px (half res)")
