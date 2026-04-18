---
author: "[[Julie Zhiyu Fu]]"
date: 2026-04-17
timestamp: "2026-04-18T00:00:00"
session_id: "session-20260418-plan-stage-marker"
git_commit: "34b1808"
git_message: "results: fact-check Stage 2 RESULTS.md"
git_dirty: true
tags: ["results", "integration", "iterative-re-entry"]
project: "[[superRA]]"
permalink: "docs/plans/2026-04-17-plan-stage-marker-results"
---

# Plan Stage Marker + Iterative Re-entry Mechanism — Results

## Objective

Give the superRA skills a unified iterative re-entry mechanism so a fresh agent picking up an in-flight project (a) can tell which workflow stage is active from `## Workflow Status` + per-task fields, (b) can re-enter execution or integration for small-scope additions without spinning up a new `PLAN.md`, and (c) main agents always have handoff-doc discipline loaded at session start. All five tasks were approved at implementation review and integration review; the shipped mechanism is now self-applied inside `PLAN.md` on this branch.

## What Shipped

Five coordinated changes ship together. They were planned as separate tasks but land as a single conceptual unit — the re-entry mechanism requires the new field, the renamed protocol section, the workflow-skill wire-ups, the agent-file header-ownership bullet, and the main-agent reference consolidation to all agree.

### Iterative re-entry protocol — `planning-workflow §Changing Plans`

The protocol that governs plan changes now lives in [`skills/planning-workflow/SKILL.md`](../../skills/planning-workflow/SKILL.md) as a top-level `## Changing Plans` section, placed after `## Living Plan and Results Docs` and before `## No Placeholders`. A single protocol covers both triggers — in-session scope drift and cross-session re-entry — because the underlying mechanic is the same: re-invoke the protocol, confirm intent, log a decision, inline-edit `PLAN.md`, update `## Workflow Status`, commit atomically, resume.

The section carries:

- A collapsed single-framing preamble — "when the plan changes, follow this protocol" — after the earlier `(a) in-execution / (b) post-integration` split was found to encode a phase distinction the body does not honor.
- The 6-step protocol, ported verbatim from the prior `handoff-doc §Scope Changes and Re-entry` section.
- The DAG transitive-downstream cascade rule: the orchestrator walks the `**Depends on:**` DAG and clears `**Review status:**` and `**Integration status:**` for every task in the transitive downstream closure of any task whose code or outputs change; exemptions require a documented blockquote per exempted task in `## Decisions`.
- Four banned-shortcut bullets, including: running a subset of the drift-test suite on re-entry because "only these tasks changed" is explicitly forbidden.
- The prefer-updating rule: "Prefer modifying existing task blocks over appending" — new tasks only when the new work is truly disjoint from every existing task.

`handoff-doc/SKILL.md §Scope Changes and Re-entry` is removed; a one-sentence pointer under `§PLAN.md Is the Task Tracker` directs readers to `planning-workflow §Changing Plans`. This follows the one-source-of-truth principle — `handoff-doc` owns doc *structure*; `planning-workflow` owns how to *create and update* plans.

### `**Integration status:**` task-block field

Task blocks in `PLAN.md` now carry two status fields. Template authored in [`skills/handoff-doc/references/plan-anatomy.md`](../../skills/handoff-doc/references/plan-anatomy.md):

```markdown
**Review status:** unset / IMPLEMENTED / REVISE / APPROVED
**Integration status:** unset / IMPLEMENTED / REVISE / APPROVED
```

`**Review status:**` is set by the execution reviewer at task completion. `**Integration status:**` is set by the integration reviewer considering drift-test coverage, refactor quality, and doc coverage for that task's contribution. Both fields follow the same DAG cascade rule on re-entry.

The `## Workflow Status` project-level checkboxes are no longer standalone flags — they are a **rollup** over per-task states. The orchestrator unchecks them at re-entry by judgment and documents the un-check reasoning in a `## Decisions` blockquote. A task that was not touched at re-entry retains APPROVED; a fully re-implemented task clears both fields; a minor-edited task may clear only `**Integration status:**`.

