# Review Mode

> Load when the request is to read a draft and produce findings, not edits — "review §X", "check my citations", "find issues", "consistency sweep". Output is a findings report.

## Workflow

1. **Confirm scope.** Which file(s), which sections, which dimensions. A one-sentence scope from the requester is enough; if the request is ambiguous between (e.g.) "review for clarity" and "review for consistency", ask before reading.
2. **Load the dimension files that match the scope** from `consistency/*.md`. For a clarity / structure review, load `style.md` and/or `structure.md` instead.
3. **Read the target end-to-end before classifying findings.** A finding's severity often depends on whether the issue recurs or is local.
4. **Classify each finding** into one of: **style** (sentence- or paragraph-level), **structure** (section ordering, missing topic sentence, buried governing idea), **consistency** (one of the eight dimensions — name it), or **argument** (the logic doesn't hold; a claim isn't supported; an unstated assumption is load-bearing). Argument findings are the highest-leverage and the easiest to miss — read for them deliberately.
5. **Report.** Per finding: file + line, classification, one-line description, recommendation. Group by classification; within a class, order by severity if obvious, otherwise by file order.

## Fix tiers

Every consistency-dimension finding carries a `Fix:` line with one of three tiers, chosen by the reviewer when the finding is written. The tier captures the supervision a downstream apply pass needs — not whether the finding *can* be auto-fixed (anything can; the question is the cost of being wrong).

- **`mechanical`** — one correct fix exists and no semantic call is needed. Typo, missing definite article, missing `\hat` on an established estimate, undefined acronym on first use. Applied silently in batch.
- **`judgment`** — one likely fix exists but the agent must pick using paper-internal conventions. Terminology-variant collapse, choice between equally legal hedge phrasings, picking which Greek letter wins when the paper has not committed yet. Applied with one finding-line per item in the commit message so the author can audit.
- **`decision`** — the right fix needs author input. Cross-section claim that may or may not generalize, sign disagreement between prose and a table that could be either way, restructure suggestion. Surfaced for the author; not applied.

The tier replaces the earlier `Auto-fixable: Yes / No` flag. Each `consistency/<dim>.md` output block names this section as the source of legal values.

## Thoroughness

- **Quick** — single reviewer, one pass. Default for short paragraph- or section-scope reviews.
- **Standard** — one reviewer per dimension in parallel (per §Multi-dimensional consistency reviews). Default for full-section / multi-dim scopes.
- **Deep** — for pre-submission / R&R rounds. Loads `long-form-review.md`, which owns the multi-perspective dispatch rule.

Infer thoroughness from scope; ask via `AskUserQuestion` only when ambiguous.

## Multi-dimensional consistency reviews

When the scope spans more than one consistency dimension (e.g., "check citations and cross-references and terminology"), dispatch **one reviewer per dimension in parallel** — each loaded with only its one `consistency/*.md` file. One generalist reviewer loaded with all eight produces shallower findings than N focused reviewers; the parallel pattern is also faster. When N > 1, load `long-form-review.md` for the shared review-doc protocol.

## Review-as-planning

When the review's findings will drive subsequent edits (the typical case for a section-level proofread), the natural shape of the report is a `PLAN.md` task list: each finding becomes a task entry the implementer can pick up. Use the handoff-doc PLAN.md task-block format (`superRA:handoff-doc references/plan-anatomy.md`) when the findings will survive across sessions or dispatches; a chat-only findings report suffices for same-session iteration.

The boundary between "findings report" and "plan" is fluid. If the requester says "now go fix these", the findings list becomes the implementer's task list directly — don't re-author.

## Intent comments as yardstick

When `% intent: …` (`.tex`) or `<!-- intent: … -->` (`.md`/`.qmd`) comments sit above paragraphs, read them alongside the prose. **Drift between stated intent and prose is a finding worth flagging** — but flag, do not adjudicate; on a recent rewrite the prose may be the latest signal of intent and the comment may be stale (`polish.md §Intent comments` priority chain). Classify under **argument** or **structure** depending on the gap.

## No edits in this mode

The reviewer does not edit the target. If the requester reads the findings and asks for fixes, that transitions the work to Polish mode (with the findings as the explicit scope).
