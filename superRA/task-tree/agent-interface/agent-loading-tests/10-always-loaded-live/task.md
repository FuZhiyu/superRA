---
title: "Always-Loaded Skills Live Coverage"
status: not-started
depends_on:
  - 08-claude-sdk-load-harness
  - 09-codex-canary-and-dispatch-hook
tags: []
created: 2026-06-19
---

## Objective

Verify live, in both harnesses, that **both** always-loaded skills are in the dispatched role's context before any task-file or code edit: `using-superra` **and** `report-in-markdown` (contract LC001 in [load_contract.json](../../../../../tests/harness-instruction-following/load_contract.json)), and regression-guard that contract.

What is already established (do not re-litigate; build the regression guard): in **Claude**, both skills are **autoloaded** via the agents' frontmatter `skills: [...]` — orchestrator-confirmed live, a dispatched `superRA:implementer` recited `report-in-markdown`'s file-citation rule with zero `Skill`-tool loads. In **Codex** there is no autoload, so the [role-spec-always-load](../../role-spec-always-load/task.md) body instruction is what loads them. This task turns those one-off confirmations into committed checks.

Deliverables:

- A fixture role dispatch (reuse `bundle-two-tasks` shape) and assertions that, for each harness, evidence both always-loaded skills:
  - **Claude** — autoloaded skills are invisible to the `Skill` hook by construction (zero `Skill`-tool loads is the expected, correct signal — not a failure). Evidence them two ways: (1) the 08 **static frontmatter contract** check (both `agents/implementer.md` and `agents/reviewer.md` declare both skills), and (2) a **live discriminating canary** via the 08 harness dispatching the real `superRA:implementer`. The canary must use a rule the base model would NOT follow unprompted — the bare file-link-with-anchor format is too close to a model default to discriminate. The orchestrator's working probe was an **introspection prompt**: ask the dispatched implementer to state its markdown file-citation rule *without loading any skill or reading any file*; a context-grounded recital of `report-in-markdown`'s rule (with zero `Skill` loads) proves autoload. Prefer that, or pick a more arbitrary skill-unique rule.
  - **Codex** via the 09 canary convention — a fixture output value producible only by following a `report-in-markdown` rule and a `using-superra` behavior; this is what exercises the role-spec body-load path that substitutes for Claude's autoload.
- The discriminating canary asserts the skill's rule reached context; the static check asserts the declared contract.

Success criteria: both always-loaded skills are evidenced loaded in both harnesses on the dispatched role turn; the red case (a required always-loaded skill not evidenced) fails.

### Constraints

- Manual-only; consume the 08/09 harnesses, do not re-implement evidence capture.
- **A failing result is a real finding, not a test bug.** If `report-in-markdown` does not load, record it in `## Results` as a loading-contract gap and escalate to the orchestrator (it likely needs a hook/manifest fix), rather than relaxing the assertion.

## Planner Guidance

Design the discriminating canary first — a rule only `report-in-markdown` defines that the base model would not produce unprompted; the introspection probe above is the proven approach. A bare presence token or a model-default format is not evidence.

The live SDK dispatch is mildly nondeterministic (it leans on the top-level model to issue the Task dispatch): use the cheapest model that dispatches reliably (sonnet did; haiku was flaky) and assert across a small retry / pass@k window, not a single shot. The deterministic backbone is the static frontmatter contract; the live canary corroborates. A genuine failure (skill's rule absent from a reliable dispatch) is a real loading-contract finding to escalate, not an assertion to relax.
