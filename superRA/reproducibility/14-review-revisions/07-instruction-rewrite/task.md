---
title: "Reproduction Instructions Pass the CLAUDE.md Gate"
status: not-started
depends_on:
  - 01-engine-freshness
  - 02-portable-records
  - 03-readiness-model
  - 05-explain-impact
---

## Objective

The agent-loaded reproduction text passes [CLAUDE.md](../../../../CLAUDE.md) §Teach the Protocol and §Skill Prose Style line by line, states each fact once in its owner per §Ownership Boundaries, and defines every term an agent acts on where the agent loads it. Scope: [skills/reproducibility/](../../../../skills/reproducibility/SKILL.md) and its references, [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md) §Effective Dependencies to the end, and [commands.md](../../../../skills/task-tree/references/commands.md) §Reproduction. Load `skill-creator` before editing any `SKILL.md`.

- **Each duplicate cluster collapses to one home** ([gate-audit.md](../attachments/gate-audit.md) §1): saved-input and `--upstream` semantics (10 copies), "acceptance executes nothing" (7), the rerun model (mechanics move from `diagnosing.md` into the contract; the skill keeps the actions), identical-output cutoff (5), the acceptance preview, the significance-count sentence in `commands.md`, "registration follows placement", and Loop steps that restate Gates.
- **Record internals leave the section subagents load.** The contract's record fields, caps, and lock-history mechanics move to task-tree `references/internals.md`.
- **Terms are defined once in `SKILL.md`:** *saved input* versus *external input* (replacing the two meanings of "boundary"), *completion targets*, and *producer chain*; call sites use those names.
- **The stale rule is exhaustive:** task-local is the explicit class and everything else is potentially significant; "maintained path" is defined or dropped.
- **One drift-test rule, in §Gates.** [designing-the-graph.md:9](../../../../skills/reproducibility/references/designing-the-graph.md#L9) blocks on every drift test protecting registered outs; [protect-and-completion.md:8](../../../../skills/reproducibility/references/protect-and-completion.md#L8) registers only researcher-selected ones.
- **Named anti-patterns are cut:** output descriptions (the 251-word §Explain layout, `rerun-or-accept.md` §Preview), wrapper lines, and background-only lines in `SKILL.md` §The Model.
- **Unparseable lines are rewritten** ([gate-audit.md](../attachments/gate-audit.md) §2 item 4).
- **The load surface matches CLAUDE.md §Agent Load Surface** (decision below).

Validation: words measured before and after (the audit estimates about −30% across the three documents); every gate, enum, default, and ordering constraint survives; one realistic harness session exercises registration and the stale rule.

### Researcher decisions

- **Subagent routing into `commands.md`.** CLAUDE.md:135 allows subagents only `task-file-contract.md` §Reproduction Section, yet the skill routes them into `commands.md`. Option (a): extend that exception to `commands.md` §Reproduction and trim it as an agent reference. Option (b): route subagents to `superra repro --help`. Recommendation: (a).

Owning tasks: [06-skill](../../06-skill/task.md), [03-skill-redesign](../../12-agent-protocol/03-skill-redesign/task.md), [03-diagnosis-guidance](../../13-staleness-provenance/03-diagnosis-guidance/task.md).

## Details

This task runs after 01–03 and 05 so the rewrite describes the settled mechanics once. The audit's top ten edits and every file:line are in [gate-audit.md](../attachments/gate-audit.md) §5.
