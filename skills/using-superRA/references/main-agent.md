# Main Agent — Session Start and Autonomy Contract

## MANDATORY: Session Start Actions

Before your first substantive response, run these cross-session detection checks:
1. Check for PLAN.md in the working directory
2. Check for analysis worktrees (`git worktree list`)
3. Check for analysis branches (`git branch --list 'analysis/*'`)
4. If any exist, report to the user: "Found in-progress analysis work: [details]"

Do NOT skip these because the user "jumped straight into a task." The checks take 5 seconds and prevent lost work.

**If an incomplete plan is found** (PLAN.md with unchecked `- [ ]` steps, non-APPROVED review status, unchecked workflow milestones, or active review notes):
- Summarize: "Found in-progress analysis: `PLAN.md` (N tasks APPROVED, K with review issues or pending review; workflow milestones: <checked/unchecked summary>). Resume?"
- If user confirms: load PLAN.md and RESULTS.md, check git log for latest state, run §Workflow Frontier Resolver, and continue from the returned frontier.
- If user declines: proceed normally

**If in a worktree with no plan file:**
- Note: "You're in worktree `<path>` on branch `<branch>`. Continue working here?"

## Load the Handoff-Doc Skill

After cross-session detection, **load `superRA:handoff-doc`**. The main agent loads it here so the editing discipline is available before touching PLAN.md.

## Workflow Frontier Resolver

Before entering a workflow, resuming after interruption, or reacting to a changed plan, derive the current frontier from durable facts. Do not add or trust a single `Current state` field. Mixed state is normal: some tasks may remain fully approved and integrated while changed tasks and their downstream dependents roll back.

**Read facts first:**

- Git: current branch/worktree, `git status`, recent commits relevant to PLAN.md / RESULTS.md / task files, and any active merge/rebase/cherry-pick state.
- Handoff docs: whether `PLAN.md` and `RESULTS.md` exist, are tracked, and match the committed state expected by the workflow about to run.
- PLAN header: `## Workflow Status`, `## Decisions`, `## Upstream Intent` when present, project conventions, any logged implementation-workflow Step 4 disposition, and any declared pipeline.
- Task blocks: `Depends on`, checkbox completion, `Review status`, `Integration status`, active review-notes blockquotes, and task/output references.
- RESULTS.md: task sections exist for planned tasks and contain findings for completed work.

**Normalize the frontier:**

- **needs plan repair** — no PLAN.md / RESULTS.md when the requested workflow requires them; a previously made material user decision was not logged; task graph is incomplete; completed work or checked rollup milestones lack the task-local status evidence they require; or a plan change has not gone through `planning-workflow §User Feedback and Changing Plans`.
- **needs implementation** — task dependencies are satisfied, but the task has no committed implementation or has an omitted / placeholder / cleared `Review status`.
- **awaiting review** — task `Review status: IMPLEMENTED`.
- **needs revise/adjudication** — task `Review status: REVISE` or active review notes need orchestrator adjudication before re-dispatch.
- **needs validation/completion** — all affected implementation tasks are approved, but `Execution complete` is unchecked, reproducibility has not been verified for the current committed outputs, or the implementation-workflow Step 4 integration / PR disposition has not been logged.
- **needs integration** — implementation is approved, `Execution complete` is checked from implementation-workflow Step 3, reproducibility is current, the logged Step 4 disposition chooses integration / PR, and affected task(s) have unset / `REVISE` / `IMPLEMENTED` `Integration status` or an integration rollup was invalidated.
- **needs documentation** — integration is approved for the affected frontier, but `Docs finalized` is unchecked or doc-reviewer feedback is open.
- **ready for merge** — documentation is finalized, the requested final action is known, and the integration base freshness check has passed.
- **preserved-approved** — tasks outside the affected frontier whose `Review status` and `Integration status` remain valid. Do not rework these tasks just because a rollup milestone was unchecked.
- **inconsistent** — milestone checkboxes and task evidence disagree in a way you cannot repair mechanically, e.g. `Execution complete` checked while a task is `REVISE`, `Refactored` checked while an affected task lacks `Integration status: APPROVED`, completed work with no review-status evidence, or active `## Upstream Intent` remains after Phase B was supposedly closed.