### Drift-test, refactor, and doc discipline across re-entry

`integration-workflow` — [`skills/integration-workflow/SKILL.md`](../../skills/integration-workflow/SKILL.md) — carries three coordinated rules so re-entry integration never ships with stale invariants or stale docs:

- **Full drift-test suite always runs.** Only *authoring* new drift tests is scoped to relevant tasks. Stage 1 always dispatches the complete suite regardless of which tasks cleared, and the `Drift tests created` box keys on all tasks having `**Integration status:** APPROVED`.
- **Refactorer scope.** Stage 2 refactors the full diff against main, not just the tasks whose `**Integration status:**` was cleared.
- **Doc-writer full; doc-reviewer diff.** Step 3 doc-writer always re-runs the whole `RESULTS.md` maturation pass; the doc-reviewer reviews the diff against the prior matured form.

`execution-workflow` Step 1 sub-step 2a — [`skills/execution-workflow/SKILL.md`](../../skills/execution-workflow/SKILL.md) — now reframes the box/status mismatch on dispatch as *resumption* of a paused `§Changing Plans` run, not an independent detection trigger. The mismatch exists only because Step 4 of the protocol unchecked the boxes as a cross-session persistence marker; resuming at Step 6 is the correct handoff. Mid-execution researcher pings enter the protocol at Step 1 instead.

### Main-agent reference consolidation

[`skills/using-superRA/references/main-agent.md`](../../skills/using-superRA/references/main-agent.md) (new) replaces two prior files — `session-bootstrap.md` and `main-agent-autonomy.md` — with one reference carrying: MANDATORY Session Start Actions; Cross-Session Detection (bash block + incomplete-plan handling + worktree handling); **Load the Handoff-Doc Skill** (new); The Three Pause Classes; Proceed Without Asking; Banned Phrasings; One Question at a Time; Log Before You Act.

Main agents now load `superRA:handoff-doc` by default at session start. This makes the editing discipline and all `planning-workflow §Changing Plans` cross-references (User Decisions Log, plan-anatomy templates) available before the main agent touches `PLAN.md`. The subagent-side Skill-Load Manifest rows are unchanged — subagents still load `handoff-doc` only on `documentation` / `planning-review` stages.

### Iterative framing in top-level docs

[`skills/using-superRA/SKILL.md`](../../skills/using-superRA/SKILL.md) gains a **Significant plan changes re-enter planning-workflow** paragraph at the level every agent reads. When the plan meaningfully changes — new task, removed or reordered task, material update to an existing task, post-integration scope addition — the agent re-invokes `planning-workflow §Changing Plans`.

[`CLAUDE.md`](../../CLAUDE.md) and [`README.md`](../../README.md) reframe the workflow as **iterative, not linear**: PLAN → IMPLEMENT → VALIDATE → INTEGRATE is a cycle, not a one-shot pipeline; re-entering PLAN mid-execution or after integration is the normal case; `planning-workflow §Changing Plans` is the hinge that makes re-entry safe.

### Agent-file header ownership

[`agents/implementer.md`](../../agents/implementer.md) and [`agents/reviewer.md`](../../agents/reviewer.md) gain a new bullet inside the "**You may NOT edit:**" lists naming the `PLAN.md` header — including `## Workflow Status` and `## Decisions` — as orchestrator-owned. Implementer-voice: "report it in your status return; the orchestrator handles the doc edit." Reviewer-voice: "raise it in your status report; do not edit the header yourself." Both bullets cite `superRA:handoff-doc references/plan-anatomy.md §Header ownership` as the source of the rule.

## Files Touched

