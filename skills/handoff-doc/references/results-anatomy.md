# RESULTS.md Anatomy

The full template for `RESULTS.md`. Load when you are creating or restructuring the findings document.

`RESULTS.md` is a **single artifact with two stages**. The same file matures from a live agent-facing dev log during IMPLEMENT into a permanent, human-facing, fact-checked record during INTEGRATE. Same file name, same identity — only the location, structure, and discipline change across stages.

- **Stage 1 — Dev log (IMPLEMENT phase).** Lives at the worktree root alongside `PLAN.md`. Task-indexed, mirrors `PLAN.md`'s task structure, terse, agent-facing. Implementer writes each task's findings; reviewer may leave a reliability caveat. "Latest state only" — re-implementation replaces a task's section; it does not append history.
- **Stage 2 — Permanent record (INTEGRATE phase).** Consolidated in place at `integration-workflow` Document: claims fact-checked, structure rewritten for reader flow (not execution order), figures materialized into a new attachments folder, frontmatter added, file relocated from worktree root into the analysis's permanent code folder (resolved from project guidance), committed as part of the integration commit.

The Stage 2 consolidation discipline lives in `skills/report-in-markdown/references/final-form.md`. This file defines Stage 1 only.

## Header

```markdown
# [Analysis Name] — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** YYYY-MM-DD (Task N, Step M)
**Status:** In Progress | Completed

---
```

## Starter scaffold — pre-allocated task stubs

At planning time, `RESULTS.md` is created with **one stub per PLAN.md task block**, in the same order and with the same task name:

```markdown
## Task 1: [Phase name as in PLAN.md]

**Status:** Not started

## Task 2: [Phase name as in PLAN.md]

**Status:** Not started

...
```

During execution, the implementer replaces its task's stub with the per-task section shape below. A stub left as `**Status:** Not started` at the end of execution is a red flag — either the task was skipped without logging the decision, or the implementer failed to update the doc.

## Per-task section (executed)

```markdown
## Task N: [Phase Name]

**Status:** Completed (Task N approved YYYY-MM-DD)

### Key Findings
- [primary result, with number]
- [secondary result]

### Row Counts / Sample
- Input: N rows
- After [operation]: N rows (delta: Δ)
- Final sample: N rows

### Figures and Tables
![Descriptive caption for fig A](results_attachments/fig_taskN_a.png)

![Descriptive caption for fig B](results_attachments/fig_taskN_b.png)

### Notes
- [any caveat, data quirk, or decision the reader needs to interpret the results]

> **⚠️ Reviewer caveat (implementation):** [only present if the implementation reviewer left one; replaced on re-review; removed when APPROVED]
```

Omit subsections that do not apply. Each task section reads as a single current-state summary after every update.

## Figure embedding (Stage 1)

Stage 1 `RESULTS.md` points at figures already committed to `results_attachments/` at the project root. The analysis script writes the figure there; `RESULTS.md` embeds it with:

```markdown
![Descriptive caption](results_attachments/fig_name.png)
```

The full figure-embedding mechanics — PDF→PNG conversion, caption discipline, file-reference conventions — live in `skills/report-in-markdown/references/rich-content.md`. Load that reference when you are writing a task section that contains a figure, a table, or LaTeX math. Stage 1 uses `results_attachments/` as the target directory; pass that as the caller parameter when invoking `report-in-markdown`.

For tables too large to inline, save as CSV/Parquet in `results_attachments/` and link with `[caption](results_attachments/table_name.csv)`.

## Section ownership

- **Planner (`planning-workflow` Phase 4)** — creates one pre-allocated stub per task block, in the same order and with the same task name as `PLAN.md`. Content of the stub is just `**Status:** Not started`.
- **Implementer** — replaces their assigned task's stub with the per-task section shape above on the first pass; on subsequent iterations, replaces the section's prior content in place. Never appends a new section at EOF.
- **Reviewer** (implementation stage only) — adds a reliability-caveat blockquote at the bottom of their task's section if needed. Replaces any prior caveat on re-review; removes it entirely when APPROVED with no remaining concerns.
- **Orchestrator / standalone author** — everything.

## Reviewer caveats

When an implementation reviewer approves a task but has a remaining reliability concern that doesn't block approval (e.g., "this result depends on a small subsample — treat as preliminary"), they add a blockquote at the bottom of the task's section:

```markdown
> **⚠️ Reviewer caveat (implementation):** Result based on 47 observations in the post-2020 subsample; power is limited. Statistical significance should be re-checked when 2025 data is added.
```

On re-review, the caveat is **replaced** with the current one, never stacked. When the concern is resolved, the caveat is removed entirely.

## Transition to Stage 2

At `integration-workflow` Document, `RESULTS.md` matures into its permanent form. The consolidation is performed by a dispatched doc-writer subagent (loaded with `superRA:report-in-markdown` in full mode) and gated by a doc-reviewer subagent — an enforced implementer-reviewer pair per workflow principle P1. The consolidation is done in place (not as a new file) and includes: fact-check against committed code/output, restructure from task-indexed to reader-facing, materialize figures from `results_attachments/` into a new `attachments/` folder next to the relocated file, add frontmatter, relocate to the permanent code folder per project guidance, and commit with the integration commit. Project-level docs (`CLAUDE.md` / `AGENTS.md` / `README.md`) are audited separately during `integration-workflow` Integrate per `refactor-and-integrate` §Project Doc Audit.

The full Stage 2 discipline — including the fact-check checklist, prohibited language patterns, and the reader-facing section layout — is defined in `skills/report-in-markdown/references/final-form.md`. Do not duplicate those rules here.
