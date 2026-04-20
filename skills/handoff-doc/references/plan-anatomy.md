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

A checklist of irreversible workflow milestones. Each box is a rollup over per-task `**Review status:**` and `**Integration status:**` fields — it flips only when all tasks that contribute to the milestone have the appropriate per-task status. Each box flips at the moment its workflow step completes, in the same commit that completes the step. A new agent reads this section first to know where the project stands without having to scan task blocks or grep commits. On re-entry, the orchestrator unchecks affected boxes by judgment and declares in §Decisions which boxes were cleared and why. The full drift-test suite must re-run green before rechecking `Drift tests created` — see `planning-workflow §Changing Plans`.

- [ ] **Plan approved** — researcher signed off on data inventory + plan (`planning-workflow` Phase 2)
- [ ] **Execution complete** — all tasks `APPROVED`, pipeline reproducible (`execution-workflow` Step 3)
- [ ] **Drift tests created** — drift tests passing on baseline (`integration-workflow` Phase A)
- [ ] **Refactored** — integration reviewer `APPROVED` on the unified sync+refactor diff (`integration-workflow` Phase B)
- [ ] **Docs finalized** — RESULTS.md matured, project docs audited, doc-reviewer `APPROVED` (`integration-workflow` Phase C)
- [ ] **Merged** — branch merged to main or PR opened (`integration-workflow` Phase D)

---
```

### Header ownership

Only the orchestrator (or standalone author) edits the header, including `## Workflow Status` and (when present) `## Decisions`. Subagents read these sections but do not modify them. If a subagent discovers something that belongs in the header (a new convention spanning multiple tasks, a data inventory correction), they report it in their status return and the orchestrator decides whether to update the header.

### `## Decisions` placement

When the first cross-task user decision arrives, insert a `## Decisions` heading immediately after `## Workflow Status` and before the first task block — so the header order is: standing context → `## Workflow Status` → `## Decisions` (when present) → `## Integration Intent` (when present) → `---` → task blocks. Format and rules per `SKILL.md` §User Decisions Log. Omit the heading entirely until there is a first decision to record.

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
- **Cross-task / project-level decision** (methodology affecting multiple tasks, sample definition, output scope, `execution-workflow` Step 4 merge-menu choice, `integration-workflow` Phase A drift-test selection, `integration-workflow` Phase C doc disposition) → a top-level `## Decisions` section in `PLAN.md`, placed immediately after the header / `## Project Conventions` and before the first task block. Append new decisions to the bottom; do not rewrite prior decisions.

**Format (both locations):**

```markdown
> **User decision (2026-04-16):** Use CRSP value-weighted returns, not equal-weighted.
> **Question asked:** Which market return definition for the benchmark?
> **Rationale (if given):** Matches prior paper; easier reviewer comparison.
```

Three lines, blockquote, dated. `Question asked` is the agent's own short restatement of what it asked — specific enough for a fresh agent to see why the decision was needed. `Rationale` is optional; include only if the researcher gave one, never invent it.

The `ask-user-question-logger` PostToolUse hook reminds the agent to log after each `AskUserQuestion` call; when the harness does not expose the hook, set a TodoWrite reminder.

If it is unclear whether an answer counts as a decision worth logging: if acting on it would change the code, data, or methodology in a way another agent could not reconstruct from the code alone, log it.

## Integration Intent

The `## Integration Intent` section bridges the integration reviewer's Phase B main-side scan and the per-task fix-review loop. When the reviewer scans `merge-base..origin/<base>` and finds incoming changes on main that materially affect this branch, it writes (or updates) this section to record what changed and which tasks need adaptation — so the orchestrator and downstream implementers know exactly what integration work is needed and why.

**Ownership:** Written and maintained by the integration reviewer only. The implementer does not edit this section. The orchestrator may append `→ orchestrator:` annotations to individual items (to reject, redirect, or flag for a second opinion), but the reviewer owns the prose.

**Lifecycle:**

1. Reviewer writes the section at `integration-workflow` Phase B Step 1 when the main-side scan surfaces material incoming changes.
2. When the last task named in a cluster reaches `Integration status: APPROVED`, the reviewer removes the corresponding item from the section.
3. When the last item is removed, the reviewer removes the section entirely. An empty section is never left in PLAN.md — its absence signals clean integration.

**Format:**

