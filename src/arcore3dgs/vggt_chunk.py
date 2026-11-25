"""VGGT on one chunk of keyframes, checked against the gyro, an SfM model and the Metric3D priors
(FEATURELESS_TRACKING_PLAN §11.a, decision D-081).

VGGT (Wang et al., CVPR 2025; Meta research licence) predicts cameras and depth maps for a set of images in one
pass, from the images alone, also where there are no corners to match. This tool runs it on N keyframes between
--t0 and --t1 (seconds from the first frame) and reports:

  1. rotations: angle between VGGT's and the gyro's relative rotation for every pair in the chunk (median, p90);
     the same for the SfM model (whose rotations are tied to the gyro) as a reference;
  2. positions: VGGT camera centres Sim3-aligned to the SfM model on frames with >= --anchor_obs 3D observations;
     residual on those anchors and the difference on the others (where the SfM path rests on the sensors);
  3. depth consistency: for frame pairs k = 1..3 apart, frame i's depth is moved into frame j with the poses and
     compared with frame j's depth (relative error, median); VGGT (its own depth + poses) against the Metric3D
     priors in <sfm dir>/mono_prior (each frame scaled on its own) with the SfM poses.

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/vggt_chunk.py <dataset> <sfm dir (frames.json, images,
      mono_prior)> <sfm model dir (images.txt)> <out dir> --vggt_dir <clone> --weights <model.pt>
      [--t0 42 --t1 63 --n 32] [--bg_json gyro_loop_bias.json] [--calib <sfm dir with sparse/0 for gyro_check>]

Images: the undistorted training images (pinhole), resized by VGGT's own loader (width 518). Weights are loaded
with torch.load(weights_only=True). Writes <out>/vggt.npz (extrinsic, intrinsic, depth, conf, names) and
<out>/vggt_chunk.json.
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import torch
from scipy.spatial.transform import Rotation as R

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
G = np.diag([1.0, -1.0, -1.0, 1.0])


def angle(Rm):
    return float(np.degrees(np.linalg.norm(R.from_matrix(Rm).as_rotvec())))


def umeyama(src, dst):
    ms, md = src.mean(0), dst.mean(0); S, D = src - ms, dst - md
    U, s, Vt = np.linalg.svd(D.T @ S / len(src)); E = np.eye(3)
    if np.linalg.det(U @ Vt) < 0:
        E[2, 2] = -1
    Rm = U @ E @ Vt; sc = np.trace(np.diag(s) @ E) / S.var(0).sum()
    return sc, Rm, md - sc * Rm @ ms


def load_model_poses(model_dir):
    """images.txt -> {name: (c2w 4x4 OpenCV, n 3D observations)}"""
    L = [l for l in open(os.path.join(model_dir, "images.txt")) if not l.startswith("#")]
    out = {}
    for hdr, pts in zip(L[0::2], L[1::2]):
        p = hdr.split()
        if len(p) < 10:
            continue
        q = np.array(list(map(float, p[1:5]))); t = np.array(list(map(float, p[5:8])))
        Rcw = R.from_quat([q[1], q[2], q[3], q[0]]).as_matrix()
        c2w = np.eye(4); c2w[:3, :3] = Rcw.T; c2w[:3, 3] = -Rcw.T @ t
        out[os.path.splitext(p[9])[0]] = (c2w, sum(1 for v in pts.split()[2::3] if v != "-1"))
    return out


def depth_consistency(D, K, c2w, pairs, valid=None, stride=4):
    """median relative depth error when frame i's depth is moved into frame j (OpenCV c2w, pinhole K per frame)"""
    errs = []
    for i, j in pairs:
        h, w = D[i].shape
        v, u = np.mgrid[0:h:stride, 0:w:stride]; z = D[i][v, u]
        m = z > 0
        if valid is not None:
            m &= valid[i][v, u]
        u, v, z = u[m] + 0.5, v[m] + 0.5, z[m]
        Ki, Kj = K[i], K[j]
        P = np.stack([(u - Ki[0, 2]) / Ki[0, 0] * z, (v - Ki[1, 2]) / Ki[1, 1] * z, z], 1)
        Pw = P @ c2w[i][:3, :3].T + c2w[i][:3, 3]
        Pj = (Pw - c2w[j][:3, 3]) @ c2w[j][:3, :3]
        ok = Pj[:, 2] > 1e-3
        uj = Kj[0, 0] * Pj[ok, 0] / Pj[ok, 2] + Kj[0, 2]; vj = Kj[1, 1] * Pj[ok, 1] / Pj[ok, 2] + Kj[1, 2]
        inb = (uj >= 0) & (uj < w - 1) & (vj >= 0) & (vj < h - 1)
        zj = D[j][vj[inb].astype(int), uj[inb].astype(int)]
        zp = Pj[ok, 2][inb]
        g = zj > 0
        if valid is not None:
            g &= valid[j][vj[inb].astype(int), uj[inb].astype(int)]
        if g.sum() > 50:
            errs.append(float(np.median(np.abs(zp[g] - zj[g]) / zj[g])))
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset"); ap.add_argument("sfm"); ap.add_argument("model"); ap.add_argument("out")
    ap.add_argument("--vggt_dir", default=None); ap.add_argument("--weights", default=None)
    ap.add_argument("--da3", default=None,
                    help="Depth Anything 3 (ByteDance, 2025) instead of VGGT: Hugging Face id or local dir, e.g. "
                         "depth-anything/DA3-LARGE; the package must be importable (D-097)")
    ap.add_argument("--da3_res", type=int, default=504)
    ap.add_argument("--t0", type=float, default=42.0); ap.add_argument("--t1", type=float, default=63.0)
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--bg_json", default=None); ap.add_argument("--calib", default=None)
    ap.add_argument("--anchor_obs", type=int, default=20)
    ap.add_argument("--video_step", type=float, default=0.0,
                    help="> 0: dense frames from dataset.mp4 every this many seconds instead of keyframes (gyro checks only)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    meta = json.load(open(os.path.join(a.sfm, "frames.json"))); fr = sorted(meta["frames"], key=lambda f: f["pts"])
    t_first = fr[0]["pts"]
    if a.video_step > 0:
        # dense frames straight from the video (the keyframes are sparse exactly where the walls are blank: R-093
        # had 3.5 s gaps with 50 - 64 deg of turning between neighbours); time from the keyframes' video_index -> pts
        import cv2
        vi = np.array([f["video_index"] for f in fr], float); pt = np.array([f["pts"] for f in fr])
        ts = np.arange(a.t0, a.t1 + 1e-6, a.video_step) + t_first
        want = np.unique(np.interp(ts, pt, vi).round().astype(int))
        os.makedirs(os.path.join(a.out, "frames"), exist_ok=True)
        cap = cv2.VideoCapture(os.path.join(a.dataset, "dataset.mp4")); k = -1; pick, img_paths = [], []
        while len(pick) < len(want):
            ok, im = cap.read(); k += 1
            if not ok:
                break
            if k in set(want.tolist()):
                p = os.path.join(a.out, "frames", f"v{k:05d}.jpg"); cv2.imwrite(p, im, [cv2.IMWRITE_JPEG_QUALITY, 95])
                pick.append(dict(name=f"v{k:05d}", pts=float(np.interp(k, vi, pt)))); img_paths.append(p)
        names = [f["name"] for f in pick]; T = np.array([f["pts"] - t_first for f in pick])
        print(f"{len(names)} video frames every {a.video_step:g} s, {T[0]:.1f} - {T[-1]:.1f} s (raw video, not undistorted)",
              flush=True)
    else:
        inside = [f for f in fr if a.t0 <= f["pts"] - t_first < a.t1]
        pick = [inside[k] for k in np.unique(np.linspace(0, len(inside) - 1, min(a.n, len(inside))).round().astype(int))]
        names = [f["name"] for f in pick]; T = np.array([f["pts"] - t_first for f in pick])
        img_paths = [os.path.join(a.sfm, "images", n + ".jpg") for n in names]
        print(f"{len(names)} keyframes {T[0]:.1f} - {T[-1]:.1f} s", flush=True)

    if a.da3:                                                   # ---- Depth Anything 3 (same checks below) ----
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import da3_loader
        DepthAnything3, stubbed = da3_loader.load_api()
        dev = "cuda"; t = time.time()
        model = DepthAnything3.from_pretrained(a.da3).to(dev).eval()
        torch.cuda.reset_peak_memory_stats()
        with torch.no_grad():
            pred = model.inference(img_paths, process_res=a.da3_res)
        ext = np.asarray(pred.extrinsics)[:, :3, :4].astype(np.float64); intr = np.asarray(pred.intrinsics).astype(np.float64)
        depth = np.asarray(pred.depth, np.float32)
        conf = np.asarray(pred.conf, np.float32) if pred.conf is not None else np.ones_like(depth)
        peak = torch.cuda.max_memory_allocated() / 2 ** 30
        print(f"DA3 ({a.da3}): {len(names)} images {depth.shape[2]}x{depth.shape[1]}, {time.time() - t:.0f} s incl. loading, "
              f"peak GPU {peak:.1f} GB (stand-ins for unused export modules: {stubbed})", flush=True)
        np.savez_compressed(os.path.join(a.out, "da3.npz"), extrinsic=ext, intrinsic=intr, depth=depth.astype(np.float16),
                            conf=conf.astype(np.float16), names=np.array(names), t=T)
        del model; torch.cuda.empty_cache()
        imgs = torch.zeros(1, 1, depth.shape[1], depth.shape[2])     # only its shape is used below
    else:
        ext, intr, depth, conf, peak, imgs = run_vggt(a, img_paths, names, T)
    Cv = np.stack([np.linalg.inv(np.r_[e, [[0, 0, 0, 1]]]) for e in ext])        # c2w OpenCV, model world
    _after_model(a, meta, pick, names, T, ext, intr, depth, conf, peak, imgs, Cv)


def run_vggt(a, img_paths, names, T):
    # ---- VGGT ----
    sys.path.insert(0, a.vggt_dir)
    sys.path.append(os.path.join(os.path.dirname(a.vggt_dir.rstrip("/\\")), "vggt_deps"))
    from vggt.models.vggt import VGGT
    from vggt.utils.load_fn import load_and_preprocess_images
    from vggt.utils.pose_enc import pose_encoding_to_extri_intri
    dev = "cuda"
    t = time.time()
    model = VGGT()
    sd = torch.load(a.weights, map_location="cpu", weights_only=True)
    model.load_state_dict(sd); del sd
    # 1.26 B parameters: in fp32 the weights alone take ~5 GB and an 8 GB card spills into system RAM (R-093, first
    # try: > 10 min). The point and track heads are not used: dropped; the rest is kept in bf16 (~2.4 GB).
    model.point_head = None; model.track_head = None
    model = model.to(torch.bfloat16).to(dev).eval()
    imgs = load_and_preprocess_images(img_paths).to(dev)
    torch.cuda.reset_peak_memory_stats()
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        tok, ps_idx = model.aggregator(imgs[None].to(torch.bfloat16))
        pose_enc = model.camera_head(tok)[-1].float()
        depth, conf = model.depth_head(tok, imgs[None].to(torch.bfloat16), ps_idx)
    ext, intr = pose_encoding_to_extri_intri(pose_enc, imgs.shape[-2:])
    ext = ext[0].float().cpu().numpy(); intr = intr[0].float().cpu().numpy()
    depth = depth[0, ..., 0].float().cpu().numpy(); conf = conf[0].float().cpu().numpy()
    peak = torch.cuda.max_memory_allocated() / 2 ** 30
    print(f"VGGT: {len(names)} images {imgs.shape[-1]}x{imgs.shape[-2]}, {time.time() - t:.0f} s incl. loading, "
          f"peak GPU {peak:.1f} GB", flush=True)
    np.savez_compressed(os.path.join(a.out, "vggt.npz"), extrinsic=ext, intrinsic=intr, depth=depth.astype(np.float16),
                        conf=conf.astype(np.float16), names=np.array(names), t=T)
    del model, tok; torch.cuda.empty_cache()
    return ext, intr, depth, conf, peak, imgs


def _after_model(a, meta, pick, names, T, ext, intr, depth, conf, peak, imgs, Cv):
    res = dict(names=names, t=T.tolist(), peak_gpu_gb=peak, size=[int(imgs.shape[-1]), int(imgs.shape[-2])])
    # ---- 1. rotations vs the gyro ----
    import rs_rectify
    camrot, _, _ = rs_rectify.setup(a.dataset, meta, a.calib or a.sfm, a.bg_json)
    Rg = camrot(np.array([f["pts"] for f in pick]) + meta.get("pose_offset", 0.0))
    M = load_model_poses(a.model)
    pairs_all = [(i, j) for i in range(len(names)) for j in range(i + 1, len(names))]
    ev = [angle((Cv[i][:3, :3].T @ Cv[j][:3, :3]).T @ (Rg[i].T @ Rg[j])) for i, j in pairs_all]
    have = [k for k, n in enumerate(names) if n in M]
    em = [angle((M[names[i]][0][:3, :3].T @ M[names[j]][0][:3, :3]).T @ (Rg[i].T @ Rg[j]))
          for i, j in pairs_all if i in have and j in have]
    # VGGT against the SfM model directly (no gyro conversion), consecutive chunk frames and all pairs
    evs = [angle((Cv[i][:3, :3].T @ Cv[j][:3, :3]).T @ (M[names[i]][0][:3, :3].T @ M[names[j]][0][:3, :3]))
           for i, j in pairs_all if i in have and j in have]
    evs1 = [angle((Cv[i][:3, :3].T @ Cv[i + 1][:3, :3]).T @ (M[names[i]][0][:3, :3].T @ M[names[i + 1]][0][:3, :3]))
            for i in range(len(names) - 1) if i in have and i + 1 in have]
    if evs:
        res["rot_vs_sfm_vggt"] = [float(np.median(evs)), float(np.percentile(evs, 90)), float(np.median(evs1))]
        print(f"rotation VGGT vs SfM model: all pairs median {np.median(evs):.2f}°, p90 {np.percentile(evs, 90):.2f}°; "
              f"consecutive frames median {np.median(evs1):.2f}°; SfM step rotation median "
              f"{np.median([angle(M[names[i]][0][:3, :3].T @ M[names[i + 1]][0][:3, :3]) for i in range(len(names) - 1) if i in have and i + 1 in have]):.1f}°",
              flush=True)
    # step by step against the gyro, in 2 s bins: where VGGT follows the camera and where it does not
    st = [(T[i + 1], angle(Rg[i].T @ Rg[i + 1]), angle((Cv[i][:3, :3].T @ Cv[i + 1][:3, :3]).T @ (Rg[i].T @ Rg[i + 1])),
           float(np.median(conf[i + 1]))) for i in range(len(names) - 1)]
    st = np.array(st); res["steps_vs_gyro"] = st.tolist()
    print("   time bin   steps  gyro step med  VGGT error med / max  conf med")
    for b0 in np.arange(np.floor(T[0] / 2) * 2, T[-1], 2.0):
        m = (st[:, 0] >= b0) & (st[:, 0] < b0 + 2)
        if m.any():
            print(f"   {b0:5.0f}-{b0 + 2:<4.0f} {m.sum():6d} {np.median(st[m, 1]):10.2f}° {np.median(st[m, 2]):12.2f}° / "
                  f"{st[m, 2].max():5.1f}° {np.median(st[m, 3]):8.2f}", flush=True)
    res["rot_vs_gyro_vggt"] = [float(np.median(ev)), float(np.percentile(ev, 90))]
    res["rot_vs_gyro_sfm"] = [float(np.median(em)), float(np.percentile(em, 90))] if em else None
    print(f"rotation vs gyro, all {len(ev)} pairs: VGGT median {np.median(ev):.2f}°, p90 {np.percentile(ev, 90):.2f}°"
          + (f"; SfM model ({len(have)} frames) median {np.median(em):.2f}°, p90 {np.percentile(em, 90):.2f}°" if em else ""),
          flush=True)

    # ---- 2. positions vs the SfM model ----
    obs = np.array([M[n][1] if n in M else -1 for n in names])
    anc = [k for k in have if obs[k] >= a.anchor_obs]
    if len(anc) >= 4:
        s, Rm, tt = umeyama(np.array([Cv[k][:3, 3] for k in anc]), np.array([M[names[k]][0][:3, 3] for k in anc]))
        Cal = (s * (Rm @ np.array([c[:3, 3] for c in Cv]).T)).T + tt
        d = np.array([np.linalg.norm(Cal[k] - M[names[k]][0][:3, 3]) if k in have else np.nan for k in range(len(names))])
        gap = [k for k in have if obs[k] < a.anchor_obs]
        step = np.median(np.linalg.norm(np.diff(np.array([M[names[k]][0][:3, 3] for k in have]), axis=0), axis=1))
        res["pos_anchor_resid"] = float(np.median(d[anc])); res["pos_gap_diff"] = float(np.nanmedian(d[gap])) if gap else None
        res["n_anchor"], res["n_gap"] = len(anc), len(gap)
        print(f"positions (model units; median SfM step between chunk frames {step:.3f}): Sim3 on {len(anc)} anchors "
              f"(>= {a.anchor_obs} obs): residual median {np.median(d[anc]):.3f}; {len(gap)} weakly supported frames: "
              f"VGGT vs SfM median {np.nanmedian(d[gap]) if gap else float('nan'):.3f}, max {np.nanmax(d[gap]) if gap else float('nan'):.3f}",
              flush=True)
        res["per_frame"] = [dict(name=names[k], t=float(T[k]), obs=int(obs[k]), vggt_vs_sfm=None if np.isnan(d[k]) else float(d[k]))
                            for k in range(len(names))]
    else:
        print(f"positions: only {len(anc)} anchors with >= {a.anchor_obs} observations, no alignment", flush=True)

    # ---- 3. depth consistency: VGGT vs Metric3D priors ----
    pairs = [(i, i + k) for k in (1, 2, 3) for i in range(len(names) - k)]
    Kv = intr
    cv_vggt = depth_consistency(depth, Kv, Cv, pairs, valid=conf > np.percentile(conf, 30, axis=(1, 2), keepdims=True))
    D_m, V_m, ok = [], [], True
    for n in names:
        p = os.path.join(a.sfm, "mono_prior", n + ".npz")
        if not os.path.exists(p):
            ok = False; break
        z = np.load(p); D_m.append(z["depth"].astype(np.float32)); V_m.append(z["valid"])
    line = f"depth consistency (median rel. error of i -> j, {len(pairs)} pairs 1-3 apart): VGGT {np.median(cv_vggt) * 100:.1f} %"
    res["depth_consistency_vggt"] = float(np.median(cv_vggt))
    if ok and all(n in M for n in names):
        dd = D_m[0].shape[1] / meta["W"]
        Km = [np.array([[meta["fx"] * dd, 0, meta["cx"] * dd], [0, meta["fy"] * dd, meta["cy"] * dd], [0, 0, 1]])] * len(names)
        Cm = [np.array(f["c2w"]) @ G for f in pick]                          # frames.json: OpenGL c2w -> OpenCV
        cv_m = depth_consistency(D_m, Km, Cm, pairs, valid=V_m)
        res["depth_consistency_metric3d"] = float(np.median(cv_m)) if cv_m else None
        line += (f"; Metric3D priors + SfM poses {np.median(cv_m) * 100:.1f} % ({len(cv_m)} pairs with valid priors)"
                 if cv_m else "; Metric3D: no valid pairs")
    print(line, flush=True)
    json.dump(res, open(os.path.join(a.out, "vggt_chunk.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
