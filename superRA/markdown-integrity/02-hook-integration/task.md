---
title: "Wire Checker into PostToolUse Hook (task-system, warn-only)"
status: revise
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

The `01-checker-and-rules` checker is now wired into the existing PostToolUse hook ([skills/task-system/scripts/task_hook.py](../../../skills/task-system/scripts/task_hook.py)) as a warn-only, broader branch alongside the unchanged `task.md`-only reconcile branch. No new hook script, wrapper, or `hooks/hooks*.json` registration was added; the generated `hooks/task-hook` shim already invokes `task_hook.py` and needed no regeneration.

**How it works.**

- A cheap gate, [`_is_markdown_under_task_root`](../../../skills/task-system/scripts/task_hook.py#L49-L62), short-circuits the hot path: a `.md` suffix check plus a path-parts scan for `superRA`/`.plan`, no file read. The common non-markdown edit returns before any work.
- [`_markdown_integrity_feedback`](../../../skills/task-system/scripts/task_hook.py#L65-L94) resolves the sibling checker relative to `task_hook.py`'s own location (`skills/task-system/scripts` → `skills/report-in-markdown/scripts`), imports `md_integrity`, and calls `check()`. The whole `skills/` tree ships together, so this resolves identically across local checkout, Claude plugin cache, Codex cache, and GitHub-clone installs. The import and check are wrapped in best-effort `try/except` (mirroring the existing reconcile steps) — any failure returns no feedback rather than breaking the hook.
- Both edit paths call it. The Claude path [`_handle_edit_write`](../../../skills/task-system/scripts/task_hook.py#L371-L409) merges render-integrity findings into the same feedback list as the `task.md` reconcile, emitting one `_feedback_json` per tool call. The Codex path [`_handle_apply_patch`](../../../skills/task-system/scripts/task_hook.py#L448-L483) runs the check on every touched `.md` path extracted from the patch payload.
- Findings reuse the existing `_feedback_json` / `_emit_feedback` channel — the model-visible `additionalContext` JSON shape both harnesses inject as context. No second feedback format was introduced. The hook always exits 0; clean `.md` files and non-`.md` edits stay silent.

**Tests.** Six new cases extend `TestTaskHook` in [skills/task-system/scripts/test_task_system.py](../../../skills/task-system/scripts/test_task_system.py): an Edit of a task `.md` with an adjacent `$$` block surfaces a `display-math-not-separated` warning naming the file; a `\diag`-class macro surfaces a `tex-only-macro` warning; a non-`task.md` `.md` under a task root is still checked (the render branch is broader than the reconcile); a clean `.md` and a non-`.md` edit both stay silent; and a Codex `apply_patch` payload touching a `.md` surfaces the warning. These assert on the real emitted `additionalContext` JSON parsed from subprocess stdout, not just a function return.

**Verification.** `uv run --with pytest --with pyyaml python -m pytest skills/task-system/scripts/test_task_system.py` — 325 passed, 0 failures (TestTaskHook: 30 passed, including the 6 new cases).

## Review Notes

Integration review (`de482ee4..649c46df`). Task-local correctness was already approved and re-verified working end-to-end (drove a real `{tool_name:"Edit", file_path:".../task.md"}` payload through `task_hook.py`: render-integrity findings merge into the existing `additionalContext` feedback JSON alongside the reconcile warning, in the shape both harnesses inject; a non-`task.md` `notes.md` under a task root also fires the render branch; `pytest -k TaskHook` → 30 passed). Code integration is clean: utility reuse (`TASK_ROOT_DIRNAME`/`LEGACY_TASK_ROOT_DIRNAME`, `_feedback_json`/`_emit_feedback`), stdlib-only, best-effort try/except, cheap hot-path gate, minimum net diff. The blocking gap is the **Project Doc Audit**.

1. **MAJOR — stale hook-architecture reference (`[BLOCKING]` Documentation currency / Project Doc Audit).** [skills/task-system/references/internals.md:114](../../../skills/task-system/references/internals.md#L114) and [:117](../../../skills/task-system/references/internals.md#L117) are the contributor-facing single source for the PostToolUse hook's behavior, reachable from `task_hook.py` in the governing diff, and are now factually incomplete:
   - Line 114 says the `Edit|Write` / `apply_patch` matcher "fires when a `task.md` is edited directly, reconciling from the edited file's plan root." After this diff the same path **also fires on any `.md` under a task root** (not just `task.md`) to run the render-integrity check — demonstrated above with `notes.md`. The "when a `task.md` is edited" framing now understates what fires.
   - Line 117 says "On a match the hook runs the same best-effort reconcile — `validate_plan`, `propagate_parent_status`." It omits the new render-integrity check (`_markdown_integrity_feedback` → `report-in-markdown/scripts/md_integrity.check`) that now runs alongside reconcile, on the broader `.md`-under-task-root gate, and merges into the same feedback emission.
   - Fix: update §Hook Architecture so the `Edit|Write` / `apply_patch` bullet and the "On a match…" paragraph describe both branches — the `task.md`-only reconcile and the broader warn-only render-integrity check on any `.md` under a task root, sourced from the sibling `report-in-markdown` checker — keeping the existing pointer/link discipline (link, do not duplicate the rule text from `report-in-markdown`).
   → implemented (orchestrator, direct edit): [internals.md §Hook Architecture](../../../skills/task-system/references/internals.md#L110) updated — the `Edit|Write` / `apply_patch` bullet now states it fires on any `.md` under a task root, and the "On a match…" paragraph now describes the warn-only render-integrity check (`_markdown_integrity_feedback` → sibling `report-in-markdown/scripts/md_integrity.check`) running alongside reconcile, pointing to the checker rather than duplicating its rule text.

2. **MINOR (advisory) — inventory entries do not surface the new self-diagnose CLI.** `report-in-markdown` now ships its first bundled scripts ([skills/report-in-markdown/scripts/check_markdown.py](../../../skills/report-in-markdown/scripts/check_markdown.py) + `md_integrity.py`), but its one-line summaries still describe it only as a style guide: [skills/CATEGORIES.md:43](../../../skills/CATEGORIES.md#L43), [README.md:93](../../../README.md#L93), the `using-superRA` skill-inventory row, and the SKILL.md frontmatter `description` ([skills/report-in-markdown/SKILL.md:3](../../../skills/report-in-markdown/SKILL.md#L3)). None is factually contradicted (none claimed "no scripts"), and the CLI is documented in the SKILL body, so this is non-blocking. Orchestrator's call whether to add a brief "self-diagnose CLI" pointer in these inventory rows / frontmatter while fixing item 1 — consolidated here because both are the same doc-coherence pass.
   → orchestrator: accepted in part. Updated the two discovery surfaces an agent reads to decide whether to load/run the tool — the [report-in-markdown frontmatter description](../../../skills/report-in-markdown/SKILL.md#L3) and the [using-superRA inventory row](../../../skills/using-superRA/SKILL.md#L72) now name the render-integrity self-diagnose CLI. Left [CATEGORIES.md:43](../../../skills/CATEGORIES.md#L43) and [README.md:93](../../../README.md#L93) as-is: those are grouping/overview surfaces where "markdown style guide" stays accurate and the script is an internal detail, so a pointer there is not worth the release-doc churn.
