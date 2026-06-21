---
title: "Merge Consolidation Gate + Document into one post-Integrate stage"
status: approved
depends_on: []
tags: []
created: 2026-06-18
---

## Objective

Rewrite `skills/superintegrate/SKILL.md` so the §Consolidation Gate and §Document sections become a single post-Integrate stage (working name: **Mature & Consolidate**), keeping the five-step INTEGRATE spine otherwise intact and the code-first ordering unchanged (Protect → Sync → Integrate → **Mature & Consolidate** → Finish).

The merged stage must encode the choreography from the parent objective points 2–7:

- **Orchestrator screening (mandatory):** survey the whole affected tree (`superra task tree` / `dag` / `task check --category placement`), identify every update-task, action-verb parent, and misplacement, AND, per touched subtree, the distillation — what of each task survives and where (durable home + altitude). Orchestrator inline work; cannot be skipped.
- **One combined, unskippable question per subtree:** the current Document maturation-home confirmation (today at `superintegrate/SKILL.md:252-258`) becomes a mandatory blocking `AskUserQuestion` that always fires (a clean subtree still gets a confirm), batched **one question per touched subtree** so the user is not flooded with a prompt per task. Each option line carries a task's proposed handling: durable home, the structure change that realizes it, and the altitude its `## Results` is distilled to (drop / pointer / short subsection / matured narrative). Material tree changes (per `superplan §User Feedback`) require explicit approval; routine distillation is presented as the proposed default the user can veto. Execution cannot begin before the answer.
- **Record → dispatch → verify:** orchestrator folds decisions into `## Revision Notes` on affected tasks, dispatches implementer(s) to execute the distillation (structural folds + results altitude together), then one whole-tree reviewer verifies structure (nothing stranded, placement clean, Protect key results retained) AND distilled results. Structural review is whole-tree and not parallelized; results distillation may fan out per subtree when large.
- **Positive rewrite of the escape-hatch line (`:242`)** while rewriting this section: tie the user-sign-off gate to the existing `superplan §User Feedback` material-change boundary (material merges/prunes/restructures route there; routine distillation executes as lifecycle) instead of "does not grant authority to restructure approved work." Align the Protect-section scoping phrase at `:46` to name the in-scope set positively. No negative "approved means…" lines and no lossless/lossy framing.

Reference mechanics rather than restating them: consolidation execution → `superplan/references/consolidation.md` (task 02); results disposition → `task-tree/references/task-file-contract.md` §Results Shape (task 03). Keep choreography here; keep mechanics in their owners (repo `CLAUDE.md` ownership table).

Use **`Stage: maturation`** as the merged stage's value (decided with the researcher) — introduce it as a new stage value, replacing the old `documentation` stage; task 05 wires it into the manifest. Update the step diagram at the top of the file, and the §When to Lighten and §Red Flags sections, to match the merged stage.

**Success:** `superintegrate/SKILL.md` describes one merged stage with the orchestrator-screening → combined-proposal → execute → whole-tree-review flow; the `:242` and `:46` lines read positively; code-first ordering and the other four steps are unchanged; every new line passes the Teach-the-Protocol gate.

## Planner Guidance

Load `skill-creator` and re-read the current `superintegrate/SKILL.md` end to end before editing — the Consolidation Gate, Document, and Finish sections are cross-referenced (freshness check, base-advance re-entry) and must stay coherent.

## Results

Merged the former §Consolidation Gate + §Document into a single post-Integrate **Mature & Consolidate** stage (`Stage: maturation`) in [superintegrate/SKILL.md](../../../../skills/superintegrate/SKILL.md), preserving the five-step spine and code-first ordering, and rewrote the two `approved`-scope lines positively. Matured narrative at the [subtree root](../task.md).

Revise round (coordinated essay cleanup): dropped the "same decision seen from two sides" essay tail from the [§Mature & Consolidate lead-in](../../../../skills/superintegrate/SKILL.md), keeping the behavioral instruction that the structural fold and results altitude are decided and executed together as one act. Rewrote Step 2's distillation question from a flat per-task "confirm, or adjust" list into a real options-with-recommendation `AskUserQuestion` per touched subtree: options are the subtree's candidate actions plus an explicit keep-as-is option (the veto path), with the screened recommendation marked first; batch count is not hardcoded — one question per subtree across as many calls as the harness per-call limit takes. Verified the Step 3 (execute distillation per `consolidation.md` + `task-file-contract.md` §Results Shape) and Step 4 (reviewer verifies structure + distilled results) dispatch `Additionally:` tails are self-sufficient, since task 05 removes the maturation clauses from the role bodies and leaves these tails as the sole prompt.
