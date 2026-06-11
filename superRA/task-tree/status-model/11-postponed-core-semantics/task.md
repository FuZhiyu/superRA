---
title: "Core postponed semantics"
status: approved
depends_on:
  - 02-data-layer
tags: []
script: 
input: []
output: []
created: 2026-06-01
---

## Objective

Add `postponed` to the status enum and wire its frontier, rollup, and cascade semantics in the core task-tree library. All edits are in `skills/task-tree/scripts/`. Use `archived` as the reference for every site; mirror it except where noted.

### `_task_io.py`

1. **Enum (line ~20).** Add `"postponed"` to `VALID_STATUSES`. This automatically flows to `parse_task` (line ~283), `validate_frontmatter` (line ~602), `task_check.py`, and the `task_update.py --status` argparse choices — confirm each accepts `postponed` after the change.

2. **Frontier — leaf exclusion (`_collect_frontier`, line ~538-543).** A `postponed` leaf must never be on the frontier, exactly like `archived`. Change the early return so it triggers for both: `if task.status in ("archived", "postponed"): return`.

3. **Frontier — branch child skip (line ~549).** A branch whose rolled-up `effective_status` is `postponed` must be skipped so the recursion never descends into it: `if child.effective_status() in ("archived", "postponed"): continue`.

4. **Frontier — dependency satisfaction (line ~564-567). DO NOT add `postponed` here.** The satisfying set stays `("approved", "archived")`. Because `postponed` is not in that set, a dependent of a postponed task already gets `deps_met = False` and is blocked from the frontier — this is the confirmed design (postponed blocks dependents). No code change is needed at this line; the requirement is to *not* add `postponed` and to cover the behavior with a test (below). Update the inline comment if it helps clarify that postponed deliberately blocks.

5. **Rollup (`compute_status`, line ~448-476).** Exclude `postponed` from the active set alongside `archived`: `child_statuses = [s for s in all_statuses if s not in ("archived", "postponed")]`. Then refine the empty-set case (currently `if not child_statuses: return "archived"`): when all children are parked, a deferred child dominates an abandoned one, so return `"postponed"` if any child is `postponed`, else `"archived"`:
   ```python
   if not child_statuses:
       return "postponed" if any(s == "postponed" for s in all_statuses) else "archived"
   ```
   Update the docstring (lines ~451-457) to describe both: postponed children are excluded from rollup, and an all-parked branch rolls up to postponed-if-any-postponed-else-archived.

### `task_update.py`

6. **Cascade allow-list (line ~24).** Add `"postponed"` to `_CASCADE_ALLOWED` so a whole subtree can be parked with `--cascade --status postponed`. Update the `--cascade` help text (line ~37-38) to include `postponed` in the "Only valid for" list.

7. **Cascade skip rule (line ~127-128) — verify, likely no change.** The existing rule `if leaf.status == "archived" and status != "archived": continue` already does the right thing: cascading `postponed` leaves `archived` leaves untouched (status is `postponed` ≠ `archived`), and cascading `not-started` (resume) overwrites `postponed` leaves as intended. Confirm both behaviors hold; only touch this line if a test proves otherwise.

### Tests (`skills/task-tree/scripts/test_task_tree.py`)

Add coverage mirroring the existing `archived` tests, including the cases that distinguish `postponed` from `archived`:

- `postponed` is a member of `VALID_STATUSES`; `parse_task` and `validate_frontmatter` accept it.
- A `postponed` leaf is absent from `compute_frontier`.
- **Dependency blocking:** sibling B `depends_on` A; with A `postponed`, B is NOT on the frontier. Contrast: with A `archived`, B IS on the frontier (regression guard that the two statuses differ here).
- Rollup: children `[approved, postponed]` → parent `approved`; children all `postponed` → parent `postponed`; children `[archived, postponed]` → parent `postponed`; children all `archived` → parent `archived` (unchanged).
- Cascade `postponed` onto a branch parks all non-archived leaves and leaves `archived` leaves archived; cascade `not-started` afterward resumes the postponed leaves.

