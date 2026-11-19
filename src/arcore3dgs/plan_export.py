"""As-built floor plan export from layout.py (+ semantic3d.py): plan.json, plan.svg, plan.dxf (#12, plan 4.9).

The plan is drawn in a local 2D frame, in metres: the longest wall runs along +x, the origin is the lower-left corner
of the plan's bounding box, +y points away from that wall (world x / z, seen from above). Contents:
  walls (polyline segments with their lengths), corners (measured filled, inferred hollow), openings (doors, windows
  and, from #9, doorways / window openings from wall gaps) as gaps drawn across the wall, fixtures as small marks
  with their height above the floor, the room height and floor area as a title.
--square (off by default): walls within --square_tol degrees of a right angle to the longest wall are turned onto it
(about their middle) and the corners recomputed, as a drawing aid; the measured plan stays the default, and plan.json
records which walls were turned and by how much.
DXF is AutoCAD R12 ASCII (LINE, CIRCLE, TEXT on layers WALLS / OPENINGS / FIXTURES / TEXT): it opens in AutoCAD,
LibreCAD, QCAD, FreeCAD. Standard library only.

  python src/arcore3dgs/plan_export.py --layout <gs>/layout/layout.json [--semantic <gs>/semantic_v10/semantic.json]
      [--out <gs>/layout] [--square] [--title "scan #8"]
"""
import argparse, json, math, os

ap = argparse.ArgumentParser()
ap.add_argument("--layout", required=True); ap.add_argument("--semantic", default="")
ap.add_argument("--out", default=""); ap.add_argument("--title", default="")
ap.add_argument("--square", action="store_true"); ap.add_argument("--square_tol", type=float, default=5.0)
args = ap.parse_args()
lay = json.load(open(args.layout))
sem = json.load(open(args.semantic)) if args.semantic else None
out = args.out or os.path.dirname(os.path.abspath(args.layout))
walls = lay["walls"]
if not walls:
    raise SystemExit("no walls in the layout: nothing to draw")

# ---------------- local frame: longest wall along +x ----------------
ref = max(walls, key=lambda w: w["length"])
ang0 = math.atan2(ref["p1"][1] - ref["p0"][1], ref["p1"][0] - ref["p0"][0])
ca, sa = math.cos(-ang0), math.sin(-ang0)
rot = lambda p: (p[0] * ca - p[1] * sa, p[0] * sa + p[1] * ca)

segs = [[rot(w["p0"]), rot(w["p1"])] for w in walls]
turned = {}
if args.square:
    for k, (a, b) in enumerate(segs):
        th = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180
        target = min((0, 90, 180), key=lambda t: abs(th - t))
        d = th - target
        if 0.01 <= abs(d) <= args.square_tol:
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2; L = math.dist(a, b); t = math.radians(target)
            if (b[0] - a[0]) * math.cos(t) + (b[1] - a[1]) * math.sin(t) < 0:
                t += math.pi
            segs[k] = [(mx - L / 2 * math.cos(t), my - L / 2 * math.sin(t)), (mx + L / 2 * math.cos(t), my + L / 2 * math.sin(t))]
            turned[k] = round(-d, 2)
    # corners: re-intersect the two walls of each corner and move the wall ends that met there
    for cn in lay.get("corners", []):
        i, j = cn["walls"]; (a, b), (c, d) = segs[i], segs[j]
        den = (b[0] - a[0]) * (d[1] - c[1]) - (b[1] - a[1]) * (d[0] - c[0])
        if abs(den) < 1e-9:
            continue
        s = ((c[0] - a[0]) * (d[1] - c[1]) - (c[1] - a[1]) * (d[0] - c[0])) / den
        X = (a[0] + s * (b[0] - a[0]), a[1] + s * (b[1] - a[1]))
        if cn.get("inferred"):
            continue
        for k in (i, j):
            e = 0 if math.dist(segs[k][0], X) < math.dist(segs[k][1], X) else 1
            segs[k][e] = X

corners = []
for cn in lay.get("corners", []):
    i, j = cn["walls"]
    # the corner is where the two (possibly turned) walls meet: the closest pair of their end points
    best = min(((p, q) for p in segs[i] for q in segs[j]), key=lambda pq: math.dist(*pq))
    p = best[0] if not cn.get("inferred") else rot(cn["xz"])
    corners.append(dict(x=p[0], y=p[1], inferred=bool(cn.get("inferred")), angle=round(cn["angle"], 1)))

