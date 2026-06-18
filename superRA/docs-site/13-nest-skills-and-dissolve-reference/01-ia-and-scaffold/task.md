---
title: "Revise IA Contract for Nested Structure + Scaffold New Page Stubs"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Revise the information-architecture contract to describe the nested, Reference-dissolved structure with a new top-level Workflows section, then scaffold the empty page stubs the content tasks will fill. The IA contract is the authoritative sitemap; leaving it describing the old flat structure plus the `05-reference/` section would be a stale-content violation. This is the gating task — `02`–`06` build to the contract this task approves.

The target top-level shape: `01-welcome`, `02-quickstart`, `03-domain-skills/` (overview + per-skill pages), `04-utility-skills/` (overview + per-skill pages, with the task-tree reference nested under `01-task-tree/`), `05-workflows/` (new — overview + a page per phase), `06-hooks`, `07-showcase`. Glossary and FAQ do **not** become pages: they are dropped, and their genuinely-useful facts are introduced on the relevant pages instead (phase questions on the workflows pages, merge-guard on the semantic-merge page, sharing/data-hygiene on the dashboard page).

**Edit `superRA/docs-site/01-information-architecture/task.md` Results in place** (this task's deliverable lives in another task's file, by design — that file owns the sitemap):

- **§1 knowledge-state table:** update the Domain Skills and Utility Skills rows to reflect overview-plus-per-skill-page reading; add a Workflows row (the reader exits knowing what each phase does and what they invoke for it, one descent down). Re-home the glossary-of-terms and FAQ concepts: terms are introduced inline where first met; the FAQ questions are folded into the workflows and skill pages — there is no standalone glossary or FAQ page to point at.
- **§2 sitemap:** replace the flat `03-domain-skills`/`04-utility-skills` rows and the entire `05-reference/` block with the new tree: `03-domain-skills/` (overview) over `01-econ-data-analysis`/`02-theory-modeling`/`03-writing`; `04-utility-skills/` (overview) over `01-task-tree` (itself over `01-task-file`/`02-cli-commands`/`03-status-and-frontier`/`04-dashboard`, the last being a new user-facing page on the dashboard's export/comments/worktree features), `02-semantic-merge`, `03-result-protection`, `04-refactor-and-integrate`, `05-report-in-markdown`, `06-worktree-data-sync`, `07-zotero-paper-reader`, `08-mistral-pdf-to-markdown`; new `05-workflows/` (overview) over `01-plan`/`02-implement`/`03-integrate`; promoted top-level `06-hooks`; renumbered `07-showcase`. Keep the "Teaches / Links to (authority) / owning content task" columns; owning task is this `13-` subtree. Record that `05-reference/04-skills-and-agents` is dropped (inventory absorbed into the two overviews; Stage→load manifest is internal) and that `05-glossary`/`06-faq` are dropped, not promoted (their useful facts fold into the relevant pages).
- **§3 authoring contract:** confirm it still holds for three-level nesting and detail subpages; add a line only if nesting exposes a genuine gap (e.g. how a detail subpage links up to its parent skill page). Do not restate unchanged rules.
- **§4 README split:** repoint the Hooks-section disposition to `06-hooks`; the README has no FAQ/glossary section, so no glossary/faq disposition changes — but confirm any line that assumed a glossary/FAQ destination is updated.
- **Renumbering note:** record the top-level changes — glossary and faq dropped (useful content folded into the relevant pages); a new `05-workflows/` section inserted; hooks promoted to `06`; showcase renumbered to `07` — with the rationale, mirroring §2's existing renumbering-rationale style.

**Scaffold the genuinely-new empty page stubs** under `docs/site/` (directories with `title`-only frontmatter and an empty `## Objective`), matching the original IA's scaffold-then-fill pattern: the domain per-skill pages, the utility per-skill pages, the `01-task-tree/` page, and the new `05-workflows/` overview plus its `01-plan`/`02-implement`/`03-integrate` children. Do **not** scaffold the relocated pages (task-file, cli, status, hooks, showcase) — those are moves of existing content owned by `04` and `05`. Use `./superRA/superra task create --root docs/site …` so frontmatter and ordering are correct.

**Stop point:** the researcher approves the revised IA sitemap before content tasks (`02`–`06`) are dispatched, exactly as the original IA stop point gated the first build.

Validation: the revised §2 sitemap cross-checks against §1's teaching inventory (every concept still homed — including the re-homed glossary/FAQ facts) and against the scaffolded `docs/site/` tree (every non-dropped page in the sitemap has a stub or an existing page; no stub is absent from the sitemap).

## Results

The IA contract now describes the nested, Reference-dissolved structure, and the genuinely-new page stubs are scaffolded. Both deliverables landed.

**IA contract revision** — edited in place in [`01-information-architecture/task.md`](../../01-information-architecture/task.md), which owns the sitemap by design:

- **Framing paragraph** rewritten to record the `13-` restructure as the current state succeeding the `12-` flat-skills-plus-Reference layout (overviews-with-per-skill-pages, task-tree reference nested under its page, Reference dissolved).
- **§1 knowledge-state table:** the Domain Skills and Utility Skills rows now describe overview-plus-per-skill-page reading (knows-which-skills-exist at the overview, design-idea-and-load-trigger one descent down; task-tree descends a further level). The third row was retitled from "Reference" to "Glossary / FAQ / Hooks (top-level lookups)" since the Reference parent is gone. The §1 concept and gap tables had their stale `Reference › …` homes repointed to the new per-skill-page / top-level homes (a stale-content fix beyond the literal scope-line, required so the contract reads as current state).
- **§2 sitemap:** the flat `03-domain-skills`/`04-utility-skills` rows and the entire `05-reference/` block (plus `06-showcase`) are replaced by the full nested tree — `03-domain-skills/` over three per-skill pages; `04-utility-skills/` over `01-task-tree` (over `01-task-file`/`02-cli-commands`/`03-status-and-frontier`/`04-dashboard`), `02-semantic-merge` … `08-mistral-pdf-to-markdown`; top-level `05-glossary`/`06-faq`/`07-hooks`/`08-showcase`. The "Teaches / Links to / owning content task" columns are kept; owning tasks point into the `13-` subtree. A "Dropped from the tree" note records that `04-skills-and-agents` is dropped (inventory absorbed into the two overviews; Stage→load manifest is internal). A "Renumbering note" records the top-level renumber and the nesting renumber with rationale, mirroring §2's prior renumbering style. The §2 intro and validation paragraph were updated for the new shape and ownership subtree.
- **§3 authoring contract:** confirmed to hold for three-level nesting; one line added to the cross-page-links bullet covering nested full-path links and how a detail subpage links up to its parent (the one genuine gap nesting exposed). No unchanged rules restated.
- **§4 README split:** the two stale page-path references (`05-reference/04-skills-and-agents/`, `05-reference/07-hooks/`) repointed to the new homes.
- **§Scaffold:** rewritten to list exactly the new stubs this task created and to name the relocated pages as moves performed by `13-/04`/`13-/05`, not scaffolded here.

**Scaffold** — created with `./superRA/superra task create --root docs/site …` so frontmatter and ordering are correct. The genuinely-new stubs (`title`-only meaningful frontmatter, empty `## Objective`): three domain per-skill pages, eight utility per-skill pages, and the new `04-utility-skills/01-task-tree/04-dashboard` page. The relocated pages (task-file, cli, status, glossary, faq, hooks, showcase) were deliberately **not** scaffolded — they are moves of existing content owned by `13-/04` and `13-/05`.

**Validation passed.** The scaffolded `docs/site/` tree (`./superRA/superra task tree --root docs/site`) cross-checks against the revised §2 sitemap: every scaffolded stub appears in the sitemap, and every non-dropped sitemap page has either a stub (new pages) or an existing page (relocations still under `05-reference/`/`06-showcase/`). §2 cross-checks against §1's teaching inventory — every concept, journey, and named gap remains homed. `report-in-markdown`'s `check_markdown.py` reports the contract file clean; no stale `Reference › …` strings remain in it.

**Stop point:** the researcher approves this revised IA sitemap before the content tasks (`02`–`05`) are dispatched.

