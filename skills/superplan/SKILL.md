---
name: superplan
description: "Proactively plan or update superRA work. Requires superRA:using-superra. Use when starting or changing work, creating/revising superRA/, or reflecting material decisions in the task tree."
---

# superplan — the PLAN phase

**First, load `superRA:using-superra` if not already loaded.**

**If the harness has activated plan mode, load `references/harness-plan-mode.md` before proceeding.**

## Overview

Owns the procedural shape of the **PLAN** phase: discovery of existing work, exploration, domain setup, task decomposition, self-review, and handoff. Output is a `superRA/` task tree for superimplement to consume.

The `## Objective` / `## Planner Guidance` split — contract vs. planning findings — is in `references/task-tree-design.md` §Writing Objectives and Planner Guidance.

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

Map the artifact pipeline, decompose the work into tasks with the active domain skill's full discipline applied, wire dependencies, and create the `superRA/` directory. Load `references/decomposition.md` for the mechanics — artifact pipeline and pipeline file, task structure, wrapper-first creation, the no-checkboxes rule, dependency tracing, task anatomy, and the umbrella-task decision.

## Phase 4: Review & Commit

### Self-Review

After writing the complete task tree, run the self-review checklist in `references/decomposition.md` §Self-Review — domain-inventory coverage, placeholder scan, pipeline consistency, validation and verification coverage, objective/guidance split, handoff test, dependency-graph sanity, and subtask coverage. Fix issues inline; no need to re-review.

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

The task tree is not a static spec — it evolves in place as work reveals surprises, and `superRA/` (not chat or `TodoWrite`) is the authoritative tracker of record. Distinguish **agent-discovered refinements** (handled as inline body edits) from **researcher-initiated scope changes** (routed through §User Feedback and Changing the Task Tree below). `references/changing-the-tree.md` owns the drift distinction, the tracker-of-record rule, and the live-`## Results` record.

## User Feedback and Changing the Task Tree

When the task tree changes — details updated, tasks added/removed/restructured, objective shifted, whether raised mid-execution or after integration/merge — route through `references/changing-the-tree.md`. It owns the materiality test (material scope changes vs. non-material inline discovery edits) and the full protocol: confirm intent → update `superRA/` inline → reset statuses → sweep stale content → commit atomically (`plan(<sub-step>): …`) → resume on the affected frontier. Do not resume the in-flight task before the change is committed, and do not treat an invalidated milestone as license to clear unrelated approved tasks.
