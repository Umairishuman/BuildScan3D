"""Rolling-shutter rectification of keyframes with the gyroscope (FEATURELESS_TRACKING_PLAN §10, step 10.b).

A phone camera reads the image row by row: on scan_009 the readout takes 19.5 ms (camera.csv), so at the walk's
17 deg/s median rotation the first and last rows see the room from orientations ~0.3 deg apart: a shear of 8 px
median, 17 px p90, against a 1.1 px reprojection error. Every stage after this (matching, tracks, SfM, training)
assumes one camera pose per image.

The fix used here is rotation only: for each keyframe, re-render the image as a global-shutter camera at the
frame's own time (its `pts`, taken as the middle of the readout). For an output pixel p, the ray b = K^-1 p
(undistorted) is rotated into the camera orientation at the time its source row was read,
b_row = R_cam(t_row)^T R_cam(t_ref) b, and projected again with the lens distortion; t_row depends on the source row,
so this is iterated (3 times; converges because the shift is small). The translation during 19.5 ms (~1 cm) is
ignored. Lens distortion is kept, so the output stays a drop-in replacement for the keyframe (same camera model).

The readout direction (image rows or columns, top-down or bottom-up) depends on how the sensor sits in the phone, so
`--axis auto --sign auto` decides it from the video: for the fastest-rotating keyframes, the next video frame
(33 ms later) is warped onto the keyframe with the gyro rotation, after rectifying both with each candidate; the
candidate with the smallest photometric error wins (the translation in 33 ms is small at room distances).

Gyro and camera are aligned with gyro_check (Kabsch on a model's rotations), as in rot_sfm.py; use the best model
available for that (on scan_009: R-080's `work_v9pfz_sfm`).

  python src/arcore3dgs/rs_rectify.py <dataset> <keyframe dir in> <sfm dir with sparse/0> <keyframe dir out>
      [--bg_json gyro_loop_bias.json] [--axis auto|rows|cols] [--sign auto|1|-1] [--skew_ms <from camera.csv>]
      [--probe_only]

The output folder gets images/ (rectified, same names) and frames.json (copied, plus an `rs_rectify` block).
"""
import argparse
import json
import os
import shutil
import sys

import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R, Slerp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import Capture  # noqa: E402
from gyro_check import check  # noqa: E402
from gyro_pairs import Orientation  # noqa: E402
from known_rot_pnp import load_model  # noqa: E402

F = np.diag([1.0, -1.0, -1.0])


class CamRot:
    """camera(OpenCV) -> world rotation at any time, interpolated between the 400 Hz gyro samples."""

    def __init__(self, orient, Rci):
        self.slerp = Slerp(orient.tt, orient.Q)
        self.t0, self.t1 = orient.tt[0], orient.tt[-1]
        self.Rci = Rci

    def __call__(self, t):
        q = self.slerp(np.clip(np.atleast_1d(t), self.t0, self.t1)).as_matrix()
        return np.einsum("ij,njk,kl->nil", F @ self.Rci, q, self.Rci.T @ F)


def distort(b, K, d):
    """unit-depth rays (..., 3) -> distorted pixels (..., 2), OpenCV model k1 k2 p1 p2."""
    x, y = b[..., 0] / b[..., 2], b[..., 1] / b[..., 2]
    k1, k2, p1, p2 = d
    r2 = x * x + y * y; rad = 1 + k1 * r2 + k2 * r2 * r2
    xd = x * rad + 2 * p1 * x * y + p2 * (r2 + 2 * x * x)
    yd = y * rad + p1 * (r2 + 2 * y * y) + 2 * p2 * x * y
    return np.stack([K[0, 0] * xd + K[0, 2], K[1, 1] * yd + K[1, 2]], -1)


def setup(dataset, meta, calib, bg_json=None):
    """gyro orientation aligned to the camera (gyro_check on the calib model) + the OPENCV camera."""
    frames = meta["frames"]
    imgs0, _, cam = load_model(os.path.join(calib, "sparse", "0"))
    assert cam[0] == "OPENCV", cam[0]
    fx, fy, cx, cy, k1, k2, p1, p2 = cam[1][:8]
    K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1.0]]); d = (k1, k2, p1, p2)
    rep = check(dataset, frames, {n: v[0] for n, v in imgs0.items()}, Capture(dataset).t0_ns,
                meta.get("pose_offset", 0.0), verbose=False)
    if bg_json:
        rep["bg"] = np.array(json.load(open(bg_json))["bg"])
    t_all = [f["pts"] + meta.get("pose_offset", 0.0) for f in frames]
    orient = Orientation(rep["imu"], rep["off"], min(t_all) - 1, max(t_all) + 1, bg=rep["bg"])
    return CamRot(orient, rep["Rci"]), K, d


def readout_s(dataset):
    Cm = np.genfromtxt(os.path.join(dataset, "camera.csv"), delimiter=",", skip_header=1)
    return float(np.median(Cm[Cm[:, 2] > 0, 2])) / 1e9


