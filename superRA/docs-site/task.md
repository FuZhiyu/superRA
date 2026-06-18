---
title: "Documentation Site: Dogfooded Task-Tree Docs + README Front Door"
status: approved
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
- **No AI-flavored prose (`[BLOCKING]` style gate, every doc page).** Write plain, substance-first prose; an implementer self-applies this before handing off and a reviewer blocks on it. The recurring tics to remove on sight: hype nouns and headings ("the killer pattern", "the payoff", "the magic/trick/beauty/secret", "superpower", "game-changer"); dramatic antithesis or flourish ("you do the thinking; the agent does the finish"); "this is where X happens / gets blocked" framing; rhetorical hooks and second-person hype ("Want X?", "Here's the thing", "the real win"); "not just X but Y" / "isn't just", and naming an internal thing only to negate it; em-dashes used for a dramatic pause or a punchy trailing payoff ("— so you never have to…") — keep em-dashes only for genuine parentheticals; empty intensifiers ("powerful", "seamless", "effortless", "simply", "just"). Lead with the reader's problem and the concrete answer, not a slogan. See `feedback_no_ai_flavored_prose`; the principle and line-level markers live in `skills/writing` (`style.md §Audience`).
- **Agent-first framing (`[BLOCKING]` gate, every skill/feature page).** The audience asks an AI agent to do the work — they say `superra plan this`, "polish §3", "sync this branch with main" — they rarely run the CLI themselves. Each page leads with how to ask the agent, with concrete example requests in plain language, then what the skill does and the failure it prevents. CLI commands, scripts, and other internals belong in a secondary section or subpage, framed as what the agent runs (and what you *can* run to inspect or drive the work yourself), never as the page's primary instruction. For the task-tree, `01-task-tree/02-cli-commands` is the designated home for the command surface; the overview and the other subpages lead agent-first and point there. An implementer self-applies this before handing off; a reviewer blocks a page that frames the reader as the command-runner. See `feedback_docs_audience_high_level_not_internals`.
- **Concise — explain only the non-obvious (`[BLOCKING]` gate, every skill page).** A skill's `SKILL.md` is already plain English and is the authority; the doc page is a short orientation, not a re-exposition. Do not re-narrate the skill's internal discipline — pitfall catalogs, step-by-step mechanics, exhaustive mode/gate/check/dimension/flag lists. State the core idea in a sentence or two and point to the `SKILL.md` for the rest. Cut anything the reader would already assume: an obvious invocation line ("invoke data analysis by saying 'use data analysis'") earns no space. Spend words only where they pay off — non-obvious usage (how to ask the agent well, with a concrete example prompt or two), CLI/script usage the reader or agent runs, and genuinely tricky concepts (e.g. the status lifecycle and the frontier). Apply the DRY/Necessity test per line: if removing it does not change what the reader would do, cut it. This refines the operating-manual bar — concrete does not mean exhaustive. See `feedback_docs_audience_high_level_not_internals`.

### Context

- The standalone export already provides: single-file self-contained HTML, hash-routed deep links (`#/<task/path>`) with back/forward support, subtree export via `--root`, KaTeX math, and base64-inlined images (`render_standalone_html`, [plan_dashboard.py](../../skills/task-tree/scripts/plan_dashboard.py)).
- Body sections render generically — any `## ` heading becomes a collapsible section (`render_task_body` in [task_node.html](../../skills/task-tree/scripts/templates/task_node.html)); doc pages need no task-semantics workarounds.
- Asset weight: ~690 KB of vendored JS/CSS/fonts inlined per export — acceptable for a single-file docs site; a multi-file export is explicitly out of scope for the first release and revisited only if the site grows heavy.
- Accepted limitation: hash-routed single-file output is weakly crawlable by search engines; the audience arrives via GitHub README links. Revisit (multi-page export) post-launch if organic discovery matters.

### Constraints

- Dashboard feature work is additive — flag-gated where it changes behavior (doc-mode is strictly opt-in), while pure capability additions (search, highlighting) may ship by default; existing `skills/task-tree/scripts` tests keep passing, and standalone exports stay self-contained (no CDN at runtime). `02-dashboard-features` carries the binding per-feature refinement.
- Generated site HTML is CI-built, never committed; only doc sources are committed.

## Critical Files

- [skills/task-tree/scripts/plan_dashboard.py](../../skills/task-tree/scripts/plan_dashboard.py) — `render_standalone_html` / `generate` own the export every feature task extends
- [skills/task-tree/scripts/templates/base.html](../../skills/task-tree/scripts/templates/base.html) — SPA shell: hash routing, `STANDALONE_FRAGMENTS`, nav sidebar, theme tokens
- [README.md](../../README.md) — source content for the reference pages and the `09-readme-front-door` restructure
- [skills/task-tree/references/task-file-contract.md](../../skills/task-tree/references/task-file-contract.md) — authority the human-facing task-tree reference pages point to
- [skills/using-superRA/SKILL.md](../../skills/using-superRA/SKILL.md) — skill inventory and manifest authority for the reference section

## Planner Guidance

Dispatch order: `01-information-architecture` and the `02-dashboard-features` children can run in parallel (IA is writing-domain, features are code). Content tasks (03–07) fan out in parallel after IA approval. `08-deploy` assembles; `09-readme-front-door` lands last so it links to a live site.
