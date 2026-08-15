---
title: "Agent Cross-Checkout Isolation: a Session Outside This Repo Committed Into It"
status: not-started
depends_on:  []
---

## Objective

Diagnose and close the path by which an agent session running with its cwd outside this repo reached this checkout's task tree, wrote a task's `## Results`, and committed the working tree's in-flight diff.

- Observed during v0.4 `workflow-defaults` validation on 2026-08-02: a live Claude Agent-SDK trace session whose cwd was a scratch two-task repo under /tmp resolved *this* checkout, wrote its own `## Results` into `superRA/v04-lean-workflow/workflow-defaults/task.md`, and committed the in-flight implementer diff as `7014a366`. The implementer recovered with `git reset --soft` and re-committed as `0b39cd7e`; nothing was lost, and `7014a366` is no longer reachable.
- The escaped session's Results also asserted a test count ("105 passed") for a suite that reports 126, so an escaped writer can land plausible-looking false evidence in a task file.
- Mechanism is undiagnosed. The task-tree CLI auto-detects its root (`--root` defaults to auto-detect preferring `superRA`), and the scratch repo had its own tree, so wrapper root-resolution is a hypothesis rather than a finding — reproduce before fixing.
- Deliverable: the reproduction, the identified path, and the fix or guard that prevents a session from mutating a checkout it was not pointed at. A guard that makes the escape loud (refuse, or warn on a task root outside cwd's repo) is acceptable if the root cause sits outside this repo's control.
- Until this closes, live agent-SDK traces against a fixture are unsafe to run from a dirty working tree of this repo.
- Once the guard is in place, run the two v0.4 traces the escape blocked: `workflow-defaults` trace 2 (a broad frontier produces a subagent-mode recommendation) and trace 3 (a completed high-stakes task produces a review recommendation naming tier and focuses). They are that task's acceptance bar, recorded there as validation debt; this task carries them because it owns the blocker.

## Details

- Evidence: this session's git history around `0b39cd7e`, and the `## Results` / `### Validation` section of `v04-lean-workflow/workflow-defaults`, which records the escape and why trace 2 was invalidated.
- Root resolution lives in `skills/task-tree/scripts/cli.py` and `lib/paths.py`; the wrapper's source-resolution chain is single-sourced in `skills/task-tree/scripts/wrapper_resolver.py`.
- Scope is isolation, not the tracing harness — the v0.4 validation gap it caused is recorded in `workflow-defaults`, not here.

## Results

