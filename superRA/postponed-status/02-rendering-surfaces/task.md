---
title: "Render postponed in CLI and dashboard"
status: approved
depends_on: 
  - 01-core-semantics

tags: []
created: 2026-06-01
---

## Objective

Make `postponed` render everywhere a status is shown — the CLI tree/DAG output and the HTML dashboard — and keep it out of the completion-percentage denominator. Every site below hard-codes the status set (it does not import `VALID_STATUSES`), so each must be edited explicitly. Mirror the existing `archived` entry at each site. Pick one visual treatment for `postponed` and use it consistently (suggestion: a muted/slate color distinct from `archived`'s grey, and a pause-style icon such as `⏸`). All paths under `skills/task-system/scripts/`.

### CLI — `task_query.py`

1. **`STATUS_ICONS` (line ~24-31).** Add a `"postponed"` icon.
2. **Mermaid DAG (lines ~144, ~167).** Add the `postponed` → class mapping (mirroring `"archived": ":::archived"`) and a matching `classDef postponed fill:...,stroke:...,color:...` line.

### Dashboard templates — `skills/task-system/scripts/templates/`

3. **`dag.html` (status_colors map, line ~22-28).** Add `'postponed': '<hex>'`.
4. **`base.html`:**
   - CSS custom properties + `.badge-postponed` rule (mirror `.badge-archived`, line ~763-768). Add the `--st-...` color vars it references.
   - Status filter dropdown options (line ~1130-1137) — add `postponed`.
   - `nodeMatchesStatus()` filter logic (line ~1579) if it enumerates statuses explicitly.
   - DAG reverse color→status map and `DAG_FILL_STATUS` lookup (lines ~2088-2089, ~2111).
5. **`kanban.html` (status list, line ~9-14).** Add a `postponed` column.
6. **`summary_bar.html` (line ~5-14).** Exclude `postponed` from the active denominator exactly like `archived`: compute `postponed_leaves` and subtract it from `active_leaves` so completion % = `approved / (leaves − archived − postponed)`. Add a visible `postponed` count pill next to the archived count so parked work is not invisible.

### Verification — render the real artifact, do not stop at the source

Build an actual dashboard from a task tree that contains at least one `postponed` leaf, one `postponed` branch (all children postponed), and a sibling blocked by a postponed dependency, then open the produced HTML and confirm against the rendered DOM:

- the postponed badge/color renders on the node and in the legend;
- the kanban view shows the postponed column with the task in it;
- the status filter includes and correctly filters `postponed`;
- the summary bar excludes postponed from the % and shows the postponed count;
- the DAG node is filled with the postponed color.

Regenerate via the project's dashboard entry point (`plan_dashboard.py` / `superRA/serve`). Inspect the rendered output, not just the template diff — a template edit that leaves a broken legend, an empty kanban column, or a miscounted summary bar is a real bug this check exists to catch.

## Results

`postponed` now renders consistently across the CLI and the HTML dashboard, and is excluded from the completion-% denominator. Visual treatment: a muted slate distinct from `archived`'s grey — light `#dde3ea` / dark `#28323e` badge fill, mermaid/DAG fill `#cfd8e3`, CLI icon `⏸`. Every site below hard-codes the status set; each was edited explicitly, mirroring `archived`. All edits under `skills/task-system/scripts/`.

### CLI — [task_query.py](../../../../skills/task-system/scripts/task_query.py)

- **`STATUS_ICONS`:** added `"postponed": "⏸"` ([task_query.py:31](../../../../skills/task-system/scripts/task_query.py#L31)).
- **Mermaid DAG:** added `"postponed": ":::postponed"` to the status→class map ([task_query.py:145](../../../../skills/task-system/scripts/task_query.py#L145)) and a matching `classDef postponed fill:#cfd8e3,stroke:#78909c,color:#37474f` ([task_query.py:169](../../../../skills/task-system/scripts/task_query.py#L169)).

### Dashboard templates — [templates/](../../../../skills/task-system/scripts/templates/)

- **[dag.html](../../../../skills/task-system/scripts/templates/dag.html):** `'postponed': '#cfd8e3'` in the `status_colors` map ([dag.html:29](../../../../skills/task-system/scripts/templates/dag.html#L29)).
- **[base.html](../../../../skills/task-system/scripts/templates/base.html):** added `--st-post`/`--st-post-t` CSS vars in both light ([base.html:53](../../../../skills/task-system/scripts/templates/base.html#L53)) and dark ([base.html:88](../../../../skills/task-system/scripts/templates/base.html#L88)) themes; a `.badge-postponed` rule ([base.html:770](../../../../skills/task-system/scripts/templates/base.html#L770)); the `postponed` filter-dropdown option ([base.html:1140](../../../../skills/task-system/scripts/templates/base.html#L1140)); and `'#cfd8e3': 'postponed'` in the DAG reverse `DAG_FILL_STATUS` map ([base.html:2093](../../../../skills/task-system/scripts/templates/base.html#L2093)). `nodeMatchesStatus()` is status-agnostic (matches `el.dataset.status` against any value) and needed no edit. There is no separate static legend block — the per-node badges are the legend.
- **[kanban.html](../../../../skills/task-system/scripts/templates/kanban.html):** added a `('postponed', 'Postponed')` column ([kanban.html:15](../../../../skills/task-system/scripts/templates/kanban.html#L15)).
- **[summary_bar.html](../../../../skills/task-system/scripts/templates/summary_bar.html):** computes `postponed_leaves` and subtracts it from `active_leaves` alongside `archived_leaves`, so completion % = `approved / (leaves − archived − postponed)`; adds a `… postponed` count pill next to the archived count ([summary_bar.html:7](../../../../skills/task-system/scripts/templates/summary_bar.html#L7)).

### Verification — rendered the real artifact

Built a fixture tree (postponed leaf, postponed branch with all children postponed, approved leaf, and a not-started sibling depending on the postponed leaf), then:

- **CLI** (`task_query.py --tree/--frontier/--dag`): tree shows `⏸` on the postponed leaf and the all-postponed branch (rolls up to postponed); frontier correctly omits the sibling blocked by the postponed dependency; DAG emits `:::postponed` nodes and the `classDef postponed`.
- **Dashboard** (`plan_dashboard.py generate`): inspected the rendered DOM, not just the template diff —
  - postponed badge renders on all 4 postponed nodes (`badge badge-postponed`, `data-status="postponed"`);
  - Kanban shows a **Postponed** column holding the postponed leaf and both branch children (3 cards);
  - status filter includes the `postponed` option (filtering handled by the status-agnostic `nodeMatchesStatus`);
  - summary bar reads `1/2 approved` with a `3 postponed` pill — the 3 postponed leaves are excluded from the denominator (5 leaves − 3 postponed = 2 active);
  - DAG nodes are filled `#cfd8e3` and resolve back to `postponed` via `DAG_FILL_STATUS`.

### Tests — [test_dashboard.py](../../../../skills/task-system/scripts/test_dashboard.py)

- Updated the two kanban column-count tests for the new column (`test_kanban_returns_7_columns`, `test_kanban_has_7_status_columns`): 6 → 7.
- Added a `postponed_plan_root` fixture and 3 tests: postponed excluded from the summary denominator + count-pill visible; the Postponed kanban column holds the postponed leaves; a postponed node renders the `badge-postponed`/`data-status="postponed"`.
- `uv run pytest skills/task-system/scripts/test_dashboard.py skills/task-system/scripts/test_task_system.py -q` → **295 passed** (292 prior + 3 new).
