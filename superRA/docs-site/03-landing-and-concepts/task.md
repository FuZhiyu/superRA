---
title: "Landing Page + Concept (Explanation) Pages"
status: approved
depends_on:
  - 01-information-architecture
tags: []
created: 2026-06-10
---

## Objective

Write the site landing page and the explanation section per the approved IA.

- **Landing (root node body):** the pitch — what superRA is, why an agent needs discipline, the PLAN → IMPLEMENT → INTEGRATE diagram, and routing into the tutorial, guides, and reference. This is what doc-mode opens on.
- **Concept pages**, at minimum (final list per IA): the three-phase workflow and how re-entry works; task-tree anatomy for humans (tasks as directories, status lifecycle and rollup, `depends_on` and the frontier); the implementer–reviewer loop and what adversarial review buys; how the researcher collaborates with agents through task files (what you read — `## Results`, `## Review Notes` — and what you edit or comment); and a short execution-modes note (subagent vs direct).

Constraints: pages explain mechanisms in the reader's terms and link to the owning skill/agent files as authority — no long paraphrases of skill bodies; one paragraph per line; public-safe examples only.

Validation: every concept page names its authoritative source file; terminology matches the glossary entries `06-reference` will carry ("task tree" not "plan", frontier, rollup, stage).

## Planner Guidance

The README's current "Why superRA?" prose and mermaid workflow diagram are good seed material — this section becomes their durable home once `09-readme-front-door` trims the README.

## Results

Authored the landing page and the explanation (Concepts) section per the approved IA contract in [01-information-architecture](../01-information-architecture/task.md) §2–3. Seven page bodies written, each under its node's `## Objective` per the authoring contract; `title`-only frontmatter (status/depends_on left at scaffold defaults, hidden by doc-mode); one paragraph per line; public-safe content only.

### Pages written

| Page | File | Authority links |
|---|---|---|
| Landing | [docs/site/01-welcome](../../../docs/site/01-welcome/task.md) | `README.md`; live mermaid phase diagram (seeded from `README.md`) |
| Concepts hub | [docs/site/03-concepts](../../../docs/site/03-concepts/task.md) | routes to the five concept pages |
| The Workflow | [.../01-the-workflow](../../../docs/site/03-concepts/01-the-workflow/task.md) | `superplan`, `superimplement`, `superintegrate`, `using-superra` |
| The Task Tree | [.../02-the-task-tree](../../../docs/site/03-concepts/02-the-task-tree/task.md) | `task-tree/SKILL.md`, `task-tree/references/task-file-contract.md` |
| Roles and Review | [.../03-roles-and-review](../../../docs/site/03-concepts/03-roles-and-review/task.md) | `agents/implementer.md`, `agents/reviewer.md`, `agent-orchestration` |
| Skills and Agents | [.../04-skills-and-agents](../../../docs/site/03-concepts/04-skills-and-agents/task.md) | `skills/CATEGORIES.md`, `using-superra` |
| Integration and Protection | [.../05-integration-and-protection](../../../docs/site/03-concepts/05-integration-and-protection/task.md) | `superintegrate`, `result-protection`, `semantic-merge`, `refactor-and-integrate` |

Every concept page names at least one authoritative source file via a repo-file link, and the landing page embeds the README's mermaid PLAN→IMPLEMENT→INTEGRATE diagram (a live diagram, per the contract's "prefer the live mermaid diagram over a raster"). Internal navigation uses hash links `#/<doc-path>`; repo-file links to skill/agent files are written as repo-relative path targets for the export to re-base (no hardcoded GitHub URLs), per contract §3.

### Validation evidence

- **Render integrity:** `report-in-markdown/scripts/check_markdown.py` reports `clean` on all seven files (no broken display-math, no KaTeX-undefined macros).
- **Export builds:** `plan_dashboard.py generate --plan-root docs/site --repo-file-base <blob-url>` exits 0 and embeds all seven page bodies. `ROOT_PREFIX="site"`, `REPO_FILE_BASE` set, and all seven of my node paths are present in the export's in-tree `TASK_PATHS` oracle — so every `#/03-concepts/...` cross-link routes to a real node rather than falling through to a file link.
- **Terminology:** "task tree" used throughout (never "plan"/"plan file"/`PLAN.md`); `frontier` and `rollup` taught on the Task Tree page; `stage`/`status` used per the glossary discipline. The only `PLAN` occurrences are the phase name in caps.
- **Hygiene:** no `## Results`/`## Review Notes` body sections on any doc node (forbidden for doc nodes per §3); no hardcoded GitHub URLs; one paragraph per line.

### Deviations from Planner Guidance / objective drafting

The task `## Objective`'s concept-page list was drafted before the IA was finalized and says "at minimum (final list per IA)", explicitly deferring the page set to the IA. The IA (binding, researcher-approved 2026-06-11) scaffolded exactly five `03-concepts/*` pages, which I authored. Two items named in the objective draft are not standalone concept pages in the approved IA, and I handled them as the IA directs rather than inventing pages outside the scaffold:

- **"Collaborate with agents through task files" (`## Results`/`## Review Notes`):** the IA homes this narrative at **How-To › Work With Task Files** (`04-how-to/03`, owned by `05-how-to-guides`), not Concepts. I covered the concept lightly on the Task Tree page (which sections each role owns) and cross-linked to that how-to guide rather than duplicating the narrative here.
- **"Execution-modes note (subagent vs direct)":** the IA has no standalone execution-modes concept page; this is `using-superra` territory. I wove the relevant framing into The Workflow and Roles and Review pages (separate implementer/reviewer agents, orchestrator coordination) instead of adding an un-scaffolded page.

Both choices keep the Concepts section matching the approved scaffold and avoid creating a second authority — which is the route that satisfies the objective's "per the approved IA" framing.

### Open seam for downstream tasks (not mine to fix)

The standalone export currently re-bases a repo-file link relative to the doc node's directory under the doc-tree root prefix: with `ROOT_PREFIX="site"`, a link `skills/superplan/SKILL.md` from page `03-concepts/01-the-workflow` resolves to `<blob>/site/03-concepts/01-the-workflow/skills/superplan/SKILL.md` — inside the doc tree, not the repo root. Repo-file links from doc pages therefore do not yet point at the real source files. This is downstream plumbing owned by `08-deploy` (exact build invocation + `--repo-file-base`) and/or `02-dashboard-features/doc-mode` (the render mode the contract assumes engaged): the fix is to make the doc-mode export strip the `site/<page>/` prefix when re-basing repo-file links (or set `--repo-file-base` to account for the doc-tree depth) so repo-relative path targets land at repo root. My pages already follow the contract's authoring rule (repo-relative targets, no hardcoded URLs); flagging so the orchestrator routes the rebasing fix to the owning task.
