# Task System Redesign — Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. Use `superRA:skill-creator` when editing any `skills/*/SKILL.md`.

**Objective:** Redesign the task-system skill to eliminate the task/step distinction (everything is a task), add structured planner/implementer ownership via `## Objective` (planner-owned) and `## Results` (implementer-owned, recursive at every tree level), auto-rebuild the dashboard after CLI mutations, and rewrite the dashboard UI as a single-page recursive expand/collapse interface using the `frontend-design` skill.

**Methodology:** Modify the existing `skills/task-system/scripts/` codebase in place. Phase 1 changes the data model and task file format. Phase 2 adds auto-rebuild hooks to all mutation scripts. Phase 3 rewrites the dashboard HTML. Phase 4 migrates the existing `.plan/` tree to the new format. Phase 5 updates tests. The existing test suite (`test_task_system.py`) provides regression coverage throughout.

**Conventions:**
- Scripts follow existing `skills/*/scripts/` patterns: stdlib-only Python, argparse CLI, `from __future__ import annotations`, type-annotated functions
- Task file body sections: `## Objective` (planner-owned), `## Results` (implementer-owned), `## Decisions`, `## Review Notes`
- No more `## Steps` or checkbox procedures — leaf tasks are directories without subdirectories
- Auto-rebuild is best-effort (try/except, never blocks the primary mutation)
- Dashboard uses Google Fonts CDN for typography, Mermaid.js CDN for DAG, markdown-it CDN for rendering

**Output:**
- `skills/task-system/scripts/_task_io.py` — updated with `parse_body_sections()`, `objective`/`results` fields on `Task`
- `skills/task-system/scripts/task_create.py` — updated template (`## Objective` / `## Results`), `--objective` arg, auto-rebuild
- `skills/task-system/scripts/task_update.py` — auto-rebuild hook
- `skills/task-system/scripts/task_add_result.py` — auto-rebuild hook
- `skills/task-system/scripts/task_link.py` — auto-rebuild hook
- `skills/task-system/scripts/task_rename.py` — auto-rebuild hook
- `skills/task-system/scripts/task_query.py` — `tree_to_json()` includes `objective`, `results`, `decisions`, `review_notes`
- `skills/task-system/scripts/plan_dashboard.py` — complete HTML rewrite (single-page, recursive expand/collapse)
- `skills/task-system/scripts/plan_migrate.py` — `--upgrade` flag for v1-to-v2 format migration
- `skills/task-system/scripts/test_task_system.py` — updated fixtures, new test classes
- `skills/task-system/SKILL.md` — rewritten core concepts, updated format example

**Pipeline:** `~/.venv/bin/python -m pytest skills/task-system/scripts/test_task_system.py -v`

---

## Workflow Status

- [ ] **Plan approved**
- [ ] **Execution complete**
- [ ] **Drift tests created**
- [ ] **Integrated**
- [ ] **Docs finalized**
- [ ] **Finished**

---

## Project Conventions

Walked at planning time (2026-05-23). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at dd7ad7d): superRA contributor guidelines. Flat skill layout, lean agents + rich references, skill authoring guidelines, ownership table, DRY + Necessity tests for every instruction line.
- `/README.md` (HEAD at dd7ad7d): User-facing product model. Skill categories table (domain, workflow, utility, meta). Install via `agents/.agents/plugins/marketplace.json`.

### Module-level docs walked
- `skills/CATEGORIES.md` (HEAD at dd7ad7d): Skill category tables mirroring README, with one-line descriptions per skill. `task-system` listed under Utility with "DAG rendering" in description.
- `skills/task-system/SKILL.md` (HEAD at dd7ad7d): Current skill definition with task/step distinction, `## Steps` format, command surface. This file will be rewritten.
- `skills/using-superRA/SKILL.md` (HEAD at dd7ad7d): Skill inventory includes `task-system` row.

### Not walked (not reachable from the planned diff)
- `skills/handoff-doc/`, workflow skills, agent specs — not modified by this work.

---

### Task 1: Data Model — Body Section Parsing
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:**

**Script:** `skills/task-system/scripts/_task_io.py`

- [ ] **Step 1: Add `parse_body_sections()` helper**

Add a function that splits a task body on `## ` headers into `{section_name: content}` pairs. Content includes everything after the header line up to the next `## ` or end of string. Returns `dict[str, str]`.

```python
def parse_body_sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_name: str | None = None
    current_lines: list[str] = []
    for line in body.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m:
            if current_name is not None:
                sections[current_name] = "\n".join(current_lines)
            current_name = m.group(1)
            current_lines = []
        elif current_name is not None:
            current_lines.append(line)
    if current_name is not None:
        sections[current_name] = "\n".join(current_lines)
    return sections
```

