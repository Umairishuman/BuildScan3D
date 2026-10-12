"""Checks that the Android app we ship is the app we expect. Used by the CI/CD workflows and by the tests.

    python .github/android/check_apk.py manifest <AndroidManifest.xml>
        static check of the source manifest (no Android SDK needed)
    python .github/android/check_apk.py apk --manifest <apkanalyzer manifest print output> --signer <apksigner output> --apk <file.apk>
        checks the built APK: package, minimum Android version, permissions, features, activities, launcher, signing key, size

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


# ---------------------------------------------------------------- manifest (source file or the one inside the APK)
def _parse_manifest_text(text):
    """Parse manifest XML. `apkanalyzer` can leave out the xmlns:android declaration, so add it when missing."""
    if "xmlns:android" not in text:
        text = text.replace("<manifest", '<manifest xmlns:android="http://schemas.android.com/apk/res/android"', 1)
    return ET.fromstring(text)


def check_manifest_text(text, expect, from_apk=False):
    """Problems found in a manifest (empty list = fine). from_apk=True also checks the minimum Android version."""
    problems = []
    try:
        root = _parse_manifest_text(text)
    except ET.ParseError as e:
        return [f"could not read the manifest: {e}"]
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
    if from_apk:
        sdk = next(iter(root.iter("uses-sdk")), None)
        min_sdk = sdk.get(ANDROID + "minSdkVersion") if sdk is not None else None
        if min_sdk is None or not str(min_sdk).isdigit() or int(min_sdk) < expect["min_sdk_at_least"]:
            problems.append(f"minimum Android version is {min_sdk}, ARCore needs at least {expect['min_sdk_at_least']}")
    return problems


def check_manifest(xml_path, expect):
    """Static check of the AndroidManifest.xml in the repository."""
    with open(xml_path, encoding="utf8") as f:
        return check_manifest_text(f.read(), expect)


# ---------------------------------------------------------------- built APK
def parse_signer_sha256(text):
    """SHA-256 of the signing certificate from `apksigner verify --print-certs`, lower case without colons."""
    m = re.search(r"certificate SHA-256 digest:\s*([0-9a-fA-F:]+)", text)
    return m.group(1).replace(":", "").lower() if m else None


def check_apk(manifest_text, signer_text, size_bytes, expect):
    """manifest_text = `apkanalyzer manifest print app.apk`, signer_text = `apksigner verify --print-certs app.apk`."""
    problems = check_manifest_text(manifest_text, expect, from_apk=True)
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
    pa.add_argument("--manifest", required=True); pa.add_argument("--signer", required=True); pa.add_argument("--apk", required=True)
    args = ap.parse_args(argv)
    expect = load_expectations()
    if args.cmd == "manifest":
        problems = check_manifest(args.path, expect)
    else:
        problems = check_apk(open(args.manifest, encoding="utf8").read(), open(args.signer, encoding="utf8").read(),
                             os.path.getsize(args.apk), expect)
    for p in problems:
        print(f"::error::{p}")
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
