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


def load_api():
    stubbed = []
    for _ in range(20):
        try:
            from depth_anything_3.api import DepthAnything3
            return DepthAnything3, stubbed
        except ModuleNotFoundError as e:
            _stub(e.name); stubbed.append(e.name)
            for k in [k for k in sys.modules if k.startswith("depth_anything_3")]:
                del sys.modules[k]
    raise RuntimeError(f"could not import, stubbed {stubbed}")
