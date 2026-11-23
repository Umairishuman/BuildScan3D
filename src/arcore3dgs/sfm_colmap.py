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
import toolpaths
from scipy.spatial.transform import Rotation as R

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True, help="existing work dir (frames.json + images/ from prepare.py)")
ap.add_argument("--out", required=True)
ap.add_argument("--colmap", default=toolpaths.colmap(), help="COLMAP 4.2 executable (default: see toolpaths.py)")
ap.add_argument("--mapper", default="global_mapper", choices=["global_mapper", "mapper"])
ap.add_argument("--skip_retriangulation", action="store_true",
                help="global_mapper: skip the final retriangulation + refinement (6.5 of 14.3 min on newRoom; poses stay "
                     "within the mapper's own run-to-run differences, TRAINING R-064)")
ap.add_argument("--extract_gpu", type=int, default=1, help="0 = CPU SIFT (e.g. while the GPU is training)")
ap.add_argument("--pairs", default="exhaustive", choices=["exhaustive", "arcore"],
                help="arcore = match only temporal + ARCore-pose neighbours (much faster than exhaustive)")
ap.add_argument("--temporal", type=int, default=10)
ap.add_argument("--spatial", type=int, default=20)
ap.add_argument("--gyro_thr", type=float, default=0.0,
                help="export: drop frames whose SfM rotation disagrees with the gyroscope by more than this many degrees "
                     "(median over keyframe pairs within 1 s; gyro_check.py, FEATURELESS_TRACKING_PLAN step 1). 0 = off")
ap.add_argument("--place_unplaced", type=int, default=0,
                help="export, needs --gyro_thr: place frames SfM did not register (or the gyro check dropped) with the gyro "
                     "rotation + a known-rotation fit to their matched 3D points (known_rot_pnp.py), if >= this many "
                     "inlier matches (e.g. 4). 0 = off")
ap.add_argument("--sim3", default="arcore", choices=["arcore", "none"],
                help="export: 'none' keeps the model's own world (rot_sfm.py with the accelerometer: already metric, +Y up)")
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
ap.add_argument("--gravity", default="arcore", choices=["arcore", "centres"],
                help="export: 'arcore' (D-071) levels the world with ARCore's camera orientations, then fits scale, "
                     "yaw and translation to the camera centres; 'centres' = the old full Sim3 from centres only "
                     "(can leave the model tilted: 9-12 deg on scans #2 / #3, R-032)")
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
ENV = dict(os.environ, PATH=os.pathsep.join([d for d in _dll if os.path.isdir(d)] + [os.environ.get("PATH", "")]))
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


def arcore_c2w(x):
    """Raw ARCore c2w of a frames.json entry, NaN (4x4) when the frame has none (select_sharp.py --pose_free)."""
    m = x.get("c2w_arcore", x.get("c2w"))
    return np.full((4, 4), np.nan) if m is None else np.array(m)


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
        # Frames without an ARCore pose (select_sharp.py --pose_free) get NaN here: no spatial pairs, only the
        # temporal ones (+ retrieval); SfM places them from the images.
        C = np.array([arcore_c2w(x)[:3, 3] for x in fr])
        Dv = np.array([-arcore_c2w(x)[:3, 2] for x in fr])                                  # OpenGL: -z = forward
        pairs = set()
        for i in range(len(fr)):
            for j in range(i + 1, min(len(fr), i + 1 + args.temporal)):
                pairs.add((i, j))
            if not np.isfinite(C[i]).all():
                continue
            dist = np.linalg.norm(C - C[i], axis=1) + 1.5 * (1 - Dv @ Dv[i])                # metres + view-angle penalty
            dist[~np.isfinite(dist)] = np.inf
            dist[max(0, i - args.temporal):i + args.temporal + 1] = np.inf
            for j in np.argsort(dist)[: args.spatial]:
                if np.isfinite(dist[j]) and Dv[i] @ Dv[j] > 0.3:
                    pairs.add((min(i, j), max(i, j)))
        names = [x["name"] + ".jpg" for x in fr]
        with open(os.path.join(OUT, "pairs.txt"), "w") as f:
            f.write("\n".join(f"{names[i]} {names[j]}" for i, j in sorted(pairs)))
        print(f"{len(pairs)} ARCore-guided pairs ({len(pairs) / len(fr):.1f}/frame, exhaustive would be "
              f"{len(fr) * (len(fr) - 1) // 2}); {int((~np.isfinite(C).all(1)).sum())} frames without an ARCore pose "
              f"(temporal + retrieval pairs only)", flush=True)
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
        colmap(args.mapper, "--database_path", db, "--image_path", os.path.join(WK, "images"), "--output_path", sp,
               *(["--GlobalMapper.skip_retriangulation", 1] if args.skip_retriangulation and args.mapper == "global_mapper" else []))
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


