---
title: "result-protection"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

An agent does a clean refactor of the code behind your headline coefficient — renames a column, fixes a join, re-runs on a refreshed extract. The diff compiles, every existing test passes, and the coefficient quietly slides from 0.42 to 0.31. None of those tests looked at the number. A bare agent has no reason to guard a result it was never told mattered, so the change lands and the first person to notice is a referee.

`result-protection` pins the specific outputs your paper depends on in drift tests, so a silent number change becomes a red test in the same run that caused it. A drift test reads the protected value from a saved output and checks it against a known-good value within a documented tolerance (scaled by domain reasoning — the band for a basis-point spread is not the band for a t-statistic). It does not re-run your pipeline, so the suite stays fast.

You normally meet the skill at the Protect step of integration: run `superintegrate` or say "protect the key results", and it walks your task tree, proposes the candidate findings from each task's `## Results`, and asks you to confirm which carry your conclusions before writing a test for each. Standalone, point it at one result — "pin the spread in `analysis/term-structure` and guard it, tolerance 1 bp" or "review the drift tests in `test/` against the current key results".

Once a test exists it is part of the results contract: every later integration pass runs it, and a failure is never waved through. If the result genuinely moved, that is a research decision you fold into the task before updating the expectation — editing an expectation only to turn a red test green is the failure this guards against.

The red-green verification, scope gate, tolerance discipline, and full gated checklist live in [`result-protection`](skills/result-protection/SKILL.md).