def rectify_points(uv, t_ref, camrot, K, d, axis, sign, skew, N):
    """raw (rolling-shutter, distorted) pixels uv (n, 2) seen in frames at times t_ref (n,) -> pixels of the
    global-shutter image at t_ref (what rs_rectify writes). Direct: the source row is known for a point."""
    uv = np.asarray(uv, np.float64); t_ref = np.asarray(t_ref, np.float64)
    c = uv[:, 1] if axis == "rows" else uv[:, 0]
    t_row = t_ref + sign * (c / (N - 1) - 0.5) * skew
    und = cv2.undistortPoints(uv.reshape(-1, 1, 2), K, np.asarray(d, float)).reshape(-1, 2)
    b = np.c_[und, np.ones(len(und))]
    M = np.einsum("nji,njk->nik", camrot(t_ref), camrot(t_row))                      # R(t_ref)^T R(t_row)
    return distort(np.einsum("nij,nj->ni", M, b), K, d)


class Rectifier:
    def __init__(self, W, H, K, d, camrot, skew, bins=128):
        self.W, self.H, self.K, self.d, self.cr, self.skew, self.bins = W, H, K, d, camrot, skew, bins
        uu, vv = np.meshgrid(np.arange(W, dtype=np.float64), np.arange(H, dtype=np.float64))
        self.pix = np.stack([uu, vv], -1)
        und = cv2.undistortPoints(self.pix.reshape(-1, 1, 2), K, np.asarray(d, float)).reshape(H, W, 2)
        self.ray = np.concatenate([und, np.ones((H, W, 1))], -1).astype(np.float32)

    def maps(self, t_ref, axis, sign):
        """remap tables (map_x, map_y) that turn the rolling-shutter image into a global-shutter one at t_ref."""
        if axis is None:
            return self.pix[..., 0].astype(np.float32), self.pix[..., 1].astype(np.float32)
        N = self.H if axis == "rows" else self.W
        tb = t_ref + sign * (np.linspace(0, 1, self.bins) - 0.5) * self.skew           # time of each row bin
        M = np.einsum("nji,jk->nik", self.cr(tb), self.cr(t_ref)[0]).astype(np.float32)  # R(t_row)^T R(t_ref)
        src = self.pix.astype(np.float32)
        for _ in range(3):
            c = src[..., 1] if axis == "rows" else src[..., 0]
            k = np.clip(np.round(c / (N - 1) * (self.bins - 1)), 0, self.bins - 1).astype(np.int32)
            b = np.einsum("hwij,hwj->hwi", M[k], self.ray)
            src = distort(b, self.K, self.d).astype(np.float32)
        return src[..., 0], src[..., 1]

    def apply(self, img, t_ref, axis, sign):
        mx, my = self.maps(t_ref, axis, sign)
        return cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def probe(rect, camrot, video, frames, K, d, n=24, cache=None):
    """photometric error of 'next video frame warped onto the keyframe by the gyro rotation', per candidate."""
    vi = np.array([f["video_index"] for f in frames]); pt = np.array([f["pts"] for f in frames])
    a, b0 = np.polyfit(vi, pt, 1)                                               # video index -> time
    rate = []
    for f in frames:
        Ra, Rb = camrot(f["pts"])[0], camrot(f["pts"] + a)[0]
        rate.append(np.degrees(np.linalg.norm(R.from_matrix(Ra.T @ Rb).as_rotvec())) / a)
    pick = [frames[i] for i in np.argsort(rate)[::-1][:n]]
    want = {f["video_index"] for f in pick} | {f["video_index"] + 1 for f in pick}
    got = {}
    if cache and os.path.exists(cache):
        z = np.load(cache); got = {int(k): z[k] for k in z.files if int(k) in want}
    if len(got) < len(want):
        cap = cv2.VideoCapture(video); i = 0; got = {}
        while len(got) < len(want):
            ok, im = cap.read()
            if not ok:
                break
            i += 1                                                                # video_index is 1-based (frame_00001)
            if i in want:
                got[i] = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        if cache:
            np.savez_compressed(cache, **{str(k): v for k, v in got.items()})
    got = {k: v.astype(np.float32) for k, v in got.items()}
    cands = [(None, 0)] + [(ax, s) for ax in ("rows", "cols") for s in (1, -1)]
    err = {c: [] for c in cands}; err_nowarp = []
    for f in pick:
        k = f["video_index"]
        if k not in got or k + 1 not in got:
            continue
        ta, tb = a * k + b0, a * (k + 1) + b0
        Ra, Rb = camrot(ta)[0], camrot(tb)[0]
        for c in cands:
            A = rect.apply(got[k], ta, *c)
            B = rect.apply(got[k + 1], tb, *c)
            # global-shutter warp of B onto A: ray in A -> ray in B = Rb^T Ra b
            bA = rect.ray; bB = np.einsum("ij,hwj->hwi", (Rb.T @ Ra).astype(np.float32), bA)
            m = distort(bB, K, d).astype(np.float32)
            Bw = cv2.remap(B, m[..., 0], m[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=-1)
            g = cv2.Laplacian(A, cv2.CV_32F, ksize=3)
            valid = (Bw >= 0) & (np.abs(g) > np.percentile(np.abs(g), 80))        # textured pixels only
            err[c].append(float(np.mean(np.abs(A[valid] - Bw[valid]))))
            if c[0] is None:                                                      # sanity: no gyro warp at all
                v2 = valid & (B >= 0)
                err_nowarp.append(float(np.mean(np.abs(A[v2] - B[v2]))))
    print(f"   {'no gyro warp':14s} photometric error {np.median(err_nowarp):.2f} (must be clearly worse than 'none')")
    for c in cands:
        print(f"   {('none' if c[0] is None else f'{c[0]} sign {c[1]:+d}'):14s} photometric error {np.median(err[c]):.3f} "
              f"(mean |diff| on textured pixels, median over {len(err[c])} frame pairs)", flush=True)
    best = min(cands, key=lambda c: np.median(err[c]))
    return best, {("none" if c[0] is None else f"{c[0]}{c[1]:+d}"): float(np.median(err[c])) for c in cands}, \
        float(np.median(np.array(rate)[np.argsort(rate)[::-1][:n]]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset"); ap.add_argument("work_in"); ap.add_argument("calib"); ap.add_argument("work_out")
    ap.add_argument("--bg_json", default=None, help="gyro bias from gyro_loop_bias.py")
    ap.add_argument("--axis", default="auto", choices=["auto", "rows", "cols"])
    ap.add_argument("--sign", default="auto", choices=["auto", "1", "-1"])
    ap.add_argument("--skew_ms", type=float, default=0.0, help="readout time; 0 = median of camera.csv")
    ap.add_argument("--probe_n", type=int, default=24)
    ap.add_argument("--probe_only", action="store_true")
    a = ap.parse_args()

    meta = json.load(open(os.path.join(a.work_in, "frames.json")))
    frames = meta["frames"]
    camrot, K, d = setup(a.dataset, meta, a.calib, a.bg_json)
    skew = a.skew_ms / 1000 if a.skew_ms > 0 else readout_s(a.dataset)
    im0 = cv2.imread(os.path.join(a.work_in, "images", frames[0]["name"] + ".jpg"))
    H, W = im0.shape[:2]
    rect = Rectifier(W, H, K, d, camrot, skew)
    print(f"{len(frames)} keyframes {W}x{H}, readout {skew * 1000:.1f} ms", flush=True)

    axis = None if a.axis == "auto" else a.axis
    sign = None if a.sign == "auto" else int(a.sign)
    scores, probe_rate = {}, None
    if axis is None or sign is None or a.probe_only:
        print(f"probe: next video frame warped onto the keyframe by the gyro, {a.probe_n} fastest-rotating keyframes")
        os.makedirs(a.work_out, exist_ok=True)
        best, scores, probe_rate = probe(rect, camrot, os.path.join(a.dataset, "dataset.mp4"), frames, K, d,
                                         a.probe_n, cache=os.path.join(a.work_out, "probe_frames.npz"))
        print(f"   rotation speed of the probed frames: median {probe_rate:.0f} deg/s")
        if best[0] is None:
            print("probe: no candidate beats 'none'; the readout model does not fit (check the gyro time offset)")
        axis = axis or best[0]
        sign = sign if sign is not None else best[1]
    if a.probe_only:
        return
    if axis is None:
        sys.exit("no readout direction: give --axis and --sign, or check the probe")

    os.makedirs(os.path.join(a.work_out, "images"), exist_ok=True)
    shift = []
    for k, f in enumerate(frames):
        t = f["pts"] + meta.get("pose_offset", 0.0)
        img = cv2.imread(os.path.join(a.work_in, "images", f["name"] + ".jpg"))
        mx, my = rect.maps(t, axis, sign)
        shift.append(float(np.percentile(np.hypot(mx - rect.pix[..., 0], my - rect.pix[..., 1]), 95)))
        out = cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        cv2.imwrite(os.path.join(a.work_out, "images", f["name"] + ".jpg"), out, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if k % 100 == 0:
            print(f"   {k}/{len(frames)}", flush=True)
    meta["rs_rectify"] = dict(axis=axis, sign=sign, skew_s=skew, calib=os.path.abspath(a.calib), bg_json=a.bg_json,
                              probe=scores, probe_rate_deg_s=probe_rate,
                              shift_px_p95_median=float(np.median(shift)), shift_px_p95_max=float(np.max(shift)))
    json.dump(meta, open(os.path.join(a.work_out, "frames.json"), "w"), indent=1)
    for extra in ("blur_motion.json",):
        if os.path.exists(os.path.join(a.work_in, extra)):
            shutil.copy(os.path.join(a.work_in, extra), a.work_out)
    print(f"wrote {len(frames)} rectified keyframes to {a.work_out}; per-frame shift (p95 of the pixels): median "
          f"{np.median(shift):.1f} px, max {np.max(shift):.1f} px ({axis}, sign {sign:+d})")


if __name__ == "__main__":
    main()
