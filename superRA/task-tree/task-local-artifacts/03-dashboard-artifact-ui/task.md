---
title: "Browse and Render Task Companion Files in the Dashboard"
status: implemented
depends_on:
  - 02-dashboard-artifact-data
---

## Objective

Expose task companion files as a lightweight, read-only canvas inside the owning task's dashboard detail view.

- Keep the sidebar semantic: task rows may show a companion-file count that opens the Files view, but files never become rows in the task hierarchy, dependency graph, status rollup, frontier, or Kanban board.
- Add a Files view that lists direct Markdown, Python, Julia, R, and notebook companions first, then attachment contents in a secondary group using their relative paths. Keep unexpected direct files reachable without presenting placement history as a user-facing taxonomy, and exclude the task-tree's required root wrapper from companion discovery.
- Retain one representative Markdown companion and one representative Python companion with this task so the live Files canvas demonstrates both renderers.
- Render Markdown companions through the existing markdown-it, KaTeX, syntax-highlighting, and DOMPurify boundary. Resolve their relative links and images from the companion's own directory rather than from `task.md`.
- Vendor and pin `notebookjs` for read-only `.ipynb` rendering, wiring it to the dashboard's existing Markdown, KaTeX, Highlight.js (including Julia and R), and DOMPurify stack. Support Markdown, raw, and code cells plus stream, error, safe text/HTML/Markdown/LaTeX, and PNG/JPEG/sanitized-SVG outputs and cell attachments. Never execute notebook code, JavaScript outputs, widgets, or other active MIME types; show an explicit unsupported-output fallback.
- Give every companion an explicit open or download action; provide safe inline previews for supported image, PDF, and text/source types without executing scripts or active content.
- Refresh the block on the owning task's artifact event and re-render an open sidecar when it changes, while preserving task hash routing, breadcrumbs, comments, expanded branches, theme, scroll, and worktree selection.
- Keep live and standalone behavior aligned, including subtree exports and explicit unavailable/oversized states. Existing figures must continue to render inline in task results and appear only once in exported bytes.
- Add browser-facing and server-rendered regressions for companion-relative links, notebook cell/output types, malicious notebook content, unsupported MIME fallbacks, Python/Julia/R highlighting, case-insensitive R extensions, nested attachment presentation, sanitization, direct/attachment grouping, supported previews, download actions, hot reload, worktree switches, standalone operation, accessibility, and unchanged task navigation; run the dashboard and full task-tree suites.

## Planner Guidance

Keep `activePath` as the owning task path and open a companion within that task's detail surface, so browser history and every task-level view retain their existing semantics. Generalize the current Markdown renderer with a content-base directory instead of creating a second rendering stack. Relevant files are [task_body.html](../../../../skills/task-tree/scripts/templates/task_body.html), [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js), [dashboard.css](../../../../skills/task-tree/scripts/templates/dashboard.css), [base.html](../../../../skills/task-tree/scripts/templates/base.html), [vendor/README.md](../../../../skills/task-tree/scripts/vendor/README.md), and [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py).

`notebookjs` 0.8.3 is approximately 8 KB minified and can reuse the renderer and sanitizer already shipped by the dashboard; do not add `nbconvert`, JupyterLab browser packages, notebook execution, or a second Markdown/highlighting stack. Its common static renderer is the intended fidelity boundary, with a narrow adapter for cell attachments and unsupported-output fallbacks. Record its pinned version, source URL, hash, and re-fetch command with the other hand-managed vendor assets.

The existing Highlight.js common bundle already includes R, while the dashboard loads Julia from its existing separate language asset. R support therefore needs only extension/language mapping and regression coverage, not another package or vendored file.

Companion search is optional for this scope: add it only if the existing index can accept owner-task file records without duplicating discovery or creating a second navigation model. The required discovery surface is the Files view on the owning task.

## Revision Notes

The Files canvas currently calls unexpected direct files “legacy placement,” and the required root `superra` wrapper is the only such file visible at the task-tree root. Remove that misleading user-facing distinction, reserve the wrapper as task-tree infrastructure, and add Markdown/Python companions here for visual inspection.

## Results

### Implemented

