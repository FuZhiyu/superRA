---
title: "Welcome to superRA"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

superRA turns an AI coding agent into a disciplined research assistant. It runs on Claude Code and Codex.

What it is:

- A **task-tree dashboard** — a live task tree of your project that keeps every important piece of state committed in your repo rather than trapped in an agent's context, so you can monitor progress in real time and hand any unfinished task to a fresh agent without losing the thread. [Here](#/07-showcase) is an example — and you are looking at the dashboard right now, since this documentation site is built on the very same system.
- An adaptive **plan-implement-integrate workflow** that enforces reviewer sign-off at every step and keeps results reproducible long-term.
- **Domain skills** that teach agents the right discipline for the research at hand and enforce it as they go — currently data analysis, theory modeling, academic writing, and slide design.
- **Utility skills** that teach agents practical mechanics — loading papers from Zotero, writing results in well-formed Markdown, syncing data across worktrees, and more.

## Why superRA?

AI agents are fast but undisciplined. They generate more code than anyone will carefully review. They drift as the context window fills, and starting fresh loses the thread of what was done and why. They drop half the sample before a regression runs, then report "everything looks good". superRA brings discipline at every step: no result ships without adversarial review, the domain skill enforces the right protocol as the work goes, and the integration phase folds each task into your codebase so what lands is coherent, not a pile of single-shot outputs.

## Why not an existing framework like Superpowers?

