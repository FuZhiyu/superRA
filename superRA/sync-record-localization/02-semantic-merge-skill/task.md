---
title: "Align the semantic-merge Skill Surface (SKILL.md, sync reviewer, standalone)"
status: not-started
depends_on:
  - 01-canonical-model
tags: []
created: 2026-06-17
---

## Objective

Bring the rest of the `semantic-merge` skill into line with the canonical model from `01-canonical-model`. Edit three files:

**1. `skills/semantic-merge/SKILL.md`:**
- Remove `## Sync Map` from the Semantic Coherence Checklist and anywhere else it appears; replace task-local context references with the canonical `## Sync Impact` section. Update the checklist item currently reading "Affected task blocks have task-local `**Sync impact:**` annotations …" to reference the `## Sync Impact` section, and "Routine task-file conflict resolutions are summarized in the Sync Map" — drop the Sync Map summary (branch narrative is in the git log).
- De-stale terminology: "task block(s)" → task / `task.md`; remove "handoff doc(s)" framing that collides with the deprecated handoff-doc skill (the "Handoff docs and merge records" checklist subsection and Step 5 wording) — the sync record is the git log + task-local `## Sync Impact` (+ commit body for standalone).
- Step 4 / Step 5: when no task tree is present, record decisions in the commit body, not a `SEMANTIC_MERGE.md` record.

**2. `skills/semantic-merge/references/workflow-sync-reviewer.md`:**
- Remove Sync Map verification (Process step 6, the inputs line "Root task.md `## Sync Map`, if present", and the Verdict section's Sync-Map-status / "Sync review notes under the Sync Map" / "create a minimal Sync Map" instructions). The reviewer verifies the sync via the sync commit chain (git log) and the task-local `## Sync Impact` sections.
- Sync-review findings use the standard mechanism: write task-scoped findings into the affected task's `## Review Notes`; a branch-level finding with no task home rides the REVISE return. Update "Commit only root task.md …" accordingly (the reviewer now edits affected task `## Review Notes`, not a root Sync Map).
- De-stale: "handoff artifacts" / "task block"; align the return to status + sync commit SHA(s).

**3. `skills/semantic-merge/references/standalone-merge.md`:**
- Remove `SEMANTIC_MERGE.md` entirely — the whole `## Semantic Merge Record Format` section, the Boundary/Process references to creating/updating it, and the "merge record location" report field. Standalone-merge records its resolution thesis, file/script impact context, and user decisions in the **commit body** (merge commit plus any propagation commits) — that is the durable record by design. Keep the rest of the standalone flow (intent investigation, escalation, checks) intact.

## Planner Guidance

The canonical `## Sync Impact` format and the "branch narrative → git log" rule are owned by `01-canonical-model`; reference them, do not restate the format here.

When removing the SEMANTIC_MERGE.md record format, make sure the standalone mode still tells the agent *what context to capture* (resolution thesis, file/script impact, user decisions, checks) — just relocate the home to the commit body rather than dropping the content requirement.
