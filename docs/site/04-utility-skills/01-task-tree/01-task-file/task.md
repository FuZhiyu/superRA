---
title: "The Task File"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

A `task.md` is the unit you read and edit. Each task is a directory holding one. You touch three places by hand; the rest is structure the tooling and agents maintain.

The frontmatter field set is closed: `title` (the name shown in the tree and dashboard), `status` (where the task sits in the cycle — you set it when you park or resume work, and the tooling rolls a parent's status up from its children; see [Status and the frontier](#/04-utility-skills/01-task-tree/03-status-and-frontier)), and `depends_on` (sibling directory names this task waits for; keeping dependencies sibling-only is what lets a parent's status be computed rather than hand-kept). Any other key is dropped the next time the tooling rewrites the file — custom metadata belongs in a body section.

Below the frontmatter, each `## ` section is owned by one role so two agents never fight over the same prose: you write `## Objective` (the goal, plus optional `### Context`/`### Conventions`/`### Constraints` the subtree inherits), and the planner may add `## Details` (leads worth passing on — candidate files, data quirks, suggested routes — informative, never binding); the implementer writes `## Results` (findings and the evidence verifying them); the reviewer's `## Review Notes` appears only while findings are open.

A scoped leaf looks like this:

```
---
title: "Filter Sample"
status: not-started
depends_on:
  - 01-load-raw-data
---

## Objective

Drop observations before 2000 and require non-missing returns.

## Results

### Key Findings
- Retained 3.8 M of 4.7 M rows after applying filters.
```

The full field-by-field contract — every key, each section's ownership and shape, context-inheritance rules, and the stale-content checklist — lives in [skills/task-tree/references/task-file-contract.md](skills/task-tree/references/task-file-contract.md).
