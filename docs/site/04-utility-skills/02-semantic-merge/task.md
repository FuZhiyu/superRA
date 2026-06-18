---
title: "semantic-merge"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

You finish a two-week feature branch, switch back to it after main has moved, and run `git merge main` (or `git rebase main`, or `git cherry-pick <sha>`). Git reports conflicts in eight files and you resolve them the usual way: read the markers, decide ours-or-theirs per hunk, delete the markers, commit once the build is green. A green build only proves no markers remain. It does not prove that the sample filter you deliberately tightened on your branch is still tightened, or that the regression coefficient your branch was built to protect still holds — and a line-by-line resolution silently reverts exactly those when main touched the same region for an unrelated reason. The merge completes clean, and the regression surfaces weeks later when a number in a table no longer matches the code that supposedly produced it. The same blindness leaves stale references behind: a variable renamed on one side stays referenced under its old name on the other, a moved module path still imports from its old location, a doc paragraph still describes behavior the merge removed.

`semantic-merge` resolves by what each side meant. Before running the operation it grounds in repository state — current branch, worktree status, merge base, incoming range, touched files — then reads commit messages, diffs, and any task or handoff context to reconstruct what each side was trying to do, and resolves by that intent rather than by which lines arrived last.

The mechanism is per-cluster classification, not one global ours-or-theirs choice. Each overlapping region is sorted by role — behavior/API, data/schema, docs/narrative, generated outputs, tests, config/build — and the role sets the resolution rule. Two compatible behavior changes get synthesized so both survive rather than one picked over the other. Figures and tables made stale by the merge get regenerated from the merged sources rather than hand-patched. Anything that would change a data contract, a test expectation, a program output, or the meaning of a published result is escalated to you with the intent and consequence stated, never resolved on the agent's own authority. The agent executes your decision; it does not make the intent-changing call for you.

Two checks run that a bare merge has no concept of. A stale-reference sweep looks past "no conflict markers" for the second-order breakage a merge creates: an identifier or label renamed on one side and still used on the other, a path moved on one side, a doc or comment describing the old shape, a dangling import or config key. And every commit it lands must leave your existing tests and drift tests green — the result-protection coverage that pins your key outputs stays passing, or the change is escalated rather than silently re-expected. What lands is one merge commit plus any propagation commits needed to make the tree coherent, with the resolution and any decisions you approved recorded in the commit bodies (and, standalone with no task tree, the merge record). The full done-condition is the §Semantic Coherence Checklist of `[BLOCKING]` items.

Reach for it any time you would otherwise type a bare merge, rebase, or cherry-pick, or whenever you sync a feature branch to its base before integration. Invoke it by naming the operation and the incoming ref: "sync this branch with main using semantic-merge", "rebase onto main, resolve conflicts by intent", "cherry-pick abc123 into this branch semantically". It infers current branch, merge base, and direction from the session, and asks only when the direction is genuinely ambiguous or when a resolution would change what the branch means. A dirty worktree with unrelated edits is stashed reversibly and reported back, not clobbered. The merge-guard hook backstops all of this: a bare `git merge` is flagged and points you here, so you do not have to remember. For a trivial fast-forward with no overlap a plain `git merge` is fine; the value shows up the moment two sides touch the same region for different reasons.

One exception: orchestrator-managed parallel worktrees — agent fan-out branches with no competing intent to reconcile — merge with a plain `git merge --no-ff`, and the hook exempts source refs matching `*/parallel/*`.

For the full mode list (standalone versus the `superintegrate`-driven sync author and reviewer), the shared steps, the escalation rules, and the complete Semantic Coherence Checklist, see [`semantic-merge`](skills/semantic-merge/SKILL.md).
