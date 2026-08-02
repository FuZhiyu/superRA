---
title: "Repo Sweep: Restyle Remaining Skill Prose to the Terse Style"
status: in-progress
depends_on: []
---

## Objective

Every instruction file under skills/ matches the terse style at implement-task / review-task density. Behavior-preserving restyle only: protocol content, gates, and ordering constraints survive verbatim in meaning. Done so far: implement-task and using-superra (2e1fbdaa), review-task (f525b63e), superintegrate mature-consolidate.md (35832fe7), using-superra task-companion-files.md (f46265a5). Remaining: workflow skills, stage references, domain and utility skills.

## Planner Guidance

Per file: apply the CLAUDE.md DRY/Necessity gate first (delete lines that fail), then compress to the style (CLAUDE.md §Skill Prose Style). The daea6ae3 failure mode is the check: if the word count barely moves, the pass cut connectives, not clauses.

## Results

Spec test (main agent applying the fresh [CLAUDE.md §Skill Prose Style](../../../../CLAUDE.md)): [superplan/SKILL.md](../../../../skills/superplan/SKILL.md) 1047 → 756 words (−28%), [references/decomposition.md](../../../../skills/superplan/references/decomposition.md) 708 → 539 (−24%). Protocol preserved — all phase gates, tier table, dispatch template, and self-review items survive; the harness contract tests pass (15/15). One consolidation: decomposition's duplicate dependency-edge check merged into Self-Review item 8.

### Group 1 — workflow/orchestration remainder

19 files restyled. Word counts below are **prose only** (fenced code blocks and markdown tables excluded), since several of these files are mostly dispatch templates and shell snippets that must survive verbatim; raw whole-file counts understate the prose cut by up to 10 points.

| File | Before | After | Δ |
|---|---:|---:|---:|
| [superplan/references/consolidation.md](../../../../skills/superplan/references/consolidation.md) | 1425 | 1191 | −16% |
| [superplan/references/task-tree-design.md](../../../../skills/superplan/references/task-tree-design.md) | 1921 | 1596 | −17% |
| [superplan/references/thorough-planning.md](../../../../skills/superplan/references/thorough-planning.md) | 893 | 737 | −17% |
| [superplan/references/harness-plan-mode.md](../../../../skills/superplan/references/harness-plan-mode.md) | 232 | 194 | −16% |
| [superplan/references/changing-the-tree.md](../../../../skills/superplan/references/changing-the-tree.md) | 607 | 513 | −15% |
| [superplan/references/interactive-mode.md](../../../../skills/superplan/references/interactive-mode.md) | 562 | 473 | −16% |
| [superplan/references/planning-review.md](../../../../skills/superplan/references/planning-review.md) | 298 | 260 | −13% |
| [superimplement/SKILL.md](../../../../skills/superimplement/SKILL.md) | 1421 | 1218 | −14% |
| [superintegrate/SKILL.md](../../../../skills/superintegrate/SKILL.md) | 458 | 406 | −11% |
| [superintegrate/references/protect.md](../../../../skills/superintegrate/references/protect.md) | 305 | 279 | −9% |
| [superintegrate/references/sync.md](../../../../skills/superintegrate/references/sync.md) | 353 | 308 | −13% |
| [superintegrate/references/integrate.md](../../../../skills/superintegrate/references/integrate.md) | 536 | 494 | −8% |
| [superintegrate/references/finish.md](../../../../skills/superintegrate/references/finish.md) | 190 | 164 | −14% |
| [using-superra/references/main-agent.md](../../../../skills/using-superra/references/main-agent.md) | 996 | 901 | −10% |
| [using-superra/references/codex-instructions.md](../../../../skills/using-superra/references/codex-instructions.md) | 329 | 282 | −14% |
| [agent-orchestration/SKILL.md](../../../../skills/agent-orchestration/SKILL.md) | 979 | 877 | −10% |
| [agent-orchestration/references/agent-teams.md](../../../../skills/agent-orchestration/references/agent-teams.md) | 1489 | 1096 | −26% |
| [agent-orchestration/references/parallel-dispatch.md](../../../../skills/agent-orchestration/references/parallel-dispatch.md) | 231 | 204 | −12% |
| [agent-orchestration/references/worktree-harness-fallback.md](../../../../skills/agent-orchestration/references/worktree-harness-fallback.md) | 445 | 359 | −19% |

