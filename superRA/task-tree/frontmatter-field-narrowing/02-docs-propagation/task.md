---
title: "Propagate the Narrowed Field Set Across Instruction Prose"
status: revise
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

### Confirmed no change needed

- [_task_io.py:291-298](../../../../skills/task-tree/scripts/_task_io.py#L291-L298) — `serialize_frontmatter` docstring already names `task-file-contract.md §Field-by-Field Notes` correctly and `field_order` is already `["title", "status", "depends_on"]`.
- [task-tree/SKILL.md](../../../../skills/task-tree/SKILL.md) — no residual field mentions in the body.
- `skills/using-superra/references/codex-instructions.md` — left untouched (unrelated pre-existing uncommitted intro-paragraph edit), not staged.

### Validation

- Field-form sweep (`^\s*(\*\*)?(script|input|output|tags|created)\s*:` over `skills/**/*.md`, `agents/**/*.md`) returns only `report-in-markdown/references/baseline-io.md` (report-artifact frontmatter `tags`, not task frontmatter).
- Task-field prose sweep (backtick-wrapped field names) returns only out-of-domain hits: Quarto `output` kwarg in `julia-quarto-guide.md`, report `tags` in `baseline-io.md`, Zotero `tags` API in `zotero-paper-reader/SKILL.md`.
- `python3 skills/task-tree/scripts/cli.py task check` — clean (0 errors; the single placement warning is a pre-existing, unrelated `main-agent-trimming` root-placement advisory).

## Review Notes

1. **MAJOR** — [internals.md:189](../../../../skills/task-tree/references/internals.md#L189) still instructs an agent preparing a legacy PLAN.md for migration to "Add missing metadata fields with safe defaults: `**Depends on:** *(none)*`, `**Script:** *(none)*`." This tells the agent to write a `**Script:**` field the migrator no longer consumes — `FIELD_RE` in [plan_migrate.py:25-29](../../../../skills/task-tree/scripts/plan_migrate.py#L25-L29) extracts only `depends_on`, `review_status`, `integration_status`, so `**Script:** *(none)*` is dead instruction prose. This is the same file and the same migration path where you correctly dropped the `script`/`input`/`output` rows from the `FIELD_RE` table (lines 151-156), but the companion normalization-checklist line was missed. It is precisely the gap the objective targets ("no instruction tells an agent to write or maintain a field the code no longer carries"). The field-form sweep missed it because the field appears mid-line inside a backtick span (`**Script:**`, capital S), not line-anchored. Fix: drop `, **Script:** *(none)*` so the line reads "Add missing metadata fields with safe defaults: `**Depends on:** *(none)*`." Then re-confirm no remaining `**Script:**`/`**Input:**`/`**Output:**` task-field prose survives anywhere in the active docs.
