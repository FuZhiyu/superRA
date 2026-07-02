---
title: "The Task File"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

A `task.md` is the unit you read and edit. Each task is a directory holding one. You touch three places by hand; the rest is structure the tooling and agents maintain.

In the frontmatter, the two keys you set are `title` (the name shown in the tree and dashboard) and `status` (where the task sits in the cycle — you set it when you park or resume work, and the tooling rolls a parent's status up from its children; see [Status and the frontier](#/04-utility-skills/01-task-tree/03-status-and-frontier)). `depends_on` lists sibling directory names this task waits for; keeping dependencies sibling-only is what lets a parent's status be computed rather than hand-kept. The create command fills the rest.

Below the frontmatter, each `## ` section is owned by one role so two agents never fight over the same prose: you write `## Objective` (the goal, plus optional `### Context`/`### Conventions`/`### Constraints` the subtree inherits); the implementer writes `## Results` (findings and the evidence verifying them); the reviewer's `## Review Notes` appears only while findings are open.

A scoped leaf looks like this:

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

The full field-by-field contract — every key, each section's ownership and shape, context-inheritance rules, and the stale-content checklist — lives in [skills/task-tree/references/task-file-contract.md](skills/task-tree/references/task-file-contract.md).
