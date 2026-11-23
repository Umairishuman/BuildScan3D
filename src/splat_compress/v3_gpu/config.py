"""Config handling: defaults from config.default.json, a user file on top, then --set key.path=value overrides."""
import copy
import json
import os

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.default.json")


def deep_merge(base, over):
    out = copy.deepcopy(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def apply_overrides(cfg, items):
    """items: ['prune.min_opacity=0.02', 'write.formats=["ply","spz"]']. Values are parsed as JSON, else kept as text."""
    cfg = copy.deepcopy(cfg)
    for it in items or []:
        key, _, raw = it.partition("=")
        if not _:
            raise ValueError(f"override '{it}' is not key=value")
        try:
            val = json.loads(raw)
        except json.JSONDecodeError:
            val = raw
        node = cfg
        parts = key.split(".")
        for p in parts[:-1]:
            if not isinstance(node.get(p), dict):
                raise KeyError(f"override '{key}': '{p}' is not a section of the config")
            node = node[p]
        if parts[-1] not in node:
            raise KeyError(f"override '{key}': unknown setting (typo?)")
        node[parts[-1]] = val
    return cfg


def load_config(path=None, overrides=None):
    with open(DEFAULT_PATH, encoding="utf-8") as f:
        cfg = json.load(f)
    if path:
        with open(path, encoding="utf-8") as f:
            cfg = deep_merge(cfg, json.load(f))
    return apply_overrides(cfg, overrides)
