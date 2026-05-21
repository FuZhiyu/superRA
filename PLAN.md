# Codex Hooks Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. This is superRA plugin-engineering work on hooks, manifests, docs, and tests; no data-analysis or theory-modeling domain gate applies. Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff.

**Objective:** Ship reliable Codex lifecycle hook support for superRA without breaking the existing Claude Code hook surface.

**Methodology:** Add a Codex-specific hook manifest and only install hooks backed by documented Codex event surfaces. Keep Claude-only `Skill` gates out of the Codex hook manifest. Use a Codex `Stop` hook in plan mode as the replacement for Claude Code's `ExitPlanMode` hook.

**Output:** Updated Codex plugin manifest, Codex hook manifest, Codex plan-stop hook, shared hook script adjustments, version bump, documentation updates, and focused hook/harness tests.

**Expected Results / Hypotheses:** Codex users can enable/trust the superRA plugin hooks and receive autoload, merge-guard, decision-log, and plan-materialization reminders through Codex-native events.

**Sensitivity Analysis:** Verify both Codex-shaped synthetic hook payloads and existing Claude hook unit tests so the new Codex support does not regress current Claude behavior.

**Pipeline:** Targeted shell tests listed in Task 1 plus optional live Codex CLI smoke test.

---

## Workflow Status

- [x] **Plan approved** - researcher asked to run the superRA workflow retroactively after the implementation was completed.
- [x] **Execution complete** - Task 1 implemented and reviewed; targeted verification re-run.
- [x] **Drift tests created** - Not applicable for plugin hook packaging; targeted hook regression tests substitute for drift tests.
- [ ] **Integrated** - Not requested in this retroactive run.
- [x] **Docs finalized** - README and Codex docs updated for the hook support shipped here.
- [ ] **Finished** - Not requested in this retroactive run.

---

## Project Conventions

Walked at planning time (2026-05-21). Re-walk on-demand only.

### Repo root
- [CLAUDE.md](CLAUDE.md) (HEAD at 08b68c8): Contributor guidance is the source for superRA internals. Treat changes to skills, hooks, agents, harness adapters, and internal docs as skill creation. Read owning files before editing, keep changes focused, verify behavior, keep Codex harness differences in adapters or Codex packaging surfaces, and do not hand-edit generated Codex named-agent artifacts.
- [AGENTS.md](AGENTS.md): Symlink to [CLAUDE.md](CLAUDE.md).
- [README.md](README.md) (HEAD at 08b68c8): User-facing overview and install instructions. Hook support and Codex setup copy must stay aligned with runtime packaging.

### Module-level docs walked
- [docs/README.codex.md](docs/README.codex.md) (HEAD at 08b68c8): Codex-specific install and verification guide. Update when Codex plugin packaging or named-agent setup changes.
- [skills/using-superRA/references/codex-instructions.md](skills/using-superRA/references/codex-instructions.md) (HEAD at 08b68c8): Codex adapter for superRA workflow behavior and tool-name mappings. It confirms named agents remain separate from plugin packaging.
- [skills/handoff-doc/SKILL.md](skills/handoff-doc/SKILL.md) (HEAD at 08b68c8): Handoff docs must be latest-state-only, inline edited, and used as the durable record.
- [skills/report-in-markdown/SKILL.md](skills/report-in-markdown/SKILL.md) (HEAD at 08b68c8): Markdown file references should use markdown links with line anchors.

### Not walked
- Historical `docs/plans/` archives, old worktrees under `.claude/worktrees/`, and unrelated domain-skill references are outside this packaging task.

## Decisions

> **User decision (2026-05-21):** Run the superRA workflow retroactively over the current Codex-hook implementation.
> **Question asked:** User said "run it" after confirming the first implementation did not fully follow the superRA workflow.

> **User decision (2026-05-21):** Use `origin/main` as the integration base.
> **Question asked:** Confirm the integration base for this run.

> **User decision (2026-05-21):** Finish by opening a PR branch rather than pushing `main` directly.
> **Question asked:** After integration review passes, what final action should I prepare for?

---

### Task 1: Add Codex hook support
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** *(not started)*
**Sync status:** No-op against `origin/main`; `BASE_HEAD_SHA=08b68c85dd49c414e6c5811aa21c764c50b1988b` is already an ancestor of `HEAD`.
**Final diff self-check:** `git diff 08b68c85dd49c414e6c5811aa21c764c50b1988b..HEAD`; surviving change classes are Codex hook packaging, hook script behavior, docs, tests, version bump, and handoff docs. Suspicious hunks: version-managed manifest changes are justified by the public Codex plugin hook surface; no unrelated hunks.

**Script:** Hook scripts under `hooks/`; test scripts under `tests/hooks/`; packaging in [.codex-plugin/plugin.json](.codex-plugin/plugin.json).
**Input:** Existing Claude hook scripts/config, Codex hook documentation, current superRA Codex plugin manifest.
**Output:** [hooks/hooks-codex.json](hooks/hooks-codex.json), [hooks/codex-plan-stop](hooks/codex-plan-stop), shared hook updates, version bump, docs, and tests.

- [x] **Step 1: Package Codex hooks explicitly**

  Add `hooks` to [.codex-plugin/plugin.json](.codex-plugin/plugin.json) and create [hooks/hooks-codex.json](hooks/hooks-codex.json) so Codex does not accidentally load Claude-only hook registrations.

- [x] **Step 2: Map only reliable Codex events**

  Wire `UserPromptSubmit` to `autoload-superra`, `PreToolUse`/`Bash` to `merge-guard`, and `Stop` to `codex-plan-stop`. Leave Claude-only `Skill` gates and unverified `request_user_input` PostToolUse wiring out of the Codex manifest.

- [x] **Step 3: Adapt shared scripts for Codex**

  Update [hooks/autoload-superra](hooks/autoload-superra) to emit Codex-native skill-load wording when `PLUGIN_ROOT` is set. Update [hooks/ask-user-question-logger](hooks/ask-user-question-logger) to accept Codex `request_user_input` tool names.

- [x] **Step 4: Add Codex plan-mode replacement**

  Add [hooks/codex-plan-stop](hooks/codex-plan-stop), a Codex `Stop` hook that emits a continuation prompt only when `permission_mode` is `plan` and the last assistant message contains `<proposed_plan>`.

- [x] **Step 5: Update docs and compatibility checks**

  Update [README.md](README.md) and [docs/README.codex.md](docs/README.codex.md) with Codex hook support, `/hooks` trust review, plugin-hook feature guidance, and the Claude/Codex hook coverage split. Extend [tests/check-harness-compatibility.sh](tests/check-harness-compatibility.sh) to assert Codex hook packaging invariants.

- [x] **Step 6: Verify behavior**

  Add [tests/hooks/test-codex-hooks.sh](tests/hooks/test-codex-hooks.sh) for synthetic Codex payloads and [tests/hooks/test-codex-e2e-cli.sh](tests/hooks/test-codex-e2e-cli.sh) as an opt-in live Codex smoke test. Re-run targeted JSON, hook, and harness compatibility checks.
