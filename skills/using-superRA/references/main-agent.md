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

Before entering a workflow, resuming after interruption, or reacting to a changed plan, resolve the next safe entry point from durable facts. Mixed state is normal: some tasks may remain approved while changed tasks and their downstream dependents roll back.

The resolver diagnoses and routes. It does not perform the plan edit, implementation pass, integration pass, or merge itself; the workflow that owns the selected layer runs its local protocol.

**Read facts first:**

- Git: current branch/worktree, `git status`, recent commits relevant to PLAN.md / RESULTS.md / task files, and any active merge/rebase/cherry-pick state.
- Handoff docs: whether `PLAN.md` and `RESULTS.md` exist, are tracked, and match the committed state expected by the workflow about to run.
- PLAN header: `## Workflow Status`, `## Decisions`, `## Upstream Intent` when present, project conventions, any logged implementation-workflow Step 4 disposition, and any declared pipeline.
- Task blocks: `Depends on`, checkbox completion, `Review status`, `Integration status`, active review-notes blockquotes, and task/output references.
- RESULTS.md: task sections exist for planned tasks and contain findings for completed work.

**Compute the affected frontier:**

1. First check whether planning must run. If `PLAN.md` / `RESULTS.md` are missing, untracked, structurally incomplete, or contradicted by an unlogged material user decision, enter `planning-workflow` before implementation or integration work. Material scope, objective, input, output, methodology, or task-graph changes use `planning-workflow §User Feedback and Changing Plans`; after that protocol updates the docs, run this resolver again.
2. Identify the changed or untrusted starting points from the durable facts: explicit user scope change, dirty or recent task-file edits, unchecked task steps, omitted / placeholder / cleared task status, active review notes, failed or missing reproducibility evidence, unchecked workflow rollups, or a requested final action.
3. For each changed task, include downstream dependents whose inputs, outputs, or assumptions may have shifted. Preserve task-local `Review status` / `Integration status` for unrelated approved tasks. If a downstream task is unaffected, document the exemption in `## Decisions`.
4. Treat `## Workflow Status` checkboxes as rollups, not task state. If a checked milestone no longer matches the task evidence or required global gate, that milestone is invalid. The owning workflow or plan-change protocol should uncheck it and record why; unrelated task-level statuses remain valid.
5. If durable facts disagree in a way you cannot repair mechanically, stop under §The Three Pause Classes and log the answer before acting.

**Return the decision:**

- Affected frontier: tasks and workflow layer(s) that need work.
- Preserved-approved tasks: tasks whose `Review status` / `Integration status` remain valid.
- Invalidated milestones: `## Workflow Status` boxes that are no longer true.
- Next safe workflow owner and entry layer: planning, implementation / review, validation / completion, integration, documentation, or final merge / PR.
- Required stop point: any researcher decision or irreparable contradiction that must be resolved before action.

**Choose the next safe action:**

1. Compare the decision with the canonical workflow order: plan repair or plan-change logging -> implementation / review -> reproducibility verification -> `Execution complete` box flip -> implementation-workflow Step 4 disposition -> integration -> documentation -> final merge / PR.
2. Enter the earliest invalid layer for the affected frontier. Invoke the workflow skill that owns that layer; the workflow then runs its local mechanics and gates.
3. For implementation or review, work only on tasks whose dependencies are satisfied and whose local status is not valid for that layer.
4. If all affected implementation tasks are approved but reproducibility, `Execution complete`, or the Step 4 disposition is missing, enter `implementation-workflow` at Step 3 / Step 4. A current integration / PR request supplies intent only after that disposition is logged.
5. For integration or later layers, scope authoring and fix work to the affected frontier while still running required global gates before merge / PR.

**Safety invariants:**

- Do not add or trust a single global `Current state` field.
- Do not act on a material user decision before it is logged in PLAN.md.
- Do not clear unrelated task-local statuses when only a rollup milestone is invalid.
- Do not advance past implementation work without reviewer approval or documented adjudication of blocking review items.
- Do not enter integration before implementation reproducibility and the Step 4 disposition are current.
- Do not merge or open a PR before integration, documentation, and base-freshness gates are valid for the current frontier.

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

Subagent mode is the default — dispatch implementers and reviewers through `superRA:agent-orchestration`. Direct mode is a fallback: only for trivial tasks or when the user explicitly requests it, and you must announce the switch before proceeding.

**Direct mode protocol:**

- **Read the direct-mode role reference for the role you are playing.** `references/direct-mode-implementer.md` for an implementation step; `references/direct-mode-reviewer.md` for a review step. These are the skill-surface copies of the role protocol that direct mode can load across repos.
- **The Skill-Load Manifest still drives loads.** Consult the manifest row for your Stage and load the listed skills/references in-session.
- **Task context comes from `PLAN.md`, `RESULTS.md`, and the current session** — there is no dispatch prompt.
- **Self-review gate, handoff-doc discipline, and verdict protocol all apply.** Walk the active domain skill's gated checklist before committing. Reviewer verdicts are still APPROVE / REVISE.
- **Review is never skipped.** Either dispatch a reviewer subagent or play the reviewer role in-session against the same discipline. Self-approval without walking the checklist is not a review.

**Codex agents: MUST load `references/codex-instructions.md` immediately.** Codex-specific delegation, warm-agent lifecycle, and named-agent rules live there.
