"""Standard SfM poses + self-calibrated lens for 3DGS, made metric with ARCore.

Why: with ARCore's factory intrinsics (no distortion) and our ARCore-initialised BA, even TRAINING views
only reached ~24.5 dB and 8% of keyframes were never registered (their raw ARCore poses polluted the model).
COLMAP self-calibration found f +1% and k1/k2 = 0.08/-0.18 (several px at mid-image) -> every view slightly
misaligned -> 3DGS averages them into blur. Phone-video 3DGS apps all estimate poses AND lens from the
images; ARCore is used here only for metric scale + gravity (Sim3 alignment of camera centres).

Stages (all into <work_sfm>):
  extract   SIFT on the keyframes, one OPENCV camera initialised from ARCore intrinsics
  match     exhaustive GPU matching (592 frames ~ 20 min)
  map       global_mapper (GLOMAP) -> sparse/0, refines poses + focal + distortion
  undistort image_undistorter -> undistorted PINHOLE images
  export    Sim3-align to the ARCore/BA poses, write frames.json (same format as prepare.py),
            images/, init_points.ply (SfM points), report.json

  python src/arcore3dgs/sfm_colmap.py --work <dataset>/work --out <dataset>/work_sfm [--stage all]
"""
import os, json, argparse, subprocess, shutil, struct, importlib.util
import numpy as np, cv2
from scipy.spatial.transform import Rotation as R

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True, help="existing work dir (frames.json + images/ from prepare.py)")
ap.add_argument("--out", required=True)
ap.add_argument("--colmap", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools",
                                                 "colmap_dl", "colmap-4.2.0", "COLMAP.bat"))
ap.add_argument("--mapper", default="global_mapper", choices=["global_mapper", "mapper"])
ap.add_argument("--extract_gpu", type=int, default=1, help="0 = CPU SIFT (e.g. while the GPU is training)")
ap.add_argument("--pairs", default="exhaustive", choices=["exhaustive", "arcore"],
                help="arcore = match only temporal + ARCore-pose neighbours (much faster than exhaustive)")
ap.add_argument("--temporal", type=int, default=10)
ap.add_argument("--spatial", type=int, default=20)
ap.add_argument("--stage", default="all", choices=["all", "extract", "match", "map", "undistort", "export"])
ap.add_argument("--feature", default="sift", choices=["sift", "aliked"],
                help="aliked = learned ALIKED-N16rot keypoints + LightGlue matching (COLMAP 4.2 ONNX models)")
ap.add_argument("--max_features", type=int, default=0, help="0 = 8192 SIFT / 4096 ALIKED")
ap.add_argument("--retrieval", type=int, default=0,
                help="> 0: also match each frame with its N most similar frames by vocabulary-tree "
                     "retrieval -- loop closures that ARCore-pose neighbours miss after ARCore drift")
ap.add_argument("--vocab", default="", help="faiss vocabulary tree (default: tools/colmap_dl/vocab/, SIFT or ALIKED)")
ap.add_argument("--bridge", type=int, default=1,
                help="if mapping splits into several components, match the frames outside the largest one against "
                     "a sample of it and map again (up to N rounds)")
args = ap.parse_args()
MATCH_TYPE = "ALIKED_LIGHTGLUE" if args.feature == "aliked" else "SIFT_BRUTEFORCE"
TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools")
VOCAB = args.vocab or os.path.join(TOOLS, "colmap_dl", "vocab", "vocab_tree_faiss_flickr100K_words64K_aliked_n16rot.bin"
                                   if args.feature == "aliked" else "vocab_tree_faiss_flickr100K_words32K.bin")
# COLMAP's ONNX models (ALIKED, LightGlue) run on onnxruntime-CUDA, which needs cuBLAS 12 + cuDNN 9 DLLs:
# tools/cudnn9 (from NVIDIA's nvidia-cudnn-cu12 wheel) + this Python's torch/lib
_dll = [os.path.abspath(os.path.join(TOOLS, "cudnn9"))]
_ts = importlib.util.find_spec("torch")
if _ts and _ts.origin:
    _dll.append(os.path.join(os.path.dirname(_ts.origin), "lib"))
