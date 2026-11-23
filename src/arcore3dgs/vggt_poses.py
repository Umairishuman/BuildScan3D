"""Camera poses from VGGT (feed-forward, robust to blur and low texture) for captures where SfM fails locally.

FEATURELESS_TRACKING_PLAN step 2. On scan_009 both COLMAP mappers produced locally wrong camera paths (the
accelerometer, ARCore and the gyro all disagree with them, TRAINING R-046 – R-048). VGGT (Wang et al., CVPR 2025)
predicts cameras and depth for a set of images in one pass.

  1. undistort the keyframes with a known lens calibration (an earlier SfM model of the same capture);
  2. VGGT on overlapping chunks (--chunk frames, --overlap shared), bf16;
  3. chain the chunks: rotation from the shared frames' rotations, scale from their depth maps, translation from the
     shared camera centres;
  4. checks against the phone: gyro (relative rotations), accelerometer (pre-integrated scale and gravity) and the
     ARCore 1-s displacement ratio;
  5. metric scale from the accelerometer (imu_scale.py), gravity from the same fit (+Y up), written in the layout of
     sfm_colmap's export (frames.json, images/, sparse.npz from VGGT depth, report.json), so run_v8.py continues
     with --from_stage export --init mono.

Needs the VGGT code and weights outside the repo (VGGT_DIR, default C:/Users/tyb/.cache/buildscan or ~/.cache/buildscan:
vggt/ (git clone), vggt_deps/ (einops, safetensors, huggingface_hub), vggt_weights/model.pt). Runs in the nerfstudio
environment (torch with CUDA).

  python src/arcore3dgs/vggt_poses.py --dataset <capture> --work <keyframe dir> --calib <sfm dir with sparse/0 + report.json>
      --out <new sfm dir> [--chunk 32] [--overlap 8] [--stage all|vggt|chain]
"""
import argparse
import glob
import json
import os
import sys

import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
VDIR = os.environ.get("VGGT_DIR", os.path.join(os.path.expanduser("~"), ".cache", "buildscan"))

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", required=True)
ap.add_argument("--work", required=True)
ap.add_argument("--calib", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--chunk", type=int, default=32)
ap.add_argument("--overlap", type=int, default=8)
ap.add_argument("--stage", default="all", choices=["all", "vggt", "chain"])
ap.add_argument("--points_per_frame", type=int, default=400)
args = ap.parse_args()
OUT = os.path.abspath(args.out)
os.makedirs(os.path.join(OUT, "images"), exist_ok=True)
os.makedirs(os.path.join(OUT, "vggt_chunks"), exist_ok=True)
meta = json.load(open(os.path.join(args.work, "frames.json")))
frames = sorted(meta["frames"], key=lambda f: f["pts"])
names = [f["name"] for f in frames]
rep_c = json.load(open(os.path.join(args.calib, "report.json")))
W, H = rep_c["undistorted_size"]
fx, fy, cx, cy = rep_c["pinhole"]
dist_cam = rep_c["distorted_camera"]                                 # model OPENCV, params fx fy cx cy k1 k2 p1 p2
p0 = dist_cam["params"]
K0 = np.array([[p0[0], 0, p0[2]], [0, p0[1], p0[3]], [0, 0, 1]])
Ku = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])

# 1. undistorted keyframes (same pinhole as the calibration model's undistorted images)
umap = cv2.initUndistortRectifyMap(K0, np.array(p0[4:8]), None, Ku, (W, H), cv2.CV_32FC1)
for n in names:
    dst = os.path.join(OUT, "images", n + ".jpg")
    if not os.path.exists(dst):
        im = cv2.imread(os.path.join(args.work, "images", n + ".jpg"))
        cv2.imwrite(dst, cv2.remap(im, umap[0], umap[1], cv2.INTER_LINEAR), [cv2.IMWRITE_JPEG_QUALITY, 95])

step = args.chunk - args.overlap
starts = list(range(0, max(1, len(names) - args.overlap), step))
chunks = [(s_, min(s_ + args.chunk, len(names))) for s_ in starts]

