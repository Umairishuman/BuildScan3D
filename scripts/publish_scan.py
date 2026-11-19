#!/usr/bin/env python3
"""Publish a processed scan's web bundle to the R2 bucket behind the deployed site (D-076, issue #29).

Uploads prototype/web-ui/public/scans/<capture>_<tag>/ (scan.json, *.spz, mesh.glb) plus the run's layout
plan.png to scans/<owner>/<capture>_<tag>/ and adds the bundle to scans/<owner>/index.json, which the site's
/api/scans reads (prototype/web-ui/src/lib/remoteBundles.ts). Every key it writes is under its own owner's
prefix, so two people never overwrite each other's scans or list; only owners.json is shared (an owner is added
to it once). Unpublishing moves the files to archive/scans/<owner>/... in the bucket (never deletes, D-049).

Runs on Linux and Windows (Python 3.9+; `pip install boto3` for the R2 target). Settings from the repo's .env:
  R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET   the bucket and an Object Read & Write token
  PUBLISH_OWNER (e.g. umair), PUBLISH_OWNER_NAME (e.g. Umair)        whose scans these are

  python scripts/publish_scan.py publish 7 r1119c [--room "Site office"] [--dry-run]
  python scripts/publish_scan.py unpublish 7 r1119c
  python scripts/publish_scan.py list
  ... --target dir:<folder>   write the same layout into a local folder instead of R2 (tests)

BUILDSCAN_ROOT=<repo> reads dataset/ and the bundles from another checkout.
<scan> is a scan number (dataset/.scan_numbers.tsv), a capture folder name or a path to it.
"""
import argparse
import datetime as dt
import json
import mimetypes
import os
import re
import shutil
import sys
from pathlib import Path

REPO = Path(os.environ.get("BUILDSCAN_ROOT") or Path(__file__).resolve().parent.parent)  # override: tests from a worktree
SCANS_DIR = REPO / "prototype" / "web-ui" / "public" / "scans"
DATASET = REPO / "dataset"
SAFE_OWNER = re.compile(r"^[a-z0-9][a-z0-9-]{0,31}$")
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
TYPES = {".spz": "application/octet-stream", ".glb": "model/gltf-binary", ".json": "application/json",
         ".png": "image/png", ".jpg": "image/jpeg"}
FILE_CACHE = "public, max-age=300"       # bundle files: a re-publish of the same run shows within minutes
INDEX_CACHE = "no-cache"                 # indexes: always revalidated


def die(msg):
    sys.exit(f"publish_scan: {msg}")


def load_env():
    env = {}
    f = REPO / ".env"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    env.update({k: v for k, v in os.environ.items() if k.startswith(("R2_", "PUBLISH_"))})
    return env


