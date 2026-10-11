"""Stage 1: keyframe selection + Metric3D depth cache.

Keyframes: video is split into windows of --window frames; the sharpest frame (Laplacian variance) of
each window is kept if it has a valid pose and is not far below the local sharpness median. This keeps
temporal coverage uniform (unlike a hard global blur threshold) while dropping motion-blurred frames.

Outputs in <out>:
  images/frame_XXXXX.jpg  raw landscape frames (full res)
  depth_m3d/frame_XXXXX.npy  Metric3D metric depth at half res (float16, metres, OpenCV z)
  frames.json  per-keyframe: video index, pts, sharpness, c2w (OpenGL)
Run with the system python (Metric3D lives there).
"""
import sys, types, os, json, argparse
import cv2, numpy as np, torch

sys.path.insert(0, os.path.dirname(__file__))
from common import Capture

mmcv = types.ModuleType('mmcv'); mmcv_utils = types.ModuleType('mmcv.utils')
mmcv_utils.collect_env = lambda: {"OS": "Windows Bypassed"}
sys.modules['mmcv'] = mmcv; sys.modules['mmcv.utils'] = mmcv_utils

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--window", type=int, default=8)
ap.add_argument("--rel_sharpness", type=float, default=0.6, help="drop keyframe if sharpness < this * local median")
ap.add_argument("--pose_offset", type=float, default=0.0)
ap.add_argument("--depth", type=int, default=1, help="0 = skip Metric3D (not needed by the SfM pipeline, sfm_colmap.py)")
ap.add_argument("--settle", type=float, default=3.0, help="skip frames within this many s after an ARCore tracking loss")
args = ap.parse_args()

cap_info = Capture(args.dataset, pose_offset=args.pose_offset)
os.makedirs(os.path.join(args.out, "images"), exist_ok=True)
os.makedirs(os.path.join(args.out, "depth_m3d"), exist_ok=True)

# ---- pass 1: sharpness of every frame (downscaled, fast) ----
print("Pass 1: sharpness scan")
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

local_med = np.array([np.median(sharp[max(0, k - 60):k + 60]) for k in range(N)])
selected = []
for s in range(0, N, args.window):
    idx = np.arange(s, min(s + args.window, N))
    k = int(idx[np.argmax(sharp[idx])])
    if sharp[k] < args.rel_sharpness * local_med[k]:
        continue
    if cap_info.frame_pose(k) is None:
        continue
    if not cap_info.tracking_settled(cap_info.pts[k] + args.pose_offset, args.settle):
        continue
    selected.append(k)
print(f"Selected {len(selected)} keyframes from {N} frames")

# ---- pass 2: write images + Metric3D depth ----
dev = torch.device("cuda")
model = torch.hub.load('yvanyin/metric3d', 'metric3d_vit_large', pretrain=True).to(dev).eval() if args.depth else None
INPUT = (616, 1064)
MEAN = torch.tensor([123.675, 116.28, 103.53], device=dev).view(1, 3, 1, 1)
STD = torch.tensor([58.395, 57.12, 57.375], device=dev).view(1, 3, 1, 1)


@torch.no_grad()
def metric_depth(bgr, fx, out_hw):
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    h, w = rgb.shape[:2]
    s = min(INPUT[0] / h, INPUT[1] / w)
    rgb = cv2.resize(rgb, (int(w * s), int(h * s)), interpolation=cv2.INTER_LINEAR)
    ph, pw = INPUT[0] - rgb.shape[0], INPUT[1] - rgb.shape[1]
    pad = [ph // 2, ph - ph // 2, pw // 2, pw - pw // 2]
    rgb = cv2.copyMakeBorder(rgb, pad[0], pad[1], pad[2], pad[3], cv2.BORDER_CONSTANT, value=[123.675, 116.28, 103.53])
    x = (torch.from_numpy(rgb.transpose(2, 0, 1)).float().to(dev)[None] - MEAN) / STD
    d, _, _ = model.inference({'input': x})
    d = d.squeeze()[pad[0]:INPUT[0] - pad[1], pad[2]:INPUT[1] - pad[3]]
    d = torch.nn.functional.interpolate(d[None, None], out_hw, mode='bilinear').squeeze()
    return (d * (fx * s / 1000.0)).clamp(0, 50).cpu().numpy()   # canonical (f=1000) -> metric


frames = []
cap = cv2.VideoCapture(cap_info.video)
sel = set(selected)
for k in range(max(selected) + 1):
    ok, f = cap.read()
    if not ok:
        break
    if k not in sel:
        continue
    H, W = f.shape[:2]
    name = f"frame_{k:05d}"
    cv2.imwrite(os.path.join(args.out, "images", name + ".jpg"), f, [cv2.IMWRITE_JPEG_QUALITY, 95])
    if args.depth:
        d = metric_depth(f, cap_info.fx, (H // 2, W // 2))
        np.save(os.path.join(args.out, "depth_m3d", name + ".npy"), d.astype(np.float16))
    frames.append({"name": name, "video_index": k, "pts": float(cap_info.pts[k]), "sharpness": float(sharp[k]),
                   "fallback": cap_info.is_fallback(cap_info.pts[k] + args.pose_offset),
                   "c2w": cap_info.frame_pose(k).tolist()})
    if len(frames) % 25 == 0:
        print(f"  {len(frames)}/{len(selected)} depth maps", flush=True)
cap.release()

meta = {"dataset": os.path.abspath(args.dataset), "W": W, "H": H,
        "fx": cap_info.fx, "fy": cap_info.fy, "cx": cap_info.cx, "cy": cap_info.cy,
        "depth_scale": 0.5, "pose_offset": args.pose_offset, "frames": frames}
json.dump(meta, open(os.path.join(args.out, "frames.json"), "w"), indent=1)
print(f"Done: {len(frames)} keyframes -> {args.out}")
