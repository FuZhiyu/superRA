---
title: "Propagate the Narrowed Field Set Across Instruction Prose"
status: implemented
depends_on:
  - 01-code-and-compat
---

## Objective

Remove every prose reference to `script`, `input`, `output`, `tags`, and `created` as task-frontmatter fields across the skill and reference docs, so no instruction tells an agent to write or maintain a field the code no longer carries. The contract's closed-set statement is already narrowed (`skills/task-tree/references/task-file-contract.md`); this task closes the remaining prose gaps.

### Known references to update

- **`skills/task-tree/references/task-file-contract.md`** — the §Stale Content rule that says to "rewrite the earlier task's `output:` frontmatter" (~line 47). Recast it in terms of the task's `## Objective` / `## Results`, not an `output:` field.
- **`skills/task-tree/references/internals.md`** — the `Task` dataclass listing (~25–29) still documents the five fields. Drop them.
- **`skills/superplan/references/harness-plan-mode.md`** — the plan-file template (~50–52) lists `**script:** / **input:** / **output:**`. Remove them.
- **`skills/superplan/references/consolidation.md`** — the survey step "declared `script` / `input` / `output`" (~line 30) and the Merge / Mature-Rename / Scope-Expansion action blocks (~55, 58, 70) that say to "update scope-defining `script` / `input` / `output` fields." Recast as objective/`depends_on` scope; drop the field names.
- **`skills/superplan/SKILL.md`** — the §User Feedback material-change list item "Changing a task's objective, script, input, or output." Reduce to "Changing a task's objective."
- **`skills/task-tree/scripts/_task_io.py`** docstring on `serialize_frontmatter` — confirm it still names the contract section correctly and does not enumerate the removed fields.
- **`skills/task-tree/SKILL.md`** — the example frontmatter is already trimmed; confirm no residual field mentions remain in the body.

### Sweep

Grep all `skills/**/*.md` and `agents/**/*.md` for residual `^\s*(script|input|output|tags|created):` field forms and for `script` / `input` / `output` used as task-field prose; reconcile anything the list above missed. Historical/completed `superRA/**/task.md` files and `docs/` fixtures that merely *carry* the legacy fields are accurate history and back-compat-safe — leave them; only fix active instruction prose.

### Validation

- Grep sweep above returns only intentional residue (e.g. `_STALE_FIELDS`, historical task bodies).
- `python3 skills/task-tree/scripts/cli.py task check` still clean.

## Results

All prose references to the five removed task-frontmatter fields (`script`, `input`, `output`, `tags`, `created`) are gone from active instruction docs. No instruction now tells an agent to write or maintain a field the data layer dropped in `01-code-and-compat`.

### Edits made

- [task-file-contract.md:47](../../../../skills/task-tree/references/task-file-contract.md#L47) — §Stale Content rule recast from "rewrite the earlier task's `output:` frontmatter" to "rewrite [the task's] `## Objective` or `## Results` descriptions in place."
- [internals.md:24-25](../../../../skills/task-tree/references/internals.md#L24-L25) — dropped the five fields (`tags`/`script`/`input`/`output`/`created`) from the `Task` dataclass listing, matching the actual dataclass in [_task_io.py:88](../../../../skills/task-tree/scripts/_task_io.py#L88).
- [internals.md](../../../../skills/task-tree/references/internals.md) — additionally dropped the stale `script`/`input`/`output` rows from the PLAN.md-migration `FIELD_RE` table (and the now-dead `_extract_file_list` sentence); the migrator's `FIELD_RE` in [plan_migrate.py:25-29](../../../../skills/task-tree/scripts/plan_migrate.py#L25-L29) no longer extracts those fields, so the table was factually wrong, not just legacy history. Not in the original list — found via the sweep.
- [harness-plan-mode.md:49](../../../../skills/superplan/references/harness-plan-mode.md#L49) — removed the `**script:** / **input:** / **output:**` lines from the plan-file template.
- [consolidation.md](../../../../skills/superplan/references/consolidation.md) — recast the survey step (line 30), the Merge Pairwise block (~55), the Mature/Rename block (~58), and the Scope-Expansion block (~70) to talk about objective/`depends_on` scope; dropped the field names.
- [SKILL.md:179](../../../../skills/superplan/SKILL.md#L179) — material-change list item reduced to "Changing a task's objective."
- [task-tree-design.md:14](../../../../skills/superplan/references/task-tree-design.md#L14) — folded the stale "Fixed `script` / `input` / `output` expectations when they define scope" bullet into the adjacent input/output-expectations bullet (now names scripts/files/artifacts generically). Not in the original list — found via the sweep.
- [internals.md:189](../../../../skills/task-tree/references/internals.md#L189) — dropped `, **Script:** *(none)*` from the legacy-PLAN.md normalization checklist (the migrator's `FIELD_RE` no longer consumes `script`). Revise-round fix for the reviewer's MAJOR: the original field-form sweep missed it because the field is a mid-line backtick span (`**Script:**`), not line-anchored. A re-sweep for `**Script:**`/`**Input:**`/`**Output:**` task-field prose across active docs now returns only legacy-PLAN.md test fixtures in `test_task_tree.py` (migrator input data, not instructions).

### Confirmed no change needed

- [_task_io.py:291-298](../../../../skills/task-tree/scripts/_task_io.py#L291-L298) — `serialize_frontmatter` docstring already names `task-file-contract.md §Field-by-Field Notes` correctly and `field_order` is already `["title", "status", "depends_on"]`.
- [task-tree/SKILL.md](../../../../skills/task-tree/SKILL.md) — no residual field mentions in the body.
- `skills/using-superra/references/codex-instructions.md` — left untouched (unrelated pre-existing uncommitted intro-paragraph edit), not staged.

### Validation

- Field-form sweep (`^\s*(\*\*)?(script|input|output|tags|created)\s*:` over `skills/**/*.md`, `agents/**/*.md`) returns only `report-in-markdown/references/baseline-io.md` (report-artifact frontmatter `tags`, not task frontmatter).
- Task-field prose sweep (backtick-wrapped field names) returns only out-of-domain hits: Quarto `output` kwarg in `julia-quarto-guide.md`, report `tags` in `baseline-io.md`, Zotero `tags` API in `zotero-paper-reader/SKILL.md`.
- `python3 skills/task-tree/scripts/cli.py task check` — clean at this task's own commit (0 errors; one pre-existing, unrelated `main-agent-trimming` placement advisory). The `task-tree/top-level-task-shape` task later dropped the `placement` check category entirely, so the current authoritative result is "All checks passed. No issues found." — re-verified in this integration pass.

**Final diff self-check (integration pass):** `git diff b57cb16b..HEAD -- skills/task-tree/references/task-file-contract.md skills/task-tree/references/internals.md skills/superplan/references/harness-plan-mode.md skills/superplan/references/consolidation.md skills/superplan/SKILL.md skills/superplan/references/task-tree-design.md`; every surviving hunk is a prose-propagation fix tracing to this task's Objective (dropping script/input/output/tags/created prose, retargeting section pointers). Fixed one leftover formatting artifact from this task's own edit: a double blank line left in `task-file-contract.md` after the "Branch tasks … do not carry `script`/`input`/`output`" bullet was deleted ([task-file-contract.md:20-21](../../../../skills/task-tree/references/task-file-contract.md#L20-L21) before the fix). No other suspicious hunks; the residual `**Script:**` sweep and field-form greps still return only out-of-domain hits after the later top-level-task-shape and terminology-sweep commits. Full suite: `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts` → 689 passed.
