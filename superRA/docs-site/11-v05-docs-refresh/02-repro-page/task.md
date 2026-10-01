---
title: "Reproducibility Docs Page: How superRA Knows a Result Is Current"
status: approved
depends_on: []
---

## Objective

Write `docs/site/04-utility-skills/09-reproducibility/task.md`, the docs home for reproduction, and point the utility-skills index at it instead of at `SKILL.md`.

The page answers three questions a researcher has after the first graph appears, each in mechanics they can predict:

1. **How freshness is decided.** A step's deps, definition (`cmd`, `params`), and outs are content-hashed and compared with the record from its last successful run in the committed `repro-lock.json`. Content, never timestamps: a Dropbox re-sync or `touch` changes nothing; any byte change, even a comment, makes the step stale; a rerun that regenerates identical bytes leaves downstream steps fresh. The lock is in git, so a coauthor's clone sees the same freshness.
2. **What runs, and when.** Nothing reruns on its own. `status` reports; `build <target>` runs only the selected steps that are not fresh; files written outside the selection are used as they sit on disk unless `--upstream` pulls in their producers; `--dry-run` and `impact` show the cost first. Selection by task, `task#step`, or `.`.
3. **What stays the researcher's call.** Accept records a reviewed result as fresh without rerunning, with a required reason, and never claims the step ran. The agent rebuilds cheap stale steps, accepts provably inert changes, and asks before a costly rerun — point to [rerun-or-accept.md](../../../../skills/reproducibility/references/rerun-or-accept.md) for the rule instead of restating it.

- **Lead with what to ask the agent** ("which results does this edit affect?", "rebuild the GRS table", "accept the panel, I checked it"), then the mechanics above, then the commands block last.
- **Show a stale cascade on the showcase graph** (from [01-showcase-graph](../01-showcase-graph/task.md) if it has landed, else its planned three steps): edit one script, which steps go stale, what `build` reruns.
- Define each state `status` prints (`fresh`, `stale`, `missing`, `failed`, `external`) in one line each.
- Every claim matches [task-file-contract.md §What invalidates a step](../../../../skills/task-tree/references/task-file-contract.md#what-invalidates-a-step) and the current CLI output; check each against a real run.

## Details

- The current index entry is in [docs/site/04-utility-skills/task.md](../../../../docs/site/04-utility-skills/task.md); its blurb ("declares producers and checks…") is internal vocabulary — rewrite it in the page's terms.
- Facts worth carrying that readers would not guess: a check that passed at the same inputs on another machine reads `fresh`; a conflicted lock still reads, dropping disputed entries to `missing`; a missing file only fails the build that reads it and never blocks planning.
- `## Reproduction` syntax belongs in a short example plus a link to the contract; the agent writes it, the researcher reads it.

## Results

The reproduction page is written at [docs/site/04-utility-skills/09-reproducibility/task.md](../../../../docs/site/04-utility-skills/09-reproducibility/task.md), and the utility-skills index entry in [docs/site/04-utility-skills/task.md](../../../../docs/site/04-utility-skills/task.md) now links to it with a blurb in the page's terms.

- **The showcase example matches the registered graph from [01-showcase-graph](../01-showcase-graph/task.md).** The diagram shows the committed raw CSVs as an external input feeding `build-panel` (01-data), `estimate-test-plot` and the `check-grs-headline` check (02-analysis). The cascade table names those three steps; the `download` row is gone, replaced by one sentence that no step writes the raw data. The `## Reproduction` example is the real `build-panel` declaration (`runner: uv` + `script:`, the two CSVs as deps), with one sentence on what `runner` and `script` mean.
- **Every showcase cascade claim was rerun on the real graph** in a scratch clone of this branch:
  - A comment edit to `01_build_panel.py` reads all three steps `stale`. `build showcase-analysis` then executes `build-panel`, and the other two report `unchanged` because the panel bytes are identical.
  - `build showcase-analysis/02-analysis` after that edit runs nothing and uses the saved panel. `status` on that selection exits 3 and names `build-panel` as a producer behind it that is not fresh.
  - `accept showcase-analysis/01-data` without `--reason` errors; with a reason, all three steps read `fresh`, `build-panel` as "reviewed baseline".
  - Setting the sample start to 1970-01 makes `impact` list all three steps, and `build showcase-analysis` executes all three.
- **The general mechanics claims match a real run.** I ran a throwaway four-step scratch project (download → build panel → analysis → check, same shape as the showcase) with this checkout's CLI. Verified behaviors:
  - `touch` keeps every step fresh; a comment edit makes the step and its two descendants stale; the rebuild writes identical bytes and the downstream steps report `unchanged`.
  - `build 02-analysis` after a real panel change runs nothing and uses the saved panel; `status` exits 3 naming the stale producer; `--upstream --dry-run` lists the three steps with last durations; `impact` lists the three affected steps.
  - A failing check reads `failed`; restoring the inputs clears it on the next build.
  - Deleting an output reads `missing`; deleting an unproduced input reads `external`, fails only the builds that reach it, gives a `task check` warning, and leaves the frontier listing the input as "not blocking".
  - `accept` without `--reason` errors. Accepting the panel step alone after a comment edit returns all three steps to `fresh`, shown as "reviewed baseline", with the last actual run still listed by `explain`.
  - A fresh clone reads the check `fresh` with "passed at these inputs in lock … not run here"; gitignored outputs read `missing` there.
  - A `params` edit makes the step stale; a conflicted lock warns and drops the disputed entry to `missing`.
- **Checks pass.** `superra task check --root docs/site` is clean, `check_markdown.py` reports the page clean, and `docs/build_site.sh` exits 0.
- **The page title is `reproducibility`**, matching the sibling skill pages.

## Review Notes

Tier: quick. Focuses: accuracy of reproduction claims against the code, contract, and CLI; docs-site gates (agent-first, concise, no AI-flavored prose, authority not paraphrase).
