---
title: "Author the interactive-mode canvas-loop reference"
status: not-started
depends_on:
  - superplan-decrowd
---

## Objective

Add `skills/superplan/references/interactive-mode.md` defining the interactive canvas — a **light-plan → execute-yourself → record** loop, co-edited with the researcher, sized for concentrated work (not trivial jots). It spans a spectrum of plan/execute interleaving, all through the same task file:

- **Light-plan, then execute.** Lightly scope a target/objective into a task file (a light superplan — positioning retained, but skipping the full exploration / domain-gate / decomposition choreography), then execute yourself and record results in place.
- **Retroactive capture — the ultimate interactive form.** Do the work first, then write it down: create the task and write the results in after the fact. Embeds superplan's retroactive documentation mode (see `references/task-tree-design.md §Retroactive Task-Tree Creation`); run the same machinery results-first rather than forking a parallel path.

Across the spectrum:

1. **Co-edit** targets, objectives, and results into the task file via the `using-superra` §Task Interface.
2. **Self-review always** — apply domain judgment (e.g. Iron Law, evidence-before-claims for data work) as a genuine pass, not a heavy multi-item ceremony.
3. **Commit instantly** per edit, per `using-superra` §Commit Hygiene.
4. **Prompt the researcher: review now / defer / skip.** "Now" dispatches a reviewer subagent (full gated pass) → `approved`. "Defer/skip" leaves the task at `implemented` for a later deferred-review sweep. No new status values.
5. **Continue, pausing frequently for feedback.**

Positioning routes to `references/task-tree-design.md §Placing Work`. The confirm-intent gate for task-tree changes **collapses when the human is the editor** (their message is the authorization); it remains only for agent-initiated scope changes. Dashboard pairing: recommend running the dashboard in live-serve as a read-only canvas view.

Success: the reference is self-contained for a main agent running the mode across both forward light-planning and retroactive capture, loadable via a clear condition from the de-crowded `superplan/SKILL.md`, and consistent with the retained positioning discipline.

## Planner Guidance

Progressive disclosure — `SKILL.md` stays lean; this reference carries the loop. Retroactive capture is the same machinery run results-first — reuse superplan's retroactive documentation path, do not fork a parallel one. Reuse `implemented`/`approved`; do not invent an "awaiting-review" status (see `task-tree/references/task-file-contract.md §Task Anatomy`). Editable-from-dashboard is out of scope. Depends on `superplan-decrowd` so it plugs into the new routing rather than the old crowded structure.
