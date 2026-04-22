# Objective-First Task/Step Semantics Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all `PLAN.md` / `RESULTS.md` editing. This change edits superRA skills and agent files, so implementers and reviewers must additionally follow `/CLAUDE.md`'s contributor rules and apply `skill-creator` discipline when editing `skills/*/SKILL.md`. Steps use checkbox (`- [ ]`) syntax. This is not a data-analysis task; the per-step cycle here is **read current canon -> edit the canonical concern owner -> verify consistency -> commit**.

**Objective:** Make `task = objective/scope contract` and `steps = planner-authored suggested route` a workflow-wide rule, so implementers can adapt within-task execution without silently changing task scope and reviewers judge objective achievement rather than literal step adherence.

**Methodology:** Treat the prior agent-produced specification in the initiating user request as the source of intent. Preserve one source of truth per concern: contributor philosophy in `/CLAUDE.md`, task-block semantics in `skills/handoff-doc/references/plan-anatomy.md`, role contracts in `agents/*.md`, workflow choreography in the workflow skills, domain-specific reinforcement in `skills/econ-data-analysis/SKILL.md`, and generated Codex mirrors only through `skills/codex-superra-setup/scripts/sync_codex_agents.py`.

**Scope contract:** The `PLAN.md` task-block shape stays unchanged. `**Objective**`, `**Script**`, `**Input**`, and `**Output**` remain the invariant task boundary. Step edits inside that boundary are autonomous and must be rewritten inline to match the actual best path taken. Whole-task add/split/combine/remove and researcher-owned methodology changes still route through `planning-workflow §User Feedback and Changing Plans`.

**Output:** Updated `CLAUDE.md`; updated `skills/handoff-doc/references/plan-anatomy.md`; updated `agents/implementer.md` and `agents/reviewer.md`; refreshed `.codex/agents/superra_implementer.toml` and `.codex/agents/superra_reviewer.toml`; updated workflow/domain skills (`planning-workflow`, `implementation-workflow`, `agent-orchestration`, `integration-workflow`, `econ-data-analysis`); focused Claude Code coverage and verification notes in `RESULTS.md`.

**Expected Results:** Implementers are explicitly empowered to rewrite, reorder, add, remove, split, or combine steps within task scope; reviewers flag under-scoped execution, missing necessary checks, and unjustified step drift instead of grading literal adherence; whole-task restructure is clearly separated from within-task adaptation; canonical docs and generated Codex agents tell the same story.

**Defaults:** Scope is workflow-wide, not data-analysis-only. `README.md` and `skills/CATEGORIES.md` stay untouched unless the canonical wording changes make them directly contradictory. Steps inside one task are implementer-owned; whole tasks are reviewer-proposed, orchestrator-authored, and researcher-approved through the existing restructure protocol.

**Pipeline:** N/A (skill/agent behavior change, not an empirical analysis).

---

## Workflow Status

- [x] **Plan approved** - researcher approved the task decomposition and clarified that rationale for within-task path changes belongs in agent status messages to the orchestrator/user, not as "change" logging in `PLAN.md` (2026-04-22)
- [ ] **Execution complete** - all tasks APPROVED and verification recorded
- [ ] **Drift tests created** - N/A for skill refactor; substitute is the verification bundle in Task 4
- [ ] **Refactored** - integration review not yet run
- [ ] **Docs finalized** - `RESULTS.md` still in Stage 1 dev-log form
- [ ] **Merged** - no merge or PR action yet

## Project Conventions

Walked at planning time (2026-04-22). Re-walk on-demand only.

### Repo root

- `/CLAUDE.md`: modifying superRA itself counts as skill creation; preserve the four workflow principles, one-source-of-truth concern ownership, and carefully tuned skill language. Contributor-facing guidance is canonical here, not in duplicated mirrors.
- `/AGENTS.md` and `/AGENT.md`: convenience symlinks to `/CLAUDE.md`; contributor-doc changes belong in `CLAUDE.md` so aliases stay in sync automatically.
- `/README.md`: user-facing workflow language should stay aligned with actual behavior, but public-doc edits are only required if the new canonical wording makes the current overview directly contradictory.

### Module-level docs walked

- `skills/using-superRA/SKILL.md`: main agents load handoff-doc discipline before touching `PLAN.md`; workflow, orchestration, domain, and utility concerns stay separated, so this change should update the owning concern directly instead of duplicating semantics across surfaces.
- `skills/handoff-doc/references/plan-anatomy.md`: task-block fields `Objective` / `Script` / `Input` / `Output` already define scope and ownership boundaries; step text and review notes are latest-state inline edits, not append-only history.
- `tests/claude-code/README.md`: Claude Code coverage lives in shell scripts using `test-helpers.sh` and `run-skill-tests.sh`; a new focused test should reuse that harness instead of inventing a separate runner.

### Not walked

- `docs/plans/` historical handoff docs and `docs/superpowers/` design archives - useful precedent, but not required to draft the initial root plan for this work.

## Decisions

