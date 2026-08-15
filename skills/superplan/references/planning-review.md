# Planning Review (Reviewer Mechanics)

Load when dispatched at `Stage: planning-review`. No git range or diff — the evidence is the assigned task/subtree, the provided context (exploration synthesis, design rationale), and `superra task check`, a structural preflight rather than the semantic review.

## Review Mode

The dispatch carries a `Review mode:` of **handoff-readiness** or **design-review**.

- **Handoff-readiness:** clarity, completeness, human readability, internal consistency, parent/sibling context, dependency sanity, objective/guidance split, and whether an implementer could execute the assigned task or subtree from the task files plus provided context. Human readability is satisfied by a self-orienting pointer naming the convention and how it bears on the task (`task-tree-design.md` §Context Distillation) — a correct pointer to an auto-loaded doc or manifest skill is not an under-distillation finding; copied rule text where a pointer would do is.
- **Design review:** objective fit of the proposed architecture, decomposition, and task structure.

Both modes return `[BLOCKING]` findings for poor tree design, not only unclear prose. Review against [task-tree-design.md](task-tree-design.md): durable ownership, depth vs. breadth, split/merge sizing (§Splitting Tasks), branching and dependency quality, parent/sibling context, update-task lifecycle, action-verb durability, `## Objective` / `## Details` split. Siblings sharing an edit surface are a merge finding, not a `depends_on` finding.

## Verdict and Note Ownership

Return **APPROVE** or **REVISE**. Planning review never changes `status:`.

- **REVISE:** numbered `[BLOCKING]` / `[ADVISORY]` findings in the assigned target's `## Review Notes` only. Link child task files when a finding concerns a descendant.
- **Re-review:** delete confirmed-fixed items.
- **APPROVE:** remove the assigned target's `## Review Notes` section.

Edit only the assigned target's `## Review Notes` — not child review notes, `## Revision Notes`, `status:`, or any other body section.
