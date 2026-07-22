---
title: "Background Serve Lifecycle for Non-Loopback --host"
status: approved
depends_on:  []
---

## Objective

Make the background dashboard launcher work when serve is given a non-loopback --host (e.g. a LAN or Tailscale interface IP). Today the launcher's readiness and reuse probes are hardcoded to loopback, so a server bound only to a non-loopback interface is never seen: the launcher declares 'failed to bind within 10s' and kills the healthy server it just spawned. Contract: (1) 'serve --root superRA --host <interface-ip> --no-open' launches a background server bound to that interface and reports success with a URL that is actually reachable (the bound host, not localhost); (2) an immediate re-launch with the same arguments reuses the running server instead of spawning or killing it; (3) 'stop' stops it; (4) the default loopback behavior and its messages are unchanged; (5) a regression test covers the non-loopback background launch (bind succeeds, launcher reports success, reuse works). Verification: the previously failing command sequence passes, and the dashboard test suite passes.

## Planner Guidance

Diagnosed in-session on macOS: 'serve --host 100.114.244.56' binds fine (uvicorn log shows it running) but serve_background's _wait_for_dashboard probes http://127.0.0.1:<port>/healthz, never sees it, prints 'Error: dashboard failed to bind http://localhost:8995 within 10s', and terminates the child. All probe/bookkeeping paths assume loopback: _probe_dashboard and _wait_for_dashboard target 127.0.0.1 (plan_dashboard.py ~L2094-2120), _port_serving connects to ('localhost', port), and success/reuse messages print http://localhost:<port>. The PID file stores only '<pid> <port>', so reuse/stop cannot know which interface a prior server bound. Suggested route (minimal): derive a probe host from the requested --host (0.0.0.0/:: probe as 127.0.0.1, else probe the host itself), thread it through _wait_for_dashboard/_probe_dashboard/_port_serving and the printed URLs, and record the host alongside pid/port in the PID file so later launches and stop probe the right interface. Do not add multi-interface binding or a --tailscale flag; the researcher explicitly scoped those out. Repro: 'uv run --script skills/task-tree/scripts/plan_dashboard.py serve --root superRA --host <your-ip> --no-open' currently exits 1 after ~10s and kills the server. Tests live in skills/task-tree/scripts/test_dashboard.py (serve-lifecycle tests near the background-supervisor coverage); run via 'uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with uvicorn[standard] --with watchfiles --with httpx python -m pytest skills/task-tree/scripts/test_dashboard.py'.

## Results

Implemented along the planner's suggested route: the launcher now derives a probe host from the requested `--host` and threads it through every readiness/reuse probe and printed URL, and the PID file records the bound host so later launches and reuse probe the right interface.

**Code changes** (all in [plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py)):

- `_probe_host(host)` ([plan_dashboard.py:2093-2100](../../../../skills/task-tree/scripts/plan_dashboard.py#L2093-L2100)) — maps a bind host to the address to probe: wildcard binds (`0.0.0.0`/`::`) probe loopback (they accept loopback connections), any other interface is probed directly.
- `_display_host(host)` ([plan_dashboard.py:2103-2110](../../../../skills/task-tree/scripts/plan_dashboard.py#L2103-L2110)) — maps a bind host to the printed-URL host: loopback/wildcard show `localhost`, while an explicit interface shows its literal IP so the printed URL is reachable.
- `_port_serving`, `_probe_dashboard`, `_wait_for_dashboard` accept a `probe_host` parameter (defaults preserve the loopback behavior for existing callers/tests); `serve_background` passes `_probe_host(host)` at every probe site — the post-spawn readiness wait, the failed-bind diagnosis, and both reuse layers ([plan_dashboard.py:2255-2413](../../../../skills/task-tree/scripts/plan_dashboard.py#L2255-L2413)).
- PID file format extended from `<pid> <port>` to `<pid> <port> <host>` ([plan_dashboard.py:2024-2061](../../../../skills/task-tree/scripts/plan_dashboard.py#L2024-L2061)); `_running_pid` returns the recorded host and probes it, with loopback fallback for legacy files (pid-only and pid+port both parse; old readers ignore the extra field, so the change is cross-version safe). Layer-1 reuse probes/announces the recorded host, so reuse works even when the current invocation omits `--host`.
- The launch/reuse/error messages and the foreground "Starting dashboard at" line compose that display host with the canonical worktree selector, so a non-loopback launch prints `http://<interface-ip>:<port>/?wt=<worktree>` while loopback/wildcard URLs retain `localhost` and route to the invoking worktree.

Scope-outs honored: no multi-interface binding, no `--tailscale` flag.

**Regression protection** (contract item 5): `TestBackgroundLaunch::test_nonloopback_host_launch_binds_reports_and_reuses` ([test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py)) discovers a real non-loopback interface IP (UDP-connect trick; skips if the host has none), launches a real background server bound to it, asserts launch success and the exact bound-interface, worktree-scoped URL, verifies `/healthz` is reachable at that interface but **not** via 127.0.0.1 (the exact scenario the old loopback-only probe missed), then re-launches with the same arguments and asserts the exact reuse URL, no dashboard spawn, and the same PID before stopping it. The default lifecycle regression asserts the exact canonical localhost launch and reuse messages. Supporting unit tests cover the 3-tuple PID-file format and legacy `pid+port` parsing.

**Verification evidence** (macOS):

- Red-green cycle for the protected URLs: the two targeted lifecycle tests passed, perturbing both expected hosts to `wrong-host` produced **2 failures**, and restoring the expectations made them pass again in the full suite.
- Full dashboard suite: `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts/test_dashboard.py` → **279 passed, 2 skipped**; the non-loopback regression ran rather than skipping.
- Live Tailscale validation against the worktree script: launch bound only to this host's Tailscale interface reported its reachable interface URL; an online Tailscale peer fetched `/healthz` and received the dashboard identity with the launched PID; an identical relaunch reported reuse with that same PID; `stop` terminated it, after which the peer's request failed with connection-refused exit 7. No private IP or machine name is embedded in the committed tests.

**Caveat:** the reuse-announce URL comes from the PID file's recorded host; for a PID file written by a pre-change server (no host field) it falls back to loopback wording, which matches the old behavior.

## Sync Impact

The host-aware lifecycle now composes with the base branch's worktree-scoped launch URLs: `_dashboard_url` uses the requested or PID-recorded display host and retains the canonical `?wt=` selector. Exact loopback and non-loopback lifecycle assertions cover the full composed URL; the non-loopback no-respawn check distinguishes dashboard children from Git subprocesses used for worktree discovery. Sync commit: `1ce4fac3`.

## Review Notes

1. **MAJOR — The sync narrative erases the intentional unscoped mode-conflict exception.** The Results claim that every launch/reuse/error URL composes the canonical worktree selector, but the preserved mode-conflict branch still constructs an unscoped display-host URL at [plan_dashboard.py:2477](../../../../skills/task-tree/scripts/plan_dashboard.py#L2477). This is consistent with the incoming base's stated intent that the mode-conflict diagnostic is not a launch URL, but it contradicts both [the current Results claim](task.md#L25) and the merge commit's broader “error … URLs … retaining the canonical `?wt=` selector” thesis. Keep the code or scope it deliberately, then make the task record and a propagation sync commit state the same exception so Integrate receives an accurate approved diff.
