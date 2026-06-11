# Data-Analysis Planning Discipline

Load at the **PLAN phase** when the analysis involves data work.

Two planning-only concerns:

1. **Data Inventory — the hard gate that blocks task drafting until available data is inventoried and gaps are surfaced.**
2. **Sensitivity Analysis Design — which robustness checks matter for this specific study.**

Both happen once at planning time and then live as scoped subsections on the `## Objective` of the task whose subtree the data governs — the top `superRA/task.md` for a single-workstream analysis, or the root of the data-analysis subtree when a larger project carries other workstreams.

---

## Data Inventory (Hard Gate)

Your job here is data logistics — what exists, what's missing, where to find it — not research design.

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

6. **Present the inventory and get researcher approval.** Use the Data Inventory format from `task-tree/references/task-file-contract.md` §Task Anatomy. Ask the researcher to confirm before proceeding to task drafting.

### Gate loopholes to close

The gate is sequential and applies to every analysis, however simple — simple analyses hide the same data-shape surprises as complex ones. Closed loopholes:

- Explore the file system before asking "what data do you have?" — don't ask about data the project directory already holds.
- The inventory is written into the governing task's objective in `superRA/`, never just verbally agreed.
- No speculative task structure while data availability is uncertain; no "I'll assume we have X, check later." Check first.
- No "pending data availability" or "TBD sources" in task steps — every source is grounded in a verified file or table.

After the researcher approves the inventory, proceed to task drafting.

---

## Sensitivity Analysis Design

Every data-analysis plan should include sensitivity analysis tasks. At the planning stage:

1. **Discuss with researcher:** What robustness checks matter for this analysis? Not all checks are meaningful for every study — the researcher knows which dimensions are most important.

2. **Pick checks from the menu** in `data-robustness-checklist.md` (same `references/` folder).

3. **Design as dedicated task(s):** Sensitivity checks are their own task(s), typically after the main analysis produces baseline results.

4. **Document expected sensitivity:** For each check, note what you expect and what would be concerning.

5. **If unsure whether a sensitivity failure would be meaningful, ask the researcher** — judging "robust enough" is research judgment, not an RA call.

---

## Pipeline File (Reproducibility Requirement)

If the analysis involves more than one script, the plan must include a pipeline file in its file-structure section — a single entry point that runs every script in dependency order and fails fast on errors. Update it whenever a new script is added.

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
