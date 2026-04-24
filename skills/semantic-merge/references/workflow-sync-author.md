# Workflow Sync Author Mode

Use when `integration-workflow` dispatches a generic sync author to bring the current branch onto a confirmed base. Walk the Shared Steps in `semantic-merge/SKILL.md` (repo-state grounding, intent investigation with role classification, resolution plan, intent-changing escalation, detect-and-resolve stale references) and the §Semantic Coherence Checklist in the same body — this reference only carries mode-specific content.

## Boundary

In `integration-workflow`, semantic-merge owns Sync and sync review. The workflow computes `BASE_REF`, `PRE_SYNC_BASE_SHA`, and `BASE_HEAD_SHA`, then dispatches a generic sync author and a generic sync reviewer that load this skill's mode references.

Workflow Sync lands the merge commit plus any propagation commits needed to reach **semantic coherence**, records branch-level `## Sync Map` clusters, and annotates affected task blocks with compact `**Sync impact:**` pointers. `SKILL.md §Semantic Coherence Checklist §Scope boundary` is the stopping rule. **Codebase coherence** — convention fit, utility reuse, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff against the host — is handled later by Integrate; Sync notes only explain the approved post-sync diff.

## Inputs

The dispatch supplies:

- `BASE_REF`
- `PRE_SYNC_BASE_SHA`
- `BASE_HEAD_SHA`
- incoming range `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`
- operation direction, defaulting to merging the confirmed base into the current branch

Current-branch intent comes from `PLAN.md` header, `## Decisions`, and `RESULTS.md`; existing `## Sync Map` content supplies prior sync context. Incoming intent comes from commits, diffs, and docs in `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`.

## Mode-Specific Process

1. Run the requested sync operation after intent investigation. For the normal workflow path, merge `BASE_REF` into the current branch.
2. Write the branch-level `## Sync Map` in `PLAN.md` when there is material overlap, a conflict, a user decision, sync-review carryover, or post-sync context worth preserving. Omit it for no-op or trivial syncs with no context.
3. Add task-local `**Sync impact:**` annotations only to task blocks whose post-sync diff needs task-specific context during Integrate. Keep them short and point back to the relevant Sync Map cluster.
4. **Land the merge commit plus any propagation commits needed to reach semantic coherence.** Include conflict resolution, resolved docs, `PLAN.md` Sync Map, and task-local Sync impact annotations with the commits that produce them. Before returning, update `**Sync commits:**` to list the full commit chain this mode landed. Every commit must leave the tree passing existing protection (drift tests + key-result coverage established in `integration-workflow` Protect); per-commit protection-pass is the lower bound, `SKILL.md §Semantic Coherence Checklist §Scope boundary` is the stopping rule.

## Workflow Sync Map Format

```markdown
## Sync Map

**Base branch:** `<base-ref>`
**Pre-sync merge base:** `<PRE_SYNC_BASE_SHA>`
**Synced base head:** `<BASE_HEAD_SHA>`
**Incoming range:** `<PRE_SYNC_BASE_SHA>..<BASE_HEAD_SHA>`
**Sync commits:** `<MERGE_COMMIT_SHA>`[, `<PROPAGATION_OR_DOC_SHA>`...]
**Sync review status:** `IMPLEMENTED | REVISE | APPROVED`

### Branch Summary

**Incoming intent:** <one paragraph from incoming commits and diffs>.
**Resolution thesis:** <one paragraph describing the governing resolution>.

### Sync Clusters

> **Sync cluster `<cluster-id>` (YYYY-MM-DD):** commits `<sha...>`; paths `<paths>`; affects Tasks `<ids>`.
> **Incoming intent:** <plain-language purpose of incoming/base changes>.
> **Sync resolution:** <what the sync commits kept, dropped, or synthesized>.
> **Integration context:** <concise context for later codebase review, or "None">.
> **User decision:** <summary or "None">.

> **Sync review notes (present only while REVISE is active):**
> 1. [MAJOR] <specific unresolved sync issue, with file/path evidence>.
```

`## Sync Map` carries the big picture. In workflow mode, do not restate current-branch intent already present in `PLAN.md` / `RESULTS.md`. It is temporary scaffolding for the active Sync / Integrate round.

## Task-Local Sync Impact Format

When a cluster affects a task, add a compact field to that task block, directly after `**Integration status:**`:

```markdown
**Sync impact:** Cluster `<cluster-id>` explains <task-specific post-sync context>. Source: `PLAN.md ## Sync Map`.
```

The task-local impact is not a second Sync Map and not an Integrate to-do list. It gives task-scoped integration implementers and reviewers the context needed to understand the approved post-sync diff without reconstructing branch history.

Remove temporary task-local Sync impact fields when Integrate closes, unless a lasting task assumption still belongs in the task block.

## Status Return

Return one of:

- `DONE`: sync commits landed and are ready for sync review.
- `DONE_WITH_CONCERNS`: sync landed, but non-blocking concerns remain for the reviewer or Integrate.
- `NEEDS_CONTEXT`: missing upstream context or a user decision is needed.
- `BLOCKED`: the sync cannot proceed safely.

Report the full sync commit chain, Sync Map location or why none was needed, task-local Sync impact annotations added, stash status (if any), checks run, and any codebase-review context recorded.
