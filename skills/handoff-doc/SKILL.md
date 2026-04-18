---
name: handoff-doc
description: Use whenever creating a PLAN.md / RESULTS.md from scratch, maturing RESULTS.md into its permanent record at INTEGRATE, or when you need the full editing discipline for a task-block-structured handoff document. Carries the four document principles, the inline-edit rule, the stale-content checklist, and pointers to full PLAN.md / RESULTS.md anatomy templates (which cover the two-stage RESULTS.md lifecycle and the User Decisions Log format). Usable standalone by a single author with no subagents — the author plays all roles and reads this skill directly. Doc-creation call sites: `planning-workflow` Phase 2 (new plan + RESULTS.md skeleton) and `integration-workflow` Step 3 doc-writer (Stage 2 maturation).
---

# Handoff Doc Discipline

Handoff docs (`PLAN.md`, `RESULTS.md`, and similarly-structured task-block docs) are the persistent state of a project — multiple agents and sessions read and write them. This skill defines the discipline. The main body below carries the load-bearing principles; the references carry the full templates and detailed section specs.

- `references/plan-anatomy.md` — full `PLAN.md` template (header, `## Project Conventions`, `## Decisions`, task blocks, review-notes blockquote format) and the full **User Decisions Log** spec (where decisions land, format, not-covered cases).
- `references/results-anatomy.md` — full `RESULTS.md` template (header, per-task sections, figure embedding, reviewer caveats), the **two-stage RESULTS.md lifecycle** (Stage 1 dev log → Stage 2 permanent record), and the transition to Stage 2 consolidation.

**Subagent-specific execution protocol** — review-loop mechanics (who writes what in the review-notes blockquote, who may delete items, the `→ implemented:` / `→ orchestrator:` annotation protocols, the `**Doc edits:**` status-line format) — lives in `agents/implementer.md` and `agents/reviewer.md`. This skill does not duplicate that.

## The Four Principles

1. **Latest state only, no history.** Handoff docs reflect current intent and current findings. They are not changelogs — git owns history. No "Previously...", no strikethroughs, no "Update:" blocks, no stacked review rounds.

2. **Live and committed.** Every edit is an inline replacement, committed atomically with the work it belongs to. Stale steps, stale review notes, and superseded discovery notes are **removed**, not struck through. The doc at any point reads as a single coherent current-state description.

3. **Task-block structure.** `PLAN.md` is a header plus a sequence of task blocks; each task block has a fixed anatomy. `RESULTS.md` mirrors the task structure. The full templates live in `references/plan-anatomy.md` and `references/results-anatomy.md`.

4. **The doc is the record. Status reports are pointers, not substitutes.** Any material finding, result, methodology change, caveat, or decision MUST be written into `PLAN.md` or `RESULTS.md` *before* it is communicated in a status report or chat message. If a result exists only in chat, it does not exist — it will be lost at the next session boundary, cache eviction, or context compaction.

   **Rule of thumb:** before typing a finding into a status report, ask "is this written in `PLAN.md` or `RESULTS.md` yet?" If not, write it in the doc first and commit, then point at it in the report.

## PLAN.md Is the Task Tracker

For analysis work, **`PLAN.md` is the primary task tracker** — not `TodoWrite`, not chat, not status reports, not a session-internal scratchpad. The task blocks with their `- [ ]` / `- [x]` checkbox steps and `**Review status:**` lines are the authoritative state of what is planned, what is in progress, and what is done. Persistence across sessions, agent handoffs, and harness boundaries depends on this being true.

`TodoWrite` (or any equivalent harness-provided todo UI) has a narrower role: a transient view of *what the agent is doing right now in this session*. It is acceptable for ephemeral session-internal todos that do not represent analysis tasks (e.g., "read three reference files, then summarize for the user", "fix three lint errors before re-running the test"). It is **not** acceptable as a substitute for a PLAN.md task block. If the work is part of the analysis — a new task, a discovered subtask, a methodology check, a sensitivity run, a refactor pass — it lives in `PLAN.md` first, then optionally mirrors into `TodoWrite` as a working view.

**Rule of thumb:** if losing this todo at session end would lose work the researcher cares about, it belongs in `PLAN.md`, not `TodoWrite`.

**Banned patterns:**

- Tracking analysis tasks only in `TodoWrite` while leaving `PLAN.md` stale.
- Discovering a new subtask, adding it to `TodoWrite`, completing it, and never reflecting it in `PLAN.md`.
- Using `TodoWrite` to coordinate work between sessions (it does not persist; the next session sees nothing).
- Treating `TodoWrite` items as "logged" — they are not. Logged work is in a committed doc.

If `TodoWrite` and `PLAN.md` ever disagree about the state of analysis work, `PLAN.md` is right by definition. Update `TodoWrite` to match — never the reverse.

## Inline-Edit Rule

Every edit replaces stale content in place. Never append, never strike through, never use "Update:" / "Revised:" / "Previously..." framing. If you catch yourself writing a sentence that references a prior version of the doc, stop — that sentence belongs in the git commit message.

## Mid-Session Scope Changes

