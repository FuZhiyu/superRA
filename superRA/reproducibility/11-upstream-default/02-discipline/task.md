---
title: "Skill, Reference, and Docs Teach the Producer-Chain Default"
status: not-started
depends_on: [01-cli]
---

## Objective

Rewrite the agent-facing and reader-facing instructions for the new default that [01-cli](../01-cli/task.md) ships, so an agent names the result it wants current and lets the build find the stale producers.

- **[reproducibility SKILL.md](../../../../skills/reproducibility/SKILL.md).**
  - §Selecting Steps: targets include their producer chain; `--only` uses saved inputs as they sit on disk.
  - Builds skip fresh steps, so name the task or the final result, not each stale step.
  - When another session is editing a producer in this worktree, use `--only`.
  - §Commands table: match the new default.
  - §Recording a Result: plain `status` covers the chain; a result checked with `--only` says so in `## Results`.
- **[rerun-or-accept.md](../../../../skills/reproducibility/references/rerun-or-accept.md).** Acceptance stays step-local: to cover a producer, name it. The `--dry-run` cost now includes stale producers.
- **[adoption.md](../../../../skills/reproducibility/references/adoption.md).** In an adopted project, a producer that has never been built reads `missing`, even when its outputs exist, so a default downstream build runs it. Accept or build such producers first, or use `--only`.
- **[review-task SKILL.md](../../../../skills/review-task/SKILL.md) line 28.** The evidence command becomes plain `status`.
- **[docs-site reproducibility page](../../../../docs/site/04-utility-skills/09-reproducibility/task.md) and [RELEASE-NOTES.md](../../../../RELEASE-NOTES.md) 0.5.0.** Describe the default and `--only`.

### Validation

- Apply the [CLAUDE.md](../../../../CLAUDE.md) §Teach the Protocol three tests line by line to every changed `skills/*` line, then §Skill Prose Style. Load `skill-creator` before editing any `SKILL.md`.
- A realistic harness session on a disposable fixture: stale producers in two tasks feed a final step. Asked to bring the final result current, the agent issues one target build, not a list of every stale step. Record the command it issued.
- `git grep -- --upstream` outside `docs/plans/` and historical `## Results` finds no instruction that still uses the flag.
