# Vendored render libraries (standalone export only)

These files are read at **export build time** by `plan_dashboard.py` and inlined into the standalone single-file dashboard so a downloaded/offline file renders markdown, math, and syntax-highlighted code with zero network calls. The live `serve` path still loads the same libraries from the jsdelivr CDN (`base.html` head); these vendored copies are used **only** in standalone mode.

The pinned versions match the CDN tags in `templates/base.html` (`markdown-it@14`, `katex@0.16`, `markdown-it-texmath@1`, `@highlightjs/cdn-assets@11`, `dompurify@3`). The markdown/math CDN tags resolved to the exact versions below on 2026-06-01; the highlight.js tag resolved on 2026-06-11; the dompurify tag resolved on 2026-06-15.

## Pinned versions and sources

| File | Package | Version | Source URL |
| --- | --- | --- | --- |
| `markdown-it.min.js` | markdown-it | 14.2.0 | `https://cdn.jsdelivr.net/npm/markdown-it@14.2.0/dist/markdown-it.min.js` |
| `katex.min.js` | katex | 0.16.47 | `https://cdn.jsdelivr.net/npm/katex@0.16.47/dist/katex.min.js` |
| `katex.min.css` | katex | 0.16.47 | `https://cdn.jsdelivr.net/npm/katex@0.16.47/dist/katex.min.css` |
| `texmath.min.js` | markdown-it-texmath | 1.0.0 | `https://cdn.jsdelivr.net/npm/markdown-it-texmath@1.0.0/texmath.min.js` |
| `highlight.min.js` | @highlightjs/cdn-assets | 11.11.1 | `https://cdn.jsdelivr.net/npm/@highlightjs/cdn-assets@11.11.1/highlight.min.js` |
| `languages/julia.min.js` | @highlightjs/cdn-assets | 11.11.1 | `https://cdn.jsdelivr.net/npm/@highlightjs/cdn-assets@11.11.1/languages/julia.min.js` |
| `purify.min.js` | dompurify | 3.4.10 | `https://cdn.jsdelivr.net/npm/dompurify@3.4.10/dist/purify.min.js` |
| `fonts/KaTeX_*.woff2` | katex | 0.16.47 | `https://cdn.jsdelivr.net/npm/katex@0.16.47/dist/fonts/<name>.woff2` |

The 20 `fonts/KaTeX_*.woff2` files are every font `katex.min.css` references via `url(fonts/KaTeX_*.woff2)`. Only the **woff2** sources are vendored; the build helper rewrites each `@font-face` to a single base64 `data:` woff2 URI (the woff/ttf fallback sources are dropped — modern browsers all accept woff2).

`purify.min.js` is DOMPurify. markdown-it runs with `html:true`, so every `md.render(...)` result is sanitized through `DOMPurify.sanitize(..., { ADD_ATTR: ['style', 'class'] })` before DOM insertion (`renderMarkdown` in `base.html`). The default allowlist strips scripts/iframes/event handlers/`javascript:` URLs; `ADD_ATTR` keeps `style`/`class` so agent-authored HTML can use inline styles and dashboard CSS tokens. Because exports are published to GitHub Pages, sanitization is a hard gate on untrusted task content, not optional.

`highlight.min.js` is the highlight.js "common" bundle (36 languages, covering bash/shell, python, yaml, markdown, json among the doc/task content). It does **not** include Julia, so `languages/julia.min.js` is vendored alongside it; loaded after the bundle, that module registers Julia onto the global `hljs`. Highlight colors are theme-driven CSS (`--hl-*` tokens in `base.html`), so no highlight.js theme stylesheet is vendored. To extend language coverage, vendor more `languages/<lang>.min.js` modules from the same CDN path and load each after the bundle.

## SHA-256 (top-level files)

```
b4c12c3d2258bbeb272ff688fea9cbf991925288d19c03ce5cacb486dc0112e4  markdown-it.min.js
a29d2961d3146de5949d78ac7c1a9d93ae54955bad22a6db4fbe836e88e8bf48  katex.min.js
0289a02cf451a44dd73add683a09644252363871ac11713a647b732cee8b1ee3  katex.min.css
b01b706e6d23e8270a55228fdba35b557127b6f2af5b4c23ca22b15bdbd1c09d  texmath.min.js
c4a399dd6f488bc97a3546e3476747b3e714c99c57b9473154c6fb8d259b9381  highlight.min.js
03330298d96dc711b8f66fc8075ff4a1ab9f830a87c5c6c9ae0503733ba99da4  languages/julia.min.js
9aca84b86a0c35926d47994f354b37116044aab0aac9874f35a44322a5c96565  purify.min.js
```

## Re-fetch recipe

To re-pin against the current CDN major tags (and update the table/hashes above):

```sh
DST=skills/task-tree/scripts/vendor
curl -sL "https://cdn.jsdelivr.net/npm/markdown-it@14/dist/markdown-it.min.js"      -o "$DST/markdown-it.min.js"
curl -sL "https://cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.js"                -o "$DST/katex.min.js"
curl -sL "https://cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.css"               -o "$DST/katex.min.css"
curl -sL "https://cdn.jsdelivr.net/npm/markdown-it-texmath@1/texmath.min.js"        -o "$DST/texmath.min.js"
curl -sL "https://cdn.jsdelivr.net/npm/@highlightjs/cdn-assets@11/highlight.min.js" -o "$DST/highlight.min.js"
curl -sL "https://cdn.jsdelivr.net/npm/dompurify@3/dist/purify.min.js"             -o "$DST/purify.min.js"
mkdir -p "$DST/languages"
curl -sL "https://cdn.jsdelivr.net/npm/@highlightjs/cdn-assets@11/languages/julia.min.js" -o "$DST/languages/julia.min.js"
# Fonts: every name katex.min.css references via url(fonts/KaTeX_*.woff2)
for f in $(grep -oE 'fonts/KaTeX_[A-Za-z0-9_-]+\.woff2' "$DST/katex.min.css" | sort -u); do
  curl -sL "https://cdn.jsdelivr.net/npm/katex@0.16/dist/$f" -o "$DST/$f"
done
```

The exact resolved version of a major CDN tag is in the response's `x-jsd-version` header (`curl -sI <url> | grep x-jsd-version`).
