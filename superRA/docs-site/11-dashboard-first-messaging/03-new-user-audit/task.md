---
title: "New-User Documentation Audit (Advertise + Clarity)"
status: not-started
depends_on: 
  - 01-front-door-and-welcome
  - 02-propagate-dashboard

tags: []
created: 2026-06-17
---

## Objective

Audit the documentation from the perspective of a **new user** arriving cold (the subtree-root Audience), against two questions the user asked explicitly:

1. **Does it advertise superRA — and the dashboard — well enough?** Would a researcher skimming the README and welcome page understand what superRA is, why it beats an unguided agent, and that the live task-tree dashboard (monitor + handoff, "this site is one") is a headline capability — not buried? Is the value proposition compelling and concrete?
2. **Is it clear enough on how to use it?** From the welcome → quickstart → how-to path, can a new user tell how to install, start a project, watch progress on the dashboard, and hand off / resume — without already knowing superRA's vocabulary? Flag undefined jargon, missing first steps, dead-end pages, and any place the dashboard is described before the reader knows how to open it.

Run this as a genuine cold read of the rendered site, not a diff review: read the README and the welcome → quickstart → how-to journey as a newcomer would, in order. Produce findings (gap, location, why it matters to a new user, suggested fix) and then **apply the improvements** that are clearly in scope of advertising + usability — sharpening the pitch, defining a term at first use, fixing a broken or missing pointer, adding a one-line bridge. Anything that would re-open a methodology or structural question beyond advertise/clarity: record as a finding for the user rather than acting.

Scope: edits stay within the docs-site pages and README; do not change CLI behavior, skills, or task-tree internals. Keep within the authoring contract (`01-information-architecture` §3).

**Carryover finding to resolve (from `01` review).** The welcome page's "What it is" domain-skills bullet lists *data analysis, theory modeling, academic writing, slide design* and frames all four as "domain skills"; the README lists only the three research verticals. Per [`skills/CATEGORIES.md`](../../../../skills/CATEGORIES.md) and the using-superRA Skill-Load Manifest Domain table, only those three are domain verticals — `slide-design` is a presentation/utility skill. Reconcile so the two front doors are consistent and slide-design is not publicly miscategorized as a research domain, while keeping it visible (the user explicitly wants slide design featured). A new user does not care about the internal domain-vs-utility taxonomy, so frame it by capability, not by category. Also sweep the cosmetic double-blank-line artifacts the `01` rewrite left in the welcome page (after `## Objective`, before `## How it works`, before `## Start here`).

Validation: findings recorded with location + rationale + disposition (fixed / left for user); applied fixes render cleanly in doc-mode (subtree-root Build command); both audit questions answered with a clear verdict, not a vague "looks good".

## Results

