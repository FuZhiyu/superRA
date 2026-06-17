---
title: "Align the INTEGRATE Skills (superintegrate, refactor-and-integrate)"
status: not-started
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
