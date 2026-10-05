---
title: "refactor-and-integrate"
status: not-started
depends_on:  []
---

## Objective

`refactor-and-integrate` reworks a correct-but-rough branch so it reads like the rest of your project — code, prose, notes, or slides — and lands as a diff a reviewer can read.

## What it fixes

- **Convention drift:** reuses your existing helpers and names (`ret_winsor`, not a new `ret_w`).
- **Stale docs:** fixes any `README.md`, `CLAUDE.md`, or `AGENTS.md` above a changed file that the diff contradicts.
- **Diff noise:** prunes to the **minimum net diff**, the smallest change that supports the results.

It prunes form, not method: different controls, sample filters, or normalizations go to you as research decisions.

## How you use it

- **In INTEGRATE:** the [Integrate stage](#/04-workflows/03-integrate) runs it. You review one refactoring task listing the pruning; agents then execute it.
- **Standalone:** ask in plain language. It reverts clear junk and flags changes it cannot judge.
  - "prune this branch to minimum net diff against main and make it codebase-coherent before I open the PR"
  - "this branch works but it's a mess — reuse our existing helpers, match naming conventions, and fix any docs the diff contradicts"

Procedure and checklist: [refactor-and-integrate](skills/refactor-and-integrate/SKILL.md).