Protocol preserved: every gate, stop point, status enum, commit-subject grammar, dispatch template, shell snippet, and structured table survives with its content intact. The `Stage:` values, seat-assignment structures, Codex tool map, and availability-routing rows are byte-identical. `tests/harness-instruction-following` passes 126/126 (verified before and after).

[main-agent.md §Workflow Map](../../../../skills/using-superra/references/main-agent.md) is compressed rather than deleted: the phase model — PLAN → IMPLEMENT → INTEGRATE with the one-line ownership statement per phase skill — has no other agent-loaded home on this branch, since the earlier v0.4 restyle (`2e1fbdaa`) removed `using-superra/SKILL.md` §Runtime Workflow Map. Kept in `main-agent.md` rather than reinstated in `using-superra/SKILL.md` so it stays out of every subagent's context; only main agents route on phase ownership.

Caveats:

- The lowest-Δ files (integrate.md −8%, protect.md −9%, main-agent.md −10%, agent-orchestration/SKILL.md −10%, superintegrate/SKILL.md −11%) are step-routing and template files whose surviving prose is mostly section names, return-path routing, and cited anchors. They took two or three compression passes; a further one would start cutting routing content.
- [agent-teams.md](../../../../skills/agent-orchestration/references/agent-teams.md) is marked ARCHIVED and instructs agents not to load or cite it, so its restyle changes no agent behavior. Deleting the file is the cheaper end state — flagged, not acted on, since the sweep's contract is restyle-only.
- `tests/harness-instruction-following/load_contract.json` documents `source_paths` with line ranges that no test asserts; several were already stale before this pass (it cites `agent-orchestration/SKILL.md#L203-L219` in a 123-line file and `codex-instructions.md#L64-L77` in a 58-line file). This pass shifted two more (`agent-orchestration/SKILL.md#L50-L85`, `codex-instructions.md#L64-L77`). Left untouched — a whole-file re-anchoring pass is its own concern.

### Group 2 — task-tree and utility skills

15 files restyled, prose-only counts as in Group 1.

| File | Before | After | Δ |
|---|---:|---:|---:|
| [task-tree/SKILL.md](../../../../skills/task-tree/SKILL.md) | 380 | 344 | −9% |
| [task-tree/references/commands.md](../../../../skills/task-tree/references/commands.md) | 592 | 493 | −17% |
| [task-tree/references/task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md) | 1528 | 1368 | −10% |
| [task-tree/references/internals.md](../../../../skills/task-tree/references/internals.md) | 2276 | 2076 | −9% |
| [report-in-markdown/SKILL.md](../../../../skills/report-in-markdown/SKILL.md) | 635 | 558 | −12% |
| [report-in-markdown/references/baseline-io.md](../../../../skills/report-in-markdown/references/baseline-io.md) | 262 | 230 | −12% |
| [report-in-markdown/references/rich-content.md](../../../../skills/report-in-markdown/references/rich-content.md) | 184 | 181 | −2% |
| [result-protection/SKILL.md](../../../../skills/result-protection/SKILL.md) | 141 | 132 | −6% |
| [result-protection/references/drift-test-quality.md](../../../../skills/result-protection/references/drift-test-quality.md) | 445 | 427 | −4% |
| [semantic-merge/SKILL.md](../../../../skills/semantic-merge/SKILL.md) | 1596 | 1443 | −10% |
| [semantic-merge/references/workflow-sync-author.md](../../../../skills/semantic-merge/references/workflow-sync-author.md) | 562 | 488 | −13% |
| [semantic-merge/references/workflow-sync-reviewer.md](../../../../skills/semantic-merge/references/workflow-sync-reviewer.md) | 379 | 350 | −8% |
| [semantic-merge/references/standalone-merge.md](../../../../skills/semantic-merge/references/standalone-merge.md) | 328 | 286 | −13% |
| [refactor-and-integrate/SKILL.md](../../../../skills/refactor-and-integrate/SKILL.md) | 1632 | 1445 | −11% |
| [worktree-data-sync/SKILL.md](../../../../skills/worktree-data-sync/SKILL.md) | 766 | 737 | −4% |

