"""Fixed off-path views of trained splats, for judging what the near-path held-out scores miss
(FEATURELESS_TRACKING_PLAN §11.e).

Tayyab judges scan_009 by moving away from the recorded path in the viewer (2026-11-21: "coherent only from the
recorded angles"). Held-out frames lie on the path, so they cannot show it. Per model this renders:
  - a ring of --n views from the room centre (median camera position, camera height), horizontal, 90 deg wide;
  - a cut-away plan: only the splats in a horizontal slice from --low below to --cut above the median camera
    height (walls, no floor / ceiling), orthographic view from above. Walls built once show as single lines; walls built at several places (drift) as parallel copies.
Colour and depth (turbo, same range for every view of a model). Every model is rendered in its own coordinates
(its own cameras), so the views of two models from different camera solutions are similar, not identical.

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/offpath_views.py --out <dir>
      --models name=<splat.ply>@<sfm dir with frames.json> [...] [--n 8] [--cut 0.5]
Writes <out>/<name>_ring.jpg, <out>/<name>_plan.jpg and <out>/compare_ring.jpg, <out>/compare_plan.jpg.
"""
import argparse
import json
import os

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from gsplat import rasterization
from plyfile import PlyData

dev = "cuda"
G = np.diag([1, -1, -1, 1.0])


def load(path):
    v = PlyData.read(path)["vertex"]; c = lambda n: torch.tensor(np.asarray(v[n]), dtype=torch.float32, device=dev)
    m = torch.stack([c("x"), c("y"), c("z")], 1); nr = len([n for n in v.data.dtype.names if n.startswith("f_rest")])
    col = torch.stack([c(f"f_dc_{i}") for i in range(3)], 1)[:, None]
    if nr:
        col = torch.cat([col, torch.stack([c(f"f_rest_{i}") for i in range(nr)], 1).reshape(len(m), 3, -1).transpose(1, 2)], 1)
    return dict(means=m, quats=F.normalize(torch.stack([c(f"rot_{i}") for i in range(4)], 1), dim=-1),
                scales=torch.exp(torch.stack([c(f"scale_{i}") for i in range(3)], 1)), opac=torch.sigmoid(c("opacity")),
                col=col, sh=int(round(np.sqrt(col.shape[1]))) - 1)


def render(g, w2c, K, W, H, keep=None, ortho=False):
    sel = (lambda x: x[keep]) if keep is not None else (lambda x: x)
    out, alpha, _ = rasterization(sel(g["means"]), sel(g["quats"]), sel(g["scales"]), sel(g["opac"]), sel(g["col"]),
                                  torch.tensor(w2c, dtype=torch.float32, device=dev)[None],
                                  torch.tensor(K, dtype=torch.float32, device=dev)[None], W, H, sh_degree=g["sh"],
                                  render_mode="RGB+ED", camera_model="ortho" if ortho else "pinhole")
    rgb = out[0, ..., :3] + (1 - alpha[0])                                  # white background
    rgb = (rgb.clamp(0, 1).cpu().numpy() * 255).astype(np.uint8)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), out[0, ..., 3].cpu().numpy()


def look(C, fwd, up=np.array([0, 1.0, 0])):
    """world-to-camera (OpenCV: x right, y down, z forward) for a camera at C looking along fwd"""
    z = fwd / np.linalg.norm(fwd); x = np.cross(z, up); x /= np.linalg.norm(x); y = np.cross(z, x)
    R = np.stack([x, y, z]); w2c = np.eye(4); w2c[:3, :3] = R; w2c[:3, 3] = -R @ C
    return w2c


