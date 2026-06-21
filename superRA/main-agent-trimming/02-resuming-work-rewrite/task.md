---
title: "Rewrite main-agent.md: Resuming Work Model + Pause/Proceed Trim + Drop Inbound Pointers"
status: approved
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

**1. `Workflow Frontier Resolver` → `Resuming Work`** ([main-agent.md](../../../skills/using-superra/references/main-agent.md)). The phase-resolution procedure (read-facts / compute-frontier / route / invariants, ~25 lines) is replaced by the one cross-cutting fact nothing else owns: there is no durable workflow-stage — task `status` + the git log are the state (frontmatter is closed; INTEGRATE keeps no stage marker). Resume is status-driven: not-all-approved → implement loop via `task frontier` (which now lists implemented/revise too, per task 01); replan resets downstream to `not-started` (rule pointed to `task-file-contract` §status, not restated). The duplicated gate-invariant list (owned by superimplement/superintegrate) is dropped. The all-approved → integrate path is owned by superimplement Step 2/Step 4, so it is not restated here.

**2. Pause/proceed distilled to principle** (§Proceeding and Pausing). The five scenario bullets, banned-phrasings list, one-question section, and three domain-flavored pause classes collapse to: default to proceeding; pause only for (1) a researcher-only decision that materially changes a task objective — materiality pointed to `superplan §User Feedback`, not re-listed — or (2) a pre-set workflow gate. This is the researcher's distillation; the old class 1 (hard blocker) folds into the new class 1 because a blocker only needs the researcher when its resolution shifts scope. The dangling "If you are about to type any of these…" and the §Execution Modes "ask"→"asks" typo are fixed.

**3. Inbound pointers dropped, one survivor.** All eight `§Workflow Frontier Resolver` references removed (`grep "Frontier Resolver" skills/ agents/` → none; remaining hits are dated `docs/plans/*` historical records, intentionally left). Each owning workflow now states the next move itself: `superintegrate` keeps its local gates, `superimplement` Step 0b/Step 1/Option 2 resume on the affected frontier, `superplan` step 6 says the reset tasks reappear on `task frontier`, `agent-orchestration` says the main agent selects the frontier. The single surviving pointer is the master map in `using-superra/SKILL.md` → `§Resuming Work`. `superimplement`'s "Pause class (1)/(2)" references were renumbered to the new two-class model.

**Files (this commit):** main-agent.md, using-superra/SKILL.md, superintegrate/SKILL.md, superimplement/SKILL.md, agent-orchestration/SKILL.md. The `superplan/SKILL.md` step-6 pointer edit is intermingled with the researcher's concurrent superplan edits and is left unstaged to ride with their superplan commit.

**Verification:** `grep` confirms zero live `Frontier Resolver` / `Three Pause Classes` / `Pause class (` references in `skills/` and `agents/`; the §Resuming Work and §Proceeding and Pausing anchors exist and every surviving cross-reference resolves. Resume-scenario walk: (a) mid-implement replan → superplan §User Feedback resets downstream → §Resuming Work routes to the implement loop via `task frontier`; (b) all-approved tree → enter superimplement, Step 2 skips dispatch to Step 3/4 → superintegrate. Both route correctly from status + git alone.
