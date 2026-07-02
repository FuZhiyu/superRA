---
name: superplan
description: "Proactively plan or update superRA work. Requires superRA:using-superra. Use when starting or changing work, creating/revising superRA/, or reflecting material decisions in the task tree."
---

# superplan — the PLAN phase

**First, load `superRA:using-superra` if not already loaded.**

**If the harness has activated plan mode, load `references/harness-plan-mode.md` before proceeding.**

## Overview

Owns the procedural shape of the **PLAN** phase: discovery of existing work, exploration, domain setup, task decomposition, self-review, and handoff. Output is a `superRA/` task tree for superimplement to consume.

The `## Objective` / `## Planner Guidance` split — binding vs. suggested content — is in `references/task-tree-design.md` §Writing Objectives and Planner Guidance.

Task-tree design judgment — placement, task splitting, context distillation, update-task lifecycle, and retroactive task-tree creation — lives in `references/task-tree-design.md`.

**Announce at start:** "I'm using the superplan skill to create the task tree."

**Output location:** `superRA/` at the worktree root if in a worktree, otherwise the project root, unless the user specifies elsewhere. Commit the task tree before execution.

## Entry Assessment

Before exploration or task design, assess three independent dimensions of the incoming work. Creating a task tree and updating one both pass through the same assessment.

**1. Placement — where it goes.** If `superRA/` exists, place work by `references/task-tree-design.md` §Placing Work in the Existing Tree. If not, check for a legacy `PLAN.md` (offer migration via `task-tree` §Migration) and otherwise create the work as the first top-level task under `superRA/`.

**2. Depth tier — how deep.** Choose a tier (§Depth Tiers) that modulates how deeply the later phases run.

**3. Routing path — what mode.** Forward planning is the default. The one alternative is **retroactive documentation** — existing code/results need a `superRA/` record, detected when the work has code without task coverage; it runs the same phases (see `references/task-tree-design.md` §Retroactive Task-Tree Creation). Structural cleanup of an existing tree is not a routing mode — it is the separate `references/consolidation.md` pass, entered when the tree has structural debt rather than when new work needs placing.

**Ask when unclear.** When the tree and project context leave placement or depth ambiguous, present the concrete options (the candidate placements from the descent, or standard vs. thorough depth) with a one-line rationale each rather than guessing — wrong placement creates rework, wrong depth wastes effort or misses complexity.

## Depth Tiers

A spectrum, not rigid modes — escalate mid-planning if complexity warrants. The tier mainly modulates Phase 1; Phases 2-3 scale with it; Phase 4 is identical except thorough adds an agent review step (§Agent Review).

**Quick** — minor updates, known additions, single-task changes (an objective rewrite after a scope revision, a well-understood subtask, a dependency adjustment). Light scan of `superRA/`, skip deep exploration, design inline.

**Standard** (default) — new workstreams in familiar territory, a significant new branch, satisfying domain hard gates. Main agent explores project structure, loads the domain skill, designs tasks.

**Thorough** — complex or unfamiliar projects, large scope spanning multiple codebase areas, or an explicit request ("plan hard", "explore thoroughly", "detailed plan"). Dispatch parallel exploration agents before task design per `references/thorough-planning.md`. Competing designs returned by multiple agents are a natural source of substantive questions for the user (§Substantive Questions).

## Phase 1: Exploration

Read project structure, existing code, data directories, documentation, `CLAUDE.md`/`README.md` files, and git history for relevant prior work, scaled to the chosen tier (quick: scan the tree neighborhood where the work lands; standard: systematic exploration of the relevant areas; thorough: parallel exploration agents per `references/thorough-planning.md`). The domain hard-gate data gathering (data inventory, model primitives survey, manuscript assessment) begins here, though the phase itself is domain-neutral.

Revisit the entry assessment if exploration shows placement or depth needs adjustment.

## Phase 2: Domain Setup & Scope

Identify the domain of the work and load the matching domain skill's planning reference, which carries the domain's hard gates and templates.

**Stop here, load the matching domain skill, follow its planning-stage reference per its own stage-load table, and satisfy its planning hard gate before returning to Phase 3.** The researcher must approve the domain skill's planning-stage inventory artifact before any task structure is drafted.

If the task is in a domain without an implemented domain skill: proceed to Phase 3, but flag the gap to the researcher.

## Phase 3: Design & Task Decomposition

### Artifact Pipeline

Before defining tasks, map the artifact pipeline: which scripts/notebooks/documents will be created (one per logical phase, following any artifact-format guidance the domain skill loads), what their inputs are, and where outputs go. Follow existing project conventions for directory structure.

