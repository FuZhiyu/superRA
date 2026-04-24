# Standalone Semantic-Merge Mode

Use when this skill is invoked directly for a merge, rebase, cherry-pick, or branch sync outside `integration-workflow`. Also load `sync-quality.md` for the gated checklist — it encodes the semantic-coherence stopping rule. Walk the Techniques in `semantic-merge/SKILL.md` (repo-state grounding, intent investigation with role classification, resolution plan, intent-changing escalation, detect-and-resolve stale references) — this reference only carries mode-specific content.

Standalone mode carries the merge through to **semantic coherence** and records any deferred **codebase-coherence** work in the merge record so the caller — or `refactor-and-integrate`, when invoked after this skill returns — can satisfy it.

## Inputs

Caller supplies (or the agent infers from the session):

- requested operation: `merge | rebase | cherry-pick`
- incoming ref (branch, tag, or commit range)
- current branch
- governing baseline (merge base, or caller-declared baseline)
- direction — ask when direction is ambiguous and affects results, scope, or architecture

Current-branch intent comes from branch name, commits, `PLAN.md` / `RESULTS.md` if present, project docs, and diffs. Incoming intent comes from commits, diffs, docs, and any caller-supplied context.

## Mode-Specific Process

1. Create or update `SEMANTIC_MERGE.md` when the operation is material, lacks PLAN.md task structure, or leaves file/script-level obligations. When `PLAN.md` is absent, record user decisions in `SEMANTIC_MERGE.md` and the relevant commit body instead of `PLAN.md §Decisions`.
2. Run the requested merge / rebase / cherry-pick after intent investigation.
3. **Land the merge commit plus any propagation commits needed to reach semantic coherence.** `sync-quality.md §Scope boundary` is the checklist. Every commit must leave existing tests and drift tests passing — per-commit protection-pass is the lower bound. Do not silently re-expect drift tests after meaningful result changes; escalate per `SKILL.md §Techniques` step 4. Include conflict resolution, resolved docs, and `SEMANTIC_MERGE.md` with the commits that produce them.
4. Record **codebase-coherence** obligations — convention fit, utility reuse, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff against the host — in the `SEMANTIC_MERGE.md` File / Script Impact Map under `Follow-up`. The caller can invoke `refactor-and-integrate` after this skill returns to satisfy them, or handle them manually.

## Semantic Merge Record Format

When no PLAN.md task structure exists, or when standalone semantic-merge needs a durable record beyond the commit body, create or update `SEMANTIC_MERGE.md`:

```markdown
# Semantic Merge Record

**Operation:** `merge | rebase | cherry-pick`
**Current branch:** `<branch>`
**Incoming ref:** `<incoming-ref>`
**Governing baseline:** `<sha/ref>`
**Merge commit:** `<sha>`
**Propagation commits:** `<sha1>, <sha2>, ...` (or `None`)

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

<deferred propagation / refactor / regeneration / doc-audit work for the caller or `refactor-and-integrate` to satisfy, or "None">
```

## Report

Report:

- operation, incoming ref, governing baseline, and direction
- current-branch intent and incoming intent
- merge commit SHA and any propagation-commit SHAs
- merge record location or why none was needed
- user decisions asked and logged
- stash status (if any)
- checks run (existing tests, drift tests) and remaining obligations deferred to the caller / `refactor-and-integrate`
