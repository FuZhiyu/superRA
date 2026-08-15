---
title: "Browse and Render Task Companion Files in the Dashboard"
status: approved
depends_on:
  - 02-dashboard-artifact-data
---

## Objective

Expose task attachments through the existing sidebar and full-width dashboard detail pane.

- Add a visually distinct `Attachments` pseudo-branch beneath each task row when attachments exist. Keep it collapsed by default; expanding it reveals file nodes using their relative hierarchy. Pseudo-nodes never enter task discovery, dependencies, status rollups, frontier, DAG, or Kanban.
- Remove the Files button and separate canvas/modal. Selecting an attachment must use the normal full-width detail pane and browser history; selecting its owning task restores the task detail.
- Move the representative Markdown and Python examples under this task's `attachments/` directory so the live dashboard demonstrates both renderers through the intended storage and navigation model.
- Render Markdown companions through the existing markdown-it, KaTeX, syntax-highlighting, and DOMPurify boundary. Resolve their relative links and images from the companion's own directory rather than from `task.md`.
- Vendor and pin `notebookjs` for read-only `.ipynb` rendering, wiring it to the dashboard's existing Markdown, KaTeX, Highlight.js (including Julia and R), and DOMPurify stack. Support Markdown, raw, and code cells plus stream, error, safe text/HTML/Markdown/LaTeX, and PNG/JPEG/sanitized-SVG outputs and cell attachments. Never execute notebook code, JavaScript outputs, widgets, or other active MIME types; show an explicit unsupported-output fallback.
- Provide safe full-pane previews for Markdown, Python, Julia, R, notebooks, images, PDFs, and text without executing scripts or active content. Source previews must use visible language highlighting; keep explicit raw/open and download actions where applicable.
- Refresh the owning task's attachment branch and re-render the selected file when it changes, while preserving task and attachment routing, breadcrumbs, comments, expanded branches, theme, scroll, and worktree selection.
- Keep live and standalone behavior aligned, including subtree exports and explicit unavailable/oversized states. Existing figures must continue to render inline in task results and appear only once in exported bytes.
- Add browser-facing and server-rendered regressions for collapsed attachment branches, task/file visual distinction, full-pane routing and history, companion-relative links, notebook cell/output types, malicious notebook content, unsupported MIME fallbacks, visibly highlighted Python/Julia/R, case-insensitive R extensions, nested attachment presentation, sanitization, supported previews, download actions, hot reload, worktree switches, standalone operation, accessibility, and unchanged task semantics; run the dashboard and full task-tree suites.

## Details

Keep the owning task as the semantic owner while giving the selected attachment an explicit URL/history state. Reuse the existing sidebar row mechanics and main `#active-node` detail surface; remove the sidecar rather than maintaining two render targets. Generalize the current Markdown renderer with a content-base directory instead of creating a second rendering stack. Relevant files are [nav_node.html](../../../../skills/task-tree/scripts/templates/nav_node.html), [task_body.html](../../../../skills/task-tree/scripts/templates/task_body.html), [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js), [dashboard.css](../../../../skills/task-tree/scripts/templates/dashboard.css), [base.html](../../../../skills/task-tree/scripts/templates/base.html), [vendor/README.md](../../../../skills/task-tree/scripts/vendor/README.md), and [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py).

`notebookjs` 0.8.3 is approximately 8 KB minified and can reuse the renderer and sanitizer already shipped by the dashboard; do not add `nbconvert`, JupyterLab browser packages, notebook execution, or a second Markdown/highlighting stack. Its common static renderer is the intended fidelity boundary, with a narrow adapter for cell attachments and unsupported-output fallbacks. Record its pinned version, source URL, hash, and re-fetch command with the other hand-managed vendor assets.

The existing Highlight.js common bundle already includes R, while the dashboard loads Julia from its existing separate language asset. R support therefore needs only extension/language mapping and regression coverage, not another package or vendored file.

Companion search is optional for this scope: add it only if the existing index can accept owner-task file records without duplicating discovery or creating a second navigation model.

## Results

The dashboard now presents retained files through one navigation tree and one
reading surface. Each task with a non-empty manifest gets a visually distinct,
collapsed-by-default **Attachments** pseudo-branch. Expanding it shows nested
directories and file nodes without giving them task status, dependencies,
frontier membership, DAG cards, or Kanban semantics
([dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js),
[dashboard.css](../../../../skills/task-tree/scripts/templates/dashboard.css)).

