---
name: planning-workflow
description: Use when starting a new piece of research work with an objective and methodology but no code or PLAN.md yet; when you have an idea and need to translate it into an executable plan document; when a fresh branch needs its planning artifacts bootstrapped. Triggers include "let's analyze X", "write me a plan for Y", "we're starting a new project on Z", "before writing any code", empty working directory for a new task, or an existing PLAN.md that is being rewritten from scratch. Sits at the PLAN phase of the superRA PLAN → IMPLEMENT → VALIDATE → INTEGRATE workflow; hands off to `execution-workflow` once the plan is approved. Domain-agnostic: for data-analysis planning, invokes `superRA:econ-data-analysis` and reads its `references/planning.md` for the Data Inventory hard gate and sensitivity design.
---

# Planning Workflow

## Overview

Workflow skill for the **PLAN** phase of the superRA workflow. Owns the procedural shape of plan creation: scope check, domain-vertical setup, task decomposition, self-review, execution handoff. Outputs `PLAN.md` and `RESULTS.md` for the execution-workflow to consume.

This skill is **domain-agnostic**. Today's only implemented domain vertical is data analysis; future verticals (theory / modeling, literature review, simulation, writing) plug in by providing their own domain skill with a `references/planning.md`. The procedure here stays the same.

Write comprehensive plans assuming the next person reading has zero context for this project. Document everything they need: which files to create, what inputs to load, how to transform them, what to validate, and how to document results. Give them the whole plan as bite-sized steps. Frequent commits.

Assume the next reader is skilled at the craft, but knows nothing about this specific project, its data / literature / prior work, or its conventions.

**Announce at start:** "I'm using the planning-workflow skill to create the project plan."

**Save plan to:** `PLAN.md` at the project root (if in a worktree, the worktree root; otherwise, the project root or user-specified location)
- Create `RESULTS.md` alongside (see Living Plan and Results Docs section below)
- (User preferences for plan location override this default)

Commit the plan before proceeding to execution.

## Phase 1: Domain Vertical Setup

Identify the domain of the work and load the matching domain skill's planning reference. The domain skill carries any domain-specific hard gates and templates that must be satisfied before tasks are drafted.

**Currently implemented verticals:**

| Vertical | Trigger | Domain skill | Planning reference |
|---|---|---|---|
| Data analysis | task involves loading, cleaning, merging, transforming, modeling, or visualizing data | `superRA:econ-data-analysis` | `references/planning.md` — carries the **Data Inventory hard gate** (no tasks until data is inventoried and approved) and **Sensitivity Analysis Design** discussion |

If the task is data analysis: **stop here, load `superRA:econ-data-analysis`, read `references/planning.md`, and satisfy its hard gate before returning to Phase 2.** The researcher must approve the Data Inventory before any task structure is drafted.

If the task is in a domain without an implemented vertical yet: proceed to Phase 2, but flag the gap to the researcher so they know superRA's domain coverage is not complete for this work.

## Phase 2: Scope Check

If the work covers multiple independent workstreams (e.g., "analyze portfolio sorts AND run Fama-MacBeth regressions AND build factor models"; "do the theory derivation AND the empirical test"), suggest breaking into separate plans — one per workstream. Each plan should produce complete, documented results on its own.

## Phase 3: File Structure

Before defining tasks, map out the artifact pipeline:

- What scripts, notebooks, or documents will be created? One per logical phase (e.g., data cleaning → variable construction → analysis → robustness; or derivation → simulation → calibration for theory work).
- **Analysis scripts**: format for notebook rendering per `econ-data-analysis/references/notebook-format.md`. Runner/pipeline scripts and non-analysis artifacts use standard format.
- What files are inputs? Where do outputs go?
- Follow existing project conventions for directory structure.

**Walk the project guidance docs and cache them in PLAN.md.** Before drafting tasks, walk up from every directory the plan will touch and `Read` every `CLAUDE.md` / `AGENTS.md` / `README.md` you encounter along the path; also read the repo-root `CLAUDE.md` and every `README.md` in a data directory the plan will load from. Populate the `## Project Conventions` section of `PLAN.md` with one-paragraph summaries per doc, stamped with the walk date (see `handoff-doc/references/plan-anatomy.md` §Project Conventions for the anatomy). This is what subagent dispatches read at task time instead of re-walking the whole tree; if a subagent later needs a convention not captured here, it walks on-demand and reports the omission so the orchestrator can update the section.

