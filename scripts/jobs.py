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
    cfg = api("GET", "/config")
    if cfg and cfg["mode"] == "runpod":
        print(f"\n  Current GPU: {BOLD}{cfg['runpod_gpu_type']}{RESET}")
        ans = input(f"  Change GPU before retrying? [y/N]: ").strip().lower()
        if ans in ("y", "yes"):
            gpu = pick_gpu()
            if gpu:
                api("POST", "/config", {"runpod_gpu_type": gpu})
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


def pick_gpu():
    """Fetch available GPUs from RunPod and let user pick one."""
    print(f"\n  {DIM}Fetching available GPUs from RunPod...{RESET}")
    gpus = api("GET", "/gpus")
    if not gpus:
        return None
    # Filter to GPUs that have pricing and are in stock
    in_stock = [g for g in gpus if g.get("price_on_demand") is not None and g.get("stock_status", "None") != "None"]
    all_priced = [g for g in gpus if g.get("price_on_demand") is not None]

    if not in_stock:
        print(f"\n  {RED}No GPUs currently in stock on RunPod.{RESET}")
        if all_priced:
            print(f"  {DIM}({len(all_priced)} GPU types exist but all show 'None' stock){RESET}")
        return None

    available = in_stock
    stock_colors = {"High": GREEN, "Medium": YELLOW, "Low": RED}
    print(f"\n  {BOLD}{'#':<4} {'GPU':<30} {'VRAM':>5} {'$/hr':>7} {'Stock':>8}{RESET}")
    print(f"  {'-'*60}")
    for i, g in enumerate(available, 1):
        price_od = f"${g['price_on_demand']:.2f}" if g['price_on_demand'] else "N/A"
        stock = g.get("stock_status", "?")
        sc = stock_colors.get(stock, DIM)
        print(f"  {BOLD}{i:<4}{RESET} {g['name']:<30} {g['vram_gb']:>3} GB {price_od:>7}  {sc}{stock}{RESET}")

    print(f"  {BOLD}0{RESET})   Keep current / Cancel")
    try:
        choice = input(f"\n  Pick GPU [1-{len(available)}]: ").strip()
        idx = int(choice) - 1
        if 0 <= idx < len(available):
            picked = available[idx]
            print(f"\n  {GREEN}Selected: {picked['name']} (${picked['price_on_demand']:.2f}/hr)")
            print(f"  GPU ID: {picked['id']}{RESET}")
            return picked["id"]
    except (ValueError, EOFError):
        pass
    return None


def show_config():
    cfg = api("GET", "/config")
    if not cfg:
        return
    mode = cfg["mode"]
    color = {"runpod": YELLOW, "dry_run": CYAN, "local": GREEN, "remote": YELLOW}.get(mode, "")
    print(f"\n  {BOLD}Mode:{RESET}        {color}{mode}{RESET}")
    if mode == "runpod":
        print(f"  {BOLD}GPU Type:{RESET}    {cfg['runpod_gpu_type']}")
        print(f"  {BOLD}API Key:{RESET}     {'Set' if cfg['runpod_api_key_set'] else RED + 'Not set' + RESET}")
    elif mode == "remote":
        rhost = cfg.get("remote_host", "")
        print(f"  {BOLD}Remote GPU:{RESET}  {rhost or RED + 'Not set' + RESET}:{cfg.get('remote_port', 22)}")
        print(f"  {BOLD}User:{RESET}        {cfg.get('remote_user', 'root')}")
        print(f"  {BOLD}Skip Setup:{RESET}  {cfg.get('remote_skip_setup', False)}")


