---
title: "Style Spec: Teach the Terse Style Well Enough to Reproduce It"
status: implemented
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
