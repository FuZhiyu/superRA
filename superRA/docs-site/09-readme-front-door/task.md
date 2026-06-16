---
title: "README Front-Door Restructure"
status: approved
depends_on:
  - 08-deploy
  - 04-quickstart-tutorial
  - 05-how-to-guides
  - 06-reference
tags: []
created: 2026-06-10
---

## Objective

Restructure `README.md` into the front door. The section-by-section disposition approved in `01-information-architecture` governs; the lists below are the planner-expected baseline the IA refines, not an independent second spec:

- **Keeps:** the pitch / why-superRA, the workflow diagram, one task-tree visual (screenshot or rendered-tree image), the Claude Code install path, a quickstart pointer, and prominent links into the site (tutorial, guides, reference, showcase).
- **Moves to the site:** the skill and hook inventory tables, multi-harness install detail, and extended principle prose — each replaced by a one-line pointer to its new page.
- README stays self-sufficient for the 60-second GitHub evaluation: a reader who never leaves the README still learns what superRA is, why it exists, and how to install it on Claude Code.

Sweep for coherence after the trim: no orphaned in-README anchors; inbound references to moved sections (`docs/README.codex.md`, `docs/README.opencode.md`, `CLAUDE.md`, contributing/marketplace surfaces) re-pointed; manifest homepage fields consistent with the live site URL from `08-deploy`.

Validation: every removed section's content is reachable from the README via exactly one link hop; repo-wide grep shows no dangling links to removed anchors.

## Results

[README.md](../../../../README.md) is restructured into a front door per the governing disposition in [`01-information-architecture` §4](../01-information-architecture/task.md). It dropped from 252 lines to ~80: the long inventory tables and multi-harness install detail moved to the live site, each replaced by a one-line pointer, while the 60-second-evaluation essentials stay in place.

### What stayed (self-sufficient for the GitHub 60-second read)

- The 0.2.0 breaking-change banner (top of file, release-critical).
- A condensed pitch (the agents-are-undisciplined framing) voiced to match the site landing page ([docs/site/01-welcome/task.md](../../../../docs/site/01-welcome/task.md)), with the three discipline ideas — implementer–reviewer pair, domain skills, task tree + integration phase — folded into the pitch as bullets (this absorbs the old "Why superRA?" and "Key principles" prose).
- The PLAN→IMPLEMENT→INTEGRATE mermaid diagram (unchanged) plus the invoke keywords.
- One task-tree visual: the dashboard workspace screenshot, copied to [docs/assets/task-tree-dashboard.png](../../../../docs/assets/task-tree-dashboard.png) (reused from the quickstart attachments — public-safe simulated-equity content, no real data) and embedded with a repo-root-relative path so it renders on GitHub.
- The Claude Code install path (marketplace add + install + update).
- Contributing → `CLAUDE.md`, Upstream attribution, License.

### What moved to the site (each a one-hop pointer)

Every removed/moved section is reachable from the README in exactly one link hop, and every deep link is an absolute site URL whose hash route resolves to a real `docs/site` node (verified — see Validation):

| Removed/moved from README | One-hop README pointer |
|---|---|
| Workflow detail + key principles | `#/03-concepts` |
| Dashboard / artifact-share paragraphs | `#/04-how-to/04-see-your-work` |
| Domain Skills table | `#/03-concepts/04-skills-and-agents` |
| Utility Skills table | `#/05-reference/04-skills-and-agents` |
| Agents table | `#/03-concepts/03-roles-and-review` |
| Hooks table | `#/05-reference/07-hooks` |
| Codex / Other-Platforms / local-clone install detail | `#/04-how-to/01-install-and-set-up` |

The top-of-file documentation banner additionally surfaces direct links to Quickstart (`#/02-quickstart`), How-To (`#/04-how-to`), Concepts, Reference (`#/05-reference`), and Showcase (`#/06-showcase`), satisfying the "prominent links into the site (tutorial, guides, reference, showcase)" keep.

**Cross-task touch (sanctioned by review):** the old README's local-clone development-install guidance (clone command + personal-marketplace-entry note) had no surviving home after the trim — the install guide's development-or-forking paragraph deferred back to the README installation section it replaced. Per review item 1, that guidance is absorbed into [docs/site/04-how-to/01-install-and-set-up/task.md:33-40](../../../../docs/site/04-how-to/01-install-and-set-up/task.md#L33-L40) and the back-pointer to `README.md#installation` is dropped. This edits a page owned by the approved `05-how-to-guides` task, consistent with IA §4's "`04-how-to/01-install-and-set-up/` mirrors and expands" the README install section.

### Manifest homepage fields

Both manifests point at the live site from [`08-deploy` §Results](../08-deploy/task.md):

- [.claude-plugin/plugin.json](../../../../.claude-plugin/plugin.json): added `"homepage": "http://fuzhiyu.me/superRA/"` (field was absent).
- [.codex-plugin/plugin.json](../../../../.codex-plugin/plugin.json): repointed `homepage` and `interface.websiteURL` from the GitHub repo URL to the site URL; `repository` left at the GitHub URL (it is the source-repo field, not a homepage).

Per the dispatch, the repo About-field update is a landing-time admin follow-up recorded in `08-deploy`, not attempted here.

### Validation

- **Hash-route resolution:** all 11 site deep links extracted from the README resolve to a real `docs/site/<path>/task.md` node (`02-quickstart`, `03-concepts` + `03-roles-and-review` + `04-skills-and-agents`, `04-how-to` + `01-install-and-set-up` + `04-see-your-work`, `05-reference` + `04-skills-and-agents` + `07-hooks`, `06-showcase`).
- **One-hop reachability:** each removed/moved section maps to exactly one direct README link (table above); the "dropped" key-principles prose is absorbed into the pitch and the workflow/concepts pointers, not orphaned.
- **No dangling anchors:** the README carries zero internal `#anchor` self-links, so the trim orphaned none. Repo-wide grep (all `.md`/`.json`/`.toml`, including `docs/site`) finds one inbound `README.md#<section-anchor>` link — the install guide's back-pointer to `README.md#installation` — which review item 1 removed by absorbing the content it deferred to; after that fix the grep shows no remaining fragment-anchor links into the README outside this task's own Review Notes prose (which quotes the fixed bug, not navigation). The `README.md#L<n>` hits are line-number provenance citations inside historical task records (not navigation, not owned by this task).
- **Local file links exist:** `./CLAUDE.md`, `RELEASE-NOTES.md`, and the embedded screenshot all resolve.
- **JSON validity:** both manifests parse (`json.load`).
- **Render integrity:** `check_markdown.py README.md` → clean.

### Caveat

Deep links use the final production URL `http://fuzhiyu.me/superRA/#/...` directly (per dispatch: the README lands in the same merge that brings the site live). The links are dead until this branch lands on `main` and the push-trigger deploy fires (`08-deploy` confirms the deploy is gated to `main`). This is expected and by design, not a defect.
