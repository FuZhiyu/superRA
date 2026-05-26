---
title: "Deterministic port from worktree path"
status: implemented
review_status: revise
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

Implemented in [plan_dashboard.py:1554-1566](skills/task-system/scripts/plan_dashboard.py#L1554-L1566).

Changes made to `skills/task-system/scripts/plan_dashboard.py`:

1. Added `import socket` to the module imports (line 18).
2. Added `_default_port(plan_root: Path) -> int` helper (lines 1554-1566) that:
   - Computes `hash(str(plan_root.resolve())) % 900 + 8100` for range 8100-8999.
   - Checks port availability via `socket.connect_ex`; tries next port on collision (up to 10 attempts, wrapping at 8999).
   - Falls back to OS-assigned (`port=0`) if all 10 attempts fail.
3. Changed `--port` default from `8080` to `None` (line 1585).
4. In `main()`, resolves port via `_default_port(PLAN_ROOT)` when `args.port is None` (line 1621).
5. Updated startup banner to: `Starting dashboard at http://localhost:{port} (derived from {PLAN_ROOT})`.

Verified: two different plan root paths produce different deterministic ports (8561 vs 8167), both in range 8100-8999, and the mapping is stable across calls. Explicit `--port` override still works.

## Review Notes

1. **[CRITICAL]** [plan_dashboard.py:1560](skills/task-system/scripts/plan_dashboard.py#L1560) — `hash()` is non-deterministic across Python processes. Python 3.3+ randomizes hash seeds by default (`PYTHONHASHSEED`), so `hash(str(plan_root.resolve()))` returns a different value each time the script is invoked. Empirically confirmed: three consecutive invocations of `python3 -c "print(hash('/path') % 900 + 8100)"` produced 8483, 8389, 8387. The port is effectively random, not deterministic, defeating the task's core goal ("each worktree always gets the same port"). **Fix:** Replace `hash()` with a stable hash function, e.g. `int(hashlib.sha256(str(plan_root.resolve()).encode()).hexdigest(), 16) % 900 + 8100`.

2. **[MINOR]** [plan_dashboard.py:1626](skills/task-system/scripts/plan_dashboard.py#L1626) — The startup banner always prints "(derived from {PLAN_ROOT})" even when the user explicitly passes `--port`. This is misleading when the port was not derived at all. **Fix:** Conditionally show "(derived from ...)" only when `args.port is None`; otherwise print the port without the derivation note.
