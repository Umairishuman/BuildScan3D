"""Structural layer next to a 3DGS model: exact room-shell planes, median-textured walls/floor, openings.

The photoreal splat model is NOT modified (post-hoc snapping killed the glossy-floor reflections and crushed
door frames). Instead the room shell is rebuilt as clean geometry:
  1. planes:   floor (horizontal peak of splat heights, refined by a robust plane fit) and the outermost wall
               on each side of the two wall directions (Manhattan angle from splat positions), each wall then
               refined individually (its own angle), corners = intersections of neighbouring walls.
  2. textures: each wall / the floor is a flat image at --texel m. Every texel is projected into the frames;
               a sample counts only if the splat model's rendered depth agrees with the plane there (not
               occluded by furniture). The texel colour is the per-texel MEDIAN over its best --k views
               (frontal + close first): reflections and glare move between views, the real texture doesn't.
               Texels where the cameras consistently see THROUGH the plane are openings (doors/windows).
  3. clean mode render: textured shell + only the splats that are not part of the shell, depth-composited.

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/structure.py --ply <v3 splat.ply> --work <work_sfm> --out <dir>
Outputs: structure.json (planes, corners, dimensions, openings), tex_*.png (RGBA), comparison sheets.
"""
import os, json, argparse, time
import numpy as np, cv2, torch, torch.nn.functional as F
from plyfile import PlyData
from scipy import ndimage
from gsplat import rasterization

