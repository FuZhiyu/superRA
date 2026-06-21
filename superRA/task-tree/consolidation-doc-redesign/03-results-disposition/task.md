---
title: "Results maturation disposition menu: mature / trim-to-pointer / drop"
status: approved
depends_on:
  - 01-core-stage-redesign
tags: []
created: 2026-06-18
---

## Objective

Extend `skills/task-tree/references/task-file-contract.md` §Results Shape (the Stage-2 maturation owner) so maturation is a disposition *menu*, not an implicit "always write a narrative."

Keep the vocabulary aligned with `consolidation.md` (task 02), which owns the structural-fold side. Do **not** explain the design (that this is "one decision viewed from two sides", that "folding is lossy") in the skill body — that rationale lives in this objective and contributor docs; the agent reading the reference needs only what to do at Stage 2.

Add three dispositions a task's `## Results` can take at the merged stage:

- **Mature** — substantive findings synthesized into the reader-facing narrative at the durable home (the current Stage-2 behavior). Default for key/substantive results.
- **Trim-to-pointer** — when the task's own output *is* a document (a report, rendered note, manuscript section), reduce `## Results` to a one-line pointer to that document so there is a single source of truth instead of a duplicated summary that drifts.
- **Drop / trim heavily** — when the task is a minor fix not worth surfacing as a feature, trim or drop the results to reduce maintenance cost (more files = more drift surface).

State the guardrail: key results selected at Protect (`result-protection`) are never dropped; trimming/dropping is for non-key, low-value, or duplicated-into-a-document results. Make clear this disposition is chosen in the merged stage's combined proposal (task 01) and recorded as a `## Revision Notes` instruction to the implementer.

**Success:** §Results Shape documents the three dispositions with the single-source-of-truth rationale for trim-to-pointer and the maintenance-cost rationale for drop, plus the Protect guardrail; the two-stage lifecycle description stays coherent.

## Planner Guidance

This is content-shape guidance owned by the task-file contract; keep the *when/who decides* in the merged-stage choreography (task 01) and only the *what each disposition means* here. Avoid duplicating the disposition list verbatim in `superintegrate` — point to it.

## Results

Added the §Maturation Disposition Menu (Mature / Trim-to-pointer / Drop) with the Protect guardrail to [task-file-contract.md §Results Shape](../../../../skills/task-tree/references/task-file-contract.md), sharing the altitude vocabulary with `consolidation.md`. Matured narrative at the [subtree root](../task.md).

Revise round (substantive — researcher feedback): cut the design essay ("distilled to a disposition along the altitude spectrum", "the results-altitude side of the single distillation decision … viewed from two sides", "folding is lossy by design") from the Stage-2 lead-in and the Drop item, leaving a plain pointer to `consolidation.md` for the structural fold and a behavioral statement of what each disposition does. Added the missing merge-into-another case: when the consolidation fold removes a task's directory (Merge or Flatten), its distilled results move into the **target** task's `## Results` at the chosen level (one-line note / short subsection / folded into the narrative) and nothing is left in the deleted directory — matching `consolidation.md`'s Merge/Flatten action text. Menu (matured narrative / short subsection / pointer / drop) and the Protect guardrail kept.
