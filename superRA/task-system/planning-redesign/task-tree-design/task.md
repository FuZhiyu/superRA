---
title: "Task Tree Design Protocol"
status: approved
depends_on:
  - placement-and-update-lifecycle
tags: []
created: 2026-06-09
---

## Objective

Redesign the superRA task-tree design protocol so durable task structure, task-file mechanics, dispatch bundling, planning review, and consolidation/integration cleanup have clear owners and coherent rules.

### Context

The current placement/update instructions sit partly in `skills/task-system/references/planning.md` and partly in `skills/superplan/SKILL.md`. That split makes task-system carry workflow judgment while superplan points back to a utility reference for tree-design decisions. Recent failures show the cost:

- Agents treat a task's current enumerated scope as closed, creating broad sibling trees instead of widening the existing owner and placing new work deeper.
- Historical provenance can beat future maintenance ownership, so a CLI command-surface change may land under restructuring history rather than the CLI surface that will own it.
- A multi-child niche update such as `postponed-status` can survive at root because subtree size is mistaken for workstream scope.
- Action-verb update parents such as "consolidation" can survive integration as durable structure even after their update episode has shipped.

The redesign should make `superplan` own task-tree design and keep `task-system` focused on task-file mechanics and command surfaces.

### Design Direction

- Create a superplan-owned reference such as `skills/superplan/references/task-tree-design.md`.
- Rename `skills/task-system/references/planning.md` to a task-file contract reference, e.g. `task-file-contract.md`, and keep only task-file schema, section semantics, status/dependency mechanics, stale-content rules, and results-shape rules there.
- Teach agents to place work by durable home: the implementation surface, artifact family, and future maintenance concern that should own the result after integration.
- Teach agents to widen existing concerns before adding breadth. Existing objectives are editable current-state contracts, not fixed historical boundaries.
- Teach agents to branch for independent review value, then use `depends_on` only for prerequisite ordering.
- Treat parent objectives as inherited shared context. Treat dependent sibling tasks as ordered peers whose results are read only when the downstream objective needs them.
- Allow temporary update subtasks for complex implementation, then mature or merge them during consolidation/integration so the tree represents latest state rather than change history.

### Validation

- Planning review covers tree-design quality, not just prose clarity.
- Dispatch instructions support bundled simple tasks without weakening task-local status and review ownership.
- Consolidation and integration instructions catch misplaced root/subtree updates, action-verb parents that need maturation, and scope expansions that require objective/status rewrites.
- Cross-reference sweep leaves no active source surface pointing to `task-system/references/planning.md` for tree-design policy.

## Results

The task-tree design redesign is implemented and reviewed across six approved child tasks.

### Key Findings

- `superplan` now owns task-tree design policy through [task-tree-design.md](../../../../skills/superplan/references/task-tree-design.md). The reference covers durable-home placement, depth over breadth, branching for review value, dependency edges as prerequisite ordering, parent context versus sibling results, temporary update tasks, update-task expiry, action-verb parent maturation, and broader-parent creation.
- `task-system` now owns task-file mechanics through [task-file-contract.md](../../../../skills/task-system/references/task-file-contract.md). The old `skills/task-system/references/planning.md` path has been removed from active source references.
- Dispatch instructions now support bundled simple tasks as spawn-cost amortization while preserving per-task reads, results, statuses, review notes, and approvals.
- Planning review now evaluates tree-design quality directly, including durable ownership, branching, dependencies, parent/sibling context, update-task lifecycle, action-verb durability, and task clarity.
- Consolidation and integration cleanup now apply the task-tree design protocol before Document, including whole-tree update-task checks, mature/rename handling, scope-expansion rewrites, and advisory use of placement diagnostics.

### Verification

- Each child task is approved after implementer/reviewer dispatch.
- The final sweep recorded clean active-reference checks, generated-agent sync, targeted task-system tests, and retained historical task-record citations only as provenance.