def umeyama_yaw(src, dst):
    """Sim3 with the rotation about +Y only (both point sets already have +Y = up): scale, yaw, translation."""
    ms, md = src.mean(0), dst.mean(0); S, D = src - ms, dst - md
    th = np.arctan2((D[:, 0] * S[:, 2] - D[:, 2] * S[:, 0]).sum(), (D[:, 0] * S[:, 0] + D[:, 2] * S[:, 2]).sum())
    c, s_ = np.cos(th), np.sin(th); Ry = np.array([[c, 0, s_], [0, 1, 0], [-s_, 0, c]])
    sc = (D * (S @ Ry.T)).sum() / (S ** 2).sum()
    return sc, Ry, md - sc * Ry @ ms


def level_rotation(u):
    """smallest rotation taking unit vector u onto +Y"""
    Y = np.array([0.0, 1.0, 0.0]); v = np.cross(u, Y); s_, c = np.linalg.norm(v), float(u @ Y)
    if s_ < 1e-9:
        return np.eye(3) if c > 0 else np.diag([1.0, -1.0, -1.0])
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K * ((1 - c) / s_ ** 2)


def arcore_up(frames, rot_of):
    """ARCore's up direction (+Y of its gravity-aligned world) expressed in another world, from every frame's two
    camera orientations (OpenGL camera axes in both); robust mean. rot_of(frame) = that frame's c2w rotation there."""
    Y = np.array([0.0, 1.0, 0.0]); U = []
    for x in frames:
        Ra = np.array(x.get("c2w_arcore", x["c2w"]))[:3, :3]
        U.append(rot_of(x) @ (Ra.T @ Y))
    U = np.array(U); U /= np.linalg.norm(U, axis=1, keepdims=True); keep = np.ones(len(U), bool)
    for _ in range(3):
        u = U[keep].mean(0); u /= np.linalg.norm(u)
        dev = np.degrees(np.arccos(np.clip(U @ u, -1, 1))); keep = dev < max(2.0, 3 * np.median(dev))
    return u, float(np.median(dev)), int(keep.sum())