**Walk the project guidance docs, then point to or distill each relevant convention into scoped objective context** per `references/task-tree-design.md` §Context Distillation. Dispatched agents inherit this context via `superra task read`.

**Pipeline file (required for multi-artifact work):** When the work has more than one executable artifact, include a single committed entry point that reproduces every output from source — running scripts in dependency order, failing fast (`set -e` or equivalent), updated whenever a script is added.

### Task Structure

**Each task is one logical unit of work with full discipline applied.** The active domain skill defines that discipline. Documentation is written continuously alongside the work, not as a separate task.

For objective writing and task splitting, see `references/task-tree-design.md` §Writing Objectives and Planner Guidance and §Splitting Tasks.

### Creating Tasks

**First, create the task-tree wrapper.** Every downstream agent reads and edits tasks through the committed `<task-root>/superra` wrapper, so it must exist before any subagent is dispatched. A fresh project has no `superra` yet, so the first call goes through the loaded task-tree skill directory (`<skill-dir>` = the directory holding its `SKILL.md`) and is committed with the tree:

```bash
uv run --script <skill-dir>/scripts/cli.py wrapper init   # writes superRA/superra
```

Afterward every call uses `./superRA/superra …` (mutation commands: `task-tree/references/commands.md`), or create directories and write `task.md` files directly (`task-tree/SKILL.md` §Task File Format).

**No checkboxes.** Tasks do not contain step checkboxes (`- [ ]` / `- [x]`). If a step needs independent tracking and review, it becomes a subtask.

### Task Dependencies

Each task declares dependencies in its `depends_on:` frontmatter field (sibling directory names). See `task-tree/references/task-file-contract.md` §Task Anatomy and `references/task-tree-design.md` §Parent and sibling context for semantics.

Identify independent branches so the orchestrator can dispatch them in parallel (see `agent-orchestration` §Workload Balancing).

**After writing all tasks:** trace the dependency edges — no cycles, no references to nonexistent siblings; terminal task(s) produce the top-line results.

### Task Anatomy

For the canonical task structure — recursive task anatomy and field-by-field notes — see `task-tree/references/task-file-contract.md`. Domain-specific top-level objective context comes from the domain skill's planning reference.

### Create the `superRA/` Directory

1. If a shared `## Objective` / `### Context` genuinely spans every top-level task (`task-tree/references/task-file-contract.md` §Tree Shape), create an umbrella `superRA/task.md` carrying the project-level goal, methodology, scope, and any project-wide `### Conventions` / `### Context` / `### Constraints` subsections. Otherwise skip it.
2. Create the top-level (and any nested) task directories with full objectives per §Task Structure above.

## Phase 4: Review & Commit

### Self-Review

After writing the complete task tree:

1. **Domain inventory coverage (where applicable):** For domains with a planning hard gate, can you point to task coverage for every item in the inventory?
2. **Placeholder scan:** Search for vague objectives — "process the data", "clean up results", "finalize" without concrete success criteria. Fix them.
3. **Pipeline consistency:** Do the artifact names in the pipeline file match the artifacts created in each task? Are they in the right order?
4. **Validation coverage:** Does every transformative task have a corresponding validation criterion in its objective?
5. **Objective/guidance split:** See `references/task-tree-design.md` §Writing Objectives and Planner Guidance. Binding deliverables and constraints in `## Objective`; advisory hints in `## Planner Guidance`.
6. **Handoff test:** If you stopped here and a new agent read any leaf task's ancestor chain, could they continue? Is there enough context?
7. **Verification coverage (where applicable):** Does the task tree cover the active domain skill's verification / robustness requirements?
8. **Dependency graph sanity:** Every task has `depends_on:` declared. No cycles. Independent branches are marked parallelizable.
9. **Subtask coverage:** No task carries implicit sub-steps that should be separate subtasks.

Fix issues inline. No need to re-review — just fix and move on.

### Agent Review

At thorough depth, dispatch `Stage: planning-review` before presenting the tree to the user. Explicit handoff-review requests can enter the same step. Load `superRA:agent-orchestration` before writing the dispatch prompt.

**Planning reviewer:**
```
Agent(subagent_type: "superRA:reviewer"):
  Stage: planning-review
  Task: <task path or root>
  Review mode: handoff-readiness | design-review
  Context: <exploration synthesis, inline or path>
```

The two review modes are defined in `references/planning-review.md` §Review Mode.

REVISE findings must be fixed before proceeding to User Review — the user should see a structurally sound tree, not one with known issues.

