---
title: "INTEGRATE: Protect, Sync, and Ship"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

The tasks are approved, so the work is correct, but correct work can still break when it lands on a shared base. INTEGRATE folds the work into your codebase so the results stay reproducible and coherent over time, then ships it. Say `superintegrate` to enter the phase.

It is a separate phase rather than a final `git commit` because each step addresses a different way work degrades after it is approved:

1. **Protect** — pin the key results with small automated checks, so a later refactor that moves a number you care about fails loudly instead of slipping through silently.
2. **Sync** — fold in your base branch by intent, reading what each incoming change means rather than resolving conflicts line by line — never a bare `git merge`.
3. **Refactor** — fit the work to your codebase with a minimal, reviewable diff instead of a pile of single-shot scripts.
4. **Document** — mature the task findings into documentation a future reader can follow.
5. **Finish** — ship by PR or fast-forward, then clean up.

The key decisions stay with you. superRA runs the steps and surfaces the choices that belong to you: which results are the key ones to protect, which branch to sync against, an intent-changing conflict it will not resolve silently, and meaningful drift it sees after a sync or refactor. It stops and asks at those points rather than guessing. The full phase is owned by [superintegrate](skills/superintegrate/SKILL.md).

### When can I skip INTEGRATE?

For a throwaway branch or a personal experiment that will never merge, you can stop after IMPLEMENT. INTEGRATE is what you run before landing work on a shared base — it protects the key results, syncs against the current base, and matures the documentation, all of which matter once the work has to live alongside everyone else's.

