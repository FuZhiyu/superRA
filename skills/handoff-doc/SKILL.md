---
name: handoff-doc
description: "Use whenever creating a PLAN.md / RESULTS.md from scratch, maturing RESULTS.md into its permanent record at INTEGRATE, or when you need the full editing discipline for a task-block-structured handoff document. Carries the four document principles, the inline-edit rule, the stale-content checklist, and pointers to full PLAN.md / RESULTS.md anatomy templates. Usable standalone by a single author with no subagents — the author plays all roles and reads this skill directly. Doc-creation call sites: `planning-workflow` Phase 2 (new plan + RESULTS.md skeleton) and `integration-workflow` Step 3 doc-writer (Stage 2 maturation)."
---

# Handoff Doc Discipline

Handoff docs (`PLAN.md`, `RESULTS.md`, and similarly-structured task-block docs) are the persistent state of a project — multiple agents and sessions read and write them. References:

- `references/plan-anatomy.md` — full `PLAN.md` template (header, `## Project Conventions`, `## Decisions`, task blocks, review-notes blockquote format) and the full **User Decisions Log** spec.
- `references/results-anatomy.md` — full `RESULTS.md` template, the **two-stage RESULTS.md lifecycle** (Stage 1 dev log → Stage 2 permanent record), and the Stage 2 transition.

Subagent-specific review-loop mechanics (annotation protocols, `**Doc edits:**` format) live in `agents/implementer.md` and `agents/reviewer.md`.

## The Four Principles

1. **Latest state only, no history.** Handoff docs reflect current intent and current findings. They are not changelogs — git owns history. No "Previously...", no strikethroughs, no "Update:" blocks, no stacked review rounds.

2. **Live and committed.** Every edit is an inline replacement, committed atomically with the work it belongs to. Stale steps, stale review notes, and superseded discovery notes are **removed**, not struck through. The doc at any point reads as a single coherent current-state description.

3. **Task-block structure.** `PLAN.md` is a header plus a sequence of task blocks; each task block has a fixed anatomy. `RESULTS.md` mirrors the task structure. The full templates live in `references/plan-anatomy.md` and `references/results-anatomy.md`.

4. **The doc is the record. Status reports are pointers, not substitutes.** Any material finding, result, methodology change, caveat, or decision MUST be written into `PLAN.md` or `RESULTS.md` *before* it is communicated in a status report or chat message. If a result exists only in chat, it does not exist — it will be lost at the next session boundary, cache eviction, or context compaction.

   **Rule of thumb:** before typing a finding into a status report, ask "is this written in `PLAN.md` or `RESULTS.md` yet?" If not, write it in the doc first and commit, then point at it in the report.

## Inline-Edit Rule

Every edit replaces stale content in place. Never append, never strike through, never use "Update:" / "Revised:" / "Previously..." framing. If you catch yourself writing a sentence that references a prior version of the doc, stop — that sentence belongs in the git commit message.

## Stale Content Checklist

- Steps describing an approach abandoned after seeing the data — rewrite them to describe what was actually done.
- Discovery notes now incorporated into the current steps.
- Review items confirmed fixed on re-review (the reviewer deletes them).
- "Previously we tried X" / "Update:" / "Revised:" framing — delete the old text and write the new.
- Upcoming task descriptions that assume an earlier approach which has since changed.
- Task output descriptions that have been superseded or further modified by a later task in the plan — rewrite the earlier task's **Output:** to reflect the latest shape, and keep the narrative of "what changed" in the Decisions log only.

## User Decisions Log

Researcher answers to `AskUserQuestion` / plain-text pauses MUST be written into `PLAN.md` **before** the agent acts on them, committed atomically with the work they unblock. This is the "autonomous with human in the loop" principle (full contract in `using-superra/references/main-agent.md`) in practice: the decision is not resolved until it is in the record.

Full spec — where task-scoped vs project-level decisions land, the three-line blockquote format, the hook reminder, and what does NOT count as a decision — lives in `references/plan-anatomy.md` §User Decisions Log.

**`## Project Conventions`** — populated at `planning-workflow` Phase 3; anatomy in `references/plan-anatomy.md §Project Conventions`.

**Figure embedding** — discipline in `report-in-markdown/references/rich-content.md`; Stage 2 materialization in `report-in-markdown/references/final-form.md`.
