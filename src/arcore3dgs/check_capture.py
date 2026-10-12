"""Validate a recording from the capture app BEFORE processing (takes ~1-2 min).

  python src/arcore3dgs/check_capture.py dataset/<scan_folder>

Checks: required files, video resolution/fps/duration, pose rate and gaps, tracking loss, live-IQA
levels, ARCore depth maps (count, validity), NaN rows in points.csv, and video<->pose sync (optical flow
vs pose rotation over the first ~60 s). Prints PASS / WARN / FAIL per item.
"""
import os, sys, json, subprocess
import numpy as np, cv2
from scipy.spatial.transform import Rotation as R

root = sys.argv[1]
ok_all = True


def report(level, msg):
    global ok_all
    if level == "FAIL":
        ok_all = False
    print(f"[{level:4s}] {msg}")


need = ["dataset.mp4", "poses.csv", "tracking.csv", "points.csv", "quality.csv", "meta.json", "depth"]
for f in need:
    report("PASS" if os.path.exists(os.path.join(root, f)) else "FAIL", f"{f} present")
if not os.path.exists(os.path.join(root, "dataset.mp4")) or not os.path.exists(os.path.join(root, "poses.csv")):
    sys.exit(1)

meta = json.load(open(os.path.join(root, "meta.json"))) if os.path.exists(os.path.join(root, "meta.json")) else {}
print("device:", meta.get("device"), "| image", meta.get("cpu_image_size"), "| fps", meta.get("fps_range"))

info = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                "stream=width,height,avg_frame_rate,nb_frames,duration", "-of", "json",
                                os.path.join(root, "dataset.mp4")])
st = json.loads(info)["streams"][0]
num, den = map(float, st["avg_frame_rate"].split("/"))
fps, dur = num / den, float(st.get("duration", 0))
report("PASS" if st["width"] >= 1920 else "WARN", f"video {st['width']}x{st['height']} @ {fps:.1f} fps, {dur:.0f} s")
report("PASS" if 60 <= dur <= 600 else "WARN", "duration 1-10 min")

P = np.loadtxt(os.path.join(root, "poses.csv"), delimiter=",")
P = P[np.argsort(P[:, 0], kind="stable")]; P = P[np.unique(P[:, 0], return_index=True)[1]]
t = (P[:, 0] - P[0, 0]) / 1e9; dt = np.diff(t)
report("PASS" if len(t) / max(t[-1], 1) > 20 else "WARN", f"poses: {len(t)} at {len(t) / max(t[-1], 1):.1f} Hz, "
       f"{int((dt > 0.5).sum())} gaps > 0.5 s (longest {dt.max():.1f} s)")

trk = [l.strip().split(",") for l in open(os.path.join(root, "tracking.csv")) if l[:1].isdigit()]
lost = np.mean([r[1] != "TRACKING" for r in trk]) if trk else 1
report("PASS" if lost < 0.05 else ("WARN" if lost < 0.15 else "FAIL"), f"tracking lost {lost * 100:.1f}% of frames")

if os.path.exists(os.path.join(root, "quality.csv")):
    q = [l.split(",")[1] for l in open(os.path.join(root, "quality.csv")).readlines()[1:]]
    g = {k: q.count(k) / max(1, len(q)) for k in ("GOOD", "WARN", "BAD")}
    report("PASS" if g["BAD"] < 0.1 else "WARN", f"live IQA: good {g['GOOD'] * 100:.0f}% / ok {g['WARN'] * 100:.0f}% / bad {g['BAD'] * 100:.0f}%")

