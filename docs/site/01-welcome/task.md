---
title: "Welcome to superRA"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

superRA turns an AI coding agent into a disciplined research assistant. You bring a research question; superRA gives the agent a workflow that plans the work, implements it under adversarial review, and integrates the result into your codebase without letting the findings quietly drift. It runs on Claude Code, Codex, or any harness that supports skills and subagents.

What it is:

- A **task-tree dashboard** — a live tree, dependency DAG, and kanban view of your project that auto-updates as work progresses, so you both monitor and steer it. Because the whole project state lives in the tree it renders, the dashboard doubles as a handoff surface: you, or a fresh agent session a week later, can pick up exactly where work left off. You are viewing one right now — this documentation site is itself built on the dashboard.
- An adaptive **plan-implement-integrate workflow** that enforces reviewer sign-off at every step and keeps results reproducible long-term.
- **Domain skills** that teach agents the right discipline for the research work at hand, enforced as they go — currently data analysis, theory modeling, and academic writing.

Why superRA rather than an existing agentic-coding framework like [Superpowers](https://github.com/obra/superpowers)?

Those frameworks are built for software engineering, where tasks are verifiable against unit tests or objective metrics, and the current direction pushes hard to remove the human from the loop. Social-science research needs a different rhythm: it is fluid and exploratory, ex-ante unit tests are often impossible to write, and the outputs need human judgement to evaluate. superRA adapts the same workflow spine but keeps the human firmly in the loop.

## How it works

superRA organizes every project into three phases — **PLAN → IMPLEMENT → INTEGRATE**.

<div style="display:flex;gap:18px;align-items:stretch;margin:1.4em 0;font-family:var(--font-text);max-width:560px;">
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
  <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;border-left:2px dashed var(--accent);padding-left:14px;color:var(--accent);font-size:13px;font-style:italic;text-align:center;line-height:1.4;">
    <span aria-hidden="true" style="font-size:20px;">&#8624;</span>
    plan change<br/>loops back to PLAN
  </div>
</div>

In **PLAN**, the agent scopes your request and decomposes it into a *task tree* — a directory of small `task.md` files, each holding one unit of work. In **IMPLEMENT**, an implementer agent executes one task and a separate reviewer agent inspects it adversarially; work only advances on `APPROVE`. In **INTEGRATE**, the finished work is protected against future drift, synced with your base branch intent-aware (never a blind merge), refactored to fit the codebase, documented, and shipped. The phases form a cycle, not a pipeline: a discovery while implementing or a scope change after merge routes back to planning and resumes at the right point, leaving unrelated finished work untouched.

Three ideas carry most of the discipline. An **implementer–reviewer pair** sits at every step, so no result ships without an independent second look. **Domain skills** teach the agent the right protocol for the work at hand — for data analysis, never transform data before describing it; for theory, define objects and assumptions before manipulating equations. And the **task tree** keeps the project's state in committed files you can read at any time, so a fresh agent — or you, a week later — can open the repo and resume from the files and git history alone.

## Start here

- New to superRA and want to try it? The [Quickstart](#/02-quickstart) runs one tiny analysis end to end in about twenty minutes — you will meet the task tree, dispatch, review, and status by doing rather than reading.
- Want the model behind what you saw? The [Concepts](#/03-concepts) section explains the workflow, the task tree, the implementer–reviewer loop, how skills and agents fit together, and what the integration phase protects.
- Have a specific job in mind? The [How-To guides](#/04-how-to) cover named journeys — installing, planning a project, working with task files, watching progress on the dashboard, and integrating and shipping.
- Looking up a field, flag, status, or command? The [Reference](#/05-reference) section has the exact definitions, with links to the skill files that own them.
- Want proof it is real? The [Showcase](#/06-showcase) embeds an actual superRA task tree exported by the same dashboard that renders this site.

superRA is open source and built for researchers comfortable with git and an AI harness. Installation and contribution details live in the project [README](README.md).
