"""Place unplaced keyframes that ARCore tracked, inside the holes of a camera path (2026-11-25).

scan_009: 33 of 39 keyframes at 125 - 133 s (the view from the room into the bathroom) were left out by the camera
chain although ARCore tracked all of them and they have texture (TRAINING R-121 correction). The bathroom is seen
nowhere else, so no image pairs tie those frames to the rest. ARCore's own poses can: locally, around each hole,
ARCore's path and the model's path differ by a similarity transform (scale, rotation, shift), which is fitted on the
frames that are placed AND tracked within --win s on both sides of the hole.

ARCore relocalises (scan_009: a 3.48 m jump in 0.11 s at 127.5 s, inside the doorway hole), so ARCore's track is
split into segments at jumps (> --max_speed m/s) and tracking gaps (> --seg_gap s); a transform is only valid within
one segment. Per hole (a gap of >= --hole_dt s between placed keyframes, the rule of analyze_recording.py):
per ARCore segment of its unplaced tracked frames, the anchors are the placed tracked frames of THE SAME segment
within --win s before / after the hole. With anchors on both sides: full fit plus the cross-side check below; with
anchors on one side only: rotation from their orientations, scale from the larger side of the hole (relocalisation
shifts ARCore's world, it does not rescale it), shift from their centres; the image-match check is then the test.
The original steps, per segment:
  1. fit frames: placed, ARCore-tracked keyframes in [start - win, start] and [end, end + win]; >= --min_side on
     each side;
  2. Sim3 from ARCore to the model: rotation from the camera orientations, scale and shift from the centres; checks: centre residual, rotation residual
     (model rotation vs the mapped ARCore rotation), and a cross-side check: fitted on one side only, how far off it
     predicts the other side (what the transform must do across the hole);
  3. if the checks pass (--max_rot deg, --max_cross units), every unplaced tracked keyframe inside the hole gets the
     mapped ARCore pose;
  4. (--database) the new poses against the image matches: for every verified pair with at least one new frame and
     both frames posed, the Sampson error of its inlier matches under the relative pose; a new frame whose median
     error over its pairs is > --max_sampson px is dropped again.
The model is written with the new images (no 2D-3D observations: training and --pose_opt refine them). Writes
<model_out>/arcore_fill.json (per hole: fit, checks, frames added / dropped).

  python src/arcore3dgs/arcore_fill.py <model_in> <selection dir with frames.json> <model_out> [--database <db>]
"""
import argparse
import json
import os
import shutil
import sqlite3
import sys

import numpy as np
from scipy.spatial.transform import Rotation as Rot

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scale_drift import read_model  # noqa: E402

G = np.diag([1.0, -1.0, -1.0])
PAIR = 2147483647


def tracked(f):
    return isinstance(f.get("c2w_arcore"), list) and f.get("arcore_pose") not in ("lost", "unsettled")


def sim3_rot_first(Rm, Ra, A, B):
    """world rotation from the camera orientations (chordal mean of Rm_i Ra_i^T: well determined even when the
    camera centres are close together), then scale and shift from the centres with that rotation fixed"""
    U, _, Vt = np.linalg.svd(sum(rm @ ra.T for rm, ra in zip(Rm, Ra)))
    R = U @ np.diag([1, 1, np.sign(np.linalg.det(U @ Vt))]) @ Vt
    RA = A @ R.T; ma, mb = RA.mean(0), B.mean(0)
    s = float(np.sum((RA - ma) * (B - mb)) / max(np.sum((RA - ma) ** 2), 1e-12))
    return s, R, mb - s * ma


def umeyama(A, B):
    """s, R, t with B ~ s R A + t"""
    ma, mb = A.mean(0), B.mean(0); a, b = A - ma, B - mb
    U, S, Vt = np.linalg.svd(b.T @ a / len(A))
    D = np.diag([1, 1, np.sign(np.linalg.det(U @ Vt))])
    R = U @ D @ Vt; s = np.trace(np.diag(S) @ D) / (a ** 2).sum(1).mean()
    return s, R, mb - s * R @ ma


def ang(Ra, Rb):
    return np.degrees(np.arccos(np.clip((np.trace(Ra @ Rb.T) - 1) / 2, -1, 1)))


