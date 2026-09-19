---
title: "Unify Logical and Inferred Task Dependencies"
status: not-started
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
