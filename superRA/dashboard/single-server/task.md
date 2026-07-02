---
title: "Dashboard Launcher: One Server Per Repo (Fix Duplicate-Spawn / Stale-Serve)"
status: approved
depends_on: []
---

## Objective

Fix the dashboard launcher so a repo has **exactly one** background server on its deterministic port, reused across all worktrees. Today multiple `plan_dashboard.py` servers accumulate on the same repo port (one per worktree launch), only one holds the socket nondeterministically, and it can be rooted at a *different* worktree — so a dashboard opened for worktree X shows stale/empty data for X's tree.

**Reproduce first, then fix the confirmed failure.** With this checkout, launch the dashboard from two different worktrees of the same repo (e.g. this one and `better-handoff`) via `./superRA/superra dashboard --no-open` and confirm whether a second live server process appears on the shared port instead of the first being reused (`ps -eo pid,command | grep plan_dashboard`, `lsof -nP -iTCP:<port> -sTCP:LISTEN`). Diagnose the actual path that spawns the duplicate before changing behavior.

**Success criteria:**

- Launching from any worktree of the repo when a healthy server is already serving the repo's port **reuses it** — no second process, regardless of which worktree launched first or whether this worktree ever launched before.
- A launcher invocation that loses a concurrent-launch race, or whose spawned child fails to bind (port already taken), does **not** leave a lingering process — the loser exits.
- The single surviving server serves the current tree of every worktree via `?wt=` (fixing the observed stale/empty `/nav` for a non-launch worktree).
- No regression to the legitimate cases: first launch spawns; `stop` still terminates and clears the pidfile; a genuinely dead/stale pidfile is cleaned and re-spawned; the idle-timeout self-exit path is unaffected.
- Tests cover the duplicate-spawn prevention (reuse when a server is already serving the repo port even if this worktree's launch sees no valid pidfile) and the lose-the-race / bind-failure no-linger path.

## Planner Guidance

Investigation priors (in `skills/task-tree/scripts/plan_dashboard.py`) — confirm against the live repro, don't fix by hypothesis:

- Port and PID/log files are keyed by `git_common_dir` (`_default_port` ~1788, `_runtime_dir`/`_pid_file` ~1849-1860), so the repo-shared identity is correct in principle. The bug is in the reuse-vs-spawn decision, not the keying.
- `serve_background` (~1982) reuses only when `_running_pid` (~1940) finds the **pidfile** naming a live PID whose recorded port is serving. Suspect gaps: (a) the reuse check trusts the pidfile — if it is missing/stale while a real server is bound, the launch spawns anyway; (b) `_default_port` (~1795-1804) increments to the **next free port** when the deterministic port is busy, which can create a *second* server on a different port for one repo instead of reusing the busy one; (c) TOCTOU between the reuse check and the child's bind lets concurrent launches both spawn, and a child that loses the bind race (uvicorn `serve()` ~1808) may linger rather than exit.
- Consider a probe-based reuse that does not depend solely on the pidfile: if the repo's deterministic port is already serving a superRA dashboard, reuse it (and rewrite the pidfile) rather than incrementing or spawning. Keep the fix minimal and within the launcher supervisor; do not change the request-serving or multi-worktree `?wt=` code paths beyond what the repro proves necessary.
- This file is bundled tooling that runs in arbitrary target projects: keep it stdlib-only and never introduce `uv`-env provisioning (invoke stays `uv run --script` / `python3`).

### Conventions

- Same worktree/scope discipline as the sibling `dashboard-worktree-open` tree: edit only within `/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/dashboard-vscode-worktree`; run tests via `uv run --with pytest --with pyyaml ... python -m pytest skills/task-tree/scripts`.

## Results

### Reproduction (confirmed before fixing)

The seven repo worktrees are true `git worktree`s sharing one common dir (`/Users/zhiyufu/Dropbox/package_dev/superRA/.git`), so port and PID file are repo-shared in principle. The live repo port (8995) was already polluted by a pile of stale `serve --foreground --port 8995` children from several worktrees, none actually listening; the PID file named PID 93558, which held only a leftover ESTABLISHED connection while a fresh `connect_ex` got ECONNREFUSED. That is the reported symptom (many accumulated servers, nondeterministic socket holder, stale/empty nav).

Both root-cause code paths were then reproduced deterministically on isolated ports (avoiding the polluted 8995 PID file):

- **Bug A — pidfile-only reuse.** With a real server bound to a port but no PID file, `_port_serving(port)` is `True` while `_running_pid(pidfile, port)` returns `None`, so `serve_background` would spawn a duplicate. A server started in `--foreground` console mode writes no PID file, and a background file can be lost/stale while the process lives.
- **Bug B — `_default_port` walks off a busy port.** When the deterministic port was occupied, `_default_port` returned the *next free* port, so a launch targeted a different port and planted a second server for the same repo instead of reusing the one already there.

### Fix ([skills/task-tree/scripts/plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py))

Kept within the launcher supervisor; stdlib-only (`urllib`, `json`, `socket`, `hashlib`); the request-serving and `?wt=` paths are untouched except for the one identity endpoint.

1. **Deterministic start port** ([`_default_port`](../../../skills/task-tree/scripts/plan_dashboard.py#L1817)): removed the "next free port" walk; the port is a pure function of repo identity, so every worktree targets the same start port and reuse finds the one server there. Collision resolution moved into `serve_background` (see 3) so it can be repo-aware.
2. **`/healthz` identity endpoint** ([plan_dashboard.py:776](../../../skills/task-tree/scripts/plan_dashboard.py#L776)) returning `{service, pid, doc_mode, repo_id}`. `repo_id` is a stable hash of the repo's git common dir ([`_repo_id`](../../../skills/task-tree/scripts/plan_dashboard.py#L1837)); it lets reuse recognise a live superRA dashboard without the PID file, recover its PID (to repair the file), match serve mode, and — the key fix — match repo identity so a different repo colliding on the same hashed port is never adopted. The background child is launched with `--repo-id <id>` so it reports the exact token the supervisor derived (a child re-deriving from cwd could diverge in tests); a manual foreground launch derives its own.
3. **Repo-aware two-layer reuse + collision walk** in [`serve_background`](../../../skills/task-tree/scripts/plan_dashboard.py#L2089): Layer 1 is the repo-keyed PID file (fast path); Layer 2 is a candidate walk from the start port ([`_candidate_ports`](../../../skills/task-tree/scripts/plan_dashboard.py#L1849)) probing each port via [`_probe_dashboard`](../../../skills/task-tree/scripts/plan_dashboard.py#L1996). At each candidate: **our** repo's dashboard (matching `repo_id` + serve mode) → reuse and repair the PID file; a **different** repo (hash collision) or a foreign process → advance to the next port; first free port → spawn there. So same-repo reuse holds across any worktree, while a colliding different repo gets its own adjacent port instead of silently adopting (and later `stop`-killing) ours. The actually-bound port is recorded in the repo-keyed PID file, so subsequent launches reuse via Layer 1. Same-repo-different-mode on the port is reported as a conflict (the PID file is per-repo, not per-mode). A repo-id-less server (predating `/healthz` identity) is trusted as ours only on the start port.
4. **No-linger race handling** (unchanged in spirit): after spawning, [`_wait_for_dashboard`](../../../skills/task-tree/scripts/plan_dashboard.py#L2029) waits on `/healthz`. If a *different* PID answers (a concurrent launch won the bind race), the redundant child is terminated and the winner reused only when it is our repo and mode; if no dashboard comes up, a still-alive child is terminated and a foreign-process / bind failure is reported with the log tail. The loser exits rather than accumulate.

### Verification

- Full task-tree script suite green: `705 passed` (`uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts`).
- Tests ([test_dashboard.py](../../../skills/task-tree/scripts/test_dashboard.py)): `/healthz` identity now includes `repo_id`; `_default_port` stays fixed on a busy port; same-repo reuse via PID file and via probe when the PID file is missing; lose-the-race terminates the child and reuses the (same-repo) winner; a failed child does not linger; a same-repo task-mode launch atop a doc-mode server reports a conflict without spawning. New repo-collision coverage: `test_different_repo_on_port_advances_to_next_free_port` (a different repo on the start port is neither reused nor killed — the launch takes the next free port; probe reuse requires a repo-id match) and end-to-end `test_colliding_repos_each_get_own_server` (two real repos sharing a start port each run their own server; the second binds an adjacent port, the first is untouched, and each serves its own `repo_id`).

### Caveats

- **Transition period**: a dashboard started before this change has no `/healthz`, so the probe cannot identify it. Layer-1 reuse still honors a healthy PID file for such a server; a pre-`/healthz` server with a *missing* PID file is trusted as ours only on the start port (Layer 2, index 0), else the launcher spawns/reports a conflict. Resolved once old servers are stopped/restarted. The pre-existing 8995 pile is such stale state; it was left as-is per the dispatch and is not depended on.
- A genuine foreign (non-dashboard) process on the start port now causes the launch to advance to the next free port and spawn there; it is never adopted. An operator can still pin a port with an explicit `--port`.
