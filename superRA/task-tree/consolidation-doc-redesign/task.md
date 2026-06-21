---
title: "Consolidation + Documentation Stage Redesign"
status: approved
depends_on: []
tags: []
created: 2026-06-18
---

## Objective

Redesign the INTEGRATE phase's task-tree consolidation and documentation maturation so consolidation can no longer be silently skipped, and so "approved" is consistently treated as *review-passed / ready-for-integration* (reversible) rather than *final*.

**Problem being fixed.** Today the Consolidation Gate is orchestrator-inline judgment with a "clean-enough" escape hatch (`skills/superintegrate/SKILL.md` §Consolidation Gate). Agents skip it or rationalize it away — most often by reading `superintegrate/SKILL.md:242` ("does not grant authority to restructure approved work unilaterally") as "approved tasks must not be touched," which collides with the create-then-merge update-task lifecycle that *expects* an approved update task to be folded at integration.

**Design decided with the researcher (this is the binding contract for the children):**

1. **Ordering is unchanged: code-integration first → consolidation → documentation.** This was evaluated and is effectively forced — the results-bearing fold actions (Merge, Mature/Rename) are atomic over objective + results + directory and must run on *final* results. Do not reorder.

2. **Merge the Consolidation Gate and Document into one post-Integrate stage** ("task-artifact maturation"). Both manage the same artifact surface (task structure + `## Results`), and the maturation home *is* a function of the consolidated structure, so the two decisions are one decision. The merged stage runs once, after Integrate closes.

3. **The orchestrator owns the proposal; the user decides.** Consolidation is user-involving, so screening and the user-facing proposal are orchestrator work (not a dispatched implementer). Flow: orchestrator screens the whole tree (mandatory) → presents ONE combined proposal — per touched subtree: the durable home, the structure change needed to realize it, and the results disposition — at the maturation-home stop point that Document already requires → user decides → orchestrator records decisions as `## Revision Notes` on affected tasks → dispatches implementer(s) to execute → one whole-tree reviewer verifies structure + matured results.

4. **Anti-skip is structural, not exhortative.** The distillation decision is surfaced as a **mandatory blocking question** (`AskUserQuestion`, or plain text if unavailable) that **always fires** — even a clean tree gets an explicit confirm ("nothing to fold; narrative matures here — confirm?"), with the content scaling to zero rather than the question disappearing. The orchestrator cannot reach execution without the user's answer, and the whole-tree reviewer independently verifies no update-task or action-verb scaffolding was left stranded. Two-sided enforcement (forced question + independent verification) replaces the skippable inline gate. This is a deliberate strengthening of current Document behavior (`superintegrate/SKILL.md:250` lets the home default without always asking); the merged stage makes the ask unconditional. To avoid flooding the user, the question is **batched per touched subtree** — one question per subtree, not one prompt per task. Each question is a real options-with-recommendation `AskUserQuestion`: the **options are that subtree's candidate consolidation actions plus an explicit keep-as-is (inaction) option**, with the orchestrator's screened recommendation marked first (the recommended option states the structural action(s) + the resulting `## Results` altitude; the inaction option is how the user vetoes). For a subtree screened clean, the recommended option is simply "keep as-is, mature at <home>" — the question still fires (anti-skip), but the recommendation carries no fold.

