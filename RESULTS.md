# Codex Agent Dispatch Preference — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-22 (Task 1 / PR polish)
**Status:** Completed

---

## Task 1: Update the Codex instructions surface for dispatch, warm-agent lifecycle, and load semantics

**Status:** Completed (Task 1 integration follow-up approved 2026-04-22)

### Key Findings
- `skills/using-superRA/references/codex-instructions.md` now tells
  Codex to treat user-invoked superRA workflow/orchestration as
  explicit authorization for named-agent dispatch.
- The Codex adapter now states that reviewer dispatch remains mandatory
  by default and that direct mode is only a fallback when the user opts
  out, the task is trivial, or agent tools are unavailable.
- The Codex adapter now also says that long-running warm agents are
  normal, should not be shut down eagerly, and can be contacted with
  warm-agent messaging when the orchestrator needs to steer a running
  subagent.
- `skills/using-superRA/SKILL.md` now explicitly tells Codex agents to
  load `references/codex-instructions.md` whenever they load the master
  skill, so the Codex instructions surface is no longer only implied by
  the harness-adapter note.
- The Codex action map now uses concrete Codex tool names instead of
  abstract placeholders: `request_user_input`, `update_plan`,
  `spawn_agent(...)`, and `send_input`.

### Notes
- Existing shared workflow files already carried the general
  implementer-reviewer and direct-mode rules, so no adjacent
  consistency rewrites were needed beyond one root-doc audit fix in
  `CLAUDE.md`, which now points contributors at the current adapter
  reference pattern and names `codex-instructions.md` explicitly.
- Draft PR [#19](https://github.com/FuZhiyu/superRA/pull/19) is open
  against `main` from `analysis/codex-agent-dispatch-preference`.
- The local wording pass briefly softened the explicit Codex load rule
  and dropped `codex-superra-setup` from the `using-superRA` inventory;
  both were restored in the polish edit.
