---
title: "Consolidation + Documentation Stage Redesign"
status: approved
depends_on: []
---

## Objective

Redesign the INTEGRATE phase's task-tree consolidation and documentation maturation so consolidation can no longer be silently skipped, and so `approved` is consistently treated as *review-passed / ready-for-integration* (reversible) rather than *final*.

**Problem.** The former Consolidation Gate was orchestrator-inline judgment with a "clean-enough" escape hatch that agents skipped or rationalized away — most often by reading the "does not grant authority to restructure approved work unilaterally" line as "approved tasks must not be touched," which collides with the create-then-merge update-task lifecycle that *expects* an approved update task to be folded at integration.

**Design (the binding contract):**

1. **Ordering is code-integration first → consolidation → documentation.** The results-bearing fold actions (Merge, Mature/Rename) are atomic over objective + results + directory and must run on *final* results, so the order is forced.
2. **Merge the Consolidation Gate and Document into one post-Integrate stage** ("task-artifact maturation"). Both manage the same surface (task structure + `## Results`), and the maturation home *is* a function of the consolidated structure, so the two are one decision, made once after Integrate closes.
3. **The orchestrator owns the proposal; the user decides.** The orchestrator screens the whole tree, presents one combined proposal per touched subtree (durable home + structure change + results disposition), records decisions as `## Revision Notes` on affected tasks, and dispatches implementer(s); one whole-tree reviewer verifies structure + matured results.
4. **Anti-skip is structural.** The distillation decision is a mandatory blocking question (`AskUserQuestion`, or plain text) that always fires — even a clean subtree gets an explicit confirm — batched one question per touched subtree, each with that subtree's candidate actions plus an explicit keep-as-is option and the screened recommendation first. The whole-tree reviewer independently verifies no update-task or action-verb scaffolding was left stranded. The forced question plus the independent verification replace the skippable inline gate.
5. **Consolidation and maturation are one act: per-task distillation.** For each touched task, decide what survives and where it lands, along a spectrum (drop / one-line note or pointer folded into the parent / short retained subsection / matured narrative at the durable home). The structural fold and the results altitude are the same decision viewed from two sides. Guardrails: key results selected at Protect are never dropped; when a task's own output *is* a document, distil its `## Results` to a pointer to that document.
6. **The distillation plan is proposed and reviewed, not auto-classified.** The user-sign-off gate is the existing `superplan §User Feedback` material-change boundary; routine distillation is presented as what-will-happen and the user can veto.
7. **"Approved" is fixed positively, with no negative instructions.** At this stage `approved` means the work is settled and verified — the precondition for distilling it, not a shield against it. In-scope work is named positively (reopened or changed tasks, plus any approved task the surviving-diff sweep reopens); no "approval does not mean X" line anywhere.

### Constraints

- superRA-internal skill work: load `skill-creator` before editing any `skills/*/SKILL.md`; every instruction line passes the DRY + Necessity gate.
- Ownership boundaries: choreography in `superintegrate`; consolidation mechanics in `superplan/references/consolidation.md`; results shape in `task-tree/references/task-file-contract.md`; manifest in `using-superra`; canonical role behavior in `agents/`. Generated Codex / direct-mode artifacts are regenerated via `skills/codex-superra-setup/scripts/sync_codex_agents.py`, never hand-edited.
- `consolidation.md` stays standalone-usable (loadable when a researcher asks to clean up a tree, not only via integration routing).
- The Skill-Load Manifest entry for the merged stage lists skills (`task-tree`, `superplan`, `report-in-markdown`, and `writing` conditionally); the stage reference inside `superintegrate` names which references the implementer reads.

## Results

All seven decisions shipped, landing across the `superintegrate` choreography, its owning references, the role specs, the manifest, and the user docs.

- **One merged stage.** The former §Consolidation Gate and §Document are a single post-Integrate **Mature & Consolidate** stage (`Stage: maturation`) in `skills/superintegrate/SKILL.md`. The code-first spine is preserved (Protect → Sync → Integrate → Mature & Consolidate → Finish); per touched task the structural fold and the results altitude are one decision.
- **Structural anti-skip.** The distillation decision is a mandatory `AskUserQuestion` that always fires, batched one question per touched subtree, and a whole-tree reviewer independently verifies no scaffolding was left stranded.
- **Positive `approved` semantics.** The escape-hatch line and the exclusionary scoping phrase are gone; in-scope work is named positively, with no "approval does not mean X" line. An audit confirmed the rest of the codebase already treats `approved` as a reversible validity marker.
- **Distillation mechanics and menu.** `skills/superplan/references/consolidation.md` reads as positive distillation lifecycle (an approved update task is in the expected state to fold), and `skills/task-tree/references/task-file-contract.md §Results Shape` gained a §Maturation Disposition Menu (Mature / Trim-to-pointer / Drop) with the key-results-never-dropped guardrail.
- **Wiring and docs.** `Stage: maturation` is in the Skill-Load Manifest (`skills/using-superra/SKILL.md`) and both role specs; the four Codex / direct-mode artifacts were regenerated; user docs (README, docs/site, CATEGORIES) and workflow-layer references were repointed from "Document" to "Mature & Consolidate". A four-scenario walkthrough exercised all dispositions and confirmed a stranded update-task is caught by the whole-tree reviewer.

At integration the branch synced onto `better-handoff`, whose concurrent integration-thoroughness work had restructured Integrate into a do-then-verify pass. The two redesigns were orthogonal: the merged Mature & Consolidate stage now sits after the do-then-verify Integrate. The shipped skill files are the source of truth.
