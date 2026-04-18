---
name: handoff-doc
description: Use when creating, reading, or editing PLAN.md, RESULTS.md, or any other task-block-structured handoff document. Defines the four discipline principles, the inline-edit rule, the stale-content checklist, and the figure embedding rule. Points at references/ for full document anatomy, and at `report-in-markdown` for the Stage 2 consolidation that matures RESULTS.md into its permanent form. Load whenever you are about to read or edit a handoff doc.
---

# Handoff Doc Discipline

Handoff docs (`PLAN.md`, `RESULTS.md`, and similarly-structured task-block docs) are the persistent state of a project. Multiple agents and sessions read and write them. This skill defines the discipline — what these docs are, how they are structured at a glance, and the universal editing rules.

`RESULTS.md` has a **two-stage lifecycle**: a Stage 1 dev log in the worktree root during IMPLEMENT (task-indexed, agent-facing, "latest state only"), maturing into a Stage 2 permanent record at the analysis's code folder during INTEGRATE (reader-facing, fact-checked, frontmatter, figures materialized). Stage 1 discipline is defined here; Stage 2 consolidation discipline lives in `skills/report-in-markdown/references/final-form.md` and is invoked by `integration-workflow` Step 3.

**This skill has progressive reveal.** Load the references below when you need deeper material:

- `references/plan-anatomy.md` — the full `PLAN.md` template (header + task blocks + code-block examples + review-notes blockquote format)
- `references/results-anatomy.md` — the full Stage 1 `RESULTS.md` template (header + per-task sections + figure embedding pointers + transition-to-Stage-2 note)

**Subagent-specific execution protocol** — including the full review-loop mechanics (who writes what in the review-notes blockquote, who may delete items, the `→ implemented:` and `→ orchestrator:` annotation protocols, and the `**Doc edits:**` status-line format) — lives in `agents/implementer.md` and `agents/reviewer.md`. Each agent file carries its own view of the loop. This skill does not duplicate that; it only specifies the document-level discipline all roles (including a standalone user with no subagents) must follow.

## The Four Principles

1. **Latest state only, no history.** Handoff docs reflect the current intended implementation and current findings. They are not changelogs. Git owns history. No "Previously...", no strikethroughs, no "Update:" blocks, no stacked review rounds.

2. **Live and committed.** Every edit is an inline replacement, committed with the work it belongs to. Stale steps, stale review notes, and superseded discovery notes are **removed**, not struck through. The doc at any point reads as a single coherent current-state description.

3. **Task-block structure.** `PLAN.md` consists of a header (project-wide context) and a sequence of task blocks. Each task block has a fixed anatomy: objective / script / I/O / steps / review status. Stage 1 `RESULTS.md` mirrors the task structure (one section per task). See `references/plan-anatomy.md` and `references/results-anatomy.md` for the full templates.

4. **The doc is the record. Status reports are pointers, not substitutes.** Any material finding, result, methodology change, caveat, or decision MUST be written into `PLAN.md` or `RESULTS.md` *before* it is communicated in a status report or chat message. If a result only exists in a chat reply, it does not exist — it will be lost at the next session boundary, cache eviction, or context compaction. The authoritative record is the committed doc; the report only points at it.

   **Rule of thumb:** before you type a finding into a status report, ask "is this written in `PLAN.md` or `RESULTS.md` yet?" If not, write it in the doc first and commit, then point at it in the report.

## At-a-Glance Structure

A `PLAN.md` in flight looks like:

```markdown
# [Analysis Name] Plan

[header: objective, methodology, data inventory, conventions, output, pipeline]

---

### Task 1: [Phase Name]
**Review status:** APPROVED
- [x] Step 1: ...
- [x] Step 2: ...

### Task 2: [Phase Name]
**Review status:** REVISE
- [x] Step 1: ...
- [ ] Step 2: ...

> **Review notes:**
> 1. [MAJOR] ... (file:line)
>    → implemented: ... (file:line)

### Task 3: [Phase Name]
**Review status:** *(not started)*
- [ ] Step 1: ...
```

A Stage 1 `RESULTS.md` mirrors the task structure, one section per task, with findings and embedded figures.

See the reference templates for the full skeleton.

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

Every edit replaces stale content in place. Never append, never strike through, never use "Update:" / "Revised:" / "Previously..." framing. If you find yourself writing a sentence that references a prior version of the doc, stop — that sentence belongs in the git commit message, not the doc.

## User Decisions Log

