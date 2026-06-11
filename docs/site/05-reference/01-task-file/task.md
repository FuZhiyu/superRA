---
title: "Task File Reference"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

Every piece of work in superRA lives in a `task.md` file.
This page is a human-friendly orientation to its structure; the authoritative field-by-field contract lives in [skills/task-tree/references/task-file-contract.md](skills/task-tree/references/task-file-contract.md).

## Frontmatter fields

Each `task.md` opens with a YAML frontmatter block.
The field set is **closed** — only these keys are recognized; anything else is silently discarded on the next CLI write.

| Field | What it holds |
|---|---|
| `title` | Human-readable name shown in the dashboard and tree views. |
| `status` | Task-local validity marker. See [Status and Frontier](#/05-reference/03-status-and-frontier) for the full enum and lifecycle. |
| `depends_on` | List of sibling directory names this task must wait for. Dependencies are sibling-only; parent status rolls up from children automatically. |
| `tags` | Free-form labels for filtering. |
| `script` | The script that implements this task (leaf tasks only). |
| `input` | Input file paths (leaf tasks only). |
| `output` | Output file paths (leaf tasks only). |
| `created` | ISO date when the task was created. |

Branch tasks (those with children) do not carry `script`, `input`, or `output`.

## Body sections

After frontmatter, a task carries named `## ` sections.
The same structure applies at every level — root, branch, and leaf.

| Section | Who owns it | What goes in it |
|---|---|---|
| `## Objective` | Planner | The task's goal; scoped `### Context`, `### Conventions`, and `### Constraints` subsections that its subtree inherits. Implementers read but do not rewrite this section. |
| `## Planner Guidance` | Planner | Optional advisory suggestions. Not binding — implementers may deviate when another route satisfies the objective. |
| `## Results` | Implementer | Findings, verification evidence, caveats, and material deviations from planner guidance. Updated in place; no append-log style. |
| `## Review Notes` | Reviewer | Active review items. Present only when there are open items; removed entirely on approval. |
| `## Revision Notes` | Planner | Temporary delta signal when a task is updated mid-flight. Reviewer removes it at approval. |
| `## Workflow Status` | Orchestrator | Integration-phase progress checkboxes on the root task only, during INTEGRATE. Removed after Finish. |

For the complete field-by-field ownership rules, results shape, context-inheritance mechanics, and stale-content checklist, see [skills/task-tree/references/task-file-contract.md](skills/task-tree/references/task-file-contract.md).

## Example

A minimal leaf task:

```
---
title: "Filter Sample"
status: not-started
depends_on:
  - 01-load-raw-data
script: Code/02_filter.py
input: [Data/raw.parquet]
output: [Data/filtered.parquet]
created: 2026-06-01
---

## Objective

Drop observations before 2000 and require non-missing returns.

## Results

### Key Findings
- Retained 3.8 M of 4.7 M rows after applying filters.
```
