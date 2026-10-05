---
title: "The Task File"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

Each task is a directory holding one `task.md`: three frontmatter fields, then body sections each written by one role. You read it to see a task's goal and outcome, and edit it to steer.

```
---
title: "Filter Sample"
status: not-started
depends_on:
  - 01-sample-design
---

## Objective

Drop observations before 2000 and require non-missing returns.

## Results

### Key Findings
- Retained 3.8 M of 4.7 M rows after applying filters.
```

## Frontmatter: three fields, no others

| Field | Holds |
|---|---|
| `title` | The name shown in the tree and dashboard. |
| `status` | Where the task sits in its lifecycle; a parent's is rolled up from its children. See [Status and the frontier](#/04-utility-skills/01-task-tree/03-status-and-frontier). |
| `depends_on` | Sibling directory names that must finish before this task is ready. |

Any other key is dropped the next time the tooling rewrites the file; put custom metadata in a body section.

## Body sections: one owner each

| Section | Written by | Holds |
|---|---|---|
| `## Objective` | Planner; you review and can edit | The goal, plus optional `### Context`, `### Conventions`, `### Constraints` that every descendant task inherits. Binding. |
| `## Details` | Planner, optional | Leads worth passing on: candidate files, data quirks, a suggested route. Informative, never binding. |
| `## Reproduction` | Implementer | The [reproduction steps](#/04-utility-skills/09-reproducibility) the task owns. |
| `## Results` | Implementer | Findings and the evidence behind them. |
| `## Review Notes` | Reviewer | Open findings; present only while any remain. |

Every field and section rule is in the [task-file contract](skills/task-tree/references/task-file-contract.md).
