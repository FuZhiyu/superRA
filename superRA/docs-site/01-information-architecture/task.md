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

**Current structure — quickstart-centered, nested, Reference dissolved (researcher-approved 2026-06-17).** The site was first built on a six-section Diátaxis-style layout (Welcome / Quickstart / Concepts / How-To / Reference / Showcase), approved 2026-06-11. That structure proved repetitive — concepts were explained in a standalone Concepts section, re-explained inline in the Quickstart, and again in the How-To guides. The [`12-condense-and-restructure`](../12-condense-and-restructure/task.md) subtree collapsed it into a lean, quickstart-centered spine plus two flat skill-introduction pages, with a Reference section retained. The [`13-nest-skills-and-dissolve-reference`](../13-nest-skills-and-dissolve-reference/task.md) subtree takes the next step: the two flat skills pages become overviews each opening onto a page per skill, the task-tree skill's reference detail nests under its page, a new top-level Workflows section adds a page per phase, and the standalone Reference section is dissolved — its Hooks page promoted to the top level, `skills-and-agents` dropped, the Glossary and FAQ dropped with their useful facts folded into the relevant pages, and showcase renumbered. The authoritative sitemap and dispositions below describe that structure; §1's audience model and §3's authoring contract carry over with the skills- and workflows-row updates in §1 and the nesting line in §3. The empty docs tree is scaffolded at [docs/site/](../../../docs/site/); each node carries only a `title` and an empty `## Objective` to be filled by its owning content task.

### 1. Audience model and teaching inventory

**Primary audience.** Academic researchers new to superRA who are comfortable with git and with an AI coding harness (Claude Code or Codex), but who are *not* assumed to know plugin internals, the skill/agent architecture, or superRA's own vocabulary (task tree, frontier, drift test, implementer/reviewer pair, semantic merge). They arrive from the GitHub README, a colleague, or a conference mention, asking one of: "what is this and is it for me?", "how do I try it in 20 minutes?", "how do I do *my* recurring task with it?", or "what does this flag/field/status mean?".

**Secondary audiences.** (a) A returning user who has run one project and wants a specific how-to or reference lookup — arrives via search or a deep link, not the landing page. (b) A prospective *contributor* who wants to extend superRA — the site routes them to `CLAUDE.md` and the skill library rather than re-teaching contributor internals (contributor docs stay authoritative in-repo).

**Knowledge-state assumptions by section.** The pages below are ordered by how much superRA-specific vocabulary the reader is assumed to already hold:

| Section | Reader state on arrival | Reader state on exit |
|---|---|---|
| Welcome | Knows research + git + a harness; zero superRA vocabulary. | Knows the one-sentence pitch, the three-phase shape, and whether to continue. |
| Quickstart | Has installed superRA; no vocabulary yet. | Has walked one project end to end; has met task tree, dispatch, review, status, drift tests, and semantic merge *along the way*, with the *why* introduced inline. |
| Domain Skills (overview + a page per skill) | Knows the basic loop from the quickstart. | From the overview: knows which domain skills exist and that each has its own page. From a skill's page, one descent down: knows the design idea behind that skill and when it loads, so they can tell whether it applies to their own work. |
| Utility Skills (overview + a page per skill) | Knows the basic loop from the quickstart. | From the overview: knows which utility skills exist and that each has its own page. From a skill's page, one descent down: knows the cross-cutting capability that skill provides and when it comes into play; the task-tree page descends a further level to operational detail (field tables, CLI surface, status mechanics, dashboard). |
| Workflows (overview + a page per phase) | Knows the loop from the quickstart but wants more on one phase. | From the overview: knows the three phases compose and re-enter. From a phase's page, one descent down: knows what that phase does for them, what they invoke for it, and the decisions that are theirs. |
| Hooks (top-level lookup) | Knows what they're looking for. | Has the exact hook trigger and its per-harness coverage, or a link to the authoritative source. |

**Teaching inventory — every concept and journey, mapped to a home.** A concept or journey is "covered" when at least one page teaches it; the page that *owns* it is bolded. The standalone Concepts and How-To sections are dropped: their essential ideas now live inline in the Quickstart narrative spine (each concept introduced at the point in the walkthrough where it matters) and in the two skills pages, with everything that does not fit there cut. The Quickstart owns the largest share of the teaching by design.

*Concepts (the "what/why"):*

