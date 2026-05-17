# REVIEW.md → PLAN.md Two-Stage Lifecycle Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. This is skill-design work on `skills/writing/` — load `superRA:writing` for context but treat the work as skill creation per `superRA-dev/CLAUDE.md §Contributor Discipline` (DRY/Necessity tests, anti-pattern checks, behavior-shaping-only instructions). Steps use checkbox syntax for tracking and cross-session handoff. The authoritative design spec for this work lives in `~/.claude/plans/currently-review-md-is-not-fancy-stream.md` — PLAN.md is the execution tracker; the plan file is the design spec.

**Objective:** Redesign `REVIEW.md` so it is a proper handoff doc the standard superRA implementation workflow runs against unchanged. Two-stage lifecycle in one file that gets renamed at the gate: Stage 1 collects findings (REVIEW.md, parallel reviewer dispatch); Stage 2 is the actionable polish plan (`git mv REVIEW.md PLAN.md` + inline rewrite). No separate POLISH.md, no separate RESULTS.md for review work.

**Methodology:** Edit four files in `skills/writing/` to specify the two-stage flow, the per-finding `**User feedback:**` field, the `## Findings` header section created at rename, the Stage-2 task-granularity rule (1 authorial = 1 task; mech/conventional batched by issue class), and the `## Workflow Status` rollup. Supersede the prior "REVIEW.md never renames to PLAN.md" rule in `writing/CLAUDE.md` in place per inline-edit discipline. Verify the new design works against canonical `agents/implementer.md` / `agents/reviewer.md` protocols without per-stage adapter prose.

**Domain vertical:** Skill design (not a currently-implemented superRA domain vertical). No domain hard gate. The work composes the writing skill add-on with the agent-orchestration dispatch templates and the handoff-doc anatomy; all three are loaded.

**Output:** Updated `skills/writing/references/long-form-review.md`, `skills/writing/references/polish.md`, `skills/writing/SKILL.md`, `skills/writing/CLAUDE.md`. No new files.

**Expected results:** A long-form review can be invoked standalone or as part of a polish workflow, and a fresh implementer/reviewer pair can pick up the resulting REVIEW.md (Stage 1) or PLAN.md (Stage 2) and execute against it using the canonical agent protocols with no special instructions.

**Sensitivity / verification:** Mock-dispatch trace through both stages end-to-end against the canonical agent specs; cross-doc grep for stragglers describing the old shape or the old "no rename" rule.

**Pipeline:** N/A — skill-edit work, no scripts.

---

## Workflow Status

- [x] **Plan approved** — researcher signed off on this plan
- [ ] **Execution complete** — all tasks `APPROVED`, mock-dispatch trace clean
- [ ] **Drift tests created** — N/A for skill-design work (auto-satisfied at Protect)
- [ ] **Integrated** — integration reviewer `APPROVED` on `BASE_HEAD_SHA..HEAD` after Sync
- [ ] **Docs finalized** — RESULTS.md matured, project docs audited, doc-reviewer `APPROVED`
- [ ] **Finished** — branch landed, PR opened, or requested cleanup completed

---

## Project Conventions

