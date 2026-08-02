# Data-Analysis Planning Discipline

Load at the **PLAN phase** when the analysis involves data work.

- **Data Inventory** — hard gate; blocks task drafting until available data is inventoried and gaps surfaced.
- **Sensitivity Analysis Design** — which robustness checks matter for this study.

Both happen once, then live as scoped subsections on the `## Objective` of the governing ancestor task — the task whose subtree the data governs.

---

## Data Inventory (Hard Gate)

Data logistics — what exists, what's missing, where to find it. Not research design.

<HARD-GATE>
Do NOT write task structure, invoke an implementation skill, or take any planning action beyond this gate until you have presented a data inventory and the researcher has approved it. Applies to EVERY data analysis regardless of perceived simplicity.
</HARD-GATE>

### Checklist

Create a task for each of these items and complete them in order:

1. **Understand the analysis goal** — ask what they need to analyze and what data they expect to use. One question at a time.

2. **Explore project data** — check existing data directories, symlinks, and documentation:
   ```bash
   ls Data/ data/ 2>/dev/null
   ls -la *.parquet *.csv *.dta *.feather *.arrow 2>/dev/null
   cat Data/README.md data/README.md 2>/dev/null
   git ls-files --others --ignored --exclude-standard --directory
   grep -ri "data" CLAUDE.md AGENTS.md README.md 2>/dev/null | head -20
   ```

3. **Inventory available data** — per dataset: name and path, format, approximate size (rows × columns), key variables, date range, source.

4. **Identify gaps** — needs against availability: missing datasets, wrong time period or frequency, missing variables within available datasets, data quality concerns.

5. **Research sources** — for missing data, suggest specific sources:
   - **Financial:** WRDS (CRSP, Compustat, IBES, TAQ), Bloomberg, Refinitiv
   - **Macro:** FRED, IMF WEO, World Bank, central bank websites
   - **Academic:** journal replication packages, ICPSR
   - **Project-specific:** check project documentation for custom data pipelines

   WRDS or Refinitiv data skills available: note them as download tools.

6. **Present the inventory and get researcher approval.** Data Inventory format: `task-tree/references/task-file-contract.md` §Task Anatomy. Confirm before task drafting.

### Gate loopholes to close

Sequential, and applies to every analysis however simple — simple analyses hide the same data-shape surprises.

- Explore the file system before asking "what data do you have?"
- The inventory is written into the governing task's objective in `superRA/`, never just verbally agreed.
- No speculative task structure while data availability is uncertain; no "I'll assume we have X, check later."
- No "pending data availability" or "TBD sources" in task steps — every source grounded in a verified file or table.

---

## Sensitivity Analysis Design

Every data-analysis plan includes sensitivity analysis tasks.

1. **Discuss with the researcher:** which robustness checks matter here. Not all checks are meaningful for every study.

2. **Pick checks from the menu** in `data-robustness-checklist.md`.

3. **Design as dedicated task(s):** typically after the main analysis produces baseline results.

4. **Document expected sensitivity:** per check, what you expect and what would be concerning.

5. **Unsure whether a sensitivity failure would be meaningful: ask the researcher** — judging "robust enough" is research judgment, not an RA call.

---

## Pipeline File (Reproducibility Requirement)

More than one script: the plan's file-structure section carries a pipeline file — one entry point running every script in dependency order, failing fast on errors. Update it whenever a script is added.

```bash
# run_all.sh
#!/bin/bash
set -e
python Code/01_clean_data.py
python Code/02_construct_variables.py
python Code/03_analysis.py
python Code/04_robustness.py
```

Julia equivalent: a `pipeline.jl` that `include`s each script in order.
