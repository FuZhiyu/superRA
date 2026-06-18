---
title: "Revise IA Contract for Nested Structure + Scaffold New Page Stubs"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Revise the information-architecture contract to describe the nested, Reference-dissolved structure, then scaffold the empty page stubs the content tasks will fill. The IA contract is the authoritative sitemap; leaving it describing the old flat structure plus the `05-reference/` section would be a stale-content violation. This is the gating task — `02`, `03`, and `05` build to the contract this task approves.

**Edit `superRA/docs-site/01-information-architecture/task.md` Results in place** (this task's deliverable lives in another task's file, by design — that file owns the sitemap):

- **§1 knowledge-state table:** update the Domain Skills and Utility Skills rows to reflect overview-plus-per-skill-page reading; the reader still exits knowing which skills exist and the design idea behind each, now reachable one descent down.
- **§2 sitemap:** replace the flat `03-domain-skills`/`04-utility-skills` rows and the entire `05-reference/` block with the new tree: `03-domain-skills/` (overview) over `01-econ-data-analysis`/`02-theory-modeling`/`03-writing`; `04-utility-skills/` (overview) over `01-task-tree` (itself over `01-task-file`/`02-cli-commands`/`03-status-and-frontier`/`04-dashboard`, the last being a new user-facing page on the dashboard's export/comments/worktree features), `02-semantic-merge`, `03-result-protection`, `04-refactor-and-integrate`, `05-report-in-markdown`, `06-worktree-data-sync`, `07-zotero-paper-reader`, `08-mistral-pdf-to-markdown`; top-level `05-glossary`, `06-faq`, `07-hooks`, `08-showcase`. Keep the "Teaches / Links to (authority) / owning content task" columns; owning task is this `13-` subtree. Record that `04-skills-and-agents` is dropped and why (inventory absorbed into the two overviews; Stage→load manifest is internal).
- **§3 authoring contract:** confirm it still holds for three-level nesting and detail subpages; add a line only if nesting exposes a genuine gap (e.g. how a detail subpage links up to its parent skill page). Do not restate unchanged rules.
- **Renumbering note:** record the top-level renumber (glossary/faq/hooks → 05/06/07, showcase → 08) and the rationale, mirroring §2's existing renumbering-rationale style.

**Scaffold the genuinely-new empty page stubs** under `docs/site/` (directories with `title`-only frontmatter and an empty `## Objective`), matching the original IA's scaffold-then-fill pattern: the domain per-skill pages, the utility per-skill pages, and the `01-task-tree/` page. Do **not** scaffold the relocated pages (task-file, cli, status, glossary, faq, hooks, showcase) — those are moves of existing content owned by `04` and `05`. Use `./superRA/superra task create --root docs/site …` so frontmatter and ordering are correct.

**Stop point:** the researcher approves the revised IA sitemap before content tasks (`02`–`05`) are dispatched, exactly as the original IA stop point gated the first build.

Validation: the revised §2 sitemap cross-checks against §1's teaching inventory (every concept still homed) and against the scaffolded `docs/site/` tree (every non-dropped page in the sitemap has a stub or an existing page; no stub is absent from the sitemap).

## Results

