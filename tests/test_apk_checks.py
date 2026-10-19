"""The APK/manifest checker used by CI and CD (.github/android/check_apk.py), plus consistency of the files it relies on.

The pipeline gets the APK's manifest from `apkanalyzer manifest print` and the signing certificate from
`apksigner verify --print-certs`. The samples below have the same shape as that output, so the checks are
tested here without an Android SDK."""
import importlib.util
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANDROID_DIR = os.path.join(ROOT, ".github", "android")
MANIFEST = os.path.join(ROOT, "googleARCore", "samples", "hello_ar_java", "app", "src", "main", "AndroidManifest.xml")
NS = "http://schemas.android.com/apk/res/android"

spec = importlib.util.spec_from_file_location("check_apk", os.path.join(ANDROID_DIR, "check_apk.py"))
check_apk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_apk)

EXPECT = check_apk.load_expectations()
GOOD_SHA = EXPECT["signing_sha256"]
NL = chr(10)

SIGNER = (
    "Signer #1 certificate DN: CN=Android Debug, O=Android, C=US" + NL
    + "Signer #1 certificate SHA-256 digest: " + GOOD_SHA + NL
    + "Signer #1 certificate SHA-1 digest: 0000000000000000000000000000000000000000" + NL
)
SIZE = 3_670_000


def apk_manifest(min_sdk="24", with_xmlns=True):
    """What `apkanalyzer manifest print` shows: the app's real manifest plus the <uses-sdk> element the build adds."""
    ET.register_namespace("android", NS)
    root = ET.parse(MANIFEST).getroot()
    if min_sdk is not None:
        sdk = ET.Element("uses-sdk")
        sdk.set("{%s}minSdkVersion" % NS, min_sdk)
        sdk.set("{%s}targetSdkVersion" % NS, "36")
        root.insert(0, sdk)
    text = ET.tostring(root, encoding="unicode")
    if not with_xmlns:
        text = text.replace(' xmlns:android="%s"' % NS, "")
    return text


def problems(manifest=None, signer=SIGNER, size=SIZE, expect=EXPECT):
    return check_apk.check_apk(apk_manifest() if manifest is None else manifest, signer, size, expect)


# ---------------------------------------------------------------- the built APK
def test_a_correct_apk_has_no_problems():
    assert problems() == []


def test_apkanalyzer_output_without_the_xmlns_declaration_still_parses():
    assert problems(manifest=apk_manifest(with_xmlns=False)) == []


def test_missing_min_sdk_is_reported():
    assert any("minimum Android version" in p for p in problems(manifest=apk_manifest(min_sdk=None)))


def test_min_sdk_below_what_arcore_needs_is_reported():
    assert any("minimum Android version" in p for p in problems(manifest=apk_manifest(min_sdk="21")))


def test_wrong_package_name_is_reported():
    bad = apk_manifest().replace('package="' + EXPECT["package"] + '"', 'package="com.example.other"', 1)
    assert any("package" in p for p in problems(manifest=bad))


def test_missing_permission_is_reported():
    bad = apk_manifest().replace("android.permission.INTERNET", "android.permission.NOTHING")
    assert any("android.permission.INTERNET" in p for p in problems(manifest=bad))


def test_missing_ar_feature_is_reported():
    bad = apk_manifest().replace("android.hardware.camera.ar", "android.hardware.camera.nothing")
    assert any("camera.ar" in p for p in problems(manifest=bad))


def test_missing_processing_screen_is_reported():
    bad = apk_manifest().replace("helloar.ProcessingActivity", "helloar.RenamedActivity")
    assert any("ProcessingActivity" in p for p in problems(manifest=bad))


def test_apk_signed_with_a_different_key_is_reported_and_explains_why_it_matters():
    other = SIGNER.replace(GOOD_SHA, "ab" * 32)
    out = problems(signer=other)
    assert len(out) == 1 and "NOT signed with the shared debug key" in out[0] and "recordings" in out[0]


def test_signer_digest_with_colons_and_capitals_still_matches():
    colon = ":".join(GOOD_SHA[i:i + 2].upper() for i in range(0, 64, 2))
    assert problems(signer="Signer #1 certificate SHA-256 digest: " + colon + NL) == []


