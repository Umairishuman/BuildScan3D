"""plan_export.py on a synthetic 4 x 3 m room with one doorway from the wall gaps (#12)."""
import json
import math
import os
import subprocess
import sys

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "src", "arcore3dgs", "plan_export.py")


def layout(tilt_deg=0.0):
    """4 x 3 m room in world x / z; the last wall can be turned a little to test --square."""
    t = math.radians(tilt_deg)
    p = [[0, 0], [4, 0], [4, 3], [0, 3]]
    walls = []
    for k in range(4):
        a, b = p[k], p[(k + 1) % 4]
        walls.append(dict(id=k, p0=a, p1=b, length=math.dist(a, b), normal=[0, 0], corners=2, openings=[]))
    walls[0]["openings"] = [dict(kind="doorway", along=1.0, width=0.9, bottom=0.0, top=2.1)]
    if tilt_deg:                                              # wall 3 from (0, 3) to (0, 0), slightly rotated
        walls[3]["p1"] = [3 * math.sin(t), 3 - 3 * math.cos(t)]
    corners = [dict(xz=p[(k + 1) % 4], walls=[k, (k + 1) % 4], angle=90.0) for k in range(4)]
    return dict(height=2.6, floor_y=0, ceiling_y=2.6, open_top=False, room_closed=True, warnings=[], walls=walls,
                corners=corners)


def run(tmp_path, lay, *extra):
    lp = tmp_path / "layout.json"
    lp.write_text(json.dumps(lay))
    subprocess.run([sys.executable, SCRIPT, "--layout", str(lp), "--out", str(tmp_path), "--title", "test", *extra],
                   check=True, capture_output=True)
    suffix = "_square" if "--square" in extra else ""
    return json.loads((tmp_path / f"plan{suffix}.json").read_text()), (tmp_path / f"plan{suffix}.dxf").read_text()


def test_walls_and_doorway(tmp_path):
    plan, dxf = run(tmp_path, layout())
    assert sorted(round(w["length"], 2) for w in plan["walls"]) == [3.0, 3.0, 4.0, 4.0]
    assert [i["cls"] for i in plan["items"]] == ["doorway"] and abs(plan["items"][0]["width"] - 0.9) < 1e-6
    assert plan["size"] == [4.0, 3.0] and plan["room_closed"] is True
    assert dxf.startswith("0\nSECTION\n2\nENTITIES") and dxf.rstrip().endswith("EOF")
    assert dxf.count("\nLINE\n") == 5                          # 4 walls + 1 opening
    assert (tmp_path / "plan.svg").read_text().startswith("<svg")


def test_square_turns_a_slightly_off_wall(tmp_path):
    plan, _ = run(tmp_path, layout(tilt_deg=2.0), "--square")
    assert plan["squared"] is True and list(plan["turned_walls_deg"]) == ["3"]
    a, b = plan["walls"][3]["p0"], plan["walls"][3]["p1"]
    assert abs(a[0] - b[0]) < 1e-6 or abs(a[1] - b[1]) < 1e-6    # now axis-aligned
