---
name: planning-workflow
description: superRA workflow PLAN step. Use when starting an analysis with a research objective and methodology, before writing any code — runs the Phase 1 data inventory hard gate, then creates a step-by-step PLAN.md with describe-analyze-doc discipline at each step. Outputs PLAN.md and RESULTS_UPDATE.md ready for execution-workflow.
---

# Planning Workflow

## Overview

Workflow skill for the **PLAN** phase of the superRA workflow. Owns data inventory (Phase 1) and plan creation (Phase 2+). Outputs `PLAN.md` and `RESULTS_UPDATE.md` for the execution-workflow to consume.

Write comprehensive analysis plans assuming the analyst has zero context for this project. Document everything they need: which files to create, what data to load, how to transform it, what to validate, and how to document results. Give them the whole plan as bite-sized steps. Frequent commits.

Assume the analyst is skilled at data work, but knows nothing about this specific project, its data, or its conventions.

**Announce at start:** "I'm using the planning-workflow skill to inventory data and create the analysis plan."

**Save plan to:** `PLAN.md` at the project root (if in a worktree, the worktree root; otherwise, the project root or user-specified location)
- Create `RESULTS_UPDATE.md` alongside (see Results Update Document section)
- (User preferences for plan location override this default)

Commit first before proceeding to execution.

## Phase 1: Data Inventory (Hard Gate)

The plan cannot be written without a data inventory. The user arrives with a research question and methodology already in mind. Your job in Phase 1 is NOT to design the research — it is to help with data logistics: what data exists, what's missing, and where to find it. The inventory becomes the **Data Inventory** section of `PLAN.md`.

<HARD-GATE>
Do NOT write any task structure, invoke any implementation skill, or take any planning action beyond Phase 1 until you have presented a data inventory and the user has approved it. This applies to EVERY analysis regardless of perceived simplicity.
</HARD-GATE>

### Phase 1 Checklist

Create a task for each of these items and complete them in order:

1. **Understand the analysis goal** — ask the user what they need to analyze and what data they expect to use. One question at a time; don't overwhelm.
2. **Explore project data** — check existing data directories, symlinks, and documentation:
   ```bash
   ls Data/ data/ 2>/dev/null
   ls -la *.parquet *.csv *.dta *.feather *.arrow 2>/dev/null
   cat Data/README.md data/README.md 2>/dev/null
   git ls-files --others --ignored --exclude-standard --directory
   grep -ri "data" CLAUDE.md AGENTS.md README.md 2>/dev/null | head -20
   ```
3. **Inventory available data** — for each dataset found, document name and path, format, approximate size (rows × columns), key variables, date range, source.
4. **Identify gaps** — compare what the user needs against what's available: missing datasets entirely, available data with wrong time period or frequency, missing variables within available datasets, data quality concerns.
5. **Research sources** — for missing data, suggest specific sources:
   - **Financial:** WRDS (CRSP, Compustat, IBES, TAQ), Bloomberg, Refinitiv
   - **Macro:** FRED, IMF WEO, World Bank, central bank websites
   - **Academic:** journal replication packages, ICPSR
   - **Project-specific:** check project documentation for custom data pipelines
   
   If WRDS or Refinitiv data skills are available, note them as tools for downloading.
6. **Present the inventory and get user approval.** Use the format from `references/plan-template.md` (the Data Inventory section of the header). Ask the user to confirm before proceeding to Phase 2.

### Phase 1 Principles

- **Be specific about sources** — "try WRDS" is vague; "CRSP Monthly Stock File via WRDS" is specific
- **Check before assuming** — explore the project before asking "do you have data?"
- **Document everything** — the inventory is a reference for the rest of the analysis

### Common Phase 1 mistakes

- **Skipping project exploration:** asking "what data do you have?" when the project directory has it. Always check the file system first, then ask about gaps.
- **Skipping the inventory:** verbal agreement on data, no written record. Always document the inventory — it becomes part of PLAN.md.

