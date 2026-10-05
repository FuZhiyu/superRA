---
title: "superRA Documentation"
status: not-started
depends_on: []
---

## Objective

<!-- This task tree is the doc source: each node's ## Objective body is one rendered page,
exported to static HTML by the task-tree dashboard in doc-mode (docs/build_site.sh) and
deployed to GitHub Pages. This root node renders as the site's landing (welcome) page.

Docs-tree authoring contract — the binding rules for every page under docs/site/.
Source-only: HTML comments do not render, so this contract never appears on the site;
doc-page authors inherit it via `task read` of any node under this root.

- Source location: docs/site/. Doc sources are committed; the generated site HTML is
  CI-built by docs/build_site.sh (GitHub Actions on push to main) and never committed.
- Frontmatter: each node uses `title` only. `status` and `depends_on` stay at their
  scaffold defaults (`not-started`, `[]`); doc-mode hides them at render time.
- Page body: the page content lives under `## Objective` (the section the export renders
  as the page). Use `## ` subheadings within a page for structure — doc-mode renders every
  `## ` section as a plain heading. Do not add `## Results` / `## Review Notes` to doc
  nodes; those are task-workflow sections, not doc content.
- Ordering: numeric directory prefixes (01-, 02-, ...) set display order; they are
  display-only (doc nodes carry no real dependencies). Number each level
  contiguously from 01-; the welcome content lives on this root node.
