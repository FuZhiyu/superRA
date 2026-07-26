---
title: "Build the Dashboard Companion-File Data Path"
status: implemented
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

The dashboard data layer now exposes exactly one task-local storage boundary. The [recursive manifest builder](../../../../skills/task-tree/scripts/_artifacts.py#L221-L317) walks only the owning task's `attachments/` directory, preserves arbitrary-depth relative paths, excludes hidden/cache components and symlinks, retains file-count, manifest-byte, traversal-entry, and preview-byte ceilings, and no longer emits a direct/attachment placement field. Files beside `task.md` are absent from the manifest.

The [shared resolver and descriptor helpers](../../../../skills/task-tree/scripts/_artifacts.py#L329-L425) require every requested path to begin with `attachments/`; direct files, absolute paths, traversal, hidden components, symlink components, non-files, cross-task paths, and workspace escapes remain rejected. Existing selected-worktree lookup, MIME classification, `nosniff`, inline/download disposition, preview limits, and byte-accurate no-follow reads remain in the query-parameter APIs. Download responses [open and verify a regular file with `O_NOFOLLOW` before returning](../../../../skills/task-tree/scripts/plan_dashboard.py#L1454-L1469), then stream and close that stable descriptor instead of allowing `FileResponse` to reopen a mutable pathname.

Watcher ownership is likewise attachment-only: [direct changes return no artifact owner](../../../../skills/task-tree/scripts/_artifacts.py#L405-L440), while attachment add/modify/delete events still emit the owning task's manifest update without a global reload. Standalone whole-tree and rebased subtree export continues to use the same resolver and preserves scoped manifests, Markdown/notebook and download bytes, figure reuse, per-file and total omission reasons, and commit-pinned repository fallback. The contributor-facing [dashboard internals](../../../../skills/task-tree/references/internals.md#L268) document the single boundary and request shape.

Focused regressions cover direct-file exclusion and access rejection, removal of placement metadata, recursive attachment ownership, hidden/checkpoint and symlink exclusion, listing and byte budgets, MIME and download headers, worktree/custom-root/rootless isolation, attachment-only watcher events, a sixteen-level manifest/content/watcher/export round trip, scoped export, size fallback, figure reuse, and [final-component symlink swaps for explicit and unsafe implicit downloads](../../../../skills/task-tree/scripts/tests/test_artifacts.py#L448-L485).

Verification: `test_artifacts.py` passed 27 tests. Python compilation, Markdown integrity checks, and `git diff --check` passed. The full task-tree suite is intentionally deferred to the combined task 02/03 verification pass.

## Review Notes

1. **MAJOR** — Explicit and download-only responses can still escape the owning task through a validation-to-open symlink race. [`artifact_content`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1405-L1459) validates and describes the path, but then hands the pathname to `FileResponse`, which reopens it later without the no-follow protection used by [`read_artifact_bytes`](../../../../skills/task-tree/scripts/_artifacts.py#L389-L402). In a focused reproduction, replacing `attachments/payload.bin` with a symlink to an out-of-workspace file inside a patched `describe_resolved` call made `GET /api/artifact?...&download=true` return `200` with the outside file's bytes. Keep the validated file identity through response streaming, or reopen through a no-follow descriptor and verify the opened regular file before streaming; add a regression that swaps the final component after resolution and proves both explicit downloads and unsafe-type implicit downloads cannot disclose outside bytes.
   → implemented: download responses now open a no-follow verified regular-file descriptor before returning and stream that stable identity; both swap paths return 403 without outside bytes ([plan_dashboard.py:1454-1469](../../../../skills/task-tree/scripts/plan_dashboard.py#L1454-L1469), [test_artifacts.py:448-485](../../../../skills/task-tree/scripts/tests/test_artifacts.py#L448-L485)).
