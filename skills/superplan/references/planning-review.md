# Planning Review (Reviewer Mechanics)

Load this reference when dispatched at `Stage: planning-review`. It carries the reviewer's execution mechanics for reviewing a task tree before implementation. Planner-facing dispatch context — when to trigger planning review, what each mode evaluates from the planner's side — lives in [thorough-planning.md](thorough-planning.md) §Planning Review; this reference is the reviewer's side.

Planning review evaluates the task tree itself, before any implementation. There may be no git range or implementation diff — the evidence is the assigned task/subtree, the provided context (exploration synthesis, design rationale), and `superra task check`.

## Review Mode

The dispatch carries a `Review mode:`:

- **handoff-readiness** — is the task/subtree clear, complete, human-readable, internally consistent, and ready for an implementer to execute from the task files plus provided context?
- **design-review** — are the proposed architecture, decomposition, assumptions, artifact pipeline, dependency structure, and domain reasoning good enough for the objective?

Use the provided context as review evidence. Run `superra task check --root superRA` when the dispatch asks for it — it is a structural preflight, not the semantic review.

## Verdict and Note Ownership

Return **APPROVE** or **REVISE** without editing task `status:` — planning review never changes status.

- **REVISE:** write numbered `[BLOCKING]` / `[ADVISORY]` findings in the assigned target's `## Review Notes` only. Link child task files when a finding concerns a descendant.
- **Re-review:** delete confirmed-fixed items.
- **APPROVE:** remove the assigned target's `## Review Notes` section.

Edit only the assigned target's `## Review Notes`. Do not edit child task review notes, `## Revision Notes`, task `status:`, or any other body section.