Walked at planning time (2026-05-16). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at 3e4bf62): Contributor guide for superRA internals. Mandates: read owning files before editing; change one concern at a time; describe the problem in commit messages; verify behavior not just prose; preserve user-facing/internal separation. Internal design philosophy: adaptive composable workflows (mechanisms over contingency trees, re-entry is normal), minimal targeted instructions (place where loaded, load only what's needed, prefer positive instructions), teach-the-protocol-don't-prescribe-each-action (DRY + Necessity gate on every line, anti-patterns: wrapper instructions, "here is what you will receive" descriptions, reminders of harness defaults, restating Skill-Load Manifest). Ownership-boundaries table assigns one source of truth per concern. Codex/harness design: canonical instructions stay shared; harness differences live in adapters; generated artifacts stay generated.
- `/AGENTS.md`: Alias for `/CLAUDE.md`.
- `/README.md`: User-facing product model — read for context, not edited here.

### Module-level docs walked
- `skills/writing/CLAUDE.md` (HEAD at 2b78713): Contributor notes for the writing vertical. Records why this skill exists (clone-from-econ-data-analysis lesson), the principle (Preserve substance, polish prose), rules-are-additive framing, mode-not-phase routing, load-configuration-is-authority-grant, inline-directive convention (TODO = work; DO NOT EDIT = hands-off), intent-comments-in-file, reviewer-dispatch-invariants-leave-this-skill, multi-agent review-pattern decisions (orchestration-only reference; **shared doc is REVIEW.md not PLAN.md** ← this entry will be superseded in Task 3 in place per inline-edit discipline; no `consistency/proofreading.md`; no new `Stage:` value; fix tiers in every consistency output). Polish-mode triage decision. Stage-scoped references. Sources. Audience-awareness as upstream discipline. Writing-side contribution to `## Project Conventions` slot.
- `skills/writing/SKILL.md`: Three working modes (Review, Polish, Draft); preserve-substance-polish-prose principle; rules-are-additive framing; write-to-the-reader audience model; Project Conventions in the handoff doc / CLAUDE.md lifecycle ladder (REVIEW.md → PLAN.md → CLAUDE.md, ordered by permanence); mode routing table; knowledge files table; coupling to superRA workflows.
- `skills/handoff-doc/SKILL.md` + `references/plan-anatomy.md` + `references/results-anatomy.md`: Four document principles, inline-edit rule, stale-content checklist, User Decisions Log, full PLAN.md / RESULTS.md anatomy templates (read for execution discipline of this very plan and for Stage-2 PLAN.md shape Task 1 specifies).
- `skills/writing/references/long-form-review.md` (HEAD at 04844b1): Current spec for REVIEW.md — flat findings dump, per-aspect task blocks with findings in review-notes blockquote, `## Workflow Status` omitted, no `**User feedback:**`, no Stage-2 rewrite. This is the file Task 1 rewrites.
- `skills/writing/references/polish.md`: Polish mode workflow; §C "Review-findings list" describes shape-C apply behavior — Task 2 lightly reframes §C to acknowledge that polish input is now a Stage-2 task block when riding REVIEW.md.

### Not walked (not reachable from the planned diff)
- `skills/writing/references/consistency/*.md` — output formats stay stable; no edit needed beyond a global F-ID note in long-form-review.md (Task 1 confirms whether one rule covers all eight or per-file edits are needed).
- `agents/implementer.md`, `agents/reviewer.md` — read in Phase 1 for protocol verification; no edit needed (the design intentionally requires no protocol change).
- `skills/handoff-doc/references/plan-anatomy.md` — read for Stage-2 PLAN.md shape; no edit needed.

---

### Task 1: Rewrite long-form-review.md for two-stage REVIEW.md → PLAN.md flow
**Depends on:** *(none)*
**Review status:** APPROVED

**Script:** `skills/writing/references/long-form-review.md` (full rewrite of `## Doc convention` and `## Dispatch convention`; add new sections per design spec)
**Input:** Current `long-form-review.md` (HEAD at 04844b1); design spec at `~/.claude/plans/currently-review-md-is-not-fancy-stream.md`
**Output:** Rewritten `long-form-review.md` covering the full two-stage design

- [x] **Step 1: Rewrite the doc**

All sections landed: two-stage lifecycle in `## Doc convention` (Stage 1 REVIEW.md, F-ID rule, `**User feedback:**` field, four-move Stage 1 → Stage 2 rewrite, standalone-only rename rule, Stage 2 PLAN.md behavior); `## Workflow Status` templates for both stages with N/A notes; Stage-2 task granularity rule; `## Implementer / reviewer interaction walk-through` tracing all roles; global F-ID rule (one rule covers all eight outputs). Existing material preserved: multi-perspective deep mode, no reviewer-of-reviewer, parallel-dispatch from agent-orchestration, final summary block.

- [x] **Step 2: Self-check before commit**

Walked design spec §Design + §Implementer/reviewer interaction walk-through section by section — all load-bearing elements confirmed present. Applied DRY/Necessity test; removed one wrapper sentence ("Each stage uses canonical agent protocols without adapter prose") that described the section rather than shaping behavior. One rule covers all eight `consistency/<dim>.md` outputs — no per-file edits needed.



### Task 2: Update polish.md §C and SKILL.md lifecycle ladder sentence
**Depends on:** Task 1

**Script:** `skills/writing/references/polish.md` (light edit to §C); `skills/writing/SKILL.md` (one-sentence clarification in §Project Conventions in the handoff doc / CLAUDE.md)
**Input:** Updated `long-form-review.md` from Task 1
**Output:** Both files updated with minimal edits
**Review status:** APPROVED

- [x] **Step 1: polish.md §C reframe**

Rewrote §C opening sentence and added two paragraphs: one for the long-form-review pipeline case (Stage-2 task block, F-ID lookup, no re-batching) and one for the standalone case (raw findings list, apply per finding). Per-tier apply rules (`mechanical` / `conventional` / `authorial`) unchanged; the `In both cases` connector preserves them for both paths.

- [x] **Step 2: SKILL.md lifecycle ladder one-sentence clarification**

Added a clause after the three-rung ladder sentence noting that in the long-form-review pipeline the REVIEW.md → PLAN.md promotion is mechanical (a literal `git mv` at the Stage-2 gate, standalone-only), with a pointer to `long-form-review.md §Standalone-only rename rule` for the detail. Edit is one sentence, inline, no parallel old+new text.

- [x] **Step 3: Self-check before commit**

Both edits are inline — no "Update:" / "Revised:" / "Previously" framing, no strikethroughs. DRY/Necessity walk: pipeline paragraph in `polish.md §C` shapes behavior the implementer could not produce from `long-form-review.md` alone (that file specs orchestrator task construction; this file specs implementer apply behavior); the standalone paragraph preserves pre-existing behavior unambiguously. SKILL.md clause is one sentence pointing at `long-form-review.md` for detail — no duplication of that file's content. No anti-patterns found (no wrapper instructions, no "here is what you will receive" descriptions, no harness-default reminders).

> **Review notes (present only during active REVISE rounds):**


### Task 3: Update writing/CLAUDE.md contributor notes
**Depends on:** Task 1

**Script:** `skills/writing/CLAUDE.md` (supersede one prior entry in place; add new design-decision entries)
**Input:** Current `writing/CLAUDE.md` (HEAD at 2b78713); design spec at `~/.claude/plans/currently-review-md-is-not-fancy-stream.md` §Files-to-change
**Output:** CLAUDE.md with the prior "no rename" rule superseded in place and new design entries appended in the long-form-review section

- [x] **Step 1: Supersede the "REVIEW.md never renames to PLAN.md" rule in place**

Rewrote the "Shared doc is REVIEW.md, not PLAN.md" bullet in `## Multi-agent review pattern` in place. The collision concern is preserved as the load-bearing reason; the resolution (standalone-only rename, with workflow-embedded reviews staying in the workflow's own PLAN.md) replaces the old rule. Cross-link to `references/long-form-review.md §Standalone-only rename rule` and a future-contributor re-litigation guard added. No parallel old+new entry stacked.

- [x] **Step 2: Append new design-decision entries**

Added `## Two-stage REVIEW.md → PLAN.md lifecycle` section after `## Multi-agent review pattern` and before `## Polish-mode triage`. Five paragraphs: (a) two-stage over one-stage (assembled-view constraint, two rejected alternatives); (b) per-finding user-feedback granularity (tier-directive failure mode); (c) task-granularity rule (1 authorial = 1 task; mechanical/conventional batch by issue class); (d) `## Findings` header section vs. inlining (duplication risk, traceability for rejected/deferred findings); (e) rename rule cross-link to the superseded bullet. Each paragraph follows existing CLAUDE.md style: decision, load-bearing reason, re-litigation bar.

- [x] **Step 3: Self-check before commit**

Superseded entry is rewritten in place — no parallel entries, no strikethroughs. New section (a)–(e) records design history; no paragraph restates behavior already specified in `long-form-review.md` (that file carries the operative spec; CLAUDE.md carries the why). DRY/Necessity walk: every paragraph shapes what a contributor would propose after reading only `long-form-review.md`; none of the paragraphs restates spec behavior. Anti-pattern check: no wrapper instructions, no "here is what you will receive" text, no harness defaults.
**Review status:** REVISE

> **Review notes (present only during active REVISE rounds):**
>
> 1. **MAJOR — `skills/writing/CLAUDE.md:45` intro count is stale after in-place edit.** The introductory sentence still reads "Four design choices that future contributors should not re-litigate:" but the bullet list now contains five bullets (the new "REVIEW.md → PLAN.md rename at Stage 2 is the spec." bullet was added in place). Per repo inline-edit discipline (and the `handoff-doc/SKILL.md §Inline-Edit Rule` cited by Step 1), an inline edit that changes the list size must update the count in the same pass — stale enumerators are the same drift risk as parallel old+new entries. Fix: change "Four" to "Five" on line 45.
>
> 2. **MAJOR — `skills/writing/CLAUDE.md:61` paragraph (c) duplicates long-form-review.md spec content instead of recording design history.** The paragraph's example list ("all typos, all citation-format fixes, all cross-ref label cleanups, the terminology-variant collapse, the nominalization cluster") is a near-verbatim restatement of `long-form-review.md:40` ("e.g., all typos, all citation-format issues, all cross-ref label cleanups, terminology-variant collapse, nominalization cluster"). This is exactly the BLOCKING failure the dispatch flagged: CLAUDE.md is for design history (rejected alternatives + load-bearing why), not behavior the spec already owns. Additionally, unlike paragraphs (a), (b), and (d) — which each name an explicit rejected alternative — paragraph (c) does not name what the chosen granularity rule was chosen *against* (e.g., the rejected "batch by manuscript geography" alternative is only implicit in "not by where in the manuscript the findings sit"). Fix: rewrite (c) to (i) name the rejected alternative (batch by manuscript section / chapter / geography) explicitly as a parallel construction to (a), (b), (d), (ii) keep only the load-bearing why (author conversation per authorial finding; PR-friendly diffs and reviewable commit scopes from kind-of-fix batching), and (iii) drop the example list — readers needing the examples follow the cross-reference to `long-form-review.md §Stage-2 task granularity`.
**Depends on:** Task 1, Task 2, Task 3

**Script:** N/A (verification work — grep, walk, mock-trace)
**Input:** All edited files from Tasks 1-3
**Output:** Verification report inline in this task's review-notes blockquote; any straggler edits committed in this task

- [ ] **Step 1: Cross-doc grep for stragglers**

```bash
grep -rn "REVIEW.md" skills/ agents/ docs/ README.md AGENTS.md AGENT.md CLAUDE.md
```

```text
For every match, confirm consistency with: (a) the two-stage shape; (b) the
rename rule (REVIEW.md → PLAN.md at Stage 2 gate for standalone; no separate
REVIEW.md when workflow-embedded). Flag and fix any straggler describing the
old flat-findings shape or the old "REVIEW.md never renames" rule.
```

- [ ] **Step 2: Skill-text DRY/Necessity walk on long-form-review.md**

```text
Re-read `long-form-review.md` line by line. For each new instruction line added
in Task 1, ask: without this line, would the agent's behavior be unstable? If
no, delete it. Walk the repo `CLAUDE.md §Anti-patterns to watch for` list
(wrapper instructions, "here is what you will receive" descriptions, default
reminders, restated Skill-Load Manifest) — drop any violation found.
```

- [ ] **Step 3: Mock dispatch trace end-to-end**

```text
Walk an imagined long-form review against the rewritten spec:

  1. Orchestrator creates REVIEW.md with N per-aspect task blocks (one per
     dimension in scope).
  2. Orchestrator dispatches N parallel `superRA:reviewer` agents per
     `long-form-review.md §Dispatch convention`. Each reviewer reads its task,
     reviews the manuscript per its `consistency/<dim>.md` reference, writes
     findings (with global F-IDs) into the review-notes blockquote, sets Review
     status: IMPLEMENTED, commits.
  3. Main agent prompts user with the assembled findings; user gives per-finding
     accept / defer / reject. Main agent writes `**User feedback:**` per task,
     commits. Workflow Status box "User feedback recorded" flips.
  4. Orchestrator performs the four-move Stage-1 → Stage-2 rewrite in one atomic
     commit: `git mv REVIEW.md PLAN.md`; hoist findings to `## Findings`; delete
     per-aspect blocks; write Stage-2 task blocks per granularity rule. Flips
     "Plan approved."
  5. Orchestrator dispatches `superRA:implementer` for Stage-2 Task 2
     (mechanical — all typos). Implementer reads PLAN.md task block, sees
     `**Sources:** F2, F11, F19, F23`, looks them up in `## Findings`, loads
     polish.md, applies the typo sweep, commits, sets Review status: IMPLEMENTED.
  6. Orchestrator dispatches `superRA:reviewer` against the commit range. Reads
     the task block, the cited Findings, and the diff; APPROVE.
  7. Verify task runs build + xref check; APPROVED on green. Workflow Status box
     "Execution complete" flips.
  8. Main agent archives / deletes PLAN.md; flips "Finished."

At every step, confirm the agent reads only what `using-superra §Skill-Load
Manifest` + the role spec + REVIEW.md / PLAN.md itself say, with no extra
wiring needed. Any step that requires a special instruction not in the standard
agent protocol is a design failure — flag and fix in Task 1 before completing
Task 4.
```

- [ ] **Step 4: Compose-with-planning-workflow check**

```text
Confirm REVIEW.md riding a workflow still composes: when long-form review is
embedded in `planning-workflow → implementation-workflow → integration-workflow`,
the writing-side conventions ladder still resolves to PLAN.md (not REVIEW.md),
the workflow's own PLAN.md carries the rollup, and no separate REVIEW.md exists.
The rename rule is standalone-only by construction. Confirm `long-form-review.md`
states this explicitly.
```

- [ ] **Step 5: Commit verification report**

```text
Record the verification outcomes in this task's review-notes blockquote (one
line per check: PASS / FAIL with file:line or "fixed in Task 4 Step N"). Set
Review status: IMPLEMENTED and commit.
```

> **Review notes (present only during active REVISE rounds):**
