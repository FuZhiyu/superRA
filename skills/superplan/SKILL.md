---
name: superplan
description: "Requires `superRA:using-superra` loaded first. Use when starting new research work, adding work to an existing task tree, or revising an existing task tree. Triggers include \"let's analyze X\", \"write me a plan for Y\", \"we're starting a new project on Z\", \"before writing any code\", an empty working directory for a new task, or an existing `superRA/` that needs new tasks or restructuring. Sits at the PLAN phase of the superRA PLAN -> IMPLEMENT -> INTEGRATE workflow; hands off to `superimplement` once the task tree is approved. Domain-agnostic: for implemented verticals such as data analysis or theory/modeling, invokes the matching domain skill and planning reference before task drafting."
---

# superplan — the PLAN phase

**First, load `superRA:using-superra` if not already loaded.**

**If the harness has activated plan mode, load `references/harness-plan-mode.md` before proceeding.**

## Overview

Owns the procedural shape of the **PLAN** phase: discovery of existing work, exploration, domain setup, task decomposition, self-review, and handoff. Output is a `superRA/` task tree for superimplement to consume.

Write task objectives for a reader skilled at the craft but with zero context for this project. The `## Objective` / `## Planner Guidance` split — binding vs. suggested content — is in `references/task-tree-design.md` §Writing Objectives and Planner Guidance.

**Announce at start:** "I'm using the superplan skill to create the task tree."

**Output location:** `superRA/` at the worktree root if in a worktree, otherwise the project root, unless the user specifies elsewhere. Commit the task tree before execution.

## Entry Assessment

Before exploration or task design, assess three independent dimensions of the incoming work. Creating a task tree and updating one both pass through the same assessment.

**1. Placement — where it goes.** If `superRA/` exists, walk the tree to find where the work belongs via the concern-first descent in `references/task-tree-design.md` §Placing Work by Durable Home. If not, check for a legacy `PLAN.md` (offer migration via `task-system` §Migration) and otherwise make the work the first root-level task.

**2. Depth tier — how deep.** Choose a tier (§Depth Tiers) that modulates how deeply the later phases run.

**3. Routing path — what mode.** Forward planning is the default. The one alternative is **retroactive documentation** — existing code/results need a `superRA/` record, detected when the work has code without task coverage; it runs the same phases but sets `status: implemented` (see `references/task-tree-design.md` §Retroactive Task-Tree Creation). Structural cleanup of an existing tree is not a routing mode — it is the separate `references/consolidation.md` pass, entered when the tree has structural debt rather than when new work needs placing.

Placement and depth are independent: work can clearly belong under an existing task yet still need thorough planning, and an uncertain tree location does not make the work hard to plan. Exploration may force either to be revisited.

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

**Currently implemented verticals:**

| Vertical | Trigger | Domain skill |
|---|---|---|
| Data analysis | task involves loading, cleaning, merging, transforming, modeling, or visualizing data | `superRA:econ-data-analysis` |
| Theory / modeling | task involves deriving or analyzing a mathematical model, equilibrium conditions, comparative statics, proofs, symbolic manipulation, or model notes | `superRA:theory-modeling` |
| Writing | task involves editing, polishing, proofreading, consistency-checking, refactoring wording, or drafting technical sections of an academic paper or manuscript | `superRA:writing` |

**Stop here, load the matching domain skill, follow its planning-stage reference per its own stage-load table, and satisfy its planning hard gate before returning to Phase 3.** The researcher must approve the domain skill's planning-stage inventory artifact before any task structure is drafted.

If the task is in a domain without an implemented vertical: proceed to Phase 3, but flag the gap to the researcher.

**Scope check:** A root-level task is a whole workstream (see `references/task-tree-design.md` §Root-task definition). If the work covers multiple genuinely independent workstreams, suggest a separate root-level task for each, producing complete results on its own; work related to an existing workstream nests under it by the placement descent rather than landing at root.

## Phase 3: Design & Task Decomposition

### Artifact Pipeline

Before defining tasks, map the artifact pipeline: which scripts/notebooks/documents will be created (one per logical phase, following any artifact-format guidance the domain skill loads), what their inputs are, and where outputs go. Follow existing project conventions for directory structure.

**Walk the project guidance docs and distill them into scoped objective context.** Walk up from every directory the tree will touch, reading every `CLAUDE.md` / `AGENTS.md` / `README.md` on the path plus the repo-root `CLAUDE.md` and every data-directory `README.md` the tasks load from. Distill what changes implementation or review behavior into scoped `### Conventions` / `### Context` / `### Constraints` subsections on the `## Objective` of the lowest task whose subtree it governs (`references/task-tree-design.md` §Context Distillation). Dispatched agents inherit these via `superra task read` instead of re-walking the tree.

