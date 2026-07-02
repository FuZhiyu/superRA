---
title: "Core Data Layer"
status: approved
depends_on: []
---

## Objective

Build the task-tree data layer: a `Task` dataclass, a stdlib-only YAML frontmatter parser and canonical serializer, the tree walker (`walk_plan`), frontier computation (`compute_frontier`), status rollup (`compute_status`), and body-section parsing (`parse_body_sections`) populating the `objective` / `results` / `review_notes` views.

## Results

The data layer is split across two stdlib-only modules (no PyYAML dependency): `skills/task-tree/scripts/_task_io.py` (parse/serialize, walk, rollup, frontier, path resolution) and `skills/task-tree/scripts/_task_validate.py` (the validation suite).

### Key Findings
- The status-validity rule has exactly one message source, `_task_validate.invalid_status_message`, consumed by `parse_task`'s lenient warning (lazy import to avoid a module cycle), `validate_frontmatter`, and `task_check.check_status_validity`.
- The `Task` dataclass carries computed properties (`is_leaf`, `is_root`, `slug`) and `effective_status()`. The frontmatter field set is closed (documented in `skills/task-tree/references/task-file-contract.md`); `serialize_frontmatter` writes only the canonical fields.
- The custom frontmatter parser handles scalars, inline lists, and multi-line lists; `~` normalizes to `""`; inline-list splitting respects quoted commas. CRLF endings and a UTF-8 BOM are stripped before frontmatter matching; an unmatched `---` body emits a `UserWarning`.
- `write_task` is atomic (temp file + `os.replace`), so the live dashboard's file watcher never reads a half-written `task.md`.
- `walk_plan()` builds the tree by recursively scanning subdirectories, topologically sorted by `depends_on` (Kahn's algorithm via `_topological_sort`); a per-file `(OSError, UnicodeDecodeError)` is caught and warned so one bad file does not abort the walk. `parse_task` errors on a task dir outside the supplied `plan_root` rather than masquerading as the root.
- `compute_frontier()` handles nested DAGs — sibling deps checked at each level, ancestor readiness propagated; the synthetic `(no root task.md)` placeholder root is excluded, while a real childless root stays dispatchable.
- Status rollup excludes parked children (archived/postponed): all-approved → any-revise → any-in-progress/implemented → any-approved → not-started.
- `parse_body_sections()` is a fence-aware split on `^## (.+)$` headers; the section views delegate to it so header matching is identical everywhere.

### Accepted Limitations
- `propagate_parent_status` re-walks the ancestor subtree per ancestor, making each mutation O(n·depth) file reads. Accepted per orchestrator adjudication: at current tree sizes the cost is negligible, and a walk-once refactor touches the propagation path every mutation depends on.
