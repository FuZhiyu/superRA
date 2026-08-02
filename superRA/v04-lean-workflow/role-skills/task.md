---
title: "Role Skills: Retire the Prototype Agents"
status: approved
depends_on: []
---

## Objective

Convert the implementer and reviewer role specs into role skills loaded by dispatched general-purpose agents, and retire the dedicated-agent plumbing, so one dispatch mechanism serves Claude Code and Codex.

- Create the role skills (working names `skills/implement-task`, `skills/review-task`) carrying the protocol now in `agents/implementer.md` / `agents/reviewer.md`. Review-protocol content is rewritten by the `review-skill` sibling; everything else lands here.
- The implement skill carries the scope contract: deliver what was asked, at the scope intended; if the request seems mistaken or a better approach exists, say so in a sentence and continue as asked rather than quietly narrowing, widening, or transforming the work. Add the planner-side counterpart in `task-tree-design.md`: objectives state when a task is deliberately open-ended; otherwise the objective's artifacts define scope. Extend, don't duplicate, `using-superra` §Code-Change Defaults (those govern code edits; this governs task scope).
- Dispatch prompts instruct the role-skill load, replacing both `subagent_type` role encoding and Claude frontmatter autoload; update the `agent-orchestration` dispatch templates and the `using-superra` Skill-Load Manifest accordingly. Main-filled seats load the role skill directly.
- Retire `agents/implementer.md`, `agents/reviewer.md`, generated `.codex/agents/*.toml`, `skills/codex-superra-setup` (generator, tests, SKILL), `skills/using-superra/scripts/resolve_role.py` + `references/canonical-role.md`, and the named-agent warning that exists only because `subagent_type` could be dropped.
- Update every surface that cites the role specs: `using-superra` §Task Interface role-ownership pointers, `task-file-contract.md` status/section ownership sentences, `codex-instructions.md` routing, `handoff-doc` redirect, `CLAUDE.md` ownership table + Agent Load Surface, plugin manifests, and the harness tests under `tests/harness-instruction-following/`.
- Validation: the test suite passes, and one scripted or live dispatch shows a general-purpose agent loading the role skill and completing a task turn (read task → edit → commit → status return).

## Planner Guidance

- The Sync step (`superintegrate/references/sync.md`) already dispatches generic agents with instructed skill loads — use its dispatch shape as the template.
- Codex has no frontmatter autoload today; the role bodies already instruct loads there, so the skill-based model is closer to how Codex works than the agent model is.
- Scope-contract motivation: latest-generation agents guess at unstated wants, delivering unrequested work that then costs review and fixing. Source phrasing and over-scoping evidence: [review-prompting research](../attachments/research-review-prompting.md) §A, §D.
- Full plumbing inventory with line references: [review-architecture map](../attachments/map-review-architecture.md) §1 and the tier-4/5 file list at its end.
- Frontmatter `skills:` autoload was the one Claude-specific benefit of agent files; the replacement is an explicit load line in the dispatch template — verify with a load canary, not hook observation (frontmatter loads are invisible to the Skill hook).

## Results

Roles are now skills. `skills/implement-task/SKILL.md` and `skills/review-task/SKILL.md` carry the protocol formerly in `agents/implementer.md` / `agents/reviewer.md`; the review protocol is a faithful port for the `review-skill` sibling to rewrite. Both open with a §Before You Start load instruction naming `superRA:using-superra` and `superRA:report-in-markdown` — that instruction is what replaces the Claude-only frontmatter `skills:` autoload, and it is the same mechanism on Codex.

Every dispatch template now reads `Agent:` with `Load \`superRA:<role>-task\` skill.` as its first line ([agent-orchestration/SKILL.md](../../../skills/agent-orchestration/SKILL.md), plus the four `superintegrate` dispatches and the `superplan` planning-review dispatch). The templates name no agent type: the harness default is the only option once roles are skills, so spelling it out in every template and every prose mention was maintenance cost with no behavioral effect. The Skill-Load Manifest gained a Role axis, so it is now three axes (Role + Stage + Domain). Seat assignment tells a main-filled seat to load the same skill; `superimplement`'s seat-execution table routes `main` to `role-skill` instead of `canonical-role`.

