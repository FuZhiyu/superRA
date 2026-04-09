---
name: data-exploration
description: "Use before starting analysis work — explores what data is already available in the project, identifies what additional data is needed, and researches where to obtain it. NOT research design — the user arrives with methodology decided."
---

# Data Exploration

Help identify and inventory the data needed for an analysis, then transition to planning.

The user arrives with a research question and methodology already in mind. Your job is NOT to design the research — it is to help with data logistics: what data exists, what's missing, and where to find it.

<HARD-GATE>
Do NOT invoke any implementation skill, write any analysis code, or take any implementation action until you have presented a data inventory and the user has approved it. This applies to EVERY analysis regardless of perceived simplicity.
</HARD-GATE>

## Checklist

You MUST create a task for each of these items and complete them in order:

1. **Understand the analysis goal** — ask the user what they need to analyze and what data they expect to use
2. **Explore project data** — check existing data directories, symlinks, and documentation
3. **Inventory available data** — list datasets found, their format, size, date range, key variables
4. **Identify gaps** — what data is needed but not yet available?
5. **Research sources** — for missing data, identify where to get it (WRDS, FRED, central banks, project-specific sources)
6. **Present data inventory** — structured summary of available + needed data, get user approval
7. **Save inventory** — write to `docs/analysis-specs/YYYY-MM-DD-<topic>-data-inventory.md` and commit
8. **Transition to planning** — invoke analysis-planning skill

## The Process

**Understanding the goal:**

- Ask the user what analysis they want to run
- Understand what variables they need (dependent, independent, controls)
- What level is the data? (firm, fund, country, individual, security)
- What time period and frequency? (daily, monthly, quarterly, annual)
- One question at a time — don't overwhelm

**Exploring project data:**

```bash
# Check common data locations
ls Data/ data/ 2>/dev/null
ls -la *.parquet *.csv *.dta *.feather *.arrow 2>/dev/null

# Check for data documentation
cat Data/README.md data/README.md 2>/dev/null

# Check gitignored data (symlinks, large files)
git ls-files --others --ignored --exclude-standard --directory

# Check for data-related config
grep -ri "data" CLAUDE.md AGENTS.md README.md 2>/dev/null | head -20
```

- Read any existing data documentation
- Check if data is symlinked from a shared folder
- Note file formats and approximate sizes

**Inventorying available data:**

For each dataset found, document:
- **Name and path**: `Data/holdings.parquet`
- **Format**: parquet, CSV, Stata DTA, etc.
- **Approximate size**: rows × columns (quick check, not full load)
- **Key variables**: what columns are available?
- **Date range**: if time-series or panel
- **Source**: where did this data originally come from?

**Identifying gaps:**

Compare what the user needs against what's available:
- Missing datasets entirely
- Available data with wrong time period or frequency
- Missing variables within available datasets
- Data quality concerns (known issues, missing coverage)

**Researching sources:**

For missing data, suggest specific sources:
- **Financial**: WRDS (CRSP, Compustat, IBES, TAQ), Bloomberg, Refinitiv
- **Macro**: FRED, IMF WEO, World Bank, central bank websites
- **Academic**: journal replication packages, ICPSR
- **Project-specific**: check project documentation for custom data pipelines

If WRDS or Refinitiv data skills are available, note them as tools for downloading.

**Presenting the inventory:**

```markdown
## Data Inventory: [Analysis Name]

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
```

Ask the user to confirm the inventory before proceeding.

## After the Inventory

**Documentation:**
- Save to `docs/analysis-specs/YYYY-MM-DD-<topic>-data-inventory.md`
  - (User preferences for spec location override this default)
- Commit the inventory document

**Transition:**
- Invoke the analysis-planning skill to create a step-by-step analysis plan
- Do NOT invoke any other skill. analysis-planning is the next step.

## Key Principles

- **Don't design the research** — the user has methodology in mind; you help with data
- **One question at a time** — don't overwhelm with multiple questions
- **Be specific about sources** — "try WRDS" is vague; "CRSP Monthly Stock File via WRDS" is specific
- **Check before assuming** — explore the project before asking "do you have data?"
- **Document everything** — the inventory is a reference for the rest of the analysis

## Common Mistakes

**Proposing methodology:**
- **Problem:** Agent starts suggesting research design, econometric methods
- **Fix:** The user has this decided. Focus on data logistics only.

**Skipping project exploration:**
- **Problem:** Asking "what data do you have?" when the project directory has it
- **Fix:** Always check the file system first, then ask about gaps

**Vague source recommendations:**
- **Problem:** "You could get this from various financial databases"
- **Fix:** Name the specific database, table, and access method

**Skipping the inventory document:**
- **Problem:** Verbal agreement on data, no written record
- **Fix:** Always write and commit the inventory — it's the handoff to planning

## Integration

**Terminal state:** Invoke `superRA:analysis-planning` to create the implementation plan.

**Pairs with:**
- **superRA:using-analysis-worktrees** — May be invoked before or after exploration, depending on whether the user wants an isolated workspace first
