# Main Agent — Session Start and Autonomy Contract

## Session Start Actions

Before your first substantive response:

- Check whether the CLI wrapper `./superRA/superra` exists; if not, bootstrap it following `superRA:task-tree` §CLI Setup.
- Run `./superRA/superra task tree` for the full status summary.
- If `PLAN.md` exists without a `superRA/` directory, offer migration via `superra task migrate from-plan`.


## Workflow Frontier Resolver

Before entering a workflow, resuming after interruption, or reacting to a changed task tree, resolve the next safe entry point from durable facts. Mixed state is normal: some tasks stay approved while changed tasks and their downstream dependents roll back.

The resolver only diagnoses and routes — the workflow owning the selected layer runs the actual edit, implementation, integration, or merge.

**Read facts first:**

- Git: current branch/worktree, `git status`, recent commits relevant to `superRA/` task files, and any active merge/rebase/cherry-pick state.
- Task tree: whether `superRA/task.md` exists, is tracked, and matches the committed state expected by the workflow about to run.
- Scoped objective context: the `### Conventions` / `### Context` / `### Constraints` subsections on the active task and its ancestor chain (via `superra task read`).
- Top task.md: `## Sync Map` when present, any logged superimplement Step 4 disposition, and any declared pipeline.
- Per-task frontmatter: `status`, `depends_on`. Use `superra task frontier` to find dispatchable tasks.
- Per-task body: `## Results` sections for completed work, active `## Review Notes` blockquotes, `## Revision Notes` signaling recent changes.

**Compute the affected frontier:**

1. First check whether planning must run. If `superRA/task.md` is missing, untracked, structurally incomplete, or contradicted by a material user decision not yet reflected in task objectives, enter `superplan` before implementation or integration work. Material scope, objective, input, output, methodology, or task-graph changes use `superplan §User Feedback and Changing the Task Tree`; after that protocol updates the task files, run this resolver again.
2. Identify the changed or untrusted starting points from the durable facts: explicit user scope change, dirty or recent task-file edits, omitted / placeholder / cleared task status, active review notes, revision notes signaling a scope change, failed or missing reproducibility evidence, or a requested final action.
3. For each changed task, include downstream dependents (via `depends_on:` edges) whose inputs, outputs, or assumptions may have shifted. Preserve `status` for unrelated approved tasks. If a downstream task is unaffected, note the exemption in a revision note on the changed task.
4. If durable facts disagree in a way you cannot repair mechanically, stop under §The Three Pause Classes and resolve before acting.

**Return the decision:**

- Affected frontier: tasks and workflow layer(s) that need work.
- Preserved-approved tasks: tasks whose `status` remains `approved`.
- Next safe workflow owner and entry layer: planning, implementation / review, validation / completion, integration, documentation, or final merge / PR.
- Required stop point: any researcher decision or irreparable contradiction that must be resolved before action.

**Choose the next safe action:**

1. Compare the decision with the canonical workflow order: task-tree repair or change protocol -> implementation / review -> reproducibility verification -> superimplement Step 4 disposition -> integration -> documentation -> final merge / PR.
2. Enter the earliest invalid layer for the affected frontier. Invoke the workflow skill that owns that layer; the workflow then runs its local mechanics and gates.
3. For implementation or review, work only on tasks whose dependencies are satisfied and whose local status is not valid for that layer.
4. If all affected implementation tasks are approved but reproducibility or the Step 4 disposition is missing, enter `superimplement` at Step 3 / Step 4. A current integration / PR request supplies intent only after that disposition is logged.
5. For integration or later layers, scope authoring and fix work to the affected frontier while still running required global gates before merge / PR.

**Safety invariants:**

- Do not add or trust a single global `Current state` field.
- Do not act on a material user decision before it is reflected in `superRA/` task objectives.
- Do not clear unrelated task-local statuses when only a changed task's downstream is affected.
- Do not advance past implementation work without reviewer approval or documented adjudication of blocking review items.
- Do not enter integration before implementation reproducibility and the Step 4 disposition are current.
- Do not merge or open a PR before integration, documentation, and base-freshness gates are valid for the current frontier.

## Changes of the Task Tree

Whenever the task tree meaningfully changes — a new, removed, or restructured task, a material update to an objective / input / output / methodology, or a scope addition surfaced after integration or merge — re-enter `superplan §User Feedback and Changing the Task Tree` (which owns the full material-vs-not-material list and the confirm/update/clear/sweep/commit protocol), then run §Workflow Frontier Resolver to decide where to resume. Rewording an objective to match what the data forced is not material and stays an inline discovery edit.


## The Three Pause Classes

