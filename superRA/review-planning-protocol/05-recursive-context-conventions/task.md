---
title: "Recursive Context and Conventions"
status: not-started
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