# openings and fixtures along their wall (semantic3d.py gives the wall and the distance along it)
def along(k, t):
    """point t m along wall k (from its layout p0), in the plan frame; on the turned wall with --square"""
    w = walls[k]; L = w["length"] or 1.0
    p = rot((w["p0"][0] + (w["p1"][0] - w["p0"][0]) * t / L, w["p0"][1] + (w["p1"][1] - w["p0"][1]) * t / L))
    a, b = segs[k]; ux, uy = b[0] - a[0], b[1] - a[1]; uu = ux * ux + uy * uy or 1.0
    s_ = ((p[0] - a[0]) * ux + (p[1] - a[1]) * uy) / uu
    return a[0] + s_ * ux, a[1] + s_ * uy


items = []
if sem:
    for f in sem.get("fixtures", []):
        if f.get("wall") is None or f.get("along_wall") is None or f["wall"] >= len(segs):
            continue
        is_op = f["cls"] in ("door", "window", "doorway", "window opening")
        p0 = along(f["wall"], f["along_wall"] - (f["width"] / 2 if is_op else 0))
        p1 = along(f["wall"], f["along_wall"] + (f["width"] / 2 if is_op else 0))
        items.append(dict(id=f["id"], cls=f["cls"], wall=f["wall"], opening=is_op, p0=p0, p1=p1,
                          width=f["width"], bottom=f.get("bottom"), top=f.get("top"), height_above_floor=f["height_above_floor"]))
else:
    for k, w in enumerate(walls):
        for n, op in enumerate(w.get("openings", []), 1):
            items.append(dict(id=f"{op['kind'].replace(' ', '_')}_{k}_{n}", cls=op["kind"], wall=k, opening=True,
                              p0=along(k, op["along"] - op["width"] / 2), p1=along(k, op["along"] + op["width"] / 2),
                              width=op["width"], bottom=op["bottom"], top=op["top"], height_above_floor=(op["bottom"] + op["top"]) / 2))

pts = [p for s in segs for p in s] + [(c["x"], c["y"]) for c in corners]
mx, my = min(p[0] for p in pts), min(p[1] for p in pts)
sh = lambda p: (round(p[0] - mx, 4), round(p[1] - my, 4))
segs = [[sh(a), sh(b)] for a, b in segs]
for c in corners:
    c["x"], c["y"] = sh((c["x"], c["y"]))
for it in items:
    it["p0"], it["p1"] = sh(it["p0"]), sh(it["p1"])
W = max(p[0] for s in segs for p in s); H = max(p[1] for s in segs for p in s)

height = lay.get("height"); area = sem.get("floor_area") if sem else None
title = args.title or os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(args.layout))))
facts = [(f"walls {height:.2f} m high (no roof)" if lay.get("open_top") else f"height {height:.2f} m")
         if height is not None and math.isfinite(height) else "height unknown",
         f"floor {area:.2f} m2" if area else "floor area not computed",
         "closed room" if lay.get("room_closed") else ("outline not closed" if lay.get("room_closed") is False else "")]
res = dict(title=title, units="m", frame="longest wall along +x, origin at the lower-left of the plan",
           squared=bool(args.square), turned_walls_deg=turned, height=height, floor_area=area, open_top=lay.get("open_top", False),
           room_closed=lay.get("room_closed"), warnings=lay.get("warnings", []),
           walls=[dict(id=k, p0=a, p1=b, length=round(math.dist(a, b), 3)) for k, (a, b) in enumerate(segs)],
           corners=corners, items=items, size=[round(W, 3), round(H, 3)])
suffix = "_square" if args.square else ""
json.dump(res, open(os.path.join(out, f"plan{suffix}.json"), "w"), indent=1)

# ---------------- SVG (1 m = 100 px, y up in the plan = up on the page) ----------------
S, M_ = 100, 60
X = lambda p: M_ + p[0] * S; Y = lambda p: M_ + (H - p[1]) * S
COL = {"door": "#285aff", "doorway": "#285aff", "window": "#00a0d0", "window opening": "#00a0d0"}
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W * S + 2 * M_ + 160:.0f}" height="{H * S + 2 * M_ + 40:.0f}" '
       f'font-family="sans-serif" font-size="13">', '<rect width="100%" height="100%" fill="white"/>',
       f'<text x="{M_}" y="24" font-size="16" font-weight="bold">{title}</text>',
       f'<text x="{M_}" y="44" fill="#555">{" · ".join(x for x in facts if x)}{" · walls squared" if args.square else ""}</text>']
