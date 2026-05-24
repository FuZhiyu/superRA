---
title: "Update Handoff-Doc Skill"
status: implemented
review_status: revise
integration_status: ~
depends_on: 
  - skill-restructure

tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Update `skills/handoff-doc/SKILL.md` and its references for `.plan/` as the primary document format. The four principles (latest state only, live and committed, task structure, doc is the record) still apply — they're about discipline, not format.

### Changes to SKILL.md body

- Reframe from "PLAN.md / RESULTS.md" to ".plan/ task hierarchy" throughout
- "Handoff docs (`.plan/` task hierarchy)" replaces "Handoff docs (`PLAN.md`, `RESULTS.md`)"
- References to `plan-anatomy.md` and `results-anatomy.md` updated for new content

### User Decisions Log

- Decisions go in the relevant task's `## Decisions` section (any `##` section works — `## Decisions` is the recommended default)
- Cross-task decisions go in root task's `## Decisions`
- Same three-line blockquote format: `> **User decision (YYYY-MM-DD):**`, `> **Question asked:**`, `> **Rationale (if given):**`
- No separate `## Decisions` section in a monolithic file
- The `ask-user-question-logger` hook guidance adapted: log in the relevant task.md, not in PLAN.md

### Stale Content Checklist

Adapted for task.md files:
- Task objectives describing an approach abandoned after seeing the data — rewrite them
- Results sections now incorporated into the current approach
- Review items confirmed fixed on re-review (reviewer deletes from `## Review Notes`)
- Sibling task objectives that assume an earlier approach which has since changed

### `references/plan-anatomy.md`

Major rewrite for `.plan/` structure:
- **Root task.md anatomy:** `## Objective` (project-level), `## Conventions` (naming, file layout, units), `## Workflow Status` (milestone checkboxes), `## Decisions` (cross-task)
- **Task.md anatomy:** frontmatter fields (title, status, review_status, integration_status, depends_on, tags, script, input, output, created, updated) + flexible `##` body sections. Show example with recommended defaults
- **Remove:** step-checkbox anatomy (`- [ ]` / `- [x]`), monolithic task block anatomy (`### Task N:`)
- **Keep:** field-by-field notes adapted for frontmatter. Ownership rules (planner vs implementer vs reviewer)

### `references/results-anatomy.md`

Simplify or merge into plan-anatomy — results now live in task.md `## Results`, not a separate file:
- Stage 1 (implementation): task's `## Results` section is the dev log — findings, row counts, figures
- Stage 2 (integration): results maturation happens in the same `## Results` sections, restructured for reader-facing clarity
- No pre-allocation needed — each task.md starts with empty `## Results` (or whatever sections the planner writes)

### Sync Map

- `## Sync Map` in root task.md (temporary, same lifecycle as current)
- Task-local sync impact in task's `## Sync Impact` section
- Removal at Integrate closeout: delete `## Sync Map` from root, delete `## Sync Impact` from affected tasks

## Results

Rewrote all three files in `skills/handoff-doc/` for `.plan/`-native operation:

**SKILL.md** — Reframed from "PLAN.md / RESULTS.md" to ".plan/ task hierarchy" throughout. Four principles preserved with Principle 3 updated from "Task-block structure" to "Task hierarchy structure". References updated to point at new content. User Decisions Log now references task.md instead of PLAN.md. `## Conventions` replaces `## Project Conventions`.

**references/plan-anatomy.md** — Major rewrite:
- Root task.md anatomy: `## Objective`, `## Conventions`, `## Workflow Status`, `## Decisions`, `## Sync Map`
- Task.md anatomy: frontmatter fields + flexible `## Heading` body sections with recommended defaults (`## Objective`, `## Results`, `## Decisions`, `## Review Notes`)
- Removed: step-checkbox anatomy, monolithic `### Task N:` task-block anatomy, `PLAN.md` header template
- Kept: ownership rules (planner vs implementer vs reviewer), field-by-field notes adapted for frontmatter, User Decisions Log spec, Sync Map lifecycle, Conventions section discipline

**references/results-anatomy.md** — Simplified from RESULTS.md file anatomy to task.md `## Results` section anatomy:
- Stage 1: results in task.md during implementation (no pre-allocation needed)
- Stage 2: maturation in the same `## Results` sections during integration
- Removed: separate file header, pre-allocated task stubs, status tracking per section
- Kept: per-task results shape, reviewer caveats, figure embedding, Stage 2 transition pointer

## Review Notes

> 1. [MAJOR] [`skills/handoff-doc/references/results-anatomy.md:46-53`](../../../../../../skills/handoff-doc/references/results-anatomy.md#L46-L53) documents reviewer caveats at the bottom of `## Results`, but the companion `agents/reviewer.md` rewrite (in sibling task `agent-protocols`) explicitly prohibits the reviewer from touching `## Results`. The two files are now in conflict. This must be resolved consistently — see agent-protocols review item 2 for the proposed fix options. The resolution choice determines whether results-anatomy.md keeps or drops its §Reviewer Caveats section.
