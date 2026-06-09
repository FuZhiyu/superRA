---
title: "Align Dispatch Bundles with Task-Local Review"
status: approved
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

Implemented bundle dispatch as a task-local orchestration mechanism.

- Added canonical `Tasks:` bundle templates for implementers and reviewers, with eligibility limited to same-stage, same-domain, same-parent frontier leaves and explicit dependent-sibling sequencing rules ([agent-orchestration/SKILL.md](../../../../../skills/agent-orchestration/SKILL.md#L87-L137)).
- Updated superimplement frontier execution so each unit can be a single task or same-parent bundle, with frontier recomputation after each completed task or bundle and a gate that rejects aggregate bundle approval ([superimplement/SKILL.md](../../../../../skills/superimplement/SKILL.md#L20-L24), [superimplement/SKILL.md](../../../../../skills/superimplement/SKILL.md#L79-L86)).
- Updated canonical role specs so implementers and reviewers read each assigned task independently, write task-local results or review notes, and move each task status separately inside a bundle ([implementer.md](../../../../../agents/implementer.md#L17-L26), [reviewer.md](../../../../../agents/reviewer.md#L19-L30)).
- Regenerated the managed Codex/direct-mode artifacts from the canonical role specs: [direct-mode-implementer.md](../../../../../skills/using-superRA/references/direct-mode-implementer.md), [direct-mode-reviewer.md](../../../../../skills/using-superRA/references/direct-mode-reviewer.md), [superra_implementer.toml](../../../../../.codex/agents/superra_implementer.toml), and [superra_reviewer.toml](../../../../../.codex/agents/superra_reviewer.toml).

Verification:

- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` confirmed generated agent files and direct-mode references are up to date.
- `python3 skills/report-in-markdown/scripts/check_markdown.py superRA/task-system/planning-redesign/task-tree-design/03-dispatch-bundles/task.md` reported the final task markdown clean.
- `git diff --check -- skills/agent-orchestration/SKILL.md skills/superimplement/SKILL.md agents/implementer.md agents/reviewer.md skills/using-superRA/references/direct-mode-implementer.md skills/using-superRA/references/direct-mode-reviewer.md .codex/agents/superra_implementer.toml .codex/agents/superra_reviewer.toml superRA/task-system/planning-redesign/task-tree-design/03-dispatch-bundles/task.md` passed with no whitespace errors.