Protocol preserved: the status enum and its ownership/transition rules, `depends_on` sibling-only semantics and the move/rename cascade rules, the maturation disposition menu and subsection menu, the semantic-coherence and drift-test gated checklists, the refactor triage boundaries and Final Diff Self-Check steps, every KaTeX render trap, and all CLI surfaces, flags, code blocks, and tables survive with content intact. `tests/harness-instruction-following` passes 126/126 (verified before and after). [load_contract.json](../../../../tests/harness-instruction-following/load_contract.json) carries ten line-anchored `source_paths` into five group-2 files — `refactor-and-integrate/SKILL.md#L16-L17` and `#L47-L58`, `result-protection/SKILL.md#L10-L23` and `#L16-L18`, `semantic-merge/SKILL.md#L12-L20`, `internals.md#L93-L95`, `#L113-L115`, `#L93-L115`, `task-file-contract.md#L23-L35` and `#L31-L35` — and none needed re-anchoring: every range still opens and closes on the same section or bullet it did at `556b4c49`. Only two of the five files changed length (`semantic-merge/SKILL.md` −2 lines, `internals.md` −2), and both deletions land below every range cited into them (line 24 and line 175, against ranges ending at L20 and L115). A later pass touching these files above those anchors must re-check them.

Two DRY deletions rather than compressions: [refactor-and-integrate/SKILL.md §Triage](../../../../skills/refactor-and-integrate/SKILL.md) dropped its "after approval, return to the researcher gate" sentence (§Apply the reviewed refactoring task already states the action boundary), and its checklist items on triage and base-current deletions now point at §Triage every hunk instead of restating it — the checklist's own intro says these are pass/fail points, not a restatement.

Caveats:

- The lowest-Δ files are the density floor, not a shallow pass: `rich-content.md` (−2%) is 181 prose words around four code blocks; `drift-test-quality.md` (−4%) is ~200 words of how-to plus a gated checklist that must survive verbatim; `worktree-data-sync/SKILL.md` (−4%) and `internals.md` (−9%) are CLI/flag reference whose prose is per-flag semantics with no rationale clauses left to cut. `refactor-and-integrate` and `semantic-merge` each took three passes to reach −11% / −10%.
- [handoff-doc/SKILL.md](../../../../skills/handoff-doc/SKILL.md) was skipped as the dispatch allows: it is a deprecated redirect whose whole body is a six-row ownership list plus one instruction line, already at the style.

### Group 3 — domain skills (econ-data-analysis, theory-modeling)

13 files restyled, prose-only counts as in Groups 1–2.

| File | Before | After | Δ |
|---|---:|---:|---:|
| [econ-data-analysis/SKILL.md](../../../../skills/econ-data-analysis/SKILL.md) | 1961 | 1685 | −14% |
| [econ-data-analysis/references/planning.md](../../../../skills/econ-data-analysis/references/planning.md) | 634 | 519 | −18% |
| [econ-data-analysis/references/integration.md](../../../../skills/econ-data-analysis/references/integration.md) | 616 | 529 | −14% |
| [econ-data-analysis/references/integrate-drift-tests.md](../../../../skills/econ-data-analysis/references/integrate-drift-tests.md) | 590 | 489 | −17% |
| [econ-data-analysis/references/data-robustness-checklist.md](../../../../skills/econ-data-analysis/references/data-robustness-checklist.md) | 330 | 263 | −20% |
| [econ-data-analysis/references/jupytext-guide.md](../../../../skills/econ-data-analysis/references/jupytext-guide.md) | 649 | 536 | −17% |
| [econ-data-analysis/references/julia-quarto-guide.md](../../../../skills/econ-data-analysis/references/julia-quarto-guide.md) | 410 | 332 | −19% |
| [econ-data-analysis/references/notebook-format.md](../../../../skills/econ-data-analysis/references/notebook-format.md) | 604 | 482 | −20% |
| [theory-modeling/SKILL.md](../../../../skills/theory-modeling/SKILL.md) | 2541 | 2178 | −14% |
| [theory-modeling/references/planning.md](../../../../skills/theory-modeling/references/planning.md) | 985 | 812 | −18% |
| [theory-modeling/references/integration.md](../../../../skills/theory-modeling/references/integration.md) | 2295 | 2054 | −11% |
| [theory-modeling/references/integrate-drift-tests.md](../../../../skills/theory-modeling/references/integrate-drift-tests.md) | 430 | 385 | −10% |
| [theory-modeling/references/objective-first.md](../../../../skills/theory-modeling/references/objective-first.md) | 696 | 633 | −9% |

