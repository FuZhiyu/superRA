---
title: "The CLI"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

Day to day you do not run these. You say "superra, work the frontier" and the agent reads the tree, finds what is ready, and runs the CLI on every step while you watch the [dashboard](#/04-utility-skills/01-task-tree/04-dashboard). Reach for `./superRA/superra` yourself — the wrapper exposes the same commands the agent runs — when you want to inspect the tree, scaffold a few tasks, or repair it after a messy edit.

Inspect state and pull up one task:

```bash
./superRA/superra task tree                      # the whole tree with status badges
./superRA/superra task frontier                  # leaf tasks ready to dispatch now
./superRA/superra task read 01-data/02-merge     # one task with its full inherited context
```

`task read` is what dispatch uses: it prints the file plus the ancestor chain, the status of depended-on siblings, and unresolved comments, so the agent arrives oriented. Run it to see exactly what an agent sees on arrival.

Scope or restructure work:

```bash
./superRA/superra task create 01-data/03-filter \
  --title "Filter Sample" \
  --objective "Drop obs before 2000, require non-missing returns." \
  --depends-on 02-merge

./superRA/superra task move 01-data/03-filter 02-analysis/01-filtered-sample
```

Use `task move`, not a raw `mv`: it carries markdown links and sibling `depends_on` edges through the rename so nothing dangles.

Comments steer a task without editing its body; a pinned note surfaces inline on the next `task read` and on the dashboard:

```bash
./superRA/superra task comment list 01-data/02-merge        # unresolved comments
./superRA/superra task comment resolve 01-data/02-merge 3   # toggle resolved state
```

After any bulk change or raw filesystem edit, confirm the tree is still consistent:

```bash
./superRA/superra task check       # audit status, dependency integrity, cycles
./superRA/superra task status fix  # repair branch statuses to match child rollups
```

The DAG view (`task dag <subtree>`, Mermaid output) and the [dashboard](#/04-utility-skills/01-task-tree/04-dashboard) round out the surface. Every flag, bulk status operation, result-append command, and migration tool is in [skills/task-tree/references/commands.md](skills/task-tree/references/commands.md).
