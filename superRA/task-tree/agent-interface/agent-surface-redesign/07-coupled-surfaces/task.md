---
title: "Finalize Coupled Agent-Facing Surfaces"
status: implemented
depends_on:
  - 06-restructure-specs
tags: []
created: 2026-06-01
---

## Objective

Finalize the coupled agent-facing surfaces the user partially edited so they cohere with the redesigned specs and strand no guidance. Scope: [skills/using-superRA/SKILL.md](../../../../../skills/using-superRA/SKILL.md) §Task Interface and §Skill-Load Manifest, and [skills/report-in-markdown/SKILL.md](../../../../../skills/report-in-markdown/SKILL.md).

**using-superRA §Task Interface.** Fix the dangling "Tasks" sentence fragment the user left mid-edit. Make §Task Interface instructions-only (how to read and edit your assigned task) and point out for the rest: per-role ownership now lives in the role specs' "What You Own"; tree tooling is the load-on-demand `task-tree`. Ensure the ownership-boundary principle (edit only what your role owns; raise another role's content rather than overwriting) stays reachable — either as a one-line principle here or a pointer to the role specs. Keep the load-on-demand `task-tree` pointer the user re-added.

**report-in-markdown.** The user removed the §Load map and the "permanent artifacts only" note on baseline-io. Do not strand the load-condition guidance it carried: relocate "load `rich-content.md` for figures/math/tables" and "`baseline-io.md` applies to permanent standalone artifacts" into the References section as one-line "load when" conditions (or into the consuming surfaces). Confirm the known consumers still reach the right reference — `econ-data-analysis`, `theory-modeling`, `writing`, `superintegrate`, `task-tree/references/planning.md`, and the implementer §Self-Check figures line. Keep the user's strengthened file-reference rule ("Always cite source files as markdown links…").

**Manifest domain-add-ons (user's inline comment).** Collapse the §Domain add-ons subsection to a short pointer ("load the relevant domain skill") and move its clearer "when the task involves…" trigger conditions up into the Skill Inventory table descriptions, so trigger conditions live with the inventory. Preserve the "domain add-ons compose with — do not replace — the generic row" note and the "applies to main agents and subagents" note. If the user's trim of the manifest's explanatory line stranded the `using-superra`/`report-in-markdown` always-loaded note or the Task-Interface/role-spec pointer, repair it.

**Verification:** no consumer of the removed load-map is left without a path to its reference; the manifest still routes every `Stage:`; `skill-creator` loaded before editing these `SKILL.md` files; `task_check.py --plan-root superRA` clean. No generated artifacts depend on these files, so no regen is required here (regen is covered by 01 and 02).

## Planner Guidance

This task edits `skills/using-superRA/SKILL.md` after task 01 has already edited it (01 added the planning-review manifest row and may have touched the report-in-markdown skills line) — work from the post-01 state and integrate rather than revert those changes. The domain-add-ons "when" conditions to migrate are in the current §Domain add-ons table; the Skill Inventory table to receive them is §Skill Inventory.

## Results

Three coupled surfaces updated.

**[skills/using-superRA/SKILL.md](../../../../../skills/using-superRA/SKILL.md):**

- §Task Interface: fixed the dangling "Tasks" fragment → complete Edit instruction; added ownership-boundary principle as a one-liner pointing to role specs §What You Own; replaced double blank + verbose task-tree paragraph with a clean one-liner.
- §Skill Inventory domain rows: migrated the "when the task involves…" trigger conditions from §Domain add-ons into the `econ-data-analysis`, `theory-modeling`, and `writing` descriptions — triggers and skill description now co-located.
- §Skill-Load Manifest: restored the trimmed always-loaded elaboration (`implementer / reviewer via frontmatter preload … main agent via explicit Skill invocation`; `report-in-markdown` always-loaded because every agent writes markdown).
- §Domain add-ons: collapsed from trigger-condition table + 3 standalone notes to a 2-line pointer — trigger conditions live in §Skill Inventory, compose/applies notes preserved inline.
- Removed the `<!-- ... -->` inline comment.

**[skills/report-in-markdown/SKILL.md](../../../../../skills/report-in-markdown/SKILL.md):**

- References section: added "load when" conditions to both entries — `rich-content.md` for figures/math/complex tables; `baseline-io.md` for permanent standalone artifacts (not task files or status returns).
- File-reference rule left unchanged (user's strengthened version preserved).

**Consumer reachability confirmed:** `task-tree/references/planning.md` references `rich-content.md` by path directly. `theory-modeling`, `writing`, and `superintegrate` reference `report-in-markdown` by skill name. The implementer §Self-Check figures line is intact. All consumers retain a load path to the correct reference.

**Verification:** `task_check.py --plan-root superRA` → all checks passed. No generated artifacts depend on these files; no regen required.

## Review Notes

> 1. [MAJOR] The manifest baseline this task finalized claims `using-superra` and `report-in-markdown` are "the two skills every agent already loads (subagents via frontmatter preload, …)" ([using-superRA/SKILL.md:90](../../../../../skills/using-superRA/SKILL.md#L90)), but [reviewer.md:8](../../../../../agents/reviewer.md#L8) preloads only `using-superra` — the baseline is false for reviewer subagents, who write `## Review Notes` markdown without the style guide the inventory calls "always-loaded alongside using-superra". Add the preload to the reviewer spec (and regenerate) or correct the manifest baseline.
>    → implemented: added `superRA:report-in-markdown` to reviewer.md frontmatter `skills:` line ([reviewer.md:8](../../../../../agents/reviewer.md#L8)); regenerated all four artifacts; `--check` exits 0
> 2. [MINOR] The `documentation` stage row lists `report-in-markdown` as an additional required skill ([using-superRA/SKILL.md:103](../../../../../skills/using-superRA/SKILL.md#L103)) although line 90 declares it always-loaded — internally contradictory; make the row `—` or drop the always-loaded claim.
>    → implemented: changed `documentation` row required skills to `—` ([using-superRA/SKILL.md:103](../../../../../skills/using-superRA/SKILL.md#L103))
> 3. [MINOR] "`Stage: planning-review` is a reviewer-only planning pass; its mechanics live in `skills/superplan/references/planning-review.md`" ([using-superRA/SKILL.md:105](../../../../../skills/using-superRA/SKILL.md#L105)) restates the table row five lines above (line 98 names the same reference), and reviewer.md states the redirect a third time; one statement should own it per the DRY gate.
>    → implemented: removed the duplicate standalone note from [using-superRA/SKILL.md](../../../../../skills/using-superRA/SKILL.md) after the table (table row at line 98 is now the single statement); reviewer.md's single redirect line at line 22 remains as the role-spec's own pointer to the reference