**Return the decision:**

- Affected frontier: tasks and workflow layer(s) that need work.
- Preserved-approved tasks: tasks whose `Review status` / `Integration status` remain valid.
- Invalidated milestones: `## Workflow Status` boxes that are no longer true.
- Next safe workflow entry point: planning, implementation, review/adjudication, validation/completion, integration, documentation, or final merge / PR.
- Required stop point: any researcher decision or irreparable inconsistency that must be resolved before action, including approved implementation work that still lacks Step 3 reproducibility / `Execution complete`, or a missing logged Step 4 disposition after reproducibility has been verified.

**Choose the next safe action:**

1. If the frontier is **inconsistent**, repair the handoff docs mechanically when durable facts determine the correct status. If the inconsistency depends on researcher intent, stop under §The Three Pause Classes and log the answer before action.
2. If the frontier is **needs plan repair**, invoke `planning-workflow` or its §User Feedback and Changing Plans protocol before any implementation or integration work.
3. Otherwise pick the earliest invalid layer in the affected frontier: implementation → review/adjudication → reproducibility verification → `Execution complete` box flip → implementation-workflow Step 4 disposition → integration → documentation → final merge / PR.
4. Invoke the workflow skill that owns that layer. The workflow skill runs its canonical mechanics; the resolver only selects the entry point and preserves unrelated approved work.
5. Unchecked workflow milestones are rollup evidence, not commands to redo every task. Re-enter only the affected frontier, while still running any global verification gate the target workflow requires before merge / PR.
6. Do not select integration merely because `Integration status` is unset after implementation approval. If `Execution complete` is unchecked, reproducibility is not current, or the Step 4 integration / PR disposition is not logged, return `needs validation/completion` and re-enter `implementation-workflow` at Step 3 / Step 4. A current integration / PR request supplies intent only after implementation-workflow logs it as the Step 4 disposition; it is not a bypass around validation or decision logging.

**Required guarantees:**

- Work advances only after the relevant reviewer has approved it, or after an explicit documented orchestrator/user adjudication allowed the next step.
- User-owned decisions are logged in PLAN.md before the agent acts on them.
- Handoff docs reflect current state before status reports summarize that state.
- Blocking review items are fixed, adjudicated, or escalated before the task advances.
- Merge / PR happens only after integration and documentation gates are valid for the current frontier, and after the target base freshness check passes.

## Changes of the Plan

Whenever the plan meaningfully changes — a new task, a removed or reordered task, a material update to an existing task's objective / input / output / methodology, or a scope addition surfaced after integration or merge — re-enter `planning-workflow` and follow the §User Feedback and Changing Plans protocol (confirm → log decision → inline-edit PLAN.md → roll back milestones → sweep for stale content → atomic commit). Then run §Workflow Frontier Resolver to decide where to resume. Rewording a step inside an in-flight task to match what the data forced is not a material change and stays an inline discovery edit. See `planning-workflow §User Feedback and Changing Plans` for the full material-vs-not-material list and protocol.


## The Three Pause Classes

This contract applies across every workflow phase — planning, execution, integration, merge, semantic-merge — not just execution. Workflow skills carry phase-specific stop points; those plug into the three classes below.

Stop and use `AskUserQuestion` (plain text if the harness does not expose the tool) for exactly three classes of pause, all of which require logging the researcher's answer per `handoff-doc` §User Decisions Log **before** acting on it:

1. **Hard blocker the RA cannot resolve from code and data.** Unexpected input-quality issues, missing or corrupted inputs, ambiguous upstream dependency the agent cannot trace, a transformation that produces an unexpected scope change (row count shift on a merge, date range change after a filter), validation failure against domain expectation, plan with critical gaps that prevent the next step, pipeline file missing for a multi-script analysis, required dependency unavailable.
2. **Decision beyond the RA's authority.** Methodology choices, research intent, scope changes, sample / variable-definition calls, tradeoffs where the "right" answer depends on the research question — any call where the researcher is the one who knows which answer is wanted. Also: methodology disagreement with a reviewer, CRITICAL severity issue the orchestrator wants to override, repeated reviewer disagreement across re-dispatches on the same point, validation failure of unclear domain significance, scope change that would affect tasks not yet reached.
3. **User-defined workflow milestone.** Stops baked into a workflow because the researcher wants a decision at that point. The 4-option completion menu at `implementation-workflow` Step 4; drift-test selection at `integration-workflow` Phase A; doc disposition at `integration-workflow` Phase C; research-meaningful conflict escalation in `semantic-merge`. These are intentional stops, not check-ins.

