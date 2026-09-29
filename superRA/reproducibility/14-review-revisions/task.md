---
title: "Design-Review Revisions: Resolve the 2026-09-28 Findings Before 0.5 Ships"
status: revise
depends_on: []
---

## Objective

Resolve the findings of the 2026-09-28 comprehensive design review so 0.5 ships without a false `fresh`, works on a Dropbox-synced multi-machine project with coauthor branches, gates readiness by one explainable rule, and gives agents instructions that pass the CLAUDE.md gate. The [review summary](attachments/review-2026-09-28.md) ranks the findings; each subtask owns one topic and one edit surface.

### Constraints

- **Reproduce before fixing.** Each finding gets a regression test or scripted fixture that fails first. A finding the evidence marks *inferred* is confirmed first; one that does not reproduce is recorded in `## Results`, not fixed.
- **Researcher decisions come first.** A subtask's `### Researcher decisions` are settled with the researcher before that part is implemented; the recommendation is a proposal. A decision that revises the [0.5 design](../attachments/v05-design.md) updates that design in the same commit.
- **Fold back at integration.** Each subtask names its owning tasks; its validated result moves into their `## Results` and this group is removed.

## Details

Evidence behind the summary, with file:line and reproduction steps (scratch fixture paths in them were session-local and are gone):

- [gate-audit.md](attachments/gate-audit.md) — line-by-line CLAUDE.md gate audit of the skill, the task-file contract, and `commands.md`
- [wiring.md](attachments/wiring.md) — workflow and role call sites, three agent scenarios, stale tree content
- [deps-report.md](attachments/deps-report.md) — effective dependencies, readiness, and the edit hook

The engine and dashboard reviews returned inline; their evidence is in the Details of 01, 02, 05, and 06.

Suggested order: 01 goes first; it replaces the engine and settles `repro-lock.json`, which 02 builds on. 03 and 04 are independent code fixes. 05 follows 02 (record formats) and 06 follows 03 (snapshot payload). 07 rewrites the instructions once the mechanics settle, 08 rewires the call sites on 07's terms, and 09 closes the upgrade path and the records.

High stakes: 01 (engine replacement and false `fresh`) and 03 (readiness and validity) warrant a thorough independent review with a correctness focus.
