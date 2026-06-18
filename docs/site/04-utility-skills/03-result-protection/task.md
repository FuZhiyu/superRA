---
title: "result-protection"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Three weeks after you run the regression behind your headline coefficient, an agent does a clean refactor: renames a column, fixes a join, re-runs on a refreshed extract. The diff compiles, every existing test passes, and the coefficient quietly slides from 0.42 to 0.31. None of those tests looked at the number. The change lands, and the first person to notice is a referee — or you, six months later, unable to reconstruct which commit moved it.

A bare agent has no reason to guard a number it was never told mattered. It optimizes the change in front of it; your key results are invisible to it unless something asserts them. `result-protection` makes the assertion. It pins the specific outputs your paper depends on in drift tests that fail the moment a refactor, branch sync, or maintenance edit moves them, so a silent number change becomes a red test in the same run that caused it.

A drift test here is a regression test that loads a saved output and checks the protected number against its known-good value within a stated tolerance. It does not re-run your pipeline — it reads the value from a saved file or results artifact, so the suite stays fast and a broken upstream stage shows up as a clear failure rather than a crash. Comparisons use a tolerance function, never exact equality, and every tolerance is scaled by domain reasoning and documented with a one-line justification (the band that fits a basis-point spread is not the band that fits a t-statistic). You protect the findings that define your conclusions, not every intermediate merge count.

You normally meet the skill at the Protect step of integration. Run `superintegrate` (or say "protect the key results"), and it walks your task tree, pulls candidate findings from each task's `## Results`, and stops to confirm which ones matter:

```text
These results seem like the key findings to protect:
- [result 1: description and value] (from task-path/subtask)
- [result 2: description and value] (from task-path/subtask)

Which should be protected? Any to add or remove?
```

You answer with the results that carry your conclusions. The skill then writes a test for each confirmed result and verifies it with a red-green cycle before committing: write the test and run it green against the current correct value; perturb the saved value or an input so it goes red; restore and confirm green again. A test that has only ever passed has never shown it can catch the drift it exists to catch — the red step is the proof.

You can also invoke it standalone, outside a full integration pass. Load the skill and point it at a result to pin: "create a drift test for the spread in `analysis/term-structure`, tolerance 1 bp" or "review the drift tests in `test/` against the current key results." Either path runs the same red-green verification and the same gated checklist (a test for every confirmed key result, a documented tolerance, loads from saved outputs).

Once the tests exist they are part of the results contract, not disposable scaffolding. Every later integration pass runs the full suite, and a failure is never silently waved through. It means one of three things: the change broke something and you fix it; the tolerance was too tight and you widen it with a documented reason; or the result genuinely moved, which is a research decision you fold into the relevant task before updating the expectation. Refreshing an expectation because the science changed is allowed; editing it to turn a red test green is the exact failure the skill exists to stop.

The full gated checklist, the scope gate, and the cross-cutting red flags live in [`result-protection`](skills/result-protection/SKILL.md).
