---
title: "Slim Role Specs + Regenerate Direct-Mode"
status: approved
depends_on:
  - 01-core-in-using-superra
tags: []
created: 2026-06-01
---

## Objective

Slim `agents/implementer.md` and `agents/reviewer.md` so they stop duplicating the shared task-editing interface (now in `using-superRA/SKILL.md §Task Interface`, task 01) and keep only genuinely role-specific protocol. Then regenerate the derived direct-mode references and Codex agent files. Depends on task 01 because the role specs must point at the new section.

**Remove the duplicated shared block.** Both `agents/implementer.md §Editing Etiquette` and `agents/reviewer.md §Editing Etiquette` carry the same shared principles (inline-edit only / latest-state-not-log / cite-as-markdown-links / doc-before-report). These are now owned by `using-superRA §Task Interface`. Replace each `§Editing Etiquette` shared block with a one-line pointer to that section, and delete the `Compact etiquette below; full discipline in task-system/references/planning.md. Load superRA:task-system on demand…` lead-in (the shared discipline is no longer "below", and the on-demand `task-system` load is no longer how an agent gets the interface). Keep the planning.md pointer only where genuinely needed for planner-depth (e.g., stale-content / results-shape), not as the route to basic editing.

**Keep (role-specific — do NOT move to the core):**
- `implementer.md`: `### What You Own, What You Don't` (the concrete implementer ownership: `## Results` + `status` up to `implemented`), `### How You Fix Review Items on a REVISE Round` (the `→ implemented:` annotation mechanics and the example block).
- `reviewer.md`: the verdict protocol (APPROVE/REVISE), `### What You Own, What You Don't` (reviewer owns `## Review Notes` + status transitions + `## Revision Notes` removal at approval), `### How You Write a Review` (first-review and re-review mechanics, `→ orchestrator:` handling, item-deletion authority).

These are role-specific interaction protocols, not shared interface, and must stay in the role specs. Only the *shared* editing principles move out. Where a role spec's etiquette bullet is a role-flavored *example* of a shared principle (e.g. reviewer "remove the `## Review Notes` section when empty"), keep the role-flavored line but drop the generic principle statement that now lives in the core.

**Do NOT touch step 4** (the `## Conventions` / `task_read` instruction in `## Before You Start`) — explicitly out of scope this round per the parent task.

**Regenerate the derived files.** After editing the source `agents/*.md`, run the generator and commit the regenerated artifacts together with the source edits:
```
python3 skills/codex-superra-setup/scripts/sync_codex_agents.py   # confirm exact subcommand/flags from its --help
```
Generated targets (never hand-edit): `skills/using-superRA/references/direct-mode-implementer.md`, `skills/using-superRA/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml`. Confirm the generated direct-mode references inherit the slimmed etiquette (they currently carry the same duplicated block via the generator) and now point to `using-superRA §Task Interface`.

**Discipline.** Apply the DRY/Necessity gate line-by-line. Do not delete a role-specific protocol line just because it mentions editing — only the *shared* principles move. If unsure whether a line is shared or role-specific, ask: would the reviewer and implementer phrase it identically? If yes, it is shared (core); if it differs by role, it stays.

**Validation (must be true to be complete):**
- The shared editing-principles block appears in exactly one place (`using-superRA §Task Interface`), not in either role spec.
- Each role spec still fully specifies its own ownership, annotation mechanics, and (reviewer) verdict protocol — no role behavior is lost.
- `sync_codex_agents.py` was run; the four generated files are regenerated, committed, and consistent with the slimmed sources (verify with `git status` that they changed and were not hand-edited).
- Step 4 is unchanged.
- **No knowledge lost:** the only thing removed from the role specs is the *shared* editing-principles block (now in `using-superRA §Task Interface`); every role-specific protocol line survives. Task `09-coverage-audit` verifies this against a git snapshot.

**Output:** `agents/implementer.md`, `agents/reviewer.md`, and the four regenerated files above.

## Results

Slimmed both role specs' `### Editing Etiquette` to a pointer at `superRA:using-superra` §Task Interface (task 01's section), keeping only role-flavored lines, then regenerated all four derived files.

**Source edits:**
- [agents/implementer.md §Editing Etiquette](../../../../../agents/implementer.md#L64) — replaced the `Compact etiquette… Load superRA:task-system on demand…` lead-in, the `**The task always reflects the latest state, not a log.**` bold statement, and the four shared bullets (inline-edit / remove-superseded / cite-as-markdown-links / doc-before-report) with a one-line pointer to §Task Interface. Kept the implementer-flavored `**Stay within your assigned task.**` bullet (it ties to `→ implemented:` annotation mechanics, not a generic principle) and the closing "flag unclear structure" line.
- [agents/reviewer.md §Editing Etiquette](../../../../../agents/reviewer.md#L92) — same treatment. Kept two reviewer-flavored bullets: `**Stay within your assigned task.**` and `**Remove superseded content…**` (the reviewer-specific "remove `## Review Notes` when empty / replace prior reliability caveats, don't stack" example called out as a keeper in the objective).

**Role-specific protocol retained (verified by heading walk):**
- implementer: `### What You Own, What You Don't`, `### How You Fix Review Items on a REVISE Round` (incl. the `→ implemented:` example block), `### Update the Task and Commit`.
- reviewer: `### Verdict` (APPROVE/REVISE), `### What You Own, What You Don't`, `### How You Write a Review` (first-review + re-review, `→ orchestrator:` handling, item-deletion authority).
- Step 4 (the `## Conventions` / `task_read` instruction in `## Before You Start`) untouched in both specs.

**Regenerated derived files** via `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` (flags confirmed from `--help`; the run writes both the `.codex/agents/*.toml` agents and the `direct-mode-*.md` references). Files changed: `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml`, `skills/using-superRA/references/direct-mode-implementer.md`, `skills/using-superRA/references/direct-mode-reviewer.md`. The two direct-mode references inherited the slimmed etiquette pointer to §Task Interface.

**Verification:**
- `sync_codex_agents.py --scope project --check` → "All generated agent files are up to date" + "All generated direct-mode role references are up to date" (generated files match sources, not hand-edited).
- `git status --short` → all six files modified (two sources + four generated).
- `grep -rn "Compact etiquette\|task-system on demand" agents/ skills/using-superRA/references/ .codex/` → no matches (stale lead-in fully removed everywhere).
- `grep "Task Interface" direct-mode-*.md` → both references point to `superRA:using-superra` §Task Interface.
- Heading walk of both specs confirms every role-specific section survived; only the shared editing-principles block was removed.

DRY/Necessity gate self-applied to the two new pointer lines: each names the four shared principles only as a contents label so the reader knows what moved and where — the authoritative statements live in §Task Interface, not restated here.