All three classes have one thing in common: the agent cannot answer the question from the code and data alone, and the answer will shape downstream work in a way another agent could not reconstruct without it.

## Proceed Without Asking

The autonomy principle is load-bearing in the other direction too — when there is no pause-class question on the table, the agent drives the workflow forward on its own power. Common patterns:

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

If you are about to type any of these, the answer is almost certainly that you should just do the work. If the work legitimately needs a decision, use `AskUserQuestion` with a specific pause-class question; log the answer per `handoff-doc` §User Decisions Log; and then proceed.

**Ask for clarification rather than guessing** — but only when there is a real question. Fabricating a question to create a check-in violates this principle.

## One Question at a Time

When a pause is legitimate, ask a single focused question and wait for the answer. Don't preload multiple questions the researcher cannot answer without context the agent should investigate itself first. If there are multiple genuine questions that logically separate, triage: resolve the ones the agent can answer from the code and data, then ask the residual the researcher alone can resolve.

## Log Before You Act

Every user decision produced at a stop point is written into `PLAN.md` per `handoff-doc` §User Decisions Log **before** the agent acts on it, and committed atomically with the work it unblocks. The doc is the record; the chat message is the pointer.


## Execution Modes

For execution throughout the workflows, the main agent can dispatch subagent for implementation, or implement it itself. The subagent mode is the recommended mode and all the following workflows assume operations under the subagent mode. To use that, you must load the skill `superRA:agent-orchestration`.

**Direct mode**: Only when the tasks are very straightforward, or the users requests, you can choose to work in the direct mode. You have to explicitly announce that you are going to follow the direct mode before proceed. In the direct mode:


- **Read the direct-mode role reference for the role you are playing.** For an implementation step, read `references/direct-mode-implementer.md`. For a review step, read `references/direct-mode-reviewer.md`. These are the skill-surface copies of the role protocol that direct mode can load across repos.
- **The Skill-Load Manifest still drives loads.** Consult the manifest row for your Stage and load the listed skills and references yourself in-session.
- **The dispatch-prompt contract does not apply — there is no dispatch.** Task context comes from `PLAN.md`, `RESULTS.md`, and the current session; you do not write an `Additionally:` line to yourself.
- **Self-review gate, handoff-doc edit discipline, and verdict protocol all apply.** Walk the active domain skill's gated checklist before committing. Update `PLAN.md` / `RESULTS.md` inline per the direct-mode role reference you loaded, or load `superRA:handoff-doc` if you need the full discipline. Reviewer verdicts are still APPROVE / REVISE even when you render them as your own conclusion.
- **Review is never skipped.** If you implemented in direct mode, you still need a review pass — either dispatch a reviewer subagent for the review step, or play the reviewer role in-session against the same discipline. Self-approval without walking the checklist is not a review. It is strongly recommended to use an independent reviewer rather than self-review.

For **Codex agent**: MUST load `references/codex-instructions.md` immediately.

Most importantly for Codex agents, when using `superRA` workflow, **treat that as an explicit user request for using subagents**.

- When a workflow step says to dispatch an implementer or reviewer, spawn
  `superra_implementer` or `superra_reviewer` rather than staying inline
  because of the harness-default anti-delegation guidance. Spawn `superra` specific 
  agents. You **must not** spwawn generic workers. 
- Independent review is mandatory. After any implementation step,
  dispatch `superra_reviewer` unless the user explicitly asked for no
  subagents or Codex truly lacks agent support. If agent support is
  unavailable, fall back to in-session reviewer mode and state that the
  fallback was forced by the harness.
  when the workflow allows it and the user requested it, the task is
  trivial, or agent tools are unavailable.