dd = os.path.join(root, "depth")
if os.path.isdir(dd):
    files = sorted(f for f in os.listdir(dd) if f.endswith(".depth"))
    if files and os.path.exists(os.path.join(dd, "size.txt")):
        w, h = map(int, open(os.path.join(dd, "size.txt")).read().split())
        valid = [np.mean(np.fromfile(os.path.join(dd, f), dtype="<u2") > 0) for f in files[:: max(1, len(files) // 40)]]
        report("PASS" if len(files) / max(dur, 1) > 1 and np.median(valid) > 0.5 else "WARN",
               f"ARCore depth: {len(files)} maps ({len(files) / max(dur, 1):.1f}/s) at {w}x{h}, median valid {np.median(valid) * 100:.0f}%")
    else:
        report("WARN", "no ARCore depth maps (device may not support depth)")

# ---- per-frame camera metadata (app >= 2026-10-12): exposure + rolling shutter for blur modelling ----
cp = os.path.join(root, "camera.csv")
if os.path.exists(cp):
    C = np.genfromtxt(cp, delimiter=",", skip_header=1)
    C = C[None] if C.ndim == 1 else C
    exp = C[:, 1][C[:, 1] > 0] / 1e6; rs = C[:, 2][C[:, 2] > 0] / 1e6; iso = C[:, 4][C[:, 4] > 0]
    if len(exp):
        report("PASS" if np.median(exp) <= 20 else "WARN",
               f"exposure: median {np.median(exp):.1f} ms (1/{1000 / np.median(exp):.0f} s), range {exp.min():.1f}-{exp.max():.1f} ms, "
               f"ISO median {np.median(iso) if len(iso) else -1:.0f}" + ("" if np.median(exp) <= 20 else "  (long exposure: more motion blur, add light)"))
    else:
        report("WARN", "camera.csv: exposure time not reported by this device")
    report("PASS" if len(rs) else "WARN", f"rolling-shutter readout: {np.median(rs):.1f} ms" if len(rs) else "rolling-shutter skew not reported")
else:
    report("WARN", "camera.csv missing (older app: no exposure / rolling-shutter metadata)")

# ---- re-anchor detection (app >= 2026-10-12): ARCore moves anchors when it corrects its world frame ----
ap_ = os.path.join(root, "anchors.csv")
if os.path.exists(ap_):
    A = [l.strip().split(",") for l in open(ap_).readlines()[1:]]
    jumps = []
    by = {}
    for r in A:
        if r[2] != "TRACKING":
            continue
        by.setdefault(int(r[1]), []).append((int(r[0]), np.array(list(map(float, r[3:6]))), np.array(list(map(float, r[6:10])))))
    for aid, seq in by.items():
        for (t0_, p0, q0), (t1_, p1, q1) in zip(seq[:-1], seq[1:]):
            dp = np.linalg.norm(p1 - p0); da = np.degrees((R.from_quat(q0).inv() * R.from_quat(q1)).magnitude())
            if dp > 0.03 or da > 1.0:                    # anchors are static: any step = world correction
                jumps.append(((t1_ - P[0, 0]) / 1e9, aid, dp, da))
    big = {}
    for tj, aid, dp, da in jumps:                       # one event = all anchors jumping at the same time
        k = round(tj, 1); big[k] = max(big.get(k, (0, 0)), (dp, da))
    ev = sorted((k, v) for k, v in big.items() if v[0] > 0.05 or v[1] > 2)
    report("PASS" if not ev else "WARN", f"anchors: {len(by)} reference anchors; ARCore world corrections > 5 cm / 2 deg: "
           + (", ".join(f"{k:.1f}s ({v[0] * 100:.0f} cm, {v[1]:.1f} deg)" for k, v in ev[:8]) if ev else "none"))
else:
    report("WARN", "anchors.csv missing (older app: silent ARCore re-anchors cannot be detected)")

pts = np.genfromtxt(os.path.join(root, "points.csv"), delimiter=",", usecols=(1, 2, 3))
nan = np.mean(~np.isfinite(pts).all(1)) if len(pts) else 1
report("PASS" if nan == 0 else "WARN", f"points.csv: {len(pts)} rows, {nan * 100:.1f}% NaN")

# ---- sync: optical flow vs pose angular velocity over the first ~60 s ----
pts_t = np.sort(np.array(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                                  "packet=pts_time", "-of", "csv=p=0", os.path.join(root, "dataset.mp4")]).split(), dtype=float))
cap = cv2.VideoCapture(os.path.join(root, "dataset.mp4")); win = cv2.createHanningWindow((320, 180), cv2.CV_32F)
prev, sh = None, []
for k in range(min(len(pts_t), int(60 * fps))):
    r_, f = cap.read()
    if not r_:
        break
    g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (320, 180), interpolation=cv2.INTER_AREA).astype(np.float32)
    sh.append(cv2.phaseCorrelate(prev, g, win)[0] if prev is not None else (0.0, 0.0)); prev = g
sh = np.array(sh); n = len(sh)
rot = R.from_quat(P[:, 4:8]); w = (rot[:-1].inv() * rot[1:]).as_rotvec() / np.maximum(dt, 1e-3)[:, None]
tm = (t[:-1] + t[1:]) / 2; okw = (dt > 0) & (dt < 0.1)
vel = sh[1:] / np.diff(pts_t[:n])[:, None]
best = (-9, 0)
for off in np.arange(-0.5, 0.51, 0.05):
    tp = pts_t[1:n] + off; m = (tp > 1) & (tp < min(t[-1], 60) - 1)
    if m.sum() < 100:
        continue
    c = np.corrcoef(vel[m, 0], np.interp(tp[m], tm[okw], w[okw, 1]))[0, 1]
    if c > best[0]:
        best = (c, off)
report("PASS" if best[0] > 0.4 and abs(best[1]) <= 0.1 else "WARN",
       f"video<->pose sync: best offset {best[1]:+.2f} s, correlation {best[0]:.2f} (expect ~0.0 s, > 0.4)")
print("\nOVERALL:", "READY TO PROCESS" if ok_all else "PROBLEMS FOUND (see FAIL lines)")
