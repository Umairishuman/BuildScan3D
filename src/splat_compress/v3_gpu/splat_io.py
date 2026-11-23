"""3DGS PLY <-> torch tensors. Layout (INRIA / nerfstudio): x y z | nx ny nz | f_dc_0..2 | f_rest_* | opacity | scale_0..2 | rot_0..3.

`rest` is stored as (N, 3, K): channel-major like the file (f_rest_0..K-1 = R, next K = G, next K = B).
`opacity` is the logit and `scale` the log, exactly as in the file; stages convert when they need the real value.
"""
import numpy as np
import torch
from plyfile import PlyData, PlyElement

SH_REST_PER_CHANNEL = {0: 0, 1: 3, 2: 8, 3: 15}
DEGREE_OF_REST = {v: k for k, v in SH_REST_PER_CHANNEL.items()}


def resolve_device(name):
    if name == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dev = torch.device(name)
    if dev.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("device 'cuda' requested but torch.cuda.is_available() is False")
    return dev


def sh_degree_of(splats):
    return DEGREE_OF_REST[splats["rest"].shape[2]]


def read_ply(path, device="cpu"):
    v = PlyData.read(path)["vertex"]
    names = v.data.dtype.names
    n = v.count

    def col(name):
        return torch.from_numpy(np.asarray(v[name], dtype=np.float32).copy())

    n_rest = sum(c.startswith("f_rest") for c in names)
    if n_rest % 3 or (n_rest // 3) not in DEGREE_OF_REST:
        raise ValueError(f"{path}: {n_rest} f_rest columns is not a valid SH degree (0, 9, 24 or 45 expected)")
    per_ch = n_rest // 3
    s = dict(
        xyz=torch.stack([col(c) for c in "xyz"], 1),
        dc=torch.stack([col(f"f_dc_{i}") for i in range(3)], 1),
        rest=(torch.stack([col(f"f_rest_{i}") for i in range(n_rest)], 1).reshape(n, 3, per_ch)
              if n_rest else torch.zeros(n, 3, 0)),
        opacity=col("opacity"),
        scale=torch.stack([col(f"scale_{i}") for i in range(3)], 1),
        rot=torch.stack([col(f"rot_{i}") for i in range(4)], 1),
        normals=(torch.stack([col(c) for c in ("nx", "ny", "nz")], 1) if "nx" in names else None),
    )
    return {k: (t.to(device) if t is not None else None) for k, t in s.items()}


def write_ply(splats, path):
    s = {k: (t.detach().cpu().numpy() if t is not None else None) for k, t in splats.items() if k != "vq"}
    n = len(s["xyz"])
    rest = s["rest"].reshape(n, -1)
    cols = [(c, s["xyz"][:, i]) for i, c in enumerate("xyz")]
    if s["normals"] is not None:
        cols += [(c, s["normals"][:, i]) for i, c in enumerate(("nx", "ny", "nz"))]
    cols += [(f"f_dc_{i}", s["dc"][:, i]) for i in range(3)]
    cols += [(f"f_rest_{i}", rest[:, i]) for i in range(rest.shape[1])]
    cols += [("opacity", s["opacity"])]
    cols += [(f"scale_{i}", s["scale"][:, i]) for i in range(3)]
    cols += [(f"rot_{i}", s["rot"][:, i]) for i in range(4)]
    out = np.empty(n, dtype=[(name, "f4") for name, _ in cols])
    for name, a in cols:
        out[name] = a
    PlyData([PlyElement.describe(out, "vertex")], text=False).write(path)


def raw_bytes(splats):
    """float32 bytes the splats would take as a PLY (what a size comparison with the input means)."""
    return sum(t.numel() * 4 for k, t in splats.items() if k != "vq" and t is not None)


def subset(splats, mask):
    return {k: (t[mask] if (t is not None and k != "vq") else t) for k, t in splats.items()}
