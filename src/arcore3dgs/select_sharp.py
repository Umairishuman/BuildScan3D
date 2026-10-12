"""Gyro-aware keyframe selection: more frames, and the sharpest ones.

Phone video walked at a normal pace is motion-blurred (newRoomAttemptSadness: median keyframe blur ~6-12 px
at 1/60-1/30 s exposure, mostly from rotation). The IMU says how fast the camera turned at every frame, so
within each window of --window frames we keep the frame with the least predicted blur
(|gyro| * exposure * focal + |v| / depth * exposure * focal), using image sharpness (Laplacian) as a
tie-break and dropping frames far below the local image sharpness median.

  python src/arcore3dgs/select_sharp.py --dataset <dataset> --out <dataset>/work_sharp [--window 6]
Writes <out>/images/frame_XXXXX.jpg (full res), <out>/frames.json (ARCore c2w per frame, predicted blur).
"""
import os, sys, json, csv, argparse
import numpy as np, cv2

sys.path.insert(0, os.path.dirname(__file__))
from common import Capture

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--window", type=int, default=6)
ap.add_argument("--exposure", type=float, default=1 / 45, help="s, assumed (ARCore does not record it)")
ap.add_argument("--rel_sharpness", type=float, default=0.6)
ap.add_argument("--settle", type=float, default=3.0)
args = ap.parse_args()
cap_info = Capture(args.dataset)
os.makedirs(os.path.join(args.out, "images"), exist_ok=True)

imu = np.load(os.path.join(args.dataset, "imu.npz"))
with open(os.path.join(args.dataset, "poses.csv")) as f:
    r = csv.reader(f); next(r); t0 = float(next(r)[0])
gt = (imu["gt"] - t0) / 1e9; w = np.linalg.norm(imu["g"], axis=1)

cap = cv2.VideoCapture(cap_info.video)
N = min(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), len(cap_info.pts))
sharp = np.zeros(N)
for k in range(N):
    ok, f = cap.read()
    if not ok:
        N = k; sharp = sharp[:N]; break
    g = cv2.cvtColor(cv2.resize(f, (960, 540), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    sharp[k] = cv2.Laplacian(g, cv2.CV_64F).var()
cap.release()
pts = np.asarray(cap_info.pts[:N])
wk = np.interp(pts, gt, np.convolve(w, np.ones(9) / 9, mode="same"))                # ~40 ms smoothed rad/s
C = np.array([(cap_info.frame_pose(k) if cap_info.frame_pose(k) is not None else np.full((4, 4), np.nan))[:3, 3] for k in range(N)])
v = np.linalg.norm(np.gradient(np.nan_to_num(C), pts, axis=0), axis=1)
blur = (wk + v / 2.5) * args.exposure * cap_info.fx                                  # predicted blur, px
print(f"{N} frames; predicted blur px: median {np.median(blur):.1f}, p10 {np.percentile(blur, 10):.1f}, "
      f"p90 {np.percentile(blur, 90):.1f}; corr(blur, -Laplacian) = {np.corrcoef(blur, -sharp)[0, 1]:.2f}")
local_med = np.array([np.median(sharp[max(0, k - 60):k + 60]) for k in range(N)])
sel = []
for s in range(0, N, args.window):
    idx = np.arange(s, min(s + args.window, N))
    idx = idx[(sharp[idx] >= args.rel_sharpness * local_med[idx])]
    idx = [k for k in idx if cap_info.frame_pose(k) is not None and cap_info.tracking_settled(pts[k], args.settle)]
    if not idx:
        continue
    idx = np.array(idx)
    score = blur[idx] - 0.5 * (sharp[idx] / local_med[idx])                          # mostly gyro, Laplacian tie-break
    sel.append(int(idx[np.argmin(score)]))
print(f"selected {len(sel)} frames: predicted blur median {np.median(blur[sel]):.1f} px "
      f"(vs {np.median(blur):.1f} px over all frames)")
frames = []
cap = cv2.VideoCapture(cap_info.video); S = set(sel)
for k in range(max(sel) + 1):
    ok, f = cap.read()
    if not ok:
        break
    if k not in S:
        continue
    name = f"frame_{k:05d}"
    p = os.path.join(args.out, "images", name + ".jpg")
    if not os.path.exists(p):
        cv2.imwrite(p, f, [cv2.IMWRITE_JPEG_QUALITY, 95])
    c2w = cap_info.frame_pose(k)
    frames.append({"name": name, "video_index": k, "pts": float(pts[k]), "sharpness": float(sharp[k]),
                   "pred_blur_px": float(blur[k]), "fallback": cap_info.is_fallback(pts[k]),
                   "c2w": c2w.tolist(), "c2w_arcore": c2w.tolist()})
cap.release()
H, W = f.shape[:2] if f is not None else (1080, 1920)
json.dump({"dataset": os.path.abspath(args.dataset), "W": 1920, "H": 1080, "fx": cap_info.fx, "fy": cap_info.fy,
           "cx": cap_info.cx, "cy": cap_info.cy, "pose_offset": 0.0, "selection": "gyro-aware", "frames": frames},
          open(os.path.join(args.out, "frames.json"), "w"), indent=1)
print(f"wrote {len(frames)} frames to {args.out}")