ENV = dict(os.environ, PATH=";".join([d for d in _dll if os.path.isdir(d)] + [os.environ.get("PATH", "")]))
WK = os.path.abspath(args.work); OUT = os.path.abspath(args.out); CM = os.path.abspath(args.colmap)
os.makedirs(OUT, exist_ok=True)
db = os.path.join(OUT, "database.db")
meta = json.load(open(os.path.join(WK, "frames.json"))); fr = meta["frames"]
G = np.diag([1.0, -1.0, -1.0, 1.0])


def colmap(*a, log=None):
    cmd = [CM] + [str(x) for x in a]
    print(">", a[0], flush=True)
    with open(os.path.join(OUT, f"{a[0]}.log"), "w") as f:
        subprocess.run(cmd, check=True, stdout=f, stderr=subprocess.STDOUT, env=ENV)


def run(stage):
    return args.stage in ("all", stage)


if run("extract"):
    if os.path.exists(db):
        os.remove(db)
    with open(os.path.join(OUT, "image_list.txt"), "w") as f:
        f.write("\n".join(x["name"] + ".jpg" for x in fr))
    colmap("feature_extractor", "--database_path", db, "--image_path", os.path.join(WK, "images"),
           "--image_list_path", os.path.join(OUT, "image_list.txt"),
           "--ImageReader.single_camera", 1, "--ImageReader.camera_model", "OPENCV",
           "--ImageReader.camera_params", f"{meta['fx']},{meta['fy']},{meta['cx']},{meta['cy']},0,0,0,0",
           "--FeatureExtraction.use_gpu", args.extract_gpu,
           *(["--FeatureExtraction.type", "ALIKED_N16ROT", "--AlikedExtraction.max_num_features", args.max_features or 4096]
             if args.feature == "aliked" else ["--SiftExtraction.max_num_features", args.max_features or 8192]))

if run("match"):
    if args.pairs == "exhaustive":
        colmap("exhaustive_matcher", "--database_path", db, "--FeatureMatching.use_gpu", 1, "--FeatureMatching.type", MATCH_TYPE)
    else:
        # ARCore-guided pairs: +-args.temporal neighbours in time, plus the args.spatial nearest cameras by ARCore
        # pose (position + viewing direction). ARCore's world is only locally consistent (silent re-anchors), so
        # neighbours are searched within it but the global SfM still decides the poses. ~30 pairs/frame instead of N.
        C = np.array([np.array(x.get("c2w_arcore", x["c2w"]))[:3, 3] for x in fr])
        Dv = np.array([-np.array(x.get("c2w_arcore", x["c2w"]))[:3, 2] for x in fr])        # OpenGL: -z = forward
        pairs = set()
        for i in range(len(fr)):
            for j in range(i + 1, min(len(fr), i + 1 + args.temporal)):
                pairs.add((i, j))
            dist = np.linalg.norm(C - C[i], axis=1) + 1.5 * (1 - Dv @ Dv[i])                # metres + view-angle penalty
            dist[max(0, i - args.temporal):i + args.temporal + 1] = np.inf
            for j in np.argsort(dist)[: args.spatial]:
                if np.isfinite(dist[j]) and Dv[i] @ Dv[j] > 0.3:
                    pairs.add((min(i, j), max(i, j)))
        names = [x["name"] + ".jpg" for x in fr]
        with open(os.path.join(OUT, "pairs.txt"), "w") as f:
            f.write("\n".join(f"{names[i]} {names[j]}" for i, j in sorted(pairs)))
        print(f"{len(pairs)} ARCore-guided pairs ({len(pairs) / len(fr):.1f}/frame, exhaustive would be "
              f"{len(fr) * (len(fr) - 1) // 2})", flush=True)
        colmap("matches_importer", "--database_path", db, "--match_list_path", os.path.join(OUT, "pairs.txt"),
               "--match_type", "pairs", "--FeatureMatching.use_gpu", 1, "--FeatureMatching.type", MATCH_TYPE)
        if args.retrieval > 0:
            colmap("vocab_tree_matcher", "--database_path", db, "--VocabTreeMatching.vocab_tree_path", os.path.abspath(VOCAB),
                   "--VocabTreeMatching.num_images", args.retrieval, "--FeatureMatching.use_gpu", 1,
                   "--FeatureMatching.type", MATCH_TYPE)


