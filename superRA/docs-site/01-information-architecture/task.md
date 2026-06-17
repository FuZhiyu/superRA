---
title: "Information Architecture + Docs-Tree Authoring Contract"
status: approved
depends_on: []
tags: []
created: 2026-06-10
---

## Objective

Produce the researcher-approved information architecture for the site, then scaffold the empty docs tree from it. Four deliverables, committed as one IA document plus the scaffold:

1. **Audience model and teaching inventory.** Who reads each section and in what state of knowledge; map every concept and journey a researcher must learn to a page. The known human-facing gaps must each have a home: visual/dashboard guide, quickstart, worked task-tree example, task-design guidance, FAQ/glossary, and the "how do I collaborate with agents via task files" narrative.
2. **Sitemap.** The full nav tree with a one-line brief per page (what it teaches, which existing skill/reference file is its authority to link to). Top level follows the tutorial / how-to / explanation / reference split unless a better structure emerges — deviations are a researcher decision, not a silent change.
3. **Docs-tree authoring contract.** Source location (proposed: `docs/site/`), node frontmatter use (`title` only; status/depends_on unused and hidden by doc-mode), ordering via numeric directory prefixes, cross-page link convention (hash links `#/<path>`), repo-file link convention (`--repo-file-base` pointing at the GitHub blob URL), and figure/screenshot conventions.
4. **README front-door split.** Section-by-section disposition for the current `README.md`: stays, moves to which page, or is dropped. Every current section must have a disposition.

**Stop point:** researcher approves the IA document before any content task (03–07) is dispatched.

Validation: cross-check the sitemap against deliverable 1's own teaching inventory (including the named gap list above) and against the current README — no concept, journey, or README section left without a disposition.

## Planner Guidance

Useful raw material: README.md structure, `skills/CATEGORIES.md`, the task-tree skill references (`task-file-contract.md`, `commands.md`, `task-tree-design.md`), `docs/README.codex.md` and `docs/README.opencode.md` (candidates to absorb or link), and the role specs under `agents/`.

Keep reference pages thin where a skill file already serves humans well — a brief framing plus a link beats a paraphrase that will drift.

## Results

This is the information architecture for the superRA documentation site, plus the authoring contract every content task follows. It is the artifact the researcher approves before any page is drafted.

**Current structure — superseded the original Diátaxis split (researcher-approved 2026-06-17).** The site was first built on a six-section Diátaxis-style layout (Welcome / Quickstart / Concepts / How-To / Reference / Showcase), approved 2026-06-11. That structure proved repetitive — concepts were explained in a standalone Concepts section, re-explained inline in the Quickstart, and again in the How-To guides. The [`12-condense-and-restructure`](../12-condense-and-restructure/task.md) subtree collapses it into a lean, quickstart-centered structure: one narrative spine plus two skill-introduction pages. The authoritative sitemap and dispositions below now describe that structure; §1's audience model and §3's authoring contract carry over unchanged. The empty docs tree is scaffolded at [docs/site/](../../../docs/site/); each node carries only a `title` and an empty `## Objective` to be filled by its owning content task.

### 1. Audience model and teaching inventory

**Primary audience.** Academic researchers new to superRA who are comfortable with git and with an AI coding harness (Claude Code or Codex), but who are *not* assumed to know plugin internals, the skill/agent architecture, or superRA's own vocabulary (task tree, frontier, drift test, implementer/reviewer pair, semantic merge). They arrive from the GitHub README, a colleague, or a conference mention, asking one of: "what is this and is it for me?", "how do I try it in 20 minutes?", "how do I do *my* recurring task with it?", or "what does this flag/field/status mean?".

**Secondary audiences.** (a) A returning user who has run one project and wants a specific how-to or reference lookup — arrives via search or a deep link, not the landing page. (b) A prospective *contributor* who wants to extend superRA — the site routes them to `CLAUDE.md` and the skill library rather than re-teaching contributor internals (contributor docs stay authoritative in-repo).

**Knowledge-state assumptions by section.** The pages below are ordered by how much superRA-specific vocabulary the reader is assumed to already hold:

| Section | Reader state on arrival | Reader state on exit |
|---|---|---|
| Welcome | Knows research + git + a harness; zero superRA vocabulary. | Knows the one-sentence pitch, the three-phase shape, and whether to continue. |
| Quickstart | Has installed superRA; no vocabulary yet. | Has walked one project end to end; has met task tree, dispatch, review, status, drift tests, and semantic merge *along the way*, with the *why* introduced inline. |
| Domain Skills | Knows the basic loop from the quickstart. | Knows which domain skills exist and the design idea behind each, so they can tell which apply to their own work. |
| Utility Skills | Knows the basic loop from the quickstart. | Knows which utility skills exist and the cross-cutting capability each provides. |
| Reference | Knows what they're looking for. | Has the exact field/flag/status/command, or a link to the authoritative skill file. |

