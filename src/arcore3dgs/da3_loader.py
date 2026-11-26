"""Import Depth Anything 3's model API (D-097) with empty stand-ins for modules only its export helpers use
(moviepy, pycolmap, evo, ...). The package (depth_anything_3 0.1.1 wheel, Apache-2.0) and its few runtime
dependencies live outside the repo and outside nerfstudio-env: <cache>/da3 and <cache>/da3_deps,
cache = $BUILDSCAN_CACHE or C:/Users/<user>/.cache/buildscan. Feasibility tests only (vggt_chunk.py --da3)."""
import os
import sys
import types

_CACHE = os.environ.get("BUILDSCAN_CACHE", os.path.join(os.path.expanduser("~"), ".cache", "buildscan"))
for _d in ("da3", "da3_deps"):
    _p = os.path.join(_CACHE, _d)
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.append(_p)


def _stub(name):
    parts = name.split(".")
    for i in range(1, len(parts) + 1):
        mn = ".".join(parts[:i])
        if mn not in sys.modules:
            m = types.ModuleType(mn); m.__path__ = []
            m.__getattr__ = lambda attr, _mn=mn: type(attr, (), {"__init__": lambda self, *a, **k: None})
            sys.modules[mn] = m


def _umeyama_sim3_from_paths(pose_ref, pose_est):
    """numpy stand-in for DA3's evo-based Sim3 fit (evo is not installed): camera centres of pose_est onto pose_ref,
    ref ~ s * R @ est + t (Umeyama 1991). Used when DA3 is given known poses (mono_prior.py --da3_poses)."""
    import numpy as np
    X, Y = pose_est[:, :3, 3], pose_ref[:, :3, 3]
    mx, my = X.mean(0), Y.mean(0); Xc, Yc = X - mx, Y - my
    U, D, Vt = np.linalg.svd(Yc.T @ Xc / len(X))
    Sg = np.diag([1.0, 1.0, np.sign(np.linalg.det(U) * np.linalg.det(Vt))])
    R = U @ Sg @ Vt
    s = float(np.trace(np.diag(D) @ Sg) / max((Xc ** 2).sum() / len(X), 1e-12))
    t = my - s * R @ mx
    import depth_anything_3.utils.pose_align as pa
    return R, t, s, pa._apply_sim3_to_poses(pose_est, R, t, s)


def load_api():
    stubbed = []
    for _ in range(20):
        try:
            from depth_anything_3.api import DepthAnything3
            import depth_anything_3.utils.pose_align as pa
            pa._umeyama_sim3_from_paths = _umeyama_sim3_from_paths
            return DepthAnything3, stubbed
        except ModuleNotFoundError as e:
            _stub(e.name); stubbed.append(e.name)
            for k in [k for k in sys.modules if k.startswith("depth_anything_3")]:
                del sys.modules[k]
    raise RuntimeError(f"could not import, stubbed {stubbed}")
