---
title: "Welcome to superRA"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

superRA turns an AI coding agent into a disciplined research assistant. You bring a research question; superRA gives the agent a workflow that plans the work, implements it under adversarial review, and integrates the result into your codebase without letting the findings drift. It runs on Claude Code, Codex, or any harness that supports skills and subagents.

What it is:

- A **task-tree dashboard** — a live tree, dependency DAG, and kanban view of your project that auto-updates as work progresses, so you both monitor and steer it. The whole project state lives in the tree it renders, so the dashboard doubles as a handoff surface: you, or a fresh agent session a week later, pick up exactly where work left off. You are looking at one now — this site is itself built on the dashboard.
- An adaptive **plan-implement-integrate workflow** that enforces reviewer sign-off at every step and keeps results reproducible long-term.
- **Domain skills** that teach agents the right discipline for the research at hand and enforce it as they go — currently data analysis, theory modeling, and academic writing.

## Why superRA?

AI agents are fast but undisciplined. They generate more code than anyone will carefully review. They drift as the context window fills, and starting fresh loses the thread of what was done and why. They drop half the sample before a regression runs, then report "everything looks good". superRA brings discipline at every step: no result ships without adversarial review, the domain skill enforces the right protocol as the work goes, and the integration phase folds each task into your codebase so what lands is coherent, not a pile of single-shot outputs.

## Why not an existing framework like Superpowers?

