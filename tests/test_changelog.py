"""The app changelog tool CD runs at every release (.github/android/changelog.py), and the changelog file itself."""
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("changelog", os.path.join(ROOT, ".github", "android", "changelog.py"))
changelog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(changelog)

SAMPLE = """# Changelog

Intro text.

## Unreleased

- New thing
- Fixed thing

## v0.3.6 · 2026-11-12

- USB upload
"""


def test_release_moves_unreleased_into_a_version():
    new, notes = changelog.release(SAMPLE, "0.3.7", "2026-11-13")
    assert notes == "- New thing\n- Fixed thing"
    assert new.index("## Unreleased") < new.index("## v0.3.7 · 2026-11-13") < new.index("## v0.3.6")
    assert changelog.notes(new, "0.3.7") == notes
    assert changelog.notes(new, "0.3.6") == "- USB upload"
    assert new.startswith("# Changelog\n\nIntro text.\n")
    # the new Unreleased section is empty
    _, secs = changelog._sections(new)
    assert secs[0][0] == "## Unreleased" and secs[0][1].strip() == ""


def test_release_twice_keeps_every_version():
    a, _ = changelog.release(SAMPLE, "0.3.7", "2026-11-13")
    b, n = changelog.release(a, "0.3.8", "2026-11-14")
    assert n == changelog.EMPTY
    for v in ("0.3.8", "0.3.7", "0.3.6"):
        assert f"## v{v}" in b
    assert b.count("## Unreleased") == 1


def test_release_refuses_an_existing_version():
    try:
        changelog.release(SAMPLE, "0.3.6", "2026-11-13")
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_release_without_unreleased_section():
    new, n = changelog.release("# Changelog\n\n## v0.1.0 · 2026-01-01\n\n- a\n", "0.1.1", "2026-01-02")
    assert n == changelog.EMPTY and "## Unreleased" in new and "## v0.1.1" in new and "## v0.1.0" in new


def test_notes_of_unknown_version():
    assert changelog.notes(SAMPLE, "9.9.9") == changelog.EMPTY


def test_repo_changelog_has_unreleased_and_current_version():
    path = os.path.join(ROOT, "android", "CHANGELOG.md")
    text = open(path, encoding="utf-8").read()
    assert "## Unreleased" in text
    gradle = open(os.path.join(ROOT, "android", "app", "build.gradle"), encoding="utf-8").read()
    import re
    current = re.search(r"versionName '([^']+)'", gradle).group(1)
    assert changelog.notes(text, current) != changelog.EMPTY, f"v{current} missing from android/CHANGELOG.md"
