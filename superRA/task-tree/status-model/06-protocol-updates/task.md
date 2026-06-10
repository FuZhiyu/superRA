---
title: "Update agent specs and workflow skills"
status: implemented
depends_on:
  - 01-design
tags:
  - docs
  - protocol
script: 
input: []
output: []
created: 2026-05-26
---

## Objective

Update all agent role specs and workflow skills to use the unified `status` field instead of the `status` + `review_status` + `integration_status` triple. The core change: where agents previously set two fields on one event, they now set one.

**Out of scope:** Rearchitecting the integration workflow for scope-flexible operation. That is tracked separately. This task removes field references and updates protocols to use `status` only.

**Agent specs:**

`agents/implementer.md`:
- §What You Own: remove `review_status:` and `integration_status:` from owned fields. Replace with: "Implementer owns `status:` transitions up to `implemented` (and `revise → implemented` on fix rounds)."
- §Update the Task and Commit: replace "Set `status: implemented` and `review_status: implemented`" with "Set `status: implemented`"
- §How You Fix Review Items: same replacement on the REVISE round commit instruction

`agents/reviewer.md`:
- §What You Own: replace `review_status:` and `integration_status:` ownership with: "Reviewer owns `status:` transitions `implemented → revise` and `implemented → approved`."
- §Verdict: replace "set `review_status: approved`" with "set `status: approved`", same for `revise`
- §Pre-Commit Self-Check: update the checklist item

**Workflow skills:**

`skills/implementation-workflow/SKILL.md`:
- §Step 2 (Execute Tasks): replace "status: implemented and review_status: implemented" with "status: implemented"
- §Step 2 reviewer dispatch: replace "review_status: approved" with "status: approved"
- §Step 3 (Verify Pipeline): remove `## Workflow Status` checkbox references

`skills/integration-workflow/SKILL.md`:
- Replace all `integration_status` references with `status` (§Integrate step, §Refactor loop, reviewer dispatch instructions, implementer fix instructions)
- Update the integration reviewer's field ownership to use `status` instead of `integration_status`

`skills/agent-orchestration/SKILL.md`:
- §Review Status Reference table: update to reference `status:` instead of `review_status:`
- §Completion gate: "task is complete when its `status` is `approved`"

`skills/planning-workflow/SKILL.md`:
- §Primary tracker: update field reference
- §Status clear instructions: now just reset `status` instead of clearing `review_status` and `integration_status` separately

**Using-superRA references:**

`skills/using-superRA/references/direct-mode-implementer.md`: same changes as implementer.md
`skills/using-superRA/references/direct-mode-reviewer.md`: same changes as reviewer.md
`skills/using-superRA/references/main-agent.md`: update frontmatter reading instructions, remove `## Workflow Status` references

**Other skill references:**

`skills/writing/references/planning.md`: update review_status references
`skills/writing/references/long-form-review.md`: update review protocol references

## Results

Updated 11 files to replace the `status` + `review_status` + `integration_status` triple with the single `status` field. All `review_status` and `integration_status` references removed from the in-scope files; verified with `grep -rn` across all 11 files (zero matches).

**Agent specs (2 canonical + 2 direct-mode generated):**

- [agents/implementer.md](../../../../agents/implementer.md) -- §What You Own: collapsed three field bullets into one (`status:` with transition ownership note). §Update the Task and Commit and §How You Fix Review Items: removed `review_status: implemented` from commit instructions.
- [agents/reviewer.md](../../../../agents/reviewer.md) -- §What You Own: replaced `review_status:` and `integration_status:` with single `status:` bullet covering both implementation and integration review transitions. §Verdict: `review_status: approved/revise` -> `status: approved/revise`. §How You Write a Review: same. §Pre-Commit Self-Check: simplified to `status:` only. Report example: `review_status` -> `status`.
- [skills/using-superRA/references/direct-mode-implementer.md](../../../../skills/using-superRA/references/direct-mode-implementer.md) -- parallel changes to implementer.md.
- [skills/using-superRA/references/direct-mode-reviewer.md](../../../../skills/using-superRA/references/direct-mode-reviewer.md) -- parallel changes to reviewer.md.

**Workflow skills (4 files):**

- [skills/superimplement/SKILL.md](../../../../skills/superimplement/SKILL.md) -- §Step 2: removed `review_status: implemented` from implementer commit description, replaced `review_status: approved` with `status: approved` for reviewer. §Step 3: replaced `## Workflow Status` checkbox flip with "proceed to the Step 4 completion menu."
- [skills/superintegrate/SKILL.md](../../../../skills/superintegrate/SKILL.md) -- 8 occurrences of `integration_status` replaced with `status` across Protect, Integrate Step 2/3/4/5, and Red Flags sections.
- [skills/agent-orchestration/SKILL.md](../../../../skills/agent-orchestration/SKILL.md) -- §Review Status Reference table: header changed from `review_status:` to `status:`, added `not-started` and `in-progress` rows, completion gate updated.
- [skills/superplan/SKILL.md](../../../../skills/superplan/SKILL.md) -- §.plan/ Is the Task Tracker: removed `/ review_status:` from field reference. §User Feedback: "Clear `review_status` and `integration_status`" replaced with "Reset `status` to `not-started`".

