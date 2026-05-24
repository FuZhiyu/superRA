---
name: handoff-doc
description: "Use whenever creating a .plan/ task hierarchy from scratch, maturing results into their permanent record at INTEGRATE, or when you need the full editing discipline for task.md files. Carries the four document principles, the inline-edit rule, the stale-content checklist, and pointers to full plan-anatomy and results-anatomy references. Usable standalone by a single author with no subagents — the author plays all roles and reads this skill directly. Doc-creation call sites: `planning-workflow` Phase 2 (new .plan/ hierarchy) and `integration-workflow` Step 3 doc-writer (Stage 2 maturation)."
---

# Handoff Doc Discipline

Handoff docs (`.plan/` task hierarchy) are the persistent state of a project — multiple agents and sessions read and write them. References:

- `references/plan-anatomy.md` — root task.md anatomy, task.md anatomy, and the **User Decisions Log** spec.
- `references/results-anatomy.md` — the **two-stage results lifecycle** (Stage 1 dev log in `## Results` -> Stage 2 permanent record).

Subagent review-loop mechanics live in `agents/implementer.md` and `agents/reviewer.md`.

## The Four Principles

1. **Latest state only, no history.** Handoff docs reflect current intent and current findings. They are not changelogs — git owns history. No "Previously...", no strikethroughs, no "Update:" blocks, no stacked review rounds.

2. **Live and committed.** Every edit is an inline replacement, committed atomically with the work it belongs to. Stale sections, stale review notes, and superseded discovery notes are **removed**, not struck through. The doc at any point reads as a single coherent current-state description.

3. **Task hierarchy structure.** `.plan/` is a root task.md plus a recursive tree of child task directories; each task.md has frontmatter and flexible body sections. The full anatomy lives in `references/plan-anatomy.md`.

4. **The doc is the record. Status reports are pointers, not substitutes.** Any material finding, result, methodology change, caveat, or decision MUST be written into the relevant `task.md` *before* it is communicated in a status report or chat message. If a result exists only in chat, it does not exist — it will be lost at the next session boundary, cache eviction, or context compaction.

   **Rule of thumb:** before typing a finding into a status report, ask "is this written in task.md yet?" If not, write it in the doc first and commit, then point at it in the report.

## Inline-Edit Rule

Every edit replaces stale content in place. Never append, never strike through, never use "Update:" / "Revised:" / "Previously..." framing. History belongs in the git commit message.

## Stale Content Checklist

Common stale content to replace in place:

- Task objectives describing an approach abandoned after seeing the data — rewrite them.
- Results sections now incorporated into the current approach.
- Review items confirmed fixed on re-review (the reviewer deletes from `## Review Notes`).
- Sibling task objectives that assume an earlier approach which has since changed.
- Task output descriptions superseded by a later task — rewrite the earlier task's `output:` frontmatter to reflect the latest shape; keep the "what changed" narrative in the Decisions section only.

## User Decisions Log

Researcher answers to `AskUserQuestion` / plain-text pauses are written into the relevant `task.md` **before** the agent acts on them, committed atomically with the work they unblock. The decision is not resolved until it is in the record. Full contract: `using-superra/references/main-agent.md`.

Full spec — where task-scoped vs project-level decisions land, the three-line blockquote format, the hook reminder, and what does NOT count as a decision — lives in `references/plan-anatomy.md` §User Decisions Log.

**`## Conventions`** — populated at `planning-workflow` Phase 3 in the root task.md; anatomy in `references/plan-anatomy.md §Conventions`.

**Figure embedding and code-file citations** — discipline in `report-in-markdown/references/rich-content.md`; Stage 2 materialization in `report-in-markdown/references/final-form.md`.
