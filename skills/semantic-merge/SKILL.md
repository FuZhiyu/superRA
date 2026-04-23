---
name: semantic-merge
description: "Use when about to run `git merge`, `git rebase`, or `git cherry-pick` on a research branch; when syncing a feature or analysis branch with a current base branch before integration; or when incoming changes may touch results-bearing files, analysis scripts, PLAN.md, RESULTS.md, drift tests, or domain-discipline artifacts. Triggers include: bare `git merge` / `git rebase` / `git cherry-pick` on a research branch (the merge-guard hook flags these automatically), \"sync with main\", \"pull main into this branch\", \"rebase onto main\", \"cherry-pick commit X\", or any branch integration where conflict resolution must preserve research intent. Invoked by `integration-workflow` during Sync and usable standalone by any agent or human doing a research-aware branch integration."
---

# Semantic Merge

Integrate branches by intent, not by lines. Understand what each side was trying to achieve, synthesize where both changes are valid, escalate research-meaningful decisions to the user, and leave a documented trail that later agents can follow.

**Core principle:** Treat conflicts as intent conflicts first and line conflicts second. Research-meaningful conflicts always go to the user. The agent implements the researcher's integration decisions; it does not judge methodology.

## Choose a Mode

Load exactly the mode reference that matches the call path, plus the shared references it names:

- **Workflow sync author:** `references/workflow-sync-author.md` when `integration-workflow` dispatches an agent to bring the current branch onto a confirmed base.
- **Workflow sync reviewer:** `references/workflow-sync-reviewer.md` when `integration-workflow` dispatches a separate reviewer before Integrate begins.
- **Standalone merge:** `references/standalone-merge.md` when this skill is invoked directly for a merge, rebase, cherry-pick, or branch sync outside the full integration workflow.
- **Shared quality and records:** `references/sync-quality.md` and `references/sync-map-format.md` carry the checklist, Sync Map, task-local Sync impact, and standalone merge-record formats.

## Shared Rules

1. Identify the governing baseline and operation direction before resolving conflicts.
2. Read commit messages, diffs, handoff docs, and relevant project docs to understand incoming and current intent.
3. Escalate research-owned conflicts before choosing a resolution.
4. Record every user decision per `handoff-doc` §User Decisions Log before committing the resolution.
5. Separate semantic sync / propagation from broad codebase refactor.
6. Verify no conflict markers remain and that touched subsystems pass targeted checks where cheap and relevant.

## Workflow Boundary

In `integration-workflow`, semantic-merge owns Sync and sync review. The workflow computes `BASE_REF`, `PRE_SYNC_BASE_SHA`, and `BASE_HEAD_SHA`, then dispatches a generic sync author and a generic sync reviewer that load this skill's mode references.

Workflow Sync lands the sync commit, records branch-level `## Sync Map` clusters, and annotates affected task blocks with compact `**Sync impact:**` pointers. It does not perform broad refactoring, codebase-fit cleanup, generated-output refreshes, drift-test expectation updates, or project-doc audit. Those are post-sync `refactor-and-integrate` responsibilities.

## Standalone Boundary

Standalone semantic-merge is complete branch-integration work, not just a map. It creates a merge record when needed, performs the requested merge/rebase/cherry-pick, lands semantic propagation commits when required, runs relevant checks and existing drift tests, and stops before broad codebase refactor.

## Exception

Orchestrator-managed parallel worktrees bypass this skill. Branches matching `<branch>/parallel/<slug>` merge with plain `git merge --no-ff`; the merge-guard hook exempts `*/parallel/*` source refs.
