---
title: "Recursive Context and Conventions"
status: approved
depends_on:
  - 01-objective-guidance-task-anatomy
  - 02-objective-first-reviewer
  - 03-planning-review-mode
  - 04-guidance-deviation-reporting
tags: []
created: 2026-06-01
---

## Objective

Resolve the PR #29 follow-up comments about root-task-special convention handling by making task context recursive across the ancestor chain.

### Context

The task system is recursive: any task can carry context for its subtree, and the top filesystem task is not a special semantic owner for conventions. Current text still treats `superRA/task.md` as a convention cache that every implementer/reviewer must read separately. Replace that with ancestor-context semantics: an agent reading a task receives the relevant ancestor chain, and reusable context/conventions should live on the lowest ancestor whose subtree they govern.

This task builds on the approved `## Objective` / `## Planner Guidance` split. The preferred design is to keep inherited binding context inside the planner-owned `## Objective` surface, using scoped `### Context`, `### Conventions`, or `### Constraints` subsections only when they change what an implementation or review agent does. Do not introduce a new protected top-level `## Context` or `## Conventions` protocol unless implementation uncovers a concrete behavior that cannot be represented under `## Objective` without ambiguity. If the implementer chooses the top-level-section alternative, document the specific behavior that requires it and keep ownership and precedence rules minimal.

### Scope

- Update `skills/task-system/scripts/task_read.py` so ancestor rendering exposes full ancestor `## Objective` content, including nested `###` subsections, instead of the current first-section excerpt capped at 10 lines. Preserve compatibility in JSON output by adding an explicit ancestor objective field rather than removing existing keys.
- Update `skills/task-system/references/planning.md` so task anatomy is recursive. It should describe how scoped context/conventions are placed in the relevant task objective, and remove root-only convention ownership.
- Update `skills/superplan/SKILL.md` to address the PR comments:
  - remove duplicated terminology prose already owned by AGENTS.md / `using-superRA`;
  - keep legacy `PLAN.md` migration only as backward compatibility when `superRA/` is absent and a legacy file exists;
  - remove ordinary `PLAN.md` wording outside that migration fallback;
  - treat consolidation as its own workflow/reference, not a regular planning routing mode;
  - remove root-task convention caching and replace it with scoped ancestor-objective context;
  - keep recursive task anatomy in `task-system/references/planning.md`, while `superplan` owns phase choreography.
- Update `skills/superimplement/SKILL.md` and `skills/using-superRA/references/main-agent.md` so helper skills, convention context, and resolver facts come from the active task/ancestor chain rather than only the top task file.
- Address the PR #29 comment questioning the value of the heading/description renames (`# superimplement — the IMPLEMENT phase` → `# Implementation Workflow`, and the parallel `# superplan — the PLAN phase` → `# Planning Workflow`). For each rename, either revert to the original phase-named heading/description or justify the change as behavior-shaping; do not keep gratuitous reword that only changes what the agent understands, per the AGENTS.md Necessity test.
- Update `agents/implementer.md` and `agents/reviewer.md` so roles rely on `task_read.py` for ancestor context and walk project docs on demand only when that context is missing, stale, or insufficient for the touched files.
- Revisit domain planning references that currently say inventories or convention tables live in the root task. Give them scoped semantics: data/model/manuscript/workstream-level by default, project-wide only when deliberately placed at the top ancestor.
- Update `skills/codex-superra-setup/scripts/sync_codex_agents.py` and regenerate generated artifacts instead of hand-editing them: `skills/using-superRA/references/direct-mode-implementer.md`, `skills/using-superRA/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, and `.codex/agents/superra_reviewer.toml`.

### Validation

- `task_read.py` tests prove that human output includes full ancestor `## Objective` content beyond the old 10-line cap and that JSON output includes the new explicit objective field while preserving existing keys.
- A stale-reference sweep finds no behavior-shaping instruction that requires root `## Conventions` as the source for implementer/reviewer context. Filesystem-root, dashboard-root, migration, and integration-global Sync Map references may remain when they are actually about those concerns.
- Generated Codex artifacts are in sync: `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check`.
- Targeted tests pass: task-system tests covering `task_read.py`, plus `uv run pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py`.
- Every new or changed instruction line passes the AGENTS.md DRY and Necessity tests.

## Results

### Key Findings

