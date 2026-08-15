# Build the Task Tree & Self-Review

Load when entering **Phase 3** (design & task decomposition) and for the **Phase 4** self-review. This file is construction mechanics and the review gate; design judgment — placement, splitting, context distillation, objective/guidance writing — lives in `task-tree-design.md`; the canonical `task.md` contract in `task-tree/references/task-file-contract.md`.

## Artifact Pipeline

**Map the artifact pipeline before defining tasks:** which scripts/notebooks/documents get created (one per logical phase, per any domain artifact-format guidance), their inputs, where outputs go. Follow existing project directory conventions.

Artifacts planned inside a task directory follow `skills/using-superra/references/task-companion-files.md`.

**Walk the project guidance docs, then point to or distill each relevant convention into scoped objective context** per `task-tree-design.md` §Context Distillation.

**Pipeline file (required for multi-artifact work):** one committed entry point that reproduces every output from source — scripts in dependency order, failing fast (`set -e` or equivalent), updated whenever a script is added.

## Task Structure

**Each task is one logical unit of work with full discipline applied.** The active domain skill defines that discipline. Documentation is written continuously alongside the work, not as a separate task.

Objective writing, task splitting: `task-tree-design.md` §Writing Objectives and Details, §Splitting Tasks.

## Creating Tasks

**Create the task-tree wrapper first** — the committed `<task-root>/superra` must exist before any subagent is dispatched. Fresh project: the first call goes through the loaded task-tree skill directory (`<skill-dir>` = the directory holding its `SKILL.md`); commit the wrapper with the tree:

```bash
uv run --script <skill-dir>/scripts/cli.py wrapper init   # writes superRA/superra
```

Afterward every call uses `./superRA/superra …` (mutation commands: `task-tree/references/commands.md`), or create directories and write `task.md` files directly (`task-tree/SKILL.md` §Task File Format).

## Task Dependencies

`depends_on:` frontmatter lists sibling directory names; semantics in `task-tree/references/task-file-contract.md` §Task Anatomy and `task-tree-design.md` §Parent and sibling context.

Mark independent branches for parallel dispatch (`agent-orchestration` §Workload Balancing). Siblings sharing an edit surface are not a dependency case — merge them (`task-tree-design.md` §Splitting Tasks).

## Task Anatomy

Canonical structure and field-by-field notes: `task-tree/references/task-file-contract.md`. Domain-specific top-level objective context: the domain skill's planning reference.

## Create the `superRA/` Directory

1. A shared `## Objective` / `### Context` genuinely spans every top-level task (`task-tree/references/task-file-contract.md` §Tree Shape): create an umbrella `superRA/task.md` carrying the project-level goal, methodology, scope, and any project-wide `### Conventions` / `### Context` / `### Constraints` subsections. Otherwise skip it.
2. Create the top-level (and any nested) task directories with full objectives per §Task Structure.

## Self-Review

After writing the complete task tree:

1. **Domain survey coverage.** Domain skill produced a planning survey: every item in it has task coverage.
2. **Placeholder scan.** Vague objectives — "process the data", "clean up results", "finalize" without concrete success criteria — fixed.
3. **Pipeline consistency.** Artifact names in the pipeline file match each task's artifacts, in dependency order.
4. **Validation coverage.** Every transformative task has a validation criterion in its objective.
5. **Objective/details split.** Contract in `## Objective`; planning findings and suggested route in `## Details` (`task-tree-design.md` §Writing Objectives and Details).
6. **Handoff test.** A new agent reading any leaf's ancestor chain could continue from here.
7. **Verification coverage.** The tree covers the active domain skill's verification / robustness requirements.
8. **Dependency sanity.** Every task declares `depends_on:`; no cycles, no nonexistent siblings; terminal task(s) produce the top-line results.
9. **Granularity, both directions.** No task hides sub-steps that should be subtasks. No two siblings share an edit surface or would be written by one agent in one pass — merge those (`task-tree-design.md` §Splitting Tasks, "Do not split when").

Fix issues inline and move on; no re-review.
