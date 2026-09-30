---
title: "Adopt the Reproduction Graph Across an Existing Project"
status: not-started
depends_on: []
---

## Objective

Rewrite [adoption.md](../../../skills/reproducibility/references/adoption.md) so it covers declaring the graph for a whole existing project, with the one-task start kept as the bounded option.

- **Declare every task's steps back to external inputs,** from the scripts as they are, without editing code. Agree the external inputs with the researcher and present the DAG for review.
- **Run by slice:** the first build goes upstream-first over targets the researcher chooses from the recorded cost.
- Keep the existing cheap-discovery rule.
- The skill's load-table row for `adoption.md` matches the new scope.
- **Validated without git:** `superra task check`, `repro status`, and the dashboard DAG work on a scratch project with declared steps and no repository; any failure is fixed or reported to [06-empty-root-bootstrap](../06-empty-root-bootstrap/task.md)'s owner.
