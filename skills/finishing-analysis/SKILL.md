---
name: finishing-analysis
description: Invoked by execution-workflow Step 4 when the user has chosen Option 1 (merge locally) or Option 2 (push + PR). Runs integration-workflow first (drift tests, refactor, report, dev doc handling), then executes the merge or PR mechanics. Assumes reproducibility is already verified by execution-workflow. Will be split into integration-workflow + merge-workflow in the next phase of the restructure.
---

# Finishing Analysis

## Overview

Transitional skill that invokes integration-workflow then performs the merge/PR mechanics. Reproducibility verification, base branch detection, and the 4-option menu are owned by `superRA:execution-workflow` Step 4 and have already happened by the time this skill runs.

**Core principle:** Run integration-workflow → Execute the merge/PR mechanics chosen by the user → Clean up worktree.

**Announce at start:** "I'm using the finishing-analysis skill to complete this work."

**Agent Teams cleanup:** If an Analysis Team is still active from execution-workflow, shut down all teammates and clean up the team before proceeding. The integration-workflow may need to spawn its own team, and only one team can exist per session.

## The Process

This skill is invoked by `superRA:execution-workflow` Step 4 only when the user has chosen Option 1 (merge) or Option 2 (PR). Reproducibility, base branch, and the option menu are handled by execution-workflow before this skill runs — assume the analysis is verified and the user has chosen merge/PR. If you find yourself running reproducibility checks here, something is wrong: stop and consult execution-workflow instead.

### Step 4: Execute Choice

#### Option 1 or 2: Keep the Work (Merge or PR)

When the user chooses to keep the work, run the integration workflow first:

**Step 4a: Integration Workflow**

```
Invoke superRA:integration-workflow
```

This creates drift tests, refactors code for codebase integration with the refactor-review loop, generates the work-journal report, and handles disposition of `PLAN.md` and `RESULTS_UPDATE.md`. See that skill for details.

Only proceed to Step 4d after `superRA:integration-workflow` returns successfully.

**Step 4d: Execute Merge or PR**

**For Option 1 (Merge Locally):**

First, update the analysis branch from the base branch using semantic merge:

```
Invoke superRA:semantic-merge to merge <base-branch> into <analysis-branch>
```

The semantic merge skill classifies conflicts by research impact, escalates research-meaningful decisions to the user, and uses a two-commit integration structure. After semantic merge completes and drift tests pass:

```bash
git checkout <base-branch>
git pull
git merge <analysis-branch>  # Should be fast-forward after branch update
```

Note: The merge-guard hook may remind you to use semantic-merge here. This is expected — semantic merge already ran above. Proceed with the fast-forward merge.

Verify pipeline still runs on merged result. Then cleanup worktree.

**For Option 2 (Push and Create PR):**

First, update the analysis branch from the base branch:

```
Invoke superRA:semantic-merge to merge <base-branch> into <analysis-branch>
```

After semantic merge completes, push and create PR:

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
- Drift tests: included in `tests/` (guard key results)
- Code refactored for codebase integration
- Integration review: passed

## Review Checklist
- [ ] Pipeline runs end-to-end
- [ ] Drift tests pass
- [ ] Data descriptions present before all analysis operations
- [ ] Row counts logged for all sample-changing operations
EOF
)"
```

Then cleanup worktree.

#### Option 3: Keep As-Is

Report: "Keeping branch <name>. Worktree preserved at <path>."

**Don't cleanup worktree.**

#### Option 4: Discard

**Confirm first:**
```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for exact confirmation. Then cleanup.

### Step 5: Cleanup (if in a worktree)

If working in a worktree:

**For Options 1, 2, 4:**

```bash
git worktree remove <worktree-path>
```

**For Option 3:** Keep worktree.

If working on a branch (no worktree): skip this step.

## Quick Reference

| Option | Pre-Merge Gate | Report | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|---------------|--------|-------|------|---------------|----------------|
| 1. Merge locally | Yes | Yes | Yes | - | - | Yes |
| 2. Create PR | Yes | Yes | - | Yes | Yes | - |
| 3. Keep as-is | - | - | - | - | Yes | - |
| 4. Discard | - | - | - | - | - | Yes (force) |

## Common Mistakes

**Skipping integration-workflow**
- **Problem:** Code merged without drift tests or integration review
- **Fix:** Always run integration-workflow for Options 1 and 2

**Skipping reproducibility verification**
- **Problem:** Report references ad-hoc outputs that can't be regenerated
- **Fix:** Always verify pipeline runs and outputs match committed code

**No pipeline file**
- **Problem:** Multiple scripts but no way to run them in order
- **Fix:** Create pipeline file before finishing (reproducibility requirement)

**Report with speculation**
- **Problem:** "This suggests the market is efficient" — unsupported interpretation
- **Fix:** Report only what was done and found. The researcher interprets.

**Stale plan file**
- **Problem:** Plan doesn't reflect what actually happened
- **Fix:** Update plan with all results and discovery notes before finishing

## Red Flags

**Never:**
- Offer completion options without reproducibility verification
- Skip integration-workflow for merge/PR options
- Skip report generation
- Merge without verifying pipeline on merged result
- Delete work without confirmation
- Write reports with unsupported interpretations
- Judge methodology in the report — the researcher decides methodology

**Always:**
- Verify all code committed
- Verify pipeline runs end-to-end
- Run integration-workflow before merge/PR
- Generate factual report with citations
- Present exactly 4 options
- Get typed confirmation for Option 4

## Integration

**Called by:**
- **superRA:execution-workflow** (after all tasks) — After all tasks complete and reviewed

**Invokes:**
- **superRA:integration-workflow** — REQUIRED for Options 1 and 2 (creates drift tests, refactors, reviews integration)
- **superRA:semantic-merge** — REQUIRED for Options 1 and 2 (intent-based branch integration in Step 4d)

**Pairs with:**
- **superRA:using-analysis-worktrees** — Cleans up worktree created by that skill
