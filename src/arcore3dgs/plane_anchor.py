"""Room-plane anchoring during training (2026-11-24; R-125 was the preview after training, plane_snap.py).

Splats float off walls and floor because the frames that see a wall disagree slightly (residual camera error) and a
plain wall gives no texture to fix the depth, so training keeps several layers ("copies") of one surface. Snapping a
trained model (R-125) showed the planes can be found from the splats themselves, but cost 3.6 dB (colours fitted to
the old positions) and missed the non-flat splats. Here the same planes are found DURING training and the splats are
moved onto them step by step, while the photometric loss (and --pose_opt) keeps fitting colours and cameras.

PlaneAnchor.fit (every --plane_fit_every steps from --plane_start):
  flat, opaque splats whose normal (smallest-scale axis) is within `snap` deg of a world axis vote for their
  coordinate on that axis (weight opacity x area); vote-histogram peaks are candidate planes; a weaker peak within
  `merge` units whose footprint (cells of `cell` units on the other two axes) overlaps a stronger one's by >= `overlap`
  is a copy and joins it. One floor / one ceiling: horizontal planes below (above) the camera height `cam_y` within
  `level_merge` units of the strongest one join it whatever their footprint (R-125: the floor came out at two levels
  0.56 units apart over different areas = height drift; a table top is further away and stays separate).
PlaneAnchor.project (every --plane_proj_every steps):
  every splat (flat or not) inside a plane's footprint (1 cell margin) and within its reach (band + its merged
  copies' distance) is assigned to the nearest such plane, moved `alpha` of the way onto it, and flat ones within
  `rot_snap` deg are turned so their normal is the plane's axis. Furniture, doors etc. outside the bands are untouched.
"""
import numpy as np
import torch


def quat_to_R(q):                                    # torch, wxyz, [N, 4] -> [N, 3, 3]
    q = torch.nn.functional.normalize(q, dim=-1); w, x, y, z = q.unbind(-1)
    return torch.stack([torch.stack([1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)], -1),
                        torch.stack([2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)], -1),
                        torch.stack([2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)], -1)], -2)


def R_to_quat(R):                                    # torch [N, 3, 3] -> wxyz (Shepperd, branch per element)
    m = R; t = m[:, 0, 0] + m[:, 1, 1] + m[:, 2, 2]
    q = torch.zeros(len(m), 4, device=m.device, dtype=m.dtype)
    c0 = t > 0
    s = torch.sqrt((t[c0] + 1).clamp(min=1e-12)) * 2
    q[c0] = torch.stack([s / 4, (m[c0, 2, 1] - m[c0, 1, 2]) / s, (m[c0, 0, 2] - m[c0, 2, 0]) / s, (m[c0, 1, 0] - m[c0, 0, 1]) / s], -1)
    for i, (a, b, c) in enumerate(((0, 1, 2), (1, 2, 0), (2, 0, 1))):
        sel = ~c0 & (m[:, a, a] >= m[:, b, b]) & (m[:, a, a] >= m[:, c, c])
        if i:
            sel &= ~(q.abs().sum(-1) > 0)
        if not sel.any():
            continue
        mm = m[sel]; s = torch.sqrt((1 + mm[:, a, a] - mm[:, b, b] - mm[:, c, c]).clamp(min=1e-12)) * 2
        v = torch.zeros(len(mm), 4, device=m.device, dtype=m.dtype)
        v[:, 0] = (mm[:, c, b] - mm[:, b, c]) / s; v[:, 1 + a] = s / 4
        v[:, 1 + b] = (mm[:, b, a] + mm[:, a, b]) / s; v[:, 1 + c] = (mm[:, c, a] + mm[:, a, c]) / s
        q[sel] = v
    return torch.nn.functional.normalize(q, dim=-1)


