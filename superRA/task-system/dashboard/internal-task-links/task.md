---
title: "Internal task-to-task links"
status: approved
depends_on:
  - unify-static-export
tags: []
created: 2026-05-31
---

## Objective

When a task body in the dashboard contains a markdown link that points at another task in the same `.plan/` tree, the link should navigate **within the dashboard** to that task's card, not open a `task.md` file in VS Code. Today every relative link is rewritten to a `vscode://file/...` URI in `renderMarkdown` (`skills/task-system/scripts/templates/base.html`, the `container.querySelectorAll('a[href]')` block, currently ~line 1173–1179). Root `task.md` already cites sibling tasks this way — e.g. `[task-system/dashboard/view-navigation](task-system/dashboard/view-navigation/task.md)` — and those citations currently bounce the reader out to the editor instead of focusing the referenced card. Make in-tree task references resolve to internal navigation while leaving genuine file links (scripts, figures, non-`.plan` paths) on the existing `vscode://` behavior.

Implementation lives in `renderMarkdown(text, sectionName, taskPath)`. For each relative `a[href]` (the branch that already excludes `http://`, `https://`, and `#`):

1. Resolve the href against the current task's directory. `taskPath` is the active task's tree path; relative hrefs (`task.md`, `../merge/task.md`, `sibling/task.md`) resolve relative to `.plan/<taskPath>/`. Normalize `.`/`..` segments so the result is a clean tree path.
2. Decide whether the resolved target is a task in the tree. A target is an in-tree task reference when it points at a `task.md` (or at a task directory itself, with or without a trailing slash) whose tree path matches a known task. Determine "known task" from data already present client-side — every rendered task carries `.task-node[data-path]`, and the embedded task data enumerates task paths; pick whichever membership source is reliable. Strip the leading `.plan/` and trailing `/task.md` to get the canonical path used by `setActive` / the URL hash.
3. If it is an in-tree task: rewrite the link to internal navigation — set `href` to the hash form `#/<task-path>` (the existing `hashchange` handler + `setActive` already route this and update history; no new navigation entry point is needed), drop the `target="_blank"`, and tag it so it is visually distinguishable as an in-app link if useful (e.g. a class the stylesheet can hook). Clicking must focus the referenced card exactly as sidebar/DAG navigation does, including for nested and sibling targets.
4. If it is not an in-tree task (a script, a figure, a path outside `.plan/`, or a `task.md` path that does not exist): leave the current `vscode://file/...` rewrite untouched.

`renderMarkdown` is defined once in `base.html` but called from two sites (initial card render ~line 1341 and the live `serve` `/node/<path>` partial re-render ~line 1710); fixing the function covers both. After `[unify-static-export](../unify-static-export/task.md)` lands, the static export also renders from `base.html`, so this single fix covers the static export too — there is no longer a second copy to patch. Test against root `task.md`'s own `## Integration Notes`, which contains real sibling-task citations, and add a body link from one task to a nested non-sibling task to confirm `..`/deep-path resolution.

