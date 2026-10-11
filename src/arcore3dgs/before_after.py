"""Before/after sheet: source photo | old model (ARCore/BA poses) | new model (SfM poses), same frames,
plus views from the room centre. Each model is rendered with its own camera solution for that frame.

  nerfstudio-env\\Scripts\\python.exe src/arcore3dgs/before_after.py --old_work <work> --old_ply <ply>
      --new_work <work_sfm> --new_ply <ply> --out <dir>
"""
import os, json, argparse, numpy as np, cv2, torch, torch.nn.functional as F
from plyfile import PlyData
from gsplat import rasterization

ap = argparse.ArgumentParser()
ap.add_argument("--old_work", required=True); ap.add_argument("--old_ply", required=True)
ap.add_argument("--new_work", required=True); ap.add_argument("--new_ply", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--scale", type=float, default=0.5)
args = ap.parse_args()
dev = "cuda"; os.makedirs(args.out, exist_ok=True)
G = np.diag([1, -1, -1, 1.0])


def load(path):
    v = PlyData.read(path)["vertex"]; c = lambda n: torch.tensor(np.asarray(v[n]), dtype=torch.float32, device=dev)
    m = torch.stack([c("x"), c("y"), c("z")], 1)
    nr = len([n for n in v.data.dtype.names if n.startswith("f_rest")])
    col = torch.stack([c(f"f_dc_{i}") for i in range(3)], 1)[:, None]
    if nr:
        col = torch.cat([col, torch.stack([c(f"f_rest_{i}") for i in range(nr)], 1).reshape(len(m), 3, -1).transpose(1, 2)], 1)
    return dict(means=m, quats=F.normalize(torch.stack([c(f"rot_{i}") for i in range(4)], 1), dim=-1),
                scales=torch.exp(torch.stack([c(f"scale_{i}") for i in range(3)], 1)),
                opacities=torch.sigmoid(c("opacity")), colors=col, sh=int(round(np.sqrt(col.shape[1]))) - 1)


class Cam:
    def __init__(self, work):
        self.m = json.load(open(os.path.join(work, "frames.json"))); s = args.scale
        self.W, self.H = int(self.m["W"] * s), int(self.m["H"] * s)
        self.K = torch.tensor([[[self.m["fx"] * s, 0, self.m["cx"] * s], [0, self.m["fy"] * s, self.m["cy"] * s], [0, 0, 1]]],
                              dtype=torch.float32, device=dev)
        self.by = {f["name"]: f for f in self.m["frames"]}


@torch.no_grad()
def render(g, cam, c2w_gl, W=None, H=None, K=None):
    w2c = torch.tensor(np.linalg.inv(np.array(c2w_gl) @ G), dtype=torch.float32, device=dev)[None]
    out, _, _ = rasterization(g["means"], g["quats"], g["scales"], g["opacities"], g["colors"], w2c,
                              cam.K if K is None else K, W or cam.W, H or cam.H, sh_degree=g["sh"])
    return cv2.resize((out[0].clamp(0, 1).cpu().numpy()[..., ::-1] * 255).astype(np.uint8), (int(1920 * args.scale), int(1080 * args.scale)))


def lab(img, t):
    img = np.ascontiguousarray(cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE))
    cv2.putText(img, t, (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 5)
    cv2.putText(img, t, (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
    return img


co, cn = Cam(args.old_work), Cam(args.new_work)
go, gn = load(args.old_ply), load(args.new_ply)
names = [f["name"] for f in cn.m["frames"] if f["name"] in co.by]
t0 = co.m["frames"][0]["pts"]
pick = [names[k] for k in np.linspace(5, len(names) - 6, 8).astype(int)]
rows = []
for n in pick:
    ph = cv2.resize(cv2.imread(os.path.join(args.old_work, "images", n + ".jpg")), (int(1920 * args.scale), int(1080 * args.scale)),
                    interpolation=cv2.INTER_AREA)
    rows.append(np.hstack([lab(ph, f"photo {co.by[n]['pts'] - t0:.0f}s"), lab(render(go, co, co.by[n]["c2w"]), "before"),
                           lab(render(gn, cn, cn.by[n]["c2w"]), "after")]))
for k in range(0, len(rows), 4):
    cv2.imwrite(os.path.join(args.out, f"frames_{k // 4}.jpg"), np.vstack(rows[k:k + 4]), [cv2.IMWRITE_JPEG_QUALITY, 88])


def look(pos, tgt):
    f = tgt - pos; f /= np.linalg.norm(f); r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    c2w = np.eye(4); c2w[:3, 0], c2w[:3, 1], c2w[:3, 2], c2w[:3, 3] = r, u, -f, pos
    return c2w @ np.array([[0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1.0]])   # portrait roll


# both models are in the ARCore metric world (old: BA-refined ARCore; new: Sim3-aligned) -> same pose works
C = np.array([np.array(f["c2w"])[:3, 3] for f in cn.m["frames"]]); c = C.mean(0)
rows = []
for k, ang in enumerate(np.radians([0, 60, 120, 180, 240, 300])):
    c2w = look(c, c + np.array([np.cos(ang), -0.3, np.sin(ang)]))
    rows.append(np.hstack([lab(render(go, co, c2w), f"before {k * 60}deg"), lab(render(gn, cn, c2w), f"after {k * 60}deg")]))
cv2.imwrite(os.path.join(args.out, "centre_0.jpg"), np.vstack(rows[:3]), [cv2.IMWRITE_JPEG_QUALITY, 88])
cv2.imwrite(os.path.join(args.out, "centre_1.jpg"), np.vstack(rows[3:]), [cv2.IMWRITE_JPEG_QUALITY, 88])
print("sheets ->", args.out)
