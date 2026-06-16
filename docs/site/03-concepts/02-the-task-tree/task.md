---
title: "The Task Tree"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

The task tree is where a superRA project keeps its state. It is an ordinary directory of files: a `superRA/` folder whose subdirectories are tasks, each holding a `task.md`. The filesystem hierarchy *is* the task hierarchy — a task that contains subdirectories is a branch that frames its children, and a task with no children is a leaf that holds actual work. Because the whole state is plain committed files, a fresh agent or a returning human can open the repo and reconstruct what was done, what is in progress, and what is left from the files and git history alone. The tooling that operates on the tree lives in the [task-tree skill](skills/task-tree/SKILL.md); the file format itself is specified in the [task file contract](skills/task-tree/references/task-file-contract.md).

The [Reference › Task File](#/05-reference/01-task-file) page is the field-by-field lookup; this page explains the ideas you need to read a tree.

## What a task holds

Every `task.md` carries a small frontmatter block and a few body sections. The frontmatter records the task's `title`, its `status`, and `depends_on` — the list of sibling tasks that must finish first. The body sections are the working content: `## Objective` states the intended work, `## Results` records what actually happened and what was found, and `## Review Notes` carries the reviewer's active findings while a task is under review. These sections are owned by different roles at different times — the planner writes the objective, the implementer fills the results, the reviewer writes the notes — which is what lets several agents collaborate through the same file without overwriting each other. The [How-To › Work With Task Files](#/04-how-to/03-work-with-task-files) guide walks through reading and editing them yourself.

## Status and rollup

A task's `status` moves through a small set of values as work progresses — from `not-started`, to `in-progress`, to `implemented` once the implementer is done, then either `approved` by the reviewer or `revise` if it needs another pass. A branch task does not carry its own status independently: its status rolls up automatically from its children, so a folder is "done" exactly when everything inside it is. This means you can glance at any level of the tree and know how much of that subtree is finished without opening every leaf. The full status set and its lifecycle are defined in the [task file contract](skills/task-tree/references/task-file-contract.md) and looked up on the [Reference › Status and Frontier](#/05-reference/03-status-and-frontier) page.

## Dependencies and the frontier

Tasks declare dependencies on their *siblings* — a task lists the directory names of the tasks under the same parent that must complete before it can start. These edges turn the tree into a directed graph of what-blocks-what. The **frontier** is the set of tasks that are ready to run right now: not yet finished, with every dependency already satisfied. When superRA asks "what is next?", it computes the frontier and dispatches from it, which is how the workflow knows what can proceed in parallel and what must wait. You never schedule tasks by hand; you declare the dependencies and the frontier follows.
