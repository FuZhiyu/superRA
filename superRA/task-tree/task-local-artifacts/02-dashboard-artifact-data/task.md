---
title: "Build the Dashboard Companion-File Data Path"
status: revise
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

Implemented one bounded companion-file data layer for the dashboard. The [manifest builder](../../../../skills/task-tree/scripts/_artifacts.py#L272-L362) classifies supported direct sources, recursive attachments, and unexpected legacy direct files while excluding hidden/cache state and symlinks. Its resolver and no-follow reader enforce owning-task and task-root containment, reject absolute/traversal/reserved paths and symlink components, and apply the documented 512-file, 256 KiB manifest, 4,096-entry traversal, 2 MiB preview, 2 MiB standalone-file, and 20 MiB standalone-total defaults. Listing itself is bounded: the [scanner](../../../../skills/task-tree/scripts/_artifacts.py#L88-L110) stops before materializing more than the traversal budget, and attachment recursion charges both files and directories.

The structural exception is centralized in [_task_io.py](../../../../skills/task-tree/scripts/_task_io.py#L28-L68): child enumeration, task parsing, task-path resolution, validation, sibling/dependency reads, command mutators, dashboard rebuilds, hooks, root discovery, and both migration passes now share the rule that `attachments/` is opaque. A retained `attachments/**/task.md` can be listed as an artifact but cannot become a task, dependency target, move/update target, hook reconciliation target, or migration input.

The dashboard exposes query-parameter manifest and content/download APIs resolved from the request's selected worktree. Safe previews use byte-bounded no-follow reads; unsafe types and explicit downloads use attachment disposition, and artifact responses carry `X-Content-Type-Options: nosniff`. Add, modify, and delete events emit only the owning task's artifact manifest event, without task-tree rebuilds or global reloads.

Standalone whole-tree and subtree exports use the same resolver to pack scoped manifests and source/download bytes. Each entry records embedded, figure-reused, per-file-omitted, total-budget-omitted, or unreadable state; commit-pinned repository URLs are included when supplied. Figure reuse is now gated by the [actual embedded image map](../../../../skills/task-tree/scripts/plan_dashboard.py#L1917-L1949), so unsupported or unreadable image references fall back to ordinary bounded artifact packing instead of losing their bytes.

Focused regressions cover [structural opacity and traversal budgets](../../../../skills/task-tree/scripts/tests/test_artifacts.py#L155-L255), path security and live APIs, artifact-scoped watcher events, [a sixteen-level manifest/content/watcher/export round trip](../../../../skills/task-tree/scripts/tests/test_artifacts.py#L432-L484), and [standalone image-map fallbacks](../../../../skills/task-tree/scripts/tests/test_artifacts.py#L577-L617). The contributor-facing [dashboard internals](../../../../skills/task-tree/references/internals.md#companion-file-data-path) document the shared invariant, API, and ceilings.

Verification:

- Focused artifact suite: 23 passed.
- Combined task-tree and artifact regression suite: 297 passed with two expected intentional-fixture warnings.
- Dashboard, multi-worktree, state-preservation, and artifact suite: 377 passed with two dependency deprecation warnings.
- Full task-tree script suite: 754 passed with four expected warnings from dependency deprecations and intentional malformed-task fixtures.
- Python compilation, focused `_artifacts.py` Ruff import/error checks, repository harness-compatibility validation, Markdown integrity checks, and `git diff --check` passed.

## Review Notes

1. **CRITICAL** — The shared structural helpers still let symlinks bypass the opaque-task invariant. [`iter_child_task_dirs`](../../../../skills/task-tree/scripts/_task_io.py#L37-L52) follows a symlinked directory through `Path.is_dir()`, so [`iter_task_markdown_files`](../../../../skills/task-tree/scripts/_task_io.py#L57-L68) can now hand an external `task.md` to both migration writers ([`upgrade_v1_to_v2`](../../../../skills/task-tree/scripts/plan_migrate.py#L399-L417), [`upgrade_status`](../../../../skills/task-tree/scripts/plan_migrate.py#L442-L456)). Separately, [`resolve_path`](../../../../skills/task-tree/scripts/_task_io.py#L773-L796) checks `attachments` only in the lexical request before resolving it: with `alias -> attachments`, [`create_task`](../../../../skills/task-tree/scripts/task_create.py#L52-L107) writes `attachments/new-task/task.md` and only then fails during parent propagation, leaving a partial mutation inside the opaque container. Reject symlink task directories and path components, enforce opacity on the resolved task-root-relative path before any write, and add regressions for an external symlinked task during migration and a symlink alias into `attachments/` during mutation.
   → implemented: centralized structural child, opaque-path, and migration iteration in [_task_io.py](../../../../skills/task-tree/scripts/_task_io.py#L28-L68), routed every cited scanner/mutator/hook through it, and added the cross-surface regression in [test_artifacts.py](../../../../skills/task-tree/scripts/tests/test_artifacts.py#L183-L255).
