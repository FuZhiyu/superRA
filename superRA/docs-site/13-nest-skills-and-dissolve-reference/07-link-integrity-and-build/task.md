---
title: "Site-Wide Link Repoint + Build/Render-Integrity Verification"
status: approved
depends_on: 
  - 02-domain-skills
  - 03-utility-skills
  - 04-task-tree-reference-nesting
  - 05-dissolve-reference
  - 06-workflows

tags: []
created: 2026-06-17
---

## Objective

Final task: repoint every cross-page link that the restructure invalidated — inside `docs/site/` **and** in the repo markdown that deep-links the site (`README.md`, `docs/README.codex.md`) — remove the emptied `05-reference/` parent, and verify the whole site builds and renders with no broken links. This is the gate that catches the seam bugs a per-page edit cannot see.

**Site-wide link repoint.** Sweep every page under `docs/site/` (welcome, quickstart, both skills overviews and all their per-skill/detail pages, the new workflows pages, hooks, showcase) and repoint every stale `#/…` hash link to its new path:

- `#/05-reference/01-task-file` → `#/04-utility-skills/01-task-tree/01-task-file`
- `#/05-reference/02-cli-commands` → `#/04-utility-skills/01-task-tree/02-cli-commands`
- `#/05-reference/03-status-and-frontier` → `#/04-utility-skills/01-task-tree/03-status-and-frontier`
- `#/05-reference/07-hooks` → `#/06-hooks`
- `#/06-showcase` → `#/07-showcase`
- `#/05-reference/05-glossary` and `#/05-reference/06-faq` → **the glossary and FAQ pages are dropped, not relocated.** Retarget each link to the page that now carries the fact (a workflows page for a phase question, the semantic-merge or result-protection page, the dashboard page, the welcome install pointer), or remove the link where the surrounding prose no longer needs it. A link to a now-nonexistent glossary/FAQ path is a dead link, not a repoint target.
- `#/05-reference/04-skills-and-agents` → retarget to the relevant skills overview or skill page, or remove the link if nothing replaces it (the page is dropped)
- In-page anchors that pointed at the old flat skills pages (e.g. "Utility Skills: The Task Tree", "Protecting Results") → repoint to the specific skill subpage, e.g. `#/04-utility-skills/01-task-tree`, `#/04-utility-skills/03-result-protection`.

Find them with a repo-wide search for `#/05-reference`, `#/06-showcase`, and `#/04-utility-skills`/`#/03-domain-skills` bare-page anchors; fix the source files. Also fix any links that point *into* the relocated task-file/cli/status pages from outside (quickstart, welcome, other pages).

**Repoint the README front-door links too.** `README.md` deep-links the site at four invalidated targets — `#/05-reference` (the Reference landing, dissolved), `#/06-showcase` (→ `#/07-showcase`), `#/05-reference/04-skills-and-agents` (dropped), and `#/05-reference/07-hooks` (→ `#/06-hooks`). Repoint the two that have a new home (showcase, hooks); for the two whose target is gone (the Reference landing and skills-and-agents), rewrite the surrounding prose to point at what replaces them (the Workflows section / the skills overview pages) or drop the link — do not leave a link to a dissolved page. Sweep `docs/README.codex.md` the same way if it deep-links the site. These are the only files outside `docs/site/` in scope.

**Remove the empty `05-reference/` parent** once tasks `04` and `05` have moved or dropped all its children.

**Build + render-integrity verification.** Run the markdown render-integrity checker over the doc sources; build the doc-mode export (or live serve) and confirm: every page renders, the new nesting shows correctly in the nav, and **no hash link 404s** — click through the moved targets (task-file/cli/status under task-tree, the workflows pages at `05`, hooks at `06`, showcase at `07`). Verify through the real build, not a `file://` open (`feedback_preview_dashboard_css_live_not_file`); check the rendered result, not just the source (`feedback_verify_real_user_path_for_ui`).

Load `writing` for any link-context prose touched.

Validation: a repo grep for `#/05-reference` and `#/06-showcase` across the full sweep scope — `docs/site/`, `README.md`, and `docs/README.codex.md` — returns nothing; no link in any of those files targets a dropped glossary/FAQ/skills-and-agents path; the render-integrity check passes; a built/served walkthrough reaches every moved page with no dead link.

## Results

