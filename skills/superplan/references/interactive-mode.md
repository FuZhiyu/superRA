# Interactive Canvas Mode

A fused **light-plan → execute-yourself → record** loop the main agent runs *with* the researcher, co-editing the task file as a live canvas. You do the work yourself and pause often for feedback; review is prompted, not automatic (§The loop, step 5).

**Select by autonomy, not difficulty:** for work the researcher steers closely — often hard, concentrated work — where plan and execution move together. Not for trivial jots. An explicit opt-in; the default stays autonomous subagent execution.

## The spectrum

One task file carries the whole range of plan/execute interleaving:

- **Light-plan, then execute.** Scope a target and objective into a task file — positioning retained, exploration/domain-gate/decomposition choreography skipped — then execute and record results in place.
- **Retroactive capture.** Work already done, researcher asks to write it up: same loop, results-first — reconstruct the task and populate `## Results` after the fact via `task-tree-design.md` §Retroactive Task-Tree Creation. Route it through this loop, not a separate path.

## The loop

You do not load the implementer or reviewer role skills here — this loop is your protocol for the task file.

1. **Co-edit** the target and objective into the task file through the `using-superra` §Task Interface.
2. **Self-review always.** Changed artifacts and recorded results against the objective; the diff and outputs for correctness, completeness, unintended scope; fresh verification per completion claim. Apply every `[BLOCKING]` item from active domain skills.
3. **Keep the task updated — required.** Before each pause, record what you did into `## Results` per `superRA:implement-task` §Reporting, and move `status` as the work lands (`in-progress` → `implemented`). The task file, not chat or the commit log, is the state of record; a code commit without a task update is an incomplete step.
4. **Commit instantly** per edit, per `using-superra` §Commits.
5. **Ask before review, with a tool — required.** `AskUserQuestion` (plain text only if the harness lacks it): review now / defer / skip. Never dispatch a reviewer on your own read.
   - **Now** — dispatch a reviewer subagent for a full gated pass (via `superRA:agent-orchestration`); APPROVE lands the task at `approved`.
   - **Defer / skip** — leave the task at `implemented`.
6. **Continue**, pausing frequently for feedback before the next unit of work.

## Positioning and the intent gate

Position every task by the recursive descent in `task-tree-design.md` §Placing Work in the Existing Tree — light planning trims choreography, not placement discipline.

The confirm-intent gate preceding a tree change (`changing-the-tree.md`) **collapses when the human is the editor**: the researcher's co-editing message *is* the authorization — apply and commit without a confirmation round. The gate remains for scope changes you initiate yourself.

## Dashboard pairing

Recommend the dashboard in live-serve as a read-only canvas view alongside the loop, so the researcher watches the tree update as you co-edit. Editing from the dashboard is out of scope.
