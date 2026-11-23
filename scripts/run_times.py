#!/usr/bin/env python3
"""Run times in one structured table: docs/progress/runs.tsv (D-090).

One row per run and room (a run over four rooms has four rows). Times come from the run's own files wherever they
exist, so nobody types them:

  <model folder>/timing.json      run_v8.py: minutes per stage up to the model (select ... ply, total)
  <model folder>/stages.tsv       run_full.sh: end time and minutes of every stage (run_v8, layout ... plan)
  <work_<tag>_sfm>/global_mapper.log   COLMAP: seconds of global positioning, bundle adjustment, retriangulation,
                                        whole reconstruction (only when the work folder belongs to this tag)

Rows of runs without such files (other PCs, scratch output, older runs) are written by hand from TRAINING.md, with
`source` = TRAINING; an empty cell means "not measured / not recorded", never 0.

  python3 scripts/run_times.py update            # fill the time columns of every row with a folder from its files
  python3 scripts/run_times.py check             # test runs.tsv against the files and TRAINING.md (exit 1 on FAIL)
  python3 scripts/run_times.py check --training git:exp/colmap-cudss --training docs/progress/TRAINING.md
  python3 scripts/run_times.py show [text]       # rows whose run / scan / tag / note contain <text>

check FAILs: a run in TRAINING.md missing here (or here but not in TRAINING.md), timing.json total vs the sum of its
stages, stages.tsv's run_v8 line vs timing.json, a run that is over but still open in TRAINING.md ("(running)",
"none so far", "(pending)", or "running / waiting / queued" in its index row), a row marked running whose files say
it finished, a finished row with no time at all. WARNs: TRAINING.md's entry does not quote the measured model time.

Standard library only (runs in any env).
"""
import argparse, csv, json, os, re, subprocess, sys
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TSV = os.path.join(ROOT, "docs", "progress", "runs.tsv")
MODEL_STAGES = ["select", "sfm", "export", "prior", "init", "train", "ply"]
AFTER_STAGES = ["layout", "sem2d", "sem3d", "verify", "sem3d2", "mesh", "meshlabels", "web", "plan"]
MAP = [("map_gp_s", "Global positioning"), ("map_ba_s", "Iterative bundle adjustment"),
       ("map_retri_s", "Iterative retriangulation and refinement"), ("map_total_s", "Reconstruction")]
COLS = (["run", "scan", "tag", "date", "who", "machine", "state", "folder", "start", "end", "wall_min", "model_min",
         "after_min"] + MODEL_STAGES + AFTER_STAGES + [c for c, _ in MAP] + ["source", "note"])
STATES = {"done", "failed", "stopped", "not run", "running"}
OPEN_ENTRY = re.compile(r"→ \(running\)|\*\* \(running\)|none so far|\*\* \(pending\)")
OPEN_INDEX = re.compile(r"^\s*(running|waiting|queued)\b", re.I)
NOTE_TIME = re.compile(r"\d\s*(min|s|h)\b|not recorded")


def read_rows(path=TSV):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    return [{c: (r.get(c) or "").strip() for c in COLS} for r in rows]


def write_rows(rows, path=TSV):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in sorted(rows, key=lambda r: (int(r["run"][2:]) if r["run"][2:].isdigit() else 0, r["scan"], r["tag"])):
            w.writerow(r)


def fmt(x, nd=1):
    return "" if x is None else f"{x:.{nd}f}"


def read_stages(path):
    """stages.tsv lines: '<YYYY-MM-DD HH:MM:SS>\t<stage name>\t<minutes> min' -> [(end datetime, name, minutes)]"""
    out = []
    for line in open(path):
        p = line.rstrip("\n").split("\t")
        if len(p) < 3:
            continue
        m = re.match(r"([\d.]+)\s*min", p[2])
        if m:
            out.append((datetime.strptime(p[0], "%Y-%m-%d %H:%M:%S"), p[1].split()[0], float(m.group(1))))
    return out


def read_map(log):
    """sum of each phase's seconds over every mapping round in global_mapper.log (None when a phase never finished)"""
    txt = open(log, errors="replace").read()
    out = {}
    for col, name in MAP:
        v = [float(x) for x in re.findall(re.escape(name) + r" done in ([\d.]+) seconds", txt)]
        out[col] = sum(v) if v else None
    return out


