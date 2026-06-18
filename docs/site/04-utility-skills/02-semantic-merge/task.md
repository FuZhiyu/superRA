---
title: "semantic-merge"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

You get conflict resolution that turns on what each side *meant* rather than which lines won. Reach for it when you sync your branch with main, rebase, or cherry-pick and `git` drops conflict markers into a dozen files — resolving them by hand, picking ours or theirs line by line, is how a careful change quietly gets reverted.

`semantic-merge` reads the intent behind both changes, synthesizes where both are valid, escalates to you when a resolution would change what the branch means, and sweeps for references that went stale across the merge — so what lands is coherent, not just free of markers. See [`semantic-merge`](skills/semantic-merge/SKILL.md).
