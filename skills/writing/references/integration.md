# Integration Discipline for Writing

> Load when the writing task is riding `superintegrate` (whole-section drafts, whole-paper revisions, R&R passes that touch a base branch). Generic codebase-coherence gates live in `superRA:refactor-and-integrate`; this file owns the writing-specific integration gates.

The writing vertical has no numerical drift tests of its own; when the task also produced numbers, `econ-data-analysis/references/integration.md` applies in addition.

## Gates

### Gate 1 — Document builds clean on the merged state

Run the full build after merging with the base branch (commands per engine in `refactor-and-compile.md §Compile`). Record build command, pass / fail, and warnings split into new-on-this-branch vs pre-existing-on-base. A failure on the merged state blocks integration; a pre-existing base-branch failure is flagged but does not block this branch.

### Gate 2 — Outline stability

Extract the outline (section / subsection headings) from both the base branch and the merged state, compare side by side. Every added, removed, reordered, or reworded heading must trace to either a task objective or a logged user decision. Unauthorized outline changes are blocking.

Quick extract:
- LaTeX: `grep -nE '\\(section|subsection|subsubsection)\{' main.tex`
- Markdown / Quarto: `grep -nE '^#{1,3} ' paper.qmd`

### Gate 3 — Voice preserved across the full diff

Sample three hunks at random from the cumulative branch diff. For each, read the edited prose against the original (`git diff`). Voice-drift signals: register shift (formal ↔ casual), diction substitution at scale, sentence-shape homogenization, hedging-style shift (`may` vs `might`), transition-word substitution. A consistent drift across the sampled hunks is blocking; isolated single-word drift is advisory.

### Gate 4 — Scope respected

Walk the cumulative branch diff and confirm every hunk traces to a task objective, a logged user decision, or (for no-plan modes) an explicit in-chat request recorded in a commit message. Untraceable hunks — most often a style sweep that escaped the planned scope — are blocking.

### Data-analysis-touching writing tasks

When the writing task also produced numbers (a methodology revision that re-ran analysis, new coefficients pulled into the prose), data-analysis integration discipline applies in addition: drift tests per `econ-data-analysis/references/integration.md`, and `consistency/numerical.md` confirms every edited number traces to current code output.

## Gated Checklist

- `[BLOCKING]` Gate 1: build clean on merged state — error list empty.
- `[BLOCKING]` Gate 2: outline changes traced to a task or decision.
- `[BLOCKING]` Gate 3: voice preserved (three-hunk sample).
- `[BLOCKING]` Gate 4: every hunk traceable to a task, decision, or chat request.
- `[BLOCKING]` If the task also produced numbers: data-analysis integration discipline applied per `econ-data-analysis/references/integration.md`.
- `[ADVISORY]` Build warnings enumerated (new vs pre-existing) with one-line triage rationale.
- `[ADVISORY]` Outline changes listed with their authorization source.
- `[ADVISORY]` Pre-submission hygiene (widows, orphans, overfull hboxes) addressed when applicable.
