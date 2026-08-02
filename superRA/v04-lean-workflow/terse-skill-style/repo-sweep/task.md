---
title: "Repo Sweep: Restyle Remaining Skill Prose to the Terse Style"
status: revise
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
| [econ-data-analysis/SKILL.md](../../../../skills/econ-data-analysis/SKILL.md) | 1961 | 1680 | −14% |
| [econ-data-analysis/references/planning.md](../../../../skills/econ-data-analysis/references/planning.md) | 634 | 519 | −18% |
| [econ-data-analysis/references/integration.md](../../../../skills/econ-data-analysis/references/integration.md) | 616 | 529 | −14% |
| [econ-data-analysis/references/integrate-drift-tests.md](../../../../skills/econ-data-analysis/references/integrate-drift-tests.md) | 590 | 485 | −18% |
| [econ-data-analysis/references/data-robustness-checklist.md](../../../../skills/econ-data-analysis/references/data-robustness-checklist.md) | 330 | 263 | −20% |
| [econ-data-analysis/references/jupytext-guide.md](../../../../skills/econ-data-analysis/references/jupytext-guide.md) | 649 | 536 | −17% |
| [econ-data-analysis/references/julia-quarto-guide.md](../../../../skills/econ-data-analysis/references/julia-quarto-guide.md) | 410 | 331 | −19% |
| [econ-data-analysis/references/notebook-format.md](../../../../skills/econ-data-analysis/references/notebook-format.md) | 604 | 482 | −20% |
| [theory-modeling/SKILL.md](../../../../skills/theory-modeling/SKILL.md) | 2541 | 2169 | −15% |
| [theory-modeling/references/planning.md](../../../../skills/theory-modeling/references/planning.md) | 985 | 812 | −18% |
| [theory-modeling/references/integration.md](../../../../skills/theory-modeling/references/integration.md) | 2295 | 2054 | −11% |
| [theory-modeling/references/integrate-drift-tests.md](../../../../skills/theory-modeling/references/integrate-drift-tests.md) | 430 | 381 | −11% |
| [theory-modeling/references/objective-first.md](../../../../skills/theory-modeling/references/objective-first.md) | 696 | 633 | −9% |

Domain discipline preserved: every `[BLOCKING]` / `[ADVISORY]` item survives with its severity and content — the econ Iron Law, Describe/Analyze/Validate items, all nine §Pitfalls operation subsections, and the theory Iron Law, four gates, both falsification tests with their worked examples, and both hard gates (Data Inventory, Model Inventory / Assumption Map) including their `<HARD-GATE>` blocks. Diagnostic thresholds (p1/p99, 1-5% / 5-10% / `1e-8`–`1e-6` tolerances, the half-page mask window), slot templates, the Model Inventory markdown skeleton, and every code block and table are unchanged in content. `tests/harness-instruction-following` passes 126/126 (verified before and after).

Three DRY deletions rather than compressions: [econ-data-analysis/SKILL.md](../../../../skills/econ-data-analysis/SKILL.md) §Key References dropped its `notebook-format.md` and `data-robustness-checklist.md` rows (§Stage-Scoped References is the load map) and its opening body-contents line; [econ integration.md](../../../../skills/econ-data-analysis/references/integration.md) dropped §Reviewer verdict protocol, whose one line restated the header's "load both skills at the `integration` stage"; [notebook-format.md](../../../../skills/econ-data-analysis/references/notebook-format.md) dropped the paragraph arguing why the major/minor decision split is load-bearing, folding its operative content into the two bullets it explained. [jupytext-guide.md](../../../../skills/econ-data-analysis/references/jupytext-guide.md) §Why percent format was deleted as pure rationale; its two behavior-bearing claims (same syntax both languages, file runs as script and converts to notebook) moved to the opening line.

Two headings renamed away from "cross-cutting" (a retired phrasing): `Cross-Cutting Integrity Rules` → `Generic Integrity Rules` in econ `integrate-drift-tests.md`, and `Cross-cutting integrity Red Flags` → `Generic integrity Red Flags` in theory `integrate-drift-tests.md`. Both point at `drift-test-quality.md` §Cross-cutting Red Flags, whose own title is unchanged; no live cross-reference targets either renamed heading (only a historical entry in [docs/plans/2026-04-23-improve-design-principle-results.md](../../../../docs/plans/2026-04-23-improve-design-principle-results.md) mentions the old econ name).

Caveats:

- The three lowest-Δ files are at their density floor. [theory-modeling/references/integration.md](../../../../skills/theory-modeling/references/integration.md) (−11%, two passes) is four principle → identification-protocol → checklist blocks where the protocol and checklist deliberately state the same rule at detection and pass/fail granularity; collapsing that overlap would delete `[BLOCKING]` items, so the pass compressed within the items instead. [theory-modeling/references/integrate-drift-tests.md](../../../../skills/theory-modeling/references/integrate-drift-tests.md) (−11%) is a five-row tolerance table plus two candidate lists. [objective-first.md](../../../../skills/theory-modeling/references/objective-first.md) (−9%) is ~190 words of quoted exhibit material (the goal-statement example and the two held-out drill snippets) that must survive verbatim to be drillable; against the ~505 non-exhibit words the cut is ~12%.
- [load_contract.json](../../../../tests/harness-instruction-following/load_contract.json) carries four line-anchored `source_paths` into group-3 files, and this pass shifted all four by the two lines the deleted body-contents / "Domain skill for…" openers occupied: `econ-data-analysis/SKILL.md#L11-L22` and `#L130-L133`, `theory-modeling/SKILL.md#L11-L22` and `#L17-L19`. Each still lands on the Stage-Scoped References table or the merges/joins bullets it was cut from, and no test asserts them. Left untouched, consistent with Group 1 — re-anchoring `load_contract.json` whole-file is its own concern.

