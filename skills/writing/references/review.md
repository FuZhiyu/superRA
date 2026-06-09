# Review Mode

> Load when the request is to read a draft and produce findings, not edits — "review §X", "check my citations", "find issues", "consistency sweep". Output is a findings report.

## Workflow

1. **Confirm scope.** Which file(s), which sections, which review lanes. A one-sentence scope from the requester is enough; if the request is ambiguous between (e.g.) "review for clarity" and "review for consistency", ask before reading.
2. **Load the review-lane files that match the scope**: `style.md` for language/style, `structure.md` for structure, and the relevant `consistency/*.md` files for consistency dimensions.
3. **Read the target end-to-end before classifying findings.** A finding's severity often depends on whether the issue recurs or is local.
4. **Classify each finding** into one of: **style** (sentence- or paragraph-level), **structure** (section ordering, missing topic sentence, buried governing idea), **consistency** (one of the eight dimensions — name it), or **argument** (the logic doesn't hold; a claim isn't supported; an unstated assumption is load-bearing). Argument findings are the highest-leverage and the easiest to miss — read for them deliberately.
5. **Report.** Per finding: source location formatted per `report-in-markdown` §File-reference rule, classification, one-line description, recommendation. Group by classification; within a class, order by severity if obvious, otherwise by file order.

## Fix tiers

A shared apply-discipline vocabulary used at two call sites: review-mode findings stamp `Fix:` on each line of every `consistency/<dim>.md` output block; polish-mode internal triage classifies each diagnosed issue along the same axis to decide apply-vs-surface (`polish.md §Triage`). The tier captures the supervision a downstream apply pass needs — not whether the finding *can* be auto-fixed (anything can; the question is the cost of being wrong).

- **`mechanical`** — surface-only change (orthography, grammar, format). Typo, missing definite article, missing `\hat` on an established estimate, undefined acronym on first use. The fix does not change meaning. Applied silently in batch.
- **`conventional`** — wording, phrasing, or sentence shape. Preserves the paragraph's **sequence** (order of ideas), **set** (propositions asserted), and **force** (claim strength / hedge level). Examples: de-nominalization, breaking a long sentence, repairing parallelism, removing redundant phrasing, terminology-variant collapse to the paper's established choice. Applied with one finding-line per item in the commit message so the author can audit.
- **`authorial`** — changes sequence, set, or force; or commits the author to a choice not yet made. Topic-sentence rewrite that moves the paragraph's argument, claim that may not generalize, sign disagreement between prose and table, terminology pick when the paper has not committed, Greek letter pick when the parameter is undefined elsewhere. Surfaced for the author; not applied.

**Sequence/set/force test.** This is the rule that draws the conventional/authorial line. If sequence + set + force are all preserved, the edit is `conventional` regardless of how aggressive the rewrite is. If any one shifts, it is `authorial`. Worked examples across the boundary: a sentence-break is `conventional` (one proposition becomes two clauses, set unchanged); a sentence-reorder is `authorial` (sequence shifts). A nominalization fix is `conventional` (action moves into the verb, force unchanged); a hedge strengthening — "may" → "does" — is `authorial` (force shifts). A coordinate sentence merge is `conventional` (two equal-weight clauses joined, force unchanged); subordinating one to the other is `authorial` (the subordinated clause loses standalone force). A topic-sentence move is `authorial` (sequence shifts; the paragraph's governing idea changes position).

Each `consistency/<dim>.md` output block names this section as the source of legal values.

## Thoroughness

- **Quick** — single reviewer, one pass. Default for short paragraph- or section-scope reviews.
- **Standard** — one reviewer per review lane in parallel (per §Multi-lane reviews). Default for full-section / multi-lane scopes.
- **Deep** — for pre-submission / R&R rounds. Loads `long-form-review.md`, which owns the multi-perspective dispatch rule.

Infer thoroughness from scope; ask via `AskUserQuestion` only when ambiguous.

## Multi-lane reviews

When the scope spans more than one lane (language/style, structure, or any consistency dimension), dispatch **one reviewer per lane in parallel**. Each reviewer loads only the lane file(s) it needs: `style.md`, `structure.md`, or one `consistency/*.md` file. One generalist reviewer loaded with every lane produces shallower findings than focused reviewers; the parallel pattern is also faster. When N > 1, load `long-form-review.md` for the shared review-doc protocol.

## Review-as-planning

When findings will drive subsequent edits, shape the report as a task list — each finding a task an implementer can pick up. Use the standard task format (`task-system/references/task-file-contract.md`) when findings survive across sessions or dispatches; a chat-only report suffices for same-session iteration. If the requester says "now go fix these", the findings list becomes the implementer's task list directly — don't re-author.

## Intent comments as yardstick

When `% intent: …` (`.tex`) or `<!-- intent: … -->` (`.md`/`.qmd`) comments sit above paragraphs, read them alongside the prose. **Drift between stated intent and prose is a finding worth flagging** — but flag, do not adjudicate; on a recent rewrite the prose may be the latest signal of intent and the comment may be stale (`polish.md §Intent comments` priority chain). Classify under **argument** or **structure** depending on the gap.

## No edits in this mode

The reviewer does not edit the target. If the requester reads the findings and asks for fixes, that transitions the work to Polish mode (with the findings as the explicit scope).
