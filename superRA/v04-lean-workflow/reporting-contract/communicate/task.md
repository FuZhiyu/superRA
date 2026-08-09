---
title: "Communicate: Write, Rewrite, Distill, Review"
status: revise
depends_on: []
---

## Objective

Deliver `superRA:communicate` as the standalone human-facing communication contract, with progressive-reveal writing references and hook-backed enforcement.

- The skill owns selection, information hierarchy, rewriting, distillation, and communication review across conversation, task files, reports, planner updates, reviews, and handoffs.
- `academic-writing` retains manuscript-specific discipline. Communicate owns Markdown mechanics through load-on-demand references after replacing `report-in-markdown`.
- Main-agent Markdown writes require Communicate before mutation. Every Markdown edit under the task tree triggers a non-blocking reminder to apply Communicate when the text is user-facing.
- Each instruction has one authoritative home; callers point rather than restate.

## Planner Guidance

- Primary evidence: [Communicate research synthesis](../../attachments/research-communicate.md), [concise-writing research](../../attachments/research-concise-writing.md), and [writing-surfaces map](../../attachments/map-writing-surfaces.md).
- Upstream reference: [`conorbronsdon/avoid-ai-writing` at `b72b7c4`](https://github.com/conorbronsdon/avoid-ai-writing/commit/b72b7c42b196e113d2477c21c62df58061bc804f). Curate by the parent contract rather than vendoring its catalog as the communication goal.
- The split is by edit surface: `skill-and-references` owns skill content, routing, and inventories; `hooks` owns runtime enforcement and harness evidence.

## Revision Notes

- Simplify the post-edit checkpoint from status-transition detection to a uniform task-tree Markdown reminder; the child `hooks` task owns the implementation.

## Results

- [`superRA:communicate`](../../../../skills/communicate/SKILL.md) now gives all superRA roles one human-facing communication contract, with load-on-demand references for structure, sentence style, rewriting, friction review, and Markdown mechanics.
  - The [style-guidance task](style-guidance/task.md) replaced compressed labels with observable tests and verified the result through cold-reader and rewrite probes.
- Main-agent hooks enforce the contract at the two requested checkpoints.
  - Markdown writes require the relevant task context and Communicate load.
  - Moving a task to `implemented` succeeds, then prompts for a final writing check.
