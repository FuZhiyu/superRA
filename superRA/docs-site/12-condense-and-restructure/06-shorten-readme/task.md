---
title: "Shorten README into a Front Door Pointing at the Docs"
status: implemented
depends_on:
  - 01-ia-and-scaffold
tags: []
created: 2026-06-17
---

## Objective

Now that the docs site is the condensed, authoritative source, shorten the repo-root `README.md` into a true front door: a tight pitch plus pointers into the docs, rather than a second copy of the content. The earlier [`09-readme-front-door`](../../09-readme-front-door/task.md) pass split README into a front door against the *old* six-section docs; this pass tightens it further and repoints it at the new structure.

- Keep: the one-paragraph pitch, the install commands, and the contributor/license essentials a GitHub visitor needs without leaving the README.
- Cut: anything the docs now own — extended concept explanations, the full workflow narrative, per-skill detail. Replace with links to the new pages (Welcome, Quickstart, Domain Skills, Utility Skills).
- Point links at the deployed docs site (use the same link convention `09-readme-front-door` established for README→docs links).
- Do not duplicate the docs audience principle's failure mode: the README should make a visitor want to read the docs, not substitute for them.

Verify no README link points at a dropped docs page (Concepts/How-To).

## Planner Guidance

Read the current `README.md` and `docs/README.codex.md` / `docs/README.opencode.md` to see what front-door material already exists. This is a trim-and-repoint pass, not a rewrite — preserve the existing voice and the contributor-facing sections.

## Results

[README.md](../../../../README.md) is repointed at the new six-page docs structure and lightly tightened, with the existing front-door voice and all contributor-facing sections (Installation, Contributing, Upstream, License, the 0.2.0 banner) preserved. The heavy trim already happened in [`09-readme-front-door`](../../09-readme-front-door/task.md) (252 → ~98 lines); this pass is the structural repoint plus one redundancy cut, leaving the README a self-sufficient 60-second GitHub read that funnels visitors into the docs rather than restating them.

### Links repointed off the dropped Concepts/How-To pages

The new structure drops `03-concepts` (5 pages) and `04-how-to` (6 pages) — their ideas now live inline in the Quickstart and on the two new skills pages. Every README link that pointed at a dropped page was moved to its surviving home, keeping the established `http://fuzhiyu.me/superRA/#/<path>` deep-link convention from `09-readme-front-door`:

| Old README link (dropped) | Repointed to |
|---|---|
| `#/04-how-to`, `#/03-concepts` (top banner) | `#/03-domain-skills` + `#/04-utility-skills` |
| `#/03-concepts` (workflow section) | `#/02-quickstart` (walks each phase, re-entry, human-in-the-loop) |
| `#/04-how-to/04-see-your-work` (dashboard guide) | `#/02-quickstart` (covers live serve + branch-snapshot sharing) |
| `#/03-concepts/04-skills-and-agents` (skills model) | `#/03-domain-skills` + `#/04-utility-skills` |
| `#/03-concepts/03-roles-and-review` (implementer/reviewer) | `#/02-quickstart` (roles introduced inline) |
| `#/04-how-to/01-install-and-set-up` (multi-harness install) | [`docs/README.codex.md`](../../../../docs/README.codex.md) (Codex setup + local-clone install) |

Links at surviving pages were left unchanged: `#/05-reference`, `#/05-reference/04-skills-and-agents`, `#/05-reference/07-hooks`, `#/06-showcase` (Reference is kept as-is; its subpages still exist).

### Tightening

- Folded two adjacent Quickstart pointers in the workflow section into one ([README.md:53-55](../../../../README.md#L53-L55)): the bare "describe what you want" invoke line no longer carries its own Quickstart link, and the dashboard paragraph's Quickstart pointer now also absorbs the re-entry / human-in-the-loop mention.
- The install pointer no longer claims a dropped page covers Copilot/Gemini and a local clone (the now-deleted how-to install page was their only home); it points at `docs/README.codex.md` for the paths that survive and notes that any skills+subagents harness installs the same plugin sources.

The mermaid PLAN→IMPLEMENT→INTEGRATE diagram, the invoke keywords, the one dashboard screenshot, and the pitch/why-superRA framing are kept as the 60-second-evaluation essentials per the `09-readme-front-door` baseline.

### Variant READMEs

`docs/README.codex.md` and `docs/README.opencode.md` carry no docs-site links (`grep` for `fuzhiyu.me`/`#/`/dropped slugs → none), so they needed no repointing. `README.opencode.md` is upstream OpenCode setup content, not a superRA install front door, so the install pointer routes to `README.codex.md` instead.

### Verification

- `grep '03-concepts\|04-how-to' README.md` → no matches. No README link points at a dropped page.
- All 7 remaining hash routes resolve to a real `docs/site/<path>/task.md` node (`02-quickstart`, `03-domain-skills`, `04-utility-skills`, `05-reference`, `05-reference/04-skills-and-agents`, `05-reference/07-hooks`, `06-showcase`) — verified by file existence.
- All repo-file links resolve: `docs/README.codex.md`, `CLAUDE.md`, `RELEASE-NOTES.md`, `LICENSE`, `docs/assets/task-tree-dashboard.png`.
- `check_markdown.py README.md` → clean.

### Caveat

As with `09-readme-front-door`, the `http://fuzhiyu.me/superRA/#/...` deep links are dead until this branch lands on `main` and the Pages deploy fires; the new `03-domain-skills`/`04-utility-skills` routes additionally require those pages to carry content (authored by sibling tasks `03`/`04`). Both are expected for a pre-merge front door, not a defect.
