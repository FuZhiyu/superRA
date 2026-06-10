---
title: "Skill Definition + Inventory"
status: approved
depends_on:
  - core-data-layer
  - cli-scripts
  - dashboard
tags: []
created: 2026-05-23
---

## Objective

Write `SKILL.md` with core concepts (everything is a task, `## Objective` planner-owned, `## Results` implementer-owned recursive, filesystem hierarchy, sibling-only deps, status rollup), directory structure, full command surface with examples, task file format template, auto-rebuild note, `--upgrade` docs. Update `CATEGORIES.md` and `README.md` skill inventory.

## Results

### Key Findings
- SKILL.md: ~170 lines, core concepts + directory structure + command surface + format example
- Auto-rebuild and `--upgrade` documented in command surface
- `CATEGORIES.md`: one-line addition to Utility table
- `README.md`: one-line addition to Utility Skills table

## Review Notes

1. **[MAJOR]** [SKILL.md:89](../../../skills/task-tree/SKILL.md#L89) — the move paragraph paraphrases [commands.md §Move / rename a task](../../../skills/task-tree/references/commands.md#L47) (link rewriting, dependency validation, hook-as-guardrail framing) and then also points to it — the paraphrase-plus-pointer anti-pattern `CLAUDE.md §Teach the Protocol` marks `[BLOCKING]`; the two copies already phrase the hook's role differently. Fix: keep the one-line invariant (intentional path changes go through `superra task move`, not raw `mv`/`git mv`) plus the pointer; delete the mechanics restatement.
2. **[MAJOR]** [internals.md:265](../../../skills/task-tree/references/internals.md#L265) — §Script Inventory, the contributor-facing map of the scripts directory, omits `cli.py` (the front-end the wrapper actually invokes), `task_check.py`, `task_hook.py`, `_worktree_discovery.py`, and `dashboard_artifact_workflow.py`, and describes `test_task_tree.py` as "Test suite for `_task_io.py`" when it tests every concern and six other test modules exist. Fix: regenerate the table from the live directory.
3. **[MINOR]** [internals.md:5](../../../skills/task-tree/references/internals.md#L5) — §Setup restates the bootstrap command (verbatim copy of [SKILL.md:25-30](../../../skills/task-tree/SKILL.md#L25)) and the contributor run-lines owned by `CLAUDE.md §Local Task-Tree CLI Development`, which it also points to. Fix: keep only the behavior-shaping "never bare `uv run superra` from a research project" line plus pointers.
4. **[MINOR]** [internals.md:117](../../../skills/task-tree/references/internals.md#L117) — §Hook Architecture's core is a single ~350-word paragraph mixing matcher gating, the render-integrity check, auto-cascade classification, scoping rationale ("the human integrates nuance" — design essay per `CLAUDE.md §Minimal, Targeted Instructions`), and payload format. Fix: split into per-concern bullets; move rationale to commit history.
5. **[MINOR]** [internals.md:82](../../../skills/task-tree/references/internals.md#L82) vs [task-file-contract.md:19](../../../skills/task-tree/references/task-file-contract.md#L19) — the parked-status rollup semantics (archived/postponed exclusion, all-parked branch rules) are spelled out in full in both references. Fix: make the contract authoritative; have the `compute_status` table row point to it.
6. **[MINOR]** [SKILL.md:90](../../../skills/task-tree/SKILL.md#L90) — leftover editorial comment `<!-- no need to route back to using superra -->` shipped in the skill body. Fix: delete.
7. **[MINOR]** [SKILL.md:77](../../../skills/task-tree/SKILL.md#L77) — the routing table gives no home for `superra task check`, the tree's validation entry point; it is mentioned only as raw-`mv` recovery advice in [commands.md:62](../../../skills/task-tree/references/commands.md#L62) and in passing in internals.md. Fix: add a routing row and a short diagnostics note in commands.md.
8. **[MINOR]** [CATEGORIES.md:45](../../../skills/CATEGORIES.md#L45), [README.md:97](../../../README.md#L97) — both inventory entries (this task's scope) still say "HTML dashboard generation"; the dashboard is a live SSE server with the static `generate` path deprecated ([internals.md:238](../../../skills/task-tree/references/internals.md#L238)). The entries are also near-duplicate ~90-word paragraphs of each other and of SKILL.md's routing table. Fix: update the dashboard wording and trim both to discovery-level descriptions.
9. **[MINOR]** [task.md:19](task.md#L19) — `## Results` describes the v1 artifact ("~170 lines, core concepts + directory structure + command surface"; "one-line addition" inventory entries); the live SKILL.md is a 90-line routing layer over three references and the inventory entries are full paragraphs. Fix: implementer refreshes Results to describe the current skill surface (Results is implementer-owned; not edited here).
