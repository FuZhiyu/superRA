---
title: "Align Welcome, Prune Dropped Sections, Verify Build"
status: approved
depends_on:
  - 02-quickstart
  - 03-domain-skills
  - 04-utility-skills
tags: []
created: 2026-06-17
---

## Objective

Make the rest of the site consistent with the new structure, remove the dropped sections, and verify the site still builds and renders. This is the cleanup-and-verify task that closes the restructure.

1. **Align `01-welcome`.** Light edit only. Update the "Start here" links so they point to the surviving pages — Quickstart, the two new skills pages, Reference, Showcase — and drop pointers to the deleted Concepts and How-To sections. Reconcile any sentence that advertised the old section structure. Do not rewrite the pitch.

   **Drop the slide-design domain claim (researcher decision, 2026-06-17).** Welcome currently lists "slide design" as a current domain skill, but it is not in the packaged library (`CATEGORIES.md` lists only data analysis, theory modeling, writing). Remove slide-design from Welcome's advertised domain list so it matches the authoritative three. Do the same in the repo-root `README.md` if it still carries the slide-design claim after `06-shorten-readme` (this is the one cross-page consistency fix this task owns on README, beyond the link sweep). The new Domain Skills page already excludes slide-design — no change there.

2. **Delete the dropped sections.** Remove the `docs/site/03-concepts/` and `docs/site/04-how-to/` directories entirely (all pages and `attachments/`).

3. **Site-wide link sweep.** Find every reference to a deleted page — `#/03-concepts/...` and `#/04-how-to/...` hash links — across all surviving doc pages, `docs/build_site.sh`, and any nav/showcase framing, and repoint or remove each. In particular, repoint or thin `05-reference/04-skills-and-agents` so it points to the new Domain/Utility Skills pages rather than duplicating them; Reference stays a lookup home, not a reading-flow page. After the sweep, no link resolves to a deleted page.

4. **Build + render verification.** Run `docs/build_site.sh` (or the doc-mode dashboard) and confirm: the site builds without error, nav lists the six pages in order (welcome, quickstart, domain-skills, utility-skills, reference, showcase), every cross-page link resolves, and the new pages render in doc-mode. Verify against the *rendered* output, not just the source. Record the verification in `## Results`.

## Planner Guidance

The link sweep is the correctness-critical step — a dropped-page link that survives is a broken link on the live site. Grep the whole `docs/` tree (and `build_site.sh`) for `03-concepts` and `04-how-to` before declaring done. The doc-mode preview caches inlined CSS, so verify on a live serve or hard refresh, not a stale `file://` open.

## Results

The restructure is closed: the site is six pages, the two dropped sections are gone, and no link resolves to a deleted page in either the source or the rendered build.

**1. Welcome aligned ([docs/site/01-welcome/task.md](../../../../../docs/site/01-welcome/task.md)).** The two "Start here" bullets that pointed at the deleted Concepts and How-To sections now point at the two new skills pages — [Domain Skills](#/03-domain-skills) and [Utility Skills](#/04-utility-skills). Pitch untouched. The "What it is" domain list dropped "slide design", leaving the authoritative three (data analysis, theory modeling, academic writing) per [skills/CATEGORIES.md §Domain](../../../../../skills/CATEGORIES.md).

**2. README slide-design fix ([README.md](../../../../../README.md)).** Both surviving slide-design mentions (the numbered "What you get" list and the prose domain-skills paragraph) were trimmed to the authoritative three. This is the one README consistency fix this task owns beyond the link sweep.

**3. Dropped sections deleted.** `docs/site/03-concepts/` (5 pages) and `docs/site/04-how-to/` (6 pages) removed entirely via `git rm -r`, including their `attachments/`.

**4. Link sweep — zero surviving dropped-page links.** Every `#/03-concepts/...` and `#/04-how-to/...` reference in a surviving page was repointed to where the content now lives:

| File | Old target | Repointed to |
|---|---|---|
| `01-welcome` (2 links) | Concepts, How-To sections | `#/03-domain-skills`, `#/04-utility-skills` |
| `05-reference/04-skills-and-agents` | (duplicated skill prose) | added pointers to `#/03-domain-skills` / `#/04-utility-skills`; kept the lookup tables (reference-appropriate, denser than the prose pages) |
| `05-reference/05-glossary` (5 links) | Concepts: Task Tree / Skills / Integration×2 / Roles | `#/04-utility-skills` (task tree, result-protection, semantic-merge), `#/03-domain-skills`, `#/02-quickstart` |
| `05-reference/06-faq` (4 links) | How-To Install / Concepts Roles / How-To Resume / Concepts Integration | `#/02-quickstart`, `[superimplement]` skill, `#/04-utility-skills` |
| `05-reference/02-cli-commands` | How-To: See Your Work | `#/02-quickstart` |
| `05-reference/07-hooks` | How-To: Install | `#/02-quickstart` + `[README](README.md)` |
| `06-showcase` (3 links) | Concepts Task Tree / Roles×2 / How-To See Your Work | `#/02-quickstart`, `#/04-utility-skills`, `[task-tree skill]` |

`docs/build_site.sh` carried no dropped-page references (verified by grep). `05-reference/04-skills-and-agents` was thinned by adding a "for the narrative introduction, see …" pointer to each of the new pages at the head of its Domain and Utility sections, so it points at them rather than competing as a second reading-flow copy while staying a lookup home.

**5. Build + render verification (verified against rendered output).**

- `docs/build_site.sh /tmp/superra-finalize-site` exited 0 and wrote all three files (`index.html`, `demo-tree.html`, `superra-dev-tree.html`).
- Source grep `grep -rn "03-concepts\|04-how-to" docs/` after the sweep: **0 matches**.
- Rendered `index.html`: `grep -c "03-concepts"` = **0**, `grep -c "04-how-to"` = **0**.
- Every `#/` hash link in the rendered output resolves to an existing node path (the only non-doc `#/` hits are a JS regex literal `/##/g` and the root `#/`).
- Six top-level pages render in document order: `01-welcome`, `02-quickstart`, `03-domain-skills`, `04-utility-skills`, `05-reference`, `06-showcase`.
- New pages render: `index.html` contains the Domain Skills body ("Iron Law") and Utility Skills body ("filesystem is the task hierarchy"); doc-mode chrome active (`data-doc-mode="true"`); "slide design" string count = **0**.
- Live-serve doc-mode check (`dashboard --doc-mode --root docs/site`, fresh server after stopping the stale one): root returns HTTP 200, `data-doc-mode="true"` present, `/api/tree` carries **0** dropped-page references.
- All seven edited pages pass `report-in-markdown/scripts/check_markdown.py` (clean).
