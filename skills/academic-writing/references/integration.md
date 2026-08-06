# Integration Discipline for Writing

> Load when the writing task is riding `superintegrate` (whole-section drafts, whole-paper revisions, R&R passes touching a base branch). Generic codebase-coherence gates live in `superRA:refactor-and-integrate`; this file owns the writing-specific ones.

## Gates

### Gate 1 — Document builds clean on the merged state

Build after merging with the base branch (commands per engine in `refactor-and-compile.md §Compile`). Record command, pass / fail, and warnings split new-on-this-branch vs pre-existing-on-base. A merged-state failure blocks integration; a pre-existing base-branch failure is flagged, not blocking.

### Gate 2 — Outline stability

Extract the outline (section / subsection headings) from the base branch and the merged state, compare side by side. Every added, removed, reordered, or reworded heading traces to a task objective or a logged user decision. Unauthorized outline changes are blocking.

Quick extract:
- LaTeX: `grep -nE '\\(section|subsection|subsubsection)\{' main.tex`
- Markdown / Quarto: `grep -nE '^#{1,3} ' paper.qmd`

### Gate 3 — Voice preserved across the full diff

Sample three hunks at random from the cumulative branch diff and read the edited prose against the original (`git diff`). Voice-drift signals: formality shift (formal ↔ casual), diction substitution at scale, sentence-shape homogenization, hedging-style shift (`may` vs `might`), transition-word substitution. Consistent drift across the sampled hunks is blocking; isolated single-word drift is advisory.

### Gate 4 — Scope respected

Every hunk in the cumulative branch diff traces to a task objective, a logged user decision, or (no-plan modes) an explicit in-chat request recorded in a commit message. Untraceable hunks — most often a style sweep that escaped the planned scope — are blocking.

### Data-analysis-touching writing tasks

The writing vertical has no numerical drift tests of its own. When the task also produced numbers (a methodology revision that re-ran analysis, new coefficients pulled into the prose), data-analysis integration discipline applies in addition: drift tests per `econ-data-analysis/references/integration.md`, and `consistency/numerical.md` confirms every edited number traces to current code output.

## Gated Checklist

- `[BLOCKING]` Gate 1: build clean on merged state — error list empty.
- `[BLOCKING]` Gate 2: outline changes traced to a task or decision.
- `[BLOCKING]` Gate 3: voice preserved (three-hunk sample).
- `[BLOCKING]` Gate 4: every hunk traceable to a task, decision, or chat request.
- `[BLOCKING]` If the task also produced numbers: data-analysis integration discipline applied per `econ-data-analysis/references/integration.md`.
- `[ADVISORY]` Build warnings enumerated (new vs pre-existing) with one-line triage.
- `[ADVISORY]` Outline changes listed with their authorization source.
- `[ADVISORY]` Pre-submission hygiene (widows, orphans, overfull hboxes) addressed when applicable.
