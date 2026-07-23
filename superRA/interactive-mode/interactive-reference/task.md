---
title: "Author the interactive-mode canvas-loop reference"
status: implemented
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

## Results

Added [interactive-mode.md](../../../skills/superplan/references/interactive-mode.md) and wired one load condition into the de-crowded [superplan/SKILL.md](../../../skills/superplan/SKILL.md).

**The reference** (self-contained for a main agent running the full spectrum):

- **Framing** — a fused light-plan → execute-yourself → record loop the main agent runs with the researcher, filling both seats and pausing often. Selection axis is autonomy (concentrated, closely-steered work), not difficulty; explicit opt-in over the autonomous-subagent default; not for trivial jots.
- **Spectrum** — forward light-plan-then-execute (positioning retained, exploration/domain-gate/decomposition choreography skipped) and retroactive capture (results-first), the latter pointing to `task-tree-design.md §Retroactive Task-Tree Creation` rather than forking a parallel path.
- **Loop** — co-edit via `using-superra` §Task Interface; self-review always against the active domain skill's gated checklist; commit instantly per `using-superra` §Commit Hygiene; prompt review now (dispatch reviewer → `approved`) / defer / skip (leave at `implemented` for a deferred sweep), reusing the existing enum; continue with frequent pauses.
- **Positioning + intent gate** — routes to `task-tree-design.md §Placing Work`; the confirm-intent gate for tree changes collapses when the human is the editor (their message is the authorization), remaining only for agent-initiated scope changes. All same-`references/` sibling citations use bare filenames per the house convention.
- **Dashboard pairing** — recommend live-serve as a read-only canvas view; editing-from-dashboard out of scope.

**Wiring** — a two-sentence pointer at `SKILL.md` Entry Assessment §3 (Routing path — "what mode"), the routing seam, stating the load condition (researcher opts into interactive canvas cadence) and the reference target. Kept to a pointer per the DRY + Necessity gate.

**DRY discipline** — the reference points to owners rather than restating them: Task Interface, Commit Hygiene, the status enum, the placement descent, the retroactive machinery, and the confirm-intent gate all resolve through links. `python3 skills/report-in-markdown/scripts/check_markdown.py` reports the reference clean.
