---
title: "Align Welcome, Prune Dropped Sections, Verify Build"
status: not-started
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
