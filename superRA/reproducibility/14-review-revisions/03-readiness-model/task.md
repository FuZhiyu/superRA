---
title: "One Readiness Rule and No False Task Cycles"
status: not-started
depends_on: []
---

## Objective

Task readiness and graph validity follow one explainable rule, and no reproduction error or grouping artifact blocks work it does not concern.

- **An error blocks only what it concerns.** One unset `env:` variable currently makes `task frontier`, `task create`, `task move`, and `task dep add` refuse: [_repro.py:1244-1247](../../../../skills/task-tree/scripts/_repro.py#L1244-L1247) folds every reproduction error into graph validity, and the `_task_snapshot` preflight rejects errors that predate the edit. Preflight rejects only errors the edit introduces; validity counts dependency-affecting errors; the frontier degrades only for affected tasks.
- **Parent-owned steps stay individual nodes at every hierarchy level**, as the [0.5 design §Hierarchy](../../attachments/v05-design.md#hierarchy-and-task-readiness) requires. [_task_dependencies.py:185-192](../../../../skills/task-tree/scripts/_task_dependencies.py#L185-L192) collapses them one level up, producing false cycles and over-blocking.
- **One readiness rule** across branch prerequisites, parent/child file edges, and own work (decision below).
- **Archiving a producer does not make a consumer with a missing input look ready.**
- **One snapshot, one computation.** Delete the legacy paths: `_task_io.compute_frontier` / `_collect_frontier`, the unused `dependencies=True` path through `_task_validate.detect_cycles` / `validate_dependencies`, `task_query.print_frontier`, and the dashboard's fallback to authored `depends_on` ([plan_dashboard.py:1000-1004](../../../../skills/task-tree/scripts/plan_dashboard.py#L1000-L1004)). `task read` stops recomputing step status. `task tree --json` reports real `effective_depends_on` and `dependencies_complete` instead of always `null` / `false` ([task_query.py:271](../../../../skills/task-tree/scripts/task_query.py#L271)).
- **Messages name the evidence.** Human `task read` says why each prerequisite exists (logical, or inferred through which file); `dep remove` on an inferred-only edge says it is inferred and from which file.
- **The failing test is resolved deliberately:** `test_bundle_fixture.py::test_task_read_json_carries_comments_and_dependency_status` (the dependency `slug` is now the full path).

### Researcher decisions

- **The readiness rule.** Recommendation: gate development by status everywhere (`implemented`, `approved`, `revise` satisfy), report stale or missing steps through `repro status` rather than the frontier, and drop `own-work` from the frontier or limit it to never-built steps. This revises the 0.5 design's "Internal parent/child file dependencies use their actual producer-step availability".
- **A subtask added to an approved producer.** The rollup sends the producer back to `not-started` and blocks consumers of unchanged files. Recommendation: keep the rollup, and have `task create` name the consumers it newly blocks.

Owning task: [unified-dependencies](../../01-section-contract/unified-dependencies/task.md).

## Details

Full evidence: [deps-report.md](../attachments/deps-report.md) M1–M4 and Minor.

- **Error lock (reproduced directly).** A scratch tree with `OUT: {env: NOPE_UNSET_VAR}` made both `task frontier` and `task create b` fail with `[ERROR] [reproduction] (root): config.yaml: variable 'OUT' reads environment variable 'NOPE_UNSET_VAR', which is not set`. On the researcher's three Dropbox-synced machines, a variable set on one machine freezes the tree on the other two.
- **False cycle.** `paper` owns step `tables`; `robustness` reads it; `paper/estimate` reads `robustness`'s output. The step graph is acyclic, but the grandparent level reports `paper → robustness → paper` and the frontier empties.
- **Over-blocking.** P's `report` step reads `q.txt` from sibling Q, which blocks P's unrelated child `P/c`.
- **Two readiness rules.** Across branches, an `implemented` task whose output was never built still unblocks its consumer. Parent to child, editing `setup.sh` drops the in-progress `P/c` from the frontier and shows `P [own work: setup]`. In this repo, `task frontier` lists `scalable-navigation`'s two stale checks, while stale steps in approved leaves `dag-design`, `02-agent-signals`, and `edit-detection` never appear.
- **Archive.** Archiving a producer put its consumer on the frontier with its input missing; `repro build --dry-run` then printed a failure and "Nothing to execute: every selected step is fresh" together.
- **What already works:** inferred, logical, and dual-origin edges; unlinking a logical edge keeps the inferred one; grouping and mixed-source cycles produce witnesses; a cycle-creating move is refused with nothing written; a logical-only prerequisite does not pull its producer into `repro build`.
