---
name: handoff-doc
description: Use when creating, reading, or editing PLAN.md, RESULTS_UPDATE.md, or any other task-block-structured handoff document. Defines the five discipline principles, the at-a-glance ownership matrix, the inline-edit rule, the stale-content checklist, and the figure embedding rule. Points at references/ for full document anatomy. Load whenever you are about to read or edit a handoff doc.
---

# Handoff Doc Discipline

Handoff docs (`PLAN.md`, `RESULTS_UPDATE.md`, and similarly-structured task-block docs) are the persistent state of a project. Multiple agents and sessions read and write them. This skill defines the discipline — what these docs are, how they are structured at a glance, and the universal editing rules.

**This skill has progressive reveal.** The main file is concise: principles, at-a-glance structure, universal rules. Load the references below when you need deeper material:

- `references/plan-anatomy.md` — the full `PLAN.md` template (header + task blocks + code-block examples + review-notes blockquote format)
- `references/results-update-anatomy.md` — the full `RESULTS_UPDATE.md` template (header + per-task sections + figure embedding)

**Subagent-specific execution protocol** — including the full review-loop mechanics (who writes what in the review-notes blockquote, who may delete items, the `→ implemented:` and `→ orchestrator:` annotation protocols, and the `**Doc edits:**` status-line format) — lives in `agents/implementer.md` and `agents/reviewer.md`. Each agent file carries its own view of the loop. This skill does not duplicate that; it only specifies the document-level discipline all roles (including a standalone user with no subagents) must follow.

## The Five Principles

1. **Latest state only, no history.** Handoff docs reflect the current intended implementation and current findings. They are not changelogs. Git owns history. No "Previously...", no strikethroughs, no "Update:" blocks, no stacked review rounds.

2. **Live and committed.** Every edit is an inline replacement, committed with the work it belongs to. Stale steps, stale review notes, and superseded discovery notes are **removed**, not struck through. The doc at any point reads as a single coherent current-state description.

3. **Task-block structure.** `PLAN.md` consists of a header (project-wide context) and a sequence of task blocks. Each task block has a fixed anatomy: objective / script / I/O / steps / review status. `RESULTS_UPDATE.md` mirrors the task structure (one section per task). See `references/plan-anatomy.md` and `references/results-update-anatomy.md` for the full templates.

4. **Ownership by role.** In a multi-agent workflow, each role has strict permissions (see the matrix below). In standalone use, the single author plays all roles and the matrix collapses — but the inline-edit rule and "latest state only" still apply.

5. **Explicit what-changed deltas in both directions.** Because the docs only show latest state, readers cannot infer what changed by reading the doc alone.
   - **Dispatch prompts and task instructions (orchestrator → worker)** carry a one-line delta describing what changed since the last touch: "Task 3 updated — revised Step 2; adjudication note on review item 3."
   - **Status returns (worker → orchestrator)** carry a `**Doc edits:**` line describing what changed. The status return is a **navigation aid**, not a content dump — it summarizes and points at the doc for detail.

6. **The doc is the record. Status reports are pointers, not substitutes.** Any material finding, result, methodology change, caveat, or decision MUST be written into `PLAN.md` or `RESULTS_UPDATE.md` *before* it is communicated in a status report or chat message. If a result only exists in a chat reply, it does not exist — it will be lost at the next session boundary, cache eviction, or context compaction. The authoritative record is the committed doc; the report only points at it.

   **Rule of thumb:** before you type a finding into a status report, ask "is this written in `PLAN.md` or `RESULTS_UPDATE.md` yet?" If not, write it in the doc first and commit, then point at it in the report.

## Ownership at a Glance

| Role | `PLAN.md` | `RESULTS_UPDATE.md` |
|---|---|---|
| **Implementer** | Only inside their assigned task: steps, step notes, `**Review status:** IMPLEMENTED`. May annotate review items but not delete them. | Only their task's section. |
| **Reviewer** | Only inside their assigned task: `**Review status:**` line and the review-notes blockquote. May delete confirmed-fixed items on re-review. | Implementation-stage reliability caveats only. |
| **Orchestrator / standalone author** | Everything, including the header. | Everything. |

For the review-loop mechanics — how items enter and leave the blockquote across iterations, the `→ implemented:` / `→ orchestrator:` annotation protocol, and the rule that **a CRITICAL-severity item cannot be silently overridden, rejected, or deleted on the basis of disagreement — the only legitimate delete of a CRITICAL item is after a reviewer verifies the fix on re-review, or after the human partner has been consulted** — see `agents/implementer.md` and `agents/reviewer.md`. Each agent file carries its own view of the loop: the implementer's file describes how to annotate fixes; the reviewer's file describes how to write first-round REVISE notes and how to verify and delete items on re-review.

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
**Review status:** REVISE (implementation)
- [x] Step 1: ...
- [ ] Step 2: ...

> **Review notes:**
> 1. [MAJOR] ... (file:line)
>    → implemented: ... (file:line)

### Task 3: [Phase Name]
**Review status:** *(not started)*
- [ ] Step 1: ...
```

A `RESULTS_UPDATE.md` mirrors the task structure, one section per task, with findings and embedded figures.

See the reference templates for the full skeleton.

## Inline-Edit Rule

Every edit replaces stale content in place. Never append, never strike through, never use "Update:" / "Revised:" / "Previously..." framing. If you find yourself writing a sentence that references a prior version of the doc, stop — that sentence belongs in the git commit message, not the doc.

## What Counts as Stale (remove, don't keep)

- Steps describing an approach that was abandoned after seeing the data — rewrite them to describe what was actually done.
- Discovery notes that are now incorporated into the current steps.
- Review items that have been confirmed fixed on re-review (the reviewer deletes them).
- "Previously we tried X" / "Update:" / "Revised:" framing — delete the old text and write the new.
- Upcoming task descriptions that assume an earlier approach which has since changed.

## Figure Embedding

Figures in `RESULTS_UPDATE.md` and any other handoff doc are always embedded with markdown image syntax:

```markdown
![Descriptive caption](results_attachments/fig_name.png)
```

- Path is relative and points at a committed PNG in `results_attachments/` at project root.
- Caption is the figure's title; readers should understand the figure without clicking into it.
- If the source is a PDF, convert to PNG for embedding and keep the PDF alongside for high-resolution access.

## How This Skill Is Used

- **Standalone use:** a single author creating or maintaining handoff docs without subagents — read the five principles, the anatomy references, and the inline-edit rule. The ownership matrix collapses; the author plays all roles.
- **Multi-agent workflows:** `planning-workflow` delegates handoff-doc discipline here from its Living Plan section rather than duplicating the rules. The implementer and reviewer subagents (`agents/implementer.md`, `agents/reviewer.md`) load this skill alongside their role-specific review-loop protocol. The other workflow skills (`execution-workflow`, `integration-workflow`, `merge-workflow`) inherit the discipline indirectly through the subagents they dispatch; they do not need to reference `handoff-doc` directly.
