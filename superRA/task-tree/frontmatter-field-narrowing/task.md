---
title: "Narrow the Frontmatter Field Set to title/status/depends_on"
status: in-progress
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