| Concept | Owning page | Also touched by |
|---|---|---|
| What superRA is / the pitch | **Welcome** | README front door |
| PLAN → IMPLEMENT → INTEGRATE phase cycle | **Quickstart** | Welcome, Workflows (+ a page per phase) |
| Each phase in depth (what you invoke, what's yours to decide) | **Workflows** (+ per-phase pages) | Quickstart |
| Task tree (filesystem = task hierarchy, `task.md`, sibling deps, status rollup) | **Quickstart** | Utility Skills › task-tree (+ its task-file detail page) |
| Implementer/reviewer pair & adversarial review | **Quickstart** | — |
| Status lifecycle & frontier | **Quickstart** | Utility Skills › task-tree › status-and-frontier |
| Drift/regression tests (result protection) | **Quickstart** | Utility Skills › result-protection |
| Semantic merge (intent-aware sync) | **Quickstart** | Utility Skills › semantic-merge |
| Domain skills (what they add, when they load) | **Domain Skills** | Welcome, Quickstart, each domain skill's page |
| Utility skills (cross-cutting capabilities) | **Utility Skills** | Quickstart, each utility skill's page |
| Autonomy-with-human-in-the-loop | **Quickstart** | Welcome |
| Adaptive/composable / re-entry | **Quickstart** | — |
| Hooks (what runs automatically, per-harness coverage) | **Hooks** (top-level) | Quickstart (inline mention) |
| superRA terms (task tree, frontier, drift test, implementer/reviewer, semantic merge) | introduced **inline where first met** (Quickstart; the owning skill and workflows pages) | — (no standalone glossary; terms link to their owning page) |

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
| FAQ / glossary | folded into the relevant pages — phase questions on the Workflows pages, skill questions on the owning skill pages, terms introduced inline (no standalone glossary or FAQ) |
| "How do I collaborate with agents via task files" narrative | Quickstart (inline along the walkthrough) |

All six gaps are homed; no gap is orphaned.

### 2. Sitemap

The structure is quickstart-centered and progressively disclosed: a single end-to-end Quickstart narrative is the spine, introducing every concept inline at the point it matters, flanked by a pitch front door, two skills overviews that each open onto a page per skill, a Workflows section that opens onto a page per phase, and — what remains after the Reference section is dissolved — top-level hooks and showcase pages. The standalone Concepts and How-To sections of the original Diátaxis layout were dropped earlier — their ideas survive inline in the Quickstart and the skills pages; the Glossary and FAQ are dropped here, their facts folded into the pages that own them. The shape of the tree now carries the teaching: a high-level overview at the top, a page per skill or phase one level down, and operational detail (the task-tree field tables, CLI surface, status mechanics, and dashboard) one level deeper still, revealed only as the reader descends.

The site is a single hash-routed standalone export; the nav tree below is the `docs/site/` directory tree. Numeric prefixes set display order. Each brief names what the page teaches and the authoritative skill/reference file it links to (rather than paraphrases). Page-to-content-task ownership (within the [`13-nest-skills-and-dissolve-reference`](../13-nest-skills-and-dissolve-reference/task.md) subtree) is shown in the rightmost column so the downstream dispatch is unambiguous; the `13-/` prefix names the child task that owns each page.

| Nav path (`docs/site/…`) | Teaches | Links to (authority) | Owning content task |
|---|---|---|---|
| `01-welcome/` | Front door: one-sentence pitch, why superRA (incl. why-not-Superpowers), the three-phase shape, install pointer, "start here" routing to the Quickstart and skills pages. | `README.md`, mermaid phase diagram | 05-finalize (light alignment only) |
| `02-quickstart/` | The walkthrough: one end-to-end narrative — setup → superplan → superimplement → superintegrate — introducing every concept (task tree, dispatch, implementer/reviewer review, status & frontier, drift tests, semantic merge, re-entry) *inline along the way*, dashboard-first, with detail linked to the relevant skill page. Ends by directing the reader to the two skills overviews. | `superplan`, `superimplement`, `superintegrate`, `task-tree/SKILL.md`, `using-superra` | 02-quickstart |
| `03-domain-skills/` (overview) | Short framing of what a domain skill is, plus a one-line entry per skill linking to its page. | `skills/CATEGORIES.md` | 13-/02-domain-skills |
| `03-domain-skills/01-econ-data-analysis/` | The data-analysis discipline (Iron Law, describe–analyze–validate) and when it loads. | `econ-data-analysis/SKILL.md` | 13-/02-domain-skills |
| `03-domain-skills/02-theory-modeling/` | The four-gate modeling discipline and when it loads. | `theory-modeling/SKILL.md` | 13-/02-domain-skills |
| `03-domain-skills/03-writing/` | The three writing modes (Review / Polish / Draft) and when it loads. | `writing/SKILL.md` | 13-/02-domain-skills |
| `04-utility-skills/` (overview) | Short framing of what a utility skill is, plus a one-line entry per skill linking to its page. | `skills/CATEGORIES.md` | 13-/03-utility-skills |
| `04-utility-skills/01-task-tree/` | High-level design of the task tree — filesystem as task hierarchy, rollup, frontier, dashboard — as the researcher's project view. Detail nests beneath. | `task-tree/SKILL.md` | 13-/03-utility-skills |
| `04-utility-skills/01-task-tree/01-task-file/` | `task.md` anatomy: frontmatter fields, body sections. | `task-tree/references/task-file-contract.md` | 13-/04-task-tree-reference-nesting (move of `05-reference/01-task-file`) |
| `04-utility-skills/01-task-tree/02-cli-commands/` | The `superra` CLI surface: query, mutate, dashboard. | `task-tree/references/commands.md` | 13-/04-task-tree-reference-nesting (move of `05-reference/02-cli-commands`) |
| `04-utility-skills/01-task-tree/03-status-and-frontier/` | Status enum, lifecycle, rollup, frontier computation. | `task-tree/references/task-file-contract.md`, `task-tree/SKILL.md` | 13-/04-task-tree-reference-nesting (move of `05-reference/03-status-and-frontier`) |
| `04-utility-skills/01-task-tree/04-dashboard/` | New user-facing page: the dashboard's static export (shareable HTML snapshots), task comments (the human-in-the-loop steering channel), and running tasks across parallel worktrees — framed as things the researcher does. | `task-tree/SKILL.md` | scaffolded by 13-/01; filled by 13-/04-task-tree-reference-nesting |
| `04-utility-skills/02-semantic-merge/` | Intent-aware sync: resolving conflicts by intent rather than ours/theirs. | `semantic-merge/SKILL.md` | 13-/03-utility-skills |
| `04-utility-skills/03-result-protection/` | Drift/regression tests that protect key results across sync, refactor, and maintenance. | `result-protection/SKILL.md` | 13-/03-utility-skills |
| `04-utility-skills/04-refactor-and-integrate/` | Codebase coherence: convention fit, utility reuse, PR-friendly diffs. | `refactor-and-integrate/SKILL.md` | 13-/03-utility-skills |
| `04-utility-skills/05-report-in-markdown/` | The markdown style guide: file-link citations, math, tables, figures. | `report-in-markdown/SKILL.md` | 13-/03-utility-skills |
| `04-utility-skills/06-worktree-data-sync/` | Non-git data sync between worktrees: seed, diff, apply, teardown. | `worktree-data-sync/SKILL.md` | 13-/03-utility-skills |
| `04-utility-skills/07-zotero-paper-reader/` | Read and analyze Zotero papers and generate citations from the library. | `zotero-paper-reader/SKILL.md` | 13-/03-utility-skills |
| `04-utility-skills/08-mistral-pdf-to-markdown/` | Convert a PDF to markdown with image extraction via Mistral OCR. | `mistral-pdf-to-markdown/SKILL.md` | 13-/03-utility-skills |
| `05-workflows/` (overview) | The PLAN → IMPLEMENT → INTEGRATE cycle as a project's spine: three phases the researcher moves work through, composable and re-enterable. One-line entry per phase linking down. | `superplan`, `superimplement`, `superintegrate` | 13-/06-workflows |
| `05-workflows/01-plan/` | Scoping and decomposing work into a task tree: what `superplan` does, what the researcher approves, when it is reasonable to skip PLAN. | `superplan/SKILL.md` | 13-/06-workflows |
| `05-workflows/02-implement/` | Executing tasks through the implementer–reviewer loop: what `superimplement` dispatches, the review gate, resuming from the frontier, direct vs. subagent mode. | `superimplement/SKILL.md` | 13-/06-workflows |
| `05-workflows/03-integrate/` | Protecting results, syncing with the base, refactoring for fit, and the final PR: what `superintegrate` does and the completion decisions that are the researcher's, when INTEGRATE can be skipped. | `superintegrate/SKILL.md` | 13-/06-workflows |
| `06-hooks/` | Hooks lookup: each hook's trigger, purpose, and Claude Code vs Codex coverage. | `hooks/` (hook sources), `docs/README.codex.md` §Hook Coverage | 13-/05-dissolve-reference (promote of `05-reference/07-hooks`) |
| `07-showcase/` | An embedded real task-tree export proving the dogfooding claim. | a sanitized real `superRA/` subtree export | 13-/05-dissolve-reference (renumber of `06-showcase`) |

**Dropped from the tree.** `05-reference/04-skills-and-agents/` is dropped, not moved: its skill inventory is now carried by the two skills overview pages (`03-domain-skills/` and `04-utility-skills/`), and the Stage → skill load manifest it also held is internal agent-routing detail that the researcher audience does not need (the user-facing fact — which skill applies to which work — lives on each skill's own page). `05-reference/05-glossary/` and `05-reference/06-faq/` are also dropped, not promoted: a standalone glossary and FAQ are a second definition home that drifts from the skill files, and for this small vocabulary the quickstart-centered design teaches better inline. Their genuinely-useful facts are folded into the pages that own them — phase questions onto the Workflows pages, merge-guard onto the semantic-merge page, drift tests onto result-protection, data hygiene and export-sharing onto the dashboard page, harness choice onto the Welcome install pointer, and term definitions inline where each term first appears. The standalone `05-reference/` parent is dissolved: it no longer exists once its hooks child is promoted, its task-tree children nest under `01-task-tree/`, and its glossary/FAQ/skills-and-agents children are dropped. The earlier-dropped `03-concepts/` (5 pages) and `04-how-to/` (6 pages), already folded into the Quickstart and the skills pages, are deleted alongside this restructure.

Reference detail pages stay thin per Planner Guidance: each is a short human framing plus a link into the authoritative skill file, never a paraphrase that will drift. `01-welcome/`, `02-quickstart/`, the skills overviews, and the per-skill pages carry original teaching prose because no skill file is written for this audience.

**Renumbering note.** A new `05-workflows/` section takes the slot freed by the dropped glossary, with `06-hooks/` (promoted from `05-reference/07-hooks`) and `07-showcase/` (renumbered from `06-showcase/`) following it to keep showcase at the end of the reading flow. Glossary and FAQ are dropped, so no page inherits their former `05`/`06` slots. The task-tree reference children (`01-task-file`, `02-cli-commands`, `03-status-and-frontier`) renumber from their `05-reference/` prefix to `04-utility-skills/01-task-tree/01..03`, where their detail belongs to the skill that owns it. This mirrors §2's earlier renumbering rationale: numbers follow the reading order, and a move that changes a page's parent renumbers it to fit the new parent's sequence. Cross-page `#/...` links to any moved page are repointed by the owning content task (`13-/04` and `13-/05`) and verified site-wide by `13-/07-link-integrity-and-build`.

**Sitemap ↔ inventory cross-check (validation).** Every concept and journey row in §1 maps to an owning page above (domain/utility concepts resolve to a skill's own page reached via its overview; each-phase-in-depth resolves to the Workflows pages; task-file and status detail resolve to the nested task-tree pages; the re-homed glossary/FAQ facts resolve to the Workflows, skill, dashboard, and Welcome pages named in §1 and the Dropped-from-the-tree note). Every named gap is homed (table in §1). Every kept page above traces to a content task in the `13-nest-skills-and-dissolve-reference` subtree. No page is authority-less, and no concept/journey/gap is page-less. Every non-dropped page in this sitemap has either a scaffolded stub (the domain per-skill pages, the utility per-skill pages, `01-task-tree/`, `04-dashboard/`, and the new `05-workflows/` overview plus its three phase pages) or an existing page relocated by `13-/04`/`13-/05`; no scaffolded stub is absent from this sitemap.

### 3. Docs-tree authoring contract

The binding rules every content task follows when authoring `docs/site/`:

- **Source location:** `docs/site/`. Doc sources are committed; generated site HTML is CI-built and never committed (per the workstream's constraints).
- **Frontmatter:** each node uses `title` only. `status` and `depends_on` are left at their scaffold defaults (`not-started`, `[]`) and are **hidden at render time by doc-mode** — the opt-in render mode whose flag/marker name is settled by `02-dashboard-features/doc-mode` and whose exact build invocation is settled by `08-deploy`. Authors must not rely on a specific flag spelling; they rely on doc-mode being engaged by the build.
- **Page body:** the page content lives under `## Objective` of each node (the body section the export renders as the page; any `## ` heading becomes a collapsible section via `render_task_body`). Use `## ` subheadings within a page for structure. Do not add `## Results` / `## Review Notes` to doc nodes — those are task-workflow sections, not doc content.
- **Ordering:** numeric directory prefixes (`01-`, `02-`, …) set display order; they are display-only and independent of any dependency DAG (doc nodes carry no real dependencies).
- **Cross-page links:** hash links `#/<path>` where `<path>` is the doc-tree-relative node path (e.g. `[the domain skills](#/03-domain-skills)`). These resolve within the single-file hash-routed export. With three-level nesting, a nested path is the full directory path (e.g. `[the CLI commands](#/04-utility-skills/01-task-tree/02-cli-commands)`). A detail subpage links up to its parent skill page the same way (e.g. the CLI page back to `#/04-utility-skills/01-task-tree`); an overview links down to each per-skill page; the export's nav already shows the descent, so a page links to its parent only where the prose hands the reader back up, not on every page by rote.
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
| Domain Skills (table + roadmap) | **Moves** to `03-domain-skills/` (overview + a page per skill); README keeps a one-line list. |
| Utility Skills (table) | **Moves** to `04-utility-skills/` (overview + a page per skill); dropped from README body. |
| Agents (table) | **Moves** to `02-quickstart/` (implementer/reviewer introduced inline at the review step); dropped from README body. |
| Hooks (table) | **Moves** to `06-hooks/`; dropped from README body. |
| Installation (Claude Code / Codex / Other Platforms) | **Stays** — install is the README's job as the GitHub landing; `01-welcome/` carries the install pointer (absorbing `docs/README.codex.md` detail by link). |
| Contributing | **Stays** — points contributors to `CLAUDE.md`; not site content (the site targets researchers, not contributors). |
| Upstream | **Stays** — attribution belongs on the repo front door. |
| License | **Stays** — repo metadata. |

Disposition of the absorb/link candidates named in Planner Guidance: `docs/README.codex.md` is **linked** from `01-welcome/`'s install pointer (Codex install detail), left in place. `docs/README.opencode.md` is upstream-Superpowers content, not superRA-specific; it is **linked, not absorbed** — referenced alongside the Codex note for "other harnesses," left in place.

**README front-door links into the site.** The README already carries hash deep-links into the site (`#/02-quickstart`, `#/03-domain-skills`, `#/04-utility-skills`, and — invalidated by this restructure — `#/05-reference`, `#/05-reference/04-skills-and-agents`, `#/05-reference/07-hooks`, `#/06-showcase`). Repointing those invalidated links is owned by `13-/07-link-integrity-and-build`, whose sweep covers `README.md` and `docs/README.codex.md` alongside `docs/site/`: showcase → `#/07-showcase` and hooks → `#/06-hooks` are repoints, while the dissolved Reference landing and the dropped skills-and-agents link are rewritten to point at the Workflows section or the skills overviews (or dropped), since their targets no longer exist.

**README cross-check (validation):** every section heading currently in `README.md` appears exactly once in the table above with a Stays / Moves / Dropped-from-README disposition. No section is left without a disposition.

### Scaffold

The `docs/site/` tree exists as a standalone task root (separate from `superRA/`); inspect it with `./superRA/superra task tree --root docs/site`. The two skills overview pages (`03-domain-skills/`, `04-utility-skills/`) already carry content from `12-condense-and-restructure`; the content tasks reshape them into overviews. The genuinely-new stubs for this restructure are scaffolded with `title` set and an empty `## Objective`: the three domain per-skill pages (`03-domain-skills/01-econ-data-analysis`, `02-theory-modeling`, `03-writing`), the eight utility per-skill pages (`04-utility-skills/01-task-tree` … `08-mistral-pdf-to-markdown`), the new `04-utility-skills/01-task-tree/04-dashboard` page, and the new Workflows section (`05-workflows/` overview plus `01-plan`, `02-implement`, `03-integrate`). The relocated pages — `01-task-file`, `02-cli-commands`, `03-status-and-frontier`, `07-hooks`, and the showcase — are not scaffolded here; they are moves of existing content under `05-reference/` (and `06-showcase/`) performed by `13-/04` and `13-/05`, which renumber and repoint them. The `05-reference/04-skills-and-agents`, `05-glossary`, and `06-faq` pages are deleted by `13-/05` once their content is absorbed into the overviews, the Workflows pages, and the relevant skill/dashboard pages.