**Pipeline file (required for multi-artifact work):** When the work has more than one executable artifact, include a single committed entry point that reproduces every output from source — running scripts in dependency order, failing fast (`set -e` or equivalent), updated whenever a script is added.

### Task Structure

**Each task is one logical unit of work with full discipline applied.** The active domain skill defines that discipline. Documentation is written continuously alongside the work, not as a separate task.

For the objective writing guide and task splitting heuristics, see `references/task-tree-design.md` §Writing Objectives and Planner Guidance and §Splitting Tasks.

### Creating Tasks

**First, create the task-tree wrapper.** Every downstream agent reads and edits tasks through the committed `<task-root>/superra` wrapper, so it must exist before any subagent is dispatched. A fresh project has no `superra` yet, so the first call goes through the loaded task-system skill directory (`<skill-dir>` = the directory holding its `SKILL.md`) and is committed with the tree:

```bash
uv run --script <skill-dir>/scripts/cli.py wrapper init   # writes superRA/superra
```

Afterward every call uses `./superRA/superra …`:

```bash
./superRA/superra task create 01-data/03-filter \
  --title "Filter Sample" \
  --objective "Apply standard filters: drop obs before 2000, require non-missing returns." \
  --guidance "Consider reusing Code/common_filters.py." \
  --depends-on 02-merge
```

Or create the directories and write `task.md` files directly (`task-system/SKILL.md` §Task File Format).

**No checkboxes.** Tasks do not contain step checkboxes (`- [ ]` / `- [x]`). If a step needs independent tracking and review, it becomes a subtask.

### Task Dependencies

Each task declares dependencies in its `depends_on:` frontmatter field (sibling directory names). See `task-system/references/task-file-contract.md` §Field-by-Field Notes for semantics.

Identify independent branches so the orchestrator can dispatch them in parallel (see `agent-orchestration` §Workload Balancing).

**A task depends on another when it:**
- reads the other task's output files;
- needs a sample / variable / methodology decision finalized in the other task; or
- runs sensitivity / robustness on the other task's baseline results.

**After writing all tasks:** trace the dependency edges — no cycles, no references to nonexistent siblings; terminal task(s) produce the top-line results.

### Task Anatomy

For the canonical task structure — recursive task anatomy and field-by-field notes — see `task-system/references/task-file-contract.md`. Domain-specific top-level objective context comes from the domain skill's planning reference.

### Create the `superRA/` Directory

1. Create `superRA/task.md` (top task) with `## Objective` carrying the project-level goal, methodology, scope, and any project-wide scoped `### Conventions` / `### Context` / `### Constraints` subsections.
2. Create child task directories with full objectives per §Task Structure above.

## Phase 4: Review & Commit

### Self-Review

After writing the complete task tree:

1. **Domain inventory coverage (where applicable):** For domains with a planning hard gate, can you point to task coverage for every item in the inventory?
2. **Placeholder scan:** Search for vague objectives — "process the data", "clean up results", "finalize" without concrete success criteria. Fix them.
3. **Pipeline consistency:** Do the artifact names in the pipeline file match the artifacts created in each task? Are they in the right order?
4. **Validation coverage:** Does every transformative task have a corresponding validation criterion in its objective?
5. **Objective/guidance split:** Are binding deliverables, constraints, decisions, fixed file expectations, and validation criteria in `## Objective`, with non-binding hints in `## Planner Guidance`?
6. **Handoff test:** If you stopped here and a new agent read the root task.md plus the ancestor chain of any leaf task, could they continue? Is there enough context?
7. **Verification coverage (where applicable):** Does the task tree cover the active domain skill's verification / robustness requirements?
8. **Dependency graph sanity:** Every task has `depends_on:` declared. No cycles. Independent branches are marked parallelizable.
9. **Subtask coverage:** No task carries implicit sub-steps that should be separate subtasks.

Fix issues inline. No need to re-review — just fix and move on.

### Agent Review

At thorough depth, dispatch `Stage: planning-review` before presenting the tree to the user. Explicit handoff-review requests can enter the same step. Choose between `Review mode: handoff-readiness` and `Review mode: design-review` per `references/thorough-planning.md` §Planning Review; use `agent-orchestration` §Dispatch Templates for the dispatch shape.

REVISE findings must be fixed before proceeding to User Review — the user should see a structurally sound tree, not one with known issues.

Skip this step at quick and standard depth unless the user explicitly asks for a handoff review — the self-review checklist is sufficient when the main agent designed the tree itself without parallel exploration.

### User Review

Verify the task tree aligns with the user's intent. Present the tree (via `superra task tree`) and surface remaining open questions — design tradeoffs, unresolved ambiguities, choices that could reasonably go another way. Present tradeoffs as options, not assertions. If you have no genuine questions, the tree presentation itself is the review.

For each newly created task — especially a root-level one — state the existing concern you considered and why it does not cover the work, so the placement decision is visible for a human catch without enforcement machinery.

### Execution Handoff

