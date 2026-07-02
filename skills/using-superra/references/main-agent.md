# Main Agent — Session Start and Autonomy Contract

## Session Start Actions

Before your first substantive response:

- Check whether the CLI wrapper `./superRA/superra` exists; if not, bootstrap it following `superRA:task-tree` §CLI Setup.
- Run `./superRA/superra task tree` for the full status summary.
- Ensure the live dashboard is up for this repo without opening a browser: run `./superRA/superra dashboard --no-open` (idempotent — reuses a running background server or starts one detached, and prints `…localhost:<port>`).
- If `PLAN.md` exists without a `superRA/` directory, the project predates the `superRA/` task tree that replaced the `PLAN.md` / `RESULTS.md` model. Tell the user about the upgrade, offer migration via `superra task migrate from-plan`, and point them to the superRA docs at http://fuzhiyu.me/superRA/ for details.

## Resuming Work

There is no durable workflow-stage to look up. The frontmatter field set is closed and INTEGRATE keeps no stage marker, so task `status` plus the git log *are* the state — "which phase are we in" (implemented-or-not, integrated-or-not) is read from statuses and commits, never from a file field. Resuming is therefore status-driven, and mixed state is normal:

- **Tree not all-approved** → there is implementation work. Resume the implement loop (`superimplement`): `superra task frontier` lists every actionable leaf with its status — `not-started` / `in-progress` to implement, `implemented` to review, `revise` to fix.

On a replan, a directly widened `approved` task flips to `revise`, and its `depends_on` dependents reset to `not-started` (`superplan/references/task-tree-design.md` §Objective rewrites on scope expansion owns the rule), while unrelated approved tasks stay approved; the reset tasks reappear on `task frontier` and the loop above picks them up. If `superRA/` is missing, untracked, or contradicted by a material user decision not yet in the task objectives, enter `superplan` first. If durable facts disagree in a way you cannot repair mechanically, stop under §Proceeding and Pausing.

## Changes of the Task Tree

When the task tree changes materially — a task added, removed, or restructured, or an objective / input / output / methodology shifted — route through `superplan §User Feedback and Changing the Task Tree`, which owns the materiality test and the confirm / update / reset / sweep / commit protocol. Then resume per §Resuming Work.

## Surfacing the Live Dashboard

After any action that changes what the tree shows the researcher — a structural or material edit (add / remove / move / replan / update a task), a status transition that completes a stage, or maturation / consolidation — give the user the affected task's live URL so they can watch it update:

```
http://localhost:<port>/?wt=<worktree-basename>#/<task-path>
```

`<port>` is from the launch line in §Session Start Actions; always include `?wt=<worktree-basename>` — this worktree's directory name (`basename` of the worktree root); `<task-path>` is the `superra task read` locator (no `superRA/` prefix, empty for the tree root).

## Proceeding and Pausing

Default to proceeding. Within a stage, drive the workflow forward on your own power: dispatch the next task once it is approved, re-dispatch after you have adjudicated reviewer feedback, advance when an internal verification passes, and settle minor in-scope choices yourself. The test is whether anything since the last approved state needs the researcher *before* the next step — if not, take the step. Do not manufacture a check-in ("Should I proceed?", "Ready for the next task?") when nothing needs deciding.

Pause — `AskUserQuestion` (plain text if the harness lacks it), folding the answer into the relevant task objective before you act — in two situations:

1. **A decision that materially changes a task objective.** You cannot settle it from code and data, and the answer reshapes work downstream agents read from the objective: methodology, research intent, scope, sample or variable definitions, or a blocker whose only resolution shifts scope. Materiality is defined in `superplan §User Feedback and Changing the Task Tree`; an objective edit you *can* make from the data is an inline discovery edit, not a pause.
2. **A pre-set workflow gate** — a stop the workflow deliberately places for the researcher (e.g. the `superimplement` Step 4 menu, drift-test selection at `superintegrate` Protect, intent-changing conflict escalation in `semantic-merge`). Intentional decision points, not check-ins.

Ask questions, and resolve what you can from code and data first.


## Execution Modes

Subagent mode is the default — dispatch implementers and reviewers through `superRA:agent-orchestration`. Direct mode is a fallback: only for trivial tasks or when the user explicitly requests it, and you must announce the switch before proceeding.

**Direct mode protocol:**

- **Read the direct-mode role reference for the role you play** — `references/direct-mode-implementer.md` or `references/direct-mode-reviewer.md`. These are the cross-repo-loadable copies of the role protocol.
- **The Skill-Load Manifest still drives loads**, in-session per your Stage row.
- **Task context comes from `superRA/` task files** (`superra task read`) — there is no dispatch prompt.
- **The self-review gate, editing discipline, and APPROVE / REVISE verdict protocol all apply.** Walk the active domain skill's gated checklist before committing.
- **Review is never skipped.** Always dispatch a reviewer subagent unless the user explicitly asks to skip it.

**Codex agents:** load `references/codex-instructions.md` immediately — Codex-specific delegation, warm-agent lifecycle, and named-agent rules live there.