def colour_depth(d, lo, hi):
    v = np.clip((d - lo) / max(hi - lo, 1e-6), 0, 1); im = cv2.applyColorMap((255 * (1 - v)).astype(np.uint8), cv2.COLORMAP_TURBO)
    im[d <= 0] = 255
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True); ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--n", type=int, default=8); ap.add_argument("--cut", type=float, default=0.5)
    ap.add_argument("--low", type=float, default=1.0, help="plan: splats lower than camera height - low removed (floor)")
    ap.add_argument("--size", type=int, default=480)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rings, plans = [], []
    for spec in a.models:
        name, rest = spec.split("=", 1); ply, sfm = rest.split("@", 1)
        g = load(ply)
        meta = json.load(open(os.path.join(sfm, "frames.json")))
        Cs = np.array([np.array(f["c2w"])[:3, 3] for f in meta["frames"]])
        ctr = np.median(Cs, axis=0)
        S = a.size; f_ = S / 2.0                                       # 90 deg wide
        K = np.array([[f_, 0, S / 2], [0, f_, S / 2], [0, 0, 1.0]])
        cols, deps = [], []
        for k in range(a.n):
            th = 2 * np.pi * k / a.n
            with torch.no_grad():
                rgb, d = render(g, look(ctr, np.array([np.sin(th), 0, np.cos(th)])), K, S, S)
            cols.append(rgb); deps.append(d)
        dv = np.concatenate([d[d > 0] for d in deps]) if any((d > 0).any() for d in deps) else np.array([0.0, 1.0])
        lo, hi = np.percentile(dv, 2), np.percentile(dv, 98)
        for k, rgb in enumerate(cols):
            cv2.putText(rgb, f"{name} yaw {360 * k // a.n}", (6, 20), 0, 0.55, (0, 0, 255), 2)
        ring = np.vstack([np.hstack(cols), np.hstack([colour_depth(d, lo, hi) for d in deps])])
        cv2.imwrite(os.path.join(a.out, f"{name}_ring.jpg"), ring, [cv2.IMWRITE_JPEG_QUALITY, 88]); rings.append(ring)

        # cut-away plan (orthographic from above), extent from the camera path + margin
        keep = (g["means"][:, 1] < float(ctr[1] + a.cut)) & (g["means"][:, 1] > float(ctr[1] - a.low))
        lo2 = np.percentile(Cs[:, [0, 2]], 1, axis=0) - 3.0; hi2 = np.percentile(Cs[:, [0, 2]], 99, axis=0) + 3.0
        span = float(max(hi2 - lo2)); P = 900; sc = P / span; mid = (lo2 + hi2) / 2
        top = np.array([mid[0], ctr[1] + a.cut + 20.0, mid[1]])
        w2c = look(top, np.array([0, -1.0, 0]), up=np.array([0, 0, -1.0]))
        Ko = np.array([[sc, 0, P / 2], [0, sc, P / 2], [0, 0, 1.0]])
        with torch.no_grad():
            rgb, d = render(g, w2c, Ko, P, P, keep=keep, ortho=True)
        for (x, z) in Cs[:, [0, 2]][::3]:                                # camera path
            p = w2c[:3, :3] @ np.array([x, ctr[1], z]) + w2c[:3, 3]
            u, v = int(sc * p[0] + P / 2), int(sc * p[1] + P / 2)
            if 0 <= u < P and 0 <= v < P:
                cv2.circle(rgb, (u, v), 2, (255, 120, 0), -1)
        cv2.putText(rgb, f"{name}: slice camera height -{a.low} .. +{a.cut}, from above (blue = camera path)", (8, 22), 0, 0.55,
                    (0, 0, 255), 2)
        cv2.imwrite(os.path.join(a.out, f"{name}_plan.jpg"), rgb, [cv2.IMWRITE_JPEG_QUALITY, 90]); plans.append(rgb)
        del g; torch.cuda.empty_cache()
        print(f"{name}: centre {ctr.round(2)}, ring depth range {lo:.2f} - {hi:.2f}", flush=True)
    w = max(r.shape[1] for r in rings)
    cv2.imwrite(os.path.join(a.out, "compare_ring.jpg"),
                np.vstack([cv2.resize(r, (w // 2, r.shape[0] * w // 2 // r.shape[1])) for r in rings]), [cv2.IMWRITE_JPEG_QUALITY, 85])
    cv2.imwrite(os.path.join(a.out, "compare_plan.jpg"), np.hstack(plans), [cv2.IMWRITE_JPEG_QUALITY, 88])


if __name__ == "__main__":
    main()
