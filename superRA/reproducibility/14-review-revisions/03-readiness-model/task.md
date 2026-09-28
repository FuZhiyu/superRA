---
title: "One Readiness Rule and No False Task Cycles"
status: not-started
depends_on: []
---

## Objective

Whether a task can start, and whether the graph is valid, follow one rule a researcher can predict, and no error or grouping artifact blocks work it does not concern.

Terms used below:

- The task graph combines **logical** prerequisites written in `depends_on` with **inferred** edges, where one task's step reads a file another task's step writes.
- The **frontier** lists the tasks ready to start.
- **Preflight** is the validation a tree-changing command (`task create`, `task move`, `task dep add`) runs on the resulting graph before writing.

### An error blocks only what it concerns

- **A reproduction error blocks only the steps and tasks it touches.** One unset environment variable in `config.yaml` makes `task frontier`, `task create`, `task move`, and `task dep add` all refuse to run. `build_graph` in [_repro.py](../../../../skills/task-tree/scripts/_repro.py) folds every reproduction error into the graph's validity, and `preflight` in [_task_snapshot.py](../../../../skills/task-tree/scripts/_task_snapshot.py) rejects errors that existed before the edit. On a Dropbox project used from three machines, a variable set on only one of them freezes planning on the other two.
  - Preflight rejects only errors the edit introduces.
  - Validity counts only errors that change dependencies.
  - The frontier degrades only for the tasks an error touches.

### Parent-owned steps never create false cycles

- **A parent task's own steps stay separate nodes at every level of the hierarchy,** as the [0.5 design](../../attachments/v05-design.md#hierarchy-and-task-readiness) requires. `compose` in [_task_dependencies.py](../../../../skills/task-tree/scripts/_task_dependencies.py) keeps them separate one level up only; above that they merge into a single node for the parent, which causes:
  - **False cycles.** `paper` owns step `tables`, `robustness` reads it, and `paper/estimate` reads `robustness`'s output. The steps form no cycle, yet the graph reports `paper → robustness → paper` and the frontier empties.
  - **Over-blocking.** Parent P's step `report` reads `q.txt` from sibling Q, which blocks P's unrelated child `P/c`.

### One readiness rule

- **Every prerequisite is met by the same test** (decision below). Today there are two:
  - **Across branches, by status.** An `implemented` task whose output was never built unblocks its consumer.
  - **Parent to child, by step freshness.** Editing the parent's `setup.sh` drops the in-progress child `P/c` from the frontier and lists `P [own work: setup]` instead.
  - The frontier lists stale steps as "own work" for approved parents but never for approved leaves. In this repository it shows `scalable-navigation`'s two stale checks, while stale steps in the approved leaves `dag-design`, `02-agent-signals`, and `edit-detection` never appear.
- **Archiving a producer does not make a consumer with a missing input look ready.** Today the consumer enters the frontier, and `repro build --dry-run` then prints a failure and "Nothing to execute: every selected step is fresh" together.

### One computation behind every view

- **`task read`, the frontier, the DAG, `task check`, preflight, and the dashboard derive from one snapshot.** Duplicates remain:
  - Legacy code paths: `compute_frontier` and `_collect_frontier` in `_task_io.py` (used only by tests), `detect_cycles` and `validate_dependencies` in `_task_validate.py`, `print_frontier` in `task_query.py` (unused), and the dashboard's fallback to authored `depends_on`.
  - `task read` recomputes step status itself.
  - `task tree --json` builds the graph without resolving variables, so it always reports `effective_depends_on: null` and `dependencies_complete: false`.
- **Messages name the evidence.** Human-readable `task read` says why each prerequisite exists: logical, or inferred through which file. `dep remove` on an inferred-only edge says it is inferred and through which file, instead of "not in depends_on".
- **The failing test is resolved deliberately:** `test_bundle_fixture.py::test_task_read_json_carries_comments_and_dependency_status` (the dependency `slug` is now the full path).

### Validation

Each scenario above becomes a regression test on a scratch tree: the unset variable with `create`, `move`, and `dep add`; the `paper` chain; P's `report` reading Q; an `implemented` producer never built; an archived producer whose output is missing. The behavior that already works stays covered: inferred, logical, and dual-origin edges; unlinking a logical edge keeps the inferred one; grouping and mixed-source cycles produce witnesses; a cycle-creating move is refused with nothing written; a logical-only prerequisite does not pull its producer into `repro build`.

### Researcher decisions

- **The readiness rule.**
  - (a) Status everywhere: `implemented`, `approved`, or `revise` meets a prerequisite, and `repro status` reports stale or missing steps instead of the frontier. "Own work" leaves the frontier or lists only never-built steps.
  - (b) Freshness everywhere: a prerequisite is met only when its producing steps are fresh.
  - Recommendation: (a). Readiness to start work and freshness of results answer different questions. Either option revises the 0.5 design's rule that parent/child file dependencies use producer-step availability.
- **A subtask added to an approved producer.** The rollup, which computes a parent's status from its children, sends the producer back to `not-started` and blocks tasks that consume its unchanged files. Recommendation: keep the rollup, and have `task create` name the consumers it newly blocks.

Owning task: [unified-dependencies](../../01-section-contract/unified-dependencies/task.md).

## Details

Evidence for every item, with the scratch scenarios that reproduced it: [deps-report.md](../attachments/deps-report.md) M1–M4 and Minor. The unset-variable lock was also reproduced directly: with `OUT: {env: NOPE_UNSET_VAR}`, `task frontier` and `task create b` both failed with `config.yaml: variable 'OUT' reads environment variable 'NOPE_UNSET_VAR', which is not set`.
