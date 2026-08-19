---
title: "Tree Hooks Respect the Invariants They Police"
status: approved
depends_on: [gate-hardening]
---

## Objective

The task-tree hooks never produce a state their own validators flag, and the validators stop flagging prescribed states.

- `propagate_parent_status` never writes `approved` onto a parent whose `## Review Notes` carries `[BLOCKING]`: it holds the current status and surfaces a warning through the hook's feedback list ("children approved but parent Review Notes still carry [BLOCKING]; clear or re-review").
- `task_hook._reconcile` propagates parent status before it validates, so warnings describe the state the run produced.
- `validate_revision_notes` allows `revise` alongside `not-started`/`in-progress` — `revise` with fresh `## Revision Notes` is the prescribed planner→implementer handoff; `skills/task-tree/references/internals.md` documents the corrected rule and gains the missing `validate_review_notes` row.
- `parse_body_sections` merges both bodies, blank line between, when a legacy `## Planner Guidance` collides with `## Details` — no planner text is ever dropped; `_comments.py` normalizes anchor sections through the same alias map so legacy anchors resolve instead of orphaning.
- Cleanup: the function-local `from _task_io import …` in `approved_with_blocking_review_notes` moves into the existing top-level import.

Validation: each fix carries its reproducing pytest case (approved-rollup-onto-blocking parent with no same-run warning; `revise` + Revision Notes emitting no warning; both-headings body parsing to merged content; legacy-anchor resolution); full suite green.

## Details

File/line map: rollup write at [_task_io.py:1147](../../../../skills/task-tree/scripts/_task_io.py#L1147) (reuse `approved_with_blocking_review_notes`; `propagate_parent_status` returns a count today — extend it or check in `task_hook.py` to emit the warning); validate-before-propagate ordering at [task_hook.py:177-197](../../../../skills/task-tree/scripts/task_hook.py#L177-L197) (the rename pass at line 371 already runs pre-validation for the same reason); allowlist at [_task_validate.py:57](../../../../skills/task-tree/scripts/_task_validate.py#L57) — update the docstring, which states the old rule; alias collision at [_task_io.py:323-357](../../../../skills/task-tree/scripts/_task_io.py#L323-L357) (last-wins dict write at 350/356); anchor lookup at [_comments.py:335](../../../../skills/task-tree/scripts/_comments.py#L335); stale doc row at [internals.md:63](../../../../skills/task-tree/references/internals.md#L63); local import at [_task_validate.py:69](../../../../skills/task-tree/scripts/_task_validate.py#L69).

`depends_on: gate-hardening` is execution order, not input: both tasks edit `task_hook.py` (parser repoint there vs. the reconcile reorder here), so they run serially to avoid conflicting edits.

## Results

- The tree hooks no longer produce states their own validators flag; each fix carries its reproducing pytest case and the full suite passes (823 tests).
  - `propagate_parent_status` holds the current status instead of writing an `approved` rollup onto a parent whose `## Review Notes` carry `[BLOCKING]`, and appends "children approved but parent Review Notes still carry [BLOCKING]; clear or re-review" to an optional `feedback` list; `task_hook._reconcile` and `_propagate_whole_tree` surface it through the hook's feedback (deduplicated across overlapping ancestor chains).
  - `_reconcile` propagates before it validates, so warnings describe the state the run produced (`test_reconcile_validates_post_propagation_state`).
  - `validate_revision_notes` allows `revise` — a fresh note there is the prescribed planner→implementer handoff; the pinned `test_revise_with_revnote_warns` flipped to `no_warn`, and [internals.md](../../../../skills/task-tree/references/internals.md) documents the corrected rule plus the previously missing `validate_review_notes` row.
  - `parse_body_sections` merges a legacy `## Planner Guidance` with `## Details` (blank line between, either order) instead of last-wins overwriting; `_comments._reanchor` normalizes anchor sections through the same alias map so legacy anchors resolve (`test_legacy_alias_anchor_resolves`).
  - Cleanup: `approved_with_blocking_review_notes`'s function-local `_task_io` import moved to the top-level import.
- Tests: `TestTreeHookInvariants`, `TestSectionAliasCollision` in [test_task_tree.py](../../../../skills/task-tree/scripts/test_task_tree.py); anchor case in [tests/test_comments.py](../../../../skills/task-tree/scripts/tests/test_comments.py).
