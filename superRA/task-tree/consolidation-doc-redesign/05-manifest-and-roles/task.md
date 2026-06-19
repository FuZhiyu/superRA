---
title: "Wire merged stage into manifest, role specs, and generated artifacts"
status: approved
depends_on:
  - 01-core-stage-redesign
  - 02-consolidation-mechanics
  - 03-results-disposition
tags: []
created: 2026-06-18
---

## Objective

Wire the merged stage (named by task 01) into the dispatch surfaces, and regenerate the generated artifacts.

- **Skill-Load Manifest (`skills/using-superra/SKILL.md` §Skill-Load Manifest).** Add/adjust the Stage row for the merged stage. Because harness skill-loading is skill-granular, the row lists **skills**: `task-tree`, `superplan` (for `task-tree-design.md` + `consolidation.md`), `report-in-markdown`, and `writing` (conditional, for prose-heavy maturation). The stage reference in `superintegrate` names which references within those skills the agent reads. If task 01 reused `documentation` rather than introducing a new stage value, update that row instead of adding one.
- **Role specs (`agents/implementer.md`, `agents/reviewer.md`) — do NOT add a maturation clause.** Keep both role bodies lean and stage-generic. The orchestrator's dispatch already prompts the role at `Stage: maturation`: the `Additionally:` tails in `superintegrate` §Mature & Consolidate Step 3 (implementer) and Step 4 (reviewer) name what to execute/verify and which owners to read. A per-stage clause in the generic role body duplicates that authoritative dispatch text (the "wrapper around authoritative content" anti-pattern). Remove the line at `agents/implementer.md` beginning "At `Stage: maturation`, the contract is the recorded `## Revision Notes` distillation…" and the symmetric `Stage: maturation` whole-tree-review sentence inside `agents/reviewer.md` step 3.
- **Regenerate generated artifacts** via `skills/codex-superra-setup/scripts/sync_codex_agents.py`: `direct-mode-implementer.md`, `direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml`. Do not hand-edit the generated files; if their content is wrong, fix the source spec or generator and re-run.

**Success:** the manifest has a correct merged-stage row; neither role spec carries a `Stage: maturation` clause (the dispatch tails own that prompting); the four generated files are regenerated from the cleaned source and match; `sync_codex_agents.py` runs clean.

## Planner Guidance

Confirm the exact generated-file list and generator invocation against repo `CLAUDE.md` §"Codex and Harness Design" before running. Depends on 01–03 because the role text must reference the final stage name, mechanics, and disposition menu.

## Results

The merged stage is wired through the dispatch surfaces, with the per-stage clauses kept out of the generic role bodies.

- **Skill-Load Manifest** ([skills/using-superra/SKILL.md](../../../../skills/using-superra/SKILL.md) §Skill-Load Manifest) carries the merged-stage row as shipped — unchanged this round.
- **Role specs stay lean and stage-generic.** Removed the `Stage: maturation` clause from [agents/implementer.md](../../../../agents/implementer.md) §Execution Protocol (the line beginning "At `Stage: maturation`, the contract is the recorded `## Revision Notes` distillation…") and the symmetric whole-tree-review sentence embedded in step 3 of "How You Write a Review" in [agents/reviewer.md](../../../../agents/reviewer.md). The orchestrator's dispatch `Additionally:` tails own that prompting — [superintegrate §Mature & Consolidate](../../../../skills/superintegrate/SKILL.md) Step 3 (implementer) and Step 4 (reviewer) each name what to execute/verify and which owners (`superplan/references/consolidation.md`, `task-tree/references/task-file-contract.md` §Results Shape) to read, so the role-body clauses were the "wrapper around authoritative content" duplication the contract forbids.
- **Regenerated the four artifacts** from the cleaned source via `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`: [.codex/agents/superra_implementer.toml](../../../../.codex/agents/superra_implementer.toml), [.codex/agents/superra_reviewer.toml](../../../../.codex/agents/superra_reviewer.toml), [direct-mode-implementer.md](../../../../skills/using-superra/references/direct-mode-implementer.md), [direct-mode-reviewer.md](../../../../skills/using-superra/references/direct-mode-reviewer.md). No hand edits.

**Verification.** `sync_codex_agents.py --scope project --check` exits 0 ("All generated agent files are up to date" / "All generated direct-mode role references are up to date"). `grep -rn "maturation"` over the four generated files returns no matches — the regenerated artifacts no longer carry the maturation clauses. Working tree shows exactly the six expected files (two source role specs + four generated artifacts).