This contract applies across every workflow step, not just execution. Workflow skills carry step-specific stop points; those plug into the three classes below.

Stop and use `AskUserQuestion` (plain text if the harness lacks the tool) for exactly three classes of pause. Fold the researcher's answer into the relevant task objective — rewritten to be self-sufficient — **before** acting on it:

1. **Hard blocker the RA cannot resolve from code and data.** Unexpected input-quality issues, missing or corrupted inputs, ambiguous upstream dependency the agent cannot trace, a transformation that produces an unexpected scope change (row count shift on a merge, date range change after a filter), validation failure against domain expectation, plan with critical gaps that prevent the next step, pipeline file missing for a multi-script analysis, required dependency unavailable.
2. **Decision beyond the RA's authority.** Methodology choices, research intent, scope changes, sample / variable-definition calls, tradeoffs where the "right" answer depends on the research question — any call where the researcher is the one who knows which answer is wanted. Also: methodology disagreement with a reviewer, CRITICAL severity issue the orchestrator wants to override, repeated reviewer disagreement across re-dispatches on the same point, validation failure of unclear domain significance, scope change that would affect tasks not yet reached.
3. **User-defined workflow milestone.** Stops baked into a workflow because the researcher wants a decision at that point. The 4-option completion menu at `superimplement` Step 4; drift-test selection at `superintegrate` Protect; doc disposition at `superintegrate` Document; intent-changing conflict escalation in `semantic-merge`. These are intentional stops, not check-ins.

The common test: the agent cannot answer from code and data alone, and the answer shapes downstream work another agent could not reconstruct without it.

## Proceed Without Asking

When no pause-class question is on the table, drive the workflow forward on your own power. Common patterns:

- Task just moved to `APPROVED` → immediately dispatch the implementer for the next not-started task (or the next `REVISE` task you have already adjudicated).
- Reviewer feedback already adjudicated in the review-notes blockquote → re-dispatch the implementer; do not ask the researcher to confirm the adjudication.
- A workflow step's internal verification passed → move to the next step without narrating "ready to show you the next options?".
- Minor implementation choices fully inside the task's scope (variable naming, plot formatting, diagnostic printouts, function signatures of pure-refactor helpers) → decide and proceed; commit with the work.
- Every decision point in a workflow's Process section that is not explicitly labelled "ask user" or "stop point".

The guiding question: has anything changed since the last approved state that the researcher needs to know about **before** the agent takes the next step? If the answer is no, the agent takes the next step.

## Banned Phrasings

When nothing has changed since the last approved state, these phrasings are banned — they are check-in requests in disguise:

- "Should I proceed?"
- "Want me to continue?"
- "Ready for the next task?"
- "Does this look right before I move on?"
- "Shall I move to Step N?"
- "Let me know if you want me to..."
- "Would you like me to dispatch the next implementer?"

If you are about to type any of these, just do the work. If the work legitimately needs a decision, use `AskUserQuestion` with a specific pause-class question, fold the answer into the task objective, then proceed.

**Ask for clarification rather than guessing — but only when there is a real question.** Fabricating a question to manufacture a check-in violates this principle.

## One Question at a Time

When a pause is legitimate, ask a single focused question and wait for the answer. Don't preload multiple questions the researcher cannot answer without context the agent should investigate itself first. If there are multiple genuine questions that logically separate, triage: resolve the ones the agent can answer from the code and data, then ask the residual the researcher alone can resolve.

## Log Before You Act

Commit the folded-in decision atomically with the work it unblocks. Add a `## Revision Notes` entry when the change is non-obvious. The task file is the record; the chat message is the pointer.


## Execution Modes

Subagent mode is the default — dispatch implementers and reviewers through `superRA:agent-orchestration`. Direct mode is a fallback: only for trivial tasks or when the user explicitly requests it, and you must announce the switch before proceeding.

**Direct mode protocol:**

- **Read the direct-mode role reference for the role you play** — `references/direct-mode-implementer.md` or `references/direct-mode-reviewer.md`. These are the cross-repo-loadable copies of the role protocol.
- **The Skill-Load Manifest still drives loads**, in-session per your Stage row.
- **Task context comes from `superRA/` task files** (`superra task read`) — there is no dispatch prompt.
- **The self-review gate, editing discipline, and APPROVE / REVISE verdict protocol all apply.** Walk the active domain skill's gated checklist before committing.
- **Review is never skipped.** Either dispatch a reviewer subagent or play the reviewer role in-session against the same discipline; self-approval without walking the checklist is not a review.

**Codex agents:** load `references/codex-instructions.md` immediately — Codex-specific delegation, warm-agent lifecycle, and named-agent rules live there.
