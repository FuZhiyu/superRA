---
title: "Repo-Wide Stale-Token Sweep Across Remaining Surfaces"
status: approved
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

## Results

### Key Findings
Ran the task-defined grep (`Sync Map`, `SEMANTIC_MERGE`, `Integration status`, `task block`, `handoff doc/artifact/record`) over `skills/` (excluding `task-tree/scripts/`), `CLAUDE.md`, and `skills/CATEGORIES.md`. Fixed the three in-scope sync-record hits; left the rest with explicit rationale (below). Both named known hits reconciled.

**Reconciled (in scope):**
- `skills/using-superRA/references/main-agent.md` — Frontier Resolver: dropped "Top task.md: `## Sync Map` when present" and added "any temporary `## Sync Impact` sections during integration" to the per-task-body read line (the localized sync record is per-task, not top-task).
- `skills/CATEGORIES.md` — semantic-merge row: "records branch-level / task-local / file-local context" → "records the approved post-sync diff in the git log (commit messages) plus a temporary task-local `## Sync Impact` section on each affected task".
- `skills/using-superRA/SKILL.md` — "executes task blocks" → "executes tasks" (the one live `task block(s)` token in scope).

**Left intentionally (with rationale):**
- `skills/semantic-merge/references/workflow-sync-author.md:40` — **excluded** (`semantic-merge/*` owned by `01`/`02`); the single "Sync Map" mention is an intentional negation ("does not reference a branch-level Sync Map (there is none)") retiring the concept, per `01`'s own Results.
- `skills/task-tree/references/internals.md:127,158` — describe the **legacy `PLAN.md` migration parser**: "task blocks" is the literal name of the `### Task N:` heading construct the migrator parses, and `**Integration status:**` is documented as a "Legacy source field" the migrator reads and maps. Rewriting these would make the migration doc describe a format the parser does not consume. Out of scope.
- `skills/theory-modeling/SKILL.md:165` — "acceptable handoff artifact" is generic English for an auditable derivation, unrelated to sync records or the deprecated handoff-doc skill.
- `skills/writing/*` (SKILL.md, planning.md, draft.md, polish.md, long-form-review.md) + `CLAUDE.md:54` — "handoff doc" framing for writing's `## Project Conventions` storage home (and CLAUDE.md's generic DRY enumeration of where info can live), plus "durable task blocks" in `planning.md`. These collide with the deprecated handoff-doc skill, but reconciling them is a **separate live concern** — where writing-side conventions live now that handoff-doc is deprecated — that is a writing-skill decision outside sync-record localization. Pulling it into this workstream would be scope creep against the "small number of edits" guidance. Flagged for a dedicated handoff-doc-deprecation cleanup.

### Notes
- Out of this task's grep paths but worth surfacing: the repo root carries a real leftover `SEMANTIC_MERGE.md` artifact file (a `merge --no-ff` record on `better-handoff`) — the exact dead-artifact class this workstream eliminates, but outside both task 05's grep scope (`skills/`, `CLAUDE.md`, `CATEGORIES.md`) and task 02's three-file scope. Left for an orchestrator scope decision.