def sampson_check(database, K, dist, fx, pose, newset, min_rows=15):
    """per new frame: list of median Sampson errors (px) of its verified pairs whose both frames are posed.
    pose: name -> (Rcw, C) for every posed frame (placed and new)"""
    import cv2
    con = sqlite3.connect(database)
    name_of = {i: n.rsplit(".", 1)[0] for i, n in con.execute("select image_id, name from images")}
    kps, errs = {}, {n: [] for n in newset}
    for pid, r, d_ in con.execute("select pair_id, rows, data from two_view_geometries where rows >= ?", (min_rows,)):
        i2 = pid % PAIR; i1 = (pid - i2) // PAIR
        na, nb = name_of.get(i1), name_of.get(i2)
        if na not in pose or nb not in pose or not ({na, nb} & newset):
            continue
        for i in (i1, i2):
            if i not in kps:
                row = con.execute("select rows, cols, data from keypoints where image_id=?", (i,)).fetchone()
                kps[i] = np.frombuffer(row[2], np.float32).reshape(row[0], row[1])[:, :2] if row and row[2] else None
        if kps[i1] is None or kps[i2] is None:
            continue
        m = np.frombuffer(d_, np.uint32).reshape(r, 2)
        x1 = cv2.undistortPoints(kps[i1][m[:, 0]].reshape(-1, 1, 2), K, dist).reshape(-1, 2)
        x2 = cv2.undistortPoints(kps[i2][m[:, 1]].reshape(-1, 1, 2), K, dist).reshape(-1, 2)
        (R1, C1), (R2, C2) = pose[na], pose[nb]
        Rr = R2 @ R1.T; tr = R2 @ (C1 - C2)
        if np.linalg.norm(tr) < 1e-6:
            continue
        tx = np.array([[0, -tr[2], tr[1]], [tr[2], 0, -tr[0]], [-tr[1], tr[0], 0]]); E = tx @ Rr
        h1 = np.c_[x1, np.ones(len(x1))]; h2 = np.c_[x2, np.ones(len(x2))]
        Ex1 = h1 @ E.T; Etx2 = h2 @ E
        samp = np.sqrt(np.sum(h2 * Ex1, 1) ** 2 / np.maximum(Ex1[:, 0] ** 2 + Ex1[:, 1] ** 2 + Etx2[:, 0] ** 2 + Etx2[:, 1] ** 2, 1e-12)) * fx
        for n in (na, nb):
            if n in newset:
                errs[n].append(float(np.median(samp)))
    con.close()
    return errs


