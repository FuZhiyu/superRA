---
title: "Dashboard-First Messaging Revision"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Revise the superRA front-door and documentation messaging on two user-directed fronts: (1) roll the README prose back to the earlier enumerated/bulleted style the user prefers, and (2) elevate the **task-tree dashboard** from an incidental tool to a first-class, top-billed feature across the README and the docs site. The welcome page is rewritten to match, the dashboard-first framing is propagated to the other pages that describe it, and the whole doc set is then audited from a new user's perspective.

Editing the rendered doc pages means editing the `docs/site/**/task.md` body bodies (the doc source) and `README.md` — not the `superRA/` task files of this subtree.

### Context

This subtree is a follow-on messaging revision, distinct from the original build tasks [`09-readme-front-door`](../09-readme-front-door/task.md) (README structure) and [`03-landing-and-concepts`](../03-landing-and-concepts/task.md) (landing + concept pages), which stay approved. The authoring contract those tasks follow still governs: [`01-information-architecture` §3](../01-information-architecture/task.md) (frontmatter `title`-only, hash links `#/<path>`, repo-file links via the GitHub blob base, one paragraph per line, public-safe examples only).

**The dashboard, elevated — the message every page in this subtree must carry.** superRA's project state is not just plain files; it ships a **live task-tree dashboard** (`./superRA/superra dashboard`) that is two things at once:

- A **monitoring and steering** surface — tree, dependency DAG, and kanban views that auto-update as tasks progress, so you watch and direct the work in flight.
- A **handoff** surface — because the entire project state lives in the tree the dashboard renders, you (or a fresh agent session a week later) can pick up exactly where work left off, with no lost thread.

The proof point is self-referential: **this documentation site is itself a superRA dashboard export** (doc-mode rendering of the `docs/site/` tree). "You are viewing one." Use this dogfooding hook where it earns its place; do not over-repeat it on every page.

### Constraints

- Roll back the README *writing style* to the earlier enumerated form (the "It ships: 1/2/3" + "Why superRA?" bulleted structure from commit `a9d09a3c`), but fold the dashboard in as a first-class shipped feature — the earlier version predates the dashboard emphasis, so this is a merge of the two, not a literal revert.
- Keep the README self-sufficient for a 60-second GitHub evaluation (the `09-readme-front-door` invariant): what superRA is, why it exists, the dashboard, the workflow diagram, install.
- The "Why superRA vs. a software-engineering framework like Superpowers" contrast must characterize superRA's own design emphasis (human-in-the-loop for exploratory, judgement-heavy social-science research) fairly — frame the difference in research workflow, not as a knock on Superpowers.

**Writing workflow:** Draft / Polish workflow

**Writing targets:** `README.md`; `docs/site/01-welcome/task.md`; and, for propagation, the dashboard-bearing pages under `docs/site/03-concepts/`, `docs/site/04-how-to/04-see-your-work/`, and `docs/site/06-showcase/`.

**Audience:** Prospective and new superRA users — academic researchers comfortable with git and an AI coding harness (Claude Code or Codex), evaluating whether to adopt superRA and learning basic use. Not assumed to know superRA internals or vocabulary (task tree, frontier, drift test, implementer/reviewer pair). The README reader may be giving a 60-second GitHub skim. This is the IA's approved primary audience.

**Mode:** Polish, with restructuring authorized for the welcome page and README (this subtree rewrites their structure, not just sentences); the audit task adds a Review lane.

**Build command:** Preview rendered output live in doc-mode — `uv run --script skills/task-tree/scripts/plan_dashboard.py dashboard --doc-mode --root docs/site` — not a `file://` open (inlined CSS caches stale). The GitHub Pages deploy pipeline is owned by `08-deploy` and is out of scope here.

**Writing output:** Edited `README.md`, welcome page, and propagated pages; new-user audit findings and applied fixes recorded in `03-new-user-audit`.

## Results

