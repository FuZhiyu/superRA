---
title: "User docs + cross-reference coherence sweep + verification"
status: approved
depends_on:
  - 01-core-stage-redesign
  - 02-consolidation-mechanics
  - 03-results-disposition
  - 04-approved-semantics
  - 05-manifest-and-roles
tags: []
created: 2026-06-18
---

## Objective

Land the user-facing docs and verify the whole redesign is coherent.

- **User docs.** Update the docs-site INTEGRATE/workflows page(s) that describe the Consolidation Gate and Document steps to the merged stage (search `superRA/docs-site` tasks and the rendered pages for "Consolidation Gate" / "Document"). Update `skills/CATEGORIES.md` and `README.md` only if they name the old separate steps.
- **Cross-reference sweep.** Grep all skills/agents/docs for references to the old "§Consolidation Gate" and separate "§Document" step, the old `:242` phrasing, and any now-stale `Stage:` value. Repoint to the merged stage. Verify ownership-boundary pointers still resolve (choreography ↔ mechanics ↔ results-shape ↔ manifest) with no paraphrase drift.
- **Verification (behavior, not just prose).** Walk one realistic integration scenario through the merged stage: a tree containing (a) an approved update-task that should fold, (b) an action-verb parent that should mature/rename, (c) a task whose output is a document (trim-to-pointer), and (d) a minor-fix task (drop). Confirm the orchestrator screening surfaces all four, the combined proposal presents home + structure + disposition, and the whole-tree reviewer would catch a stranded update-task. Capture the walkthrough in this task's `## Results`.
- **Gate self-application.** Walk every instruction line added across tasks 01–05 against the repo `CLAUDE.md` Teach-the-Protocol DRY + Necessity tests; record any line removed.

**Success:** no dangling references to the old two-step structure; docs-site reflects the merged stage; the scenario walkthrough passes; the DRY/Necessity self-application is recorded.

## Planner Guidance

This is the integration/coherence task for the workstream — run it last. If the walkthrough surfaces a design gap, route it back through `superplan §User Feedback` rather than patching prose locally.

## Results

The user docs and the merged-stage cross-references were verified coherent against the post-revise state (tasks 01/02/03/05 reopened: role specs lost their `Stage: maturation` clauses, and the menu/mechanics prose was rewritten plainer with the merge-into-target results landing added). Both verification passes were re-run and pass with no stale prose to fix; the four-disposition behavior walkthrough still holds. The matured workstream narrative lives at the [subtree root](../task.md).

### Pass 1 — Cross-reference coherence sweep (clean)

