---
title: "Internal task-to-task links"
status: not-started
depends_on:  []
tags: []
created: 2026-05-31
updated: 2026-05-31
---

## Objective

When a task body in the dashboard contains a markdown link that points at another task in the same `.plan/` tree, the link should navigate **within the dashboard** to that task's card, not open a `task.md` file in VS Code. Today every relative link is rewritten to a `vscode://file/...` URI in `renderMarkdown` (`skills/task-system/scripts/templates/base.html`, the `container.querySelectorAll('a[href]')` block, currently ~line 1173–1179). Root `task.md` already cites sibling tasks this way — e.g. `[task-system/dashboard/view-navigation](task-system/dashboard/view-navigation/task.md)` — and those citations currently bounce the reader out to the editor instead of focusing the referenced card. Make in-tree task references resolve to internal navigation while leaving genuine file links (scripts, figures, non-`.plan` paths) on the existing `vscode://` behavior.

Implementation lives in `renderMarkdown(text, sectionName, taskPath)`. For each relative `a[href]` (the branch that already excludes `http://`, `https://`, and `#`):

1. Resolve the href against the current task's directory. `taskPath` is the active task's tree path; relative hrefs (`task.md`, `../merge/task.md`, `sibling/task.md`) resolve relative to `.plan/<taskPath>/`. Normalize `.`/`..` segments so the result is a clean tree path.
2. Decide whether the resolved target is a task in the tree. A target is an in-tree task reference when it points at a `task.md` (or at a task directory itself, with or without a trailing slash) whose tree path matches a known task. Determine "known task" from data already present client-side — every rendered task carries `.task-node[data-path]`, and the embedded task data (`__TASK_DATA_JSON__`) enumerates task paths; pick whichever membership source is reliable in both the static-export and live-serve render paths. Strip the leading `.plan/` and trailing `/task.md` to get the canonical path used by `setActive` / the URL hash.
3. If it is an in-tree task: rewrite the link to internal navigation — set `href` to the hash form `#/<task-path>` (the existing `hashchange` handler + `setActive` already route this and update history; no new navigation entry point is needed), drop the `target="_blank"`, and tag it so it is visually distinguishable as an in-app link if useful (e.g. a class the stylesheet can hook). Clicking must focus the referenced card exactly as sidebar/DAG navigation does, including for nested and sibling targets.
4. If it is not an in-tree task (a script, a figure, a path outside `.plan/`, or a `task.md` path that does not exist): leave the current `vscode://file/...` rewrite untouched.

Both render paths must behave identically: the static one-shot dashboard export and the live `serve` path that fetches `/node/<path>` partials and re-runs `renderMarkdown` (the second call site, ~line 1710). Test against root `task.md`'s own `## Integration Notes`, which contains real sibling-task citations, and add a body link from one task to a nested non-sibling task to confirm `..`/deep-path resolution.

This is the navigation-behavior counterpart to the sibling `[hyperlink-styling](../hyperlink-styling/task.md)` task, which restyles link color/hover/visited states. The two are independent in code (JS link rewriting here vs. CSS there) and can proceed in parallel; ensure internal task links still pick up the themed accent styling that task establishes (don't introduce a link variant that escapes the accent rule). Load `frontend-design` only if you add an in-app-link affordance (icon/class) that needs design judgment; the core change is the JS resolution-and-rewrite logic.

Validation: in both themes and both render paths, clicking an in-tree task citation navigates to that task's card inside the dashboard (URL hash becomes `#/<path>`, back/forward work) and does **not** launch VS Code; links to scripts/figures/out-of-tree files still open via `vscode://`; resolution handles same-dir (`task.md`), sibling (`../slug/task.md`), and deep/nested targets. Regenerate or serve the dashboard to confirm.

## Results

