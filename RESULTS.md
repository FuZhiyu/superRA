# Theory-Modeling Vertical — Results

> Mirrors `PLAN.md` structure. Updated after each task with key findings.
> New agents: read `PLAN.md` for what to do, `RESULTS.md` for what was found.

**Last updated:** 2026-04-22 (planning scaffold created)
**Status:** In Progress

---

## Task 1: Create the `theory-modeling` domain skill and its stage-scoped references

**Status:** Implemented (pending review)

### Key Findings
- Added `skills/theory-modeling/SKILL.md` with a proactive trigger surface, stage-scoped load table, an iron law centered on defined objects plus stated assumptions, and a shared `Define–Derive–Validate` checklist.
- The checklist makes notation discipline, interpretable primitive-level assumptions, stepwise derivations, and proof / special-case / numerical verification `[BLOCKING]` requirements.
- Added planning, drift-test, and integration references so the vertical has a complete PLAN / Phase A / Phase B path without inventing a new workflow or rendering utility.

### Notes
- The skill explicitly points human-facing equation/table/figure rendering back to `superRA:report-in-markdown`.
- The task is awaiting adversarial review; no reviewer findings have been incorporated yet.

## Task 2: Wire the new vertical into runtime surfaces, docs, and discovery

**Status:** Implemented (pending review)

### Key Findings
- Added `theory-modeling` to the `using-superRA` inventory and manifest, the `planning-workflow` routing table, and the `refactor-and-integrate` domain-specific integration pointers.
- Generalized the planning template and exit-plan-mode reminder so a second planning hard gate is first-class rather than a data-only exception.
- Updated contributor/runtime docs (`README.md`, `skills/CATEGORIES.md`, `CLAUDE.md`) to present theory/modeling as an implemented vertical, added `.agents/skills/theory-modeling`, and extended `tests/check-harness-compatibility.sh` with discovery/wiring assertions.

### Notes
- The compatibility suite and targeted smoke checks are being treated as Task 3 verification rather than as Task 2 completion criteria.
- The task is awaiting adversarial review; no reviewer findings have been incorporated yet.

## Task 3: Verify the new vertical end to end and reconcile any drift

**Status:** Not started
