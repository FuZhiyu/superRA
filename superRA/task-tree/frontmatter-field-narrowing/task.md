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

- Editing any `skills/*/SKILL.md` requires loading `skill-creator` first and applying the root `CLAUDE.md` DRY + Necessity gate line by line.
- The closed field set is single-sourced: the `serialize_frontmatter` docstring in `_task_io.py` points at `task-file-contract.md §Task Anatomy`. Keep that pointer accurate.

## Results

The frontmatter field set is narrowed to `title`/`status`/`depends_on` across the data layer, CLI, tests, and instruction prose, with legacy-field back-compat preserved and verified end to end.

- **Data layer and CLI:** `script`, `input`, `output`, `tags`, `created` are gone from the `Task` dataclass, `serialize_frontmatter`, `write_task`, `parse_task`, readable/JSON output (`task_read.py`, `task_query.py`), the `task_check.py` placement smell that inspected them, `plan_migrate.py`, and the dashboard template. `parse_frontmatter` stays tolerant of unknown keys, so legacy files carrying these fields still parse without error and shed them on the next `write_task`.
- **Back-compat regression test:** `TestParseTask::test_legacy_fields_parse_and_are_dropped_on_rewrite` in `skills/task-tree/scripts/test_task_tree.py` is the executable guarantee — a `task.md` carrying all five legacy fields plus an unknown key parses cleanly and the fields are dropped on rewrite.
- **Docs propagated:** every prose reference to the five fields as task-frontmatter fields is removed from active instruction docs — `task-file-contract.md`, `internals.md`, `harness-plan-mode.md`, `consolidation.md`, `superplan/SKILL.md`, `task-tree-design.md` — so no instruction tells an agent to write or maintain a field the code no longer carries.
- **Verification:** `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts` → 689 passed; `python3 skills/task-tree/scripts/cli.py task check` clean; back-compat proven end to end against this repo's own tree (304 tracked `task.md` files still carrying legacy fields, all parsed with no errors).
