# Review Mode

> Load when the request is to read a draft and produce findings, not edits — "review §X", "check my citations", "find issues", "consistency sweep". Output is a findings report.

## Workflow

1. **Confirm scope.** Which file(s), which sections, which dimensions. A one-sentence scope from the requester is enough; if the request is ambiguous between (e.g.) "review for clarity" and "review for consistency", ask before reading.
2. **Load the dimension files that match the scope** from `consistency/*.md`. For a clarity / structure review, load `style.md` and/or `structure.md` instead.
3. **Read the target end-to-end before classifying findings.** A finding's severity often depends on whether the issue recurs or is local.
4. **Classify each finding** into one of: **style** (sentence- or paragraph-level), **structure** (section ordering, missing topic sentence, buried governing idea), **consistency** (one of the eight dimensions — name it), or **argument** (the logic doesn't hold; a claim isn't supported; an unstated assumption is load-bearing). Argument findings are the highest-leverage and the easiest to miss — read for them deliberately.
5. **Report.** Per finding: file + line, classification, one-line description, recommendation. Group by classification; within a class, order by severity if obvious, otherwise by file order.

## Multi-dimensional consistency reviews

When the scope spans more than one consistency dimension (e.g., "check citations and cross-references and terminology"), dispatch **one reviewer per dimension in parallel** — each loaded with only its one `consistency/*.md` file. One generalist reviewer loaded with all eight produces shallower findings than N focused reviewers; the parallel pattern is also faster.

## Review-as-planning

When the review's findings will drive subsequent edits (the typical case for a section-level proofread), the natural shape of the report is a `PLAN.md` task list: each finding becomes a task entry the implementer can pick up. Use the handoff-doc PLAN.md task-block format (`superRA:handoff-doc references/plan-anatomy.md`) when the findings will survive across sessions or dispatches; a chat-only findings report suffices for same-session iteration.

The boundary between "findings report" and "plan" is fluid. If the requester says "now go fix these", the findings list becomes the implementer's task list directly — don't re-author.

## Intent comments as yardstick

When `% intent: …` (`.tex`) or `<!-- intent: … -->` (`.md`/`.qmd`) comments sit above paragraphs, read them alongside the prose. **Drift between stated intent and prose is a finding** — the intent line is the author's commitment about what the paragraph achieves; prose that misses it is higher-leverage than a sentence-level style issue. Classify these under **argument** or **structure** depending on the gap.

## No edits in this mode

The reviewer does not edit the target. If the requester reads the findings and asks for fixes, that transitions the work to Polish mode (with the findings as the explicit scope).
