---
title: "Per-Stage Skill Loads Live Coverage"
status: not-started
depends_on:
  - 08-claude-sdk-load-harness
  - 09-codex-canary-and-dispatch-hook
tags: []
created: 2026-06-19
---

## Objective

Verify live, in both harnesses, that each non-empty workflow stage loads the skill/reference the Skill-Load Manifest assigns it before stage action (contracts LC002, LC007–LC010):

- `planning-review` → `skills/superplan/references/planning-review.md`
- `protection` → `result-protection`
- `sync` → `semantic-merge`
- `integration` → `refactor-and-integrate`

Also assert the negative: `implementation` and `documentation` carry **no** extra stage-skill expectation.

Deliverables:

- A parametrized set of stage fixtures (a minimal dispatch per stage carrying `Stage: <name>`), each with an assertion that the stage's required skill/reference is evidenced loaded — Claude via the 08 SDK skill-load hook, Codex via the 09 canary — before the stage's first action.
- The two negative cases (implementation/documentation) asserting no stage-skill load is required.

Success criteria: each of the four stages evidences its manifest skill/reference loaded on its triggering dispatch in both harnesses; the negative cases hold; a red case (stage skill not loaded) fails.

### Constraints

- Manual-only; consume the 08/09 harnesses.
- Keep each stage fixture minimal — the test target is the stage→skill load, not stage work quality. Per the audit's SF002, assert `protection` from the manifest, not older `drift-test` wording.

## Planner Guidance

Parametrize over a `{stage, expected_skill}` table so adding a future stage is a one-row change. `planning-review` loads a reference *file*, the others load *skills* — the assertion helper should accept either a skill name or a reference path as the expected evidence. Reuse one fixture body across stages where only the dispatch `Stage:` line differs.
