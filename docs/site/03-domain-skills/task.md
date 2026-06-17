---
title: "Domain Skills"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

A domain skill loads *on top of* a workflow phase, not instead of it. The [workflow](#/02-quickstart) supplies the choreography — dispatch a task, review it, advance — and the domain skill supplies the discipline applied inside it: what counts as good work for *this kind of research*, enforced as the agent goes and checked again by the reviewer. The implementer and reviewer working a data-analysis task both load the data-analysis skill, so they are held to the same standard.

The payoff for you as an adopter: supporting a new kind of research means writing one domain skill, not forking the workflow. The implementer–reviewer pair, the task tree, and the integration phase all carry over unchanged. Whether your work is a regression, a proof, or a manuscript, the same spine runs and the matching domain skill decides what discipline applies inside it.

The sections below introduce each currently-implemented domain skill with the one idea you need to tell whether it fits your work. Each links to its `SKILL.md`, which is the authority for the full discipline — read the skill file when you want the details, not a second copy here. The authoritative grouping lives in [CATEGORIES.md](skills/CATEGORIES.md).

## Data analysis — `econ-data-analysis`

Use this when the task imports, cleans, merges, filters, constructs variables from, aggregates, or models data — economic, financial, or panel data especially, but the discipline is language-agnostic (Python, Julia, R, Stata).

Its flagship discipline is the **Iron Law: no transformation without first describing the data.** The agent describes what it actually has — shapes, keys, distributions, missingness — before it filters a row or builds a variable, because the most expensive analysis bugs are the ones where the agent silently dropped half the sample and reported that everything looked fine. Around that law sits a **describe–analyze–validate** loop run as three concurrent disciplines, plus pitfall catalogs for the operations that bite most often (merges, time series, aggregations). See [`econ-data-analysis/SKILL.md`](skills/econ-data-analysis/SKILL.md).

## Theory and modeling — `theory-modeling`

Use this when the task derives, solves, verifies, or proves anything mathematical — stating assumptions, writing first-order conditions, solving an equilibrium, running comparative statics, checking a proof, or producing renderable model notes.

Its flagship discipline is **four gates, walked in the order a reader's trust depends on them: Objects & Notation → Assumptions → Derivations → Verification & Rendering.** A reader cannot evaluate an assumption that uses an undefined symbol, a derivation without the active assumption set, or a verification claim without an auditable derivation — so the agent defines the objects and notation first, fixes the assumptions next, and only then manipulates equations. The gates are concurrent: every modeling step exercises all four, and the documentation is part of the artifact rather than a cleanup phase afterward. See [`theory-modeling/SKILL.md`](skills/theory-modeling/SKILL.md).

## Writing — `writing`

Use this when the task drafts, polishes, proofreads, or reviews prose a human will read — a manuscript section, an abstract, a response letter. It is language- and format-agnostic (LaTeX, Markdown, Quarto, plain text).

Its flagship discipline is one principle across three modes: **preserve substance, polish prose.** The argument, the logic, the structure, the technical claims, and the author's intent are sovereign; wording, flow, parallelism, and mechanical correctness are the editing target. The three working modes — **Review** (find issues), **Polish** (apply edits within a fixed scope), and **Draft** (write new prose) — share that principle, a style and structure knowledge base, and eight consistency dimensions an agent can check in parallel. See [`writing/SKILL.md`](skills/writing/SKILL.md).

## On the roadmap

The architecture is built to grow by adding verticals, not by forking the workflow. Two are planned but not yet implemented:

- **Literature review** — citation integrity and claim-evidence mapping.
- **Simulation** — seed discipline, sensitivity across parameter grids, and stochastic reproducibility.

Each plugs into the same scaffolding the implemented domains use: the implementer–reviewer pair, the task-tree handoff, and the human-in-the-loop review gates.

When you have a sense of which discipline your work needs, the next page introduces the [utility skills](#/04-utility-skills) — the domain-neutral tools the workflow and agents compose across every vertical.
