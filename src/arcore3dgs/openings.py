"""Openings in a wall from gaps in its surface: doorways and window openings without a leaf or frame (#9, plan 4.5).

The 2D detector only knows doors with a leaf and windows with a frame; a doorway in a finished room or the empty
openings of a building under construction (scan #7) are never detected. Here every wall of the layout is looked at
as a grid along the wall x height (--cell m):
  - "surface": opaque Gaussians on the wall face (from --behind_tol behind it to --front_tol in front of it);
  - "through": opaque Gaussians behind the wall (from --behind_min to --behind_max m beyond it): the camera saw
    through the wall there. Something seen through a gap is what makes it an opening; a gap with nothing behind it
    was simply not seen (or is hidden by furniture) and is ignored.
A cell is open if it has no surface and something behind it. Open cells are closed morphologically (one cell),
grouped into connected components and classified by size (heights above the floor):
  doorway: from the floor (bottom < 0.3 m), >= 1.6 m tall, 0.6 - 2.5 m wide
  window opening: sill >= 0.3 m, 0.3 - 3 m wide, 0.3 - 2.5 m tall
Everything else is dropped, and so is a gap with fewer than --min_through Gaussians seen behind it per open cell (a
few stray splats behind a wall are not a view through it; threshold from R-054, two rooms). Pure numpy (scipy for the components): imported by layout.py, tested in tests/.
"""
import numpy as np
from scipy import ndimage

DOOR = dict(max_bottom=0.3, min_height=1.6, min_width=0.6, max_width=2.5)
WINDOW = dict(min_sill=0.3, min_width=0.3, max_width=3.0, min_height=0.3, max_height=2.5)


def find_openings(P, o, cen, dirv, nrm, t0, t1, floor_y, top_y, cell=0.1, front_tol=0.08, behind_tol=0.12,
                  behind_min=0.3, behind_max=4.0, min_opac=0.5, min_fill=0.5, min_through=10.0):
    """P: (N, 3) Gaussian centres (+Y up), o: (N,) opacity; the wall: centre / direction / normal (into the room) in
    the floor plane (x, z) and its extent t0..t1 along dirv; floor_y / top_y: heights of the floor and the wall top.
    Returns a list of dicts: kind (doorway / window opening), along (centre, m from t0), width, bottom, top (above
    the floor), cells (open cells), fill (open share of its bounding box), through (Gaussians seen behind it)."""
    if not np.isfinite(top_y) or top_y - floor_y < 1.0 or t1 - t0 < 0.5:
        return []
    keep = (o > min_opac) & (P[:, 1] > floor_y) & (P[:, 1] < top_y)
    Q = P[keep]
    rel = Q[:, [0, 2]] - cen
    t = rel @ dirv - t0
    sd = rel @ nrm                                           # + into the room, - behind the wall
    h = Q[:, 1] - floor_y
    L, H = t1 - t0, top_y - floor_y
    nt, nh = int(np.ceil(L / cell)), int(np.ceil(H / cell))
    inside = (t >= 0) & (t < L)
    ti = np.clip((t / cell).astype(int), 0, nt - 1); hi = np.clip((h / cell).astype(int), 0, nh - 1)
    surf = np.zeros((nh, nt), bool); thr = np.zeros((nh, nt), np.int32)
    m = inside & (sd > -behind_tol) & (sd < front_tol)
    surf[hi[m], ti[m]] = True
    # behind the wall: project along the viewing direction onto the wall would need the cameras; the wall normal is
    # a close stand-in for views roughly facing the wall and keeps this independent of the poses
    m = inside & (sd < -behind_min) & (sd > -behind_max)
    np.add.at(thr, (hi[m], ti[m]), 1)
    open_ = ~surf & (thr > 0)
    # closing on a padded grid: without the pad it erodes the border rows, and a doorway would not reach the floor
    open_ = ndimage.binary_closing(np.pad(open_, 1, mode="edge"), structure=np.ones((3, 3)))[1:-1, 1:-1] & ~surf
    lab, n = ndimage.label(open_)
    out = []
    for k in range(1, n + 1):
        rr, cc = np.nonzero(lab == k)
        a0, a1 = cc.min() * cell, (cc.max() + 1) * cell
        b0, b1 = rr.min() * cell, (rr.max() + 1) * cell
        w_, h_ = a1 - a0, b1 - b0
        fill = len(rr) / (((cc.max() - cc.min() + 1) * (rr.max() - rr.min() + 1)))
        through = int(thr[lab == k].sum())
        # a real opening shows a lot of the model behind it (R-054: scan #7's doorway / big window 41 / 19 Gaussians
        # per open cell); a few stray splats behind a wall are not a view through it (scan #3's four false
        # "windows" and scan #7's two small ones: 1-4 per cell)
        if fill < min_fill or through < min_through * len(rr):
            continue
        if b0 < DOOR["max_bottom"] and h_ >= DOOR["min_height"] and DOOR["min_width"] <= w_ <= DOOR["max_width"]:
            kind = "doorway"
        elif b0 >= WINDOW["min_sill"] and WINDOW["min_width"] <= w_ <= WINDOW["max_width"] and \
                WINDOW["min_height"] <= h_ <= WINDOW["max_height"]:
            kind = "window opening"
        else:
            continue
        out.append(dict(kind=kind, along=round(float((a0 + a1) / 2), 3), width=round(float(w_), 3),
                        bottom=round(float(b0), 3), top=round(float(b1), 3), cells=int(len(rr)),
                        fill=round(float(fill), 2), through=through))
    return out
