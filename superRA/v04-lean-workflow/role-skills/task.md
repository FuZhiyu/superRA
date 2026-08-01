---
title: "Role Skills: Retire the Prototype Agents"
status: not-started
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
