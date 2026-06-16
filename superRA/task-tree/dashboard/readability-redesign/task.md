---
title: "Dashboard Readability Redesign — Reading Typography, HTML Rendering, Doc Chrome"
status: approved
depends_on: []
tags: []
created: 2026-06-11
---

## Objective

Make long-form content in the dashboard genuinely readable — in both the task tracker and the doc-mode documentation site — by fixing the diagnosed typography, contrast, and chrome problems in the shared rendering layer, and by letting agents write raw HTML into task markdown that renders properly.

All rendering changes land in the shared template `skills/task-tree/scripts/templates/base.html` (plus `plan_dashboard.py` / vendored assets where a task says so), so every fix applies to the live dashboard, static exports, and the doc-mode site simultaneously. Doc content edits are limited to `docs/site/01-welcome/task.md` (the broken diagram).

### Context

Diagnosis (from Playwright renders of the built `_site/` and computed-style probes, 2026-06-11):

1. **All markdown prose is 12px IBM Plex Mono.** `.rendered-md` sets `font-family: var(--font-mono); font-size: 12px` for paragraphs, lists, and tables. Mono uniform letterforms make multi-paragraph reading slow and tiring — this is the dominant cause of the "hard to read" feel.
2. **No measure constraint.** Content has no max-width; paragraphs run ~1100px ≈ 150–170 characters per line (comfortable is 60–80ch).
3. **Heading hierarchy collapsed inside content.** `.rendered-md` h1/h2/h3 are 16/14/13px over a 12px body — a flat wall. Chrome uses ~11 ad-hoc sizes (10–23px) with no scale.
4. **Tracker-dense vertical rhythm.** `p { margin: 4px 0 }`, `li { margin: 2px 0 }` — fine for collapsed tracker rows, oppressive for documentation.
5. **Code indistinguishable from prose** — same face and size; only a faint background separates them.
6. **WCAG contrast failures.** `--text-mute` #9e9890 on #faf9f7 = 2.72:1 (light), #706b63 on #1c1b19 = 3.26:1 (dark); `not-started` badge text 2.91:1. AA needs 4.5:1 at these sizes.
7. **Task chrome leaks into doc-mode**: "Objective" disclosure toggles, `root` breadcrumb, slug-prefixed page titles.
8. **Raw HTML is escaped**: `markdownit({ html: false })` at base.html:1861 renders the welcome page's mermaid block (and any agent-written HTML) as visible escaped text.

Root cause: the dashboard was designed as a tracker (collapsed bodies, terminal aesthetic); doc-mode later reused the same content CSS for long-form reading without upgrading it.

Researcher decisions (2026-06-11): body prose moves to **IBM Plex Sans** (same Google Fonts link family; mono stays for code/slugs/badges/metadata; Source Serif 4 stays the display face). The welcome flow diagram is **hand-built HTML/CSS** (no mermaid dependency), enabled by the raw-HTML rendering task.

### Conventions

- Implementers and reviewers on the typography/chrome tasks load the `frontend-design:frontend-design` skill before editing styles.
- Verification follows the real user path: open the rendered page (live serve or rebuilt export) in a browser via Playwright, in both light and dark themes, in both tracker and doc-mode; computed-style/DOM probes over route-level checks. Screenshots are evidence in task Results.
- Vendored third-party assets follow `skills/task-tree/scripts/vendor/README.md`: pin version + SHA-256, record source URL, CDN tag in base.html must match the vendored version.
- The dashboard test suite must stay green: `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts`.

## Results

The dashboard's shared rendering layer was rebuilt so long-form content reads as documentation in both the task tracker and the doc-mode site. All rendering changes land in the shared template [base.html](../../../../skills/task-tree/scripts/templates/base.html), so the fixes apply to live serve, static exports, and the doc-mode site at once. Verified on the real user path (Playwright on rebuilt artifacts, both themes, tracker + doc-mode, computed-style probes); the dashboard suite stays green at 684 passed / 2 skipped, including the new HTML-sanitization security lock.

