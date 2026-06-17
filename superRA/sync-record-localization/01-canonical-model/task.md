---
title: "Canonical Model: Localized Temporary ## Sync Impact, No Sync Map"
status: approved
depends_on: []
tags: []
created: 2026-06-17
---

## Objective

Author the single source of truth for the localized sync-record model. This task is the keystone; `02`–`05` align to what it establishes. Edit three files:

**1. `skills/semantic-merge/references/workflow-sync-author.md`** (owner of the sync-record format):
- Remove the entire `## Workflow Sync Map Format` section and all instructions to write a branch-level `## Sync Map` in root `superRA/task.md`. The branch-level narrative (incoming intent, resolution thesis, cluster breakdown) is now carried by the merge commit message plus any propagation commit messages — i.e. the git log. State that explicitly where the Sync Map instruction used to be.
- Replace the `## Task-Local Sync Impact Format` section with the canonical form: a **`## Sync Impact` section** added to each affected task's `task.md`. It is self-contained — it explains the task-specific post-sync context needed to understand the approved diff during Integrate, and may cite the relevant sync commit SHA(s) for branch context. It does **not** reference a `## Sync Map` (there is none) and is **not** anchored to `**Integration status:**` (that field no longer exists; integration review uses the `status:` frontmatter field). Give the canonical block shape (see the design intent in the parent `## Objective`).
- State the temporary lifecycle: the sync author adds `## Sync Impact` only to tasks whose post-sync diff needs task-specific context; it is removed at Integrate closeout; a warn-only `superra task check` rule (built in `04-cleanup-check`) catches any that survive.
- Replace the `## Status Return` verbose blob with the lean model: return status + the sync commit SHA(s); the authored narrative lives in the commit messages, not the return.
- Sweep stale terminology in this file: "task block(s)" → task / `task.md`; tasks referenced by path, not "Tasks `<ids>`".

**2. `skills/task-tree/references/task-file-contract.md`** (owner of the body-section vocabulary):
- Add `## Sync Impact` to the recognized body-section list as a **conditional, integration-phase-only, temporary** section — lifecycle sibling of `## Workflow Status` — owned by the sync author, present only on tasks with post-sync context, removed at Integrate closeout. Keep the entry minimal and point to `semantic-merge` for the format.

**3. `CLAUDE.md`** (ownership table, line ~83):
- Change the semantic-merge ownership row from "Sync Map + task-local Sync impact formats" to "task-local `## Sync Impact` format (temporary)". Do not otherwise reword the row.

## Planner Guidance

The format owner is `semantic-merge` per the CLAUDE.md ownership table; the contract only registers the section in the vocabulary and points back. Keep the contract entry a pointer, not a paraphrase, per DRY.

This file currently anchors Sync Impact "directly after `**Integration status:**`" — that anchor is being deleted, so the new `## Sync Impact` section is self-anchoring (a top-level heading like `## Results`).

## Results

### Key Findings

Authored the single source of truth for the localized sync-record model across three files.

**1. [`skills/semantic-merge/references/workflow-sync-author.md`](../../../skills/semantic-merge/references/workflow-sync-author.md)** — the format owner:
- Removed the entire `## Workflow Sync Map Format` section. The branch-level narrative (incoming intent, resolution thesis, cluster breakdown) is now stated explicitly to live in the merge commit message plus propagation commit messages (the git log), in the Boundary and Mode-Specific Process — not the task tree.
- Replaced `## Task-Local Sync Impact Format` with the canonical `## Sync Impact` Format: a self-contained top-level section (self-anchoring like `## Results`), added only to affected tasks, citing sync commit SHA(s) for branch context, explicitly not referencing a Sync Map and not anchored to the deleted `**Integration status:**` field.
- Stated the temporary lifecycle: added only where needed, removed at Integrate closeout (lasting assumptions fold into `## Objective`), with a warn-only `superra task check` rule (built in `04-cleanup-check`) catching survivors.
- Replaced the verbose `## Status Return` blob with the lean model: status enum + sync commit SHA(s); narrative lives in commit messages.
- Swept stale terminology: "task block(s)" → task / `task.md`; "Tasks `<ids>`" path-referenced; the dead `**Sync impact:**` inline field and `**Sync commits:**` field removed. Existing inputs/process references to `## Sync Map` content rewritten to the git log.

**2. [`skills/task-tree/references/task-file-contract.md`](../../../skills/task-tree/references/task-file-contract.md)** — body-section vocabulary owner:
- Added `## Sync Impact` as a conditional, integration-phase-only, temporary body section (lifecycle sibling of `## Workflow Status`), owned by the sync author, present only on tasks with post-sync context, removed at Integrate closeout. Kept as a pointer to `semantic-merge` for the format, not a paraphrase, per Planner Guidance.

**3. [`CLAUDE.md`](../../../CLAUDE.md) ownership table** — changed the semantic-merge row from "Sync Map + task-local Sync impact formats" to "task-local `## Sync Impact` format (temporary)"; no other rewording.

### Notes

- The single remaining "Sync Map" mention in the author reference is an intentional negation ("does not reference a branch-level Sync Map (there is none)"), retiring the old concept for the reader — not a stale reference.
- `SKILL.md` cross-references to `**Sync impact:**` / `## Sync Map` (SKILL.md §Semantic Coherence Checklist, `workflow-sync-reviewer.md`) are task `02`'s scope and intentionally left for that task to align to this canonical model.
- Verified the in-text cross-refs land: `SKILL.md §Shared Steps` step 4 (intent-changing escalation, fold into objective) and step 5 (land merge + propagation commits) both exist as cited.