**Pipeline file (required for multi-artifact work):**

If the work involves more than one script, the plan MUST include a pipeline file that runs all scripts in the correct order. This is a reproducibility requirement. Examples and detail for data analysis are in `econ-data-analysis/references/planning.md`. The same principle applies to any multi-artifact workstream: a single entry point that reproduces every output from source.

The pipeline file must:
- Run all scripts in dependency order
- Fail fast on errors (`set -e` or equivalent)
- Be committed to version control
- Be updated whenever a new script is added

## Phase 4: Task Decomposition

### Step Granularity

**Each step is one logical unit of work with full discipline applied.** For data analysis, that discipline is the three concurrent disciplines describe-analyze-validate (see `superRA:econ-data-analysis` main body). Documentation is written continuously alongside the three, not as a separate step. Typical step shapes:

- "Describe the raw holdings data (panel structure, key variables, missing values)" — step
- "Merge holdings with fund characteristics (left join on fund_id × date)" — step
- "Validate merge result (row counts, check unmatched, spot-check merged variables), commit" — step

For other verticals, the operational cycle looks different (e.g., derivation → verification → proof-check for theory work), but the granularity rule is the same: one logical operation per step, with the cycle completed in-step.

### Task Dependencies

Not every task is sequential. Identify independent branches at plan
time so the orchestrator can dispatch them in parallel (see
`agent-orchestration` §Workload Balancing).

**Format.** Each task block declares a `**Depends on:**` line listing
upstream task numbers, or `*(none)*` if the task has no upstream
dependency. See `superRA:handoff-doc` `references/plan-anatomy.md` §Task Block Anatomy for the required format.

**When a task depends on another.**
- It reads the other task's output files.
- It needs a sample / variable / methodology decision finalized in the
  other task.
- It runs sensitivity / robustness on the other task's baseline
  results.

**When a task is independent (`Depends on: *(none)*`).**
- Loads its own raw inputs, produces its own outputs.
- Sits in a separate pipeline branch that doesn't meet downstream.

**Orchestration contract.** The `execution-workflow` orchestrator reads
these fields. Tasks whose dependencies are all `APPROVED` may be
dispatched as a single parallel Agent-tool batch, subject to
`agent-orchestration` §Workload Balancing. Mutually independent tasks
SHOULD run in parallel; serializing them is waste.

**Plan-time DAG sanity.** After writing all tasks, trace the dependency
edges. No cycles. No `Depends on: Task 99` pointing at a task that
doesn't exist. The terminal task(s) (no downstream) should be the ones
that produce the top-line results.

### Plan Document Header and Task Structure

For the canonical `PLAN.md` template — required header (objective, methodology, domain-specific sections, output, expected results, pipeline) plus task block structure with the domain's step cycle and a worked example — load `superRA:handoff-doc` and read `references/plan-anatomy.md`. Domain-specific header sections (e.g., the Data Inventory section for data analysis) come from the domain skill's planning reference.

Required header fields and task block structure are non-negotiable. The template's example code is illustrative — adapt the content to your domain and methodology, but preserve the step-cycle rhythm the domain prescribes.

## Living Plan and Results Docs

**The plan is NOT a static spec.** Work reveals surprises; the plan evolves in place.

