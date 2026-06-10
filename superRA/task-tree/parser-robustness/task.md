---
title: "Parser robustness: tolerate unknown status, fence-aware section parsing"
status: approved
depends_on:  []
tags: []
created: 2026-06-03
---

## Objective

Make the shared task.md parser in `skills/task-tree/scripts/_task_io.py` degrade gracefully on edge-case task content instead of crashing the readers that depend on it (dashboard, `task query`, `task read`). Two independent robustness fixes, one concern — the core parser must not break on content a hand-edited or differently-versioned `task.md` can legitimately contain.

**Fix 1 — tolerate an unknown `status:` value.** `parse_task` hard-raised `ValueError` on any status outside `VALID_STATUSES`. Most readers funnel through `parse_task` during a plain tree walk (`walk_plan` → `_walk_children` → `parse_task`) with no error handling, so a single malformed status anywhere in any watched tree aborts the whole walk. The live failure: serving the dashboard against a tree containing `status: done` crashed at FastAPI lifespan startup (`rebuild_tree` → `walk_plan`), so the server never came up; `task query` and `task read` share the same unguarded path. The one reader that already coped is `task check`, which wraps `parse_task` in its own `try/except ValueError` (`task_check.py:238` `_walk_plan_tolerant`) to reconstruct a partial task and still report the bad value via `check_status_validity` (`task_check.py:77`). The fix: make leniency universal at the parser level — `parse_task` **warns and preserves the raw status string** rather than raising — so every reader survives, and `task check` stays the single strict validator. This is safe because everything downstream already tolerates unrecognized values — `compute_status` treats an unknown leaf status as inert (falls through to not-started at the branch), and the dashboard template renders `badge-{{ status }}` (an unknown status just gets an unstyled badge). A reader must never mutate the file; warn-and-preserve keeps the on-disk value untouched for `task check` to report and the human to fix.

**Fix 2 — fence-aware section parsing.** `parse_body_sections` split the body on any line matching `^## `, so a `## ` line quoted *inside* a ``` ``` ``` / `~~~` fenced code block (e.g. a task that embeds a `task.md` template in a code fence) started a phantom section and truncated the real section containing the fence. The dashboard's Jinja `render_task_body` macro had the same naive split. Both must become fence-aware — toggle an `in_fence` flag on fence lines and treat `## ` as a header only when not in a fence — matching the behavior `_has_nonempty_section` (`_task_io.py:201`) already had. The Python parser and the template renderer must agree so a task renders the same sections in the dashboard as the CLI reads.

**Scope discipline.** Touch `skills/task-tree/scripts/_task_io.py`, `skills/task-tree/scripts/templates/task_node.html`, and the test suite `skills/task-tree/scripts/test_task_tree.py` (regression tests that lock in both fixes). Do **not** edit `task_check.py` — its now-redundant tolerant wrapper is a separate follow-up (see Results). No regeneration of Codex agent files is involved (no `skills/*` or `agents/*` behavior text changed).

### Conventions

Work in this project worktree only: `/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/better-handoff`. Concurrent worktrees of this repo exist; keep all edits and the commit on this worktree's branch.

## Validation

- **Status leniency, real failure path.** Build the tree (`walk_plan`) over a directory containing a `task.md` with `status: done` and confirm it no longer raises — the raw value is preserved on the Task and a `UserWarning` is emitted. Confirm `superra task check` still reports the bad status as an `[ERROR]` finding (it is now reachable).
- **Fence-aware parsing, both sites agree.** Parse a body whose Objective contains a fenced block with a `## Foo` line inside it; confirm `parse_body_sections` does not create a `Foo` section and does not truncate the Objective. Confirm the dashboard `render_task_body` macro produces the same section set for the same body.
- **Regression tests lock in both fixes.** `TestParseTask::test_unknown_status_warns_and_preserves` and `TestParseBodySections::test_fenced_header_not_a_section` in `test_task_tree.py` assert the warn-and-preserve behavior and the fence-aware split respectively, so neither can silently regress.
- **No regression.** The task-tree test suite passes: `uv run --project skills/task-tree --with pytest --with httpx python -m pytest skills/task-tree/scripts -q`.

## Results

The shared task.md parser now degrades gracefully on edge-case content instead of aborting the readers that depend on it. Both fixes live in [_task_io.py](../../../skills/task-tree/scripts/_task_io.py); the fence fix also lands in the dashboard template [task_node.html](../../../skills/task-tree/scripts/templates/task_node.html).

