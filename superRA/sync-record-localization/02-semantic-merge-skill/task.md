---
title: "Align the semantic-merge Skill Surface (SKILL.md, sync reviewer, standalone)"
status: approved
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

## Results

### Key Findings
All three files aligned to the canonical localized `## Sync Impact` model; the targeted stale-token grep over the three files is clean (`Sync Map`, `SEMANTIC_MERGE`, inline `Sync impact`, `Integration status`, `task block`, `handoff doc/artifact/record` all gone — the one remaining "handoff" is the generic "pre-handoff self-check" in the checklist preamble, kept intentionally).

- **`skills/semantic-merge/SKILL.md`** — checklist subsection "Handoff docs and merge records" renamed to "Sync record"; dropped the `[ADVISORY]` "summarized in the Sync Map" item; rewrote the task-local item to "Affected tasks carry a `## Sync Impact` section (per `references/workflow-sync-author.md`)" — a pointer to the canonical owner, not a restatement. Step 5 prose and two §Scope-boundary `[BLOCKING]` items: "handoff artifact" → "sync record" (git log + task-local `## Sync Impact` in workflow mode, commit body in standalone). Step 2 intent sources: dropped "handoff docs". Step 4: "record the decision in the standalone merge record and the sync commit body" → "in the sync commit body".
- **`skills/semantic-merge/references/workflow-sync-reviewer.md`** — removed the `## Sync Map` input line; rewrote Process step 6 (branch thesis is the git log) and step 7 (`## Sync Impact` section); replaced the whole Sync-Map-status Verdict block with the standard review mechanism (task-scoped findings → affected task's `## Review Notes`; branch-level finding rides the REVISE return; commit only edited task files; return verdict + reviewed sync commit SHA(s)). Header use-line trimmed to "the `## Sync Impact` format". Removed "handoff artifacts" from Review Scope.
- **`skills/semantic-merge/references/standalone-merge.md`** — deleted the entire `## Semantic Merge Record Format` block and collapsed the 4-step process to 2; the resolution thesis, file/script impact + codebase context, user decisions, and checks are now captured in the **commit body** (content requirement preserved per Planner Guidance, only the home relocated). Boundary rewritten to cite the "git for change" principle; removed the "merge record location" report field and the "merge record format" mention in the intro line.

### Notes
- Self-applied the DRY + Necessity gate: the task-local-context checklist item and the reviewer header now *point* to `workflow-sync-author.md` for the `## Sync Impact` format rather than paraphrasing it. Net effect is a leaner surface (standalone reference dropped ~45 lines).
- **Out-of-scope artifact flagged, not touched:** the repo root carries a real leftover `SEMANTIC_MERGE.md` (a `merge --no-ff` record on `better-handoff`). It is the exact dead-artifact class this workstream eliminates, but it is outside task 02's three-file scope and outside task 05's grep paths (`skills/`, `CLAUDE.md`, `CATEGORIES.md`). Left for an orchestrator scope decision — deleting a tracked root file is not a dispatch verdict I should make silently.
