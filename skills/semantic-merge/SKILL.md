---
name: semantic-merge
description: "Use when about to run `git merge`, `git rebase`, or `git cherry-pick`; when syncing a feature, analysis, or work branch with a current base branch before integration; or when incoming changes may touch results-bearing files, source scripts, PLAN.md, RESULTS.md, drift tests, or domain-discipline artifacts. Triggers include: bare `git merge` / `git rebase` / `git cherry-pick` (the merge-guard hook flags these automatically), \"sync with main\", \"pull main into this branch\", \"rebase onto main\", \"cherry-pick commit X\", or any branch integration where conflict resolution must preserve the intent behind each side. Invoked by `integration-workflow` during Sync and usable standalone by any agent or human doing an intent-aware branch integration."
---

# Semantic Merge

Integrate branches by intent, not by lines. Understand what each side was trying to achieve, synthesize where both changes are valid, escalate decisions that would change what the branch means to the user, and leave a documented trail that later agents can follow.

**Core principle:** Treat conflicts as intent conflicts first and line conflicts second. Conflicts that change intent always go to the user. The agent implements the user's integration decisions; it does not override them.

## Choose a Mode

Load exactly the mode reference that matches the call path:

- **Workflow sync author:** `references/workflow-sync-author.md` when `integration-workflow` dispatches an agent to bring the current branch onto a confirmed base. The author owns the Workflow Sync Map and task-local Sync impact format, and carries the Workflow Sync scope boundary.
- **Workflow sync reviewer:** `references/workflow-sync-reviewer.md` when `integration-workflow` dispatches a separate reviewer before Integrate begins. The reviewer points at the author reference for boundary and format recognition.
- **Standalone merge:** `references/standalone-merge.md` when this skill is invoked directly for a merge, rebase, cherry-pick, or branch sync outside the full integration workflow. The standalone reference owns the Semantic Merge Record format and the standalone scope boundary.

All modes walk the §Semantic Coherence Checklist below as the shared gated checklist.

## Shared Steps

The following steps are shared by all modes.

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

Run the sync operation only after intent investigation. Resolve by the plan from Step 3. Preserve base-current deletions and relocations by default; restore branch-side content only when current-branch intent, an approved task objective, or a logged user decision justifies it.

**Land one merge commit plus N propagation commits as needed to reach semantic coherence.** Every commit must leave the tree passing **existing protection** — drift tests and key-result coverage established in `integration-workflow` Protect when in workflow mode, or existing tests and drift tests when standalone. Protection-pass is the per-commit lower bound, not the whole-mode stopping rule: the whole-mode stopping rule is §Semantic Coherence Checklist §Scope boundary below.

Include the conflict resolution, resolved docs, and the mode-specific handoff artifact (Sync Map + task-local Sync impact in workflow mode; `SEMANTIC_MERGE.md` merge record in standalone mode) with the commits that produce them. Broader **codebase-coherence** work — fitting the resulting code into the host project's naming conventions, reusing utilities, keeping the PR-friendly diff, walking up project docs, minimizing net diff against the host — is out of scope for this skill. Handoff artifacts may record context that explains the post-sync diff for later codebase review; they do not carry unresolved semantic-merge work into Integrate.

### 6. Detect and resolve stale references

Run more than a "no conflict markers" check. Before returning, sweep for stale references the merge may have left behind and **resolve those that live within the merge's semantic reach** — fixing them is part of semantic coherence and belongs to this skill:

- labels, identifiers, or variable names renamed on one side but still used on the other,
- paths or module locations moved on one side,
- docs and comments that reference the old shape,
- generated outputs that should have been regenerated,
- cross-file imports, registry entries, or config keys.

Run targeted checks for touched subsystems where cheap and relevant. Fix stale references that follow directly from the merge itself (a renamed symbol still used at its old call sites, a moved path referenced by a doc that describes the merged code, a generated output the merged sources made stale). Defer broader codebase-fit work — wider convention alignment, utility reuse, diff minimization — to `refactor-and-integrate`. Confirm the tree matches the integrated intent, not just a conflict-free state.

