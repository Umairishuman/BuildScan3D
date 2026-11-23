"""v3 GPU compression engine (src/splat_compress/v3_gpu), run on CPU torch with synthetic splats.
Skipped where torch / plyfile are missing. GPU behaviour is not covered here (see PLAN.md test plan)."""
import importlib.util
import json
import os

import numpy as np
import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("plyfile")
from plyfile import PlyData, PlyElement  # noqa: E402

from splat_compress.v3_gpu import config as cfgmod  # noqa: E402
from splat_compress.v3_gpu import compress_gpu, pipeline, stages  # noqa: E402
from splat_compress.v3_gpu.splat_io import raw_bytes, read_ply, resolve_device, sh_degree_of, write_ply  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _v1():
    p = os.path.join(ROOT, "src", "splat_compress", "v1_ply_prune_sh_ksplat", "compress.py")
    spec = importlib.util.spec_from_file_location("v1_compress", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def make_ply(path, n=500, per_ch=15, seed=0, normals=True):
    rng = np.random.default_rng(seed)
    cols = [(c, rng.normal(size=n)) for c in "xyz"]
    if normals:
        cols += [(c, np.zeros(n)) for c in ("nx", "ny", "nz")]
    cols += [(f"f_dc_{i}", rng.normal(size=n)) for i in range(3)]
    cols += [(f"f_rest_{i}", rng.normal(size=n) * 0.1) for i in range(3 * per_ch)]
    cols += [("opacity", rng.normal(scale=3, size=n))]
    cols += [(f"scale_{i}", rng.normal(loc=-4, scale=1, size=n)) for i in range(3)]
    cols += [(f"rot_{i}", rng.normal(size=n)) for i in range(4)]
    arr = np.empty(n, dtype=[(c, "f4") for c, _ in cols])
    for c, v in cols:
        arr[c] = v
    PlyData([PlyElement.describe(arr, "vertex")]).write(str(path))
    return str(path)


@pytest.fixture
def cfg():
    return cfgmod.load_config(overrides=["device=cpu"])


def test_config_defaults_and_overrides():
    c = cfgmod.load_config(overrides=["prune.min_opacity=0.5", 'write.formats=["ply","spz"]'])
    assert c["prune"]["min_opacity"] == 0.5
    assert c["write"]["formats"] == ["ply", "spz"]
    assert c["sh_reduce"]["sh_degree"] == 1                      # untouched default
    with pytest.raises(KeyError):
        cfgmod.load_config(overrides=["prune.min_opacty=0.5"])   # typo is an error, not a silent no-op


def test_config_file_merges_over_defaults(tmp_path):
    f = tmp_path / "c.json"
    f.write_text(json.dumps({"prune": {"min_opacity": 0.2}}))
    c = cfgmod.load_config(str(f))
    assert c["prune"]["min_opacity"] == 0.2 and c["prune"]["max_scale_mult"] == 0.0


def test_ply_roundtrip(tmp_path):
    src = make_ply(tmp_path / "a.ply")
    s = read_ply(src)
    assert sh_degree_of(s) == 3 and s["rest"].shape == (500, 3, 15)
    out = tmp_path / "b.ply"
    write_ply(s, str(out))
    a, b = PlyData.read(src)["vertex"].data, PlyData.read(str(out))["vertex"].data
    assert a.dtype.names == b.dtype.names
    for n in a.dtype.names:
        np.testing.assert_array_equal(a[n], b[n])


def test_bad_sh_column_count_rejected(tmp_path):
    src = make_ply(tmp_path / "a.ply", per_ch=4)
    with pytest.raises(ValueError):
        read_ply(src)


def test_defaults_match_v1_compress(tmp_path, cfg):
    """v3 with default settings must keep the same splats and values as the v1 numpy script."""
    src = make_ply(tmp_path / "in.ply")
    rep, _ = pipeline.run(cfg, src, str(tmp_path / "out"))
    el, stats = _v1().compress(PlyData.read(src)["vertex"], min_opacity=0.05, sh_degree=1, max_scale_mult=0.0)
    v3 = PlyData.read(rep["outputs"]["ply"]["path"])["vertex"].data
    assert rep["output_splats"] == stats["kept"]
    assert v3.dtype.names == el.data.dtype.names
    for n in v3.dtype.names:
        np.testing.assert_allclose(v3[n], el.data[n], rtol=1e-6)
    assert os.path.exists(tmp_path / "out" / "report.json")


def test_prune_importance_quantile(cfg):
    s = {"xyz": torch.zeros(100, 3), "opacity": torch.full((100,), 5.0), "scale": torch.zeros(100, 3),
         "dc": torch.zeros(100, 3), "rest": torch.zeros(100, 3, 0), "rot": torch.zeros(100, 4), "normals": None}
    s["scale"][:, 0] = torch.linspace(-5, 0, 100)                 # volumes strictly increasing
    out, st = stages.prune(s, dict(min_opacity=0.0, max_scale_mult=0.0, importance_quantile=0.3), {})
    assert st["splats_out"] == 70
    assert out["scale"][:, 0].min() > s["scale"][29, 0]            # the 30 smallest are gone


def test_sh_reduce_degrees_and_normals(tmp_path):
    s = read_ply(make_ply(tmp_path / "a.ply"))
    for deg, per in ((0, 0), (1, 3), (2, 8), (3, 15)):
        out, _ = stages.sh_reduce(s, dict(sh_degree=deg, drop_normals=True), {})
        assert out["rest"].shape[2] == per and out["normals"] is None
    with pytest.raises(ValueError):
        stages.sh_reduce(s, dict(sh_degree=4, drop_normals=True), {})
    keep, _ = stages.sh_reduce(s, dict(sh_degree=1, drop_normals=False), {})
    assert keep["normals"] is not None


def test_kmeans_recovers_clusters():
    g = torch.Generator().manual_seed(0)
    centres = torch.tensor([[0.0, 0], [10, 0], [0, 10], [10, 10]])
    x = torch.cat([c + 0.05 * torch.randn(200, 2, generator=g) for c in centres])
    cent, idx = stages.kmeans(x, 4, 20, 128, g)
    assert float(((cent[idx] - x) ** 2).mean()) < 0.01             # each point sits on its own cluster


def test_vq_sh_reports_and_dequantises(tmp_path, cfg):
    s = read_ply(make_ply(tmp_path / "a.ply", n=2000))
    out, st = stages.vq_sh(s, dict(codebook_size=16, iters=5, chunk=300), dict(seed=0))
    assert out["rest"].shape == s["rest"].shape
    assert len(torch.unique(out["rest"].reshape(2000, -1), dim=0)) <= 16
    assert st["rest_bytes_packed"] < st["rest_bytes_before"]
    assert out["vq"]["indices"].shape == (2000,)


def test_vq_must_be_last(tmp_path, cfg):
    cfg["pipeline"] = ["vq_sh", "prune"]
    with pytest.raises(ValueError):
        pipeline.run(cfg, make_ply(tmp_path / "a.ply"), str(tmp_path / "o"))


def test_unknown_stage_and_format_rejected(tmp_path, cfg):
    src = make_ply(tmp_path / "a.ply")
    cfg["pipeline"] = ["nope"]
    with pytest.raises(ValueError):
        pipeline.run(cfg, src, str(tmp_path / "o"))
    cfg["pipeline"] = ["prune"]
    cfg["write"]["formats"] = ["gif"]
    with pytest.raises(ValueError):
        pipeline.run(cfg, src, str(tmp_path / "o"))


def test_ksplat_without_converter_fails_clearly(tmp_path, cfg):
    cfg["write"]["formats"] = ["ksplat"]
    with pytest.raises(ValueError, match="converter"):
        pipeline.run(cfg, make_ply(tmp_path / "a.ply"), str(tmp_path / "o"))


def test_cli_end_to_end(tmp_path, capsys):
    src = make_ply(tmp_path / "a.ply")
    assert compress_gpu.main([src, str(tmp_path / "o"), "--device", "cpu", "--set", "sh_reduce.sh_degree=0"]) == 0
    rep = json.load(open(tmp_path / "o" / "report.json"))
    assert rep["device"] == "cpu" and rep["outputs"]["ply"]["smaller_percent"] > 0
    assert "smaller" in capsys.readouterr().out


def test_cuda_requested_without_cuda_is_an_error():
    if torch.cuda.is_available():
        pytest.skip("this machine has CUDA")
    with pytest.raises(RuntimeError):
        resolve_device("cuda")


def test_raw_bytes_counts_float32(tmp_path):
    s = read_ply(make_ply(tmp_path / "a.ply", n=10))
    assert raw_bytes(s) == 10 * (3 + 3 + 3 + 45 + 1 + 3 + 4) * 4
