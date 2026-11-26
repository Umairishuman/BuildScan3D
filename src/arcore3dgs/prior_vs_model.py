"""Compare depth-prior variants with the depth a trained model renders at the same cameras (offline check before a
training run, R-133). Per time window: median relative depth difference on the prior's valid pixels, the share of
frames that have a prior, and DA3's median confidence (if the variant stored it in stats.json).

  nerfstudio-env python src/arcore3dgs/prior_vs_model.py --work <work_sfm> --ply <splat.ply> \
      --priors mono_prior mono_prior_da3chain ... [--windows 0,30,50,60,90,134,140,200] [--sheet out.jpg --sheet_t 52,56,58]
"""
import argparse, json, os, sys
import numpy as np, cv2, torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from offpath_views import load, render  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True); ap.add_argument("--ply", required=True)
ap.add_argument("--priors", nargs="+", required=True)
ap.add_argument("--windows", default="0,30,50,60,90,134,140,200")
ap.add_argument("--sheet", default=""); ap.add_argument("--sheet_t", default="52,55,58")
ap.add_argument("--consistency", action="store_true",
                help="no model reference: do the priors of frames 1-3 apart agree in 3D when placed with OUR cameras "
                     "(the ones training uses)? median |z_i->j - D_j| / D_j per pair, median per window")
a = ap.parse_args()
if a.consistency:
    meta = json.load(open(os.path.join(a.work, "frames.json"))); fr = meta["frames"]
    d0 = np.load(os.path.join(a.work, a.priors[0], fr[0]["name"] + ".npz"))["depth"]; h, w = d0.shape
    sx, sy = w / meta["W"], h / meta["H"]
    fx, fy, cx, cy = meta["fx"] * sx, meta["fy"] * sy, meta["cx"] * sx, meta["cy"] * sy
    G = np.diag([1, -1, -1, 1.0])
    vv, uu = np.mgrid[2:h:4, 2:w:4]
    win = [float(x) for x in a.windows.split(",")]
    print("prior consistency with our cameras: median |z_i->j - D_j| / D_j, pairs 1-3 frames apart (both valid)")
    for lo, hi in zip(win[:-1], win[1:]):
        fs = [f for f in fr if lo <= f["pts"] < hi]
        line = f"{lo:5.0f}-{hi:<5.0f}s {len(fs):3d} frames"
        for p in a.priors:
            L = {f["name"]: np.load(os.path.join(a.work, p, f["name"] + ".npz")) for f in fs}
            errs = []
            for i in range(len(fs)):
                Di = L[fs[i]["name"]]["depth"].astype(np.float32)[vv, uu]; Vi = L[fs[i]["name"]]["valid"][vv, uu]
                if Vi.mean() < 0.05:
                    continue
                Pc = np.stack([(uu - cx) / fx * Di, (vv - cy) / fy * Di, Di], -1)[Vi]
                Ci = np.array(fs[i]["c2w"]) @ G; Pw = Pc @ Ci[:3, :3].T + Ci[:3, 3]
                for j in range(i + 1, min(i + 4, len(fs))):
                    Dj = L[fs[j]["name"]]["depth"].astype(np.float32); Vj = L[fs[j]["name"]]["valid"]
                    if Vj.mean() < 0.05:
                        continue
                    Cj = np.array(fs[j]["c2w"]) @ G; Q = (Pw - Cj[:3, 3]) @ Cj[:3, :3]
                    z = Q[:, 2]; ok = z > 0.1
                    u = np.round(Q[ok, 0] / z[ok] * fx + cx).astype(int); v = np.round(Q[ok, 1] / z[ok] * fy + cy).astype(int)
                    ins = (u >= 0) & (u < w) & (v >= 0) & (v < h)
                    if ins.sum() < 50:
                        continue
                    u, v, zz = u[ins], v[ins], z[ok][ins]; m = Vj[v, u]
                    if m.sum() < 50:
                        continue
                    errs.append(np.median(np.abs(zz[m] - Dj[v[m], u[m]]) / Dj[v[m], u[m]]))
            e = f"{100 * np.median(errs):5.1f}% ({len(errs):3d} pairs)" if errs else "   -  (  0 pairs)"
            line += f" | {p[11:] or 'metric3d'}: {e}"
        print(line, flush=True)
    sys.exit(0)
