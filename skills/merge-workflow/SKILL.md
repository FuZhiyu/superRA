---
name: merge-workflow
description: Use after `integration-workflow` has produced a merge-ready branch (drift tests committed, refactor approved, all docs finalized via the doc-writer + doc-reviewer pair, PLAN.md disposed) and you need to update the analysis branch with main, verify results survived the update, and land the work via local merge or PR; when an analysis branch is behind main and about to be finished; when you need a post-merge safety check (drift tests + integration review against the merged state); when cleaning up a worktree after merge completion. Triggers include "merge this back", "open the PR", "sync with main and merge", "finish this analysis", or the transition from `integration-workflow` completing successfully. Sits at the INTEGRATE phase, step 2 of 2 — the final phase of the superRA workflow.
---

# Merge Workflow

Workflow skill for the **MERGE** phase of the superRA workflow — the final step of finishing an analysis. Owns: pulling main into the analysis branch, post-merge verification (drift tests + integration review), the refactor-review loop on post-merge failures, the actual local merge or PR push, and worktree cleanup.

This is **not** the ad-hoc merge skill. For random `git merge` / `git rebase` / `git cherry-pick` outside the analysis-finishing flow, the merge-guard hook directs callers at `superRA:semantic-merge` directly.

**Relationship to `semantic-merge`:** merge-workflow **delegates** the base-branch-into-analysis-branch update in Step 1 to `superRA:semantic-merge` via an explicit Skill invocation — you call it, wait for it to return, and then continue with Step 2. semantic-merge owns the tier classification and conflict resolution for that update; merge-workflow owns the outer choreography (post-merge drift tests + fresh integration review + refactor loop + the actual local merge or PR push + cleanup) that sits on either side of the semantic-merge call.

**Core principle:** Update with main → drift tests + integration review on the merged state → re-enter refactor-review loop on either failure → execute the actual merge or PR → clean up.

**Announce at start:** "I'm using the merge-workflow skill to integrate this work into main."

## When This Skill Runs

merge-workflow is invoked by `superRA:execution-workflow` Step 4 (Option 1 or 2) after `superRA:integration-workflow` has returned successfully. By the time this skill starts:

- Drift tests have been created, reviewed, and committed (integration-workflow Stage 1)
- Code has been refactored for codebase fit and integration-reviewer-approved (integration-workflow Stage 2)
- `RESULTS.md` has been matured into its permanent form at `RESULTS_DIR` via the doc-writer + doc-reviewer pair (integration-workflow Step 3 sub-part A); project-level docs (CLAUDE.md / AGENTS.md / README.md) have been audited during Stage 2 per `refactor-and-integrate/references/codebase-integration.md` §Project Doc Audit
- `PLAN.md` has been disposed of (integration-workflow Step 3 sub-part C)
- The user has chosen Option 1 (merge locally) or Option 2 (push + PR) — execution-workflow Step 4 captured this choice

If any of those preconditions are missing, stop and consult integration-workflow / execution-workflow rather than proceeding.

## The Process

1. **Step 1** — Update analysis branch with main by invoking `superRA:semantic-merge` (delegated mode). It returns a tier classification and an incoming-impact line.
2. **Step 2** — Post-merge verification:
   - **2.0** Read tier + incoming-impact to decide 2b eligibility.
   - **2a** Run drift tests on the merged state.
   - **2b** If not skippable (anything other than Tier 1 with no analysis-path changes) → dispatch a fresh integration reviewer. If skippable → skip 2b and document the skip in the merge commit (2c).
   - If drift tests fail OR the integration reviewer returns non-APPROVE → re-enter the integration-workflow Stage 2 refactor-review loop, then return to 2a.
3. **Step 3** — Execute local merge OR push + create PR.
4. **Step 4** — Cleanup worktree.

### Step 1: Update Analysis Branch with Main