# ---------------------------------------------------------------- stores (R2 or a local folder with the same keys)
class DirStore:
    def __init__(self, root):
        self.root = Path(root)

    def _p(self, key):
        return self.root / key

    def put_file(self, key, path, ctype, cache):
        self._p(key).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, self._p(key))

    def put_json(self, key, obj):
        self._p(key).parent.mkdir(parents=True, exist_ok=True)
        self._p(key).write_text(json.dumps(obj, indent=1), encoding="utf-8")

    def get_json(self, key):
        p = self._p(key)
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    def keys(self, prefix):
        base = self._p(prefix)
        return sorted(str(p.relative_to(self.root)).replace(os.sep, "/") for p in base.rglob("*") if p.is_file()) if base.exists() else []

    def size(self, key):
        p = self._p(key)
        return p.stat().st_size if p.exists() else None

    def move(self, src, dst):
        self._p(dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(self._p(src), self._p(dst))


class R2Store:
    def __init__(self, env):
        try:
            import boto3
        except ImportError:
            die("boto3 is missing: pip install boto3")
        miss = [k for k in ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET") if not env.get(k)]
        if miss:
            die(f"missing in .env: {', '.join(miss)} (issue #26)")
        self.bucket = env["R2_BUCKET"]
        self.s3 = boto3.client("s3", endpoint_url=f"https://{env['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
                               aws_access_key_id=env["R2_ACCESS_KEY_ID"],
                               aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"], region_name="auto")

    def put_file(self, key, path, ctype, cache):
        self.s3.upload_file(str(path), self.bucket, key, ExtraArgs={"ContentType": ctype, "CacheControl": cache})

    def put_json(self, key, obj):
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=json.dumps(obj, indent=1).encode(),
                           ContentType="application/json", CacheControl=INDEX_CACHE)

    def get_json(self, key):
        try:
            return json.loads(self.s3.get_object(Bucket=self.bucket, Key=key)["Body"].read())
        except self.s3.exceptions.NoSuchKey:
            return None

    def keys(self, prefix):
        out, tok = [], None
        while True:
            kw = {"Bucket": self.bucket, "Prefix": prefix, **({"ContinuationToken": tok} if tok else {})}
            r = self.s3.list_objects_v2(**kw)
            out += [o["Key"] for o in r.get("Contents", [])]
            if not r.get("IsTruncated"):
                return out
            tok = r["NextContinuationToken"]

    def size(self, key):
        try:
            return self.s3.head_object(Bucket=self.bucket, Key=key)["ContentLength"]
        except Exception:
            return None

    def move(self, src, dst):
        self.s3.copy_object(Bucket=self.bucket, Key=dst, CopySource={"Bucket": self.bucket, "Key": src})
        if self.size(dst) is None:
            die(f"copy to {dst} not confirmed; {src} left in place")
        self.s3.delete_object(Bucket=self.bucket, Key=src)


# ---------------------------------------------------------------- what to publish
def scan_numbers():
    out = {}
    f = DATASET / ".scan_numbers.tsv"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            parts = line.strip().split("\t")
            if len(parts) == 2 and parts[0].isdigit():
                out[parts[1]] = int(parts[0])
    return out


def resolve_capture(scan, numbers):
    if scan.isdigit():
        hit = [c for c, n in numbers.items() if n == int(scan)]
        if not hit:
            die(f"no scan #{scan} in dataset/.scan_numbers.tsv")
        return hit[0]
    return Path(scan.rstrip("/\\")).name


def run_info(tag):
    """(run ID, date) of the first TRAINING.md heading naming this tag, as scanBundles.ts reads it."""
    f = REPO / "docs" / "progress" / "TRAINING.md"
    if not f.exists():
        return None, None
    for m in re.finditer(r"^### (R-\d+) · (\d{4}-\d{2}-\d{2}) · (.*)$", f.read_text(encoding="utf-8"), re.M):
        explicit = re.search(r"tag `([^`]+)`", m.group(3))
        tags = [explicit.group(1)] if explicit else re.findall(r"`([^`]+)`", m.group(3))
        if tag in tags:
            return m.group(1), m.group(2)
    return None, None


def owner_of(env, args):
    owner = (args.owner or env.get("PUBLISH_OWNER", "")).strip().lower()
    if not SAFE_OWNER.match(owner):
        die("set PUBLISH_OWNER in .env (lower case letters, digits, '-'; e.g. umair) or pass --owner")
    name = (args.owner_name or env.get("PUBLISH_OWNER_NAME") or owner.capitalize())[:40]
    return owner, name


def read_index(store, owner, name):
    idx = store.get_json(f"scans/{owner}/index.json") or {"version": 1, "owner": owner, "name": name, "bundles": []}
    if idx.get("owner") != owner:
        die(f"scans/{owner}/index.json belongs to {idx.get('owner')!r}: not touching it")
    return idx


def publish(store, env, args):
    owner, name = owner_of(env, args)
    numbers = scan_numbers()
    capture = resolve_capture(args.scan, numbers)
    folder = f"{capture}_{args.tag}"
    if not SAFE_NAME.match(folder):
        die(f"unsafe folder name {folder!r}")
    src = SCANS_DIR / folder
    if not (src / "scan.json").exists():
        die(f"no bundle {src} (run the web stage first, or is it in scans_archive/?)")
    scan = json.loads((src / "scan.json").read_text(encoding="utf-8"))
    files = sorted(p for p in src.iterdir() if p.is_file() and SAFE_NAME.match(p.name))
    # the run's folder is work_<tag>_sfm/gs_<tag>/, or work_<model tag>_sfm/gs_<tag>/ for re-runs on a trained
    # model (R-054 – R-057: work_r1118_sfm/gs_r1119c/)
    plans = sorted((DATASET / capture).glob(f"work_*_sfm/gs_{args.tag}/layout/plan.png"))
    plan = plans[0] if plans else Path("-")
    if plan.exists():
        files.append(plan)
    run_id, date = run_info(args.tag)
    entry = {"folder": folder, "capture": capture, "tag": args.tag, "scan_number": numbers.get(capture),
             "run_id": run_id, "date": date or dt.date.today().isoformat(), "room": args.room or None,
             "plan": "plan.png" if plan.exists() else None, "scan": scan,
             "published": dt.datetime.now().isoformat(timespec="seconds")}
    prefix = f"scans/{owner}/{folder}/"
    total = sum(p.stat().st_size for p in files)
    print(f"{name} ({owner}): {folder} -> {prefix}  {len(files)} files, {total / 1e6:.1f} MB"
          f"{'' if run_id else '  (no TRAINING.md run for this tag)'}")
    if args.dry_run:
        for p in files:
            print(f"  would upload {p.name} ({p.stat().st_size / 1e6:.1f} MB)")
        return
    for p in files:
        key = prefix + p.name
        store.put_file(key, p, TYPES.get(p.suffix.lower()) or mimetypes.guess_type(p.name)[0] or "application/octet-stream", FILE_CACHE)
        if store.size(key) != p.stat().st_size:
            die(f"upload of {p.name} not confirmed (size differs); index not changed")
        print(f"  {p.name} ok")
    idx = read_index(store, owner, name)
    idx["name"] = name
    idx["bundles"] = [b for b in idx["bundles"] if b.get("folder") != folder] + [entry]
    idx["updated"] = entry["published"]
    store.put_json(f"scans/{owner}/index.json", idx)
    owners = store.get_json("owners.json") or {"version": 1, "owners": []}
    if not any(o.get("id") == owner for o in owners["owners"]):
        owners["owners"].append({"id": owner, "name": name})
        store.put_json("owners.json", owners)
    print(f"published: {len(idx['bundles'])} bundle(s) in scans/{owner}/index.json")


def unpublish(store, env, args):
    owner, name = owner_of(env, args)
    folder = f"{resolve_capture(args.scan, scan_numbers())}_{args.tag}"
    idx = read_index(store, owner, name)
    if not any(b.get("folder") == folder for b in idx["bundles"]):
        die(f"{folder} is not published by {owner}")
    idx["bundles"] = [b for b in idx["bundles"] if b.get("folder") != folder]
    store.put_json(f"scans/{owner}/index.json", idx)  # off the site first, then the files move
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    for key in store.keys(f"scans/{owner}/{folder}/"):
        store.move(key, f"archive/{key[:-len(key.split('/')[-1])]}{stamp}/{key.split('/')[-1]}")
    print(f"unpublished {folder}: files moved to archive/scans/{owner}/{folder}/{stamp}/ (not deleted)")


def list_published(store, env, args):
    owners = (store.get_json("owners.json") or {}).get("owners", [])
    if not owners:
        print("nothing published yet")
    for o in owners:
        idx = store.get_json(f"scans/{o['id']}/index.json") or {"bundles": []}
        print(f"{o.get('name', o['id'])} ({o['id']}): {len(idx['bundles'])} bundle(s)")
        for b in idx["bundles"]:
            n = f"scan #{b['scan_number']}" if b.get("scan_number") is not None else b["capture"]
            print(f"  {n:10s} {b['tag']:10s} {b.get('run_id') or '-':6s} {b['date']}  {b.get('room') or ''}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["publish", "unpublish", "list"])
    ap.add_argument("scan", nargs="?")
    ap.add_argument("tag", nargs="?")
    ap.add_argument("--room", default="", help="room name shown on the card")
    ap.add_argument("--owner", default="", help="overrides PUBLISH_OWNER")
    ap.add_argument("--owner-name", default="", help="overrides PUBLISH_OWNER_NAME")
    ap.add_argument("--target", default="r2", help="r2 (default) or dir:<folder>")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.action != "list" and not (args.scan and args.tag):
        ap.error(f"{args.action} needs <scan> <tag>")
    env = load_env()
    store = DirStore(args.target[4:]) if args.target.startswith("dir:") else R2Store(env)
    {"publish": publish, "unpublish": unpublish, "list": list_published}[args.action](store, env, args)


if __name__ == "__main__":
    main()