Swept the full scope (`docs/site/`, `README.md`, `docs/README.codex.md`) for stale hash links, repointed every one, removed the emptied `05-reference/` parent, and verified the build through both a static doc-mode export and a live doc-mode serve.

**Links repointed.** `docs/README.codex.md` carries no site deep-links, so it needed no edits; the changed files are the three doc pages and `README.md`.

| File | Stale link | New target |
|---|---|---|
| [07-showcase/task.md:19](../../../../docs/site/07-showcase/task.md) | `#/05-reference/03-status-and-frontier` | `#/04-utility-skills/01-task-tree/03-status-and-frontier` |
| [07-showcase/task.md:21](../../../../docs/site/07-showcase/task.md) | `#/05-reference/03-status-and-frontier` | `#/04-utility-skills/01-task-tree/03-status-and-frontier` |
| [07-showcase/task.md:23](../../../../docs/site/07-showcase/task.md) | `#/05-reference/01-task-file` | `#/04-utility-skills/01-task-tree/01-task-file` |
| [02-quickstart/task.md:104](../../../../docs/site/02-quickstart/task.md) | `#/05-reference/01-task-file` | `#/04-utility-skills/01-task-tree/01-task-file` |
| [02-quickstart/task.md:131](../../../../docs/site/02-quickstart/task.md) | `#/05-reference` (dissolved) + `#/06-showcase` | rewrote to point at `#/05-workflows`, the three task-tree lookup subpages, and `#/07-showcase` |
| [01-welcome/task.md:96](../../../../docs/site/01-welcome/task.md) | `#/05-reference` (dissolved) | rewrote the Start-here bullet to point at the new `#/05-workflows` section |
| [01-welcome/task.md:97](../../../../docs/site/01-welcome/task.md) | `#/06-showcase` | `#/07-showcase` |
| [README.md:5](../../../../README.md) | `#/05-reference` (dissolved) + `#/06-showcase` | `#/05-workflows` + `#/07-showcase` |
| [README.md:61](../../../../README.md) | `#/05-reference/04-skills-and-agents` (dropped) | dropped the trailing clause; the two overview pages already carry the skill inventory and the Stage→load map is internal |
| [README.md:63](../../../../README.md) | `#/05-reference/07-hooks` | `#/06-hooks` |

The dropped glossary (`#/05-reference/05-glossary`) and FAQ (`#/05-reference/06-faq`) targets had no live links in scope — their facts were already folded into the relevant pages by tasks `04`/`05`, so there was nothing to retarget. No in-page anchor into an old flat skills page survived (a search for the old anchor phrasing and for bare-fragment `](#...)` links returned nothing).

**Empty parent removed.** [docs/site/05-reference/](../../../../docs/site/05-reference/) held only its dissolved landing `task.md` after tasks `04`/`05` moved or dropped every child; removed it with `git rm -r`.

**Validation — link integrity.** Repo greps for `#/05-reference` and `#/06-showcase` across `docs/site/`, `README.md`, and `docs/README.codex.md` return nothing; a grep for any `glossary`/`faq`/`skills-and-agents` hash target returns nothing. Cross-checking every rendered hash-link target against the embedded node-path set: 23 distinct targets used, all resolve to a real node — zero dead links.

**Validation — render integrity.** Ran `check_markdown.py` over all 25 doc pages: every page reports `clean`.

**Validation — real build, not file://.**
- Static doc-mode export built clean: `plan_dashboard.py generate --plan-root docs/site --doc-mode` → 2.2 MB single-file HTML, exit 0. Every moved target path (`04-utility-skills/01-task-tree/{01-task-file,02-cli-commands,03-status-and-frontier,04-dashboard}`, `05-workflows[/01-plan,02-implement,03-integrate]`, `06-hooks`, `07-showcase`) is present in the embedded tree; every dropped/old path (`05-reference*`, `06-showcase`) is absent.
- Live doc-mode serve (`dashboard --root docs/site --doc-mode`) returned `200` on `/`; the `/api/search-index` the nav and client-side search build from lists exactly the 25 real pages with correct nesting (task-tree detail pages 3-deep, workflows nested, hooks/showcase top-level) and contains no `05-reference` or `06-showcase` entry. This is the real user path: the live nav resolves moved targets and excludes dropped ones.

Verification commands are re-runnable from the repo root; the build artifact lives at `/tmp/superra-docsite-build/index.html` (generated, not committed).
