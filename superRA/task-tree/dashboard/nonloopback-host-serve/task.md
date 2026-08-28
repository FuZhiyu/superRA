---
title: "Background Serve Lifecycle for Non-Loopback --host"
status: approved
depends_on: []
---

## Objective

Make the background dashboard launcher work when serve is given a non-loopback --host (e.g. a LAN or Tailscale interface IP). Today the launcher's readiness and reuse probes are hardcoded to loopback, so a server bound only to a non-loopback interface is never seen: the launcher declares 'failed to bind within 10s' and kills the healthy server it just spawned. Contract: (1) 'serve --root superRA --host <interface-ip> --no-open' launches a background server bound to that interface and reports success with a URL that is actually reachable (the bound host, not localhost); (2) an immediate re-launch with the same arguments reuses the running server instead of spawning or killing it; (3) 'stop' stops it; (4) the default loopback behavior and its messages are unchanged; (5) a regression test covers the non-loopback background launch (bind succeeds, launcher reports success, reuse works). Verification: the previously failing command sequence passes, and the dashboard test suite passes.

## Details

Diagnosed in-session on macOS: 'serve --host <interface-ip>' binds fine (uvicorn log shows it running) but serve_background's _wait_for_dashboard probes http://127.0.0.1:<port>/healthz, never sees it, prints 'Error: dashboard failed to bind http://localhost:8995 within 10s', and terminates the child. All probe/bookkeeping paths assume loopback: _probe_dashboard and _wait_for_dashboard target 127.0.0.1 (plan_dashboard.py ~L2094-2120), _port_serving connects to ('localhost', port), and success/reuse messages print http://localhost:<port>. The PID file stores only '<pid> <port>', so reuse/stop cannot know which interface a prior server bound. Suggested route (minimal): derive a probe host from the requested --host (0.0.0.0/:: probe as 127.0.0.1, else probe the host itself), thread it through _wait_for_dashboard/_probe_dashboard/_port_serving and the printed URLs, and record the host alongside pid/port in the PID file so later launches and stop probe the right interface. Do not add multi-interface binding or a --tailscale flag; the researcher explicitly scoped those out. Repro: 'uv run --script skills/task-tree/scripts/plan_dashboard.py serve --root superRA --host <your-ip> --no-open' currently exits 1 after ~10s and kills the server. Tests live in skills/task-tree/scripts/test_dashboard.py (serve-lifecycle tests near the background-supervisor coverage); run via 'uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with uvicorn[standard] --with watchfiles --with httpx python -m pytest skills/task-tree/scripts/test_dashboard.py'.

## Results

A background launch bound to a non-loopback `--host` now succeeds, reports a URL reachable at the bound interface, and is reused rather than killed.

### Outcome

The launcher derives its probe address from the requested `--host` instead of assuming loopback. [`_probe_host`](../../../../skills/task-tree/scripts/plan_dashboard.py#L2607-L2615) maps a wildcard bind (`0.0.0.0`/`::`) to loopback, which still accepts local connections, and passes any other explicit interface through to be probed directly; [`_display_host`](../../../../skills/task-tree/scripts/plan_dashboard.py#L2617-L2625) makes the same split for printed URLs, so loopback and wildcard binds keep their exact `localhost` text and an explicit interface is shown literally. That probe host threads through [`_port_serving`](../../../../skills/task-tree/scripts/plan_dashboard.py#L2627-L2632), [`_probe_dashboard`](../../../../skills/task-tree/scripts/plan_dashboard.py#L2634-L2666), and [`_wait_for_dashboard`](../../../../skills/task-tree/scripts/plan_dashboard.py#L2668-L2687), and the host composes into the worktree-scoped launch URL at [`_dashboard_url`](../../../../skills/task-tree/scripts/plan_dashboard.py#L203-L208).

The PID file records `<pid> <port> <host>` ([`_write_pid_port`](../../../../skills/task-tree/scripts/plan_dashboard.py#L2573-L2575)), so a later launch probes the interface the running server actually bound rather than the one this invocation asked for ([`_running_pid`](../../../../skills/task-tree/scripts/plan_dashboard.py#L2689-L2711)). [`_read_pid_port`](../../../../skills/task-tree/scripts/plan_dashboard.py#L2538-L2571) returns `None` for fields a legacy pid-only or pid+port file omits, and loopback is the fallback host, so a server started before this change is still recognised.

Recording the host also closed a hole in the cross-mode conflict check. A same-repo server in the other serve mode used to be reported only by the layer-2 candidate walk, which starts from the freshly derived port; a server that had walked to a different port was missed and a second, conflicting server was spawned. The PID fast path now reports the conflict itself, against the recorded interface and port ([`_report_mode_conflict`](../../../../skills/task-tree/scripts/plan_dashboard.py#L2781-L2792)).

### Result protection

Permanent regressions cover the legacy and host-aware PID record ([test_dashboard.py:5769-5773](../../../../skills/task-tree/scripts/test_dashboard.py#L5769-L5773)), the exact unchanged loopback launch and reuse output ([test_dashboard.py:5846-5875](../../../../skills/task-tree/scripts/test_dashboard.py#L5846-L5875)), the recorded-host cross-mode conflict ([test_dashboard.py:6164-6204](../../../../skills/task-tree/scripts/test_dashboard.py#L6164-L6204)), and a real non-loopback bind/readiness/reuse/stop cycle against this host's own outbound interface ([test_dashboard.py:6310-6393](../../../../skills/task-tree/scripts/test_dashboard.py#L6310-L6393)). The cycle test asserts the server answers at the bound interface and *not* at `127.0.0.1` — the exact condition a loopback-only probe missed.

### Verification

The full task-tree script suite passes except seven `TestTaskHook` failures that reproduce identically on the base commit; they belong to the markdown-gate hook, not this change.

Live check on a Tailscale interface, run after merging onto `0.4.1`: the launch reported a worktree-scoped URL at the tailnet address, `GET /healthz` succeeded there and was refused on `127.0.0.1`, the PID file held all three fields, relaunches with both the same `--host` and the default `--host` reused the same PID, and `stop` made the tailnet connection fail.

### Known limits

- **Reuse ignores a changed `--host`.** With a server already running on loopback, `serve --host <interface>` reports `already running at http://localhost:<port>` and exits 0 without binding the requested interface. The reported URL is the one that works, so nothing is misstated, but the request is silently dropped. Reuse has always been blind to `--port` the same way. Stop the server and relaunch to change the bind.
- **IPv6 literals are unsupported.** `_port_serving` opens an `AF_INET` socket and the URL builders do not bracket the host, so `--host ::1` raises `socket.gaierror` from the candidate walk. IPv6 never worked here; before this change the same command failed with a bind-timeout message instead.
