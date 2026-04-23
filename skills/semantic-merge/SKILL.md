---
name: semantic-merge
description: "Use when about to run `git merge`, `git rebase`, or `git cherry-pick`; when syncing a feature, analysis, or work branch with a current base branch before integration; or when incoming changes may touch results-bearing files, source scripts, PLAN.md, RESULTS.md, drift tests, or domain-discipline artifacts. Triggers include: bare `git merge` / `git rebase` / `git cherry-pick` (the merge-guard hook flags these automatically), \"sync with main\", \"pull main into this branch\", \"rebase onto main\", \"cherry-pick commit X\", or any branch integration where conflict resolution must preserve the intent behind each side. Invoked by `integration-workflow` during Sync and usable standalone by any agent or human doing an intent-aware branch integration."
---

# Semantic Merge

Integrate branches by intent, not by lines. Understand what each side was trying to achieve, synthesize where both changes are valid, escalate decisions that would change what the branch means to the user, and leave a documented trail that later agents can follow.

**Core principle:** Treat conflicts as intent conflicts first and line conflicts second. Conflicts that change intent always go to the user. The agent implements the user's integration decisions; it does not override them.

## Choose a Mode

Load exactly the mode reference that matches the call path:

- **Workflow sync author:** `references/workflow-sync-author.md` when `integration-workflow` dispatches an agent to bring the current branch onto a confirmed base. The author owns the Workflow Sync Map and task-local Sync impact format.
- **Workflow sync reviewer:** `references/workflow-sync-reviewer.md` when `integration-workflow` dispatches a separate reviewer before Integrate begins. The reviewer points at the author reference for format recognition.
- **Standalone merge:** `references/standalone-merge.md` when this skill is invoked directly for a merge, rebase, cherry-pick, or branch sync outside the full integration workflow. The standalone reference owns the Semantic Merge Record format.
- **Shared checklist:** `references/sync-quality.md` carries the gated quality checklist that both modes walk.

## Shared Procedure

All modes walk the same canonical flow. Mode references add only mode-specific inputs, format specs, commit-shape constraints, and status returns.

### 1. Ground in repository state

Inspect before changing anything:

- Current branch, worktree status, and any ongoing merge / rebase / cherry-pick state.
- Merge base, incoming commit range, and the set of touched files.
- For workflow mode: the dispatched `BASE_REF`, `PRE_SYNC_BASE_SHA`, `BASE_HEAD_SHA`, and incoming range.

If the worktree is dirty with unrelated changes, preserve them reversibly with a named stash before any sync operation and report the stash in the status return. Stop and clarify only when the repository is already mid-operation (unresolved merge, in-flight rebase, detached HEAD) in a way that makes intent ambiguous.

### 2. Investigate intent on both sides

Read commit messages, diffs, and handoff docs for each side. For workflow mode, current-branch intent comes from `PLAN.md` / `RESULTS.md`; for standalone mode, it comes from the branch name, commits, any present handoff docs, and diffs. Incoming intent comes from the commit range on the other side of the merge base.

**Classify each cluster of changes by role.** The role drives how the cluster is resolved:

- **Behavior or API** — code that changes what the program does or how it is called. Synthesize when both sides extend behavior compatibly; escalate when they contradict.
- **Data or schema** — column names, file formats, key definitions, sample filters. Escalate before choosing — the user owns these calls.
- **Docs or narrative** — prose explaining intent. Prefer synthesis; stale claims from either side get rewritten.
- **Generated outputs** — figures, tables, compiled artifacts, fixtures. Prefer **regeneration** from merged sources over hand-editing either side's copy.
- **Tests** — including drift tests. Preserve both sides' assertions unless a meaningful result change justifies re-expecting; escalate result changes rather than silently updating.
- **Config or build** — dependencies, pipeline wiring, environment. Synthesize when additive; escalate when directions diverge.

The agent classifies and executes within each role; calls that would change intent — data contracts, test expectations, outputs — go to the user.

### 3. Build a resolution plan

For each overlapping area, pick one of:

- keep incoming,
- keep current-branch,
- **synthesize** both (preferred when both are valid and compatible),
- **regenerate** derived artifacts from merged sources,
- escalate to the user.

Prefer synthesis over picking sides. Prefer regeneration over hand-editing generated files.

### 4. Escalate intent-changing choices

Ask the user before resolving — with intent and consequences, not raw diff chunks — when:

- both sides imply different valid intents,
- a conflict changes data contracts, inputs, test expectations, program outputs, or the meaning of a published result,
- task structure in `PLAN.md` would change (routed through `planning-workflow §User Feedback and Changing Plans`),
- drift-test or result-level expectations would move because outputs meaningfully changed.

Log every answer per `handoff-doc` §User Decisions Log before committing the resolution. When `PLAN.md` is absent, record the decision in the standalone merge record and the sync commit body.

### 5. Resolve and land

Run the sync operation only after intent investigation. Resolve by the plan from Step 3. Preserve base-current deletions and relocations by default; restore branch-side content only when an approved task objective, logged user decision, or Sync impact obligation justifies it.

**Land exactly one minimal merge commit.** The same rule applies to both modes. The commit must leave the tree passing **existing protection** — drift tests and key-result coverage established in `integration-workflow` Phase A when in workflow mode, or existing tests and drift tests when standalone. Protection-pass is the unambiguous definition of "not broken": if the existing protection passes after the commit, the sync is coherent; if it fails, the commit is not yet minimal enough or needs escalation.

Include in this commit: conflict resolution, resolved docs, and the mode-specific handoff artifact (Sync Map + task-local Sync impact in workflow mode; `SEMANTIC_MERGE.md` merge record in standalone mode). Do not include broader propagation in this commit — caller updates for renames, output regeneration, drift-test expectation updates, project-doc audit. Those defer to `refactor-and-integrate` (via Integrate in workflow mode, or invoked by the caller after standalone returns) and are recorded as post-sync obligations in the handoff artifact.

### 6. Verify — stale-reference sweep

Run more than a "no conflict markers" check. Before returning, sweep for stale references the merge may have left behind:

- labels, identifiers, or variable names renamed on one side but still used on the other,
- paths or module locations moved on one side,
- docs and comments that reference the old shape,
- generated outputs that should have been regenerated,
- cross-file imports, registry entries, or config keys.

Run targeted checks for touched subsystems where cheap and relevant. Confirm the tree matches the integrated intent, not just a conflict-free state.

## Workflow Boundary

In `integration-workflow`, semantic-merge owns Sync and sync review. The workflow computes `BASE_REF`, `PRE_SYNC_BASE_SHA`, and `BASE_HEAD_SHA`, then dispatches a generic sync author and a generic sync reviewer that load this skill's mode references.

Workflow Sync lands the single minimal merge commit, records branch-level `## Sync Map` clusters, and annotates affected task blocks with compact `**Sync impact:**` pointers. Broader propagation — caller updates for renames, output regeneration, drift-test expectation updates, project-doc audit, broad refactor — defers to the post-sync `refactor-and-integrate` phase and is recorded as a Sync Map obligation.

## Standalone Boundary

Standalone semantic-merge lands the same single minimal merge commit that leaves existing tests and drift tests passing, and captures the resolution plus any remaining obligations in `SEMANTIC_MERGE.md`. Broader propagation and refactor are out of scope for this skill; the caller can invoke `refactor-and-integrate` after this skill returns, or satisfy obligations manually.

## Exception

Orchestrator-managed parallel worktrees bypass this skill. Branches matching `<branch>/parallel/<slug>` merge with plain `git merge --no-ff`; the merge-guard hook exempts `*/parallel/*` source refs.
