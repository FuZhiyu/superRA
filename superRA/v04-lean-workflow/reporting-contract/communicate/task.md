---
title: "Communicate: Write, Rewrite, Distill, Review"
status: implemented
depends_on: []
---

## Objective

Deliver `superRA:communicate` as the standalone human-facing communication contract, with progressive-reveal writing references and hook-backed enforcement.

- The skill owns selection, information hierarchy, rewriting, distillation, and communication review across conversation, task files, reports, planner updates, reviews, and handoffs.
- Academic `writing` retains manuscript-specific discipline. Communicate owns Markdown mechanics through load-on-demand references after replacing `report-in-markdown`.
- Main-agent Markdown writes require the relevant task context and Communicate load before mutation. Moving a task to `implemented` triggers a non-blocking final writing check.
- Each instruction has one authoritative home; callers point rather than restate.

## Planner Guidance

- Primary evidence: [Communicate research synthesis](../../attachments/research-communicate.md), [concise-writing research](../../attachments/research-concise-writing.md), and [writing-surfaces map](../../attachments/map-writing-surfaces.md).
- Upstream reference: [`conorbronsdon/avoid-ai-writing` at `b72b7c4`](https://github.com/conorbronsdon/avoid-ai-writing/commit/b72b7c42b196e113d2477c21c62df58061bc804f). Curate by the parent contract rather than vendoring its catalog as the communication goal.
- The split is by edit surface: `skill-and-references` owns skill content, routing, and inventories; `hooks` owns runtime enforcement and harness evidence.

## Results