Bring the latest `main` (or whichever base branch the user is targeting) into the analysis branch by explicitly delegating to `superRA:semantic-merge` **in delegated mode** — this skill owns the post-merge drift tests + integration review in Step 2, so semantic-merge should NOT re-run them:

```
Invoke Skill `superRA:semantic-merge` with the task:
  "merge <base-branch> into <analysis-branch> — delegated mode: skip post-merge drift tests and pipeline run; the caller will verify"
```

This is a real Skill invocation, not a metaphor — load semantic-merge via the Skill tool and hand control to it. semantic-merge classifies conflicts by research impact (Tier 1/2/3), escalates research-meaningful decisions to the user, and uses a two-commit integration structure (mechanical resolution + integration commit). **Wait for it to return successfully** before proceeding to Step 2.

semantic-merge's return contract in delegated mode (see `superRA:semantic-merge` §What to Report — delegated mode) carries:
- **Tier classification** (`Tier 1` / `Tier 2` / `Tier 3`) and a one-sentence rationale.
- **Incoming impact** — one line naming which paths the incoming diff touched, specifically whether any analysis-path file was changed.

Both are load-bearing: Step 2 sub-step 2.0 reads them to decide whether Step 2b (fresh integration review) can be skipped.

Note: the merge-guard hook may fire here reminding you to use semantic-merge. That is expected — you just did. Continue.

### Step 2: Post-Merge Verification

