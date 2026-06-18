---
title: "worktree-data-sync"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

You get the non-git-controlled files kept in sync when you run tasks in parallel across several git worktrees. The code is versioned and travels with each worktree, but the data usually is not — a new worktree starts empty, and parallel runs leave each one's data files out of step.

The skill works in three modes:

- **seed** a fresh worktree with the data it needs, copying or symlinking only the files that are missing and never overwriting what is already there;
- **diff** two worktrees, reporting which data files are new or modified between them;
- **apply** selected changes from one worktree into another to reconcile after parallel work — either overwriting in place, or copying alongside with a suffix so neither version is lost.

It figures out which files count as data on its own — gitignored paths and symlinks that point outside the repo — so you don't enumerate them, and there is no separate cleanup step: deleting a worktree removes its seeded data while the source is left untouched. The exact CLI, flags, and the symlink-versus-copy controls are in [`worktree-data-sync`](skills/worktree-data-sync/SKILL.md), which reads as a usable command reference.
