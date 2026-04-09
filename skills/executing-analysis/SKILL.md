---
name: executing-analysis
description: Use when you have a written analysis plan to execute in the current session with data-first discipline and checkpoint commits
---

# Executing Analysis

## Overview

Load plan, review critically, execute all steps with data-first discipline, checkpoint after each step, report when complete.

**Announce at start:** "I'm using the executing-analysis skill to implement this analysis plan."

**Note:** Tell your human partner that econ-superpowers works much better with access to subagents. If subagents are available, use econ-superpowers:subagent-driven-analysis instead of this skill.

## The Process

### Step 1: Load and Review Plan

1. Read plan file
2. Review critically — identify any questions or concerns:
   - Are data sources available and accessible?
   - Are the steps in the right order?
   - Is the pipeline file included (for multi-script analyses)?
3. If concerns: Raise them with your human partner before starting
4. If no concerns: Create TodoWrite with all steps and proceed

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
4. **Update the plan file:**
   - Mark step `- [x]` with brief result note
   - If findings change upcoming steps, update them now
   - Add discovery notes for the next agent/session
   ```bash
   git add <plan-file>
   git commit -m "update plan: step N complete, <brief note>"
   ```
5. Mark as completed

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
- **REQUIRED SKILL:** Use econ-superpowers:finishing-analysis
- Follow that skill to generate report, present merge/PR options

## Plan as Living Document

**The plan evolves as you discover things.** At each checkpoint:

- Mark completed steps with results: `- [x] Step 3: Merged holdings — 4.7M rows, 2% unmatched`
- Update upcoming steps if findings require changes
- Add discovery notes: "Unmatched rate higher than expected — added validation step before regression"

**The plan at any point should be a complete handoff document.** If the session ends, the next agent reads the plan and knows: what's done, what changed, what's next.

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
- **econ-superpowers:using-analysis-worktrees** — REQUIRED: Set up isolated workspace before starting
- **econ-superpowers:analysis-planning** — Creates the plan this skill executes
- **econ-superpowers:data-first-analysis** — REQUIRED: Discipline at every step
- **econ-superpowers:finishing-analysis** — Complete work after all steps done
