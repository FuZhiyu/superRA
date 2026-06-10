---
title: "Rewrite planning-workflow SKILL.md"
status: approved
depends_on: []
tags: []
created: 2026-05-24
---

## Objective

Rewrite `skills/planning-workflow/SKILL.md` with a new 5-phase structure that is domain-neutral, exploration-first, and existing-plan-aware.

### New Phase Structure

**Phase 0: Task Tree Discovery** — Check for existing `.plan/` in working directory. If found, read the tree, summarize current state, and assess whether the new work relates to any existing root-level task. If related, recommend updating the existing task (routes to §User Feedback and Changing Plans) and let the user confirm or redirect. If not related, create a new root-level task. If no existing tasks, skip to Phase 1. Also check for legacy PLAN.md and offer migration.

When adding to an existing tree, Phase 0 determines **where in the tree** the new work belongs — new root-level task (independent workstream) or subtask under an existing task. Present the existing tree to the user and let them decide placement.

**Phase 1: Exploration** — Domain-neutral context exploration before planning. Read project structure, existing code, data directories, documentation, CLAUDE.md/README.md files, git history for relevant prior work. Depth is adaptive: lightweight scan for simple/known work, deeper systematic exploration for complex/unfamiliar projects. This is where domain skills' hard-gate data gathering begins (data inventory exploration, model primitives survey, manuscript assessment) — but the phase itself is domain-neutral.

**Phase 2: Domain Setup & Scope** — Identify domain vertical (unchanged routing table), load domain skill's planning reference, satisfy hard gates. Scope check: split independent workstreams. (Merges current Phase 1 + Phase 2, reordered after exploration.)

**Phase 3: Design & Task Decomposition** — Map artifact pipeline, walk project conventions (cache in root task.md `## Conventions`), create/update `.plan/` task tree. Pipeline file for multi-artifact work. References `task-tree/references/planning.md` for objective writing and task splitting. (Merges current Phase 3 + Phase 4.)

**Phase 4: Review & Commit** — Self-review checklist. Then present the plan to the user for review before committing: show the task tree (via `task_query.py --tree`), highlight key design decisions, and ask for approval. Commit only after user approval. Hand off to implementation-workflow.

### Plan Updates and Revision Notes

**Drop `## Decisions` log.** Methodology decisions are folded into the task objective directly. The objective is always self-sufficient — rewritten fully on every update, not patched.

**Revision notes for plan changes.** When a task is updated (scope change, methodology pivot, added/removed work), add a `## Revision Notes` section with a brief delta: what changed, why, and how significant (trivial/mechanical vs substantive). This signals to the next agent whether they need to re-explore or can proceed directly. Revision notes follow the same cleanup lifecycle as review notes — cleaned out when the task is re-implemented and approved.

**Update discipline:** When updating a task objective, rewrite it to be fully self-sufficient with the new scope. Don't just change a number — include all planning context. The revision note carries the delta signal; the objective carries the full current state.

### Sections to Keep (adapt as needed)
- Retroactive Plan Creation
- Living Plan and Results
- .plan/ Is the Task Tracker
- User Feedback and Changing Plans (adapted: drop `## Decisions` protocol, add revision notes)
- Remember

### Design Principles

**"Plan" is the verb, not the noun.** "Planning" is the process (this workflow). Everything in `.plan/` is a **task** — root-level tasks scope a workstream, nested tasks are dispatchable work. `.plan/` is "the task tree," not "the plan." There is no separate "plan" artifact type. This convention must be reflected throughout the SKILL.md language: use "task tree" not "plan" when referring to the `.plan/` artifact, "planning" not "plan creation" when referring to the process.

Also add this convention to:
- `CLAUDE.md` contributor guidelines (under a terminology or conventions section)
- `task-tree/references/planning.md` (terminology note at the top)

Other principles:
- Core phases are domain-neutral — no assumption of software engineering, data analysis, or any specific domain
- Domain skills plug in at Phase 2 with their hard gates and templates
- Exploration depth is the agent's judgment call, not a mechanical rule — teach the mechanism, not a contingency tree
- Borrow the exploration-before-design spirit from Claude Code plan mode, adapted for research: understand data, code, papers, conventions before designing tasks
- Phase 0 ensures we never create duplicate tasks or lose track of existing work

## Results

### Files Modified

- [`skills/planning-workflow/SKILL.md`](skills/planning-workflow/SKILL.md) — Complete rewrite. New 5-phase structure (Phase 0-4): Task Tree Discovery, Exploration, Domain Setup & Scope, Design & Task Decomposition, Review & Commit. Dropped `## Decisions` log from task-tree creation and change protocol. Added `## Revision Notes` mechanism. Renamed sections to use "task tree" terminology throughout. Kept and adapted: Retroactive Plan Creation, Living Task Tree, .plan/ Is the Task Tracker, User Feedback and Changing the Task Tree, Remember.
- [`CLAUDE.md`](CLAUDE.md) — Added §Terminology section with the "plan is the verb" convention.
- [`skills/task-tree/references/planning.md`](skills/task-tree/references/planning.md) — Added terminology pointer at the top, referencing CLAUDE.md §Terminology.

### Key Design Decisions

- **Terminology authority chain:** CLAUDE.md §Terminology is the project-wide canonical source. SKILL.md §Overview carries the full convention (owning skill — shapes every word choice in the file). planning.md points to CLAUDE.md.
- **`## Decisions` removal is scoped:** This task drops `## Decisions` from the SKILL.md (no longer created in Phase 3, no longer logged in the change protocol). The deeper removal from `planning.md` (§User Decisions Log, §Field-by-Field Notes, §Root task.md Anatomy) is owned by the `revision-notes` sibling task.
- **Phase 3 merges old Phase 3 + Phase 4.** The old file-structure and task-decomposition phases were artificially split; the new Phase 3 covers artifact pipeline mapping, task structure, creation, and dependencies in one coherent section.
- **Phase 4 adds user review gate.** The old Self-Review section is now Phase 4 with an explicit user-review step before commit — the task tree is presented to the user for approval, not auto-committed.
