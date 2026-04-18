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

**Before you create directories or start editing:** if this work may span multiple sessions, run in parallel with other work, or need an isolated data / environment copy, consider loading `superRA:worktree-data-sync` for the worktree setup before any file creation. A worktree at this point is cheap; retrofitting one later is not. For simple single-session work on an existing branch, skip it — a feature branch is sufficient. (See `worktree-data-sync` §When to Use a Worktree for the full decision table.)

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
dependency. See the task-block template in `references/plan-template.md` for the required format.

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

**The editing discipline and the full anatomy templates** — the four document principles, inline-edit rule, stale-content checklist, User Decisions Log format, figure-embedding pointer, `## Project Conventions` layout, section layouts, code-block examples, status-line formats, the two-stage `RESULTS.md` lifecycle — live in `superRA:handoff-doc`. Load it when authoring `PLAN.md` / `RESULTS.md` from scratch; its `references/plan-anatomy.md` and `references/results-anatomy.md` carry the full templates. Role-by-role ownership and the review-loop annotation protocols live in `agents/implementer.md` and `agents/reviewer.md`.

**Results document:** Create `RESULTS.md` alongside `PLAN.md`. For the starter scaffold and anatomy, load `superRA:handoff-doc` and read `references/results-anatomy.md`. It is the Stage 1 form of `RESULTS.md`; at `integration-workflow` Step 3 it matures into a permanent record.

## No Placeholders

Every step must contain the actual code, instructions, or artifacts someone needs to execute it. These are **plan failures** — never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate validation" / "check results" (without actual code or criteria)
- "Similar to Task N" (repeat the content — the executor may read tasks out of order)
- "Run descriptive statistics" (without showing which variables and what statistics)
- Steps that describe what to do without showing how (code blocks required for code steps)

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

After finalizing the plan, commit it, then offer execution choice:

**"Plan complete and saved to `PLAN.md`. RESULTS.md created. Two execution options:**

**1. Subagent-Driven (recommended for independent tasks)** - I dispatch a fresh subagent per task, review between tasks, fast iteration. Best when tasks don't heavily depend on each other's outputs.

**2. Inline Execution (recommended for sequential pipelines)** - Execute tasks in this session using execution-workflow, context preserved across steps. Best when each step's output informs the next.

**Which approach?"**

**REQUIRED DISCIPLINE:** Use `superRA:execution-workflow`
- Defaults to subagent mode (fresh subagent per task + one-pass review per the active domain skill's §Three Concurrent Disciplines)
- Falls back to direct mode for simple tasks or when user requests it
- Review always happens regardless of mode
