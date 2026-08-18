---
title: "De-crowd superplan SKILL.md into a routing spine"
status: approved
depends_on: []
---

## Objective

Slim `skills/superplan/SKILL.md` (currently ~196 lines) to a **routing spine** and move phase detail into references, without dropping or weakening any gate. Progressive disclosure: `SKILL.md` keeps Overview, Entry Assessment, Depth Tiers, the Phase 1–4 sequence as pointers, and Substantive Questions; the mechanical detail moves out.

Content to relocate into new or existing references (one level deep, each with a clear load condition from `SKILL.md`):
- Phase 3 decomposition mechanics (Artifact Pipeline, Task Structure, Creating Tasks, Dependencies, Anatomy).
- Phase 4 Self-Review checklist.
- The `Living Task Tree` and `User Feedback and Changing the Task Tree` update-task protocol. Where that lifecycle already lives in `references/task-tree-design.md`, point rather than duplicate.

Success: `SKILL.md` is materially shorter and reads as a spine; every `[BLOCKING]` gate, stop point, and status-transition rule survives verbatim in its new home and remains loadable via a stated `SKILL.md` load condition; ownership boundaries per `CLAUDE.md` intact.

## Details

Pure structural refactor with real correctness risk: a moved gate must not be silently softened. The reviewer verifies every gate/stop-point/transition present before the move is present after, in a reference with a clear load condition. Keep references one level deep. This task lands before `interactive-reference`, which plugs the new interactive loop into the de-crowded routing.

## Results

[superplan/SKILL.md](../../../skills/superplan/SKILL.md) became a routing spine — 111 lines, down from 196 — keeping Overview, Entry Assessment, Depth Tiers, the Phase 1–4 sequence, the researcher-question section, and slim pointer sections for the living tree and user feedback. Mechanical detail moved to two one-level-deep references, each with a stated load condition.

**Every gate, stop point, and transition moved verbatim.**

- Phase 3 decomposition mechanics — artifact pipeline and its required pipeline file, task structure, wrapper-first task creation, the no-checkboxes rule, the dependency edge trace, task anatomy — and the nine-item Phase 4 self-review checklist went to [build-and-review.md](../../../skills/superplan/references/build-and-review.md) (then named `decomposition.md`).
- The living-tree sections and the six-step change protocol went to [changing-the-tree.md](../../../skills/superplan/references/changing-the-tree.md).
- The spine kept what superplan owns: the Phase 4 REVISE-before-User-Review gate and its dispatch template, User Review, Execution Handoff, and the do-not-resume-before-commit invariant. Phase 2's domain approval stop was still in the spine at this point; [grilling](../../task-tree/planning-redesign/task.md) retired it later.

**Externally cited headings stayed in `SKILL.md` as pointer sections.** `§User Feedback and Changing the Task Tree` alone had 15 citations across 8 files, so moving the prose out while leaving the heading in kept every cross-skill anchor live and edited no external file. (`§Substantive Questions`, one of the three, was itself replaced by `§Grilling` later, with its citations repointed then.)

**Verification.** Every moved `[BLOCKING]` and stop phrase was confirmed present in its new home by grep — wrapper-first, no-checkboxes, dependency trace, all nine self-review items, confirm-intent, do-not-resume-before-commit — and every internal and externally cited `§` anchor resolved.

A follow-up pass on researcher feedback compressed Depth Tiers into a table and cut a justification clause. Further externalization would have moved ownership rather than prose, so the phase choreography stayed.
