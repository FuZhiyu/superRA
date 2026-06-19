---
title: "Dissolve Reference: Promote Hooks, Drop Glossary/FAQ/skills-and-agents, Renumber Showcase"
status: approved
depends_on: 
  - 01-ia-and-scaffold
  - 03-utility-skills
  - 04-task-tree-reference-nesting
  - 06-workflows

tags: []
created: 2026-06-17
---

## Objective

Dissolve the standalone `05-reference/` section: promote the one cross-cutting page worth a top-level home, drop the three pages the rest of the restructure makes redundant, and renumber the showcase. The glossary and FAQ are not promoted — their useful content is folded into the relevant pages first, then the pages are deleted.

**Promote to a top-level page:**

- `05-reference/07-hooks` → `06-hooks`
- `06-showcase` → `07-showcase`

Sequence the moves to avoid transient prefix collisions. Use `./superRA/superra task move --root docs/site …` so frontmatter/ordering stay correct, or `git mv` with a manual pass. Repoint only the moved pages' own internal `#/…` links; the site-wide repoint of links *into* them is task `07`.

**Drop `05-reference/05-glossary` and `05-reference/06-faq`, folding their useful facts into the relevant pages first.** The site carries no standalone glossary or FAQ; terms are met inline where they first matter, and each genuinely-useful FAQ answer has a natural home. Before deleting, confirm each fact is carried:

- Phase questions (skip PLAN / skip INTEGRATE, direct vs. subagent mode, resuming an old project) → the `05-workflows/` pages (task `06`).
- The `merge-guard` reminder and intent-aware merging → the `04-utility-skills/02-semantic-merge` page; drift tests → `03-result-protection`.
- Public-repo data hygiene and sharing an export → the `04-utility-skills/01-task-tree/04-dashboard` page (and the site-wide hygiene convention).
- Harness choice (Claude Code vs. Codex) → already the Welcome install pointer.
- Glossary term definitions → introduced inline in the quickstart / the owning skill page where each term first appears.

If any genuinely user-facing fact has no home after this pass, add it to the most relevant page rather than losing it. Do not create a replacement glossary or FAQ page.

**Drop `05-reference/04-skills-and-agents`.** Confirm its content is carried or intentionally dropped: the domain/utility skill inventory is now the two overview pages plus their per-skill pages; implementer/reviewer and Stage are taught inline in the quickstart and the workflows pages; the Stage→skill load manifest is agent-internal and stays in `using-superra`, not the user-facing site.

**Leave the empty `05-reference/` parent for task `07` to remove** after all relocations (task `04` also moves pages out of it); removing it here would race with `04`.

User-facing framing throughout: hooks is a reader lookup — what runs automatically and on which harness, not internal wiring. Load `writing`.

Validation: hooks renders at `06` with its content intact; showcase renders at `07`; glossary, FAQ, and `skills-and-agents` are gone with no user-facing fact orphaned (each fact traceable to a home page above); `05-reference/` holds only the pages task `04` is relocating.

## Results

The standalone Reference section is dissolved. Tree after the moves (`task tree --root docs/site`): top-level `06-hooks` and `07-showcase`; `05-reference/` holds only its own `task.md` parent stub (its `01-task-file`/`02-cli-commands`/`03-status-and-frontier` were already relocated under `04-utility-skills/01-task-tree/` by task `04`).

**Promotions.** Both done with `superra task move --root docs/site`, sequenced to avoid prefix collision — `06-showcase` → `07-showcase` first (no top-level `07` existed), then `05-reference/07-hooks` → `06-hooks`. The move tool re-based the hooks page's relative repo-file link from depth-2 to depth-1; it stripped the trailing slash on the bare directory link, which I restored to keep the prose byte-identical to the original (`[hooks/](hooks/)`, [docs/site/06-hooks/task.md:13](../../../../docs/site/06-hooks/task.md#L13)). No `#/…` cross-page links exist inside either moved page's own body, so nothing else needed repointing; links *into* these pages are task `07`'s site-wide repoint.

**Drops.** `git rm`'d `04-skills-and-agents`, `05-glossary`, `06-faq`. Confirmed every useful fact has a home before deleting:

| Dropped fact | Home (verified present) |
|---|---|
| skip PLAN / skip INTEGRATE, direct vs. subagent, resuming a project | `05-workflows/01-plan`, `02-implement`, `03-integrate` |
| merge-guard / intent-aware merging | `04-utility-skills/02-semantic-merge` |
| drift tests | `04-utility-skills/03-result-protection` |
| public-repo data hygiene + sharing an export | `04-utility-skills/01-task-tree/04-dashboard` |
| harness choice (Claude Code vs. Codex) | `01-welcome` install pointer; per-harness coverage also on `06-hooks` |
| skill/agent inventory, Stage→skill manifest | domain + utility overview pages and their per-skill pages; the Stage manifest is agent-internal (`using-superra`), intentionally not on the user-facing site |

Glossary term definitions are met inline in the quickstart and owning skill pages. No genuinely user-facing fact was orphaned, so no page needed a new fact added, and no replacement glossary/FAQ was created.

**Parent left for task `07`.** `05-reference/task.md` still lists the dropped/moved children in its body — that stale parent stub is removed wholesale by task `07`, which also owns repointing the remaining site-wide links into these pages (`#/06-showcase`, `#/05-reference`, `#/05-reference/07-hooks` in `01-welcome`, `02-quickstart`, and the `05-reference` stub). Removing the parent here would race with task `04`.

**Verification.** Doc-mode static build is clean: `uv run --script skills/task-tree/scripts/plan_dashboard.py generate --plan-root docs/site --doc-mode --output /tmp/docsite-verify.html` exits 0. In the rendered output, hooks content (e.g. `autoload-superra`) renders under `06-hooks`, showcase renders under `07-showcase`, and the dropped page titles (`Skills and Agents Reference`, `Glossary`, `FAQ`) no longer appear as rendered pages — they survive only as stale cross-page links in the bodies listed above, which task `07` repoints. `check_markdown.py` reports both moved pages clean.

