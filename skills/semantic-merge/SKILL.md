---
name: semantic-merge
description: "Use when about to run `git merge`, `git rebase`, or `git cherry-pick` on a research branch; when syncing a feature or analysis branch with a current base branch before integration; or when incoming changes may touch results-bearing files, analysis scripts, PLAN.md, RESULTS.md, drift tests, or domain-discipline artifacts. Triggers include: bare `git merge` / `git rebase` / `git cherry-pick` on a research branch (the merge-guard hook flags these automatically), \"sync with main\", \"pull main into this branch\", \"rebase onto main\", \"cherry-pick commit X\", or any branch integration where conflict resolution must preserve research intent. Invoked by `integration-workflow` during Sync via `Stage: sync`; also usable standalone by any agent or human doing a research-aware branch integration."
---

# Semantic Merge

Integrate branches by intent, not by lines. Understand what each side was trying to achieve, synthesize where both changes are valid, escalate research-meaningful decisions to the user, and leave the tree ready for post-sync integration review.

**Core principle:** Treat conflicts as intent conflicts first and line conflicts second. Research-meaningful conflicts always go to the user. The agent implements the researcher's integration decisions; it does not judge methodology.

**Sync boundary:** In `integration-workflow`, semantic-merge owns the **Sync** step only. The sync agent researches incoming intent, resolves conflicts, writes `## Sync Map` when needed, and lands exactly one sync commit. It does not perform broad refactoring, codebase-fit cleanup, generated-output refreshes, drift-test expectation updates, or project-doc audit. Those are post-sync `refactor-and-integrate` responsibilities.

**Exception:** Orchestrator-managed parallel worktrees bypass this skill. Branches matching `<branch>/parallel/<slug>` merge with plain `git merge --no-ff`; the merge-guard hook exempts `*/parallel/*` source refs.

## References

Load `references/sync-quality.md` for the sync-quality checklist, Sync Map format, Tier 3 escalation rules, handoff-doc coherence rules, and verification expectations.

## Process

### 1. Ground in repo state

Before changing anything:

```bash
git status
git branch --show-current
git log --oneline -5
git merge-base HEAD <incoming-ref>
git log --oneline <merge-base>..<incoming-ref>
git diff --name-only <merge-base>..<incoming-ref>
```

If the worktree is dirty, preserve it safely first with a reversible snapshot such as a named stash. Stop and clarify only if the repository is already mid-operation in a way that makes intent ambiguous.

### 2. Identify direction and governing baseline

Every semantic sync has a direction. Identify it before resolving conflicts.

**Integration-workflow Sync call:** use the caller-provided anchors:

- `PRE_SYNC_BASE_SHA` - the pre-sync merge base; use only to research incoming base changes.
- `BASE_HEAD_SHA` - the current base branch head; this becomes the governing post-sync baseline.
- Incoming range: `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`.

For this call path, current base intent is canonical by default. Feature-branch hunks survive only when approved task objectives, logged user decisions, or the Sync Map's post-sync obligations justify them.

**Standalone call:** use the caller-declared governing baseline and direction. If absent, infer only when obvious from the request and repo state; otherwise ask. Prefer syncing the feature branch with the target base first, then finishing with a fast-forward or PR, over directly integrating a stale feature branch into main.

### 3. Understand incoming and current intent

Read commit messages and diffs since the relevant branch point. Classify changes by role:

- **Results-bearing** - analysis scripts, computation pipelines, and output-affecting code.
- **Domain-discipline artifacts** - validation artifacts, row-count logs, drift tests, and domain-specific records.
- **Handoff docs** - PLAN.md and RESULTS.md.
- **Infrastructure** - utilities, build scripts, CI, dependencies.
- **Documentation** - README and non-results docs.
- **Generated outputs** - figures, tables, compiled artifacts, and lockfiles.

Do the same for the current branch if its purpose is not already clear from PLAN.md, RESULTS.md, branch name, commit history, or the caller's instructions.

### 4. Build the Sync Map

For each overlapping area, decide one of:

- keep incoming behavior
- keep current-branch behavior
- synthesize both
- regenerate derived artifacts later
- ask the user

Prefer synthesis when both changes are valid and compatible. Prefer regeneration over manual editing for generated files.

Write `## Sync Map` in PLAN.md when there is material overlap, a conflict, a user decision, or a post-sync obligation. If PLAN.md is absent, put the same information in the sync commit body. If the sync is trivial and creates no obligations, a concise commit message and status return are enough.

### 5. Ask the user when the semantic choice is not discoverable

Ask when:

- two semantic integrations are both reasonable
- incoming and current changes point toward different valid research goals, methodology choices, scope decisions, or result interpretations
- incoming and current changes point in opposite architectural directions
- PLAN.md / RESULTS.md conflicts imply task add/remove/combine, DAG changes, or APPROVED status invalidation

Present ambiguity in terms of intent and consequences, not raw diff chunks. Log every user decision per `handoff-doc` §User Decisions Log before committing the resolution. If PLAN.md is absent, record the decision in the sync commit message.

### 6. Land the sync commit

When called by integration-workflow:

- Land exactly one sync commit when the base has advanced.
- Resolve conflicts with the lowest-assumption reconciliation that preserves information and restores a coherent tree.
- Keep post-sync obligations in `## Sync Map`; do not perform the downstream refactor work inside the sync commit.
- If no sync is needed because `BASE_HEAD_SHA` is already an ancestor of `HEAD`, report a no-op.

For standalone merge, rebase, or cherry-pick requests, preserve the same intent separation. Land incoming changes cleanly first; make dedicated adaptation commits only when the caller explicitly asks for standalone full integration rather than sync-only.

### 7. Verify and report

Verify the synced tree is coherent:

- no conflict markers remain
- touched subsystems pass targeted checks where cheap and relevant
- handoff docs are syntactically coherent
- generated artifacts are either regenerated or recorded as post-sync obligations

Run drift tests when this skill is used standalone and the branch has them. In integration-workflow, the caller owns the full drift-test and integration-review pass after Sync.

Report:

- governing baseline and direction
- incoming objective
- what the sync commit kept, dropped, or synthesized
- Sync Map location or why none was needed
- user decisions asked and logged
- checks run and post-sync obligations

## Red Flags

**Never:**
- Run bare `git merge`, `git rebase`, or `git cherry-pick` on a research branch without inspecting incoming intent first.
- Choose `--ours` or `--theirs` for results-bearing files without a documented semantic rationale or user decision.
- Resolve methodology, sample, variable-definition, or result conflicts without the researcher.
- Judge the researcher's methodology.
- Discard dirty worktree state without explicit approval.
- Silently update drift-test expectations after a meaningful result change.
- Restore base-deleted or base-relocated content without an approved objective, logged user decision, or Sync Map obligation.

**Always:**
- Identify the governing baseline and direction before resolving conflicts.
- Understand incoming intent before editing conflict regions.
- Use `## Sync Map` or the sync commit body to carry post-sync obligations.
- Escalate research-meaningful conflicts with intent and consequences.
- Preserve and re-validate domain-discipline artifacts through the sync.
- Log every user decision per `handoff-doc` §User Decisions Log.
