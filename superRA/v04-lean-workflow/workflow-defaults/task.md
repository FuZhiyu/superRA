---
title: "Workflow Defaults: Interactive Main Agent, On-the-Fly Review"
status: approved
depends_on: [role-skills, review-skill]
---

## Objective

Make interactive main-agent execution the default workflow and independent review an execution-time decision, re-scoping `superimplement` as the explicitly-entered autonomous mode.

- Interactive default: on a built tree the main agent executes tasks itself (the canvas loop) without loading `superimplement`. `superimplement` becomes the autonomous subagent workflow, loaded only when the researcher requests it or accepts the agent's recommendation — recommend with a one-line rationale when the frontier is broad, parallelizable, or context-heavy; never silently switch.
- Review is decided on the fly by whoever orchestrates, with researcher input — not scheduled at planning. After a task completes, judge from the result's stakes and plausibility (and any implementer concern return) whether an independent pass is worth it and at which tier/focuses; when the researcher is present, recommend and ask rather than dispatch. Planners may suggest a review in `## Details`; the suggestion does not bind.
- Define the approval transition when no review runs — the orchestrating agent sets `approved` after its own verification — and update the status-ownership sentence in `task-file-contract.md`, the resume semantics in `main-agent.md` §Resuming Work (`implemented` no longer universally means "to review"), and every unconditional review step in `superimplement`.
- Record what review an approved task actually got. At APPROVE the reviewer's tier/focus header goes away with `## Review Notes`, so an approved task carries no record of the depth and focus it was reviewed under — or of whether an independent pass ran at all. Under triggered review that record is load-bearing for the next reader; give it a durable home (the approving agent's commit body is the cheapest candidate).
- The INTEGRATE boundary keeps one thorough review of accumulated work as the safety net.
- Re-scope or verify `hooks/ensure-agent-orchestration` — it gates the `agent-orchestration` load for `superimplement`, which misfires when the default path dispatches nothing.
- Task-sizing instruction fixes live in the `planning-sizing` sibling (different edit surface: superplan references).
- Update the statements the flip invalidates: the `CLAUDE.md` "Gates are local discipline … enforced" principle (gates still bind when a review runs), and execution-mode/implement descriptions in `CLAUDE.md`, `README.md`, and `docs/site`.
- Validation: a fresh-session trace on a small tree runs interactive with zero dispatches and zero `superimplement` loads; a broad-frontier trace produces a subagent-mode recommendation; a completed high-stakes task produces a review recommendation naming tier and focuses.

## Details

- Motivation: subagent-heavy execution is slow and implements/reviews things the researcher never wanted; high human cadence catches misdirection early.
- Choreography map with the unconditional-review lines: [review-architecture map](../attachments/map-review-architecture.md) §2; scheduling options and evidence: [review-prompting research](../attachments/research-review-prompting.md) §C.
- Interactive mode's "ask before review: now / defer / skip" (`superplan/references/interactive-mode.md`) is the precedent; the canvas loop likely moves out of superplan's references to a home both PLAN and IMPLEMENT enter.
- Seat assignment in `agent-orchestration` stays useful for the autonomous mode — re-scope it, don't delete it.

## Results

Interactive is the default execution mode and independent review is an execution-time call. Both decisions have one home each in [main-agent.md](../../../skills/using-superra/references/main-agent.md): §Execution Modes and §Deciding on Review.

**The default flipped.** §Execution Modes opens on interactive — the main agent executes the task itself through the canvas loop, with no `superimplement` load and no dispatch — and demotes autonomous to the opt-in, entered on researcher request or an accepted one-line recommendation (recommend when the frontier is broad, parallelizable, or context-heavy). [superimplement](../../../skills/superimplement/SKILL.md) is re-framed to match: entering it *is* autonomous mode. The canvas loop moved to [using-superra/references/interactive-mode.md](../../../skills/using-superra/references/interactive-mode.md), a home both phases enter.

**§Deciding on Review is the single home for the review call**, read by the orchestrating agent in either mode: judge stakes and plausibility; review on a researcher request, a planner high-stakes mark, an implementer concern, or a load-bearing result the evidence cannot settle; recommend-and-ask when the researcher is present; otherwise verify it yourself and set `approved`. `superimplement` and the interactive loop branch off it rather than restating it, `implemented` now reads as "approval decision still open," and the planner side gets one line: mark high-stakes work with the tier and focus you would want, never schedule review as a task.

**The review-depth record goes in the commit body**, one sentence in [using-superra §Commits](../../../skills/using-superra/SKILL.md): a commit landing `status: approved` names the tier and focuses, or states that no independent pass ran and approval rests on the approving agent's own verification. A task-file field would have needed the same rule stated in both role skills and would put back exactly what the reporting contract moved out; the commit body is already read by both possible writers and sits next to the diff it describes.

**The default path can close IMPLEMENT without loading `superimplement`.** Its reproducibility check and four-option completion menu moved verbatim to [completion.md](../../../skills/superimplement/references/completion.md), which both the spine and the interactive loop reach by a plain `Read` — preserving the zero-load property of the default path. Ownership stays with `superimplement`. At the other end, [integrate.md](../../../skills/superintegrate/references/integrate.md) Step 6 states that its reviewer pass runs regardless of what individual tasks got, at `Tier: thorough`.

`CLAUDE.md`, `README.md`, and the `docs/site` pages taught autonomous-by-default and reviewer-APPROVE-required; all now teach interactive-by-default and review-where-it-earns-its-cost, keeping the blind-spot argument for independence.

### Validation

**One live trace ran and passed.** A fresh Claude Agent-SDK session over a scratch two-task tree, prompted `superra: work the frontier of the task tree in this repo.`, loaded `using-superra` and `implement-task` and **not** `superimplement`, dispatched nothing, did the work itself, committed, and closed with a three-way ask naming `thorough` plus `correctness`/`scope-fidelity` as what it would use.

**Two of the objective's three traces were never executed** — the broad-frontier recommendation trace and the high-stakes review recommendation. The second attempt escaped its scratch fixture and committed into this repo's own worktree (reset as `7014a366`), so live tracing was stopped rather than risk a second escape. The escape is owned by [task-tree/agent-cwd-isolation](../../task-tree/agent-cwd-isolation/task.md), and the re-run rides with it. Nothing in this branch verifies those two behaviors beyond the instruction text.

**The live smoke deliberately covers the review-requested path, not the new default.** Its orchestrator prompt supplies the researcher-request trigger so the reviewer-seat dispatch stays covered; a shallow sentinel task gives an autonomous run no reason to review, so asserting the no-review path there would trade real dispatch coverage for a weak assertion.

**Suites.** `tests/harness-instruction-following` 126 passed, matching the pre-change baseline; hooks 15/15; `check-harness-compatibility.sh` exit 0. One test failed mid-work — `test_seat_fillers_reach_the_role_skills_by_name` — and was fixed by naming both role skills in `main-agent.md`, not by weakening the test. `skills/task-tree/scripts` produced three different `test_dashboard.py` failures across three runs, each passing in isolation on the same diff; they are timing and port flakes on this machine, and the diff touches no file in that directory.
