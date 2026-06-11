---
title: "Information Architecture + Docs-Tree Authoring Contract"
status: implemented
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

This is the information architecture for the superRA documentation site, plus the authoring contract every content task (03–08) follows. It is the artifact the researcher approves before any page is drafted. The empty docs tree is scaffolded at [docs/site/](../../../docs/site/) from the sitemap in §2; each node carries only a `title` and an empty `## Objective` to be filled by its owning content task.

### 1. Audience model and teaching inventory

**Primary audience.** Academic researchers new to superRA who are comfortable with git and with an AI coding harness (Claude Code or Codex), but who are *not* assumed to know plugin internals, the skill/agent architecture, or superRA's own vocabulary (task tree, frontier, drift test, implementer/reviewer pair, semantic merge). They arrive from the GitHub README, a colleague, or a conference mention, asking one of: "what is this and is it for me?", "how do I try it in 20 minutes?", "how do I do *my* recurring task with it?", or "what does this flag/field/status mean?".

**Secondary audiences.** (a) A returning user who has run one project and wants a specific how-to or reference lookup — arrives via search or a deep link, not the landing page. (b) A prospective *contributor* who wants to extend superRA — the site routes them to `CLAUDE.md` and the skill library rather than re-teaching contributor internals (contributor docs stay authoritative in-repo).

**Knowledge-state assumptions by section.** The four Diátaxis quadrants below are ordered by how much superRA-specific vocabulary the reader is assumed to already hold:

| Section | Reader state on arrival | Reader state on exit |
|---|---|---|
| Landing | Knows research + git + a harness; zero superRA vocabulary. | Knows the one-sentence pitch, the three-phase shape, and whether to continue. |
| Tutorial (Quickstart) | Has installed superRA; no vocabulary yet. | Has run one task end to end; has met task tree, dispatch, review, status by *doing*. |
| How-to guides | Knows the basic loop from the tutorial. | Can accomplish one named recurring journey. |
| Explanation (Concepts) | Wants the *why* behind a mechanism they've seen. | Understands the model: phases, roles, the task file, drift tests, semantic merge. |
| Reference | Knows what they're looking for. | Has the exact field/flag/status/command, or a link to the authoritative skill file. |

**Teaching inventory — every concept and journey, mapped to a home.** A concept or journey is "covered" when at least one page teaches it; the page that *owns* it is bolded.

*Concepts (the "what/why"):*

| Concept | Owning page | Also touched by |
|---|---|---|
| What superRA is / the pitch | **Landing** | README front door |
| PLAN → IMPLEMENT → INTEGRATE phase cycle | **Concepts › The Workflow** | Landing, Quickstart |
| Task tree (filesystem = task hierarchy, `task.md`, sibling deps, status rollup) | **Concepts › The Task Tree** | Quickstart, Reference › Task File |
| Implementer/reviewer pair & adversarial review | **Concepts › Roles & Review** | Quickstart |
| Status lifecycle & frontier | **Concepts › The Task Tree** | Reference › Status & Frontier |
| Drift/regression tests (result protection) | **Concepts › Integration & Protection** | How-to › Integrate |
| Semantic merge (intent-aware sync) | **Concepts › Integration & Protection** | How-to › Integrate |
| Domain skills (what they add, when they load) | **Concepts › Skills & Agents** | Landing, Reference › Skills |
| Autonomy-with-human-in-the-loop | **Concepts › The Workflow** | — |
| Adaptive/composable / re-entry | **Concepts › The Workflow** | — |
| Glossary of superRA terms | **Reference › Glossary** | every page (link target) |

*Journeys (the "how"):*

| Journey | Owning page |
|---|---|
| Install on Claude Code / Codex / other harness | **How-to › Install & Set Up** |
| Run my first analysis end to end | **Tutorial › Quickstart** |
| Plan a new project / decompose into a task tree | **How-to › Plan a Project** |
| Collaborate with agents through task files (read/edit/handoff) | **How-to › Work With Task Files** |
| Watch and steer work via the dashboard | **How-to › See Your Work (Dashboard)** |
| Integrate, protect results, sync, and open a PR | **How-to › Integrate & Ship** |
| Resume an interrupted or revised project | **How-to › Resume & Revise** |