When the researcher adds, modifies, removes, or reorders work during a session — or changes methodology, sample, output, or data sources — the change is **material** and MUST land in `PLAN.md` before any new work begins. There is one `PLAN.md` per analysis. Update it inline; do not start a parallel doc, append an "Addendum" section, or carry the change in chat.

**Material (require this protocol):**

- Adding, removing, or reordering a task block.
- Changing a task's objective, script, input, or output.
- Changing the analysis-level objective, methodology, sample definition, or expected output.
- Changing data sources or project-wide conventions.

**Not material (handle as inline discovery edits per the Living Plan section in `planning-workflow`):**

- Rewording a step within an in-flight task to match what the data forced.
- Adjusting expected results based on early findings.
- Refining methodology details that the researcher already approved at planning time.

**Protocol:**

1. **Confirm intent.** A passing remark in chat is not authorization. Use `AskUserQuestion` (or a plain-text question if the tool is not available) to confirm the researcher wants the change. This is the same escalation gate as `execution-workflow` Stop-Points class (b).
2. **Log the decision** per §User Decisions Log above — top-level `## Decisions` for cross-task changes, task-scoped blockquote for single-task changes.
3. **Update `PLAN.md` inline:**
   - **New task** → append `### Task N+1: [name]` block with the full anatomy from `references/plan-anatomy.md`. Renumber later tasks if inserting earlier in the sequence.
   - **Modified task** → rewrite the affected fields in place. Do not strike through. Do not add "Modified:" annotations.
   - **Removed task** → delete the block entirely. The Decisions entry preserves the rationale.
   - **Reordered tasks** → renumber and rewrite. The decision log preserves the original sequence.
4. **Update `## Workflow Status`** if the change reverts a completed milestone. Adding a new task means `Execution complete` is no longer checked; changing methodology after refactor means `Refactored` and `Docs finalized` are no longer checked and the affected downstream stages must re-run.
5. **Commit atomically** — PLAN.md edit + decision log entry + any code touched by the change, in one commit. Title: `plan: <one-line scope change>`.
6. **Resume the appropriate workflow** for the new state. If the new task is unstarted, dispatch through `execution-workflow`. If the change rolled back `Refactored`, re-enter `integration-workflow` Stage 2.

**Banned shortcuts:**

- Carrying the new task in chat or only in `TodoWrite` without writing it into `PLAN.md` (see §PLAN.md Is the Task Tracker — `TodoWrite` is a transient view, not a record).
- Creating a `PLAN_v2.md` or appending an "Addendum" section. There is one `PLAN.md`.
- Resuming the in-flight task before reflecting the change in the doc — the change is not real until it is committed.

## What Counts as Stale (remove, don't keep)

- Steps describing an approach abandoned after seeing the data — rewrite them to describe what was actually done.
- Discovery notes now incorporated into the current steps.
- Review items confirmed fixed on re-review (the reviewer deletes them).
- "Previously we tried X" / "Update:" / "Revised:" framing — delete the old text and write the new.
- Upcoming task descriptions that assume an earlier approach which has since changed.

## User Decisions Log

Researcher answers to `AskUserQuestion` / plain-text pauses MUST be written into `PLAN.md` **before** the agent acts on them, committed atomically with the work they unblock. This is the "autonomous with human in the loop" principle (see `using-superRA` §Universal Principles #4) in practice: the decision is not resolved until it is in the record.

Full spec — where task-scoped vs project-level decisions land, the three-line blockquote format, the hook reminder, and what does NOT count as a decision — lives in `references/plan-anatomy.md` §User Decisions Log.

## Project Conventions and Figure Embedding

- **`## Project Conventions`** — section of `PLAN.md` populated by the orchestrator at `planning-workflow` Phase 3 with one-paragraph summaries of every `CLAUDE.md` / `AGENTS.md` / `README.md` walked from the directories the plan touches. Subagents read this section rather than re-walking the tree each dispatch. Full anatomy in `references/plan-anatomy.md` §Project Conventions.
- **Figure embedding** — Stage 1 `RESULTS.md` uses `![caption](results_attachments/fig_name.png)` pointing at committed PNGs. The full discipline (PDF→PNG, captions, math, tables) lives in `skills/report-in-markdown/references/rich-content.md`; the Stage 2 materialization + relocation lives in `skills/report-in-markdown/references/final-form.md`.

## How This Skill Is Used

- **Standalone use:** a single author maintaining handoff docs without subagents — read the four principles and the anatomy references; the author plays all roles.
- **`planning-workflow` Phase 2:** the planner loads this skill for the templates and drafts `PLAN.md` + a Stage 1 `RESULTS.md` skeleton.
- **`integration-workflow` Step 3 doc-writer:** loads this skill (for `references/results-anatomy.md` — carries the two-stage lifecycle and the transition pointer) plus `report-in-markdown/references/final-form.md` for the Stage 2 materialization and relocation discipline.
- **Implementer / reviewer subagents during execution:** do NOT load this skill by default — a compact editing etiquette lives in `agents/implementer.md` / `agents/reviewer.md` step 1 (inline-edit, remove-stale, no-append). Load on demand when the etiquette is not enough (unusual structural edit, first-time encounter with the doc format, writing a User Decisions Log entry).
