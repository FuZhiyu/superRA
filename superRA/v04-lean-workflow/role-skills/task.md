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

## Details

- The Sync step (`superintegrate/references/sync.md`) already dispatches generic agents with instructed skill loads — use its dispatch shape as the template.
- Codex has no frontmatter autoload today; the role bodies already instruct loads there, so the skill-based model is closer to how Codex works than the agent model is.
- Scope-contract motivation: latest-generation agents guess at unstated wants, delivering unrequested work that then costs review and fixing. Source phrasing and over-scoping evidence: [review-prompting research](../attachments/research-review-prompting.md) §A, §D.
- Full plumbing inventory with line references: [review-architecture map](../attachments/map-review-architecture.md) §1 and the tier-4/5 file list at its end.
- Frontmatter `skills:` autoload was the one Claude-specific benefit of agent files; the replacement is an explicit load line in the dispatch template — verify with a load canary, not hook observation (frontmatter loads are invisible to the Skill hook).

## Results

Roles are skills. [implement-task](../../../skills/implement-task/SKILL.md) and [review-task](../../../skills/review-task/SKILL.md) carry the protocol the `agents/` prototypes held; the review protocol was ported faithfully for the [review-skill](../review-skill/task.md) sibling to rewrite. Each opens with a §Before You Start load instruction, which replaces the Claude-only frontmatter autoload with one mechanism that works on Codex too. (It named `report-in-markdown` at the time; the [reporting-contract](../reporting-contract/task.md) sibling replaced that with `communicate`.)

**Every dispatch template names the role skill and no agent type.** Once roles are skills the harness default is the only option, so spelling it out in every template was maintenance cost with no behavioral effect. The Skill-Load Manifest gained a Role axis, making it three: Role, Stage, Domain. A main-filled seat loads the same skill a dispatched seat does.

**Retired:** `agents/`, the generated `.codex/agents/*.toml`, `skills/codex-superra-setup/`, the `resolve_role.py` canonical-role resolver and its reference, `claude-instructions.md` (whose entire content was canonical-role routing), and the named-agent warning in `agent-orchestration`. `RELEASE-NOTES.md` carries the `rm -f ~/.codex/agents/superra_*.toml` cleanup line for Codex users who installed the named agents globally.

**The scope contract landed in `using-superra` §Work Defaults**, not the implement skill as the objective suggested: `using-superra` is loaded by every agent including the interactive main agent, which loads no role skill. The planner-side counterpart is in `task-tree-design.md` §Writing Objectives — mark deliberately open-ended tasks, otherwise the named artifacts are the scope.

**`implement-task` was trimmed on review.** The evidence-before-claims, completeness, and stale-content self-check gates are gone — frontier models self-verify, and explicit verification scaffolding drives over-verification — leaving a two-item §Self-Check of gate walk and editing hygiene.

**The test suite changed mechanism with the contract.** The always-loaded check moved from frontmatter parsing to asserting each role skill's §Before You Start names both skills, and dispatch detection moved from agent type to prompt content, with the committed sample transcripts rewritten to the new shape. Six `load_contract.json` entries and their README matrix rows were repointed; LC006 changed from generated-agent drift to role-skill surface. 125 harness tests pass and the compatibility script is clean.

### Notes

- **Codex loses one distinction.** Both seats now spawn `default`, and the `SubagentStart` payload carries the agent type but not the prompt, so the Codex orchestrator smoke can no longer tell an implementer dispatch from a reviewer dispatch — it asserts two `default` dispatches instead of two named types. Claude's event carries the prompt and is unaffected.
- **The live-dispatch leg is unrun.** The static half is covered by the seat-name test, the load-instruction contract, and the packaging checks, but the load canary the objective asks for needs a real dispatched turn. The Codex smoke and the SDK harness are updated and ready for it.
