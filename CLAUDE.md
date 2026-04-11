# superRA — Contributor Guidelines

This repo is **superRA**, a fork of [Superpowers](https://github.com/obra/superpowers) adapted for economic research. It ships a complete PLAN → IMPLEMENT → VALIDATE → INTEGRATE workflow for AI agents acting as disciplined Research Assistants. See `README.md` for the full skill inventory and design rationale.

## Working in This Repo

When you are modifying superRA itself (skills, hooks, agents, docs), you are editing behavior-shaping content. Treat it with care.

- **Read before you change.** Skill content has been tuned through real sessions. Understand why a piece of text exists before rewording it. Red Flags tables, rationalization lists, and the "your human partner" / RA-framing language are deliberate.
- **One problem per commit.** Keep commits focused. Don't bundle unrelated edits.
- **Describe the problem, not just the change.** Commit messages should explain what was broken or missing, not just what moved.
- **Test on at least one harness** (Claude Code is primary) before claiming a change works. Skills are code — verify behavior, don't just read the diff.

## Skill Changes

Skills are not prose. If you modify skill content:

- Use `superRA:writing-skills` to develop and test changes.
- Run the skill through a realistic session to confirm it triggers when it should and doesn't when it shouldn't.
- Be cautious editing carefully-tuned content (Red Flags tables, rationalization lists, RA-framing language, severity protocols). Changes here should be driven by observed failures, not stylistic preference.

## Understand the Project Before Restructuring

superRA has its own tested philosophy:

- **RA framing.** The agent is a Research Assistant implementing the researcher's ideas, not judging methodology.
- **Iron Law.** NO TRANSFORMATION WITHOUT PRIOR DESCRIPTION. This is non-negotiable and shapes every analysis-touching skill.
- **Living handoff docs.** PLAN.md and RESULTS_UPDATE.md are updated inline at each step, owned atomically by the agent doing the work.
- **Two-stage review.** Data integrity first, implementation correctness second. Review is never skipped.
- **Lean agents, rich references.** Two prototype agents (implementer, reviewer) load stage-specific domain references at dispatch time. One source of truth per concern.

Before proposing structural changes to skill design, workflow phases, or agent orchestration, read the existing skills in `skills/superRA/` and the workflow skills they reference.

## General

- Keep `README.md`, `RELEASE-NOTES.md`, and skill tables in sync when adding or renaming skills.
- Prefer editing existing skills over creating new ones. New skills should carve out a clearly distinct concern.
- Domain-specific or project-specific configuration does not belong in core superRA — publish it as a separate plugin.
