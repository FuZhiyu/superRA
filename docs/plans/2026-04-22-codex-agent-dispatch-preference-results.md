---
author: "Julie Zhiyu Fu"
date: 2026-04-22
timestamp: "2026-04-23T00:52:17"
session_id: "session-20260422-195217"
git_commit: "baa8a33e429a02a5de37668d07830a8fad03b016"
git_message: "remove the harness pointer for claude"
git_dirty: true
tags: ["results", "integration"]
project: "superRA"
permalink: "docs/plans/2026-04-22-codex-agent-dispatch-preference-results"
---

# Codex Agent Dispatch Preference — Results

This branch finalized the Codex-specific orchestration instructions for
superRA so a Codex agent treats user-invoked superRA workflow as
explicit authorization for named-agent dispatch, keeps reviewer
dispatch mandatory by default, uses concrete Codex tool names in the
adapter map, and loads the Codex adapter from `using-superra`
explicitly. The permanent plan companion is
[2026-04-22-codex-agent-dispatch-preference-plan.md](./2026-04-22-codex-agent-dispatch-preference-plan.md).

## Permanent Artifacts

- The Codex-specific adapter surface now lives at
  [../../skills/using-superra/references/codex-instructions.md](../../skills/using-superra/references/codex-instructions.md).
- The shared master-skill load rule lives at
  [../../skills/using-superra/SKILL.md](../../skills/using-superra/SKILL.md).
- Contributor guidance for harness adapter ownership lives at
  [../../CLAUDE.md](../../CLAUDE.md).
- The compatibility gate for this branch lives at
  [../../tests/check-harness-compatibility.sh](../../tests/check-harness-compatibility.sh).

## Implementation

- The Codex adapter reference is now
  [../../skills/using-superra/references/codex-instructions.md](../../skills/using-superra/references/codex-instructions.md),
  which carries the Codex-only dispatch override, warm-agent lifecycle
  guidance, named-agent setup notes, and the concrete Codex tool map
  for `request_user_input`, `update_plan`,
  `spawn_agent(agent_type="superra_implementer"|"superra_reviewer")`,
  and `send_input`.
- The shared master skill now states that Codex agents load
  [../../skills/using-superra/references/codex-instructions.md](../../skills/using-superra/references/codex-instructions.md)
  immediately after
  [../../skills/using-superra/SKILL.md](../../skills/using-superra/SKILL.md)
  loads `superRA:using-superra`; the final follow-up on this branch
  also removed the extra Claude-only harness pointer from that sentence.
- Contributor guidance in
  [../../CLAUDE.md](../../CLAUDE.md) now points maintainers at the
  owning harness adapter reference under `skills/using-superra/references/`
  instead of hardcoding the older `<harness>-tools.md` naming pattern.
- The branch validation script
  [../../tests/check-harness-compatibility.sh](../../tests/check-harness-compatibility.sh)
  now checks for `codex-instructions.md` and the generated Codex agent
  files.

## Validation

- The integration validation entrypoint for this branch is
  `bash tests/check-harness-compatibility.sh`; the executable check is
  [../../tests/check-harness-compatibility.sh](../../tests/check-harness-compatibility.sh).
- Draft PR [#19](https://github.com/FuZhiyu/superRA/pull/19) is open
  against `main`.

## Scope Notes

- No drift-test suite was added for this branch; that omission was an
  explicit user decision recorded in the companion
  [2026-04-22-codex-agent-dispatch-preference-plan.md](./2026-04-22-codex-agent-dispatch-preference-plan.md).
- No root `results_attachments/` directory existed on this branch, so
  Phase C did not need a figure-materialization pass.
- A post-archive follow-up identified a remaining direct-mode
  accessibility gap: the main agent still relied on raw
  `agents/implementer.md` / `agents/reviewer.md` in direct mode. That
  follow-up ultimately matured into
  [2026-04-22-direct-mode-role-references-plan.md](./2026-04-22-direct-mode-role-references-plan.md)
  and
  [2026-04-22-direct-mode-role-references-results.md](./2026-04-22-direct-mode-role-references-results.md)
  and is outside the scope of this permanent record.

## Reproducibility

Reproduce the integration check from the repository root by running
`bash tests/check-harness-compatibility.sh` on this branch. The
pre-Phase-C branch head for this permanent record was
`baa8a33e429a02a5de37668d07830a8fad03b016`
(`remove the harness pointer for claude`).
