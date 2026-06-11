---
title: "Documentation Site: Dogfooded Task-Tree Docs + README Front Door"
status: not-started
depends_on: []
tags: []
created: 2026-06-10
---

## Objective

Build and deploy a public documentation site for superRA that teaches human researchers the full product — with the task tree as the flagship, most-developed section — and restructure `README.md` into a front door that links into it.

**Architecture (researcher-approved 2026-06-10): the site is dogfooded.** Documentation pages are authored as a task-tree-shaped directory of `task.md` files and rendered to static HTML by the task-tree dashboard's existing standalone export (`plan_dashboard.py generate`), deployed to GitHub Pages via GitHub Actions. The dashboard enhancements the site needs (doc-mode chrome suppression, client-side search, code highlighting) ship as dual-use dashboard features under `02-dashboard-features` — each is a feature the dashboard benefits from independently of the docs.

Scope: full-product documentation — landing/pitch, quickstart tutorial, researcher-journey how-to guides, concept explanations, reference section, and an embedded task-tree showcase — plus the README front-door restructure. Content architecture follows a Diátaxis-style tutorial / how-to / explanation / reference split, finalized by `01-information-architecture`.

**Writing workflow:** Draft / Polish workflow

**Writing targets:** all doc pages under the docs source tree (location settled by `01-information-architecture`)

**Audience:** academic researchers new to superRA — comfortable with git and an AI coding harness (Claude Code or Codex), not assumed to know plugin internals or superRA terminology.

**Mode:** Draft

**Build command:** `uv run --script skills/task-tree/scripts/plan_dashboard.py generate --plan-root <docs tree>` (exact invocation and flags settled by `08-deploy`)

**Writing output:** doc pages as task-node markdown bodies, rendered to the static site

### Conventions

- Doc pages follow `report-in-markdown`; one paragraph per line, no hard wraps inside paragraphs.
- Doc pages teach human journeys and **link to skill/agent files as the authority** — never paraphrase agent-facing skill bodies at length. Canonical behavior text stays in `skills/` and `agents/` per CLAUDE.md §Ownership Boundaries; the site must not become a second authority.
- This is a public repo: examples use placeholder or hypothetical research content only — no personal data, real group names, or private paths.

### Context

- The standalone export already provides: single-file self-contained HTML, hash-routed deep links (`#/<task/path>`) with back/forward support, subtree export via `--root`, KaTeX math, and base64-inlined images (`render_standalone_html`, [plan_dashboard.py](../../skills/task-tree/scripts/plan_dashboard.py)).
- Body sections render generically — any `## ` heading becomes a collapsible section (`render_task_body` in [task_node.html](../../skills/task-tree/scripts/templates/task_node.html)); doc pages need no task-semantics workarounds.
- Asset weight: ~690 KB of vendored JS/CSS/fonts inlined per export — acceptable for a single-file docs site; a multi-file export is explicitly out of scope for the first release and revisited only if the site grows heavy.
- Accepted limitation: hash-routed single-file output is weakly crawlable by search engines; the audience arrives via GitHub README links. Revisit (multi-page export) post-launch if organic discovery matters.

### Constraints

- Dashboard feature work is additive and flag-gated: default dashboard/export behavior unchanged, existing `skills/task-tree/scripts` tests keep passing, standalone exports stay self-contained (no CDN at runtime).
- Generated site HTML is CI-built, never committed; only doc sources are committed.

## Critical Files

- [skills/task-tree/scripts/plan_dashboard.py](../../skills/task-tree/scripts/plan_dashboard.py) — `render_standalone_html` / `generate` own the export every feature task extends
- [skills/task-tree/scripts/templates/base.html](../../skills/task-tree/scripts/templates/base.html) — SPA shell: hash routing, `STANDALONE_FRAGMENTS`, nav sidebar, theme tokens
- [README.md](../../README.md) — source content for the reference pages and the `09-readme-front-door` restructure
- [skills/task-tree/references/task-file-contract.md](../../skills/task-tree/references/task-file-contract.md) — authority the human-facing task-tree reference pages point to
- [skills/using-superRA/SKILL.md](../../skills/using-superRA/SKILL.md) — skill inventory and manifest authority for the reference section

## Planner Guidance

Dispatch order: `01-information-architecture` and the `02-dashboard-features` children can run in parallel (IA is writing-domain, features are code). Content tasks (03–07) fan out in parallel after IA approval. `08-deploy` assembles; `09-readme-front-door` lands last so it links to a live site.

## Review Notes

