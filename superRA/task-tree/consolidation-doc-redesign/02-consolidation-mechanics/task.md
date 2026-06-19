---
title: "Consolidation mechanics: approved=precondition reframe + distillation actions"
status: approved
depends_on:
  - 01-core-stage-redesign
tags: []
created: 2026-06-18
---

## Objective

Update `skills/superplan/references/consolidation.md` so its mechanics match the merged stage and the create-then-merge lifecycle, while preserving standalone usability (a researcher loading it directly to clean up a tree).

Changes:

- **Reframe approved scaffolding positively.** State that at integration an approved update-task is in the expected state to be folded — approval is the precondition for the fold, and folding into the durable owner is the default. Flip the burden: justify *keeping* a piece of scaffolding, not folding it. Do this with positive instructions only; add no "approved does not mean…" lines.
- **Frame the actions as distillation, not loss-preservation.** Every fold is inherently lossy — the existing Merge / Mature-Rename / Flatten / Prune actions decide *what of a task survives and where*, and most intermediate detail is dropped by design (a simple update-task may collapse to one inline line in its parent). Revise §Issue Classification and §Action Details to drop any "preserve all content" implication and instead describe each action as choosing the surviving altitude into the durable owner. Do **not** introduce a lossless/lossy axis.
- **Re-own the proposal as orchestrator-authored.** The §User Approval Gate proposal (current tree → proposed tree → per-change rationale → approval) is authored by the orchestrator from its screening and is the carrier for the merged stage's combined decision; the implementer executes the approved result. Keep the gate; do not turn it into a dispatched discovery step.
- **State the user-sign-off boundary as the existing one.** Material tree changes (per `superplan §User Feedback` — prune-with-results, merging two substantive concerns, status-invalidating scope-expansion, ambiguous durable home) require explicit approval; routine distillation executes as lifecycle. Decisions arrive to the implementer as `## Revision Notes` on the affected tasks. Do not invent a separate authorization concept.

Keep the §Standalone vs Integration Use section accurate for both entry paths after the merged-stage change.

**Success:** `consolidation.md` reads as positive lifecycle execution (approved = fold-ready by default), frames its actions as distillation into the durable owner (no lossless/lossy axis, no "preserve all content" claims), names the orchestrator as proposal author and the implementer as executor, ties user sign-off to the existing material-change boundary, and still works when loaded standalone.

## Planner Guidance

Coordinate wording with task 01 so choreography (in `superintegrate`) and mechanics (here) point at each other without paraphrase. The update-task lifecycle authority is `superplan/references/task-tree-design.md` §Update-Task Lifecycle — point to it, do not restate it.

## Results

Reframed [consolidation.md](../../../../skills/superplan/references/consolidation.md) as positive distillation lifecycle — an approved update task is the precondition to fold (no negative / "shield" lines), the actions choose the surviving altitude, the proposal is orchestrator-authored, and standalone usability is preserved. Matured narrative at the [subtree root](../task.md).

Revise round (coordinated essay cleanup with 03): trimmed the "fold is inherently lossy by design" / "viewed from two sides" essay framing from the intro, §Issue Classification lead-in, and the §Standalone vs Integration Use closer down to plain behavioral statements (consolidation distils each task — what survives and where it lands; most scaffolding drops; the implementer executes the structural fold and `## Results` altitude together). Kept the Merge and Flatten action text that folds the surviving result into the **target** task's `## Results` and removes the directory — the structural-side answer that stays consistent with 03's menu. Standalone usability preserved.
