---
title: "semantic-merge"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

You sync a feature branch to main with `git merge main` (or `rebase`, or `cherry-pick`), resolve the conflicts the usual way, and commit once the build is green. A green build only proves no markers remain. It does not prove the sample filter you deliberately tightened on your branch is still tightened, or that the coefficient your branch protects still holds — a line-by-line resolution silently reverts exactly those when main touched the same region for an unrelated reason, and the regression surfaces weeks later as a table number that no longer matches its code. The same blindness leaves stale references behind: a variable renamed on one side still used under its old name on the other, a moved import path, a doc paragraph describing behavior the merge removed.

`semantic-merge` resolves by what each side *meant* instead of which lines arrived last. It reconstructs each side's intent from commit messages, diffs, and task context, synthesizes compatible changes so both survive, regenerates figures and tables the merge made stale, sweeps for stale references, and keeps your drift tests green. Anything that would change a data contract, a test expectation, or the meaning of a published result is escalated to you with the consequence stated, never resolved on the agent's own authority.

Reach for it any time you would otherwise type a bare merge, rebase, or cherry-pick — naming the operation and the incoming ref: "sync this branch with main using semantic-merge", "rebase onto main, resolve conflicts by intent", "cherry-pick abc123 into this branch semantically". It infers the branch, merge base, and direction from the session and asks only when the direction is ambiguous or a resolution would change what the branch means. A dirty worktree is stashed reversibly, not clobbered, and a merge-guard hook flags a bare `git merge` and points you here. A trivial fast-forward with no overlap needs none of this; a plain `git merge` is fine.

For the modes, escalation rules, and the full Semantic Coherence Checklist — including the parallel-worktree exception — see [`semantic-merge`](skills/semantic-merge/SKILL.md).