# 2. VGGT per chunk
if args.stage in ("all", "vggt"):
    sys.path.insert(0, os.path.join(VDIR, "vggt"))
    sys.path.append(os.path.join(VDIR, "vggt_deps"))                   # appended: the environment's packages win
    import torch
    from vggt.models.vggt import VGGT
    from vggt.utils.load_fn import load_and_preprocess_images
    from vggt.utils.pose_enc import pose_encoding_to_extri_intri
    dev = "cuda"
    model = VGGT()
    model.load_state_dict(torch.load(os.path.join(VDIR, "vggt_weights", "model.pt"), map_location="cpu"))
    model = model.to(torch.bfloat16).to(dev).eval()
    for ci, (a, b) in enumerate(chunks):
        out_c = os.path.join(OUT, "vggt_chunks", f"{ci:03d}.npz")
        if os.path.exists(out_c):
            continue
        paths = [os.path.join(OUT, "images", n + ".jpg") for n in names[a:b]]
        imgs = load_and_preprocess_images(paths).to(dev)
        with torch.no_grad():
            x = imgs[None].to(torch.bfloat16)
            tokens, ps_idx = model.aggregator(x)
            pose_enc = model.camera_head(tokens)[-1]
            extr, intr = pose_encoding_to_extri_intri(pose_enc.float(), x.shape[-2:])
            depth, conf = model.depth_head(tokens, x, ps_idx)
        np.savez_compressed(out_c, names=np.array(names[a:b]), extr=extr[0].cpu().numpy(), intr=intr[0].cpu().numpy(),
                            depth=depth[0, ..., 0].float().cpu().numpy().astype(np.float16),
                            conf=conf[0].float().cpu().numpy().astype(np.float16), hw=np.array(x.shape[-2:]))
        print(f"chunk {ci + 1}/{len(chunks)}: frames {a}-{b - 1}, peak GPU {torch.cuda.max_memory_allocated() / 2**30:.1f} GB",
              flush=True)
        del tokens, depth, conf
        torch.cuda.empty_cache()
    if args.stage == "vggt":
        sys.exit(0)

# 3. chain chunks into one world (OpenCV cameras)
c2w, dscale, src = {}, {}, {}
for ci in range(len(chunks)):
    z = np.load(os.path.join(OUT, "vggt_chunks", f"{ci:03d}.npz"))
    nm = list(z["names"]); E = z["extr"]
    loc = {}
    for k, n in enumerate(nm):
        M = np.eye(4); M[:3, :4] = E[k]; loc[n] = np.linalg.inv(M)                 # camera-to-chunk-world
    shared = [n for n in nm if n in c2w]
    if not shared:                                                                  # first chunk defines the world
        for k, n in enumerate(nm):
            c2w[n] = loc[n]; dscale[n] = 1.0; src[n] = (ci, k)
        continue
    # rotation: chordal mean of global R * local R^T over the shared frames
    Ms = sum(c2w[n][:3, :3] @ loc[n][:3, :3].T for n in shared)
    U, _, Vt = np.linalg.svd(Ms); Ra = U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt
    # scale: median ratio of the shared frames' depth maps (robust when the shared cameras barely moved)
    ratios = []
    for n in shared:
        gci, gk = src[n]
        dg = np.load(os.path.join(OUT, "vggt_chunks", f"{gci:03d}.npz"))["depth"][gk].astype(np.float32) * dscale[n]
        dl = z["depth"][nm.index(n)].astype(np.float32)
        ok = (dg > 0) & (dl > 0)
        if ok.sum() > 100:
            ratios.append(np.median(dg[ok] / dl[ok]))
    s_ = float(np.median(ratios)) if ratios else 1.0
    tr = np.mean([c2w[n][:3, 3] - s_ * Ra @ loc[n][:3, 3] for n in shared], axis=0)
    for k, n in enumerate(nm):
        if n in c2w:
            continue
        M = np.eye(4); M[:3, :3] = Ra @ loc[n][:3, :3]; M[:3, 3] = s_ * Ra @ loc[n][:3, 3] + tr
        c2w[n] = M; dscale[n] = s_; src[n] = (ci, k)
print(f"chained {len(c2w)} of {len(names)} frames from {len(chunks)} chunks")

# 4. checks against the phone + 5. metric scale and gravity from the accelerometer
from common import Capture  # noqa: E402
from gyro_check import check  # noqa: E402
from imu_scale import estimate_preint  # noqa: E402
t0 = Capture(args.dataset).t0_ns
gyro = check(args.dataset, frames, {n: M[:3, :3] for n, M in c2w.items()}, t0, meta.get("pose_offset", 0.0))
sc = estimate_preint(frames, c2w, gyro, meta.get("pose_offset", 0.0), T=1.0, gyro_orient=True)
rows = estimate_preint(frames, c2w, gyro, meta.get("pose_offset", 0.0), T=1.0, verbose=False, return_rows=True,
                       gyro_orient=True)
x = np.linalg.lstsq(rows["A"], rows["b"], rcond=None)[0]
g_w = x[1:4]                                                                       # gravity acceleration (down)
# ARCore 1-s displacement ratio (local consistency; ARCore is locally accurate even when it drifts)
fr_by = {f["name"]: f for f in frames}
tA = [(fr_by[n]["pts"], c2w[n][:3, 3], np.array(fr_by[n].get("c2w_arcore") or fr_by[n]["c2w"])[:3, 3])
      for n in names if n in c2w and (fr_by[n].get("c2w_arcore") or fr_by[n].get("c2w")) is not None]
