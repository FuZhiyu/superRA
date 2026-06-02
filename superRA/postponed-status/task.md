---
title: "Add postponed task status"
status: approved
depends_on: []
tags: []
created: 2026-06-01
---

## Objective

Add a new task status `postponed` to the superRA task system. A `postponed` task still exists in the tree (it is not deleted), but it never enters the dispatch frontier and never contaminates completion accounting. It is the "park this work for now, maybe resume later" status, sitting alongside the existing `archived` ("removed from scope, treat as resolved") status.

`postponed` deliberately mirrors `archived` in most respects but differs in one place — dependency satisfaction (see the semantics table below). The canonical owner of the status set is `VALID_STATUSES` in `skills/task-system/scripts/_task_io.py`; every other site either imports that constant or hard-codes an echo of the enum that must be kept in sync.

### Target semantics for `postponed`

| Behavior | `archived` (today) | `postponed` (this feature) |
| --- | --- | --- |
| A `postponed` *leaf* on the frontier | never | never — same as archived |
| Excluded from completion % denominator on the dashboard | yes | yes |
| Parent rollup with an `approved` child + a parked child | can reach `approved` | can reach `approved` |
| Parent rollup when *all* children are parked | → `archived` | → `postponed` (a deferred child dominates an abandoned one) |
| Does a parked task **satisfy a dependent's `depends_on`**? | yes (downstream proceeds) | **no — dependents are blocked until it is resumed and approved** |

The dependency difference is the design crux, confirmed with the researcher on 2026-06-01: postponing task A parks A *and its whole downstream chain*, because a dependent typically consumes A's output and cannot run without it. `archived` differs because an archived task is treated as resolved/removed, so downstream proceeds.

### Resume model

A task is resumed by setting its status back to `not-started` (via `task_update.py --status not-started`, or `--cascade --status not-started` for a subtree that was postponed in bulk). Postpone does not preserve a prior `implemented`/`approved` signal — parking is expected to apply to not-yet-finished work; resuming starts the task fresh. This is an intentional limitation, not a gap to design around.

## Conventions

- **This is a contributor change to superRA itself, not research analysis.** No data-analysis / theory / writing domain vertical applies. The relevant discipline is skill-authoring discipline.
- **Skill-prose edits are skill creation.** Any task that edits a `skills/*/SKILL.md` or `agents/*` file loads `skill-creator` first and self-applies the "Teach the Protocol, Don't Prescribe Each Action" DRY/Necessity gate in `CLAUDE.md` line by line before committing.
- **Single source of truth for the enum:** `skills/task-system/scripts/_task_io.py` `VALID_STATUSES` (line ~20). Validation (`parse_task`, `validate_frontmatter`), `task_check.py`, and `task_update.py --status` choices all derive from it. Dashboard templates and `task_query.py` hard-code echoes that must be edited explicitly.
- **`archived` is the reference implementation.** For every site, find how `archived` is handled and mirror it for `postponed`, *except* the dependency-satisfaction site, where `postponed` must NOT be added to the satisfying set.
- **No generated artifacts are affected.** A grep of `skills/using-superRA/references/` (direct-mode role refs), `.codex/agents/`, and `agents/` on 2026-06-01 found no echo of the status enum, so no `sync_codex_agents.py` regeneration is required. The doc task re-confirms this with a fresh grep before completing.
- **Verify the real user path** for the dashboard task: regenerate an actual dashboard containing a postponed task and inspect the rendered HTML — do not stop at editing template source.

## Results

`postponed` is now a first-class task status across the task system. A postponed task stays in the tree but is parked off the dispatch frontier and excluded from completion accounting — the "defer this, maybe resume later" status, alongside `archived` ("removed from scope, treat as resolved").

**Behavior (see `01-core-semantics` for the per-site record):** a postponed leaf never enters the frontier; a branch whose children are all parked rolls up to `postponed` when any child is postponed (else `archived`); postponed children are excluded from a parent's completion rollup, so a parent with `[approved, postponed]` children still reaches `approved`. The one deliberate divergence from `archived`: a postponed task **blocks its dependents** — anything that `depends_on` it stays off the frontier until it is resumed (`archived` lets dependents through, because archived work is treated as resolved). Resume by setting the status back to `not-started` (`--cascade` for a bulk-parked subtree). Set by the orchestrator/researcher as a scope decision, not by an implementer/reviewer verdict.

**Surfaces (`02-rendering-surfaces`):** rendered everywhere a status appears — CLI tree icon (`⏸`) and mermaid DAG class, dashboard badge/color (slate, distinct from archived grey), a Postponed kanban column, the status filter, and the DAG fill. The completion bar excludes postponed leaves from the denominator and shows a separate postponed count. Verified against a rendered dashboard, not just template source.

**Docs (`03-docs`) + integration:** documented in the task-system SKILL/references and the agent-orchestration Review Status Reference; a dependency-integrity diagnostic in `task_check.py` now warns when a task depends on a postponed task (it is blocked until resumed), mirroring the archived warning; `RELEASE-NOTES.md` carries an `[Unreleased] → Added` entry.

**Verification:** full task-system + dashboard suite green (296 passed), including 17 new regression tests pinning the frontier/rollup/dependency-blocking/cascade/rendering/diagnostic behavior. Single source of truth for the enum is `VALID_STATUSES` in `_task_io.py`; no generated artifact echoes the enum, so none needed regeneration.
