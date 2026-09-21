---
title: "Agent Cross-Checkout Isolation: a Session Outside This Repo Committed Into It"
status: revise
depends_on:  []
---

## Objective

Diagnose and close the path by which an agent session running with its cwd outside this repo reached this checkout's task tree, wrote a task's `## Results`, and committed the working tree's in-flight diff.

- Observed during v0.4 `workflow-defaults` validation on 2026-08-02: a live Claude Agent-SDK trace session whose cwd was a scratch two-task repo under /tmp resolved *this* checkout, wrote its own `## Results` into `superRA/v04-lean-workflow/workflow-defaults/task.md`, and committed the in-flight implementer diff as `7014a366`. The implementer recovered with `git reset --soft` and re-committed as `0b39cd7e`; nothing was lost, and `7014a366` is no longer reachable.
- The escaped session's Results also asserted a test count ("105 passed") for a suite that reports 126, so an escaped writer can land plausible-looking false evidence in a task file.
- Mechanism is undiagnosed. The task-tree CLI auto-detects its root (`--root` defaults to auto-detect preferring `superRA`), and the scratch repo had its own tree, so wrapper root-resolution is a hypothesis rather than a finding — reproduce before fixing.
- Deliverable: the reproduction, the identified path, and the fix or guard that prevents a session from mutating a checkout it was not pointed at. A guard that makes the escape loud (refuse, or warn on a task root outside cwd's repo) is acceptable if the root cause sits outside this repo's control.
- The session anchor is `CLAUDE_PROJECT_DIR` where the harness sets it, else the payload `cwd`. The researcher accepts the Claude-specific name in the shared `_checkout_scope.py`: protection against a session whose cwd drifted into another checkout holds on Claude Code only, and the other harnesses get the payload-`cwd` rule.
- Until this closes, live agent-SDK traces against a fixture are unsafe to run from a dirty working tree of this repo.
- Once the guard is in place, run the two v0.4 traces the escape blocked: `workflow-defaults` trace 2 (a broad frontier produces a subagent-mode recommendation) and trace 3 (a completed high-stakes task produces a review recommendation naming tier and focuses). They are that task's acceptance bar, recorded there as validation debt; this task carries them because it owns the blocker.

## Details

- Evidence: this session's git history around `0b39cd7e`, and the `## Results` / `### Validation` section of `v04-lean-workflow/workflow-defaults`, which records the escape and why trace 2 was invalidated.
- Root resolution lives in `skills/task-tree/scripts/cli.py` and `lib/paths.py`; the wrapper's source-resolution chain is single-sourced in `skills/task-tree/scripts/wrapper_resolver.py`.
- Scope is isolation, not the tracing harness — the v0.4 validation gap it caused is recorded in `workflow-defaults`, not here.

## Results

No task-tree code path escapes its cwd — the escape was an unguarded agent action, and superRA had no guard that could see it. The new `guard-foreign-checkout` PreToolUse gate now stops it, asking for approval rather than refusing outright so cross-checkout work a researcher set up on purpose still has a route through.

### The root-resolution hypothesis is wrong

Every root the tooling resolves is anchored on the process cwd, and auto-detection fails loudly rather than falling back:

- [`autodetect_plan_root`](../../../skills/task-tree/scripts/_task_io.py#L129) walks up from cwd only, and [cli.py](../../../skills/task-tree/scripts/cli.py#L104) exits with `Error: could not auto-detect task root. Use --root.` when the walk finds nothing. There is no fallback to the script's own location, so running the source checkout's wrapper from a foreign cwd resolves the foreign cwd's tree, not the checkout's.
- The wrapper's `SUPERRA_REPO_ROOT` export ([superRA/superra](../../../superRA/superra)) and `CLAUDE_PLUGIN_ROOT` select *which copy of the code* runs, never which tree it operates on.
- `task_hook.py` derives its plan root from the edited file's own path, so it reconciles whatever tree the write already landed in. That is what made the escape silent: the hook cheerfully validated and rolled up the foreign tree.

What put the source checkout in the traced session's reach is [sdk_load_harness.py](../../../tests/harness-instruction-following/sdk_load_harness.py#L263): the session gets `plugins=[{"type": "local", "path": REPO_ROOT}]` (so every skill it reads carries this checkout's absolute paths), `permission_mode="acceptEdits"`, and `allowed_tools` containing an unrestricted `Bash`. Nothing in that configuration ties writes to `cwd`, so an agent that conflated "the task tree in this repo" with the checkout whose skills it was reading could write `superRA/v04-lean-workflow/workflow-defaults/task.md` by absolute path and `cd` there to commit.

### The guard stops both halves of the escape

[hooks/checkout_isolation_gate.py](../../../hooks/checkout_isolation_gate.py), wired as `guard-foreign-checkout` in all three harness manifests, stops:

- an `Edit`/`Write`/`apply_patch` on a `task.md` whose task root is in neither the session's cwd nor its repository — the write that lands false evidence such as the escape's "105 passed";
- a git history-writing `Bash` command pointed at another *task-tree* checkout by `cd`, `git -C`, or `--git-dir`/`--work-tree` — the commit that swept up the in-flight diff. The `cd` boundary admits every opener a shell segment can start with, so the subshell, brace-group, and `bash -c "…"` forms are caught alongside the plain `&&` chain.

The decision is `ask`, not `deny`: a researcher who deliberately pointed a session at a second repository approves and proceeds, while an unattended session stops. Membership is the git common dir, so sibling worktrees of the session's own repository never prompt; that is where superRA dispatches implementers, and a rule based on cwd containment or repo toplevel would have prompted on every worktree dispatch. The session anchor is `CLAUDE_PROJECT_DIR` when the harness sets it, since a `cd` earlier in the session can move the payload `cwd` into the foreign checkout. Git commands in a foreign repo that holds no task tree are left alone — cross-repo git is the researcher's business; a commit into another task-tree checkout is the escape. The gate fails open wherever identity is unresolvable.

`deny_reason()` is the whole decision, and the trace harness registers it as a third in-process `PreToolUse` hook ([`confinement_hook`](../../../tests/harness-instruction-following/sdk_load_harness.py#L167)) that hard-denies on it, since a traced session has no approver.

### The reproduction runs in CI, with no credentials

[tests/hooks/test-guard-foreign-checkout.sh](../../../tests/hooks/test-guard-foreign-checkout.sh) builds two disposable git checkouts under `mktemp` and replays the escape end to end: a session pointed at one checkout writes `## Results` into the other's `task.md` and commits that checkout's uncommitted `in-flight.txt`. Part 1 asserts the pre-existing surfaces all accept it — `guard-task-approval` allows the foreign write and `task_hook.py` reconciles the foreign tree with no complaint — which is why the escape was visible only in `git log`. Parts 2 and 3 assert the gate stops both mutations — through the `cd` chain, subshell, brace group, `bash -c`, `git -C`, and `--git-dir`/`--work-tree` forms — and stays out of the way of a session's own tree, a sibling worktree including its subshell form, non-task files, foreign non-task-tree git, and read-only git. 24 checks, all passing. [test_trace_confinement.py](../../../tests/harness-instruction-following/test_trace_confinement.py) covers the harness callback with no SDK import and no model call.

### Boundaries

- **A `task.md` written through `Bash` is outside the gate.** A Python heredoc or `sed -i` that rewrites a foreign task file carries no `Edit`/`Write` payload and no git verb, so nothing fires. That route matters more than the count of `Edit` calls suggests — [edit-detection](../edit-detection/task.md) §Details is the task for edits arriving by tools other than `Edit`/`Write`, and closing this needs the same command-parsing surface it builds, not a second parser here.
- **A bare `git commit` after a `cd` in an *earlier* Bash call is not stopped**: the command carries no path token, and the payload's shell cwd is not observable. The `cd` that first enters the foreign checkout with a git verb does prompt, and `CLAUDE_PROJECT_DIR` keeps the anchor from drifting, so reaching this state takes a deliberate two-step.
- **Non-task files in a foreign checkout are writable.** Prompting on every foreign write would interrupt ordinary cross-repo work for a plugin installed user-wide; the gate stays scoped to task trees and their history.
- **`ask` degrades to allow on a runtime that does not honor it.** Codex and Cursor are wired but unverified on this decision value; a harness that ignores `ask` loses the guard rather than blocking, which is the safe direction for a hook that must never wedge a session.

### Still owed: the two v0.4 traces

`workflow-defaults` traces 2 and 3 are unblocked but not run. They need live model calls, and this session has no `ANTHROPIC_API_KEY` and no `~/.claude/.credentials.json` (`claude-agent-sdk` itself installs and imports fine). They also need new fixtures — a broad frontier, and a completed high-stakes task — plus graders for "recommends subagent mode" and "names tier and focuses", which is fixture work belonging to that task's acceptance bar. The blocker this task owned is closed: a traced session can no longer reach another checkout, from a dirty working tree or otherwise.

### Suite status

`tests/hooks/*.sh` pass except two that fail identically at `b2985c68` (`test-codex-hooks.sh` "Codex manifest command executes task PostToolUse hook", `test-codex-e2e-cli.sh` "missing hook evidence"). `tests/harness-instruction-following` is 128 passed / 1 failed, the failure (`test_bundle_fixture.py::test_task_read_json_carries_comments_and_dependency_status`, a `slug` shape mismatch) also reproducing at `b2985c68`. `check-harness-compatibility.sh` exits 0.

## Review Notes

Tier: thorough; narrow re-review. Focus: correctness. Reviewer: main agent. The four first-pass findings are confirmed fixed. Deferred by the orchestrator, pending the researcher's disposition:

1. `[BLOCKING]` **The objective's last bullet is unmet: the two v0.4 traces have not run.** `workflow-defaults` trace 2 and trace 3 need API credentials the implementer's session lacked, plus new fixtures and graders. The guard that blocked them is in place. The researcher decides whether the traces move back to [workflow-defaults](../../v04-lean-workflow/workflow-defaults/task.md) as its validation debt, letting this task close on the guard, or stay owed here.
