# Interactive Canvas Mode

A fused **light-plan → execute-yourself → record** loop the main agent runs *with* the researcher, co-editing the task file as a live canvas. You do the work yourself and pause often for feedback. This is the default execution mode, in PLAN and IMPLEMENT alike; autonomous mode (`superRA:superimplement`) is the opt-in (`main-agent.md` §Execution Modes).

## The spectrum

One task file carries the whole range of plan/execute interleaving:

- **Light-plan, then execute.** Scope a target and objective into a task file — positioning retained, exploration/domain-gate/decomposition choreography skipped — then execute and record results in place.
- **Retroactive capture.** Work already done, researcher asks to write it up: same loop, results-first — reconstruct the task and populate `## Results` after the fact via `superplan/references/task-tree-design.md` §Retroactive Task-Tree Creation. Route it through this loop, not a separate path.

## The loop

You fill no seat and run no role protocol here — this loop is your protocol for the task file.

1. **Co-edit** the target and objective into the task file through the `using-superra` §Task Interface.
2. **Self-review always.** Changed artifacts and recorded results against the objective; the diff and outputs for correctness, completeness, unintended scope; fresh verification per completion claim. Apply every `[BLOCKING]` item from active domain skills.
3. **Review and update the task.** Before each pause, update `## Results` per `superRA:communicate` and move `status` as the work lands (`in-progress` → `implemented`). Remove stale content so the task always reflects the latest stage.
4. **Commit instantly** per edit, per `using-superra` §Commits.
5. **Ask before review, with a tool — required.** `AskUserQuestion` (plain text only if the harness lacks it): review now / defer / skip, carrying the recommendation `main-agent.md` §Deciding on Review calls for. Never dispatch a reviewer on your own read.
   - **Now** — load `superRA:agent-orchestration` and dispatch a reviewer subagent at the tier and focuses you named; APPROVE lands the task at `approved`.
   - **Defer** — leave the task at `implemented`; the review is still owed.
   - **Skip** — §Deciding on Review's no-review branch.
6. **Continue**, pausing frequently for feedback before the next unit of work.
7. **Frontier empty** — close IMPLEMENT through `../../superimplement/references/completion.md`.

## Positioning and the intent gate

Position every task by the recursive descent in `superplan/references/task-tree-design.md` §Placing Work in the Existing Tree — light planning trims choreography, not placement discipline.

The confirm-intent gate preceding a tree change (`superplan/references/changing-the-tree.md`) **collapses when the human is the editor**: the researcher's co-editing message *is* the authorization — apply and commit without a confirmation round. The gate remains for scope changes you initiate yourself.

## Dashboard pairing

Recommend the dashboard in live-serve as a read-only canvas view alongside the loop, so the researcher watches the tree update as you co-edit. Editing from the dashboard is out of scope.
