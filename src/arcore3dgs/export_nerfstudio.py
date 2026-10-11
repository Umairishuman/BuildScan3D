"""Export a work dir as a Nerfstudio dataset (sanity baseline: train splatfacto on the same inputs).

Writes <work>/transforms.json (BA-refined c2w in OpenGL convention, which Nerfstudio uses), points
splatfacto at init_points.ply (BA + MVS-measured points from make_init.py), and creates the
downscaled image folder images_<d>/ that nerfstudio-data expects for --downscale-factor d.

  ns-train splatfacto --data <work> ... nerfstudio-data --auto-scale-poses False --center-method none
      --orientation-method none --downscale-factor 2 --load-3D-points True
"""
import os, json, argparse
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--downscale", type=int, default=2)
ap.add_argument("--frames_file", default="frames.json")
ap.add_argument("--ply", default="init_points.ply")
args = ap.parse_args()

meta = json.load(open(os.path.join(args.work, args.frames_file)))
meta["frames"] = [f for f in meta["frames"] if not f.get("fallback_unverified")]
out = {"camera_model": "OPENCV", "fl_x": meta["fx"], "fl_y": meta["fy"], "cx": meta["cx"], "cy": meta["cy"],
       "w": meta["W"], "h": meta["H"], "k1": 0.0, "k2": 0.0, "p1": 0.0, "p2": 0.0,
       "ply_file_path": args.ply,
       "frames": [{"file_path": f"images/{f['name']}.jpg", "transform_matrix": f["c2w"]} for f in meta["frames"]]}
json.dump(out, open(os.path.join(args.work, "transforms.json"), "w"), indent=1)

d = args.downscale
if d > 1:
    dst = os.path.join(args.work, f"images_{d}")
    os.makedirs(dst, exist_ok=True)
    for f in meta["frames"]:
        p = os.path.join(dst, f["name"] + ".jpg")
        if not os.path.exists(p):
            im = cv2.imread(os.path.join(args.work, "images", f["name"] + ".jpg"))
            cv2.imwrite(p, cv2.resize(im, (meta["W"] // d, meta["H"] // d), interpolation=cv2.INTER_AREA),
                        [cv2.IMWRITE_JPEG_QUALITY, 95])
print(f"transforms.json with {len(out['frames'])} frames; images_{d}/ ready")
