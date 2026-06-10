---
title: "Sync Doc Surfaces to New Structure"
status: approved
depends_on:
  - 01-core-in-using-superra
  - 02-task-tree-slim
  - 03-role-spec-slim
tags: []
created: 2026-06-01
---

## Objective

Update every doc surface that describes the task-tree skill's structure or ownership so it matches the post-relocation reality (interface in `using-superRA`, `task-tree` is load-on-demand tooling). Depends on tasks 01–03 because it documents their final shape; do it last.

**Surfaces to update:**

1. **`CLAUDE.md` §Ownership Boundaries table.** Adjust the relevant rows: the universal task interface (read/edit mechanics, editing principles, ownership boundary) is now owned by `using-superRA`; `task-tree/references/planning.md` keeps task anatomy / field notes / results shape / stale-content; role protocol stays in `agents/implementer.md` / `agents/reviewer.md`. Also update the `## Handoff Docs`-related wording in `using-superRA/references/main-agent.md` and the `using-superRA` §Handoff Docs pointer if task 01 left any stale phrasing (verify against the actual edited files).

2. **`skills/CATEGORIES.md`** task-tree entry (line ~45). It currently reads "Consumer-facing SKILL.md body, planner-facing `references/planning.md`, contributor-facing `references/internals.md`." Rewrite to drop the "consumer-facing SKILL.md" framing — the executing-agent interface now lives in `using-superRA`; SKILL.md is tree tooling loaded on demand.

3. **`README.md`** task-tree inventory entry (line ~89). Same fix: it currently says "Consumer-facing SKILL.md covers reading, editing, and querying tasks." Update so reading/editing is attributed to `using-superRA §Task Interface` and SKILL.md is described as the load-on-demand tooling/tree-management layer.

4. **`using-superRA/SKILL.md` §Skill Inventory** — the one-line `task-tree` purpose row in the inventory table. Confirm it describes tree tooling, not "the agent's task interface." (The new §Task Interface section from task 01 is the interface; the inventory row points at the tooling skill.)

**Discipline.** Load `skill-creator` before editing skill files. Each surface is a short description, not a place to re-explain the interface — point, do not restate (DRY/Necessity gate). Keep descriptions consistent across all four surfaces (same framing of what lives where).

**Validation (must be true to be complete):**
- No surface still calls `task-tree/SKILL.md` "consumer-facing" or implies every agent must load it. Verify: `grep -rn "[Cc]onsumer-facing" skills/ README.md CLAUDE.md` returns nothing referring to task-tree SKILL.md.
- `CLAUDE.md` §Ownership Boundaries, `CATEGORIES.md`, `README.md`, and the `using-superRA` skill-inventory row all describe the same structure (interface → `using-superRA`; tooling → `task-tree/SKILL.md`; planner depth → `planning.md`; contributor depth → `internals.md`).
- The `using-superRA` skill inventory and `skills/CATEGORIES.md` remain in sync (CLAUDE.md §Skill Authoring Guidelines requires it).

**Output:** `CLAUDE.md`, `skills/CATEGORIES.md`, `README.md`, `skills/using-superRA/SKILL.md` (inventory row only).

## Results

All four doc surfaces now describe the post-relocation structure consistently: executing-agent read/edit → `using-superRA §Task Interface`; tree tooling (lean router) → `task-tree/SKILL.md`, load-on-demand; mutation commands → `references/commands.md`; planner depth → `references/planning.md`; contributor depth → `references/internals.md`. No surface calls `task-tree/SKILL.md` "consumer-facing" or implies every agent loads it.

**Surface 1 — [`CLAUDE.md` §Ownership Boundaries](../../../../../CLAUDE.md#L65).** Split the single task-tree ownership row into three pointer rows so each concern has one owner:
- Universal task read/edit interface → `using-superra` (§Task Interface).
- Tree tooling (concepts, query/frontier/DAG, dashboard, migration, mutation command surface) → `task-tree/SKILL.md` load-on-demand, commands in `references/commands.md`.
- Task anatomy / field notes / results shape / stale-content / planner-owned fields → `task-tree` (references/planning.md) — unchanged owner, refined wording.

**Surface 2 — [`skills/CATEGORIES.md`](../../../../../skills/CATEGORIES.md#L45).** Dropped the "primary handoff mechanism" + "Consumer-facing SKILL.md body" framing; now reads "Directory-tree task tooling … Load-on-demand: SKILL.md is the tree-tooling layer … with `references/commands.md` for mutation commands … The executing-agent read/edit interface lives in `using-superRA §Task Interface`, not here."

**Surface 3 — [`README.md`](../../../../../README.md#L89) inventory row.** Same fix: reading/editing your own task attributed to `using-superRA §Task Interface`; SKILL.md described as the load-on-demand tree-tooling layer with `references/commands.md` for the mutation command surface; planning.md / internals.md unchanged.

**Surface 4 — [`using-superRA/SKILL.md` §Skill Inventory](../../../../../skills/using-superRA/SKILL.md#L80).** One-line task-tree row rewritten to "Load-on-demand tree tooling … The executing-agent read/edit interface is §Task Interface above, not this skill." This row and the CATEGORIES.md row remain in sync.

**Objective item 1 sub-check (main-agent.md / §Handoff Docs).** Verified `skills/using-superRA/references/main-agent.md` and `skills/using-superRA/SKILL.md` carry no `## Handoff Docs` section and no stale task-tree framing — task 01 already restructured that content into §Task Interface, so no edits were needed there.

**Verification.**
- `grep -rn "[Cc]onsumer-facing" skills/ README.md CLAUDE.md` → no matches (exit 1).
- `grep -rn "primary handoff mechanism" skills/CATEGORIES.md README.md skills/using-superRA/SKILL.md` → no matches.
- The only "every agent already loads" line ([using-superRA/SKILL.md:96](../../../../../skills/using-superRA/SKILL.md#L96)) correctly names `using-superra` + `report-in-markdown` as the two universal loads and attributes the task interface to §Task Interface, not task-tree.

## Review Notes

> 1. [MINOR] Doc-surface sweep gap: [claude-tools.md:15](../../../../../skills/using-superRA/references/claude-tools.md#L15) carries contributor policy ("Claude remains the primary harness. Keep the shared workflow behavior in canonical `skills/` and put harness-specific mapping rules in these adapter references…") inside an agent-facing adapter reference — it restates CLAUDE.md §Codex and Harness Design for the wrong audience and shapes no agent behavior. Drop the paragraph from the adapter.