**Reading typography** ([01-reading-typography](01-reading-typography/task.md)). Three explicit type roles replace the uniform 12px mono: `--font-text` (IBM Plex Sans) for prose, `--font-display` (Source Serif 4) for titles, `--font-mono` for code/slugs/badges. `.rendered-md` became a reading surface — 15px/1.65 body, a stepped serif heading scale (h1 23 / h2 19 / h3 16), em-relative rhythm, a constrained reading measure (with `pre`/tables opting out), and inline/fenced code differentiated from prose. KaTeX inherits the new size naturally.

**Raw HTML in task markdown** ([02-html-in-markdown](02-html-in-markdown/task.md)). The renderer flipped to `html: true` with every render routed through a single `renderMarkdown` helper that sanitizes with DOMPurify (default allowlist plus `style`/`class`). Exports are published to GitHub Pages, so sanitization is a hard security gate — verified against real hostile payloads (`<script>`, `onerror=`, `javascript:`) through the loaded library on the published-export path. DOMPurify 3.4.10 is vendored (pinned version + SHA-256 + source) and inlined into standalone exports; authoring guidance added to the `report-in-markdown` skill.

**Doc-mode reading chrome** ([03-doc-mode-reading-chrome](03-doc-mode-reading-chrome/task.md)). In `html[data-doc-mode]`, task-tracker anatomy is suppressed: the Objective renders inline (no disclosure toggle), other sections become plain headings, titles drop slug prefixes, the breadcrumb uses the site title, and the column centers at the reading measure. Tracker mode is byte-for-byte unchanged — every change is doc-mode-scoped CSS or `DOC_MODE`-gated JS.

**Chrome contrast + type scale** ([04-chrome-contrast](04-chrome-contrast/task.md)). The failing tokens were re-derived within the warm palette to meet WCAG AA on resting surfaces (`--text-mute` and the status-badge text pairs), ~34 ad-hoc chrome sizes were mapped onto a six-step modular scale shared with the content surface, and sidebar rows now degrade so the status badge never clips. One documented residual: in dark theme, muted child text on container-hover rows sits at ~4.12:1 while hovered (resting AA is met everywhere).

**Welcome flow diagram** ([05-welcome-flow-diagram](05-welcome-flow-diagram/task.md)). The broken mermaid block in the welcome page became a themed semantic `<ol>` flow (PLAN → IMPLEMENT → INTEGRATE → finished) rendered through the raw-HTML path, themed only via CSS tokens so it adapts to both themes, and degrading to a legible ordered list where raw HTML is stripped (GitHub).

**Integrated visual QA** ([06-visual-qa](06-visual-qa/task.md)). Full sweep across themes × viewports (1440/1024/390px) on docs and tracker, artifacts rebuilt, suite green. The docs site is fully AA in both themes with no task chrome, rendered diagram, highlighted code, and no overflow at 390px. Deferred follow-ups (all pre-existing, tracker-only, none on the docs site): the dark hover-state contrast item above; light accent file-links on tinted code backgrounds (4.43:1); the dark active view-toggle button (3.01:1, suppressed in doc-mode); and a long `.header-title` overflow at 390px.

**Integration refinement** (2026-06-15). After live review on a wide display, the reading measure was widened from 72ch to `--measure: 96ch` ([base.html:1429](../../../../skills/task-tree/scripts/templates/base.html#L1429)) and the reading column — breadcrumb plus active node — now centers at `max-width: 100ch; margin-inline: auto` in **both** tracker and doc-mode ([base.html:826](../../../../skills/task-tree/scripts/templates/base.html#L826)), with the children-DAG band centering too; on an ultra-wide monitor the column reads as a balanced centered page rather than a narrow left-anchored strip. The earlier doc-mode-only `#active-node { max-width: 76ch }` override (task 03) was collapsed into this one shared rule. The child task records below — including 06's Playwright screenshots and the `648px ≈ 72ch` / `76ch` measurements — capture the as-built baseline before this widening; the qualitative result (sans reading face, constrained centered measure, no task chrome) is unchanged.