Remaining for later groups: the `using-superra`/`superintegrate` references not listed in Groups 1–3.

## Review Notes

Scoped to Group 3 (`e18bfce4..37ecf4c6`). Verified independently: all `[BLOCKING]`/`[ADVISORY]`/`<HARD-GATE>`/`REVISE` marker counts and all `$$` display-math counts are identical per file before and after; every fenced code block except one (item 3) is byte-identical; the only markdown table reworded is theory §Common Rationalizations (meaning preserved); the four `load_contract.json` anchors still land on their cited content; no live cross-reference targets any renamed or deleted heading; prose-only word counts reproduce the reported deltas to the point; `tests/harness-instruction-following` 126/126 (uv is sandbox-blocked here, re-run outside the sandbox).

1. **MAJOR — the drift-test failure-attribution rule lost its hedge in both domains, and now disagrees with `result-protection`'s three-way classification.** [econ integrate-drift-tests.md:57](../../../../skills/econ-data-analysis/references/integrate-drift-tests.md#L57) now reads "A failure matching one of these: the test is right, the refactor is the cause"; the pre-pass text was "the test is almost certainly correct and the refactor is almost certainly the cause." [theory integrate-drift-tests.md:53](../../../../skills/theory-modeling/references/integrate-drift-tests.md#L53) made the same cut from "usually correct … usually the cause." [drift-test-quality.md:37](../../../../skills/result-protection/references/drift-test-quality.md#L37) makes it `[BLOCKING]` that a post-refactor failure is classified into one of three causes — broken change, too-tight tolerance, or a meaningfully shifted result needing a research conversation. The hedge is what kept a pattern-matched failure inside that classification; the flat assertion tells the agent the third branch is closed whenever the failure resembles a listed mode, which is exactly the silent-attribution path the red flag guards. Restore the epistemic qualifier in both files (e.g. "a failure matching one of these is usually the refactor, not the result — confirm before updating anything").

2. **MINOR — hedge-to-directive shift in the weak-candidate lists.** [econ integrate-drift-tests.md:22](../../../../skills/econ-data-analysis/references/integrate-drift-tests.md#L22) and [theory integrate-drift-tests.md:19](../../../../skills/theory-modeling/references/integrate-drift-tests.md#L19) turned "**Weak candidates** (probably skip)" into "(skip)". These are selection heuristics, not gates; the original left the researcher's judgment in play. Restore "usually skip" or equivalent, or state in `## Results` that the strengthening is intended.

3. **MINOR — a fenced template block was edited, and `## Results` says it was not.** The `## Results` Group 3 entry asserts "the Model Inventory markdown skeleton, and every code block and table are unchanged in content," but the note inside the fenced `markdown` skeleton at [theory planning.md:45-48](../../../../skills/theory-modeling/references/planning.md#L45-L48) was rewritten — the per-symbol glosses ("`r` for an interest rate, `beta` for a discount factor, `w` for a wage") and "and skip further justification" are gone. The tables in the skeleton are untouched and the meaning survives, so this is an accuracy fix in `## Results`, not necessarily a revert: state that the one edited fenced block is the skeleton's embedded instruction paragraph.

4. **MINOR — two undocumented or awkward heading edits.** [julia-quarto-guide.md:3](../../../../skills/econ-data-analysis/references/julia-quarto-guide.md#L3) renamed `## Why Not Jupytext` → `## Not Jupytext`; the rename is not recorded in `## Results` alongside the other three heading changes, and the new title no longer reads as a section that explains a prohibition. [theory integrate-drift-tests.md:56](../../../../skills/theory-modeling/references/integrate-drift-tests.md#L56) is now `## Generic integrity Red Flags` — mid-title lowercase "integrity" against the neighbouring `## Generic Integrity Rules`. Restore "Why Not Jupytext" (or a title that still signals the prohibition), fix the capitalization, and record the rename.

5. **MINOR — small content losses in `[BLOCKING]` items.** [econ-data-analysis/SKILL.md:36](../../../../skills/econ-data-analysis/SKILL.md#L36): the Panel structure item dropped "first priority for" and trimmed the ID examples from `(firm, fund, country, individual)` / `(year, quarter, month, day)` to three each — "individual" and "day" are not carried anywhere else and were the daily-frequency and micro-panel cues. [theory-modeling/SKILL.md:181](../../../../skills/theory-modeling/SKILL.md#L181): the Gate 4 artifact spec dropped "if any" from "the parameters used", so a non-numerical check (substitute back, limiting case) now reads as owing parameters it does not have. Restore the two examples and the "if any".

6. **MINOR — `## Results` says "all nine §Pitfalls operation subsections"; there are eight** ([econ-data-analysis/SKILL.md](../../../../skills/econ-data-analysis/SKILL.md), merges/time-series/reshaping/aggregations/deduplication/filtering/variable-construction/missing-data). Correct the count. Related: [theory-modeling/SKILL.md:71-74](../../../../skills/theory-modeling/SKILL.md#L71-L74) moved the "counts against the work like an algebra error" weight off "notation that fails this bar" and onto "shorthand left standing", so the new-symbol bar now ends at the unweighted "A symbol meeting neither is inlined." The Gate 1 `[BLOCKING]` item still enforces it — worth a line in `## Results` if the move was deliberate.
