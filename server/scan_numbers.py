"""Scan numbers: every recording in dataset/ gets a fixed number 1, 2, 3, ... in the order it arrived (D-065).

The register is dataset/.scan_numbers.tsv ("<number>\\t<folder name>" per line). It is the only source of the numbers:
a number never changes, even when a folder is modified later (a processing run changes its modification time, so
"newest by date" is not reliable). Folders not in the register yet (older recordings, folders copied in by hand) are
added on first sight, oldest first by creation time.

New uploads are saved as scan_<NNN>_<id> (e.g. scan_004_6de634cbb8b2) so the number is in the folder name too.
Recordings from before 2026-11-12 keep their names (scan_056fe94d3399 is #1): the records refer to them.

    python3 server/scan_numbers.py              # list: number, folder, newest last (registers unknown folders)
    python3 server/scan_numbers.py resolve 4    # -> dataset/scan_004_...   ("latest" = highest number)

Used by server/main.py (naming uploads) and scripts/buildscan (datasets, <scan> arguments). Standard library only.
"""
from __future__ import annotations

import os
import re
import sys
import uuid
from pathlib import Path

try:
    import fcntl  # Linux / macOS: lock the register while it is changed
except ImportError:  # Windows: no lock (one server, uploads rarely overlap)
    fcntl = None

REGISTER = ".scan_numbers.tsv"
NUMBERED = re.compile(r"^scan_(\d{3,})_([0-9a-f]+)$")


def _created(p: Path) -> float:
    st = p.stat()
    return getattr(st, "st_birthtime", 0) or st.st_mtime


class _Locked:
    def __init__(self, root: Path):
        self.path = root / REGISTER
        self.f = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.f = open(self.path, "a+", encoding="utf8")
        if fcntl:
            fcntl.flock(self.f, fcntl.LOCK_EX)
        self.f.seek(0)
        return self.f

    def __exit__(self, *exc):
        if fcntl:
            fcntl.flock(self.f, fcntl.LOCK_UN)
        self.f.close()


def _read(f) -> dict[str, int]:
    out: dict[str, int] = {}
    for line in f.read().splitlines():
        parts = line.strip().split("\t")
        if len(parts) == 2 and parts[0].isdigit():
            out[parts[1]] = int(parts[0])
    return out


def _register_unknown(root: Path, f, known: dict[str, int]) -> dict[str, int]:
    """Adds every folder of root that has no number yet (oldest first); returns the full register."""
    nxt = max(known.values(), default=0) + 1
    new = [p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".") and p.name not in known]
    new.sort(key=lambda p: (int(NUMBERED.match(p.name).group(1)) if NUMBERED.match(p.name) else 10**9, _created(p)))
    for p in new:
        m = NUMBERED.match(p.name)
        n = int(m.group(1)) if m and int(m.group(1)) not in known.values() else nxt
        known[p.name] = n
        f.write(f"{n}\t{p.name}\n")
        nxt = max(known.values()) + 1
    f.flush()
    return known


def numbers(root: str | os.PathLike) -> list[tuple[int, str]]:
    """[(number, folder name)] for every folder in root, oldest first; registers folders it has not seen."""
    root = Path(root)
    if not root.is_dir():
        return []
    with _Locked(root) as f:
        known = _register_unknown(root, f, _read(f))
    present = {p.name for p in root.iterdir() if p.is_dir()}
    return sorted((n, name) for name, n in known.items() if name in present)


def new_scan_dir(root: str | os.PathLike, job_id: str | None = None) -> tuple[Path, int, str]:
    """Reserves the next number for an upload: (folder path, number, job id). The folder is created."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    job_id = job_id or uuid.uuid4().hex[:12]
    with _Locked(root) as f:
        known = _register_unknown(root, f, _read(f))
        n = max(known.values(), default=0) + 1
        name = f"scan_{n:03d}_{job_id}"
        (root / name).mkdir()
        f.write(f"{n}\t{name}\n")
        f.flush()
    return root / name, n, job_id


def release(root: str | os.PathLike, name: str) -> None:
    """Gives a reserved number back (the upload into that folder failed and the folder was removed)."""
    root = Path(root)
    with _Locked(root) as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip() and ln.split("\t")[-1] != name]
        f.seek(0)
        f.truncate()
        f.write("".join(ln + "\n" for ln in lines))
        f.flush()


def number_of(root: str | os.PathLike, name: str) -> int | None:
    return dict((v, k) for k, v in numbers(root)).get(name)


def job_id_of(name: str) -> str:
    """Job id from a folder name: scan_004_6de634cbb8b2 -> 6de634cbb8b2; scan_056fe94d3399 -> 056fe94d3399."""
    m = NUMBERED.match(name)
    return m.group(2)[:12] if m else name.replace("scan_", "")[:12]


def resolve(root: str | os.PathLike, which: str) -> str | None:
    """'4', '#4', 'latest', or a folder name / path -> 'dataset/<folder>' style path, or None."""
    root = Path(root)
    rows = numbers(root)
    w = which.strip().lstrip("#")
    if w == "latest":
        return str(root / rows[-1][1]) if rows else None
    if w.isdigit():
        for n, name in rows:
            if n == int(w):
                return str(root / name)
        return None
    name = Path(w.rstrip("/")).name
    return str(root / name) if (root / name).is_dir() else None


def main(argv: list[str]) -> int:
    root = os.environ.get("BUILDSCAN_DATASET", "dataset")
    if len(argv) >= 2 and argv[0] == "resolve":
        r = resolve(root, argv[1])
        if r is None:
            return 1
        print(r)
        return 0
    for n, name in numbers(root):
        print(f"{n}\t{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
