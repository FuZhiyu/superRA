---
title: "The Task File"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

A `task.md` is the unit you read and edit. Each task is a directory holding one, and you spend your time in three places: the frontmatter at the top, the `## Objective` you write when scoping work, and the `## Results` an implementer fills in when it finishes. The rest is structure the tooling and agents maintain for you.

The frontmatter you touch by hand is short. `title` is the name shown in the tree and dashboard. `status` tracks where the task sits in the cycle — you set it when you park or resume work, and the tooling rolls a parent's status up from its children (see [Status and the frontier](#/04-utility-skills/01-task-tree/03-status-and-frontier)). `depends_on` lists the sibling directory names this task waits for; dependencies are sibling-only, which is what lets a parent's status be computed rather than hand-kept. The remaining keys (`tags`, `created`, and leaf-only `script`/`input`/`output`) are filled by the create command or left alone.

Below the frontmatter, a task carries named `## ` sections, each owned by one role so two agents never fight over the same prose:

- **`## Objective`** — what you write when you scope the task: its goal, plus optional `### Context`, `### Conventions`, and `### Constraints` that the whole subtree inherits. Implementers read it but do not rewrite it.
- **`## Results`** — what the implementer writes: findings, the evidence that verifies them, caveats, and any deviation from your guidance. This is where you read what a finished task actually found.
- **`## Review Notes`** — the reviewer's open findings; present only while items are unresolved, removed on approval.

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

The full field-by-field contract — every key, every body section's ownership and shape, the context-inheritance rules, and the stale-content checklist — lives in [skills/task-tree/references/task-file-contract.md](skills/task-tree/references/task-file-contract.md). Reach for it when you need the exact rule; this page is the orientation.
