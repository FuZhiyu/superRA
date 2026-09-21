# superRA 0.5: one dependency model, selective reproduction

## One task DAG combines both sources of dependency

Across disjoint task groups, a consumer task depends on another task when it consumes an output produced by that task, or when its authored `depends_on` names a logical prerequisite. Parent/child containment is expanded internally under the hierarchy rule below, not emitted as a parent self-dependency. The effective task DAG is the union of these relationships. Inferred edges are computed, never copied into frontmatter; one edge retains every source of evidence. Existing `depends_on` sibling-slug syntax remains compatible.

The step graph supplies execution detail inside this hierarchy. Reject step cycles, task cycles produced by grouping an acyclic step graph, and cycles that arise only when inferred and logical edges are combined. Report a concrete cycle with task paths, step names, connecting files, and authored logical declarations. Correct erroneous declarations or restructure task boundaries; never remove a true consumed-artifact edge to make validation pass.

### Hierarchy and task readiness

A task may own steps and contain subtasks. Adding a child does not relocate existing steps, change their identifiers or hashes, or require a migration solely because the owner became a parent. Collapsing a task hides internal edges; only dependencies crossing its boundary remain.

At each hierarchy boundary, project cross-branch dependencies onto sibling task groups and reject cycles in their combined inferred/logical ordering. Map each endpoint to its direct child group or, for work owned by the containing task, its individual step. An edge with both endpoints inside the same collapsed child stays internal to that child; retain it when that child expands. Within a parent, retain its own steps as individual nodes alongside child task groups: parent setup → child task → parent report is valid when the internal graph is acyclic. Never collapse all parent-owned steps into a single virtual prerequisite that fabricates a cycle, and never infer a parent task depends on itself from an internal file edge. Cross-boundary A → B → A between disjoint task groups remains invalid.

Explicit logical and inferred cross-branch prerequisites gate task development through the same effective graph and existing status policy: `implemented`, `approved`, and `revise` satisfy an active prerequisite; `not-started`, `in-progress`, and `postponed` block. A branch prerequisite applies to descendant work. Internal parent/child file dependencies use their actual producer-step availability, not the containing parent's rolled-up status: a child must not wait for a parent whose completion already includes that child. When parent-owned prerequisite work is missing or stale, the frontier exposes the blocking owner and steps as actionable own work instead of silently omitting them. This is derived context, not a new authored dependency list or persistent own-work status.

Preserve task-status and freshness meanings: adding children uses the existing child-status rollup, while source edits and acceptance do not silently rewrite workflow status. Reproduction validity and required output verification remain additional completion evidence; an approved task status alone cannot certify its outputs.
Reproduction replays declared scripts from their actual file dependencies. Logical prerequisites govern task development, not the replay of an already implemented calculation: they do not add artificial file inputs, invalidate hashes, or pull unrelated scripts into a targeted build. Full and targeted builds still reject an invalid combined task graph before running. Tasks with no reproduction steps remain first-class nodes in the task DAG.

### Archived tasks leave the active graph

Exclude archived tasks and their subtrees from the active task/step DAG, counts, frontier, and automatic build selection; dependency closure must not pull their steps back in. Warn active downstream tasks, including transitive dependents, naming the archived prerequisite and the dependency path or file evidence. Archival alone is a warning, not a blocking dependency or a cycle error. Retain declarations and provenance for diagnostics; consumed files from archived producers remain boundary inputs subject to normal existence/content checks, so a missing required file still prevents execution.

### One shared snapshot

Compose effective dependencies from a parsed tree and resolved step edges in a pure module, separate from filesystem walking. Task read, frontier, DAG, dependency validation, mutation preflight, and dashboard payloads consume the same snapshot and edge evidence.

Resolve configured paths once per command; preserve existing resolved-path alias matching. Resolution or parsing failures must not advertise a complete or actionable graph. Structural tree inspection remains available for repair. Hook relevance scans stay free of shell evaluation; dependency-changing explicit CLI operations perform the authoritative preflight. Invalid direct file edits remain readable and report errors.

Removing an explicit prerequisite removes only that evidence: an inferred edge can remain. Renames and moves recompute inferred ownership and validate the resulting hierarchy before committing writes. Preserve the existing reviewable handling of logical edges stranded by a cross-parent move. No mutation silently deletes dependencies to repair a cycle.

## Task and step views expand the same hierarchy

Integrate dependencies into the task workspace: `Tree` and `DAG` are alternative navigators sharing task selection, the task reader, comments, and attachments. Remove the separate reproduction destination, overview tree, and subtree picker. Selection, one-level expansion/folding, and subtree focus are distinct actions; selection and expansion do not change scope. DAG mode gives the graph the main canvas beside the shared reader. Preserve nested expansion choices and navigator-specific positions when switching modes. The [navigation contract](../04-dashboard-view/scalable-navigation/attachments/design.md) owns interaction details and legacy-link compatibility.

