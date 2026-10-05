---
title: "semantic-merge"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

`semantic-merge` runs a merge, rebase, or cherry-pick by what each side *meant*, not by which lines arrived last. A line-by-line resolution can silently revert a sample filter you tightened, and a conflict-free merge can still leave a renamed variable, moved path, or outdated doc behind.

## Ask for it instead of a bare merge

Name the operation and the incoming ref:

- "sync this branch with main using semantic-merge"
- "rebase onto main, resolve conflicts by intent"
- "cherry-pick abc123 into this branch semantically"

In INTEGRATE, the [Sync stage](#/05-workflows/03-integrate) runs it for you. An agent that types a bare `git merge` gets a reminder from the [merge-guard hook](#/06-hooks).

## What you see

- **A question only when a resolution changes meaning:** the sides want different things, or the choice moves a sample filter, data contract, test expectation, or published result. The agent states the consequence, not raw diff chunks.
- **A merge commit plus follow-up commits** that regenerate stale figures and tables and fix stale references. Commit bodies record what was kept, dropped, or combined, and your decisions.
- **Tests and drift tests passing on every commit.** A moved result comes to you; it is never re-expected silently.
- **A named stash** holding any unrelated uncommitted changes, reported so you can restore them.

Modes, escalation rules, and the checklist live in [semantic-merge](skills/semantic-merge/SKILL.md).
