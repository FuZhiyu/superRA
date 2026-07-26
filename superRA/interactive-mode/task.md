---
title: "Execution Mode Model & Interactive Canvas"
status: in-progress
depends_on: []
---

## Objective

Reshape superRA's execution-mode model and add an interactive canvas mode. Model the choice as **two dials, surfaced as named presets plus a seat knob**:

- **Axis A — human cadence (autonomy).** Autonomous (runs to completion) ↔ interactive (pauses often for the researcher). Default is autonomous/subagent; interactive is an explicit opt-in. `superimplement` on a built tree defaults to subagent unless interactive is requested.
- **Axis B — seat assignment.** Each task has an implementer seat and a reviewer seat; each is filled by the main agent or a dispatched subagent. The orchestrator chooses **per task** — subagent reviewer for large/routine subtrees (lean main context), main-agent reviewer for small or high-stakes tasks (strongest model on the critical, adversarial seat). Whoever fills a seat runs that seat's role spec.

Two modes over these dials: **subagent** (autonomous — default; Axis B picks one of three seat structures, main-in-a-seat runs that seat's role spec) and **interactive** (main executes directly at high human cadence — the canvas). There is no `manual` preset; main-fills-both is served by interactive with review deferred. Seat assignment is a knob `agent-orchestration` owns, not a mode.

**Interactive mode** replaces the old direct mode's behavior (renamed `interactive`, `direct` kept as an alias; old full-gate behavior retired). It is a fused **light-plan → execute-yourself → record** loop, not only an implementer mode: it spans lightly scoping a target into a task and executing it, through **retroactive capture** — writing up work already done (a handoff note, or a task reflecting what changed) by running the same loop results-first. In it: co-edit the task file as a live canvas; **self-review always**; **keep the task updated** (results + status) and **ask before review with a tool** as required loop steps; independent review elective (now / defer / skip) reusing `implemented` / `approved` — no new status; positioning retained; full gate ceremony and automatic reviewer dispatch dropped. The selection axis is autonomy/human-involvement — interactive is for work the researcher steers closely, often hard and concentrated. Routed through `superplan`.

Success: the contract documents the two modes on the autonomy axis; the interactive canvas is a loadable superplan reference sized for concentrated work, with keep-updated and tool-ask-before-review as required steps; `agent-orchestration` supports per-task seat assignment (three structures); `superimplement` defaults to subagent unless interactive is requested; the generated direct-mode role references are removed and their generator updated; no gate is silently weakened by the superplan de-crowd.

### Context

superRA-internal skill authoring. Follow `CLAUDE.md` — the DRY + Necessity gate, ownership boundaries, generated-artifact rules, and "instruct, don't justify." No domain skill governs this work; `skill-creator` governs `skills/*/SKILL.md` edits where available.

### Conventions

- Route interactive-mode procedure through `superplan`; `task-tree` remains the tooling (CLI/dashboard) the mode drives, not the procedure home.
- The contract *names* the seat model; `agent-orchestration` owns the seat-assignment *mechanics* — point, do not duplicate.
- Reuse the existing status enum; no new status for the elective-review state.
- Editable-from-dashboard is out of scope — the dashboard is a read-only live canvas view for this workstream.

## Review Notes

1. MAJOR — [interactive-mode.md:22-26](../../skills/superplan/references/interactive-mode.md#L22-L26), [main-agent.md:14-16](../../skills/using-superra/references/main-agent.md#L14-L16), and [superimplement/SKILL.md:90-110](../../skills/superimplement/SKILL.md#L90-L110). The elective-review lifecycle is not coherent: **Defer** and **Skip** both leave the only durable state as `implemented`; session resume treats every `implemented` task as requiring review; and `superimplement` refuses reproducibility/completion handoff until every task is `approved`. A skip is therefore neither distinguishable nor durable, while a deferred interactive task cannot reach the completion menu without the supposedly elective review. Fix the status/results routing so now, defer, and skip have distinct durable effects while reusing the existing status enum, and make the resume and completion paths honor the recorded choice.
   → implemented: [interactive-mode.md:22-32](../../skills/superplan/references/interactive-mode.md#L22-L32) records distinct dispositions and routes defer/skip to `approved`; [main-agent.md:16](../../skills/using-superra/references/main-agent.md#L16) preserves those choices on resume.

2. MAJOR — [superimplement/SKILL.md:20-25](../../skills/superimplement/SKILL.md#L20-L25), [superimplement/SKILL.md:74-83](../../skills/superimplement/SKILL.md#L74-L83), and [agent-orchestration/SKILL.md:85-109](../../skills/agent-orchestration/SKILL.md#L85-L109). The autonomous workflow still mandates implementer and reviewer **subagent** dispatches, so its executable process contradicts the new main/subagent seat structures. Fix `superimplement` to select and execute the per-task seat structure rather than hard-code two dispatches.
   → implemented: [superimplement/SKILL.md:20-24](../../skills/superimplement/SKILL.md#L20-L24) and [superimplement/SKILL.md:74-89](../../skills/superimplement/SKILL.md#L74-L89) now select the structure and execute each filler through a structured main/dispatch route.

3. MAJOR — [agent-orchestration/SKILL.md:101-109](../../skills/agent-orchestration/SKILL.md#L101-L109), [codex-instructions.md:10-18](../../skills/using-superra/references/codex-instructions.md#L10-L18), and [codex-superra-setup/SKILL.md:36-43](../../skills/codex-superra-setup/SKILL.md#L36-L43). Named-agent installation is correctly required/prompted and the generated agents are current, but main-seat and harness-forced-inline paths load bare `agents/*.md` paths without a cross-repo resolution rule. The setup skill recognizes that plugin use runs from another repository and resolves its own resource relative to the skill directory; the new transcript fixtures prove role reads only from this repository's cwd. Give main-filled and forced-inline seats a plugin-resolvable path to the canonical role specs and cover that packaged, cross-repo path.
   → implemented: [codex-instructions.md:16-20](../../skills/using-superra/references/codex-instructions.md#L16-L20) routes both paths through `canonical-role`; [codex-superra-setup/SKILL.md:74-83](../../skills/codex-superra-setup/SKILL.md#L74-L83) and its resolver emit the plugin-relative canonical path, covered from a foreign working directory.

4. MAJOR — [interactive-mode.md:16-20](../../skills/superplan/references/interactive-mode.md#L16-L20). The reference promises “self-review always” and deliberately loads no role spec, but its sole review instruction is to walk the active **domain** checklist. A no-domain task—such as superRA workflow maintenance itself—therefore has no self-review operation at all. Add the minimum domain-neutral objective/evidence/verification pass, with active domain gates applied in addition when present.
   → implemented: [interactive-mode.md:18-19](../../skills/superplan/references/interactive-mode.md#L18-L19) now requires a domain-neutral objective/diff/output/verification pass before adding active domain gates.

5. MAJOR — [CLAUDE.md:46-66](../../CLAUDE.md#L46-L66), [agent-orchestration/SKILL.md:89-107](../../skills/agent-orchestration/SKILL.md#L89-L107), and [superplan/SKILL.md:105-111](../../skills/superplan/SKILL.md#L105-L111). The instruction diff fails the repository's explicit blocking DRY/Necessity gate. `agent-orchestration` repeats the seat-choice criteria in both the table and the following signal list, then restates reviewer-owned review-note/verdict behavior immediately after requiring `agents/reviewer.md`; the slimmed `superplan` spine paraphrases the drift distinction, tracker rule, full change protocol, and stop rule already owned by `changing-the-tree.md`. Keep the seat-specific orchestration delta and routing conditions, but remove the duplicated role/reference content and point to the authoritative owners.
   → implemented: [agent-orchestration/SKILL.md:85-95](../../skills/agent-orchestration/SKILL.md#L85-L95) retains one seat-choice table plus the orchestration delta; [superplan/SKILL.md:104-110](../../skills/superplan/SKILL.md#L104-L110) now routes without paraphrasing the owner.

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
and is net-negative. The branch-wide test diff is 663 additions and 2,551
deletions across 52 files, including the retained structured interactive and
seat-routing tests. See
[prose-test-cleanup/task.md](prose-test-cleanup/task.md) for its narrower
accepted-cleanup accounting and preserved behavior classes.

Verification on the integrated tree:

- Full CI-safe Python suite: `899 passed`, `0 failed`, four expected warnings.
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