def switch_mode():
    show_config()
    modes = ["local", "runpod", "remote", "dry_run"]
    descs = {
        "local":   "Process on this machine's GPU (your partner's PC)",
        "runpod":  "Process on RunPod cloud GPU (costs credits)",
        "remote":  "SSH into a friend's GPU machine for processing",
        "dry_run": "Save uploads only, no processing",
    }
    print()
    for i, m in enumerate(modes, 1):
        print(f"  {BOLD}{i}{RESET}) {m:<10} {DIM}{descs[m]}{RESET}")
    print(f"  {BOLD}0{RESET}) Cancel")
    try:
        choice = input(f"\n  Switch to [1-{len(modes)}]: ").strip()
        idx = int(choice) - 1
        if 0 <= idx < len(modes):
            new_mode = modes[idx]
            config_data = {"mode": new_mode}

            if new_mode == "runpod":
                gpu = pick_gpu()
                if gpu:
                    config_data["runpod_gpu_type"] = gpu

            elif new_mode == "remote":
                host = input(f"  Remote GPU host (IP or hostname): ").strip()
                port = input(f"  SSH port [22]: ").strip() or "22"
                user = input(f"  SSH user [root]: ").strip() or "root"
                skip = input(f"  Skip setup (deps already installed)? [y/N]: ").strip().lower()
                config_data["remote_host"] = host
                config_data["remote_port"] = int(port)
                config_data["remote_user"] = user
                config_data["remote_skip_setup"] = skip in ("y", "yes")

            api("POST", "/config", config_data)
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
  {BOLD}6{RESET}) Reprocess existing scan
  {BOLD}7{RESET}) Processing mode
  {BOLD}8{RESET}) Browse RunPod GPUs
  {BOLD}9{RESET}) Run on existing pod {DIM}(create pod on RunPod website first){RESET}
  {BOLD}C{RESET}) Cancel stuck job
  {BOLD}H{RESET}) Server health
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
            datasets = api("GET", "/datasets")
            if datasets is None:
                pause()
                continue
            if not datasets:
                print(f"\n  {DIM}No datasets on disk. Upload a scan from the app first.{RESET}")
            else:
                print(f"\n  {BOLD}Existing scans on disk:{RESET}\n")
                for i, ds in enumerate(datasets, 1):
                    status_str = ""
                    if ds["job_status"]:
                        jcolor = {"completed": GREEN, "failed": RED, "processing": YELLOW, "queued": CYAN}.get(ds["job_status"], "")
                        status_str = f"  {jcolor}[{ds['job_status'].upper()}]{RESET}"
                    print(f"  {BOLD}{i}{RESET}) {ds['name']}  {DIM}{ds['size_mb']} MB{RESET}{status_str}")
                print(f"  {BOLD}0{RESET}) Cancel")
                try:
                    pick = input(f"\n  Reprocess which scan? [1-{len(datasets)}]: ").strip()
                    idx = int(pick) - 1
                    if 0 <= idx < len(datasets):
                        ds = datasets[idx]
                        iters = input(f"  Iterations [30000]: ").strip() or "30000"
                        change_gpu = input(f"  Change GPU? (current: from config) [y/N]: ").strip().lower()
                        gpu_param = {}
                        if change_gpu == "y":
                            gpu = pick_gpu()
                            if gpu:
                                api("POST", "/config", {"runpod_gpu_type": gpu})
                                print(f"  {GREEN}GPU set to {gpu}{RESET}")
                        import urllib.parse
                        form_data = urllib.parse.urlencode({"dataset_name": ds["name"], "iterations": int(iters)}).encode()
                        url = f"{SERVER}/reprocess"
                        req = urllib.request.Request(url, data=form_data, method="POST")
                        req.add_header("Content-Type", "application/x-www-form-urlencoded")
                        try:
                            with urllib.request.urlopen(req, timeout=10) as resp:
                                r = json.loads(resp.read())
                            print(f"\n  {GREEN}Queued {ds['name']} as job {r['job_id']} ({r['mode']} mode){RESET}")
                            ans = input(f"\n  Watch live? [Y/n]: ").strip().lower()
                            if ans != "n":
                                do_watch(r["job_id"])
                        except urllib.error.HTTPError as e:
                            err = json.loads(e.read()) if e.fp else {}
                            print(f"\n  {RED}ERROR: {err.get('detail', e.reason)}{RESET}")
                except (ValueError, EOFError):
                    pass
            pause()

        elif choice == "7":
            switch_mode()
            pause()

        elif choice == "8":
            gpu = pick_gpu()
            if gpu:
                ans = input(f"\n  Set as default GPU for RunPod? [Y/n]: ").strip().lower()
                if ans != "n":
                    api("POST", "/config", {"runpod_gpu_type": gpu})
                    print(f"\n  {GREEN}GPU updated.{RESET}")
            pause()

        elif choice == "9":
            # Run on existing RunPod pod
            datasets = api("GET", "/datasets")
            if datasets is None:
                pause()
                continue
            if not datasets:
                print(f"\n  {DIM}No datasets on disk. Upload a scan from the app first.{RESET}")
                pause()
                continue

            print(f"\n  {BOLD}Step 1:{RESET} Create a pod on {CYAN}https://runpod.io/console/pods{RESET}")
            print(f"  {DIM}Pick any GPU, use template 'RunPod Pytorch 2.4.0' or similar{RESET}")
            print(f"  {DIM}Once it shows 'Running', copy the Pod ID{RESET}")
            pod_id = input(f"\n  Enter Pod ID: ").strip()
            if not pod_id:
                pause()
                continue

            print(f"\n  {BOLD}Step 2:{RESET} Pick a scan to process:\n")
            for i, ds in enumerate(datasets, 1):
                status_str = ""
                if ds["job_status"]:
                    jcolor = {"completed": GREEN, "failed": RED, "processing": YELLOW, "queued": CYAN}.get(ds["job_status"], "")
                    status_str = f"  {jcolor}[{ds['job_status'].upper()}]{RESET}"
                print(f"  {BOLD}{i}{RESET}) {ds['name']}  {DIM}{ds['size_mb']} MB{RESET}{status_str}")
            print(f"  {BOLD}0{RESET}) Cancel")
            try:
                pick = input(f"\n  Which scan? [1-{len(datasets)}]: ").strip()
                idx = int(pick) - 1
                if 0 <= idx < len(datasets):
                    ds = datasets[idx]
                    iters = input(f"  Iterations [30000]: ").strip() or "30000"
                    import urllib.parse
                    form_data = urllib.parse.urlencode({
                        "dataset_name": ds["name"],
                        "pod_id": pod_id,
                        "iterations": int(iters),
                    }).encode()
                    url = f"{SERVER}/run-on-pod"
                    req = urllib.request.Request(url, data=form_data, method="POST")
                    req.add_header("Content-Type", "application/x-www-form-urlencoded")
                    try:
                        with urllib.request.urlopen(req, timeout=10) as resp:
                            r = json.loads(resp.read())
                        print(f"\n  {GREEN}Running on pod {pod_id} — job {r['job_id']}{RESET}")
                        print(f"  {DIM}Pod will be auto-terminated when done or on failure{RESET}")
                        ans = input(f"\n  Watch live? [Y/n]: ").strip().lower()
                        if ans != "n":
                            do_watch(r["job_id"])
                    except urllib.error.HTTPError as e:
                        err = json.loads(e.read()) if e.fp else {}
                        print(f"\n  {RED}ERROR: {err.get('detail', e.reason)}{RESET}")
            except (ValueError, EOFError):
                pass
            pause()

        elif choice.lower() == "c":
            job_list = api("GET", "/jobs")
            if job_list is None:
                pause()
                continue
            stuck = [j for j in job_list if j["status"] in ("processing", "queued", "uploading")]
            if not stuck:
                print(f"\n  {DIM}No stuck jobs.{RESET}")
            else:
                print(f"\n  {BOLD}Running/queued jobs:{RESET}\n")
                for i, j in enumerate(stuck, 1):
                    print(f"  {BOLD}{i}{RESET}) {j['job_id']}  [{j['status']}]  {j.get('current_step_label', '')}")
                print(f"  {BOLD}0{RESET}) Cancel")
                try:
                    pick = input(f"\n  Cancel which job? [1-{len(stuck)}]: ").strip()
                    idx = int(pick) - 1
                    if 0 <= idx < len(stuck):
                        jid = stuck[idx]["job_id"]
                        req = urllib.request.Request(f"{SERVER}/jobs/{jid}/cancel", method="POST")
                        try:
                            with urllib.request.urlopen(req, timeout=10) as resp:
                                json.loads(resp.read())
                            print(f"\n  {GREEN}Job {jid} cancelled.{RESET}")
                        except urllib.error.HTTPError as e:
                            err = json.loads(e.read()) if e.fp else {}
                            print(f"\n  {RED}ERROR: {err.get('detail', e.reason)}{RESET}")
                except (ValueError, EOFError):
                    pass
            pause()

        elif choice.lower() == "h":
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