> **User decision (2026-04-22):** Approve the plan, with one added reporting rule: when an agent rewrites the within-task step path, the rationale must be explained in the status message to the orchestrator/user, while `PLAN.md` itself stays latest-state only and does not narrate "changes from" prior text.
> **Question asked:** Should the workflow also capture why an implementer changed the in-task route, and where should that rationale live?
> **Rationale (if given):** `PLAN.md` should reflect only the latest state per handoff-doc discipline; the explanation belongs in the message layer to the orchestrator/user.

### Task 1: Canonicalize objective-first task-block semantics
**Depends on:** *(none)*
**Review status:** APPROVED

**Script:** N/A
**Input:** `/CLAUDE.md`, `skills/handoff-doc/references/plan-anatomy.md`, and the source-intent specification captured in this plan header.
**Output:** A concise contributor principle in `/CLAUDE.md` and canonical handoff-doc wording in `plan-anatomy.md` that establish: task objective/scope fields are invariant, steps are planner-authored starter guidance, within-task step combine/split is routine, and whole-task combine/split is restructure routed through the existing planning protocol.

- [x] **Step 1: Read the current semantics in both concern owners.** Re-read `/CLAUDE.md` and `plan-anatomy.md` together to separate the contributor-level principle from the canonical handoff-doc mechanics without duplicating workflow choreography.
- [x] **Step 2: Edit `/CLAUDE.md`.** Added one concise contributor principle stating that the task heading names the objective, `Script` / `Input` / `Output` bind scope, steps are the suggested route, and review is objective-completeness first while the exact mechanics stay owned by `plan-anatomy.md`.
- [x] **Step 3: Edit the handoff-doc canon.** Updated `plan-anatomy.md` and `results-anatomy.md` so every demonstrated task heading uses an objective-style placeholder, while the canonical scope/step semantics remain owned by `plan-anatomy.md`.
- [x] **Step 4: Update the live results handoff and verify coherence.** Refreshed the root `RESULTS.md` header so it reflects that execution has begun, then re-read the affected handoff-doc references together and confirmed the objective-first rule is expressed consistently without creating a new source of truth.

### Task 2: Reframe implementer and reviewer role contracts
**Depends on:** Task 1
**Review status:** APPROVED

**Script:** N/A
**Input:** `agents/implementer.md`, `agents/reviewer.md`, `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml`, and `skills/codex-superra-setup/scripts/sync_codex_agents.py`.
**Output:** Implementer guidance that prioritizes the task objective over literal step adherence while allowing necessary within-task diagnostics/robustness work, and that requires the rationale for any within-task path rewrite to be communicated in the status return to the orchestrator/user rather than logged as prior-vs-current history in `PLAN.md`; reviewer guidance that judges objective completion, flags missing necessary checks and unjustified step drift, and routes whole-task combine/split through the existing restructure protocol; refreshed generated Codex mirrors with no manual drift.

- [x] **Step 1: Inspect the current agent-role boundaries.** Re-read `agents/implementer.md`, `agents/reviewer.md`, and the current generated TOML mirrors together to isolate the existing ownership, verdict, and reporting language that needed tightening without replacing the broader handoff protocol.
- [x] **Step 2: Edit `agents/implementer.md`.** Updated the implementer contract so the task heading/objective plus `Script` / `Input` / `Output` define scope, the step list is the planner's current best route, in-scope step split/combine plus extra diagnostics/validation/robustness work are allowed when needed, and any within-task route rewrite is explained in the status return rather than as `PLAN.md` history.
- [x] **Step 3: Edit `agents/reviewer.md`.** Updated the reviewer contract to judge objective completion before literal step adherence, flag under-scoped mechanical execution and unjustified step drift, and route integration-stage whole-task combine/split recommendations through `planning-workflow §User Feedback and Changing Plans`.
- [x] **Step 4: Refresh generated Codex agents.** Ran `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` after the canonical agent edits so `.codex/agents/superra_implementer.toml` and `.codex/agents/superra_reviewer.toml` were regenerated from the updated markdown.
- [x] **Step 5: Verify generated-to-canonical parity.** Re-read the generated TOML prompts and ran `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` to confirm the updated agent semantics landed in both files with no manual hand-edit drift.

### Task 3: Update workflow and domain skills to treat steps as mutable guidance
**Depends on:** Task 1
**Review status:** APPROVED

**Script:** N/A
**Input:** `skills/planning-workflow/SKILL.md`, `skills/implementation-workflow/SKILL.md`, `skills/agent-orchestration/SKILL.md`, `skills/integration-workflow/SKILL.md`, and `skills/econ-data-analysis/SKILL.md`.
**Output:** Workflow wording aligned with objective-first semantics: planners write steps as actionable suggested routes, implementation flow checks objective clarity rather than treating steps as a literal contract, orchestration/reporting guidance distinguishes within-task adaptation from scope change and keeps the rationale for within-task route rewrites in the agent message layer rather than as handoff-doc history, integration review escalates whole-task restructure through `planning-workflow`, and `econ-data-analysis` adds a narrow within-task robustness/diagnostic reinforcement.

