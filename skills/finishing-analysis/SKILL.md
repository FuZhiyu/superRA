---
name: finishing-analysis
description: Use when analysis implementation is complete and you need to verify reproducibility, generate reports, and decide how to integrate the work - guides completion via merge, PR, or archival
---

# Finishing Analysis

## Overview

Guide completion of analysis work by verifying reproducibility, generating reports, and presenting integration options.

**Core principle:** Verify reproducibility → Generate report → Present options → Execute choice → Clean up.

**Announce at start:** "I'm using the finishing-analysis skill to complete this work."

## The Process

### Step 1: Verify Reproducibility

**Before presenting options, verify the analysis is reproducible:**

1. **All code committed?**
   ```bash
   git status
   ```
   If uncommitted changes exist: commit or ask the user.

2. **Pipeline runs end-to-end?** (for multi-script analyses)
   ```bash
   bash run_all.sh  # or: julia pipeline.jl
   ```
   If no pipeline file exists and there are multiple scripts: create one before proceeding.

3. **Outputs exist and match committed code?**
   Check that key output files (tables, figures, logs) exist and were generated from the current committed code, not ad-hoc runs.

4. **Plan file up to date?**
   All steps marked `- [x]` with result notes? Discovery notes captured? Upcoming steps (if any) reflect current understanding?

5. **RESULTS_UPDATE.md up to date?**
   Has findings for all completed tasks? Figure attachments in `results_attachments/` committed?

**If any check fails:** Fix it before proceeding. Don't offer completion options for unreproducible work.

### Step 1.5: Archive Development Documents

`PLAN.md` and `RESULTS_UPDATE.md` are development artifacts — they cannot remain at project root on the main branch.

**Ask the user:**
```
PLAN.md and RESULTS_UPDATE.md are development documents. Options:
1. Archive to docs/analysis-archive/YYYY-MM-DD-<name>/ (preserves in repo)
2. Delete (git history preserves them on this branch)
Which option?
```

**Option 1 (Archive):**
```bash
mkdir -p docs/analysis-archive/YYYY-MM-DD-<name>
git mv PLAN.md docs/analysis-archive/YYYY-MM-DD-<name>/
git mv RESULTS_UPDATE.md docs/analysis-archive/YYYY-MM-DD-<name>/
git mv results_attachments/ docs/analysis-archive/YYYY-MM-DD-<name>/ 2>/dev/null
git commit -m "archive analysis plan and results"
```

**Option 2 (Delete):**
```bash
git rm PLAN.md RESULTS_UPDATE.md
rm -rf results_attachments/
git add -A results_attachments/ 2>/dev/null
git commit -m "remove development documents (preserved in branch history)"
```

### Step 2: Generate Report

Create a work journal entry documenting the analysis results. Use `RESULTS_UPDATE.md` as source material — the finishing report is the polished version; RESULTS_UPDATE.md was the development log.

**Entry file:** `[WORK_JOURNAL_DIR]/YYYY-MM-DD-[Author]-[Description].md`
- Resolve path from project guidance (AGENTS.md, CLAUDE.md, README)
- Default: `notes/` or `work-journal/`

**Frontmatter:**
```yaml
---
author: "[[Author]]"
date: YYYY-MM-DD
timestamp: "YYYY-MM-DDTHH:MM:SS"
project: "[[ProjectName]]"
git_commit: [current HEAD hash]
git_message: "[latest commit message]"
tags: ["work-journal", "analysis"]
permalink: working-journal/YYYY-MM-DD-author-description
---
```

**Content structure** (flexible, but typically includes):
- Objective
- Data description (sources, sample, key variables)
- Methodology
- Results with tables and figures
- Technical details

**Rules:**
- **Factual and objective** — state what was done and found
- **Every claim cited** — link to code files, output files, or documentation
- **No speculation** — don't interpret economic meaning unless the user explicitly asked
- **Relative paths** — `[descriptive text](relative/path/from/report/to/file)`

**Figure handling:**
- PDF figures → convert to PNG, copy to `attachments/` subdirectory
- Embed with relative paths and cite original source
- ```markdown
  ![Descriptive caption](./attachments/YYYY-MM-DD-description.png)
  Source: [Original](relative/path/to/original/figure.pdf)
  ```

**Report verification** (inline checklist):
- [ ] All claims cited and accurate?
- [ ] Numbers match source files?
- [ ] No speculation or subjective language?
- [ ] Figures copied and cite sources?
- [ ] File paths resolve correctly?

If issues found, fix before finalizing.

### Step 3: Determine Base Branch

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

Or ask: "This branch split from main — is that correct?"

### Step 4: Present Options

Present exactly these 4 options:

```
Analysis complete. Report written to <path>. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

### Step 5: Execute Choice

#### Option 1: Merge Locally

```bash
git checkout <base-branch>
git pull
git merge <analysis-branch>
```

Verify pipeline still runs on merged result. Then cleanup worktree.

#### Option 2: Push and Create PR

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

## Review Checklist
- [ ] Pipeline runs end-to-end
- [ ] Outputs match committed code
- [ ] Data descriptions present before all transformations
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

### Step 6: Cleanup Worktree

**For Options 1, 2, 4:**

```bash
git worktree remove <worktree-path>
```

**For Option 3:** Keep worktree.

## Quick Reference

| Option | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|-------|------|---------------|----------------|
| 1. Merge locally | Yes | - | - | Yes |
| 2. Create PR | - | Yes | Yes | - |
| 3. Keep as-is | - | - | Yes | - |
| 4. Discard | - | - | - | Yes (force) |

## Common Mistakes

**Skipping reproducibility verification**
- **Problem:** Report references ad-hoc outputs that can't be regenerated
- **Fix:** Always verify pipeline runs and outputs match committed code

**No pipeline file**
- **Problem:** Multiple scripts but no way to run them in order
- **Fix:** Create pipeline file before finishing (reproducibility requirement)

**Report with speculation**
- **Problem:** "This suggests the market is efficient" — unsupported interpretation
- **Fix:** Report only what was done and found. User interprets.

**Stale plan file**
- **Problem:** Plan doesn't reflect what actually happened
- **Fix:** Update plan with all results and discovery notes before finishing

## Red Flags

**Never:**
- Offer completion options without reproducibility verification
- Skip report generation
- Merge without verifying pipeline on merged result
- Delete work without confirmation
- Write reports with unsupported interpretations

**Always:**
- Verify all code committed
- Verify pipeline runs end-to-end
- Generate factual report with citations
- Present exactly 4 options
- Get typed confirmation for Option 4

## Integration

**Called by:**
- **subagent-driven-analysis** (after all tasks) — After all tasks complete and reviewed
- **executing-analysis** (after all steps) — After all steps complete

**Pairs with:**
- **using-analysis-worktrees** — Cleans up worktree created by that skill
