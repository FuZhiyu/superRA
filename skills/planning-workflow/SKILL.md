---
name: planning-workflow
description: "Requires `superRA:using-superra` loaded first. Use when starting a new piece of research work with an objective and methodology but no .plan/ yet; when you have an idea and need to translate it into an executable task tree; when a fresh branch needs its planning artifacts bootstrapped. Triggers include \"let's analyze X\", \"write me a plan for Y\", \"we're starting a new project on Z\", \"before writing any code\", empty working directory for a new task, or an existing .plan/ that is being rewritten from scratch. Sits at the PLAN phase of the superRA PLAN -> IMPLEMENT -> INTEGRATE workflow; hands off to `implementation-workflow` once the plan is approved. Domain-agnostic: for implemented verticals such as data analysis or theory/modeling, invokes the matching domain skill and planning reference before task drafting."
---

# Planning Workflow

**First, load `superRA:using-superra` if not already loaded.**

## Overview

Workflow skill for the **PLAN** phase of the superRA workflow. Owns the procedural shape of plan creation: scope check, domain-vertical setup, task decomposition, self-review, execution handoff. Outputs a `.plan/` task tree for the implementation-workflow to consume.

Write comprehensive plans for a reader skilled at the craft but with zero context for this specific project — which files to create, what inputs to load, how to transform them, what to validate, and how to document results. Frequent commits.

**Announce at start:** "I'm using the planning-workflow skill to create the project plan."

**Output:** A `.plan/` directory at the project root (if in a worktree, the worktree root; otherwise, the project root or user-specified location) containing a root `task.md` and child task directories. User preferences for plan location override this default.

Commit the plan before proceeding to execution.

## Phase 1: Domain Vertical Setup

Identify the domain of the work and load the matching domain skill's planning reference. The domain skill carries any domain-specific hard gates and templates that must be satisfied before tasks are drafted.

**Currently implemented verticals:**

| Vertical | Trigger | Domain skill |
|---|---|---|
| Data analysis | task involves loading, cleaning, merging, transforming, modeling, or visualizing data | `superRA:econ-data-analysis` |
| Theory / modeling | task involves deriving or analyzing a mathematical model, equilibrium conditions, comparative statics, proofs, symbolic manipulation, or model notes | `superRA:theory-modeling` |
| Writing | task involves editing, polishing, proofreading, consistency-checking, refactoring wording, or drafting technical sections of an academic paper or manuscript | `superRA:writing` |

**Stop here, load the matching domain skill, follow its planning-stage reference per its own stage-load table, and satisfy its planning hard gate before returning to Phase 2.** The researcher must approve the domain skill's planning-stage inventory artifact (e.g., Data Inventory, Model Inventory / Assumption Map, or Writing Plan Header) before any task structure is drafted.

If the task is writing: load `skills/writing/references/planning.md`. Large writing work continues into Phase 2 under that reference.

If the task is in a domain without an implemented vertical yet: proceed to Phase 2, but flag the gap to the researcher so they know superRA's domain coverage is not complete for this work.

## Phase 2: Scope Check

If the work covers multiple independent workstreams (e.g., "analyze portfolio sorts AND run Fama-MacBeth regressions AND build factor models"; "do the theory derivation AND the empirical test"), suggest breaking into separate plans — one per workstream. Each plan should produce complete, documented results on its own.

## Phase 3: File Structure

Before defining tasks, map out the artifact pipeline:

- What scripts, notebooks, or documents will be created? One per logical phase (e.g., data cleaning → variable construction → analysis → robustness; or model setup → derivation → verification → write-up). Follow any artifact-format guidance the active domain skill loads at PLAN or IMPLEMENT stage.
- What files are inputs? Where do outputs go?
- Follow existing project conventions for directory structure.

**Walk the project guidance docs and cache them in root task.md `## Conventions`.** Before drafting tasks, walk up from every directory the plan will touch and `Read` every `CLAUDE.md` / `AGENTS.md` / `README.md` you encounter along the path; also read the repo-root `CLAUDE.md` and every `README.md` in a data directory the plan will load from. Populate the root `.plan/task.md` `## Conventions` section with one-paragraph summaries per doc, stamped with the walk date (see `task-system/references/planning.md` §Conventions Section for the discipline).

