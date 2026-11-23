"""src/arcore3dgs/tape_check.py: model vs tape table (COMPLETION_PLAN E2, NFR6)."""
import json

import pytest

import tape_check as tc

LAYOUT = {"height": 2.7, "dimensions": [{"walls": [0, 2], "distance": 4.4}, {"walls": [1, 3], "distance": 6.6}]}


def test_layout_values_take_the_larger_distance_as_length():
    assert tc.layout_values(LAYOUT) == {"room_length": 6.6, "room_width": 4.4, "height": 2.7}


def test_layout_values_skip_a_missing_ceiling():
    assert "height" not in tc.layout_values({"height": float("nan"), "dimensions": []})


def test_readings_accept_several_values():
    assert tc.readings("2.71;2.72; 2.73") == [2.71, 2.72, 2.73]
    with pytest.raises(ValueError):
        tc.readings(" ")


def test_compare_uses_layout_and_manual_values():
    rows = [dict(item="len", kind="room_length", tape_m="6.70", model_m=""),
            dict(item="h", kind="height", tape_m="2.69;2.71", model_m=""),
            dict(item="table", kind="manual", tape_m="1.750", model_m="1.748"),
            dict(item="door", kind="manual", tape_m="0.9", model_m="")]
    r = {x["item"]: x for x in tc.compare(rows, LAYOUT)}
    assert r["len"]["error_m"] == pytest.approx(-0.10)
    assert r["h"]["tape"] == pytest.approx(2.70) and r["h"]["tape_spread"] == pytest.approx(0.02)
    assert r["table"]["error_pct"] == pytest.approx(-0.002 / 1.75 * 100)
    assert "skipped" in r["door"]


def test_summary_checks_nfr6():
    res = [dict(error_m=-0.1, error_pct=-1.5), dict(error_m=0.4, error_pct=6.0)]
    s = tc.summary(res)
    assert s["n"] == 2 and s["max_abs_pct"] == 6.0 and s["nfr6_met"] is False
    assert tc.summary([dict(error_m=0.01, error_pct=0.5)])["nfr6_met"] is True
    assert tc.summary([dict(item="x", skipped="no")]) == {"n": 0}


def test_main_writes_json(tmp_path):
    (tmp_path / "tape.csv").write_text("item,kind,tape_m,model_m,note\nlen,room_length,6.7,,\n", encoding="utf-8")
    (tmp_path / "layout.json").write_text(json.dumps(LAYOUT), encoding="utf-8")
    assert tc.main(["--tape", str(tmp_path / "tape.csv"), "--layout", str(tmp_path / "layout.json"),
                    "--out", str(tmp_path / "o.json")]) == 0
    assert json.load(open(tmp_path / "o.json"))["summary"]["n"] == 1