def find_planes(X, nrm, flat, op, area, snap=15.0, bin_=0.02, smooth=0.04, min_support=0.02, merge=0.9, cell=0.25,
                overlap=0.3, band=0.15, cam_y=None, level_merge=0.8):
    """numpy inputs; returns a list of dict(axis, offset, reach, cells (set of 2D cell tuples), support, copies)"""
    cos = np.cos(np.radians(snap)); planes = []
    for ax in range(3):
        al = np.abs(nrm[:, ax]) > cos
        vote = al & flat
        c = X[vote, ax]; w = op[vote] * area[vote]
        if len(c) < 100:
            continue
        k = int(max(1, round(smooth / bin_))); ker = np.exp(-0.5 * (np.arange(-3 * k, 3 * k + 1) / k) ** 2)
        lo, hi = np.percentile(c, 0.5) - 4 * k * bin_, np.percentile(c, 99.5) + 4 * k * bin_   # >= kernel length
        edges = np.arange(lo, hi + bin_, bin_); h, _ = np.histogram(c, edges, weights=w)
        hs = np.convolve(h, ker / ker.sum(), "same"); ctr = (edges[:-1] + edges[1:]) / 2
        pk = [i for i in range(1, len(hs) - 1) if hs[i] >= hs[i - 1] and hs[i] > hs[i + 1] and hs[i] > min_support * hs.max()]
        pk = sorted(pk, key=lambda i: -hs[i])
        if not pk:
            continue
        idx = np.flatnonzero(al)
        dist = np.abs(X[idx, ax][:, None] - ctr[pk][None])
        nb = np.argmin(dist, 1); inb = dist[np.arange(len(idx)), nb] < band
        oth = [o for o in range(3) if o != ax]
        foot = [set(map(tuple, np.floor(X[idx[inb & (nb == j)]][:, oth] / cell).astype(int))) for j in range(len(pk))]
        owner = list(range(len(pk)))
        for j in range(len(pk)):
            for i in range(j):
                if owner[i] != i:
                    continue
                d_ = abs(ctr[pk[i]] - ctr[pk[j]])
                level = (ax == 1 and cam_y is not None and d_ <= level_merge
                         and (ctr[pk[i]] < cam_y) == (ctr[pk[j]] < cam_y))      # one floor / one ceiling
                if level or (d_ <= merge and foot[j] and len(foot[j] & foot[i]) >= overlap * len(foot[j])):
                    owner[j] = i; break
        for i in range(len(pk)):
            if owner[i] != i:
                continue
            grp = [j for j in range(len(pk)) if owner[j] == i]
            cells = set().union(*[foot[j] for j in grp])
            if not cells:
                continue
            off = float(ctr[pk[i]]); copies = [float(ctr[pk[j]]) for j in grp if j != i]
            planes.append(dict(axis=ax, offset=off, reach=band + max([abs(c_ - off) for c_ in copies], default=0.0),
                               cells=cells, support=float(hs[pk[i]] / hs.max()), copies=copies))
    return planes


