---
name: handoff-doc
description: >
  Use when creating or restructuring PLAN.md or RESULTS.md, maturing
  RESULTS.md into its final record, or when an agent needs the full
  task-block editing discipline for handoff docs.
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

**`PLAN.md` is the primary task tracker, not `TodoWrite` or chat.** The task-tracker discipline (banned patterns, the `TodoWrite`-as-transient-view rule, and the re-invoke-`§Changing Plans`-on-plan-change pointer) lives in `planning-workflow §PLAN.md Is the Task Tracker`.

## Inline-Edit Rule

Every edit replaces stale content in place. Never append, never strike through, never use "Update:" / "Revised:" / "Previously..." framing. If you catch yourself writing a sentence that references a prior version of the doc, stop — that sentence belongs in the git commit message.

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