**Teaching inventory — every concept and journey, mapped to a home.** A concept or journey is "covered" when at least one page teaches it; the page that *owns* it is bolded. The standalone Concepts and How-To sections are dropped: their essential ideas now live inline in the Quickstart narrative spine (each concept introduced at the point in the walkthrough where it matters) and in the two skills pages, with everything that does not fit there cut. The Quickstart owns the largest share of the teaching by design.

*Concepts (the "what/why"):*

| Concept | Owning page | Also touched by |
|---|---|---|
| What superRA is / the pitch | **Welcome** | README front door |
| PLAN → IMPLEMENT → INTEGRATE phase cycle | **Quickstart** | Welcome |
| Task tree (filesystem = task hierarchy, `task.md`, sibling deps, status rollup) | **Quickstart** | Reference › Task File |
| Implementer/reviewer pair & adversarial review | **Quickstart** | — |
| Status lifecycle & frontier | **Quickstart** | Reference › Status & Frontier |
| Drift/regression tests (result protection) | **Quickstart** | Utility Skills, Reference › Skills |
| Semantic merge (intent-aware sync) | **Quickstart** | Utility Skills, Reference › Skills |
| Domain skills (what they add, when they load) | **Domain Skills** | Welcome, Quickstart, Reference › Skills |
| Utility skills (cross-cutting capabilities) | **Utility Skills** | Quickstart, Reference › Skills |
| Autonomy-with-human-in-the-loop | **Quickstart** | Welcome |
| Adaptive/composable / re-entry | **Quickstart** | — |
| Hooks (what runs automatically, per-harness coverage) | **Reference › Hooks** | Quickstart (inline mention) |
| Glossary of superRA terms | **Reference › Glossary** | every page (link target) |

*Journeys (the "how"):*

| Journey | Owning page |
|---|---|
| Install on Claude Code / Codex / other harness | **Welcome** (install pointer) + README §Installation |
| Walk a project end to end | **Quickstart** |
| Plan a new project / decompose into a task tree | **Quickstart** (superplan stage of the walkthrough) |
| Collaborate with agents through task files (read/edit/handoff) | **Quickstart** (inline along the walkthrough) |
| Watch and steer work via the dashboard | **Quickstart** (dashboard-first throughout) |
| Integrate, protect results, sync, and open a PR | **Quickstart** (superintegrate stage of the walkthrough) |
| Resume an interrupted or revised project | **Quickstart** (re-entry, introduced inline) |

The dropped How-To journeys are not lost: each is folded into the corresponding stage of the single Quickstart walkthrough rather than carried as a separate goal-oriented recipe. Anything that did not fit the narrative spine is cut, per the condense subtree's prune-aggressively mandate.

