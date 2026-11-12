"""App changelog for releases (android/CHANGELOG.md), used by CD (.github/workflows/cd.yml).

  python .github/android/changelog.py release android/CHANGELOG.md 0.3.7 2026-11-13   # at an auto-bump
  python .github/android/changelog.py notes   android/CHANGELOG.md 0.3.7              # at a tag push

`release` turns the "## Unreleased" section into "## v<version> · <date>", puts a new empty "## Unreleased" above it,
rewrites the file and prints the section's notes. `notes` prints the notes of an existing version. The printed notes
become the GitHub release body, which the app shows in its update dialog and after an update ("What's new").
"""
import re
import sys

UNRELEASED = "## Unreleased"
EMPTY = "No changes listed for this version."


def _sections(text):
    """[(heading line, body)] for every '## ' section, in file order, plus the text before the first one."""
    parts = re.split(r"(?m)^(## .*)$", text)
    head, rest = parts[0], parts[1:]
    return head, [(rest[i].strip(), rest[i + 1]) for i in range(0, len(rest), 2)]


def _clean(body):
    body = body.strip("\n")
    return body.strip() if body.strip() else ""


def release(text, version, date):
    """Return (new changelog text, notes) after releasing the Unreleased section as v<version>."""
    head, secs = _sections(text)
    if any(h.split(" ")[1] == f"v{version}" for h, _ in secs if len(h.split(" ")) > 1):
        raise ValueError(f"v{version} is already in the changelog")
    notes = ""
    out = []
    found = False
    for h, body in secs:
        if h == UNRELEASED and not found:
            found = True
            notes = _clean(body)
            out.append((UNRELEASED, "\n\n"))
            out.append((f"## v{version} · {date}", "\n\n" + (notes or EMPTY) + "\n\n"))
        else:
            out.append((h, body))
    if not found:  # no Unreleased section: add both at the top
        out.insert(0, (f"## v{version} · {date}", "\n\n" + EMPTY + "\n\n"))
        out.insert(0, (UNRELEASED, "\n\n"))
    new = head.rstrip("\n") + "\n\n" + "".join(h + (b if b.startswith("\n") else "\n" + b) for h, b in out)
    return new.rstrip("\n") + "\n", notes or EMPTY


def notes(text, version):
    """Notes of v<version>, or EMPTY when the version is not in the changelog."""
    _, secs = _sections(text)
    for h, body in secs:
        if h.startswith(f"## v{version} ") or h == f"## v{version}":
            return _clean(body) or EMPTY
    return EMPTY


def main(argv):
    if len(argv) >= 4 and argv[1] == "release":
        path, version = argv[2], argv[3]
        date = argv[4] if len(argv) > 4 else __import__("datetime").date.today().isoformat()
        text = open(path, encoding="utf-8").read()
        new, n = release(text, version, date)
        open(path, "w", encoding="utf-8").write(new)
        print(n)
        return 0
    if len(argv) == 4 and argv[1] == "notes":
        print(notes(open(argv[2], encoding="utf-8").read(), argv[3]))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
