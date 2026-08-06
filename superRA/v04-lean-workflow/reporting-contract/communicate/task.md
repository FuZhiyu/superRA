---
title: "Communicate: Write, Rewrite, Distill, Review"
status: not-started
depends_on: []
---

## Objective

Implement the expanded parent contract as the concise, standalone `superRA:communicate` skill, replacing the current split across `using-superra` §Communication, `implement-task` §Reporting, and `report-in-markdown`.

- Teach one three-layer hierarchy: outcome, decision, or present state first; decision-relevant evidence, caveat, and next action second; linked mechanics and optional detail last. Decide the reader and action before selecting content; ground material claims; use structural budgets rather than word quotas. Keep disqualifying caveats beside the conclusion and do not manufacture a bottom line for unresolved exploration.
- Add `references/structures.md` for concrete, skimmable forms across chat, task results, planner updates, reviews, and handoffs.
  - Nested lists with short, complete sentences are the default pyramid: top-level bullets carry takeaways; nested bullets carry support, caveats, and mechanics in descending importance.
  - Headings carry conclusions rather than generic topics. Paragraphs carry connected reasoning, narrative, or causality that a list would fragment.
  - Reject paragraph walls, flat bullet lists with no hierarchy, and fragments that gain brevity by hiding relationships.
- Add `references/rewrite.md` for applying the contract to existing low-density material. It routes `patch`, `structural rewrite`, or `stop`; distills source units as keep, point, merge, drop, or conflict; preserves exact literals, meaning, claim force, dependencies, and useful voice; and verifies truth, cold-readability, and the final diff. It must work on task files, reports, handoffs, and conversation drafts.
- Make `communicate` an always-loaded companion to `using-superra`: the main-agent autoload path and both role skills load it before human-facing output, with harness evidence. Preserve direct standalone invocation. Other skills point without restating; academic `writing` retains manuscript-specific audience, argument, citation, and consistency discipline.
- Retire `report-in-markdown` as a separate skill. Move its Markdown, rich-content, standalone-IO, scripts, and render-integrity support under `communicate` as load-on-demand mechanics; update every active call site, hook, test, inventory, and user-facing document.
- Add `references/friction-audit.md`, informed by `avoid-ai-writing`, organized by observable reader cost: redundancy, indirection, unsupported abstraction, buried structure, and ambiguity. Do not infer authorship, use banned-word or punctuation quotas, flatten voice, or change any marker without a density or friction cost. Preserve provenance and the upstream MIT notice for copied material.
- Keep one authoritative home per instruction and apply the contributor DRY, same-file-restatement, and necessity gates line by line. Update `README.md`, `skills/CATEGORIES.md`, `CLAUDE.md`, the Skill-Load Manifest, release notes, and affected docs-site utility pages.
- Verify discovery and behavior with the skill validator, relevant automated suites, and realistic harness sessions covering a planner update, task-result distillation, an implementer return, a communication review/rewrite, Markdown render guidance, and academic-writing composition. Test that the same information becomes a skimmable nested pyramid rather than a paragraph wall or flat bullet list. Include a negative case where an `avoid-ai-writing` pattern carries no density or friction cost and must survive.

## Planner Guidance

- Primary evidence: [Communicate research synthesis](../../attachments/research-communicate.md), [concise-writing research](../../attachments/research-concise-writing.md), and [writing-surfaces map](../../attachments/map-writing-surfaces.md).
- Upstream reference: [`conorbronsdon/avoid-ai-writing` at `b72b7c4`](https://github.com/conorbronsdon/avoid-ai-writing/commit/b72b7c42b196e113d2477c21c62df58061bc804f). Curate by the parent contract rather than vendoring its catalog as the communication goal.
- Preserve the current render checker behavior while relocating [`report-in-markdown`](../../../../skills/report-in-markdown/SKILL.md); the task-tree hook imports its scripts by path, and harness canaries name the skill explicitly.
- Use paired before/after examples only where they teach a transferable decision: answer-first hierarchy, selection over compression, and friction-based rewriting. Put rewrite detail and examples in `references/rewrite.md`; the skill body itself must model the target style.

## Results
