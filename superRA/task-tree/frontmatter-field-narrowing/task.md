---
title: "Narrow the Frontmatter Field Set to title/status/depends_on"
status: approved
depends_on: []
---

## Objective

Narrow the active `task.md` frontmatter schema to the three load-bearing fields — `title`, `status`, `depends_on` — and remove `script`, `input`, `output`, `tags`, and `created` from the data model, every CLI read/write/validate path, the test suite, and all instruction prose. After this work the contract claim in `skills/task-tree/references/task-file-contract.md` ("the frontmatter field set is **closed**: `title`, `status`, `depends_on` … any other key is discarded the next time a CLI mutation rewrites the file") is literally true.

**Why:** these five fields are no longer load-bearing. `script` / `input` / `output` encoded a per-task data-pipeline contract the workflow now carries as prose in `## Objective`; `tags` is unused; `created` is not a substitute for git history. They survive only as serializer/parser surface area and a `task_check` placement smell, and the docs already dropped them (this branch closes the resulting code↔docs gap).

**Hard backward-compatibility requirement:** the parser must keep tolerating task files that still carry these fields (and any other unknown key) without error. Today `parse_frontmatter` reads frontmatter into a dict and `parse_task` picks only known keys, so unknown keys parse and are ignored, dropped only on the next CLI rewrite. **Do not** add strict frontmatter-key validation that would reject legacy files. No bulk migration of existing `task.md` files is required — they shed the fields naturally as they are next rewritten.

### Constraints

- Editing any `skills/*/SKILL.md` requires loading `skill-creator` first and applying the root `CLAUDE.md` DRY + Necessity gate line by line (see the docs subtask).
- The closed field set is single-sourced: the `serialize_frontmatter` docstring in `_task_io.py` points at `task-file-contract.md §Field-by-Field Notes`. Keep that pointer accurate.

This is a code-and-tests task (`01-code-and-compat`) followed by a prose-propagation task (`02-docs-propagation`).

## Results

Both children complete the objective: the frontmatter field set is narrowed to `title`/`status`/`depends_on` across the data layer, CLI, tests, and instruction prose, with legacy-field back-compat preserved and verified end to end. Per-task evidence lives in [01-code-and-compat](01-code-and-compat/task.md) and [02-docs-propagation](02-docs-propagation/task.md).

**Final diff self-check (integration pass):** re-ran the full drift suite after this task's own governing-diff refactor pass — `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts` → 689 passed — and `python3 skills/task-tree/scripts/cli.py task check` → "All checks passed. No issues found." No surviving hunks under this parent path beyond what its two children own; see their self-checks for the file-level triage.

## Revision Notes
Maturation decision (2026-07-01 integration pass): fold children `01-code-and-compat` and `02-docs-propagation` into this parent — distil `## Results` to one short self-contained subsection (fields dropped, back-compat guarantee + regression test, docs propagated), remove the two child directories and the integration self-check trails.