def write_with_new(model_in, model_out, new):
    """copy a COLMAP text model and add images (and COLMAP 4 frames) for new = [dict(key, Rcw, C)], no observations"""
    os.makedirs(model_out, exist_ok=True)
    for fn in ("cameras.txt", "rigs.txt", "points3D.txt"):
        if os.path.exists(os.path.join(model_in, fn)):
            shutil.copy(os.path.join(model_in, fn), os.path.join(model_out, fn))
    body = [l for l in open(os.path.join(model_in, "images.txt")).read().splitlines() if not l.startswith("#")]
    ids = [int(body[i].split()[0]) for i in range(0, len(body), 2)]
    ext = os.path.splitext(body[0].split()[9])[1]
    nid = max(ids) + 1
    NL = chr(10)
    with open(os.path.join(model_out, "images.txt"), "w") as f:
        f.write(f"# Number of images: {len(ids) + len(new)}" + NL + NL.join(body) + NL)
        for j, n in enumerate(new):
            q = Rot.from_matrix(n["Rcw"]).as_quat(); tt = -n["Rcw"] @ n["C"]
            f.write(f"{nid + j} {q[3]} {q[0]} {q[1]} {q[2]} {tt[0]} {tt[1]} {tt[2]} 1 {n['key']}{ext}" + NL + NL)
    fr_path = os.path.join(model_in, "frames.txt")
    if os.path.exists(fr_path):
        L = [l for l in open(fr_path).read().splitlines() if not l.startswith("#")]
        fid = max(int(l.split()[0]) for l in L) + 1
        with open(os.path.join(model_out, "frames.txt"), "w") as f:
            f.write(f"# Number of frames: {len(L) + len(new)}" + NL + NL.join(L) + NL)
            for j, n in enumerate(new):
                q = Rot.from_matrix(n["Rcw"]).as_quat(); tt = -n["Rcw"] @ n["C"]
                f.write(f"{fid + j} 1 {q[3]} {q[0]} {q[1]} {q[2]} {tt[0]} {tt[1]} {tt[2]} 1 CAMERA 1 {nid + j}" + NL)
    return len(ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model_in"); ap.add_argument("selection"); ap.add_argument("model_out")
    ap.add_argument("--database", default=None)
    ap.add_argument("--hole_dt", type=float, default=2.5); ap.add_argument("--win", type=float, default=10.0)
    ap.add_argument("--min_side", type=int, default=3)
    ap.add_argument("--max_rot", type=float, default=5.0, help="deg, median rotation residual of the fit")
    ap.add_argument("--max_cross", type=float, default=0.3, help="model units, cross-side prediction error (median)")
    ap.add_argument("--max_sampson", type=float, default=4.0, help="px")
    ap.add_argument("--max_res", type=float, default=0.15, help="model units, centre residual of the anchors (median)")
    ap.add_argument("--max_speed", type=float, default=3.0, help="m/s between keyframes: faster = ARCore jumped")
    ap.add_argument("--seg_gap", type=float, default=1.0, help="s without tracking that starts a new ARCore segment")
    a = ap.parse_args()

    sel = json.load(open(os.path.join(a.selection, "frames.json")))["frames"]
    pts_of = {f["name"]: f["pts"] for f in sel}; t0 = min(pts_of.values()); by = {f["name"]: f for f in sel}
    K, dist, fx, fy, imgs = read_model(a.model_in, pts_of)
    pl = {d["key"]: d for d in imgs}
    T = np.array([pts_of[d["key"]] - t0 for d in imgs])
    arc_C = lambda f: np.array(f["c2w_arcore"])[:3, 3]
    arc_Rwc = lambda f: np.array(f["c2w_arcore"])[:3, :3] @ G               # OpenCV camera -> ARCore world

    # ARCore segments: a new segment starts where ARCore jumps (relocalisation: > --max_speed m/s between keyframes)
    # or where tracking stops for > --seg_gap s; inside a segment ARCore's world is one frame
    trk = sorted([f for f in sel if tracked(f)], key=lambda f: f["pts"]); seg_of, sg = {}, 0
    for i, f in enumerate(trk):
        if i:
            dtt = f["pts"] - trk[i - 1]["pts"]; d = np.linalg.norm(arc_C(f) - arc_C(trk[i - 1]))
            if dtt > a.seg_gap or d / max(dtt, 1e-3) > a.max_speed:
                sg += 1
                if dtt <= a.seg_gap:
                    print(f"ARCore jump at {trk[i - 1]['pts'] - t0:.2f} -> {f['pts'] - t0:.2f} s: {d:.2f} m in {dtt:.2f} s", flush=True)
        seg_of[f["name"]] = sg

    def fit_report(anchors):
        A = np.array([arc_C(by[d["key"]]) for d in anchors]); B = np.array([d["C"] for d in anchors])
        s, R, t_ = sim3_rot_first([d["Rcw"].T for d in anchors], [arc_Rwc(by[d["key"]]) for d in anchors], A, B)
        return s, R, t_, A, B

    report, new = [], []
    for k in np.flatnonzero(np.diff(T) >= a.hole_dt):
        s0, s1 = T[k], T[k + 1]
        cand = [f for f in sel if s0 < f["pts"] - t0 < s1 and f["name"] not in pl and tracked(f)]
        rep = dict(hole=[float(s0), float(s1)], unplaced_tracked=len(cand), segments=[])
        if not cand:
            rep["result"] = "nothing to add (no unplaced tracked frames)"; report.append(rep); continue
        left_all = [d for d in imgs if s0 - a.win <= pts_of[d["key"]] - t0 <= s0 and tracked(by[d["key"]])]
        right_all = [d for d in imgs if s1 <= pts_of[d["key"]] - t0 <= s1 + a.win and tracked(by[d["key"]])]
        # scale reference: the larger side with >= 2 * min_side frames (a relocalisation shifts ARCore's world, it
        # does not rescale it)
        ref = max([x for x in (left_all, right_all) if len(x) >= 2 * a.min_side], key=len, default=None)
        s_ref = fit_report(ref)[0] if ref else None
        for g in sorted({seg_of[f["name"]] for f in cand}):
            grp = [f for f in cand if seg_of[f["name"]] == g]
            L = [d for d in left_all if seg_of.get(d["key"]) == g]; Rr = [d for d in right_all if seg_of.get(d["key"]) == g]
            anchors = L + Rr
            gr = dict(segment=int(g), frames=len(grp), t=[float(grp[0]["pts"] - t0), float(grp[-1]["pts"] - t0)],
                      anchors_left=len(L), anchors_right=len(Rr))
            if len(anchors) < a.min_side:
                gr["result"] = "skipped: too few placed tracked frames in the same ARCore segment"
                rep["segments"].append(gr)
                print(f"hole {s0:.1f} -> {s1:.1f} s, ARCore segment {g} ({gr['t'][0]:.1f} - {gr['t'][1]:.1f} s, {len(grp)} frames): "
                      f"{gr['result']} ({len(L)} + {len(Rr)})", flush=True)
                continue
            s, R, t_, A, B = fit_report(anchors)
            mode = "both sides"
            if not (len(L) >= a.min_side and len(Rr) >= a.min_side):
                if s_ref is None:
                    gr["result"] = "skipped: one-sided and no scale reference"; rep["segments"].append(gr); continue
                s = s_ref; t_ = (B - s * (A @ R.T)).mean(0); mode = "one side, scale from the larger side"
            res_c = np.linalg.norm(s * (A @ R.T) + t_ - B, axis=1)
            res_r = np.array([ang(d["Rcw"].T, R @ arc_Rwc(by[d["key"]])) for d in anchors])
            gr.update(mode=mode, scale=float(s), centre_residual_median=float(np.median(res_c)),
                      rot_residual_median=float(np.median(res_r)))
            ok = gr["rot_residual_median"] <= a.max_rot and gr["centre_residual_median"] <= a.max_res
            if mode == "both sides":
                cross = []
                for fa, fb in ((L, Rr), (Rr, L)):
                    sa, Ra_, ta, Aa, Ba = fit_report(fa)
                    Ab = np.array([arc_C(by[d["key"]]) for d in fb]); Bb = np.array([d["C"] for d in fb])
                    cross += list(np.linalg.norm(sa * (Ab @ Ra_.T) + ta - Bb, axis=1))
                gr["cross_side_median"] = float(np.median(cross)); ok = ok and gr["cross_side_median"] <= a.max_cross
            print(f"hole {s0:.1f} -> {s1:.1f} s, ARCore segment {g} ({gr['t'][0]:.1f} - {gr['t'][1]:.1f} s, {len(grp)} frames): "
                  f"anchored on {len(L)} + {len(Rr)} frames ({mode}), scale {s:.3f}, centre residual "
                  f"{gr['centre_residual_median']:.3f} units, rotation {gr['rot_residual_median']:.2f} deg"
                  + (f", cross-side {gr['cross_side_median']:.3f}" if 'cross_side_median' in gr else "")
                  + f" -> {'ADD' if ok else 'rejected'}", flush=True)
            gr["result"] = "added" if ok else "rejected by the fit checks"
            if ok:
                for f in grp:
                    Rwc = R @ arc_Rwc(f); C = s * R @ arc_C(f) + t_
                    new.append(dict(key=f["name"], Rcw=Rwc.T, C=C, hole=len(report)))
                gr["added"] = [f["name"] for f in grp]
            rep["segments"].append(gr)
        report.append(rep)

    # image-match check of the new poses
    if new and a.database:
        pose = {d["key"]: (d["Rcw"], d["C"]) for d in imgs}; pose.update({n["key"]: (n["Rcw"], n["C"]) for n in new})
        errs = sampson_check(a.database, K, dist, fx, pose, {n["key"] for n in new})
        keep = []
        for n in new:
            e = errs[n["key"]]
            n["sampson_median"] = float(np.median(e)) if e else None; n["pairs"] = len(e)
            if e and np.median(e) > a.max_sampson:
                report[n["hole"]].setdefault("dropped_by_matches", []).append(n["key"])
            else:
                keep.append(n)
        print(f"image-match check: {len(new)} new frames, {sum(1 for n in new if n['pairs'])} with verified pairs; "
              f"Sampson error medians {[round(n['sampson_median'], 1) for n in new if n['pairs']]}; "
              f"{len(new) - len(keep)} dropped (> {a.max_sampson:g} px)", flush=True)
        new = keep
    n_in = write_with_new(a.model_in, a.model_out, new)
    json.dump(dict(params=vars(a), holes=report, added=[dict(name=n["key"], C=n["C"].tolist(),
                                                              sampson_median=n.get("sampson_median"), pairs=n.get("pairs"))
                                                         for n in new]),
              open(os.path.join(a.model_out, "arcore_fill.json"), "w"), indent=1)
    print(f"wrote {a.model_out}: {n_in} + {len(new)} images", flush=True)


if __name__ == "__main__":
    main()
