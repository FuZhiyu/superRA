---
title: "Create harness-plan-mode.md reference"
status: revise
depends_on: []
tags: []
created: 2026-05-24
---

## Objective

Create `skills/planning-workflow/references/harness-plan-mode.md` — a reference file that teaches agents how to use harness-provided plan mode (Claude Code, Codex) productively while outputting directly to `.plan/` at exit.

### Problem This Solves
When harness plan mode is active, the agent is constrained to write only a specific plan file in a harness-prescribed format. Currently, the agent creates a plan in that format and then must migrate it to the `.plan/` task tree — a two-step process that loses information (task dependencies, frontmatter fields, structured objectives get flattened).

### Design
The reference teaches a single principle: **harness plan mode is your exploration and approval environment; `.plan/` is the output.**

**During plan mode (read-only):**
- Use harness tools productively: Explore subagents for broad context, file reads for project understanding
- Run Phases 0–2 of the planning workflow (Discovery, Exploration, Domain Setup) within the read-only constraint
- Write a **flattened view of the planned `.plan/` changes** in the harness plan file — showing each task with its title, objective, dependencies, and placement in the tree. This is NOT the authoritative plan, but it presents the same information the user would see after `.plan/` creation, in a readable flat format suitable for review and approval in plan mode

**At exit from plan mode:**
- The agent returns to normal mode with full write access
- Create `.plan/` task tree directly from the agent's full understanding (conversation context, exploration findings, design decisions)
- No migration needed — the plan file was never the authoritative plan

**Harness plan file template:**
Provide a structured template that mirrors what `.plan/` will contain. For each planned task: path in tree, title, objective (full text), `depends_on`, `script`/`input`/`output` when known. Include the tree visualization and DAG. The user reviews this flat representation; on approval and exit, the agent creates the actual `.plan/` task files from it. The template should be close enough to the task.md format that writing it is also writing the plan — just in a single-file flat format instead of a directory tree.

### Load Condition
This reference is loaded when the harness activates plan mode AND the agent recognizes it is in a superRA context. Add a load directive in SKILL.md: "If the harness has activated plan mode, load `references/harness-plan-mode.md` before proceeding."

## Results

Created [`skills/planning-workflow/references/harness-plan-mode.md`](../../../../skills/planning-workflow/references/harness-plan-mode.md) with four sections:

- **Core Principle** — states the non-default constraint: plan mode is exploration + approval; `.plan/` is the output; the plan file is not authoritative
- **During Plan Mode** — names the three pre-write phases (Discovery, Exploration, Domain Setup) and requires writing the plan file last after exploration and domain hard gates are satisfied
- **What Goes in the Harness Plan File** — specifies the per-task fields (path, title, objective, depends_on, script/input/output) plus tree visualization and dependency DAG
- **At Exit from Plan Mode** — instructs direct creation of `.plan/` from conversation context; no migration

Also added a load directive in [`skills/planning-workflow/SKILL.md`](../../../../skills/planning-workflow/SKILL.md) immediately after the `using-superra` load line: "If the harness has activated plan mode, load `references/harness-plan-mode.md` before proceeding."

DRY/Necessity gate applied: every line either states a non-default constraint, provides a concrete format the agent needs, or scopes when to load. No restated defaults, no cross-skill pattern citations, no design essays.

## Review Notes

1. **[MAJOR]** Dead Results links: both citations target `skills/planning-workflow/references/harness-plan-mode.md` and `skills/planning-workflow/SKILL.md`, paths renamed to `skills/superplan/…` — the links no longer resolve and the durable record misleads about the live owner. Fix: repoint to [harness-plan-mode.md](../../../../skills/superplan/references/harness-plan-mode.md) and [superplan/SKILL.md](../../../../skills/superplan/SKILL.md), or annotate as historical.
