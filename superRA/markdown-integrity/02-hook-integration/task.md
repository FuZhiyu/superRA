---
title: "Wire Checker into PostToolUse Hook (task-system, warn-only)"
status: not-started
depends_on: 
  - 01-checker-and-rules

tags: []
created: 2026-06-08
---

## Objective

Wire the `01-checker-and-rules` checker into the existing PostToolUse hook so any markdown file edited under a task root is auto-checked, warn-only, for both harnesses. The detection logic is **not** reimplemented here — this task only invokes the checker from `report-in-markdown/scripts/md_integrity.py` and folds its findings into the hook's existing feedback channel.

**Where the change goes.** Extend [skills/task-system/scripts/task_hook.py](../../../skills/task-system/scripts/task_hook.py) — do not add a new hook script, wrapper, or `hooks/hooks*.json` registration. The `Edit|Write` → `task-hook` → `task_hook.py` PostToolUse path already exists and fires for both Claude and Codex; the `hooks/task-hook` shim is generated and already invokes `task_hook.py`, so it needs no regeneration.

**Behavior:**

- In the Claude Edit/Write path (`_handle_edit_write`) and the Codex apply_patch path (`_handle_apply_patch`), for every touched file whose path is a `.md` under a task root (`superRA/` or legacy `.plan/`), run the markdown checker and add its findings to the same feedback list that is emitted via `_feedback_json`. The current `task.md`-only reconcile branch stays as-is; the markdown check is an **additional, broader** branch (any `.md`, not just `task.md`) whose findings merge into one feedback emission per tool call.
- Import the checker by resolving the sibling skill relative to `task_hook.py`'s own location (`skills/task-system/scripts/task_hook.py` → `skills/report-in-markdown/scripts/`), so it resolves identically across local checkout, Claude plugin cache, Codex cache, and GitHub-clone installs (the whole `skills/` tree ships together). Guard the import/check in best-effort try/except like the existing reconcile steps — a checker failure must never break the hook.
- **Non-blocking, fast, silent-when-clean.** Always exit 0. Emit feedback only when there are findings; a clean `.md` and any non-`.md` file produce no output. Keep the hot path cheap: the `.md`-under-task-root gate must short-circuit before any file read for the common non-markdown edit.

**Tests** — extend the `task_hook.py` test suite: a PostToolUse Edit payload for a task `.md` containing an adjacent `$$` block produces feedback JSON naming the file and the issue; a clean `.md` produces no output; a non-`.md` edit produces no markdown feedback; a Codex `apply_patch` payload touching a `.md` is covered. Run with deps supplied per repo `CLAUDE.md` (`uv run --with pytest --with pyyaml python -m pytest skills/task-system/scripts`).

**Done when:** Edit/Writing a task `.md` with an adjacent `$$` block or a `\diag`-class macro yields a non-blocking hook warning naming the file and line via the existing feedback channel, for both the Edit/Write and apply_patch paths; clean and non-markdown edits stay silent; no new hook registration or generated-shim edit was needed; tests pass.

## Planner Guidance

- `_feedback_json` / `_emit_feedback` already produce the model-visible `additionalContext` JSON — reuse them; do not invent a second feedback format.
- The existing task-root gating helpers (`TASK_ROOT_DIRNAMES`, the `.md` path checks already used for `task.md`) are the model for the cheap path gate.
- Verify the real surfaced output, not just the function return — confirm the emitted JSON is the shape both harnesses inject as context (the existing tests/feedback contract show the expected shape).

## Results

