---
title: "Roll Back README + Rewrite Welcome (Dashboard-First)"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Establish the dashboard-first front-door messaging on the two entry surfaces — `README.md` and the welcome page `docs/site/01-welcome/task.md` — keeping their shared "what it is" content consistent (one agent writes both). Resolve the three inline `<!-- ... -->` author comments the user left in those files and delete the comments once addressed.

**README (`README.md`) — roll the writing style back and elevate the dashboard:**

- Restore the earlier enumerated style from commit `a9d09a3c` (run `git show a9d09a3c:README.md` to read it): an "It ships:" enumerated list of what superRA provides, and a "Why superRA?" section with the agents-are-undisciplined bullets — in place of the current flowing-paragraph rewrite (lines ~8–16).
- Fold the **task-tree dashboard** in as a first-class shipped item in the "It ships:" list (the earlier version predates the dashboard, so this is a merge, not a literal revert). Carry the monitoring + handoff + "this doc site is a dashboard export" framing from the subtree-root §Context, compressed to README scale.
- Keep what the `09-readme-front-door` invariant requires: the breaking-change banner, the doc-site link line, the PLAN→IMPLEMENT→INTEGRATE mermaid diagram and invoke keywords, the existing dashboard screenshot embed, the Claude Code install path, contributing/upstream/license. Keep the Superpowers attribution line.
- Delete the `<!-- I like my writing in the earlier version. help me roll it back -->` comment.

**Welcome page (`docs/site/01-welcome/task.md`) — adopt the earlier README style, dashboard-first, with the mermaid diagram:**

- Replace the long second paragraph with the bulleted style the user prefers. Realize the user's drafted "What it is:" list (currently lines 18–26) cleanly, with the **dashboard as the first item** and its self-referential hook ("You are viewing one — this documentation site is built on the dashboard"), followed by the plan-implement-integrate workflow, then the domain skills (data analysis, modeling, writing, slide design). Fix the draft's typos/grammar.
- Realize the user's drafted "Why superRA rather than a framework like Superpowers?" section (currently lines 29–33) into clean prose: existing agentic-coding frameworks target software engineering — verifiable tasks, unit tests, objective metrics, and a push to remove the human from the loop; social-science research is fluid and exploratory, ex-ante unit tests are often impossible, and outputs need human judgement, so superRA's design keeps the human in the loop. Characterize the contrast fairly per the subtree-root §Constraints.
- In "How it works", replace the hand-built HTML `<ol>` phase flow (lines 40–58) with the **mermaid diagram** from `README.md` (the `flowchart TB` with the dotted "plan change" arrows looping IMPLEMENT and INTEGRATE back to PLAN) — this is the "arrow pointing back" diagram the user's comment asks for. Keep the surrounding explanatory paragraphs.
- Delete both `<!-- ... -->` comments on this page once addressed.

Follow the authoring contract (frontmatter `title`-only — the welcome page keeps its scaffold frontmatter; one paragraph per line; hash/`#/` links; public-safe content). The "What it is" list wording must match the README's "It ships" items so the two front doors stay consistent.

Validation: render both surfaces in doc-mode (subtree-root Build command) and confirm the welcome mermaid diagram renders and the README still renders on GitHub; confirm no `<!-- -->` author comments remain in either file; confirm the dashboard appears as the first/lead feature in both.

## Results

