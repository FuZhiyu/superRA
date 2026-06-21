---
title: "Main-Agent Trimming: Status+Git Resume Model, Less Prescription"
status: approved
depends_on: []
tags: []
created: 2026-06-21
---

## Objective

`skills/using-superra/references/main-agent.md` has drifted from how the workflow actually operates and over-prescribes. Two problems:

1. **The "Workflow Frontier Resolver" framing assumes a workflow-stage that does not exist.** The only durable state is per-task `status` frontmatter plus the git log. The frontmatter field set is closed (`title, status, depends_on, tags, script, input, output, created`) — there is no place to store a phase, and INTEGRATE deliberately keeps no stage marker (`superintegrate/SKILL.md`: progress is read from git + statuses). So "stages" — implemented-or-not, integrated-or-not — are reconstructed from git, while files track only per-task status. The resolver's elaborate "compute which phase to enter" procedure is mostly ceremony over a status-driven loop, and its safety-invariant list restates gates the workflows already own locally (DRY violation per [CLAUDE.md](../../CLAUDE.md) Ownership Boundaries).

2. **The pause/proceed guidance enumerates scenarios instead of teaching the idea.** "Banned Phrasings", scenario-by-scenario "Proceed Without Asking" lists, and the long pause-class enumerations violate the CLAUDE.md "Teach the Protocol, Don't Prescribe Each Action" gate.

**Goal:** make `main-agent.md` reflect the status+git architecture (a "Resuming Work" model, not phase resolution) and state pause/proceed as principles, not scenario trees. Build on the researcher's in-flight unstaged edits to this file rather than reverting them.

### Context

- Conversation origin: the resolver was found redundant with `superra task frontier` / `task check`, then found to assume a durable stage that does not exist. `compute_frontier` (`skills/task-tree/scripts/_task_io.py:851`) returns only `not-started`/`in-progress` leaves — `implemented` (awaiting review) and `revise` (awaiting fix) are off the frontier, which is why "just run the frontier and execute" is not yet the complete loop. That gap is the subject of [01-frontier-completeness](01-frontier-completeness/task.md) and decides how the resume prose in [02-resuming-work-rewrite](02-resuming-work-rewrite/task.md) is written.
- Eight files currently point at "§Workflow Frontier Resolver": `superimplement/SKILL.md` (×4), `superplan/SKILL.md` (step 6), `superintegrate/SKILL.md`, `using-superra/SKILL.md`, `agent-orchestration/SKILL.md`. The researcher's view: once an agent knows how to resume it knows how to proceed, so most of these pointers can be dropped, not just repointed.

### Constraints

- The working tree carries unrelated unstaged changes (deleted harness-adapter references `claude-tools.md`/`copilot-tools.md`/`gemini-tools.md`, `codex-instructions.md` edits, `docs/` edits). These are a separate effort — out of scope here. Per `using-superra` §Commit Hygiene, stage only the files each task touches.
- This work edits `skills/*` prose and `skills/*/SKILL.md` — treat as skill creation (load `skill-creator`) and self-apply the CLAUDE.md DRY + Necessity gate line by line.

## Results
