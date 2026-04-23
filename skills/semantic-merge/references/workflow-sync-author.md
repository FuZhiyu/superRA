# Workflow Sync Author Mode

Use when `integration-workflow` dispatches a generic sync author to bring the current branch onto a confirmed base. Also load `sync-quality.md` for the gated checklist. Walk the Shared Procedure in `semantic-merge/SKILL.md` (repo-state grounding, intent investigation with role classification, resolution plan, intent-changing escalation, stale-reference sweep) — this reference only carries mode-specific content.

## Inputs

The dispatch supplies:

- `BASE_REF`
- `PRE_SYNC_BASE_SHA`
- `BASE_HEAD_SHA`
- incoming range `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`
- operation direction, defaulting to merging the confirmed base into the current branch

Current-branch intent comes from `PLAN.md` header, `## Decisions`, any existing `## Sync Map`, and `RESULTS.md`. Incoming intent comes from commits, diffs, and docs in `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`.

## Mode-Specific Process

1. Run the requested sync operation after intent investigation. For the normal workflow path, merge `BASE_REF` into the current branch.
2. Write the branch-level `## Sync Map` in `PLAN.md` when there is material overlap, a conflict, a user decision, sync-review carryover, or a post-sync obligation. Omit it for no-op or trivial syncs with no obligations.
3. Add task-local `**Sync impact:**` annotations only to task blocks that need task-specific propagation during Integrate. Keep them short and point back to the relevant Sync Map cluster.
4. **Land exactly one minimal merge commit.** Include conflict resolution, resolved docs, `PLAN.md` Sync Map, and task-local Sync impact annotations in the same commit. The tree must pass existing protection (drift tests + key-result coverage established in `integration-workflow` Phase A) after the commit — that is the unambiguous "coherent tree" test. Do not include broader propagation in this commit.
5. Record broader propagation — caller updates for renames, output regeneration, drift-test expectation updates, project-doc audit, broad refactor — as post-sync obligations in the Sync Map. Integrate satisfies them.

## Workflow Sync Map Format

```markdown
## Sync Map

**Base branch:** `<base-ref>`
**Pre-sync merge base:** `<PRE_SYNC_BASE_SHA>`
**Synced base head:** `<BASE_HEAD_SHA>`
**Incoming range:** `<PRE_SYNC_BASE_SHA>..<BASE_HEAD_SHA>`
**Sync commit:** `<SYNC_COMMIT_SHA>`
**Sync review status:** `IMPLEMENTED | REVISE | APPROVED`

### Branch Summary

**Current branch intent:** <one paragraph, usually from PLAN.md / RESULTS.md>.
**Incoming intent:** <one paragraph from incoming commits and diffs>.
**Resolution thesis:** <one paragraph describing the governing resolution>.

### Sync Clusters

> **Sync cluster `<cluster-id>` (YYYY-MM-DD):** commits `<sha...>`; paths `<paths>`; affects Tasks `<ids>`.
> **Incoming intent:** <plain-language purpose of incoming/base changes>.
> **Sync resolution:** <what the sync commit kept, dropped, or synthesized>.
> **Post-sync obligations:** <task IDs, stale paths, APIs, docs, generated outputs, tests, or review areas for Integrate>.
> **User decision:** <summary or "None">.

> **Sync review notes (present only while REVISE is active):**
> 1. [MAJOR] <specific unresolved sync issue, with file/path evidence>.
```

`## Sync Map` carries the big picture. It is temporary scaffolding for the active Sync / Integrate round.

## Task-Local Sync Impact Format

When a cluster affects a task, add a compact field to that task block, directly after `**Integration status:**`:

```markdown
**Sync impact:** Cluster `<cluster-id>` requires <task-specific integration obligation>. Source: `PLAN.md ## Sync Map`.
```

The task-local impact is not a second Sync Map. It gives task-scoped integration implementers and reviewers the relevant sync intent without making them reconstruct branch history.

Remove satisfied task-local Sync impact fields when Integrate closes, unless a lasting task assumption still belongs in the task block.

## Status Return

Return one of:

- `DONE`: sync commit landed and is ready for sync review.
- `DONE_WITH_CONCERNS`: sync landed, but non-blocking concerns remain for the reviewer or Integrate.
- `NEEDS_CONTEXT`: missing upstream context or a user decision is needed.
- `BLOCKED`: the sync cannot proceed safely.

Report the sync commit SHA, Sync Map location or why none was needed, task-local Sync impact annotations added, stash status (if any), checks run, and post-sync obligations.