- **`task_read.py` ancestor rendering is now full-objective.** Replaced the 10-line `_first_body_excerpt` cap with `_ancestor_objective`, which returns each ancestor's complete `## Objective` (nested `### Context` / `### Conventions` / `### Constraints` included), falling back to the first body section then first paragraph for pre-convention tasks ([../../../skills/task-system/scripts/task_read.py:84](../../../../../skills/task-system/scripts/task_read.py#L84)). Human output prints the whole objective; JSON adds an explicit `objective` key and keeps `first_section` (now mirroring it) plus `sections`, `path`, `title`, `status`, `effective_status` so existing consumers are unaffected ([../../../skills/task-system/scripts/task_read.py:242](../../../../../skills/task-system/scripts/task_read.py#L242)). Verified on the real `review-planning-protocol` ancestor: 1215-char objective rendered in full, well past the old cap.
- **Recursive task anatomy in the planning reference.** Renamed "Root task.md Anatomy" → "Task Anatomy" applying to every task, and "Conventions Section" → "Ancestor Context and Conventions"; both now teach that scoped context lives on the lowest ancestor whose subtree it governs and is inherited via `task_read.py`, removing root-only convention ownership ([../../../skills/task-system/references/planning.md:75](../../../../../skills/task-system/references/planning.md#L75), [../../../skills/task-system/references/planning.md:140](../../../../../skills/task-system/references/planning.md#L140)). Added a scoped-context paragraph to §Writing Objectives ([../../../skills/task-system/references/planning.md:20](../../../../../skills/task-system/references/planning.md#L20)).
- **`superplan` PR comments addressed.** Removed the duplicated terminology paragraph (owned by AGENTS.md §Terminology); kept legacy `PLAN.md` only as the `superRA/`-absent migration fallback; demoted consolidation from a routing mode to a separate cleanup pass owned by `references/consolidation.md`; replaced root convention caching with scoped-objective distillation; renamed §"Root task.md and Task Anatomy" → §"Task Anatomy" ([../../../skills/superplan/SKILL.md:16](../../../../../skills/superplan/SKILL.md#L16), [../../../skills/superplan/SKILL.md:32](../../../../../skills/superplan/SKILL.md#L32), [../../../skills/superplan/SKILL.md:89](../../../../../skills/superplan/SKILL.md#L89), [../../../skills/superplan/SKILL.md:129](../../../../../skills/superplan/SKILL.md#L129)).
- **Heading renames reverted.** The `# superplan — the PLAN phase` → `# Planning Workflow` rename (and the parallel superimplement/superintegrate renames from commit 3e0de358) only changed what the agent understands, not what it does, and dropped the explicit phase label that the body still carries. Per the AGENTS.md Necessity test, reverted all three H1s to their phase-named form ([../../../skills/superplan/SKILL.md:6](../../../../../skills/superplan/SKILL.md#L6), [../../../skills/superimplement/SKILL.md:6](../../../../../skills/superimplement/SKILL.md#L6), [../../../skills/superintegrate/SKILL.md:6](../../../../../skills/superintegrate/SKILL.md#L6)). The `name:` frontmatter (the actual subject of the 3e0de358 Workflow-tool-collision fix) was left untouched.
- **Resolver and role context come from the ancestor chain.** `superimplement` Step 1 now reads scoped `### Conventions`/`### Context`/`### Constraints` from the active task and ancestors and loads helper skills named anywhere in the chain ([../../../skills/superimplement/SKILL.md:74](../../../../../skills/superimplement/SKILL.md#L74), [../../../skills/superimplement/SKILL.md:75](../../../../../skills/superimplement/SKILL.md#L75)); `main-agent.md` Workflow Frontier Resolver reads scoped objective context via `task_read.py`, keeping only the genuinely-global `## Sync Map` / Step-4 disposition / pipeline on the top task ([../../../skills/using-superRA/references/main-agent.md:34](../../../../../skills/using-superRA/references/main-agent.md#L34)); both role specs now treat the rendered ancestor context as their convention source and walk docs on-demand only when the chain is insufficient for the touched files ([../../../agents/implementer.md:22](../../../../../agents/implementer.md#L22), [../../../agents/reviewer.md:29](../../../../../agents/reviewer.md#L29)).
- **Domain planning references scoped.** econ-data-analysis Data Inventory and theory-modeling Model Inventory / Notation Conventions now place their artifacts on the `## Objective` of the task whose subtree they govern (the top task for single-workstream / single-model / single-manuscript projects, the subtree root otherwise) instead of asserting root-special ownership ([../../../skills/econ-data-analysis/references/planning.md:10](../../../../../skills/econ-data-analysis/references/planning.md#L10), [../../../skills/theory-modeling/references/planning.md:9](../../../../../skills/theory-modeling/references/planning.md#L9), [../../../skills/writing/references/planning.md:13](../../../../../skills/writing/references/planning.md#L13)). The orchestrator override example and the deprecated handoff-doc pointer were updated to match ([../../../skills/agent-orchestration/SKILL.md:178](../../../../../skills/agent-orchestration/SKILL.md#L178), [../../../skills/handoff-doc/SKILL.md:15](../../../../../skills/handoff-doc/SKILL.md#L15)).
- **No new top-level protocol introduced.** All inherited binding context stays inside planner-owned `## Objective` via scoped `###` subsections, as the objective preferred.
- **Writing `## Project Conventions` surface scoped to the manuscript-governing task.** The writing vertical's existing `## Project Conventions` surface no longer pins to "root `superRA/task.md` read separately by every writing agent." It now lives on the `## Objective` of the manuscript-governing task — the top `superRA/task.md` for a single-manuscript project, or the writing-subtree root otherwise — inherited via the ancestor chain, matching the econ Data Inventory and theory Model Inventory scoping. Genuinely paper-wide conventions stay at the manuscript ancestor (the allowed deliberate top-ancestor placement); the promotion ladder is otherwise unchanged ([../../../skills/writing/SKILL.md:40](../../../../../skills/writing/SKILL.md#L40), [../../../skills/writing/CLAUDE.md:33](../../../../../skills/writing/CLAUDE.md#L33), [../../../skills/writing/references/long-form-review.md:19](../../../../../skills/writing/references/long-form-review.md#L19), [../../../skills/writing/references/long-form-review.md:55](../../../../../skills/writing/references/long-form-review.md#L55)). `polish.md`/`draft.md` reach the surface only through the `SKILL.md §Project Conventions` pointer, so they inherit the scoped semantics unchanged.

### Validation

- `uv run pytest skills/task-system/scripts/test_task_system.py skills/task-system/scripts/test_dashboard.py skills/task-system/scripts/test_worktree_selector.py skills/task-system/scripts/tests/test_state_preservation.py skills/codex-superra-setup/scripts/test_sync_codex_agents.py` — 384 passed. Added two `task_read` tests proving full-objective human output past the old 10-line cap (including a nested `### Conventions` subsection) and the explicit JSON `objective` field with all prior keys preserved ([../../../skills/task-system/scripts/test_task_system.py:1947](../../../../../skills/task-system/scripts/test_task_system.py#L1947)).
- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` — generated agents and direct-mode references up to date after regeneration from the edited role specs and generator.
- `python3 skills/task-system/scripts/task_check.py --plan-root superRA` — all checks passed.
- Stale-reference sweep: no behavior-shaping instruction now requires a root `## Conventions` cache as the implementer/reviewer convention source. Remaining `root task.md` references are integration-global (`## Sync Map`), the deliberately-project-wide theory-modeling Notation Conventions canonical table, dashboard/migration concerns, or the top task as a real task — all legitimately root-scoped.
- DRY/Necessity self-check on changed instruction lines: each edit shapes behavior at its owner surface (ancestor-context convention sourcing, scoped placement, consolidation demotion) or removes a duplicate (terminology paragraph). The reverted headings restored the more-informative phase label rather than adding instruction.

### Notes

- **Generated artifacts** were regenerated, never hand-edited: `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml`, `skills/using-superRA/references/direct-mode-implementer.md`, `skills/using-superRA/references/direct-mode-reviewer.md` via `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`. The generator's inline direct-mode `## Before You Start` strings for both roles were updated at source so the regenerated files carry the ancestor-context wording. The REVISE-round writing-vertical re-scoping touched only `skills/writing/*` and `skills/task-system/references/planning.md` (no generator inputs); `--scope project --check` confirmed generated artifacts remain in sync.

### Guidance Deviations

- None — the task carried no `## Planner Guidance` section; all work followed the `### Scope` deliverables.
