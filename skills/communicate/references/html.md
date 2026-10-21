# HTML Artifacts

An HTML artifact is one self-contained interactive page, committed as a file. The same bytes render in the superRA dashboard's sandboxed frame, open from disk, and publish unchanged to claude.ai.

**Design craft:** the harness has an artifact design skill (`artifact-design` on Claude): load it. Where it conflicts with this file, this file wins: keep the complete document below rather than its hosted skeleton, and add no `claude:` meta tags.

## When a page earns its place

- **Interaction answers a question a fixed view cannot:** filtering many series, hovering for exact values, switching specifications, browsing a grid of estimates. One fixed view: a PNG or a table.
- **It supplements, never replaces.** Key figures stay PNG in `## Results`; the page is an extra linked view.

## File format

- **A complete document:** `<!doctype html>`, `<html>`, a `<head>` with `<meta charset="utf-8">`, a viewport meta, and a `<title>` that names the page, then `<body>`.
- **Everything inline.** CSS in `<style>`, JS in `<script>`, data in a `<script type="application/json" id="data">` block read with `JSON.parse(document.getElementById("data").textContent)`.
- **At most 2 MiB.** Larger: aggregate or thin the data.

## Libraries

- **Plain HTML, SVG, or Canvas** when no library does substantial work.
- **Otherwise a UMD build by `<script src>`**, pinned to an exact version and placed before the inline script that uses its global, from only these hosts:
  - `https://cdnjs.cloudflare.com`
  - `https://cdn.jsdelivr.net/npm/`
  - `https://unpkg.com`
- **Stylesheets only from `https://fonts.googleapis.com`**, font files from `https://fonts.gstatic.com`. A library's own CSS goes inline.

## The sandbox fails silently

The page runs in an opaque-origin frame with no access to the parent page, cookies, or dashboard APIs. These fail without an error the reader sees:

- **No network.** `fetch` and XHR are blocked; embed every byte the page shows. Images are `data:` or `blob:` URIs. No iframes, media, or `<object>`.
- **Storage may throw.** Wrap every `localStorage` access in `try`/`catch`; the page renders correctly without it.
- **No forms or modal dialogs.** `<form>` never submits and `alert`/`confirm`/`prompt` do nothing: drive the page from `input`, `change`, and `click` handlers and in-page UI.
- **No downloads on claude.ai.** A download link works only in the dashboard; never make it the only way to the data.
- **External links:** `<a href="…" target="_blank" rel="noopener">`.
- **Narrow width.** The page fits phone width (about 400px) with no horizontal page scroll: rows wrap, and wide tables and plots scroll in their own `overflow-x: auto` box.

## Theme

The host sets `data-theme="light"` or `"dark"` on `<html>` before page scripts run and updates it live, or leaves it unset to follow the system.

- **Define every color as a token** in this shape:

  ```css
  :root { --bg: …; --fg: …; --accent: … }
  @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: …; --fg: …; --accent: …; color-scheme: dark } }
  :root[data-theme="dark"] { --bg: …; --fg: …; --accent: …; color-scheme: dark }
  body { background: var(--bg); color: var(--fg) }
  ```

- **Script-drawn colors** (canvas, chart libraries) read the tokens and redraw on either change:

  ```js
  const token = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  new MutationObserver(draw).observe(document.documentElement, {attributeFilter: ["data-theme"]});
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", draw);
  ```

## Computed numbers come from a generator

- **A page showing computed numbers is written by a generator script**, never typed by hand. The script reads the result files and writes the whole page, data block included; register it as a reproduction step per `superRA:reproducibility`.
- **Deterministic bytes:** no timestamps or random IDs, sorted keys, fixed number formatting, so a rebuild reproduces the committed file.

## Save and link

- **Save under the owning task's `attachments/`** as a task companion; lifecycle and provenance per [task-companion-files.md](../../using-superra/references/task-companion-files.md).
- **Link from `## Results`** with a plain link, `[Alpha explorer](attachments/alpha-explorer.html)`, beside the PNG it supplements.

## Publish on request

When the harness has an artifact-publishing tool (`Artifact` on Claude), publish only when the researcher asks to publish or share:

- **Publish the committed file** as is.
- **Record the returned URL next to the attachment link** in `## Results`.
- **After the page changes, republish to the same URL.**