```markdown
## Integration Intent

> **Main-side change (2026-04-19):** `origin/main` added a session-start hook that drops a banner into every new session; touches no analysis files but adds a new `hooks/session-start` script and updates `README.md §Hooks`. Affects Tasks 5, 7 (README edit conflicts).
> **Adaptation needed:** Tasks 5 and 7's README edits must be re-based on top of the new §Hooks language.
```

One blockquote cluster per incoming change. Each cluster has two lines: `Main-side change (YYYY-MM-DD)` naming what landed on main and which tasks are affected, and `Adaptation needed` describing the specific work required. Affected task IDs are named explicitly so the orchestrator can scope implementer dispatches without re-reading the diff.

**Placement:** Directly after `## Decisions` (if present) and before the first task block, in the same position as that section in the header order. Omit entirely until the reviewer's first Phase B main-side scan surfaces a material change.

## Task Block Anatomy

````markdown
### Task N: [Phase Name]
**Depends on:** Task N-1 [, Task N-2] | *(none)*
**Review status:** *(set during execution — not filled at planning time)*
**Integration status:** *(set during integration — not filled at planning time)*

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

- **`**Review status:**`** is always present on a task once execution begins. Valid values: `IMPLEMENTED`, `REVISE (<stage>)`, `APPROVED`. Before execution starts, leave it as a placeholder or omit. On re-entry, tasks in the transitive downstream closure of a modified task have their status cleared by default; the orchestrator may exempt a downstream task by documenting why the upstream change does not affect its inputs (one blockquote per exempted task in §Decisions).
- **`**Integration status:**`** is owned by the integration reviewer and the implementer across Phase B's choreography — symmetric with `**Review status:**`, where the reviewer itself sets REVISE / APPROVED and the orchestrator intervenes only to overrule. The **integration reviewer** (annotation pass) flips to `REVISE` on tasks it annotates with integration review-notes (tasks it does not annotate stay `APPROVED`), in the same commit that writes the blockquote. The **implementer** flips to `IMPLEMENTED` on each in-scope task when it commits the refactor. The **integration reviewer** (verify pass) flips the in-scope tasks to `APPROVED` when the cumulative diff passes (or back to `REVISE` on specific tasks if it finds issues), in the same commit that writes its review. The orchestrator does not flip Integration status by default; it only overrules a reviewer's flip via a `→ orchestrator: ...` annotation when it disagrees, same as for Review status. Valid values: unset / `IMPLEMENTED` / `REVISE` / `APPROVED`. The same DAG cascade rule applies as for `**Review status:**` — downstream tasks in the closure of a modified task have their Integration status cleared by default, with documented exemptions in §Decisions. **B→B re-entry trigger:** when main advances mid-integration, the integration reviewer's annotation gates the flip — tasks it annotates get `**Integration status:** REVISE`; tasks it does not annotate stay `APPROVED`.
- **Script / Input / Output** are fixed at planning time and only the orchestrator may change them (they define task scope).
- **Steps** are editable by the implementer: they may rewrite, reorder, add, or remove steps when the data forces deviation from the planned approach. Steps are expressed as checkbox items with inline code blocks that contain the actual analyst code.
- **Review notes blockquote** is present only when there are active items. On `APPROVED`, the blockquote is removed entirely. For how items enter, get annotated, and exit across iterations, see `agents/reviewer.md` (first-round REVISE and re-review deletion) and `agents/implementer.md` (annotating fixes with `→ implemented: ...`).
- **`## Workflow Status` checkboxes** are flipped only by the orchestrator (or standalone author), only at the moment the named workflow step completes, and only in the same commit that completes that step. Each box is a rollup over per-task statuses: e.g., `Execution complete` flips only when every task has `**Review status:** APPROVED`; `Drift tests created` flips only when the full drift-test suite passes (which requires all tasks to have `**Integration status:**` coverage). A box is unchecked again only when a scope change or post-merge refactor invalidates the milestone — see `planning-workflow §Changing Plans`. Subagents may not flip boxes; if a subagent reports work that completes a milestone, the orchestrator flips the box in the next commit.

## No Placeholders

Every step must contain the actual code an analyst needs. These are **plan failures**:

- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate validation" / "check results" (without actual code)
- "Similar to Task N" (repeat the code — readers may jump tasks)
- "Run descriptive statistics" (without naming variables and statistics)
- Prose that describes what to do without showing how (code blocks required)
