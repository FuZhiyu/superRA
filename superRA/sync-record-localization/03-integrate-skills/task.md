---
title: "Align the INTEGRATE Skills (superintegrate, refactor-and-integrate)"
status: approved
depends_on:
  - 01-canonical-model
tags: []
created: 2026-06-17
---

## Objective

Bring the INTEGRATE-phase workflow and utility skills into line with the canonical model from `01-canonical-model`. Edit two files:

**1. `skills/superintegrate/SKILL.md`:**
- Remove every `## Sync Map` reference: the Sync Step 3 dispatch prose ("Write `## Sync Map` section in root task.md …"), the Sync Step 4 reviewer dispatch ("Sync Map completeness (root task.md `## Sync Map`)" and "record … in root task.md `## Sync Map`"), the Integrate Step 2 dispatch's "root task.md `## Sync Map`" context, and the Step 5 closeout "remove temporary `## Sync Map` from root task.md". The branch-level sync narrative is the git log; the only task-tree sync record is task-local `## Sync Impact`.
- Align the sync author / sync reviewer dispatch-and-return to the lean reporting model: drop the verbose "Return the full sync commit chain, Sync Map status, task-local Sync Impact annotations, checks run, and codebase-review context recorded" tail — the return is status + sync commit SHA(s); the narrative is the commit messages. The dispatch still names the inputs (BASE refs, incoming range) and the `semantic-merge` mode reference.
- **Strengthen the `## Sync Impact` cleanup into a guaranteed gate.** The Integrate Step 5 closeout already removes temporary task-local sync context; make removal of all `## Sync Impact` sections an explicit closeout requirement, and have it run / cite `superra task check` (the warn-only `sync-impact` category built in `04-cleanup-check`) so a survivor is caught. Keep "unless a lasting task assumption still belongs in the task.md" as the one carve-out.
- `## Sync Impact` is already the term superintegrate uses — keep it, just ensure it matches the canonical section form and drop any Sync-Map coupling.

**2. `skills/refactor-and-integrate/SKILL.md`:**
- Replace the dead `**Integration status: APPROVED**` / `**Integration status**` / `REVISE` inline-field references (the task-selection wording, ~lines 54–56) with the single `status:` frontmatter field (`approved`, `revise`, lowercase) — integration review never used a separate integration-status field in the current design.
- Fix the Sync Impact Context section (~line 45): task-local context is the `## Sync Impact` section; remove the "Sync Map cluster" pointer (no Sync Map exists). The section is self-contained justification evidence for why a hunk already exists in the governing diff.

## Planner Guidance

The canonical `## Sync Impact` format, the "branch narrative → git log" rule, and the lean reporting model are owned by `01-canonical-model` and `using-superRA`; reference them, do not restate.

The cleanup gate has two halves: the workflow closeout (this task, prose) guarantees removal, and the `superra task check` rule (`04-cleanup-check`, code) is the safety net that surfaces a leak. Make the closeout prose cite the check so the two stay coupled.

## Results

### Key Findings
Both INTEGRATE skills aligned to the canonical model; targeted-token grep over the two files is clean (`Sync Map`, `SEMANTIC_MERGE`, `Integration status`, `**Sync impact:**` inline field, `task block` all gone). Remaining "Sync impact" mentions are the generic concept ("supplied Sync impact context", "Sync impact as evidence") that now refers to the `## Sync Impact` section — kept intentionally.

- **`skills/superintegrate/SKILL.md`** — removed all five `## Sync Map` couplings:
  - Sync Step 3 dispatch: dropped the "Write `## Sync Map` section in root task.md …" instruction (branch narrative is the commit messages; sync author adds a task-local `## Sync Impact` to each affected task needing context) and dropped the verbose return tail ("Return the full sync commit chain, Sync Map status, …") — the lean return (status + sync SHA) is owned by the mode reference and `using-superRA`, so restating it in the dispatch would violate DRY.
  - Sync Step 4 reviewer dispatch: replaced "Sync Map completeness / Record … in root task.md `## Sync Map`" with the standard review mechanism (affected task's `## Review Notes`, or the REVISE return for a branch-level finding).
  - Integrate intro + Step 2/Step 4 dispatch "Sync context": "root task.md `## Sync Map`" → "the sync commit messages (git log)".
  - Step 5 closeout: dropped the "remove temporary `## Sync Map`" line and **strengthened the `## Sync Impact` cleanup into a guaranteed gate** — every section removed (lasting assumptions folded into `## Objective`), then run `superra task check` (warn-only `sync-impact` category) and confirm it flags no survivor. The check is a forward reference to the rule `04-cleanup-check` builds, per Planner Guidance's two-halves coupling.
  - §When to Lighten: "keep `## Sync Map` absent" → "add no `## Sync Impact` sections" when there is no material sync context.
- **`skills/refactor-and-integrate/SKILL.md`** —
  - §Sync Impact Context (line 45): rewrote to "When a task file carries a `## Sync Impact` section, use it as self-contained evidence …" and dropped the "Follow the referenced Sync Map cluster" pointer (no Sync Map exists; the section is self-contained).
  - Final Diff Self-Check step 4: dead inline field `Integration status: APPROVED` → `status: approved`.
  - Final Diff Self-Check step 6: "tasks whose `Integration status` is unset or `REVISE`" → "tasks whose `status` is not `approved`".

### Notes
- DRY + Necessity self-applied: the dispatch prompts now name only inputs + the mode reference and trust the mode reference / `using-superRA` for the return shape and the `## Sync Impact` format, rather than restating them.
- The `sync-impact` task-check category does not exist yet (verified: only an unrelated `Sync Impact` string in `plan_migrate.py`). Citing it in the closeout is the intended forward reference; `04-cleanup-check` builds the rule. Not a blocker for this task.
