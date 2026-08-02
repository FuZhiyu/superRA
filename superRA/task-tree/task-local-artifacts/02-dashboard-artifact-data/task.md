---
title: "Build the Dashboard Companion-File Data Path"
status: approved
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

## Results

The dashboard data layer now exposes exactly one task-local storage boundary. The [recursive manifest builder](../../../../skills/task-tree/scripts/_artifacts.py#L221-L317) walks only the owning task's `attachments/` directory, preserves arbitrary-depth relative paths, excludes hidden/cache components and symlinks, retains file-count, manifest-byte, traversal-entry, and preview-byte ceilings, and no longer emits a direct/attachment placement field. Files beside `task.md` are absent from the manifest.

The [shared resolver and descriptor walker](../../../../skills/task-tree/scripts/_artifacts.py#L330-L479) require every requested path to begin with `attachments/`; direct files, absolute paths, traversal, hidden components, symlink components, non-files, cross-task paths, and workspace escapes remain rejected. Reads open the resolved task root once, walk every owning-task and attachment directory component with directory-relative `O_DIRECTORY | O_NOFOLLOW`, open and verify the final regular file with `O_NOFOLLOW`, and fail closed when the required descriptor operations are unavailable. That walk is now factored into a root-relative primitive, [`open_regular_file_nofollow`](../../../../skills/task-tree/scripts/_artifacts.py#L399-L452), which `open_artifact_file` calls with the task-scoped root and parts and which the standalone figure embedder (below) reuses directly for non-attachment paths — the same no-follow descriptor walk now guards both branches, closing the check-then-act gap the non-attachment branch previously had between a `Path.is_symlink()` check loop and a later `Path.read_bytes()`. Existing selected-worktree lookup, MIME classification, `nosniff`, inline/download disposition, preview limits, and byte-accurate reads remain in the query-parameter APIs. Preview and download responses [consume the same stable-handle path](../../../../skills/task-tree/scripts/plan_dashboard.py#L1433-L1482); downloads stream and close that descriptor instead of allowing `FileResponse` to reopen a mutable pathname.

Watcher ownership is likewise attachment-only: [direct changes return no artifact owner](../../../../skills/task-tree/scripts/_artifacts.py#L509-L544), while attachment add/modify/delete events still emit the owning task's manifest update without a global reload. Standalone whole-tree and rebased subtree export continues to use the same resolver and preserves scoped manifests, Markdown/notebook and download bytes, figure reuse, per-file and total omission reasons, and commit-pinned repository fallback. [Attachment-figure and non-attachment project-figure embedding](../../../../skills/task-tree/scripts/plan_dashboard.py#L1901-L1946) both read through the stable no-follow descriptor walker after resolution. The contributor-facing [dashboard internals](../../../../skills/task-tree/references/internals.md#L268) document the single boundary and request shape.

Focused regressions cover direct-file exclusion and access rejection, removal of placement metadata, recursive attachment ownership, hidden/checkpoint and symlink exclusion, listing and byte budgets, MIME and download headers, worktree/custom-root/rootless isolation, attachment-only watcher events, a sixteen-level manifest/content/watcher/export round trip, scoped export, size fallback, figure reuse, [intermediate-directory symlink swaps for explicit and unsafe implicit downloads](../../../../skills/task-tree/scripts/tests/test_artifacts.py#L448-L487), [the equivalent standalone attachment-figure race](../../../../skills/task-tree/scripts/tests/test_artifacts.py#L781-L819), and [the matching non-attachment project-figure race](../../../../skills/task-tree/scripts/tests/test_artifacts.py#L822-L857).

Verification: `test_artifacts.py` passed 30 tests, `test_dashboard.py` passed 296 tests, and the full task-tree script suite (`pytest .` from `skills/task-tree/scripts`) passed 742 tests, 0 failed.
