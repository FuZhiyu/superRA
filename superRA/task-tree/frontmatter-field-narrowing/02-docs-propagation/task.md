---
title: "Propagate the Narrowed Field Set Across Instruction Prose"
status: not-started
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
