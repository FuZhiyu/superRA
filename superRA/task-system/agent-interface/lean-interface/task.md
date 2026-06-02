---
title: "Lean Task Interface — Relocate Universal Core to using-superRA"
status: approved
depends_on: []
tags: []
created: 2026-06-01
---

## Objective

Relocate the *universal* task-system interface into `using-superRA` so that `task-system/SKILL.md` stops being a mandatory mixed-audience load and becomes genuinely load-on-demand tooling for orchestrators, planners, and contributors.

**The problem.** `task-system/SKILL.md` carries consumer, planner, and contributor concerns at once. A prior round (`../skill-restructure`, "Progressive Skill Revelation", approved) split it into three tiers — SKILL.md (consumer), `references/planning.md` (planner), `references/internals.md` (contributor) — but the consumer tier still dumps orchestrator/planner/contributor material on every executing agent (frontier, DAG, dashboard, `task_create`/`task_link`/`task_rename`, migration, v1→v2 upgrade), none of which an implementer or reviewer needs. Worse, the genuinely-shared editing interface is *duplicated*: the editing-etiquette block is copy-pasted across `agents/implementer.md §Editing Etiquette`, `agents/reviewer.md §Editing Etiquette`, and the two generated `direct-mode-*` references (four copies), and `SKILL.md §Command Surface` duplicates `references/planning.md §Hierarchy Management Commands`.

**The decision (confirmed with the researcher).** Fold the universal task interface into `using-superRA/SKILL.md` — the only skill preloaded via agent frontmatter (`skills: [superRA:using-superra]`), so this adds **zero** new mandatory loads. `task-system` then drops to load-on-demand. The role specs keep only role-specific protocol and point to the new `using-superRA` core for shared principles. This collapses both existing duplications (editing etiquette across role specs; command surface across SKILL.md/planning.md) into one source of truth each.

**Target ownership after this work:**
- **Universal task interface** (read a task, edit a task + hook safety net, status enum, body-section vocabulary, shared editing principles, ownership-boundary principle) → `using-superRA/SKILL.md`.
- **Tree tooling** (core concepts for tree reasoning, query/frontier/DAG, mutation command surface, dashboard, migration) → `task-system/SKILL.md`, load-on-demand.
- **Planner depth** (objective writing, splitting, placement, results shape, stale-content, conventions, retroactive, field-by-field anatomy) → `task-system/references/planning.md` (unchanged role).
- **Contributor depth** (data layer, hooks, migration internals) → `task-system/references/internals.md` (unchanged role).
- **Role protocol** (annotation mechanics, status-transition authority, verdict) → `agents/implementer.md` / `agents/reviewer.md`.

**Out of scope for this round (do not touch):** the `task_read.py` / root `## Conventions` redundancy — the role specs' step-4 "Read the root task.md `## Conventions` section" instruction stays as-is. `task_read.py` currently injects only a 10-line excerpt of each ancestor's first section (the objective), not `## Conventions`, so step 4 is not redundant today; reconciling that is a separate effort.

**Contributor gates that apply to every child task** (from repo `CLAUDE.md`):
- Load `skill-creator` before editing any `skills/*/SKILL.md`.
- Apply the "Teach the Protocol, Don't Prescribe Each Action" gate line-by-line: every line must pass DRY (don't restate what another skill/reference/role spec already carries — point instead) and Necessity (delete any line that only tells the agent what it would already do). The whole point of this work is removing duplication; do not reintroduce it.
- Generated files (`skills/using-superRA/references/direct-mode-implementer.md`, `direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml`) are produced by `skills/codex-superra-setup/scripts/sync_codex_agents.py` from `agents/implementer.md` / `agents/reviewer.md` — edit the source, then regenerate; never hand-edit the generated files.
- Scope all edits to this worktree: `/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/better-handoff-skill-instruction`.

**Success criterion for the whole subtree:** a dispatched implementer or reviewer that loads only `using-superRA` (its single frontmatter preload) can correctly read and edit its assigned `task.md` without loading `task-system`; no shared content is duplicated across more than one owner; and — the load-bearing invariant — **no knowledge is lost for any agent**: every distinct unit of guidance that existed before the restructure is still present somewhere after and still reachable by every role that needs it through that role's actual load path. Removing a duplicate is fine (the single surviving copy must stay reachable); removing or stranding the only copy is not. Task `05-coverage-audit` proves this invariant against a git snapshot of the pre-restructure surfaces.

## Results
