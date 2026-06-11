#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""Live server-level verification of the watcher-teardown spin fix.

Launches the real dashboard server (in-process, foreground) on a high port,
connects one SSE client to /events, disconnects it, then samples the server
process CPU and thread list over a >=30 s window (long enough to clear the
spin's delayed onset). Asserts:
  * no `notify-rs fsevents loop` (or any watchfiles native watch) thread lingers,
  * process CPU returns to baseline rather than climbing.

Run from the worktree root:
  uv run --project skills/task-tree --with httpx python \
    superRA/task-tree/dashboard/multi-worktree-serving/06-watcher-teardown-spin/attachments/live_verify.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import httpx

REPO = Path(__file__).resolve().parents[6]
SCRIPTS = REPO / "skills" / "task-tree" / "scripts"
PORT = 8137


def cpu_pct(pid: int) -> float:
    out = subprocess.run(
        ["ps", "-o", "%cpu=", "-p", str(pid)], capture_output=True, text=True
    ).stdout.strip()
    return float(out) if out else -1.0


def fsevents_threads(pid: int) -> int:
    """Count `notify-rs fsevents loop` threads in a 1 s sample of the process."""
    out = subprocess.run(
        ["sample", str(pid), "1"], capture_output=True, text=True
    ).stdout
    return out.count("notify-rs fsevents loop")


def main() -> int:
    env = dict(os.environ)
    # Run the in-process serve path directly so we own the PID.
    proc = subprocess.Popen(
        [sys.executable, str(SCRIPTS / "plan_dashboard.py"), "serve",
         "--foreground", "--port", str(PORT), "--no-open"],
        cwd=str(REPO), env=env,
    )
    pid = proc.pid
    try:
        # Wait for the port to bind.
        for _ in range(60):
            try:
                httpx.get(f"http://127.0.0.1:{PORT}/", timeout=1.0)
                break
            except Exception:
                time.sleep(0.5)
        else:
            print("server never bound")
            return 2

        print(f"server pid={pid}, baseline cpu={cpu_pct(pid):.1f}%  "
              f"fsevents_threads={fsevents_threads(pid)}")

        # Connect one SSE client, read the heartbeat, then disconnect.
        with httpx.Client(timeout=10.0) as c:
            with c.stream("GET", f"http://127.0.0.1:{PORT}/events") as r:
                it = r.iter_lines()
                next(it)  # consume the initial heartbeat
                time.sleep(2.0)
                print(f"while connected: cpu={cpu_pct(pid):.1f}%  "
                      f"fsevents_threads={fsevents_threads(pid)}")
            # stream context exit => client disconnect => SSE finally => _stop_watcher
        print("disconnected; sampling post-disconnect window (>=30 s)...")

        worst_cpu = 0.0
        worst_threads = 0
        start = time.monotonic()
        samples = []
        for target in (5, 15, 25, 35):
            while time.monotonic() - start < target:
                time.sleep(0.2)
            cpu = cpu_pct(pid)
            thr = fsevents_threads(pid)
            samples.append((target, cpu, thr))
            worst_cpu = max(worst_cpu, cpu)
            worst_threads = max(worst_threads, thr)
            print(f"  t+{target:>2}s  cpu={cpu:5.1f}%  fsevents_threads={thr}")

        print(f"\nworst post-disconnect cpu={worst_cpu:.1f}%  "
              f"worst fsevents_threads={worst_threads}")
        ok = worst_threads == 0 and worst_cpu < 10.0
        print("RESULT:", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