[Superpowers](https://github.com/obra/superpowers) and similar agentic-coding frameworks are built for software engineering, where tasks are verifiable against unit tests or objective metrics, and the frontier of agentic-driven software engineering pushes hard to remove the human from the loop.

However, **social-science research needs a different rhythm**: it is fluid and exploratory, ex-ante unit tests are often impossible to write, and the outputs need human judgement to evaluate. superRA adapts the same workflow spine but keeps the human firmly in the loop.

## How it works

A typical superRA workflow looks like this:

<div style="margin:1.4em auto;max-width:560px;">
<svg viewBox="0 0 560 324" style="width:100%;height:auto;font-family:var(--font-text);" role="img" aria-label="PLAN, IMPLEMENT, and INTEGRATE phase boxes in a vertical flow down to a finished state, with two dashed 'plan change' edges looping back from IMPLEMENT and INTEGRATE into PLAN.">
  <defs>
    <marker id="ra-loop" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="var(--accent)"/></marker>
    <marker id="ra-down" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="var(--text-mute)"/></marker>
  </defs>

  <path d="M 170 122 C 118 122, 114 46, 168 46" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#ra-loop)"/>
  <path d="M 170 214 C 72 214, 72 34, 168 34" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="5 4" marker-end="url(#ra-loop)"/>

  <line x1="356" y1="70" x2="356" y2="94" stroke="var(--text-mute)" stroke-width="1.5" marker-end="url(#ra-down)"/>
  <line x1="356" y1="162" x2="356" y2="186" stroke="var(--text-mute)" stroke-width="1.5" marker-end="url(#ra-down)"/>
  <line x1="356" y1="254" x2="356" y2="278" stroke="var(--text-mute)" stroke-width="1.5" marker-end="url(#ra-down)"/>

  <g>
    <rect x="170" y="6" width="372" height="62" rx="6" fill="var(--bg-card)" stroke="var(--border)"/>
    <rect x="171" y="14" width="3" height="46" rx="1.5" fill="var(--accent)"/>
    <text x="188" y="29" style="font-family:var(--font-display);font-size:17px;font-weight:700;letter-spacing:.02em;fill:var(--accent);">PLAN</text>
    <text x="188" y="47" style="font-size:13px;fill:var(--text-mid);">scope &middot; task decomposition</text>
    <text x="188" y="62" style="font-size:13px;fill:var(--text-mid);"><tspan style="font-family:var(--font-mono);font-size:11.5px;">superRA/</tspan> task tree</text>
  </g>

  <g>
    <rect x="170" y="98" width="372" height="62" rx="6" fill="var(--bg-card)" stroke="var(--border)"/>
    <rect x="171" y="106" width="3" height="46" rx="1.5" fill="var(--accent)"/>
    <text x="188" y="121" style="font-family:var(--font-display);font-size:16px;font-weight:700;letter-spacing:.02em;fill:var(--accent);">IMPLEMENT<tspan style="font-family:var(--font-text);font-size:11px;font-weight:400;fill:var(--text-mute);"> (per task)</tspan></text>
    <text x="188" y="139" style="font-size:13px;fill:var(--text-mid);">implementer &#8644; reviewer loop</text>
    <text x="188" y="154" style="font-size:13px;fill:var(--text-mid);">APPROVE advances &middot; REVISE loops back</text>
  </g>

  <g>
    <rect x="170" y="190" width="372" height="62" rx="6" fill="var(--bg-card)" stroke="var(--border)"/>
    <rect x="171" y="198" width="3" height="46" rx="1.5" fill="var(--accent)"/>
    <text x="188" y="213" style="font-family:var(--font-display);font-size:16px;font-weight:700;letter-spacing:.02em;fill:var(--accent);">INTEGRATE</text>
    <text x="188" y="231" style="font-size:13px;fill:var(--text-mid);">Protect results &middot; Sync with base</text>
    <text x="188" y="246" style="font-size:13px;fill:var(--text-mid);">Refactor &middot; Mature &amp; consolidate &middot; Finish</text>
  </g>

  <rect x="298" y="282" width="116" height="36" rx="18" fill="var(--st-ok)" stroke="var(--st-ok-t)"/>
  <text x="356" y="305" text-anchor="middle" style="font-family:var(--font-display);font-size:14px;font-weight:600;fill:var(--st-ok-t);">finished</text>

  <rect x="88" y="75" width="60" height="15" fill="var(--bg)"/>
  <text x="118" y="86" text-anchor="middle" style="font-size:10.5px;font-style:italic;fill:var(--accent);">plan change</text>
  <rect x="44" y="118" width="60" height="15" fill="var(--bg)"/>
  <text x="74" y="129" text-anchor="middle" style="font-size:10.5px;font-style:italic;fill:var(--accent);">plan change</text>
</svg>
</div>

In **PLAN**, the agent scopes your request and decomposes it into a *task tree* — a directory of small `task.md` files, each holding one unit of work. In **IMPLEMENT**, an implementer agent executes one task and a separate reviewer agent inspects it adversarially; work advances only on `APPROVE`. In **INTEGRATE**, the finished work is protected against future drift, synced with your base branch intent-first (never a blind merge), refactored to fit the codebase, documented, and shipped.

Research is rarely this linear, though: unanticipated issues surface mid-implementation, and exploratory sessions turn up findings worth recording as tasks for later. superRA supports changing the plan on the fly, or retroactively creating tasks to be reviewed and integrated.

## Design Philosophy

superRA's design centers on a few ideas:

- **The repo reflects the latest state of every task.** Each task's objective, status, and results live in committed files — not in a chat log or an agent's working memory. So you can always start a fresh agent and continue the work without losing the context.
- **Adversarial review at every step.** A separate reviewer agent must `APPROVE` each task before it advances; a `REVISE` loops the work back until it passes.
- **Autonomous by default, human-in-the-loop by design.** The agent drives the workflow forward on its own and stops only for a hard blocker, a decision that is genuinely yours, or a milestone you set — never for procedural "should I proceed?" check-ins.
- **Composable and adaptive.** superRA hands the agent composable mechanisms rather than a fixed pipeline. The workflow is domain-neutral, so you can drop in your own domain skill (say, model simulation) without forking it.

## Start here

- To try it, start with the [Quickstart](#/02-quickstart).
- For which discipline fits your work, the [Domain Skills](#/03-domain-skills) page introduces each one — data analysis, theory modeling, academic writing, slide design.
- For more on the three phases — what each does for you and what you decide along the way — the [Workflows](#/05-workflows) section covers plan, implement, and integrate one page at a time.
- For the tools the workflow composes, the [Utility Skills](#/04-utility-skills) page covers the task tree, intent-aware merging, result protection, and the rest of the domain-neutral layer.
- The [Showcase](#/07-showcase) embeds a real superRA task tree, exported by the same dashboard that renders this site.

superRA is open source and built for researchers comfortable with git and an AI harness. Installation and contribution details live in the project [README](README.md).
