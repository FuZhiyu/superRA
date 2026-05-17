# Simplify long-form review: drop the `## Findings` header indirection

> For agentic workers: REQUIRED DISCIPLINE — use `superRA:handoff-doc` for all editing; load `superRA:writing` for every step touching skill bodies. Steps use checkbox syntax for tracking. **Dispatch scope:** all edits are inside the project working tree at `/Users/zhiyufu/Dropbox/package_dev/superRA-domain-writing-skills/`. Implementers and reviewers must use absolute paths inside that tree; do not edit copies that may exist in other worktrees of this repo (e.g., `superRA-dev/`).

## Objective

Replace the two-stage *task-block* design in `long-form-review.md` (Stage 1 per-aspect task blocks → Stage 2 actionable task blocks + `## Findings` header lookup) with a simpler single-set-of-tasks design: Stage 1 collects findings in a flat `## Findings` section grouped by dimension (no per-aspect Stage-1 task blocks); Stage 2 rewrites by inlining accepted findings directly into actionable task blocks and consolidating rejected/deferred findings into a small `## Deferred & Rejected` log. The REVIEW.md → PLAN.md file rename at the Stage-2 gate stays. F-IDs stay (useful for user-feedback granularity and commit-message audit). What goes away: the per-aspect Stage-1 task blocks, the `## Findings` header section in Stage 2, the `**Sources:** F2, F5, F9` indirection pattern in Stage-2 tasks.

## Methodology

Edit-and-verify against the repo `CLAUDE.md` DRY/Necessity tests per task. Implementer/reviewer cycle per `implementation-workflow`. No drift tests (skill-design work).

## Output

Updated skill files:
- `skills/writing/references/long-form-review.md` — full rewrite of `## Doc convention` for the simpler design
- `skills/writing/references/polish.md` — §C reframe (Stage-2 task block now carries findings inline; no F-ID lookup)
- `skills/writing/CLAUDE.md` — rewrite the `## Two-stage REVIEW.md → PLAN.md lifecycle` section (decision (d) is reversed; decisions (a), (b), (c), (e) stand with light edits)
- `skills/writing/SKILL.md` — ladder clause check (likely no change)

## Expected results

A long-form review pipeline that:
- still produces a REVIEW.md → PLAN.md handoff via `git mv` at the Stage-2 gate (standalone-only)
- still gives every finding per-finding user feedback (accept/defer/reject)
- still batches mechanical/conventional findings by issue class
- has **one** set of task blocks, not two
- has findings inlined in their owning task block, not stored in a separate `## Findings` header

## Pipeline

Single-document edits; no pipeline file.

## Project Conventions

Walked 2026-05-16.

- **Repo CLAUDE.md** (`/Users/zhiyufu/Dropbox/package_dev/superRA-domain-writing-skills/CLAUDE.md`) — contributor design rules: DRY/Necessity tests, ownership boundaries (handoff-doc owns plan-anatomy; writing owns vertical conventions), anti-patterns (wrapper instructions, "here is what you will receive" descriptions, default reminders, restating Skill-Load Manifest). Every new instruction line passes "without this line, would the agent's behavior be unstable?"
- **writing/CLAUDE.md** — design history; carries the five-decision block on the two-stage lifecycle that this round must rewrite. Decisions (a)/(b)/(c)/(e) carry over; (d) reverses (header indirection rejected in favor of inlining).
- **writing/SKILL.md §Project Conventions in the handoff doc / CLAUDE.md** — lifecycle ladder `REVIEW.md → PLAN.md → CLAUDE.md`. The clause about "REVIEW.md → PLAN.md promotion is mechanical (`git mv` at the Stage-2 gate, standalone-only)" still holds in the new design.
- **writing/references/long-form-review.md** — primary target. Current content reflects two-stage task-block + `## Findings` header design and must be rewritten.

## Workflow Status

