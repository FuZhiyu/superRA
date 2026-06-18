---
title: "The CLI"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

`./superRA/superra` is how you read and operate on the tree from the shell. Most days you reach for a handful of commands — see the state, find what is ready, and hand a task to an agent:

```bash
./superRA/superra task tree                      # the whole tree with status badges
./superRA/superra task frontier                  # leaf tasks ready to dispatch now
./superRA/superra task read 01-data/02-merge     # one task with its full inherited context
```

`task read` is how you give an agent context. Beyond printing the file, it injects the ancestor chain, the status of every sibling the task depends on, and any unresolved comments pinned to the task, so the agent arrives oriented. The dispatch prompts throughout superRA assume you read tasks this way.

When you scope or restructure work, you create and move tasks:

```bash
./superRA/superra task create 01-data/03-filter \
  --title "Filter Sample" \
  --objective "Drop obs before 2000, require non-missing returns." \
  --depends-on 02-merge

./superRA/superra task move 01-data/03-filter 02-analysis/01-filtered-sample
```

Use `task move` rather than a raw `mv`: it carries markdown links and sibling `depends_on` edges through the rename so nothing dangles.

Comments steer a task without editing its body. You pin a note to a task, and it surfaces inline the next time anyone runs `task read` on it (and on the dashboard). You resolve a comment once it is addressed:

```bash
./superRA/superra task comment list 01-data/02-merge        # unresolved comments
./superRA/superra task comment resolve 01-data/02-merge 3   # toggle resolved state
```

After any bulk change or a raw filesystem edit, run the diagnostics to confirm the tree is still consistent:

```bash
./superRA/superra task check       # audit status, dependency integrity, cycles
./superRA/superra task status fix  # repair branch statuses to match child rollups
```

The dependency DAG view (`task dag <subtree>`, Mermaid output) and the dashboard (`./superRA/superra dashboard`) round out the surface; the dashboard has [its own page](#/04-utility-skills/01-task-tree/04-dashboard). The complete command surface — every flag, the bulk status operations, result-append commands, and migration tools — is in [skills/task-tree/references/commands.md](skills/task-tree/references/commands.md).