def from_files(folder, root=ROOT):
    """time columns measured from a run folder (a model folder gs_<tag>, or a work folder work_<tag>_sfm)"""
    d = os.path.join(root, folder)
    got, notes = {}, []
    base = os.path.basename(d.rstrip("/"))
    work = d if base.endswith("_sfm") else os.path.dirname(d)
    tj, st = os.path.join(d, "timing.json"), os.path.join(d, "stages.tsv")
    if os.path.exists(tj):
        t = json.load(open(tj))
        for k in MODEL_STAGES:
            if k in t:
                got[k] = fmt(t[k], 2)
        if "total" in t:
            got["model_min"] = fmt(t["total"])
    if os.path.exists(st):
        s = read_stages(st)
        if s:
            start = s[0][0] - timedelta(minutes=s[0][2])
            got["start"], got["end"] = start.strftime("%Y-%m-%d %H:%M"), s[-1][0].strftime("%Y-%m-%d %H:%M")
            got["wall_min"] = fmt((s[-1][0] - start).total_seconds() / 60)
            after = [x for x in s if x[1] in AFTER_STAGES]
            for _, n, m in after:
                got[n] = fmt(m)
            if after:
                got["after_min"] = fmt(sum(m for _, _, m in after))
    tag = base[3:] if base.startswith("gs_") else None
    log = os.path.join(work, "global_mapper.log")
    if os.path.exists(log) and (tag is None or os.path.basename(work) == f"work_{tag}_sfm"):
        for k, v in read_map(log).items():
            if v is not None:
                got[k] = fmt(v, 2)
    if not got:
        notes.append("no timing files")
    return got, notes


def update(rows, root=ROOT):
    changed = 0
    for r in rows:
        if not r["folder"] or not os.path.isdir(os.path.join(root, r["folder"])):
            continue
        got, _ = from_files(r["folder"], root)
        for k, v in got.items():
            if r[k] != v:
                r[k] = v; changed += 1
        if got:
            r["source"] = "files" if r["source"] in ("", "files") else (r["source"] if "files" in r["source"] else "files+" + r["source"])
    return changed


def load_training(specs):
    """{run: (entry text, index row)} from TRAINING.md files or git refs ('git:<ref>'); later specs win"""
    runs = {}
    for spec in specs:
        if spec.startswith("git:"):
            txt = subprocess.run(["git", "-C", ROOT, "show", spec[4:] + ":docs/progress/TRAINING.md"],
                                 capture_output=True, text=True, check=True).stdout
        else:
            txt = open(spec if os.path.isabs(spec) else os.path.join(ROOT, spec)).read()
        index = {m.group(1): m.group(0) for m in re.finditer(r"^\| (R-\d+) \|.*$", txt, re.M)}
        parts = re.split(r"^(?=### R-\d+ )", txt, flags=re.M)
        entries = {re.match(r"### (R-\d+)", p).group(1): p for p in parts if p.startswith("### R-")}
        for rid in set(index) | set(entries):
            old = runs.get(rid, ("", ""))
            runs[rid] = (entries.get(rid, old[0]), index.get(rid, old[1]))
    return runs


