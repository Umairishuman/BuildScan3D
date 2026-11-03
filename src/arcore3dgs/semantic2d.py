"""Per-frame 2D semantics of building fixtures, for semantic3d.py (which lifts them onto the 3D model).

Open-vocabulary detection (Grounding DINO tiny) finds doors, windows, light switches, sockets, lights, AC units
... from a text prompt (no training on our data); SAM (ViT-B) turns each box into a pixel mask. The phone
frames are stored sideways (portrait capture), and detectors are trained on upright photos, so every frame is
first rotated upright using gravity (world +Y from the frame's pose). All classes go into one prompt; each
detection is assigned the class whose prompt tokens score highest (no fragile phrase matching).

Writes <work>/semantic2d/<name>.npz: cls (uint8 [H/2, W/2], 0 = none, i = CLASSES[i-1]), inst (uint16, per-frame
detection index + 1), and <work>/semantic2d/detections.json (class, score, box, mask area per frame).

  semantic-env\\Scripts\\python.exe src/arcore3dgs/semantic2d.py --work <work_sfm> [--every 3] [--debug 12]
"""
import os, json, argparse, time
import truststore
truststore.inject_into_ssl()                                  # this network re-signs TLS: use the Windows store
import numpy as np, cv2, torch, torchvision
from PIL import Image
from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor, SamModel, SamProcessor

CLASSES = ["door", "window", "light switch", "power socket", "ceiling light", "tube light", "lamp", "air conditioner", "ceiling fan"]
# decoys: everyday things the detector otherwise calls a fixture (framed pictures -> "window", microwave ->
# "socket", wardrobe -> "door"); a detection is assigned to the best-scoring class INCLUDING these, and
# semantic3d.py ignores decoy classes
DECOYS = ["picture frame", "wardrobe", "cabinet", "television", "microwave", "mirror", "clock", "rug", "curtain", "bottle", "sticker"]
# ... except that furniture does not compete with "door": it took real doors away (door detections 534 -> 366 and
# a door lost), and semantic3d.py separates the two by geometry (a wardrobe front stands in front of the wall)
FURNITURE = ["wardrobe", "cabinet"]
# second pass on zoomed tiles (--tiles): small things are only ~35 px wide once the frame is resized for the detector
SMALL = ["light switch", "power socket", "picture frame", "mirror", "clock", "bottle", "sticker"]
ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--every", type=int, default=3)
ap.add_argument("--box_thr", type=float, default=0.30)
ap.add_argument("--classes", default=",".join(CLASSES + DECOYS))
ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--out", default="semantic2d", help="output folder inside --work")
ap.add_argument("--tiles", type=int, default=0, help="> 0: tile size (px) of the second pass for small objects, e.g. 640")
ap.add_argument("--debug", type=int, default=0, help="write N overlay images to semantic2d/_debug")
args = ap.parse_args()
classes = args.classes.split(",")
dev = "cuda"
out = os.path.join(args.work, args.out); os.makedirs(out, exist_ok=True)
meta = json.load(open(os.path.join(args.work, "frames.json")))
frames = meta["frames"][:: args.every]
frames = frames[: args.limit] if args.limit else frames
G = np.diag([1.0, -1.0, -1.0, 1.0])

dp = AutoProcessor.from_pretrained("IDEA-Research/grounding-dino-tiny")
dm = AutoModelForZeroShotObjectDetection.from_pretrained("IDEA-Research/grounding-dino-tiny").to(dev).eval()
sp = SamProcessor.from_pretrained("facebook/sam-vit-base")
sm = SamModel.from_pretrained("facebook/sam-vit-base").to(dev).eval()


def make_prompt(names):
    text = ". ".join(names) + "."
    enc = dp.tokenizer(text, return_offsets_mapping=True)
    spans, pos = [], 0
    for c in names:                                           # prompt tokens belonging to each class phrase
        a = text.index(c, pos); b = a + len(c); pos = b
        spans.append([t for t, (s_, e) in enumerate(enc["offset_mapping"]) if s_ >= a and e <= b and e > s_])
    return dict(text=text, spans=spans, ids=[classes.index(c) for c in names], names=names)