**Named-gap coverage check (from the objective's gap list).** Each required gap has an explicit home:

| Required gap | Home page |
|---|---|
| Visual / dashboard guide | Quickstart (dashboard-first throughout) |
| Quickstart | Quickstart |
| Worked task-tree example | Showcase (embedded real export) |
| Task-design guidance | Quickstart (superplan stage; links to `superplan/references/task-tree-design.md`) |
| FAQ / glossary | Reference › Glossary + Reference › FAQ |
| "How do I collaborate with agents via task files" narrative | Quickstart (inline along the walkthrough) |

All six gaps are homed; no gap is orphaned.

### 2. Sitemap

The structure is quickstart-centered: a single end-to-end Quickstart narrative is the spine, introducing every concept inline at the point it matters, flanked by a pitch front door, two skill-introduction pages, a reference lookup home, and an embedded showcase. The standalone Concepts and How-To sections of the original Diátaxis layout are dropped — their ideas survive only inline in the Quickstart and the two skills pages.

The site is a single hash-routed standalone export; the nav tree below is the `docs/site/` directory tree. Numeric prefixes set display order. Each brief names what the page teaches and the authoritative skill/reference file it links to (rather than paraphrases). Page-to-content-task ownership (within the [`12-condense-and-restructure`](../12-condense-and-restructure/task.md) subtree) is shown in the rightmost column so the downstream dispatch is unambiguous.

| Nav path (`docs/site/…`) | Teaches | Links to (authority) | Owning content task |
|---|---|---|---|
| `01-welcome/` | Front door: one-sentence pitch, why superRA (incl. why-not-Superpowers), the three-phase shape, install pointer, "start here" routing to the Quickstart and skills pages. | `README.md`, mermaid phase diagram | 05-finalize (light alignment only) |
| `02-quickstart/` | The walkthrough: one end-to-end narrative — setup → superplan → superimplement → superintegrate — introducing every concept (task tree, dispatch, implementer/reviewer review, status & frontier, drift tests, semantic merge, re-entry) *inline along the way*, dashboard-first, with detail linked to Reference. Ends by directing the reader to the two skills pages. | `superplan`, `superimplement`, `superintegrate`, `task-tree/SKILL.md`, `using-superRA` | 02-quickstart |
| `03-domain-skills/` | Each domain skill introduced one by one with its high-level design idea: what research work it disciplines and when it loads. | `skills/CATEGORIES.md`, the domain skill files (`econ-data-analysis`, `theory-modeling`, `writing`, …) | 03-domain-skills |
| `04-utility-skills/` | Each utility skill introduced one by one with its high-level design idea: the cross-cutting capability it provides and when it comes into play. | `skills/CATEGORIES.md`, the utility skill files (`result-protection`, `semantic-merge`, `refactor-and-integrate`, `report-in-markdown`, …) | 04-utility-skills |
| `05-reference/` (parent) | Reference hub (information-oriented lookups). Kept as-is — a lookup/fallback home, not part of the reading flow. | — | 05-finalize (link repointing only) |
| `05-reference/01-task-file/` | `task.md` anatomy: frontmatter fields, body sections. | `task-tree/references/task-file-contract.md` | 05-finalize (link repointing only) |
| `05-reference/02-cli-commands/` | The `superra` CLI surface: query, mutate, dashboard. | `task-tree/references/commands.md` | 05-finalize (link repointing only) |
| `05-reference/03-status-and-frontier/` | Status enum, lifecycle, rollup, frontier computation. | `task-tree/references/task-file-contract.md`, `task-tree/SKILL.md` | 05-finalize (link repointing only) |
| `05-reference/04-skills-and-agents/` | Skill inventory and the Stage → skill load manifest, as a lookup. | `using-superRA` §Skill Inventory & §Skill-Load Manifest, `skills/CATEGORIES.md` | 05-finalize (link repointing only) |
| `05-reference/05-glossary/` | Every superRA term defined once. | (definitions; links to owning skills) | 05-finalize (link repointing only) |
| `05-reference/06-faq/` | Common questions: harness choice, when to skip phases, public-repo data hygiene. | `README.md`, `CLAUDE.md` | 05-finalize (link repointing only) |
| `05-reference/07-hooks/` | Hooks lookup: each hook's trigger, purpose, and Claude Code vs Codex coverage. | `hooks/` (hook sources), `docs/README.codex.md` §Hook Coverage | 05-finalize (link repointing only) |
| `06-showcase/` | An embedded real task-tree export proving the dogfooding claim. | a sanitized real `superRA/` subtree export | 05-finalize (link repointing only) |

**Dropped from the tree** (deleted in `05-finalize` once content tasks have repointed away): `03-concepts/` (5 pages) and `04-how-to/` (6 pages). Their essential ideas are folded inline into the Quickstart and the two skills pages; everything that does not fit is cut. The numbering works out cleanly — deleting `03-concepts` and `04-how-to` frees `03`/`04` for the two new skills pages, and `05-reference`/`06-showcase` keep their numbers.

Reference pages stay thin per Planner Guidance: each is a short human framing plus a link into the authoritative skill file, never a paraphrase that will drift. `01-welcome/`, `02-quickstart/`, and the two skills pages carry original teaching prose because no skill file is written for this audience.

**Sitemap ↔ inventory cross-check (validation).** Every concept and journey row in §1 maps to exactly one owning page above, and every named gap is homed (table in §1). Every kept page above traces to a content task in the `12-condense-and-restructure` subtree. No page is authority-less, and no concept/journey/gap is page-less.

### 3. Docs-tree authoring contract

The binding rules every content task follows when authoring `docs/site/`:

- **Source location:** `docs/site/`. Doc sources are committed; generated site HTML is CI-built and never committed (per the workstream's constraints).
- **Frontmatter:** each node uses `title` only. `status` and `depends_on` are left at their scaffold defaults (`not-started`, `[]`) and are **hidden at render time by doc-mode** — the opt-in render mode whose flag/marker name is settled by `02-dashboard-features/doc-mode` and whose exact build invocation is settled by `08-deploy`. Authors must not rely on a specific flag spelling; they rely on doc-mode being engaged by the build.
- **Page body:** the page content lives under `## Objective` of each node (the body section the export renders as the page; any `## ` heading becomes a collapsible section via `render_task_body`). Use `## ` subheadings within a page for structure. Do not add `## Results` / `## Review Notes` to doc nodes — those are task-workflow sections, not doc content.
- **Ordering:** numeric directory prefixes (`01-`, `02-`, …) set display order; they are display-only and independent of any dependency DAG (doc nodes carry no real dependencies).
- **Cross-page links:** hash links `#/<path>` where `<path>` is the doc-tree-relative node path (e.g. `[the domain skills](#/03-domain-skills)`). These resolve within the single-file hash-routed export.
- **Repo-file links:** to cite a skill/agent/source file as authority, link to the GitHub blob via the export's `--repo-file-base` (settled by `08-deploy` to the repo's blob URL at the built ref). In source, write the link as a normal repo-relative path target that the export re-bases; authors do not hardcode full GitHub URLs.
- **Figures/screenshots:** dashboard screenshots and diagrams are committed under `docs/site/<page>/attachments/` and embedded with `![caption](attachments/<file>)`; the export base64-inlines images, so relative paths from the node directory are correct. Prefer the live mermaid phase diagram (already in `README.md`) over a raster where a diagram suffices.
- **Public-repo hygiene:** all examples use placeholder or hypothetical research content — no personal data, real group names, real paths, or private query results.
- **Authority, not paraphrase:** doc pages teach the human journey and link to the canonical skill/agent file for behavior detail; they never become a second authority for agent-facing behavior (per workstream Conventions and `CLAUDE.md` §Ownership Boundaries).

### 4. README front-door split

The current [README.md](../../../README.md) becomes a *front door*: a tight pitch plus links into the site, with deep how-to/explanation prose moved onto pages. Every current section has a disposition. Section names below match the current README headings.

| Current README section | Disposition |
|---|---|
| Breaking-change banner (0.2.0) | **Stays** — release-critical, belongs at the top of the repo front door. |
| Intro ("superRA turns AI coding agents…") | **Stays** (condensed) — becomes the pitch; the full version seeds `01-welcome/`. |
| Why superRA? | **Stays** (condensed to 2–3 bullets) — full version moves to `01-welcome/`. |
| The Plan-Implement-Integrate Workflow (+ mermaid + invoke keywords) | **Moves** to `01-welcome/` (three-phase shape) and `02-quickstart/` (the walkthrough); README keeps the mermaid diagram and a one-line pointer. |
| dashboard / artifact-share paragraphs | **Moves** to `02-quickstart/` (dashboard-first throughout); README keeps a one-line mention with a link. |
| Key principles of the workflow | **Moves** to `02-quickstart/` (introduced inline); dropped from README. |
| Domain Skills (table + roadmap) | **Moves** to `03-domain-skills/` and `05-reference/04-skills-and-agents/`; README keeps a one-line list. |
| Utility Skills (table) | **Moves** to `04-utility-skills/` and `05-reference/04-skills-and-agents/`; dropped from README body. |
| Agents (table) | **Moves** to `02-quickstart/` (implementer/reviewer introduced inline at the review step); dropped from README body. |
| Hooks (table) | **Moves** to `05-reference/07-hooks/`; dropped from README body. |
| Installation (Claude Code / Codex / Other Platforms) | **Stays** — install is the README's job as the GitHub landing; `01-welcome/` carries the install pointer (absorbing `docs/README.codex.md` detail by link). |
| Contributing | **Stays** — points contributors to `CLAUDE.md`; not site content (the site targets researchers, not contributors). |
| Upstream | **Stays** — attribution belongs on the repo front door. |
| License | **Stays** — repo metadata. |

Disposition of the absorb/link candidates named in Planner Guidance: `docs/README.codex.md` is **linked** from `01-welcome/`'s install pointer (Codex install detail), left in place. `docs/README.opencode.md` is upstream-Superpowers content, not superRA-specific; it is **linked, not absorbed** — referenced alongside the Codex note for "other harnesses," left in place.

**README cross-check (validation):** every section heading currently in `README.md` appears exactly once in the table above with a Stays / Moves / Dropped-from-README disposition. No section is left without a disposition.

### Scaffold

The `docs/site/` tree exists as a standalone task root (separate from `superRA/`); inspect it with `./superRA/superra task tree --root docs/site`. Under the current structure the two new skills pages (`03-domain-skills/`, `04-utility-skills/`) are scaffolded with `title` set and an empty `## Objective` placeholder for their owning content tasks; the dropped `03-concepts/` and `04-how-to/` directories remain in place as valid link targets until the content tasks repoint away and `05-finalize` deletes them.
