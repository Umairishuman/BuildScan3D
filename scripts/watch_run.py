#!/usr/bin/env python3
"""Readable live view of a pipeline run, used by `scripts/buildscan watch` (raw logs: `buildscan watch ... --raw`).

  python3 scripts/watch_run.py <run dir: dataset/<scan>/work_<tag>_sfm/gs_<tag>> [--label "scan #3 ..."]
                               [--session run-<tag>] [--once] [--every 5]

Reads run_full.log (stage markers written by run_full.sh and run_v8.py) and train.log, and shows which of the 15
stages is running, what it does, how long it has been running (and how long it took in R-030 for comparison), the
training step, the GPU, and the last message with the long paths removed. Standard library only.
"""
import argparse
import os
import re
import subprocess
import sys
import time

# (stage, what it does, minutes in R-030: scan #2, lab room, 97 s video, this PC; TRAINING.md R-030)
STAGES = [
    ("select", "picking the sharpest video frames", 0.2),
    ("sfm", "working out where the camera was for every frame (COLMAP)", 4.9),
    ("export", "writing the frames and camera positions for training", 0.0),
    ("prior", "estimating a depth map for every frame (Metric3D)", 1.9),
    ("init", "first 3D points of the room (fast multi-view stereo)", 6.6),
    ("train", "training the 3D model (Gaussian splats)", 27.8),
    ("ply", "saving the model (splat.ply)", 0.3),
    ("layout", "finding walls, floor and ceiling", 0.1),
    ("sem2d", "finding doors, windows, switches, sockets, lights in the frames", 7.7),
    ("sem3d", "placing those fixtures in 3D", 0.1),
    ("verify", "checking every fixture again in the frames", 0.1),
    ("sem3d2", "final fixture labels after the check", 0.1),
    ("mesh", "building a surface mesh", 0.1),
    ("meshlabels", "colouring the mesh with the labels", 0.2),
    ("web", "packing everything for the web viewer", 0.1),
]
NAMES = [s[0] for s in STAGES]
GPU_RE = re.compile(r"^\s*\[gpu (\d\d:\d\d:\d\d)\] (\d+)% \| (\d+) / (\d+) MiB \| (\d+) C \| (\d+) W")
V8_START = re.compile(r"^== (\w+): ")
V8_DONE = re.compile(r"^   (\w+) ([\d.]+) min\s*$")
OUT_START = re.compile(r"^=== \[(\d\d:\d\d:\d\d)\] (\w+)\s*$")
OUT_DONE = re.compile(r"^=== \[(\d\d:\d\d:\d\d)\] (\w+) done in (\d+) min (\d+) s")
HEADER = re.compile(r"^=== run_full\.sh (\S+ \S+) ")
TRAIN = re.compile(r"^(\d+) \(([\d.]+)%\)(.*)$")
NOISE = ("FutureWarning", "warnings.warn", "UserWarning", "DeprecationWarning")


def hms_to_s(t):
    h, m, s = map(int, t.split(":"))
    return h * 3600 + m * 60 + s


def short(line, root):
    """Drop the long absolute paths and interpreter commands from a log line."""
    line = line.replace(root + "/", "")
    line = re.sub(r"/home/[^\s]*/(micromamba|\.local)/[^\s]*", "", line)
    line = re.sub(r"(?:/[\w.-]+){3,}/([\w.-]+)", r"\1", line)        # remaining absolute paths -> file name
    line = re.sub(r"\brun -r \S+ -n (\S+) python\b", r"(\1)", line)
    return re.sub(r"\s{2,}", " ", line).strip()


def parse(run_dir):
    log = os.path.join(run_dir, "run_full.log")
    lines = open(log, errors="replace").read().replace("\r", "\n").splitlines() if os.path.exists(log) else []
    st = {"started": None, "done": {}, "current": None, "cur_since": None, "gpu": None, "last": "", "finished": False,
          "errors": [], "last_gpu_t": None, "ended": None}
    for ln in lines:
        m = HEADER.match(ln)
        if m:
            st["started"] = m.group(1)
            continue
        g = GPU_RE.match(ln)
        if g:
            st["gpu"] = g.groups()
            st["last_gpu_t"] = g.group(1)
            continue
        if ln.startswith("=== all done"):
            st["finished"] = True
            m = re.match(r"=== all done (\S+ \S+):", ln)
            st["ended"] = m.group(1) if m else None
            st["current"] = None
            continue
        m = V8_START.match(ln) or OUT_START.match(ln)
        if m:
            name = m.group(m.lastindex)
            if name in NAMES:
                st["current"] = name
                st["cur_since"] = m.group(1) if m.re is OUT_START else st["last_gpu_t"]
                st["last"] = ""
                continue
        m = V8_DONE.match(ln)
        if m and m.group(1) in NAMES:
            st["done"][m.group(1)] = float(m.group(2))
            if st["current"] == m.group(1):
                st["current"] = None
            continue
        m = OUT_DONE.match(ln)
        if m and m.group(2) in NAMES:
            st["done"][m.group(2)] = int(m.group(3)) + int(m.group(4)) / 60
            if st["current"] == m.group(2):
                st["current"] = None
            continue
        if any(n in ln for n in NOISE) or not ln.strip() or ln.startswith("=== ["):
            continue
        if re.search(r"Traceback|\b[A-Z]\w*Error\b|^Error\b|\bFAILED\b|\bKilled\b|out of memory", ln):
            st["errors"].append(ln)
        st["last"] = ln
    if st["current"] is None and not st["finished"]:
        nxt = [n for n in NAMES if n not in st["done"]]
        if nxt and st["done"]:
            st["current"] = nxt[0]          # between two stages: the next one is starting
    return st


