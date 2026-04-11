# PLAN.md Template

The plan document at the project root. Every analysis plan starts with this header, then has a task block per step.

## Header

```markdown
# [Analysis Name] Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use superRA:econ-data-analysis at every step. Use superRA:execution-workflow to execute this plan. Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff.

**Objective:** [One sentence describing what this analysis produces]

**Methodology:** [Brief description — the user has already decided this]

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

**Sensitivity Analysis:** [What robustness checks should be performed? Discuss with user which checks matter most for this analysis. Reference econ-data-analysis skill's `references/data-robustness-checklist.md` for a menu of options.]

**Pipeline:** [Path to pipeline file, e.g., `run_all.sh`]

---
```

## Task Block Structure

````markdown
### Task N: [Phase Name]
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

- [ ] **Step 3: Doc — verify, update handoff docs, and commit**

Verify: row count unchanged, unmatched rate reasonable, merged variables have expected distributions.
Update PLAN.md: mark steps [x], set `**Review status:** IMPLEMENTED`, note findings.
Update RESULTS_UPDATE.md: add key results for this task (row counts, summary stats, figures).
Save any figures to `results_attachments/`.
Commit code and docs together in a single atomic commit:

```bash
git add Code/01_clean_data.py PLAN.md RESULTS_UPDATE.md results_attachments/
git commit -m "Task 1: merge holdings with fund characteristics"
```
````
