# Map: Surfaces Shaping What Agents Write (v0.3.3 baseline)

Hand-authored from a read-only exploration agent dispatch, 2026-08-01, against this worktree at commit `ec5a4897`. Line numbers drift as files change; section anchors are the durable reference.

## 1. Task-file contract (`task-tree/references/task-file-contract.md`)

The only conciseness word in the IMPLEMENT-phase contract is one adjective (:52): Stage 1 `## Results` is "the live findings record — terse, agent-facing." Never operationalized. The per-task results template (:67-91) enumerates five subsections with only "Omit subsections that do not apply" as a brake — a slot list read as a slot-filling contract. Economy language exists only at Stage 2 maturation (:59-63 Mature / Trim-to-pointer / Drop) — it arrives once, at the very end, after the text was written, reviewed, and rolled up. The only anti-duplication line (:97) is scoped to monitoring rollups. Stale-content rules (:36-44) govern currency, not volume. Gap: nothing answers "what does NOT belong in `## Results`."

## 2. report-in-markdown — the always-loaded style skill

Loaded by every implementer/reviewer dispatch; opening line: "Apply the rules below to any markdown you write." Contents: file-reference links, math, tables, raw HTML. Zero content-economy rules. Its one economy-adjacent rule is table sizing (:55): inline < ~15 rows, else link to the output file — the shape of the needed concision rule, existing for exactly one content type. **The highest-leverage empty slot in the repo: the one skill guaranteed present in every writing agent's context has no conciseness contract.**

## 3. Role-spec reporting instructions and the core tension

`implementer.md:44` (self-check): "`## Results` carr[ies] the major outcomes, numbers, caveats, and verification evidence, as the self-contained account `using-superra` §Task Interface requires." `:56`: "Every material finding I am about to report is already written into the task's `task.md`." Return side is tightly capped (:110-116: enum + SHA). Commit body = dispatch delta, "not a copy of `## Results`" (:106). Reviewer mirrors all three (`reviewer.md:26,60,113,117`).

`using-superra/SKILL.md` §Task Interface (:66-70): edit-in-place/no-log; doc-before-report; "Write the body sections you own as a self-contained account a reader can follow standalone."

**The diagnosed tension**: "self-contained account" is the only qualitative standard on results content and has no counterweight. (1) "Standalone" defeats point-over-copy — the reader who must not leave the file needs the upstream sample, method, numbers that parent/sibling files already carry; `task-tree-design.md:35` tells the planner "point over copy," nothing tells the implementer the same about results. (2) Self-containment is asserted at three altitudes simultaneously (leaf, parent rollup, matured narrative) — the same finding legitimately written three times. (3) Combined with "every material finding must be in the file" and no ceiling: write everything, in full, at every level. The file side is uncapped by construction; the return side is perfectly capped.

## 4. Objective/guidance economy rules (planner-owned only)

`task-tree-design.md` is the best-developed economy discipline in the repo — for planner prose only: :7 "Keep it short"; :9 rejection test ("a line belongs in the objective only if the reviewer should reject work that violates it"); :15 overflow valve; :17 sufficiency framing ("not to reproduce context that already lives there"); :21 guidance delete test; :33-44 point-over-copy ladder with :42 self-orienting-line bar; :63 right-sizing test. None of it applies to `## Results`. Remaining objective-side gaps: :88 scope-expansion rewrites mandate growth ("include the original durable context") with no trim counterpart; nothing sweeps a child objective restating its parent's conventions.

## 5. Main-agent conversation behavior — undefined boundary

`main-agent.md` has no instruction on what to say after a dispatch returns or how much task-file content to reproduce in chat. Its §Surfacing the Live Dashboard (:26-28) is the existing pointer-not-prose precedent, scoped to change notifications. `agent-orchestration` §Orchestrator Duties covers agent↔agent adjudication; the agent→user leg is unwritten. The one explicit instruction invites re-narration — `superimplement/SKILL.md:125-127`:

```
Work complete and verified. Here are the results summary:
<summarize the results>
```

Unbounded, at the moment the orchestrator's context is fullest. The subagent→orchestrator boundary (enum + SHA) was never extended one hop further.

## 6. Live evidence — what actually makes files long

