---
title: "Agent-Facing Surface Redesign — Lean Relocation + Role-Spec Restructure"
status: approved
depends_on: []
tags: []
created: 2026-06-01
---

## Objective

Redesign the agent-facing surfaces — the two role specs (`agents/implementer.md`, `agents/reviewer.md`), `using-superra/SKILL.md`, `task-tree/SKILL.md`, and the generated `direct-mode-*` / `superra_*.toml` artifacts — into a clean, deduplicated, load-on-demand structure, **losing no behavior-shaping instruction for any role**. In the release diff vs merge-base `5dfe928b` this is one coherent net delta to those surfaces (≈368 insertions / 375 deletions across six files); it was produced in two phases tracked as the children below.

**Phase A — Lean relocation (tasks 01–05).** Fold the *universal* task interface (read/edit a task + hook safety net, status enum, body-section vocabulary, shared editing principles, ownership-boundary principle) into `using-superra/SKILL.md` — the only skill preloaded via agent frontmatter (`skills: [superRA:using-superra]`), so it adds **zero** new mandatory loads — and drop `task-tree/SKILL.md` to load-on-demand tree tooling. A prior round (`../skill-restructure`, "Progressive Skill Revelation") split task-tree into three tiers but the consumer tier still dumped orchestrator/planner/contributor material on every executing agent, and the editing-etiquette block was copy-pasted across four files. Phase A collapses both duplications (editing etiquette across role specs; command surface across SKILL.md/planning.md) to one source of truth each, then a DRY/Necessity follow-up (05) cleans residual echoes.

**Phase B — Role-spec restructure (tasks 06–08).** A holistic clarity restructure of the two role specs that had accreted across many incremental passes: rewrite both to one parallel skeleton, relocate planning-review mode to the planning workflow, reconcile the heading-coupled generator, and collapse the reporting model onto *commit = change summary, return = status + SHA, `## Results` = latest state*.

**Target ownership after this work:**
- **Universal task interface** → `using-superra/SKILL.md` §Task Interface.
- **Tree tooling** (tree concepts, query/frontier/DAG, mutation command surface, dashboard, migration) → `task-tree/SKILL.md`, load-on-demand.
- **Planner depth** (objective writing, splitting, placement, results shape, stale-content, anatomy) → `task-tree/references/planning.md`.
- **Contributor depth** (data layer, hooks, migration internals) → `task-tree/references/internals.md`.
- **Role protocol** (per-role ownership, status-transition authority, verdict, REVISE mechanics) → `agents/implementer.md` / `agents/reviewer.md`.

**Contributor gates that apply to every child task** (from repo `CLAUDE.md`):
- Load `skill-creator` before editing any `skills/*/SKILL.md`.
- Apply the "Teach the Protocol, Don't Prescribe Each Action" gate line-by-line: every line must pass DRY (point, don't restate what another skill/reference/role spec already carries) and Necessity (delete any line that only tells the agent what it would already do). This work removes duplication; do not reintroduce it.
- Generated files (`skills/using-superra/references/direct-mode-implementer.md`, `direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml`) are produced by `skills/codex-superra-setup/scripts/sync_codex_agents.py` from the role specs — edit the source + generator, then regenerate; never hand-edit a generated file.
- Scope all edits to the project worktree.

**Success criterion for the whole subtree:** a dispatched implementer or reviewer that loads only `using-superra` (its single frontmatter preload) can correctly read and edit its assigned `task.md` without loading `task-tree`; no shared content is duplicated across more than one owner; and — the load-bearing invariant — **no knowledge is lost for any agent**. Removing a duplicate is fine (the single surviving copy must stay reachable); removing or stranding the only copy is not. Task `09-coverage-audit` proves this invariant against git snapshots of both phases' pre-round surfaces.

## Results

The agent-facing surfaces for the superRA workflow — `agents/implementer.md`, `agents/reviewer.md`, `using-superra/SKILL.md`, `task-tree/SKILL.md`, and the four generated `direct-mode-*` / `superra_*.toml` artifacts — were redesigned into a clean, deduplicated, load-on-demand structure across nine coordinated child tasks. The release diff vs merge-base `5dfe928b` is one coherent net delta (≈368 insertions / 375 deletions across six files) with no knowledge lost for any agent role.

**Phase A — Lean relocation ([01](01-core-in-using-superra/task.md)–[05](05-review-followups/task.md)):** The universal task interface (read/edit a task, hook safety net, status enum, body-section vocabulary, shared editing principles, ownership-boundary principle) was folded into `using-superra/SKILL.md §Task Interface` — preloaded by every subagent via frontmatter, so zero new mandatory loads were added. `task-tree/SKILL.md` was reduced to load-on-demand tree tooling. The editing-etiquette block that had been copy-pasted across four files now lives in one place; the mutation command surface was consolidated into `references/commands.md`. Task [05](05-review-followups/task.md) cleaned residual DRY/Necessity gate violations.

**Phase B — Role-spec restructure ([06](06-restructure-specs/task.md)–[08](08-report-commit-model/task.md)):** Both role specs were rewritten to one parallel skeleton with planning-review mode relocated to `superplan/references/planning-review.md` (manifest-loaded), the generator reconciled to the new heading structure, and the reporting model collapsed onto *commit = change summary, return = status + SHA, `## Results` = latest state*. The `## Results` human-readability principle was stated once in `using-superra §Task Interface` and referenced from the implementer §Self-Check and reviewer §Review Protocol.

**[09-coverage-audit](09-coverage-audit/task.md)** proved the no-knowledge-lost invariant: 39 baseline units from Round 1 and 43 from Round 2 were all classified (K/R/D/ID/RA), zero LOST, zero dangling pointers in live surfaces.

**Target ownership confirmed:**
- Universal task interface → `using-superra/SKILL.md §Task Interface` (preloaded by all agents)
- Tree tooling → `task-tree/SKILL.md`, load-on-demand
- Role protocol → `agents/implementer.md` / `agents/reviewer.md`