- [ ] **Step 2: Add `objective` and `results` fields to `Task` dataclass**

Add two new `str` fields after `body`:

```python
@dataclass
class Task:
    # ... existing fields ...
    body: str = ""
    objective: str = ""
    results: str = ""
    children: list[Task] = field(default_factory=list)
```

- [ ] **Step 3: Update `parse_task()` to populate new fields**

After parsing body, call `parse_body_sections(body)` and populate:

```python
    sections = parse_body_sections(body)
    # in the Task constructor:
    objective=sections.get("Objective", ""),
    results=sections.get("Results", ""),
```

---

### Task 2: CLI Format Changes
**Depends on:** Task 1
**Review status:**
**Integration status:**

**Script:** `skills/task-system/scripts/task_create.py`, `skills/task-system/scripts/task_query.py`

- [ ] **Step 1: Update `TASK_TEMPLATE` in `task_create.py`**

Replace the current template. Drop the `# {title}` heading (redundant with frontmatter). Replace `{description}` with `## Objective` / `## Results` sections:

```python
TASK_TEMPLATE = """\
---
title: "{title}"
status: not-started
review_status: ~
integration_status: ~
depends_on: {depends_on}
tags: []
{script_line}{input_line}{output_line}created: {today}
updated: {today}
---

## Objective

{objective}

## Results

"""
```

- [ ] **Step 2: Rename `--description` arg to `--objective`**

In `parse_args()`: rename `--description` to `--objective`.
In `create_task()`: rename `description` parameter to `objective`.
In `main()`: pass `args.objective` instead of `args.description`.
In `TASK_TEMPLATE`: `{objective}` instead of `{description}`.

- [ ] **Step 3: Update `tree_to_json()` in `task_query.py`**

Add parsed body sections to the JSON output so the dashboard can render them individually:

```python
def tree_to_json(task: Task) -> dict:
    sections = parse_body_sections(task.body)
    return {
        # ... existing fields ...,
        "objective": sections.get("Objective", ""),
        "results": sections.get("Results", ""),
        "decisions": sections.get("Decisions", ""),
        "review_notes": sections.get("Review Notes", ""),
        "body": task.body,
        "children": [tree_to_json(c) for c in task.children],
    }
```

Import `parse_body_sections` from `_task_io`.

---

### Task 3: Auto-Rebuild Dashboard
**Depends on:** Task 1
**Review status:** APPROVED
**Integration status:**

**Script:** `skills/task-system/scripts/task_create.py`, `skills/task-system/scripts/task_update.py`, `skills/task-system/scripts/task_add_result.py`, `skills/task-system/scripts/task_link.py`, `skills/task-system/scripts/task_rename.py`

- [ ] **Step 1: Add auto-rebuild to all five mutation scripts**

At the end of each mutation function, after the primary write succeeds, add:

```python
try:
    from plan_dashboard import generate_dashboard
    generate_dashboard(plan_root)
except Exception:
    pass
```

Insertion points:
- `task_create.py`: after line 103 (`print(f"Created {task_md}")`)
- `task_update.py`: inside the `if changed:` block, after line 83 (`print(f"Updated {task_md}")`)
- `task_add_result.py`: after line 98 (`print(f"Updated results in {task_md}")`)
- `task_link.py`: after line 67 (`print(f"Removed dependency...")`) and after line 91 (`print(f"Added dependency...")`)
- `task_rename.py`: after the sibling update loop ends (line 63)

---

### Task 4: Dashboard Rewrite
**Depends on:** Task 1, Task 2
**Review status:** APPROVED
**Integration status:**

**Script:** `skills/task-system/scripts/plan_dashboard.py`

- [ ] **Step 1: Design dashboard architecture**

Single-page recursive expand/collapse. No sidebar/detail split. All tasks visible on one scrollable page with progressive disclosure:
- **Level 0 (always visible)**: Task title/slug + status badge + progress count (branch tasks)
- **Level 1 (expand task)**: Shows children (branch) and section toggles (Objective, Results, etc.)
- **Level 2 (expand section)**: Rendered markdown content

Each task node and each section within a node is independently expandable.

- [ ] **Step 2: Implement recursive `renderTaskNode()` JS function**

```javascript
function renderTaskNode(task, depth) {
  // Create container with data-depth for CSS indentation
  // Header row: toggle-icon, title, status-badge, progress
  // Collapsible body:
  //   - If has children: recursively render each child
  //   - Expandable <details> for Objective, Results, Decisions, Review Notes, Metadata
  // Click header to toggle body visibility
}
```

- [ ] **Step 3: Write complete HTML/CSS/JS template**