### What changed

**Fix 1 — unknown `status:` no longer crashes readers.** `parse_task` ([_task_io.py:295](../../../skills/task-tree/scripts/_task_io.py#L295)) previously raised `ValueError` on any status outside `VALID_STATUSES`; the dashboard, `task query`, and `task read` all walk the tree through `parse_task` on a plain unguarded path (`walk_plan` → `_walk_children`), so one malformed `status: done` crashed the dashboard at lifespan startup. It now `warnings.warn(...)` and **preserves the raw status string** ([_task_io.py:301](../../../skills/task-tree/scripts/_task_io.py#L301)), pointing the user at `superra task check`. This is the correct separation of concerns: readers are lenient and never crash on one bad file; `task check` is the single strict validator that reports the bad status as an `[ERROR]` finding ([task_check.py:77](../../../skills/task-tree/scripts/task_check.py#L77)). `task check` already coped with the old hard-raise via its own `_walk_plan_tolerant` wrapper ([task_check.py:238](../../../skills/task-tree/scripts/task_check.py#L238)) that caught the `ValueError` and rebuilt a partial task; with leniency now universal at the parser level that wrapper is redundant — a separate follow-up cleanup left out of this task's scope. Downstream consumers were already safe: `compute_status` treats an unrecognized leaf status as inert, and the template's `badge-{{ status }}` falls back to an unstyled badge.

**Fix 2 — section parsing is fence-aware.** `parse_body_sections` ([_task_io.py:181](../../../skills/task-tree/scripts/_task_io.py#L181), [:188](../../../skills/task-tree/scripts/_task_io.py#L188)) now tracks an `in_fence` flag and treats `## ` as a section header only outside a ``` ``` ``` / `~~~` fence, so a quoted header inside a code block no longer starts a phantom section or truncates the section that contains the fence. This brings it in line with `_has_nonempty_section` ([_task_io.py:201](../../../skills/task-tree/scripts/_task_io.py#L201)), which was already fence-aware. The dashboard's Jinja `render_task_body` macro ([task_node.html:25](../../../skills/task-tree/scripts/templates/task_node.html#L25), [:28](../../../skills/task-tree/scripts/templates/task_node.html#L28), [:32](../../../skills/task-tree/scripts/templates/task_node.html#L32)) received the matching fence toggle, so the dashboard renders the same section set the CLI parser reads.

**Doc coherence (integration pass).** `skills/task-tree/references/internals.md` documented the pre-change behavior — that `parse_task()` "raise[s] `ValueError`" on an invalid enum, and that `parse_body_sections` is a plain `## ` split. The integration project-doc audit updated all three affected spots ([internals.md:58](../../../skills/task-tree/references/internals.md#L58), [:60](../../../skills/task-tree/references/internals.md#L60), [:101](../../../skills/task-tree/references/internals.md#L101)) to describe the new lenient-parse / strict-`task check` split and the fence-aware section parsing.

### Verification

- **Status leniency.** `walk_plan` over a tree containing `status: done` builds without raising; the parsed `Task.status` keeps the raw `'done'` and a `UserWarning` naming the file and `superra task check` is emitted. The previously-crashing live tree (`ClaudeReimbursement/superRA`) now walks cleanly. `superra task check` on a tree with a `done` child reports `[ERROR] [status] child: invalid status 'done'`, confirming the strict path is reachable.
- **Fence-aware parsing.** A synthetic body with a `## ` line inside a fenced block parses without a phantom section and without truncating the enclosing section.
- **Test suite.** `python -m pytest skills/task-tree/scripts -q` → 424 passed (incl. the two new regression tests). `test_detects_invalid_status` still passes through the new lenient parse path (its `UserWarning` is expected), confirming `task_check` detection is intact.

### Follow-up

`task_check._walk_plan_tolerant` ([task_check.py:238](../../../skills/task-tree/scripts/task_check.py#L238)) wraps `parse_task` in `try/except ValueError` to survive the old hard-raise on bad status. Now that `parse_task` is lenient, that branch is dead for the status case and the wrapper can be collapsed to a plain `walk_plan`. Out of this task's scope (`task_check.py` is not touched here); flagged for a future task-check cleanup.
