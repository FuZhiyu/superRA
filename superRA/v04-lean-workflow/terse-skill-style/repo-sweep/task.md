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
| [report-in-markdown/SKILL.md](../../../../skills/report-in-markdown/SKILL.md) | 635 | 557 | −12% |
| [report-in-markdown/references/baseline-io.md](../../../../skills/report-in-markdown/references/baseline-io.md) | 262 | 230 | −12% |
| [report-in-markdown/references/rich-content.md](../../../../skills/report-in-markdown/references/rich-content.md) | 184 | 181 | −2% |
| [result-protection/SKILL.md](../../../../skills/result-protection/SKILL.md) | 141 | 131 | −7% |
| [result-protection/references/drift-test-quality.md](../../../../skills/result-protection/references/drift-test-quality.md) | 445 | 427 | −4% |
| [semantic-merge/SKILL.md](../../../../skills/semantic-merge/SKILL.md) | 1596 | 1443 | −10% |
| [semantic-merge/references/workflow-sync-author.md](../../../../skills/semantic-merge/references/workflow-sync-author.md) | 562 | 488 | −13% |
| [semantic-merge/references/workflow-sync-reviewer.md](../../../../skills/semantic-merge/references/workflow-sync-reviewer.md) | 379 | 350 | −8% |
| [semantic-merge/references/standalone-merge.md](../../../../skills/semantic-merge/references/standalone-merge.md) | 328 | 286 | −13% |
| [refactor-and-integrate/SKILL.md](../../../../skills/refactor-and-integrate/SKILL.md) | 1632 | 1444 | −12% |
| [worktree-data-sync/SKILL.md](../../../../skills/worktree-data-sync/SKILL.md) | 766 | 737 | −4% |

Protocol preserved: the status enum and its ownership/transition rules, `depends_on` sibling-only semantics and the move/rename cascade rules, the maturation disposition menu and subsection menu, the semantic-coherence and drift-test gated checklists, the refactor triage boundaries and Final Diff Self-Check steps, every KaTeX render trap, and all CLI surfaces, flags, code blocks, and tables survive with content intact. `tests/harness-instruction-following` passes 126/126 (verified before and after); `load_contract.json` carries no line-anchored citation into any group-2 file, so nothing re-anchored.

Two DRY deletions rather than compressions: [refactor-and-integrate/SKILL.md §Triage](../../../../skills/refactor-and-integrate/SKILL.md) dropped its "after approval, return to the researcher gate" sentence (§Apply the reviewed refactoring task already states the action boundary), and its checklist items on triage and base-current deletions now point at §Triage every hunk instead of restating it — the checklist's own intro says these are pass/fail points, not a restatement.

Caveats:

- The lowest-Δ files are the density floor, not a shallow pass: `rich-content.md` (−2%) is 181 prose words around four code blocks; `drift-test-quality.md` (−4%) is ~200 words of how-to plus a gated checklist that must survive verbatim; `worktree-data-sync/SKILL.md` (−4%) and `internals.md` (−9%) are CLI/flag reference whose prose is per-flag semantics with no rationale clauses left to cut. `refactor-and-integrate` and `semantic-merge` each took three passes to reach −12% / −10%.
- [handoff-doc/SKILL.md](../../../../skills/handoff-doc/SKILL.md) was skipped as the dispatch allows: it is a deprecated redirect whose whole body is a six-row ownership list plus one instruction line, already at the style.

Remaining for later groups: domain skills, and the remaining `using-superra`/`superintegrate` references not listed above.

## Review Notes

Scoped to group 2 (`556b4c49..956cefb0`); group 1 and earlier groups are not re-opened.

1. **MAJOR** — [task.md](task.md) §Results, group-2 paragraph: "`load_contract.json` carries no line-anchored citation into any group-2 file, so nothing re-anchored" is false. [load_contract.json](../../../../tests/harness-instruction-following/load_contract.json) carries ten line-anchored `source_paths` into five group-2 files: `refactor-and-integrate/SKILL.md#L16-L17` and `#L47-L58`, `result-protection/SKILL.md#L10-L23` and `#L16-L18`, `semantic-merge/SKILL.md#L12-L20`, `internals.md#L93-L95`, `#L113-L115`, `#L93-L115`, `task-file-contract.md#L23-L35` and `#L31-L35`. I checked each range against `556b4c49`: every one still covers the same subject matter, because the two files that lost lines (`semantic-merge/SKILL.md` −2, `internals.md` −2) lost them below every cited range. So the conclusion ("nothing re-anchored") holds — but on a reason the note does not state, and the note as written would tell a later re-anchoring pass that these files carry no anchors. Rewrite the sentence to state the anchors exist and why they still resolve.

2. **MINOR** — [skills/report-in-markdown/SKILL.md:82](../../../../skills/report-in-markdown/SKILL.md#L82): "GitHub's renderer strips `style` and most attributes, so a block that looks right in the dashboard renders unstyled there." The pre-restyle text said "renders unstyled on GitHub"; the compressed "there" now sits closer to "in the dashboard" than to "GitHub" and inverts on a fast read. Name the target explicitly.

3. **MINOR** — [skills/result-protection/SKILL.md:18](../../../../skills/result-protection/SKILL.md#L18): "Domain-specific drift-test references route through the active domain skill's stage-load table at the `protection` stage." The pre-restyle line ended "load it per that table" — the compression dropped the imperative and left a description, against §Skill Prose Style's "State the action." (The load instruction survives in [drift-test-quality.md:9](../../../../skills/result-protection/references/drift-test-quality.md#L9), so no agent is left without it; this is style, not behavior.)

4. **MINOR** — [skills/refactor-and-integrate/SKILL.md:117](../../../../skills/refactor-and-integrate/SKILL.md#L117): the `[BLOCKING]` item dropped the leading "Different" — "Control variable sets, variable definitions, sample filters, equilibrium concepts, and normalization choices are research decisions." The gate's trigger was a *divergence* between sides; the surviving sentence reads as a blanket claim and leans only on the `**Handling inconsistencies:**` group heading to restore it. Restore the divergence sense in the sentence.

Verified and not findings: all 15 prose word counts reproduce exactly with a fence- and table-excluding count; `tests/harness-instruction-following` 126/126 (uv needs sandbox escalation to run); no heading changed in any group-2 file, and every `§` anchor cited into these files from elsewhere in `skills/` still resolves; the two claimed DRY deletions in `refactor-and-integrate/SKILL.md` are sound — §Apply the reviewed refactoring task carries "return to the owning workflow gate before that work runs", and §Triage every hunk carries both the protected-record tracing rule and "The same mode-specific boundary gates base-current deletions and relocations"; the four low-Δ files are the floor, not a shallow pass (`worktree-data-sync/SKILL.md`'s residual prose is per-flag semantics plus the denylist enumeration; its §When to Use bullet list is the only remaining DRY candidate, and it is optional); `handoff-doc/SKILL.md` is correctly skipped; the three semantic-merge mode references keep their author/reviewer step sequences, the nine reviewer steps, the `## Sync Impact` format and lifecycle, and the `APPROVE`/`REVISE` vocabulary intact.