def components(sp):
    """Image names of every model the mapper wrote (largest first)."""
    comps = []
    for d in sorted(os.listdir(sp)):
        if not os.path.isdir(os.path.join(sp, d)):
            continue
        tmp = os.path.join(OUT, "_comp_txt"); os.makedirs(tmp, exist_ok=True)
        colmap("model_converter", "--input_path", os.path.join(sp, d), "--output_path", tmp, "--output_type", "TXT")
        L = [l for l in open(os.path.join(tmp, "images.txt")) if l[0] != "#"][0::2]
        comps.append((d, [l.split()[9][:-4] for l in L if len(l.split()) >= 10]))
        shutil.rmtree(tmp)
    return sorted(comps, key=lambda c: -len(c[1]))


if run("map"):
    sp = os.path.join(OUT, "sparse")
    for rnd in range(args.bridge + 1):
        if os.path.exists(sp):
            shutil.rmtree(sp)
        os.makedirs(sp)
        colmap(args.mapper, "--database_path", db, "--image_path", os.path.join(WK, "images"), "--output_path", sp)
        comps = components(sp)
        print(f"mapping round {rnd}: components {[len(c[1]) for c in comps]} of {len(fr)} frames", flush=True)
        if comps and comps[0][0] != "0":                     # export reads sparse/0: make it the largest
            os.rename(os.path.join(sp, "0"), os.path.join(sp, "_0")); os.rename(os.path.join(sp, comps[0][0]), os.path.join(sp, "0"))
            os.rename(os.path.join(sp, "_0"), os.path.join(sp, comps[0][0]))
        if len(comps) < 2 or rnd == args.bridge:
            break
        # Bridge: the frames outside the largest component (plus the unregistered ones) are matched against an
        # even sample of the largest component; ARCore-pose neighbours miss these links after an ARCore drift.
        main = comps[0][1]; out_ = [x["name"] for x in fr if x["name"] not in set(main)]
        sample = main[:: max(1, len(main) // 80)]
        pairs = {(a, b) if a < b else (b, a) for a in out_ for b in sample}
        with open(os.path.join(OUT, f"pairs_bridge{rnd}.txt"), "w") as f:
            f.write("\n".join(f"{a}.jpg {b}.jpg" for a, b in sorted(pairs)))
        print(f"bridge round {rnd}: {len(out_)} frames outside the main component x {len(sample)} -> {len(pairs)} pairs", flush=True)
        colmap("matches_importer", "--database_path", db, "--match_list_path", os.path.join(OUT, f"pairs_bridge{rnd}.txt"),
               "--match_type", "pairs", "--FeatureMatching.use_gpu", 1, "--FeatureMatching.type", MATCH_TYPE)

if run("undistort"):
    d = os.path.join(OUT, "undist")
    if os.path.exists(d):
        shutil.rmtree(d)
    colmap("image_undistorter", "--image_path", os.path.join(WK, "images"), "--input_path", os.path.join(OUT, "sparse", "0"),
           "--output_path", d, "--output_type", "COLMAP")
    colmap("model_converter", "--input_path", os.path.join(d, "sparse"), "--output_path", os.path.join(d, "sparse"),
           "--output_type", "TXT")
    colmap("model_converter", "--input_path", os.path.join(OUT, "sparse", "0"), "--output_path", os.path.join(OUT, "sparse", "0"),
           "--output_type", "TXT")


def read_model(d):
    cams = {}
    for l in open(os.path.join(d, "cameras.txt")):
        if l[0] == "#" or not l.strip():
            continue
        p = l.split(); cams[int(p[0])] = (p[1], int(p[2]), int(p[3]), list(map(float, p[4:])))
    imgs = {}
    L = [l for l in open(os.path.join(d, "images.txt")) if l[0] != "#"]
    for a in L[0::2]:
        p = a.split()
        if len(p) < 10:
            continue
        q = np.array(list(map(float, p[1:5]))); t = np.array(list(map(float, p[5:8])))
        w2c = np.eye(4); w2c[:3, :3] = R.from_quat([q[1], q[2], q[3], q[0]]).as_matrix(); w2c[:3, 3] = t
        imgs[p[9][:-4]] = (np.linalg.inv(w2c), int(p[8]))
    pts = []
    for l in open(os.path.join(d, "points3D.txt")):
        if l[0] == "#" or not l.strip():
            continue
        p = l.split(); pts.append([float(x) for x in p[1:8]] + [len(p[8:]) // 2])
    return cams, imgs, np.array(pts)


def umeyama(src, dst):
    ms, md = src.mean(0), dst.mean(0); S, D = src - ms, dst - md
    U, s, Vt = np.linalg.svd(D.T @ S / len(src)); E = np.eye(3)
    if np.linalg.det(U @ Vt) < 0:
        E[2, 2] = -1
    Rm = U @ E @ Vt; sc = np.trace(np.diag(s) @ E) / S.var(0).sum()
    return sc, Rm, md - sc * Rm @ ms


if run("export"):
    cams0, imgs0, _ = read_model(os.path.join(OUT, "sparse", "0"))
    cams, imgs, pts = read_model(os.path.join(OUT, "undist", "sparse"))
    names = [x["name"] for x in fr if x["name"] in imgs]
    # Sim3 COLMAP -> ARCore metric world: RANSAC on camera centres against the RAW ARCore poses. ARCore
    # re-anchors silently (here ~1 m / 28 deg at 60 s), so only its largest self-consistent segment is used;
    # the scale matches the BA-refined poses to 0.06% (newRoomAttemptSadness), so no BA is needed.
    idx = {x["name"]: i for i, x in enumerate(fr)}
    trust = names
    A = np.array([imgs[n][0][:3, 3] for n in trust])
    B = np.array([np.array(fr[idx[n]].get("c2w_arcore", fr[idx[n]]["c2w"]))[:3, 3] for n in trust])
    rng = np.random.default_rng(0); best = None
    for _ in range(2000):
        k = rng.choice(len(A), 4, replace=False); s, Rm, t = umeyama(A[k], B[k])
        inl = np.linalg.norm((s * (Rm @ A.T)).T + t - B, axis=1) < 0.10
        if best is None or inl.sum() > best.sum():
            best = inl
    s, Rm, t = umeyama(A[best], B[best])
    res = np.linalg.norm((s * (Rm @ A.T)).T + t - B, axis=1)
    T = np.eye(4); T[:3, :3] = s * Rm; T[:3, 3] = t
    cam = cams[list(cams)[0]]; fx, fy, cx, cy = cam[3][:4]
    out_frames = []
    os.makedirs(os.path.join(OUT, "images"), exist_ok=True)
    for x in fr:
        if x["name"] not in imgs:
            continue
        c2w = imgs[x["name"]][0].copy()                      # OpenCV camera, COLMAP world
        c2w_m = np.eye(4); c2w_m[:3, :3] = Rm @ c2w[:3, :3]; c2w_m[:3, 3] = s * Rm @ c2w[:3, 3] + t
        y = dict(x); y["c2w"] = (c2w_m @ G).tolist(); y["c2w_arcore"] = x.get("c2w_arcore", x["c2w"])
        y.pop("fallback_unverified", None)                  # registered by SfM from the images = verified
        out_frames.append(y)
        dst = os.path.join(OUT, "images", x["name"] + ".jpg")
        if not os.path.exists(dst):
            shutil.copy(os.path.join(OUT, "undist", "images", x["name"] + ".jpg"), dst)
    # SfM mis-registrations: a slowly walked video cannot jump; drop frames > 30 cm from the median of
    # their +-3 temporal neighbours (global SfM occasionally snaps a frame onto a similar-looking place)
    Cs = np.array([np.array(y["c2w"])[:3, 3] for y in out_frames])
    dev = np.array([np.linalg.norm(Cs[i] - np.median(Cs[[j for j in range(max(0, i - 3), min(len(Cs), i + 4)) if j != i]], 0))
                    for i in range(len(Cs))])
    jumps = [y["name"] for y, d_ in zip(out_frames, dev) if d_ > 0.3]
    out_frames = [y for y, d_ in zip(out_frames, dev) if d_ <= 0.3]
    print(f"dropped {len(jumps)} mis-registered frames (jump > 30 cm from temporal neighbours)")
    m2 = dict(meta); m2.update(W=cam[1], H=cam[2], fx=fx, fy=fy, cx=cx, cy=cy, frames=out_frames,
                               sfm=dict(source="colmap " + args.mapper, registered=len(out_frames), total=len(fr),
                                        sim3_scale=float(s), align_inliers=int(best.sum()), align_trusted=len(trust),
                                        align_median_cm=float(np.median(res[best]) * 100), dropped_jumps=jumps,
                                        distorted_camera=dict(model=cams0[list(cams0)[0]][0], params=cams0[list(cams0)[0]][3])))
    m2.pop("ba", None); m2.pop("fusion_dropped", None)
    json.dump(m2, open(os.path.join(OUT, "frames.json"), "w"), indent=1)
    # metric sparse.npz (X, cam, pt, uv in undistorted pixels) for compare_models.py / train.py --sparse_depth_w
    kept = {y["name"]: k for k, y in enumerate(out_frames)}
    P3 = {}
    for l in open(os.path.join(OUT, "undist", "sparse", "points3D.txt")):
        if l[0] != "#" and l.strip():
            p = l.split(); P3[int(p[0])] = [float(v) for v in p[1:4]]
    pid = sorted(P3); pmap = {k: i for i, k in enumerate(pid)}
    Xs = (s * (Rm @ np.array([P3[k] for k in pid]).T)).T + t
    L = [l for l in open(os.path.join(OUT, "undist", "sparse", "images.txt")) if l[0] != "#"]
    cam_l, pt_l, uv_l = [], [], []
    for a_, b_ in zip(L[0::2], L[1::2]):
        n_ = a_.split()[9][:-4]
        if n_ not in kept or not b_.strip():
            continue
        xy = np.array(b_.split(), float).reshape(-1, 3); xy = xy[xy[:, 2] >= 0]
        cam_l += [kept[n_]] * len(xy); pt_l += [pmap[int(k)] for k in xy[:, 2]]; uv_l.append(xy[:, :2])
    np.savez(os.path.join(OUT, "sparse.npz"), X=Xs, cam=np.array(cam_l), pt=np.array(pt_l),
             uv=np.concatenate(uv_l).astype(np.float32))
    # SfM points (seen in >= 3 images) -> metric init cloud
    P = pts[pts[:, 7] >= 3]; X = (s * (Rm @ P[:, :3].T)).T + t
    el = np.zeros(len(X), [("x", "f4"), ("y", "f4"), ("z", "f4"), ("red", "u1"), ("green", "u1"), ("blue", "u1")])
    el["x"], el["y"], el["z"] = X.T; el["red"], el["green"], el["blue"] = P[:, 3:6].T.astype(np.uint8)
    with open(os.path.join(OUT, "init_points.ply"), "wb") as f:
        f.write((f"ply\nformat binary_little_endian 1.0\nelement vertex {len(el)}\nproperty float x\nproperty float y\n"
                 "property float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n").encode())
        f.write(el.tobytes())
    rep = m2["sfm"]; rep.update(points=len(X), undistorted_size=[cam[1], cam[2]], pinhole=[fx, fy, cx, cy])
    json.dump(rep, open(os.path.join(OUT, "report.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1))