FULL = make_prompt(classes)
TILE = make_prompt([c for c in SMALL if c in classes])
ROT = [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]
UNROT = [None, cv2.ROTATE_90_COUNTERCLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_CLOCKWISE]


def upright_k(c2w_gl):
    """number of 90 deg clockwise turns that put world-up at the top of the image"""
    up = (np.array(c2w_gl) @ G)[:3, :3].T @ np.array([0.0, 1.0, 0.0])   # world up in OpenCV camera axes
    v = np.array([up[0], up[1]]); best, bk = 1e9, 0
    for k in range(4):
        if k:
            v_ = v.copy()
            for _ in range(k):
                v_ = np.array([-v_[1], v_[0]])                # a 90 deg clockwise image turn maps (x, y) -> (-y, x)
        else:
            v_ = v
        if v_[1] < best:                                      # want "up" pointing to -y (top of the image)
            best, bk = v_[1], k
    return bk


def per_class_nms(dets):
    res = []
    for c in {d[0] for d in dets}:
        ds = [d for d in dets if d[0] == c]
        k = torchvision.ops.nms(torch.tensor([d[2] for d in ds]), torch.tensor([d[1] for d in ds]), 0.5)
        res += [ds[i] for i in k.tolist()]
    return res


@torch.no_grad()
def detect(rgb, prompt):
    """[(class id in `classes`, score, box)]: each query goes to its best-scoring class"""
    h, w = rgb.shape[:2]
    inp = dp(images=Image.fromarray(rgb), text=prompt["text"], return_tensors="pt").to(dev)
    o = dm(**inp)
    L = o.logits.sigmoid()[0]                                 # [queries, tokens]
    S = torch.stack([L[:, sp_].max(1).values for sp_ in prompt["spans"]], 1)   # [queries, classes of the prompt]
    sc, ci = S.max(1)
    if "door" in prompt["names"]:                             # furniture does not compete with door
        door = prompt["names"].index("door"); furn = [prompt["names"].index(c) for c in FURNITURE if c in prompt["names"]]
        m = torch.isin(ci, torch.tensor(furn, device=ci.device)) & (S[:, door] > args.box_thr)
        ci[m] = door; sc[m] = S[m, door]
    keep = sc > args.box_thr
    bx = o.pred_boxes[0][keep]; sc = sc[keep]; ci = ci[keep]
    cx, cy, bw, bh = bx.unbind(1)
    boxes = torch.stack([(cx - bw / 2) * w, (cy - bh / 2) * h, (cx + bw / 2) * w, (cy + bh / 2) * h], 1)
    res = [(prompt["ids"][int(c)], float(v), b.tolist()) for c, v, b in zip(ci, sc, boxes)]
    # a box covering most of the frame is a "the whole scene is a room" hallucination
    return [r for r in res if (r[2][2] - r[2][0]) * (r[2][3] - r[2][1]) < 0.6 * w * h]


def detect_tiles(rgb, size):
    """small objects on overlapping zoomed tiles, boxes back in frame coordinates; a box cut by a tile border is dropped"""
    h, w = rgb.shape[:2]; step = int(size * 0.7); res = []
    xs = sorted({*range(0, max(1, w - size), step), max(0, w - size)}); ys = sorted({*range(0, max(1, h - size), step), max(0, h - size)})
    for y0 in ys:
        for x0 in xs:
            cr = rgb[y0:y0 + size, x0:x0 + size]
            for c, v, b in detect(cr, TILE):
                cut = (b[0] < 4 and x0 > 0) or (b[1] < 4 and y0 > 0) or (b[2] > cr.shape[1] - 4 and x0 + size < w) or (b[3] > cr.shape[0] - 4 and y0 + size < h)
                if cut or max(b[2] - b[0], b[3] - b[1]) > 0.6 * size:
                    continue
                res.append((c, v, [b[0] + x0, b[1] + y0, b[2] + x0, b[3] + y0]))
    return res


@torch.no_grad()
def masks(rgb, boxes):
    if not boxes:
        return []
    inp = sp(Image.fromarray(rgb), input_boxes=[boxes], return_tensors="pt").to(dev)
    o = sm(**inp, multimask_output=True)
    ms = sp.image_processor.post_process_masks(o.pred_masks.cpu(), inp["original_sizes"].cpu(), inp["reshaped_input_sizes"].cpu())[0]
    best = o.iou_scores[0].argmax(-1).cpu()                   # [boxes]
    return [ms[i, best[i]].numpy() for i in range(len(boxes))]


