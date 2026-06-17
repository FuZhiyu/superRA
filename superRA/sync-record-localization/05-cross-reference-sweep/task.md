---
title: "Repo-Wide Stale-Token Sweep Across Remaining Surfaces"
status: not-started
depends_on:
  - 01-canonical-model
tags: []
created: 2026-06-17
---

## Objective

Catch every surviving reference to the old sync-record model outside the files owned by `01`–`04`. Grep `skills/` (excluding `skills/task-tree/scripts/`, owned by `04`), `CLAUDE.md`, and `skills/CATEGORIES.md` for the stale token set and reconcile each live hit to the localized model:

- `Sync Map` — remove; branch narrative is the git log, localized context is `## Sync Impact`.
- `SEMANTIC_MERGE` — remove; standalone records live in the commit body.
- `**Integration status:**` / `Integration status` (inline-field sense) — integration review uses the `status:` frontmatter field.
- `task block(s)` — tasks are `task.md` files, referenced by path.
- "handoff doc/artifact/record" framing that collides with the deprecated handoff-doc skill.

Known live hits to fix (verify and reconcile, plus anything else the grep surfaces):
- `skills/using-superRA/references/main-agent.md` — the Frontier Resolver line "Top task.md: `## Sync Map` when present …" → reference task-local `## Sync Impact`, drop Sync Map.
- `skills/CATEGORIES.md` — the `semantic-merge` row mentions recording "branch-level / task-local / file-local context" → trim to the localized record (task-local `## Sync Impact` + commit body / git log).

### Constraints

- **Exclude** the files owned by sibling tasks: `semantic-merge/*` (`01`, `02`), `superintegrate/SKILL.md` and `refactor-and-integrate/SKILL.md` (`03`), `task-tree/scripts/*` (`04`), and `task-tree/references/task-file-contract.md` and the `CLAUDE.md` ownership row (`01`). Touch only the remaining surfaces so the parallel tasks stay file-disjoint.
- **Do not touch** `docs/plans/*` or `docs/process-issues-*` — historical records of the old design.

## Planner Guidance

This is the downstream cleanup; expect a small number of edits. If the grep surfaces a hit inside a file another sibling task owns, leave it (that task covers it) and note it in `## Results` so nothing is assumed-covered that wasn't.
