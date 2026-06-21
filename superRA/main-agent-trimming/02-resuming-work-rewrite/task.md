---
title: "Rewrite main-agent.md: Resuming Work Model + Pause/Proceed Trim + Drop Inbound Pointers"
status: not-started
depends_on: ["01-frontier-completeness"]
tags: []
created: 2026-06-21
---

## Objective

Rewrite `skills/using-superra/references/main-agent.md` so it reflects the status+git architecture and stops enumerating scenarios. Build on the researcher's in-flight unstaged edits to this file; do not revert them.

**1. Replace "## Workflow Frontier Resolver" with "## Resuming Work".** State the one cross-cutting fact nothing else owns, then defer to the owners:

- No durable workflow-stage exists — task `status` plus the git log are the only state; stages (implemented-or-not, integrated-or-not) are read from git, not a file field (INTEGRATE keeps no stage marker).
- Status-driven resume, two cases: **tree not all-approved** → resume the implement loop (whatever [01-frontier-completeness](../01-frontier-completeness/task.md) makes `task frontier` surface, plus review/fix work per the status table); **tree all-approved** → implementation is done — verify reproducibility and record the Step 4 disposition (`superimplement` Step 3–4), then resume `superintegrate`, reading integration/merge progress from git.
- On replan: reset the transitive downstream of each changed task to `not-started` (point to `task-tree/references/task-file-contract.md` §status, which owns the rule; do not restate it).
- Drop the "Read the durable facts" orientation block and the safety-invariant list that restates gates `superimplement`/`superintegrate` already enforce locally. Keep only genuinely non-default, cross-cutting invariants (if any survive the Necessity test).

**2. Trim pause/proceed to principles.** Condense "When to proceed and when to pause", "The Three Pause Classes", and the remnants of "Banned Phrasings" / "One Question at a Time" / "Log Before You Act" into the *idea*: proceed autonomously within a stage; pause only when the agent cannot answer from code and data and the answer shapes downstream work (the three classes named once, not enumerated scenario-by-scenario). Remove the banned-phrasing list. Fix the researcher's in-flight artifacts: the dangling "If you are about to type any of these…" sentence (its list was deleted) and the typo "unless the user explicitly ask to skip" in §Execution Modes.

**3. Drop the inbound pointers, don't just repoint.** Audit the eight "§Workflow Frontier Resolver" references — `superimplement/SKILL.md` (×4), `superplan/SKILL.md` step 6, `superintegrate/SKILL.md`, `using-superra/SKILL.md`, `agent-orchestration/SKILL.md`. Default to removing each: once the owning workflow says what to do next, a pointer back to a resume section is redundant. Keep a "§Resuming Work" pointer only where an agent genuinely lands cold with no owning-workflow instruction (e.g. a true session-start / post-replan handoff). Each survivor must justify itself against the DRY + Necessity gate.

**Success:**

- `main-agent.md` has a "## Resuming Work" section (no "Frontier Resolver"); pause/proceed reads as principle, not scenario list; no dangling references or typos.
- `grep -rn "Workflow Frontier Resolver"` returns only intentional survivors (ideally zero); any remaining pointer targets "§Resuming Work" and is justified in `## Results`.
- A realistic check that the changed path works: walk a resume scenario (mid-implement replan; all-approved → integrate) against the new prose and confirm an agent could route correctly from status + git alone.

## Planner Guidance

Load `skill-creator` before editing `SKILL.md` files; self-apply the CLAUDE.md DRY + Necessity gate line by line (this repo's most common drift source). The downstream-reset rule, the status enum, and the status→action table are owned by `task-file-contract` and `agent-orchestration` respectively — point, don't paraphrase. Stage only the files this task touches; leave the unrelated unstaged adapter/doc changes alone.

## Results
