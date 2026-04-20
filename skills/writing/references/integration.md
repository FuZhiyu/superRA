# Integration Discipline for Writing

> This reference is the single source of truth for writing-vertical integration discipline at the `integration` stage. The implementer walks it as pre-handoff self-check; the reviewer walks it as verification criteria. `[BLOCKING]` items must be fixed to earn APPROVE; `[ADVISORY]` items are suggestions the reviewer MAY flag as MINOR and do not block APPROVE. The verdict protocol is the same as `writing/SKILL.md` §Three Concurrent Disciplines — two verdicts (APPROVE / REVISE).

Generic cross-cutting code-integration concerns (naming consistency, utility reuse, PR-friendly diffs, documentation currency) live in `refactor-and-integrate/references/codebase-integration.md`. Load both files at the `integration` stage when the writing work is embedded in a larger codebase — this one owns the writing-specific gates; the generic file owns the cross-cutting ones.

## Scope of writing integration

The writing vertical's INTEGRATE phase is **different from data analysis**. There are no numerical drift tests to run (unless the task also produced analysis numbers, in which case `econ-data-analysis/references/integration.md` applies in addition to this file). The pre-merge gates for writing are:

1. **Document builds clean on the merged state.**
2. **Outline stability** — the structural skeleton of the document is preserved (or changes are authorized).
3. **Cross-reference integrity** across the full merged document.
4. **Consistency dimensions relevant to the edited sections pass** — one reviewer per applicable `consistency/*.md`.
5. **Voice preserved across the full diff** (sample check — random hunks, does the diff still sound like the author?).
6. **Scope respected** — no edits outside the original request that slipped through.

## How-To

### Gate 1 — Document builds clean on the merged state

Run the full build after merging with the base branch. See `writing/references/refactor-and-compile.md` §Compile for commands per engine. Record:

- Build command used.
- Pass / fail.
- Error list (must be empty).
- Warning list, classified: new-to-this-branch vs pre-existing-on-base-branch.

A build failure on the merged state blocks integration. A build failure on the base branch (pre-existing) is flagged but does not block *this* branch's integration.

### Gate 2 — Outline stability

Extract the outline of the document (section headings + subsection headings) from both the base branch and the merged state. Compare:

- **Sections added, removed, reordered.** Each should be traceable to the task plan (`PLAN.md`) or a documented user decision.
- **Subsection moves.** Same — traceable.
- **Heading rewording.** Small wording changes (especially reader-facing improvements per `structure-checklist.md`) are fine; full renames that break downstream references are flagged.

**Quick outline extract:**

- LaTeX: `grep -nE '\\(section|subsection|subsubsection)\{' main.tex`
- Markdown / Quarto: `grep -nE '^#{1,3} ' paper.qmd`

Compare pre- and post-merge outlines side by side. Unauthorized outline changes are `[BLOCKING]`.

### Gate 3 — Cross-reference integrity

Run the cross-reference integrity check per `writing/references/consistency/cross-references.md` on the full merged document (not just the edited sections — a rename in one section can break references in another). Specifically:

- No unresolved `\ref` / `\eqref` / `\cite` (no `??` in output).
- Every `\label` referenced at least once, or documented as deliberately orphan.
- Figure / table numbering consistent.

### Gate 4 — Consistency dimensions relevant to the edited sections

Identify which `consistency/*.md` dimensions apply to the edits:

| Edit type | Dimensions to check |
|---|---|
| Sentence-level polish | `terminology.md`, `cross-references.md` |
| Section drafting / restructuring | all eight dimensions applicable |
| Terminology / notation refactor | `terminology.md`, `notation.md`, `cross-references.md` |
| Citation cleanup | `citations.md`, `cross-references.md` |
| Numerical / results section | `numerical.md`, `cross-references.md`, `citations.md` |
| Methodology section draft / revision | `terminology.md`, `notation.md`, `math.md`, `citations.md` |
| Pre-submission sweep | all eight |

Dispatch one reviewer per applicable dimension (parallel, per `writing/references/workflow.md` §Mode (b)). Each reviewer loads `writing/SKILL.md` + the one `consistency/*.md` + this `integration.md`. All must return APPROVE for the integration gate to pass.

### Gate 5 — Voice preserved across the full diff

Sample three hunks at random from the full branch diff. For each hunk, read the edited prose alongside the original (`git diff`). Question: would the author's co-author recognize the edited passage as the author's own? Signals of voice drift:

- Register shift (formal → casual, or the reverse).
- Diction substitution at scale (preferred terms silently replaced).
- Sentence-shape homogenization (variable-length author prose compressed into uniform academic megastructures).
- Hedging-style shift (`may` vs `might` vs `could`).
- Transition word substitution (`however` for `that said`, etc.).

See `writing/references/collaboration.md` §What "voice preservation" means in practice for the full list.

A consistent drift across the sampled hunks is `[BLOCKING]`; occasional single-word drift in isolated hunks is `[ADVISORY]`.

### Gate 6 — Scope respected

Walk the branch diff and confirm every hunk is traceable to either:

- A task in `PLAN.md`, or
- An explicit user decision logged in `PLAN.md` §Decisions, or (for no-plan modes)
- An explicit in-chat request documented in a commit message.

Hunks that cannot be traced are out-of-scope edits — `[BLOCKING]`. Common offenders: a style-sweep of a section that was not in the plan's scope; a commented-out-text cleanup that removed author work-in-progress.

## Data-analysis-touching writing tasks

When the writing task also produced numbers (e.g., a methodology revision that re-ran analysis and re-pulled coefficients into the prose), data-analysis integration discipline applies in addition:

- Run data-analysis drift tests per `econ-data-analysis/references/integration.md` and `integrate-drift-tests.md`.
- Numerical consistency check per `writing/references/consistency/numerical.md` — every edited number traces to current code output.

Otherwise the data-analysis integration gates are not required for writing-only tasks.

## Gated Checklist

- `[BLOCKING]` **Gate 1: Document builds clean on merged state.** Error list empty.
- `[BLOCKING]` **Gate 2: Outline stability verified.** Unauthorized section / subsection changes flagged or reversed.
- `[BLOCKING]` **Gate 3: Cross-reference integrity across the full merged document.** No `??`; no undefined refs or citations.
- `[BLOCKING]` **Gate 4: Applicable consistency dimensions pass.** Each relevant `consistency/*.md` reviewer returned APPROVE.
- `[BLOCKING]` **Gate 5: Voice preserved.** Three-hunk sample check passed.
- `[BLOCKING]` **Gate 6: Scope respected.** Every hunk traceable to a task, user decision, or in-chat request.
- `[BLOCKING]` **If the task also produced numbers:** data-analysis integration discipline applied per `econ-data-analysis/references/integration.md`.
- `[ADVISORY]` **Build warnings enumerated** — new vs pre-existing, each new one triaged with rationale.
- `[ADVISORY]` **Outline changes listed** in the handoff with traceability to authorization.
- `[ADVISORY]` **Pre-submission-quality hygiene** (when applicable) — widows, orphans, overfull-hboxes addressed.

## Reviewer verdict protocol

Walk this file top to bottom. **Never halt on a failure.** Return APPROVE / REVISE. Dependent findings noted in prose (e.g., "couldn't assess Gate 4 because Gate 1 build failed — re-check after build is restored"). Re-review after REVISE is narrow.
