---
title: "Dashboard Link Resolution — External Schemes + PDF Direct-Open"
status: implemented
depends_on: []
---

## Objective

Extend the dashboard's client-side link resolver (`renderMarkdown` in `skills/task-tree/scripts/templates/dashboard.js`) so a task/ledger body can carry the literature-review trace-link cluster — Zotero deeplink, web, PDF, markdown — as **relative paths and scheme URIs the dashboard resolves**, never machine-absolute paths. Today the resolver rewrites every non-`http`/non-`#` href to `vscode://file/…`, and the pre-render DOMPurify pass strips custom schemes, so a `zotero://` link is dropped and a PDF only ever opens in VSCode. Two targeted changes; nothing else about the resolver moves.

Scope all edits/commits to this worktree (`/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/literature-review`). Generated dashboard assets, if any, follow the task-tree skill's regeneration rules.

### Deliverables

**1. External-scheme passthrough.** A relative-link rewrite must fire only for genuine relative paths. Leave any href with a URL **scheme** untouched:
- Allow the `zotero:` scheme through the DOMPurify pass (extend `ALLOWED_URI_REGEXP`, or the equivalent config, to add `zotero` — without weakening the default block on `javascript:` / untrusted `data:`), so an authored `zotero://select/library/items/<KEY>` link survives sanitization.
- In `renderMarkdown`, skip the relative-link rewrite for any href that already carries a scheme (`zotero:`, `mailto:`, `tel:`, and already-absolute `vscode:` / `file:`), in addition to the existing `http(s)` / `#` skips — so scheme URIs are never double-prefixed into `vscode://file/…/zotero://…`.

**2. PDF links open directly, not in VSCode.** For a genuine relative **file** link (the non-task, non-scheme branch), route browser-openable types to the file-serving route instead of the editor:
- A relative link ending in `.pdf` resolves to the `/files/` route in **server mode** (the same `repoPathPrefix` the image branch builds), so it opens in the browser's native PDF viewer.
- In **standalone** mode (no server) resolve it like the standalone image branch (relative to `STANDALONE_PLAN_DIR`) so a `file://` open still reaches it.
- All other relative file links (`.md`, source) keep the current `vscode://file/` behavior unchanged.

Keep the change limited to `.pdf` (the one browser-openable type the trace cluster needs); do not add a broader type table speculatively.

### Validation criteria

Verify the real rendered DOM, not just the source (per the "verify the real user path for UI" discipline): render a task body containing all four link forms and inspect the resulting `<a>`/href values —

- `[Zotero](zotero://select/library/items/ABC123)` → href **unchanged** `zotero://…` (survives DOMPurify, not rewritten), clickable.
- `[Web](https://doi.org/10.1111/jofi.10001)` → unchanged.
- `[PDF](attachments/key.pdf)` → server mode `/files/<prefix>key.pdf`; standalone → the `STANDALONE_PLAN_DIR`-relative form.
- `[MD](attachments/key.md)` → `vscode://file/<RESOLVED_ROOT>/…/key.md` (unchanged behavior).

Do both a live-serve render and a standalone export render (the two resolver modes). If the task-tree suite has a DOM/rendering harness for `renderMarkdown`, add cases there too; otherwise record the served-DOM inspection as the evidence.

## Planner Guidance

This is the dashboard half of the literature-review trace-link cluster (the skill half is `literature-review/agent-judgment-and-provenance`, which authors relative paths + a `zotero://` link against this contract). The resolver already builds `repoPathPrefix` for the image `/files/` branch and `RESOLVED_ROOT` for the vscode branch — reuse them; do not introduce a new path base. The dashboard's own `vscode://` links are added post-sanitize and are unaffected; only author-written scheme links need the DOMPurify allowance.

## Results

Both deliverables are implemented in the extracted client template [skills/task-tree/scripts/templates/dashboard.js](../../../skills/task-tree/scripts/templates/dashboard.js) (`renderMarkdown`), reusing the existing `repoPathPrefix` and `RESOLVED_ROOT` path bases — no new base introduced.

### Changes

1. **External-scheme passthrough.**
   - DOMPurify config sets `ALLOWED_URI_REGEXP` to the vendored DOMPurify default scheme list plus `zotero`, so an authored `zotero://…` href survives sanitization. `javascript:` and untrusted `data:` remain blocked.
   - The relative-link rewrite guard skips any href carrying a URL scheme (`/^[a-z][a-z0-9+.\-]*:/i`) in addition to the `#`-anchor skip — subsuming the old `http(s)` checks and adding `zotero:`/`mailto:`/`tel:`/absolute `vscode:`/`file:`, so scheme URIs are never double-prefixed.

2. **PDF direct-open.** A genuine relative `.pdf` link (non-task, non-scheme, non-doc-mode, non-GitHub) routes to the browser instead of the editor: server mode → `/files/` + `repoPathPrefix` (the same base the image branch builds); standalone → `STANDALONE_PLAN_DIR + taskDirRel + href` (the image branch's standalone form). All other relative file links (`.md`, source) keep the `vscode://file/` behavior. Change is limited to `.pdf`; no broader type table was added. Doc-mode / GitHub-export PDFs retain their existing browser-openable paths.

### Verification — real rendered DOM, both resolver modes

The dashboard suite now extracts the real `renderMarkdown` implementation from [dashboard.js](../../../skills/task-tree/scripts/templates/dashboard.js) and executes its link branches under Node. It covers scheme passthrough, live and standalone PDF targets, and the unchanged VS Code target for other relative files. The original real-DOM inspection also loaded a self-contained standalone export with the vendored DOMPurify and markdown-it assets and exercised the same server/standalone branches.

Rendered hrefs for `[…](…)` body links (task `demo-task`, `ROOT_PREFIX=superRA`):

| Link | Standalone export | Server mode |
|---|---|---|
| `zotero://select/library/items/ABC123` | `zotero://select/library/items/ABC123` (unchanged) | unchanged |
| `https://doi.org/10.1111/jofi.10001` | unchanged | unchanged |
| `attachments/key.pdf` | `testtree/superRA/demo-task/attachments/key.pdf` (`STANDALONE_PLAN_DIR`-relative) | `/files/superRA/demo-task/attachments/key.pdf` |
| `attachments/key.md` | `vscode://file/<RESOLVED_ROOT>/demo-task/attachments/key.md` (unchanged) | same vscode target |
| `javascript:alert(1)` | no anchor / no href emitted | no anchor / no href emitted |

Every row matches the validation criteria. The `javascript:` link produces **zero** dangerous hrefs — markdown-it's own `validateLink` rejects it (renders as literal text `[Danger](javascript:alert(1))`) and DOMPurify's allowlist would strip it too (defense in depth); the `zotero` addition does not weaken this.

**Live-serve render:** `plan_dashboard.py dashboard` booted (index `200`), the `/node/demo-task` fragment served all four raw link forms to the client renderer, and the exact server-mode PDF target `/files/superRA/demo-task/attachments/key.pdf` returned `200` — the rendered href resolves to a real served PDF.

**Regression:** [test_dashboard.py](../../../skills/task-tree/scripts/test_dashboard.py) verifies both the sanitizer configuration and the behavioral link-rewrite matrix against the extracted implementation.
