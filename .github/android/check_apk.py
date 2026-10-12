"""Checks that the Android app we ship is the app we expect. Used by the CI/CD workflows and by the tests.

    python .github/android/check_apk.py manifest <AndroidManifest.xml>
        static check of the source manifest (no Android SDK needed)
    python .github/android/check_apk.py apk --badging <aapt2 dump badging output> --signer <apksigner output> --apk <file.apk>
        checks the built APK: package, minimum Android version, permissions, launcher, signing key, size

The expected values live in apk_expectations.json next to this file. Exit code 1 and a list of problems if
anything is off, so the pipeline fails with a readable reason instead of shipping a broken APK.
"""
import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ANDROID = "{http://schemas.android.com/apk/res/android}"


def load_expectations(path=None):
    with open(path or os.path.join(HERE, "apk_expectations.json"), encoding="utf8") as f:
        return json.load(f)


# ---------------------------------------------------------------- source manifest
def check_manifest(xml_path, expect):
    """Problems found in the AndroidManifest.xml in the repository (empty list = fine)."""
    problems = []
    root = ET.parse(xml_path).getroot()
    if root.get("package") != expect["package"]:
        problems.append(f"manifest package is {root.get('package')!r}, expected {expect['package']!r}")
    perms = {e.get(ANDROID + "name") for e in root.iter("uses-permission")}
    for p in expect["required_permissions"]:
        if p not in perms:
            problems.append(f"permission missing from the manifest: {p}")
    feats = {e.get(ANDROID + "name") for e in root.iter("uses-feature")}
    for ft in expect["required_features"]:
        if ft not in feats:
            problems.append(f"uses-feature missing from the manifest: {ft}")
    activities = {e.get(ANDROID + "name") for e in root.iter("activity")}
    for a in expect["required_activities"]:
        if a not in activities:
            problems.append(f"activity not declared in the manifest: {a}")
    metas = {e.get(ANDROID + "name"): e.get(ANDROID + "value") for e in root.iter("meta-data")}
    if "com.google.ar.core" not in metas:
        problems.append("ARCore meta-data (com.google.ar.core) is missing from the manifest")
    launchers = [a.get(ANDROID + "name") for a in root.iter("activity")
                 if any(c.get(ANDROID + "name") == "android.intent.category.LAUNCHER" for c in a.iter("category"))]
    if launchers != [expect["launchable_activity"]]:
        problems.append(f"launcher activity is {launchers}, expected [{expect['launchable_activity']!r}]")
    return problems


# ---------------------------------------------------------------- built APK
def parse_badging(text):
    """Pull the facts we care about out of `aapt2 dump badging` output."""
    info = {"permissions": set(), "features": set()}
    m = re.search(r"^package: name='([^']+)'(?: versionCode='([^']*)')?(?: versionName='([^']*)')?", text, re.M)
    if m:
        info["package"], info["version_code"], info["version_name"] = m.group(1), m.group(2), m.group(3)
    m = re.search(r"^sdkVersion:'(\d+)'", text, re.M)
    info["min_sdk"] = int(m.group(1)) if m else None
    m = re.search(r"^targetSdkVersion:'(\d+)'", text, re.M)
    info["target_sdk"] = int(m.group(1)) if m else None
    info["permissions"] = set(re.findall(r"^uses-permission: name='([^']+)'", text, re.M))
    info["features"] = set(re.findall(r"^uses-feature(?:-not-required)?: name='([^']+)'", text, re.M))
    m = re.search(r"^launchable-activity: name='([^']+)'", text, re.M)
    info["launcher"] = m.group(1) if m else None
    return info


def parse_signer_sha256(text):
    """SHA-256 of the signing certificate from `apksigner verify --print-certs`, lower case without colons."""
    m = re.search(r"certificate SHA-256 digest:\s*([0-9a-fA-F:]+)", text)
    return m.group(1).replace(":", "").lower() if m else None


def check_apk(badging_text, signer_text, size_bytes, expect):
    problems = []
    info = parse_badging(badging_text)
    if info.get("package") != expect["package"]:
        problems.append(f"APK package is {info.get('package')!r}, expected {expect['package']!r}")
    if info["min_sdk"] is None or info["min_sdk"] < expect["min_sdk_at_least"]:
        problems.append(f"minimum Android version is {info['min_sdk']}, ARCore needs at least {expect['min_sdk_at_least']}")
    for p in expect["required_permissions"]:
        if p not in info["permissions"]:
            problems.append(f"APK is missing permission {p}")
    for ft in expect["required_features"]:
        if ft not in info["features"]:
            problems.append(f"APK is missing uses-feature {ft}")
    if info["launcher"] != expect["launchable_activity"]:
        problems.append(f"APK launcher is {info['launcher']!r}, expected {expect['launchable_activity']!r}")
    sig = parse_signer_sha256(signer_text)
    if sig is None:
        problems.append("could not read the signing certificate (is the APK signed?)")
    elif sig != expect["signing_sha256"].lower():
        problems.append("APK is NOT signed with the shared debug key: phones would refuse to update over the previous "
                        f"build and the app's recordings would be lost (got {sig}, expected {expect['signing_sha256']})")
    mb = size_bytes / 1e6
    if not expect["min_apk_mb"] <= mb <= expect["max_apk_mb"]:
        problems.append(f"APK size {mb:.1f} MB is outside the expected {expect['min_apk_mb']}-{expect['max_apk_mb']} MB")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    pm = sub.add_parser("manifest"); pm.add_argument("path")
    pa = sub.add_parser("apk")
    pa.add_argument("--badging", required=True); pa.add_argument("--signer", required=True); pa.add_argument("--apk", required=True)
    args = ap.parse_args(argv)
    expect = load_expectations()
    if args.cmd == "manifest":
        problems = check_manifest(args.path, expect)
    else:
        problems = check_apk(open(args.badging, encoding="utf8").read(), open(args.signer, encoding="utf8").read(),
                             os.path.getsize(args.apk), expect)
    for p in problems:
        print(f"::error::{p}")
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
