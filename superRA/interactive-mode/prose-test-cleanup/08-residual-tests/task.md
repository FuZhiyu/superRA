---
title: "Delete Residual Prose-Layout Oracles"
status: implemented
depends_on:  []
---

## Objective

Delete the superplan phase-heading/subheading/list-count layout tests while preserving reference routing/existence checks, and remove the exact report-in-markdown remediation-message assertion while retaining rule ID, issue count, and line evidence. Success: no residual prose-layout or remediation-copy oracle remains in these files and targeted tests pass.

## Planner Guidance

Own tests/harness-instruction-following/test_contract.py prose-layout block and skills/report-in-markdown/scripts/test_md_integrity.py exact message assertion only.

## Results

Deleted the phase-heading count, Phase 4 subheading count, and ordered-list run-length assertions from [test_contract.py:232-241](../../../../tests/harness-instruction-following/test_contract.py#L232-L241). These assertions observed only authored Markdown layout; the retained contract still parses the routed reference paths, requires both intended references, and verifies that every routed file exists.

Deleted the exact remediation-message assertion from [test_md_integrity.py:54-59](../../../../skills/report-in-markdown/scripts/test_md_integrity.py#L54-L59). The parameterized test still verifies every configured TeX-only macro produces exactly one `tex-only-macro` issue on line 1.

Deletion evidence: a static sweep found none of the removed phase/subheading/list-run helpers or `Issue.message` assertions in the two owned files. Verification: `uv run --with pytest python -m pytest tests/harness-instruction-following/test_contract.py skills/report-in-markdown/scripts/test_md_integrity.py -q` completed with 41 passed; pytest emitted one non-test-failure warning because its cache directory was not writable.