ap = argparse.ArgumentParser()
ap.add_argument("--ply", required=True); ap.add_argument("--work", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--texel", type=float, default=0.005)
ap.add_argument("--k", type=int, default=12, help="views kept per texel for the median")
ap.add_argument("--every", type=int, default=1, help="use every n-th frame for texturing")
ap.add_argument("--shell_band", type=float, default=0.06, help="m: splats this close to a shell plane are hidden in clean mode")
args = ap.parse_args()
assert os.path.abspath(args.out) != os.path.abspath(os.path.dirname(args.ply))
os.makedirs(args.out, exist_ok=True)
dev = "cuda"; UP = np.array([0.0, 1.0, 0.0]); G = np.diag([1, -1, -1, 1.0])

# ---------------- splats ----------------
v = PlyData.read(args.ply)["vertex"]; D = v.data
P = np.stack([D["x"], D["y"], D["z"]], 1).astype(np.float64); OP = 1 / (1 + np.exp(-D["opacity"].astype(np.float64)))
c_ = lambda n: torch.tensor(np.asarray(D[n]), dtype=torch.float32, device=dev)
nr = len([n for n in D.dtype.names if n.startswith("f_rest")])
GS = dict(means=torch.stack([c_("x"), c_("y"), c_("z")], 1),
          quats=F.normalize(torch.stack([c_(f"rot_{i}") for i in range(4)], 1), dim=-1),
          scales=torch.exp(torch.stack([c_(f"scale_{i}") for i in range(3)], 1)), opac=torch.sigmoid(c_("opacity")),
          col=torch.cat([torch.stack([c_(f"f_dc_{i}") for i in range(3)], 1)[:, None],
                         torch.stack([c_(f"f_rest_{i}") for i in range(nr)], 1).reshape(len(P), 3, -1).transpose(1, 2)], 1))
SH = int(round(np.sqrt(GS["col"].shape[1]))) - 1
meta = json.load(open(os.path.join(args.work, "frames.json"))); fr = meta["frames"]
W, H = meta["W"], meta["H"]
C_cam = np.array([np.array(f["c2w"])[:3, 3] for f in fr]); room_c = C_cam.mean(0)


def peaks(x, lo, hi, bin_=0.01, min_rel=0.15, sep=0.15):
    h, e = np.histogram(x, bins=max(10, int((hi - lo) / bin_)), range=(lo, hi))
    h = ndimage.gaussian_filter1d(h.astype(float), 1.0); c = 0.5 * (e[1:] + e[:-1])
    pr = h - ndimage.median_filter(h, size=41); out = []
    for i in np.argsort(-pr):
        if pr[i] < min_rel * pr.max():
            break
        if all(abs(c[i] - c[j]) > sep for j in out):
            out.append(i)
    return [float(c[i]) for i in out]


def fit_plane(pts, w, vertical):
    """weighted least-squares plane through pts; vertical=True keeps the normal horizontal."""
    m = (pts * w[:, None]).sum(0) / w.sum(); X = (pts - m) * np.sqrt(w)[:, None]
    if vertical:
        X2 = X[:, [0, 2]]; _, _, Vt = np.linalg.svd(X2, full_matrices=False); n = np.array([Vt[-1, 0], 0.0, Vt[-1, 1]])
    else:
        _, _, Vt = np.linalg.svd(X, full_matrices=False); n = Vt[-1]
    n /= np.linalg.norm(n)
    return n, float(n @ m)


# ---------------- 1. planes ----------------
op = OP > 0.5; Y = P[:, 1]
hpk = sorted(peaks(Y[op], *np.percentile(Y[op], [0.5, 99.5])))
floor_y = hpk[0]
sel = op & (np.abs(Y - floor_y) < 0.03)
n_f, d_f = fit_plane(P[sel], OP[sel], False)
if n_f[1] < 0:
    n_f, d_f = -n_f, -d_f
for band in (0.03, 0.02):                                            # robust refinement
    dist = P @ n_f - d_f; sel = op & (np.abs(dist) < band); n_f, d_f = fit_plane(P[sel], OP[sel], False)
    if n_f[1] < 0:
        n_f, d_f = -n_f, -d_f
ceil_y = next((y for y in reversed(hpk) if y > floor_y + 2.0), None)
mid = op & (Y > floor_y + 0.3) & (Y < floor_y + 2.6); XZ = P[mid][:, [0, 2]]


def sharp(a):
    return sum((np.histogram(XZ @ np.array([np.cos(b), np.sin(b)]), bins=1000)[0].astype(float) ** 2).sum() for b in (a, a + np.pi / 2))


th = np.radians(np.arange(0, 90, 0.25))[int(np.argmax([sharp(a) for a in np.radians(np.arange(0, 90, 0.25))]))]
fine = th + np.radians(np.arange(-0.5, 0.5, 0.02)); th = fine[int(np.argmax([sharp(a) for a in fine]))]
walls = []
for k in range(2):
    a = th + k * np.pi / 2; dv = np.array([np.cos(a), 0.0, np.sin(a)]); off = XZ @ dv[[0, 2]]
    pk = peaks(off, *np.percentile(off, [0.5, 99.5]))
    for d0 in ({min(pk), max(pk)} if len(pk) >= 2 else set(pk)):
        n, d = dv.copy(), d0
        wsel = mid.copy()
        for band in (0.06, 0.04, 0.025):                             # each wall gets its own angle
            dist = P @ n - d; s = wsel & (np.abs(dist) < band)
            n2, d2 = fit_plane(P[s], OP[s], True)
            if n2 @ n < 0:
                n2, d2 = -n2, -d2
            if np.degrees(np.arccos(np.clip(n2 @ dv, -1, 1))) < 5:
                n, d = n2, d2
        if room_c @ n - d < 0:                                       # normal points into the room
            n, d = -n, -d
        walls.append(dict(n=n, d=d, dev_deg=float(np.degrees(np.arccos(np.clip(abs(n @ dv), -1, 1))))))
# order walls around the room and intersect neighbours -> corners (floor polygon)
foot = lambda w_: room_c - (room_c @ w_["n"] - w_["d"]) * w_["n"]
walls.sort(key=lambda w_: np.arctan2(*(foot(w_) - room_c)[[2, 0]]))
corners = []
for i in range(len(walls)):
    a, b = walls[i], walls[(i + 1) % len(walls)]
    A = np.array([[a["n"][0], a["n"][2]], [b["n"][0], b["n"][2]]])
    x, z = np.linalg.solve(A, [a["d"], b["d"]]); corners.append(np.array([x, 0.0, z]))
height = (ceil_y - floor_y) if ceil_y is not None else float(np.percentile(Y[mid], 99.5) - floor_y)
floor_at = lambda x, z: (d_f - n_f[0] * x - n_f[2] * z) / n_f[1]
for c in corners:
    c[1] = floor_at(c[0], c[2])
surfaces = []
for i, w_ in enumerate(walls):                                       # wall i spans corner[i-1] -> corner[i]
    A_, B_ = corners[i - 1], corners[i]
    surfaces.append(dict(kind="wall", name=f"wall{i}", n=w_["n"], d=w_["d"], origin=A_, u=(B_ - A_) / np.linalg.norm(B_ - A_),
                         v=UP.copy(), size=(float(np.linalg.norm(B_ - A_)), float(height))))
poly = np.array([[c[0], c[2]] for c in corners])
fx0, fz0 = poly.min(0); fx1, fz1 = poly.max(0)
o_f = np.array([fx0, floor_at(fx0, fz0), fz0])
u_f = np.array([1.0, 0, 0]) - (np.array([1.0, 0, 0]) @ n_f) * n_f; u_f /= np.linalg.norm(u_f); v_f = np.cross(n_f, u_f)
if v_f[2] < 0:
    v_f = -v_f
surfaces.append(dict(kind="floor", name="floor", n=n_f, d=d_f, origin=o_f, u=u_f, v=v_f, size=(float(fx1 - fx0), float(fz1 - fz0))))
dims = [float(abs(walls[i]["d"] + walls[j]["d"])) if walls[i]["n"] @ walls[j]["n"] < -0.99 else None
        for i in range(len(walls)) for j in range(i + 1, len(walls))]
devs = ", ".join("%.2f" % w_["dev_deg"] for w_ in walls)
print(f"floor tilt {np.degrees(np.arccos(n_f[1])):.2f} deg, height {height:.3f} m; {len(walls)} walls, "
      f"deviation from the Manhattan angle: {devs} deg")
print("wall lengths (corner to corner): " + ", ".join(f"{s['size'][0]:.3f}" for s in surfaces if s["kind"] == "wall") + " m")
opp = [abs((room_c @ walls[i]["n"] - walls[i]["d"]) + (room_c @ walls[j]["n"] - walls[j]["d"]))
       for i in range(len(walls)) for j in range(i + 1, len(walls)) if walls[i]["n"] @ walls[j]["n"] < -0.99]
print("opposite-wall distances at the room centre: " + ", ".join("%.3f" % x for x in opp) + " m")

# ---------------- 2. textures ----------------
for s in surfaces:
    nu, nv = int(s["size"][0] / args.texel), int(s["size"][1] / args.texel)
    uu, vv = np.meshgrid((np.arange(nu) + 0.5) * args.texel, (np.arange(nv) + 0.5) * args.texel)
    X = s["origin"][None, None] + uu[..., None] * s["u"] + vv[..., None] * s["v"]
    inside = np.ones((nv, nu), bool)
    if s["kind"] == "floor":
        path = poly.astype(np.float32)
        inside = np.array([[cv2.pointPolygonTest(path, (float(X[r, c_i, 0]), float(X[r, c_i, 2])), False) >= 0
                            for c_i in range(0, nu, 8)] for r in range(0, nv, 8)])
        inside = cv2.resize(inside.astype(np.uint8), (nu, nv), interpolation=cv2.INTER_NEAREST).astype(bool)
    s.update(nu=nu, nv=nv, X=torch.tensor(X.reshape(-1, 3), dtype=torch.float32, device=dev),
             inside=inside, n_on=torch.zeros(nu * nv, device=dev), n_thru=torch.zeros(nu * nv, device=dev))
print("texels: " + ", ".join(f"{s['name']} {s['nu']}x{s['nv']}" for s in surfaces), flush=True)
Kd = torch.tensor([[meta["fx"] / 2, 0, meta["cx"] / 2], [0, meta["fy"] / 2, meta["cy"] / 2], [0, 0, 1]], dtype=torch.float32, device=dev)
Wd, Hd = W // 2, H // 2
t0 = time.time(); ids = list(range(0, len(fr), args.every))
for it, i in enumerate(ids):
    c2w = np.array(fr[i]["c2w"]) @ G; w2c = torch.tensor(np.linalg.inv(c2w), dtype=torch.float32, device=dev)
    with torch.no_grad():
        out, alpha, _ = rasterization(GS["means"], GS["quats"], GS["scales"], GS["opac"], GS["col"], w2c[None], Kd[None],
                                      Wd, Hd, sh_degree=SH, render_mode="ED", near_plane=0.05, far_plane=50)
    dep = out[0, ..., 0]; alp = alpha[0, ..., 0]
    cam = torch.tensor(c2w[:3, 3], dtype=torch.float32, device=dev)
    for s in surfaces:
        pc = s["X"] @ w2c[:3, :3].T + w2c[:3, 3]; z = pc[:, 2]
        uvd = (pc @ Kd.T); ud, vd = uvd[:, 0] / z, uvd[:, 1] / z
        ok = (z > 0.2) & (ud >= 0) & (ud < Wd - 1) & (vd >= 0) & (vd < Hd - 1)
        if ok.sum() < 100:
            continue
        nrm = torch.tensor(s["n"], dtype=torch.float32, device=dev)
        vdir = cam - s["X"]; dist = vdir.norm(dim=1); cosv = (vdir @ nrm) / dist
        ok &= cosv > 0.15
        gd = torch.stack([ud / (Wd - 1) * 2 - 1, vd / (Hd - 1) * 2 - 1], 1)[None, None]
        rd = F.grid_sample(dep[None, None], gd, align_corners=True)[0, 0, 0]
        ra = F.grid_sample(alp[None, None], gd, align_corners=True)[0, 0, 0]
        tol = 0.05 + 0.02 * z
        on = ok & (ra > 0.5) & ((rd - z).abs() < tol)
        thru = ok & (ra > 0.5) & (rd > z + 0.15 + 0.03 * z)
        s["n_on"] += on.float(); s["n_thru"] += thru.float()
    if it % 50 == 0:
        el = time.time() - t0; print(f"  frame {it}/{len(ids)}  {el:.0f}s, ETA {el / (it + 1) * (len(ids) - it - 1):.0f}s", flush=True)

openings = []


@torch.no_grad()
def ortho_texture(sf):
    """orthographic render of the splats within --shell_band of the surface: v3's own (exposure-corrected)
    appearance, flattened onto the plane; furniture in front is excluded because it is not in the band."""
    nrm = torch.tensor(sf["n"], dtype=torch.float32, device=dev); o = torch.tensor(sf["origin"], dtype=torch.float32, device=dev)
    u = torch.tensor(sf["u"], dtype=torch.float32, device=dev); vv_ = torch.tensor(sf["v"], dtype=torch.float32, device=dev)
    rel = GS["means"] - o; a_, b_ = rel @ u, rel @ vv_
    m = ((rel @ nrm).abs() < args.shell_band) & (a_ > -0.1) & (a_ < sf["size"][0] + 0.1) & (b_ > -0.1) & (b_ < sf["size"][1] + 0.1)
    centre = sf["origin"] + sf["u"] * sf["size"][0] / 2 + sf["v"] * sf["size"][1] / 2
    pos = centre + sf["n"] * 1.0                                      # in front of the surface, looking at it
    z = -sf["n"]; y = -sf["v"]; x = np.cross(y, z)                    # OpenCV camera axes, right-handed
    Rw = np.stack([x, y, z]); w2c = np.eye(4); w2c[:3, :3] = Rw; w2c[:3, 3] = -Rw @ pos
    Ko = torch.tensor([[1 / args.texel, 0, sf["nu"] / 2], [0, 1 / args.texel, sf["nv"] / 2], [0, 0, 1]], dtype=torch.float32, device=dev)
    out, alpha, _ = rasterization(GS["means"][m], GS["quats"][m], GS["scales"][m], GS["opac"][m], GS["col"][m],
                                  torch.tensor(w2c, dtype=torch.float32, device=dev)[None], Ko[None], sf["nu"], sf["nv"],
                                  sh_degree=SH, camera_model="ortho", near_plane=0.0, far_plane=10.0)
    rgb = (out[0] / alpha[0].clamp(min=1e-3)).clamp(0, 1).cpu().numpy(); al = alpha[0, ..., 0].cpu().numpy()
    rgb, al = rgb[::-1], al[::-1]                                     # image row 0 = top -> row 0 = v = 0 (floor side)
    if x @ sf["u"] < 0:
        rgb, al = rgb[:, ::-1], al[:, ::-1]
    return np.ascontiguousarray(rgb), np.ascontiguousarray(al), int(m.sum())


for s in surfaces:
    rgb, al, nsp = ortho_texture(s)
    thru = (s["n_thru"] > torch.clamp(1.5 * s["n_on"], min=3)).reshape(s["nv"], s["nu"]).cpu().numpy()
    alpha = s["inside"] & (al > 0.5)
    hole = s["inside"] & (al <= 0.5)
    small = hole & ~ndimage.binary_opening(hole, iterations=10)       # holes < ~10 cm: fill
    if s["kind"] == "wall":
        thru = ndimage.binary_opening(thru & hole | thru & (al < 0.9), iterations=4)
        lab, nl = ndimage.label(thru)
        for j, sl in enumerate(ndimage.find_objects(lab), 1):
            hgt = (sl[0].stop - sl[0].start) * args.texel; wid = (sl[1].stop - sl[1].start) * args.texel
            if hgt < 0.4 or wid < 0.3:
                continue
            bottom = sl[0].start * args.texel
            kind = "door" if bottom < 0.15 and hgt > 1.6 else "window/opening"
            openings.append(dict(wall=s["name"], kind=kind, x_m=sl[1].start * args.texel, width_m=wid, bottom_m=bottom, height_m=hgt))
            alpha[lab == j] = False; small[lab == j] = False
    tex8 = (rgb * 255).astype(np.uint8)
    if small.any():
        tex8 = cv2.inpaint(tex8, small.astype(np.uint8), 5, cv2.INPAINT_TELEA); alpha |= small
    s["coverage"] = float(alpha[s["inside"]].mean())
    rgba = np.dstack([tex8, alpha.astype(np.uint8) * 255])
    cv2.imwrite(os.path.join(args.out, f"tex_{s['name']}.png"), cv2.cvtColor(rgba[::-1].copy() if s["kind"] == "wall" else rgba, cv2.COLOR_RGBA2BGRA))
    s["tex"] = torch.tensor(rgba[None].transpose(0, 3, 1, 2) / 255.0, dtype=torch.float32, device=dev)
    print(f"{s['name']}: {s['nu']}x{s['nv']} texels from {nsp} splats, {100 * s['coverage']:.1f}% covered", flush=True)
json.dump(dict(floor=dict(n=n_f.tolist(), d=d_f), height_m=height, wall_angle_deg=float(np.degrees(th)),
               walls=[dict(n=w_["n"].tolist(), d=w_["d"], deviation_deg=w_["dev_deg"]) for w_ in walls],
               corners=[c.tolist() for c in corners],
               surfaces=[dict(name=s["name"], kind=s["kind"], origin=s["origin"].tolist(), u=s["u"].tolist(), v=s["v"].tolist(),
                              size_m=s["size"], coverage=s["coverage"]) for s in surfaces],
               openings=openings), open(os.path.join(args.out, "structure.json"), "w"), indent=1)
print(f"openings: {openings}")

# ---------------- 3. clean-mode renders ----------------
keep = torch.ones(len(P), dtype=torch.bool, device=dev)
for s in surfaces:
    nrm = torch.tensor(s["n"], dtype=torch.float32, device=dev); o = torch.tensor(s["origin"], dtype=torch.float32, device=dev)
    rel = GS["means"] - o; a_ = rel @ torch.tensor(s["u"], dtype=torch.float32, device=dev); b_ = rel @ torch.tensor(s["v"], dtype=torch.float32, device=dev)
    near = ((rel @ nrm).abs() < args.shell_band) & (a_ > -0.05) & (a_ < s["size"][0] + 0.05) & (b_ > -0.05) & (b_ < s["size"][1] + 0.05)
    keep &= ~near
print(f"clean mode: {int((~keep).sum())} shell splats hidden, {int(keep.sum())} object splats kept")
Kf = torch.tensor([[meta["fx"] / 2, 0, meta["cx"] / 2], [0, meta["fy"] / 2, meta["cy"] / 2], [0, 0, 1]], dtype=torch.float32, device=dev)
yy, xx = torch.meshgrid(torch.arange(Hd, device=dev).float() + 0.5, torch.arange(Wd, device=dev).float() + 0.5, indexing="ij")
dirs_cam = torch.stack([(xx - Kf[0, 2]) / Kf[0, 0], (yy - Kf[1, 2]) / Kf[1, 1], torch.ones_like(xx)], -1)


@torch.no_grad()
def render(c2w_gl, clean):
    c2w = np.array(c2w_gl) @ G; w2c = torch.tensor(np.linalg.inv(c2w), dtype=torch.float32, device=dev)
    m = keep if clean else torch.ones_like(keep)
    out, alpha, _ = rasterization(GS["means"][m], GS["quats"][m], GS["scales"][m], GS["opac"][m], GS["col"][m], w2c[None], Kf[None],
                                  Wd, Hd, sh_degree=SH, render_mode="RGB+ED", near_plane=0.05, far_plane=50)
    rgb, dep, a = out[0, ..., :3], out[0, ..., 3], alpha[0, ..., 0]
    if not clean:
        return rgb.clamp(0, 1)
    R = torch.tensor(c2w[:3, :3], dtype=torch.float32, device=dev); o = torch.tensor(c2w[:3, 3], dtype=torch.float32, device=dev)
    dw = dirs_cam @ R.T; zc = torch.full((Hd, Wd), 1e9, device=dev); pc_ = torch.zeros(Hd, Wd, 3, device=dev)
    for s in surfaces:
        n_ = torch.tensor(s["n"], dtype=torch.float32, device=dev)
        den = dw @ n_; t = (s["d"] - o @ n_) / den
        p = o + t[..., None] * dw; rel = p - torch.tensor(s["origin"], dtype=torch.float32, device=dev)
        a_ = rel @ torch.tensor(s["u"], dtype=torch.float32, device=dev) / s["size"][0]
        b_ = rel @ torch.tensor(s["v"], dtype=torch.float32, device=dev) / s["size"][1]
        ok = (t > 0.05) & (a_ >= 0) & (a_ <= 1) & (b_ >= 0) & (b_ <= 1)
        gd = torch.stack([a_ * 2 - 1, b_ * 2 - 1], -1)[None]
        tx = F.grid_sample(s["tex"], gd, align_corners=False)[0].permute(1, 2, 0)
        ok &= tx[..., 3] > 0.5
        zz = t                                                            # dirs have unit camera z -> t is depth
        better = ok & (zz < zc)
        zc = torch.where(better, zz, zc); pc_ = torch.where(better[..., None], tx[..., :3], pc_)
    hit = zc < 1e8
    front = (dep < zc - 0.03) | ~hit
    comp = torch.where(front[..., None], rgb + (1 - a[..., None]) * pc_ * hit[..., None], pc_)
    return comp.clamp(0, 1)


def lab(img, t):
    img = np.ascontiguousarray(cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE))
    cv2.putText(img, t, (8, 30), 0, 0.9, (0, 0, 0), 5); cv2.putText(img, t, (8, 30), 0, 0.9, (0, 255, 255), 2)
    return img


