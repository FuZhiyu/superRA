---
title: "Server-Side Escaping: One Trust Boundary for Task Content"
status: implemented
depends_on:
  - dead-code-removal
---

## Objective

Make server-rendered HTML treat task-file content as untrusted, matching the client's existing DOMPurify posture, so agent-written task files cannot inject markup into the live page or into shared standalone exports.

- Turn on Jinja autoescape for the dashboard environment; audit every remaining template and mark only intentional raw spots `| safe` (pre-rendered fragment embedding, `text/x-markdown` payloads, `| tojson` sites which are already safe).
- **User decision (2026-07-19):** titles and section previews display HTML as literal text; markdown bodies keep full HTML support through the client DOMPurify gate. Do not add per-site sanitization to preserve raw titles.
- Remove the kanban inline `onclick` built by interpolating the task path; use a data attribute + delegated handler (the sidebar already uses delegation).
- Fix string-built HTML and selectors in client JS: active-card assembly goes through the existing escaping helpers; comment-anchor `querySelector` strings use `CSS.escape`.
- Validation: an adversarial fixture (title and section text containing `<script>`, `<img src=x onerror=…>`, single/double quotes, and a standalone ` --> ` line) renders as literal text in the sidebar, kanban, page `<title>`, section previews, and inside a standalone export; regression tests cover these; both suites green.

## Planner Guidance

Findings (2026-07-19 review): `autoescape=False` at [plan_dashboard.py:744-747](../../../../skills/task-tree/scripts/plan_dashboard.py#L744-L747); raw `{{ task.title }}` at [nav_node.html:36](../../../../skills/task-tree/scripts/templates/nav_node.html#L36), [kanban.html:31-32](../../../../skills/task-tree/scripts/templates/kanban.html#L31-L32), [base.html:6](../../../../skills/task-tree/scripts/templates/base.html#L6); the section preview strips `>` but not `<`. `dag.html:86,91` already escapes manually with `| e` — those become redundant-but-harmless under autoescape. JS sites: string-concat `innerHTML` card assembly at base.html:2985-3000 (helpers `escapeHtml`/`escapeAttr` exist at 3349-3354 and are used elsewhere — the safe pattern is in-file); selector building from user-derived section names at base.html:4674-4724 (a `"` in a `##` header currently throws and aborts comment loading for the task).

Audit scope after `dead-code-removal` lands: `base.html`, `nav_node.html`, `node_body.html`, `summary_bar.html`, `kanban.html`, `dag.html`. Check what `_render_summary` and the breadcrumb do with titles (breadcrumb uses `textContent` — already safe).

## Results

Autoescape is on for the dashboard's Jinja environment, and every remaining raw spot is an intentional, audited `| safe` (or `| tojson`, already safe). Six templates were audited: `base.html`, `nav_node.html`, `node_body.html`, `summary_bar.html`, `kanban.html`, `dag.html`.

- **Autoescape on:** [plan_dashboard.py:720](../../../../skills/task-tree/scripts/plan_dashboard.py#L720) — `autoescape=True`.
- **Intentional raw spots, all marked `| safe`:**
  - The `text/x-markdown` payload — [task_body.html:52](../../../../skills/task-tree/scripts/templates/task_body.html#L52). Must stay raw: it is read client-side via `textContent` inside a `<script>` (a raw-text element whose content the browser never entity-decodes), then sanitized through DOMPurify before insertion. The `</script>`-breakout guard (`<\/script>`) is unaffected — it already ran before the new `| safe`, and the closing-script regression test (`test_script_payload_escapes_closing_script_tag`) still passes.
  - The six inlined standalone render-library bodies (`standalone_assets.*`) in the export's `<head>` — [base.html:20-26](../../../../skills/task-tree/scripts/templates/base.html#L20-L26). These are vendored library source, not task content; escaping would have corrupted the CSS/JS.
  - `dag.html`'s existing manual `| e` calls at lines 86 and 91 are confirmed redundant-but-harmless under autoescape (Jinja's `escape` filter returns a `Markup`-wrapped result, so autoescape does not re-escape it) — left unchanged, no double-escaping observed in the export smoke test.
- **Titles/section previews now render as literal text** wherever they were previously raw (`nav_node.html:36`, `kanban.html`, `base.html`'s `<title>`/`#header-title`), per the 2026-07-19 user decision — no per-site sanitization added.
- **Kanban click wiring** — [kanban.html:31](../../../../skills/task-tree/scripts/templates/kanban.html#L31) now carries `data-path` (autoescaped) instead of an inline `onclick="revealTask('{{ t.path }}')"`; a delegated `onKanbanCardClick` handler on `#view-kanban` reads `card.dataset.path`, mirroring the existing `onChildCardClick` pattern ([base.html:2744-2751](../../../../skills/task-tree/scripts/templates/base.html#L2744-L2751)).
- **Comment-anchor selectors use `CSS.escape`** at both section-name-derived `querySelector` sites — the grouped-anchor match and the orphan-section lookup ([base.html:4664](../../../../skills/task-tree/scripts/templates/base.html#L4664), [base.html:4690](../../../../skills/task-tree/scripts/templates/base.html#L4690)) — so a `"` in a `##` header no longer throws and aborts comment loading for the whole task.
- **Active-card assembly (`childCardHTML`) was already escaped** via the existing `escapeHtml`/`escapeAttr` helpers ([base.html:3247-3250](../../../../skills/task-tree/scripts/templates/base.html#L3247-L3250)) — pre-existing code, not the line-numbered `2985-3000` region the guidance cited (line numbers shifted after `dead-code-removal`/`standalone-state` landed); no change needed there, only the kanban and comment-selector sites required fixes.

**Validation:** a new `TestServerSideEscaping` class in [test_dashboard.py:3637-3795](../../../../skills/task-tree/scripts/test_dashboard.py#L3637-L3795) plants `<script>`, `<img src=x onerror=…>`, single/double quotes, and a standalone ` --> ` line across a root title, a leaf title, and a leaf section body, then asserts:
- the page `<title>`/header, sidebar row, and kanban card render the adversarial title as literal escaped text (never raw), with no inline `onclick` interpolating the path;
- the section preview shows literal escaped text while the `text/x-markdown` payload for the same content stays raw (unescaped) for the client DOMPurify gate;
- the same split holds inside a standalone export, where per-task fragments are pre-rendered through the same templates and then JSON-string-encoded via `| tojson` for embedding: the title's HTML-escaped form gets that JSON-safe encoding layered on top (still literal text once decoded), while the raw markdown payload's angle brackets get only the JSON-safe encoding, with no HTML-entity escaping underneath — checked against the generated export's actual bytes, not assumed;
- `CSS.escape` is present at both comment-anchor selector sites (source-presence check, consistent with this suite's existing convention for browser-only behavior it cannot exercise headlessly).

Both suites are green: `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts -q` → **703 passed, 2 skipped** (696 pre-existing + 7 new). A manual `plan_dashboard.py generate` export of this repo's real `superRA/` tree (with its real task titles/content) also completed without error and showed no double-escaping artifacts (`&amp;amp;` etc. absent).

No deviation from Planner Guidance — the two cited JS sites (card assembly, section-name selectors) were re-located under their current line numbers after the `dead-code-removal`/`standalone-state` predecessor tasks shifted the file, and the card-assembly site turned out to already be safe (pre-existing `escapeHtml`/`escapeAttr` usage), which the guidance itself anticipated ("the safe pattern is in-file").
