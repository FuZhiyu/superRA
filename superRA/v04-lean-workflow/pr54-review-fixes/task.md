---
title: "PR #54 Review Fixes: Close Every Confirmed Finding Before Merge"
status: approved
depends_on: []
---

## Objective

Fix all sixteen findings from the PR #54 pre-merge review — the ten reported plus the six capped-out cleanups the researcher pulled back in — so the v0.4 branch merges with no known defects in its hook gates, tree hooks, or docs.

### Constraints

- Every behavioral fix lands with the review's reproducing case as a regression test: `tests/hooks/` for the shell-invoked gates, the `skills/task-tree/scripts` pytest suite for the tree hooks.
- Hooks warn on ambiguous tree state; they never auto-mutate task content or flip a status to resolve ambiguity.

## Details

Provenance: adversarially verified review of [PR #54](https://github.com/FuZhiyu/superRA/pull/54) (2026-08-18); most findings were confirmed by running the hooks against the described inputs. Finding-by-finding file/line maps and fix designs are distilled into each child's `## Details`.