**Named-gap coverage check (from the objective's gap list).** Each required gap has an explicit home:

| Required gap | Home page |
|---|---|
| Visual / dashboard guide | How-to › See Your Work (Dashboard) |
| Quickstart | Tutorial › Quickstart |
| Worked task-tree example | Showcase (embedded real export) |
| Task-design guidance | How-to › Plan a Project (links to `superplan/references/task-tree-design.md`) |
| FAQ / glossary | Reference › Glossary + Reference › FAQ |
| "How do I collaborate with agents via task files" narrative | How-to › Work With Task Files |

All six gaps are homed; no gap is orphaned.

### 2. Sitemap

Top level keeps the Diátaxis tutorial / how-to / explanation / reference split, with two superRA-specific additions outside the four quadrants: a **Landing** page (the pitch front door) and a **Showcase** (an embedded real task-tree export — the dogfooding proof). This is not a deviation from the split; it is the split plus a front door and a demo, which the objective's "unless a better structure emerges" clause anticipates.

The site is a single hash-routed standalone export; the nav tree below is the `docs/site/` directory tree. Numeric prefixes set display order. Each brief names what the page teaches and the authoritative skill/reference file it links to (rather than paraphrases). Page-to-content-task ownership is shown in the rightmost column so the downstream dispatch is unambiguous.

| Nav path (`docs/site/…`) | Teaches | Links to (authority) | Owning content task |
|---|---|---|---|
| `01-welcome/` | Landing: one-sentence pitch, why superRA, the three-phase diagram, "start here" routing. | `README.md`, mermaid phase diagram | 03-landing-and-concepts |
| `02-quickstart/` | Tutorial: install → plan one tiny analysis → implement one task → review → see status. End to end in ~20 min. | `superplan`, `superimplement`, `task-tree/SKILL.md` | 04-quickstart-tutorial |
| `03-concepts/` (parent) | Explanation hub. | — | 03-landing-and-concepts |
| `03-concepts/01-the-workflow/` | The PLAN→IMPLEMENT→INTEGRATE cycle, re-entry, autonomy-with-human. | `superplan`, `superimplement`, `superintegrate`, `using-superRA` | 03-landing-and-concepts |
| `03-concepts/02-the-task-tree/` | Filesystem-as-hierarchy, `task.md`, sibling deps, status rollup, frontier. | `task-tree/SKILL.md`, `task-tree/references/task-file-contract.md` | 03-landing-and-concepts |
| `03-concepts/03-roles-and-review/` | Implementer/reviewer pair, APPROVE/REVISE, adversarial review. | `agents/implementer.md`, `agents/reviewer.md`, `agent-orchestration` | 03-landing-and-concepts |
| `03-concepts/04-skills-and-agents/` | Workflow / domain / utility skill model; when domain skills load. | `skills/CATEGORIES.md`, `using-superRA` §Skill Inventory | 03-landing-and-concepts |
| `03-concepts/05-integration-and-protection/` | Drift tests, semantic merge, why integration is a distinct phase. | `result-protection`, `semantic-merge`, `superintegrate` | 03-landing-and-concepts |
| `04-how-to/` (parent) | How-to hub (goal-oriented recipes). | — | 05-how-to-guides |
| `04-how-to/01-install-and-set-up/` | Install on Claude Code, Codex, other harnesses. | `README.md` §Installation, `docs/README.codex.md` | 05-how-to-guides |
| `04-how-to/02-plan-a-project/` | Scope and decompose work into a task tree; objective/guidance writing. | `superplan`, `superplan/references/task-tree-design.md` | 05-how-to-guides |
| `04-how-to/03-work-with-task-files/` | Read/edit/hand off via task files; the agent-collaboration narrative. | `using-superRA` §Task Interface, `task-tree/references/commands.md` | 05-how-to-guides |
| `04-how-to/04-see-your-work/` | Dashboard: tree/DAG/kanban, live serve, artifact share. | `task-tree/SKILL.md` (dashboard), `task-tree/references/internals.md` §Dashboard | 05-how-to-guides |
| `04-how-to/05-integrate-and-ship/` | Protect results, sync with base, refactor, open the PR. | `superintegrate`, `result-protection`, `semantic-merge`, `refactor-and-integrate` | 05-how-to-guides |
| `04-how-to/06-resume-and-revise/` | Resume interrupted work; revise the task tree mid-flight. | `superplan` §User Feedback and Changing the Task Tree | 05-how-to-guides |
| `05-reference/` (parent) | Reference hub (information-oriented lookups). | — | 06-reference |
| `05-reference/01-task-file/` | `task.md` anatomy: frontmatter fields, body sections. | `task-tree/references/task-file-contract.md` | 06-reference |
| `05-reference/02-cli-commands/` | The `superra` CLI surface: query, mutate, dashboard. | `task-tree/references/commands.md` | 06-reference |
| `05-reference/03-status-and-frontier/` | Status enum, lifecycle, rollup, frontier computation. | `task-tree/references/task-file-contract.md`, `task-tree/SKILL.md` | 06-reference |
| `05-reference/04-skills-and-agents/` | Skill inventory and the Stage → skill load manifest, as a lookup. | `using-superRA` §Skill Inventory & §Skill-Load Manifest, `skills/CATEGORIES.md` | 06-reference |
| `05-reference/05-glossary/` | Every superRA term defined once. | (definitions; links to owning skills) | 06-reference |
| `05-reference/06-faq/` | Common questions: harness choice, when to skip phases, public-repo data hygiene. | `README.md`, `CLAUDE.md` | 06-reference |
| `06-showcase/` | An embedded real task-tree export proving the dogfooding claim. | a sanitized real `superRA/` subtree export | 07-showcase |

Reference pages stay thin per Planner Guidance: each is a short human framing plus a link into the authoritative skill file, never a paraphrase that will drift. `01-welcome/` and the `03-concepts/*` pages carry original teaching prose because no skill file is written for this audience.

**Sitemap ↔ inventory cross-check (validation).** Every concept and journey row in §1 maps to exactly one owning page above, and every named gap is homed (table in §1). Every page above traces to one of the already-scaffolded content tasks 03–07. No page is authority-less, and no concept/journey/gap is page-less.

### 3. Docs-tree authoring contract

The binding rules every content task (03–08) follows when authoring `docs/site/`:

- **Source location:** `docs/site/`. Doc sources are committed; generated site HTML is CI-built and never committed (per the workstream's constraints).
- **Frontmatter:** each node uses `title` only. `status` and `depends_on` are left at their scaffold defaults (`not-started`, `[]`) and are **hidden at render time by doc-mode** — the opt-in render mode whose flag/marker name is settled by `02-dashboard-features/doc-mode` and whose exact build invocation is settled by `08-deploy`. Authors must not rely on a specific flag spelling; they rely on doc-mode being engaged by the build.
- **Page body:** the page content lives under `## Objective` of each node (the body section the export renders as the page; any `## ` heading becomes a collapsible section via `render_task_body`). Use `## ` subheadings within a page for structure. Do not add `## Results` / `## Review Notes` to doc nodes — those are task-workflow sections, not doc content.
- **Ordering:** numeric directory prefixes (`01-`, `02-`, …) set display order; they are display-only and independent of any dependency DAG (doc nodes carry no real dependencies).
- **Cross-page links:** hash links `#/<path>` where `<path>` is the doc-tree-relative node path (e.g. `[the task tree](#/03-concepts/02-the-task-tree)`). These resolve within the single-file hash-routed export.
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
| Why superRA? | **Stays** (condensed to 2–3 bullets) — full version moves to `01-welcome/` Landing. |
| The Plan-Implement-Integrate Workflow (+ mermaid + invoke keywords) | **Moves** to `03-concepts/01-the-workflow/`; README keeps the mermaid diagram and a one-line pointer. |
| dashboard / artifact-share paragraphs | **Moves** to `04-how-to/04-see-your-work/`; README keeps a one-line mention with a link. |
| Key principles of the workflow | **Moves** to `03-concepts/01-the-workflow/`; dropped from README. |
| Domain Skills (table + roadmap) | **Moves** to `03-concepts/04-skills-and-agents/` and `05-reference/04-skills-and-agents/`; README keeps a one-line list. |
| Utility Skills (table) | **Moves** to `05-reference/04-skills-and-agents/`; dropped from README body. |
| Agents (table) | **Moves** to `03-concepts/03-roles-and-review/`; dropped from README body. |
| Hooks (table) | **Moves** to `05-reference/` (a hooks lookup, sibling of CLI/status); dropped from README body. |
| Installation (Claude Code / Codex / Other Platforms) | **Stays** — install is the README's job as the GitHub landing; `04-how-to/01-install-and-set-up/` mirrors and expands it (absorbing `docs/README.codex.md` detail). |
| Contributing | **Stays** — points contributors to `CLAUDE.md`; not site content (the site targets researchers, not contributors). |
| Upstream | **Stays** — attribution belongs on the repo front door. |
| License | **Stays** — repo metadata. |

Disposition of the absorb/link candidates named in Planner Guidance: `docs/README.codex.md` is **absorbed/linked** by `04-how-to/01-install-and-set-up/` (Codex install detail). `docs/README.opencode.md` is upstream-Superpowers content, not superRA-specific; it is **linked, not absorbed** — referenced from the install how-to's "other harnesses" note, left in place.

**README cross-check (validation):** every section heading currently in `README.md` appears exactly once in the table above with a Stays / Moves / Dropped-from-README disposition. No section is left without a disposition.

### Scaffold produced

The empty `docs/site/` tree was created from §2 via `superra task create`, one node per sitemap row, each with `title` set and an empty `## Objective` placeholder for its owning content task to fill. Verify with `./superRA/superra task tree --root docs/site` (the docs tree is a standalone task root, separate from `superRA/`).

**Stop point reached:** this IA document is ready for researcher approval before content tasks 03–07 are dispatched.