## Semantic Coherence Checklist

Shared gated checklist. All modes walk it: the implementer as pre-handoff self-check, the reviewer as verification. It defines when semantic-merge is done — the merge's meaning is fully represented in the tree. Walk every item. `[BLOCKING]` items must be satisfied for the sync to be accepted; `[ADVISORY]` items may be flagged without blocking.

**Intent preservation:**

- `[BLOCKING]` Incoming intent understood from commits, diffs, docs, and caller context.
- `[BLOCKING]` Governing baseline and direction identified before conflict resolution.
- `[BLOCKING]` Each overlapping cluster classified by role (behavior/API, data/schema, docs/narrative, generated outputs, tests, config/build) before resolution.
- `[BLOCKING]` No silent losses from either side; dropped hunks have a documented rationale.
- `[BLOCKING]` No silent restorations of base-current deletions or relocations in workflow Sync.
- `[ADVISORY]` Synthesized changes are coherent and minimal.

**Scope boundary (semantic coherence stopping rule):**

- `[BLOCKING]` Stale references within the merge's semantic reach are resolved — renamed symbols at old call sites, moved paths referenced by docs describing the merged code, and other follow-through edits the merge itself forced.
- `[BLOCKING]` Generated outputs made stale by the merged sources are regenerated, or — when regeneration would change a meaningful result — escalated per the intent-changing-escalation step and recorded in the handoff artifact.
- `[BLOCKING]` Docs and comments that describe the merged code are updated to match.
- `[BLOCKING]` No conflict markers remain in the tree (also checked in Verification below).
- `[BLOCKING]` Existing protection passes on every commit landed by this skill — drift tests + key-result coverage in workflow mode; existing tests + drift tests in standalone mode. Per-commit protection-pass is the lower bound; semantic coherence is the stopping rule.
- `[BLOCKING]` Broader **codebase-coherence** work — convention fit, utility reuse, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff against the host — is left to `refactor-and-integrate` (or the caller). Handoff artifacts may explain codebase-review context, but they do not define unresolved semantic-sync targets.

**Intent integrity:**

- `[BLOCKING]` Intent-changing choices were escalated, logged per `handoff-doc §User Decisions Log`, and implemented as stated.
- `[BLOCKING]` Data-discipline artifacts and drift tests were preserved.
- `[BLOCKING]` Meaningful result changes were not silently accepted or re-expected.

**Handoff docs and merge records:**

- `[BLOCKING]` PLAN.md and RESULTS.md remain coherent after the sync when present.
- `[BLOCKING]` Task-structure changes were routed through `planning-workflow §User Feedback and Changing Plans` before adaptation proceeded.
- `[BLOCKING]` Affected task blocks have task-local `**Sync impact:**` annotations when workflow Sync leaves task-specific context needed to understand the post-sync diff.
- `[ADVISORY]` Routine handoff-doc conflict resolutions are summarized in the Sync Map.

**Verification:**

- `[BLOCKING]` No conflict markers remain.
- `[BLOCKING]` Stale-reference sweep covered labels, paths, docs, and generated outputs — not just absence of conflict markers.
- `[BLOCKING]` Targeted checks were run or explicitly reported as not applicable.
- `[BLOCKING]` Generated outputs made stale by the merge were regenerated within this skill's commit chain, or — when regeneration would change a meaningful result — escalated per Step 4 above and recorded in the handoff artifact. Regeneration within the merge's semantic reach is not deferred.
- `[BLOCKING]` Dirty-state stash (when used) was reported in the status return so the user can restore it.

## Exception

Orchestrator-managed parallel worktrees bypass this skill. Branches matching `<branch>/parallel/<slug>` merge with plain `git merge --no-ff`; the merge-guard hook exempts `*/parallel/*` source refs.
