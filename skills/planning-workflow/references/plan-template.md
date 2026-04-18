# PLAN.md Template

The plan document at the project root. Every plan starts with this header, then has a task block per step.

The header and task examples below are written for the **data-analysis vertical** — today's only implemented domain. Three header sections (**Data Inventory**, **Sensitivity Analysis**) and the describe/analyze/validate step cycle are data-analysis specifics; the domain skill `econ-data-analysis` (and its `references/planning.md`) owns them. For other verticals, swap the data-specific sections for the domain's equivalent (e.g., a derivation-status table for theory work) as the vertical's domain skill prescribes. The overall PLAN.md skeleton — objective, methodology, output, expected results, pipeline, then task blocks — is universal.

## Header

```markdown
# [Project Name] Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use the active domain skill (for data analysis: `superRA:econ-data-analysis`) at every step. Use `superRA:execution-workflow` to execute this plan. Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff.

**Objective:** [One sentence describing what this analysis produces]

**Methodology:** [Brief description — the user has already decided this]

<!-- Data-analysis-specific header section — comes from econ-data-analysis/references/planning.md. -->
<!-- Other verticals omit this block and substitute the domain's equivalent. -->

**Data Inventory:**

### Available
| Dataset | Path | Format | Rows | Date Range | Key Variables |
|---------|------|--------|------|------------|---------------|
| ... | ... | ... | ... | ... | ... |

### Needed (Not Yet Available)
| Dataset | Source | Access Method | Notes |
|---------|--------|---------------|-------|
| ... | ... | ... | ... |

### Data Quality Notes
- [Any known issues, missing coverage, etc.]

**Output:** [What files/tables/figures will this produce?]

**Expected Results / Hypotheses:** [What does the user expect to find? Can be hypotheses, conjectures, objectives, or prior intuition. Helps agents interpret results and judge sensitivity tests. Leave blank for purely exploratory work.]

<!-- Data-analysis-specific header section — see econ-data-analysis/references/planning.md §Sensitivity Analysis Design. -->
**Sensitivity Analysis:** [What robustness checks should be performed? Discuss with researcher which checks matter most. Menu of options in `econ-data-analysis/references/data-robustness-checklist.md`.]

**Pipeline:** [Path to pipeline file, e.g., `run_all.sh`]

---

## Project Conventions

Walked at planning time (YYYY-MM-DD). Subagents read this section instead of re-walking the project tree on every dispatch; if a subagent needs a convention not captured here, it walks on-demand and reports the omission so the orchestrator can update this section. See `handoff-doc/references/plan-anatomy.md` §Project Conventions for the full anatomy.

### Repo root
- `/CLAUDE.md` (HEAD at <SHA>): [one-paragraph summary — package manager, directory layout, test conventions, branching model].
- `/AGENTS.md`: symlink to `/CLAUDE.md`.
- `/README.md` (HEAD at <SHA>): [one-paragraph project-purpose summary].

### Module-level docs walked
- `Code/pipeline/CLAUDE.md` (HEAD at <SHA>): [summary of pipeline-specific conventions].
- `Data/README.md` (HEAD at <SHA>): [provenance, caveats, known data quality issues].

### Not walked (not reachable from the planned diff)
- `docs/archive/`, `sandbox/` — out of scope for this plan.

---
```

## Task Block Structure

The task-block example below is a **data-analysis example** — the step cycle (describe → analyze → validate) and the Python/pandas syntax come from the data-analysis vertical. For other verticals, preserve the three-element shape (input-diagnosis → operation → validate/commit) but substitute the domain's cycle and language. Documentation is written continuously inside each step, not as a separate step.

Each task block must declare a `**Depends on:**` line listing upstream task numbers, or `*(none)*` if the task has no upstream dependency. This field is required — an omitted field is a plan failure. The `execution-workflow` orchestrator reads these fields to identify tasks that may be dispatched in parallel.

````markdown
### Task N: [Phase Name]
**Depends on:** Task N-1 [, Task N-2] | *(none)*
**Review status:** *(set during execution — do not fill at planning time)*

**Script:** `Code/NN_phase_name.py` (notebook-compatible format)
**Input:** `Data/input_file.parquet`
**Output:** `Data/output_file.parquet`, `Output/figure.pdf`

- [ ] **Step 1: Describe — input data**

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

- [ ] **Step 2: Analyze — merge with fund characteristics**

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

- [ ] **Step 3: Validate — verify the result, document, and commit**

Validate: row count matches expectation (left join preserves left-table count), unmatched rate reasonable, merged variables have expected distributions, magnitudes make economic sense, PLAN.md expectations compared.
Update PLAN.md: mark steps [x], set `**Review status:** IMPLEMENTED`, note findings.
Update RESULTS.md: add key results for this task (row counts, summary stats, figures).
Save any figures to `results_attachments/`.
Commit code and docs together in a single atomic commit:

```bash
git add Code/01_clean_data.py PLAN.md RESULTS.md results_attachments/
git commit -m "Task 1: merge holdings with fund characteristics"
```
````
