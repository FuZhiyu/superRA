---
title: "Build the Dashboard Companion-File Data Path"
status: not-started
depends_on:
  - 01-artifact-contract
---

## Objective

Give the dashboard a secure, worktree-aware data path for task companions under `attachments/`.

- Discover `attachments/` recursively while treating the directory as opaque to task discovery, even if it contains a file named `task.md`. Preserve relative paths at arbitrary depth, skip hidden path components and symlinks, and bound listing and preview work by file-count and byte budgets rather than an artificial depth limit. Exclude direct non-`task.md` files from the companion manifest.
- Add a task-scoped companion-file manifest and content/download API using query parameters rather than new catch-all routes. Resolve every request from the selected worktree and owning task; reject absolute paths, traversal, hidden components, symlink escapes, and reads outside the workspace, and serve unsafe types as downloads with `nosniff`.
- Extend the watcher so artifact add/modify/delete events refresh only the owning task's artifact state. Preserve active-task, expanded-tree, scroll, and worktree state rather than issuing a global reload.
- Extend standalone subtree export with the companion-file manifest plus Markdown and notebook source. Embed preview/download bytes only within documented per-file and total budgets; identify omitted files explicitly and use the existing commit-pinned repository fallback when available.
- Preserve rootless forests, custom `--root`, subtree rebasing, collision-safe worktree selectors, and existing figure embedding. Do not broaden the project-wide `/files` route into an artifact browser.
- Add focused regressions for direct-file classification versus subtask ownership, deeply nested attachments, hidden/checkpoint exclusion, file-count and byte budgets, traversal and symlink attacks, MIME headers, worktree isolation, add/modify/delete events, custom/rootless roots, scoped export, size fallback, and byte-accurate downloads; run the full task-tree script suite.

## Planner Guidance

Current task discovery is already based on directories containing `task.md`, task moves already carry all files, and Markdown link rewriting already scans all `.md` files. Reuse those ownership seams rather than adding artifact metadata to the `Task` frontmatter.

Centralize attachment resolution so listing, serving, watching, search/export preparation, and standalone image reads share the same ownership and containment rules. Relevant seams are [plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py), [_task_io.py](../../../../skills/task-tree/scripts/_task_io.py), [_worktree_discovery.py](../../../../skills/task-tree/scripts/_worktree_discovery.py), [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py), and [test_state_preservation.py](../../../../skills/task-tree/scripts/tests/test_state_preservation.py).

Notebook rendering is read-only and does not create filesystem entries. Exclude `.ipynb_checkpoints` and similar hidden tool state; attachment recursion exists for outputs created by separately executed code or tools, not because viewing an `.ipynb` requires companion directories.

## Revision Notes

The storage contract now has one boundary: `attachments/`. Remove the direct/attachment placement taxonomy while preserving the approved containment, watcher, export, rollback, and resource-limit guarantees.

## Results

Implemented one bounded companion-file data layer for the dashboard. The [manifest builder](../../../../skills/task-tree/scripts/_artifacts.py#L272-L362) classifies supported direct sources, recursive attachments, and unexpected direct files while excluding hidden/cache state, symlinks, and the required root `superra` wrapper. Its resolver and no-follow reader enforce owning-task and task-root containment, reject absolute/traversal/reserved paths and symlink components, and apply the documented 512-file, 256 KiB manifest, 4,096-entry traversal, 2 MiB preview, 2 MiB standalone-file, and 20 MiB standalone-total defaults. Listing itself is bounded: the [scanner](../../../../skills/task-tree/scripts/_artifacts.py#L88-L110) stops before materializing more than the traversal budget, and attachment recursion charges both files and directories.

The structural exception is centralized in [_task_io.py](../../../../skills/task-tree/scripts/_task_io.py#L28-L97): child enumeration, task parsing, task-path resolution, validation, sibling/dependency reads, command mutators, dashboard rebuilds, hooks, root discovery, and both migration passes share the rule that `attachments/` is opaque. Structural scans reject symlink task directories and symlink `task.md` files before reading them. The [task-path resolver](../../../../skills/task-tree/scripts/_task_io.py#L1032-L1070) rejects every task-relative symlink component, then rechecks containment and `attachments/` against the canonical resolved path before returning a location to any mutator. A retained `attachments/**/task.md` can be listed as an artifact but cannot become a task, dependency target, move/update target, hook reconciliation target, migration input, or alias-based write destination.

Task moves now enforce the same boundary for Markdown maintenance. The [link-rewrite scanner and no-follow file opener](../../../../skills/task-tree/scripts/_task_io.py#L618-L826) exclude symlinked Markdown files and symlinked directory components from both the moved-subtree and tree-wide passes. The [shared rewrite transaction](../../../../skills/task-tree/scripts/_task_io.py#L829-L880) snapshots every original byte sequence, opens the complete regular, contained queue before mutation, and includes descriptor finalization in its success boundary. A write failure restores touched descriptors; a close failure still closes every remaining descriptor, restores every path through fresh no-follow descriptors, and retries failed closes before reporting the error to directory rollback. The [cross-parent preflight](../../../../skills/task-tree/scripts/task_rename.py#L58-L80) validates source and destination structural ancestor chains before mutation, while the [move boundary](../../../../skills/task-tree/scripts/task_rename.py#L156-L209) rejects a symlinked source `task.md` and restores the source path after any rewrite failure. The post-move hook uses the same transactional writer.

The dashboard exposes query-parameter manifest and content/download APIs resolved from the request's selected worktree. Safe previews use byte-bounded no-follow reads; unsafe types and explicit downloads use attachment disposition, and artifact responses carry `X-Content-Type-Options: nosniff`. Add, modify, and delete events emit only the owning task's artifact manifest event, without task-tree rebuilds or global reloads.

Standalone whole-tree and subtree exports use the same resolver to pack scoped manifests and source/download bytes. Each entry records embedded, figure-reused, per-file-omitted, total-budget-omitted, or unreadable state; commit-pinned repository URLs are included when supplied. Figure reuse is now gated by the [actual embedded image map](../../../../skills/task-tree/scripts/plan_dashboard.py#L1917-L1949), so unsupported or unreadable image references fall back to ordinary bounded artifact packing instead of losing their bytes.

Focused regressions cover [external task symlinks and atomic alias rejection](../../../../skills/task-tree/scripts/tests/test_artifacts.py#L183-L245), [move preflight and external Markdown containment](../../../../skills/task-tree/scripts/test_task_tree.py#L929-L1123), [read-only and injected later-write rollback](../../../../skills/task-tree/scripts/test_task_tree.py#L1125-L1177), [descriptor-close rollback and close order](../../../../skills/task-tree/scripts/test_task_tree.py#L1179-L1216), structural opacity and traversal budgets, path security and live APIs, artifact-scoped watcher events, a sixteen-level manifest/content/watcher/export round trip, and standalone image-map fallbacks. The contributor-facing [dashboard internals](../../../../skills/task-tree/references/internals.md#companion-file-data-path) document the shared invariant, API, and ceilings.

Verification:

- Focused artifact suite: 25 passed.
- Focused move, rename, and hook suite: 22 passed.
- Combined task-tree and artifact regression suite: 308 passed.
- Full task-tree script suite: 765 passed with four expected warnings from dependency deprecations and intentional malformed-task fixtures.
- Python compilation, focused Ruff syntax checks, repository harness-compatibility validation, Markdown integrity checks, and `git diff --check` passed.