This is the navigation-behavior counterpart to the sibling `[hyperlink-styling](../hyperlink-styling/task.md)` task, which restyles link color/hover/visited states. Ensure internal task links still pick up the themed accent styling that task establishes (don't introduce a link variant that escapes the accent rule). Load `frontend-design` only if you add an in-app-link affordance (icon/class) that needs design judgment; the core change is the JS resolution-and-rewrite logic.

Validation: in both themes, clicking an in-tree task citation navigates to that task's card inside the dashboard (URL hash becomes `#/<path>`, back/forward work) and does **not** launch VS Code; links to scripts/figures/out-of-tree files still open via `vscode://`; resolution handles same-dir (`task.md`), sibling (`../slug/task.md`), and deep/nested targets. Verify in both the live `serve` dashboard and the static `generate` export. Regenerate or serve the dashboard to confirm.

## Results

In-tree task citations in any rendered task body now navigate **within** the dashboard instead of launching VS Code; genuine file links (scripts, figures, out-of-tree paths) keep the existing `vscode://file/...` rewrite. Implemented entirely in `base.html`'s `renderMarkdown`, so the live `serve` server and the static `generate` export inherit it from one source (per the `[unify-static-export](../unify-static-export/task.md)` unification this task depends on). The deep-path case is exercised live by this sentence's link to the nested non-sibling task `[routing-shell](../view-navigation/routing-shell/task.md)` — a `../slug/child/task.md` ref that resolves to `task-system/dashboard/view-navigation/routing-shell`.

### What changed

- **Membership oracle.** Added `TASK_PATHS`, a JS set of every task's tree path, emitted into the template from the `all_tasks` list both render paths already pass ([base.html:1256](../../../../skills/task-system/scripts/templates/base.html#L1256)). Built from the full tree rather than the DOM, so it stays complete even though the sidebar nav lazy-loads deep branches.
- **Resolver.** Added `resolveInternalTaskPath(href, taskPath)` ([base.html:1267](../../../../skills/task-system/scripts/templates/base.html#L1267)): strips any `#fragment`/`?query`, resolves the href against the active task's tree dir (`.plan/`-absolute and filesystem-absolute hrefs handled), normalizes `.`/`..` (over-popping past the root yields `null`), drops a trailing `task.md` or bare `/` so a directory ref and a `task.md` ref canonicalize identically, and returns the canonical tree path only when it is in `TASK_PATHS` — otherwise `null`.
- **Rewrite branch.** In the `a[href]` loop ([base.html:1321](../../../../skills/task-system/scripts/templates/base.html#L1321)), a relative href that resolves to a real task becomes `href="#/<task-path>"` with `target` dropped and a `task-link` class added; everything else keeps the `vscode://file/...` rewrite untouched. Internal navigation routes through the existing `hashchange` + `setActive` path — no new entry point. `setActive` → `loadActiveNode` fetches `/node/<path>` (resolved offline from the embedded fragments in standalone mode), so sibling, nested, and deep targets all focus correctly without the card needing to be pre-rendered.

### Styling

The `task-link` class is a non-visual hook only; no separate CSS rule was added, so internal links keep the themed `.rendered-md a` accent styling the sibling `[hyperlink-styling](../hyperlink-styling/task.md)` task establishes ([base.html:895](../../../../skills/task-system/scripts/templates/base.html#L895)) rather than escaping the accent rule. `frontend-design` was not needed — the change is pure resolution-and-rewrite logic, no new affordance.

### Verification

- `uv run pytest skills/task-system/scripts/test_task_system.py -q` → **180 passed** (includes `test_generate_embeds_internal_task_link_resolver`, a regression guard asserting `resolveInternalTaskPath` + `TASK_PATHS` survive into the embedded static export).
- A node harness over the actual resolver covered 15 cases — same-dir (`task.md`), sibling (`../slug/task.md`), deep/nested (`../slug/child/task.md`), directory refs with and without a trailing slash, `.plan/`-absolute, ancestor, `#fragment`/`?query` stripping, and root-task citations (empty `taskPath`) all resolve to internal paths; scripts, figures, nonexistent `task.md`, filesystem-absolute, root-escaping `..`, and out-of-tree paths all return `null` (keeping `vscode://`). A second harness over the full rewrite branch confirmed the internal case sets `#/<path>`, removes `target`, and adds `task-link`, while the file/external/`#`-anchor cases are left on their existing behavior.
- The root `task.md` citation `[task-system/planning-redesign/planmd-sweep](task-system/planning-redesign/planmd-sweep/task.md)` renders from the root task (`data-path=""`), so it resolves to `task-system/planning-redesign/planmd-sweep`, a known task → internal link. This is the real sibling-citation case the objective called for.
- Regenerated `.plan/dashboard.html` (`plan_dashboard.py generate`) and rendered the live `serve` index in-process: both embed `resolveInternalTaskPath` and a 100-entry `TASK_PATHS` set. Because both paths render from `base.html`, the static export and the live server are identical by construction.

