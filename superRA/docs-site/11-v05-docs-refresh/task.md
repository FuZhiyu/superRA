---
title: "v0.5 Docs: Explain Reproduction and Refresh Stale Pages"
status: implemented
depends_on: []
---

## Objective

Bring the public docs up to the 0.5.0 release: teach how reproduction works, show it on the showcase study, and fix every page that still describes pre-0.5 behavior.

- **Reproduction is taught as mechanics, not as a pipeline concept.** Readers already understand a DAG of scripts. What they need is how superRA decides a result is still current, what runs when, and what stays under their control. No make/pytask or spreadsheet analogy.
- **The showcase study demonstrates it** through a real registered graph, so the Quickstart and the reproducibility page point at a live export instead of a made-up pipeline.
- **The release ships after this task.** Once approved, [tmp-v05-integrate-refactor](../../tmp-v05-integrate-refactor/task.md) runs against a protected record that includes the new pages and the showcase graph, then Finish ships 0.5.0.

### Conventions

- Every page follows the docs-tree authoring contract in the HTML comment of [docs/site/task.md](../../../docs/site/task.md) and the parent's agent-first, concise, no-AI-prose gates.
- Pages link to [skills/reproducibility/SKILL.md](../../../skills/reproducibility/SKILL.md), [task-file-contract.md §Reproduction Section](../../../skills/task-tree/references/task-file-contract.md#reproduction-section), and [commands.md](../../../skills/task-tree/references/commands.md#reproduction) as the authority; they never restate flag lists or the stale-rule table.
- `docs/build_site.sh` exits 0 and `superra task check` is clean on `docs/site` after each child lands.

## Details

- The frozen showcase fixtures under `docs/showcase-fixtures/` stay untouched; only the live `superRA/showcase-analysis` tree and its `showcase-analysis-tree.html` export change.
- High-stakes for accuracy: a page that misstates when a step is `fresh` or what `build` runs teaches researchers to trust a stale result. Suggested review: standard tier, focuses *accuracy against the repro code and contract* and *docs-site gates*, over 02 and 03 together.
