---
title: "Teach Agents to Act on Provenance, and Verify They Do"
status: not-started
depends_on:
  - 01-provenance-explain
  - 02-build-record
---

## Objective

Agents resolve a stale step from `explain` output alone, and the claim is verified in a real harness session.

- **Skill.** [diagnosing.md §Read what explain names](../../../../skills/reproducibility/references/diagnosing.md#read-what-explain-names) becomes one table mapping each cause from [01](../01-provenance-explain/task.md) to the action it calls for; `rerun-or-accept.md` points there rather than restating it. Edits pass the [CLAUDE.md §Teach the Protocol gate](../../../../CLAUDE.md#teach-the-protocol-dont-prescribe-each-action).
- **Validation:** a fresh subagent given only "these steps are stale; decide what to do" on the 01 fixture reaches the correct diagnosis for every step in at most three `repro` calls, runs no manual `git log -S`, `shasum`, or `stat`, and does not accept the sync-lag steps. Record the transcript's call count against the ~20-call baseline in `## Results`.

## Details

- The current table in `diagnosing.md` names symptoms ("an out you did not edit") and investigation steps that the resolver now performs; most rows shrink to an action.
- Load `skill-creator` and `superRA:reproducibility` before editing.
