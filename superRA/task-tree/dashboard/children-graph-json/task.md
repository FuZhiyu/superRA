---
title: "Children Panel Consumes JSON, Not Regex-Parsed Mermaid Text"
status: not-started
depends_on: []
---

## Objective

The children dependency panel is driven by a structured JSON payload instead of regex-parsing never-rendered mermaid diagram source, and the status→color mapping lives in exactly one place.

- A JSON endpoint (new `/api/children-graph?root=<path>`, or `/dag` returning JSON) provides nodes (`path`, `slug`, `title`, `status`) and dependency edges; the client builds the panel from it.
- The `DAG_FILL_STATUS` color-inversion map and the mermaid-source regex parsing are deleted from the client.
- The standalone export embeds the JSON payloads through the existing fetch-shim fragment map, same as other per-task fragments.
- The global DAG view's behavior is unchanged — investigate whether it shares the text-parsing path and scope it in only if it does.
- Validation: the children panel renders identically (statuses, colors, edges, ordering) live and in a standalone export; a task title containing a standalone ` --> ` line no longer corrupts the panel; both suites green.

## Planner Guidance

Findings (2026-07-19 review): `dag.html:16-17` states the `.mermaid` div "is no longer rendered — it is the line-based source the parser reads"; the client recovers status by regexing `style <id> fill:#…` and inverting the hard-coded `DAG_FILL_STATUS` map at [base.html:3209-3248](../../../../skills/task-tree/scripts/templates/base.html#L3209-L3248), which must stay byte-synced with `status_colors` in [dag.html:22-30](../../../../skills/task-tree/scripts/templates/dag.html#L22-L30); edges come from a `/^\s*(\S+)\s*-->\s*(\S+)\s*$/gm` scan. The JSON precedent already exists in the same template: the `data-node-paths` attribute on `.dag-controls` carries JSON.

Server-side, the sibling-graph data is trivially available from `Task.children` + `depends_on` (see the `/dag` route at plan_dashboard.py:1111-1132). Standalone embedding pattern: `_build_standalone_fragments` at plan_dashboard.py:1481-1530.
