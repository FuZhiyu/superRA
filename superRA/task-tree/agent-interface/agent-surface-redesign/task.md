---
title: "Agent-Facing Surface Redesign — Lean Relocation + Role-Spec Restructure"
status: revise
depends_on: []
tags: []
created: 2026-06-01
---

## Objective

Redesign the agent-facing surfaces — the two role specs (`agents/implementer.md`, `agents/reviewer.md`), `using-superRA/SKILL.md`, `task-tree/SKILL.md`, and the generated `direct-mode-*` / `superra_*.toml` artifacts — into a clean, deduplicated, load-on-demand structure, **losing no behavior-shaping instruction for any role**. In the release diff vs merge-base `5dfe928b` this is one coherent net delta to those surfaces (≈368 insertions / 375 deletions across six files); it was produced in two phases tracked as the children below.

**Phase A — Lean relocation (tasks 01–05).** Fold the *universal* task interface (read/edit a task + hook safety net, status enum, body-section vocabulary, shared editing principles, ownership-boundary principle) into `using-superRA/SKILL.md` — the only skill preloaded via agent frontmatter (`skills: [superRA:using-superra]`), so it adds **zero** new mandatory loads — and drop `task-tree/SKILL.md` to load-on-demand tree tooling. A prior round (`../skill-restructure`, "Progressive Skill Revelation") split task-tree into three tiers but the consumer tier still dumped orchestrator/planner/contributor material on every executing agent, and the editing-etiquette block was copy-pasted across four files. Phase A collapses both duplications (editing etiquette across role specs; command surface across SKILL.md/planning.md) to one source of truth each, then a DRY/Necessity follow-up (05) cleans residual echoes.

**Phase B — Role-spec restructure (tasks 06–08).** A holistic clarity restructure of the two role specs that had accreted across many incremental passes: rewrite both to one parallel skeleton, relocate planning-review mode to the planning workflow, reconcile the heading-coupled generator, and collapse the reporting model onto *commit = change summary, return = status + SHA, `## Results` = latest state*.

**Target ownership after this work:**
- **Universal task interface** → `using-superRA/SKILL.md` §Task Interface.
- **Tree tooling** (tree concepts, query/frontier/DAG, mutation command surface, dashboard, migration) → `task-tree/SKILL.md`, load-on-demand.
- **Planner depth** (objective writing, splitting, placement, results shape, stale-content, anatomy) → `task-tree/references/planning.md`.
- **Contributor depth** (data layer, hooks, migration internals) → `task-tree/references/internals.md`.
- **Role protocol** (per-role ownership, status-transition authority, verdict, REVISE mechanics) → `agents/implementer.md` / `agents/reviewer.md`.

**Contributor gates that apply to every child task** (from repo `CLAUDE.md`):
- Load `skill-creator` before editing any `skills/*/SKILL.md`.
- Apply the "Teach the Protocol, Don't Prescribe Each Action" gate line-by-line: every line must pass DRY (point, don't restate what another skill/reference/role spec already carries) and Necessity (delete any line that only tells the agent what it would already do). This work removes duplication; do not reintroduce it.
- Generated files (`skills/using-superRA/references/direct-mode-implementer.md`, `direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml`) are produced by `skills/codex-superra-setup/scripts/sync_codex_agents.py` from the role specs — edit the source + generator, then regenerate; never hand-edit a generated file.
- Scope all edits to the project worktree.

**Success criterion for the whole subtree:** a dispatched implementer or reviewer that loads only `using-superRA` (its single frontmatter preload) can correctly read and edit its assigned `task.md` without loading `task-tree`; no shared content is duplicated across more than one owner; and — the load-bearing invariant — **no knowledge is lost for any agent**. Removing a duplicate is fine (the single surviving copy must stay reachable); removing or stranding the only copy is not. Task `09-coverage-audit` proves this invariant against git snapshots of both phases' pre-round surfaces.

## Results

## Review Notes

> 1. [MAJOR] `## Results` is empty on this approved 9-child redesign parent. The objective promises "one coherent net delta", but no rollup exists and readers must reverse-engineer the outcome from nine children. Add the matured narrative with links to child evidence per the Results lifecycle in [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md) §Results Shape.
