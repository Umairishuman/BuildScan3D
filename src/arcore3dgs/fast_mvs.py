"""Fast dense initialisation: COLMAP PatchMatch on a subset of frames at low resolution (minutes, not hours).

The v6/v8 quality comes from a dense MVS init (mvs_init.py, PatchMatch on all 1108 frames at 1000 px: 2 h 15 m);
the mono-depth init (mono_init.py, 12 s) covers plain walls but loses detail seen by few frames. Depth for an
INIT does not need every frame at high resolution: here every --every-th frame is a reference view at
--size px, with --sources source views chosen among the same subset by shared SfM points (so the geometric
consistency pass only needs depth maps that are computed anyway). Fusion -> mvs_init.py (Sim3 to the
metric world, voxels, + SfM points). Optionally --mono adds the mono-depth points of mono_init.py where the
MVS has nothing (plain walls) -> a hybrid init.

  python src/arcore3dgs/fast_mvs.py --work <work_sfm> --json transforms_offpath.json --out_json transforms_offpath_fmvs.json
Needs <work>/undist/sparse (sfm_colmap.py undistort stage) and <work>/images (undistorted).
"""
import os, json, argparse, subprocess, shutil, time
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True); ap.add_argument("--json", required=True); ap.add_argument("--out_json", required=True)
ap.add_argument("--every", type=int, default=7); ap.add_argument("--size", type=int, default=640)
ap.add_argument("--sources", type=int, default=6); ap.add_argument("--min_pixels", type=int, default=3)
ap.add_argument("--mono", action="store_true", help="add mono-depth points where the MVS cloud is empty")
ap.add_argument("--colmap", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools",
                                                 "colmap_dl", "colmap-4.2.0", "COLMAP.bat"))
args = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__)); WK = os.path.abspath(args.work); CM = os.path.abspath(args.colmap)
ws = os.path.join(WK, "undist_fast")
t0 = time.time()


def colmap(*a):
    print(">", a[0], flush=True)
    with open(os.path.join(ws, f"{a[0]}.log"), "w") as f:
        subprocess.run([CM] + [str(x) for x in a], check=True, stdout=f, stderr=subprocess.STDOUT)


if os.path.exists(ws):
    if os.path.exists(os.path.join(ws, "images")):
        os.rmdir(os.path.join(ws, "images"))                # removes the junction only (fails safely on a real dir)
    shutil.rmtree(ws)
os.makedirs(os.path.join(ws, "stereo", "depth_maps")); os.makedirs(os.path.join(ws, "stereo", "normal_maps"))
os.makedirs(os.path.join(ws, "stereo", "consistency_graphs"))
shutil.copytree(os.path.join(WK, "undist", "sparse"), os.path.join(ws, "sparse"))
# the workspace's images/ = the undistorted training images (directory junction: no copy)
subprocess.run(["cmd", "/c", "mklink", "/J", os.path.join(ws, "images"), os.path.join(WK, "images")], check=True,
               capture_output=True)

meta = json.load(open(os.path.join(WK, "frames.json"))); fr = meta["frames"]
sub = list(range(0, len(fr), args.every))
sp = np.load(os.path.join(WK, "sparse.npz")); cam, pt = sp["cam"], sp["pt"]
vis = {}                                                     # SfM points seen by each subset frame
for i in sub:
    vis[i] = set(pt[cam == i].tolist())
C = np.array([np.array(f["c2w"])[:3, 3] for f in fr])
srcs = {}
for i in sub:
    score = sorted(((len(vis[i] & vis[j]), j) for j in sub if j != i and np.linalg.norm(C[i] - C[j]) > 0.05), reverse=True)
    srcs[i] = [j for s_, j in score[: args.sources] if s_ >= 20]
# the geometric pass needs every source's own depth map: sources must be reference frames too (iterate,
# since dropping a reference with < 2 sources can leave others short)
while True:
    refs = {i for i, s_ in srcs.items() if len(s_) >= 2}
    srcs = {i: [j for j in srcs[i] if j in refs] for i in refs}
    if all(len(s_) >= 2 for s_ in srcs.values()):
        break
pm = [f"{fr[i]['name']}.jpg\n" + ", ".join(f"{fr[j]['name']}.jpg" for j in srcs[i]) for i in sorted(srcs)]
fu = [f"{fr[i]['name']}.jpg" for i in sorted(srcs)]
open(os.path.join(ws, "stereo", "patch-match.cfg"), "w").write("\n".join(pm) + "\n")
open(os.path.join(ws, "stereo", "fusion.cfg"), "w").write("\n".join(fu) + "\n")
print(f"{len(fu)} reference frames (every {args.every}th of {len(fr)}) at {args.size} px, {args.sources} sources each", flush=True)
colmap("patch_match_stereo", "--workspace_path", ws, "--workspace_format", "COLMAP",
       "--PatchMatchStereo.max_image_size", args.size, "--PatchMatchStereo.geom_consistency", "true")
t1 = time.time()
colmap("stereo_fusion", "--workspace_path", ws, "--workspace_format", "COLMAP", "--input_type", "geometric",
       "--output_path", os.path.join(ws, "fused.ply"), "--StereoFusion.min_num_pixels", args.min_pixels,
       "--StereoFusion.max_image_size", args.size)
t2 = time.time()
ply = "init_fmvs.ply"
subprocess.run(["python", os.path.join(HERE, "mvs_init.py"), "--work", WK, "--sparse", os.path.join(ws, "sparse"),
                "--fused", os.path.join(ws, "fused.ply"), "--out_ply", ply, "--out_json", "_tmp_fmvs.json"], check=True)
os.remove(os.path.join(WK, "_tmp_fmvs.json"))
if args.mono:                                                # hybrid: mono points only where MVS found nothing
    subprocess.run(["python", os.path.join(HERE, "mono_init.py"), "--work", WK, "--json", args.json, "--out_json", "_tmp_mono.json",
                    "--every", "6", "--voxel", "0.015", "--min_views", "6", "--base", ply, "--fill_only", "0.05",
                    "--out_ply", "init_fmvs_mono.ply"], check=True)
    os.remove(os.path.join(WK, "_tmp_mono.json")); ply = "init_fmvs_mono.ply"
tj = json.load(open(os.path.join(WK, args.json))); tj["ply_file_path"] = ply
json.dump(tj, open(os.path.join(WK, args.out_json), "w"), indent=1)
shutil.rmtree(os.path.join(ws, "stereo", "depth_maps")); shutil.rmtree(os.path.join(ws, "stereo", "normal_maps"))
shutil.rmtree(os.path.join(ws, "stereo", "consistency_graphs"))
print(f"done: PatchMatch {(t1 - t0) / 60:.1f} min, fusion {(t2 - t1) / 60:.1f} min, total {(time.time() - t0) / 60:.1f} min "
      f"-> {ply}, {args.out_json}")
