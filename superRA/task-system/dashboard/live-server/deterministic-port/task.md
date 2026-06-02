---
title: "Deterministic port from worktree path"
status: approved
depends_on: []
tags: []
created: 2026-05-25
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

Implemented in [plan_dashboard.py:1555-1567](skills/task-system/scripts/plan_dashboard.py#L1555-L1567).

Changes made to `skills/task-system/scripts/plan_dashboard.py`:

1. Added `import hashlib` and `import socket` to the module imports (lines 17-19).
2. Added `_default_port(plan_root: Path) -> int` helper (lines 1555-1567) that:
   - Computes `int(hashlib.sha256(str(plan_root.resolve()).encode()).hexdigest(), 16) % 900 + 8100` for range 8100-8999.
   - Checks port availability via `socket.connect_ex`; tries next port on collision (up to 10 attempts, wrapping at 8999).
   - Falls back to OS-assigned (`port=0`) if all 10 attempts fail.
3. Changed `--port` default from `8080` to `None` (line 1586).
4. In `main()`, resolves port via `_default_port(PLAN_ROOT)` when `args.port is None` (line 1622).
5. Startup banner conditionally shows "(derived from ...)" only when port was auto-computed (lines 1627-1630).

Verified: `hashlib.sha256` produces the same port for the same path across multiple Python invocations (8913 consistently for the test path), and different paths yield different ports (8913 vs 8458). Explicit `--port` override still works and no longer shows misleading "derived from" text.