def test_unsigned_apk_is_reported():
    assert any("signing certificate" in p for p in problems(signer="DOES NOT VERIFY" + NL))


@pytest.mark.parametrize("size", [100_000, 400_000_000])
def test_implausible_apk_size_is_reported(size):
    assert any("size" in p for p in problems(size=size))


def test_empty_or_garbage_tool_output_does_not_crash_the_checker():
    for manifest, signer in (("", ""), ("not xml at all", "x"), ("<manifest", SIGNER)):
        out = problems(manifest=manifest, signer=signer)
        assert out and all(isinstance(p, str) for p in out)


def test_command_line_apk_check(tmp_path):
    m, sg, apk = tmp_path / "m.xml", tmp_path / "signer.txt", tmp_path / "app.apk"
    m.write_text(apk_manifest(), encoding="utf8")
    sg.write_text(SIGNER, encoding="utf8")
    apk.write_bytes(bytes(3_000_000))
    assert check_apk.main(["apk", "--manifest", str(m), "--signer", str(sg), "--apk", str(apk)]) == 0
    sg.write_text(SIGNER.replace(GOOD_SHA, "cd" * 32), encoding="utf8")
    assert check_apk.main(["apk", "--manifest", str(m), "--signer", str(sg), "--apk", str(apk)]) == 1


# ---------------------------------------------------------------- the source manifest (static)
def test_the_real_manifest_passes_the_checks():
    assert check_apk.check_manifest(MANIFEST, EXPECT) == []


@pytest.mark.parametrize("old,new,needle", [
    ("android.permission.INTERNET", "android.permission.NOTHING", "android.permission.INTERNET"),
    ("helloar.ProcessingActivity", "helloar.RenamedActivity", "ProcessingActivity"),
    ('com.google.ar.core" android:value', 'com.example.other" android:value', "meta-data"),
    ("android.hardware.camera.ar", "android.hardware.camera.nothing", "camera.ar"),
])
def test_manifest_problems_are_found(tmp_path, old, new, needle):
    text = open(MANIFEST, encoding="utf8").read()
    assert old in text
    broken = tmp_path / "AndroidManifest.xml"
    broken.write_text(text.replace(old, new), encoding="utf8")
    assert any(needle in p for p in check_apk.check_manifest(str(broken), EXPECT))


def test_two_launcher_activities_are_reported(tmp_path):
    tree = ET.parse(MANIFEST)
    processing = next(a for a in tree.getroot().iter("activity")
                      if a.get("{%s}name" % NS, "").endswith("ProcessingActivity"))
    intent = ET.SubElement(processing, "intent-filter")
    ET.SubElement(intent, "category").set("{%s}name" % NS, "android.intent.category.LAUNCHER")
    broken = tmp_path / "AndroidManifest.xml"
    tree.write(broken, encoding="utf-8", xml_declaration=True)
    assert any("launcher" in p for p in check_apk.check_manifest(str(broken), EXPECT))


# ---------------------------------------------------------------- files the pipeline depends on
def test_the_shared_keystore_is_committed_and_matches_the_expected_fingerprint():
    keystore = os.path.join(ANDROID_DIR, "debug.keystore")
    assert os.path.exists(keystore)
    keytool = shutil.which("keytool")
    if keytool is None:
        pytest.skip("keytool (Java) is not installed here")
    out = subprocess.run([keytool, "-list", "-v", "-keystore", keystore, "-storepass", "android",
                          "-alias", "androiddebugkey"], capture_output=True, text=True).stdout
    line = next(row for row in out.splitlines() if row.strip().startswith("SHA256:"))
    assert line.split("SHA256:")[1].strip().replace(":", "").lower() == GOOD_SHA


def test_expectation_file_is_complete():
    for key in ("package", "min_sdk_at_least", "launchable_activity", "required_permissions",
                "required_activities", "required_features", "signing_sha256", "min_apk_mb", "max_apk_mb"):
        assert key in EXPECT
    assert len(EXPECT["signing_sha256"]) == 64


def test_command_line_manifest_check_exit_codes(tmp_path):
    assert check_apk.main(["manifest", MANIFEST]) == 0
    broken = tmp_path / "m.xml"
    broken.write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="x"/>')
    assert check_apk.main(["manifest", str(broken)]) == 1
