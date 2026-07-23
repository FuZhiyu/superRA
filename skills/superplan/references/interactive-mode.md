# Interactive Canvas Mode

A fused **light-plan → execute-yourself → record** loop the main agent runs *with* the researcher, co-editing the task file as a live canvas. You do the work yourself and pause often for feedback instead of dispatching and running to completion; review is prompted, not automatic (§The loop, step 4).

Select it by **autonomy**, not difficulty: interactive is for work the researcher steers closely — often hard, concentrated work — where the plan and the execution move together. It is not for trivial jots. The default remains autonomous subagent execution; interactive is an explicit opt-in.

## The spectrum

One task file carries the whole range of plan/execute interleaving:

- **Light-plan, then execute.** Scope a target and objective into a task file — positioning retained, but skipping the full exploration, domain-gate, and decomposition choreography of a standard superplan pass — then execute the task yourself and record results in place.
- **Retroactive capture.** When the work is already done and the researcher asks to write it up — a handoff note, or a task that reflects what changed — run this same loop results-first: reconstruct the task and populate `## Results` after the fact via `task-tree-design.md` §Retroactive Task-Tree Creation. Route the request through this loop rather than building a separate path.

## The loop

You do not load the implementer or reviewer role specs here — this loop is your protocol for handling the task file.

1. **Co-edit** the target and objective into the task file through the `using-superra` §Task Interface.
2. **Self-review always.** Walk the active domain skill's gated checklist as a genuine judgment pass (e.g. the Iron Law for modeling, evidence-before-claims for data work) — every `[BLOCKING]` item, sized to the work, not a heavy multi-item ceremony.
3. **Keep the task updated — required.** Before each pause, record what you did into the task's `## Results` and move `status` as the work lands (`in-progress` → `implemented`). The task file, not the chat or the commit log alone, is the state of record; code commits without a task update are an incomplete step.
4. **Commit instantly** per edit, per `using-superra` §Commit Hygiene.
5. **Ask before review, with a tool — required.** Use `AskUserQuestion` (plain text only if the harness lacks it) to ask the researcher: review now / defer / skip. Never dispatch a reviewer on your own read of the situation.
   - **Now** — dispatch a reviewer subagent for a full gated pass (via `superRA:agent-orchestration`); on APPROVE the task reaches `approved`.
   - **Defer / skip** — leave the task at `implemented` for a later deferred-review sweep.

   Reuse `implemented` / `approved` for these states; do not invent an awaiting-review status.
6. **Continue**, pausing frequently for feedback before the next unit of work.

## Positioning and the intent gate

Position every task by the recursive descent in `task-tree-design.md` §Placing Work in the Existing Tree — light planning trims the choreography, not the placement discipline.

The confirm-intent gate that normally precedes a tree change (`changing-the-tree.md`) **collapses when the human is the editor**: the researcher's message co-editing the canvas *is* the authorization, so apply the change and commit without a separate confirmation round. The gate remains only for scope changes you initiate on your own.

## Dashboard pairing

Recommend running the dashboard in live-serve as a read-only canvas view alongside the loop, so the researcher watches the task tree update as you co-edit. Editing from the dashboard is out of scope.
