---
title: "Dual-Use Dashboard Features for Doc Rendering"
status: not-started
depends_on: []
tags: []
created: 2026-06-10
---

## Objective

Extend the task-tree dashboard and its standalone export with the three features the docs site needs — doc-mode rendering, client-side search, and code syntax highlighting — each implemented as a generally useful dashboard feature, not a docs-only fork. Children own one feature each.

Shared constraints binding on every child:

- Additive and flag-gated where behavior changes: default `serve`/`generate` output is unchanged unless the new flag/feature is engaged (search and highlighting may appear by default since they add capability without removing anything; doc-mode is strictly opt-in).
- Existing tests under `skills/task-tree/scripts/` keep passing; each child adds tests for its own behavior.
- Standalone exports stay fully self-contained — no CDN or network fetch at runtime; new vendored assets follow `skills/task-tree/scripts/vendor/README.md` conventions (hand-managed, re-fetchable, documented).
- Features work in **both** the live server and the standalone export, and are verified by opening the produced artifact (rendered DOM), not only by route-level tests.

### Context

These features land in `skills/task-tree/scripts/` — the same surface as the existing dashboard work under the `task-tree/dashboard` workstream. They are placed here because they ship with, and are motivated by, the docs site; their durable home for future maintenance remains the task-tree skill's scripts.

**Open placement decision (researcher review pending):** durable-home policy would put these three tasks under `task-tree/dashboard`; they sit here to keep the docs workstream self-contained on this branch. The researcher confirms the placement — or a fold-into-`task-tree/dashboard` disposition at integration — at plan review; record the outcome here.