- [x] **Step 1: Edit `planning-workflow/SKILL.md`.** Clarified that task headings plus `Script` / `Input` / `Output` carry scope, planners write steps as the best current route rather than an exhaustive script, and in-scope step refinement is expected during execution.
- [x] **Step 2: Edit `implementation-workflow/SKILL.md`.** Updated Step 1 and Step 2 so the orchestrator checks task-boundary clarity, treats steps as starter guidance, and keeps accepted in-scope implementer step rewrites in `PLAN.md`.
- [x] **Step 3: Edit `agent-orchestration/SKILL.md` and `integration-workflow/SKILL.md`.** Added the within-task-adaptation versus scope-change rule, made the orchestrator expect route-rewrite rationale in the agent status message layer rather than in `PLAN.md`, and routed whole-task combine/split or boundary-change findings back through `planning-workflow`.
- [x] **Step 4: Edit `econ-data-analysis/SKILL.md`.** Added the narrow implementation-standard reinforcement that evidence-driven diagnostics, validation passes, or within-task robustness checks must be added when needed and reflected in the rewritten step text.
- [x] **Step 5: Run a stale-language sweep.** Re-read the touched workflow/domain files with targeted `rg` and `git diff` checks, tightened the remaining contradictory literal-adherence wording, and aligned the mid-INTEGRATE restructure example in `planning-workflow` with whole-task combine/split routing.

### Task 4: Add verification coverage and validate the change end-to-end
**Depends on:** Tasks 2, 3
**Review status:** IMPLEMENTED

**Script:** N/A
**Input:** The cumulative diff from Tasks 1-3, `tests/claude-code/run-skill-tests.sh`, `tests/claude-code/test-helpers.sh`, the existing Claude Code tests, and `skills/codex-superra-setup/scripts/sync_codex_agents.py`.
**Output:** One focused Claude Code test covering an incomplete task where an obvious within-task check is missing, updated test-runner wiring if needed, successful text-consistency and generated-agent verification evidence, and manual toy-plan validation notes recorded in `RESULTS.md`.

- [x] **Step 1: Add focused Claude Code coverage.** Added `tests/claude-code/test-objective-first-task-semantics.sh`, which asks Claude about a task whose steps omit an obvious duplicate-key validation after a merge and asserts that the response treats the task objective/scope as the contract, adds the missing within-task check, and expects reviewer pushback on mechanical step-following.
- [x] **Step 2: Wire the focused test into the runner and shared harness.** Added the new test to `tests/claude-code/run-skill-tests.sh`, updated the runner help text, documented the coverage in `tests/claude-code/README.md`, and made `tests/claude-code/test-helpers.sh` provide a portable `run_with_timeout` wrapper plus argv-safe `run_claude` execution so the suite runs on this macOS environment.
- [x] **Step 3: Run the text-level consistency sweep.** Ran targeted `rg` queries across `skills/`, `agents/`, `tests/`, and `.codex/agents/`; the only remaining literal-adherence phrases are the deliberate reviewer/domain guardrails and the new focused test prompt, while the objective/scope and changing-plans language remains aligned across the concern-owner surfaces.
- [x] **Step 4: Re-run generated-agent verification.** Ran `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` and confirmed the tracked `.codex/agents/*.toml` files are still up to date with no manual drift.
- [x] **Step 5: Run one manual Claude Code validation session.** Used a temporary toy `PLAN.md` / `RESULTS.md` pair with an omitted within-task merge check and confirmed that Claude rewrote the step list to add describe-before-merge and key-uniqueness checks, returned `REVISE` for a reviewer if the check were skipped, and routed any genuine whole-task split recommendation through `planning-workflow §User Feedback and Changing Plans`.
- [x] **Step 6: Sweep the final diff and record verification.** Re-read the owned diff for Task 4 scope, confirmed no manual edits were made to generated agent files, and recorded the focused test result, the consistency sweep, the generated-agent check, the manual validation outcome, and the remaining fast-suite concern in `RESULTS.md`.

> 1. MAJOR — [RESULTS.md](/Users/zhiyufu/Dropbox/package_dev/superRA-task-step-refinment/RESULTS.md:65): the non-regression note records the wrong remaining fast-suite failure mode. Re-running `tests/claude-code/run-skill-tests.sh` on this branch failed in 23s because the pre-existing legacy `tests/claude-code/test-subagent-driven-development.sh` still probes a nonexistent `subagent-driven-development` skill, not because it timed out. Update the Task 4 verification notes to describe the actual current failure while keeping it scoped as a legacy-suite follow-up rather than a blocker introduced by the new objective-first test.
>    → implemented: updated the Task 4 note to describe the actual legacy fast-suite failure mode as the stale nonexistent-skill probe rather than a timeout ([RESULTS.md](/Users/zhiyufu/Dropbox/package_dev/superRA-task-step-refinment/RESULTS.md:65))
