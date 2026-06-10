---
title: "Self-contained export: embed figures and math"
status: approved
depends_on:
  - subtree-export
tags: []
created: 2026-06-01
---

## Objective

Make the standalone HTML export **fully self-contained for figures and math**, so a shared/downloaded single file renders correctly when moved away from the repo and when opened with no network. Today the export embeds task *data* offline (no calls back to the dashboard server) but is neither figure-complete nor CDN-independent: figures are referenced by a relative path into the `superRA` task tree (the `[subtree-export](../subtree-export/task.md)` "Known limitation" — figures break in a downloaded file), and all rendering libraries load from CDNs ([base.html:7–15](../../../../skills/task-tree/scripts/templates/base.html#L7) — Google Fonts, htmx + sse, markdown-it, markdown-it-texmath, KaTeX CSS+JS). Bodies are raw markdown rendered **client-side** by markdown-it + markdown-it-texmath + KaTeX ([base.html:1267](../../../../skills/task-tree/scripts/templates/base.html#L1267), delimiters `dollars`), so without those libs a moved/offline file shows unrendered markdown and unrendered math.

Approved scope decisions (do not re-litigate):
- **Math:** keep the exact current renderer (markdown-it-texmath + KaTeX) and inline its JS/CSS plus the KaTeX **woff2 fonts** — output stays byte-identical to the live view; no MathML/SVG conversion, no new toolchain.
- **Assets:** **vendor** the library files into the repo and read them at build time, so export is hermetic and works offline (no fetch-at-build).
- **Prose fonts:** embed figures and math **only**. Leave the Source Serif 4 / IBM Plex Mono display fonts (Google Fonts) and htmx/sse on CDN; offline they fall back to system serif/mono (readable) and htmx features are already unused in standalone. Do **not** inline display fonts.

Build on the single unified standalone machinery from `[unify-static-export](../unify-static-export/task.md)` and `[subtree-export](../subtree-export/task.md)` — `render_standalone_html()` / `_build_standalone_fragments()` and the `standalone` template flag. Do **not** build a parallel renderer or a second template. The live `serve` path stays CDN-backed and otherwise unchanged; only the standalone (`generate` / `GET /export`) output gains embedding. Both whole-tree and subtree exports get it.

### Deliverable 1 — Base64-embed figures

At export build time, produce a JS map (e.g. `STANDALONE_IMAGES`) of `{ <client-key>: <data-URI> }` and inject it into the standalone template the same way `standalone_plan_dir` is injected ([plan_dashboard.py:1212 area / template var](../../../../skills/task-tree/scripts/plan_dashboard.py#L1061)). For every task in the (possibly re-based) export tree, find the relative image references in its raw markdown body — both `![alt](src)` and any `<img src=...>` forms — skip absolute / `http(s):` / `data:` srcs, resolve each remaining src against the task's real on-disk dir (`task.dir_path` is deliberately left un-rebased by [`_rebase_subtree`](../../../../skills/task-tree/scripts/plan_dashboard.py#L990) precisely so figure bytes stay reachable), read the bytes, and base64-encode with the correct MIME (png/jpeg/gif/svg+xml/webp by extension). Key the map by the **exact string the client computes** in the `img[src]` loop ([base.html:1370](../../../../skills/task-tree/scripts/templates/base.html#L1370)): `taskPath + '/' + src` for a task body, and bare `src` for the root body (empty `taskPath`) — use the re-based `task.path`, not `dir_path`, for the key. Then in that client loop's standalone branch, look the key up in `STANDALONE_IMAGES` first: if present, set the `<img src>` to the data URI; if absent, fall back to today's relative-path rewrite unchanged. Server (`!STANDALONE`) mode is untouched.

### Deliverable 2 — Vendor and inline the render libraries

Vendor the rendering assets under `skills/task-tree/scripts/vendor/` (new dir), pinned to the versions the CDN tags currently use — markdown-it@14, markdown-it-texmath@1, katex@0.16 (`katex.min.js`, `katex.min.css`, and the `fonts/KaTeX_*.woff2` set). Record the exact resolved versions and their source URLs in a short `vendor/README.md` so the pin is auditable and re-fetchable. KaTeX's CSS references its fonts via `url(fonts/KaTeX_*.woff2)`; build an **inlined** CSS string by rewriting each `@font-face` to a single base64 `data:` woff2 URI (woff2 only — drop the woff/ttf fallback sources to keep size down; modern browsers all take woff2).

Gate the head asset tags on the `standalone` flag: in standalone mode emit the markdown-it / texmath / KaTeX JS as inline `<script>` blocks and the font-inlined KaTeX CSS as an inline `<style>`, instead of the four CDN `<link>`/`<script>` tags at [base.html:12–15](../../../../skills/task-tree/scripts/templates/base.html#L12); in server mode keep the CDN tags exactly as today. Pass the inlined JS/CSS strings as template vars computed only on the standalone path (a small build helper that reads the vendored files and applies the CSS font-inlining transform). Leave the Google Fonts link and htmx/sse tags as-is in both modes (a failed external `<script src>` offline fires `onerror` and does not halt later inline scripts, so the page still runs; prose falls back to system fonts).

### Scope boundaries

- No parallel renderer, no second template, no change to `serve` output or to whole-tree-vs-subtree scoping logic.
- `plan_dashboard.py` and `base.html` are **not** in the generated-from-spec set (that set is the direct-mode role references and Codex agent files); this task does not touch generated artifacts and needs no `sync_codex_agents.py` run.
- Keep edits surgical and within this project worktree.

## Validation

Exercise the **real end-user path**, not just routes/units (a prior round shipped three dashboard bugs that passed isolated checks but failed when the actual file was opened — open the produced artifact and inspect the rendered DOM):

- **Real offline open.** Export the `hyperlink-styling` subtree (`generate --root task-tree/dashboard/hyperlink-styling`, or the Share button) — it has real figures (`attachments/links-light.png`, `links-dark.png`). Open the produced file via `file://` **with the network disabled / DevTools offline**, and confirm: the two figures display, the markdown is rendered (not raw), and any `$…$` math renders via KaTeX. Add a task whose body contains a math expression to the fixture if no exported task has one, so math is actually exercised; a temporary synthetic plan-tree fixture (task with one image + one `$…$`) opened offline is an acceptable way to prove both at once.
- **Source/DOM evidence.** The standalone output contains `data:image/...;base64,` for each referenced figure, contains the inlined KaTeX `@font-face` data-URI woff2 and the inlined markdown-it/texmath/KaTeX `<script>` bodies, and contains **no** required CDN `<link>`/`<script src>` for markdown-it / texmath / katex (Google Fonts + htmx/sse CDN tags may remain). The `img[src]` loop consults `STANDALONE_IMAGES` before the relative-path fallback.
- **Server mode unchanged.** A `serve`-rendered page still uses the CDN tags and is otherwise byte-equivalent to before; whole-tree `generate` with no `--root` still works.
- **Tests.** Add coverage to `skills/task-tree/scripts/test_task_tree.py` / `test_dashboard.py`: figure-key mapping + data-URI emission, inlined-asset presence and CDN-tag absence in standalone, server-mode CDN tags retained. Client-side JS has no pytest runner here, so behavioral checks of the `img` loop / render path are node harnesses; committed pytest are source-presence — state which is which honestly in `## Results`. Run `uv run pytest skills/task-tree/scripts/test_task_tree.py skills/task-tree/scripts/test_dashboard.py`.

## Results

The standalone export is now fully self-contained for figures and math. Both deliverables ship on the single unified standalone machinery (`render_standalone_html()` / `_build_standalone_fragments()` / the `standalone` flag) — no parallel renderer, no second template, no change to `serve` output. The live `serve` path stays CDN-backed and byte-equivalent to before; both whole-tree and subtree exports gain the embedding.

### Deliverable 1 — Base64-embed figures

[`_build_standalone_images(scoped_root)`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1076) builds a `{ client-key -> data-URI }` map injected into the template as `standalone_images` and surfaced client-side as `var STANDALONE_IMAGES` ([base.html:1227](../../../../skills/task-tree/scripts/templates/base.html#L1227)). For every task in the (re-based) export tree it scans the raw markdown `body` for image refs — both `![alt](src)` and `<img src=...>` ([`_iter_body_image_srcs`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1046)) — skips absolute / `http(s):` / `data:` srcs ([`_is_embeddable_src`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1064)), resolves each remaining src against the task's **real on-disk** `dir_path` (left un-rebased by `_rebase_subtree` so figure bytes stay reachable), reads the bytes, and base64-encodes with the extension's MIME (png/jpeg/gif/svg+xml/webp). The key is the exact string the client computes in the `img[src]` loop: `task.path + '/' + src` for a task body, bare `src` for the root body (empty re-based path).

The client `img[src]` loop's standalone branch now consults `STANDALONE_IMAGES` first ([base.html:1394](../../../../skills/task-tree/scripts/templates/base.html#L1394)): on a hit it sets `<img src>` to the data URI; on a miss it falls back to today's relative-path rewrite unchanged. Server (`!STANDALONE`) mode is untouched.

### Deliverable 2 — Vendor and inline the render libraries

Vendored under [`skills/task-tree/scripts/vendor/`](../../../../skills/task-tree/scripts/vendor/README.md): `markdown-it.min.js` (14.2.0), `katex.min.js` + `katex.min.css` (0.16.47), `texmath.min.js` (1.0.0), and all 20 `fonts/KaTeX_*.woff2`. Exact versions, source URLs, SHA-256s, and a re-fetch recipe are in `vendor/README.md` so the pin is auditable. The major-version CDN tags in `base.html` resolved to these exact versions on 2026-06-01 (via the jsdelivr `x-jsd-version` header).

[`_build_standalone_assets()`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1149) reads the vendored files and returns the inline JS bodies plus a font-inlined KaTeX CSS. [`_inline_katex_css`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1121) rewrites each `@font-face` so its `src` is a single base64 `data:font/woff2` URI, dropping the woff/ttf fallback sources (woff2 only). The head asset tags are gated on `standalone` ([base.html:12](../../../../skills/task-tree/scripts/templates/base.html#L12)): standalone mode emits the three libraries as inline `<script>` blocks and the font-inlined CSS as an inline `<style>`; server mode keeps the four CDN `<link>`/`<script>` tags exactly as before. Google Fonts and htmx/sse stay on CDN in both modes (offline they fail gracefully — `onerror` does not halt later inline scripts; prose falls back to system serif/mono). A defensive `</script>`/`</style>` → `<\/...` escape guards a future re-pin whose body might contain a literal closer (none do today).

### Validation

- **Real offline open (behavioral, headless Chromium with the network HARD-BLOCKED).** A synthetic plan-tree fixture (one task with one figure + one `$e^{i\pi}+1=0$`) exported via `generate --root`, opened via `file://` with every non-`file://` request aborted: the figure renders with `naturalWidth > 0` (bytes decoded from the data URI), KaTeX produced its `.katex` DOM, and the markdown is rendered (not raw). The only blocked external requests were Google Fonts + htmx/sse (the allowed-to-remain CDN tags) — no markdown-it/katex/texmath fetch, proving self-containment. The named real-figure fixture — the `task-tree/dashboard/hyperlink-styling` subtree (`attachments/links-light.png`, `links-dark.png`) — exported and opened offline the same way: both figures decode (2/2, `naturalWidth > 0`).
- **Source/DOM evidence.** The standalone output contains a `data:image/...;base64,` per referenced figure, the 20 inlined KaTeX `@font-face` `data:font/woff2;base64,` URIs, the inline markdown-it/texmath/KaTeX `<script>` bodies, and **no** CDN `<link>`/`<script src>` for markdown-it / texmath / katex (Google Fonts + htmx/sse remain). The `img[src]` loop consults `STANDALONE_IMAGES` before the relative-path fallback.
- **Server mode unchanged.** A `serve`-rendered page still uses the four CDN render tags, inlines nothing (no woff2 data URI, no `STANDALONE_IMAGES`), and is `window.STANDALONE = false`. Whole-tree `generate` with no `--root` works; `generate_dashboard(root=None)` stays byte-identical to the bare call (existing regression test).
- **Tests.** `uv run pytest skills/task-tree/scripts/test_task_tree.py skills/task-tree/scripts/test_dashboard.py` → **273 passed** (broader run incl. `tests/` + `test_worktree_selector.py` → 362 passed). New: `TestStandaloneSelfContained` (9 tests) in `test_task_tree.py` and `test_served_page_keeps_cdn_render_tags` in `test_dashboard.py`. These committed pytest are **source-presence / build-helper unit** checks (data-URI emission, image-map keys + MIME + remote/absolute/HTML-img handling, CDN-tag absence in standalone, woff2-only font inlining, vendor-file presence, server-mode CDN retained). The **behavioral** browser check (figure actually decodes + KaTeX actually renders from an offline `file://` open) is the headless-Chromium run above — recorded here, not committed, since this suite has no browser harness.

### Final diff self-check

**Final diff self-check:** `git diff 30a9dd48..HEAD`, checked hunk-by-hunk; surviving-change classes — standalone build helpers in `plan_dashboard.py` (`_build_standalone_images` / `_iter_body_image_srcs` / `_is_embeddable_src` / `_build_standalone_assets` / `_inline_katex_css`), standalone-gated template branches in `base.html` (head asset tags + `img[src]` loop), vendored render assets under `skills/task-tree/scripts/vendor/` (markdown-it / texmath / katex JS+CSS + 20 `KaTeX_*.woff2` + `vendor/README.md`), new pytest coverage (`TestStandaloneSelfContained` in `test_task_tree.py`, `test_served_page_keeps_cdn_render_tags` in `test_dashboard.py`), and this task.md. Every hunk is justified by the approved objective (figure embedding, vendored/inlined render libs gated on the `standalone` flag, their tests, and the vendored assets) — minimum net diff, no out-of-scope hunks, no unrelated cleanup, no formatting churn, no base-side restorations, `serve` path untouched. No suspicious hunks.

### Notes / caveats

- The whole-tree default-output (`dashboard.html` written into `superRA`, gitignored) is not committed — regenerate-only.
- The downloaded-file figure-portability limitation from `[subtree-export](../subtree-export/task.md)` is now **resolved** for embedded figures: figures travel as base64 data URIs, so a file moved to Downloads still shows them. The relative-path fallback only fires for srcs with no embedded bytes.
- `plan_dashboard.py` and `base.html` are not in the generated-from-spec set; no `sync_codex_agents.py` run is needed.

## Review Notes

*(Retrospective audit, 2026-06-10 — MINOR item only; status stays `approved`.)*

1. **MINOR** — version split-brain between serve and export: the live page loads floating major CDN tags ([base.html:21-24](../../../../skills/task-tree/scripts/templates/base.html#L21): `markdown-it@14`, `katex@0.16`, `texmath@1`) while the export inlines the exact pins recorded in [vendor/README.md](../../../../skills/task-tree/scripts/vendor/README.md) (14.2.0 / 0.16.47 / 1.0.0). The CDN can advance within a major silently, after which serve and export render with different library versions and the README's "pinned versions match the CDN tags" claim drifts; nothing couples the two beyond that sentence. Pin the CDN tags to the exact vendored versions and add a small guard test asserting the tag versions in `base.html` match the vendor README table.
