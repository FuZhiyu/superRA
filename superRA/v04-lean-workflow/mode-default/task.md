---
title: "Interactive as Default Execution Mode"
status: not-started
depends_on: [review-policy]
---

## Objective

Make interactive the default execution mode, with subagent mode entered on researcher request or agent recommendation.

- Flip the default in `main-agent.md` §Execution Modes, `using-superra` §Execution Modes, and `superimplement`: the main agent executes tasks itself at high human cadence unless subagent mode is chosen.
- Agent recommendation, not silent switching: when the frontier is broad (many independent tasks), parallelizable, or too context-heavy for one agent, recommend subagent mode with a one-line rationale and let the researcher decide.
- Promote the interactive canvas loop from `superplan/references/interactive-mode.md` to wherever the new default's owning home is; keep it enterable from planning and implementation alike.
- Update statements the flip invalidates (`CLAUDE.md` execution-mode rows, `README.md`, `docs/site` mode descriptions if asserted there), and re-scope or verify `hooks/ensure-agent-orchestration` — it gates the `agent-orchestration` load for `superimplement`, which misfires when the default path dispatches nothing.
- Validation: a fresh-session trace on a small tree runs interactive with zero dispatches; a broad-frontier trace produces a subagent-mode recommendation.

## Planner Guidance

- Motivation: subagent-heavy execution is slow and implements/reviews things the researcher never wanted; high human cadence catches misdirection early.
- The current two-dial contract (autonomous default, interactive opt-in) is at `main-agent.md` §Execution Modes; seat assignment stays useful for subagent mode — don't delete it, re-scope it.
- Review triggering (`review-policy`) already lands the ask-before-review behavior; this task only changes which mode is default and adds the recommendation duty.

## Results