def check(rows, training, root=ROOT):
    fails, warns = [], []
    ids = {r["run"] for r in rows}
    for rid in sorted(set(training) - ids):
        fails.append(f"{rid}: in TRAINING.md but no row in runs.tsv")
    for rid in sorted(ids - set(training)):
        fails.append(f"{rid}: row in runs.tsv but not in TRAINING.md")
    by_run = {}
    for r in rows:
        by_run.setdefault(r["run"], []).append(r)
        key = f"{r['run']} {r['scan']} {r['tag']}".strip()
        if r["state"] not in STATES:
            fails.append(f"{key}: state '{r['state']}' is not one of {sorted(STATES)}")
        timed = any(r[c] for c in ["wall_min", "model_min", "after_min"] + MODEL_STAGES + AFTER_STAGES + [c for c, _ in MAP])
        if r["state"] in ("done", "failed", "stopped") and not timed and not NOTE_TIME.search(r["note"]):
            fails.append(f"{key}: {r['state']} but no time at all (write the time, or 'not recorded' in note)")
        if not r["folder"]:
            continue
        d = os.path.join(root, r["folder"])
        if not os.path.isdir(d):
            warns.append(f"{key}: folder {r['folder']} not on this machine (not checked)")
            continue
        tj, st = os.path.join(d, "timing.json"), os.path.join(d, "stages.tsv")
        if os.path.exists(tj):
            t = json.load(open(tj))
            if "total" in t:
                s = sum(t.get(k, 0) for k in MODEL_STAGES) + t.get("init_wait_cpu", 0)
                if abs(s - t["total"]) > 0.3:
                    fails.append(f"{key}: timing.json total {t['total']} min but its stages add up to {s:.2f}")
                if os.path.exists(st):
                    v8 = [m for _, n, m in read_stages(st) if n == "run_v8"]
                    if v8 and abs(v8[0] - t["total"]) > 0.15:
                        fails.append(f"{key}: stages.tsv run_v8 {v8[0]} min vs timing.json total {t['total']}")
        finished = os.path.exists(st) and any(n in ("web", "plan") for _, n, _ in read_stages(st))
        log = os.path.join(d, "run_full.log")
        finished = finished or (os.path.exists(log) and "=== all done" in open(log, errors="replace").read())
        if r["state"] == "running" and finished:
            fails.append(f"{key}: marked running but its files say it finished (close it)")
    for rid, rs in by_run.items():
        entry, index = training.get(rid, ("", ""))
        running = any(r["state"] == "running" for r in rs)
        if not running and OPEN_ENTRY.search(entry):
            fails.append(f"{rid}: over ({rs[0]['state']}) but its TRAINING.md entry is still open: "
                         f"'{OPEN_ENTRY.search(entry).group(0)}'")
        cells = index.split("|")
        for cell in (cells[5:6] + cells[-2:-1]) if not running and len(cells) > 6 else []:
            if OPEN_INDEX.search(cell):
                fails.append(f"{rid}: over but its index row still says '{cell.strip()}'")
        for r in rs:
            if "files" in r["source"] and r["model_min"] and entry and r["model_min"] not in entry and r["model_min"] not in index:
                warns.append(f"{rid} {r['scan']}: measured model time {r['model_min']} min is not quoted in TRAINING.md")
            if ("files" in r["source"] and r["wall_min"] and len(rs) == 1 and entry
                    and r["wall_min"] not in entry and r["wall_min"] not in index):
                warns.append(f"{rid} {r['scan']}: measured wall time {r['wall_min']} min ({r['start']} → {r['end']}) "
                             f"is not quoted in TRAINING.md")
    known = {os.path.normpath(r["folder"]) for r in rows if r["folder"]}
    for f in find_run_folders(root):
        if f not in known:
            warns.append(f"{f}: has timing files but no row in runs.tsv (which run is it?)")
    return fails, warns


def find_run_folders(root=ROOT):
    """every model folder with timing.json / stages.tsv and every work folder with a global_mapper.log under dataset/"""
    out = set()
    ds = os.path.join(root, "dataset")
    if not os.path.isdir(ds):
        return []
    for scan in sorted(os.listdir(ds)):
        sd = os.path.join(ds, scan)
        if not os.path.isdir(sd):
            continue
        for work in sorted(os.listdir(sd)):
            wd = os.path.join(sd, work)
            if not (work.startswith("work_") and work.endswith("_sfm") and os.path.isdir(wd)):
                continue
            gs = [g for g in sorted(os.listdir(wd)) if g.startswith("gs_") and
                  any(os.path.exists(os.path.join(wd, g, n)) for n in ("timing.json", "stages.tsv"))]
            out |= {os.path.relpath(os.path.join(wd, g), root) for g in gs}
            if os.path.exists(os.path.join(wd, "global_mapper.log")) and f"gs_{work[5:-4]}" not in gs:
                out.add(os.path.relpath(wd, root))
    return sorted(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["update", "check", "show"])
    ap.add_argument("text", nargs="?", default="")
    ap.add_argument("--tsv", default=TSV)
    ap.add_argument("--training", action="append", help="TRAINING.md path or git:<ref> (repeatable; later wins)")
    a = ap.parse_args(argv)
    rows = read_rows(a.tsv)
    if a.cmd == "update":
        n = update(rows); write_rows(rows, a.tsv)
        print(f"{len(rows)} rows, {n} values changed -> {os.path.relpath(a.tsv, ROOT)}")
        return 0
    if a.cmd == "show":
        cols = ["run", "scan", "tag", "state", "start", "wall_min", "model_min", "sfm", "init", "train", "after_min",
                "sem2d", "map_total_s", "source"]
        sel = [r for r in rows if a.text.lower() in " ".join([r["run"], r["scan"], r["tag"], r["note"]]).lower()]
        wd = {c: max([len(c)] + [len(r[c]) for r in sel]) for c in cols}
        print("  ".join(c.ljust(wd[c]) for c in cols))
        for r in sel:
            print("  ".join(r[c].ljust(wd[c]) for c in cols))
        return 0
    fails, warns = check(rows, load_training(a.training or ["docs/progress/TRAINING.md"]))
    for w in warns:
        print("WARN", w)
    for f in fails:
        print("FAIL", f)
    print(f"{len(rows)} rows: {len(fails)} FAIL, {len(warns)} WARN")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
