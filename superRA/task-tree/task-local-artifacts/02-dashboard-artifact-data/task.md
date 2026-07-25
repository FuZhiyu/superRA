---
title: "Build the Dashboard Artifact Data Path"
status: not-started
depends_on:
  - 01-artifact-contract
---

## Objective

Give the dashboard a secure, worktree-aware data path for the owning task's `attachments/` workspace.

- Treat `attachments/` as opaque to task discovery: neither it nor directories beneath it become tasks, even if they contain a file named `task.md`. Discover its non-hidden files recursively for an owning task while excluding caches, symlinks, reserved task metadata, and paths that enter another task.
- Add a task-scoped artifact manifest and content/download API using query parameters rather than new catch-all routes. Resolve every request from the selected worktree and owning task; reject absolute paths, traversal, hidden components, symlink escapes, and reads outside the workspace, and serve unsafe types as downloads with `nosniff`.
- Extend the watcher so artifact add/modify/delete events refresh only the owning task's artifact state. Preserve active-task, expanded-tree, scroll, and worktree state rather than issuing a global reload.
- Extend standalone subtree export with the artifact manifest and Markdown sidecar content. Embed preview/download bytes only within documented per-file and total budgets; identify omitted files explicitly and use the existing commit-pinned repository fallback when available.
- Preserve rootless forests, custom `--root`, subtree rebasing, collision-safe worktree selectors, and existing figure embedding. Do not broaden the project-wide `/files` route into an artifact browser.
- Add focused regressions for ownership boundaries, traversal and symlink attacks, MIME headers, worktree isolation, add/modify/delete events, custom/rootless roots, scoped export, size fallback, and byte-accurate downloads; run the full task-tree script suite.

## Planner Guidance

Current task discovery is already based on directories containing `task.md`, task moves already carry all files, and Markdown link rewriting already scans all `.md` files. Reuse those ownership seams rather than adding artifact metadata to the `Task` frontmatter.

The dashboard currently ignores watcher events for ordinary files, serves known project files through `/files`, and embeds only figures in standalone export. Centralize attachment resolution so listing, serving, watching, search/export preparation, and standalone image reads share the same containment rules. Relevant seams are [plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py), [_task_io.py](../../../../skills/task-tree/scripts/_task_io.py), [_worktree_discovery.py](../../../../skills/task-tree/scripts/_worktree_discovery.py), [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py), and [test_state_preservation.py](../../../../skills/task-tree/scripts/tests/test_state_preservation.py).

## Results
