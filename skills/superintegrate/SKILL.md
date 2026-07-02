---
name: superintegrate
description: "Integrate code-complete superRA work. Requires superRA:using-superra. Use for result protection, base sync, codebase-fit refactors, permanent records, cleanup, or PR preparation."
---

# superintegrate — the INTEGRATE phase

Workflow skill for the **INTEGRATE** phase. It takes a reproducibility-verified branch through five steps:

```
Protect              -> protect key results (default: drift tests)
Sync                 -> bring the branch onto the current base via semantic-merge
Integrate            -> refactor with Sync context (do-then-verify), then pass integration review
Mature & Consolidate -> distil each touched task: where its content lands + how
                        much of its ## Results survives, decided as one act
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
| Integrate | `references/integrate.md` |
| Mature & Consolidate | `references/mature-consolidate.md` |
| Finish | `references/finish.md` |

## Stop Points

Once entered, run the selected step's local gates; do not redo task-local approvals outside the affected frontier. INTEGRATE keeps no progress checkboxes — each step's completion is recorded by its commit and the per-task `status` it leaves behind, so a resumed session reads progress from git and statuses, not from a tracker section. INTEGRATE is one multi-step phase, so its commit subjects carry the step name in the scope per `using-superra` §Commit Hygiene: `integrate(<step>): <summary>`, where `<step>` is one of `protect | sync | fit | mature | finish`.

Legitimate stop points:

- **Protect:** key-result protection confirmation.
- **Sync:** target base confirmation when no prior decision records it; intent-changing conflicts surfaced by `semantic-merge`.
- **Integrate:** meaningful drift after sync or refactor; user-owned choices surfaced by the first-pass self-review or the integration reviewer.
- **Mature & Consolidate:** the distillation question, one per touched subtree, always fires before any execution — even a clean subtree gets an explicit confirm.
- **Finish:** hard blockers only, such as target base advancing again after Integrate.

## Dispatch Convention

**Load `superRA:agent-orchestration` before writing any dispatch prompt.** Task-scoped dispatches use the Stage values in `superRA:using-superra` §Skill-Load Manifest; do not restate load lists in prompts.

Any REVISE verdict at any step is adjudicated per `agent-orchestration` §Handling Reviewer Feedback and iterated until APPROVE.

A non-trivial Sync uses `Stage: sync` with generic sync author / sync reviewer agents and the relevant `semantic-merge` mode reference; a trivial Sync lands inline in Direct mode (`references/sync.md` Step 3).

## When to Lighten

- **Standalone analysis:** Protect still runs. Sync may be a no-op. Integrate often collapses to an inline pruning sweep plus a short reviewer pass.
- **Small changes:** Keep the same five steps, but dispatch fewer agents and add no `## Sync Impact` sections when there is no material sync context.
- **Writing-vertical tasks:** Most writing work runs as standalone Review / Polish / Draft per `skills/writing/SKILL.md` and does not enter this workflow. Only large work (whole-section drafts, whole-paper revisions, R&R passes) reaches Integrate; for those, Protect substitutes build + outline-stability for drift tests, and the Integrate reviewer additionally walks `skills/writing/references/integration.md`.
- **Task tree consolidation:** The distillation question always fires, but a clean subtree's content scales to zero — an explicit confirm, no structural fold — see `references/mature-consolidate.md`.
