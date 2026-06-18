---
title: "Redesign task-tree SKILL.md for Progressive Revelation"
status: approved
depends_on:
  - 01-core-in-using-superra
tags: []
created: 2026-06-01
---

## Objective

Redesign `skills/task-tree/SKILL.md` so the main body is a **lean router** that progressively reveals detail through references. The universal read/edit interface now lives in `using-superra/SKILL.md §Task Interface` (task 01), so this skill is loaded **on demand** only — by whoever needs to operate on the *tree* (not by every executing agent). Depends on task 01.

**Step 1 — Persona/situation analysis (do this first; record it in `## Results`).** Work out who loads `task-tree` after the relocation, in what situation, and therefore what they need *immediately in the body* vs. what can live in a reference. Expected personas (verify and refine):
- **Orchestrator, mid-workflow** — the most frequent on-demand reason: inspect tree state (`task_query.py --tree` / `--frontier` / `--dag`), bulk status propagation, parent-results rollup, moving/reorganizing tasks. Needs the mental model and the read/query surface fast.
- **Planner (superplan)** — create and structure tasks (`task_create`/`task_link`/`task_rename`); objective-writing/splitting/placement already owned by `references/planning.md`.
- **Contributor** — data layer / hooks / migration internals → `references/internals.md`.
- **One-time migration** — `plan_migrate.py` / v1→v2 upgrade.
- **Human** — `bash .plan/serve` for the dashboard.

The body should serve the common case inline and route the situational cases to references.

**Step 2 — Restructure the body to a lean router:**
- **`## Core Concepts`** (keep, in body): the mental model needed to reason about the tree — everything is a task, filesystem hierarchy = task hierarchy, sibling-only dependencies, parent status rollup, DAG-derived ordering vs. numeric display prefixes. This is what task 01 deliberately *excluded* from the universal core; it lands here.
- **Reading the tree** (keep, in body — the common on-demand path): the query surface (`task_query.py --tree/--frontier/--dag`) and a one-line pointer that single-task reading + the editing interface live in `using-superra §Task Interface`.
- **A routing table** ("to do X, see Y") for the situational paths, each pointing to a reference, with at most a one-line invocation in the body:
  - Creating / restructuring / linking / renaming / moving tasks, bulk status ops → a references file (see Step 3).
  - Migration (`plan_migrate.py`) and v1→v2 upgrade → `references/internals.md §Migration`.
  - Dashboard → `bash .plan/serve` one-liner; mechanics in `references/internals.md`.
  - Modifying the skill itself (data layer, hooks) → `references/internals.md`.

**Step 3 — Move the command-surface detail into references, single owner per command.** The current `SKILL.md §Command Surface` duplicates `references/planning.md §Hierarchy Management Commands` (create/rename/link). Resolve the duplication by giving each command exactly one authoritative home and pointing from the body. Choose the cleanest layout and justify it in `## Results`: either extend `references/planning.md` to host the full mutation surface, or add a dedicated `references/commands.md` (the user explicitly endorsed using reference files for detail). Migration/upgrade detail consolidates into `references/internals.md` (which already documents the migrator). After this task, no command invocation appears in two places.

**Step 4 — Fix the stale "self-contained" claim.** The current SKILL.md says "read `task.md` directly … the file is self-contained" while also telling readers to read ancestors for context — contradictory and wrong. Remove the self-contained framing wherever it remains in this skill; the authoritative read guidance (always use `task_read`) is in `using-superra §Task Interface`.

**Step 5 — Update the top-of-file role-scoped references pointer and frontmatter.** Rewrite the `**Role-scoped references:**` block to the new map: executing-agent interface → `using-superra §Task Interface`; tree concepts + read/query → this body; planner/orchestrator command + structure depth → `references/planning.md` (or `references/commands.md`); contributor depth → `references/internals.md`. Confirm the `description:` frontmatter describes tooling/tree triggers and no longer implies every agent must load it.

**Discipline.** Load `skill-creator` before editing. Apply the DRY/Necessity gate line-by-line — the body should *route*, not restate. Preserve standalone usability: a researcher who loads only `task-tree` should still be able to operate the tree by following the body's pointers. Keep the body short enough that the progressive-revelation goal is visibly met (concepts + common path + routing map), not a relabeled monolith.

**Validation (must be true to be complete):**
- The persona/situation analysis is recorded in `## Results` and visibly drives what stayed in the body.
- The body is a lean router: core concepts + tree-reading + a routing table; no full command surface, no migration walkthrough, no editing-mechanics duplication.
- Each task-management command and the migration/upgrade detail live in exactly one reference; the body points to them.
- No "self-contained `task.md`" claim remains in this skill; read/edit mechanics and ownership are not restated here (only pointed to `using-superra §Task Interface`).
- No dangling internal references to moved sections (grep `task-tree/SKILL.md §` mentions across `skills/` and `agents/`).
- The skill still works standalone via its pointers.
- **No knowledge lost:** every command, concept, and migration detail you remove from the body still exists in a reachable reference; nothing is dropped, only relocated and de-duplicated. Task `09-coverage-audit` verifies this against a git snapshot.

**Output:** `skills/task-tree/SKILL.md`; `skills/task-tree/references/planning.md` and/or a new `skills/task-tree/references/commands.md`; `skills/task-tree/references/internals.md` (migration/dashboard consolidation as needed).

## Results

### Step 1 — Persona/situation analysis (drives the body)

After task 01 relocated the universal read/edit interface to `using-superra §Task Interface`, no executing agent (implementer/reviewer/direct-mode main agent) needs to load `task-tree` — they read/edit their one assigned task through the preloaded `using-superra`. So `task-tree` is now loaded **only** by someone operating on the *tree*. Refined personas and what each needs:

