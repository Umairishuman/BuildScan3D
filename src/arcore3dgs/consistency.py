"""Find frames whose depth/pose contradict other views (ghost geometry sources).

For frame i, its depth points are projected into other cameras j that look at the same area.
If a point lands clearly IN FRONT of the surface camera j observed (j saw through that space),
it violates free space. Frames with a high violation ratio carry a wrong pose or wrong depth and
create floating duplicates when fused.
"""
import os, json, argparse, numpy as np, torch

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--depth_dir", default="depth_mvs")
ap.add_argument("--margin", type=float, default=0.10, help="m in front of observed surface = violation")
ap.add_argument("--k", type=int, default=20, help="number of other views checked per frame")
args = ap.parse_args()
dev = "cuda"
meta = json.load(open(os.path.join(args.work, "frames.json"))); fr = meta["frames"]; N = len(fr)
s = meta["depth_scale"]; W, H = int(meta["W"] * s), int(meta["H"] * s)
K = torch.tensor([[meta["fx"] * s, 0, meta["cx"] * s], [0, meta["fy"] * s, meta["cy"] * s], [0, 0, 1]], device=dev)
G = torch.diag(torch.tensor([1.0, -1, -1], device=dev))
Rw = torch.stack([torch.tensor(f["c2w"], dtype=torch.float32, device=dev)[:3, :3] @ G for f in fr])
Cw = torch.stack([torch.tensor(f["c2w"], dtype=torch.float32, device=dev)[:3, 3] for f in fr])
D = torch.stack([torch.from_numpy(np.load(os.path.join(args.work, args.depth_dir, f["name"] + ".npy")).astype(np.float32)) for f in fr]).to(dev)
st = 4
vv, uu = torch.meshgrid(torch.arange(0, H, st, device=dev), torch.arange(0, W, st, device=dev), indexing="ij")
rays = torch.linalg.inv(K) @ torch.stack([uu.flatten() + .5, vv.flatten() + .5, torch.ones(uu.numel(), device=dev)])
# candidate views: cameras whose look-at points (centre + 1.5 m forward) are close
look = Cw + 1.5 * Rw[:, :, 2]
viol = np.zeros(N); checked = np.zeros(N)
for i in range(N):
    d = D[i, vv, uu].flatten()
    ok = (d > 0.2) & (d < 5)
    X = Cw[i][:, None] + Rw[i] @ (rays[:, ok] * d[ok])
    dist = (look - look[i]).norm(dim=1); dist[i] = 1e9
    nb = torch.argsort(dist)[:args.k]
    vcount = torch.zeros(X.shape[1], device=dev); ccount = torch.zeros(X.shape[1], device=dev)
    for j in nb.tolist():
        pc = Rw[j].T @ (X - Cw[j][:, None]); z = pc[2]
        u = (K[0, 0] * pc[0] / z + K[0, 2]).long(); v = (K[1, 1] * pc[1] / z + K[1, 2]).long()
        inb = (z > 0.2) & (u >= 0) & (u < W) & (v >= 0) & (v < H)
        dj = torch.zeros_like(z); dj[inb] = D[j, v[inb], u[inb]]
        valid = inb & (dj > 0.2)
        ccount += valid.float()
        vcount += (valid & (z < dj - args.margin - 0.03 * dj)).float()      # point in front of j's surface
    viol[i] = float(vcount.sum() / ccount.sum().clamp_min(1))
    checked[i] = float(ccount.sum())
np.save(os.path.join(args.work, "frame_violation.npy"), viol)
order = np.argsort(-viol)
print(f"free-space violation ratio: median {np.median(viol) * 100:.1f}%, p90 {np.percentile(viol, 90) * 100:.1f}%, max {viol.max() * 100:.1f}%")
print("worst frames (index, name, violation%, has MVS sources?):")
mask_dir = os.path.join(args.work, "mvs_mask")
for i in order[:25]:
    mfrac = np.load(os.path.join(mask_dir, fr[i]["name"] + ".npy")).mean()
    print(f"  {i:4d} {fr[i]['name']}  {viol[i] * 100:5.1f}%   mvs-measured {mfrac * 100:4.1f}%")
