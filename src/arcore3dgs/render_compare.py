"""Compare two scan_009 models on the keyframes both kept: PSNR per model over all common frames (half res),
and a photo | A | B sheet for 8 of them (training views, not held out; R-081 vs R-071). Moved here from a
scratchpad 2026-11-21.

  nerfstudio-env/Scripts/python.exe src/arcore3dgs/render_compare.py <sfmA> <plyA> <sfmB> <plyB> <out_prefix>
"""
import sys, os, json, numpy as np, cv2, torch
from plyfile import PlyData
from gsplat import rasterization
SA, PA, SB, PB, outp = sys.argv[1:6]; dev = "cuda"; G = np.diag([1, -1, -1, 1.0])
t = lambda a: torch.tensor(np.asarray(a), dtype=torch.float32, device=dev)


def load(S, ply):
    meta = json.load(open(os.path.join(S, "frames.json")))
    v = PlyData.read(ply)["vertex"]; P = np.c_[v["x"], v["y"], v["z"]]
    q = np.c_[v["rot_0"], v["rot_1"], v["rot_2"], v["rot_3"]]; sc = np.exp(np.c_[v["scale_0"], v["scale_1"], v["scale_2"]])
    op = 1 / (1 + np.exp(-np.asarray(v["opacity"]))); sh0 = np.c_[v["f_dc_0"], v["f_dc_1"], v["f_dc_2"]]
    rest = sorted([n for n in v.data.dtype.names if n.startswith("f_rest_")], key=lambda s: int(s.split("_")[-1]))
    shr = np.stack([v[n] for n in rest], 1).reshape(len(P), 3, -1).transpose(0, 2, 1) if rest else np.zeros((len(P), 0, 3))
    sh = np.concatenate([sh0[:, None], shr], 1)
    W, H = meta["W"] // 2, meta["H"] // 2
    K = t([[meta["fx"] / 2, 0, meta["cx"] / 2], [0, meta["fy"] / 2, meta["cy"] / 2], [0, 0, 1]])[None]
    return dict(meta=meta, fr={f["name"]: f for f in meta["frames"]}, g=(t(P), t(q), t(sc), t(op), t(sh)),
                deg=int(np.sqrt(sh.shape[1])) - 1, W=W, H=H, K=K, S=S)


def render(m, name):
    c2w = np.array(m["fr"][name]["c2w"]) @ G
    img, _, _ = rasterization(*m["g"], t(np.linalg.inv(c2w))[None], m["K"], m["W"], m["H"], sh_degree=m["deg"])
    return (img[0].clamp(0, 1).cpu().numpy()[..., ::-1] * 255).astype(np.uint8)


A, B = load(SA, PA), load(SB, PB)
common = sorted(set(A["fr"]) & set(B["fr"]), key=lambda n: A["fr"][n]["pts"])
ps = {"A": [], "B": []}
for n in common:
    for k, m in (("A", A), ("B", B)):
        ph = cv2.resize(cv2.imread(os.path.join(m["S"], "images", n + ".jpg")), (m["W"], m["H"])).astype(np.float32)
        r = render(m, n).astype(np.float32)
        ps[k].append(10 * np.log10(255 ** 2 / max(np.mean((r - ph) ** 2), 1e-6)))
pa, pb = np.array(ps["A"]), np.array(ps["B"])
print(f"common frames {len(common)}: PSNR A median {np.median(pa):.2f} mean {pa.mean():.2f} | B median {np.median(pb):.2f} "
      f"mean {pb.mean():.2f} | B better on {np.mean(pb > pa) * 100:.0f}% of frames, by median {np.median(pb - pa):+.2f} dB")
rows = []
for n in [common[int(i)] for i in np.linspace(0, len(common) - 1, 8)]:
    ph = cv2.resize(cv2.imread(os.path.join(SA, "images", n + ".jpg")), (A["W"], A["H"]))
    ra, rb = render(A, n), cv2.resize(render(B, n), (A["W"], A["H"]))
    row = np.hstack([ph, ra, rb]); cv2.putText(row, f"{A['fr'][n]['pts']:.0f}s", (10, 40), 0, 1.2, (0, 255, 255), 3)
    rows.append(cv2.resize(row, (1440, 270)))
cv2.imwrite(outp + "_compare.jpg", np.vstack(rows))