class PlaneAnchor:
    def __init__(self, cam_y=None, snap=15.0, flat=0.3, min_opacity=0.2, merge=0.9, cell=0.25, overlap=0.3,
                 band=0.15, level_merge=0.8, alpha=0.5, rot_snap=30.0):
        self.cam_y, self.snap, self.flat, self.min_op = cam_y, snap, flat, min_opacity
        self.merge, self.cell, self.overlap, self.band, self.level_merge = merge, cell, overlap, band, level_merge
        self.alpha, self.rot_snap = alpha, rot_snap
        self.planes = []

    @staticmethod
    def _geom(quats, scales):
        R = quat_to_R(quats); S = torch.exp(scales)
        imin = S.argmin(1); srt = S.sort(1).values
        nrm = R[torch.arange(len(R), device=R.device), :, imin]
        return R, S, imin, srt, nrm

    @torch.no_grad()
    def fit(self, means, quats, scales, opacities):
        R, S, imin, srt, nrm = self._geom(quats, scales)
        op = torch.sigmoid(opacities).reshape(-1)
        flat = (srt[:, 0] / srt[:, 1].clamp(min=1e-9) < self.flat) & (op > self.min_op)
        pl = find_planes(means.double().cpu().numpy(), nrm.double().cpu().numpy(), flat.cpu().numpy(),
                         op.double().cpu().numpy(), (srt[:, 1] * srt[:, 2]).double().cpu().numpy(), snap=self.snap,
                         merge=self.merge, cell=self.cell, overlap=self.overlap, band=self.band, cam_y=self.cam_y,
                         level_merge=self.level_merge)
        dev = means.device
        for p in pl:                                  # dense footprint grid, dilated by one cell
            C = np.array(sorted(p["cells"]))
            lo = C.min(0) - 1; hi = C.max(0) + 1
            g = np.zeros(tuple(hi - lo + 1), bool)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    g[C[:, 0] - lo[0] + dx, C[:, 1] - lo[1] + dy] = True
            p["lo"] = torch.tensor(lo, device=dev); p["grid"] = torch.from_numpy(g).to(dev)
            del p["cells"]
        self.planes = pl
        return pl

    @torch.no_grad()
    def project(self, means, quats, scales):
        """moves assigned splats `alpha` of the way onto their plane (in place); returns (assigned, mean |d| before)"""
        if not self.planes:
            return 0, 0.0
        X = means.data; N = len(X); dev = X.device
        best_d = torch.full((N,), float("inf"), device=dev, dtype=X.dtype); best_p = torch.full((N,), -1, dtype=torch.long, device=dev)
        for pi, p in enumerate(self.planes):
            ax = p["axis"]; oth = [o for o in range(3) if o != ax]
            d = (X[:, ax] - p["offset"]).abs()
            near = d < p["reach"]
            ci = torch.floor(X[:, oth] / self.cell).long() - p["lo"]
            G = p["grid"]
            inside = near & (ci[:, 0] >= 0) & (ci[:, 1] >= 0) & (ci[:, 0] < G.shape[0]) & (ci[:, 1] < G.shape[1])
            ok = torch.zeros_like(inside)
            ok[inside] = G[ci[inside, 0], ci[inside, 1]]
            upd = ok & (d < best_d)
            best_d[upd] = d[upd]; best_p[upd] = pi
        a = best_p >= 0
        n = int(a.sum())
        if n == 0:
            return 0, 0.0
        mean_d = float(best_d[a].mean())
        axes = torch.tensor([p["axis"] for p in self.planes], device=dev)[best_p[a]]
        offs = torch.tensor([p["offset"] for p in self.planes], device=dev, dtype=X.dtype)[best_p[a]]
        ia = torch.nonzero(a).squeeze(1)
        cur = X[ia, axes]
        X[ia, axes] = cur + self.alpha * (offs - cur)
        # turn flat, nearly aligned splats so the smallest axis is the plane normal
        R, S, imin, srt, nrm = self._geom(quats.data[ia], scales.data[ia])
        nax = torch.nn.functional.one_hot(axes, 3).to(R.dtype)
        cosang = (nrm * nax).sum(-1)
        sel = (srt[:, 0] / srt[:, 1].clamp(min=1e-9) < self.flat) & (cosang.abs() > np.cos(np.radians(self.rot_snap)))
        if sel.any():
            c0 = nrm[sel] * torch.sign(cosang[sel])[:, None]; t = nax[sel]
            v = torch.cross(c0, t, dim=-1); s = v.norm(dim=-1).clamp(min=1e-9); c = (c0 * t).sum(-1)
            K = torch.zeros(len(v), 3, 3, device=dev, dtype=R.dtype)
            K[:, 0, 1], K[:, 0, 2], K[:, 1, 0], K[:, 1, 2], K[:, 2, 0], K[:, 2, 1] = -v[:, 2], v[:, 1], v[:, 2], -v[:, 0], -v[:, 1], v[:, 0]
            Ra = torch.eye(3, device=dev, dtype=R.dtype)[None] + K + K @ K * ((1 - c) / s ** 2)[:, None, None]
            q = R_to_quat(Ra @ R[sel])
            qi = ia[sel]
            quats.data[qi] = q.to(quats.dtype)
        return n, mean_d
