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

Verify live, in both harnesses, that **both** always-loaded skills load on a real role dispatch before any task-file or code edit: `using-superra` **and** `report-in-markdown` (contract LC001 in [load_contract.json](../../../../../tests/harness-instruction-following/load_contract.json)). The manifest claims both are always loaded; nothing in the suite currently proves `report-in-markdown` loads at all, which is the specific gap this task closes.

Deliverables:

- A fixture role dispatch (reuse `bundle-two-tasks` shape) and assertions that, for each harness, evidence both always-loaded skills:
  - **Claude** via the 08 SDK harness — `report-in-markdown` may surface through `InstructionsLoaded` or a `Skill` tool_use; if neither fires, fall back to a canary the `report-in-markdown` body prescribes.
  - **Codex** via the 09 canary convention — a fixture output value producible only by following a `report-in-markdown` rule (e.g. its file-link/citation or figure/table format) and a `using-superra` behavior.
- Both checks assert the skills are evidenced **before** the first edit/write.

Success criteria: both always-loaded skills are evidenced loaded in both harnesses on the dispatched role turn; the red case (a required always-loaded skill not evidenced) fails.

### Constraints

- Manual-only; consume the 08/09 harnesses, do not re-implement evidence capture.
- **A failing result is a real finding, not a test bug.** If `report-in-markdown` does not load, record it in `## Results` as a loading-contract gap and escalate to the orchestrator (it likely needs a hook/manifest fix), rather than relaxing the assertion.

## Planner Guidance

`report-in-markdown` is the high-risk skill — design its proof first and make the canary depend on a rule only that skill defines (a structural "was-applied" proxy is stronger than a bare presence token). For `using-superra`, the existing task-read behavior already implies its load, but assert it by name via the SDK hook where possible.