| File | Change |
|---|---|
| [`skills/planning-workflow/SKILL.md`](../../skills/planning-workflow/SKILL.md) | New `## Changing Plans` section (6-step protocol + DAG cascade + banned shortcuts) |
| [`skills/handoff-doc/SKILL.md`](../../skills/handoff-doc/SKILL.md) | `§Scope Changes and Re-entry` body removed; one-sentence pointer under `§PLAN.md Is the Task Tracker` |
| [`skills/handoff-doc/references/plan-anatomy.md`](../../skills/handoff-doc/references/plan-anatomy.md) | `**Integration status:**` added to task-block template; `## Workflow Status` description expanded with rollup + re-entry semantics; Field-by-Field updated with cascade rule |
| [`skills/execution-workflow/SKILL.md`](../../skills/execution-workflow/SKILL.md) | Step 1 sub-step 2a rewritten as resumption-of-paused-protocol; Stop-Points pointer retargeted to `planning-workflow §Changing Plans` |
| [`skills/integration-workflow/SKILL.md`](../../skills/integration-workflow/SKILL.md) | Stage 1 always-full-drift-suite rule; Stage 2 scoped refactor; Step 3 doc-writer-full + doc-reviewer-diff; pointers retargeted |
| [`skills/using-superRA/SKILL.md`](../../skills/using-superRA/SKILL.md) | Main-agent default-load paragraph added; new **Significant plan changes re-enter planning-workflow** paragraph |
| [`skills/using-superRA/references/main-agent.md`](../../skills/using-superRA/references/main-agent.md) | New consolidated reference |
| `skills/using-superRA/references/session-bootstrap.md` | Deleted |
| `skills/using-superRA/references/main-agent-autonomy.md` | Deleted |
| [`agents/implementer.md`](../../agents/implementer.md), [`agents/reviewer.md`](../../agents/reviewer.md) | Header-ownership bullet added to "You may NOT edit" list |
| [`CLAUDE.md`](../../CLAUDE.md), [`README.md`](../../README.md) | Iterative-workflow reframing |
| [`skills/agent-orchestration/references/agent-teams.md`](../../skills/agent-orchestration/references/agent-teams.md), [`skills/CATEGORIES.md`](../../skills/CATEGORIES.md) | Stale pointers retargeted to `main-agent.md` |
| [`RELEASE-NOTES.md`](../../RELEASE-NOTES.md) | New Unreleased entry |

## Verification

- `grep -rn "Scope Changes and Re-entry" skills/` → 0 hits. The rename consolidated under `planning-workflow §Changing Plans` is complete.
- `grep -rn "Changing Plans" skills/` → the new `planning-workflow` section plus retargeted pointers from `execution-workflow`, `integration-workflow`, `plan-anatomy.md`, `main-agent.md`, `using-superRA/SKILL.md`, and `handoff-doc/SKILL.md`.
- `grep -rn "session-bootstrap.md\|main-agent-autonomy.md" skills/` → 0 hits. The two deleted files have no lingering references.
- `ls skills/using-superRA/references/` → `main-agent.md` only.
- `execution-workflow` Step 1 sub-step 2a is three sentences that cleanly name both triggers.
- [`tests/structural-invariants.sh`](../../tests/structural-invariants.sh) passes (0 FAIL) against the post-re-entry tree.
- Behavior-based self-test: the `PLAN.md` on this branch is itself the first end-to-end use of the new mechanism. `## Workflow Status` is a rollup over per-task fields; the 2026-04-17 re-entry unchecked `Execution complete`, `Refactored`, `Docs finalized` and declared which tasks to re-work; the 2026-04-18 re-entry added the iterative-framing additions as an inline extension. The mechanism is self-applicable.

## Limitations

- **Vertical-coverage gap.** `planning-workflow` Phase 1's domain routing table has no entry for "skill editing" or "plugin development." This PR's work fell in that gap — it proceeded without a domain skill, using `CLAUDE.md`'s Design Principles section in the role a domain skill normally plays. The gap is flagged here, not closed; a future vertical for skill-editing is on the roadmap.
- **Verification is behavior-based, not numeric.** This PR ships only skill-file edits — no data pipeline, no figures, no numerical results. Per `CLAUDE.md §Skill Changes`, verification is running the skill through a realistic session and confirming triggering. The `PLAN.md` on this branch serves as that realistic session; further behavioral testing happens in follow-on PRs that exercise re-entry on other branches.

## Reproducibility

Reproduce via inspection at commit `8ad4b9f` (pre-consolidation integration APPROVED) or at the matured-docs commit range following it. All changes are static text edits to skills and top-level docs; no build or data step is involved.
