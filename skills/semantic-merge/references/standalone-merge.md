# Standalone Semantic-Merge Mode

Use when this skill is invoked directly for a merge, rebase, cherry-pick, or branch sync outside `integration-workflow`. Also load `sync-quality.md` for the gated checklist. Walk the Shared Procedure in `semantic-merge/SKILL.md` (repo-state grounding, intent research with role classification, resolution plan, research-meaningful escalation, stale-reference sweep) — this reference only carries mode-specific content.

Standalone mode completes semantic merge work. It does not stop after identifying the map.

## Inputs

Caller supplies (or the agent infers from the session):

- requested operation: `merge | rebase | cherry-pick`
- incoming ref (branch, tag, or commit range)
- current branch
- governing baseline (merge base, or caller-declared baseline)
- direction — ask when direction is ambiguous and affects results, scope, or architecture

Current-branch intent comes from branch name, commits, `PLAN.md` / `RESULTS.md` if present, project docs, and diffs. Incoming intent comes from commits, diffs, docs, and any caller-supplied context.

## Mode-Specific Process

1. Create or update `SEMANTIC_MERGE.md` when the operation is material, lacks PLAN.md task structure, or leaves file/script-level obligations.
2. When `PLAN.md` is absent, record research-owned user decisions in `SEMANTIC_MERGE.md` and the relevant commit body instead of `PLAN.md §Decisions`.
3. Run the requested merge / rebase / cherry-pick after intent research.
4. Land the **sync commit**.
5. Make **follow-up semantic propagation commits** when needed so non-conflicted sibling files, scripts, tests, docs, and handoff records reflect the chosen resolution. Separate intent-bearing propagation from the mechanical sync when both are non-trivial; a single combined commit is acceptable only when the sync and propagation are both trivial enough for the commit message to describe honestly.
6. Run targeted checks and existing drift tests when present. Do not silently re-expect drift tests after meaningful result changes — escalate per `SKILL.md §Shared Procedure` step 4.
7. Stop before broad codebase refactor. If broad refactor is needed, record it as a remaining obligation in the merge record.

## Semantic Merge Record Format

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

## Report

Report:

- operation, incoming ref, governing baseline, and direction
- current-branch intent and incoming intent
- sync commit and propagation commits
- merge record location or why none was needed
- user decisions asked and logged
- stash status (if any)
- checks run and remaining obligations