After the user approves the inventory, proceed to Phase 2 (Scope Check + Plan Creation).

## Phase 2: Scope Check

If the analysis covers multiple independent workstreams (e.g., "analyze portfolio sorts AND run Fama-MacBeth regressions AND build factor models"), suggest breaking into separate plans — one per workstream. Each plan should produce complete, documented results on its own.

## File Structure

Before defining tasks, map out the analysis pipeline:

- What scripts will be created? One per logical phase (data cleaning, variable construction, analysis, robustness).
- **Analysis scripts**: format for notebook rendering per `superRA:script-to-notebook`. Runner/pipeline scripts use standard format.
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

## Plan Document Header and Task Structure

The full PLAN.md template — required header (objective, methodology, data inventory, output, expected results, sensitivity analysis, pipeline) plus task block structure with describe → analyze → doc steps and worked example — lives in `references/plan-template.md` inside this skill. Load this skill via the Skill tool and read `<base_dir>/references/plan-template.md` when authoring a plan, then fill in the placeholders for the current analysis.

Required header fields and task block structure are non-negotiable. The template's example code is illustrative — adapt the content to your data and methodology, but preserve the describe → analyze → doc cycle.

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
3. Edit discovery notes into the relevant task sections
4. The plan at any point should be a complete handoff document: what's done, what changed, what's next
5. **Every update is an inline edit** — replace outdated text, don't append "Update:" blocks. The plan should always read as a single coherent document reflecting current understanding.

**Reviewers check:** Does the plan reflect what actually happened? Are upcoming steps still valid given what was found?

## Results Update Document

After saving `PLAN.md`, create `RESULTS_UPDATE.md` at the project root using the template at `references/results-update-template.md` inside this skill (load this skill via the Skill tool, then read `<base_dir>/references/results-update-template.md`).

The document is updated after each completed step alongside PLAN.md. Key rules:

- One section per task — replace prior content on re-implementation, never append a second version
- Reviewer caveats appear as blockquoted notes below the implementer's findings (replaced on re-review, not stacked)
- Save figures and tables as PNG in `results_attachments/` at project root (committed to git)
- The document should always read as a clean current-state summary, not a changelog
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
- Complete code in every step
- Row counts logged for every sample-changing operation
- Describe → Analyze → Doc → Commit at each step (see `econ-data-analysis` for the micro-level discipline)
- Pipeline file for multi-script analyses

## Self-Review

After writing the complete plan:

**1. Data inventory coverage:** Can you point to a task that handles each dataset from the Data Inventory section of this plan?

**2. Placeholder scan:** Search for red flags from the "No Placeholders" section. Fix them.

**3. Pipeline consistency:** Do the script names in the pipeline file match the scripts created in each task? Are they in the right order?

**4. Validation coverage:** Does every merge, filter, and variable construction have a corresponding validation step?

**5. Plan serves as handoff:** If you stopped here and a new agent read only this plan and RESULTS_UPDATE.md, could they continue? Is there enough context?

**6. Sensitivity coverage:** Are sensitivity analysis tasks included? Were they discussed with the user to determine which checks matter most for this analysis?

Fix issues inline. No need to re-review — just fix and move on.

## Execution Handoff

After finalizing the plan, commit the plan, then offer execution choice:

**"Plan complete and saved to `PLAN.md`. RESULTS_UPDATE.md created. Two execution options:**

**1. Subagent-Driven (recommended for independent tasks)** - I dispatch a fresh subagent per task, review between tasks, fast iteration. Best when tasks don't heavily depend on each other's outputs.

**2. Inline Execution (recommended for sequential pipelines)** - Execute tasks in this session using execution-workflow, context preserved across steps. Best when each step's output informs the next.

**Which approach?"**

**REQUIRED DISCIPLINE:** Use superRA:execution-workflow
- Defaults to subagent mode (fresh subagent per task + two-stage review)
- Falls back to direct mode for simple tasks or when user requests it
- Review always happens regardless of mode
