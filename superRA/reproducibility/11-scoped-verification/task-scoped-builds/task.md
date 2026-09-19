---
title: "Build selected tasks against saved inputs by default"
status: not-started
depends_on: []
---

## Objective

Implement one task/step selection contract for reproduction build, status, and preview: execute only the selected steps by default, expand to upstream producers explicitly, and report scoped success separately from upstream freshness. The [CLI and evidence design](attachments/design.md) defines the contract and identifies the remaining researcher preferences to settle before implementation.

- Preserve the complete declared graph, step identities, and existing successful-run evidence. A run boundary never rewrites dependencies or accepts a stale producer as fresh.
- Cover the CLI, engine bridge, scoped evidence, task-reader/dashboard reporting, workflow loads and completion gates, documentation, and migration under the design's ownership map. Register executable support for retained results by default, including interactive work and initially unconfigured trees.
- Verify the design's behavioral matrix in disposable fixtures and one isolated existing-project pilot; record actual commands executed, boundary fingerprints, build/status agreement, and unchanged-run latency. No project-wide analysis runs during development of this feature.

## Details

This is one update task because target resolution, execution nodes, status propagation, receipts, and their public contract share an edit surface. The existing scoped-verification task covers this concern; a separate top-level reproduction task would duplicate it. Fold the outcome into that parent and the durable owning tasks at integration.

- [Selection and status](../../../../skills/task-tree/scripts/_repro_state.py) always add producer ancestors today. [Runner](../../../../skills/task-tree/scripts/repro_run.py) separately calculates direct targets for force; [acceptance propagation](../../../../skills/task-tree/scripts/_repro_acceptance.py) lifts locally fresh steps to stale when upstream is stale. Selection alone is insufficient: successful local execution needs an explicit evidence scope.
- [Dependency contract](../../../../skills/task-tree/references/task-file-contract.md#effective-dependencies) keeps logical task prerequisites separate from executable file edges. Preserve its global validation and task-readiness rules.
- Baseline selection/force checks passed six cases in [runner tests](../../../../skills/task-tree/scripts/test_repro_runner.py); they exercise the existing behavior and must be revised with the new contract. They do not validate the proposed default.
- The working tree contains unrelated task-link and DAG UI edits. Coordinate changes to shared task-tree files when implementation starts.

## Results

[Design and acceptance matrix](attachments/design.md) record the proposed CLI, saved-input boundary, reporting, migration, and workflow integration. Implementation has not started. The design is hand-authored from the researcher discussion and inspection of the linked parser, runner, status, and workflow owners.
