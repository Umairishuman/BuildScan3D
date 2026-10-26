"""v8 pipeline, one command: ARCore capture -> metric 3DGS, every stage timed (Problems_and_Solutions 4.15).

  select_sharp (gyro-aware keyframes) -> sfm_colmap --pairs arcore (ARCore-guided matching, global mapper,
  undistort, Sim3 to ARCore) -> export_nerfstudio -> mono_prior (Metric3D aligned to the SfM points) ->
  mono_init (dense init from the aligned depth; replaces the 2 h PatchMatch) -> geo_splatfacto (depth +
  edge-aware normal priors, DashGaussian resolution schedule, 15k) -> ns-export.

  python src/arcore3dgs/run_v8.py --dataset dataset/<capture> [--tag v8] [--iters 15000] [--split <offpath_test.txt>]
Output: <dataset>/work_<tag>_sfm/gs_<tag>/splat.ply (metric, ARCore world, +Y up) and timing.json next to it.
--split holds out the frames listed in that file (for eval_offpath.py); without it every frame trains.
Run with system python (Metric3D and COLMAP wrappers); nerfstudio steps use nerfstudio-env automatically.
"""
import os, sys, json, time, shutil, argparse, subprocess

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", required=True)
ap.add_argument("--tag", default="v8")
ap.add_argument("--iters", type=int, default=15000)
ap.add_argument("--window", type=int, default=6, help="select_sharp window (frames)")
ap.add_argument("--mono_model", default="large", choices=["large", "small"],
                help="Metric3D size; per 1108 frames on a 3070 (fp16): large ~7 min, small ~2.6 min, aligned error 1.8%% vs 2.0%%")
ap.add_argument("--no_fp16", action="store_true", help="Metric3D in full precision (2x slower, same aligned error)")
ap.add_argument("--split", default="", help="file with held-out frame names (e.g. offpath_test.txt)")
ap.add_argument("--from_stage", default="select", choices=["select", "sfm", "export", "prior", "init", "train", "ply"])
ap.add_argument("--sfm_args", default="", help='extra sfm_colmap.py args, e.g. "--retrieval 20" or "--feature aliked"')
ap.add_argument("--init", default="fmvs", choices=["mono", "fmvs", "fmvs_mono"],
                help="dense init: mono depth (12 s), fast PatchMatch on every 7th frame (fast_mvs.py), or both")
ap.add_argument("--planar", type=float, default=0.0, help="> 0: planar prior weight (plane_seg.py runs on the CPU during init)")
ap.add_argument("--blur", type=float, default=0.0, help="> 0: motion-blur model with this exposure (s)")
args = ap.parse_args()

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.join(ROOT, "src", "arcore3dgs")
NS = os.path.join(ROOT, "nerfstudio-env", "Scripts")
D = os.path.abspath(args.dataset)
W, S = os.path.join(D, f"work_{args.tag}"), os.path.join(D, f"work_{args.tag}_sfm")
NAME = f"{os.path.basename(D)}_{args.tag}"
OUT = os.path.join(S, f"gs_{args.tag}")
env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
STAGES = ["select", "sfm", "export", "prior", "init", "train", "ply"]
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


py, nspy = sys.executable, os.path.join(NS, "python.exe")
run("select", [py, os.path.join(HERE, "select_sharp.py"), "--dataset", D, "--out", W, "--window", str(args.window)])
run("sfm", [py, os.path.join(HERE, "sfm_colmap.py"), "--work", W, "--out", S, "--pairs", "arcore"] + args.sfm_args.split())
if STAGES.index(args.from_stage) <= STAGES.index("export"):
    shutil.rmtree(os.path.join(S, "undist", "images"), ignore_errors=True)   # export copies what it needs
run("export", [nspy, os.path.join(HERE, "export_nerfstudio.py"), "--work", S, "--downscale", "1"])
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
mono = [py, os.path.join(HERE, "mono_prior.py"), "--work", S, "--model", args.mono_model] + ([] if args.no_fp16 else ["--fp16"])
run("prior", mono)
# CPU side jobs for the priors (plane regions, camera motion) run while the GPU does the dense init
side = []
if STAGES.index(args.from_stage) <= STAGES.index("init"):
    if args.planar > 0:
        side.append(subprocess.Popen([py, os.path.join(HERE, "plane_seg.py"), "--work", S], cwd=ROOT, env=env,
                                     stdout=open(os.path.join(OUT, "plane_seg.log"), "w"), stderr=subprocess.STDOUT))
    if args.blur > 0:
        side.append(subprocess.Popen([py, os.path.join(HERE, "blur_motion.py"), "--work", S], cwd=ROOT, env=env,
                                     stdout=open(os.path.join(OUT, "blur_motion.log"), "w"), stderr=subprocess.STDOUT))
init_json = f"transforms_{args.init}.json"
if args.init == "mono":
    run("init", [py, os.path.join(HERE, "mono_init.py"), "--work", S, "--json", data, "--out_json", init_json,
                 "--every", "6", "--voxel", "0.015", "--min_views", "6"])
else:
    run("init", [py, os.path.join(HERE, "fast_mvs.py"), "--work", S, "--json", data, "--out_json", init_json]
        + (["--mono"] if args.init == "fmvs_mono" else []))
t_side = time.time()
for p_ in side:
    if p_.wait():
        sys.exit("plane_seg / blur_motion failed, see their logs in " + OUT)
if side:
    timing["init_wait_cpu"] = round((time.time() - t_side) / 60, 2)
half = str(args.iters // 2)
run("train", [nspy, "-W", "ignore", os.path.join(HERE, "geo_splatfacto.py"), "--data", os.path.join(S, init_json),
              "--name", NAME, "--iters", str(args.iters), "--dash_res_steps", half, "--stop_split_at", half, "--no_eval",
              "--prior", os.path.join(S, "mono_prior", f"train_{args.tag}.npz"),
              "--planar_lambda", str(args.planar), "--blur_exposure", str(args.blur)], log=os.path.join(OUT, "train.log"))
cfg = os.path.join(ROOT, "outputs", "v8", "splatfacto", NAME, "config.yml")
run("ply", [os.path.join(NS, "ns-export.exe"), "gaussian-splat", "--load-config", cfg, "--output-dir", OUT],
    log=os.path.join(OUT, "export.log"), extra_env={"PYTHONPATH": HERE})
shutil.rmtree(os.path.join(ROOT, "outputs", "v8", "splatfacto", NAME, "nerfstudio_models"), ignore_errors=True)
timing["total"] = round(sum(v for k, v in timing.items() if k in STAGES + ["init_wait_cpu"]), 1)
json.dump(timing, open(timing_file, "w"), indent=1)
print(f"Done: {OUT}\\splat.ply  timing (min): {timing}")
