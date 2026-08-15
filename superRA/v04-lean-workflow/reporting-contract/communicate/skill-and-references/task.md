---
title: "Communicate Skill and References"
status: approved
depends_on: []
---

## Objective

Create the concise, standalone `superRA:communicate` skill and its progressive-reveal references, replacing `using-superra` §Communication, `implement-task` §Reporting, and `report-in-markdown` as instruction owners.

- Teach one three-layer hierarchy: outcome, decision, or present state first; decision-relevant evidence, caveat, and next action second; linked mechanics and optional detail last. Decide the reader and action before selecting content; ground material claims; use structural budgets rather than word quotas. Keep disqualifying caveats beside the conclusion and do not manufacture a bottom line for unresolved exploration.
- Add `references/structures.md` for concrete, skimmable forms across surfaces.
  - Nested lists with short, complete sentences are the default pyramid: top-level bullets carry takeaways; nested bullets carry support, caveats, and mechanics in descending importance.
  - Headings carry conclusions rather than generic topics. Paragraphs carry connected reasoning, narrative, or causality that a list would fragment.
  - Reject paragraph walls, flat bullet lists with no hierarchy, and fragments that gain brevity by hiding relationships.
- Add `references/rewrite.md` for existing low-density material. Route `patch`, `structural rewrite`, or `stop`; distill units as keep, point, merge, drop, or conflict; preserve exact literals, meaning, claim force, dependencies, and useful voice; verify truth, cold-readability, and the final diff.
- Add `references/friction-audit.md`, informed by `avoid-ai-writing`, organized by observable reader cost: redundancy, indirection, unsupported abstraction, buried structure, and ambiguity. Do not infer authorship, use banned-word or punctuation quotas, flatten voice, or change a marker without a density or friction cost. Preserve provenance and the upstream MIT notice for copied material.
- Retire `report-in-markdown` as a separate skill. Move its Markdown, rich-content, standalone-IO, scripts, and render-integrity support under `communicate`; update active call sites while preserving checker behavior.
- Make `communicate` an always-loaded companion to `using-superra` and directly invocable standalone. Other role, workflow, domain, and academic-writing skills point without restating.
- Update `README.md`, `skills/CATEGORIES.md`, `CLAUDE.md`, the Skill-Load Manifest, release notes, and affected docs-site utility pages. Apply the contributor DRY, same-file-restatement, and necessity gates line by line.
- Validate with the skill validator, relevant automated suites, and realistic sessions covering planning, task-result distillation, implementer returns, review/rewrite, Markdown rendering, and academic-writing composition. Test a nested pyramid against paragraph-wall and flat-list variants, plus a harmless `avoid-ai-writing` marker that must survive.

## Details

- Read the parent research pointers before authoring. Use paired examples only for transferable decisions: answer-first hierarchy, selection over compression, nested pyramid structure, and friction-based rewriting.
- Preserve the current render checker while relocating [`report-in-markdown`](../../../../../skills/report-in-markdown/SKILL.md); the task-tree hook imports its scripts by path, and harness canaries name the skill explicitly.
- The skill body models the target style; detailed structures, rewrite operations, friction diagnostics, and Markdown mechanics load from their owning references.

## Results

- `superRA:communicate` now owns human-facing selection, hierarchy, rewriting, distillation, and review ([SKILL.md:8](../../../../../skills/communicate/SKILL.md#L8)).
  - The three-layer contract leads with the outcome or honest present state, keeps evidence and disqualifying caveats together, and links mechanics last.
  - The load map composes manuscript work with academic `writing` and routes structures, rewrites, friction audits, Markdown, figures, and standalone IO to on-demand references ([SKILL.md:22](../../../../../skills/communicate/SKILL.md#L22)).
- The references make the contract operational.
  - `structures.md` defaults multi-point output to short nested pyramids and includes paragraph-wall, flat-list, and nested variants ([structures.md:3](../../../../../skills/communicate/references/structures.md#L3)).
  - `rewrite.md` routes patch, structural rewrite, or stop; classifies source units; and preserves exact literals, semantics, dependencies, claim force, and voice ([rewrite.md:3](../../../../../skills/communicate/references/rewrite.md#L3)).
  - `friction-audit.md` changes only patterns with observable reader cost and preserves harmless voice markers; its pinned provenance records the adapted MIT source ([friction-audit.md:18](../../../../../skills/communicate/references/friction-audit.md#L18)).
- `report-in-markdown` is retired; its Markdown, rich-content, standalone-IO, checker, tests, and packaging entry moved under `communicate`.
  - Active role, workflow, domain, task-tree, showcase-fixture, inventory, release-note, docs-site, and harness callers now point to the new owner.
- Verification:
  - The skill validator, 29 render-checker tests, 47 targeted always-loaded and migration contract tests, harness compatibility, Markdown self-diagnosis, and task-tree check pass.
  - Two read-only Codex sessions covered planning, task-result distillation, role returns, review/rewrite, and academic composition. The first exposed paragraph drift and tightened the surface rule; the second produced the nested pyramid from paragraph-wall and flat-list inputs, preserved the exact `DONE` schema and literals, and retained first-person voice, a calibrated hedge, and em dashes.
  - The broader `test_contract.py` still has two unrelated baseline failures: it expects a removed `superimplement` seat table and `superplan/references/decomposition.md`.
