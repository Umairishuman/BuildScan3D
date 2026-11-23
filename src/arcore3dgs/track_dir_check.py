"""Do the video-track pair directions agree with a model's path? Angle between the track direction (rotation fixed
from the model) and the model's own C_a -> C_b direction, binned by the pair's 3D support and by time stretch.
  python src/arcore3dgs/track_dir_check.py <work(frames.json)> <model> <vt_pairs.npz>

Used for R-077 - R-079 (moved here from a scratchpad 2026-11-21).
"""
import sys, json, numpy as np
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from known_rot_pnp import load_model
from rot_sfm import pair_direction

pts = {f["name"]: f["pts"] for f in json.load(open(sys.argv[1] + "/frames.json"))["frames"]}
M, _, _ = load_model(sys.argv[2])
sup = {n: int((v[2] >= 0).sum()) for n, v in M.items()}
z = np.load(sys.argv[3]); rng = np.random.default_rng(0)
rows = []
for na, nb, o0, o1 in zip(z["a"], z["b"], z["off"][:-1], z["off"][1:]):
    na, nb = str(na), str(nb)
    if na not in M or nb not in M or o1 - o0 < 15:
        continue
    Ra, Ca = M[na][0], M[na][1]; Rb, Cb = M[nb][0], M[nb][1]       # camera -> world
    Rba = Rb.T @ Ra
    t, inl, par = pair_direction(Rba, z["b1"][o0:o1], z["b2"][o0:o1], 0.004, rng=rng)
    if t is None or inl.sum() < 15 or par < 1.0:
        continue
    d = Rb.T @ (Ca - Cb); nd = np.linalg.norm(d)                   # X_b = R_ba X_a + R_b^T(C_a - C_b) ... in cam b
    if nd < 1e-9:
        continue
    ang = np.degrees(np.arccos(np.clip(t @ (d / nd), -1, 1)))
    rows.append((pts[na], pts[nb], min(sup[na], sup[nb]), int(inl.sum()), par, ang))
r = np.array(rows)
print(f"{len(r)} pairs with >=15 inliers and >=1 deg parallax")
def show(m, lab):
    if m.sum() == 0:
        print(f"  {lab:28s} none"); return
    a = r[m, 5]
    print(f"  {lab:28s} {m.sum():5d} pairs | angle median {np.median(a):5.1f} deg, p75 {np.percentile(a, 75):5.1f}, "
          f"<10 deg {100 * (a < 10).mean():4.0f}%, >90 deg (sign flip) {100 * (a > 90).mean():3.0f}% | parallax med "
          f"{np.median(r[m, 4]):.1f}")
for lo, hi in ((0, 10), (10, 50), (50, 150), (150, 1e9)):
    show((r[:, 2] >= lo) & (r[:, 2] < hi), f"support {lo}-{hi:g}")
for lo, hi, lab in ((45, 60, "45-60 s"), (90, 105, "90-105 s"), (120, 140, "120-140 s")):
    show((r[:, 0] >= lo) & (r[:, 1] < hi), lab)
for plo, phi in ((1, 2), (2, 4), (4, 90)):
    show((r[:, 4] >= plo) & (r[:, 4] < phi) & (r[:, 2] >= 150), f"support>=150, parallax {plo}-{phi}")
