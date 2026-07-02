---
title: "superRA Documentation"
status: not-started
depends_on: []
tags: []
created: 2026-06-11
---

## Objective

Root of the superRA documentation site. This task tree is the *doc source*: each node's `## Objective` body is one rendered page, exported to static HTML by the task-tree dashboard in doc-mode (`docs/build_site.sh`) and deployed to GitHub Pages. Display order follows numeric directory prefixes; `status` and `depends_on` are unused here and hidden by doc-mode at render time. Authoring rules are the contract in this file's source (the comment below).

<!-- Docs-tree authoring contract — the binding rules for every page under docs/site/.
Source-only: HTML comments do not render, so this contract never appears on the site;
doc-page authors inherit it via `task read` of any node under this root.

- Source location: docs/site/. Doc sources are committed; the generated site HTML is
  CI-built by docs/build_site.sh (GitHub Actions on push to main) and never committed.
- Frontmatter: each node uses `title` only. `status` and `depends_on` stay at their
  scaffold defaults (`not-started`, `[]`); doc-mode hides them at render time.
- Page body: the page content lives under `## Objective` (the section the export renders
  as the page). Use `## ` subheadings within a page for structure — doc-mode renders every
  `## ` section as a plain heading. Do not add `## Results` / `## Review Notes` to doc
  nodes; those are task-workflow sections, not doc content.
- Ordering: numeric directory prefixes (01-, 02-, ...) set display order; they are
  display-only (doc nodes carry no real dependencies).
- Cross-page links: hash links #/<path> where <path> is the doc-tree-relative node path,
  e.g. [the domain skills](#/03-domain-skills); a nested page uses its full directory
  path, e.g. #/04-utility-skills/01-task-tree/02-cli-commands. The export's nav already
  shows the descent, so link a page to its parent only where the prose hands the reader
  back up, not on every page by rote.
- Repo-file links: to cite a skill/agent/source file as authority, write a normal
  repo-relative link target; the build re-bases it to the GitHub blob URL at the built
  ref via --repo-file-base (see docs/build_site.sh). Never hardcode full GitHub URLs.
- Sibling exports: pages link to the showcase HTML exports by relative basename;
  docs/build_site.sh passes --doc-local-link for each so those links stay relative
  instead of being rebased.
- Figures/screenshots: committed under docs/site/<page>/attachments/ and embedded with
  ![caption](attachments/<file>); the export base64-inlines images, so node-relative
  paths are correct. Prefer a live mermaid diagram over a raster where a diagram suffices.
- Public-repo hygiene: all examples use placeholder or hypothetical research content —
  no personal data, real group names, real paths, or private query results.
- Authority, not paraphrase: doc pages teach the human journey and link to the canonical
  skill/agent file for behavior detail; they never become a second authority for
  agent-facing behavior.
-->
