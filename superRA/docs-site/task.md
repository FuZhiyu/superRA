---
title: "Documentation Site: Dogfooded Task-Tree Docs + README Front Door"
status: approved
depends_on: []
---

## Objective

Build and deploy a public documentation site for superRA that teaches human researchers the full product — with the task tree as the flagship, most-developed section — and restructure `README.md` into a front door that links into it.

**Architecture (researcher-approved 2026-06-10): the site is dogfooded.** Documentation pages are authored as a task-tree-shaped directory of `task.md` files and rendered to static HTML by the task-tree dashboard's standalone export running in doc-mode, deployed to GitHub Pages via GitHub Actions. The dashboard enhancements the site needed (doc-mode chrome suppression, client-side search, code highlighting) shipped as dual-use dashboard features, each useful to the dashboard independently of the docs.

Scope: full-product documentation — front door, quickstart tutorial, skill and workflow pages, and an embedded task-tree showcase — plus the README front-door restructure.

**Audience:** academic researchers new to superRA — comfortable with git and an AI coding harness (Claude Code or Codex), not assumed to know plugin internals or superRA terminology.

### Conventions

These govern every future doc edit as well.

- Doc pages follow `report-in-markdown`; one paragraph per line, no hard wraps inside paragraphs.
- Doc pages teach human journeys and **link to skill/agent files as the authority** — never paraphrase agent-facing skill bodies at length. Canonical behavior text stays in `skills/` and `agents/` per CLAUDE.md §Ownership Boundaries; the site must not become a second authority.
- This is a public repo: examples use placeholder or hypothetical research content only — no personal data, real group names, or private paths.
- **No AI-flavored prose (`[BLOCKING]` style gate, every doc page).** Write plain, substance-first prose; an implementer self-applies this before handing off and a reviewer blocks on it. The recurring tics to remove on sight: hype nouns and headings ("the killer pattern", "the payoff", "the magic/trick/beauty/secret", "superpower", "game-changer"); dramatic antithesis or flourish ("you do the thinking; the agent does the finish"); "this is where X happens / gets blocked" framing; rhetorical hooks and second-person hype ("Want X?", "Here's the thing", "the real win"); "not just X but Y" / "isn't just", and naming an internal thing only to negate it; em-dashes used for a dramatic pause or a punchy trailing payoff ("— so you never have to…") — keep em-dashes only for genuine parentheticals; empty intensifiers ("powerful", "seamless", "effortless", "simply", "just"). Lead with the reader's problem and the concrete answer, not a slogan. See `feedback_no_ai_flavored_prose`; the principle and line-level markers live in `skills/writing` (`style.md §Audience`).
- **Agent-first framing (`[BLOCKING]` gate, every skill/feature page).** The audience asks an AI agent to do the work — they say `superra plan this`, "polish §3", "sync this branch with main" — they rarely run the CLI themselves. Each page leads with how to ask the agent, with concrete example requests in plain language, then what the skill does and the failure it prevents. CLI commands, scripts, and other internals belong in a secondary section or subpage, framed as what the agent runs (and what you *can* run to inspect or drive the work yourself), never as the page's primary instruction. For the task-tree, the `01-task-tree/02-cli-commands` page is the designated home for the command surface; the overview and the other subpages lead agent-first and point there. An implementer self-applies this before handing off; a reviewer blocks a page that frames the reader as the command-runner. See `feedback_docs_audience_high_level_not_internals`.
- **Concise — explain only the non-obvious (`[BLOCKING]` gate, every skill page).** A skill's `SKILL.md` is already plain English and is the authority; the doc page is a short orientation, not a re-exposition. Do not re-narrate the skill's internal discipline — pitfall catalogs, step-by-step mechanics, exhaustive mode/gate/check/dimension/flag lists. State the core idea in a sentence or two and point to the `SKILL.md` for the rest. Cut anything the reader would already assume: an obvious invocation line ("invoke data analysis by saying 'use data analysis'") earns no space. Spend words only where they pay off — non-obvious usage (how to ask the agent well, with a concrete example prompt or two), CLI/script usage the reader or agent runs, and genuinely tricky concepts (e.g. the status lifecycle and the frontier). Apply the DRY/Necessity test per line: if removing it does not change what the reader would do, cut it. This refines the operating-manual bar — concrete does not mean exhaustive. See `feedback_docs_audience_high_level_not_internals`.

### Context

