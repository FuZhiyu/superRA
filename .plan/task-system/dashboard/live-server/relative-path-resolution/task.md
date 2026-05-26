---
title: "Fix relative path resolution in rendered markdown"
status: not-started
review_status: ~
integration_status: ~
depends_on:  []
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

Relative paths in task.md markdown (links and images like `./diagram.png` or `../../scripts/foo.py`) are resolved against the project root, but they should be resolved against the task's own directory (`.plan/<task-path>/`).

**Current behavior:**
- `renderMarkdown(text, sectionName)` in `base.html` rewrites image `src` to `/files/{src}`
- The `/files/{path}` server route resolves against `_project_root` (parent of `.plan/`)
- A relative path like `./output.png` in `.plan/task-system/dashboard/task.md` resolves to `project_root/output.png` instead of `project_root/.plan/task-system/dashboard/output.png`

**Fix:**

1. **Frontend:** Pass the task path to `renderMarkdown()`. The task path is available on the DOM element as `data-path` attribute. Update the `renderMarkdown(text, sectionName, taskPath)` signature and resolve relative paths by prepending `.plan/{taskPath}/` before the `/files/` prefix:
   - Images: `/files/.plan/{taskPath}/{src}`
   - Links (non-http, non-anchor): `vscode://file/{PROJECT_ROOT}/.plan/{taskPath}/{href}`

2. **Call sites:** Update all places that call `renderMarkdown()` to pass the task path. The section-toggle expand handler at the bottom of `base.html` can walk up to the `.task-node` parent and read `dataset.path`.

3. **Server route:** No change needed — `/files/` already resolves against project root, and `.plan/task-system/dashboard/output.png` is a valid relative path from there.

**Files to modify:**
- `skills/task-system/scripts/templates/base.html` — update `renderMarkdown()` and its call sites

**Validation:** Add a test image or link in a task.md and verify it resolves correctly when expanded in the live dashboard.

## Results

