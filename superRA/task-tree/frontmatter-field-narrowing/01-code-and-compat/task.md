---
title: "Drop the Five Fields from the Data Layer, CLI, and Tests (Back-Compat Preserved)"
status: not-started
depends_on: []
---

## Objective

Remove `script`, `input`, `output`, `tags`, and `created` from the task-tree data model and every code path that reads, writes, validates, or tests them, while keeping the parser tolerant of legacy/unknown keys (no errors, no strict key validation).

### Code changes

- **`skills/task-tree/scripts/_task_io.py`**
  - Drop the five fields from the `Task` dataclass (currently lines ~97–101).
  - Remove them from `serialize_frontmatter`'s `field_order` (~306–310) so they are no longer emitted.
  - Remove the conditional writes in `write_task` (~424–435), including the *unconditional* `tags: []` write. Preserve the existing `depends_on` write behavior.
  - Remove the reads in `parse_task` (~394–399). Leave `parse_frontmatter` unchanged — it must keep accepting unknown keys into the dict so legacy files don't error.
- **`skills/task-tree/scripts/task_read.py`** — remove the five from `_render_frontmatter_readable`'s `field_order` (~162–163) and from the JSON output (~310–314). Add the five to the `_STALE_FIELDS` suppression set (~167) so a legacy file still carrying them renders cleanly.
- **`skills/task-tree/scripts/task_query.py`** — remove the five from JSON output (~227–231).
- **`skills/task-tree/scripts/task_check.py`** — remove Smell 1 (the "root carries leaf-only `script`/`input`/`output`" check, ~234–252) entirely; it is meaningless once the fields are gone. Update or delete the function docstring's stale section reference (`§Placing Work by Durable Home` → `§Placing Work in the Existing Tree`, ~225). Keep Smell 2 (single-child-root wrapper).
- **`skills/task-tree/scripts/plan_migrate.py`** — stop extracting/emitting `script`/`input`/`output` from legacy `PLAN.md` (~29–31, ~347–349); legacy migration no longer produces these fields.
- **`skills/task-tree/scripts/conftest.py`** and **`skills/task-tree/scripts/tests/test_state_preservation.py`** — remove the fixture-builder support for these fields (conftest ~37, 40, 66–68; mirror in test_state_preservation ~39, 43).
- **`skills/task-tree/scripts/test_task_tree.py`** and the other test modules — update the ~143 references: drop assertions on these fields' round-trip, and **add a regression test** that a `task.md` carrying all five legacy fields (plus an arbitrary unknown key) parses without error and that the fields are dropped on the next `write_task`. This test is the executable form of the back-compat guarantee.

### Validation

- `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts` — all green.
- `python3 skills/task-tree/scripts/cli.py task check` passes on this repo's own `superRA/` tree (which still contains legacy fields) — proving back-compat end to end.
- Grep for residual attribute access (`\.script\b`, `\.input\b`, `\.output\b`, `\.tags\b`, `\.created\b`) and `"script"|"input"|"output"|"tags"|"created"` keys in active `skills/task-tree/scripts/` code; remaining hits are only the `_STALE_FIELDS` suppression entry and ordinary prose/variable names.