- The standalone export provides: single-file self-contained HTML, hash-routed deep links (`#/<task/path>`) with back/forward support, subtree export via `--root`, KaTeX math, and base64-inlined images (`render_standalone_html` in `skills/task-tree/scripts/plan_dashboard.py`).
- Body sections render generically — any `## ` heading becomes a collapsible section (`render_task_body` in `skills/task-tree/scripts/templates/task_node.html`); doc pages need no task-semantics workarounds.
- Asset weight: ~690 KB of vendored JS/CSS/fonts inlined per export — acceptable for a single-file docs site; a multi-file export is out of scope and revisited only if the site grows heavy.
- Accepted limitation: hash-routed single-file output is weakly crawlable by search engines; the audience arrives via GitHub README links. Revisit (multi-page export) if organic discovery matters.

### Constraints

- Dashboard feature work is additive — flag-gated where it changes behavior (doc-mode is strictly opt-in), while pure capability additions (search, highlighting) may ship by default; existing `skills/task-tree/scripts` tests keep passing, and standalone exports stay self-contained (no CDN at runtime).
- Generated site HTML is CI-built, never committed; only doc sources are committed.

## Critical Files

- `docs/site/` — the committed doc-source tree; its root `task.md` carries the docs-tree authoring contract (an HTML comment in its `## Objective`)
- `docs/build_site.sh` — the committed build entry point; emits the doc-mode site plus the three showcase exports, and its header carries the fixture-refresh instructions
- `.github/workflows/docs-site.yml` — CI build + GitHub Pages deploy on push to `main`
- `skills/task-tree/scripts/plan_dashboard.py` — `render_standalone_html` / `generate` own the export
- `skills/task-tree/scripts/templates/base.html` — SPA shell: hash routing, doc-mode chrome suppression, nav sidebar, theme tokens
- `README.md` — the front door linking into the site

## Results

The documentation site is built, deployed, and live at `http://fuzhiyu.me/superRA/`, with `README.md` restructured into a front door that links into it.

**Dogfooded architecture.** Doc pages are authored as a task-tree-shaped directory of `task.md` files under `docs/site/` and rendered to a single self-contained HTML file by the task-tree dashboard's standalone export running in doc-mode — the docs site is itself a superRA tree. The dashboard features the site needed (doc-mode chrome suppression, client-side search, syntax highlighting) shipped as dual-use additions, each useful to the dashboard independently of the docs. The build pipeline is one committed entry script, `docs/build_site.sh`, invoked by the GitHub Actions workflow `.github/workflows/docs-site.yml` on push to `main`; generated HTML is CI-built and never committed. The docs-tree authoring contract every future page edit follows lives at the doc-source root, `docs/site/task.md` (an HTML comment in its `## Objective`, invisible on the rendered page).

**Final information architecture** (a reading-flow order, not the Diátaxis split the project started from): Welcome → Quickstart → Domain Skills → Utility Skills → Workflows → Hooks → Showcase. Skill pages are nested one-per-skill under the Domain and Utility overviews, and the task-tree page carries its own detail subpages (task-file / CLI / status-and-frontier / dashboard). Every page leads agent-first — how to ask the agent to do the work — and points to the canonical `skills/`/`agents/` files as the authority rather than re-narrating them, so the site never becomes a second source of truth.

**Showcase.** The site's worked example is a real CAPM-vs-FF3 asset-pricing study ([showcase-analysis](../showcase-analysis/task.md)) run end-to-end through the workflow, embedded as live explorable tree exports at three workflow moments (after-planning, mid-implement, complete). The two historical states are built from frozen fixtures under `docs/showcase-fixtures/` — deliberately not synced with later edits to the live tree; the regeneration commands live in the `docs/build_site.sh` header. The earlier simulated demo was retired so the real study is the sole example.

**Structural evolution.** The first full build was followed by several whole-site passes that shaped the current state: dashboard-first messaging, a condense-and-restructure to the quickstart-centered architecture above, nesting the per-skill pages and dissolving the standalone reference section, making the real study the sole showcase, and a depth-elaboration pass on the over-concise reading-flow pages. Two quality gates were enforced site-wide across these rounds and remain binding for future doc edits: no AI-flavored prose, and agent-first framing on every skill/feature page (both recorded in §Conventions).

**Verification at integration.** Docs build exits 0 and emits all four pages; render-integrity is clean over all 27 pages; no dangling cross-page links or references to the retired reference/showcase-demo pages. The post-launch docs version switcher ([10-version-switcher](10-version-switcher/task.md)) is intentionally `postponed`.

**Known rollup caveat.** After consolidation this task's only remaining child is the postponed `10-version-switcher`, and the tree tooling's rollup rule computes a parent with only parked children as `postponed` — so `task check` reports a stored-`approved`-vs-computed-`postponed` rollup warning here, and a status cascade triggered by a future edit under this subtree may rewrite the stored status. The `approved` status is the researcher's consolidation decision (the workstream is complete; one future enhancement is deferred) and should be restored if a cascade flips it.
