---
name: superintegrate
description: "Integrate code-complete superRA work. Requires superRA:using-superra. Use for result protection, base sync, codebase-fit refactors, permanent records, cleanup, or PR preparation."
---

# superintegrate — the INTEGRATE phase

Workflow skill for the **INTEGRATE** phase. It takes a reproducibility-verified branch through five steps:

```
Protect              -> choose results, permanent documentation, and protection
Sync                 -> bring the branch onto the current base via semantic-merge
Mature & Consolidate -> write the permanent record, mature the task tree, and
                        review both into one temporary refactoring task
Integrate            -> approve, execute, and verify that refactoring task
Finish               -> final freshness check, PR or fast-forward, and cleanup

Any step -> superplan §User Feedback and Changing the Task Tree
           when scope, methodology, task structure, or task status changes materially
```

**Announce at start:** "I'm using the superintegrate skill to prepare this work for integration."

## Step References

Load each step's reference on entry; each is self-contained for its step:

| Step | Load |
|---|---|
| Protect | `references/protect.md` |
| Sync | `references/sync.md` |
| Mature & Consolidate | `references/mature-consolidate.md` |
| Integrate | `references/integrate.md` |
| Finish | `references/finish.md` |

## Stop Points

Once entered, run the selected step's local gates; do not redo task-local approvals outside the affected frontier. INTEGRATE keeps no progress checkboxes — progress is recovered from commits and task statuses. The `integrate(protect)` decision commit records the researcher-confirmed permanent-record, consolidation, and protection choices even when Protect changes no files. INTEGRATE is one multi-step phase, so its commit subjects carry the step name in the scope per `using-superra` §Commit Hygiene: `integrate(<step>): <summary>`, where `<step>` is one of `protect | sync | fit | mature | finish`.

Legitimate stop points:

- **Protect:** result, documentation, and protection choices before permanent documentation is written.
- **Sync:** target base confirmation when no prior decision records it; intent-changing conflicts surfaced by `semantic-merge`.
- **Integrate:** the researcher reviews the completed protected record and mechanically derived refactoring task together before execution; return to Mature & Consolidate when a requested or discovered change would alter the protected record.
- **Finish:** hard blockers only, such as target base advancing again after Integrate.

## Dispatch Convention

**Load `superRA:agent-orchestration` before writing any dispatch prompt.** Task-scoped dispatches use the Stage values in `superRA:using-superra` §Skill-Load Manifest; do not restate load lists in prompts.

Any REVISE verdict at any step is adjudicated per `agent-orchestration` §Handling Reviewer Feedback and iterated until APPROVE.

A non-trivial Sync uses `Stage: sync` with generic sync author / sync reviewer agents and the relevant `semantic-merge` mode reference; a trivial Sync lands inline (`references/sync.md` Step 3).

## When to Lighten

- **Standalone analysis:** Protect still runs. Sync may be a no-op. Permanent results documentation may be sufficient protection, and Integrate often collapses to an inline refactoring sweep plus a short reviewer pass.
- **Small changes:** Keep the same five steps, but dispatch fewer agents and add no `## Sync Impact` sections when there is no material sync context.
- **Writing-vertical tasks:** Most writing work runs as standalone Review / Polish / Draft per `skills/writing/SKILL.md` and does not enter this workflow. Only large work (whole-section drafts, whole-paper revisions, R&R passes) reaches Integrate; for those, Protect offers document build and outline stability as protection options, and the Integrate reviewer additionally walks `skills/writing/references/integration.md`.
- **Task tree consolidation:** Standalone consolidation keeps its own proposal and approval gate. During INTEGRATE, the Mature & Consolidate reviewer derives the temporary refactoring task after the structural fold; Integrate owns the researcher gate.
