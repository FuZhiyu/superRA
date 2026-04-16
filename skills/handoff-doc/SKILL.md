---
name: handoff-doc
description: Doc-creation skill — use when authoring a PLAN.md or RESULTS.md from scratch (`planning-workflow` Phase 2) or maturing Stage 1 RESULTS.md into the Stage 2 permanent record (`integration-workflow` Step 3 doc-writer). Carries the full document-anatomy templates in `references/plan-anatomy.md` and `references/results-anatomy.md`. For everyday implementer / reviewer handoff-doc editing (the four principles, inline-edit rule, stale-content checklist, User Decisions Log, figure embedding pointer), see `superRA:using-superRA` §Handoff Doc Discipline — that is always in effect via the master skill and does not require loading this one.
---

# Handoff Doc Creation

Cross-cutting agent-runtime essentials for editing `PLAN.md` / `RESULTS.md` — the four principles, inline-edit rule, stale-content checklist, User Decisions Log format, figure embedding pointer, `## Project Conventions` pointer — live in `superRA:using-superRA` §Handoff Doc Discipline. Every agent already loads that skill, so the everyday editing rules are always available without loading this one.

This skill is for doc *creation*: invoked by `planning-workflow` Phase 2 to author a new `PLAN.md` / `RESULTS.md` from scratch, and by the Stage 2 doc-writer in `integration-workflow` Step 3 to mature the Stage 1 `RESULTS.md` into its permanent form. Both callers need the full document anatomy — section layouts, code-block examples, status-line formats, transition-to-Stage-2 mechanics — which live in the references below.

## The Two-Stage RESULTS.md Lifecycle

`RESULTS.md` has two stages:

- **Stage 1** — a dev log in the worktree root during IMPLEMENT. Task-indexed, agent-facing, "latest state only." Created by `planning-workflow` Phase 2 alongside `PLAN.md`; updated inline by the implementer per task per `using-superRA` §Handoff Doc Discipline.
- **Stage 2** — a permanent record at the analysis's code folder, materialized during INTEGRATE. Reader-facing, fact-checked, carries frontmatter, figures materialized into `${RESULTS_DIR}/attachments/`. Consolidation discipline lives in `skills/report-in-markdown/references/final-form.md` and is invoked by `integration-workflow` Step 3 sub-part A.

## References

- `references/plan-anatomy.md` — the full `PLAN.md` template: header (objective, methodology, data inventory, conventions, output, pipeline, `## Project Conventions`, `## Decisions`), task-block structure (objective / files affected / input / output / steps / review status / review-notes blockquote), code-block examples, status-line formats.
- `references/results-anatomy.md` — the full Stage 1 `RESULTS.md` template: header, per-task sections (status, key findings, figures, notes), figure-embedding conventions, transition-to-Stage-2 pointer.

Load the reference that matches the doc you are creating or maturing. The two anatomy files are independent — load `plan-anatomy.md` when authoring a plan, `results-anatomy.md` when setting up Stage 1 or editing Stage 2.

## How This Skill Is Used

- **Standalone use.** A single author creating handoff docs without subagents — read the anatomy reference for the doc you are creating; the cross-cutting rules in `using-superRA` §Handoff Doc Discipline apply as usual.
- **`planning-workflow` Phase 2.** The planner loads this skill (for the templates) plus `using-superRA` (which every agent already has) for the principles. Drafts `PLAN.md` and a Stage 1 `RESULTS.md` skeleton.
- **`integration-workflow` Step 3 doc-writer.** The Stage 2 doc-writer loads this skill (for `results-anatomy.md`) plus `report-in-markdown/references/final-form.md` for the materialization + relocation discipline. Produces the permanent `RESULTS.md` in `${RESULTS_DIR}/`.