Distinguish two kinds of drift: (a) **agent-discovered refinements** during in-flight work (a step's method adjusted after seeing the data, expected results tuned to early findings) — handle these as inline edits per the discipline below; (b) **researcher-initiated scope changes** mid-session (new tasks, removed tasks, methodology pivots, sample redefinition) — these MUST be routed through §User Feedback and Changing Plans below, which defines the confirm → log → inline-edit → roll-back-milestones → sweep-for-stale-content → atomic-commit protocol.

**The editing discipline and the full anatomy templates** — the four document principles, inline-edit rule, stale-content checklist, User Decisions Log format, figure-embedding pointer, `## Project Conventions` layout, section layouts, code-block examples, status-line formats, the two-stage `RESULTS.md` lifecycle — live in `superRA:handoff-doc`. Load it when authoring `PLAN.md` / `RESULTS.md` from scratch; its `references/plan-anatomy.md` and `references/results-anatomy.md` carry the full templates. Role-by-role ownership and the review-loop annotation protocols live in `agents/implementer.md` and `agents/reviewer.md`.

**Results document:** Create `RESULTS.md` alongside `PLAN.md` with the header and **one pre-allocated stub per task block** — same order, same task name as in `PLAN.md`, body just `**Status:** Not started`. Full anatomy and ownership rules in `superRA:handoff-doc` §references/results-anatomy.md (including why pre-allocation is load-bearing for parallel dispatch). This is the Stage 1 form; at `integration-workflow` Phase C it matures into a permanent record.

### PLAN.md Is the Task Tracker

**`PLAN.md` is the primary task tracker** — not `Todo` tools, not chat, not status reports, not a session-internal scratchpad. The task blocks with their `- [ ]` / `- [x]` checkbox steps and `**Review status:**` lines are the authoritative state of what is planned, what is in progress, and what is done. Persistence across sessions, agent handoffs, and harness boundaries depends on this being true.

`TodoWrite` (or any equivalent harness-provided todo UI) has a narrower role: a transient view of *what the agent is doing right now in this session*. It is acceptable for ephemeral session-internal todos that do not represent analysis tasks (e.g., "read three reference files, then summarize for the user", "fix three lint errors before re-running the test"). It is **not** acceptable as a substitute for a PLAN.md task block. If the work is part of the analysis — a new task, a discovered subtask, a methodology check, a sensitivity run, a refactor pass — it lives in `PLAN.md` first, then optionally mirrors into `TodoWrite` as a working view.

**Rule of thumb:** if losing this todo at session end would lose work the researcher cares about, it belongs in `PLAN.md`, not `TodoWrite`.

**Banned patterns:**

- Tracking analysis tasks only in `TodoWrite` while leaving `PLAN.md` stale.
- Discovering a new subtask, adding it to `TodoWrite`, completing it, and never reflecting it in `PLAN.md`.
- Using `TodoWrite` to coordinate work between sessions (it does not persist; the next session sees nothing).
- Treating `TodoWrite` items as "logged" — they are not. Logged work is in a committed doc.

If `TodoWrite` and `PLAN.md` ever disagree about the state of analysis work, `PLAN.md` is right by definition. Update `TodoWrite` to match — never the reverse.

When the plan itself changes — in-session scope change or cross-session re-entry — re-invoke §User Feedback and Changing Plans below and follow its protocol.

## User Feedback and Changing Plans

When the plan changes — task details updated, tasks added, removed, or reordered, objective shifted — whether prompted by explicit user feedback or surfaced during execution, follow this protocol. The same procedure applies whether the change is raised mid-execution or after integration / merge; the protocol itself records how much rolls back via Step 4's box-unchecking and Step 6's re-entry point. There is one `PLAN.md` per analysis. Update it inline; do not start a parallel doc, append an "Addendum" section, or carry the change in chat.

**Material (require this protocol):**

- Adding, removing, or reordering a task block.
- Changing a task's objective, script, input, or output.
- Changing the analysis-level objective, methodology, sample definition, or expected output.
- Changing data sources or project-wide conventions.
- Scope additions arriving after integration or merge (post-PR additions, adjacent features surfaced by reviewers, follow-on ideas).
- Substantive restructure findings surfaced mid-INTEGRATE (by `integration-workflow` Phase B integration reviewer, Phase C doc-reviewer, or Phase D semantic-merge) — task add/remove/combine, DAG edge flip, prior APPROVED status invalidation. The orchestrator authors the Restructure Proposal; the researcher decides.

**Not material (handle as inline discovery edits per the Living Plan section above):**

- Rewording a step within an in-flight task to match what the data forced.
- Adjusting expected results based on early findings.
- Refining methodology details that the researcher already approved at planning time.

**Protocol:**

1. **Confirm intent.** A passing remark in chat is not authorization. Use `AskUserQuestion` (or a plain-text question if the tool is not available) to confirm the researcher wants the change. 
2. **Log the decision** per `handoff-doc` §User Decisions Log — top-level `## Decisions` for cross-task changes, task-scoped blockquote for single-task changes. The log entry must declare which tasks are affected and which project-level boxes are unchecked.
3. **Update `PLAN.md` inline:**
   - **Prefer modifying existing task blocks over appending.** Walk the task list and identify every task whose objective or output is affected by the change. Update each in place to reflect the new scope.
   - **New task** → Only when the change is genuinely independent of every existing task's scope, append `### Task N+1: [name]` with the full anatomy from `handoff-doc/references/plan-anatomy.md`. Renumber later tasks if inserting earlier in the sequence.
   - **Modified task** → rewrite the affected fields in place. Do not strike through. Do not add "Modified:" annotations.
   - **Removed task** → delete the block entirely. The Decisions entry preserves the rationale.
   - **Reordered tasks** → renumber and rewrite. The decision log preserves the original sequence.

4. **Update statuses** by orchestrator judgment. The orchestrator declares in the §Decisions entry *which* boxes are unchecked and *why*, then flips both the project-level `## Workflow Status` checkboxes and the per-task status lines. Rules: per-task `**Review status:**` and `**Integration status:**` on fully re-implemented tasks are cleared; untouched tasks retain APPROVED; minor-edited tasks (code unchanged) clear `**Integration status:**` while keeping `**Review status:** APPROVED`. **DAG cascade:** walk the transitive downstream closure of every changed task and clear statuses on any dependent whose inputs or assumptions shift.
5. **Sweep PLAN.md for stale content** per `handoff-doc` §Stale Content Checklist. Earlier task blocks whose output has been superseded by a later task, cross-references to removed sections, review notes resolved by subsequent work — fix in place now, not later.
6. **Commit atomically** — PLAN.md edit + decision log entry + any code touched by the change, in one commit. Title: `plan: <one-line scope change>`.
7. **Resume the appropriate workflow** for the new state. If the new task is unstarted, dispatch through `execution-workflow`. If the change rolled back `Refactored`, re-enter `integration-workflow` Phase B. On every re-entry, `integration-workflow` runs the **full** drift-test suite regardless of which tasks changed — only *authoring* new drift tests is scoped to the affected tasks. The doc-writer re-runs the whole matured doc; the doc-reviewer reviews the diff.


**Banned shortcuts:**

- Carrying the new task in chat or only in `TodoWrite` without writing it into `PLAN.md` (see §PLAN.md Is the Task Tracker above — `TodoWrite` is a transient view, not a record).
- Creating a `PLAN_v2.md` or appending an "Addendum" section. There is one `PLAN.md`.
- Resuming the in-flight task before reflecting the change in the doc — the change is not real until it is committed.
- Running a subset of the drift-test suite on re-entry because "only these tasks changed" — authoring is scoped, running is not. Always run the full suite.


## Remember

- Exact file paths always
- Complete content in every step
- For data analysis, row counts logged for every sample-changing operation
- Domain-appropriate discipline (for data: describe → analyze → validate at each step, with commit bundled into the validate step; documentation written continuously — see `superRA:econ-data-analysis`)
- Pipeline file for multi-artifact work

## Self-Review

After writing the complete plan:

**1. Domain inventory coverage (where applicable):** For data analysis, can you point to a task that handles each dataset from the Data Inventory section?

**2. Placeholder scan:** Search for the red flags listed in the "No Placeholders" section. Fix them.

**3. Pipeline consistency:** Do the artifact names in the pipeline file match the artifacts created in each task? Are they in the right order?

**4. Validation coverage:** Does every transformative step have a corresponding validation step? (For data: every merge, filter, and variable construction.)

**5. Plan serves as handoff:** If you stopped here and a new agent read only this plan and `RESULTS.md`, could they continue? Is there enough context?

**6. Sensitivity / robustness coverage (where applicable):** For data analysis, are sensitivity analysis tasks included? Were they discussed with the researcher to determine which checks matter most?

**7. Dependency graph sanity:** Every task has a `**Depends on:**` line. No cycles. If the plan has ≥2 independent branches, at least one pair of tasks is marked parallelizable.

Fix issues inline. No need to re-review — just fix and move on.

## Execution Handoff

After finalizing the plan, check the **`Plan approved`** box in `PLAN.md` §Workflow Status (see `superRA:handoff-doc` references/plan-anatomy.md for the checklist anatomy) and commit the plan + box-flip atomically. Then offer execution choice:

**"Plan complete and saved to `PLAN.md`. RESULTS.md created. Two execution options:**

**1. Subagent-Driven (recommended for independent tasks)** - I dispatch a fresh subagent per task, review between tasks, fast iteration. Best when tasks don't heavily depend on each other's outputs.

**2. Inline Execution (recommended for sequential pipelines)** - Execute tasks in this session using execution-workflow, context preserved across steps. Best when each step's output informs the next.

**Which approach?"**

**REQUIRED DISCIPLINE:** Use `superRA:execution-workflow`
- Defaults to subagent mode (fresh subagent per task + one-pass review per the active domain skill's §Three Concurrent Disciplines)
- Falls back to direct mode for simple tasks or when user requests it
- Review always happens regardless of mode
