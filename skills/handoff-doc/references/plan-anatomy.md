# PLAN.md Anatomy

The full template for `PLAN.md`. Load when you are creating a new plan, restructuring an existing one, or need to understand exactly where a piece of content belongs.

A plan has two top-level parts: a **header** (project-wide context) and a sequence of **task blocks**. Integration and merge workflows append their own task blocks to the same file using the same anatomy.

## Header

The header is the project's standing context, written at planning time and updated in place as the project evolves (new datasets, emergent conventions).

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

A checklist of workflow milestone rollups. Each box summarizes task-local validity markers (`**Review status:**` and `**Integration status:**`) plus any required global verification for that milestone. It flips only when all contributing tasks and gates have the appropriate status. Each box flips at the moment its workflow step completes, in the same commit that completes the step. A new agent reads this section as evidence for the main-agent Workflow Frontier Resolver; the task blocks remain the authority for mixed-state work. On re-entry, the orchestrator unchecks affected boxes by judgment and declares in §Decisions which boxes were cleared and why. Unchecking a rollup does not clear unrelated task statuses. The full drift-test suite must re-run green before rechecking `Drift tests created` — see `planning-workflow §User Feedback and Changing Plans`.

- [ ] **Plan approved** — researcher signed off on data inventory + plan (`planning-workflow` Phase 2)
- [ ] **Execution complete** — all tasks `APPROVED`, pipeline reproducible (`implementation-workflow` Step 3)
- [ ] **Drift tests created** — drift tests passing on baseline (`integration-workflow` Protect)
- [ ] **Integrated** — integration reviewer `APPROVED` on `BASE_HEAD_SHA..HEAD` after Sync (`integration-workflow` Integrate)
- [ ] **Docs finalized** — RESULTS.md matured, project docs audited, doc-reviewer `APPROVED` (`integration-workflow` Document)
- [ ] **Finished** — branch landed locally, PR opened, or requested cleanup completed (`integration-workflow` Finish)

---
```

### Header ownership

Only the orchestrator (or standalone author) edits the header, including `## Workflow Status` and (when present) `## Decisions`. Subagents read the header but treat it as read-only. If a subagent discovers something that belongs in the header (a new convention spanning multiple tasks, a data inventory correction), they report it in their status return and the orchestrator decides whether to update the header.

`## Sync Map` is the narrow Sync/Integrate exception. When Sync needs it, the generic sync author owns the branch-level map and task-local Sync impact annotations for the current round. The generic sync reviewer owns only the sync-review status / notes inside that map. Integration reviewers and implementers read the map and task-local pointers as context; the orchestrator removes temporary Sync scaffolding at Integrate closeout.

### Top-Level Order

Use one top-level order for every PLAN.md:

```markdown
# [Analysis Name] Plan
[standing context fields]
---
## Workflow Status
[milestone checklist]
---
## Project Conventions
[walk summaries]
## Decisions
[optional; omit until the first cross-task decision]
## Sync Map
[optional; omit unless the current Sync round needs it]
---
### Task 1: ...
```

`## Decisions` and `## Sync Map` both sit after `## Project Conventions` and before the separator that opens task blocks. If `## Decisions` is absent, insert `## Sync Map` directly after `## Project Conventions` and before that separator. If both are present, `## Sync Map` follows `## Decisions`.

## Project Conventions

Sits after `## Workflow Status` and before optional `## Decisions` / `## Sync Map` sections. Populated by the orchestrator at `planning-workflow` Phase 3 and refreshed at `implementation-workflow` Step 1 when new upstream docs are discovered. Subagents read this section instead of re-walking the project's `CLAUDE.md` / `AGENTS.md` / `README.md` tree on every dispatch; if something they need is missing, they walk on-demand and flag the omission in their status return so the orchestrator can update the section.

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
- **Cross-task / project-level decision** (methodology affecting multiple tasks, sample definition, output scope, `implementation-workflow` Step 4 completion choice, `integration-workflow` Protect drift-test selection, `integration-workflow` Document doc disposition) → a top-level `## Decisions` section in `PLAN.md`, placed after `## Project Conventions` and before `## Sync Map` / the first task block. Append new decisions to the bottom; do not rewrite prior decisions.

**Format (both locations):**

```markdown
> **User decision (2026-04-16):** Use CRSP value-weighted returns, not equal-weighted.
> **Question asked:** Which market return definition for the benchmark?
> **Rationale (if given):** Matches prior paper; easier reviewer comparison.
```

Three lines, blockquote, dated. `Question asked` is the agent's own short restatement of what it asked — specific enough for a fresh agent to see why the decision was needed. `Rationale` is optional; include only if the researcher gave one, never invent it.

The `ask-user-question-logger` PostToolUse hook reminds the agent to log after each `AskUserQuestion` call; when the harness does not expose the hook, set a TodoWrite reminder.

If it is unclear whether an answer counts as a decision worth logging: if acting on it would change the code, data, or methodology in a way another agent could not reconstruct from the code alone, log it.

## Sync Map

The `## Sync Map` section bridges Sync and Integrate. It answers the branch-wide question, "what did the semantic sync learn and resolve?" Task-local `**Sync impact:**` fields answer the narrower question, "what context explains this task's post-sync diff?"

**Ownership:** The generic sync author creates or updates `## Sync Map` and affected task-local `**Sync impact:**` fields when there is material overlap, a conflict, a user decision, sync-review carryover, or post-sync context worth preserving. The generic sync reviewer edits only `**Sync review status:**` and `> **Sync review notes:**` in the map, except when no Sync Map exists yet and a finding must be recorded — in that case the reviewer creates a minimal Sync Map with sync-review notes before returning REVISE (see `semantic-merge/references/workflow-sync-reviewer.md`). Integration reviewers and implementers read the map and task-local pointers but do not rewrite them unless their dispatch explicitly assigns the affected task. The orchestrator removes Sync scaffolding at Integrate closeout because it is temporary, not a later-phase record.

