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

Remaining for later groups: domain and utility skills, `task-tree`, `semantic-merge`, `result-protection`, `refactor-and-integrate`, and the remaining `using-superra`/`superintegrate` references not listed above.

## Review Notes

Scope: group 1 only (`5a74c4e2..5904f0f3`). Verdict **REVISE** for this group; frontmatter stays `in-progress` because groups 2–5 are outstanding.

Verified clean: heading sets across all 19 files are identical before/after except two removals (`main-agent.md §Workflow Map` — item 1 below — and `agent-orchestration §Overview`, which nothing cites and whose one sentence survives as the file's lede); every outgoing `§`-anchor from the changed files still resolves (`mature-consolidate.md` Steps 1–3, `semantic-merge §Scope the merge first`, `task-tree §CLI Setup`, `theory-modeling §Documentation and handoff`, `implement-task §Reporting`, `review-task §Review Protocol`, `task-companion-files §Promote`, `task-file-contract §Stale Content Checklist` / `§Results Shape`, `superplan §Agent Review` / `§Substantive Questions` / `§User Feedback and Changing the Task Tree`, `writing/references/integration.md`); no live file cites `main-agent.md §Workflow Map` or `agent-orchestration §Overview`; `tests/harness-instruction-following` reproduces 126/126; every prose word count in the Results table reproduces exactly under the stated fenced-code-and-table exclusion.

1. **MAJOR** — the `## Workflow Map` deletion in [main-agent.md](../../../../skills/using-superra/references/main-agent.md) rests on a premise that is false on this branch, and it removed the last agent-loaded statement of the phase model. `## Results` justifies it as "reproducing `using-superra/SKILL.md` §Runtime Workflow Map verbatim in the same skill, whose closing line already routes main agents to `main-agent.md` §Resuming Work". That section exists on `main` ([SKILL.md#L20](../../../../skills/using-superra/SKILL.md#L20) at `main`) but was already deleted from this branch's [using-superra/SKILL.md](../../../../skills/using-superra/SKILL.md) by the earlier v0.4 restyle (`2e1fbdaa`) — its heading list is now Communication / Commits / Task Interface / Skill-Load Manifest only, and there is no closing routing line. Grepping the branch, the PLAN → IMPLEMENT → INTEGRATE ordering and the one-line statement of what each phase skill owns now survive only in [README.md:26](../../../../README.md#L26), which no agent loads. The DRY gate does not fire against a copy that no longer exists. Either restore the section in `main-agent.md`, or restore §Runtime Workflow Map in `using-superra/SKILL.md` and keep the pointer — then correct the `## Results` paragraph, which currently asserts a duplicate that is not there. Note also that this deletion is ~88 of the 201 words `main-agent.md` lost; the file's real restyle Δ is about −12%, not the −20% in the table.
   → implemented: confirmed — this branch's [using-superra/SKILL.md](../../../../skills/using-superra/SKILL.md) heading list is Communication / Commits / Task Interface / Skill-Load Manifest, with no §Runtime Workflow Map and no routing line. Restored the map in [main-agent.md](../../../../skills/using-superra/references/main-agent.md) as a compact three-bullet `## Workflow Map` (phase order + one line of ownership per phase skill, closing on the re-entry pointer to §Resuming Work) rather than reinstating it in `using-superra/SKILL.md`: `using-superra/SKILL.md` loads into every dispatched subagent, and phase ownership is main-agent routing knowledge that no implementer or reviewer acts on. `## Results` corrected — the false-duplicate claim replaced with this placement rationale, and the table row now reads 996 → 901 (−10%).

2. **MAJOR** — [sync.md:3](../../../../skills/superintegrate/references/sync.md#L3) dropped the commit-verb mapping for a dispatched sync. The original opener carried two grammar facts: "A dispatched sync (its own `Stage: sync`) commits under the `sync` stage verb; an inline sync lands as `integrate(sync): …`". The rewrite keeps only the inline half and describes the non-trivial path purely as a `Stage:` value, which is a dispatch field, not a commit verb. `using-superra` §Commits lists `sync` among the workflow verbs but never says which sync path uses it, so an agent following the surviving text can reasonably land a dispatched sync as `integrate(sync)`. Restore the dispatched-sync verb. This also makes the `## Results` sentence "every gate, stop point, status enum, commit-subject grammar … survives with its content intact" inaccurate as written.
   → implemented: restored both halves of the grammar in the opener — a non-trivial sync "is dispatched under its own `Stage: sync`, commits under the `sync` stage verb", against the trivial path's `integrate(sync): …` ([sync.md:3](../../../../skills/superintegrate/references/sync.md#L3)). The commit-subject-grammar claim in `## Results` now holds; row updated to 353 → 308 (−13%).

3. **MINOR** — [agent-orchestration/SKILL.md](../../../../skills/agent-orchestration/SKILL.md) is the one file in the group where the −10% looks like the `daea6ae3` signature rather than a floor. Two edits removed the verb instead of a clause and left broken or non-instructing prose: [SKILL.md:95](../../../../skills/agent-orchestration/SKILL.md#L95) "The orchestrator's alone, at every workflow stage:" (was "Done by the orchestrator alone, …"), and [SKILL.md:16](../../../../skills/agent-orchestration/SKILL.md#L16) "The small-task structure in §Seat Assignment." (was "Use the small-task structure …"), which leaves a section body with no instruction. Meanwhile whole rationale clauses the style rule targets survived untouched: [SKILL.md:110](../../../../skills/agent-orchestration/SKILL.md#L110) "The reviewer graded severity by effect on the task's result; you hold the workflow context, so you decide when each fix lands" is pure derivation under a bold that already states the action, and [SKILL.md:38](../../../../skills/agent-orchestration/SKILL.md#L38) §Model Tier Selection is still a single run-on that the bullet form would compress. Fix the two grammar regressions and take the rationale clauses; the other three low-Δ files (integrate.md, protect.md, superintegrate/SKILL.md) do read at target density and need no further pass.
   → implemented: both verbs restored — "Done by the orchestrator alone, at every workflow stage:" ([SKILL.md:102](../../../../skills/agent-orchestration/SKILL.md#L102)) and "Use the small-task structure in §Seat Assignment." ([SKILL.md:16](../../../../skills/agent-orchestration/SKILL.md#L16)). Rationale clause cut: the schedule-fixes lead now reads "**Schedule accepted fixes against the whole workflow** — the reviewer graded severity by effect on the task's result alone", dropping the "you hold the workflow context, so you decide" derivation the bold already states ([SKILL.md:117](../../../../skills/agent-orchestration/SKILL.md#L117)). §Model Tier Selection split from one run-on into four step-up bullets ([SKILL.md:36-45](../../../../skills/agent-orchestration/SKILL.md#L36-L45)). Net Δ is unchanged at −10% because the two restored verbs and the bullet form add words back; the density gain is structural, not count-driven.

4. **MINOR** — [protect.md:3](../../../../skills/superintegrate/references/protect.md#L3) and [protect.md:14](../../../../skills/superintegrate/references/protect.md#L14) both dropped "existing" from the protection-mechanism wording ("or other existing mechanisms" → gone from the intro; "another existing mechanism appropriate to the artifact" → "another mechanism fitting the artifact"). The constraint was to select from mechanisms that already exist rather than invent one at Protect time. Restore the qualifier in the Step 2 bullet.
   → implemented: qualifier restored in both places — "or other existing mechanisms only where the researcher selects them" in the intro ([protect.md:3](../../../../skills/superintegrate/references/protect.md#L3)) and "another existing mechanism appropriate to the artifact" in the Step 2 bullet ([protect.md:14](../../../../skills/superintegrate/references/protect.md#L14)); row updated to 305 → 279 (−9%).
