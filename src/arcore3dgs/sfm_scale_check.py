"""SfM scale-consistency check: finds parts of a COLMAP model that were rebuilt at the wrong scale ("mini room").

For every frame: median of (SfM point depth / raw Metric3D depth) at the frame's observed SfM points, using the
Metric3D maps that mono_prior.py saved (<work>/mono_prior/*.npz + stats.json; raw = (depth - shift) / scale).
A consistent model has a roughly constant ratio; a block of frames far below the median is a shrunken sub-model.
Found on scan_3028a4de8fa0 (lecture hall, TRAINING R-036/R-037): GLOMAP put 175 frames at ~0.38x; newRoom: 0 frames.

  python src/arcore3dgs/sfm_scale_check.py <COLMAP TXT model dir> <work>/mono_prior [--width 1920]
(binary model -> TXT: colmap model_converter --input_path sparse/0 --output_path <dir> --output_type TXT)
"""
import sys, os, json, numpy as np
def qrot(q):
    w, x, y, z = q
    return np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],[2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],[2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])
import argparse
ap = argparse.ArgumentParser(); ap.add_argument("model"); ap.add_argument("mono_prior")
ap.add_argument("--width", type=int, default=1920, help="width of the keyframes the model was made from")
args = ap.parse_args(); md, mp = args.model, args.mono_prior
P = {}
for l in open(os.path.join(md, "points3D.txt")):
    if l[0] != "#":
        s = l.split(); P[int(s[0])] = np.array(s[1:4], float)
st = json.load(open(os.path.join(mp, "stats.json")))
L = [l for l in open(os.path.join(md, "images.txt")) if l[0] != "#"]
res = {}
for a, b in zip(L[0::2], L[1::2]):
    s = a.split(); name = s[9][:-4]
    if name not in st: continue
    R = qrot(np.array(s[1:5], float)); t = np.array(s[5:8], float)
    o = np.array(b.split(), float).reshape(-1, 3); o = o[o[:, 2] >= 0]
    if len(o) < 20: continue
    X = np.array([P[int(i)] for i in o[:, 2] if int(i) in P]); uv = o[[int(i) in P for i in o[:, 2]], :2]
    z = (X @ R.T + t)[:, 2]
    m = np.load(os.path.join(mp, name + ".npz")); D = m["depth"].astype(np.float32); h, w = D.shape
    raw = (D - st[name]["shift"]) / st[name]["scale"]; d = args.width / w
    px = np.clip((uv[:, 0] / d).astype(int), 0, w - 1); py = np.clip((uv[:, 1] / d).astype(int), 0, h - 1)
    r = raw[py, px]; ok = (z > 0) & (r > 0.1)
    if ok.sum() >= 20: res[name] = np.median(z[ok] / r[ok])
k = sorted(res); a = np.array([res[n] for n in k]); g = np.median(a)
print(f"{len(k)} frames, ratio median {g:.3f} (model units per Metric3D metre)")
for i in range(0, len(k), 40):
    w_ = a[i:i+40] / g
    print(f"{k[i]}  rel. scale median {np.median(w_):.2f}  p10 {np.percentile(w_,10):.2f}  p90 {np.percentile(w_,90):.2f}")
print(f"frames at < 0.5x of the median: {(a/g < 0.5).sum()}, > 2x: {(a/g > 2).sum()}")
