---
title: "Polish Pass: Fix Audience Leaks + Prose Quality Across Reading-Flow Pages"
status: not-started
depends_on:
  - 02-quickstart
  - 03-domain-skills
  - 04-utility-skills
  - 05-finalize
  - 06-shorten-readme
  - 07-welcome-design-philosophy
tags: []
created: 2026-06-17
---

## Objective

A `writing`-skill **Polish pass** over the user-facing reading-flow prose. The content and structure are settled and approved; this pass improves *how it reads* and removes *audience leaks*. Sentence/paragraph scope — do not restructure pages or change which concepts each page covers.

**Targets:** `docs/site/01-welcome/task.md`, `docs/site/02-quickstart/task.md`, `docs/site/03-domain-skills/task.md`, `docs/site/04-utility-skills/task.md`, and the repo-root `README.md`. Build the audience model first (researchers adopting superRA), then check every sentence against it.

**Goal 1 — eliminate audience leaks.** The prose repeatedly addresses the wrong audience or names agent-facing internals the adopter does not need. The discipline is "write to the reader, not the conversation": never make the reader think about a thing only to tell them they don't use it.

- Worked example to fix: *"You read the tree not through the CLI — that is the agents' interface — but through the **dashboard**…"* → just *"You read the tree on the **dashboard**."* The CLI/agent-interface contrast should vanish, not be explained.
- Soften the `frontier` jargon in the Quickstart to the plain behavior (the agent automatically picks up the next task whose dependencies are satisfied; you watch the order unfold on the dashboard). The formal term stays only in Reference, which this task does not touch.
- Sweep for the same class of leak everywhere: references to the `superra` CLI surface, internal mechanisms (hooks, status rollup internals, load order), or "as we saw / as the conversation" framing. Surface behavior and design intent; cut the wiring.

**Goal 2 — prose quality.** Tighten wording, fix awkward or clunky sentences, parallelism, hedging, and flow so the pages read like clean published documentation. Preserve the argument, structure, technical claims, and the researcher-approved design-philosophy framing — polish the prose, not the substance.

**Verify:** `docs/build_site.sh` builds clean; the five pages pass the markdown self-diagnose; no `03-concepts`/`04-how-to` link regressions; the six-page structure and all approved content decisions are intact (slide-design still absent, dashboard-first framing preserved).

## Planner Guidance

Load the `writing` skill in Polish mode (`references/polish.md` + `references/style.md`; the audience-leak rule is `style.md §Audience: write to the reader, not the conversation`). The leaks are systemic, not one-off — read each page end to end against the audience model rather than fixing only the cited example. One paragraph per line.