def train_progress(run_dir):
    p = os.path.join(run_dir, "train.log")
    if not os.path.exists(p) or time.time() - os.path.getmtime(p) > 120:
        return None
    with open(p, "rb") as f:
        f.seek(max(0, os.path.getsize(p) - 6000))
        tail = f.read().decode(errors="replace").replace("\r", "\n")
    rows = [TRAIN.match(re.sub(r"\x1b\[[0-9;]*m", "", ln).strip()) for ln in tail.splitlines()]
    rows = [r for r in rows if r]
    if not rows:
        return None
    step, pct, rest = rows[-1].groups()
    cols = [c.strip() for c in re.split(r"\s{2,}", rest.strip()) if c.strip()]
    eta = cols[1] if len(cols) > 1 else ""
    return int(step), float(pct), eta


def session_running(name):
    if not name:
        return None
    try:
        out = subprocess.run(["screen", "-ls"], capture_output=True, text=True).stdout
    except OSError:
        return None
    return re.search(r"\d+\." + re.escape(name) + r"\s", out) is not None


def fmt_min(m):
    return f"{m:.1f} min" if m < 60 else f"{int(m // 60)} h {int(m % 60)} min"


def render(run_dir, label, session, root):
    st = parse(run_dir)
    out = []
    now = time.strftime("%H:%M:%S")
    head = f"Run {os.path.basename(run_dir).replace('gs_', '', 1)} on {label}" if label else f"Run {run_dir}"
    out.append(head)
    if st["started"]:
        t0 = time.mktime(time.strptime(st["started"], "%Y-%m-%d %H:%M:%S"))
        if st["finished"] and st["ended"]:
            t1 = time.mktime(time.strptime(st["ended"], "%Y-%m-%d %H:%M:%S"))
            out.append(f"started {st['started']}, finished {st['ended']} after {fmt_min((t1 - t0) / 60)}")
        else:
            out.append(f"started {st['started']}, running for {fmt_min((time.time() - t0) / 60)}   (now {now})")
    out.append("")
    alive = session_running(session)
    if st["finished"]:
        out.append(f"FINISHED: all {len(NAMES)} stages done.  Results: scripts/buildscan results <scan> <tag>")
    elif alive is False:
        out.append(f"STOPPED: the run is not running any more ({session} ended) and did not finish.")
        out.append("  Look at the last lines below, or the full log with --raw. Continue later with --from <stage>.")
    cur = st["current"]
    if cur and not st["finished"]:
        i = NAMES.index(cur)
        desc, ref = STAGES[i][1], STAGES[i][2]
        out.append(f"NOW: stage {i + 1} of {len(NAMES)}: {cur}  -  {desc}")
        since = ""
        if st["cur_since"]:
            el = (hms_to_s(now) - hms_to_s(st["cur_since"])) % 86400 / 60
            since = f"running for about {fmt_min(el)}; "
        out.append(f"     {since}took {fmt_min(ref)} in R-030 (scan #2, 97 s video)")
        tp = train_progress(run_dir) if cur == "train" else None
        if tp:
            step, pct, eta = tp
            bar = "#" * int(pct / 5) + "-" * (20 - int(pct / 5))
            out.append(f"     training step {step}  [{bar}] {pct:.0f}% of the training" + (f", about {eta} left" if eta else ""))
    out.append("")
    done = [f"{n} {fmt_min(st['done'][n])}" for n in NAMES if n in st["done"]]
    left = [n for n in NAMES if n not in st["done"] and n != cur]
    out.append(f"Done ({len(done)} of {len(NAMES)}): " + (", ".join(done) if done else "none yet"))
    if left and not st["finished"]:
        out.append("Still to come: " + ", ".join(left))
    if st["gpu"]:
        t, u, mu, mt, c, w = st["gpu"]
        out.append(f"GPU at {t}: busy {u}% (how hard the graphics card works, not the run's progress), "
                   f"memory {int(mu) / 1024:.1f} of {int(mt) / 1024:.1f} GB, {c} °C")
    if st["errors"]:
        out.append("")
        out.append("Errors in the log (newest last):")
        out.extend("  " + short(e, root)[:160] for e in st["errors"][-3:])
    if st["last"]:
        out.append("")
        out.append("Last message: " + short(st["last"], root)[:200])
    out.append("")
    out.append("Ctrl+C stops watching, not the run.  Full logs: add --raw.")
    return "\n".join(out), st["finished"] or alive is False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--label", default="")
    ap.add_argument("--session", default="")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--every", type=float, default=5)
    a = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        while True:
            text, end = render(a.run_dir, a.label, a.session, root)
            if a.once or not sys.stdout.isatty():
                print(text)
                return
            sys.stdout.write("\x1b[H\x1b[2J" + text + "\n")
            sys.stdout.flush()
            if end:
                return
            time.sleep(a.every)
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
