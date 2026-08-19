# Review Mode

> Load when the request is to read a draft and produce findings, not edits — "review §X", "check my citations", "find issues", "consistency sweep". Output is a findings report.

## Workflow

1. **Confirm scope.** Which file(s), sections, and review lanes. A one-sentence scope from the requester is enough; ambiguity between (e.g.) "review for clarity" and "review for consistency" gets asked before reading.
2. **Load the review-lane files matching the scope**: `style.md` for language/style, `structure.md` for structure, the relevant `consistency/*.md` for consistency dimensions.
3. **Read the target end-to-end before classifying findings.** Severity often depends on whether the issue recurs or is local.
4. **Classify each finding** as **style** (sentence- or paragraph-level), **structure** (section ordering, missing topic sentence, buried governing idea), **consistency** (name the dimension), or **argument** (the logic doesn't hold; a claim isn't supported; an unstated assumption is load-bearing). Argument findings are the highest-leverage and easiest to miss — read for them deliberately.
5. **Report.** Per finding: source location as a link with a line anchor per `communicate/references/markdown.md`, classification, one-line description, recommendation. Group by classification; within a class, order by severity if obvious, otherwise by file order.

## Fix tiers

Shared apply-discipline vocabulary at two call sites: review-mode findings stamp `Fix:` on each line of every `consistency/<dim>.md` output block; polish-mode triage classifies each diagnosed issue on the same axis to decide apply-vs-surface (`polish.md §Triage`). The tier captures the supervision a downstream apply pass needs, not whether the finding *can* be auto-fixed.

- **`mechanical`** — surface-only change (orthography, grammar, format): typo, missing definite article, missing `\hat` on an established estimate, undefined acronym on first use. Meaning unchanged. Applied silently in batch.
- **`conventional`** — wording, phrasing, or sentence shape, preserving the paragraph's **sequence** (order of ideas), **set** (propositions asserted), and **force** (claim strength / hedge level): de-nominalization, breaking a long sentence, repairing parallelism, removing redundant phrasing, terminology-variant collapse to the paper's established choice. Applied with one finding-line per item in the commit message so the author can audit.
- **`authorial`** — changes sequence, set, or force, or commits the author to a choice not yet made: topic-sentence rewrite that moves the paragraph's argument, claim that may not generalize, sign disagreement between prose and table, terminology pick when the paper has not committed, Greek letter pick when the parameter is undefined elsewhere. Surfaced for the author; not applied.

**Sequence/set/force test.** The conventional/authorial line: all three preserved → `conventional`, however aggressive the rewrite; any one shifts → `authorial`. Worked examples across the boundary: a sentence-break is `conventional` (one proposition becomes two clauses, set unchanged), a sentence-reorder `authorial` (sequence shifts); a nominalization fix is `conventional` (action moves into the verb, force unchanged), a hedge strengthening — "may" → "does" — `authorial` (force shifts); a coordinate sentence merge is `conventional` (two equal-weight clauses joined), subordinating one to the other `authorial` (the subordinated clause loses standalone force); a topic-sentence move is `authorial` (the governing idea changes position).

Each `consistency/<dim>.md` output block names this section as the source of legal values.

## Thoroughness

- **Quick** — single reviewer, one pass. Default for short paragraph- or section-scope reviews.
- **Standard** — one reviewer per lane in parallel (§Multi-lane reviews). Default for full-section / multi-lane scopes.
- **Deep** — pre-submission / R&R rounds. Loads `long-form-review.md`, which owns the multi-perspective dispatch rule.

Infer thoroughness from scope; ask via `AskUserQuestion` only when ambiguous.

## Multi-lane reviews

Scope spanning more than one lane (language/style, structure, any consistency dimension): dispatch **one reviewer per lane in parallel**, each loading only its lane file — `style.md`, `structure.md`, or one `consistency/*.md`. One generalist loaded with every lane produces shallower findings, and runs slower. N > 1: load `long-form-review.md` for the review task-tree protocol.

## Review-as-planning

Findings driving edits in the same session: shape the chat report as an actionable list. Findings that must survive across sessions or dispatches: create or update task-tree tasks rather than a standalone review file; accepted findings live in task-local `## Review Notes` until a follow-up Polish task applies them. "Now go fix these" in a standalone session makes the findings list the explicit Polish scope directly — don't re-author.

## Intent comments as yardstick

Read `% intent: …` (`.tex`) / `<!-- intent: … -->` (`.md`/`.qmd`) comments above paragraphs alongside the prose. **Drift between stated intent and prose is a finding worth flagging** — flag, do not adjudicate; after a recent rewrite the prose may be the latest signal of intent and the comment stale (`polish.md §Intent comments` priority chain). Classify under **argument** or **structure** depending on the gap.

## No edits in this mode

The reviewer does not edit the target. A follow-on request for fixes transitions the work to Polish mode, with the findings as the explicit scope.
