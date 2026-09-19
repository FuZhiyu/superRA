---
title: "Unify Logical and Inferred Task Dependencies"
status: approved
depends_on: []
---

## Objective

Ship the effective dependency graph and its task-tooling consumers under the [0.5 design](../../attachments/v05-design.md#one-task-dag-combines-both-sources-of-dependency). Task ordering, readiness, validation, read context, and dashboard data must agree without duplicating inferred dependencies in authored metadata.

- Support parent-owned steps and nested task groups, including adding a child without changing existing step identities or freshness. Expose blocked parent-owned work without a parent/child readiness deadlock.
- Preserve dependency provenance and diagnose step, sibling-group, mixed-source, and parent-boundary cycles. Filtering, explicit build targets, or incomplete parsing must not bypass invalidity.
- Apply the [archived-task rule](../../attachments/v05-design.md#archived-tasks-leave-the-active-graph): exclude archived work from the active graph and warn its active downstream dependents.
- Make dependency-changing CLI operations preflight the proposed effective graph; retain readable diagnostics for direct file edits. Preserve no-reproduction compatibility and resolved-path matching without introducing recursive imports or repeated shell probes.
- Own the dependency-related schema/CLI reference updates and the graph portion of the [verification matrix](../../attachments/v05-design.md#verification-and-upgrade). Exercise public commands against realistic temporary trees, not just private graph functions.

## Details

- **Runtime ownership:** [_task_io.py](../../../../skills/task-tree/scripts/_task_io.py), [_repro.py](../../../../skills/task-tree/scripts/_repro.py), a pure dependency-composition module, task read/query/check/link/create/move and hook consumers, and task-related API payloads in [plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py). Keep the state/runner changes in [reviewed acceptance](../../02-runner/reviewed-acceptance/task.md).
- **Mechanics references:** [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md), [commands.md](../../../../skills/task-tree/references/commands.md), and [internals.md](../../../../skills/task-tree/references/internals.md). Workflow prose is owned by [workflow integration](../../07-workflow-integration/unified-dependency-workflow/task.md).
- The existing walker sorts explicit siblings before reproduction is built; [_repro.py](../../../../skills/task-tree/scripts/_repro.py) imports task parsing. Compose after parsing rather than importing reproduction back into the walker.
- The graph currently exposes exact owner edges and only warns against opposite sibling order. Dependency-query clients need one resolved snapshot; structural repair paths and hook relevance scans must remain available without running shell configuration.
- Retain enough dependency-origin evidence for `repro impact` to explain script, declared, include-closure, and environment dependencies. Shared Python files belong to this task until its graph interface lands; downstream tasks consume that interface.

## Results

- [The pure dependency snapshot](../../../../skills/task-tree/scripts/_task_dependencies.py) combines logical declarations with inferred file edges at every parent boundary, preserves provenance, excludes archived subtrees, and exposes actionable parent-owned steps. Parent setup → child → parent report keeps individual step identities and avoids a status-rollup deadlock.
- [Graph assembly](../../../../skills/task-tree/scripts/_repro.py), [task adapters](../../../../skills/task-tree/scripts/_task_snapshot.py), and the read/query/check/mutation/dashboard consumers share that snapshot. Explicit dependency mutations preflight proposed trees; archived names and outputs cannot shadow active producers. Structural tree inspection remains shell-free and labels effective dependency data unavailable.
- [Command-level fixtures](../../../../skills/task-tree/scripts/test_task_dependencies.py) cover inferred/logical/mixed edges, step and collapsed-group cycles, targeted-build rejection, archived direct/transitive dependencies, create/link/move/resume preflight, single variable resolution, incomplete parsing, and an actual parent/child build that preserves the already-built setup step's freshness and last-run record.
- Verification: the task-tree suite passed **1,080 tests, 9 skipped** with pytask and dashboard dependencies installed. The final graph/model regressions and runner/CLI regressions each passed **118 tests**; the real parent/child build passed independently. The repository's live-source `task check --category dependency --json` reported zero findings. Mechanics are documented in [the task contract](../../../../skills/task-tree/references/task-file-contract.md#effective-dependencies), [commands](../../../../skills/task-tree/references/commands.md), and [internals](../../../../skills/task-tree/references/internals.md#effective-dependency-snapshot).
