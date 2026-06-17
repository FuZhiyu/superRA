---
title: "Rewrite Quickstart as the Single End-to-End Narrative"
status: not-started
depends_on:
  - 01-ia-and-scaffold
tags: []
created: 2026-06-17
---

## Objective

Rewrite `docs/site/02-quickstart/task.md` into the spine of the whole site: one walkthrough that takes a researcher through a full task workflow and introduces every core concept *inline along the way*, instead of deferring them to a Concepts section (now deleted). Details that a reader does not need in the flow are linked to Reference, not explained. Keep the toy size-and-momentum example and the existing dashboard screenshots.

The user's design sketch committed on this branch (section headers + inline `<!-- ... -->` comments in this file) is the authoritative baseline; resolve every inline comment and remove it. The intended shape:

### Prerequisite

- Git literacy is required (branching/merging recommended) — this is a real prerequisite for using agents at all, state it plainly.
- superRA runs on **Claude Code or Codex**. The narrative uses Claude Code; note it applies equally to Codex, with install and agent-invocation being the only differences (link the Codex specifics to Reference / Install).
- Resolve the `uv` vs `python3` question accurately rather than hand-waving: the bundled CLI scripts are run via `uv run --script` (PEP 723), and `uv` is the recommended path; state the actual requirement, don't leave the reader guessing. (Authority: repo `CLAUDE.md §Local Task-Tree CLI Development`.)

### Install + set up a project

- Plugin install: the two `claude plugin …` commands, plus a one-line Codex pointer.
- Lead onboarding with the **adopt-an-existing-project** path, matching the user's edit: commit existing work, start the harness, and ask something like *"use superRA and retroactively create task trees for [what I'm working on], and show me the dashboard."*
- Introduce the trigger word at high level: **saying `superra` triggers the workflow** — that is all the reader needs. Do not explain how the hook is wired (contributor internal).

### A typical workflow — superplan → superimplement → superintegrate

Walk one workflow end to end, with a subsection per phase, introducing concepts as they first appear:

- **Superplan.** Plain-language request; trigger phrase `superplan`; no harness plan-mode needed. Introduce the **task tree** *at a high level* here — the project's state is stored as a committed tree of small task files the agent reads and writes. Do **not** teach the `superra` CLI surface (that is for agents); instead introduce the **dashboard** as how a *human* sees the tree, and show how to open it (`./superRA/superra dashboard`, or just ask the agent to show it). Keep the one-gate approval point (plan is presented before code is written). Link full task-tree design to Reference.
- **Superimplement.** Trigger `superimplement`. The **implementer–reviewer pair** is the central discipline — implementer writes, an independent reviewer returns APPROVE/REVISE, work only advances on APPROVE, review is never skipped. Introduce **roles & adversarial review** inline here (this content used to be its own Concepts page — fold the essential idea in, link the role specs for detail).
- **Watch + read results (merged).** Merge the old "watch progress" and "read results" steps. The **dashboard is the default way to monitor** — it auto-updates in real time as agents work; results live in the committed task files (durable handoff), and the dashboard is how you read them. De-emphasize the markdown-file/CLI path to a brief mention.
- **Superintegrate.** Introduce the INTEGRATE phase at high level — protect results against drift, sync with the base branch intent-aware, refactor for codebase fit, document, and ship. Link `superintegrate` for detail. (This replaces the deleted Concepts › Integration & Protection page's role in the reading flow.)

### Where to go next

End by directing the reader to the two new skill pages — [Domain Skills](#/03-domain-skills) and [Utility Skills](#/04-utility-skills) — as the next read, plus Reference for lookups and Showcase for a real tree.

## Planner Guidance

This is the longest single rewrite. Lean on the existing prose already in the file and in the soon-deleted concepts pages — you are condensing and inlining proven copy, not writing from scratch. Cut ruthlessly: anything that reads as repetition of a concept already introduced earlier in the same page is the verbosity this restructure exists to remove. Keep one paragraph per line.
