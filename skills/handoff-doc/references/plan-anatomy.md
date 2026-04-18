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
```

**Header ownership:** Only the orchestrator (or standalone author) edits the header. Subagents read it but do not modify it. If a subagent discovers something that belongs in the header (a new convention spanning multiple tasks, a data inventory correction), they report it in their status return and the orchestrator decides whether to update the header.

## Project Conventions

Sits between the header's closing `---` and the first task block (or, if a `## Decisions` section is present, directly above it). Populated by the orchestrator at `planning-workflow` Phase 3 and refreshed at `execution-workflow` Step 1 when new upstream docs are discovered. Subagents read this section instead of re-walking the project's `CLAUDE.md` / `AGENTS.md` / `README.md` tree on every dispatch; if something they need is missing, they walk on-demand and flag the omission in their status return so the orchestrator can update the section.

```markdown
## Project Conventions

Walked at planning time (YYYY-MM-DD). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at <SHA>): [one-paragraph summary of the top-level conventions — package manager, directory layout rules, test conventions, branching model, etc.]
- `/AGENTS.md`: symlink to `/CLAUDE.md`.
- `/README.md` (HEAD at <SHA>): [one-paragraph summary of project purpose + pointers].

### Module-level docs walked
- `Code/pipeline/CLAUDE.md` (HEAD at <SHA>): [one-paragraph summary of pipeline-specific conventions — naming, output format, logging].
- `Data/README.md` (HEAD at <SHA>): [provenance, caveats, known quality issues for the data in this directory].
- `tests/README.md` (HEAD at <SHA>): [test-naming rules, helpers to reuse, drift-test location].

### Not walked (not reachable from the planned diff)
- `docs/archive/`, `sandbox/`, `Notebooks/exploratory/` — out of scope for this plan.
```

**Discipline:**

- **Populated by the orchestrator.** Subagents do not edit this section. If a subagent needs a convention the section does not carry, it walks on-demand, uses the result, and reports the omission so the orchestrator can add it.
- **Entry format: one paragraph per doc.** Not an excerpt — a summary. The subagent dispatches re-read the actual doc only if they need specifics; the summary is for fast triage.
- **Stamp the walk date.** A convention that was true two months ago may not be true today. The walk date tells the next orchestrator whether to re-walk.
- **List the NOT-walked paths too.** An empty section is ambiguous (orchestrator forgot? or nothing reachable?). Explicitly naming the out-of-scope directories removes the ambiguity.

## User Decisions Log

Researcher answers to `AskUserQuestion` / plain-text pauses land in `PLAN.md` **before** the agent acts on them, committed atomically with the work they unblock. The four document principles and the inline-edit rule (in `handoff-doc/SKILL.md` body) still apply — this section defines *where* decisions land and *what format* they take.

**Where it lands:**

- **Task-scoped decision** (affects one task's scope, methodology, or implementation) → blockquote inside that task block, directly under `**Review status:**`. Uses the same blockquote syntax as review notes, so it sits naturally beside the adjudication protocol in `agents/implementer.md` / `agents/reviewer.md`.
- **Cross-task / project-level decision** (methodology affecting multiple tasks, sample definition, output scope, `execution-workflow` Step 4 merge-menu choice, `integration-workflow` Step 1 drift-test selection, `integration-workflow` Step 3 doc disposition) → a top-level `## Decisions` section in `PLAN.md`, placed immediately after the header / `## Project Conventions` and before the first task block. Append new decisions to the bottom; do not rewrite prior decisions.

**Format (both locations):**

```markdown
> **User decision (2026-04-16):** Use CRSP value-weighted returns, not equal-weighted.
> **Question asked:** Which market return definition for the benchmark?
> **Rationale (if given):** Matches prior paper; easier reviewer comparison.
```

Three lines, blockquote, dated. `Question asked` is the agent's own short restatement of what it asked — specific enough for a fresh agent to see why the decision was needed. `Rationale` is optional; include only if the researcher gave one, never invent it.

The `ask-user-question-logger` PostToolUse hook reminds the agent to log after each `AskUserQuestion` call; when the harness does not expose the hook, set a TodoWrite reminder.

**Not covered here:**

- Reviewer-feedback adjudication inside review-notes blockquotes — that is the `→ orchestrator:` / `→ implemented:` protocol owned by `agents/implementer.md` and `agents/reviewer.md`. User decisions are upstream: the researcher answering a question the agent could not decide.
- Ephemeral clarifications the agent could have resolved from the code ("which file holds X?") — those are not decisions, they do not belong in the log.

If it is unclear whether an answer counts as a decision worth logging: if acting on it would change the code, data, or methodology in a way another agent could not reconstruct from the code alone, log it.

## Task Block Anatomy

````markdown
### Task N: [Phase Name]
**Depends on:** Task N-1 [, Task N-2] | *(none)*
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

## No Placeholders

Every step must contain the actual code an analyst needs. These are **plan failures**:

- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate validation" / "check results" (without actual code)
- "Similar to Task N" (repeat the code — readers may jump tasks)
- "Run descriptive statistics" (without naming variables and statistics)
- Prose that describes what to do without showing how (code blocks required)