for k, (a, b) in enumerate(segs):
    svg.append(f'<line x1="{X(a):.1f}" y1="{Y(a):.1f}" x2="{X(b):.1f}" y2="{Y(b):.1f}" stroke="#222" stroke-width="6" stroke-linecap="square"/>')
    m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    svg.append(f'<text x="{X(m):.1f}" y="{Y(m) - 8:.1f}" text-anchor="middle" fill="#060">{math.dist(a, b):.2f} m</text>')
for it in items:
    if it["opening"]:
        c = COL.get(it["cls"], "#285aff")
        svg.append(f'<line x1="{X(it["p0"]):.1f}" y1="{Y(it["p0"]):.1f}" x2="{X(it["p1"]):.1f}" y2="{Y(it["p1"]):.1f}" '
                   f'stroke="white" stroke-width="8"/>')
        svg.append(f'<line x1="{X(it["p0"]):.1f}" y1="{Y(it["p0"]):.1f}" x2="{X(it["p1"]):.1f}" y2="{Y(it["p1"]):.1f}" '
                   f'stroke="{c}" stroke-width="3" stroke-dasharray="{"6 4" if "opening" in it["cls"] or it["cls"] == "doorway" else "none"}"/>')
        svg.append(f'<text x="{X(it["p0"]):.1f}" y="{Y(it["p0"]) + 20:.1f}" fill="{c}" font-size="11">{it["cls"]} {it["width"]:.2f} m</text>')
    else:
        svg.append(f'<circle cx="{X(it["p0"]):.1f}" cy="{Y(it["p0"]):.1f}" r="5" fill="#c06" />'
                   f'<text x="{X(it["p0"]) + 7:.1f}" y="{Y(it["p0"]) + 4:.1f}" fill="#c06" font-size="10">{it["cls"]} {it["height_above_floor"]:.2f} m</text>')
for c in corners:
    svg.append(f'<circle cx="{X((c["x"], c["y"])):.1f}" cy="{Y((c["x"], c["y"])):.1f}" r="5" '
               f'fill="{"white" if c["inferred"] else "#d00"}" stroke="#d00" stroke-width="2"/>')
svg.append(f'<line x1="{M_}" y1="{H * S + M_ + 25:.0f}" x2="{M_ + S}" y2="{H * S + M_ + 25:.0f}" stroke="#000" stroke-width="2"/>'
           f'<text x="{M_ + S + 6}" y="{H * S + M_ + 29:.0f}">1 m</text></svg>')
open(os.path.join(out, f"plan{suffix}.svg"), "w").write("\n".join(svg) + "\n")

# ---------------- DXF R12 ----------------
dx = ["0", "SECTION", "2", "ENTITIES"]
def line(a, b, layer):
    dx.extend(["0", "LINE", "8", layer, "10", f"{a[0]:.4f}", "20", f"{a[1]:.4f}", "30", "0.0",
               "11", f"{b[0]:.4f}", "21", f"{b[1]:.4f}", "31", "0.0"])
def text(p, s, layer, h=0.08):
    dx.extend(["0", "TEXT", "8", layer, "10", f"{p[0]:.4f}", "20", f"{p[1]:.4f}", "30", "0.0", "40", f"{h}", "1", s])
for a, b in segs:
    line(a, b, "WALLS"); text(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 0.05), f"{math.dist(a, b):.2f} m", "TEXT")
for it in items:
    if it["opening"]:
        line(it["p0"], it["p1"], "OPENINGS"); text((it["p0"][0], it["p0"][1] - 0.15), f"{it['cls']} {it['width']:.2f} m", "TEXT", 0.06)
    else:
        dx.extend(["0", "CIRCLE", "8", "FIXTURES", "10", f"{it['p0'][0]:.4f}", "20", f"{it['p0'][1]:.4f}", "30", "0.0", "40", "0.05"])
        text((it["p0"][0] + 0.07, it["p0"][1]), f"{it['cls']} {it['height_above_floor']:.2f} m", "TEXT", 0.05)
for c in corners:
    dx.extend(["0", "CIRCLE", "8", "WALLS", "10", f"{c['x']:.4f}", "20", f"{c['y']:.4f}", "30", "0.0", "40", "0.04"])
text((0, H + 0.4), f"{title}: " + ", ".join(x for x in facts if x), "TEXT", 0.12)
dx.extend(["0", "ENDSEC", "0", "EOF"])
open(os.path.join(out, f"plan{suffix}.dxf"), "w").write("\n".join(dx) + "\n")
print(f"{len(segs)} walls, {len(corners)} corners, {sum(i['opening'] for i in items)} openings, "
      f"{sum(not i['opening'] for i in items)} fixtures{', squared: ' + str(turned) if args.square else ''} -> "
      f"{os.path.join(out, 'plan' + suffix)}.json / .svg / .dxf")