- Added a task-owned Files sidecar and count affordances without changing `activePath` or admitting companions into task navigation. The canvas groups first-class direct companions and recursive attachments, with genuinely unexpected direct files kept in a collapsed, neutrally named **Additional files** group; explicit preview/download/unavailable actions cover supported Markdown, source, image, PDF, and text types ([dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js#L1135), [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js#L1388), [dashboard.css](../../../../skills/task-tree/scripts/templates/dashboard.css#L1139)).
- Reserved the required root `superra` wrapper as task-tree infrastructure so it does not enter companion manifests or standalone exports. Unexpected direct files remain discoverable with the neutral internal placement `other` ([\_artifacts.py](../../../../skills/task-tree/scripts/_artifacts.py#L17), [\_artifacts.py](../../../../skills/task-tree/scripts/_artifacts.py#L277)).
- Generalized the existing Markdown renderer with a companion content base. Relative links and images now resolve from the companion's directory through the bounded artifact API/export data, while task-body links retain their prior task-relative behavior ([dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js#L231)).
- Vendored NotebookJS 0.8.3 and replaced its permissive output renderers with the dashboard's Markdown, KaTeX, Highlight.js, and DOMPurify stack. The adapter supports Markdown/raw/code cells, attachments, stream/error outputs, and safe static text/HTML/Markdown/LaTeX/PNG/JPEG/SVG output; JavaScript, widgets, and unknown MIME types render explicit inert fallbacks and no code executes ([dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js#L1640), [vendor/README.md](../../../../skills/task-tree/scripts/vendor/README.md#L40)).
- Kept live and standalone paths aligned by serving/inlining the pinned library and embedded artifact payloads. Task-scoped SSE refreshes re-render an open preview from `event.detail.data` while preserving hash, breadcrumbs, theme, scroll, and worktree selection; close actions restore keyboard focus even if the active-card button was re-rendered ([plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py#L2020), [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js#L1619)).
- Fixed the review-round interaction edges: delegated tree keyboard handling now leaves nested controls to native Enter/Space activation while retaining ordinary row navigation, and every still-selected artifact re-enters the preview renderer after SSE refresh so newly oversized or unavailable files replace stale content with the explicit unavailable state ([dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js#L1428), [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js#L3011)).
- Retained hand-authored [renderer-example.md](renderer-example.md) and [renderer-example.py](renderer-example.py) beside this task as visual fixtures requested by the researcher. Their decision basis is renderer inspection: the Markdown file exercises headings, a relative companion link, inline/display math, fenced Python, and a table; the Python file exercises source highlighting with a small executable example.

### Verification

- Server and browser regressions cover direct/attachment/additional grouping, root-wrapper exclusion, companion-relative URLs, Python/Julia/case-insensitive R highlighting, NotebookJS cell/output types, attachment images, malicious HTML/SVG sanitization, unsupported active MIME fallbacks, downloads, Enter/Space Files activation and focus return, ordinary tree-row keyboard navigation, oversized SSE transitions and state preservation, standalone operation, and worktree switching ([test_artifact_ui.py](../../../../skills/task-tree/scripts/test_artifact_ui.py#L238), [test_artifact_ui.py](../../../../skills/task-tree/scripts/test_artifact_ui.py#L276), [test_artifacts.py](../../../../skills/task-tree/scripts/tests/test_artifacts.py#L67)).
- Focused artifact UI/discovery suite: `33 passed` with two non-failing warnings via `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx --with playwright python -m pytest skills/task-tree/scripts/test_artifact_ui.py skills/task-tree/scripts/tests/test_artifacts.py -q`.
- Full task-tree suite: `773 passed` with four non-failing warnings via `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx --with playwright python -m pytest skills/task-tree/scripts`.
- Static checks passed: `node --check` for `dashboard.js`, Python byte-compilation for the changed Python/tests, and `git diff --check`. Desktop Chromium inspection at 1440×900 confirmed the Files list and notebook preview remain legible alongside the active task.
- The example script printed `f(2) = 5` and `f(3) = 10`; the Markdown companion passed `skills/report-in-markdown/scripts/check_markdown.py`.
- `notebook.min.js` matches the documented SHA-256 `673b1916c250d2093c8c8920e5503348a2283ef67d6ad429f0b0dc6c98f7c115`. The generic skill-creator validator was not applicable as a clean gate: it rejects the task-tree skill's pre-existing `user-invocable` frontmatter key, which this task did not modify.
