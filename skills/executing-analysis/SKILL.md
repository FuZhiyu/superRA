---
name: executing-analysis
description: Use when you have a written analysis plan to execute in the current session with data-first discipline and checkpoint commits
---

# Executing Analysis

## Overview

Load plan, review critically, execute all steps with data-first discipline, checkpoint after each step, report when complete.

**Announce at start:** "I'm using the executing-analysis skill to implement this analysis plan."

**Note:** Tell your human partner that superRA works much better with access to subagents. If subagents are available, use superRA:subagent-driven-analysis instead of this skill.

## The Process

### Step 1: Load and Review Plan

1. Read `PLAN.md` and `RESULTS_UPDATE.md`
2. Review PLAN.md critically — identify any questions or concerns:
   - Are data sources available and accessible?
   - Are the steps in the right order?
   - Is the pipeline file included (for multi-script analyses)?
3. Review RESULTS_UPDATE.md for context on any completed steps (if resuming)
4. If concerns: Raise them with your human partner before starting
5. If no concerns: Create TodoWrite with all steps and proceed

### Step 2: Execute Steps

For each step in the plan:

1. Mark as in_progress
2. **Follow data-first-analysis discipline:**
   - DESCRIBE: Run diagnostics on input data
   - TRANSFORM: Execute the operation
   - VALIDATE: Check results (row counts, distributions, economic sense)
   - DOCUMENT: Log decisions in jupytext markdown cells
3. **Commit** the work:
   ```bash
   git add <script-files>
   git commit -m "<descriptive message for this step>"
   ```
4. **Update PLAN.md and RESULTS_UPDATE.md:**
   - PLAN.md: Mark step `- [x]` with brief result note. If findings change upcoming steps, update them now. Add discovery notes for the next agent/session.
   - RESULTS_UPDATE.md: Add key findings for this step (row counts, summary stats, figures). Save any figures/tables to `results_attachments/` as PNG.
   ```bash
   git add PLAN.md RESULTS_UPDATE.md results_attachments/
   git commit -m "update plan + results: step N complete"
   ```
5. Mark as completed

**For sensitivity analysis steps:**
- Compare results to baseline (from RESULTS_UPDATE.md) and expected results (from PLAN.md, if provided)
- If a sensitivity check fails: assess **economic significance**, not just statistical significance
- If unsure whether a failure is meaningful: **stop and ask the user**
- Document the assessment in RESULTS_UPDATE.md

### Step 3: Verify Pipeline

After all steps complete:

1. If the analysis has multiple scripts, verify the pipeline file runs end-to-end:
   ```bash
   bash run_all.sh  # or: julia pipeline.jl
   ```
2. Check that all expected outputs exist (tables, figures, logs)
3. Verify outputs are generated from committed code (reproducibility gate)

### Step 4: Complete Analysis

After all steps complete and pipeline verified:
- Announce: "I'm using the finishing-analysis skill to complete this work."
- **REQUIRED SKILL:** Use superRA:finishing-analysis
- Follow that skill to generate report, present merge/PR options

## Plan as Living Document

**The plan evolves as you discover things.** At each checkpoint:

- Mark completed steps with results: `- [x] Step 3: Merged holdings — 4.7M rows, 2% unmatched`
- Update upcoming steps if findings require changes
- Add discovery notes: "Unmatched rate higher than expected — added validation step before regression"

**RESULTS_UPDATE.md evolves alongside PLAN.md.** Together they are the handoff:
- **PLAN.md** = what to do + what changed
- **RESULTS_UPDATE.md** = what was found + figures + key numbers

If the session ends, the next agent reads both and knows: what's done, what was found, what changed, what's next.

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Data description reveals unexpected issues (wrong magnitudes, high missingness)
- Merge produces unexpected row count change
- Validation fails (results don't match economic intuition)
- Plan has critical gaps preventing next step
- Pipeline file is missing and analysis has multiple scripts

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on findings
- Data issues require rethinking the approach

**Don't force through data issues** — stop and investigate.

## Review Scope

**At execution checkpoints:** Focus on data integrity and implementation correctness. Codebase integration review (naming consistency, utility function adoption, code simplification) is deferred to the pre-merge gate, which runs during finishing-analysis when the user chooses to merge or create a PR.

## Remember
- Review plan critically first
- Follow data-first-analysis discipline at every step
- Commit after each step (code + plan update)
- Pipeline must run end-to-end before completion
- Reference skills when plan says to
- Stop when blocked, don't guess
- Never start analysis on main/master branch without explicit user consent

## Integration

**Required workflow skills:**
- **superRA:using-analysis-worktrees** — REQUIRED: Set up isolated workspace before starting
- **superRA:analysis-planning** — Creates the plan this skill executes
- **superRA:data-first-analysis** — REQUIRED: Discipline at every step
- **superRA:finishing-analysis** — Complete work after all steps done
- **superRA:pre-merge-gate** — Code integration and drift tests before merge (invoked by finishing-analysis)
