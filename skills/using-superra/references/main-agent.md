# Main Agent — Session Start and Autonomy Contract

## Session Start Actions

Before your first substantive response:

- Check whether the CLI wrapper `./superRA/superra` exists; bootstrap it per `superRA:task-tree` §CLI Setup if not.
- Run `./superRA/superra task tree` for the full status summary.
- Bring up the live dashboard without opening a browser: `./superRA/superra dashboard --no-open` (idempotent — reuses a running background server or starts one detached). Retain its emitted scoped URL.
- `PLAN.md` without a `superRA/` directory: the project predates the task tree that replaced the `PLAN.md` / `RESULTS.md` model. Tell the user about the upgrade, offer `superra task migrate from-plan`, and point to the superRA docs at http://fuzhiyu.me/superRA/.
- **Branch check.** `git branch --show-current`; on `main`/`master`, recommend a topic branch before the first commit — the researcher declining is consent to proceed on the default branch.

## Workflow Map

SuperRA work moves through **PLAN -> IMPLEMENT -> INTEGRATE**:

1. `superplan` — creates or revises the `superRA/` task tree, records researcher decisions, declares which task-local statuses or workflow rollups a tree change invalidates.
2. IMPLEMENT — you run the frontier yourself in interactive mode (§Execution Modes); `superimplement` runs it autonomously through dispatched seats. Either way it ends by verifying reproducibility and recording the researcher's completion disposition before integration begins.
3. `superintegrate` — selects how key results are documented and protected, syncs against the integration base, matures the permanent record and task tree, derives and gets approval for a temporary refactoring task, executes it, and performs the final merge / PR / cleanup.

Ordered, but re-entry is normal — §Resuming Work.

## Resuming Work

There is no durable workflow-stage to look up. The frontmatter field set is closed and INTEGRATE keeps no stage marker, so task `status` plus the git log *are* the state — "which phase are we in" is read from statuses and commits, never a file field. Resuming is status-driven and mixed state is normal:

- **Tree not all-approved** → implementation work remains. Resume on the frontier in the current execution mode: `superra task frontier` lists every actionable leaf with its status — `not-started` / `in-progress` to implement, `implemented` awaiting an approval decision (§Deciding on Review), `revise` to fix.

On a replan, a directly widened `approved` task flips to `revise` and its `depends_on` dependents reset to `not-started` (`superplan/references/task-tree-design.md` §Objective rewrites on scope expansion owns the rule); unrelated approved tasks stay approved. The reset tasks reappear on `task frontier`.

## Changes of the Task Tree

Material tree change — a task added, removed, or restructured, or an objective / input / output / methodology shifted — routes through `superplan §User Feedback and Changing the Task Tree`, which owns the materiality test and the confirm / update / reset / sweep / commit protocol. Then resume per §Resuming Work.

## Surfacing the Live Dashboard

After any action that changes what the tree shows the researcher — a structural or material edit (add / remove / move / replan / update a task), a status transition that completes a stage, maturation / consolidation — give the user the affected task's live URL.

Append `#/<task-path>` to the scoped URL retained in §Session Start Actions; do not reconstruct its selector. `<task-path>` is the `superra task read` locator (no `superRA/` prefix, empty for the tree root).

## Execution Modes

- **interactive** (default; `direct` is an alias) — you execute the task yourself at high human cadence, through the light-plan → execute-yourself → record canvas loop in `references/interactive-mode.md`. No `superimplement` load, no dispatch, no seat.
- **autonomous** — dispatched implementer and reviewer seats, run by `superRA:superimplement` and orchestrated per `superRA:agent-orchestration` §Seat Assignment. Enter it on researcher request or a recommendation the researcher accepts; never switch silently. Recommend it with a one-line rationale when the frontier is broad, parallelizable, or context-heavy. Doesn't always mean dispatching a subagent — a seat you fill yourself still runs its role skill (`superRA:implement-task`, `superRA:review-task`) in this session; dispatch is the usual choice for larger work.

**Codex agents:** load `references/codex-instructions.md` immediately — Codex-specific delegation, warm-agent lifecycle, and named-agent rules live there.

## Proceeding and Pausing in the Autonomous Mode

**Default to proceeding.** Within a stage, drive the workflow forward on your own power. The test is whether anything since the last approved state needs the researcher *before* the next step. Never manufacture a check-in ("Should I proceed?", "Ready for the next task?").

Pause — `AskUserQuestion` (plain text if the harness lacks it), folding the answer into the relevant task objective before you act — in two situations:

1. **A decision that materially changes a task objective.** Unsettleable from code and data, and the answer reshapes work downstream agents read from the objective: methodology, research intent, scope, sample or variable definitions, or a blocker whose only resolution shifts scope. Materiality is defined in `superplan §User Feedback and Changing the Task Tree`; an objective edit you *can* make from the data is an inline discovery edit, not a pause.
2. **A pre-set workflow gate** — a stop the workflow deliberately places for the researcher (the IMPLEMENT completion menu in `superimplement/references/completion.md`, drift-test selection at `superintegrate` Protect, intent-changing conflict escalation in `semantic-merge`).

Resolve what you can from code and data first.

## Deciding on Review

Judge from the result's stakes and plausibility whether a separate pass is worth it, and at which tier and focuses (`superRA:review-task` §Scope). Review when the researcher asks, when `## Details` marks the task high-stakes, when the implementer returns a concern or uncertainty, or when a load-bearing result is one you cannot verify from the evidence in front of you. A planner suggestion is advice, not a binding schedule.

The action once you've judged differs by mode:

- **Interactive — recommend and ask.** Name the tier, focuses, and a one-line rationale, then ask (`interactive-mode.md` step 5 owns the ask/now/defer/skip mechanics). Never dispatch a reviewer on your own read.
- **Autonomous — decide and act**, without asking (§Proceeding and Pausing).

**No review runs:** verify the work yourself and set `status: approved`.

The INTEGRATE boundary reviews the accumulated work regardless (`superRA:superintegrate`).

