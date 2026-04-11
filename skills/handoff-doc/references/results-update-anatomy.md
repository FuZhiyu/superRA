# RESULTS_UPDATE.md Anatomy

The full template for `RESULTS_UPDATE.md`. Load when you are creating or restructuring the findings document.

`RESULTS_UPDATE.md` mirrors `PLAN.md`'s task structure. It has a short header and one section per task, added as findings come in. Together with `PLAN.md`, it forms a complete handoff: context + what to do + what was found.

## Header

```markdown
# [Analysis Name] — Results Update

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS_UPDATE.md for what was found.

**Last updated:** YYYY-MM-DD (Task N, Step M)
**Status:** In Progress | Completed

---
```

## Per-Task Section

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

## Figure Rules

- **Always embed with markdown image syntax:** `![caption](results_attachments/fig_name.png)`.
- The path is relative and points at a committed image file in `results_attachments/` at project root.
- Save figures as PNG. If the source is a PDF or SVG, convert to PNG for embedding and keep the original alongside for high-resolution access.
- The caption is the figure's title; a reader should understand what the figure shows from the caption alone.
- For tables too large to inline, save as CSV/Parquet in `results_attachments/` and link with `[caption](results_attachments/table_name.csv)`.

## Section Ownership

- **Implementer** — updates their assigned task's section on each iteration, replacing prior content in place.
- **Reviewer** (implementation stage only) — adds a reliability-caveat blockquote at the bottom of their task's section if needed. Replaces any prior caveat on re-review; removes it entirely when APPROVED with no remaining concerns.
- **Orchestrator / standalone author** — everything.

## Reviewer Caveats

When an implementation reviewer approves a task but has a remaining reliability concern that doesn't block approval (e.g., "this result depends on a small subsample — treat as preliminary"), they add a blockquote at the bottom of the task's section:

```markdown
> **⚠️ Reviewer caveat (implementation):** Result based on 47 observations in the post-2020 subsample; power is limited. Statistical significance should be re-checked when 2025 data is added.
```

On re-review, the caveat is **replaced** with the current one, never stacked. When the concern is resolved, the caveat is removed entirely.
