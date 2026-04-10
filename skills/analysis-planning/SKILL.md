---
name: analysis-planning
description: Use when you have a research objective and data inventory, before writing analysis code — creates a step-by-step analysis plan with describe-transform-validate discipline at each step
---

# Analysis Planning

## Overview

Write comprehensive analysis plans assuming the analyst has zero context for this project. Document everything they need: which files to create, what data to load, how to transform it, what to validate, and how to document results. Give them the whole plan as bite-sized steps. Describe first. Validate always. Log everything.

Assume the analyst is skilled at data work, but knows nothing about this specific project, its data, or its conventions.

**Announce at start:** "I'm using the analysis-planning skill to create the analysis plan."

**Context:** This should be run in a dedicated worktree (created by using-analysis-worktrees skill).

**Save plan to:** `PLAN.md` at the project root (each worktree has its own root)
- Create `RESULTS_UPDATE.md` alongside (see Results Update Document section)
- (User preferences for plan location override this default)

## Scope Check

If the analysis covers multiple independent workstreams (e.g., "analyze portfolio sorts AND run Fama-MacBeth regressions AND build factor models"), suggest breaking into separate plans — one per workstream. Each plan should produce complete, documented results on its own.

## File Structure

Before defining tasks, map out the analysis pipeline:

- What scripts will be created? One per logical phase (data cleaning, variable construction, analysis, robustness).
- **All scripts in jupytext percent format** (`.py` or `.jl` with `# %%` cells). See the `econ-data-analysis` skill's `references/jupytext-guide.md`.
- What data files are inputs? Where do outputs go?
- Follow existing project conventions for directory structure.

**Pipeline file (required for multi-script analyses):**

If the analysis involves more than one script, the plan MUST include a pipeline file that runs all scripts in the correct order. This is a reproducibility requirement.

```bash
# Example: run_all.sh
#!/bin/bash
set -e
echo "Step 1: Clean data"
python Code/01_clean_data.py
echo "Step 2: Construct variables"
python Code/02_construct_variables.py
echo "Step 3: Main analysis"
python Code/03_analysis.py
echo "Step 4: Robustness checks"
python Code/04_robustness.py
echo "Pipeline complete."
```

Or for Julia:
```julia
# pipeline.jl
include("Code/01_clean_data.jl")
include("Code/02_construct_variables.jl")
include("Code/03_analysis.jl")
```

The pipeline file must:
- Run all scripts in dependency order
- Fail fast on errors (`set -e` or equivalent)
- Be committed to version control
- Be updated whenever a new script is added to the analysis

## Step Granularity

**Each step is one data operation with full discipline:**

- "Describe the raw holdings data (panel structure, key variables, missing values)" — step
- "Merge holdings with fund characteristics (left join on fund_id × date)" — step
- "Validate merge result (row counts, check unmatched, spot-check merged variables)" — step
- "Document merge decisions and commit" — step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Analysis Name] Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use superRA:econ-data-analysis at every step. Use superRA:executing-analysis to execute this plan. Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff.

**Objective:** [One sentence describing what this analysis produces]

**Methodology:** [Brief description — the user has already decided this]

**Data:** [Key datasets and their sources — reference data inventory if available]

**Output:** [What files/tables/figures will this produce?]

**Expected Results / Hypotheses (optional):** [What does the user expect to find? Can be hypotheses, conjectures, objectives, or prior intuition. Helps agents interpret results and judge sensitivity tests. Leave blank for purely exploratory work.]

