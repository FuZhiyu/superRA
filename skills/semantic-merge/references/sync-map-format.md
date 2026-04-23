# Sync Map and Impact Formats

Use these formats for workflow Sync and standalone semantic-merge records. Keep branch-level context in one place and task/file-local obligations as short pointers.

## Workflow Sync Map

Write `## Sync Map` in PLAN.md when there is material overlap, a conflict, a user decision, a sync-review finding, or a post-sync obligation. Omit it for no-op or trivial syncs with no obligations.

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

## Task-Local Sync Impact

When a cluster affects a task, add a compact field to that task block, directly after `**Integration status:**`:

```markdown
**Sync impact:** Cluster `<cluster-id>` requires <task-specific integration obligation>. Source: `PLAN.md ## Sync Map`.
```

The task-local impact is not a second Sync Map. It gives task-scoped integration implementers and reviewers the relevant sync intent without making them reconstruct branch history.

Remove satisfied task-local Sync impact fields when Integrate closes, unless a lasting task assumption still belongs in the task block.

## Standalone Merge Record

When no PLAN.md task structure exists, or when standalone semantic-merge needs a durable record beyond the commit body, create or update `SEMANTIC_MERGE.md`:

```markdown
# Semantic Merge Record

**Operation:** `merge | rebase | cherry-pick`
**Current branch:** `<branch>`
**Incoming ref:** `<incoming-ref>`
**Governing baseline:** `<sha/ref>`
**Sync commit:** `<sha>`
**Propagation commits:** `<sha... or None>`

## Current Branch Intent

<summary from branch name, commits, docs, and diffs>

## Incoming Intent

<summary from incoming commits, docs, and diffs>

## Resolution Thesis

<what the merge kept, dropped, or synthesized>

## File / Script Impact Map

| Path or path cluster | Incoming intent | Resolution | Follow-up |
|---|---|---|---|
| `<path>` | `<intent>` | `<resolution>` | `<remaining obligation or None>` |

## User Decisions

<logged decisions or "None">

## Checks

<commands and outcomes>

## Remaining Obligations

<non-refactor obligations that remain, or "None">
```
