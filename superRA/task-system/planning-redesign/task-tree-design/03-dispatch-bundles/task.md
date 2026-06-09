---
title: "Align Dispatch Bundles with Task-Local Review"
status: not-started
depends_on: 
  - 02-tree-design-protocol

tags: []
created: 2026-06-09
---

## Objective

Align dispatch and implementation instructions with the new tree-design model.

Define bundle dispatch as spawn-cost amortization across multiple simple tasks, while keeping each task as an independent contract.

### Required Behavior

- Add a canonical bundle dispatch shape in `skills/agent-orchestration/SKILL.md` for same-stage, same-domain, same-parent frontier leaves that share context and are simple enough for one agent.
- Update `skills/superimplement/SKILL.md` so frontier execution can dispatch either one task or a bundle, then re-compute the frontier after the bundled work finishes.
- Preserve task-local ownership inside a bundle: each task path is read with `superra task read`, each task gets its own `## Results`, each task status moves independently, and each task is reviewed to its own verdict.
- Let bundled reviewers review multiple simple tasks in one dispatch while writing `## Review Notes` and status changes in each assigned task file separately.
- Keep dependent siblings out of the same implementation bundle unless the upstream task is already approved. Use `depends_on` to sequence tasks whose outputs or findings are prerequisites.
- Teach the parent/sibling context model at the dispatch boundary: parent objectives provide inherited shared context; dependency status alone does not inject sibling results; downstream agents read approved dependency `## Results` when their objective requires those findings.

### Role Specs and Generated Files

If the implementation needs role-spec changes, update canonical `agents/implementer.md` and `agents/reviewer.md`, then regenerate and check:

- `skills/using-superRA/references/direct-mode-implementer.md`
- `skills/using-superRA/references/direct-mode-reviewer.md`
- `.codex/agents/superra_implementer.toml`
- `.codex/agents/superra_reviewer.toml`

### Validation

- A bundle cannot be approved as an aggregate: verification shows every bundled task has its own final `status: approved`.
- Reviewer instructions make a shallow aggregate review invalid by requiring per-task evidence and notes.
- Existing single-task dispatch templates remain valid.

## Results
