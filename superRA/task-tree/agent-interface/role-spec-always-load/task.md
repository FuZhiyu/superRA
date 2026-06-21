---
title: "Explicit Body Load for Always-Loaded Skills (Non-Autoload Harnesses)"
status: implemented
depends_on: []
tags: []
created: 2026-06-19
---

## Objective

Make both always-loaded skills — `superRA:using-superra` and `superRA:report-in-markdown` — reliably enter every implementer/reviewer dispatch's context across harnesses, not just Claude.

Background: Claude autoloads an agent's frontmatter `skills: [...]` into the dispatched subagent's context (live-confirmed — see Results). Non-Claude harnesses (Codex) have no such autoload, so a skill named only in frontmatter never enters context there. The role-spec body previously said only "Load skills per `superRA:using-superra` §Skill-Load Manifest", which is two indirections away from `report-in-markdown` (load using-superra → read manifest → discover report-in-markdown → load it) and does not reliably trigger its load where autoload is absent.

Deliverable: the role-spec bodies (`agents/implementer.md`, `agents/reviewer.md`) instruct loading both always-loaded skills **if not already in context** (so Claude's autoload is not double-loaded), then the stage/domain skills per the manifest, before any edit. Regenerate the Codex named agents and direct-mode references from source.

Success criteria: both role-spec bodies carry the conditional-load instruction naming both skills; the four generated artifacts are regenerated and `sync_codex_agents.py --scope project --check` is clean; Claude autoload still no-ops the redundant load (live-confirmed); the Codex path loads both per the body instruction (to verify on the Codex live path via the 09 canary).

### Constraints

- `agents/*.md` are generated-artifact sources. After editing, run `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` — it regenerates `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml`, `skills/using-superra/references/direct-mode-implementer.md`, `skills/using-superra/references/direct-mode-reviewer.md`. The direct-mode "Before You Start" text is hard-coded in the generator (`render_*_direct_mode_before_you_start`), not copied from the source body — update it there too.
- The bootstrap load instruction must live in the role-spec body (the agent reads it before it has loaded `using-superra`), not inside `using-superra`.

## Results

Implemented in direct mode by the orchestrator.

- Rewrote item 1 of `## Before You Start` in [agents/implementer.md](../../../../agents/implementer.md) and [agents/reviewer.md](../../../../agents/reviewer.md): "If `superRA:using-superra` and `superRA:report-in-markdown` are not already in your context, load them … Skip any skill already in context; do not reload."
- Updated the two hard-coded direct-mode templates in [sync_codex_agents.py](../../../../skills/codex-superra-setup/scripts/sync_codex_agents.py) to match, then regenerated all four artifacts; `--check` is clean.

**Live evidence (orchestrator ran the SDK harness against the subscription, sonnet):** a dispatched real `superRA:implementer`, asked to state its markdown file-citation rule **without loading any skill or reading any file**, answered "markdown links with line anchors, not backtick-wrapped paths" with **zero `Skill`-tool loads** — proving `report-in-markdown` is autoloaded into context via the frontmatter `skills:` field in Claude. The conditional wording therefore no-ops correctly in Claude (no double-load) and is the load mechanism for non-autoload harnesses (Codex). The `Skill` PreToolUse hook is blind to autoloaded skills by construction, so always-loaded coverage must use a discriminating behavioral canary (task 10), not the hook.

**Integration self-check (`git diff 1739a8ff..HEAD`):** the role-spec change surface is [agents/implementer.md](../../../../agents/implementer.md), [agents/reviewer.md](../../../../agents/reviewer.md), the generator [sync_codex_agents.py](../../../../skills/codex-superra-setup/scripts/sync_codex_agents.py) (both hard-coded direct-mode templates), and the four regenerated artifacts (`.codex/agents/superra_{implementer,reviewer}.toml`, `direct-mode-{implementer,reviewer}.md`). All hunks tie to this objective; the source-body and generator-template wording match and the regenerated artifacts are in sync (`sync_codex_agents.py --scope project --check` clean). Host-fit and DRY+Necessity gate pass: the added instruction encodes the non-default conditional-load mechanism for non-autoload harnesses, behavior the agent would not infer on its own. No suspicious hunks.
