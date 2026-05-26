---
title: "Deterministic port from worktree path"
status: not-started
review_status: ~
integration_status: ~
depends_on:  []
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

When multiple worktrees each run their own dashboard, they collide on the default port 8080. Assign a deterministic port derived from the resolved plan root path so each worktree always gets the same port without manual `--port` flags.

**Implementation:**

1. Add a `_default_port(plan_root: Path) -> int` helper near the CLI arg parsing in `plan_dashboard.py`:
   - Compute `hash(str(plan_root.resolve())) % 900 + 8100` to map into the range 8100–8999.
   - If that port is in use (`socket.connect_ex` returns 0), try the next port up, wrapping at 8999 back to 8100. Give up after 10 attempts and fall back to OS-assigned (`port=0`).

2. Change the `--port` argument default from `8080` to `None`. When `args.port is None`, call `_default_port(PLAN_ROOT)` to resolve the port.

3. Print the chosen port clearly in the startup banner: `Starting dashboard at http://localhost:{port} (derived from {PLAN_ROOT})`.

**Files to modify:**
- `skills/task-system/scripts/plan_dashboard.py` — add `_default_port()`, update arg default and `main()` logic.

**Validation:** Start two dashboard instances from two different `--root` paths in the same shell session and confirm they get different ports without conflict. Explicit `--port` still overrides.

## Results

