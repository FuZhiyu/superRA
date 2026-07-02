---
title: "Drop the Five Fields from the Data Layer, CLI, and Tests (Back-Compat Preserved)"
status: implemented
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

## Results

The five fields (`script`, `input`, `output`, `tags`, `created`) are gone from the data model and every read/write/validate/test path; the parser stays tolerant of legacy/unknown keys.

**Code changes (verified against the working tree):**

- **Data layer** (`_task_io.py`): the five fields are absent from the `Task` dataclass, `serialize_frontmatter`'s `field_order` (now `title`/`status`/`depends_on`), `write_task` (no `tags: []` write), and `parse_task` reads. `parse_frontmatter` is unchanged — it still reads every key into the dict, so unknown keys parse and are simply not picked up by `parse_task`.
- **Readable/JSON output** (`task_read.py`, `task_query.py`): the five dropped from `field_order` and JSON; all five added to `_STALE_FIELDS` (`task_read.py:165`) so a legacy file renders cleanly.
- **Placement smells** (`task_check.py`): the root-leaf-fields smell and the cross-subtree `output`-overlap check are removed here. Docstring section ref updated to `§Placing Work in the Existing Tree`. (The two smells this task left standing — single-child-root and root-leaf-beside-branch — were removed in full by the later `task-tree/top-level-task-shape` task, which dropped `check_placement` and the `placement` category entirely; current `task_check.py` carries no placement checks.)
- **Dashboard** (`templates/task_node.html`): the metadata-pill block reduced to the `depends` pill only; `script`/`tags`/`in`/`out` pills removed.
- **Migration** (`plan_migrate.py`), **fixtures** (`conftest.py`, `tests/test_state_preservation.py`), **tests** (`test_task_tree.py`, `test_dashboard.py`): field support removed; dead `tags=`/`script=`/`output=` kwargs (silently ignored no-ops) stripped from fixtures; the three tests that asserted now-removed behavior (`test_placement_flags_root_with_leaf_fields`, `test_placement_flags_cross_subtree_output_overlap`, `test_placement_ignores_generic_output_overlap`) deleted.

**Back-compat regression test (the executable guarantee):** `TestParseTask::test_legacy_fields_parse_and_are_dropped_on_rewrite` writes a `task.md` carrying all five retired fields plus an arbitrary unknown key (`some_future_key`), asserts it parses without error with the known fields intact, then asserts `write_task` drops all six keys and the result round-trips.

**Verification:**

- `pytest skills/task-tree/scripts` → 693 passed, 2 skipped at this task's own commit (was 3 failed before this work; net −2 from 3 stale tests deleted, 1 regression test added). The suite has moved since: `task-tree/top-level-task-shape` deleted further placement tests it obsoleted and a later maintenance pass (`fix(task-tree/scripts): remove two dead/duplicate tests`) un-shadowed a silently-duplicated test class, so the current authoritative count is **689 passed** (0 skipped) — re-verified in this integration pass.
- `python3 skills/task-tree/scripts/cli.py task check` parses this repo's tree — **304** tracked `task.md` files still carry legacy fields — with no field errors (only a pre-existing, unrelated `main-agent-trimming` placement warning). Back-compat proven end-to-end on real legacy data.
- Residual-reference grep over active `skills/task-tree/scripts/*.py`: only the intentional `_STALE_FIELDS` entry and unrelated `--output`/`args.output` CLI path flags remain.

**Final diff self-check (integration pass):** `git diff b57cb16b..HEAD -- skills/task-tree/scripts/_task_io.py skills/task-tree/scripts/task_check.py skills/task-tree/scripts/task_read.py skills/task-tree/scripts/task_query.py skills/task-tree/scripts/plan_migrate.py skills/task-tree/scripts/conftest.py skills/task-tree/scripts/tests/test_state_preservation.py skills/task-tree/scripts/test_task_tree.py skills/task-tree/scripts/templates/task_node.html skills/task-tree/scripts/_task_validate.py skills/task-tree/scripts/cli.py skills/task-tree/references/commands.md`; every surviving hunk is field-removal + back-compat test coverage tracing directly to this task's Objective (data-layer, CLI, dashboard template, fixtures, tests); no debug artifacts, no scope creep. No suspicious hunks. Full suite: `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts` → 689 passed.