1. **[BLOCKING] `09-readme-front-door` dependency gap — frontier would dispatch it before its link targets exist.** [09-readme-front-door/task.md](09-readme-front-door/task.md) depends only on `08-deploy`, but its "Moves to the site" sections land in tasks `08-deploy` explicitly does not gate on: skill/hook inventory tables → [06-reference/task.md](06-reference/task.md), multi-harness install detail → [05-how-to-guides/task.md](05-how-to-guides/task.md), and the quickstart pointer → [04-quickstart-tutorial/task.md](04-quickstart-tutorial/task.md). [08-deploy/task.md](08-deploy/task.md) Planner Guidance says "Content tasks 04–06 are not build prerequisites," so once 08 is approved the frontier offers 09 while 04–06 may be unwritten stubs — and 09's own validation ("every removed section's content is reachable from the README via exactly one link hop") cannot pass against stub pages. The root Planner Guidance line "09 lands last" is advisory, not enforced. Fix: add `04-quickstart-tutorial`, `05-how-to-guides`, `06-reference` to 09's `depends_on` (or restructure so 08 gates on full content, contradicting its own stub-deploy allowance).

2. **[BLOCKING] `08-deploy` validation is unsatisfiable from this branch as written — deploy trigger and Pages enablement undecided.** [08-deploy/task.md](08-deploy/task.md) specifies a workflow triggered "on push to the default branch" and validates by "loading the published URL." The repo's default branch is `main` (`git remote show origin`), which is hundreds of commits behind this lineage and lacks `skills/task-tree/scripts` entirely, so the workflow cannot fire — let alone build — until this workstream lands on `main`. Enabling GitHub Pages (Actions source) is additionally a repo-admin/researcher action the task does not mention. The implementer is handed a validation criterion they cannot satisfy without an unrecorded researcher decision. Fix: record the intended verification path in the objective — e.g. a `workflow_dispatch` trigger runnable from this branch plus a researcher stop point for Pages enablement, or explicitly defer the live-URL validation to landing on `main` and make local-build + artifact verification the in-branch criterion.

3. **[ADVISORY] Root `### Constraints` contradicts the `02-dashboard-features` refinement it inherits to.** The root constraint says "default dashboard/export behavior unchanged," while [02-dashboard-features/task.md](02-dashboard-features/task.md) deliberately allows "search and highlighting may appear by default." A child-feature reviewer walking the inherited root constraint could fail a default-on search box the planner intended. Relatedly, [02-dashboard-features/doc-mode/task.md](02-dashboard-features/doc-mode/task.md)'s criterion "a default (no-flag) export is byte-comparable in behavior to today's output" breaks once a sibling (highlighting/search) lands by default and shifts "today's output." Fix: align the root constraint with 02's refinement ("flag-gated where behavior changes; additive capability may ship by default"), and scope doc-mode's no-flag criterion to "unchanged relative to the pre-doc-mode baseline."

4. **[ADVISORY] `01-information-architecture` validation points at content that does not exist where claimed.** [01-information-architecture/task.md](01-information-architecture/task.md) validation says "cross-check the sitemap against the concept inventory in the workstream root's Context," but this root's `### Context` carries export capabilities and asset-weight notes, not a concept inventory. The actual gap inventory lives in 01's own deliverable 1. Fix the pointer (or add the inventory where the validation claims it is) so the no-gap cross-check has a real target.

5. **[ADVISORY] `09-readme-front-door` both defers to the IA disposition and prescribes it.** [09-readme-front-door/task.md](09-readme-front-door/task.md) opens with "following the section-by-section disposition approved in `01-information-architecture`" and then fixes specific Keeps/Moves lists. If the researcher-approved IA disposition differs, the objective is self-contradictory about which governs. State the relationship explicitly — e.g. the lists are the planner-expected baseline and the approved IA disposition governs, or the lists are constraints the IA must honor.

6. **[ADVISORY] The `02-dashboard-features` placement deviation is rationalized but its pending researcher review is not recorded in the tree.** [02-dashboard-features/task.md](02-dashboard-features/task.md) Context honestly notes the durable home is `skills/task-tree/scripts/` (the existing `task-tree/dashboard` subtree owns that surface), and the dispatch says the placement is flagged for researcher review — but the task file carries no trace of that open decision, unlike the root's stamped "researcher-approved 2026-06-10" architecture decision. Record the open placement decision (and the outcome once made) in 02's task file, including the expected disposition at integration (whether these feature tasks fold into `task-tree/dashboard` per durable-home policy).