**Lifecycle:**

1. Sync resolves `<base-ref>`, fetches it when it is a remote-tracking ref, computes `PRE_SYNC_BASE_SHA` and `BASE_HEAD_SHA`, and dispatches a generic sync author when the base has advanced.
2. The sync author writes `## Sync Map` only when needed. If Sync is a no-op or trivial with no context to preserve, leave the section absent.
3. The sync author adds task-local `**Sync impact:**` fields only to tasks whose post-sync diff needs task-specific context during Integrate.
4. The sync reviewer verifies the sync and records `**Sync review status:** APPROVED` or tasking notes before Integrate begins.
5. Integrate reads task-local Sync impact plus referenced Sync Map clusters as context. It does not re-review semantic sync or turn Sync notes into a backlog.
6. Integrate closeout removes the section and temporary task-local Sync impact fields in the same commit that flips `Integrated`.

**Format:** see `semantic-merge/references/workflow-sync-author.md §Workflow Sync Map Format`.

**Placement:** After `## Project Conventions` and optional `## Decisions`, before the separator that opens task blocks. Omit entirely until Sync surfaces a material change.

### Task-local Sync impact

When a Sync cluster affects a task, add a compact `**Sync impact:**` field directly after `**Integration status:**`. **Format and removal rule:** see `semantic-merge/references/workflow-sync-author.md §Task-Local Sync Impact Format`.

## Task Block Anatomy

````markdown
### Task N: [Phase Name]
**Depends on:** Task N-1 [, Task N-2] | *(none)*
**Review status:** *(set during execution — not filled at planning time)*
**Integration status:** *(set during integration — not filled at planning time)*
**Sync impact:** *(optional; present only while an active Sync cluster affects this task)*

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

- **`**Review status:**`** is a task-local validity marker, present on a task once execution begins. Valid values: `IMPLEMENTED`, `REVISE (<stage>)`, `APPROVED`. Before execution starts, leave it as a placeholder or omit. On re-entry, tasks in the transitive downstream closure of a modified task have their status cleared by default; unrelated approved tasks keep their status. The orchestrator may exempt a downstream task by documenting why the upstream change does not affect its inputs (one blockquote per exempted task in §Decisions).
- **`**Integration status:**`** is a task-local validity marker owned by the integration reviewer and the implementer across the Integrate step — symmetric with `**Review status:**`, where the reviewer itself sets REVISE / APPROVED and the orchestrator intervenes only to overrule. The **integration reviewer** sets `REVISE` on tasks it annotates with integration review-notes and `APPROVED` on touched or Sync-impact-affected tasks that pass (in the same commit that writes the blockquote). The **implementer** flips in-scope `REVISE` tasks to `IMPLEMENTED` when it commits refactor work. The **integration reviewer** flips in-scope tasks to `APPROVED` when the cumulative diff passes (or back to `REVISE` on specific tasks if it finds issues), in the same commit that writes its review. The orchestrator does not flip Integration status by default; it only overrules a reviewer's flip via a `→ orchestrator: ...` annotation when it disagrees, same as for Review status. Valid values: unset / `IMPLEMENTED` / `REVISE` / `APPROVED`. The same DAG cascade rule applies as for `**Review status:**` — downstream tasks in the closure of a modified task have their Integration status cleared by default, with documented exemptions in §Decisions; unrelated approved tasks keep their status.
- **`**Sync impact:**`** is temporary Sync/Integrate scaffolding, written by the generic sync author and verified by the generic sync reviewer. It points to the relevant Sync Map cluster and states only the task-specific context needed to understand the approved post-sync diff. Integration implementers and reviewers read it as context; the orchestrator removes it at Integrate closeout unless the text describes a lasting task assumption.
- **Script / Input / Output** are fixed at planning time and only the orchestrator may change them (they define task scope).
- **Steps** are editable by the implementer: they may rewrite, reorder, add, or remove steps when the data forces deviation from the planned approach. Steps are expressed as checkbox items with inline code blocks that contain the actual analyst code.
- **Review notes blockquote** is present only when there are active items. On `APPROVED`, the blockquote is removed entirely. During Integrate, review items should cite Sync impact only as context for the approved post-sync diff; they should still identify a codebase-coherence, documentation, drift-test, or minimum-net-diff issue. For how items enter, get annotated, and exit across iterations, see `agents/reviewer.md` (first-round REVISE and re-review deletion) and `agents/implementer.md` (annotating fixes with `→ implemented: ...`).
- **`## Workflow Status` checkboxes** are flipped only by the orchestrator (or standalone author), only at the moment the named workflow step completes, and only in the same commit that completes that step. Each box is a rollup over per-task statuses plus global gates: e.g., `Execution complete` flips only when every task has `**Review status:** APPROVED`; `Drift tests created` flips only when the full drift-test suite passes (which requires all tasks to have `**Integration status:**` coverage). A box is unchecked again only when a scope change or post-sync refactor invalidates the milestone — see `planning-workflow §User Feedback and Changing Plans`. Unchecking a box records that the rollup is false; it does not clear unrelated task-local status. Subagents may not flip boxes; if a subagent reports work that completes a milestone, the orchestrator flips the box in the next commit.

## No Placeholders

Every step must contain the actual code an analyst needs. These are **plan failures**:

- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate validation" / "check results" (without actual code)
- "Similar to Task N" (repeat the code — readers may jump tasks)
- "Run descriptive statistics" (without naming variables and statistics)
- Prose that describes what to do without showing how (code blocks required)
