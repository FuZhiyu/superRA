# Data-Analysis Planning Discipline

Load at the **PLAN phase** when the analysis involves data work. `planning-workflow` invokes this reference after Phase 1 (scope check) to apply domain-specific discipline before tasks are drafted.

This reference carries two planning-only concerns that would otherwise bloat the main `econ-data-analysis` SKILL.md:

1. **Data Inventory — the hard gate that blocks task drafting until available data is inventoried and gaps are surfaced.**
2. **Sensitivity Analysis Design — the researcher-scoped discussion of which robustness checks matter for this specific study.**

Both happen once, at planning time, and then live in `PLAN.md` as sections the whole analysis references.

---

## Data Inventory (Hard Gate)

The plan cannot be written without a data inventory. The researcher arrives with a research question and methodology already in mind. Your job at this gate is NOT to design the research — it is to help with data logistics: what data exists, what's missing, and where to find it. The inventory becomes the **Data Inventory** section of `PLAN.md`.

<HARD-GATE>
Do NOT write any task structure, invoke any implementation skill, or take any planning action beyond this gate until you have presented a data inventory and the researcher has approved it. This applies to EVERY data analysis regardless of perceived simplicity.
</HARD-GATE>

### Checklist

Create a task for each of these items and complete them in order:

1. **Understand the analysis goal** — ask the researcher what they need to analyze and what data they expect to use. One question at a time; don't overwhelm.

2. **Explore project data** — check existing data directories, symlinks, and documentation:
   ```bash
   ls Data/ data/ 2>/dev/null
   ls -la *.parquet *.csv *.dta *.feather *.arrow 2>/dev/null
   cat Data/README.md data/README.md 2>/dev/null
   git ls-files --others --ignored --exclude-standard --directory
   grep -ri "data" CLAUDE.md AGENTS.md README.md 2>/dev/null | head -20
   ```

3. **Inventory available data** — for each dataset found, document name and path, format, approximate size (rows × columns), key variables, date range, source.

4. **Identify gaps** — compare what the researcher needs against what's available: missing datasets entirely, available data with wrong time period or frequency, missing variables within available datasets, data quality concerns.

5. **Research sources** — for missing data, suggest specific sources:
   - **Financial:** WRDS (CRSP, Compustat, IBES, TAQ), Bloomberg, Refinitiv
   - **Macro:** FRED, IMF WEO, World Bank, central bank websites
   - **Academic:** journal replication packages, ICPSR
   - **Project-specific:** check project documentation for custom data pipelines

   If WRDS or Refinitiv data skills are available, note them as tools for downloading.

6. **Present the inventory and get researcher approval.** Use the Data Inventory format from `superRA:handoff-doc` `references/plan-anatomy.md` (the **Data Inventory:** section of the header). Ask the researcher to confirm before proceeding to task drafting.

### Principles

- **Be specific about sources** — "try WRDS" is vague; "CRSP Monthly Stock File via WRDS" is specific.
- **Check before assuming** — explore the project before asking "do you have data?"
- **Document everything** — the inventory is a reference for the rest of the analysis.

### Common Mistakes

- **Skipping project exploration:** asking "what data do you have?" when the project directory has it. Always check the file system first, then ask about gaps.
- **Skipping the inventory:** verbal agreement on data, no written record. Always document the inventory — it becomes part of `PLAN.md`.

### Red Flags — Hard Gate Protection

The Data Inventory gate applies to every data analysis regardless of perceived simplicity. The following loopholes are closed:

**Never:**
- Skip the gate and propose the data inventory verbally. It must be written into `PLAN.md`.
- Proceed to task drafting before the researcher explicitly approves the inventory.
- Say "I'll assume we have X data — we can check later." Check first, then plan.
- Write task structure speculatively while data availability is uncertain.
- Use phrases like "pending data availability" or "TBD sources" in task steps — every source must be grounded in a verified file or table.
- Draft tasks in parallel with the inventory "to save time" — the gate is sequential.

**Common rationalizations that mean STOP:**
- "This analysis is simple — the gate is overkill." The gate applies every time. Simple analyses hide the same data-shape surprises as complex ones.
- "The researcher clearly knows what data they want." Write it down anyway. The doc is the record; verbal confirmation is not.
- "We can move faster if I draft tasks in parallel with inventory." No. Gate first, then tasks.
- "I'll sketch tasks and revise after inventory." A sketch written against unknown data will be thrown away — the revision is a rewrite, not an edit.

**Why the gate exists:** skipping the inventory means writing a plan for data you don't have, which means rewriting the plan after seeing the data — 2–3× the overhead. The Iron Law ("no transformation without prior description") has a planning-phase analogue: **no tasks without prior data inventory**.

After the researcher approves the inventory, proceed to task drafting.

---

## Sensitivity Analysis Design

Every data-analysis plan should include sensitivity analysis tasks. At the planning stage:

1. **Discuss with researcher:** What robustness checks matter for this analysis? Not all checks are meaningful for every study — the researcher knows which dimensions are most important.

2. **Reference `data-robustness-checklist.md`** (in this same `references/` folder) for a menu of options:
   - Alternative outlier treatment (winsorization cutoffs, trimming vs no treatment)
   - Alternative variable definitions (functional form, denominators, lag structure, aggregation)
   - Alternative sample restrictions (time windows, geographic subsets, balanced vs unbalanced panel)
   - Leave-one-out / influential observations
   - Alternative data sources (when the same concept is measured by multiple providers)

3. **Design as dedicated task(s):** Sensitivity checks are their own task(s) in the plan, typically after the main analysis produces baseline results.

4. **Document expected sensitivity:** For each check, note what you expect and what would be concerning.

5. **Not all failures are problems:** A result that's sensitive to outlier treatment may be fine if the outliers are legitimate data points. Use economic reasoning, not mechanical pass/fail. **If unsure whether a sensitivity failure is meaningful, ask the researcher.**

---

## Pipeline File (Reproducibility Requirement)

If the analysis involves more than one script, the plan MUST include a pipeline file that runs all scripts in the correct order. This is a reproducibility requirement and is captured in the plan's file structure section.

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

---

## Handoff to Implementation

After the Data Inventory is approved, the sensitivity menu is agreed, and tasks are drafted, `planning-workflow` commits the plan and hands off to `execution-workflow`. The main `econ-data-analysis` SKILL.md body carries the cross-cutting discipline that applies at every implementation step (Iron Law, describe-analyze-validate, pitfalls, validation). Agents load the main body automatically at dispatch time.
