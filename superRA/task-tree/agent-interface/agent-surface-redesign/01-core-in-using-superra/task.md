---
title: "Author Task Interface Section in using-superRA"
status: approved
depends_on: []
tags: []
created: 2026-06-01
---

## Objective

Add a single authoritative **Task Interface** section to `skills/using-superRA/SKILL.md` that carries everything an executing agent (implementer, reviewer, direct-mode main agent) needs to read and edit its assigned `task.md` — and nothing more. This section becomes the one source of truth that the slimmed `task-tree/SKILL.md` (task 02) and the slimmed role specs (task 03) point to. This is the foundational task; do it first and get the boundary exactly right, because everything else points here.

**Where it goes.** Replace/absorb the current thin `## Handoff Docs` pointer paragraph in `skills/using-superRA/SKILL.md` (around line 41). That paragraph currently only points at `agents/*.md §Editing Etiquette` and `task-tree/references/planning.md`; it becomes the new self-contained interface section (keep a pointer to planning.md for *depth*, but carry the operational essentials inline).

**What the section MUST carry (the universal core):**
- A task is a `task.md` file: YAML frontmatter + free-form `##` body sections. (Do NOT carry the "everything is a task / filesystem = hierarchy" *mental model* here — that is tree-reasoning concept material owned by `task-tree/SKILL.md §Core Concepts`, and it does not describe the orchestrator/planner who work across many tasks. The core only needs the shape of the file an agent reads and edits.)
- **Read your task** via `python3 <task-tree-skill-dir>/scripts/task_read.py --path <path>` — **always use it**: it injects the ancestor-chain context and sibling dependency status that a bare `task.md` lacks. A `task.md` is **not** self-contained (it depends on its ancestors' objectives and the root conventions), so do not present "just Read the file" as an equivalent. To go deeper than the injected excerpt, read the ancestor `task.md` files up to the root.
- **Edit your task** by editing `task.md` directly with Read/Edit. State why this is the *safe* path: the PostToolUse hook validates frontmatter (enum values, dependency refs, cycles), propagates parent status, and rebuilds the dashboard after each edit — so direct edit is canonical, not a shortcut around tooling.
- The **status enum** (`not-started | in-progress | implemented | revise | approved | archived`) and the **body-section vocabulary** (`## Objective`, `## Results`, `## Revision Notes`, `## Review Notes`) — as a compact list, not a re-derivation of planning.md's field-by-field table.
- The **shared editing principles**: the task reflects latest state, not a log (no "Update:"/"Revised:"/strikethrough — git owns history); inline-edit and remove-superseded-content in place; cite source files as markdown links (per `report-in-markdown` §File-reference rule); doc-before-report (material findings land in the task body before the status return).
- The **ownership-boundary principle, stated generically** (NOT as a single role's rule — the core is also loaded by the orchestrator and planner, who legitimately edit multiple tasks, parent rollups, and scope frontmatter): edit only the body sections and frontmatter fields your current role owns; never rewrite another role's content in place — raise it instead of overwriting it. Point to the role specs (and `planning.md` for planner-owned fields like `## Objective` / scope frontmatter) for the concrete per-role ownership split; do not assert "one task per agent" or enumerate the implementer/reviewer split here.

**What the section MUST NOT carry (keep the core thin; these stay where they are):**
- Tree-management tooling — frontier, DAG, `--tree`, `task_create`/`task_update`/`task_link`/`task_rename`, dashboard, migration. These stay in `task-tree/SKILL.md` (task 02).
- Field-by-field anatomy depth, results-shape templates, stale-content checklist, objective-writing, splitting, placement. These stay in `task-tree/references/planning.md` — point to it for depth, do not paraphrase it.
- The concrete **role split** (who owns `## Results` vs `## Review Notes`), the **annotation mechanics** (`→ implemented:` / `→ orchestrator:` / item-deletion authority), and the verdict protocol. Per the researcher's decision, the core states only the ownership *boundary principle*; the role-specific split and annotation mechanics stay in `agents/implementer.md` / `agents/reviewer.md` (task 03).

**Discipline.** Apply the `CLAUDE.md` "Teach the Protocol" DRY/Necessity gate to every line: if planning.md or a role spec already carries it, point — do not restate. The section is a behavior-shaping summary + pointers, not a second copy of the anatomy. Load `skill-creator` before editing.

**Validation (must be true to be complete):**
- A reader who loads only `using-superRA/SKILL.md` can, from this section alone, correctly read their task, edit it inline, set their status, and stay within ownership bounds — without loading `task-tree`.
- No line duplicates content that `planning.md` or the role specs own; pointers are used instead.
- The old `## Handoff Docs` pointer paragraph is gone (absorbed), with no dangling references to it elsewhere in `using-superRA`.
- **No knowledge lost:** any interface guidance you remove from its old location must already be present in this new section (or another reachable owner). You are only de-duplicating and relocating, never dropping the last copy — task `09-coverage-audit` will check this against a git snapshot.

**Output:** `skills/using-superRA/SKILL.md`.

## Results

Replaced the thin `## Handoff Docs` pointer paragraph in [SKILL.md](../../../../../skills/using-superRA/SKILL.md) (was line 41) with a self-contained `## Task Interface` section. The section is the single source of truth the slimmed `task-tree/SKILL.md` (task 02) and role specs (task 03) will point to.

**What the new section carries (universal core, inline):**
- Task = `task.md` (frontmatter + `##` body sections), with the mental-model framing deliberately omitted (owned by `task-tree §Core Concepts`).
- **Read** via `python3 <task-tree-skill-dir>/scripts/task_read.py --path <path>`, mandated because a bare `task.md` is not self-contained (objective inherits ancestor objectives + root `## Conventions`; script injects ancestor chain + sibling dependency status).
- **Edit** directly with Read/Edit, with the PostToolUse-hook rationale (validates frontmatter, propagates parent status, rebuilds dashboard) explaining why direct edit is canonical.
- **Status enum** and **body-section vocabulary** as compact lists.
- **Editing principles**: latest-state-not-a-log / inline-edit, remove-superseded-content, markdown-link citations, doc-before-report.
- **Ownership boundary** stated generically (edit only what your role owns; raise rather than overwrite), pointing to the role specs for the per-role split + annotation mechanics and to `planning.md` for planner-owned fields.

**Deliberately not carried** (kept where they live, pointed to): tree tooling (frontier/DAG/dashboard/mutation commands → `task-tree/SKILL.md`); anatomy depth, results templates, stale-content checklist, objective-writing → `planning.md`; concrete role split + `→ implemented:`/`→ orchestrator:` annotation mechanics + verdict protocol → role specs.

**Second edit:** updated the §Skill-Load Manifest paragraph that previously said "subagents get editing etiquette from `agents/implementer.md` / `agents/reviewer.md`" — it now points to §Task Interface as the shared read/edit interface, with role specs owning only the per-role split. This avoids a stale pointer now that the shared interface lives in this skill.

**Verification:**
- `grep -rn "Handoff Docs" skills/ agents/` → no matches; old section fully absorbed, no dangling reference.
- Remaining `§Handoff` references in `agents/*.md`, `references/direct-mode-*.md`, and `sync_codex_agents.py` all point to the role specs' own intra-file `## Handoff` section (not the removed `## Handoff Docs`); slimming those is task 03's scope, not this task's.
- DRY/Necessity gate self-applied line by line: every retained line is behavior-shaping (mandated read path + rationale, edit rationale, the one inline copy of the editing principles, generic ownership boundary); no line restates `planning.md` anatomy or role-spec annotation mechanics — those are pointers only.

**Validation criteria met:** a reader with only `using-superRA/SKILL.md` can read (via `task_read`), edit inline, set status (enum present), and stay in ownership bounds; no duplicated owned content; old paragraph absorbed with no dangling references; no last-copy knowledge dropped.
