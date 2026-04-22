# Objective-First Task/Step Semantics - Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-22 (Task 1 revise pass)
**Status:** In Progress - Task 1 implemented, Tasks 2-4 not started

---

## Task 1: Canonicalize objective-first task-block semantics

**Status:** Implemented (awaiting review 2026-04-22)

### Key Findings
- `CLAUDE.md` now carries a contributor-level rule that the task heading names the objective, `Script` / `Input` / `Output` bind scope, steps are the current best route, and review is objective-first.
- `skills/handoff-doc/references/plan-anatomy.md` and `skills/handoff-doc/references/results-anatomy.md` now show objective-style task-title placeholders everywhere the handoff-doc canon demonstrates task headings.
- The root `RESULTS.md` header now reflects that execution has started and Task 1 is implemented, instead of leaving the file in a planning-only state.

### Notes
- The current task-block anatomy has no per-task `**Objective:**` line, so the canonical wording treats the task heading as the objective carrier and preserves the existing block shape.
- Re-read both concern owners after editing and kept the exact task-block mechanics in `plan-anatomy.md` rather than duplicating them in contributor guidance.

## Task 2: Reframe implementer and reviewer role contracts

**Status:** Implemented (awaiting review 2026-04-22)

### Key Findings
- `agents/implementer.md` now treats the task heading/objective plus `Script` / `Input` / `Output` as the scope contract, allows within-task step split/combine plus extra diagnostics/validation/robustness work when needed, and directs any step-path rationale to the status return instead of `PLAN.md` history.
- `agents/reviewer.md` now judges objective completion before literal step adherence, treats missing necessary checks as review findings even when the listed steps were followed, and routes integration-stage whole-task combine/split recommendations through `planning-workflow §User Feedback and Changing Plans`.
- The managed Codex mirrors were regenerated only through `skills/codex-superra-setup/scripts/sync_codex_agents.py`, and `--check` confirmed both `.codex/agents/*.toml` files are up to date.

### Notes
- Re-read the regenerated TOML prompts to confirm the new objective-first language appears in both managed Codex agent files.
- No manual edits were made to `.codex/agents/superra_implementer.toml` or `.codex/agents/superra_reviewer.toml`.

## Task 3: Update workflow and domain skills to treat steps as mutable guidance

**Status:** Implemented (awaiting review 2026-04-22)

### Key Findings
- `skills/planning-workflow/SKILL.md` now tells planners that task headings plus `Script` / `Input` / `Output` bind scope, while steps are the best current route and should guide execution without trying to pre-script every in-task diagnostic or robustness branch.
- `skills/implementation-workflow/SKILL.md` now makes the orchestrator check task-boundary clarity during Step 1 and judge completion against the task objective/scope plus the checklist during Step 2, instead of grading literal adherence to the planner's first step wording.
- `skills/agent-orchestration/SKILL.md` and `skills/integration-workflow/SKILL.md` now separate normal within-task route adaptation from scope change, keep the explanation for route rewrites in the implementer status message layer, and route whole-task combine/split or boundary-change findings back through `planning-workflow §User Feedback and Changing Plans`.
- `skills/econ-data-analysis/SKILL.md` now explicitly requires implementers to add evidence-driven diagnostics, validation passes, or within-task robustness checks when needed to trust a result, even if the original step list omitted them.

### Notes
- The stale-language sweep used targeted `rg` queries plus a focused `git diff` review over the five touched skill files; the remaining “literal adherence” phrasing is now only the deliberate guardrail in `econ-data-analysis` that rejects literalism when the evidence demands extra checks.
- The sweep also caught one lingering mid-INTEGRATE restructure example in `planning-workflow` that still said task add/remove/combine; it now says add/remove/combine/split so the owned workflow surfaces tell the same story.
- The REVISE pass fixed one additional stale summary in `skills/integration-workflow/SKILL.md`'s Phase Map so the high-level overview now matches the file's later operative rules on whole-task split and task-boundary changes.

## Task 4: Add verification coverage and validate the change end-to-end

**Status:** Not started
