---
name: semantic-merge
description: "Use when about to run `git merge`, `git rebase`, or `git cherry-pick` on a research branch — or any time incoming changes from another branch may touch results-bearing files, analysis scripts, PLAN.md, RESULTS.md, drift tests, or domain-discipline artifacts — and you want thoughtful, research-aware conflict resolution rather than mechanical ours/theirs. Triggers include: bare `git merge` / `git rebase` / `git cherry-pick` on a research branch (the merge-guard hook flags these automatically), \"pull main into this branch\", \"rebase onto main\", \"cherry-pick commit X\", or any merge where at least one hunk touches a results-bearing file. Invoked by `integration-workflow` Phase B Step 3 mechanical-merge commit when conflicts or material main-side changes exist; also usable standalone by any agent or human doing a research-aware merge."
---

# Semantic Merge

Integrate branches by intent, not by lines. Understand what each side was trying to achieve, synthesize where both changes are valid, escalate research-meaningful decisions to the user, and verify the integrated result.

**Core principle:** Treat conflicts as intent conflicts first and line conflicts second. Research-meaningful conflicts always go to the user. The agent implements the researcher's integration decisions — never judges methodology.

**Upstream-intent rule:** Identify the governing upstream intent before changing files. In Phase B, use the active `## Upstream Intent` section in `PLAN.md` when the reviewer recorded one for the current round, plus any relevant task-local review notes. Otherwise use the caller-supplied upstream-intent context for the incoming objective and allowed deltas. Preserve base intent by default: the merged tree should match the base branch unless approved task objectives or the recorded contract explicitly authorize a surviving branch-side delta. Upstream deletions and relocations stay deleted or relocated unless the recorded contract says otherwise.

**Exception — orchestrator-managed parallel worktrees bypass this skill.** Branches matching `<branch>/parallel/<slug>` merge with plain `git merge --no-ff` (the `merge-guard` hook exempts `*/parallel/*` source refs).

## The Process

### Step 1: Ground in repo state

Before changing anything:

```bash
git status
git branch --show-current
git log --oneline -5

MERGE_BASE=$(git merge-base HEAD <incoming-branch>)
git log --oneline $MERGE_BASE..<incoming-branch>
git diff --name-only $MERGE_BASE..<incoming-branch>
```

If the worktree is dirty, preserve it safely first:

```bash
git stash push -m "pre-merge snapshot"
```

Stop and clarify only if the repository is already mid-operation in a way that makes intent ambiguous.

### Step 2: Understand incoming intent

Read commit messages and diffs since the merge base. Classify changes by role:

- **Results-bearing** — domain analysis scripts, computation pipelines, anything that affects outputs
- **Domain-discipline artifacts** — validation artifacts the domain skill requires (e.g. for data analysis: describe steps, row-count logs, validation checks); drift tests
- **Handoff docs** — PLAN.md, RESULTS.md (conflicting edits to these may imply structural reorganization — see below)
- **Infrastructure** — utilities, build scripts, CI config
- **Documentation** — README, non-results docs
- **Generated outputs** — compiled artifacts, figures, tables that should be regenerated from merged sources

Do the same for the current branch if its purpose is not already obvious.

If `PLAN.md` has an active `## Upstream Intent` section for this Phase B round, read it now before building the integration map. Otherwise read the caller-supplied upstream-intent context now. Use that source as the authority for what survives.

### Step 3: Build an integration map

For each overlapping area, decide one of:

- keep incoming behavior
- keep current-branch behavior
- synthesize both
- regenerate derived artifacts from merged sources
- ask the user

Prefer synthesis over picking sides when both changes are valid and compatible. Prefer regeneration over manual editing for generated files.

Base intent wins unless an approved task objective or reviewer-recorded allowed delta says the current branch has earned a surviving hunk.

**PLAN.md / RESULTS.md conflicts** require extra care: a conflict here may indicate that the incoming branch reorganized a task, removed a section, or changed research scope. If the conflict implies a substantive restructure of the analysis plan, escalate to `planning-workflow §User Feedback and Changing Plans` rather than resolving it as a line conflict. The researcher decides — the agent proposes.

