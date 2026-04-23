---
name: semantic-merge
description: "Use when about to run `git merge`, `git rebase`, or `git cherry-pick` on a research branch; when syncing a feature or analysis branch with a current base branch before integration; or when incoming changes may touch results-bearing files, analysis scripts, PLAN.md, RESULTS.md, drift tests, or domain-discipline artifacts. Triggers include: bare `git merge` / `git rebase` / `git cherry-pick` on a research branch (the merge-guard hook flags these automatically), \"sync with main\", \"pull main into this branch\", \"rebase onto main\", \"cherry-pick commit X\", or any branch integration where conflict resolution must preserve research intent. Invoked by `integration-workflow` during Sync and usable standalone by any agent or human doing a research-aware branch integration."
---

# Semantic Merge

Integrate branches by intent, not by lines. Understand what each side was trying to achieve, synthesize where both changes are valid, escalate research-meaningful decisions to the researcher, and leave a documented trail that later agents can follow.

**Core principle:** Treat conflicts as intent conflicts first and line conflicts second. Research-meaningful conflicts always go to the researcher. The agent implements the researcher's integration decisions; it does not judge methodology.

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

### 2. Research intent on both sides

Read commit messages, diffs, and handoff docs for each side. For workflow mode, current-branch intent comes from `PLAN.md` / `RESULTS.md`; for standalone mode, it comes from the branch name, commits, any present handoff docs, and diffs. Incoming intent comes from the commit range on the other side of the merge base.

**Classify each cluster of changes by role.** The role drives how the cluster is resolved:

- **Behavior or API** — code that changes what the program does or how it is called. Synthesize when both sides extend behavior compatibly; escalate when they contradict.
- **Data or schema** — column names, file formats, key definitions, sample filters. Research-meaningful; escalate before choosing.
- **Docs or narrative** — prose explaining intent. Prefer synthesis; stale claims from either side get rewritten.
- **Generated outputs** — figures, tables, compiled artifacts, fixtures. Prefer **regeneration** from merged sources over hand-editing either side's copy.
- **Tests** — including drift tests. Preserve both sides' assertions unless a research-meaningful result change justifies re-expecting; escalate meaningful result changes rather than silently updating.
- **Config or build** — dependencies, pipeline wiring, environment. Synthesize when additive; escalate when directions diverge.

The agent classifies and executes within each role; research-meaningful calls inside data, tests, and analysis outputs go to the researcher.

### 3. Build a resolution plan

For each overlapping area, pick one of:

- keep incoming,
- keep current-branch,
- **synthesize** both (preferred when both are valid and compatible),
- **regenerate** derived artifacts from merged sources,
- escalate to the researcher.

Prefer synthesis over picking sides. Prefer regeneration over hand-editing generated files.

### 4. Escalate research-meaningful choices

Ask the researcher before resolving — with intent and consequences, not raw diff chunks — when:

- both sides imply different valid research goals,
- a conflict changes variable definitions, sample construction, filters, data sources, econometric specifications, or analysis outputs,
- task structure in `PLAN.md` would change (routed through `planning-workflow §User Feedback and Changing Plans`),
- drift-test expectations would move because results meaningfully changed.

Log every answer per `handoff-doc` §User Decisions Log before committing the resolution. When `PLAN.md` is absent, record the decision in the standalone merge record and the sync commit body.

### 5. Resolve and land

Run the sync operation only after intent research. Resolve by the plan from Step 3. Preserve base-current deletions and relocations by default; restore branch-side content only when an approved task objective, logged user decision, or Sync impact obligation justifies it.

Mode references specify commit shape: workflow lands exactly one sync commit; standalone lands a sync commit plus as many semantic propagation commits as the resolution needs.

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

Workflow Sync lands the sync commit, records branch-level `## Sync Map` clusters, and annotates affected task blocks with compact `**Sync impact:**` pointers. It does not perform broad refactoring, codebase-fit cleanup, generated-output refreshes, drift-test expectation updates, or project-doc audit. Those are post-sync `refactor-and-integrate` responsibilities.

## Standalone Boundary

Standalone semantic-merge is complete branch-integration work, not just a map. It creates a merge record when needed, performs the requested merge / rebase / cherry-pick, lands semantic propagation commits when required, runs relevant checks and existing drift tests, and stops before broad codebase refactor. Broad refactor, if needed, is recorded as a remaining obligation.

## Exception

Orchestrator-managed parallel worktrees bypass this skill. Branches matching `<branch>/parallel/<slug>` merge with plain `git merge --no-ff`; the merge-guard hook exempts `*/parallel/*` source refs.