- **Triple-written result (showcase)**: mean |α|, GRS statistics, and the small-growth exception each appear in `showcase-analysis/task.md`, `02-analysis/task.md` (multiple times: results, tables, a validation checklist restating its own numbers), and `03-writeup/task.md`; figure captions duplicated verbatim across files. `03-writeup`'s objective even says "link down... rather than restating every number" — and the result restates the verdict table anyway. A reader needs ~25 lines of the 118-line `## Results`. This subtree is the docs-site showcase, so it teaches the norm.
- **Stage accretion (`econ-data-efficiency/task.md`, folded into `econ-data-analysis/SKILL.md` and the `0.3.4` release notes)**: `## Results` = implement findings + `### Integration protection` (duplicating the protect commit body) + `### Integration fit` + `**Final diff self-check**` (mandated by `refactor-and-integrate:91`, `[BLOCKING]` if missing per :97) — process telemetry useful for one review round, permanently resident.
- **Four-way duplicated verification counts**: the same test-suite numbers in child, parent, grandparent, and an unrelated sibling task file; plus a round-by-round `Revision:` log surviving review despite the no-log rule.
- **Changelog-style leaf (`task-tree/dashboard/task.md`)**: six "what shipped" bullets + per-feature subsections, duplicating its parent's and `docs-site`'s descriptions of the same capabilities.
- **The counter-example that works**: `task-tree/task.md` (35 lines) — four one-line child summaries with links, one design decision, one verification line. Concise rollup is achievable under today's rules; it is just not required.

## 7. Ranked diagnosis

1. "Self-contained account" is the only content standard on `## Results` and has no counterweight (checked by both roles; contradicts point-over-copy).
2. No conciseness/exclusion rule exists anywhere for `## Results`; `report-in-markdown` (always loaded) has zero economy content.
3. One-sided gates: "thin results" fails a gate (`superimplement:107`), ledgers/figures/comparisons are mandated — no symmetric gate for bloat/duplication. Every incentive points one direction.
4. Stage accretion: each phase appends a permanent section; the only compaction step (maturation) fires once at the very end.
5. Parent rollups are additive ("roll it up selectively") with no strictly-shorter or link-don't-restate requirement.
6. The orchestrator→user boundary is undefined; `<summarize the results>` invites re-narration.
7. Objectives grow monotonically on scope expansion; planning telemetry lands in `### Context`.
8. The exemplars (showcase, docs) teach the wrong norm.
9. No mechanism detects cross-file duplication; hooks check render integrity and structure only. (`refactor-and-integrate:54-58` has exactly the right eye — "a procedure or passage repeated across the work → state it once" — scoped to code diffs at INTEGRATE, never turned on the task tree.)

## 8. Files to change for the concise-writing + no-duplication contract

**Tier 1 (define what gets written)**: `using-superra/SKILL.md` §Task Interface :66-70 (rebalance "self-contained"); `task-file-contract.md` §Results Shape (operationalize "terse", exclusion guidance, demote template, generalize :97, move trim-to-pointer instinct to write time); `report-in-markdown/SKILL.md` (add the economy section; generalize the table threshold); role skills' self-check items (symmetric economy item).

**Tier 2 (stage accretion, rollups)**: `superimplement/SKILL.md` :77 :107 :126-127; `refactor-and-integrate/SKILL.md` :91 :97 (self-check trail → commit body); `superintegrate/references/protect.md:31` (no re-narration); `mature-consolidate.md:28`; `superplan/references/consolidation.md` (add volume/duplication symptom).

**Tier 3 (conversation)**: `main-agent.md` (add reporting-to-researcher section); `agent-orchestration` §Orchestrator Duties; `interactive-mode.md:20`.

**Tier 4 (planner)**: `task-tree-design.md:88` trim counterpart.

**Tier 5 (exemplars/docs — deferred out of v0.4 scope)**: showcase task files + `docs/showcase-fixtures/**`; `docs/site` quickstart/task-file pages; hygiene of this repo's own tree (`task-tree/dashboard`, `interactive-mode` subtree — `econ-data-efficiency` since folded into `econ-data-analysis/SKILL.md` and the `0.3.4` release notes, so no longer applicable here).
