---
title: "Delete Residual Prose-Layout Oracles"
status: not-started
depends_on:  []
---

## Objective

Delete the superplan phase-heading/subheading/list-count layout tests while preserving reference routing/existence checks, and remove the exact report-in-markdown remediation-message assertion while retaining rule ID, issue count, and line evidence. Success: no residual prose-layout or remediation-copy oracle remains in these files and targeted tests pass.

## Planner Guidance

Own tests/harness-instruction-following/test_contract.py prose-layout block and skills/report-in-markdown/scripts/test_md_integrity.py exact message assertion only.

## Results
