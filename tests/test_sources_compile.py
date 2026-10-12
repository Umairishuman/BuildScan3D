"""Every Python file in the repo must at least compile (catches syntax errors in scripts that need a GPU to run)."""
import os
import py_compile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _python_files():
    for top in ("src", "scratch", "tests"):
        for dirpath, _, names in os.walk(os.path.join(ROOT, top)):
            for n in names:
                if n.endswith(".py"):
                    yield os.path.join(dirpath, n)


@pytest.mark.parametrize("path", sorted(_python_files()), ids=lambda p: os.path.relpath(p, ROOT))
def test_file_compiles(path, tmp_path):
    py_compile.compile(path, cfile=str(tmp_path / "x.pyc"), doraise=True)
