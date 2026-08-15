---
title: "Reporting Contract: Concise Writing and the Conversation Boundary"
status: approved
depends_on:
  - role-skills
---

## Objective

Maintain **Communicate**, superRA's human-facing communication contract across conversation, task files, reports, and workflow handoffs. A cold reader should reach the outcome, evidence, caveats, and next action without duplicated facts or avoidable decoding work.

- `superRA:communicate` is standalone and available to planners, implementers, reviewers, integrators, and direct user invocations.
- Brevity comes from selection and structure; clarity wins when compression would obscure meaning.
- The contract governs information choice, order, rewriting, distillation, and review. `academic-writing` owns manuscript discipline; technical Markdown guidance owns rendering mechanics.
- State each fact once. Other surfaces link to the source that produces or maintains it.
- Learn from `avoid-ai-writing` only where a pattern lowers information density or raises communication friction. Authorship detection and “sound human” are outside scope.

## Details

- The approved Results below document the v0.4 baseline. The child task owns the expanded architecture.
- Evidence: [writing-surfaces map](../attachments/map-writing-surfaces.md) and [concise-writing research](../attachments/research-concise-writing.md).
- Showcase/task-file hygiene remains out of scope; update user-facing docs invalidated by the skill replacement.

## Results

- [`superRA:communicate`](../../../skills/communicate/SKILL.md) is the always-loaded owner for human-facing selection, hierarchy, rewriting, distillation, review, and Markdown mechanics.
  - It leads with the answer or honest current state, puts evidence and caveats before implementation details, and states each fact once.
  - Its on-demand references cover nested-pyramid structure, sentence style, rewriting, friction audits, rich Markdown, and standalone-report IO. Academic manuscripts compose it with `superRA:academic-writing`.
  - The [Communicate task](communicate/task.md) owns the implementation and verification record.
- Hook enforcement now covers the two writing checkpoints requested for main agents.
  - Markdown mutations require Communicate evidence; task-owned Markdown also requires the exact task-read context.
  - A direct leaf transition to `implemented` succeeds, then emits a one-shot final-writing reminder.
  - The [hooks task](communicate/hooks/task.md) owns cross-harness behavior and test evidence.
- `report-in-markdown` is retired. Its checker and technical references moved under Communicate, while active role, workflow, domain, inventory, docs-site, showcase-fixture, and harness callers point to the new owner.
- The academic-prose domain skill is now `superRA:academic-writing`; its substantive protocol is unchanged.