5. **Consolidation and maturation are one act: per-task distillation.** For each task the integration touched, decide *what survives and where it lands*, along a spectrum — drop entirely / a one-line note or pointer folded into the parent / a short retained subsection / a matured reader-facing narrative at the durable home. Folding is **inherently lossy by design**: most intermediate outputs and dev-log detail are noise once the work is integrated, and how much survives depends on the task (a simple update task may collapse to a single inline change in its parent). The structural fold (where a task's content lands — merged into the parent, kept as a task, directory removed) and the results altitude (how much detail survives) are the **same decision** viewed from two sides; do not model them as separate steps and do not introduce a "lossless vs lossy" classification. Guardrails: key results selected at Protect are never dropped; when a task's own output *is* a document, distil its `## Results` to a pointer to that document so there is a single source of truth.

6. **The distillation plan is proposed and reviewed, not auto-classified.** The orchestrator proposes a distillation per touched subtree; the user reviews the whole plan at the maturation stop; the implementer executes. The gate for *explicit* user sign-off is the **existing** `superplan §User Feedback` material-change boundary — pruning a task whose result a reader would expect, merging two substantive concerns, or a scope-expansion that invalidates downstream are material and need approval; routine distillation is presented as what-will-happen and the user can veto. No new authorization concept is needed beyond that boundary.

7. **"Approved" is fixed positively, with NO negative instructions.** At this stage every touched task is a distillation candidate, and `approved` means its work is settled and verified — i.e. the precondition for distilling it, not a shield against it. Do not add "approval does not mean X" lines anywhere. Rewrite the one escape-hatch line (`superintegrate/SKILL.md:242`) and align the scoping framing (`refactor-and-integrate/SKILL.md:56`, `superintegrate/SKILL.md:46`) by stating what IS in scope (reopened/changed tasks; the surviving-diff sweep that can reopen an approved task), so the reversible `approved → revise` transition the contract already grants is the operative model. The canonical definition (`task-file-contract.md:22`, validity marker; `agent-orchestration` status table, "review passed") is already correct and needs no change.

### Constraints

- This is superRA-internal skill work: load `skill-creator` before editing any `skills/*/SKILL.md`; load the owning workflow skills before changing workflow behavior (per repo `CLAUDE.md`).
- Every instruction line added/changed passes the repo's **Teach the Protocol** DRY + Necessity gate. Add no negative instructions to fix "approved."
- The one-act / lossy distillation **rationale** (decision 5) lives in this objective and contributor docs only. Agent-facing skill bodies (`task-file-contract.md` §Results Shape, `consolidation.md`, `superintegrate` §Mature & Consolidate) state what the agent does at the stage, not why the decision is "one decision viewed from two sides" — no design essay in skill prose.
- No per-stage `Stage: maturation` clause in the generic role bodies (`agents/implementer.md`, `agents/reviewer.md`). The orchestrator's dispatch `Additionally:` tails prompt the roles at that stage; the role specs stay lean and stage-generic.
- Respect ownership boundaries (repo `CLAUDE.md` table): choreography in `superintegrate`; consolidation mechanics in `superplan/references/consolidation.md`; results shape in `task-tree/references/task-file-contract.md`; manifest in `using-superra`; canonical role behavior in `agents/`.
- Generated artifacts (`direct-mode-implementer.md`, `direct-mode-reviewer.md`, `.codex/agents/superra_*.toml`) are regenerated via `skills/codex-superra-setup/scripts/sync_codex_agents.py`, never hand-edited.
- Preserve standalone usability of `consolidation.md` (loadable when a researcher asks to clean up a tree, not only via integration routing).
- Verify behavior, not just prose: exercise at least one realistic integration walkthrough of the merged stage before the workstream is approved.

### Manifest / harness note

Harness skill-loading is skill-granular: an agent loads a *skill* and then reads its references. So the Skill-Load Manifest entry for the merged stage lists **skills** (`task-tree`, `superplan`, `report-in-markdown`, and `writing` conditionally), and the stage reference inside `superintegrate` names which references within them the implementer reads.

## Results

Redesigned the INTEGRATE phase's task-tree consolidation and documentation maturation so consolidation can no longer be silently skipped and `approved` is treated as *review-passed / ready-for-integration* (reversible), not *final*. All seven binding decisions in the objective shipped, landing across the `superintegrate` choreography, its owning references, the role specs, the manifest, and the user docs.

**One merged stage.** The former §Consolidation Gate (orchestrator-inline, skippable) and §Document are now a single post-Integrate **Mature & Consolidate** stage (`Stage: maturation`) in [superintegrate/SKILL.md](../../../skills/superintegrate/SKILL.md). The five-step spine and code-first ordering are preserved (Protect → Sync → Integrate → Mature & Consolidate → Finish). Per touched task, the structural fold (where content lands) and the results altitude (how much survives) are one decision. ([01-core-stage-redesign](01-core-stage-redesign/task.md))

**Structural anti-skip.** The distillation decision is a mandatory `AskUserQuestion` that always fires — even a clean subtree gets an explicit confirm — batched one question per touched subtree, and a whole-tree reviewer independently verifies no update-task or action-verb scaffolding was left stranded. The forced question plus the independent verification replace the skippable inline gate. ([01-core-stage-redesign](01-core-stage-redesign/task.md), [06-docs-and-verification](06-docs-and-verification/task.md))

**Positive `approved` semantics.** The escape-hatch line and the exclusionary scoping phrase are gone; in-scope work is named positively (reopened or changed tasks, plus any `approved` task the surviving-diff sweep reopens), with no "approval does not mean X" line anywhere. A 99-occurrence audit confirmed the rest of the codebase already treats `approved` as a reversible validity marker. ([02-consolidation-mechanics](02-consolidation-mechanics/task.md), [04-approved-semantics](04-approved-semantics/task.md))

**Distillation mechanics and menu.** [consolidation.md](../../../skills/superplan/references/consolidation.md) reads as positive distillation lifecycle (an approved update task is in the expected state to fold), and [task-file-contract.md §Results Shape](../../../skills/task-tree/references/task-file-contract.md) gained a §Maturation Disposition Menu (Mature / Trim-to-pointer / Drop) with the guardrail that key results selected at Protect are never dropped. ([02-consolidation-mechanics](02-consolidation-mechanics/task.md), [03-results-disposition](03-results-disposition/task.md))

**Wiring and docs.** `Stage: maturation` is in the [Skill-Load Manifest](../../../skills/using-superra/SKILL.md) and both role specs; the four Codex / direct-mode artifacts were regenerated, not hand-edited; user docs (README, docs/site, CATEGORIES) and the workflow-layer references were repointed from "Document" to "Mature & Consolidate". A four-scenario behavior walkthrough exercised all four dispositions and confirmed a stranded update-task is caught by the whole-tree reviewer. ([05-manifest-and-roles](05-manifest-and-roles/task.md), [06-docs-and-verification](06-docs-and-verification/task.md))

**Integration note.** At integration the branch was synced onto `better-handoff`, whose concurrent integration-thoroughness work had restructured Integrate into a do-then-verify pass and generalized the role-spec gates. The two redesigns were orthogonal and synthesized cleanly: the merged Mature & Consolidate stage now sits after better-handoff's do-then-verify Integrate (Steps 1–6). See the sync commit `362bdab9`.

Per-task implementation detail is distilled to one-line pointers on the child tasks; the shipped skill files are the source of truth.