### Step 4: Ask the user when the semantic choice is not discoverable

Ask when:

- two different semantic integrations are both reasonable
- the incoming and current changes point toward different valid research goals, methodological choices, or scope decisions (e.g. scope-defining variables, key model specifications, data sources, research conclusions)
- incoming and current changes point in opposite architectural directions
- a PLAN.md conflict implies a substantive restructure of scope or task ordering

Do not ask for conflicts that can be resolved by inspecting the repo, commit range, tests, or docs.

**Present ambiguity in terms of intent and consequences**, not raw diff chunks:
- Bad: "Lines 42-58 conflict between HEAD and incoming"
- Good: "Incoming changes redefine how the outcome variable is constructed. Your branch uses this in the main analysis. Keep yours / adopt theirs / investigate impact?"

**Log every user decision** per `handoff-doc §User Decisions Log` and include the log entry in the commit that implements it. If PLAN.md is absent, record the decision in the merge commit message instead — the commit message is the record of record once the doc is gone.

### Step 5: Resolve conflicts and integrate

A common workflow: one **mechanical merge commit** (lowest-assumption reconciliation that preserves information and restores a coherent tree) followed by one or more **integration commits** (adapt code, docs, tests, and generated artifacts so the branch meaningfully incorporates the incoming objective — rewrite stale names, paths, and references; regenerate derived outputs from merged sources).

This 1+N shape is **one possible workflow**, not mandatory. Callers may collapse to a single commit when adaptation is trivial, or may split integration work into parallel commits across independent task areas.

If rebase or cherry-pick is required instead of merge, preserve the same conceptual separation: land incoming changes cleanly first, then make a dedicated integration commit unless the user explicitly wants one combined commit.

### Step 6: Verify the integrated result

- Run targeted checks for touched subsystems.
- Run drift tests if the branch has them. Load `refactor-and-integrate/references/drift-test-quality.md` before running — failing drift tests after a merge must be adjudicated (present before/after values, assess significance, stop for user decision on meaningful drift), never silently re-expected. Failing tests that are purely mechanical (a path rename, a renamed function with identical behavior) may be updated with a documented reason.
- Search for stale references, outdated labels, old paths, inconsistent docs, and generated outputs that should have been regenerated.
- Confirm the final tree reflects the integrated intent, not just a conflict-free state.

When called from a pipeline whose caller runs drift tests and post-merge verification (e.g., `integration-workflow` Phase B Step 3), complete the merge and report back — do not duplicate the caller's verification pass.

## What to Report

When the integration is complete, summarize:

- The incoming branch's objective
- How it interacted with the current branch's work
- What was kept from each side, what was synthesized or regenerated
- What questions were asked (and the user's answers) because intent was unclear
- Drift test and verification results

## Red Flags

**Never:**
- Run bare `git merge` without inspecting incoming intent first on a research branch
- Choose `--ours` or `--theirs` for results-bearing files without user input
- Resolve domain-discipline conflicts without presenting options to the user
- Judge the researcher's methodology — you integrate; you do not evaluate
- Discard dirty worktree state without explicit approval
- Silently update drift-test expectations after a meaningful result change
- Restore upstream-deleted or relocated content without an explicit allowed delta in the governing upstream-intent contract

**Always:**
- Understand incoming intent before resolving conflicts
- Prefer synthesis over picking sides when both changes are valid
- Use the governing upstream-intent source as the authority for what survives. In Phase B, that source is `## Upstream Intent`
- Escalate research-meaningful conflicts to the user with intent and consequences, not raw diffs
- Run drift tests on the merged result when the branch has them (unless the caller, e.g. `integration-workflow` Phase B, owns that verification pass)
- Preserve and re-validate domain-discipline artifacts through the merge
- Log every user decision per `handoff-doc §User Decisions Log`

**References:**
- **semantic-merge-integration** (global skill, `~/.claude/skills/semantic-merge-integration/SKILL.md`) — General-purpose merge philosophy that this skill extends for research contexts