**Sensitivity Analysis:** [What robustness checks should be performed? Discuss with user which checks matter most for this analysis. Reference econ-data-analysis skill's `references/data-robustness-checklist.md` for a menu of options.]

**Pipeline:** [Path to pipeline file, e.g., `run_all.sh`]

---
```

## Task Structure

````markdown
### Task N: [Phase Name]

**Script:** `Code/NN_phase_name.py` (jupytext percent format)
**Input:** `Data/input_file.parquet`
**Output:** `Data/output_file.parquet`, `Output/figure.pdf`

- [ ] **Step 1: Describe input data**

```python
# %% [markdown]
"""
## Load Raw Holdings
Source: CRSP mutual fund holdings, 2000-2020.
Expect ~4.7M rows across ~12K funds.
"""

# %%
df = pd.read_parquet("Data/holdings.parquet")
print(f"Shape: {df.shape}")
print(f"Funds: {df['fund_id'].nunique()}, Dates: {df['date'].nunique()}")
print(f"Period: {df['date'].min()} to {df['date'].max()}")

# Balancedness
obs_per_fund = df.groupby('fund_id')['date'].nunique()
print(f"Periods/fund — mean: {obs_per_fund.mean():.0f}, "
      f"median: {obs_per_fund.median():.0f}, "
      f"min: {obs_per_fund.min()}, max: {obs_per_fund.max()}")

# Key variables
df[["market_value", "weight"]].describe(percentiles=[.01, .05, .5, .95, .99])
```

- [ ] **Step 2: Merge with fund characteristics**

```python
# %% [markdown]
"""
## Merge with Fund Characteristics
Left join on fund_id × date. Expect same row count (fund_chars is m:1).
"""

# %%
n_before = len(df)
df = df.merge(chars, on=["fund_id", "date"], how="left")
print(f"Rows: {n_before} → {len(df)} (delta: {len(df) - n_before})")
print(f"Unmatched: {df['char_var'].isna().sum()} ({df['char_var'].isna().mean():.1%})")
```

- [ ] **Step 3: Validate merge and commit**

Verify: row count unchanged, unmatched rate reasonable, merged variables have expected distributions.

```bash
git add Code/01_clean_data.py
git commit -m "merge holdings with fund characteristics"
```

- [ ] **Step 4: Update plan and results, commit**

Update PLAN.md: mark steps [x], note findings affecting downstream steps.
Update RESULTS_UPDATE.md: add key results for this task (row counts, summary stats, figures).
Save any figures to `results_attachments/`.

```bash
git add PLAN.md RESULTS_UPDATE.md results_attachments/
git commit -m "update plan + results: Task 1 complete"
```
````

## Sensitivity Analysis Design

Every analysis plan should include sensitivity analysis tasks. At the planning stage:

1. **Discuss with user:** What robustness checks matter for this analysis? Not all checks are meaningful for every study — the user knows which dimensions are most important.
2. **Reference `data-robustness-checklist.md`** for a menu of options:
   - Alternative outlier treatment (winsorization cutoffs, trimming vs no treatment)
   - Alternative variable definitions (functional form, denominators, lag structure, aggregation)
   - Alternative sample restrictions (time windows, geographic subsets, balanced vs unbalanced panel)
   - Leave-one-out / influential observations
   - Alternative data sources (when the same concept is measured by multiple providers)
3. **Design as dedicated task(s):** Sensitivity checks are their own task(s) in the plan, typically after the main analysis produces baseline results.
4. **Document expected sensitivity:** For each check, note what you expect and what would be concerning.
5. **Not all failures are problems:** A result that's sensitive to outlier treatment may be fine if the outliers are legitimate data points. Use economic reasoning, not mechanical pass/fail. **If unsure whether a sensitivity failure is meaningful, ask the user.**

## Living Plan Document

**The plan is NOT a static spec.** Research reveals surprises. At each checkpoint:

1. Mark completed steps `- [x]` with brief result notes
2. **Update upcoming steps** if findings change the approach
3. Add discovery notes: "Merge unmatched rate is 15% — investigate before proceeding to regression"
4. The plan at any point should be a complete handoff document: what's done, what changed, what's next

**Reviewers check:** Does the plan reflect what actually happened? Are upcoming steps still valid given what was found?

## Results Update Document

After saving `PLAN.md`, create `RESULTS_UPDATE.md` at the project root:

```markdown
# [Analysis Name] — Results Update

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS_UPDATE.md for what was found.

**Last updated:** [date] (Task N, Step M)
**Status:** In Progress

---

[Sections added as tasks complete — initially empty]
```

**Rules:**
- Update after each completed step (alongside PLAN.md update)
- Include: key row counts, summary statistics, figures, surprising findings
- Save figures and tables as PNG in `results_attachments/` at project root (committed to git)
- Reference full output files for detailed results (these may be gitignored)
- Commit `RESULTS_UPDATE.md` and `results_attachments/` with each checkpoint commit
- Together with PLAN.md, this forms a complete handoff: context + what happened + what was found

## No Placeholders

Every step must contain the actual code an analyst needs. These are **plan failures** — never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate validation" / "check results" (without actual code)
- "Similar to Task N" (repeat the code — the analyst may read tasks out of order)
- "Run descriptive statistics" (without showing which variables and what statistics)
- Steps that describe what to do without showing how (code blocks required)

## Remember
- Exact file paths always
- Complete code in every step — jupytext percent format
- Row counts logged for every sample-changing operation
- Describe → Transform → Validate → Document → Commit at each step
- Pipeline file for multi-script analyses

## Self-Review

After writing the complete plan:

**1. Data inventory coverage:** Can you point to a task that handles each dataset from the data inventory?

**2. Placeholder scan:** Search for red flags from the "No Placeholders" section. Fix them.

**3. Pipeline consistency:** Do the script names in the pipeline file match the scripts created in each task? Are they in the right order?

**4. Validation coverage:** Does every merge, filter, and variable construction have a corresponding validation step?

**5. Plan serves as handoff:** If you stopped here and a new agent read only this plan and RESULTS_UPDATE.md, could they continue? Is there enough context?

**6. Sensitivity coverage:** Are sensitivity analysis tasks included? Were they discussed with the user to determine which checks matter most for this analysis?

Fix issues inline. No need to re-review — just fix and move on.

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to `PLAN.md`. RESULTS_UPDATE.md created. Two execution options:**

**1. Subagent-Driven (recommended for independent tasks)** - I dispatch a fresh subagent per task, review between tasks, fast iteration. Best when tasks don't heavily depend on each other's outputs.

**2. Inline Execution (recommended for sequential pipelines)** - Execute tasks in this session using executing-analysis, context preserved across steps. Best when each step's output informs the next.

**Which approach?"**

**REQUIRED DISCIPLINE:** Use superRA:executing-analysis
- Defaults to subagent mode (fresh subagent per task + two-stage review)
- Falls back to direct mode for simple tasks or when user requests it
- Review always happens regardless of mode
