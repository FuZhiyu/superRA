# PLAN.md Anatomy

The full template for `PLAN.md`. Load when you are creating a new plan, restructuring an existing one, or need to understand exactly where a piece of content belongs.

A plan has two top-level parts: a **header** (project-wide context) and a sequence of **task blocks**. Integration and merge workflows append their own task blocks to the same file using the same anatomy.

## Header

The header is the project's standing context, written at planning time and updated in place as the project evolves (new datasets, emergent conventions). Subagents read it at the start of every task.

```markdown
# [Analysis Name] Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. Use `superRA:econ-data-analysis` for every step that touches data. Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff.

**Objective:** [One sentence describing what this analysis produces]

**Methodology:** [Brief description — the researcher has already decided this]

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

**Conventions:** [Naming rules, file layout, unit choices, variable definitions that apply across tasks. Populated during execution as conventions emerge.]

**Output:** [What files/tables/figures this analysis produces]

**Expected Results / Hypotheses:** [What the researcher expects to find. Helps interpret results and judge sensitivity tests. Leave blank for purely exploratory work.]

**Sensitivity Analysis:** [What robustness checks matter most]

**Pipeline:** [Path to pipeline file, e.g., `run_all.sh`]

---

## Workflow Status

A checklist of irreversible workflow milestones. Each box flips at the moment its workflow step completes, in the same commit that completes the step. A new agent reads this section first to know where the project stands without having to scan task blocks or grep commits. If a later scope change reverts a completed milestone, uncheck the affected boxes — see `SKILL.md` §Mid-Session Scope Changes.

- [ ] **Plan approved** — researcher signed off on data inventory + plan (`planning-workflow` Phase 2)
- [ ] **Execution complete** — all tasks `APPROVED`, pipeline reproducible (`execution-workflow` Step 3)
- [ ] **Drift tests created** — drift tests passing on baseline (`integration-workflow` Stage 1)
- [ ] **Refactored** — integration-reviewer `APPROVED` on refactored code (`integration-workflow` Stage 2)
- [ ] **Docs finalized** — RESULTS.md matured, project docs audited, doc-reviewer `APPROVED` (`integration-workflow` Step 3)
- [ ] **Merged** — branch merged to main or PR opened (`merge-workflow` Step 4)

---
```

### Header ownership

Only the orchestrator (or standalone author) edits the header, including `## Workflow Status` and (when present) `## Decisions`. Subagents read these sections but do not modify them. If a subagent discovers something that belongs in the header (a new convention spanning multiple tasks, a data inventory correction), they report it in their status return and the orchestrator decides whether to update the header.

### `## Decisions` placement

When the first cross-task user decision arrives, insert a `## Decisions` heading immediately after `## Workflow Status` and before the first task block — so the header order is: standing context → `## Workflow Status` → `## Decisions` (when present) → `---` → task blocks. Format and rules per `SKILL.md` §User Decisions Log. Omit the heading entirely until there is a first decision to record.

## Task Block Anatomy

````markdown
### Task N: [Phase Name]
**Review status:** *(set during execution — not filled at planning time)*

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
```

- [ ] **Step 3: Validate — verify the result, document, commit**

Validate: row count matches expectation, unmatched rate reasonable, distributions sensible, magnitudes economically plausible. Update PLAN.md (mark steps `[x]`, set Review status: IMPLEMENTED). Update RESULTS.md (key findings, figures in `results_attachments/`). Commit code + handoff docs in a single atomic commit.

> **Review notes (present only during active REVISE rounds):**
> 1. [MAJOR] Step 2 uses inner join; should be left join to preserve all rows. (`Code/03.py:42`)
>    → implemented: switched to left join, row count preserved (`Code/03.py:42`)
> 2. [MINOR] Missing row-count log after merge.
>    → orchestrator: rejected — row count is logged two lines above, reviewer misread
````

## Field-by-Field Notes

- **`**Review status:**`** is always present on a task once execution begins. Valid values: `IMPLEMENTED`, `REVISE (<stage>)`, `APPROVED`. Before execution starts, leave it as a placeholder or omit.
- **Script / Input / Output** are fixed at planning time and only the orchestrator may change them (they define task scope).
- **Steps** are editable by the implementer: they may rewrite, reorder, add, or remove steps when the data forces deviation from the planned approach. Steps are expressed as checkbox items with inline code blocks that contain the actual analyst code.
- **Review notes blockquote** is present only when there are active items. On `APPROVED`, the blockquote is removed entirely. For how items enter, get annotated, and exit across iterations, see `agents/reviewer.md` (first-round REVISE and re-review deletion) and `agents/implementer.md` (annotating fixes with `→ implemented: ...`).
- **`## Workflow Status` checkboxes** are flipped only by the orchestrator (or standalone author), only at the moment the named workflow step completes, and only in the same commit that completes that step. A box is unchecked again only when a scope change or post-merge refactor invalidates the milestone — see `SKILL.md` §Mid-Session Scope Changes. Subagents may not flip boxes; if a subagent reports work that completes a milestone, the orchestrator flips the box in the next commit.

## No Placeholders

Every step must contain the actual code an analyst needs. These are **plan failures**:

- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate validation" / "check results" (without actual code)
- "Similar to Task N" (repeat the code — readers may jump tasks)
- "Run descriptive statistics" (without naming variables and statistics)
- Prose that describes what to do without showing how (code blocks required)
