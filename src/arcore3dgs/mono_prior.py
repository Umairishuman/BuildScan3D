"""SfM-anchored monocular depth + normal priors for geometry-regularised 3DGS (v8geo).

Metric3D (ViT-L) predicts dense depth on every frame, including plain walls where stereo / SfM has no
points; its scale is unreliable (median error ~25% on newRoom), but its SHAPE (planarity, corners) is good.
Each frame's prediction is therefore aligned to the metric SfM points that frame observes with a robust
least-squares fit z_sfm = a * z_mono + b ("SfM-supervised monocular depth", as in Textureless-Splatter).
Normals are computed from the aligned depth (finite differences, OpenCV camera frame), so depth and
normal priors share one convention.

Writes <work>/mono_prior/<name>.npz at 1/4 resolution: depth (float16, m), normal (int8 x127, camera
frame), valid (bool), plus <work>/mono_prior/stats.json (alignment residuals per frame).

  python src/arcore3dgs/mono_prior.py --work <work_sfm>          (system python: Metric3D lives there)
  speed: --model small (ViT-S) and/or --fp16; --out / --limit for benchmarking without touching the priors
"""
import sys, types, os, json, argparse, time
from concurrent.futures import ThreadPoolExecutor
import numpy as np, cv2, torch

mm = types.ModuleType("mmcv"); mu = types.ModuleType("mmcv.utils"); mu.collect_env = lambda: {"OS": "Windows"}
sys.modules["mmcv"] = mm; sys.modules["mmcv.utils"] = mu

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--down", type=int, default=4)
ap.add_argument("--model", choices=["large", "small"], default="large")
ap.add_argument("--fp16", action="store_true", help="autocast the network to half precision")
ap.add_argument("--out", default="mono_prior", help="output folder inside --work")
ap.add_argument("--limit", type=int, default=0, help="only the first N frames (benchmarking)")
ap.add_argument("--fill_scale", action="store_true",
                help="frames with < 5 SfM points get a scale interpolated in time instead of no prior (FEATURELESS §10)")
ap.add_argument("--da3", default="",
                help="Depth Anything 3 weights folder (DA3-BASE / DA3-SMALL, Apache 2.0, D-098) instead of Metric3D: "
                     "overlapping chunks of consecutive frames, chunk scales chained so the whole walk shares one depth "
                     "scale (R-131: depth 2 - 5x more consistent across frames than Metric3D)")
ap.add_argument("--da3_chunk", type=int, default=32, help="frames per DA3 forward pass")
ap.add_argument("--da3_overlap", type=int, default=8, help="frames shared by consecutive chunks (scale chaining)")
ap.add_argument("--da3_res", type=int, default=504, help="DA3 processing resolution (longest side)")
args = ap.parse_args()
meta = json.load(open(os.path.join(args.work, "frames.json"))); fr = meta["frames"]
W, H, d = meta["W"], meta["H"], args.down
w, h = W // d, H // d
out_dir = os.path.join(args.work, args.out); os.makedirs(out_dir, exist_ok=True)
sp = np.load(os.path.join(args.work, "sparse.npz")); X, cam, pt, uv = sp["X"], sp["cam"], sp["pt"], sp["uv"]
G = np.diag([1.0, -1.0, -1.0, 1.0])
dev = torch.device("cuda")
model = None if args.da3 else torch.hub.load("yvanyin/metric3d", f"metric3d_vit_{args.model}", pretrain=True).to(dev).eval()
INPUT = (616, 1064)
MEAN = torch.tensor([123.675, 116.28, 103.53], device=dev).view(1, 3, 1, 1)
STD = torch.tensor([58.395, 57.12, 57.375], device=dev).view(1, 3, 1, 1)


