---
title: "Background Serve Lifecycle for Non-Loopback --host"
status: not-started
depends_on:  []
---

## Objective

Make the background dashboard launcher work when serve is given a non-loopback --host (e.g. a LAN or Tailscale interface IP). Today the launcher's readiness and reuse probes are hardcoded to loopback, so a server bound only to a non-loopback interface is never seen: the launcher declares 'failed to bind within 10s' and kills the healthy server it just spawned. Contract: (1) 'serve --root superRA --host <interface-ip> --no-open' launches a background server bound to that interface and reports success with a URL that is actually reachable (the bound host, not localhost); (2) an immediate re-launch with the same arguments reuses the running server instead of spawning or killing it; (3) 'stop' stops it; (4) the default loopback behavior and its messages are unchanged; (5) a regression test covers the non-loopback background launch (bind succeeds, launcher reports success, reuse works). Verification: the previously failing command sequence passes, and the dashboard test suite passes.

## Planner Guidance

Diagnosed in-session on macOS: 'serve --host 100.114.244.56' binds fine (uvicorn log shows it running) but serve_background's _wait_for_dashboard probes http://127.0.0.1:<port>/healthz, never sees it, prints 'Error: dashboard failed to bind http://localhost:8995 within 10s', and terminates the child. All probe/bookkeeping paths assume loopback: _probe_dashboard and _wait_for_dashboard target 127.0.0.1 (plan_dashboard.py ~L2094-2120), _port_serving connects to ('localhost', port), and success/reuse messages print http://localhost:<port>. The PID file stores only '<pid> <port>', so reuse/stop cannot know which interface a prior server bound. Suggested route (minimal): derive a probe host from the requested --host (0.0.0.0/:: probe as 127.0.0.1, else probe the host itself), thread it through _wait_for_dashboard/_probe_dashboard/_port_serving and the printed URLs, and record the host alongside pid/port in the PID file so later launches and stop probe the right interface. Do not add multi-interface binding or a --tailscale flag; the researcher explicitly scoped those out. Repro: 'uv run --script skills/task-tree/scripts/plan_dashboard.py serve --root superRA --host <your-ip> --no-open' currently exits 1 after ~10s and kills the server. Tests live in skills/task-tree/scripts/test_dashboard.py (serve-lifecycle tests near the background-supervisor coverage); run via 'uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with uvicorn[standard] --with watchfiles --with httpx python -m pytest skills/task-tree/scripts/test_dashboard.py'.

## Results