- **Orchestrator, mid-workflow (most frequent on-demand load).** Inspects tree state — `task_query.py --tree/--frontier/--dag` — and occasionally moves/reorganizes tasks or runs bulk status ops. Needs the **mental model** (Core Concepts) and the **query surface** immediately in the body; mutation/bulk detail can be one routing hop away.
- **Planner (superplan).** Scaffolds and structures tasks (`task_create`/`task_link`/`task_rename`). Needs to know *what a task.md looks like* (Task File Format) and *where the mutation commands are*; objective-writing/splitting/placement depth already lives in `references/planning.md`.
- **Contributor.** Data layer / hooks / migration / dashboard internals → `references/internals.md`.
- **One-time migration.** `plan_migrate.py` / v1→v2 upgrade — rare, belongs in a reference, not the body.
- **Human.** `bash .plan/serve` — a one-liner is all the body owes them.

**What this dictates for the body:** keep the mental model (Core Concepts) and the common query path (Reading the Tree) inline; keep the Task File Format template inline (planner-facing and the target of an external `superplan` pointer); route every situational case (mutation surface, migration, dashboard mechanics, skill internals) to a reference via a routing table. The single-task read/edit interface is *not* restated — it is pointed to `using-superra §Task Interface` from both the header and the "Reading the Tree" section, since that is where a tree-inspecting reader is most likely to want it.

### Step 2–3 — Lean-router restructure and command relocation

[SKILL.md](../../../../../skills/task-tree/SKILL.md) went from 258 → ~103 lines. Body now = header/role-map + **Core Concepts** + **Reading the Tree** (query surface only) + **Task File Format** + **Routing table** (+ a one-paragraph `mv` note pointing to the full move caveat in commands.md).

Command surface relocated to a **new** [references/commands.md](../../../../../skills/task-tree/references/commands.md) (`task_create`, `task_update` bulk/cascade, `task_add_result`, `task_link`, `task_rename`, plain-`mv` move + caveat). Per the orchestrator's scope change, `references/planning.md` was **not** touched — the SKILL.md↔planning.md command dedup against `planning.md §Hierarchy Management Commands` is deferred to a separate worktree, so a copy of create/rename/link temporarily co-exists in planning.md by design. Within *this* task's surfaces, each command appears once (body points; commands.md owns).

Migration/dashboard detail consolidated into [references/internals.md](../../../../../skills/task-tree/references/internals.md): added the "Preparing a legacy PLAN.md" normalization checklist + manual-migration procedure under §Migration (previously only in the body), and made §Dashboard self-contained with the `.plan/serve` / `uv run` / port-derivation detail (it previously pointed back to the now-removed `SKILL.md §Dashboard` as authoritative — that circular pointer is resolved).

### Step 4 — Stale "self-contained" claim removed

The contradictory body line ("read `task.md` directly … the file is self-contained" while also telling readers to read ancestors) is gone. `grep -rn "self-contained" skills/task-tree/` now returns only unrelated matches (figures moving with a task in `planning.md`; standalone-HTML export in `plan_dashboard.py`). The authoritative read guidance (always use `task_read`, a bare `task.md` is *not* self-contained) lives in `using-superra §Task Interface` and is pointed to, not restated.

### Step 5 — Role-map and frontmatter

Rewrote the `**Role-scoped references:**` block to the new map: executing agent → `using-superra §Task Interface`; orchestrator/planner tree ops → this body + `references/commands.md`; planner depth → `references/planning.md`; contributor → `references/internals.md`. The `description:` frontmatter now frames the skill as load-on-demand tree tooling for orchestrators/planners/contributors and states explicitly that executing agents do not need it (triggers: frontier/DAG/create/dashboard/migrate).

### Verification

- `grep` for removed section names (`§Command Surface`, `§How to Read/Edit a Task`, `§Ownership Model`, `§Moving / reorganizing`, `§Preparing a PLAN`, `SKILL.md §Dashboard/§Migrate/§Upgrade`) across `skills/ agents/ README.md CLAUDE.md` → no dangling references.
- All body pointers resolve: `references/commands.md` exists; `references/internals.md §Migration` and `§Dashboard` headings exist; `using-superra/SKILL.md §Task Interface` exists (task 01, approved). Reference→SKILL.md back-pointers (`SKILL.md §Task File Format`) resolve to a section that was kept.
- `task_query.py`/`task_read.py` run cleanly in this env (used during task read). `test_task_tree.py` requires `pytest` (absent here); no script was modified, so this is doc-only and not load-bearing.
- DRY/Necessity gate applied line-by-line: dropped the redundant body `mv` prose paragraph that duplicated commands.md; the body now routes rather than restates, with single-task read/edit pointed (not copied) to `using-superra §Task Interface`.

**No knowledge lost (within this task's scope):** every command, concept, migration step, and dashboard detail removed from the body now lives in `references/commands.md` or `references/internals.md` (or was already in `planning.md`), reachable via the body's routing table. Task `09-coverage-audit` verifies this against a git snapshot.

## Review Notes

> 1. [MINOR] `## Results` defer a create/rename/link command-surface duplicate as "temporarily co-exists in planning.md by design" pending a separate dedup; `planning.md` no longer exists, so the caveat is resolved-by-deletion and now misleads readers (the 09 audit's units 20/23/24 and "planning.md whole, unchanged" lean on it). Rewrite the caveat as resolved, pointing at [commands.md](../../../../../skills/task-tree/references/commands.md) as the surviving home.
