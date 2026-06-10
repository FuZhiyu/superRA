---
title: "Core Data Layer"
status: approved
depends_on: []
tags: []
script: skills/task-tree/scripts/_task_io.py
created: 2026-05-23
---

## Objective

Build `_task_io.py`: `Task` dataclass (path, title, status, depends_on, tags, script, input, output, created, body, children + body-derived section fields). YAML frontmatter parser (stdlib-only, no PyYAML). Serializer with canonical field order. Tree walker (`walk_plan`). Frontier computation (`compute_frontier`). Status rollup (`compute_status`). Body section parsing (`parse_body_sections`) populating `objective`, `results`, `decisions`, `revision_notes`, `review_notes` fields.

## Results

### Key Findings
- Data layer split across two stdlib-only modules (no PyYAML dependency): [_task_io.py](../../../skills/task-tree/scripts/_task_io.py) (772 lines — parse/serialize, walk, rollup, frontier, path resolution) and [_task_validate.py](../../../skills/task-tree/scripts/_task_validate.py) (186 lines — the validation suite)
- The status-validity rule has exactly one message source: `_task_validate.invalid_status_message` — consumed by `parse_task`'s lenient warning (lazy import to avoid a module cycle), `validate_frontmatter`, and `task_check.check_status_validity`
- `Task` dataclass with 17 fields + 3 computed properties (`is_leaf`, `is_root`, `slug`) and 1 method (`effective_status`)
- Custom YAML frontmatter parser handles scalars, inline lists, multi-line lists; `~` normalized to `""` at the scalar level; inline-list split respects quoted commas (`["a, b", c]` → two items)
- The frontmatter field set is closed (documented in [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md)); `serialize_frontmatter` writes only canonical fields, and the formerly dead extras loop is deleted
- `write_task` is atomic: temp file + `os.replace`, so the live dashboard's file watcher never reads a half-written `task.md`
- `walk_plan()` builds full task tree by recursively scanning subdirectories topologically sorted by `depends_on` (Kahn's algorithm via `_topological_sort`); per-file `(OSError, UnicodeDecodeError)` caught and warned so one bad file does not abort the whole walk
- `parse_task` errors on a task dir outside the supplied `plan_root` instead of silently masquerading as the root
- `compute_frontier()` handles nested DAGs — checks sibling deps at each level, propagates ancestor readiness; the synthetic `(no root task.md)` placeholder root is excluded (a real childless root remains dispatchable)
- Status rollup: parked children (archived/postponed) excluded; all-approved → any-revise → any-in-progress/implemented → any-approved → not-started
- `parse_body_sections()` fence-aware split on `^## (.+)$` headers into `{name: content}` dict; `objective`, `results`, `decisions`, `revision_notes`, `review_notes` fields are read-only views; `_has_nonempty_section` delegates to `parse_body_sections` so header matching is identical in both places
- CRLF line endings and UTF-8 BOM stripped before frontmatter matching; unmatched `---` body emits a `UserWarning`

### Accepted Limitations
- `propagate_parent_status` re-walks the ancestor subtree per ancestor, making each mutation O(n·depth) file reads. Accepted per orchestrator adjudication: at current tree sizes the cost is negligible, and a walk-once refactor touches the propagation path every mutation depends on — risk outweighs benefit.

