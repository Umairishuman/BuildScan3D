"""The APK/manifest checker used by CI and CD (.github/android/check_apk.py), plus consistency of the files it relies on.

The sample `aapt2 dump badging` and `apksigner` texts below are shaped like the real tool output, so the
parsing is tested here without an Android SDK."""
import copy
import importlib.util
import os
import shutil
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANDROID_DIR = os.path.join(ROOT, ".github", "android")
MANIFEST = os.path.join(ROOT, "googleARCore", "samples", "hello_ar_java", "app", "src", "main", "AndroidManifest.xml")

spec = importlib.util.spec_from_file_location("check_apk", os.path.join(ANDROID_DIR, "check_apk.py"))
check_apk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_apk)

EXPECT = check_apk.load_expectations()
GOOD_SHA = EXPECT["signing_sha256"]

BADGING = """package: name='com.google.ar.core.examples.java.helloar' versionCode='1' versionName='1.0' platformBuildVersionCode='36' compileSdkVersion='36'
sdkVersion:'24'
targetSdkVersion:'36'
uses-permission: name='android.permission.CAMERA'
uses-permission: name='android.permission.INTERNET'
uses-permission: name='android.permission.VIBRATE'
uses-feature: name='android.hardware.camera'
uses-feature: name='android.hardware.camera.ar'
uses-feature: name='android.hardware.opengles.version' reqGlEsVersion='0x20000'
application-label:'BuildScan'
launchable-activity: name='com.google.ar.core.examples.java.helloar.HelloArActivity'  label='' icon=''
"""
SIGNER = f"""Signer #1 certificate DN: CN=Android Debug, O=Android, C=US
Signer #1 certificate SHA-256 digest: {GOOD_SHA}
Signer #1 certificate SHA-1 digest: 0000000000000000000000000000000000000000
"""
SIZE = 3_670_000


def problems(badging=BADGING, signer=SIGNER, size=SIZE, expect=EXPECT):
    return check_apk.check_apk(badging, signer, size, expect)


# ---------------------------------------------------------------- the built APK
def test_a_correct_apk_has_no_problems():
    assert problems() == []


def test_parse_badging_reads_the_important_facts():
    info = check_apk.parse_badging(BADGING)
    assert info["package"] == EXPECT["package"] and info["min_sdk"] == 24 and info["target_sdk"] == 36
    assert {"android.permission.CAMERA", "android.permission.INTERNET"} <= info["permissions"]
    assert "android.hardware.camera.ar" in info["features"]
    assert info["launcher"] == EXPECT["launchable_activity"]


def test_wrong_package_name_is_reported():
    assert any("package" in p for p in problems(badging=BADGING.replace("helloar'", "other'", 1)))


def test_min_sdk_below_what_arcore_needs_is_reported():
    assert any("minimum Android version" in p for p in problems(badging=BADGING.replace("sdkVersion:'24'", "sdkVersion:'21'")))


def test_missing_permission_is_reported():
    bad = BADGING.replace("uses-permission: name='android.permission.INTERNET'\n", "")
    assert any("android.permission.INTERNET" in p for p in problems(badging=bad))


def test_missing_ar_feature_is_reported():
    bad = BADGING.replace("uses-feature: name='android.hardware.camera.ar'\n", "")
    assert any("camera.ar" in p for p in problems(badging=bad))


def test_wrong_launcher_is_reported():
    bad = BADGING.replace("HelloArActivity", "ProcessingActivity")
    assert any("launcher" in p for p in problems(badging=bad))


def test_apk_signed_with_a_different_key_is_reported_and_explains_why_it_matters():
    other = SIGNER.replace(GOOD_SHA, "ab" * 32)
    out = problems(signer=other)
    assert len(out) == 1 and "NOT signed with the shared debug key" in out[0] and "recordings" in out[0]


def test_signer_digest_with_colons_and_capitals_still_matches():
    colon = ":".join(GOOD_SHA[i:i + 2].upper() for i in range(0, 64, 2))
    assert problems(signer=f"Signer #1 certificate SHA-256 digest: {colon}\n") == []


def test_unsigned_apk_is_reported():
    assert any("signing certificate" in p for p in problems(signer="DOES NOT VERIFY\n"))


@pytest.mark.parametrize("size", [100_000, 400_000_000])
def test_implausible_apk_size_is_reported(size):
    assert any("size" in p for p in problems(size=size))


def test_empty_tool_output_does_not_crash_the_checker():
    out = problems(badging="", signer="")
    assert out and all(isinstance(p, str) for p in out)


# ---------------------------------------------------------------- the source manifest (static)
def test_the_real_manifest_passes_the_checks():
    assert check_apk.check_manifest(MANIFEST, EXPECT) == []


@pytest.mark.parametrize("old,new,needle", [
    ("android.permission.INTERNET", "android.permission.NOTHING", "android.permission.INTERNET"),
    ("helloar.ProcessingActivity", "helloar.RenamedActivity", "ProcessingActivity"),
    ("com.google.ar.core\" android:value", "com.example.other\" android:value", "meta-data"),
    ("android.hardware.camera.ar", "android.hardware.camera.nothing", "camera.ar"),
])
def test_manifest_problems_are_found(tmp_path, old, new, needle):
    text = open(MANIFEST, encoding="utf8").read()
    assert old in text
    broken = tmp_path / "AndroidManifest.xml"
    broken.write_text(text.replace(old, new), encoding="utf8")
    assert any(needle in p for p in check_apk.check_manifest(str(broken), EXPECT))


def test_two_launcher_activities_are_reported(tmp_path):
    import xml.etree.ElementTree as ET
    ns = "{http://schemas.android.com/apk/res/android}"
    tree = ET.parse(MANIFEST)
    processing = next(a for a in tree.getroot().iter("activity")
                      if a.get(ns + "name", "").endswith("ProcessingActivity"))
    intent = ET.SubElement(processing, "intent-filter")
    ET.SubElement(intent, "category").set(ns + "name", "android.intent.category.LAUNCHER")
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
    line = next(l for l in out.splitlines() if l.strip().startswith("SHA256:"))
    assert line.split("SHA256:")[1].strip().replace(":", "").lower() == GOOD_SHA


def test_expectation_file_is_complete():
    for key in ("package", "min_sdk_at_least", "launchable_activity", "required_permissions",
                "required_activities", "required_features", "signing_sha256", "min_apk_mb", "max_apk_mb"):
        assert key in EXPECT
    assert len(EXPECT["signing_sha256"]) == 64
    assert copy.deepcopy(EXPECT) == EXPECT


def test_command_line_exit_codes(tmp_path):
    assert check_apk.main(["manifest", MANIFEST]) == 0
    broken = tmp_path / "m.xml"
    broken.write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="x"/>')
    assert check_apk.main(["manifest", str(broken)]) == 1
