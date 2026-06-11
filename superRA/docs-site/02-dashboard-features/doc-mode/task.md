---
title: "Doc-Mode Rendering Toggle"
status: approved
depends_on: []
tags: []
created: 2026-06-10
---

## Objective

Add an opt-in doc-mode to `plan_dashboard.py serve` and `generate` (plumbed through the `cli.py dashboard` surface) that renders a tree as documentation rather than as a task tracker.

In doc-mode:

- Task-workflow chrome is suppressed: status pills/badges, the header progress bar and status stats, and the kanban view toggle.
- The root node's body renders as the landing view on load, so the exported file opens on a home page rather than an empty selection.
- Tree sidebar navigation, section rendering, math, images, hash deep links, and theming all behave as today.

Success criteria: a doc-mode standalone export contains no status-pill or kanban markup; a default (no-flag) export is unchanged relative to the pre-doc-mode baseline (sibling features that legitimately ship by default are not regressions); both verified by inspecting the rendered artifact and covered by tests on the generated HTML.

## Planner Guidance

Whether the DAG view is suppressed too is implementer judgment — it is meaningless for a docs tree with no `depends_on` edges; document the call in `## Results`.

The flag name and whether doc-mode is a CLI flag, frontmatter marker on the root node, or both is implementer judgment within the additive/opt-in constraint — coordinate the choice with `08-deploy`'s build invocation by recording it in `## Results`.

## Results

Doc-mode is an opt-in `--doc-mode` CLI flag (not a frontmatter marker) on both `generate` and `serve`, plumbed through every dashboard entry surface. Default output is unchanged: without the flag the page carries no doc-mode attribute and `window.DOC_MODE = false`.

### Flag surface (for `08-deploy` coordination)

The site build invokes one of these — all reach the same `doc_mode=True` render:

- `uv run --script skills/task-tree/scripts/plan_dashboard.py generate --plan-root <docs tree> --doc-mode` ([plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py))
- `superra dashboard export --doc-mode` (the wrapper/`cli.py` surface) — `--doc-mode` is accepted either before or after the `export` subcommand ([cli.py](../../../../skills/task-tree/scripts/cli.py))
- `superra dashboard --doc-mode` / `plan_dashboard.py serve --doc-mode` for a live doc preview

`08-deploy` should add `--doc-mode` to its `generate`/`export` invocation.

### Mechanism

`doc_mode` threads as a single template variable into `base.html`, which renders `<html data-doc-mode="true">` and sets `window.DOC_MODE`. Chrome suppression is CSS-driven off the `html[data-doc-mode]` attribute selector — inert without the attribute, so a normal dashboard is byte-for-byte unchanged ([base.html](../../../../skills/task-tree/scripts/templates/base.html)):

- Status badges (`.badge` — sidebar rows, child cards, active-node head), per-group approved progress (`.task-progress`), the header summary stats + progress bar (`#summary-bar`), and the Kanban toggle (`#btn-kanban`) are hidden via CSS.
- The one badge built in JS (active-node head) is additionally gated on `!window.DOC_MODE` so it is never emitted.
- The root body already renders as the landing view at an empty hash (the router loads `/node/` with `path=''`), so no new landing logic was needed; verified the export opens on the root home page, not an empty selection.

Threading: `render_standalone_html`/`generate_dashboard` take `doc_mode` and pass it to the template; `generate`'s `--doc-mode` flows through `main()`; the live path sets the module global `DOC_MODE` (read by the index route), carried into the detached background server via a `--doc-mode` child-argv flag in `serve_background`.

### Judgment call: DAG view suppressed

The per-parent children dependency view (`.children-dag`, the "Subtasks" flow) **is suppressed** in doc-mode. It is meaningless for a docs tree carrying no `depends_on` edges — it would render a flat card grid of child pages with workflow framing ("click to drill in"). Sidebar navigation already covers child-page navigation, so suppressing it keeps the doc reader on the page body. This is hidden via the same CSS attribute selector; the workspace landing/body/breadcrumb path is untouched.

### Verification

- Tests: `TestDocMode` in [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py) (10 tests) — attribute/flag presence, default-unchanged, the four CSS suppression rules, the JS badge gate, serve-route flag honoring, and CLI flag forwarding (both `export --doc-mode` and `--doc-mode export`). Full suite: 281 passed, 2 skipped.
- Rendered artifact (real headless Chrome, `file://` open of a doc-mode export): `<html data-doc-mode="true">`, `#summary-bar` and `#btn-kanban` compute `display: none`, the root landing body renders ("Docs Home" title), and the active-node head carries no status badge. A default export in the same harness keeps the summary bar, kanban button, and renders normally.
