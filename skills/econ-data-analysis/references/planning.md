# Data-Analysis Planning Discipline

Load at the **PLAN phase** when the analysis involves data work.

- **Data Inventory** — what data exists, what's missing, where to find it.
- **Sensitivity Analysis Design** — which robustness checks matter for this study.

Both happen once, during planning.

---

## Data Inventory

Data logistics, not research design.

**Not objective content.** The inventory itself never goes into a task's `## Objective`. Carry into a task only the specific paths, variables, and known gaps its work depends on. A durable record of the survey belongs in `## Details` of the governing task — information, not binding, per `task-tree/references/task-file-contract.md` §Task Anatomy.

### Checklist

In order:

1. **Understand the analysis goal** — what needs analyzing, and what data the researcher expects to use.

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

### Frontier Contributions

The inventory settles facts; what it leaves open goes to the researcher as frontier questions (`superplan §Grilling`):

- **Disposition of each gap** — acquire it, scope the analysis down to what exists, or proceed and mark the limitation.
- **Which robustness checks matter** for this study, from the `data-robustness-checklist.md` menu.
- **Whether a borderline sensitivity failure is meaningful** — judging "robust enough" is research judgment, not an RA call.

### Discipline

Applies to every analysis however simple — simple analyses hide the same data-shape surprises.

- Explore the file system before asking "what data do you have?"
- No speculative task structure while data availability is uncertain; no "I'll assume we have X, check later."
- No "pending data availability" or "TBD sources" in task steps — every source grounded in a verified file or table.

---

## Sensitivity Analysis Design

Every data-analysis plan includes sensitivity analysis tasks.

1. **Pick candidate checks from the menu** in `data-robustness-checklist.md`. Not all checks are meaningful for every study, so the selection is a frontier question (§Frontier Contributions).

2. **Design as dedicated task(s):** typically after the main analysis produces baseline results.

3. **Document expected sensitivity:** per check, what you expect and what would be concerning.

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
