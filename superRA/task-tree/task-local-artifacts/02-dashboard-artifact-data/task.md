---
title: "Build the Dashboard Companion-File Data Path"
status: implemented
depends_on:
  - 01-artifact-contract
---

## Objective

Give the dashboard a secure, worktree-aware data path for direct companion files and retained content in `attachments/`.

- Discover first-class `.md`, `.py`, `.jl`, `.r`/`.R`, and `.ipynb` files beside `task.md`, excluding `task.md`, reserved metadata, hidden files, caches, and symlinks. Directories containing `task.md` remain subtasks and never enter the file manifest; safely identify unexpected direct files as legacy placement without endorsing it for new work.
- Discover `attachments/` recursively while treating the directory as opaque to task discovery, even if it contains a file named `task.md`. Preserve relative paths at arbitrary depth, skip hidden path components and symlinks, and bound listing and preview work by file-count and byte budgets rather than an artificial depth limit. Ignore every other ancillary directory.
- Add a task-scoped companion-file manifest and content/download API using query parameters rather than new catch-all routes. Resolve every request from the selected worktree and owning task; reject absolute paths, traversal, hidden components, symlink escapes, and reads outside the workspace, and serve unsafe types as downloads with `nosniff`.
- Extend the watcher so artifact add/modify/delete events refresh only the owning task's artifact state. Preserve active-task, expanded-tree, scroll, and worktree state rather than issuing a global reload.
- Extend standalone subtree export with the companion-file manifest plus Markdown and notebook source. Embed preview/download bytes only within documented per-file and total budgets; identify omitted files explicitly and use the existing commit-pinned repository fallback when available.
- Preserve rootless forests, custom `--root`, subtree rebasing, collision-safe worktree selectors, and existing figure embedding. Do not broaden the project-wide `/files` route into an artifact browser.
- Add focused regressions for direct-file classification versus subtask ownership, deeply nested attachments, hidden/checkpoint exclusion, file-count and byte budgets, traversal and symlink attacks, MIME headers, worktree isolation, add/modify/delete events, custom/rootless roots, scoped export, size fallback, and byte-accurate downloads; run the full task-tree script suite.

## Planner Guidance

Current task discovery is already based on directories containing `task.md`, task moves already carry all files, and Markdown link rewriting already scans all `.md` files. Reuse those ownership seams rather than adding artifact metadata to the `Task` frontmatter.

The dashboard currently ignores watcher events for ordinary files, serves known project files through `/files`, and embeds only figures in standalone export. Centralize companion-file resolution so listing, serving, watching, search/export preparation, and standalone image reads share the same ownership and containment rules. Relevant seams are [plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py), [_task_io.py](../../../../skills/task-tree/scripts/_task_io.py), [_worktree_discovery.py](../../../../skills/task-tree/scripts/_worktree_discovery.py), [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py), and [test_state_preservation.py](../../../../skills/task-tree/scripts/tests/test_state_preservation.py).

Notebook rendering is read-only and does not create filesystem entries. Exclude `.ipynb_checkpoints` and similar hidden tool state; attachment recursion exists for outputs created by separately executed code or tools, not because viewing an `.ipynb` requires companion directories.

## Results

Implemented one bounded companion-file data layer for the dashboard. The [manifest builder](../../../../skills/task-tree/scripts/_artifacts.py#L242-L319) classifies supported direct sources, recursive attachments, and unexpected legacy direct files while excluding hidden/cache state and symlinks. Its [resolver and bounded reader](../../../../skills/task-tree/scripts/_artifacts.py#L331-L411) enforce owning-task and task-root containment, reject absolute/traversal/reserved paths and symlink components, and apply the documented 512-file, 256 KiB manifest, 2 MiB preview, 2 MiB standalone-file, and 20 MiB standalone-total defaults. `attachments/` is also excluded at the [task-discovery seam](../../../../skills/task-tree/scripts/_task_io.py#L690-L713), so a nested `attachments/**/task.md` remains an artifact rather than a subtask.

The dashboard now exposes query-parameter [manifest and content/download APIs](../../../../skills/task-tree/scripts/plan_dashboard.py#L1363-L1450) resolved from the request's selected worktree. Safe previews use byte-bounded no-follow reads; unsafe types and explicit downloads use attachment disposition, and artifact responses carry `X-Content-Type-Options: nosniff`. Add, modify, and delete events emit only the owning task's [artifact manifest event](../../../../skills/task-tree/scripts/plan_dashboard.py#L379-L479), without task-tree rebuilds or global reloads.

Standalone whole-tree and subtree exports use the same resolver to [pack scoped manifests and source/download bytes](../../../../skills/task-tree/scripts/_artifacts.py#L455-L555). Each entry records embedded, figure-reused, per-file-omitted, total-budget-omitted, or unreadable state; commit-pinned repository URLs are included when supplied. Existing task-body figure data is reused rather than duplicated, and non-companion figure reads are confined to the project workspace. The contributor-facing [dashboard internals](../../../../skills/task-tree/references/internals.md#L268-L276) document the API, ceilings, and owning module.

Focused regressions cover [discovery and budgets](../../../../skills/task-tree/scripts/tests/test_artifacts.py#L58-L142), [path security and live APIs](../../../../skills/task-tree/scripts/tests/test_artifacts.py#L145-L282), [artifact-scoped watcher events](../../../../skills/task-tree/scripts/tests/test_artifacts.py#L285-L323), and [scoped/budgeted standalone exports](../../../../skills/task-tree/scripts/tests/test_artifacts.py#L326-L414).

Verification:

- Focused artifact and state-preservation tests: 47 passed.
- Dashboard compatibility suite: 308 passed.
- Full task-tree script suite: 750 passed with four expected warnings from dependency deprecations and intentional malformed-task fixtures.
- Python compilation, focused Ruff import/error checks, repository harness-compatibility validation, Markdown integrity checks, and `git diff --check` passed.
