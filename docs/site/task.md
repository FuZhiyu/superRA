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
  display-only (doc nodes carry no real dependencies). The 01- slot is retired: the
  welcome content lives on this root node, and child numbering starts at 02-.
- Cross-page links: hash links #/<path> where <path> is the doc-tree-relative node path,
  e.g. [the domain skills](#/03-domain-skills); a nested page uses its full directory
  path, e.g. #/04-utility-skills/01-task-tree/02-cli-commands. The export's nav already
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

superRA turns an AI coding agent into a disciplined research assistant. It runs on Claude Code and Codex.

## What you get

- A **task-tree dashboard.** Every task's objective, status, and results are committed files in your repo, not an agent's memory, so you can watch progress live and hand any unfinished task to a fresh agent. This site is built on the same dashboard; the [Showcase](#/07-showcase) shows a real research tree.
- A **plan–implement–integrate [workflow](#/05-workflows)** — interactive by default, autonomous on request, with results kept reproducible.
- **[Domain skills](#/03-domain-skills)** that enforce the right discipline as the agent works: data analysis, theory modeling, academic writing, and slide design.
- **[Utility skills](#/04-utility-skills)** for practical mechanics: tracing each result to the code that produced it, merging branches by intent, loading papers from Zotero, syncing data across worktrees, and more.

## Why superRA

AI agents are fast but undisciplined. They write more code than anyone reviews, drift as their context fills, and drop half the sample before a regression, then report "everything looks good."

Frameworks such as [Superpowers](https://github.com/obra/superpowers) address this for software engineering, where unit tests verify the work and the goal is to take the human out of the loop. Research is different: it is exploratory, rarely testable in advance, and judged by people. superRA keeps the workflow spine and keeps you in the loop — review at every step, domain discipline as the work goes, and an integration phase that folds each task into a coherent codebase.

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

- **[PLAN](#/05-workflows/01-plan)** — the agent scopes your request into a *task tree*: a directory of small `task.md` files, one per unit of work, that you review before execution starts.
- **[IMPLEMENT](#/05-workflows/02-implement)** — the agent works each task with you, self-reviews, and asks whether to run an independent review now, later, or not at all. On request, autonomous mode hands the tasks to implementer and reviewer subagents.
- **[INTEGRATE](#/05-workflows/03-integrate)** — you choose which results enter the permanent record and how they are protected. The agent syncs with your base branch, writes the record, and proposes one refactoring task; once you approve, it executes and ships.

Research is rarely this linear. Each phase also runs alone; a surprise mid-implementation or a later scope change routes back to PLAN; and exploratory work can be recorded as tasks after the fact.

## Design principles

- **Review where it earns its cost.** Every task is self-reviewed against its objective. An independent review runs when the stakes or the agent's uncertainty call for one — in interactive mode, only after you agree — and once over all the work before it ships.
- **Forward by default, you decide what is yours.** Autonomous mode never stops to ask "should I proceed?"; it pauses for decisions that change a task's objective — methodology, scope, sample definitions — and at the workflow's set review points.
- **Domain-neutral.** Add your own domain skill (say, model simulation) without forking the workflow.

## Start here

| You want to | Go to |
|---|---|
| Try one analysis end to end, or bring in an existing project | [Quickstart](#/02-quickstart) |
| Pick the discipline for your work | [Domain Skills](#/03-domain-skills) |
| Learn the task tree, intent-aware merging, and result protection | [Utility Skills](#/04-utility-skills) |
| Know which tables and figures are out of date after an edit | [Reproducibility](#/04-utility-skills/09-reproducibility) |
| Understand one phase and what you decide in it | [Workflows](#/05-workflows) |
| See a real task tree | [Showcase](#/07-showcase) |
| Install, upgrade, or contribute | [README](README.md) |

superRA is open source and built for researchers comfortable with git and an AI harness.
