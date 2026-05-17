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
**Review status:** IMPLEMENTED

**Script:** `skills/writing/references/long-form-review.md` (full rewrite of `## Doc convention` and `## Dispatch convention`; add new sections per design spec)
**Input:** Current `long-form-review.md` (HEAD at 04844b1); design spec at `~/.claude/plans/currently-review-md-is-not-fancy-stream.md`
**Output:** Rewritten `long-form-review.md` covering the full two-stage design

- [x] **Step 1: Rewrite the doc**

All sections landed: two-stage lifecycle in `## Doc convention` (Stage 1 REVIEW.md, F-ID rule, `**User feedback:**` field, four-move Stage 1 → Stage 2 rewrite, standalone-only rename rule, Stage 2 PLAN.md behavior); `## Workflow Status` templates for both stages with N/A notes; Stage-2 task granularity rule; `## Implementer / reviewer interaction walk-through` tracing all roles; global F-ID rule (one rule covers all eight outputs). Existing material preserved: multi-perspective deep mode, no reviewer-of-reviewer, parallel-dispatch from agent-orchestration, final summary block.

- [x] **Step 2: Self-check before commit**

Walked design spec §Design + §Implementer/reviewer interaction walk-through section by section — all load-bearing elements confirmed present. Applied DRY/Necessity test; removed one wrapper sentence ("Each stage uses canonical agent protocols without adapter prose") that described the section rather than shaping behavior. One rule covers all eight `consistency/<dim>.md` outputs — no per-file edits needed.

> **Review notes (present only during active REVISE rounds):**


### Task 2: Update polish.md §C and SKILL.md lifecycle ladder sentence
**Depends on:** Task 1

**Script:** `skills/writing/references/polish.md` (light edit to §C); `skills/writing/SKILL.md` (one-sentence clarification in §Project Conventions in the handoff doc / CLAUDE.md)
**Input:** Updated `long-form-review.md` from Task 1
**Output:** Both files updated with minimal edits

- [ ] **Step 1: polish.md §C reframe**

```text
Current §C ("Review-findings list") describes shape-C input as a free-floating
findings list. Reframe to acknowledge that when polish rides REVIEW.md, shape-C
input is the Stage-2 task block in PLAN.md (post-rename), and the per-tier
batching has already happened at Stage-2 task construction time — the implementer
applies the batch the task block names, not re-batches inside the polish pass.

Keep the existing per-tier apply rules (mechanical / conventional / authorial)
unchanged — they still describe how the implementer applies each item. Only the
input-shape paragraph and the batching framing change.
```

- [ ] **Step 2: SKILL.md lifecycle ladder one-sentence clarification**

```text
In `SKILL.md §Project Conventions in the handoff doc / CLAUDE.md`, the lifecycle
ladder sentence reads:

  "Where they live (lifecycle ladder, ordered by permanence). REVIEW.md (born for
   one review, dies at closeout) → PLAN.md (analysis-scoped) → CLAUDE.md
   (project-permanent)."

Add one clause noting that the long-form-review pipeline literally promotes
REVIEW.md → PLAN.md via `git mv` at the Stage-2 gate. The ladder mental model
is unchanged; this clarifies that the promotion is mechanical, not just
conceptual. Keep the edit to one sentence.
```

- [ ] **Step 3: Self-check before commit**

```text
Confirm both edits are inline (no "Update:" / "Revised:" framing per
`handoff-doc/SKILL.md §Inline-Edit Rule`). Confirm no new instruction line in
either file violates DRY/Necessity. Commit atomically with the Task 2 PLAN.md
status flip.
```

> **Review notes (present only during active REVISE rounds):**


### Task 3: Update writing/CLAUDE.md contributor notes
**Depends on:** Task 1

**Script:** `skills/writing/CLAUDE.md` (supersede one prior entry in place; add new design-decision entries)
**Input:** Current `writing/CLAUDE.md` (HEAD at 2b78713); design spec at `~/.claude/plans/currently-review-md-is-not-fancy-stream.md` §Files-to-change
**Output:** CLAUDE.md with the prior "no rename" rule superseded in place and new design entries appended in the long-form-review section

- [ ] **Step 1: Supersede the "REVIEW.md never renames to PLAN.md" rule in place**

```text
The current entry under "Multi-agent review pattern" reads:

  "Shared doc is `REVIEW.md`, not `PLAN.md`. Naming the review artifact `PLAN.md`
   would collide with the workflow's own `PLAN.md` whenever the review rides one.
   The two coexist by name and lifecycle: `PLAN.md` spans the project; `REVIEW.md`
   is born for one review and dies at closeout (delete or archive). A future
   'just reuse PLAN.md' suggestion needs to solve the collision before it is
   reopened."

Rewrite this entry in place (do NOT stack a new entry alongside per
`handoff-doc/SKILL.md §Inline-Edit Rule`) to reflect the new rule:

  REVIEW.md → PLAN.md rename at Stage 2 is the spec. Collision avoidance: rename
  rule applies only to standalone reviews. When riding an existing workflow
  PLAN.md, Stage 1 blocks live in that PLAN.md as temporary tasks; Stage 2
  rewrites them inline within the same file. There is only ever one PLAN.md in
  play — no collision possible.

Preserve the load-bearing reason (collision concern) as the why-this-rule
exists; the resolution (standalone-only rename) is what changed.
```

- [ ] **Step 2: Append new design-decision entries**

```text
Add a new "## Two-stage REVIEW.md → PLAN.md lifecycle" section under the
long-form-review group recording the five load-bearing decisions per design
spec §Files-to-change for writing/CLAUDE.md:

  (a) Two-stage decision + rejected alternatives — one-stage with reviewers
      pre-building tasks; paired review+polish tasks per dimension. Load-bearing
      reason against re-litigating one-stage: cross-finding issue-class batching
      needs the assembled view that only exists after parallel reviewers return.

  (b) Per-finding user-feedback granularity decision — per-task tier directives
      bolt per-item exceptions on awkwardly; authorial decisions need explicit
      per-item authorization.

  (c) Task-granularity rule — 1 authorial = 1 task; mechanical/conventional
      batched by issue class (kind-of-fix, not manuscript geography).

  (d) `## Findings` header section vs. inlining findings in each Stage-2 task
      — avoid duplication; preserve traceability for rejected/deferred findings;
      keep Stage-2 tasks lean.

  (e) Stage-2 rename rule (cross-link to the superseded entry from Step 1).

Each entry follows the existing CLAUDE.md style: short, names what was decided,
why (load-bearing reason), and what future contributors must clear before
re-litigating.
```

- [ ] **Step 3: Self-check before commit**

```text
Confirm the superseded entry is rewritten in place (no parallel old + new
entries). Confirm no new entry restates content owned by long-form-review.md
itself (CLAUDE.md is for design history, not behavior spec). Commit atomically
with the Task 3 PLAN.md status flip.
```

> **Review notes (present only during active REVISE rounds):**


### Task 4: Verification sweep
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
