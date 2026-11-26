"""v8 pipeline, one command: ARCore capture -> metric 3DGS, every stage timed (Problems_and_Solutions 4.15).

  select_sharp (gyro-aware keyframes) -> sfm_colmap --pairs arcore (ARCore-guided matching, global mapper,
  undistort, Sim3 to ARCore) -> export_nerfstudio -> mono_prior (Metric3D aligned to the SfM points) ->
  mono_init (dense init from the aligned depth; replaces the 2 h PatchMatch) -> geo_splatfacto (depth +
  edge-aware normal priors, DashGaussian resolution schedule, 15k) -> ns-export.

  python src/arcore3dgs/run_v8.py --dataset dataset/<capture> [--tag v8] [--iters 15000] [--split <offpath_test.txt>]
Output: <dataset>/work_<tag>_sfm/gs_<tag>/splat.ply (metric, ARCore world, +Y up) and timing.json next to it.
--split holds out the frames listed in that file (for eval_offpath.py); without it every frame trains.
Run with system python (Metric3D and COLMAP wrappers); nerfstudio steps use nerfstudio-env automatically.

--auto (2026-11-27, Tayyab: "the user inputs video -> gets web viewer output", no hand-picked stretches; D-099,
PIPELINE_ANALYZER_PLAN): the recipe and the per-recording choices are made here, not by the caller:
  recipe    keep frames without an ARCore pose (--pose_free), SfM with retrieval pairs, fast-MVS init, planar prior,
            blur model, PGSR-lite, camera refinement in training (--pose_opt)
  analyze   analyze_recording.py labels every 5 s window textured / weak / featureless / hole from the SfM output
            and says whether normal SfM placed the recording (route)
  densify   weak / featureless windows get the dropped video frames between placed keyframes (densify_frames.py,
            R-128: +0.29 dB for +3.6 min); SfM model and frames re-exported with them
  prior     Depth Anything 3 (DA3-BASE, Apache 2.0, D-098) with the confidence cut-off (R-133) when its weights are
            found (--da3), else Metric3D (non-commercial licence, D-098)
Every choice and its reason goes to gs_<tag>/auto.json. A recording SfM cannot place (route "sensor path") is
reported there; the sensor-path camera chain is not automated yet, so the run continues with the frames SfM placed.
"""
import os, sys, json, time, shutil, argparse, subprocess
import toolpaths

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", required=True)
ap.add_argument("--tag", default="v8")
ap.add_argument("--iters", type=int, default=15000)
ap.add_argument("--window", type=int, default=6, help="select_sharp window (frames)")
ap.add_argument("--pose_free", action="store_true",
                help="select_sharp --pose_free: keep frames without an ARCore pose; SfM places them from the images")
ap.add_argument("--mono_model", default="large", choices=["large", "small"],
                help="Metric3D size; per 1108 frames on a 3070 (fp16): large ~7 min, small ~2.6 min, aligned error 1.8%% vs 2.0%%")
ap.add_argument("--no_fp16", action="store_true", help="Metric3D in full precision (2x slower, same aligned error)")
ap.add_argument("--split", default="", help="file with held-out frame names (e.g. offpath_test.txt)")
ap.add_argument("--from_stage", default="select",
                choices=["select", "sfm", "analyze", "densify", "export", "prior", "init", "train", "ply"])
ap.add_argument("--auto", action="store_true",
                help="recipe + analyzer-driven choices (see the docstring); writes gs_<tag>/auto.json")
ap.add_argument("--da3", default=os.path.join(os.environ.get("BUILDSCAN_CACHE", os.path.join(os.path.expanduser("~"), ".cache", "buildscan")),
                                              "da3_weights", "DA3-BASE"),
                help="--auto: DA3 weights folder for the depth priors (Metric3D when it does not exist)")
ap.add_argument("--da3_conf_min", type=float, default=1.1, help="--auto: DA3 confidence cut-off (R-133)")
ap.add_argument("--no_densify", action="store_true", help="--auto: do not add frames in weak windows")
ap.add_argument("--frame_budget", type=int, default=1100,
                help="--auto: most training frames (keyframes + densified); RAM, ~5.8 MB each")
ap.add_argument("--sfm_args", default="", help='extra sfm_colmap.py args, e.g. "--retrieval 20" or "--feature aliked"')
ap.add_argument("--init", default="fmvs", choices=["mono", "fmvs", "fmvs_mono"],
                help="dense init: mono depth (12 s), fast PatchMatch on every 7th frame (fast_mvs.py), or both")