Domain discipline preserved: every `[BLOCKING]` / `[ADVISORY]` item survives with its severity and content — the econ Iron Law, Describe/Analyze/Validate items, all eight §Pitfalls operation subsections, and the theory Iron Law, four gates, both falsification tests with their worked examples, and both hard gates (Data Inventory, Model Inventory / Assumption Map) including their `<HARD-GATE>` blocks. Diagnostic thresholds (p1/p99, 1-5% / 5-10% / `1e-8`–`1e-6` tolerances, the half-page mask window), slot templates, and every table are unchanged in content. One fenced block was edited: the instruction paragraph embedded in the Model Inventory skeleton at [theory planning.md:47-49](../../../../skills/theory-modeling/references/planning.md#L47-L49), compressed as prose — the skeleton's headings and tables are byte-identical. Of the dropped fragments, checklist item 4 carries the `r` and `beta` glosses (interest rate, discount factor); `w` survives only as a bare conventional-symbol example in the skeleton, no longer glossed anywhere in the file. "Skip further justification" is carried by the surviving "may leave it as \"conventional\"". Every other code block is byte-identical. `tests/harness-instruction-following` passes 126/126 (verified before and after).

Three DRY deletions rather than compressions: [econ-data-analysis/SKILL.md](../../../../skills/econ-data-analysis/SKILL.md) §Key References dropped its `notebook-format.md` and `data-robustness-checklist.md` rows (§Stage-Scoped References is the load map) and its opening body-contents line; [econ integration.md](../../../../skills/econ-data-analysis/references/integration.md) dropped §Reviewer verdict protocol, whose one line restated the header's "load both skills at the `integration` stage"; [notebook-format.md](../../../../skills/econ-data-analysis/references/notebook-format.md) dropped the paragraph arguing why the major/minor decision split is load-bearing, folding its operative content into the two bullets it explained. [jupytext-guide.md](../../../../skills/econ-data-analysis/references/jupytext-guide.md) §Why percent format was deleted as pure rationale; its two behavior-bearing claims (same syntax both languages, file runs as script and converts to notebook) moved to the opening line.

Epistemic hedges that carry a decision branch are protocol content, not filler, and survive in both domains' `integrate-drift-tests.md`: the failure-attribution rule stays qualified ("a failure matching one of these is usually the refactor, not the result — confirm before updating anything") so a pattern-matched failure stays inside [drift-test-quality.md](../../../../skills/result-protection/references/drift-test-quality.md)'s three-way classification, including the meaningfully-shifted-result branch; the weak-candidate lists stay "usually skip" rather than "skip", leaving the selection heuristic to the researcher's judgment.

Two headings renamed away from "cross-cutting" (a retired phrasing): `Cross-Cutting Integrity Rules` → `Generic Integrity Rules` in econ `integrate-drift-tests.md`, and `Cross-cutting integrity Red Flags` → `Generic Integrity Red Flags` in theory `integrate-drift-tests.md`. Both point at `drift-test-quality.md` §Cross-cutting Red Flags, whose own title is unchanged; no live cross-reference targets either renamed heading (only a historical entry in [docs/plans/2026-04-23-improve-design-principle-results.md](../../../../docs/plans/2026-04-23-improve-design-principle-results.md) mentions the old econ name). No other heading was renamed — `## Why Not Jupytext` in [julia-quarto-guide.md](../../../../skills/econ-data-analysis/references/julia-quarto-guide.md) keeps its title, since the section argues the prohibition rather than merely naming it.

Caveats:

- The three lowest-Δ files are at their density floor. [theory-modeling/references/integration.md](../../../../skills/theory-modeling/references/integration.md) (−11%, two passes) is four principle → identification-protocol → checklist blocks where the protocol and checklist deliberately state the same rule at detection and pass/fail granularity; collapsing that overlap would delete `[BLOCKING]` items, so the pass compressed within the items instead. [theory-modeling/references/integrate-drift-tests.md](../../../../skills/theory-modeling/references/integrate-drift-tests.md) (−11%) is a five-row tolerance table plus two candidate lists. [objective-first.md](../../../../skills/theory-modeling/references/objective-first.md) (−9%) is ~190 words of quoted exhibit material (the goal-statement example and the two held-out drill snippets) that must survive verbatim to be drillable; against the ~505 non-exhibit words the cut is ~12%.
- [load_contract.json](../../../../tests/harness-instruction-following/load_contract.json) carries four line-anchored `source_paths` into group-3 files, and this pass shifted all four by the two lines the deleted body-contents / "Domain skill for…" openers occupied: `econ-data-analysis/SKILL.md#L11-L22` and `#L130-L133`, `theory-modeling/SKILL.md#L11-L22` and `#L17-L19`. Each still lands on the Stage-Scoped References table or the merges/joins bullets it was cut from, and no test asserts them. Left untouched, consistent with Group 1 — re-anchoring `load_contract.json` whole-file is its own concern.

### Group 4 — writing and slide-design domain skills

24 files restyled, prose-only counts as in Groups 1–3.

| File | Before | After | Δ |
|---|---:|---:|---:|
| [writing/SKILL.md](../../../../skills/writing/SKILL.md) | 833 | 731 | −12% |
| [writing/references/style.md](../../../../skills/writing/references/style.md) | 2600 | 2293 | −12% |
| [writing/references/structure.md](../../../../skills/writing/references/structure.md) | 1617 | 1417 | −12% |
| [writing/references/refactor-and-compile.md](../../../../skills/writing/references/refactor-and-compile.md) | 1046 | 918 | −12% |
| [writing/references/review.md](../../../../skills/writing/references/review.md) | 876 | 776 | −11% |
| [writing/references/polish.md](../../../../skills/writing/references/polish.md) | 792 | 724 | −9% |
| [writing/references/draft.md](../../../../skills/writing/references/draft.md) | 424 | 382 | −10% |
| [writing/references/integration.md](../../../../skills/writing/references/integration.md) | 446 | 412 | −8% |
| [writing/references/long-form-review.md](../../../../skills/writing/references/long-form-review.md) | 333 | 286 | −14% |
| [writing/references/planning.md](../../../../skills/writing/references/planning.md) | 299 | 280 | −6% |
| [consistency/terminology.md](../../../../skills/writing/references/consistency/terminology.md) | 843 | 701 | −17% |
| [consistency/cross-references.md](../../../../skills/writing/references/consistency/cross-references.md) | 716 | 611 | −15% |
| [consistency/code-paper.md](../../../../skills/writing/references/consistency/code-paper.md) | 854 | 733 | −14% |
| [consistency/citations.md](../../../../skills/writing/references/consistency/citations.md) | 772 | 683 | −12% |
| [consistency/math.md](../../../../skills/writing/references/consistency/math.md) | 812 | 712 | −12% |
| [consistency/argument-logic.md](../../../../skills/writing/references/consistency/argument-logic.md) | 897 | 798 | −11% |
| [consistency/notation.md](../../../../skills/writing/references/consistency/notation.md) | 619 | 552 | −11% |
| [consistency/numerical.md](../../../../skills/writing/references/consistency/numerical.md) | 832 | 754 | −9% |
| [slide-design/SKILL.md](../../../../skills/slide-design/SKILL.md) | 1042 | 950 | −9% |
| [slide-design/references/layout-checks.md](../../../../skills/slide-design/references/layout-checks.md) | 432 | 371 | −14% |
| [slide-design/references/beamer-techniques.md](../../../../skills/slide-design/references/beamer-techniques.md) | 711 | 638 | −10% |
| [slide-design/references/planning.md](../../../../skills/slide-design/references/planning.md) | 287 | 259 | −10% |
| [slide-design/references/beamer-overlays.md](../../../../skills/slide-design/references/beamer-overlays.md) | 311 | 293 | −6% |
| [slide-design/references/integration.md](../../../../skills/slide-design/references/integration.md) | 182 | 172 | −5% |

Domain discipline preserved: every `[BLOCKING]` / `[ADVISORY]` item in all ten gated checklists (style, structure, refactor, compile, the eight consistency dimensions, writing integration, slide-design Quick Checklist) survives with its severity and content; slide-design's `\resizebox` prohibition survives in the Core Principle, the checklist item, `beamer-techniques.md §Layout Tools`, and `layout-checks.md` alike. The writing mode-routing and knowledge-file tables, the `Fix:` tier definitions and the sequence/set/force test with all four worked example pairs, the intent-comment priority chain, the four audience marker families with their replacement patterns, every Before/After exhibit in `style.md` and `structure.md`, the Chaubey/LRS page citations, the writing plan header template, the eight `consistency/*.md` output-format blocks, and every LaTeX/Beamer snippet are unchanged in content. `tests/harness-instruction-following` passes 126/126 (verified before and after).

Judgment-teaching prose was treated as content, not derivation, per the dispatch's caution class: the "Do NOT fire when" exception lists, the four-marker-family detection language, the tone-matching instruction in `draft.md`, and the hedge-calibration rules were compressed in wording only. Decision-carrying hedges survive — `terminology.md`'s "twenty to thirty terms is usually enough", `numerical.md`'s off-by-two "usually a filter ambiguity", `cross-references.md`'s "usually harmless leftovers", and slide-design's "one-line bullets are a strong default, not an absolute rule".

Four DRY deletions rather than compressions:

- The nine `Source dimensions harvested from \`draft-reviewer:*\`` provenance lines across the eight `consistency/*.md` files plus their two-file "multi-dimensional sweeps dispatch one reviewer per file in parallel" clause. The `draft-reviewer:*` agent specs do not exist anywhere in the repo (grep-verified), so the lines were dangling provenance carrying no behavior; the dispatch rule is owned by [review.md §Multi-lane reviews](../../../../skills/writing/references/review.md). `terminology.md` keeps its real Chaubey p. 76 / p. 157 citation, now standalone.
- [writing integration.md](../../../../skills/writing/references/integration.md) dropped its opening "no numerical drift tests of its own" line, whose content §Data-analysis-touching writing tasks already carried; the surviving section absorbed the one-clause claim.
- [refactor-and-compile.md](../../../../skills/writing/references/refactor-and-compile.md) dropped its two-bullet section-contents map (the §Refactor scope constraint moved into that section's opening line) and the Principle's restatement of the four Always items.
- [long-form-review.md §Review Task Tree](../../../../skills/writing/references/long-form-review.md) dropped its restatement of the artifact-under-review framing and per-task granularity, both owned by [planning.md §Review Task Trees](../../../../skills/writing/references/planning.md) and §Task Granularity one section below.

One render fix folded in: the two LaTeX error strings quoted in `refactor-and-compile.md §LaTeX-rendering hazards` (the missing-delimiter and display-math messages) are now backticked, clearing a pre-existing unclosed-inline-math warning on a line this pass rewrote.

Caveats:

- The four lowest-Δ files are checklist-and-bullet floors, not shallow passes: [slide-design integration.md](../../../../skills/slide-design/references/integration.md) (−5%) is 172 words of pure review bullets; [beamer-overlays.md](../../../../skills/slide-design/references/beamer-overlays.md) (−6%) is per-command semantics (`\only` vs `\visible` vs `overprint`); [writing planning.md](../../../../skills/writing/references/planning.md) (−6%) is a hard gate plus the review-only-tree protocol around a header template that must survive verbatim; [writing integration.md](../../../../skills/writing/references/integration.md) (−8%) is four gates plus eight checklist items. [style.md](../../../../skills/writing/references/style.md) (−12%, two passes) carries ~600 words of Before/After exhibit that must survive verbatim to be usable; against its ~1,700 non-exhibit words the cut is ~18%.
- [load_contract.json](../../../../tests/harness-instruction-following/load_contract.json) carries three line-anchored `source_paths` into group-4 files. `slide-design/SKILL.md#L11-L25` and `#L86-L92` still open and close on the same blocks (Stage-Scoped References; Layout Triage through Beamer Implementation). `writing/SKILL.md#L58-L86` shifted by the two lines deleted above it — it now opens inside §Before you start item 2 rather than on its heading, and closes on the §Coupling heading rather than the end of the knowledge-file table. No test asserts it; left untouched, consistent with Groups 1 and 3.
- `skills/writing/CLAUDE.md` was out of scope per the dispatch (contributor doc). Its Reference-ownership list still matches the restyled files' section ownership, so no follow-up is pending there.

Remaining for later groups: the `using-superra`/`superintegrate` references not listed in Groups 1–4.