dets_all = {}; dbg = 0; t0 = time.time()
base = [[40, 120, 255], [255, 200, 0], [255, 0, 255], [0, 255, 255], [255, 255, 255], [0, 255, 0], [255, 80, 80], [160, 80, 255]]
pal = np.array([[0, 0, 0]] + [base[i % len(base)] if c not in DECOYS else [128, 128, 128] for i, c in enumerate(classes)], np.uint8)
for fi, f in enumerate(frames):
    img = cv2.imread(os.path.join(args.work, "images", f["name"] + ".jpg"))
    H, W = img.shape[:2]
    k = upright_k(f["c2w"])
    up = cv2.rotate(img, ROT[k]) if k else img
    rgb = cv2.cvtColor(up, cv2.COLOR_BGR2RGB)
    dets = detect(rgb, FULL)
    if args.tiles:
        dets += detect_tiles(rgb, args.tiles)
    dets = per_class_nms(dets)
    ms = masks(rgb, [d[2] for d in dets])
    cls = np.zeros(up.shape[:2], np.uint8); inst = np.zeros(up.shape[:2], np.uint16)
    order = np.argsort([-(m.sum()) for m in ms]) if ms else []
    for j in order:                                           # big masks first, small (switches) painted on top
        cls[ms[j]] = dets[j][0] + 1; inst[ms[j]] = j + 1
    if k:
        cls = cv2.rotate(cls, UNROT[k]); inst = cv2.rotate(inst, UNROT[k])
    np.savez_compressed(os.path.join(out, f["name"] + ".npz"),
                        cls=cv2.resize(cls, (W // 2, H // 2), interpolation=cv2.INTER_NEAREST),
                        inst=cv2.resize(inst, (W // 2, H // 2), interpolation=cv2.INTER_NEAREST))
    dets_all[f["name"]] = dict(rot=k, det=[dict(cls=classes[c], score=round(s, 3), box_upright=[round(x, 1) for x in b],
                                                area=int(m.sum())) for (c, s, b), m in zip(dets, ms)])
    if dbg < args.debug and fi % max(1, len(frames) // args.debug) == 0:
        os.makedirs(os.path.join(out, "_debug"), exist_ok=True)
        ov = up.copy(); cu = cv2.rotate(cls, ROT[k]) if k else cls
        ov[cu > 0] = (0.45 * ov[cu > 0] + 0.55 * pal[cu[cu > 0]][:, ::-1]).astype(np.uint8)
        for (c, s, b) in dets:
            x0, y0, x1, y1 = map(int, b)
            cv2.rectangle(ov, (x0, y0), (x1, y1), tuple(int(v) for v in pal[c + 1][::-1]), 3)
            cv2.putText(ov, f"{classes[c]} {s:.2f}", (x0 + 4, max(20, y0 + 22)), 0, 0.8, (0, 0, 0), 4)
            cv2.putText(ov, f"{classes[c]} {s:.2f}", (x0 + 4, max(20, y0 + 22)), 0, 0.8, (255, 255, 255), 2)
        cv2.imwrite(os.path.join(out, "_debug", f["name"] + ".jpg"), cv2.resize(ov, (ov.shape[1] // 2, ov.shape[0] // 2)))
        dbg += 1
    if fi % 50 == 0:
        print(f"{fi}/{len(frames)} {f['name']} rot {k}: " + ", ".join(f"{classes[c]} {s:.2f}" for c, s, _ in dets), flush=True)
json.dump(dict(classes=classes, decoys=[c for c in classes if c in DECOYS], every=args.every, box_thr=args.box_thr, frames=dets_all),
          open(os.path.join(out, "detections.json"), "w"), indent=1)
cnt = {}
for v in dets_all.values():
    for d in v["det"]:
        cnt[d["cls"]] = cnt.get(d["cls"], 0) + 1
print(f"done: {len(frames)} frames in {time.time() - t0:.0f} s; detections per class: {cnt}")