Any time the agent stops to consult the researcher — via `AskUserQuestion` or plain-text question — and the researcher gives an answer that shapes the analysis, the answer MUST be written into the handoff doc **before** the agent acts on it, and committed atomically with the work it unblocks. This is the "autonomous with human in the loop" principle in practice (see `CLAUDE.md` §Workflow principles #4): the decision is not resolved until it is in the record. A decision that only lives in chat will be lost at the next session boundary, and the next agent will re-open the same question — or worse, make a different call silently.

**Where it lands:**

- **Task-scoped decision** (affects one task's scope, methodology, or implementation) → appended as a blockquote inside that task block, directly under `**Review status:**`. Uses the same blockquote syntax as review notes, so it sits naturally beside the adjudication protocol defined in `agents/implementer.md` / `agents/reviewer.md`.
- **Cross-task or project-level decision** (affects methodology across tasks, sample definition, output scope, the 4-option merge menu at execution-workflow Step 4, drift-test selection at integration-workflow Step 1) → a top-level `## Decisions` section in `PLAN.md` immediately after the header and before the first task block. Append new decisions to the bottom of that section; do not rewrite prior decisions.

**Format (both locations):**

```markdown
> **User decision (2026-04-11):** Use CRSP value-weighted returns, not equal-weighted.
> **Question asked:** Which market return definition for the benchmark?
> **Rationale (if given):** Matches prior paper; easier reviewer comparison.
```

Three lines, blockquote, dated. The `Question asked` line is the agent's own restatement of what it asked — short enough to read at a glance, specific enough that a fresh agent sees why the decision was needed. The `Rationale` line is optional and appears only if the researcher gave one; do not invent rationale.

**Not covered by this section:**

- Adjudication of reviewer feedback inside the review-notes blockquote — that is the `→ orchestrator: ...` / `→ implemented: ...` protocol owned by `agents/implementer.md` and `agents/reviewer.md`. User decisions are a separate, upstream thing: the researcher answering a question the agent could not decide, not the orchestrator overriding a reviewer.
- Ephemeral clarifications the agent could have resolved from the code ("which file holds X?") — those are not decisions, they do not belong in the log.

If you are not sure whether an answer counts as a decision worth logging: if acting on it would change the code, data, or methodology in a way another agent could not reconstruct from the code alone, log it.

## Mid-Session Scope Changes

When the researcher adds, modifies, removes, or reorders work during a session — or changes methodology, sample, output, or data sources — the change is **material** and MUST land in `PLAN.md` before any new work begins. There is one `PLAN.md` per analysis. We update it; we do not start a parallel doc, append an "Addendum" section, or carry the change in chat.

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

- Steps describing an approach that was abandoned after seeing the data — rewrite them to describe what was actually done.
- Discovery notes that are now incorporated into the current steps.
- Review items that have been confirmed fixed on re-review (the reviewer deletes them).
- "Previously we tried X" / "Update:" / "Revised:" framing — delete the old text and write the new.
- Upcoming task descriptions that assume an earlier approach which has since changed.

## Figure Embedding

Figures in Stage 1 `RESULTS.md` and any other handoff doc are embedded with markdown image syntax pointing at a committed PNG in `results_attachments/` at project root:

```markdown
![Descriptive caption](results_attachments/fig_name.png)
```

The full figure-embedding discipline — PDF→PNG conversion, caption requirements, file reference conventions, math/table handling — lives in `skills/report-in-markdown/references/rich-content.md`. Load that reference when you are writing a handoff-doc task section that contains a figure, a table, or LaTeX math. Pass `results_attachments/` as the target attachments directory when invoking `report-in-markdown`.

The Stage 2 consolidation that matures `RESULTS.md` into its permanent form — fact-check, restructure, figure materialization, relocation — is invoked from `integration-workflow` Step 3 and defined in `skills/report-in-markdown/references/final-form.md`. This skill does not duplicate that discipline.

## How This Skill Is Used

- **Standalone use:** a single author creating or maintaining handoff docs without subagents — read the four principles, the anatomy references, and the inline-edit rule. The role split collapses; the author plays all roles.
- **Multi-agent workflows:** `planning-workflow` delegates handoff-doc discipline here from its Living Plan section rather than duplicating the rules. The implementer and reviewer subagents (`agents/implementer.md`, `agents/reviewer.md`) load this skill alongside their role-specific review-loop protocol. The other workflow skills (`execution-workflow`, `integration-workflow`, `merge-workflow`) inherit the discipline indirectly through the subagents they dispatch; they do not need to reference `handoff-doc` directly.