- [x] Plan approved
- [ ] Execution complete — every task APPROVED
- [ ] Drift tests created — N/A for skill-design work (auto-satisfied)
- [ ] Integrated — every task `Integration status: APPROVED`
- [ ] Docs finalized — disposition logged
- [ ] Finished

---

### Task 1: Rewrite `long-form-review.md` for the simpler design

**Depends on:** *(none)*
**Review status:** APPROVED

The current `long-form-review.md` (read it as the authoritative source) specifies two stages of task blocks and a `## Findings` header section in Stage 2. Rewrite `## Doc convention` to:

**Stage 1 (REVIEW.md):**
- No per-aspect task blocks. Findings live directly in a top-level `## Findings` section organized as subsections per dimension (`### Notation`, `### Terminology`, …). Reviewers dispatched in parallel write findings into their assigned subsection using the `consistency/<dim>.md` output format unchanged. Each finding still gets a stable global F-ID at write time (F-IDs survive into Stage 2 for commit-message audit even though Stage 2 no longer indexes by them).
- Per-finding `**User:** accept | defer | reject [— reason]` inline at the end of each finding (replaces the prior per-aspect `**User feedback:**` field).
- Stage-1 `## Workflow Status` tracks dispatch via per-dimension checkboxes (one `- [ ] <dimension> reviewer done` per dispatched dimension) plus `- [ ] User feedback recorded`.

**Stage 1 → Stage 2 rewrite (orchestrator action, one atomic commit). Four moves:**
1. `git mv REVIEW.md PLAN.md`
2. Replace the Stage-1 Workflow Status with the standard PLAN.md rollup.
3. For every accepted finding, build an actionable Stage-2 task block per the granularity rule (1 authorial = 1 task; mechanical and conventional batched by issue class). Inline each absorbed finding's body inside its task block under a `**Findings absorbed:**` subheading, preserving the `consistency/<dim>.md`-format entry and the F-ID.
4. Move every rejected and deferred finding into a single `## Deferred & Rejected` section at the bottom of the doc (one line per finding, retaining F-ID, verdict, and reason). Delete the now-empty `## Findings` section.

**Stage 2 (PLAN.md):** standard `implementation-workflow` runs over the task blocks unchanged; `Integration status:` is omitted (review-driven polish does not flow through `integration-workflow`).

**Standalone-only rename rule:** carries over verbatim — applies only to standalone reviews; reviews riding a workflow PLAN.md live inside that PLAN.md as temporary task blocks rewritten inline at Stage 2.

**Stage-2 task granularity:** carries over (1 authorial-accepted = 1 task; mechanical and conventional batched by issue class; final Verify task).

**Review-time indices, dispatch convention, deep mode, final summary block:** carry over from the current file. Update any wording that references the removed per-aspect task blocks or the removed `## Findings` header indirection.

**Apply the DRY/Necessity tests line by line.** Every line must shape behavior the agent would not produce on its own. Walk the anti-patterns list in repo CLAUDE.md (wrapper instructions, "here is what you will receive" descriptions, default reminders, restating the Skill-Load Manifest); flag and drop violations.

- [x] **Step 1:** Read the current `skills/writing/references/long-form-review.md` end-to-end and the related anchors in `skills/writing/SKILL.md`, `skills/writing/CLAUDE.md`, and `skills/handoff-doc/references/plan-anatomy.md` (§Task Block Anatomy, §Header ownership).
- [x] **Step 2:** Rewrite `## Doc convention` per the spec above. Update §Dispatch convention, §Multi-perspective deep mode, §Final summary block, and §Trigger only where wording references the removed per-aspect task blocks or the removed `## Findings` header indirection.
- [x] **Step 3:** Walk the DRY/Necessity tests line by line. Drop any line that fails the necessity test (no behavior shaped) or the DRY test (already authoritative elsewhere).
- [x] **Step 4:** Commit.

### Task 2: Update `polish.md §C` to drop F-ID lookup

**Depends on:** Task 1 (so the new Stage-2 task block shape is fixed before §C describes it)
**Review status:** IMPLEMENTED

