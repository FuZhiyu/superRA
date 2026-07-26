# Task Decomposition & Self-Review

Load when entering **Phase 3** (design & task decomposition) and for the **Phase 4** self-review. Owns the mechanical detail of building the `superRA/` task tree and checking it before review. Task-tree design judgment — placement, splitting, context distillation, objective/guidance writing — lives in `task-tree-design.md`; the canonical file contract for `task.md` lives in `task-tree/references/task-file-contract.md`.

## Artifact Pipeline

Before defining tasks, map the artifact pipeline: which scripts/notebooks/documents will be created (one per logical phase, following any artifact-format guidance the domain skill loads), what their inputs are, and where outputs go. Follow existing project conventions for directory structure.

**Walk the project guidance docs, then point to or distill each relevant convention into scoped objective context** per `task-tree-design.md` §Context Distillation. Dispatched agents inherit this context via `superra task read`.

**Pipeline file (required for multi-artifact work):** When the work has more than one executable artifact, include a single committed entry point that reproduces every output from source — running scripts in dependency order, failing fast (`set -e` or equivalent), updated whenever a script is added.

## Task Structure

**Each task is one logical unit of work with full discipline applied.** The active domain skill defines that discipline. Documentation is written continuously alongside the work, not as a separate task.

For objective writing and task splitting, see `task-tree-design.md` §Writing Objectives and Planner Guidance and §Splitting Tasks.

## Creating Tasks

**First, create the task-tree wrapper.** Every downstream agent reads and edits tasks through the committed `<task-root>/superra` wrapper, so it must exist before any subagent is dispatched. A fresh project has no `superra` yet, so the first call goes through the loaded task-tree skill directory (`<skill-dir>` = the directory holding its `SKILL.md`) and is committed with the tree:

```bash
uv run --script <skill-dir>/scripts/cli.py wrapper init   # writes superRA/superra
```

Afterward every call uses `./superRA/superra …` (mutation commands: `task-tree/references/commands.md`), or create directories and write `task.md` files directly (`task-tree/SKILL.md` §Task File Format).

**No checkboxes.** Tasks do not contain step checkboxes (`- [ ]` / `- [x]`). If a step needs independent tracking and review, it becomes a subtask.

## Task Dependencies

Each task declares dependencies in its `depends_on:` frontmatter field (sibling directory names). See `task-tree/references/task-file-contract.md` §Task Anatomy and `task-tree-design.md` §Parent and sibling context for semantics.

Identify independent branches so the orchestrator can dispatch them in parallel (see `agent-orchestration` §Workload Balancing).

**After writing all tasks:** trace the dependency edges — no cycles, no references to nonexistent siblings; terminal task(s) produce the top-line results.

## Task Anatomy

For the canonical task structure — recursive task anatomy and field-by-field notes — see `task-tree/references/task-file-contract.md`. Domain-specific top-level objective context comes from the domain skill's planning reference.

## Create the `superRA/` Directory

1. If a shared `## Objective` / `### Context` genuinely spans every top-level task (`task-tree/references/task-file-contract.md` §Tree Shape), create an umbrella `superRA/task.md` carrying the project-level goal, methodology, scope, and any project-wide `### Conventions` / `### Context` / `### Constraints` subsections. Otherwise skip it.
2. Create the top-level (and any nested) task directories with full objectives per §Task Structure above.

## Self-Review

After writing the complete task tree:

1. **Domain inventory coverage (where applicable):** For domains with a planning hard gate, can you point to task coverage for every item in the inventory?
2. **Placeholder scan:** Search for vague objectives — "process the data", "clean up results", "finalize" without concrete success criteria. Fix them.
3. **Pipeline consistency:** Do the artifact names in the pipeline file match the artifacts created in each task? Are they in the right order?
4. **Validation coverage:** Does every transformative task have a corresponding validation criterion in its objective?
5. **Objective/guidance split:** See `task-tree-design.md` §Writing Objectives and Planner Guidance. The contract in `## Objective`; planning findings and suggested route in `## Planner Guidance`.
6. **Handoff test:** If you stopped here and a new agent read any leaf task's ancestor chain, could they continue? Is there enough context?
7. **Verification coverage (where applicable):** Does the task tree cover the active domain skill's verification / robustness requirements?
8. **Dependency graph sanity:** Every task has `depends_on:` declared. No cycles. Independent branches are marked parallelizable.
9. **Subtask coverage:** No task carries implicit sub-steps that should be separate subtasks.

Fix issues inline. No need to re-review — just fix and move on.
