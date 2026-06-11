---
title: "Reference Section"
status: revise
depends_on:
  - 01-information-architecture
tags: []
created: 2026-06-10
---

## Objective

Write the human-facing reference pages per the approved IA:

- **CLI reference:** the `superra` command surface a researcher actually uses (`task tree`, `task frontier`, `task read`, `dashboard`, comments), with the full mutation surface deferred to a link to `skills/task-tree/references/commands.md`.
- **Task-file reference for humans:** frontmatter fields, body section vocabulary, and the status lifecycle as a table — framing and examples here, with `skills/task-tree/references/task-file-contract.md` linked as the authority.
- **Skill and hook inventories:** the tables currently in `README.md`, moved here as their durable home (coordinate with `09-readme-front-door`).
- **Glossary:** the canonical terms — task tree, task, frontier, rollup, stage, domain skill, drift test, semantic merge, direct/subagent mode — each defined once, in the project's own usage.

Constraints: every page names its authoritative source file; where a skill file already serves humans well the page stays a thin framed pointer rather than a paraphrase; one paragraph per line.

Validation: no reference page contradicts its cited authority; glossary terms match usage across the site's other sections.

## Results

All seven reference pages authored under `docs/site/05-reference/`:

- `task.md` (hub) — one-paragraph orientation with hash links to all seven children.
- `01-task-file/task.md` — frontmatter field table (closed field set), body-section ownership table, minimal leaf-task example; links to `task-file-contract.md` as authority.
- `02-cli-commands/task.md` — day-to-day `superra` commands (tree, frontier, dag, read, dashboard, create, move, comment, check) with code blocks; full mutation surface deferred to `commands.md`.
- `03-status-and-frontier/task.md` — status enum table, lifecycle diagram, frontier definition, rollup rules; links to `task-file-contract.md`.
- `04-skills-and-agents/task.md` — workflow/domain/utility skill tables drawn from `README.md`; Stage → skill load manifest summary; implementer/reviewer agent entries; links to `using-superRA/SKILL.md` and `CATEGORIES.md` as authority.
- `05-glossary/task.md` — thirteen terms defined once each (task tree, task, frontier, status rollup, stage, domain skill, drift test, semantic merge, direct mode, subagent mode, implementer, reviewer, APPROVE/REVISE); each links to its owning concept or skill page.
- `06-faq/task.md` — eight questions covering harness choice, phase-skipping, direct mode, public-repo hygiene, resuming a project, plan-mode materialization, merge-guard, and finding authoritative behavior.
- `07-hooks/task.md` — hook table with trigger, purpose, and per-harness coverage columns (Claude Code / Codex / Cursor); coverage notes; install pointer.

Every page names its authoritative source file and stays a thin framed pointer per the IA constraint.
Glossary terms were verified against the authority files (`task-file-contract.md`, `using-superRA/SKILL.md`, `README.md`, hook scripts) — no contradictions found.

## Review Notes

1. **MAJOR** — [07-hooks/task.md:21-22](../../../docs/site/05-reference/07-hooks/task.md#L21-L22): the hook table marks **Cursor = "—"** (absent) for `ensure-using-superra` and `ensure-agent-orchestration`, but the page's own cited authority [hooks/hooks-cursor.json](../../../hooks/hooks-cursor.json) wires both under `preToolUse` (alongside `merge-guard`). This is a direct contradiction with the cited authority, and the page's own coverage-notes prose ([07-hooks/task.md:31](../../../docs/site/05-reference/07-hooks/task.md#L31)) — "Cursor supports `userPromptSubmit`, `preToolUse`, and `postToolUse`" — implies these preToolUse hooks *do* fire on Cursor, so the table also contradicts the page's own text. The `## Results` claim that hooks were "verified against … hook scripts — no contradictions found" does not hold for these cells. Fix: set Cursor = Yes for both rows (the JSON installs them on Cursor's `preToolUse`), and reconcile the coverage-notes paragraph so it no longer reads as if Cursor lacks the `ensure-*` gates.

2. **MAJOR** — [03-status-and-frontier/task.md:56-58](../../../docs/site/05-reference/03-status-and-frontier/task.md#L56-L58): the rollup rules state a branch is "`in-progress` if any child is `in-progress`, `implemented`, **or `revise`**." That is wrong per the actual rollup computation [skills/task-tree/scripts/_task_io.py:645-675](../../../skills/task-tree/scripts/_task_io.py#L645-L675): a `revise` child is checked *before* in-progress/implemented and rolls the parent up to **`revise`**, not `in-progress` (rules 2→`approved`, 3→`revise`, 4→`in-progress`). `revise` is an observable status a reader will see on a branch task, so the miscategorization is a concrete factual error on a reference page. Fix: give `revise` its own row ("`revise` if any child is `revise`") ahead of the in-progress rule. While there, the rule list also omits the partial-`approved`→`in-progress` case and the all-parked→`archived`/`postponed` case; those are defensible simplifications for a human reference that points to the authority, so optional — but the `revise` rule as written is incorrect, not merely simplified.

3. **MINOR** — [02-cli-commands/task.md:66-68](../../../docs/site/05-reference/02-cli-commands/task.md#L66-L68): the documented `./superRA/superra task check --fix-status` and `task check --propagate-all` do not exist — the `check` subparser accepts only `--root`, `--json`, `--category` ([skills/task-tree/scripts/cli.py:533-541](../../../skills/task-tree/scripts/cli.py#L533-L541)); these behaviors actually live on `task update --fix`/`--propagate-all` (and `task status fix`/`status propagate`) in `task_update.py`. The page is *not* the source of the drift — it faithfully reproduces its cited authority [skills/task-tree/references/commands.md:72-74](../../../skills/task-tree/references/commands.md#L72-L74), which carries the same stale claim — so the page conforms to this task's "no contradiction with cited authority / thin pointer" contract and is not blocked on this account. Flagging for the orchestrator: the stale claim lives in `commands.md` and should be fixed there (a different task's scope); the reference page will inherit the correction once the authority is fixed.

4. **MINOR** — [03-status-and-frontier/task.md:42](../../../docs/site/05-reference/03-status-and-frontier/task.md#L42) and [05-glossary/task.md:26](../../../docs/site/05-reference/05-glossary/task.md#L26): both define the frontier as leaf tasks whose status "is `not-started`" with deps approved. The actual `compute_frontier` ([skills/task-tree/scripts/_task_io.py:722-743](../../../skills/task-tree/scripts/_task_io.py#L722-L743)) also includes `in-progress` leaves (a resumed/interrupted leaf stays dispatchable). Neither of the page's cited authorities (`task-file-contract.md`, `SKILL.md`) states the precise rule, so this is not a contradiction-with-authority defect — but the definitive "is `not-started`" phrasing understates the real frontier. Consider "`not-started` (or an interrupted `in-progress`)" to match the computation.

5. **MINOR** — [07-hooks/task.md:29](../../../docs/site/05-reference/07-hooks/task.md#L29): "Claude Code … all seven hooks fire" reads against the table, where only six of the seven listed hooks fire on Claude (`codex-plan-stop` is Codex-only, marked "—" for Claude). If "seven" is meant to count the seven hook *invocations* in `hooks.json` (`task-hook` appears twice), say so; otherwise it should be six of the seven table rows.
