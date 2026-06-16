---
title: "Syntax Highlighting for Fenced Code Blocks"
status: approved
depends_on: []
tags: []
created: 2026-06-10
---

## Objective

Render fenced code blocks with syntax highlighting in both the live server and the standalone export.

- Vendor a highlighting library (highlight.js or equivalent) under `skills/task-tree/scripts/vendor/` per its README conventions, with a language set covering the doc and task content actually present (at minimum: bash/shell, python, julia, yaml, markdown, json).
- Wire it into the existing markdown-it rendering path so highlighting applies wherever markdown bodies render today.
- Highlight colors respect the existing light/dark theme tokens in `base.html` — readable in both themes.
- Standalone export inlines the new assets like the existing vendored libraries; no network fetch at runtime.

Success criteria: a fenced block with a language tag renders highlighted in a live session and in an exported file, in both themes, verified in the rendered DOM; unknown/absent language tags degrade to today's plain rendering; vendored assets documented in `vendor/README.md`.

## Results

Highlighting ships by default (a pure capability addition) in both live and standalone modes via highlight.js, wired into the existing markdown-it path.

### Library + language coverage

Vendored two files under [vendor/](../../../../skills/task-tree/scripts/vendor/), documented in [vendor/README.md](../../../../skills/task-tree/scripts/vendor/README.md) with versions, source URLs, SHA-256, and a re-fetch recipe:

- `highlight.min.js` — highlight.js 11.11.1 "common" bundle (36 languages, covering bash/shell, python, yaml, markdown, json among the required set).
- `languages/julia.min.js` — the Julia module (not in the common bundle), loaded after the bundle so it registers Julia onto the global `hljs`.

Required language set (bash/shell, python, julia, yaml, markdown, json) is fully covered. Extending coverage = vendor another `languages/<lang>.min.js` from the same CDN path; recorded in the README.

### Wiring

markdown-it is constructed with a `highlight: highlightFence` option ([base.html](../../../../skills/task-tree/scripts/templates/base.html)). `highlightFence(code, lang)` highlights only when `hljs.getLanguage(lang)` resolves a registered language, emitting `<pre><code class="hljs language-<lang>">…</code></pre>`. For an absent or unknown language tag it returns `''`, so markdown-it keeps its default escaped `<pre><code>` — today's plain rendering, unchanged. This applies wherever markdown bodies render today (all `renderMarkdown` call sites).

### Theme-aware colors

No highlight.js theme stylesheet is vendored. Token colors are driven by new `--hl-*` CSS variables defined in both the `:root` (light) and `[data-theme="dark"]` blocks, mapped to `.hljs-*` classes scoped under `.rendered-md`. Colors reuse the existing palette family (accent/status token hues) so highlighted code is readable on the `--bg-alt` code-block background in both themes and follows the existing theme toggle.

### Standalone self-containment

`_build_standalone_assets` reads both vendored files and the standalone template inlines them as `<script>` bodies alongside markdown-it/katex/texmath ([plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py)). The highlight.js CDN tags are emitted only in server mode; the standalone export contains no `cdn.jsdelivr.net/npm/@highlightjs` reference — no network fetch at runtime.

### Verification

- Tests: `TestCodeHighlighting` in [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py) (7 tests) — markdown-it wiring, unknown-language fall-through gate, standalone inlining + CDN-tag absence, asset builder, theme tokens defined in both themes, vendor files present, server-mode CDN tags retained. Full suite: 281 passed, 2 skipped.
- End-to-end render (node + vendored libs): a ` ```python ` and ` ```julia ` block produce `hljs-*` token spans; a no-language and an unknown-language block produce no `hljs` class and stay in plain `<pre><code>`.
- Rendered artifact (real headless Chrome, `file://` open of an export): fenced code carries `class="hljs"` highlighted spans; verified in both default and doc-mode exports (highlighting is independent of doc-mode).
