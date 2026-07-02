# Workflow Sync Author Mode

Workflow sync author mode uses `semantic-merge/SKILL.md` §Shared Steps and §Semantic Coherence Checklist. This reference carries the workflow Sync boundary, inputs, task-local `## Sync Impact` format, and status return.

## Boundary

In `superintegrate`, semantic-merge owns Sync and sync review. The workflow computes `BASE_REF`, `PRE_SYNC_BASE_SHA`, and `BASE_HEAD_SHA`, then dispatches a generic sync author and a generic sync reviewer that load this skill's mode references.

Workflow Sync lands the merge commit plus any propagation commits needed to reach **semantic coherence**, and adds a `## Sync Impact` section to each affected task whose post-sync diff needs task-specific context. The branch-level narrative — incoming intent, resolution thesis, cluster breakdown — is carried by the merge commit message plus any propagation commit messages, i.e. the git log; it is not written into the task tree. `SKILL.md §Semantic Coherence Checklist §Scope boundary` is the stopping rule. Codebase coherence is handled later by Integrate; `## Sync Impact` only explains the approved post-sync diff.

## Inputs

Required inputs:

- `BASE_REF`
- `PRE_SYNC_BASE_SHA`
- `BASE_HEAD_SHA`
- incoming range `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`
- operation direction, defaulting to merging the confirmed base into the current branch

Current-branch intent comes from the `superRA/` task tree (root and task objectives) and prior sync commit messages in the git log. Incoming intent comes from commits, diffs, and docs in `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`.

## Mode-Specific Process

1. Run the requested sync operation after intent investigation. For the normal workflow path, merge `BASE_REF` into the current branch.
2. Carry the branch-level narrative — incoming intent, resolution thesis, cluster breakdown — in the merge commit message and any propagation commit messages. User decisions are also folded into the relevant task `## Objective` per `SKILL.md §Shared Steps` step 4.
3. Add a `## Sync Impact` section only to tasks whose post-sync diff needs task-specific context during Integrate.
4. **Land the merge commit plus any propagation commits needed to reach semantic coherence** per `SKILL.md §Shared Steps` step 5, including each affected task's `## Sync Impact` section with the commits that produce it.

## `## Sync Impact` Format

When the post-sync diff to a task needs task-specific context to be understood during Integrate, add a self-contained `## Sync Impact` section to that task's `task.md`:

```markdown
## Sync Impact

<Task-specific post-sync context: what the sync changed in this task's area, what was kept/dropped/synthesized, and any assumption a later Integrate implementer or reviewer needs to read the approved diff.> Sync commits: `<sha>`[, `<sha>`...].
```

It is a top-level section, self-anchoring like `## Results` — not anchored to any inline field. It does not reference a branch-level Sync Map (there is none) and does not restate the branch narrative carried by the commit messages; cite the sync commit SHA(s) for that context instead. It is not an Integrate to-do list.

**Lifecycle.** `## Sync Impact` is temporary scaffolding for the active Sync / Integrate round, added only to tasks that need it. Remove it at Integrate closeout, unless a lasting task assumption belongs in the task — in which case fold that into `## Objective` and drop the `## Sync Impact` section. A warn-only `superra task check` rule flags any `## Sync Impact` that survives closeout.

## Status Return

Return the status enum plus the sync commit SHA(s); the branch narrative lives in those commit messages, not the return.

- `DONE`: sync commits landed and are ready for sync review.
- `DONE_WITH_CONCERNS`: sync landed, but non-blocking concerns remain for the reviewer or Integrate.
- `NEEDS_CONTEXT`: missing upstream context or a user decision is needed.
- `BLOCKED`: the sync cannot proceed safely.

Note stash status if anything was stashed.
