# Vendored render libraries (standalone export only)

These files are read at **export build time** by `plan_dashboard.py` and inlined into the standalone single-file dashboard so a downloaded/offline file renders markdown and math with zero network calls. The live `serve` path still loads the same libraries from the jsdelivr CDN (`base.html` head); these vendored copies are used **only** in standalone mode.

The pinned versions match the CDN tags in `templates/base.html` (`markdown-it@14`, `katex@0.16`, `markdown-it-texmath@1`). The major-version CDN tags resolved to the exact versions below on 2026-06-01.

## Pinned versions and sources

| File | Package | Version | Source URL |
| --- | --- | --- | --- |
| `markdown-it.min.js` | markdown-it | 14.2.0 | `https://cdn.jsdelivr.net/npm/markdown-it@14.2.0/dist/markdown-it.min.js` |
| `katex.min.js` | katex | 0.16.47 | `https://cdn.jsdelivr.net/npm/katex@0.16.47/dist/katex.min.js` |
| `katex.min.css` | katex | 0.16.47 | `https://cdn.jsdelivr.net/npm/katex@0.16.47/dist/katex.min.css` |
| `texmath.min.js` | markdown-it-texmath | 1.0.0 | `https://cdn.jsdelivr.net/npm/markdown-it-texmath@1.0.0/texmath.min.js` |
| `fonts/KaTeX_*.woff2` | katex | 0.16.47 | `https://cdn.jsdelivr.net/npm/katex@0.16.47/dist/fonts/<name>.woff2` |

The 20 `fonts/KaTeX_*.woff2` files are every font `katex.min.css` references via `url(fonts/KaTeX_*.woff2)`. Only the **woff2** sources are vendored; the build helper rewrites each `@font-face` to a single base64 `data:` woff2 URI (the woff/ttf fallback sources are dropped — modern browsers all accept woff2).

## SHA-256 (top-level files)

```
b4c12c3d2258bbeb272ff688fea9cbf991925288d19c03ce5cacb486dc0112e4  markdown-it.min.js
a29d2961d3146de5949d78ac7c1a9d93ae54955bad22a6db4fbe836e88e8bf48  katex.min.js
0289a02cf451a44dd73add683a09644252363871ac11713a647b732cee8b1ee3  katex.min.css
b01b706e6d23e8270a55228fdba35b557127b6f2af5b4c23ca22b15bdbd1c09d  texmath.min.js
```

## Re-fetch recipe

To re-pin against the current CDN major tags (and update the table/hashes above):

```sh
DST=skills/task-system/scripts/vendor
curl -sL "https://cdn.jsdelivr.net/npm/markdown-it@14/dist/markdown-it.min.js"      -o "$DST/markdown-it.min.js"
curl -sL "https://cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.js"                -o "$DST/katex.min.js"
curl -sL "https://cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.css"               -o "$DST/katex.min.css"
curl -sL "https://cdn.jsdelivr.net/npm/markdown-it-texmath@1/texmath.min.js"        -o "$DST/texmath.min.js"
# Fonts: every name katex.min.css references via url(fonts/KaTeX_*.woff2)
for f in $(grep -oE 'fonts/KaTeX_[A-Za-z0-9_-]+\.woff2' "$DST/katex.min.css" | sort -u); do
  curl -sL "https://cdn.jsdelivr.net/npm/katex@0.16/dist/$f" -o "$DST/$f"
done
```

The exact resolved version of a major CDN tag is in the response's `x-jsd-version` header (`curl -sI <url> | grep x-jsd-version`).