[Superpowers](https://github.com/obra/superpowers) and similar agentic-coding frameworks are built for software engineering, where tasks are verifiable against unit tests or objective metrics, and the trend pushes hard to remove the human from the loop. Social-science research needs a different rhythm: it is fluid and exploratory, ex-ante unit tests are often impossible to write, and the outputs need human judgement to evaluate. superRA adapts the same workflow spine but keeps the human firmly in the loop.

## How it works

superRA organizes every project into three phases — **PLAN → IMPLEMENT → INTEGRATE**.

<div style="display:flex;align-items:stretch;margin:1.4em 0;font-family:var(--font-text);max-width:560px;">
  <div style="position:relative;width:118px;flex:none;margin-right:-1px;">
    <div style="position:absolute;top:34px;bottom:18px;right:0;border-left:2px dashed var(--accent);border-top:2px dashed var(--accent);border-bottom:2px dashed var(--accent);border-top-left-radius:10px;border-bottom-left-radius:10px;"></div>
    <div style="position:absolute;top:24px;right:-7px;color:var(--accent);font-size:15px;line-height:1;" aria-hidden="true">&#9650;</div>
    <div style="position:absolute;top:50%;left:0;transform:translateY(-50%);width:104px;color:var(--accent);font-size:12px;font-style:italic;text-align:center;line-height:1.35;">plan change<br/>loops back<br/>to PLAN</div>
  </div>
  <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:0;">
    <div style="width:100%;border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:6px;background:var(--bg-card);padding:14px 18px;box-shadow:var(--shadow-sm);">
      <strong style="font-family:var(--font-display);font-size:17px;color:var(--accent);letter-spacing:0.02em;">PLAN</strong>
      <div style="font-size:14px;color:var(--text-mid);line-height:1.5;margin-top:4px;">scope &middot; task decomposition &middot; <code style="font-family:var(--font-mono);font-size:0.9em;">superRA/</code> task tree</div>
    </div>
    <div style="font-size:18px;color:var(--text-mute);line-height:1;padding:6px 0;" aria-hidden="true">&darr;</div>
    <div style="width:100%;border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:6px;background:var(--bg-card);padding:14px 18px;box-shadow:var(--shadow-sm);">
      <strong style="font-family:var(--font-display);font-size:17px;color:var(--accent);letter-spacing:0.02em;">IMPLEMENT</strong> <span style="font-size:13px;color:var(--text-mute);">(per task)</span>
      <div style="font-size:14px;color:var(--text-mid);line-height:1.5;margin-top:4px;">implementer &#8644; reviewer loop<br/>APPROVE advances &middot; REVISE loops back</div>
    </div>
    <div style="font-size:18px;color:var(--text-mute);line-height:1;padding:6px 0;" aria-hidden="true">&darr;</div>
    <div style="width:100%;border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:6px;background:var(--bg-card);padding:14px 18px;box-shadow:var(--shadow-sm);">
      <strong style="font-family:var(--font-display);font-size:17px;color:var(--accent);letter-spacing:0.02em;">INTEGRATE</strong>
      <div style="font-size:14px;color:var(--text-mid);line-height:1.5;margin-top:4px;">Protect results &middot; Sync with base &middot; Integrate/refactor &middot; Document &middot; Finish</div>
    </div>
    <div style="font-size:18px;color:var(--text-mute);line-height:1;padding:6px 0;" aria-hidden="true">&darr;</div>
    <div style="border:1px solid var(--st-ok-t);border-radius:999px;background:var(--st-ok);color:var(--st-ok-t);padding:6px 22px;font-family:var(--font-display);font-size:15px;font-weight:600;">finished</div>
  </div>
</div>

In **PLAN**, the agent scopes your request and decomposes it into a *task tree* — a directory of small `task.md` files, each holding one unit of work. In **IMPLEMENT**, an implementer agent executes one task and a separate reviewer agent inspects it adversarially; work advances only on `APPROVE`. In **INTEGRATE**, the finished work is protected against future drift, synced with your base branch intent-first (never a blind merge), refactored to fit the codebase, documented, and shipped. The phases form a cycle, not a pipeline: a discovery while implementing, or a scope change after merge, routes back to planning and resumes at the right point, leaving unrelated finished work untouched.

## Design Philosophy

Five ideas carry most of the discipline. If they fit how you work, superRA is for you.

- **Everything important is in the repo.** Every task's objective, status, and results live in committed files — not in a chat log or an agent's working memory. *Why it matters:* a fresh agent session, or you a week later, resumes from the repo alone. You never lose the thread between sessions or get locked into one long conversation.
- **Adversarial review at every step.** A separate reviewer agent must `APPROVE` each task before it advances; a `REVISE` loops the work back until it passes. *Why it matters:* it catches the "everything looks good" failure — the agent drops half the sample before running the regression — which is the biggest risk of fast AI output.
- **Domain discipline, enforced as the work happens.** A domain skill applies your field's methodology while the agent works — describe-before-transform for data, assumptions-before-algebra for theory — and the reviewer re-checks it. *Why it matters:* you get methodology you can defend, not just code that runs.
- **Autonomous by default, human-in-the-loop by design.** The agent drives the workflow forward on its own and stops only for a hard blocker, a decision that is genuinely yours, or a milestone you set — never for procedural "should I proceed?" check-ins. *Why it matters:* momentum without babysitting, and interruptions reserved for the judgment calls only a researcher can make.
- **Composable and adaptive.** superRA hands the agent reusable mechanisms it assembles for the situation rather than a fixed script, and the phases form a cycle, not a pipeline — discoveries and scope changes route back to the right point, leaving finished work untouched. A new research type is one new domain skill, not a workflow fork. *Why it matters:* the tool bends to research's exploratory rhythm and grows with your work.

## Start here

- To try it, start with the [Quickstart](#/02-quickstart): one tiny analysis end to end in about twenty minutes. You meet the task tree, dispatch, review, and status by doing rather than reading.
- For which discipline fits your work, the [Domain Skills](#/03-domain-skills) page introduces each one — data analysis, theory modeling, academic writing — with the single idea that tells you whether it applies.
- For the tools the workflow composes, the [Utility Skills](#/04-utility-skills) page covers the task tree, intent-aware merging, result protection, and the rest of the domain-neutral layer.
- To look up a field, flag, status, or command, the [Reference](#/05-reference) section has the exact definitions, with links to the skill files that own them.
- The [Showcase](#/06-showcase) embeds a real superRA task tree, exported by the same dashboard that renders this site.

superRA is open source and built for researchers comfortable with git and an AI harness. Installation and contribution details live in the project [README](README.md).
