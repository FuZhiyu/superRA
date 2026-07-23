---
title: "De-crowd superplan SKILL.md into a routing spine"
status: implemented
depends_on: []
---

## Objective

Slim `skills/superplan/SKILL.md` (currently ~196 lines) to a **routing spine** and move phase detail into references, without dropping or weakening any gate. Progressive disclosure: `SKILL.md` keeps Overview, Entry Assessment, Depth Tiers, the Phase 1–4 sequence as pointers, and Substantive Questions; the mechanical detail moves out.

Content to relocate into new or existing references (one level deep, each with a clear load condition from `SKILL.md`):
- Phase 3 decomposition mechanics (Artifact Pipeline, Task Structure, Creating Tasks, Dependencies, Anatomy).
- Phase 4 Self-Review checklist.
- The `Living Task Tree` and `User Feedback and Changing the Task Tree` update-task protocol. Where that lifecycle already lives in `references/task-tree-design.md`, point rather than duplicate.

Success: `SKILL.md` is materially shorter and reads as a spine; every `[BLOCKING]` gate, stop point, and status-transition rule survives verbatim in its new home and remains loadable via a stated `SKILL.md` load condition; ownership boundaries per `CLAUDE.md` intact.

## Planner Guidance

Pure structural refactor with real correctness risk: a moved gate must not be silently softened. The reviewer verifies every gate/stop-point/transition present before the move is present after, in a reference with a clear load condition. Keep references one level deep. This task lands before `interactive-reference`, which plugs the new interactive loop into the de-crowded routing.

## Results

`skills/superplan/SKILL.md` is now a **routing spine of 109 lines, down from 196** ([SKILL.md](../../../skills/superplan/SKILL.md)). It keeps Overview, Entry Assessment, Depth Tiers, the Phase 1–4 sequence, Substantive Questions, and slim Living-Task-Tree / User-Feedback pointer sections; all mechanical detail moved to two new one-level-deep references, each with a stated load condition from `SKILL.md`.

**Relocations (all gate/stop/transition text moved verbatim):**

- **Phase 3 decomposition mechanics** → [references/decomposition.md](../../../skills/superplan/references/decomposition.md) — Artifact Pipeline (+ required pipeline file), Task Structure, Creating Tasks (wrapper-first "must exist before any subagent is dispatched" + No-checkboxes rule), Task Dependencies (edge-trace "no cycles, no references to nonexistent siblings"), Task Anatomy, Create the `superRA/` Directory. Loaded from [SKILL.md Phase 3](../../../skills/superplan/SKILL.md#L60-L62).
- **Phase 4 Self-Review checklist** (9 items verbatim) → [references/decomposition.md §Self-Review](../../../skills/superplan/references/decomposition.md). Loaded from [SKILL.md Phase 4 §Self-Review](../../../skills/superplan/SKILL.md#L66-L68).
- **Living Task Tree + `superRA/` Is the Task Tracker + User Feedback and Changing the Task Tree** (full material/not-material lists and 6-step protocol verbatim) → [references/changing-the-tree.md](../../../skills/superplan/references/changing-the-tree.md). Loaded from the [SKILL.md Living Task Tree](../../../skills/superplan/SKILL.md#L103-L109) pointer sections.

**Gates/stop-points kept in the spine** (safety choreography, not mechanical detail): Phase 2 domain-gate STOP + inventory-approval, Phase 4 Agent-Review REVISE-before-User-Review gate + dispatch template, User Review, Execution Handoff, and the "do not resume before the change is committed" invariant.

**Anchor-stability decision.** `superplan §User Feedback and Changing the Task Tree` is cited 15× across 8 files (superimplement, superintegrate, semantic-merge, refactor-and-integrate, main-agent, thorough-planning, consolidation), plus `§Substantive Questions` and `§Agent Review` once each. To avoid 17 dangling cross-skill anchors, all three headings are **retained in `SKILL.md`** — the two moved ones as slim pointer sections that route to the reference for the full protocol. This relocates the mechanical detail (the task's intent) while every external citation still resolves to a live `superplan §<section>`. No external files were edited.

**Point-not-duplicate.** `changing-the-tree.md` points to `task-tree-design.md` §Placing Work / §Objective rewrites for the update-task lifecycle rather than duplicating it; intra-skill paths were rewritten from `references/X` to `X` for the new file location, cross-skill paths (`task-tree/…`, `agent-orchestration`, `using-superra/…`, `agents/…`) left unchanged.

**Verification:** every moved `[BLOCKING]`/stop phrase confirmed present in its new home via `grep` (wrapper-first, no-checkboxes, dependency-trace, all 9 self-review items, confirm-intent, do-not-resume-before-commit); all internal `§` anchors in the slimmed `SKILL.md` resolve (Depth Tiers, Agent Review, Substantive Questions, User Feedback); `grep "superplan §"` across `skills/`+`agents/` shows all externally-cited anchors still present in `SKILL.md`.