Skip this step at quick and standard depth unless the user explicitly asks for a handoff review — the self-review checklist is sufficient when the main agent designed the tree itself without parallel exploration.

### User Review

Verify the task tree aligns with the user's intent. Present the tree (via `superra task tree`) and surface remaining open questions — design tradeoffs, unresolved ambiguities, choices that could reasonably go another way. Present tradeoffs as options, not assertions. If you have no genuine questions, the tree presentation itself is the review.

For each newly created task — especially a new top-level one — state the existing concern you considered and why it does not cover the work, so the placement decision is visible for a human catch without enforcement machinery.

### Execution Handoff

Commit the `superRA/` directory atomically (`plan(add): <summary>` for the initial tree authoring; see §User Feedback and Changing the Task Tree for the full sub-step set). Then hand off to `superRA:superimplement`, which owns execution-mode selection, frontier-based dispatch, and review discipline.

## Substantive Questions

At any point during planning, when you hit a genuine design tradeoff with distinct alternatives, present the options for the user to choose rather than assuming intent silently or asserting one and narrating your reasoning. Questions are a quality mechanism for tying loose ends, not process checkpoints.

## Living Task Tree

**The task tree is NOT a static spec.** Work reveals surprises; the task tree evolves in place.

Distinguish two kinds of drift: (a) **agent-discovered refinements** during in-flight work (a task's approach adjusted after seeing the data, expected results tuned to early findings) — handle these as inline edits to the task's body sections per the editing discipline in `agents/implementer.md` §Editing Etiquette; (b) **researcher-initiated scope changes** mid-session (new tasks, removed tasks, methodology pivots, sample redefinition) — these MUST be routed through §User Feedback and Changing the Task Tree below.

**Results:** Each task's `## Results` section is the live findings record. See `task-tree/references/task-file-contract.md` §Results Shape for the template and two-stage lifecycle.

### `superRA/` Is the Task Tracker

`superRA/` is the authoritative task tracker — its task files and frontmatter `status:` fields are the state of record, not chat, status reports, or `TodoWrite` (a transient within-session view that does not persist). Any work that is part of the project lives in `superRA/` first; if losing a todo at session end would lose work the researcher cares about, it belongs there. When the two disagree, `superRA/` is right.

## User Feedback and Changing the Task Tree

When the task tree changes — details updated, tasks added/removed/restructured, objective shifted — follow this protocol, whether the change is raised mid-execution or after integration/merge. Update task files inline; never start a parallel tree, append an "Addendum", or leave the change in chat.

**Material (require this protocol):**

- Adding, removing, or restructuring task directories.
- Changing a task's objective.
- Changing the project-level objective, methodology, sample definition, or expected output.
- Changing data sources or project-wide conventions.
- Scope additions arriving after integration or merge.
- Substantive restructure findings surfaced mid-INTEGRATE. The orchestrator authors the Restructure Proposal; the researcher decides.

**Not material (handle as inline discovery edits per §Living Task Tree above):**

- Rewording a task objective to match what the data forced (within the same scope).
- Adjusting expected results based on early findings.
- Refining methodology details that the researcher already approved at planning time.

**Protocol:**

1. **Confirm intent.** A passing remark in chat is not authorization. Ask (`AskUserQuestion`) to confirm the researcher wants the change.
2. **Update `superRA/` inline:** Place, rewrite, split, merge, or remove tasks by `references/task-tree-design.md` §Placing Work in the Existing Tree and §Objective rewrites on scope expansion. After task edits, rewrite any field in a governing ancestor task that no longer matches the new tree.
3. **Update statuses** by orchestrator judgment, per `references/task-tree-design.md` §Objective rewrites on scope expansion.
4. **Sweep for stale content** per `task-tree/references/task-file-contract.md` §Stale Content Checklist.
5. **Commit atomically** — all affected task.md files + any code touched by the change, in one commit. PLAN is one multi-step phase, so its commit subject carries the sub-step in the scope per `using-superra` §Commit Hygiene: `plan(<sub-step>): <summary>`, where `<sub-step>` is `add` (tree authoring), `revise` (this update-task path), `rollup` (status rollup), or `review` (a planning-review verdict commit, which carries its `<STATE>`: `plan(review): APPROVE|REVISE — <summary>`). This update-task change is `plan(revise): <one-line scope change>`.
6. **Resume** on the affected frontier per `using-superra/references/main-agent.md` §Resuming Work.

Do not resume the in-flight task before the change is committed — it is not real until then — and do not treat an invalidated milestone as license to clear unrelated approved tasks.