meta = json.load(open(os.path.join(a.work, "frames.json"))); fr = meta["frames"]
d0 = np.load(os.path.join(a.work, a.priors[0], fr[0]["name"] + ".npz"))["depth"]; h, w = d0.shape
sx, sy = w / meta["W"], h / meta["H"]
K = np.array([[meta["fx"] * sx, 0, meta["cx"] * sx], [0, meta["fy"] * sy, meta["cy"] * sy], [0, 0, 1.0]])
G = np.diag([1, -1, -1, 1.0])
g = load(a.ply)
stats = {p: json.load(open(os.path.join(a.work, p, "stats.json"))) for p in a.priors}
ref = {}
with torch.no_grad():
    for f in fr:
        _, D = render(g, np.linalg.inv(np.array(f["c2w"]) @ G), K, w, h)
        ref[f["name"]] = D
win = [float(x) for x in a.windows.split(",")]
print(f"reference: {a.ply}; median |prior - model| / model on valid prior pixels, per frame then median per window")
for lo, hi in zip(win[:-1], win[1:]):
    names = [f["name"] for f in fr if lo <= f["pts"] < hi]
    unsup = [n for n in names if stats[a.priors[0]][n]["n_sfm"] < 5]
    line = f"{lo:5.0f}-{hi:<5.0f}s {len(names):3d} frames ({len(unsup):3d} without SfM)"
    for p in a.priors:
        errs, has, cf = [], 0, []
        for n in names:
            z = np.load(os.path.join(a.work, p, n + ".npz")); D = z["depth"].astype(np.float32); V = z["valid"]
            R = ref[n]; m = V & (R > 0.1)
            if "conf_med" in stats[p][n]:
                cf.append(stats[p][n]["conf_med"])
            if m.mean() < 0.05:
                continue
            has += 1; errs.append(np.median(np.abs(D[m] - R[m]) / R[m]))
        e = f"{100 * np.median(errs):5.1f}%" if errs else "   - "
        c = f" conf {np.median(cf):.2f}" if cf else ""
        line += f" | {p[11:] or 'metric3d'}: {e} on {has:3d}{c}"
    print(line, flush=True)
if a.sheet:
    rows = []
    for t in [float(x) for x in a.sheet_t.split(",")]:
        f = min(fr, key=lambda x: abs(x["pts"] - t)); n = f["name"]
        img = cv2.resize(cv2.imread(os.path.join(a.work, "images", n + ".jpg")), (w, h))
        R = ref[n]; hi_ = np.percentile(R[R > 0], 98) if (R > 0).any() else 5
        cm = lambda D: cv2.applyColorMap((np.clip(D / hi_, 0, 1) * 255).astype(np.uint8), cv2.COLORMAP_TURBO)
        tiles = [img, cm(R)]
        for p in a.priors:
            z = np.load(os.path.join(a.work, p, n + ".npz")); c = cm(z["depth"].astype(np.float32))
            c[~z["valid"]] = (c[~z["valid"]] * 0.25).astype(np.uint8); tiles.append(c)
        row = np.hstack(tiles)
        cv2.putText(row, f"{f['pts']:.1f}s sfm={stats[a.priors[0]][n]['n_sfm']} | photo | model | " + " | ".join(p[11:] or "metric3d" for p in a.priors),
                    (6, 20), 0, 0.55, (255, 255, 255), 2)
        rows.append(row)
    cv2.imwrite(a.sheet, np.vstack(rows))
    print(a.sheet)
