---
title: "Self-contained export: embed figures and math"
status: not-started
depends_on:
  - subtree-export
tags: []
created: 2026-06-01
---

## Objective

Make the standalone HTML export **fully self-contained for figures and math**, so a shared/downloaded single file renders correctly when moved away from the repo and when opened with no network. Today the export embeds task *data* offline (no calls back to the dashboard server) but is neither figure-complete nor CDN-independent: figures are referenced by a relative path into the `.plan` tree (the `[subtree-export](../subtree-export/task.md)` "Known limitation" — figures break in a downloaded file), and all rendering libraries load from CDNs ([base.html:7–15](../../../../skills/task-system/scripts/templates/base.html#L7) — Google Fonts, htmx + sse, markdown-it, markdown-it-texmath, KaTeX CSS+JS). Bodies are raw markdown rendered **client-side** by markdown-it + markdown-it-texmath + KaTeX ([base.html:1267](../../../../skills/task-system/scripts/templates/base.html#L1267), delimiters `dollars`), so without those libs a moved/offline file shows unrendered markdown and unrendered math.

Approved scope decisions (do not re-litigate):
- **Math:** keep the exact current renderer (markdown-it-texmath + KaTeX) and inline its JS/CSS plus the KaTeX **woff2 fonts** — output stays byte-identical to the live view; no MathML/SVG conversion, no new toolchain.
- **Assets:** **vendor** the library files into the repo and read them at build time, so export is hermetic and works offline (no fetch-at-build).
- **Prose fonts:** embed figures and math **only**. Leave the Source Serif 4 / IBM Plex Mono display fonts (Google Fonts) and htmx/sse on CDN; offline they fall back to system serif/mono (readable) and htmx features are already unused in standalone. Do **not** inline display fonts.

Build on the single unified standalone machinery from `[unify-static-export](../unify-static-export/task.md)` and `[subtree-export](../subtree-export/task.md)` — `render_standalone_html()` / `_build_standalone_fragments()` and the `standalone` template flag. Do **not** build a parallel renderer or a second template. The live `serve` path stays CDN-backed and otherwise unchanged; only the standalone (`generate` / `GET /export`) output gains embedding. Both whole-tree and subtree exports get it.

### Deliverable 1 — Base64-embed figures

At export build time, produce a JS map (e.g. `STANDALONE_IMAGES`) of `{ <client-key>: <data-URI> }` and inject it into the standalone template the same way `standalone_plan_dir` is injected ([plan_dashboard.py:1212 area / template var](../../../../skills/task-system/scripts/plan_dashboard.py#L1061)). For every task in the (possibly re-based) export tree, find the relative image references in its raw markdown body — both `![alt](src)` and any `<img src=...>` forms — skip absolute / `http(s):` / `data:` srcs, resolve each remaining src against the task's real on-disk dir (`task.dir_path` is deliberately left un-rebased by [`_rebase_subtree`](../../../../skills/task-system/scripts/plan_dashboard.py#L990) precisely so figure bytes stay reachable), read the bytes, and base64-encode with the correct MIME (png/jpeg/gif/svg+xml/webp by extension). Key the map by the **exact string the client computes** in the `img[src]` loop ([base.html:1370](../../../../skills/task-system/scripts/templates/base.html#L1370)): `taskPath + '/' + src` for a task body, and bare `src` for the root body (empty `taskPath`) — use the re-based `task.path`, not `dir_path`, for the key. Then in that client loop's standalone branch, look the key up in `STANDALONE_IMAGES` first: if present, set the `<img src>` to the data URI; if absent, fall back to today's relative-path rewrite unchanged. Server (`!STANDALONE`) mode is untouched.

### Deliverable 2 — Vendor and inline the render libraries

Vendor the rendering assets under `skills/task-system/scripts/vendor/` (new dir), pinned to the versions the CDN tags currently use — markdown-it@14, markdown-it-texmath@1, katex@0.16 (`katex.min.js`, `katex.min.css`, and the `fonts/KaTeX_*.woff2` set). Record the exact resolved versions and their source URLs in a short `vendor/README.md` so the pin is auditable and re-fetchable. KaTeX's CSS references its fonts via `url(fonts/KaTeX_*.woff2)`; build an **inlined** CSS string by rewriting each `@font-face` to a single base64 `data:` woff2 URI (woff2 only — drop the woff/ttf fallback sources to keep size down; modern browsers all take woff2).

Gate the head asset tags on the `standalone` flag: in standalone mode emit the markdown-it / texmath / KaTeX JS as inline `<script>` blocks and the font-inlined KaTeX CSS as an inline `<style>`, instead of the four CDN `<link>`/`<script>` tags at [base.html:12–15](../../../../skills/task-system/scripts/templates/base.html#L12); in server mode keep the CDN tags exactly as today. Pass the inlined JS/CSS strings as template vars computed only on the standalone path (a small build helper that reads the vendored files and applies the CSS font-inlining transform). Leave the Google Fonts link and htmx/sse tags as-is in both modes (a failed external `<script src>` offline fires `onerror` and does not halt later inline scripts, so the page still runs; prose falls back to system fonts).

### Scope boundaries

- No parallel renderer, no second template, no change to `serve` output or to whole-tree-vs-subtree scoping logic.
- `plan_dashboard.py` and `base.html` are **not** in the generated-from-spec set (that set is the direct-mode role references and Codex agent files); this task does not touch generated artifacts and needs no `sync_codex_agents.py` run.
- Keep edits surgical and within this project worktree.

## Validation

Exercise the **real end-user path**, not just routes/units (a prior round shipped three dashboard bugs that passed isolated checks but failed when the actual file was opened — open the produced artifact and inspect the rendered DOM):

- **Real offline open.** Export the `hyperlink-styling` subtree (`generate --root task-system/dashboard/hyperlink-styling`, or the Share button) — it has real figures (`attachments/links-light.png`, `links-dark.png`). Open the produced file via `file://` **with the network disabled / DevTools offline**, and confirm: the two figures display, the markdown is rendered (not raw), and any `$…$` math renders via KaTeX. Add a task whose body contains a math expression to the fixture if no exported task has one, so math is actually exercised; a temporary synthetic plan-tree fixture (task with one image + one `$…$`) opened offline is an acceptable way to prove both at once.
- **Source/DOM evidence.** The standalone output contains `data:image/...;base64,` for each referenced figure, contains the inlined KaTeX `@font-face` data-URI woff2 and the inlined markdown-it/texmath/KaTeX `<script>` bodies, and contains **no** required CDN `<link>`/`<script src>` for markdown-it / texmath / katex (Google Fonts + htmx/sse CDN tags may remain). The `img[src]` loop consults `STANDALONE_IMAGES` before the relative-path fallback.
- **Server mode unchanged.** A `serve`-rendered page still uses the CDN tags and is otherwise byte-equivalent to before; whole-tree `generate` with no `--root` still works.
- **Tests.** Add coverage to `skills/task-system/scripts/test_task_system.py` / `test_dashboard.py`: figure-key mapping + data-URI emission, inlined-asset presence and CDN-tag absence in standalone, server-mode CDN tags retained. Client-side JS has no pytest runner here, so behavioral checks of the `img` loop / render path are node harnesses; committed pytest are source-presence — state which is which honestly in `## Results`. Run `uv run pytest skills/task-system/scripts/test_task_system.py skills/task-system/scripts/test_dashboard.py`.

## Results

_(to be filled by the implementer)_