ap.add_argument("--planar", type=float, default=0.0, help="> 0: planar prior weight (plane_seg.py runs on the CPU during init)")
ap.add_argument("--blur", type=float, default=0.0, help="> 0: motion-blur model with this exposure (s)")
ap.add_argument("--init_args", default="", help='extra fast_mvs.py args, e.g. "--photometric" (7.5 vs 20 min, TRAINING R-063)')
ap.add_argument("--prior_args", default="", help='extra mono_prior.py args, e.g. "--fill_scale" (FEATURELESS §10)')
ap.add_argument("--pgsr", action="store_true", help="PGSR-lite in the same training (the best model's recipe, R-023)")
ap.add_argument("--save_every", type=int, default=2500, help="checkpoint interval for --resume after a crash")
ap.add_argument("--pose_opt", action="store_true", help="refine camera poses during training (sensor-path models)")
ap.add_argument("--blur_gyro", default="", help="motion-blur velocities from the gyro where ARCore has no pose: path to "
                "a gyro bias json (gyro_loop_bias.py) or 'nobias'; per-frame exposure from camera.csv (FEATURELESS 10.f)")
ap.add_argument("--train_args", default="", help='extra geo_splatfacto.py args, e.g. "--depth_lambda 0.1"')
args = ap.parse_args()
AUTO = {"recipe": [], "decisions": []}                      # --auto: what was chosen and why (gs_<tag>/auto.json)
if args.auto:
    # the best general recipe (RUN_PIPELINE §4, R-023) + camera refinement (R-120); the caller's explicit values win
    if not args.pose_free:
        args.pose_free = True; AUTO["recipe"].append("--pose_free: frames without an ARCore pose stay, SfM places them")
    if "--retrieval" not in args.sfm_args:
        args.sfm_args = (args.sfm_args + " --retrieval 20").strip(); AUTO["recipe"].append("SfM pairs by image retrieval (20)")
    if args.planar == 0:
        args.planar = 0.2; AUTO["recipe"].append("planar prior 0.2")
    if args.blur == 0:
        args.blur = 0.0222; AUTO["recipe"].append("motion-blur model, exposure 1/45 s")
    if not args.pgsr:
        args.pgsr = True; AUTO["recipe"].append("PGSR-lite (flat surfaces, unbiased depth for the mesh)")
    if not args.pose_opt:
        args.pose_opt = True; AUTO["recipe"].append("camera refinement during training (R-120)")
    # Frame budget: training caches every image (~5.8 MB at 1839 x 1048); ~1,100 frames fit a 16 GB PC (R-069 needed
    # --window 8 on a long recording by hand). Window = video frames / budget, at least 6 (the default).
    if args.window == 6:
        import cv2
        cap_ = cv2.VideoCapture(os.path.join(os.path.abspath(args.dataset), "dataset.mp4"))
        n_vid = int(cap_.get(cv2.CAP_PROP_FRAME_COUNT)); cap_.release()
        if n_vid > 0:
            args.window = max(6, -(-n_vid // args.frame_budget))
            AUTO["recipe"].append(f"keyframe window {args.window}: {n_vid} video frames, budget {args.frame_budget} "
                                  "training frames (RAM)")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.join(ROOT, "src", "arcore3dgs")
D = os.path.abspath(args.dataset)
W, S = os.path.join(D, f"work_{args.tag}"), os.path.join(D, f"work_{args.tag}_sfm")
NAME = f"{os.path.basename(D)}_{args.tag}"
OUT = os.path.join(S, f"gs_{args.tag}")
env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
STAGES = ["select", "sfm", "analyze", "densify", "export", "prior", "init", "train", "ply"]
timing_file = os.path.join(OUT, "timing.json")
os.makedirs(OUT, exist_ok=True)
timing = json.load(open(timing_file)) if os.path.exists(timing_file) else {}


def run(stage, cmd, log=None, extra_env=None):
    if STAGES.index(stage) < STAGES.index(args.from_stage):
        return
    print(f"== {stage}: {' '.join(cmd)}", flush=True)
    t0 = time.time()
    e = dict(env, **(extra_env or {}))
    if log:
        with open(log, "w") as f:
            r = subprocess.run(cmd, cwd=ROOT, env=e, stdout=f, stderr=subprocess.STDOUT)
    else:
        r = subprocess.run(cmd, cwd=ROOT, env=e)
    if r.returncode:
        sys.exit(f"stage {stage} failed ({r.returncode})" + (f", see {log}" if log else ""))
    timing[stage] = round((time.time() - t0) / 60, 2)
    json.dump(timing, open(timing_file, "w"), indent=1)
    print(f"   {stage} {timing[stage]:.1f} min", flush=True)


py, nspy = sys.executable, toolpaths.ns_cmd("python")   # nspy is a command list
run("select", [py, os.path.join(HERE, "select_sharp.py"), "--dataset", D, "--out", W, "--window", str(args.window)]
    + (["--pose_free"] if args.pose_free else []))
run("sfm", [py, os.path.join(HERE, "sfm_colmap.py"), "--work", W, "--out", S, "--pairs", "arcore"] + args.sfm_args.split())


def save_auto():
    AUTO["timing_min"] = timing
    json.dump(AUTO, open(os.path.join(OUT, "auto.json"), "w"), indent=1)


if args.auto:
    analysis = os.path.join(S, "analysis.json")
    run("analyze", [py, os.path.join(HERE, "analyze_recording.py"), "--selection", W, "--model", S, "--out", analysis])
    an = json.load(open(analysis))
    AUTO["analysis"] = {k: an[k] for k in ("duration_s", "selected", "placed", "placed_share", "obs_median",
                                           "arcore_tracked", "hole_time_s", "labels", "route")}
    AUTO["analysis"]["windows"] = "".join({"textured": "T", "weak": "w", "featureless": "f", "hole": "_"}[w["label"]]
                                          for w in an["windows"])
    if an["route"] != "normal SfM":
        AUTO["decisions"].append(
            f"route: SfM placed {100 * an['placed_share']:.0f} % of the keyframes, holes {an['hole_time_s']:.0f} s of "
            f"{an['duration_s']:.0f} s: this recording needs the sensor-path camera chain (not automated yet, "
            "PIPELINE_ANALYZER_PLAN §2.2); continuing with the frames SfM placed")
    else:
        AUTO["decisions"].append(f"route: normal SfM ({100 * an['placed_share']:.0f} % of the keyframes placed)")
    n_weak = an["labels"].get("weak", 0) + an["labels"].get("featureless", 0)
    room = min(300, args.frame_budget - an["selected"])            # densify cap within the RAM budget
    if args.no_densify or n_weak == 0 or room < 20:
        AUTO["decisions"].append("densify: no" + (" (--no_densify)" if args.no_densify else
                                                  ": no weak / featureless windows" if n_weak == 0 else
                                                  f": the frame budget is used ({an['selected']} keyframes)"))
    else:
        AUTO["decisions"].append(f"densify: yes, {n_weak} weak / featureless windows of {len(an['windows'])} get the "
                                 "video frames between their placed keyframes (R-128)")
        sp0, keep = os.path.join(S, "sparse", "0"), os.path.join(S, "sparse_sfm")
        if STAGES.index(args.from_stage) <= STAGES.index("densify"):
            if not os.path.isdir(keep):
                shutil.copytree(sp0, keep)                   # the SfM model as mapped, kept for a re-run
            dense = os.path.join(S, "sparse_dense")
            shutil.rmtree(dense, ignore_errors=True)
            run("densify", [py, os.path.join(HERE, "densify_frames.py"), D, W, keep, analysis, dense,
                            "--max_new", str(room)])
            shutil.rmtree(sp0); shutil.copytree(dense, sp0)
            for st in ("undistort", "export"):              # undistort the added frames, Sim3 + frames.json again
                t0 = time.time()
                r = subprocess.run([py, os.path.join(HERE, "sfm_colmap.py"), "--work", W, "--out", S, "--stage", st]
                                   + args.sfm_args.split(), cwd=ROOT, env=env)
                if r.returncode:
                    sys.exit(f"densify: sfm_colmap --stage {st} failed ({r.returncode})")
                timing["densify"] = round(timing.get("densify", 0) + (time.time() - t0) / 60, 2)
            json.dump(timing, open(timing_file, "w"), indent=1)
            add = json.load(open(os.path.join(dense, "densify.json")))
            AUTO["densify_added"] = len(add["added"])
    if os.path.isdir(args.da3) and os.path.exists(os.path.join(args.da3, "model.safetensors")):
        args.prior_args = (args.prior_args + f" --da3 {args.da3} --fill_scale --da3_conf_min {args.da3_conf_min}").strip()
        AUTO["decisions"].append(f"depth priors: Depth Anything 3 ({os.path.basename(args.da3)}, Apache 2.0) with the "
                                 f"confidence cut-off {args.da3_conf_min}; frames without SfM points get a filled prior "
                                 "where DA3 is confident (R-133)")
    else:
        AUTO["decisions"].append(f"depth priors: Metric3D (DA3 weights not found at {args.da3}); NOTE: Metric3D's "
                                 "licence is non-commercial (D-098)")
    save_auto()
if STAGES.index(args.from_stage) <= STAGES.index("export"):
    shutil.rmtree(os.path.join(S, "undist", "images"), ignore_errors=True)   # export copies what it needs
run("export", nspy + [os.path.join(HERE, "export_nerfstudio.py"), "--work", S, "--downscale", "1"])
data = "transforms.json"
if args.split and STAGES.index(args.from_stage) <= STAGES.index("export"):
    held = set(open(args.split).read().split())
    tj = json.load(open(os.path.join(S, data)))
    fp = [f["file_path"] for f in tj["frames"]]
    tj["train_filenames"] = [p for p in fp if os.path.splitext(os.path.basename(p))[0] not in held]
    tj["val_filenames"] = tj["test_filenames"] = [p for p in fp if os.path.splitext(os.path.basename(p))[0] in held]
    json.dump(tj, open(os.path.join(S, data), "w"), indent=1)
    shutil.copy(args.split, os.path.join(S, "offpath_test.txt"))
    print(f"   split: {len(tj['train_filenames'])} train / {len(tj['test_filenames'])} held out")
mono = [py, os.path.join(HERE, "mono_prior.py"), "--work", S, "--model", args.mono_model] + ([] if args.no_fp16 else ["--fp16"]) + args.prior_args.split()
run("prior", mono)
# warn when SfM placed part of the room at a different scale ("mini room", TRAINING R-066 / R-067); warning only
if STAGES.index(args.from_stage) <= STAGES.index("prior") and os.path.exists(os.path.join(S, "sparse", "0", "points3D.txt")):
    subprocess.run([py, os.path.join(HERE, "sfm_scale_check.py"), os.path.join(S, "sparse", "0"),
                    os.path.join(S, "mono_prior"), "--json", os.path.join(OUT, "sfm_scale_check.json")], cwd=ROOT, env=env)
# CPU side jobs for the priors (plane regions, camera motion) run while the GPU does the dense init
side = []
if STAGES.index(args.from_stage) <= STAGES.index("init"):
    if args.planar > 0:
        side.append(subprocess.Popen([py, os.path.join(HERE, "plane_seg.py"), "--work", S], cwd=ROOT, env=env,
                                     stdout=open(os.path.join(OUT, "plane_seg.log"), "w"), stderr=subprocess.STDOUT))
    if args.blur > 0:
        bg = ([] if args.blur_gyro in ("", "nobias") else ["--bg_json", args.blur_gyro])
        gy = (["--source", "gyro", "--gyro_calib", S, "--per_frame_exposure"] + bg) if args.blur_gyro else []  # ARCore vs gyro: 14 deg median apart on scan_009
        side.append(subprocess.Popen([py, os.path.join(HERE, "blur_motion.py"), "--work", S] + gy, cwd=ROOT, env=env,
                                     stdout=open(os.path.join(OUT, "blur_motion.log"), "w"), stderr=subprocess.STDOUT))
init_json = f"transforms_{args.init}.json"
if args.init == "mono":
    run("init", [py, os.path.join(HERE, "mono_init.py"), "--work", S, "--json", data, "--out_json", init_json,
                 "--every", "6", "--voxel", "0.015", "--min_views", "6"])
else:
    run("init", [py, os.path.join(HERE, "fast_mvs.py"), "--work", S, "--json", data, "--out_json", init_json]
        + (["--mono"] if args.init == "fmvs_mono" else []) + args.init_args.split())
t_side = time.time()
for p_ in side:
    if p_.wait():
        sys.exit("plane_seg / blur_motion failed, see their logs in " + OUT)
if side:
    timing["init_wait_cpu"] = round((time.time() - t_side) / 60, 2)
half = str(args.iters // 2)
run("train", nspy + ["-W", "ignore", os.path.join(HERE, "geo_splatfacto.py"), "--data", os.path.join(S, init_json),
              "--name", NAME, "--iters", str(args.iters), "--dash_res_steps", half, "--stop_split_at", half, "--no_eval",
              "--prior", os.path.join(S, "mono_prior", f"train_{args.tag}.npz"),
              "--planar_lambda", str(args.planar), "--blur_exposure", str(args.blur),
              "--save_every", str(args.save_every)] + (["--pgsr"] if args.pgsr else [])
              + (["--pose_opt"] if args.pose_opt else []) + args.train_args.split(), log=os.path.join(OUT, "train.log"))
cfg = os.path.join(ROOT, "outputs", "v8", "splatfacto", NAME, "config.yml")
run("ply", toolpaths.ns_cmd("ns-export") + ["gaussian-splat", "--load-config", cfg, "--output-dir", OUT],
    log=os.path.join(OUT, "export.log"), extra_env={"PYTHONPATH": HERE})
shutil.rmtree(os.path.join(ROOT, "outputs", "v8", "splatfacto", NAME, "nerfstudio_models"), ignore_errors=True)
timing["total"] = round(sum(v for k, v in timing.items() if k in STAGES + ["init_wait_cpu"]), 1)
json.dump(timing, open(timing_file, "w"), indent=1)
if args.auto:
    timing["total"] = round(sum(v for k, v in timing.items() if k in STAGES + ["init_wait_cpu"]), 1)
    save_auto()
    print("auto: " + " | ".join(AUTO["decisions"]))
print(f"Done: {os.path.join(OUT, 'splat.ply')}  timing (min): {timing}")
