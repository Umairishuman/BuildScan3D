#!/usr/bin/env python3
"""BuildScan 3D — Job Manager CLI (interactive menu + direct commands)"""

import os
import sys
import time
import json
import urllib.request
import urllib.error

SERVER = os.environ.get("BUILDSCAN_SERVER", "http://localhost:8000")

YELLOW = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"
CYAN = "\033[36m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def api(method, path, data=None):
    url = f"{SERVER}{path}"
    req = urllib.request.Request(url, method=method)
    req.add_header("Content-Type", "application/json")
    body = json.dumps(data).encode() if data else None
    try:
        with urllib.request.urlopen(req, body, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = json.loads(e.read()) if e.fp else {}
        print(f"\n  {RED}ERROR {e.code}: {err.get('detail', e.reason)}{RESET}")
        return None
    except urllib.error.URLError:
        print(f"\n  {RED}Cannot connect to {SERVER} — is the server running?{RESET}")
        return None


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input(f"\n  {DIM}Press Enter to continue...{RESET}")


def pick_job(jobs, prompt="Pick a job"):
    if not jobs:
        print(f"\n  {DIM}No jobs available.{RESET}")
        return None
    print()
    for i, j in enumerate(jobs, 1):
        status = j["status"].upper()
        color = {"completed": GREEN, "failed": RED, "processing": YELLOW, "queued": CYAN}.get(j["status"], "")
        print(f"  {BOLD}{i}{RESET}) {j['job_id']}  {color}{status:<12}{RESET} {j['progress_pct']:>3}%  {j.get('current_step_label', '')}")
    print(f"  {BOLD}0{RESET}) Back")
    try:
        choice = input(f"\n  {prompt} [1-{len(jobs)}]: ").strip()
        if not choice or choice == "0":
            return None
        idx = int(choice) - 1
        if 0 <= idx < len(jobs):
            return jobs[idx]["job_id"]
    except (ValueError, EOFError):
        pass
    return None


def show_status(job_id):
    s = api("GET", f"/status/{job_id}")
    if not s:
        return
    status = s["status"].upper()
    color = {"COMPLETED": GREEN, "FAILED": RED, "PROCESSING": YELLOW, "QUEUED": CYAN}.get(status, "")
    print(f"\n  {BOLD}Job:{RESET}      {s['job_id']}")
    print(f"  {BOLD}Status:{RESET}   {color}{status}{RESET}")
    if s.get("error"):
        print(f"  {BOLD}Error:{RESET}    {RED}{s['error']}{RESET}")
    print(f"  {BOLD}Step:{RESET}     {s.get('current_step_label', '-')} ({s['step_index']}/{s['total_steps']})")
    print(f"  {BOLD}Progress:{RESET} {s['progress_pct']}%")
    print(f"  {BOLD}Elapsed:{RESET}  {s['elapsed_sec']}s")
    if s.get("recent_logs"):
        print(f"\n  {DIM}--- Recent Logs ---{RESET}")
        for line in s["recent_logs"]:
            print(f"  {line}")


def show_logs(job_id):
    s = api("GET", f"/logs/{job_id}")
    if not s:
        return
    status = s["status"].upper()
    color = {"COMPLETED": GREEN, "FAILED": RED, "PROCESSING": YELLOW}.get(status, "")
    print(f"\n  {BOLD}Job {s['job_id']}{RESET} — {color}{status}{RESET}")
    if s.get("error"):
        print(f"  {RED}Error: {s['error']}{RESET}")
    print(f"\n  {DIM}--- Full Log ({len(s['log_lines'])} lines) ---{RESET}")
    for line in s["log_lines"]:
        print(f"  {line}")


def do_retry(job_id):
    r = api("POST", f"/retry/{job_id}")
    if r:
        print(f"\n  {GREEN}Retrying job {r['job_id']} in {r['mode']} mode{RESET}")
        ans = input(f"\n  Watch live? [Y/n]: ").strip().lower()
        if ans != "n":
            do_watch(job_id)


def do_watch(job_id):
    seen = 0
    print(f"\n  Watching job {job_id} {DIM}(Ctrl+C to stop){RESET}\n")
    try:
        while True:
            s = api("GET", f"/logs/{job_id}")
            if not s:
                time.sleep(3)
                continue
            lines = s["log_lines"]
            for line in lines[seen:]:
                print(f"  {line}")
            seen = len(lines)

            status = s["status"]
            if status in ("completed", "failed"):
                print(f"\n  {'='*40}")
                if status == "failed":
                    print(f"  {RED}FAILED: {s.get('error', 'unknown')}{RESET}")
                else:
                    print(f"  {GREEN}COMPLETED{RESET}")
                break
            time.sleep(3)
    except KeyboardInterrupt:
        print(f"\n  {DIM}Stopped watching.{RESET}")


def show_config():
    cfg = api("GET", "/config")
    if not cfg:
        return
    mode = cfg["mode"]
    color = {"runpod": YELLOW, "dry_run": CYAN, "local": GREEN}.get(mode, "")
    print(f"\n  {BOLD}Mode:{RESET}      {color}{mode}{RESET}")
    print(f"  {BOLD}GPU:{RESET}       {cfg['runpod_gpu_type']}")
    print(f"  {BOLD}API Key:{RESET}   {'Set' if cfg['runpod_api_key_set'] else RED + 'Not set' + RESET}")


def switch_mode():
    show_config()
    modes = ["runpod", "dry_run", "local"]
    print()
    for i, m in enumerate(modes, 1):
        desc = {"runpod": "Process on RunPod GPU (costs credits)",
                "dry_run": "Save uploads only, no processing",
                "local": "Process on this machine"}.get(m, "")
        print(f"  {BOLD}{i}{RESET}) {m:<10} {DIM}{desc}{RESET}")
    print(f"  {BOLD}0{RESET}) Cancel")
    try:
        choice = input(f"\n  Switch to [1-3]: ").strip()
        if choice in ("1", "2", "3"):
            new_mode = modes[int(choice) - 1]
            api("POST", "/config", {"mode": new_mode})
            print(f"\n  {GREEN}Switched to: {new_mode}{RESET}")
    except (ValueError, EOFError):
        pass


def menu():
    while True:
        clear()
        print(f"""
  {BOLD}BuildScan 3D — Job Manager{RESET}
  {'='*30}

  {BOLD}1{RESET}) List jobs
  {BOLD}2{RESET}) Job status & logs
  {BOLD}3{RESET}) Watch job (live tail)
  {BOLD}4{RESET}) Retry failed job
  {BOLD}5{RESET}) Full logs
  {BOLD}6{RESET}) Processing mode
  {BOLD}7{RESET}) Server health
  {BOLD}0{RESET}) Exit
""")
        try:
            choice = input(f"  > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if choice == "0" or choice.lower() == "q":
            break

        elif choice == "1":
            jobs = api("GET", "/jobs")
            if jobs is not None:
                if not jobs:
                    print(f"\n  {DIM}No jobs yet. Upload a scan from the app.{RESET}")
                else:
                    print(f"\n  {BOLD}{'JOB ID':<14} {'STATUS':<12} {'PROGRESS':>8}  STEP{RESET}")
                    print(f"  {'-'*60}")
                    for j in jobs:
                        status = j["status"].upper()
                        color = {"completed": GREEN, "failed": RED, "processing": YELLOW, "queued": CYAN}.get(j["status"], "")
                        print(f"  {j['job_id']:<14} {color}{status:<12}{RESET} {j['progress_pct']:>7}%  {j.get('current_step_label', '')}")
            pause()

        elif choice == "2":
            jobs = api("GET", "/jobs")
            if jobs:
                job_id = pick_job(jobs, "View status for")
                if job_id:
                    show_status(job_id)
            pause()

        elif choice == "3":
            jobs = api("GET", "/jobs")
            if jobs:
                active = [j for j in jobs if j["status"] in ("processing", "queued", "uploading")]
                pool = active if active else jobs
                job_id = pick_job(pool, "Watch")
                if job_id:
                    do_watch(job_id)
            pause()

        elif choice == "4":
            jobs = api("GET", "/jobs")
            if jobs:
                failed = [j for j in jobs if j["status"] == "failed"]
                if not failed:
                    print(f"\n  {DIM}No failed jobs to retry.{RESET}")
                else:
                    job_id = pick_job(failed, "Retry")
                    if job_id:
                        do_retry(job_id)
            pause()

        elif choice == "5":
            jobs = api("GET", "/jobs")
            if jobs:
                job_id = pick_job(jobs, "Show logs for")
                if job_id:
                    show_logs(job_id)
            pause()

        elif choice == "6":
            switch_mode()
            pause()

        elif choice == "7":
            h = api("GET", "/health")
            if h:
                print(f"\n  {GREEN}Server is running{RESET}")
                print(f"  Mode: {h['mode']}")
            pause()

        else:
            print(f"\n  {DIM}Invalid choice.{RESET}")
            time.sleep(0.5)


def main():
    args = sys.argv[1:]
    if not args:
        menu()
    elif args[0] == "list":
        jobs = api("GET", "/jobs")
        if jobs is not None:
            if not jobs:
                print("No jobs.")
            else:
                print(f"{'JOB ID':<14} {'STATUS':<12} {'PROGRESS':>8}  STEP")
                print("-" * 60)
                for j in jobs:
                    status = j["status"].upper()
                    color = {"completed": GREEN, "failed": RED, "processing": YELLOW}.get(j["status"], "")
                    print(f"{j['job_id']:<14} {color}{status:<12}{RESET} {j['progress_pct']:>7}%  {j.get('current_step_label', '')}")
    elif args[0] == "status" and len(args) > 1:
        show_status(args[1])
    elif args[0] == "logs" and len(args) > 1:
        show_logs(args[1])
    elif args[0] == "retry" and len(args) > 1:
        do_retry(args[1])
    elif args[0] == "watch" and len(args) > 1:
        do_watch(args[1])
    elif args[0] == "mode":
        if len(args) > 1:
            switch_mode()
        else:
            show_config()
    else:
        print("Usage: python scripts/jobs.py  (interactive menu)")
        print("       python scripts/jobs.py list|status|logs|retry|watch|mode [args]")


if __name__ == "__main__":
    main()
