---
title: "Revise IA Contract for Nested Structure + Scaffold New Page Stubs"
status: implemented
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

The IA contract now describes the nested structure with a top-level Workflows section and no standalone glossary/FAQ, and the genuinely-new page stubs (including the workflows section) are scaffolded. Both deliverables landed.

**IA contract revision** — edited in place in [`01-information-architecture/task.md`](../../01-information-architecture/task.md), which owns the sitemap by design:

- **Framing paragraph** records the current state: overviews-with-per-skill-pages, task-tree reference nested under its page, a new Workflows section with a page per phase, and the Reference section dissolved (hooks promoted, glossary/FAQ dropped with facts folded, skills-and-agents dropped, showcase renumbered).
- **§1 knowledge-state table:** added a Workflows row (overview → knows the three phases compose; phase page → knows what it does, what to invoke, what's theirs to decide); retitled the lookups row to "Hooks" since glossary/FAQ are gone. In the concept table, the phase-cycle row now also points at Workflows, a new "each phase in depth" row owns the Workflows pages, and the glossary-of-terms row is re-homed to "introduced inline where first met" (no standalone glossary). The named-gap "FAQ / glossary" row is re-homed to the Workflows/skill/inline destinations.
- **§2 sitemap:** the glossary/FAQ rows are removed and the new `05-workflows/` overview plus `01-plan`/`02-implement`/`03-integrate` inserted; hooks renumbered to `06-hooks`, showcase to `07-showcase`. The "Dropped from the tree" note now records glossary/FAQ as dropped-not-promoted with each fact's fold destination; the "Renumbering note" and validation cross-check are rewritten for the new tail. Owning-task column points into the `13-` subtree (now `13-/02`–`13-/07`).
- **§3 authoring contract:** unchanged — three-level nesting and the detail-subpage link-up line already cover the workflows nesting; no new rule needed.
- **§4 README split:** Hooks disposition repointed to `06-hooks/`.
- **§Scaffold:** lists the workflows stubs among the new pages and moves glossary/FAQ from the "relocated" list to the "dropped" list.

**Scaffold** — created with `./superRA/superra task create --root docs/site …` so frontmatter and ordering match the prior scaffold (title-only meaningful frontmatter, empty `## Objective`). The genuinely-new stubs added this round: the `05-workflows/` overview and its `01-plan`/`02-implement`/`03-integrate` children. The domain per-skill, utility per-skill, and `04-dashboard` stubs from the prior run are unchanged (those sections keep their `03`/`04` numbering). The relocated pages (task-file, cli, status, hooks, showcase) and the dropped pages (glossary, faq, skills-and-agents) are not scaffolded — they are moves/drops owned by `13-/04` and `13-/05`.

**Validation passed.** `./superRA/superra task tree --root docs/site` shows the `05-workflows/` section with its three phase pages; every scaffolded stub appears in the revised §2 sitemap and every non-dropped sitemap page has a stub or an existing page (the transient double-`05` with `05-reference/` resolves once `13-/04`/`13-/05` relocate and drop its children). §2 cross-checks against §1's teaching inventory — every concept, journey, and re-homed glossary/FAQ fact is homed. `report-in-markdown`'s `check_markdown.py` reports the contract file clean; no stale `08-showcase`/`07-hooks`-as-target/glossary-as-page strings remain.

**Stop point:** the researcher approves this revised IA sitemap before the content tasks (`02`–`06`) are dispatched.

## Review Notes

1. **MAJOR** — the README-link repoint is now owned in the objective prose, but its validation gate is still scoped to `docs/site/`, so the gate can pass green with the four README links left stale. The objective and new repoint paragraph in [`07-link-integrity-and-build`](../07-link-integrity-and-build/task.md#L17) now correctly cover `README.md`/`docs/README.codex.md`, and IA §4's new paragraph records the ownership — those parts are resolved. But the Validation line [07-link-integrity-and-build/task.md:40](../07-link-integrity-and-build/task.md#L40) still reads "a repo grep for `#/05-reference` and `#/06-showcase` **returns nothing in `docs/site/`**" — the same `docs/site/`-only scope my original finding flagged on the validation grep, not just the sweep. A grep restricted to `docs/site/` passes even when [README.md:5](../../../../README.md#L5), [README.md:61](../../../../README.md#L61), and [README.md:63](../../../../README.md#L63) still point at dissolved/renumbered targets, so the gate does not actually verify the README scope the objective now claims. Extend the Validation grep to `README.md` and `docs/README.codex.md` too (drop the "in `docs/site/`" qualifier or add the two files to the grep set) so the gate checks the full scope.
   → implemented: accepted on both rounds. Round 1 extended `13-/07`'s sweep to `README.md`/`docs/README.codex.md` and recorded ownership in IA §4. Round 2 (this fix) extends the **Validation** line too — the grep for `#/05-reference`/`#/06-showcase` and the dropped-path check now run across the full sweep scope (`docs/site/`, `README.md`, `docs/README.codex.md`), dropping the `docs/site/`-only qualifier, so the gate verifies the README scope the objective claims. ([07-link-integrity-and-build/task.md:40](../07-link-integrity-and-build/task.md#L40))