The scope contract landed in `using-superra` §Work Defaults as item 4 (the section was renamed from §Code-Change Defaults, which no longer covered its content). Placement differs from the objective's suggestion of the implement skill: `using-superra` is loaded by every agent including the interactive main agent, which will not load a role skill once the `workflow-defaults` sibling makes interactive the default. Researcher chose this placement. The planner-side counterpart is in `task-tree-design.md` §Writing Objectives — mark deliberately open-ended tasks, otherwise the named artifacts are the scope.

Retired: `agents/`, `.codex/agents/*.toml`, `skills/codex-superra-setup/`, `skills/using-superra/scripts/` (`resolve_role.py` + test), `references/canonical-role.md`, and the named-agent warning in `agent-orchestration`. Also retired `references/claude-instructions.md` and its `main-agent.md` pointer — its entire content was canonical-role routing, so it had nothing left. `.agents/skills/` symlinks and `RELEASE-NOTES.md` (with the `rm -f ~/.codex/agents/superra_*.toml` cleanup line for existing Codex users) were updated to match.

Consumer surfaces updated: `using-superra` §Task Interface, `task-file-contract.md` (status and section ownership), `codex-instructions.md` (availability routing collapses to agent-tool present/absent; tool map maps `Agent` → `spawn_agent(agent_type="default")`; §Named Agent Setup and §Related Codex Skill deleted), `handoff-doc` redirect, `changing-the-tree.md`, `interactive-mode.md`, `econ-data-analysis`, `theory-modeling/CLAUDE.md`, `CLAUDE.md` (ownership table, Agent Load Surface, Codex and Harness Design, the `skills/*`-or-`agents/*` gate line, the retired generated-artifacts bullet), `CATEGORIES.md` (new Role category, five categories), `.codex-plugin/plugin.json`, `docs/README.codex.md`, and both `docs/site` pages. `sync.md` now says `Agent:` so the Codex tool map covers it.

`implement-task` was trimmed on review: the evidence-before-claims, completeness, and stale-content self-check gates are gone (frontier models self-verify; the Opus 5 prompting guidance calls explicit verification scaffolding an over-verification driver), leaving a two-item §Self-Check — gate walk and editing hygiene. §Handoff became §Writing Results, a pointer to `using-superra` §Task Interface plus the one implementation-specific line about what `## Results` must carry. §Dispatch Templates in `agent-orchestration` lost a paragraph of shape description the templates already show. `review-task` is untouched; the `review-skill` sibling rewrites it.

The results-writing self-check hook belongs to the `reporting-contract` sibling, which owns the rules it would enforce; it is not added here.

### Test suite

`125 passed` for `tests/harness-instruction-following`, and `tests/check-harness-compatibility.sh` is clean (its Codex-agent-generation section became a role-skills-packaged check).

The always-loaded contract changed mechanism, so `check_always_loaded_frontmatter` / `parse_frontmatter_skills` became `check_always_loaded_load_instruction` / `parse_section`, asserting each role skill's §Before You Start names both skills. Dispatch detection moved from agent type to prompt content: `TranscriptEvent.is_role_dispatch(role_skill)` replaces `is_dispatch_of` at the role call sites, and the committed sample transcripts were rewritten to the new dispatch shape. LC001, LC005, LC006, LC007, LC020, LC022 in `load_contract.json` and their README matrix rows were repointed; LC006 changed from generated-agent drift to role-skill surface (both role skills exist and reach every seat; no named-agent surface survives).

**Coverage regression, Codex only.** Both seats now spawn `default`, and the `SubagentStart` payload carries the agent type but not the prompt, so the Codex orchestrator smoke can no longer tell the implementer dispatch from the reviewer dispatch. `evaluate_dispatch_log` gained `minimum_dispatches` and the smoke asserts two `default` dispatches instead of two distinct named types. The Claude path is unaffected — its `Task`/`Agent` event carries the prompt.

### Not done

The validation's live-dispatch leg is unrun: no subagent has been dispatched to load a role skill and complete a task turn. The static half is covered (`test_seat_fillers_reach_the_role_skills_by_name`, the load-instruction contract, packaging checks), but the load-canary the objective asks for needs a real dispatch, which this session's standing instruction reserves for an explicit researcher request. `always-loaded-codex-smoke.sh` and the SDK harness are updated and ready for it.