Selecting a file records its owning task and `attachments/...` path in the URL
hash, renders it in the normal full-width `#active-node` pane, clears the child
DAG, and participates in browser Back/Forward navigation. Selecting the owner or
using **Back to task** restores the task body. The Files button, count badge, and
sidecar markup are absent. Live attachment events replace the owning pseudo-branch
and re-render an open file; worktree switches clear manifest caches and preserve
the attachment route only when its owner survives
([base.html](../../../../skills/task-tree/scripts/templates/base.html),
[dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js)).

Markdown, notebook, image, PDF, and text/source previews reuse the existing
bounded data path and renderer stack. Relative Markdown links and images resolve
from the selected attachment's directory. Python, Julia, and case-insensitive R
source previews use Highlight.js with visible token colors; notebooks remain
read-only and sanitize active HTML/SVG while showing inert unsupported-output
fallbacks. Live and standalone exports share these renderers and download
actions ([test_artifact_ui.py](../../../../skills/task-tree/scripts/test_artifact_ui.py)).

The hand-authored visual fixtures now obey the attachment-only contract:
[renderer-example.md](attachments/renderer-example.md) exercises Markdown,
relative links, math, fenced code, and a table; [renderer-example.py](attachments/renderer-example.py)
exercises highlighted Python. Their decision basis is the researcher's request
for representative renderer examples.

Verification:

- Browser UI suite: `3 passed` with two non-failing deprecation warnings via
  `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx --with playwright python -m pytest skills/task-tree/scripts/test_artifact_ui.py -q`.
- Focused UI/data suite: `29 passed, 2 skipped` with one cache-permission warning
  via the same command targeting `test_artifact_ui.py` and
  `tests/test_artifacts.py`; the skipped cases are the browser tests proven
  separately in the preceding invocation.
- `node --check`, Python byte-compilation, Markdown integrity, example-script
  execution (`f(2) = 5`, `f(3) = 10`), and `git diff --check` passed.
- Full task-tree suite: `772 passed` with four known non-failing fixture and
  dependency warnings. The first run exposed one stale breadcrumb source
  assertion after attachment-aware routing; the targeted regression and full
  rerun passed after aligning it with the new active-attachment condition.

The review round removed the dormant Files-sidecar implementation and styles,
made task-row SSE swaps rebuild attachment branches without losing expansion or
the active file, added explicit sanitized KaTeX rendering for notebook LaTeX,
and added worktree-isolation plus accessible keyboard/tree regressions. The
dedicated installed-Chromium live and standalone tests passed `2 passed`; the
installed-Chromium worktree-switch test passed `1 passed`.

The accessibility fix now treats task rows, the Attachments disclosure,
directory parents, and file nodes as one roving-tabindex tree. Exactly one
visible treeitem is tabbable; Up/Down crosses task and attachment boundaries,
Right/Left enters and exits each hierarchy level, and nested directories own
their descendant `role="group"` elements. The dedicated installed-Chromium
unified-tree regression passed `1 passed`.

The final return-path fix maps `ArrowLeft` from a collapsed Attachments
disclosure directly to its owning task row. The installed-Chromium regression
now verifies file → directory → Attachments → owner, then re-enters the
collapsed disclosure and verifies `ArrowDown` exits to the following task;
the test passed `1 passed`.

This round dropped the dead client-side branch in
[`resolveArtifactRelativePath`](../../../../skills/task-tree/scripts/templates/dashboard.js#L148-L170)
that generated an open/preview link for a same-directory, non-`attachments/`
companion — a link the server's `attachments/`-only contract always 404s.
The function now returns `''` unless the resolved path has at least two
segments with `attachments` as the first, matching
[`_validated_parts`](../../../../skills/task-tree/scripts/_artifacts.py#L342)
exactly, and no in-scope objective or contract calls for opening a
same-directory non-`attachments/` companion through this link, so no server
expansion was made. It also documented the intentional soft-fail on the
attachment-manifest fetch in
[`loadAttachmentBranches`](../../../../skills/task-tree/scripts/templates/dashboard.js#L1593-L1607).

Verification: `uv run --with pytest --with pyyaml --with fastapi --with jinja2
--with 'uvicorn[standard]' --with watchfiles --with httpx --with playwright
python -m pytest skills/task-tree/scripts/test_artifact_ui.py
skills/task-tree/scripts/test_dashboard.py -q` — `300 passed, 2 warnings`
(non-failing `websockets.legacy` deprecation warnings); `node --check
skills/task-tree/scripts/templates/dashboard.js` passed.

