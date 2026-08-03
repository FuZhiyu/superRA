---
title: "Style Spec: Teach the Terse Style Well Enough to Reproduce It"
status: revise
depends_on:  []
---

## Objective

The instructions that carry the terse style teach it well enough that an agent produces restyle-quality output without the exemplars in context. Audit the style's homes — using-superra §Communication (agent speech), implement-task §Reporting (task-file writing), CLAUDE.md §Skill Authoring Guidelines (skill prose) — against the review-task restyle; close gaps at the owning home, one home per rule. Record commit f525b63e as the worked example and daea6ae3 as the insufficient first cut. Plain naming (researcher decision): the convention is called "the terse style" — the word "register" is retired from task files and skill prose.

## Planner Guidance

The commit pair is the teaching device: same file, same instructions, only the second pass hit the level. Diff daea6ae3..f525b63e for the concrete moves — Scope collapsed to definition bullets, derivation clauses dropped, re-review actions as fragments. Whatever spec revision you write must predict that diff.

## Results

The gap was skill prose: no home taught how instruction lines are written. Closed by [CLAUDE.md §Skill Prose Style](../../../../CLAUDE.md) — two passes in order (DRY/Necessity gate deletes lines, then compress survivors) plus six concrete moves extracted from the daea6ae3..f525b63e diff, each mapping to a hunk class in that diff: framing sentence → definition bullets, condition-colon-fragment, rationale-clause deletion, second-mention shortening, bolded imperative shape, meaning-preserved compression. The pass is measured in words, not lines: the insufficient first cut (daea6ae3) cut 12% of words; the accepted pass (f525b63e) cut another 18% with no protocol loss.

The other two homes already teach their layer and were left unchanged: using-superra §Communication carries word/sentence-level economy for all agent speech and documents; implement-task §Reporting carries results-content selection.

Naming: "register" is retired everywhere per the researcher's decision. Task files under v04-lean-workflow now say "the terse style"; domain skill prose uses plain substitutes — "formality" ([theory-modeling/references/integration.md](../../../../skills/theory-modeling/references/integration.md), [writing/references/integration.md](../../../../skills/writing/references/integration.md)), "technicality" ([writing/references/draft.md](../../../../skills/writing/references/draft.md)), "terse style" ([superplan/references/task-tree-design.md](../../../../skills/superplan/references/task-tree-design.md)).

## Review Notes

Tier: thorough. Focus: correctness, scope-fidelity, results-writing. Verified: the word-count claims (`skills/review-task/SKILL.md` 1902 → 1674 → 1373 words = −12.0% then −18.0%, both exact), all six moves against the `daea6ae3..f525b63e` hunks (three quote the diff verbatim), the two unchanged homes ([using-superra/SKILL.md:12-24](../../../../skills/using-superra/SKILL.md#L12-L24), [implement-task/SKILL.md:37-48](../../../../skills/implement-task/SKILL.md#L37-L48)) do carry the layers the Results claims, and that no `tests/harness-instruction-following/load_contract.json` anchor points into `CLAUDE.md`.

1. **MAJOR** — [CLAUDE.md §Skill Prose Style, "Meaning survives verbatim"](../../../../CLAUDE.md) under-specifies what counts as protocol content, and the sibling sweep proved it. The bullet enumerates "gates, enums, defaults, and ordering constraints"; that list reads as exhaustive and licenses cutting everything else as wording. Downstream, five implementer rounds applying this spec lost content from exactly the classes the enumeration omits — decision-carrying epistemic hedges (the drift-test failure-attribution rule, whose unqualified form collapses a three-way classification), qualifiers that carry a branch (the dropped "only" that inverted an advisory, the "existing" qualifier in `protect.md`), and a protocol verb in `sync.md`. Group 1 also produced two edits that removed the imperative verb rather than the clause, leaving a section body with no instruction — a compression failure mode this spec's "delete whole clauses" framing does not warn against. These are spec classes, not reviewer-catch classes: an agent reading the bullet as written would make the same cuts. The rule the sweep settled — "a hedge that carries a decision branch is protocol content, not filler" — currently lives only in [repo-sweep/task.md `## Results`](../repo-sweep/task.md), a transient home that disappears at consolidation. Extend the bullet at its owning home to cover decision-carrying hedges and qualifiers, and to require the imperative verb survive compression. If the orchestrator judges the sweep evidence out of scope for this task, the rule still needs a durable home — schedule it rather than letting it die with the sweep's Results.

2. **MINOR** — "register" survives in [attachments/research-concise-writing.md:88](../../attachments/research-concise-writing.md#L88) ("write the skill itself in the target register"), which is the implementer's own summary line rather than quoted source, and at line 51 inside a Keep list. `## Results` asserts retirement "everywhere". Either sweep the summary line or narrow the Results claim to exclude verbatim research evidence.
