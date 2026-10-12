"""Grazing-angle comparison sheet: look along each room-shell wall and across the floor (where fuzzy,
non-flat surfaces show most), for several models side by side. Uses planes.json from planarize.py.

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/grazing_views.py --work <work_sfm> --planes <planes.json>
      --out <dir> --models v3=<ply> planar=<ply>
"""
import os, json, argparse, numpy as np, cv2, torch, torch.nn.functional as F
from plyfile import PlyData
from gsplat import rasterization

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True); ap.add_argument("--planes", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--models", nargs="+", required=True)
args = ap.parse_args()
dev = "cuda"; os.makedirs(args.out, exist_ok=True)
meta = json.load(open(os.path.join(args.work, "frames.json")))
W, H = 960, 540; f = meta["fx"] / meta["W"] * W
K = torch.tensor([[[f, 0, W / 2], [0, f, H / 2], [0, 0, 1]]], dtype=torch.float32, device=dev)
G = np.diag([1, -1, -1, 1.0]); UP = np.array([0.0, 1, 0])


def load(path):
    v = PlyData.read(path)["vertex"]; c = lambda n: torch.tensor(np.asarray(v[n]), dtype=torch.float32, device=dev)
    m = torch.stack([c("x"), c("y"), c("z")], 1)
    nr = len([n for n in v.data.dtype.names if n.startswith("f_rest")])
    col = torch.cat([torch.stack([c(f"f_dc_{i}") for i in range(3)], 1)[:, None],
                     torch.stack([c(f"f_rest_{i}") for i in range(nr)], 1).reshape(len(m), 3, -1).transpose(1, 2)], 1)
    return dict(means=m, quats=F.normalize(torch.stack([c(f"rot_{i}") for i in range(4)], 1), dim=-1),
                scales=torch.exp(torch.stack([c(f"scale_{i}") for i in range(3)], 1)),
                opac=torch.sigmoid(c("opacity")), col=col, sh=int(round(np.sqrt(col.shape[1]))) - 1)


def look(pos, tgt):
    fw = tgt - pos; fw /= np.linalg.norm(fw); r = np.cross(fw, UP); r /= np.linalg.norm(r); u = np.cross(r, fw)
    c2w = np.eye(4); c2w[:3, 0], c2w[:3, 1], c2w[:3, 2], c2w[:3, 3] = r, u, -fw, pos
    return c2w


@torch.no_grad()
def render(g, c2w):
    w2c = torch.tensor(np.linalg.inv(c2w @ G), dtype=torch.float32, device=dev)[None]
    out, _, _ = rasterization(g["means"], g["quats"], g["scales"], g["opac"], g["col"], w2c, K, W, H, sh_degree=g["sh"])
    return (out[0].clamp(0, 1).cpu().numpy()[..., ::-1] * 255).astype(np.uint8)


models = [(s.split("=", 1)[0], load(s.split("=", 1)[1])) for s in args.models]
pl = json.load(open(args.planes))["planes"]
C = np.array([np.array(x["c2w"])[:3, 3] for x in meta["frames"]]); c = C.mean(0)
floor = next(p for p in pl if p["kind"] == "floor")["d"]
views = []
for k, p in enumerate([p for p in pl if p["kind"] == "wall"]):
    n = np.array(p["n"]); s = 1 if c @ n - p["d"] > 0 else -1                 # side of the room centre
    foot = c - (c @ n - p["d"]) * n; t = np.cross(n, UP)
    pos = foot + s * 0.7 * n; pos[1] = floor + 1.3
    views.append((f"wall {k} grazing", look(pos, pos + 2.5 * t - s * 0.35 * n + np.array([0, -0.2, 0]))))
pos = c.copy(); pos[1] = floor + 0.45
views.append(("floor grazing", look(pos, pos + np.array([1.0, -0.12, 0.3]))))
for vi in range(0, len(views), 3):
    rows = []
    for name, c2w in views[vi:vi + 3]:
        row = []
        for mn, g in models:
            im = np.ascontiguousarray(render(g, c2w))
            cv2.putText(im, f"{mn}: {name}", (8, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4)
            cv2.putText(im, f"{mn}: {name}", (8, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            row.append(im)
        rows.append(np.hstack(row))
    cv2.imwrite(os.path.join(args.out, f"grazing_{vi // 3}.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
print("sheets ->", args.out)
