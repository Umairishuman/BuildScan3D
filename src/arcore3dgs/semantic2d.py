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
import numpy as np, cv2, torch
from PIL import Image
from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor, SamModel, SamProcessor

CLASSES = ["door", "window", "light switch", "power socket", "ceiling light", "lamp", "air conditioner", "ceiling fan"]
# decoys: everyday things the detector otherwise calls a fixture (framed pictures -> "window", microwave ->
# "socket", wardrobe -> "door"); a detection is assigned to the best-scoring class INCLUDING these, and
# semantic3d.py ignores decoy classes
DECOYS = ["picture frame", "wardrobe", "cabinet", "television", "microwave", "mirror", "clock", "rug", "curtain"]
ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--every", type=int, default=3)
ap.add_argument("--box_thr", type=float, default=0.30)
ap.add_argument("--classes", default=",".join(CLASSES + DECOYS))
ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--debug", type=int, default=0, help="write N overlay images to semantic2d/_debug")
args = ap.parse_args()
classes = args.classes.split(",")
dev = "cuda"
out = os.path.join(args.work, "semantic2d"); os.makedirs(out, exist_ok=True)
meta = json.load(open(os.path.join(args.work, "frames.json")))
frames = meta["frames"][:: args.every]
frames = frames[: args.limit] if args.limit else frames
G = np.diag([1.0, -1.0, -1.0, 1.0])

dp = AutoProcessor.from_pretrained("IDEA-Research/grounding-dino-tiny")
dm = AutoModelForZeroShotObjectDetection.from_pretrained("IDEA-Research/grounding-dino-tiny").to(dev).eval()
sp = SamProcessor.from_pretrained("facebook/sam-vit-base")
sm = SamModel.from_pretrained("facebook/sam-vit-base").to(dev).eval()
text = ". ".join(classes) + "."
enc = dp.tokenizer(text, return_offsets_mapping=True)
spans, pos = [], 0
for c in classes:                                             # prompt tokens belonging to each class phrase
    a = text.index(c, pos); b = a + len(c); pos = b
    spans.append([t for t, (s, e) in enumerate(enc["offset_mapping"]) if s >= a and e <= b and e > s])
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


@torch.no_grad()
def detect(rgb):
    h, w = rgb.shape[:2]
    inp = dp(images=Image.fromarray(rgb), text=text, return_tensors="pt").to(dev)
    o = dm(**inp)
    L = o.logits.sigmoid()[0]                                 # [queries, tokens]
    S = torch.stack([L[:, sp_].max(1).values for sp_ in spans], 1)   # [queries, classes]
    sc, ci = S.max(1)
    keep = sc > args.box_thr
    bx = o.pred_boxes[0][keep]; sc = sc[keep]; ci = ci[keep]
    cx, cy, bw, bh = bx.unbind(1)
    boxes = torch.stack([(cx - bw / 2) * w, (cy - bh / 2) * h, (cx + bw / 2) * w, (cy + bh / 2) * h], 1)
    res = []
    for c in ci.unique():                                     # per-class NMS
        m = ci == c
        k = torch.ops.torchvision.nms(boxes[m], sc[m], 0.5) if hasattr(torch.ops, "torchvision") else torch.arange(int(m.sum()))
        idx = torch.nonzero(m).squeeze(1)[k]
        res += [(int(c), float(sc[i]), boxes[i].tolist()) for i in idx]
    # a box covering most of the frame is a "the whole scene is a room" hallucination
    return [r for r in res if (r[2][2] - r[2][0]) * (r[2][3] - r[2][1]) < 0.6 * w * h]


@torch.no_grad()
def masks(rgb, boxes):
    if not boxes:
        return []
    inp = sp(Image.fromarray(rgb), input_boxes=[boxes], return_tensors="pt").to(dev)
    o = sm(**inp, multimask_output=True)
    ms = sp.image_processor.post_process_masks(o.pred_masks.cpu(), inp["original_sizes"].cpu(), inp["reshaped_input_sizes"].cpu())[0]
    best = o.iou_scores[0].argmax(-1).cpu()                   # [boxes]
    return [ms[i, best[i]].numpy() for i in range(len(boxes))]


try:
    import torchvision  # noqa: F401  (registers torch.ops.torchvision.nms)
except ImportError:
    pass
dets_all = {}; dbg = 0; t0 = time.time()
base = [[40, 120, 255], [255, 200, 0], [255, 0, 255], [0, 255, 255], [255, 255, 255], [0, 255, 0], [255, 80, 80], [160, 80, 255]]
pal = np.array([[0, 0, 0]] + [base[i % len(base)] if c not in DECOYS else [128, 128, 128] for i, c in enumerate(classes)], np.uint8)
for fi, f in enumerate(frames):
    img = cv2.imread(os.path.join(args.work, "images", f["name"] + ".jpg"))
    H, W = img.shape[:2]
    k = upright_k(f["c2w"])
    up = cv2.rotate(img, ROT[k]) if k else img
    rgb = cv2.cvtColor(up, cv2.COLOR_BGR2RGB)
    dets = detect(rgb)
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
