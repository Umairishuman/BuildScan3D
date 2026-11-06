"""Second opinion on small fixtures: is this candidate really a switch / socket? (semantic-env, after semantic3d.py)

Small things near a wall pass semantic3d.py's geometry rules whatever they are (a mirror piece, a bottle label), so
each light switch / power socket candidate is looked at again: crops from the sharpest frames that detected it
are scored by CLIP against electrical-plate descriptions and generic alternatives (averaged over the views). A
candidate is kept if the electrical descriptions win more than --keep of the probability.

Writes <semantic dir>/verdicts.json, then rerun semantic3d.py with --verdicts to apply it; crops sheet: verify.jpg.

  semantic-env\\Scripts\\python.exe src/arcore3dgs/verify_fixtures.py --work <work_sfm> --sem2d semantic2d_v10 --semantic <dir>
"""
import os, json, argparse
import truststore
truststore.inject_into_ssl()
import numpy as np, cv2, torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True); ap.add_argument("--sem2d", required=True); ap.add_argument("--semantic", required=True)
ap.add_argument("--views", type=int, default=8); ap.add_argument("--keep", type=float, default=0.5)
args = ap.parse_args()
POS = ["a photo of a light switch on a wall", "a photo of a switchboard on a wall", "a photo of an electrical power socket on a wall",
       "a photo of an electrical outlet"]
NEG = ["a photo of a picture frame on a wall", "a photo of a mirror", "a photo of a bottle", "a photo of a sticker or paper label",
       "a photo of a small household object", "a photo of furniture", "a photo of a bare painted wall", "a photo of an electrical appliance"]
dev = "cuda"
m = CLIPModel.from_pretrained("openai/clip-vit-base-patch16").to(dev).eval()
pr = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")
sem = json.load(open(os.path.join(args.semantic, "semantic.json")))
det = json.load(open(os.path.join(args.work, args.sem2d, "detections.json")))
meta = json.load(open(os.path.join(args.work, "frames.json"))); by = {f["name"]: f for f in meta["frames"]}
G = np.diag([1, -1, -1, 1.0]); W, H = meta["W"], meta["H"]; fx, fy, cx, cy = meta["fx"], meta["fy"], meta["cx"], meta["cy"]
ROT = [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]
cache = {}
with torch.no_grad():
    t = pr(text=POS + NEG, return_tensors="pt", padding=True).to(dev)
    T = m.get_text_features(**t); T = T / T.norm(dim=-1, keepdim=True)


def views_of(f):
    """sharpest crops of the frames that detected this candidate at its position"""
    c = det["classes"].index(f["cls"]) + 1; out = []
    for n in det["frames"]:
        p = np.linalg.inv(np.array(by[n]["c2w"]) @ G) @ np.array(f["position"] + [1.0])
        if p[2] < 0.2:
            continue
        u, v = fx * p[0] / p[2] + cx, fy * p[1] / p[2] + cy
        r = max(12, max(f["width"], f["height"]) * fx / p[2] / 2); s = int(max(48, 2.5 * r))
        if not (s <= u < W - s and s <= v < H - s):
            continue
        if n not in cache:
            cache[n] = np.load(os.path.join(args.work, args.sem2d, n + ".npz"))["cls"]
        w = cache[n][max(0, int(v / 2) - 6):int(v / 2) + 7, max(0, int(u / 2) - 6):int(u / 2) + 7]
        if not (w == c).any():
            continue
        im = cv2.imread(os.path.join(args.work, "images", n + ".jpg"))
        cr = im[int(v) - s:int(v) + s, int(u) - s:int(u) + s]
        k = det["frames"][n]["rot"]
        if k:
            cr = cv2.rotate(cr, ROT[k])
        out.append((cv2.Laplacian(cv2.cvtColor(cr, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var() * min(1.0, s / 96), cr))
    out.sort(key=lambda x: -x[0])
    return [c_ for _, c_ in out[: args.views]]


verdicts, rows = [], []
for f in sem["fixtures"] + [r for r in sem["rejected"] if r["cls"] in ("light switch", "power socket") and "seen in" not in r["rejected"] and r["views"] >= 6]:
    if f["cls"] not in ("light switch", "power socket"):
        continue
    cr = views_of(f)
    if not cr:
        verdicts.append(dict(cls=f["cls"], position=f["position"], p_electrical=0.0, keep=False, views_checked=0)); continue
    with torch.no_grad():
        x = pr(images=[Image.fromarray(c_[..., ::-1]) for c_ in cr], return_tensors="pt").to(dev)
        I = m.get_image_features(**x); I = I / I.norm(dim=-1, keepdim=True)
        P = (100 * I @ T.T).softmax(-1).mean(0).cpu().numpy()
    pe = float(P[: len(POS)].sum()); top = (POS + NEG)[int(P.argmax())].replace("a photo of ", "")
    verdicts.append(dict(cls=f["cls"], position=f["position"], height_above_floor=f["height_above_floor"], accepted_by_geometry="rejected" not in f,
                         p_electrical=round(pe, 3), keep=pe > args.keep, top=top, views_checked=len(cr)))
    print(f"{f.get('id', 'rejected ' + f['cls']):20s} {f['height_above_floor']:.2f} m  p(electrical) {pe:.2f}  -> {'KEEP' if pe > args.keep else 'DROP'}   top: {top}")
    tiles = [cv2.resize(c_, (150, 150)) for c_ in (cr + [np.zeros_like(cr[0])] * 6)[:6]]
    row = np.hstack(tiles); cv2.putText(row, f"{f.get('id', 'rej ' + f['cls'])} {f['height_above_floor']:.2f} m p={pe:.2f}", (6, 20), 0, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
    rows.append(row)
json.dump(verdicts, open(os.path.join(args.semantic, "verdicts.json"), "w"), indent=1)
if rows:
    cv2.imwrite(os.path.join(args.semantic, "verify.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
