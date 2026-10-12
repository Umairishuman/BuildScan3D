"""Fair comparison of models trained on DIFFERENT frame sets / SfM solutions of the same recording.

Reference = the v3 work dir (its undistorted photos + intrinsics). Test frames = the reference's nerfstudio
held-out frames that no compared model trained on. Each model lives in its own metric world (Sim3-aligned
to ARCore separately); a Sim3 from the reference world into each model's world is estimated from the frames
both share, and every test / room-centre camera is mapped through it.

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/fair_compare.py --ref_work <work_sfm> --out <dir>
      --models v3=<ply>@<work_sfm> sharp=<ply>@<work_sharp_sfm> ...
Writes metrics.json, heldout.jpg (photo | models), centre.jpg, crops.jpg (full-res crops).
"""
import os, json, argparse, numpy as np, cv2, torch, torch.nn.functional as F
from plyfile import PlyData
from gsplat import rasterization
from pytorch_msssim import ssim

ap = argparse.ArgumentParser()
ap.add_argument("--ref_work", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--models", nargs="+", required=True, help="name=splat.ply@work_dir")
args = ap.parse_args()
dev = "cuda"; os.makedirs(args.out, exist_ok=True); G = np.diag([1, -1, -1, 1.0])
ref = json.load(open(os.path.join(args.ref_work, "frames.json"))); rf = {f["name"]: f for f in ref["frames"]}
W, H = ref["W"], ref["H"]


def ns_split(names):
    n = len(names); tr = set(np.linspace(0, n - 1, int(np.ceil(n * 0.9)), dtype=int).tolist())
    return {names[i] for i in tr}


def sim3(A, B):
    ma, mb = A.mean(0), B.mean(0); s = np.sqrt(((B - mb) ** 2).sum() / ((A - ma) ** 2).sum())
    U, _, Vt = np.linalg.svd((B - mb).T @ (A - ma)); R = U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt
    return s, R, mb - s * R @ ma


def load(path):
    v = PlyData.read(path)["vertex"]; c = lambda n: torch.tensor(np.asarray(v[n]), dtype=torch.float32, device=dev)
    m = torch.stack([c("x"), c("y"), c("z")], 1); nr = len([n for n in v.data.dtype.names if n.startswith("f_rest")])
    col = torch.cat([torch.stack([c(f"f_dc_{i}") for i in range(3)], 1)[:, None],
                     torch.stack([c(f"f_rest_{i}") for i in range(nr)], 1).reshape(len(m), 3, -1).transpose(1, 2)], 1)
    return dict(means=m, quats=F.normalize(torch.stack([c(f"rot_{i}") for i in range(4)], 1), dim=-1),
                scales=torch.exp(torch.stack([c(f"scale_{i}") for i in range(3)], 1)), opac=torch.sigmoid(c("opacity")),
                col=col, sh=int(round(np.sqrt(col.shape[1]))) - 1, n=len(m))


models = []; trained = set()
for spec in args.models:
    name, rest = spec.split("=", 1); ply, work = rest.rsplit("@", 1)
    meta = json.load(open(os.path.join(work, "frames.json"))); names = [f["name"] for f in meta["frames"]]
    trained |= ns_split(names); by = {f["name"]: f for f in meta["frames"]}
    common = [n for n in names if n in rf]
    Aa = np.array([np.array(rf[n]["c2w"])[:3, 3] for n in common]); Bb = np.array([np.array(by[n]["c2w"])[:3, 3] for n in common])
    keep = np.ones(len(common), bool)
    for _ in range(5):                                            # trimmed: ignore cameras one model mis-registered
        s, R, t = sim3(Aa[keep], Bb[keep]); res = np.linalg.norm((s * (R @ Aa.T)).T + t - Bb, axis=1)
        keep = res < max(0.005, 3 * np.median(res[keep]))
    bad_pose = {n for n, k in zip(common, keep) if not k}
    res = res[keep]
    print(f"{name}: {len(names)} frames, ref->model Sim3 from {len(common)} common frames, scale {s:.5f}, "
          f"residual median {np.median(res) * 100:.2f} cm", flush=True)
    models.append(dict(name=name, g=load(ply), s=s, R=R, t=t, bad_pose=bad_pose))
test = [n for n in [f["name"] for f in ref["frames"]] if n not in trained and not any(n in m["bad_pose"] for m in models)]
print(f"{len(test)} test frames not trained on by any model")
K = torch.tensor([[[ref["fx"] / 2, 0, ref["cx"] / 2], [0, ref["fy"] / 2, ref["cy"] / 2], [0, 0, 1]]], dtype=torch.float32, device=dev)
Kf = torch.tensor([[[ref["fx"], 0, ref["cx"]], [0, ref["fy"], ref["cy"]], [0, 0, 1]]], dtype=torch.float32, device=dev)


def to_model(m, c2w_ref):
    c = np.array(c2w_ref, dtype=np.float64).copy(); out = np.eye(4)
    out[:3, :3] = m["R"] @ c[:3, :3]; out[:3, 3] = m["s"] * m["R"] @ c[:3, 3] + m["t"]
    return out


@torch.no_grad()
def render(m, c2w_ref, full=False):
    w2c = torch.tensor(np.linalg.inv(to_model(m, c2w_ref) @ G), dtype=torch.float32, device=dev)[None]
    g = m["g"]; w, h = (W, H) if full else (W // 2, H // 2)
    out, _, _ = rasterization(g["means"], g["quats"], g["scales"], g["opac"], g["col"], w2c, Kf if full else K, w, h, sh_degree=g["sh"])
    return out[0].clamp(0, 1)


def photo(n, full=False):
    im = cv2.imread(os.path.join(args.ref_work, "images", n + ".jpg"))
    if not full:
        im = cv2.resize(im, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    return torch.from_numpy(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).to(dev).float() / 255


def lap(x):
    return cv2.Laplacian(cv2.cvtColor((x * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY), cv2.CV_64F).var()


@torch.no_grad()
def cf_psnr(r, gt):
    A = torch.cat([r.reshape(-1, 3), torch.ones(r.shape[0] * r.shape[1], 1, device=dev)], 1)
    ra = (A @ torch.linalg.lstsq(A, gt.reshape(-1, 3)).solution).reshape(gt.shape).clamp(0, 1)
    return float(-10 * torch.log10(((ra - gt) ** 2).mean()))


best = {n: max(cf_psnr(render(m, rf[n]["c2w"]), photo(n)) for m in models) for n in test}
dropped = [n for n in test if best[n] < 17.0]
test = [n for n in test if best[n] >= 17.0]
print(f"{len(test)} test frames ({len(dropped)} dropped: every model < 17 dB there = reference pose wrong: {dropped})")
res = {}
for m in models:
    ps, ss, sh = [], [], []
    for n in test:
        gt = photo(n); r = render(m, rf[n]["c2w"])
        A = torch.cat([r.reshape(-1, 3), torch.ones(r.shape[0] * r.shape[1], 1, device=dev)], 1)
        ra = (A @ torch.linalg.lstsq(A, gt.reshape(-1, 3)).solution).reshape(gt.shape).clamp(0, 1)
        ps.append(float(-10 * torch.log10(((ra - gt) ** 2).mean())))
        ss.append(float(ssim(ra.permute(2, 0, 1)[None], gt.permute(2, 0, 1)[None], data_range=1.0)))
        sh.append(lap(r.cpu().numpy()) / max(lap(gt.cpu().numpy()), 1e-6))
    res[m["name"]] = dict(splats=m["g"]["n"], psnr_cf=float(np.mean(ps)), ssim=float(np.mean(ss)), sharpness=float(np.mean(sh)),
                          n_test=len(test))
    print(f"{m['name']:14s} splats {m['g']['n']:8d}  PSNR(cf) {np.mean(ps):6.2f}  SSIM {np.mean(ss):.4f}  sharpness {np.mean(sh):.2f}", flush=True)
json.dump(res, open(os.path.join(args.out, "metrics.json"), "w"), indent=1)


def lab(img, t, rot=True):
    img = np.ascontiguousarray(cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) if rot else img)
    cv2.putText(img, t, (8, 30), 0, 0.9, (0, 0, 0), 5); cv2.putText(img, t, (8, 30), 0, 0.9, (0, 255, 255), 2)
    return img


bgr = lambda x: (x.cpu().numpy()[..., ::-1] * 255).astype(np.uint8)
pick = [test[k] for k in np.linspace(0, len(test) - 1, 5).astype(int)]
rows = [np.hstack([lab(bgr(photo(n)), "photo")] + [lab(bgr(render(m, rf[n]["c2w"])), m["name"]) for m in models]) for n in pick]
cv2.imwrite(os.path.join(args.out, "heldout.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
# full-res 1:1 crops (centre 480x480) of 4 test frames: sharpness vs the source photo
rows = []
for n in pick[:4]:
    cy, cx, s_ = H // 2, W // 2, 240
    tiles = [bgr(photo(n, True))[cy - s_:cy + s_, cx - s_:cx + s_]] + [bgr(render(m, rf[n]["c2w"], True))[cy - s_:cy + s_, cx - s_:cx + s_] for m in models]
    rows.append(np.hstack([lab(t, l) for t, l in zip(tiles, ["photo"] + [m["name"] for m in models])]))
cv2.imwrite(os.path.join(args.out, "crops.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 92])
UP = np.array([0.0, 1, 0]); c = np.array([np.array(f["c2w"])[:3, 3] for f in ref["frames"]]).mean(0)


def look(pos, tgt):
    fw = tgt - pos; fw /= np.linalg.norm(fw); r = np.cross(fw, UP); r /= np.linalg.norm(r); u = np.cross(r, fw)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = r, u, -fw, pos
    return m @ np.array([[0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1.0]])


rows = []
for k, a in enumerate(np.radians([0, 90, 180, 270])):
    c2w = look(c, c + np.array([np.cos(a), -0.35, np.sin(a)]))
    rows.append(np.hstack([lab(bgr(render(m, c2w)), f"{m['name']} centre {k * 90}") for m in models]))
cv2.imwrite(os.path.join(args.out, "centre.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
print("sheets ->", args.out)