bgr = lambda x: (x.cpu().numpy()[..., ::-1] * 255).astype(np.uint8)
rows = []
for i in [35, 245, 400, 560]:
    ph = cv2.resize(cv2.imread(os.path.join(args.work, "images", fr[i]["name"] + ".jpg")), (Wd, Hd), interpolation=cv2.INTER_AREA)
    rows.append(np.hstack([lab(ph, "photo"), lab(bgr(render(fr[i]["c2w"], False)), "v3 (photo mode)"),
                           lab(bgr(render(fr[i]["c2w"], True)), "clean mode")]))
cv2.imwrite(os.path.join(args.out, "compare_frames.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])


def look(pos, tgt):
    fw = tgt - pos; fw /= np.linalg.norm(fw); r = np.cross(fw, UP); r /= np.linalg.norm(r); u = np.cross(r, fw)
    c2w = np.eye(4); c2w[:3, 0], c2w[:3, 1], c2w[:3, 2], c2w[:3, 3] = r, u, -fw, pos
    return c2w @ np.array([[0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1.0]])   # portrait roll for the sheet


rows = []
for k, ang in enumerate(np.radians([0, 90, 180, 270])):
    c2w = look(room_c, room_c + np.array([np.cos(ang), -0.35, np.sin(ang)]))
    rows.append(np.hstack([lab(bgr(render(c2w, False)), f"v3 centre {k * 90}"), lab(bgr(render(c2w, True)), f"clean {k * 90}")]))
cv2.imwrite(os.path.join(args.out, "compare_centre.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
# ---------------- clean-mode splat file (viewable in view.py / any 3DGS viewer) ----------------
# object splats of the original + one flat, opaque 1 cm splat per covered texel of each shell surface
from plyfile import PlyElement
from scipy.spatial.transform import Rotation as Rot
C0, cell = 0.28209479177387814, 0.01
parts = [D[keep.cpu().numpy()]]
for sf in surfaces:
    t = sf["tex"][0].permute(1, 2, 0).cpu().numpy(); f_ = int(round(cell / args.texel))
    t = cv2.resize(t, (sf["nu"] // f_, sf["nv"] // f_), interpolation=cv2.INTER_AREA)
    rr, cc = np.nonzero(t[..., 3] > 0.5)
    pos = sf["origin"] + ((cc + 0.5) * cell)[:, None] * sf["u"] + ((rr + 0.5) * cell)[:, None] * sf["v"]
    Rm = np.stack([sf["u"], sf["v"], sf["n"]], 1)
    if np.linalg.det(Rm) < 0:
        Rm[:, 1] *= -1
    q = Rot.from_matrix(Rm).as_quat()                                 # xyzw
    el = np.zeros(len(rr), dtype=D.dtype)
    el["x"], el["y"], el["z"] = pos.T
    for k_ in range(3):
        el[f"f_dc_{k_}"] = (t[rr, cc, k_] - 0.5) / C0
    el["opacity"] = 4.6
    el["scale_0"] = el["scale_1"] = np.log(0.6 * cell); el["scale_2"] = np.log(0.001)
    el["rot_0"], el["rot_1"], el["rot_2"], el["rot_3"] = q[3], q[0], q[1], q[2]
    parts.append(el)
allv = np.concatenate(parts)
PlyData([PlyElement.describe(allv, "vertex")]).write(os.path.join(args.out, "clean.ply"))
print(f"clean.ply: {len(allv)} splats ({int(keep.sum())} objects + {len(allv) - int(keep.sum())} shell texels)")
print("done ->", args.out)