ratio = []
for i, (ti, si, ai) in enumerate(tA):
    for tj, sj, aj in tA[i + 1:]:
        if 0.8 < tj - ti < 1.3:
            if np.linalg.norm(aj - ai) > 0.05:
                ratio.append(np.linalg.norm(sj - si) * sc["scale"] / np.linalg.norm(aj - ai))
            break
ratio = np.array(ratio)
checks = dict(gyro_pair_err_deg_median=gyro["pair_err_deg_median"], gyro_pair_err_deg_p90=gyro["pair_err_deg_p90"],
              gyro_frames_over_2deg=len(gyro["flagged"]), imu_scale=sc["scale"], imu_scale_p5_p95=sc["scale_p5_p95"],
              imu_gravity_norm=sc["gravity_norm"],
              arcore_ratio_median=float(np.median(ratio)) if len(ratio) else None,
              arcore_ratio_p90_over_p10=float(np.percentile(ratio, 90) / np.percentile(ratio, 10)) if len(ratio) > 5 else None,
              arcore_windows=int(len(ratio)))
print(json.dumps(checks, indent=1))

# world: metric (IMU scale), gravity along -Y (ARCore convention: +Y up), first camera at the origin
s_m = sc["scale"]
up = -g_w / np.linalg.norm(g_w)
v = np.cross(up, [0, 1, 0]); cth = up @ [0, 1, 0]
Rg = np.eye(3) if np.linalg.norm(v) < 1e-9 else R.from_rotvec(v / np.linalg.norm(v) * np.arccos(np.clip(cth, -1, 1))).as_matrix()
origin = c2w[names[0]][:3, 3] if names[0] in c2w else next(iter(c2w.values()))[:3, 3]
G = np.diag([1.0, -1.0, -1.0, 1.0])
out_frames, Xs, cam_l, uv_l = [], [], [], []
rng = np.random.default_rng(0)
for n in names:
    if n not in c2w:
        continue
    M = c2w[n]; Mm = np.eye(4); Mm[:3, :3] = Rg @ M[:3, :3]; Mm[:3, 3] = s_m * Rg @ (M[:3, 3] - origin)
    y = dict(fr_by[n]); y["c2w"] = (Mm @ G).tolist(); y["c2w_arcore"] = fr_by[n].get("c2w_arcore", fr_by[n].get("c2w"))
    y["placed_by"] = "vggt"
    out_frames.append(y)
    # sparse points for mono_prior: confident VGGT depth pixels, unprojected with the known pinhole (full res)
    ci, k = src[n]
    z = np.load(os.path.join(OUT, "vggt_chunks", f"{ci:03d}.npz"))
    d = z["depth"][k].astype(np.float32) * dscale[n] * s_m; cf = z["conf"][k].astype(np.float32)
    h, w = d.shape
    ok = np.argwhere((d > 0.1) & (cf > np.percentile(cf, 50)))
    if len(ok) == 0:
        continue
    pick = ok[rng.choice(len(ok), min(args.points_per_frame, len(ok)), replace=False)]
    u = (pick[:, 1] + 0.5) * W / w; v_ = (pick[:, 0] + 0.5) * H / h; zz = d[pick[:, 0], pick[:, 1]]
    Pc = np.c_[(u - cx) / fx * zz, (v_ - cy) / fy * zz, zz]
    Xs.append(Pc @ Mm[:3, :3].T + Mm[:3, 3]); cam_l += [len(out_frames) - 1] * len(Pc); uv_l.append(np.c_[u, v_])
X = np.concatenate(Xs)
np.savez(os.path.join(OUT, "sparse.npz"), X=X, cam=np.array(cam_l), pt=np.arange(len(X)),
         uv=np.concatenate(uv_l).astype(np.float32))
m2 = dict(meta); m2.update(W=W, H=H, fx=fx, fy=fy, cx=cx, cy=cy, frames=out_frames,
                           sfm=dict(source="vggt", registered=len(out_frames), total=len(names), scale_source="imu",
                                    imu_scale=s_m, checks=checks, chunk=args.chunk, overlap=args.overlap))
json.dump(m2, open(os.path.join(OUT, "frames.json"), "w"), indent=1)
json.dump(dict(m2["sfm"], undistorted_size=[W, H], pinhole=[fx, fy, cx, cy], distorted_camera=dist_cam),
          open(os.path.join(OUT, "report.json"), "w"), indent=1)
print(f"wrote {OUT}: {len(out_frames)} frames, {len(X)} sparse points, metric scale {s_m:.4f} (IMU)")
_ = glob  # (kept for interactive use)