@torch.no_grad()
def metric_depth(bgr):
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB); hh, ww = rgb.shape[:2]
    s = min(INPUT[0] / hh, INPUT[1] / ww)
    rgb = cv2.resize(rgb, (int(ww * s), int(hh * s)), interpolation=cv2.INTER_LINEAR)
    ph, pw = INPUT[0] - rgb.shape[0], INPUT[1] - rgb.shape[1]
    pad = [ph // 2, ph - ph // 2, pw // 2, pw - pw // 2]
    rgb = cv2.copyMakeBorder(rgb, pad[0], pad[1], pad[2], pad[3], cv2.BORDER_CONSTANT, value=[123.675, 116.28, 103.53])
    x = (torch.from_numpy(rgb.transpose(2, 0, 1)).float().to(dev)[None] - MEAN) / STD
    with torch.autocast("cuda", dtype=torch.float16, enabled=args.fp16):
        dd, _, _ = model.inference({"input": x})
    dd = dd.float()
    dd = dd.squeeze()[pad[0]:INPUT[0] - pad[1], pad[2]:INPUT[1] - pad[3]]
    dd = torch.nn.functional.interpolate(dd[None, None], (h, w), mode="bilinear").squeeze()
    return (dd * (meta["fx"] * s / 1000.0)).clamp(0, 50).cpu().numpy()


fx, fy, cx, cy = meta["fx"] / d, meta["fy"] / d, meta["cx"] / d, meta["cy"] / d
uu, vv = np.meshgrid(np.arange(w) + 0.5, np.arange(h) + 0.5)


def normals_from_depth(D):
    P = np.dstack([(uu - cx) / fx * D, (vv - cy) / fy * D, D])          # OpenCV camera frame
    dx = np.zeros_like(P); dy = np.zeros_like(P)
    dx[:, 1:-1] = P[:, 2:] - P[:, :-2]; dy[1:-1] = P[2:] - P[:-2]
    n = np.cross(dx, dy); n /= np.linalg.norm(n, axis=2, keepdims=True) + 1e-9
    flip = (n * P).sum(2) > 0                                          # face the camera
    n[flip] *= -1
    return n


def post(i, f, m):
    """align one frame's Metric3D depth to its SfM points, derive normals, save (runs in a worker thread)"""
    o = cam == i
    c2w = np.array(f["c2w"]) @ G
    z = ((X[pt[o]] - c2w[:3, 3]) @ c2w[:3, :3])[:, 2]
    px = np.clip((uv[o, 0] / d).astype(int), 0, w - 1); py = np.clip((uv[o, 1] / d).astype(int), 0, h - 1)
    zm = m[py, px]; ok = (z > 0.1) & (zm > 0.1)
    z, zm = z[ok], zm[ok]
    a, b, n_in = 1.0, 0.0, 0
    if len(z) >= 20:
        keep = np.ones(len(z), bool)
        for _ in range(4):                                              # robust LSQ: trim outliers
            A = np.stack([zm[keep], np.ones(keep.sum())], 1)
            a, b = np.linalg.lstsq(A, z[keep], rcond=None)[0]
            r = np.abs(a * zm + b - z) / z
            keep = r < max(0.03, 3 * np.median(r[keep]))
        n_in = int(keep.sum())
        if a <= 0.2 or a > 5:                                           # degenerate fit -> scale only
            a, b = float(np.median(z / zm)), 0.0
    elif len(z) >= 5:
        a = float(np.median(z / zm))
    D = a * m + b
    rel = np.abs(D[py[ok], px[ok]] - z) / z if len(z) else np.array([1.0])
    valid = (D > 0.15) & (D < 15) & (len(z) >= 5)
    Dn = cv2.medianBlur(D.astype(np.float32), 5)
    n = normals_from_depth(Dn)
    np.savez_compressed(os.path.join(out_dir, f["name"] + ".npz"), depth=D.astype(np.float16),
                        normal=np.clip(n * 127, -127, 127).astype(np.int8), valid=valid)
    stats[f["name"]] = dict(scale=float(a), shift=float(b), n_sfm=int(len(z)), inliers=n_in,
                            ratio=float(np.median(z / zm)) if len(z) else None,
                            median_rel_err=float(np.median(rel)), raw_median_rel_err=float(np.median(np.abs(zm - z) / z)) if len(z) else None)
    if i % 100 == 0:
        print(f"{i}/{len(fr)}  aligned median err {100 * np.median(rel):.1f}% (raw Metric3D "
              f"{100 * stats[f['name']]['raw_median_rel_err'] if len(z) else -1:.1f}%), scale {a:.3f}", flush=True)


def da3_depths(todo):
    """DA3 relative depth for every frame at (h, w), one shared scale along the walk.

    DA3's any-view models return depth up to one unknown scale per forward pass. Chunks of consecutive frames
    (time order) overlap; each chunk's depth is rescaled to the previous chunk by the median per-pixel ratio on
    the shared frames, so frames without SfM points can take their scale from their neighbours (--fill_scale)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import da3_loader
    DepthAnything3, stubbed = da3_loader.load_api()
    net = DepthAnything3.from_pretrained(args.da3).to(dev).eval()
    order = sorted(range(len(todo)), key=lambda k: todo[k][1]["pts"])
    step = max(1, args.da3_chunk - args.da3_overlap)
    starts = list(range(0, max(1, len(order) - args.da3_overlap), step))
    out, links = {}, []
    for c, s0 in enumerate(starts):
        ks = order[s0:s0 + args.da3_chunk]
        paths = [os.path.join(args.work, "images", todo[k][1]["name"] + ".jpg") for k in ks]
        with torch.no_grad():
            pred = net.inference(paths, process_res=args.da3_res)
        dep = torch.from_numpy(np.asarray(pred.depth, np.float32))[:, None]
        dep = torch.nn.functional.interpolate(dep, (h, w), mode="bilinear").squeeze(1).numpy()
        shared = [j for j, k in enumerate(ks) if k in out]
        s = 1.0
        if shared:
            r = [np.median(out[ks[j]][dep[j] > 1e-3] / dep[j][dep[j] > 1e-3]) for j in shared]
            s = float(np.median(r)); links.append((c, len(shared), s, float(np.std(np.log(r)))))
        for j, k in enumerate(ks):
            if k not in out:
                out[k] = dep[j] * s
        if c % 10 == 0:
            print(f"DA3 chunk {c + 1}/{len(starts)}: {len(ks)} frames, chain scale {s:.3f}", flush=True)
    del net; torch.cuda.empty_cache()
    sp_ = np.array([l[3] for l in links]) if links else np.zeros(1)
    print(f"DA3 ({args.da3}): {len(out)} frames in {len(starts)} chunks of {args.da3_chunk} (overlap {args.da3_overlap}); "
          f"spread of the chaining ratio over shared frames (std log): median {np.median(sp_):.3f}, max {sp_.max():.3f}; "
          f"stand-ins: {stubbed}", flush=True)
    return out


# the GPU only runs the network: the next JPEG is read and the previous frame aligned / saved in threads
stats = {}; t0 = time.time()
todo = list(enumerate(fr[:args.limit] if args.limit else fr))
read = lambda f: cv2.imread(os.path.join(args.work, "images", f["name"] + ".jpg"))
if args.da3:
    dd = da3_depths(todo)
    # bring the chained DA3 depth to roughly metres (one global factor), so post()'s scale sanity bounds apply
    rr = []
    for k, (i, f) in enumerate(todo):
        o = cam == i
        if o.sum() < 20:
            continue
        c2w = np.array(f["c2w"]) @ G
        z = ((X[pt[o]] - c2w[:3, 3]) @ c2w[:3, :3])[:, 2]
        px = np.clip((uv[o, 0] / d).astype(int), 0, w - 1); py = np.clip((uv[o, 1] / d).astype(int), 0, h - 1)
        zm = dd[k][py, px]; ok = (z > 0.1) & (zm > 1e-3)
        if ok.sum() >= 20:
            rr.append(np.median(z[ok] / zm[ok]))
    g = float(np.median(rr)) if rr else 1.0
    rr = np.array(rr) / g
    print(f"DA3 global scale {g:.4f} from {len(rr)} frames with >= 20 SfM points; per-frame ratio after it: "
          f"p10 {np.percentile(rr, 10):.3f}, p90 {np.percentile(rr, 90):.3f} (1.0 = the chain holds one scale)", flush=True)
    dd = {k: v * g for k, v in dd.items()}
    with ThreadPoolExecutor(3) as writer:
        for j in [writer.submit(post, i, f, dd[k]) for k, (i, f) in enumerate(todo)]:
            j.result()
else:
    with ThreadPoolExecutor(1) as reader, ThreadPoolExecutor(3) as writer:
        nxt = reader.submit(read, todo[0][1]) if todo else None
        jobs = []
        for k, (i, f) in enumerate(todo):
            img = nxt.result()
            if k + 1 < len(todo):
                nxt = reader.submit(read, todo[k + 1][1])
            jobs.append(writer.submit(post, i, f, metric_depth(img)))
        for j in jobs:
            j.result()                                                  # re-raise any worker error
if args.fill_scale and not args.limit:
    # Frames with < 5 SfM points (no image support: textureless walls, FEATURELESS_TRACKING_PLAN §10) would get no
    # depth / normal prior at all, so 3DGS is free to put their surfaces at any depth that fits the training view.
    # Metric3D's scale error drifts slowly along the walk, so such a frame gets a scale interpolated in time (log)
    # from the robust ratio median(z_sfm / z_mono) of well-fitted frames (>= 20 inliers, residual < 15 %), shift 0.
    # The leave-one-out error of that interpolation on the well-fitted frames is printed as the expected error.
    t = {f["name"]: f["pts"] for f in fr}
    good = sorted((t[n], np.log(s["ratio"]), n) for n, s in stats.items()
                  if s["inliers"] >= 20 and s["median_rel_err"] < 0.15 and s["ratio"])
    gt = np.array([g[0] for g in good]); gl = np.array([g[1] for g in good])
    loo = [abs(np.exp(np.interp(gt[k], np.delete(gt, k), np.delete(gl, k)) - gl[k]) - 1) for k in range(1, len(gt) - 1)]
    filled = 0
    for f in fr:
        s = stats[f["name"]]
        if s["n_sfm"] >= 5 or len(gt) < 2:
            continue
        a_f = float(np.exp(np.interp(t[f["name"]], gt, gl)))
        p = os.path.join(out_dir, f["name"] + ".npz")
        z_ = np.load(p); D = z_["depth"].astype(np.float32) * a_f       # saved with a = 1, b = 0 (raw Metric3D)
        n = normals_from_depth(cv2.medianBlur(D, 5))
        np.savez_compressed(p, depth=D.astype(np.float16), normal=np.clip(n * 127, -127, 127).astype(np.int8),
                            valid=(D > 0.15) & (D < 15))
        s["scale_filled"] = a_f; filled += 1                            # "scale" stays the fitted value (sfm_scale_check)
    print(f"fill_scale: {filled} frames without SfM support got a time-interpolated scale from {len(gt)} well-fitted "
          f"frames; leave-one-out scale error on those: median {100 * np.median(loo):.1f} %, p90 "
          f"{100 * np.percentile(loo, 90):.1f} %", flush=True)
json.dump(stats, open(os.path.join(out_dir, "stats.json"), "w"), indent=1)
e = np.array([s["median_rel_err"] for s in stats.values()]); r = np.array([s["raw_median_rel_err"] for s in stats.values() if s["raw_median_rel_err"] is not None])
print(f"done: {len(stats)} frames in {time.time() - t0:.0f} s, aligned median error {100 * np.median(e):.1f}% (raw Metric3D {100 * np.median(r):.1f}%)")
