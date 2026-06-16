---
title: "Skills and Agents Reference"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

Skills are the instruction sets superRA loads at runtime to teach agents the right discipline for a phase or domain.
Agents are the role prototypes — implementer and reviewer — that execute and sign off on work.
This page is a lookup table; the authoritative inventory with one-line descriptions lives in [skills/using-superRA/SKILL.md §Skill Inventory](skills/using-superRA/SKILL.md), and the category grouping lives in [skills/CATEGORIES.md](skills/CATEGORIES.md).

## Workflow skills

Workflow skills are domain-agnostic.
They own the procedural shape of each phase and call the matching domain skill when a task touches a research vertical.

| Skill | Phase | What it does |
|---|---|---|
| `superplan` | PLAN | Scope check, task decomposition, task tree creation. |
| `superimplement` | IMPLEMENT + VALIDATE | Per-task dispatch, one-pass review loop, reproducibility verification. |
| `superintegrate` | INTEGRATE | Protect key results, sync with base, integrate/refactor, document, finish. |
| `agent-orchestration` | Cross-cutting | Multi-agent dispatch patterns, parallel subagents, reviewer-feedback adjudication. |

## Domain skills

Domain skills carry vertical-specific discipline and load on top of the workflow skill when a task touches their domain.

| Skill | Domain | Flagship discipline |
|---|---|---|
| `econ-data-analysis` | Data analysis | Iron Law (no transformation without prior description), describe–analyze–validate loop, pitfall catalogs. |
| `theory-modeling` | Theory / modeling | Four-gate discipline (Objects & Notation, Assumptions, Derivations, Verification & Rendering). |
| `writing` | Academic writing | Preserve-substance / polish-prose principle over Review, Polish, and Draft modes. |

## Utility skills

Utility skills are domain-neutral tools callable by workflow skills, agents, or directly by a researcher.

| Skill | What it provides |
|---|---|
| `result-protection` | Drift/regression tests to guard key results from unintended changes. |
| `refactor-and-integrate` | Codebase-coherence tools — convention fit, PR-friendly diffs, minimum net diff. |
| `report-in-markdown` | Markdown style guide for agents writing markdown, with figure, math, and table references. |
| `semantic-merge` | Intent-aware branch integration — conflict resolution, stale-reference sweep, propagation-to-coherence. |
| `task-tree` | Tree tooling — query/frontier/DAG, scaffolding, live dashboard, static export, migration. |
| `worktree-data-sync` | Non-git data sync between worktrees (seed, diff, apply, teardown). |
| `zotero-paper-reader` | Search, retrieve, and analyze papers from a Zotero library; BibTeX/citation generation. |
| `mistral-pdf-to-markdown` | PDF → Markdown conversion with image extraction via the Mistral OCR API. |

## Stage → skill load manifest

Agents load skills based on the `Stage:` field in their dispatch.
The full Stage → required-skills table is the authoritative map in [skills/using-superRA/SKILL.md §Skill-Load Manifest](skills/using-superRA/SKILL.md).

A compressed view:

| Stage | Skills loaded (beyond the always-on pair) |
|---|---|
| `implementation` | _(none beyond `using-superra` + `report-in-markdown`)_ |
| `planning-review` | `superplan/references/planning-review.md` |
| `protection` | `result-protection` |
| `sync` | `semantic-merge` |
| `integration` | `refactor-and-integrate` |
| `documentation` | _(none beyond the always-on pair)_ |

Domain add-ons (e.g. `econ-data-analysis`, `writing`) load in addition to the generic Stage row when the task matches the domain.

## Agents

| Agent | Role |
|---|---|
| **implementer** | Executes tasks under the active domain's discipline. Dispatched by the orchestrator. Sources: [agents/implementer.md](agents/implementer.md). |
| **reviewer** | Verifies work independently using the APPROVE / REVISE protocol. Sources: [agents/reviewer.md](agents/reviewer.md). |