The merge with main may have introduced drift in your results (subtle interactions with main's code) or violated codebase conventions that have moved since integration-workflow ran. Both signals matter in the general case, but when semantic-merge returned Tier 1 AND the incoming diff did not touch any analysis-path file, Step 2b is provably redundant and is skipped.

**2.0. Read semantic-merge's return contract.** From Step 1's return, extract:
- The tier classification (`Tier 1` / `Tier 2` / `Tier 3`).
- The incoming-impact line naming which paths the incoming diff touched.

Decide Step 2b eligibility:
- **Tier 1 AND no analysis-path changes in the incoming diff** → skip 2b. Run 2a only. Record the skip in the merge commit (see 2c).
- **Otherwise** (Tier 2, Tier 3, or Tier 1 with analysis-path changes) → run 2a AND 2b both. This is the default and covers every case where main moved code that your analysis depends on, renamed a utility you import, or introduced conflicts that resolved cleanly but may still have shifted intent.

"Analysis paths" = every directory your analysis code lives in, as identified during `integration-workflow`. When in doubt, do not skip — 2b is cheap insurance compared to shipping integration drift.

**2a. Run drift tests on the merged state.** (Always.)
```bash
# Use whatever the project's test runner is
pytest tests/  # or: julia --project test/runtests.jl
```
- **Pass:** drift tests still guard your results after the merge. Proceed to 2b (or to 2c if 2b was skipped at 2.0).
- **Fail:** either the merge changed your results or the test environment moved. Skip directly to Step 3 (refactor-review loop).

**2b. Dispatch a fresh integration reviewer on the merged state.** Skip this sub-step only if 2.0 said so.
```
Agent(subagent_type: "superRA:reviewer"):
  Stage: integration
  Task: post-merge integration review on the merged state
  Git range: <merge-base>..HEAD  # the merged state vs the base branch tip

  Follow the standard stage-relevant workflow and load
    relevant skills and documents to proceed. Additionally, this is a
    post-merge review — verify the merge didn't break codebase fit
    (convention drift, renamed utilities, moved files, stale imports).
```

- **APPROVE:** drift tests passed AND integration is clean. Proceed to Step 4.
- **REVISE:** integration broke during the merge. Adjudicate the reviewer's feedback per the orchestrator discipline in `superRA:agent-orchestration` §Handling Reviewer Feedback. For accepted issues, proceed to Step 3.

**2c. If 2b was skipped, document the skip in the merge commit.** When the user chooses Option 1 in Step 4, the merge commit message gets this trailer:

```
Post-merge integration review skipped: Tier 1 clean merge, no
analysis-path changes incoming.
```

For Option 2 (PR), include the same sentence under "Pre-Merge Quality" in the PR body so the skip is auditable at review time. The skip saves a dispatch cycle when it is safe; the trailer makes the saving visible.

### Step 3: Refactor-Review Loop on Post-Merge Failure

When drift tests fail OR the post-merge integration reviewer returns REVISE, re-enter the same refactor-review loop that integration-workflow Stage 2 uses. The machinery is identical — only the trigger changed.

1. **Dispatch refactorer:**
   ```
   Agent(subagent_type: "superRA:implementer"):
     Stage: integration
     Task: post-merge refactoring — address integration reviewer's accepted findings on the merged state

     Follow the standard stage-relevant workflow and load
       relevant skills and documents to proceed. Additionally, this is
       post-merge refactoring — main has moved since integration-workflow
       ran; address the drift introduced by the merge.
   ```

2. **After refactoring, re-run drift tests.**
   - **Pass:** commit refactored code and re-dispatch the integration reviewer (back to Step 2b).
   - **Fail with minor variation** (rounding, floating-point): update test expectation with a comment explaining the post-merge cause, commit, re-dispatch reviewer.
   - **Fail with meaningful drift** (results changed substantively): STOP. Show the user before/after values from the merge. The merge changed something material; this is not a refactoring problem — it is a research conversation. Wait for instructions.

3. **Iterate until both drift tests pass AND integration reviewer APPROVES.**

The orchestrator discipline applies: read each cited issue yourself before forwarding to the refactorer, override with documented reasoning if the reviewer is wrong, and never silently dismiss CRITICAL findings. See `superRA:agent-orchestration` §Handling Reviewer Feedback for the full protocol.

### Step 4: Execute Merge or PR

Once Step 2 returns clean, execute the user's choice from execution-workflow Step 4.

**For Option 1 (Merge Locally):**

```bash
git checkout <base-branch>
git pull
git merge <analysis-branch>  # Should be fast-forward after the Step 1 update
```

If Step 2b was skipped at Step 2.0, append the skip trailer to the merge commit (amend before pushing, or include it in the `-m` for a non-fast-forward merge):

```
Post-merge integration review skipped: Tier 1 clean merge, no
analysis-path changes incoming.
```

Verify the pipeline still runs on the merged result:

```bash
bash run_all.sh  # or: julia pipeline.jl
```

If it fails on the merged result, something happened between Step 2 and now. Stop and investigate.

**For Option 2 (Push and Create PR):**

```bash
git push -u origin <analysis-branch>

gh pr create --title "<title>" --body "$(cat <<'EOF'
## Analysis Summary
<2-3 bullets of what was analyzed and key findings>

## Data
<Key datasets used, sample period, observation counts>

## Reproducibility
- Pipeline file: `run_all.sh` (or equivalent)
- All outputs generated from committed code
- Report: `<path-to-report>`

## Pre-Merge Quality
- Drift tests: included in `tests/` (guard key results); passed on merged state
- Code refactored for codebase integration
- Integration review: passed pre-merge; post-merge review run [OR: skipped per Step 2.0 — Tier 1 clean merge, no analysis-path changes incoming]

## Review Checklist
- [ ] Pipeline runs end-to-end
- [ ] Drift tests pass on merged state
- [ ] Data descriptions present before all analysis operations
- [ ] Row counts logged for all sample-changing operations
EOF
)"
```

### Step 5: Cleanup Worktree

If the analysis was done in a git worktree, invoke `superRA:worktree-data-sync` §Cleanup for the teardown ritual. If the analysis was done on a feature branch without a worktree, skip this step.

Report what was merged/pushed and what was cleaned up.

## Agent Teams Mode

When Agent Teams are available (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`), merge-workflow can be orchestrated as a team instead of sequential subagent dispatches — direct iteration between merge-proposer/merge-reviewer and post-merge-refactorer/post-merge-integration-reviewer without the orchestrator relaying feedback. See `superRA:agent-orchestration` §Integration and `references/agent-teams.md` for spawn mechanics. Composition is derived from the manifest — one teammate per stage this workflow runs.

The lead still handles the user-facing meaningful-drift escalation (Step 3), executes Step 4 (local merge or PR push) outside the team, executes Step 5 (worktree cleanup) outside the team, and cleans up the team after final APPROVE. Spawn the Merge Team only after the Integration Team has been cleaned up — both share the session's team slot.

## Why Both Drift Tests AND Integration Review Post-Merge — and when one is redundant

The two signals cover different failure modes:

- **Drift tests** guard your *results*. If main's changes interact with your analysis in a way that shifts a coefficient, drift tests catch it. They cannot catch convention drift (renamed utility functions, moved files, stale imports) because those don't change numerical results.
- **Integration reviewer** guards your *integration into the codebase*. If main renamed a utility you imported, drift tests still pass but the code is now stylistically broken. The integration reviewer catches it.

Together they cover both failure modes. The default is to run BOTH — skipping is the exception.

**When the integration reviewer is provably redundant.** If semantic-merge returned Tier 1 (clean merge, no conflicts of any kind) AND the incoming diff did not touch any analysis-path file, there is no surface for convention drift on your code: main touched only files your analysis does not import or execute. In that case, drift tests alone carry both signals — results unchanged (the tests would catch it) and integration unchanged (the incoming diff did not reach your paths). Step 2 sub-step 2.0 codifies this as a skip condition; 2c documents the skip in the merge commit so the audit trail shows why Step 2b did not run.

The refactor-review loop in Step 3 reuses integration-workflow Stage 2 verbatim — there is no new machinery here, just a second invocation site for the same loop. The loop triggers when either 2a fails OR (when 2b runs) the reviewer returns REVISE.

## Red Flags

**Never:**
- Push or local-merge without running drift tests (2a) on the merged state — 2a runs in every case
- Skip Step 2b on anything other than Tier 1 clean merges with no analysis-path changes incoming — 2.0's skip condition is tight for a reason
- Silently swallow integration-reviewer REVISE on the merged state — adjudicate per the orchestrator discipline in `superRA:agent-orchestration` §Handling Reviewer Feedback, then either fix or document the override
- Skip Step 1 (the semantic-merge update) and go straight to git merge — main may have moved since integration-workflow ran
- Invoke semantic-merge in its default (standalone) mode — delegated mode is load-bearing, because merge-workflow Step 2 owns the post-merge drift-test and integration-review re-runs
- Cleanup the worktree before the merge or push has actually completed

**Always:**
- Run semantic-merge in delegated mode for the main update (tier classification handles conflicts properly; the delegated return contract enables Step 2's skip logic)
- Run drift tests (2a) post-merge unconditionally
- Run integration reviewer (2b) post-merge unless 2.0's skip condition is met; document the skip in the merge commit / PR body per 2c when skipped
- Re-enter the refactor-review loop on any post-merge failure
- Stop and ask the researcher via `AskUserQuestion` (plain text if unavailable) when post-merge drift indicates meaningful result changes; log the answer in `PLAN.md` per `handoff-doc` §User Decisions Log before acting on it
- Report what was merged and what was cleaned up

**Drift-test integrity on the merged state is governed by the cross-cutting rules in `refactor-and-integrate` reference `drift-test-quality.md` — failing drift tests after the main update must be adjudicated, not silently re-expected. Load the reference before running post-merge tests.**

## Integration

**Called by:**
- **superRA:execution-workflow** Step 4 (Option 1 or 2) — Directly, after dispatching `superRA:integration-workflow` first

**Invokes:**
- **superRA:semantic-merge** — REQUIRED for the main update in Step 1 (tier classification + conflict resolution)
- **superRA:integration-workflow** (via the post-merge refactor-review loop) — Reuses Stage 2 machinery for refactor + review

**Pairs with:**
- **superRA:worktree-data-sync** — §Cleanup ritual for the worktree created by that skill at planning time
