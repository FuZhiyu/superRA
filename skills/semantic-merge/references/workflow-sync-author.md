# Workflow Sync Author Mode

Uses `semantic-merge/SKILL.md` §Shared Steps and §Semantic Coherence Checklist. This reference carries the workflow Sync boundary, inputs, task-local `## Sync Impact` format, and status return.

## Boundary

In `superintegrate`, semantic-merge owns Sync and sync review. The workflow computes `BASE_REF`, `PRE_SYNC_BASE_SHA`, and `BASE_HEAD_SHA`, then dispatches a generic sync author and a generic sync reviewer that load this skill's mode references.

Workflow Sync lands the merge commit plus any propagation commits needed to reach **semantic coherence**, and adds a `## Sync Impact` section to each affected task whose post-sync diff needs task-specific context. The branch-level narrative — incoming intent, resolution thesis, cluster breakdown — rides the merge and propagation commit messages, never the task tree. Stopping rule: `SKILL.md §Semantic Coherence Checklist §Scope boundary`. Codebase coherence is Integrate's; `## Sync Impact` only explains the approved post-sync diff.

## Inputs

Required inputs:

- `BASE_REF`
- `PRE_SYNC_BASE_SHA`
- `BASE_HEAD_SHA`
- incoming range `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`
- operation direction, defaulting to merging the confirmed base into the current branch

Current-branch intent: the `superRA/` task tree (root and task objectives) plus prior sync commit messages. Incoming intent: commits, diffs, and docs in `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`.

## Mode-Specific Process

1. Run the requested sync operation after intent investigation. For the normal workflow path, merge `BASE_REF` into the current branch.
2. Carry the branch-level narrative — incoming intent, resolution thesis, cluster breakdown — in the merge commit message and any propagation commit messages. User decisions are also folded into the relevant task `## Objective` per `SKILL.md §Shared Steps` step 4.
3. Add a `## Sync Impact` section only to tasks whose post-sync diff needs task-specific context during maturation or Integrate.
4. **Land the merge commit plus any propagation commits needed to reach semantic coherence** per `SKILL.md §Shared Steps` step 5, including each affected task's `## Sync Impact` section with the commits that produce it.

## `## Sync Impact` Format

A task whose post-sync diff needs task-specific context during maturation or Integrate gets a self-contained `## Sync Impact` section in its `task.md`:

```markdown
## Sync Impact

<Task-specific post-sync context: what the sync changed in this task's area, what was kept/dropped/synthesized, and any assumption a later maturation or Integrate implementer or reviewer needs to read the approved diff.> Sync commits: `<sha>`[, `<sha>`...].
```

Top-level and self-anchoring like `## Results`, not anchored to any inline field. It never restates the branch narrative the commit messages carry — cite the sync commit SHA(s) instead — and it is not an Integrate to-do list.

**Lifecycle.** Temporary scaffolding for the active Sync / maturation / Integrate round, added only to tasks that need it. Remove it at Integrate closeout; a lasting task assumption folds into `## Objective` first. A warn-only `superra task check` rule flags any `## Sync Impact` surviving closeout.

## Status Return

Return the status enum plus the sync commit SHA(s); the branch narrative lives in those commit messages, not the return.

- `DONE`: sync commits landed and are ready for sync review.
- `DONE_WITH_CONCERNS`: sync landed, but non-blocking concerns remain for the reviewer or Integrate.
- `NEEDS_CONTEXT`: missing upstream context or a user decision is needed.
- `BLOCKED`: the sync cannot proceed safely.

Note stash status if anything was stashed.