**Other references (3 files):**

- [skills/using-superRA/references/main-agent.md](../../../../skills/using-superRA/references/main-agent.md) -- §Workflow Frontier Resolver: frontmatter field list simplified to `status`, `depends_on`; removed `review_status` / `integration_status` from preservation and return-value language.
- [skills/writing/references/planning.md](../../../../skills/writing/references/planning.md) -- `review_status:` -> `status:` in retrofit description.
- [skills/writing/references/long-form-review.md](../../../../skills/writing/references/long-form-review.md) -- `review_status: revise` -> `status: revise` in dispatch convention; `integration_status` paragraph replaced with unified `status` note.

## Review Notes

Retrospective audit of the agent-spec / workflow-skill status surfaces this task owns (current findings; some arose after this task's original approval as the skills were renamed and extended).

1. **MAJOR** — [agent-orchestration/SKILL.md §Review Status Reference](../../../../skills/agent-orchestration/SKILL.md) (table at ~line 204) enumerates six of seven statuses; there is no `archived` row. This is the orchestrator's read-state-from-frontmatter table, and `archived` is one of the two statuses only the orchestrator/researcher sets — an orchestrator encountering it gets no guidance. The later `postponed` row was added ([13-postponed-docs](../13-postponed-docs/task.md)) without catching the gap, evidence the table restates rather than points. Fix: add the `archived` row (dependency treated as satisfied; dependents proceed), or replace the table with a pointer to the status-lifecycle owner plus only the orchestrator-action column.
   → implemented: added `archived` row to the Review Status Reference table in [agent-orchestration/SKILL.md](../../../../skills/agent-orchestration/SKILL.md).
2. **MAJOR** — Re-entry transition disagrees inside the superplan surfaces: [superplan/SKILL.md:215](../../../../skills/superplan/SKILL.md#L215) says "Reset `status` to `not-started` … by orchestrator judgment" while [task-tree-design.md:89](../../../../skills/superplan/references/task-tree-design.md#L89) and [consolidation.md:68](../../../../skills/superplan/references/consolidation.md#L68) say set affected approved tasks to `revise`. The Design Spec's state machine only sanctions `approved → not-started` for scope invalidation and makes `→ revise` reviewer-owned, so the `revise` route also creates a second, unacknowledged owner for that transition. Fix: pick one re-entry target, align all three superplan lines, and point them at the contract (contract-side ambiguity tracked in [05-task-tree-docs](../05-task-tree-docs/task.md) `## Review Notes`).
   → implemented: aligned task-tree-design.md:89 and consolidation.md:68 to use `not-started` (matching superplan/SKILL.md:215); the contract-side fix is tracked in task 05's review notes and implemented in this round ([task-tree-design.md:89](../../../../skills/superplan/references/task-tree-design.md#L89), [consolidation.md:68](../../../../skills/superplan/references/consolidation.md#L68)).
3. **MINOR** — [writing/references/planning.md:43](../../../../skills/writing/references/planning.md#L43): the review-retrofit lifecycle has reviewers moving tasks `not-started → revise/approved`, bypassing `implemented` and the contract's transition ownership. It is declared a writing-owned exception, but the lifecycle owner never acknowledges any exception exists, so the surfaces simply contradict. Fix: one clause in the contract permitting review-only trees to skip implementer states, or reframe the writing reference as orchestrator-mediated.
   → implemented: added one-sentence exception clause to task-file-contract.md status line: "Exception: review-only trees (e.g. writing-workflow review lanes) skip the implementer states entirely — tasks go directly from `not-started` to `revise` or `approved` as the reviewer sets them." ([task-file-contract.md:19](../../../../skills/task-tree/references/task-file-contract.md#L19)).
4. **MINOR** — This task's `## Results` cite [skills/implementation-workflow/SKILL.md](../../../../skills/implementation-workflow/SKILL.md), [skills/integration-workflow/SKILL.md](../../../../skills/integration-workflow/SKILL.md), and [skills/planning-workflow/SKILL.md](../../../../skills/planning-workflow/SKILL.md) — all since renamed to `superimplement` / `superintegrate` / `superplan`, so the evidence links are dead (the in-Results links are also repo-root-relative rather than task-relative). Fix: repoint the Results citations to the renamed skills with task-relative paths.
   → implemented: repointed all four Results link groups to the renamed skills with 4-up task-relative paths ([06-protocol-updates/task.md §Results](task.md)).
