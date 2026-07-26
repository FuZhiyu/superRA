---
title: "Execution Mode Model & Interactive Canvas"
status: approved
depends_on: []
---

## Objective

Reshape superRA's execution-mode model and add an interactive canvas mode. Model the choice as **two dials, surfaced as named presets plus a seat knob**:

- **Axis A — human cadence (autonomy).** Autonomous (runs to completion) ↔ interactive (pauses often for the researcher). Default is autonomous/subagent; interactive is an explicit opt-in. `superimplement` on a built tree defaults to subagent unless interactive is requested.
- **Axis B — seat assignment.** Each task has an implementer seat and a reviewer seat; each is filled by the main agent or a dispatched subagent. The orchestrator chooses **per task** — subagent reviewer for large/routine subtrees (lean main context), main-agent reviewer for small or high-stakes tasks (strongest model on the critical, adversarial seat). Whoever fills a seat runs that seat's role spec.

Two modes over these dials: **subagent** (autonomous — default; Axis B picks one of three seat structures, main-in-a-seat runs that seat's role spec) and **interactive** (main executes directly at high human cadence — the canvas). There is no `manual` preset; main-fills-both is served by interactive with review deferred. Seat assignment is a knob `agent-orchestration` owns, not a mode.

**Interactive mode** replaces the old direct mode's behavior (renamed `interactive`, `direct` kept as an alias; old full-gate behavior retired). It is a fused **light-plan → execute-yourself → record** loop, not only an implementer mode: it spans lightly scoping a target into a task and executing it, through **retroactive capture** — writing up work already done (a handoff note, or a task reflecting what changed) by running the same loop results-first. In it: co-edit the task file as a live canvas; **self-review always**; **keep the task updated** (results + status) and **ask before review with a tool** as required loop steps; defer / skip leaves the task `implemented`; positioning retained; full gate ceremony and automatic reviewer dispatch dropped. The selection axis is autonomy/human-involvement — interactive is for work the researcher steers closely, often hard and concentrated. Routed through `superplan`.

Success: the contract documents the two modes on the autonomy axis; the interactive canvas is a loadable superplan reference sized for concentrated work, with keep-updated and tool-ask-before-review as required steps; `agent-orchestration` supports per-task seat assignment (three structures); `superimplement` defaults to subagent unless interactive is requested; the generated direct-mode role references are removed and their generator updated; no gate is silently weakened by the superplan de-crowd.

### Context

superRA-internal skill authoring. Follow `CLAUDE.md` — the DRY + Necessity gate, ownership boundaries, generated-artifact rules, and "instruct, don't justify." No domain skill governs this work; `skill-creator` governs `skills/*/SKILL.md` edits where available.

### Conventions

- Route interactive-mode procedure through `superplan`; `task-tree` remains the tooling (CLI/dashboard) the mode drives, not the procedure home.
- The contract *names* the seat model; `agent-orchestration` owns the seat-assignment *mechanics* — point, do not duplicate.
- Reuse the existing status enum; no new status for the elective-review state.
- Editable-from-dashboard is out of scope — the dashboard is a read-only live canvas view for this workstream.

## Results

The integrated branch now carries one coherent execution contract:

- [main-agent.md:42-52](../../skills/using-superra/references/main-agent.md#L42-L52)
  defines autonomous/subagent as the default and interactive as the explicit
  high-human-cadence opt-in.
- [agent-orchestration/SKILL.md:85-109](../../skills/agent-orchestration/SKILL.md#L85-L109)
  owns the three autonomous seat structures and routes a main-filled seat
  through the same canonical role spec as a dispatched seat.
- [interactive-mode.md:14-27](../../skills/superplan/references/interactive-mode.md#L14-L27)
  owns the self-contained canvas loop: self-review, live task updates, and a
  tool-mediated review-now/defer/skip question.
- [codex-instructions.md:10-30](../../skills/using-superra/references/codex-instructions.md#L10-L30)
  keeps harness-forced inline execution separate from interactive mode.

### Integration contract repair

Review-now/defer/skip now uses the existing lifecycle: defer and skip leave the
task `implemented`, without a parallel review-status field. The shared
[canonical-role resolver](../../skills/using-superra/references/canonical-role.md)
makes the canonical implementer and reviewer specs available to main-filled and
forced-inline seats in both Claude and Codex, including installed cross-repo
use. Contract owners now point to those shared mechanics; duplicate lifecycle,
tree-change, and seat-routing instructions were pruned under the DRY/Necessity
gate. Focused verification passed for packaged role resolution (`1` test),
Codex agent generation (`3` tests), execution-contract behavior (`32` tests),
the CI-safe harness (`126` tests), and all five edited skill directories.

The obsolete generated direct-mode role mirrors and their generator path are
gone. The canonical [implementer](../../agents/implementer.md) and
[reviewer](../../agents/reviewer.md) specs remain unchanged and the committed
`.codex/agents` TOMLs byte-match generator output. A current-surface sweep found
no stale direct-mode function names, deleted mirror paths, `manual` preset, or
trivial-task interactive fallback outside dated historical records.

The Project Doc Audit reconciled the current user and workflow surfaces:
[README.md:9-26](../../README.md#L9-L26) and the documentation-site overview,
quickstart, workflow, domain, and status pages now distinguish default
autonomous review from interactive self-review and elective independent review.
The trivial Sync and integration-pruning paths are described as inline paths,
not automatic switches into interactive mode
([sync.md:1-50](../../skills/superintegrate/references/sync.md#L1-L50)).
[RELEASE-NOTES.md:9-33](../../RELEASE-NOTES.md#L9-L33) names the interactive
contract, generated-role cleanup, retained econ-data rules, and conservative
prose-test cleanup as the three PR concerns. Historical plan and release records
remain untouched.

The conservative test cleanup remains test-, fixture-, and test-documentation
only, adds no live/model/network execution or production testability surface,
and is net-negative. The branch-wide test diff is 721 additions and 2,556
deletions across 52 files, including the retained structured interactive and
seat-routing tests. See
[prose-test-cleanup/task.md](prose-test-cleanup/task.md) for its narrower
accepted-cleanup accounting and preserved behavior classes.

Verification on the integrated tree:

- Task-tree and harness suites: `824 passed`, `0 failed`, four expected warnings.
- Harness compatibility: exit `0`; generator tests `3/3`; committed Codex
  agents up to date.
- Codex hook shell suite: `15/15`.
- Zotero shell suite: `18/18`.
- Markdown checker on every integration-edited Markdown file: clean.
- `git diff --check`: clean.

**Final diff self-check:** `git diff origin/main...HEAD`; surviving-change
classes are the two-mode/seat contract, interactive canvas and routed
superplan refactor, canonical-agent generator simplification, econ-data
efficiency rules, conservative test/fixture/test-doc pruning, current user and
workflow documentation currency, release metadata, and task records.
Suspicious hunks are justified: instruction edits under `skills/*` implement
the approved contract and DRY/necessity gates; deleted direct-mode mirrors and
generator logic retire the explicitly obsolete generated surface while the
Codex TOMLs remain source-generated; broad test deletions are the approved
net-negative prose-oracle cleanup with state/schema/path/exit/order/mutation/
secret coverage retained; current-doc migrations correct claims contradicted by
the contract; no scope-ambiguous hunk remains.
