---
title: "Core Data Layer"
status: implemented
depends_on: []
tags: []
script: skills/task-tree/scripts/_task_io.py
created: 2026-05-23
---

## Objective

Build `_task_io.py`: `Task` dataclass (path, title, status, depends_on, tags, script, input, output, created, body, children + body-derived section fields). YAML frontmatter parser (stdlib-only, no PyYAML). Serializer with canonical field order. Tree walker (`walk_plan`). Frontier computation (`compute_frontier`). Status rollup (`compute_status`). Body section parsing (`parse_body_sections`) populating `objective`, `results`, `decisions`, `revision_notes`, `review_notes` fields.

## Results

### Key Findings
- 873-line module, stdlib-only (no PyYAML dependency)
- `Task` dataclass with 17 fields + 3 computed properties (`is_leaf`, `is_root`, `slug`) and 1 method (`effective_status`)
- Custom YAML frontmatter parser handles scalars, inline lists, multi-line lists; `~` normalized to `""` at the scalar level
- `walk_plan()` builds full task tree by recursively scanning subdirectories topologically sorted by `depends_on` (Kahn's algorithm via `_topological_sort`); per-file `(OSError, UnicodeDecodeError)` caught and warned so one bad file does not abort the whole walk
- `compute_frontier()` handles nested DAGs — checks sibling deps at each level, propagates ancestor readiness
- Status rollup: parked children (archived/postponed) excluded; all-approved → any-revise → any-in-progress/implemented → any-approved → not-started
- `parse_body_sections()` fence-aware split on `^## (.+)$` headers into `{name: content}` dict; `objective`, `results`, `decisions`, `revision_notes`, `review_notes` fields are read-only views; `_has_nonempty_section` delegates to `parse_body_sections` so header matching is identical in both places
- CRLF line endings and UTF-8 BOM stripped before frontmatter matching; unmatched `---` body emits a `UserWarning`

## Review Notes

1. **MAJOR** — [_task_io.py:345](../../../skills/task-tree/scripts/_task_io.py#L345) — Stale `## Objective`: it lists "review/integration status" among the `Task` dataclass fields, but those fields were removed (`parse_task` now silently ignores `review_status`/`integration_status` in old files; `TestUpgradeStatus::test_strips_review_and_integration_status` strips them on migration). Fix: planner rewrites the field list in place per the Stale Content Checklist.
   → implemented: rewrote `## Objective` field list in place, removing "review/integration status" and reflecting current 17-field `Task` ([core-data-layer/task.md](task.md))
2. **MAJOR** — [_task_io.py:86](../../../skills/task-tree/scripts/_task_io.py#L86) — Stale `## Results` on nearly every line: `Task` has 17 fields, not 18 (verified via `dataclasses.fields`), and 3 computed properties — `effective_status` is a method; the module is 873 lines, not "400+"; the rollup description omits the archived/postponed exclusion rules and the any-approved→in-progress rule ([compute_status](../../../skills/task-tree/scripts/_task_io.py#L561)); the `parse_body_sections` description omits fence-awareness and the `revision_notes` field; "sorted subdirectories" omits the topological sort ([_walk_children](../../../skills/task-tree/scripts/_task_io.py#L520)). Fix: implementer refreshes `## Results` in place to describe the current module.
   → implemented: refreshed `## Results` in place with accurate line count, field count, rollup rules, fence-awareness, tilde fix, CRLF/BOM handling, topological sort, and per-file walk error containment ([core-data-layer/task.md](task.md))
3. **MAJOR** — [_task_io.py:719](../../../skills/task-tree/scripts/_task_io.py#L719) — God-module drift with a triplicated rule: the status-validity check now exists in three places with three message strings — `parse_task`'s warning ([_task_io.py:338](../../../skills/task-tree/scripts/_task_io.py#L338)), `validate_frontmatter` ([_task_io.py:719](../../../skills/task-tree/scripts/_task_io.py#L719)), and `check_status_validity` ([task_check.py:77](../../../skills/task-tree/scripts/task_check.py#L77)). The module spans root autodetection, parse/serialize, rename cascade, walk/toposort, path resolution, rollup, frontier, and a ~165-line validation suite. Fix: extract validation into its own module with one message source; one owner per concern.
4. **MINOR** — [_task_io.py:369](../../../skills/task-tree/scripts/_task_io.py#L369) — `write_task` rebuilds frontmatter from `Task` fields only while `parse_task` discards unknown keys, so any hand-added frontmatter key is silently destroyed by every CLI mutation (including each ancestor touched by `propagate_parent_status`); the extras loop in `serialize_frontmatter` ([_task_io.py:292](../../../skills/task-tree/scripts/_task_io.py#L292)) is dead code on this path. Fix: round-trip an extras dict, or state the closed field set in the task-file contract.
5. **MINOR** — [cli.py:218](../../../skills/task-tree/scripts/cli.py#L218), [task_update.py:84](../../../skills/task-tree/scripts/task_update.py#L84) — Inconsistent path resolution: `resolve_path` (root-prefix stripping + escape check) is used by `task_read`/`task_rename`/`task_comment`, but the CLI wrapper only validates with it and forwards the raw path to update/link/add-result/create, which do a bare `plan_root / task_path` join ([task_add_result.py:52](../../../skills/task-tree/scripts/task_add_result.py#L52), [task_link.py:57](../../../skills/task-tree/scripts/task_link.py#L57), [task_create.py:66](../../../skills/task-tree/scripts/task_create.py#L66)). So `superra task update --path superRA/foo` passes validation then fails "task not found", and invoking those scripts directly bypasses the escape check (`--path ../../x` resolves). Fix: route all mutators through `resolve_path`.
6. **MINOR** — [_task_io.py:131](../../../skills/task-tree/scripts/_task_io.py#L131) — Tilde handling contradicts the Results claim: `_parse_yaml_value` returns the literal string `"~"` for scalars (only `_to_list` coerces it), so `script: ~` yields `Task.script == "~"`, which is truthy and round-trips as a bogus value. Fix: map `~` to `""` at the scalar level.
   → implemented: `_parse_yaml_value` now maps `~` to `""` at the scalar level; updated `test_tilde_value` to assert `== ""` ([_task_io.py](../../../skills/task-tree/scripts/_task_io.py))
7. **MINOR** — [_task_io.py:396](../../../skills/task-tree/scripts/_task_io.py#L396) — `write_task` is non-atomic (direct `write_text`, no tmp+rename): the live dashboard's file watcher can read a half-written `task.md`, and an interrupted `propagate_parent_status` leaves mixed ancestor statuses. Fix: write to a temp file and rename.
8. **MINOR** — [_task_io.py:594](../../../skills/task-tree/scripts/_task_io.py#L594) — `propagate_parent_status` re-walks the entire ancestor subtree for each ancestor (the root pass re-parses every file), making each mutation O(n·depth) file reads; the single-condition `changed` flag is vestigial. Fix: walk once and reuse the parsed tree.
9. **MINOR** — [_task_io.py:470](../../../skills/task-tree/scripts/_task_io.py#L470) — Edge behaviors: a fabricated root ("(no root task.md)", default `not-started`) with no children is itself returned as a frontier task by `_collect_frontier`; and in `parse_task` ([_task_io.py:324](../../../skills/task-tree/scripts/_task_io.py#L324)) a task dir outside the supplied `plan_root` falls back to `path == ""`, masquerading as root instead of erroring. Inline-list parsing also splits quoted commas ([_task_io.py:135](../../../skills/task-tree/scripts/_task_io.py#L135): `["a, b", "c"]` → three items). Fix: exclude synthetic roots from the frontier, error on out-of-root parses, and respect quotes when splitting.