The dashboard begins with task nodes and their effective dependencies. Expanding a task exposes its steps and the file connections supporting those edges; mixed expansion keeps other tasks compact. Logical-only edges remain labeled connections between task boundaries, including tasks with no steps. They are never fabricated into step-level file edges.

Use compact containers with task titles and per-state counts, readable initial scale, and explicit Fit overview. Keep step names readable, route directional edges around cards, and emphasize the selected connection chain. Opening the inspector keeps selection visible. Preserve search, history, worktree isolation, keyboard/touch support, and offline export from the [navigation contract](../04-dashboard-view/scalable-navigation/attachments/design.md).

Filtering changes the view, not validity. Retain hidden prerequisite markers and global cycle diagnostics. Invalid graphs remain inspectable, with links to their declarations; do not present them as an executable DAG. Findings must distinguish omitted malformed steps from validly parsed steps involved in a cycle.

## Narrow dependencies before accepting stale results

Keep conservative content hashing and transitive include tracking. Split helper modules by consumer set and separate estimation specifications from presentation settings. Consumers include only the modules they execute. Downstream presentation consumes saved estimates rather than importing estimation code solely for provenance.

For a shared specification, a cheap producer can emit deterministic per-consumer configuration artifacts. Consumers depend on their own artifact; an unrelated specification edit reruns the cheap producer and unchanged artifact bytes stop the cascade. Do not retain the monolithic source as a redundant downstream dependency unless the consumer actually reads it. Do not introduce function-level hashing or dependency exclusions as a substitute for correct inputs.

`repro impact <path...>` reports direct consumers, transitive affected steps, and why each file is tracked (declared dependency, script, include closure, or environment input). It supports JSON and scope selection without concealing affected steps outside the scope. Impact is a conservative invalidation prediction, not a claim that every output value will change. Extend `explain` to distinguish a step's own changes from upstream uncertainty and to locate the baseline when source diffs can be recovered.

## Reviewed acceptance is evidence distinct from execution

`repro accept` establishes or replaces the reviewed current baseline, including newly registered producers and changed outputs from direct runs. Require a reason; evidence files and per-node notes are optional. Preserve exact preview/apply, revoke, saved-input scope, downstream invalidation, forced execution, and truthful execution history. Never-run checks still require execution.

The [acceptance task](../02-runner/reviewed-acceptance/task.md) owns implementation and validation. The [record contract](../../../skills/task-tree/references/task-file-contract.md#acceptance-and-successful-baseline-records) defines persistence; the [reproducibility skill](../../../skills/reproducibility/SKILL.md#build-and-status) owns agent behavior. Acceptance introduces no additional user-confirmation gate within authorized work.

## Verification and upgrade

| Fixture or journey | Required evidence |
| --- | --- |
| No reproduction declarations | Existing logical dependency syntax and frontier behavior remain compatible |
| Archived prerequisite or subtree with active direct/transitive consumers | Archived nodes stay excluded; downstream warnings retain provenance; existing boundary inputs remain usable and missing inputs still block execution |
| Inferred-only, logical-only, and duplicate-origin edge | CLI and UI agree; one edge retains both reasons; unlinking logical evidence preserves an inferred edge |
| Step cycle, owner cycle with acyclic steps, mixed-source cycle, parent-branch cycle | Actionable cycle witness; no dispatch or build bypass through target selection |
| Add a subtask to a task with existing steps; parent setup → child → parent report; umbrella-root work | No ownership/hash migration or self-blocking; valid internal ordering stays valid; missing own work is actionable |
| Parsing/resolution failure and dependency-changing move | Repair remains possible; no falsely ready frontier or partial CLI mutation |
| Shared helper and split configuration fixture | Impact explains fan-out; unrelated edits leave independent consumers untouched; identical derived configuration stops reruns |
| Reviewed harmless edit | Ordinary build skips accepted producers, runs independently dirty descendants, and preserves lock and last-run evidence |
| Subsequent dep/spec/output edit, revoke, missing file, failed force, concurrent change | Acceptance cannot hide staleness/failure or install a stale decision |
| Forced build, parallel build, dry-run, older lock | Correct scope and engine behavior; no fake successful execution or unintended descendant skipping |
| Live dashboard and offline export | Task/step/mixed views agree; accepted evidence, invalid graphs, scope, and selection survive navigation and refresh |

The 0.5.0 manifests identify the development release. Publication waits for the runtime, UI, and workflow work; the version bump does not assert that planned behavior has shipped. Existing approvals document the earlier implementation, not verification of these changes. File-open tracing remains postponed; real-project use replaces a dedicated compatibility pilot.

## Decision basis

The researcher selected automatic task dependencies plus logical prerequisites, task-level cycle rejection, expandable task/step views, and treating reviewed acceptance as fresh. Parent-owned steps remain supported so adding a subtask does not invalidate existing work. The separation of task-development prerequisites from file-driven script replay is the proposed implementation default; it preserves selective reruns without inventing executable steps for logical decisions.