**Pipeline file (required for multi-artifact work):**

If the work involves more than one script or executable artifact, the plan MUST include a pipeline file that runs all artifacts in the correct order (see the active domain skill's planning reference for examples). A single entry point that reproduces every output from source.

The pipeline file must:
- Run all scripts in dependency order
- Fail fast on errors (`set -e` or equivalent)
- Be committed to version control
- Be updated whenever a new script is added

**Create the `.plan/` directory.** After mapping the file structure:

1. Create `.plan/task.md` (root) with `## Objective` (project-level goal, methodology, scope), `## Conventions` (cached project guidance), and `## Decisions` (empty, ready for user decisions).
2. Create child task directories as determined in Phase 4.

## Phase 4: Task Decomposition

### Subtask Structure

**Each task is one logical unit of work with full discipline applied.** The active domain skill defines that discipline (its main checklist plus any planning-stage guidance). Documentation is written continuously alongside the work, not as a separate task. Typical task shapes:

- "Describe the raw holdings data (panel structure, key variables, missing values)" — task
- "Merge holdings with fund characteristics" — task
- "Validate merge result and derive portfolio weights" — task
- "State primitives, timing, and assumptions; derive the Euler equation" — task
- "Verify the closed form in a limiting case and numerical check" — task

For the objective writing guide and task splitting heuristics, see `task-system/references/planning.md` §Writing Objectives and §Splitting Tasks.

### Creating Tasks

Use `task_create.py` to create tasks (auto-fills template with dates, frontmatter defaults):

```bash
python3 <skill-dir>/scripts/task_create.py \
  --plan-root .plan --path 01-data/03-filter \
  --title "Filter Sample" \
  --objective "Apply standard filters: drop obs before 2000, require non-missing returns." \
  --depends-on 02-merge
```

Or create task directories and write `task.md` files directly — the format is self-explanatory (see `task-system/SKILL.md` §Task File Format).

**No checkboxes.** Tasks do not contain step checkboxes (`- [ ]` / `- [x]`). If a step needs independent tracking and review, it becomes a **subtask** (child directory with its own `task.md`). Suggestive approaches stay as prose in the objective.

### Task Dependencies

Each task declares dependencies in its `depends_on:` frontmatter field (sibling directory names). See `task-system/references/planning.md` §Field-by-Field Notes for semantics.

Identify independent branches so the orchestrator can dispatch them in parallel (see `agent-orchestration` §Workload Balancing).

**A task depends on another when it:**
- reads the other task's output files;
- needs a sample / variable / methodology decision finalized in the other task; or
- runs sensitivity / robustness on the other task's baseline results.

**After writing all tasks:** trace the dependency edges — no cycles, no references to nonexistent siblings; terminal task(s) produce the top-line results.

### Root task.md and Task Anatomy

For the canonical task structure — root task.md anatomy, per-task anatomy, and field-by-field notes — see `task-system/references/planning.md`. Domain-specific root sections (e.g., Data Inventory for data analysis, or Model Inventory / Assumption Map for theory/modeling) come from the domain skill's planning reference.

## Retroactive Plan Creation

When documenting existing exploratory work into `.plan/`:

1. Survey existing code, outputs, and notebooks
2. Create `.plan/` structure with `task_create.py` — one task per logical unit of work done
3. Edit each `task.md`: set `status: implemented` in frontmatter, fill body sections with what was done (`## Objective`: what was the goal) and found (`## Results`: what was discovered)
4. Hooks validate + rebuild dashboard. The plan is now a retroactive record that can drive review, integration, and future work

See `task-system/references/planning.md` §Retroactive Plan Creation for the full workflow.

## Living Plan and Results

**The plan is NOT a static spec.** Work reveals surprises; the plan evolves in place.

Distinguish two kinds of drift: (a) **agent-discovered refinements** during in-flight work (a task's approach adjusted after seeing the data, expected results tuned to early findings) — handle these as inline edits to the task's body sections per the editing discipline below; (b) **researcher-initiated scope changes** mid-session (new tasks, removed tasks, methodology pivots, sample redefinition) — these MUST be routed through §User Feedback and Changing Plans below.

**Editing discipline** lives in `agents/implementer.md` §Editing Etiquette and `agents/reviewer.md` §Editing Etiquette.

**Results:** Each task's `## Results` section is the live findings record. See `task-system/references/planning.md` §Results Shape for the template and two-stage lifecycle. At `integration-workflow` Document, results mature into a permanent record. Follow the active domain planning reference when it declares a different durable record.

### .plan/ Is the Task Tracker

**`.plan/` is the primary task tracker** — not `Todo` tools, not chat, not status reports, not a session-internal scratchpad. The task files with their frontmatter `status:` / `review_status:` fields are the authoritative state of what is planned, what is in progress, and what is done. Persistence across sessions, agent handoffs, and harness boundaries depends on this being true.

`TodoWrite` (or any equivalent harness-provided todo UI) has a narrower role: a transient view of *what the agent is doing right now in this session*. It is acceptable for ephemeral session-internal todos that do not represent analysis tasks (e.g., "read three reference files, then summarize for the user", "fix three lint errors before re-running the test"). It is **not** acceptable as a substitute for a `.plan/` task. If the work is part of the analysis — a new task, a discovered subtask, a methodology check, a sensitivity run, a refactor pass — it lives in `.plan/` first, then optionally mirrors into `TodoWrite` as a working view.

**Rule of thumb:** if losing this todo at session end would lose work the researcher cares about, it belongs in `.plan/`, not `TodoWrite`.

**Banned patterns:**

- Tracking analysis tasks only in `TodoWrite` while leaving `.plan/` stale.
- Discovering a new subtask, adding it to `TodoWrite`, completing it, and never reflecting it in `.plan/`.
- Using `TodoWrite` to coordinate work between sessions (it does not persist; the next session sees nothing).
- Treating `TodoWrite` items as "logged" — they are not. Logged work is in a committed task file.

If `TodoWrite` and `.plan/` ever disagree about the state of analysis work, `.plan/` is right by definition. Update `TodoWrite` to match — never the reverse.

When the plan itself changes, re-invoke §User Feedback and Changing Plans below.

## User Feedback and Changing Plans

When the plan changes — task details updated, tasks added, removed, or restructured, objective shifted — whether prompted by explicit user feedback or surfaced during execution, follow this protocol. The same procedure applies whether the change is raised mid-execution or after integration / merge; the protocol records which task statuses and workflow rollups are invalidated. Update task files inline; do not start a parallel plan, append an "Addendum" section, or carry the change in chat.

**Material (require this protocol):**

- Adding, removing, or restructuring task directories.
- Changing a task's objective, script, input, or output.
- Changing the analysis-level objective, methodology, sample definition, or expected output.
- Changing data sources or project-wide conventions.
- Scope additions arriving after integration or merge (post-PR additions, adjacent features surfaced by reviewers, follow-on ideas).
- Substantive restructure findings surfaced mid-INTEGRATE (by the `integration-workflow` Sync agent, Integrate reviewer, or Document reviewer) — task add/remove/combine, DAG edge flip, prior APPROVED status invalidation. The orchestrator authors the Restructure Proposal; the researcher decides.

**Not material (handle as inline discovery edits per the Living Plan section above):**

- Rewording a task objective to match what the data forced (within the same scope).
- Adjusting expected results based on early findings.
- Refining methodology details that the researcher already approved at planning time.

**Protocol:**

1. **Confirm intent.** A passing remark in chat is not authorization. Use `AskUserQuestion` (or a plain-text question if the tool is not available) to confirm the researcher wants the change.
2. **Log the decision** per `task-system/references/planning.md` §User Decisions Log — root task.md `## Decisions` for cross-task changes, task-scoped `## Decisions` for single-task changes. The log entry must declare which tasks are affected and which workflow status milestones are invalidated.
3. **Update `.plan/` inline:**
   - **Prefer modifying existing task.md files over adding new tasks.** Walk the task tree and identify every task whose objective or output is affected by the change. Update each in place to reflect the new scope.
   - **New task** → Only when the change is genuinely independent of every existing task's scope, create a new task directory with `task_create.py` or mkdir + write task.md.
   - **Modified task** → rewrite affected fields in place. Do not strike through. Do not add "Modified:" annotations.
   - **Removed task** → delete the directory entirely. The Decisions entry preserves the rationale.
   - **Root task.md.** After the task edits above, rewrite any field in root task.md that no longer matches the new plan. The root and task tree must describe the same analysis after the edit.

4. **Update statuses** by orchestrator judgment. The orchestrator declares in the §Decisions entry *which* task statuses are invalidated and *why*. Rules: clear `review_status` and `integration_status` only for the changed task(s) and transitive downstream dependents whose inputs or assumptions shift; preserve unrelated `approved` tasks.
5. **Sweep for stale content** per `task-system/references/planning.md` §Stale Content Checklist. Earlier task objectives whose output has been superseded, cross-references to removed tasks, review notes resolved by subsequent work — fix in place now, not later.
6. **Commit atomically** — all affected task.md files + any code touched by the change, in one commit. Title: `plan: <one-line scope change>`.
7. **Resolve the next frontier.** Run `using-superRA/references/main-agent.md` §Workflow Frontier Resolver to choose the next workflow entry point. On every re-entry through `integration-workflow`, the **full** drift-test suite runs regardless of which tasks changed; only *authoring* new drift tests is scoped to the affected tasks.


**Banned shortcuts:**

- Carrying the new task in chat or only in `TodoWrite` without writing it into `.plan/` (see §.plan/ Is the Task Tracker above — `TodoWrite` is a transient view, not a record).
- Resuming the in-flight task before reflecting the change in the committed task files — the change is not real until it is committed.
- Treating an invalidated workflow milestone as permission to clear unrelated approved tasks. Preserve task-local validity unless the changed task's downstream closure invalidates it.


## Remember

- Exact file paths always
- Complete content in every task objective
- Domain-appropriate discipline applied at each task, with documentation written continuously — see the active domain skill's main checklist
- When the active domain has a hard gate or required verification plan, the finished tasks visibly cover it
- Pipeline file for multi-artifact work

## Self-Review

After writing the complete plan:

**1. Domain inventory coverage (where applicable):** For domains with a planning hard gate, can you point to task coverage for every item in that section (for example, each dataset in Data Inventory or each object/assumption block in a Model Inventory / Assumption Map)?

**2. Placeholder scan:** Search for vague objectives — "process the data", "clean up results", "finalize" without concrete success criteria. Fix them.

**3. Pipeline consistency:** Do the artifact names in the pipeline file match the artifacts created in each task? Are they in the right order?

**4. Validation coverage:** Does every transformative task have a corresponding validation criterion in its objective? (For data: every merge, filter, and variable construction.)

**5. Plan serves as handoff:** If you stopped here and a new agent read the root task.md plus the ancestor chain of any leaf task, could they continue? Is there enough context?

**6. Sensitivity / robustness / verification coverage (where applicable):** Does the plan cover the active domain skill's verification / robustness requirements (e.g., sensitivity analysis tasks for data work, or derivation / proof / numerical-check planning for theory work)?

**7. Dependency graph sanity:** Every task has `depends_on:` declared. No cycles. If the plan has 2+ independent branches, at least one pair of tasks is marked parallelizable (no mutual dependency).

**8. Subtask coverage:** No task carries implicit sub-steps that should be separate subtasks. If a task's objective requires more than one logical operation that each warrants independent review, split it.

Fix issues inline. No need to re-review — just fix and move on.

## Execution Handoff

After finalizing the plan, commit the `.plan/` directory atomically. Then hand off to `superRA:implementation-workflow`, which owns execution-mode selection (subagent vs direct — see `superRA:using-superra` §Execution Modes), frontier-based dispatch, and review discipline.
