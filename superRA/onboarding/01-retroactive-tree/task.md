---
title: "Retroactive Tasks Read Like Regular Tasks"
status: not-started
depends_on: []
---

## Objective

Rewrite [task-tree-design.md](../../../skills/superplan/references/task-tree-design.md#retroactive-task-tree-creation) §Retroactive Task-Tree Creation so a tree built from existing work reads like a forward-planned one.

- **Sources:** code, generated outputs, the paper or draft, and project documents.
- **Each task** gets an objective stating what the work achieves and the outputs it produces, and `## Results` recording the current results with links to those outputs.
- **Status:** `implemented` until the results are verified by a reproduction run or accepted by the researcher; then `approved`. This replaces the current `approved` rule for complete work.
- **Writes stay inside `superRA/`** while the tree is being built.
- Existing callers (`superplan` §Entry Assessment routing path, [interactive-mode.md](../../../skills/using-superra/references/interactive-mode.md) §The spectrum) keep pointing at this section and stay consistent with it.
