---
title: "FAQ"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

Common questions from researchers starting with superRA.

**Which harness should I use — Claude Code or Codex?**
Both are fully supported.
Claude Code gives you a richer hook surface (hard-gate hooks on `PreToolUse`, `ExitPlanMode`, and `UserPromptSubmit` all fire reliably).
Codex gives you named custom agents (`superra_implementer`, `superra_reviewer`) that surface in the Codex agent picker.
If you are unsure, start with Claude Code — the install is a single `claude plugin install` command.
See the [Quickstart](#/02-quickstart) for the install and setup steps.

**Can I skip PLAN and go straight to IMPLEMENT?**
Yes, for small or exploratory work.
You can create a single task file by hand, fill in `## Objective`, and dispatch an implementer directly.
The three-phase cycle is the recommended path for work that spans multiple tasks or will need a PR; skipping PLAN on a single self-contained task is reasonable.

**Can I skip INTEGRATE for a quick experiment?**
Yes.
INTEGRATE is required before landing work on `main` — it protects key results, syncs against the current base, and matures documentation.
For a throwaway branch or a personal experiment that will never merge, you can stop after IMPLEMENT.

**Do I have to use the implementer–reviewer subagent pair every time?**
No.
Direct mode (the main agent implements the task itself) is available for small, clearly-scoped tasks where the overhead of dispatching two subagents outweighs the benefit.
The recommended default is subagent mode because adversarial review catches errors the implementer cannot self-check.
See the [Quickstart](#/02-quickstart) for the implementer–reviewer loop in action and [skills/using-superRA/SKILL.md §Execution Modes](skills/using-superRA/SKILL.md).

**My project is a public repo. What data hygiene rules apply?**
superRA tasks are committed alongside your code, so any content in `task.md` files becomes public.
Use placeholder or hypothetical research content in examples — never commit real group names, real subject IDs, real query results, or private file paths.
The same rule applies to dashboard exports shared via GitHub Actions artifacts.

**How do I resume a project I set down months ago?**
Run `./superRA/superra task frontier` to see what is ready to dispatch.
Run `./superRA/superra task tree` to see the full status picture.
Open the dashboard (`./superRA/superra dashboard`) for a visual overview.
From there, dispatch the frontier tasks with the same `superimplement` invocation you would use for new work.
Resuming and revising mid-flight is owned by [superimplement](skills/superimplement/SKILL.md).

**What happens when the agent makes a plan-mode proposal — does that create task files?**
Not automatically.
The `exit-plan-mode` hook (Claude Code) and `codex-plan-stop` hook (Codex) remind the agent to materialize a proposed plan into a `superRA/` task tree via `superplan`, but they do not create files on their own.
If you accept the plan and want it durable, invoke `superplan` to scaffold the task tree.

**I see a `merge-guard` reminder when I run `git merge`. Should I ignore it?**
No — use `superRA:semantic-merge` instead of a bare `git merge`.
Semantic merge preserves research intent across branches: it classifies conflicts, escalates intent-changing decisions to you, and ensures existing drift tests keep passing after the sync.
A bare merge can silently overwrite result-protection tests or stale references without warning.
See [Utility Skills: Intent-aware Merging](#/04-utility-skills).

**Where do I find the full authority for any superRA behavior?**
The `skills/` and `agents/` directories are the authoritative source for all agent-facing behavior.
This documentation site teaches human journeys and links to those files; it is never a second authority.
When in doubt, read the cited skill file directly.