if run("export"):
    cams0, imgs0, _ = read_model(os.path.join(OUT, "sparse", "0"))
    cams, imgs, pts = read_model(os.path.join(OUT, "undist", "sparse"))
    gyro_rep = None
    if args.gyro_thr > 0:
        # frames SfM placed with a rotation the gyroscope contradicts are misplaced: drop them before the Sim3
        # fit and the jump filter, so they distort neither
        from gyro_check import check as gyro_check
        from common import Capture
        gyro_rep = gyro_check(meta["dataset"], fr, {n: v[0][:3, :3] for n, v in imgs.items()},
                              Capture(meta["dataset"]).t0_ns, meta.get("pose_offset", 0.0), thr_deg=args.gyro_thr)
        for n in gyro_rep["flagged"]:
            imgs.pop(n, None)
        print(f"gyro check: dropped {len(gyro_rep['flagged'])} frames over {args.gyro_thr} deg")
    placed = []
    if args.place_unplaced > 0 and gyro_rep is not None:
        # FEATURELESS_TRACKING_PLAN step 4 (points): rotation from the gyro (chained from the nearest accepted
        # frames), position from >= 2 matched 3D points with that rotation fixed. The jump filter below still applies.
        from gyro_check import fill_rotations
        import known_rot_pnp as krp
        mimgs, mX, mcam = krp.load_model(os.path.join(OUT, "sparse", "0"))
        kps, mts = krp.load_db(db)
        acc = [x for x in fr if x["name"] in imgs]
        t_acc = np.array([x["pts"] + meta.get("pose_offset", 0.0) for x in acc])
        anchors = {x["name"] for x in acc}
        cnt = {}
        for n in anchors:
            if n in mimgs:
                for pid in mimgs[n][2][mimgs[n][2] >= 0]:
                    cnt[pid] = cnt.get(pid, 0) + 1
        valid = {q for q, c in cnt.items() if c >= 2}
        todo = [x for x in fr if x["name"] not in imgs and x["name"] in kps]
        t_todo = np.array([x["pts"] + meta.get("pose_offset", 0.0) for x in todo])
        near = np.array([np.min(np.abs(t_acc - tq)) for tq in t_todo]) if len(t_todo) else np.zeros(0)
        Rq = fill_rotations(gyro_rep["imu"], gyro_rep["Rci"], gyro_rep["off"], t_acc,
                            [imgs[x["name"]][0][:3, :3] for x in acc], t_todo)
        cu = cams[list(cams)[0]]; c0 = cams0[list(cams0)[0]]
        K0 = np.array([[c0[3][0], 0, c0[3][2]], [0, c0[3][1], c0[3][3]], [0, 0, 1]])
        Ku = np.array([[cu[3][0], 0, cu[3][2]], [0, cu[3][1], cu[3][3]], [0, 0, 1]])
        umap = cv2.initUndistortRectifyMap(K0, np.array(c0[3][4:8]), None, Ku, (cu[1], cu[2]), cv2.CV_32FC1)
        for x, Rk, dn in zip(todo, Rq, near):
            if dn > 15.0:
                continue
            uv, Xs = krp.correspondences(x["name"], kps, mts, mimgs, mX, anchors, valid)
            C, m = krp.place_known_rotation(Rk, krp.bearings(uv, mcam), Xs)
            if C is None or m.sum() < args.place_unplaced or m.mean() < 0.5:
                continue
            c2w = np.eye(4); c2w[:3, :3] = Rk; c2w[:3, 3] = C
            imgs[x["name"]] = (c2w, None)
            placed.append(x["name"])
            dst = os.path.join(OUT, "images", x["name"] + ".jpg")      # where the export loop looks first
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.exists(dst):
                im = cv2.imread(os.path.join(WK, "images", x["name"] + ".jpg"))
                cv2.imwrite(dst, cv2.remap(im, umap[0], umap[1], cv2.INTER_LINEAR), [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"placed {len(placed)} of {len(todo)} unplaced frames with gyro rotation + known-rotation fit "
              f"(>= {args.place_unplaced} inliers)")
    names = [x["name"] for x in fr if x["name"] in imgs]
    # Sim3 COLMAP -> ARCore metric world: RANSAC on camera centres against the RAW ARCore poses. ARCore
    # re-anchors silently (here ~1 m / 28 deg at 60 s), so only its largest self-consistent segment is used;
    # the scale matches the BA-refined poses to 0.06% (newRoomAttemptSadness), so no BA is needed.
    idx = {x["name"]: i for i, x in enumerate(fr)}
    trust = [n for n in names if np.isfinite(arcore_c2w(fr[idx[n]])).all()]    # frames with an ARCore pose
    A = np.array([imgs[n][0][:3, 3] for n in trust])
    B = np.array([arcore_c2w(fr[idx[n]])[:3, 3] for n in trust])
    # Gravity (D-071): camera centres alone leave the rotation about the walk's main direction weakly fixed (a short or
    # nearly straight walk), so the world is first levelled with ARCore's orientations (gravity-aligned in every frame,
    # also across re-anchors); then only scale, yaw and translation come from the centres.
    up_col, up_spread, up_n = arcore_up([fr[idx[n]] for n in trust], lambda x: imgs[x["name"]][0][:3, :3] @ G[:3, :3])
    Rl = level_rotation(up_col) if args.gravity == "arcore" else np.eye(3)
    fit = umeyama_yaw if args.gravity == "arcore" else umeyama
    A0 = A; A = A @ Rl.T
    rng = np.random.default_rng(0); best = None
    for _ in range(2000):
        k = rng.choice(len(A), 4, replace=False); s, Rm, t = fit(A[k], B[k])
        inl = np.linalg.norm((s * (Rm @ A.T)).T + t - B, axis=1) < 0.10
        if best is None or inl.sum() > best.sum():
            best = inl
    s, Rm, t = fit(A[best], B[best])
    res = np.linalg.norm((s * (Rm @ A.T)).T + t - B, axis=1)
    Rm = Rm @ Rl                                             # COLMAP world -> levelled -> ARCore metric world
    tilt = float(np.degrees(np.arccos(np.clip((Rm @ up_col)[1], -1, 1))))
    R0 = umeyama(A0[best], B[best])[1]      # a full-rotation Sim3 on the same inliers, for comparison only (the old
    tilt_centres = float(np.degrees(np.arccos(np.clip((R0 @ up_col)[1], -1, 1))))   # RANSAC picked other inliers)
    print(f"for comparison: a full-rotation Sim3 on these inliers would be {tilt_centres:.2f} deg off gravity")
    print(f"Sim3 ({args.gravity}): scale {s:.4f}, {best.sum()} / {len(A)} centre inliers, median {np.median(res[best]) * 100:.1f} cm; "
          f"ARCore gravity {tilt:.2f} deg from the model's +Y (per-frame spread {up_spread:.2f} deg, {up_n} frames)")
    if args.sim3 == "none":                                   # metric, gravity-aligned model (rot_sfm.py --imu 1)
        s, Rm, t = 1.0, np.eye(3), np.zeros(3)
        print("sim3: none (the model is already metric and +Y up)")
    T = np.eye(4); T[:3, :3] = s * Rm; T[:3, 3] = t
    cam = cams[list(cams)[0]]; fx, fy, cx, cy = cam[3][:4]
    out_frames = []
    os.makedirs(os.path.join(OUT, "images"), exist_ok=True)
    for x in fr:
        if x["name"] not in imgs:
            continue
        c2w = imgs[x["name"]][0].copy()                      # OpenCV camera, COLMAP world
        c2w_m = np.eye(4); c2w_m[:3, :3] = Rm @ c2w[:3, :3]; c2w_m[:3, 3] = s * Rm @ c2w[:3, 3] + t
        y = dict(x); y["c2w"] = (c2w_m @ G).tolist(); y["c2w_arcore"] = x.get("c2w_arcore", x.get("c2w"))
        y.pop("fallback_unverified", None)                  # registered by SfM from the images = verified
        if x["name"] in placed:
            y["placed_by"] = "gyro_rotation+known_rotation_pnp"
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
                                        gyro_check=None if gyro_rep is None else dict(
                                            thr_deg=args.gyro_thr, dropped=gyro_rep["flagged"],
                                            time_offset_ms=gyro_rep["time_offset_ms"],
                                            pair_err_deg_median=gyro_rep["pair_err_deg_median"],
                                            pair_err_deg_p90=gyro_rep["pair_err_deg_p90"]),
                                        placed_unplaced=placed,
                                        gravity=args.gravity, gravity_tilt_deg=tilt, gravity_spread_deg=up_spread,
                                        gravity_tilt_full_sim3_same_inliers_deg=tilt_centres,
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