- Cross-page links: hash links #/<path> where <path> is the doc-tree-relative node path,
  e.g. [the domain skills](#/02-domain-skills); a nested page uses its full directory
  path, e.g. #/02-domain-skills/01-econ-data-analysis. The export's nav already
  shows the descent, so link a page to its parent only where the prose hands the reader
  back up, not on every page by rote.
- Repo-file links: to cite a skill/agent/source file as authority, write a normal
  repo-relative link target; the build re-bases it to the GitHub blob URL at the built
  ref via --repo-file-base (see docs/build_site.sh). Never hardcode full GitHub URLs.
- Sibling exports: pages link to the showcase HTML exports by relative basename;
  docs/build_site.sh passes --doc-local-link for each so those links stay relative
  instead of being rebased.
- Figures/screenshots: committed under docs/site/<page>/attachments/ and embedded with
  ![caption](attachments/<file>); the export base64-inlines images, so node-relative
  paths are correct. Prefer a live mermaid diagram over a raster where a diagram suffices.
- Public-repo hygiene: all examples use placeholder or hypothetical research content —
  no personal data, real group names, real paths, or private query results.
- Authority, not paraphrase: doc pages teach the human journey and link to the canonical
  skill/agent file for behavior detail; they never become a second authority for
  agent-facing behavior.
-->

**superRA turns AI agents into research assistants whose work you can see, steer, and reproduce.** It brings a plan–implement–integrate workflow, domain discipline, and a reproduction graph that traces every table and figure to the code that made it. A live dashboard ties them together: every task, decision, and result is a committed file, so you see where the work stands and which results are current. It runs on Claude Code and Codex.

[Explore an example project →](showcase-analysis-tree.html)

![The superRA dashboard: the live Graph view of an asset-pricing study after an edit to the analysis script. The data step reads fresh; the analysis step reads stale, with a hover card naming the changed file; its downstream check is stale through it. The selected task's results and figures sit beside the graph.](01-quickstart/attachments/showcase-graph.webp)

## Why superRA?

Research is exploratory, rarely testable in advance, and judged by people, so the researcher has to stay in the loop. Agent work makes that hard because it lives in the chat, not in a record. The reasoning vanishes when the session ends, the project's stage is invisible, and nothing logs which script and inputs produced each result, so no one can tell whether a table still comes from the current code and data.

Frameworks such as [Superpowers](https://github.com/obra/superpowers) target software, where unit tests verify the work and the goal is to take the human out of the loop. superRA keeps you in it: the project lives where you and the agent both see it.

## What you get

- **[A dashboard for the whole project.](#/03-utility-skills/01-task-tree)** This site is one.
  - **Persistent history.** Each task's objective, decisions, results, and reviews are committed files. Any session or coauthor resumes from them; one exported HTML file shares them.
  - **Task management.** A task tree with status, dependencies, and what is ready next. Pin a comment to a task to steer it.
  - **The project's stage at a glance.** Status rolls up the tree: planned, in progress, awaiting your call, done.
- **[Know which results are current.](#/03-utility-skills/02-reproducibility)** Each table and figure traces to the script that made it. After an edit, the Graph view marks what went stale and rebuilds only that.
- **[An agent that works with you.](#/04-workflows)** It edits the task file with you as a live canvas, pauses for feedback, and asks before spending on a review. Autonomous runs on request.
- **Discipline as the work goes.** [Domain skills](#/02-domain-skills) for data analysis, theory, writing, and slides; independent review where it earns its cost; an integration step that lands the work as clean, protected code.
- **Quality-of-life utilities.** [Utility skills](#/03-utility-skills) that read and cite papers from Zotero, convert PDFs to Markdown, merge branches by intent, and sync data across worktrees.

## How it works

<div style="margin:1.4em auto;max-width:560px;">
<svg viewBox="0 0 560 324" style="width:100%;height:auto;font-family:var(--font-text);" role="img" aria-label="PLAN, IMPLEMENT, and INTEGRATE phase boxes in a vertical flow down to a finished state, with two dashed 'plan change' edges looping back from IMPLEMENT and INTEGRATE into PLAN.">
  <defs>
    <marker id="ra-loop" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="var(--accent)"/></marker>
    <marker id="ra-down" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="var(--text-mute)"/></marker>
  </defs>

  <path d="M 170 122 C 118 122, 114 46, 168 46" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#ra-loop)"/>
  <path d="M 170 214 C 72 214, 72 34, 168 34" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#ra-loop)"/>

  <line x1="356" y1="70" x2="356" y2="94" stroke="var(--text-mute)" stroke-width="1.5" marker-end="url(#ra-down)"/>
  <line x1="356" y1="162" x2="356" y2="186" stroke="var(--text-mute)" stroke-width="1.5" marker-end="url(#ra-down)"/>
  <line x1="356" y1="254" x2="356" y2="278" stroke="var(--text-mute)" stroke-width="1.5" marker-end="url(#ra-down)"/>

  <g>
    <rect x="170" y="6" width="372" height="62" rx="6" fill="var(--bg-card)" stroke="var(--border)"/>
    <rect x="171" y="14" width="3" height="46" rx="1.5" fill="var(--accent)"/>
    <text x="188" y="29" style="font-family:var(--font-display);font-size:17px;font-weight:700;letter-spacing:.02em;fill:var(--accent);">PLAN</text>
    <text x="188" y="47" style="font-size:13px;fill:var(--text-mid);">scope &middot; task decomposition</text>
    <text x="188" y="62" style="font-size:13px;fill:var(--text-mid);"><tspan style="font-family:var(--font-mono);font-size:11.5px;">superRA/</tspan> task tree</text>
  </g>

  <g>
    <rect x="170" y="98" width="372" height="62" rx="6" fill="var(--bg-card)" stroke="var(--border)"/>
    <rect x="171" y="106" width="3" height="46" rx="1.5" fill="var(--accent)"/>
    <text x="188" y="121" style="font-family:var(--font-display);font-size:16px;font-weight:700;letter-spacing:.02em;fill:var(--accent);">IMPLEMENT<tspan style="font-family:var(--font-text);font-size:11px;font-weight:400;fill:var(--text-mute);"> (per task)</tspan></text>
    <text x="188" y="139" style="font-size:13px;fill:var(--text-mid);">execute with you &middot; self-review</text>
    <text x="188" y="154" style="font-size:13px;fill:var(--text-mid);">independent review where it earns its cost</text>
  </g>

  <g>
    <rect x="170" y="190" width="372" height="62" rx="6" fill="var(--bg-card)" stroke="var(--border)"/>
    <rect x="171" y="198" width="3" height="46" rx="1.5" fill="var(--accent)"/>
    <text x="188" y="213" style="font-family:var(--font-display);font-size:16px;font-weight:700;letter-spacing:.02em;fill:var(--accent);">INTEGRATE</text>
    <text x="188" y="231" style="font-size:13px;fill:var(--text-mid);">Choose results &middot; Sync &middot; Mature record</text>
    <text x="188" y="246" style="font-size:13px;fill:var(--text-mid);">Review refactoring &middot; Execute &middot; Finish</text>
  </g>

  <rect x="298" y="282" width="116" height="36" rx="18" fill="var(--st-ok)" stroke="var(--st-ok-t)"/>
  <text x="356" y="305" text-anchor="middle" style="font-family:var(--font-display);font-size:14px;font-weight:600;fill:var(--st-ok-t);">finished</text>

  <rect x="88" y="75" width="60" height="15" fill="var(--bg)"/>
  <text x="118" y="86" text-anchor="middle" style="font-size:10.5px;font-style:italic;fill:var(--accent);">plan change</text>
  <rect x="44" y="118" width="60" height="15" fill="var(--bg)"/>
  <text x="74" y="129" text-anchor="middle" style="font-size:10.5px;font-style:italic;fill:var(--accent);">plan change</text>
</svg>
</div>

- **[PLAN](#/04-workflows/01-plan)** — the agent scopes your request into a *task tree*: a directory of small `task.md` files, one per unit of work, that you review before execution starts.
- **[IMPLEMENT](#/04-workflows/02-implement)** — the agent works each task with you, self-reviews, and asks whether to run an independent review now, later, or not at all. On request, autonomous mode hands the tasks to implementer and reviewer subagents.
- **[INTEGRATE](#/04-workflows/03-integrate)** — you choose which results enter the permanent record and how they are protected. The agent syncs with your base branch, writes the record, and proposes one refactoring task; once you approve, it executes and ships.

Research is rarely this linear. Each phase also runs alone; a surprise mid-implementation or a later scope change routes back to PLAN; and exploratory work can be recorded as tasks after the fact.

## Get started

In Claude Code v2.1+:

```bash
claude plugin marketplace add FuZhiyu/superRA
claude plugin install superRA@superRA
```

Restart Claude Code, then in a project ask:

```text
Use superRA to onboard this project and show me the dashboard.
```

Onboarding builds a task tree and reproduction graph for the work already there, and changes nothing outside `superRA/` until you approve. For new work, the [Quickstart](#/01-quickstart) runs one study end to end. Codex setup, updating, and upgrading are in the [README](README.md).

## Start here

| You want to | Go to |
|---|---|
| Try one analysis end to end, or bring in an existing project | [Quickstart](#/01-quickstart) |
| Learn the task tree, the dashboard, and the reproduction graph | [task-tree](#/03-utility-skills/01-task-tree) |
| Know which tables and figures are out of date after an edit | [Reproducibility](#/03-utility-skills/02-reproducibility) |
| Understand one phase and what you decide in it | [Workflows](#/04-workflows) |
| Pick the discipline for your work | [Domain Skills](#/02-domain-skills) |
| See an example task tree | [Showcase](#/06-showcase) |
