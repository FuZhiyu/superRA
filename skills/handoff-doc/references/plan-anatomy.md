# Plan Anatomy (.plan/ Task Hierarchy)

The full anatomy for `.plan/` task trees. Load when you are creating a new plan, restructuring an existing one, or need to understand exactly where a piece of content belongs.

A plan has two levels: a **root task.md** (project-wide context) and a **recursive tree of child task directories**, each containing its own `task.md`.

## Root task.md

The root task sits at `.plan/task.md` and carries the project's standing context, written at planning time and updated in place as the project evolves.

```yaml
---
title: "Analysis Name"
status: not-started
review_status: ~
integration_status: ~
depends_on: []
tags: []
created: 2026-05-24
updated: 2026-05-24
---
```

### Root body sections

```markdown
## Objective

[One sentence describing what this analysis produces]

**Methodology:** [Brief description — the researcher has already decided this]

**[Domain-specific planning section(s) from the active domain reference]:** [For example: `Data Inventory` for data analysis, or `Model Inventory / Assumption Map` for theory/modeling.]

**Output:** [What files/tables/figures this analysis produces]

**Expected Results / Hypotheses:** [What the researcher expects to find]

**Sensitivity Analysis:** [What robustness checks matter most]

**Pipeline:** [Path to pipeline file, e.g., `run_all.sh`]

## Conventions

Walked at planning time (YYYY-MM-DD). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at <SHA>): [one-paragraph summary]
- `/README.md` (HEAD at <SHA>): [one-paragraph summary]

### Module-level docs walked
- `Code/pipeline/CLAUDE.md` (HEAD at <SHA>): [one-paragraph summary]

### Not walked (not reachable from the planned diff)
- `docs/archive/`, `sandbox/` — out of scope for this plan.

## Workflow Status

- [ ] **Plan approved** — researcher signed off
- [ ] **Execution complete** — all tasks `approved`, pipeline reproducible
- [ ] **Drift tests created** — drift tests passing on baseline
- [ ] **Integrated** — integration reviewer `approved` after Sync
- [ ] **Docs finalized** — results matured, project docs audited
- [ ] **Finished** — branch landed, PR opened, or cleanup completed

## Decisions

> **User decision (2026-05-24):** Use CRSP value-weighted returns, not equal-weighted.
> **Question asked:** Which market return definition for the benchmark?
> **Rationale (if given):** Matches prior paper; easier reviewer comparison.

## Sync Map

[Temporary — present only during active Sync round. Removed at Integrate closeout.]
```

### Root ownership

Only the orchestrator (or standalone author) edits the root task.md, including `## Workflow Status` and `## Decisions`. Subagents read the root but treat it as read-only. If a subagent discovers something that belongs in the root (a new convention spanning multiple tasks, a domain-inventory correction), they report it in their status return and the orchestrator decides whether to update the root.

`## Sync Map` is the narrow Sync/Integrate exception. When Sync needs it, the generic sync author owns the branch-level map and task-local Sync impact sections for the current round.

### Conventions section discipline

- **Populated by the orchestrator.** Subagents do not edit this section. If a subagent needs a convention the section does not carry, it walks on-demand, uses the result, and reports the omission so the orchestrator can add it.
- **Entry format: one paragraph per doc.** Not an excerpt — a summary.
- **Stamp the walk date.** A convention that was true two months ago may not be true today.
- **List the NOT-walked paths too.** An empty section is ambiguous; explicitly naming out-of-scope directories removes the ambiguity.

### Domain-specific root sections

The active domain skill's planning reference defines any required root sections beyond the generic fields above. Examples:

- **Data analysis** -> `Data Inventory` with available/needed datasets and data quality notes.
- **Theory / modeling** -> `Model Inventory / Assumption Map` with primitives, endogenous objects, timing, solution concept.

### Workflow Status checkboxes

Flipped only by the orchestrator (or standalone author), only at the moment the named workflow step completes, and only in the same commit that completes that step. Each box is a rollup over per-task statuses plus global gates. A box is unchecked again only when a scope change or post-sync refactor invalidates the milestone. Unchecking a box does not clear unrelated task-local status.

## Task.md Anatomy

Each task lives at `.plan/<path>/task.md`. The path is the canonical identifier.

### Frontmatter

```yaml
---
title: "Merge with Fund Characteristics"
status: not-started           # not-started | in-progress | implemented | revise | approved
review_status: ~              # ~ | implemented | revise | approved
integration_status: ~         # ~ | implemented | revise | approved
depends_on:                   # sibling directory names only
  - 01-load-raw-data
tags: [data-merge]
script: Code/03_merge_chars.py
input: [Data/holdings.parquet]
output: [Data/merged.parquet]
created: 2026-05-24
updated: 2026-05-24
---
```

### Body sections

Any `## Heading` is valid. Recommended defaults:

