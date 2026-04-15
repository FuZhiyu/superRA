# superRA Plugin Restructure Plan

> **For agentic workers:** this is a PLUGIN META-REFACTOR — the "analysis" is the superRA plugin itself, not a data analysis. The domain skill `superRA:econ-data-analysis` applies only when tasks touch data-analysis content; most tasks here are skill-file rewrites. Use `superRA:execution-workflow` to coordinate. Steps use checkbox (`- [ ]`) syntax.

**Objective:** Make `execution-workflow` domain-agnostic; share the gating/review checklist between implementer (self-check) and reviewer (verification) by keeping it inline in `econ-data-analysis/SKILL.md` main body; standardize dispatch-prompt language across all workflow skills so the prompt carries only steering on top of the agent's standard protocol.

**Methodology:** Phased commits on `refactor/workflow-domain-split`. Each commit leaves repo in a working state (structural-invariants green). PR #1 updates on push.

**Data Inventory:** N/A — plugin meta-refactor. No datasets.

**Output:** Rewritten skill / agent / workflow files. Updated `tests/structural-invariants.sh`. New `RELEASE-NOTES.md` entry.

**Pipeline:** `bash tests/structural-invariants.sh`.

**Background plan document:** `/Users/zhiyufu/.claude/plans/agile-orbiting-star.md` carries the full design rationale. This PLAN.md is the task-tracker.

---

## Decisions

> **User decision (2026-04-15):** default to one comprehensive review pass per task; reviewer walks the full checklist even on gating failure and returns `CONDITIONAL APPROVE` (gating items must be fixed; downstream verified and contingent on gating fix not invalidating). Rationale: reviewer dispatches are costly; re-review on gating fix becomes narrow (verify the fix + downstream still holds).

> **User decision (2026-04-15):** shared gating lives in `econ-data-analysis/SKILL.md` main body, NOT as separate `implementation-review.md` / `integration-review.md` references. Single source of truth; no possibility of divergence between what implementer self-checks and what reviewer verifies.

> **User decision (2026-04-15):** dispatch prompts use the prefix "Follow the standard stage-relevant workflow and load relevant skills and documents to proceed. Additionally, …" so agents always treat the standard workflow (from agent files) as in effect, and the dispatch prompt is ADDITIONAL steering on top. Same protocol applies across every workflow skill that dispatches agents.

---

## Task 1: Standardize Dispatch-Prompt Protocol Across All Workflow Skills

**Review status:** IMPLEMENTED

**Objective:** Rewrite every dispatch template in the plugin so it opens with the language

> "Follow the standard stage-relevant workflow and load relevant skills and documents to proceed. Additionally, ..."

The `Additionally, ...` tail carries only steering — focus areas, prior-round adjudication, warnings, non-default skill/reference overrides. The dispatch prompt NEVER repeats (a) the standard protocol that lives in `agents/implementer.md` / `agents/reviewer.md`, (b) PLAN.md task content (the agent reads it), or (c) domain-skill checklist content (the agent walks it per their Before-You-Start).

**Files the dispatcher touches:**

- `skills/execution-workflow/SKILL.md` — per-task implementer + reviewer dispatch templates (currently in §"Dispatch Templates" around L150-L200).
- `skills/integration-workflow/SKILL.md` — Stage 1 drift-test-creator + drift-test-reviewer dispatches; Stage 2 integration-reviewer + refactorer dispatches; Step 3 doc-writer + doc-reviewer dispatches.
- `skills/merge-workflow/SKILL.md` — any dispatch templates.
- `skills/semantic-merge/SKILL.md` — Tier 2 merge-proposer + merge-reviewer dispatches; Tier 3 same.
- `skills/agent-orchestration/SKILL.md` — team-recipe dispatch patterns.

**Steps:**

- [x] **Step 1: Describe — audit every dispatch template in the plugin.** Grepped `Agent(subagent_type:` across `skills/`. Found 16 dispatch templates across 5 files: `execution-workflow/SKILL.md` (3), `integration-workflow/SKILL.md` (6), `merge-workflow/SKILL.md` (2), `semantic-merge/SKILL.md` (3), `refactor-and-integrate/SKILL.md` (2 illustrative). Legacy over-specification observed: `Work from:` + `Counterpart:` in `execution-workflow`'s three primary templates; free-form `Note:` fields in `merge-workflow` post-merge reviewer + post-merge refactorer and in `semantic-merge` Tier 3. `using-superRA/references/codex-tools.md` contains one mention inside a harness-mapping table (prose context, not a dispatch template) — left alone.

- [x] **Step 2: Analyze — rewrite each template to the new canonical shape.** Template form:

  ```
  Agent(subagent_type: "superRA:<implementer|reviewer>"):
    # --- REQUIRED FIELDS FIRST (dispatch cannot function without them) ---
    Stage: <stage-name>
    Task: <PLAN.md pointer or git range>
    [Git range: <BASE>..<HEAD>]     # for review stages
    [Skills: <extras>]              # only if non-default
    [References: <extras>]          # only if non-default
    # --- THEN the standard-workflow anchor + optional steering ---
    Additionally: Follow the standard stage-relevant workflow and load
      relevant skills and documents to proceed. Additionally,
      <optional one-or-two-sentence steering — focus area, prior-round
      adjudication, warning, anything non-default>.
  ```

  **Ordering rule (non-negotiable):** required identifying information (Stage, Task, Git range, Skills/References overrides) comes **first** — the agent needs it to load the right context. The `Additionally:` block comes **last** — it anchors "standard workflow is in effect" plus any free-form steering on top. Do NOT invert the order (Additionally-block on top, required fields below) — that buries required information after prose and invites the agent to miss it.

  - Drop `Work from:` lines (subagent runs in cwd by default).
  - Drop `Counterpart:` lines outside explicit Agent Teams subsections.
  - Drop any preamble that restates standard protocol, PLAN.md content, or checklist items the agent already reads.
  - The prefix "Follow the standard stage-relevant workflow..." is literal and common across every template. This is the anchor that tells the agent: your standard Before-You-Start + stage-reference-auto-load is in effect; what follows is additions on top.

- [x] **Step 3: Validate — verify and commit.**
  - Grep: no dispatch template in `skills/` is missing the "Follow the standard stage-relevant workflow..." prefix.
  - Grep: no dispatch template retains `Work from:` (outside explicit worktree-setup prose) or `Counterpart:` (outside Agent Teams subsections).
  - `bash tests/structural-invariants.sh` passes.
  - Add one new assertion to `structural-invariants.sh`: every dispatch template in the live surface contains "Follow the standard stage-relevant workflow" (use a grep count >= N where N = number of templates).
  - Update RELEASE-NOTES.md top entry to note the dispatch-protocol standardization.
  - Atomic commit: `refactor(dispatch): standardize dispatch-prompt prefix across all workflow skills`.

**Out of scope for this task (will be handled in follow-on tasks):**

- The execution-workflow domain-agnosticism restructure (one-pass review, Step 3 parametric, completion menu generic).
- Integrating §Review & Self-Check Discipline into `econ-data-analysis/SKILL.md` main body.
- Agent-file Stage table updates.

Those tasks depend on this task landing first (so the subsequent restructure builds on the new dispatch protocol), and are tracked in the background plan document.
