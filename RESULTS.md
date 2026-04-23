# Direct-Mode Role References — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-22 (implementation)
**Status:** In Progress

---

## Task 1: Add skill-owned direct-mode role references and wire main-agent direct mode to them

**Status:** Implemented

- Chose a narrow manual-copy boundary: the mirrored files carry the
  direct-mode role protocol the main agent actually needs in-session
  (stage loads, pre-start checks, self-review / review behavior,
  handoff ownership, commit discipline, escalation), while leaving
  dispatch-only framing, worktree-return protocol, and orchestrator
  report format in the canonical agent files.
- Added
  `skills/using-superRA/references/direct-mode-implementer.md` and
  `skills/using-superRA/references/direct-mode-reviewer.md`, each with
  an explicit manual-mirror note pointing back to
  `agents/implementer.md` or `agents/reviewer.md` as the canonical
  source.
- Rewired `skills/using-superRA/references/main-agent.md` so direct mode
  now loads the skill-owned references instead of depending on raw
  `agents/*.md`.
- Validation: `bash tests/check-harness-compatibility.sh` passed after
  the change, including the new direct-mode role-mirror assertions.

## Task 2: Document and validate the temporary manual-mirror approach

**Status:** Implemented

- Added contributor guidance in `CLAUDE.md` that direct mode must load
  the skill-owned role mirrors and that any direct-mode-relevant change
  to the canonical agent files must update the mirrors in the same
  change until automation exists.
- Extended `tests/check-harness-compatibility.sh` to require the new
  direct-mode reference files, ensure `main-agent.md` points at them,
  reject regressions back to raw `agents/*.md`, and require each mirror
  to declare its canonical source plus temporary-manual-mirror status.
- The archived 2026-04-22 plan/results pair already points at this
  follow-up plan/results from commit `cc4ea46`, so no further archive
  edit was needed in this implementation pass.
- `.agents/skills/` remains in place. Repo docs and the compatibility
  check treat it as the repo-local Codex skill-discovery surface rather
  than a stray generated agent artifact, so this pass intentionally does
  not delete it.