Use `frontend-design` skill for visual design. Requirements:
- Distinctive font pair via Google Fonts CDN (not system fonts)
- Muted professional palette with subtle status tint backgrounds
- Tree connector lines (left-border) that trace hierarchy
- Smooth expand/collapse transitions
- Dense information display (work dashboard, not marketing)
- Summary progress bar in header
- Dark/light mode via CSS custom properties
- Status filter dropdown
- Search box (filters by title/path)
- View toggle: Tree (default), DAG, Kanban

- [ ] **Step 4: Replace `DASHBOARD_HTML` constant**

Replace the entire `DASHBOARD_HTML` string in `plan_dashboard.py` with the new template. Keep the `__TASK_DATA_JSON__` placeholder pattern. Keep the `generate_dashboard()` function signature unchanged.

---

### Task 5: V1-to-V2 Migration
**Depends on:** Task 1
**Review status:**
**Integration status:**

**Script:** `skills/task-system/scripts/plan_migrate.py`

- [ ] **Step 1: Update `_build_task_md()` for new format**

Change the body template to emit `## Objective` instead of `## Steps`. Strip checkbox syntax (`- [ ] `, `- [x] `) from migrated step text and place it as prose under `## Objective`.

- [ ] **Step 2: Add `--upgrade` flag for in-place v1-to-v2 migration**

Add a new code path that walks an existing `.plan/` tree and for each `task.md`:
1. Parse frontmatter and body
2. If body contains `## Steps`: rename to `## Objective`, strip checkbox prefixes
3. If body starts with `# ` title heading: remove it (redundant with frontmatter `title`)
4. Write back
5. Idempotent — no-op on files already in v2 format

```bash
python3 plan_migrate.py --upgrade --plan-root .plan
```

- [ ] **Step 3: Run migration on project's `.plan/` directory**

Execute `--upgrade` on the existing `.plan/` tree. Verify all 7 `task.md` files have `## Objective` not `## Steps`, and no `# Title` headings.

---

### Task 6: SKILL.md + Inventory Updates
**Depends on:** Task 1, Task 2, Task 4
**Review status:** APPROVED
**Integration status:**

- [ ] **Step 1: Rewrite `SKILL.md` core concepts**

Remove "Tasks are objectives. Steps are procedures." Replace with:
- Everything is a task. Leaf tasks have no subdirectories.
- `## Objective` is planner-owned: goal, methodology, conventions.
- `## Results` is implementer-owned: findings, notes. Present at every level (recursive).
- Filesystem is the single source of truth for hierarchy.
- Numeric prefix on directory names controls display order. DAG (`depends_on`) controls execution order.

- [ ] **Step 2: Update task file format example**

Replace `## Steps` with `## Objective` in the format template. Remove checkbox examples. Show the new format with `## Objective` and `## Results`.

- [ ] **Step 3: Document auto-rebuild**

Add note: "The dashboard is automatically regenerated after every mutation command (`task_create`, `task_update`, `task_add_result`, `task_link`, `task_rename`)."

---

### Task 7: Test Suite Updates
**Depends on:** Task 1, Task 2, Task 3, Task 4, Task 5
**Review status:** APPROVED
**Integration status:**

**Script:** `skills/task-system/scripts/test_task_system.py`

- [ ] **Step 1: Update all fixture `task.md` content**

Replace `## Steps\n\n- [ ] Step 1\n` with `## Objective\n\n<objective text>\n\n## Results\n` in all `_write_task_md()` calls and inline task.md content strings throughout the test file.

- [ ] **Step 2: Add `TestParseBodySections` test class**

Test `parse_body_sections()`:
- Body with all sections (Objective, Results, Decisions, Review Notes)
- Body with only Objective
- Empty body (returns empty dict)
- Body with unknown/extra sections (preserved in dict)

- [ ] **Step 3: Update existing tests for new format**

- `TestTaskCreate.test_create_basic`: verify template contains `## Objective`, `--objective` arg works
- `TestTaskQuery.test_tree_to_json`: verify JSON includes `objective`, `results` fields
- `TestPlanMigrate.test_migrate_basic`: update expected output format
- `TestDashboard.test_generate_dashboard`: update assertions for new HTML template

- [ ] **Step 4: Add `TestAutoRebuild` test class**

Verify that mutation operations trigger dashboard regeneration:
- Create a task with an existing `dashboard.html` → file is updated
- Update task status → `dashboard.html` reflects change
- Verify the embedded JSON in the dashboard contains the latest data

- [ ] **Step 5: Add `TestMigrateV2` test class**

Test the `--upgrade` migration path:
- `## Steps` with checkboxes → `## Objective` with stripped text
- `# Title` heading → removed
- Idempotent: running on v2 file produces identical output
- `## Results` section preserved unchanged