```markdown
## Objective

Left join holdings with fund characteristics on fund_id x date.
Use CRSP-style merge conventions. Validate row counts post-merge.

## Results

### Key Findings
- Merge preserved all 4.7M rows

### Notes
- Used fuzzy date matching for quarterly vs monthly frequency mismatch

## Decisions

> **User decision (2026-05-24):** Use fuzzy date matching for quarterly data.
> **Question asked:** How to handle frequency mismatch between holdings (monthly) and chars (quarterly)?
> **Rationale (if given):** Standard practice in the literature.

## Review Notes

> [MAJOR] Inner join used instead of left join ([Code/03.py:42](Code/03.py#L42))
>    -> implemented: switched to left join, row count preserved ([Code/03.py:42](Code/03.py#L42))
```

### Field-by-field notes

- **`status`** is a task-local validity marker. Valid values: `not-started`, `in-progress`, `implemented`, `revise`, `approved`. On re-entry, tasks in the transitive downstream closure of a modified task have their status cleared by default; unrelated approved tasks keep their status.
- **`review_status`** — the implementer sets `implemented` (signaling ready-for-review); the reviewer sets `revise` or `approved`. Valid values: `~` (unset), `implemented`, `revise`, `approved`. Before execution starts, leave as `~`.
- **`integration_status`** is owned by the integration reviewer and the implementer across the Integrate step. Valid values: `~`, `implemented`, `revise`, `approved`. The same DAG cascade rule applies as for `review_status`.
- **`depends_on`** lists sibling directory names. Dependencies are sibling-only; parent status rolls up from children automatically.
- **`script` / `input` / `output`** are fixed at planning time and only the orchestrator may change them (they define task scope).
- **`## Objective`** is planner-owned. Implementers read it but do not rewrite it.
- **`## Results`** is implementer-owned. Updated with findings during execution. See `references/results-anatomy.md` for the two-stage lifecycle.
- **`## Decisions`** holds task-scoped user decisions. Uses the three-line blockquote format (see below).
- **`## Review Notes`** is present only when there are active items. On `approved`, the section content is removed entirely. For how items enter, get annotated, and exit, see `agents/reviewer.md` and `agents/implementer.md`.

### Sync impact

When a Sync cluster affects a task, add a `## Sync Impact` section. Present only while an active Sync cluster affects this task. Removed at Integrate closeout.

**Format:** see `semantic-merge/references/workflow-sync-author.md`. Contains a pointer to the relevant Sync Map cluster in root task.md and task-specific context needed to understand the post-sync diff.

## User Decisions Log

Researcher answers to `AskUserQuestion` / plain-text pauses land in the relevant `task.md` **before** the agent acts on them, committed atomically with the work they unblock. The four document principles and the inline-edit rule (in `handoff-doc/SKILL.md` body) still apply — this section defines *where* decisions land and *what format* they take.

**Where it lands:**

- **Task-scoped decision** (affects one task's scope, methodology, or implementation) -> task's `## Decisions` section.
- **Cross-task / project-level decision** (methodology affecting multiple tasks, sample definition, output scope, completion choices, drift-test selection, doc disposition) -> root task.md `## Decisions` section. Append new decisions to the bottom; do not rewrite prior decisions.

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

The `## Sync Map` section in root task.md bridges Sync and Integrate. It answers the branch-wide question, "what did the semantic sync learn and resolve?" Task-local `## Sync Impact` sections answer the narrower question, "what context explains this task's post-sync diff?"

**Ownership:** The generic sync author creates or updates `## Sync Map` in root task.md and affected task-local `## Sync Impact` sections when there is material overlap, a conflict, a user decision, sync-review carryover, or post-sync context worth preserving. The generic sync reviewer edits only sync-review status and notes within the map. Integration reviewers and implementers read the map and task-local sections but do not rewrite them unless their dispatch explicitly assigns the affected task. The orchestrator removes Sync scaffolding at Integrate closeout because it is temporary, not a later-phase record.

**Lifecycle:**

1. Sync resolves `<base-ref>`, fetches it when it is a remote-tracking ref, computes `PRE_SYNC_BASE_SHA` and `BASE_HEAD_SHA`, and dispatches a generic sync author when the base has advanced.
2. The sync author writes `## Sync Map` in root task.md only when needed. If Sync is a no-op or trivial with no context to preserve, leave the section absent.
3. The sync author adds `## Sync Impact` sections only to tasks whose post-sync diff needs task-specific context during Integrate.
4. The sync reviewer verifies the sync and records approval or tasking notes before Integrate begins.
5. Integrate reads task-local Sync Impact plus referenced Sync Map clusters as context.
6. Integrate closeout removes `## Sync Map` from root task.md and `## Sync Impact` sections from affected tasks in the same commit that flips `Integrated`.

**Format:** see `semantic-merge/references/workflow-sync-author.md §Workflow Sync Map Format`.

**Placement in root task.md:** After `## Decisions`, before `## Workflow Status` or at the end of root body sections. Omit entirely until Sync surfaces a material change.
