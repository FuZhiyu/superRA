# Results Anatomy (task.md `## Results`)

Results now live in each task's `## Results` section within `task.md`, not in a separate `RESULTS.md` file. The same section matures through two stages.

## Two-Stage Lifecycle

- **Stage 1 — Dev log (IMPLEMENT phase).** Each task's `## Results` is the live findings record — terse, agent-facing. Implementer writes findings as they execute. "Latest state only" — re-implementation replaces a task's results; it does not append history.
- **Stage 2 — Permanent record (INTEGRATE phase).** Results maturation happens in the same `## Results` sections, restructured for reader-facing clarity — claims fact-checked, prose tightened for a human audience.

The Stage 2 consolidation discipline lives in `skills/report-in-markdown/references/final-form.md`. This file defines Stage 1 only.

## Stage 1: Results During Implementation

No pre-allocation needed. Each task.md starts with an empty `## Results` section (or whatever sections the planner writes). The implementer fills it during execution.

### Per-task results shape

```markdown
## Results

### Key Findings
- [primary result, with number]
- [secondary result]

### Row Counts / Sample
- Input: N rows
- After [operation]: N rows (delta: +/- N)
- Final sample: N rows

### Figures and Tables
![Descriptive caption for fig A](results_attachments/fig_taskN_a.png)

### Notes
- [any caveat, data quirk, or decision the reader needs to interpret the results]

### Notation & Assumptions Ledger
*(theory-modeling tasks only — required by `theory-modeling/SKILL.md`. Tasks introducing nothing record "None.")*
```

Omit subsections that do not apply (other than the Notation & Assumptions Ledger for theory-modeling tasks, which is mandatory and records "None" when empty). Each task's `## Results` reads as a single current-state summary after every update.

## Section Ownership

- **Planner (`planning-workflow`)** — creates task.md with `## Results` section (empty or with placeholder text describing expected outputs).
- **Implementer** — fills and updates `## Results` during execution. On subsequent iterations, replaces the section's prior content in place.
- **Orchestrator / standalone author** — everything.

Reviewers do NOT edit `## Results`. Reliability concerns are raised as findings in `## Review Notes`; the implementer addresses them on the next REVISE round.

## Figure Embedding (Stage 1)

Stage 1 `## Results` points at figures committed to `results_attachments/` at the project root. The analysis script writes the figure there; the results section embeds it with:

```markdown
![Descriptive caption](results_attachments/fig_name.png)
```

The full figure-embedding mechanics — PDF->PNG conversion, caption discipline, file-reference conventions — live in `skills/report-in-markdown/references/rich-content.md`. Load that reference when you are writing results that contain a figure, a table, or LaTeX math.

For tables too large to inline, save as CSV/Parquet in `results_attachments/` and link with `[caption](results_attachments/table_name.csv)`.

## Transition to Stage 2

At `integration-workflow` Document, results mature into their permanent form. The consolidation is performed by a dispatched doc-writer subagent (loaded with `superRA:report-in-markdown` in full mode) and gated by a doc-reviewer subagent. The consolidation restructures each task's `## Results` for reader-facing clarity: fact-check against committed code/output, tighten prose, materialize figures, and commit with the integration commit. Project-level docs (`CLAUDE.md` / `README.md`) are audited separately during `integration-workflow` Integrate per `refactor-and-integrate` §Project Doc Audit.

The full Stage 2 discipline — including the fact-check checklist, prohibited language patterns, and the reader-facing section layout — is defined in `skills/report-in-markdown/references/final-form.md`. Do not duplicate those rules here.