Run `python3 skills/task-tree/scripts/test_task_tree.py` (or the project's test runner) and confirm green before marking implemented.

## Results

Core `postponed` semantics wired into the task-tree library. All edits in `skills/task-tree/scripts/`.

### `_task_io.py`

- **Enum:** added `"postponed"` to `VALID_STATUSES` ([_task_io.py:20](../../../../skills/task-tree/scripts/_task_io.py#L20)). Confirmed it flows to `parse_task` ([line 283](../../../../skills/task-tree/scripts/_task_io.py#L283)), `validate_frontmatter` ([line 602](../../../../skills/task-tree/scripts/_task_io.py#L602)), `task_check.py` (imports the constant), and the `task_update.py --status` argparse choices — verified via `task_update.py --help` showing `postponed` in the `--status` choice list.
- **Frontier leaf exclusion:** `_collect_frontier` early return now triggers for both parked statuses — `if task.status in ("archived", "postponed"): return` ([_task_io.py:539](../../../../skills/task-tree/scripts/_task_io.py#L539)).
- **Frontier branch skip:** branch children whose `effective_status()` is in `("archived", "postponed")` are skipped ([_task_io.py:549](../../../../skills/task-tree/scripts/_task_io.py#L549)).
- **Dependency satisfaction — deliberately unchanged.** The satisfying set stays `("approved", "archived")` ([_task_io.py:565](../../../../skills/task-tree/scripts/_task_io.py#L565)); `postponed` is NOT added, so a dependent of a postponed task gets `deps_met = False` and is blocked. Updated the inline comment to state postponed deliberately blocks dependents.
- **Rollup `compute_status`:** `postponed` excluded from the active set alongside `archived`; all-parked branch returns `"postponed"` if any child is postponed else `"archived"` ([_task_io.py:463-466](../../../../skills/task-tree/scripts/_task_io.py#L463)). Docstring updated to describe both rules.

### `task_update.py`

- **Cascade allow-list:** added `"postponed"` to `_CASCADE_ALLOWED` ([task_update.py:24](../../../../skills/task-tree/scripts/task_update.py#L24)) and the `--cascade` help text ([task_update.py:38](../../../../skills/task-tree/scripts/task_update.py#L38)).
- **Cascade skip rule (line ~128) — verified, no change.** The rule `if leaf.status == "archived" and status != "archived": continue` already parks non-archived leaves on `--cascade postponed` while leaving archived leaves untouched, and resumes (`not-started` overwrites) postponed leaves. Confirmed by the two cascade tests below; no edit needed.

### `task_check.py`

- **Dependency diagnostic `postponed` branch.** `_check_deps_recursive` now mirrors the `archived` warning with a `postponed` branch ([task_check.py:157](../../../../skills/task-tree/scripts/task_check.py#L157)): a task depending on a `postponed` sibling emits a `warning` — `depends on postponed task '<dep>' (blocked until resumed)`. This surfaces the case where the dependent is actively blocked off the frontier (`deps_met=False`) until the dependency is resumed, the inverse of the prior behavior where the `postponed` dependency was silent while the satisfied `archived` dependency warned.

### Tests (`test_task_tree.py`)

Added 14 tests in `TestPostponedSemantics`, `TestPostponedInRollup`, `TestCascade`, and `TestTaskCheck`:

- Membership in `VALID_STATUSES`; `parse_task` and `validate_frontmatter` accept `postponed`.
- A `postponed` leaf is absent from `compute_frontier`.
- **Dependency blocking + regression guard:** with A `postponed`, dependent B is NOT on the frontier; with A `archived` (same tree shape), B IS — the two statuses differ exactly here.
- Rollup: `[approved, postponed]` → `approved`; all `postponed` → `postponed`; `[archived, postponed]` → `postponed`; all `archived` → `archived` (unchanged).
- Cascade `postponed` parks all leaves; with one leaf pre-archived, cascade `postponed` parks the others and leaves the archived one archived; cascade `not-started` afterward resumes the postponed leaves.
- **`task_check` postponed-dependency diagnostic:** `test_warns_postponed_dependency` asserts that a task depending on a `postponed` sibling produces a `dependency` `warning` whose message names `postponed`, alongside the existing `test_warns_archived_dependency`.

### Verification

`~/.venv/bin/pytest skills/task-tree/scripts/test_task_tree.py -q` → **215 passed** (14 new + 201 existing, no regressions). New regression `test_warns_postponed_dependency` confirmed individually by node id.

**Final diff self-check:** `git diff 876178e3..HEAD`; surviving-change classes — status-enum mirroring of `archived` for `postponed` across `_task_io.py` / `task_update.py` / `task_check.py` / `task_query.py`, dashboard rendering surfaces (`templates/*.html`, `summary_bar.html`), and matching test coverage in `test_task_tree.py` / `test_dashboard.py`, plus the four task.md files and root task.md. No suspicious hunks: no `agents/*` edits; the `skills/*` script edits are the feature implementation, the `SKILL.md` / references prose edits are the doc mirror owned by [13-postponed-docs](../13-postponed-docs/task.md). This turn added only the `task_check.py` `postponed` branch and its regression test.

