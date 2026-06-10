# Planning Review (Reviewer Mechanics)

Load when dispatched at `Stage: planning-review`. Planner-facing dispatch context — when to trigger, what each mode evaluates — lives in [thorough-planning.md](thorough-planning.md) §Planning Review; this is the reviewer's side.

Planning review evaluates the task tree before any implementation, so there is no git range or diff. The evidence is the assigned task/subtree, the provided context (exploration synthesis, design rationale), and `superra task check` — a structural preflight, not the semantic review.

## Review Mode

The dispatch carries a `Review mode:` of **handoff-readiness** or **design-review** (defined in [thorough-planning.md](thorough-planning.md) §Planning Review).

Both modes can return `[BLOCKING]` findings for poor tree design, not only unclear prose. Review against [task-tree-design.md](task-tree-design.md): durable ownership, depth vs. breadth, branching and dependency quality, parent/sibling context, update-task lifecycle, action-verb durability, and the `## Objective` / `## Planner Guidance` split.

## Verdict and Note Ownership

Return **APPROVE** or **REVISE** without editing task `status:` — planning review never changes status.

- **REVISE:** write numbered `[BLOCKING]` / `[ADVISORY]` findings in the assigned target's `## Review Notes` only. Link child task files when a finding concerns a descendant.
- **Re-review:** delete confirmed-fixed items.
- **APPROVE:** remove the assigned target's `## Review Notes` section.

Edit only the assigned target's `## Review Notes`. Do not edit child task review notes, `## Revision Notes`, task `status:`, or any other body section.