The current §C says: "shape-C input is a Stage-2 task block in PLAN.md (post-rename from REVIEW.md). The task block names a pre-batched sweep ... and cites source findings by F-ID pointing into `## Findings`. ... Look up each cited F-ID in `## Findings` for the full finding text and its user-accepted verdict before editing."

Rewrite to match the new design: the task block now carries findings inline under `**Findings absorbed:**`. The implementer reads the findings directly from the task block; no F-ID lookup is needed. The per-tier apply rules below the paragraph are unchanged.

- [x] **Step 1:** Edit `skills/writing/references/polish.md §C` to drop the F-ID lookup language. State that shape-C input is a Stage-2 task block whose `**Findings absorbed:**` subheading carries each accepted finding's body inline. Preserve the standalone-shape-C paragraph and the per-tier apply rules verbatim.
- [x] **Step 2:** Commit.

### Task 3: Rewrite `writing/CLAUDE.md §Two-stage REVIEW.md → PLAN.md lifecycle`

**Depends on:** Task 1
**Review status:**

The current contributor-notes section carries five load-bearing decisions (a)–(e). Decisions (a), (b), (c), (e) survive with light edits (drop any wording that assumed the `## Findings` header). Decision (d) is **reversed** — the rejected-alternative direction (inlining findings) is now the chosen design. Rewrite (d) accordingly:

- New (d): inline accepted findings in each Stage-2 task; consolidate rejected and deferred findings in a small `## Deferred & Rejected` section at the bottom. Rejected alternative: a `## Findings` header section with `**Sources:** F2, F5, F9` indirection in Stage-2 tasks. Why rejected: the header indirection adds a lookup hop without buying enough to justify it. The duplication concern that motivated the header (a finding cited by multiple tasks would be inlined twice) does not occur in practice — issue-class batching means each accepted finding is absorbed by exactly one task. The rejected/deferred-findings home concern is satisfied by the `## Deferred & Rejected` section. Net: one fewer indirection, lower cognitive load on implementers, cleaner Stage-2 task blocks that are self-contained.

Apply the inline-edit rule from `superRA:handoff-doc` — rewrite the section in place, do not stack a new entry alongside the old one.

- [ ] **Step 1:** Edit `skills/writing/CLAUDE.md §Two-stage REVIEW.md → PLAN.md lifecycle`. Update (a) to reflect single-set-of-tasks vocabulary (the assembled-view argument still holds and still rejects the one-stage alternative). Lightly edit (b), (c), (e) to drop any phrasing that assumed the `## Findings` header. Reverse (d) per the spec above.
- [ ] **Step 2:** Commit.

### Task 4: Verification sweep

**Depends on:** Tasks 1, 2, 3
**Review status:**

Sweep for stale references and confirm cross-doc coherence.

- [ ] **Step 1:** `grep -rn "## Findings\|Sources: F\|F-ID\|per-aspect task block\|Stage-1 task block\|Stage-1 per-aspect" skills/ --include="*.md"`. Every surviving mention should either be in the new contributor-notes (d) explaining the rejected alternative, or in something orthogonal. Flag and fix stragglers.
- [ ] **Step 2:** Read `skills/writing/SKILL.md §Project Conventions in the handoff doc / CLAUDE.md`. Confirm the lifecycle-ladder clause still reads correctly (the rename at Stage-2 gate is unchanged). Edit only if a clause now misleads.
- [ ] **Step 3:** Walk an imagined long-form review end-to-end against the rewritten `long-form-review.md`: parallel reviewer dispatch → Stage-1 findings in `## Findings` by dimension → user feedback inline → Stage-2 rewrite (rename + task-block authoring + Deferred & Rejected log) → implementer dispatch on a mechanical-batch task → reviewer APPROVE → Closeout. Confirm canonical implementer/reviewer protocols apply at every step without new wiring.
- [ ] **Step 4:** Commit any fixes from Steps 1–2 atomically; if no fixes, commit an empty marker is not needed — just record verification results in RESULTS.md.