- **No dangling pointer to a removed role-spec maturation clause.** The `Stage: maturation` clause was dropped from all four role surfaces — canonical [agents/implementer.md](../../../../agents/implementer.md), [agents/reviewer.md](../../../../agents/reviewer.md), and the generated [direct-mode-implementer.md](../../../../skills/using-superra/references/direct-mode-implementer.md) / [direct-mode-reviewer.md](../../../../skills/using-superra/references/direct-mode-reviewer.md) and `.codex/agents/superra_*.toml`. A grep for `At \`Stage: maturation\`` across every role surface returns nothing. The roles are now prompted solely by the dispatch `Additionally:` tails in [superintegrate/SKILL.md:292-298](../../../../skills/superintegrate/SKILL.md#L292-L298) (Step 3, implementer) and [:312-316](../../../../skills/superintegrate/SKILL.md#L312-L316) (Step 4, reviewer), which name the same two references the dropped clause did, so no information was lost.
- **Ownership-boundary pointers resolve with no paraphrase drift.** The four-way chain holds: choreography in [superintegrate §Mature & Consolidate](../../../../skills/superintegrate/SKILL.md#L258) ("owns when and who decides") → mechanics in [consolidation.md](../../../../skills/superplan/references/consolidation.md) (owns the structural fold) → results-shape in [task-file-contract.md §Results Shape](../../../../skills/task-tree/references/task-file-contract.md#L51) (owns the altitude/disposition) → manifest in [using-superra/SKILL.md:76](../../../../skills/using-superra/SKILL.md#L76) (Stage table). Each home points outward by reference, none paraphrases another's content — e.g. [task-file-contract.md:59](../../../../skills/task-tree/references/task-file-contract.md#L59) says "the structural fold … is `consolidation.md`'s; the disposition here sets how much of the results survive," delegating rather than restating.
- **No residual design-essay phrasing in agent-facing prose.** Greps for "disposition along the altitude spectrum", "viewed/seen from two sides", "lossy by design / lossless", and "same decision" return nothing in `skills/`, `agents/`. The only surviving "one act" usage is the operational instruction at [superintegrate/SKILL.md:260](../../../../skills/superintegrate/SKILL.md#L260) (decide+execute the fold and altitude as one act) — that is what the agent does, not the stripped "why it is one decision" rationale.
- **No stale Consolidation Gate / separate Document step / stale `Stage:` value.** "Consolidation Gate" returns nothing in live skills/agents/docs. The only "Document step" hits are in dated `docs/plans/*` archived plan records (e.g. [2026-05-21-codex-hooks-plan.md](../../../../docs/plans/2026-05-21-codex-hooks-plan.md)) — frozen historical artifacts (the oldest still references the deprecated `handoff-doc` skill), out of scope for repointing. `Stage: maturation` appears only where it should: the manifest row and the Step 3/4 dispatch tails in `superintegrate`. User docs ([docs/site/02-quickstart](../../../../docs/site/02-quickstart/task.md#L129), [05-workflows/03-integrate](../../../../docs/site/05-workflows/03-integrate/task.md#L31)), [README.md](../../../../README.md), and [CATEGORIES.md:15](../../../../skills/CATEGORIES.md#L15) all name "Mature & Consolidate"; no old-term hits.

### Pass 2 — Teach-the-Protocol DRY + Necessity over the revise-round lines

Lines changed this round: role-spec clause removals (×4 surfaces), the [superintegrate:260](../../../../skills/superintegrate/SKILL.md#L260) "one act" rewrite, the [Step 2 question](../../../../skills/superintegrate/SKILL.md#L270) rewrite, the [consolidation.md](../../../../skills/superplan/references/consolidation.md) essay-strips, and the [task-file-contract.md:59,67,69](../../../../skills/task-tree/references/task-file-contract.md#L59) edits.

- **Role-spec clause removal — DRY pass (this is the gate outcome, not a new line).** The dropped clause restated the dispatch-tail content; removing it eliminates the drift surface. The dispatch `Additionally:` tails are the single authoritative prompt.
- **Essay-strips in `consolidation.md` and `task-file-contract.md` — Necessity pass.** "disposition along the altitude spectrum … viewed from two sides … lossy by design" only told the agent *why* the decision is one decision; it shaped understanding, not behavior, so deletion is correct. The retained "The actions below choose the surviving altitude rather than carry a task over wholesale" stays — it is the non-default lossy-by-default behavior the agent would not otherwise assume.
- **One line kept after re-checking necessity — the merge-into-target landing.** [task-file-contract.md:69](../../../../skills/task-tree/references/task-file-contract.md#L69) ("When the consolidation fold removes a task's directory … its distilled results move into the **target** task's `## Results` … Nothing is left behind in the deleted directory.") passes Necessity: the altitude menu alone does not say *where* results land when the directory is deleted, so an implementer executing a Merge could strand or lose them. It passes DRY: results-landing is a results-shape concern owned here, not a structural-fold concern owned by `consolidation.md`. Kept.
- **Lines removed this round:** the four `Stage: maturation` role-spec clauses and the three essay clauses above. No further line failed either test.

### Behavior walkthrough (four dispositions — re-confirmed PASS)

Scenario: an integration touched subtree `feat/` with four children —
(a) `feat/update-config-default` — an **approved update-task** that patched a config default already merged into the parent's diff;
(b) `feat/` itself — an **action-verb parent** ("Add config layer") whose substantive findings should mature/rename to a durable home;
(c) `feat/render-design-note` — a task whose **output is a document** (a rendered note);
(d) `feat/fix-typo` — a **minor-fix task**.

1. **Screening surfaces all four** ([Step 1](../../../../skills/superintegrate/SKILL.md#L264)). The orchestrator loads `task-tree-design.md`, runs `task tree` / `task dag` / `task check --category placement`, and per the step explicitly hunts "every update-task, action-verb parent, and misplacement," drafting each task's home + structure change + altitude. (a) reads as an update-task → fold; (b) as an action-verb parent → mature/rename; (c) matches "when a task's own output *is* a document, distil … to a pointer"; (d) as a minor fix → drop. All four are caught.
2. **The combined proposal presents home + structure + disposition** ([Step 2](../../../../skills/superintegrate/SKILL.md#L268)). One options-with-recommendation `AskUserQuestion` fires for subtree `feat/`, recommendation marked first, each option line carrying the structural action and the resulting `## Results` altitude — e.g. recommended: "Fold `update-config-default` into `feat/` (results → one-line note); drop `fix-typo` (already in diff); `render-design-note` → trim-to-pointer; `feat/` matures at its durable home." The explicit keep-as-is option is the user's veto. The question fires even though the recommendation carries real folds (anti-skip).
3. **The whole-tree reviewer catches a stranded update-task** ([Step 4](../../../../skills/superintegrate/SKILL.md#L301)). If execution left `update-config-default` as a live directory with action-verb scaffolding still in its `## Objective`, the reviewer's tail — "verify the consolidated structure — no update-task or action-verb scaffolding left stranded, placement clean, Protect key results retained" — flags it as a structural finding and returns the tree to REVISE. Two-sided enforcement (forced question + independent verification) holds.

No design gap surfaced; all fixes were stale-prose-or-clean confirmations, so no escalation to `superplan §User Feedback` was warranted.