Commit the `superRA/` directory atomically. Then hand off to `superRA:superimplement`, which owns execution-mode selection, frontier-based dispatch, and review discipline.

## Substantive Questions

At any point during planning, when you hit a genuine design tradeoff with distinct alternatives, present the options for the user to choose rather than assuming intent silently or asserting one and narrating your reasoning. Questions are a quality mechanism for tying loose ends, not process checkpoints.

## Retroactive Plan Creation

Survey existing code, outputs, and notebooks, then create one task per logical unit of work done, each with `status: implemented` and its `## Objective` (the goal) and `## Results` (what was found) filled in. The full workflow is in `references/task-tree-design.md` §Retroactive Task-Tree Creation.

## Living Task Tree

**The task tree is NOT a static spec.** Work reveals surprises; the task tree evolves in place.

Distinguish two kinds of drift: (a) **agent-discovered refinements** during in-flight work (a task's approach adjusted after seeing the data, expected results tuned to early findings) — handle these as inline edits to the task's body sections per the editing discipline in `agents/implementer.md` §Editing Etiquette; (b) **researcher-initiated scope changes** mid-session (new tasks, removed tasks, methodology pivots, sample redefinition) — these MUST be routed through §User Feedback and Changing the Task Tree below.

**Results:** Each task's `## Results` section is the live findings record. See `task-system/references/task-file-contract.md` §Results Shape for the template and two-stage lifecycle.

### `superRA/` Is the Task Tracker

`superRA/` is the authoritative task tracker — its task files and frontmatter `status:` fields are the state of record, not chat, status reports, or `TodoWrite`. Any work that is part of the analysis (a new task, discovered subtask, methodology check, sensitivity run, refactor pass) lives in `superRA/` first; if losing a todo at session end would lose work the researcher cares about, it belongs there. `TodoWrite` is only a transient within-session view — it does not persist, so it cannot carry analysis tasks or coordinate work across sessions. When the two disagree, `superRA/` is right.

## Revision Notes

When a task is updated (scope change, methodology pivot, added/removed work), add a `## Revision Notes` section with the delta: what changed, why, and how significant (trivial/mechanical vs substantive), so the next agent knows whether to re-explore. The note carries only the delta; the objective itself is always rewritten fully to the current state, not patched. Revision notes are cleaned out when the task is re-implemented and approved, like review notes.

## User Feedback and Changing the Task Tree

When the task tree changes — details updated, tasks added/removed/restructured, objective shifted — follow this protocol, whether the change is raised mid-execution or after integration/merge. Update task files inline; never start a parallel tree, append an "Addendum", or leave the change in chat.

**Material (require this protocol):**

- Adding, removing, or restructuring task directories.
- Changing a task's objective, script, input, or output.
- Changing the analysis-level objective, methodology, sample definition, or expected output.
- Changing data sources or project-wide conventions.
- Scope additions arriving after integration or merge.
- Substantive restructure findings surfaced mid-INTEGRATE. The orchestrator authors the Restructure Proposal; the researcher decides.

**Not material (handle as inline discovery edits per §Living Task Tree above):**

- Rewording a task objective to match what the data forced (within the same scope).
- Adjusting expected results based on early findings.
- Refining methodology details that the researcher already approved at planning time.

**Protocol:**

1. **Confirm intent.** A passing remark in chat is not authorization. Use `AskUserQuestion` (or a plain-text question if the tool is not available) to confirm the researcher wants the change.
2. **Update `superRA/` inline:** Place the change by the recursive descent in `references/task-tree-design.md` §Placing Work by Durable Home — the presumption is MODIFY/MERGE the task that owns the concern; a new task, especially at root, is the justified exception.
   - **Modified task** — Walk the tree, identify every task whose objective or output is affected, and update each in place. Rewrite each objective to be fully self-sufficient with the new scope (all planning context included, not just the changed part). Add a `## Revision Notes` section with the delta signal.
   - **New task** — Only when the descent reaches a branch no child covers; record which concern you read and why it does not cover the work.
   - **Removed task** — Delete the directory entirely.
   - **Root task.md** — After the task edits above, rewrite any field in root task.md that no longer matches the new tree.

3. **Update statuses** by orchestrator judgment. Reset `status` to `not-started` only for the changed task(s) and transitive downstream dependents whose inputs or assumptions shift; preserve unrelated `approved` tasks.
4. **Sweep for stale content** per `task-system/references/task-file-contract.md` §Stale Content Checklist.
5. **Commit atomically** — all affected task.md files + any code touched by the change, in one commit. Title: `plan: <one-line scope change>`.
6. **Resolve the next frontier.** Run `using-superRA/references/main-agent.md` §Workflow Frontier Resolver to choose the next workflow entry point.

Do not resume the in-flight task before the change is committed — it is not real until then — and do not treat an invalidated milestone as license to clear unrelated approved tasks.
