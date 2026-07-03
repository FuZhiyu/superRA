---
title: "Shared Store And Client Mechanisms"
status: implemented
depends_on:
  - task-tree-native-orchestration
---

## Objective

Give the shared candidate store and citation client the mechanics that make concurrent recon and read dispatches safe. The candidate store is the coordination space for parallel review agents; these four capabilities are its backbone:

1. **Concurrency-safe materialization** — parallel dispatches write into the same shared non-git candidate store; `materialize` must merge concurrent writes for the same paper safely rather than racing. A paper card exists only after minimal metadata identifies a specific paper; recon materialization leaves the card `status: not-started`.
2. **Atomic claim-for-read** — a way for an agent to atomically claim a candidate before a substantive read by changing `status: not-started` to `status: in-progress`, so concurrent claims for the same paper yield exactly one winner; the loser adopts the existing record instead of re-reading.
3. **Flexible move-based permanent-record placement** — a `candidate_materializer.py promote` subcommand that moves (not copies) a candidate folder into a main-agent-supplied destination, defaulting to `superRA/<review>/papers/` when no project-specific destination is chosen, and repoints any candidate-store links that pointed at its old path.
4. **Version-DOI union on the citation client** — a tool-level way to union forward citations across a paper's NBER/SSRN/journal version DOIs, replacing per-dispatch manual looping.

### Required design

- `candidate_materializer.py materialize`: make folder creation/merge safe under concurrent invocation — atomic create-if-absent (mirror `citation_client.py`'s existing `fcntl`-guarded critical-section pattern for its rate gate). A test drives concurrent materialize calls for the same paper and asserts one clean merged folder, merged provenance/handles where applicable, `status: not-started`, and no race or corrupted `task.md`.
- Claim-for-read: an atomic claim operation (e.g. `candidate_materializer.py claim <key> --by <dispatch-label>`) that records the claimant, changes the card from `status: not-started` to `status: in-progress`, and reports in machine output whether the caller won. Claiming an already-claimed or already-decided candidate loses cleanly and returns the existing state. Include claim timestamp/lease metadata so stale `in-progress` claims can be diagnosed or reclaimed by an explicit override. A test drives concurrent claims for the same paper and asserts exactly one winner and one `in-progress` card.
- New `candidate_materializer.py promote` subcommand: given a candidate key/path and an explicit destination, move the folder, then find candidate-store links pointing at the old path (`## Discovery Provenance` `Discovered via:` links, and any other candidate record referencing it) and rewrite them to the new permanent path. Report unrewritten/ambiguous links for main-agent follow-up rather than guessing at them.
- `citation_client.py`: add a way to union forward citations across multiple version DOIs for the same work (NBER `10.3386/*`, SSRN `10.2139/ssrn.*`, journal DOI) — one call, deduplicated normalized-record output, `source` retained per member. This absorbs the manual per-DOI looping the workflow layer currently owns.
- Update `references/citation-client.md`'s command-surface docs for both additions; remove the "a workflow step, not a tool feature" framing for version-DOI union now that the tool does it.

### Files to update

- `skills/literature-review/scripts/candidate_materializer.py` — locking/atomicity, `promote` subcommand.
- `skills/literature-review/scripts/test_candidate_materializer.py` — concurrency test, promote test (move + link repoint).
- `skills/literature-review/scripts/citation_client.py` — version-DOI union.
- `skills/literature-review/scripts/test_citation_client.py` — union test.
- `skills/literature-review/references/citation-client.md` — document both additions.

### Validation criteria

- Concurrent `materialize` calls for the same paper converge to one `status: not-started` folder with no partial/corrupted `task.md`.
- Concurrent claims for the same `not-started` paper yield exactly one winner, transition the winner's card to `status: in-progress`, and return the existing record state to the loser.
- `promote` moves the folder to a caller-supplied destination (destination exists, source directory gone) and updates at least one dependent candidate-store link in the test fixture.
- The version-DOI union path returns a deduplicated record set from ≥2 fake-transport DOIs in the offline test suite.
- `uv run --with pytest --with pyyaml python -m pytest skills/literature-review/scripts` passes.

## Planner Guidance

Keep this task to the four mechanisms above — do not touch workflow or agent-protocol prose here. The dependent task (`read-once-review-agent`) wires the new commands into agent-facing instructions once they exist and are named; land this task first so that one can reference concrete command names.

## Results

Implemented the shared coordination mechanisms.

- [`candidate_materializer.py`](../../../skills/literature-review/scripts/candidate_materializer.py) now serializes store mutations, writes task files atomically, merges recon provenance and newly surfaced blank identity/retrieval fields into existing cards, supports `claim` for atomic `not-started` -> `in-progress` read claims, and supports `promote` to move a candidate folder to an explicit permanent-record destination while rewriting provable candidate-store links and reporting ambiguous bare mentions.
- [`citation_client.py`](../../../skills/literature-review/scripts/citation_client.py) now exposes `citations-union`, which unions forward citations across version IDs and preserves per-record `source_versions`.
- [`citation-client.md`](../../../skills/literature-review/references/citation-client.md) documents `citations-union` and the materializer's materialize / claim / promote behavior.

Verification: `uv run --with pytest --with pyyaml python -m pytest skills/literature-review/scripts` passed with 72 tests.

## Review Notes

1. **MAJOR** — [`materialize_one`](../../../skills/literature-review/scripts/candidate_materializer.py#L354-L365) only appends a provenance line when a later record matches an existing card; it does not merge newly surfaced handles or retrieval trace fields. A targeted check with first materialization `{doi}` and second materialization `{doi, arxiv, s2, pdf_url, pdf_path}` left `arXiv`, `S2`, `PDF URL`, and `PDF path` blank, even though the task requires merged provenance/handles for concurrent/repeated materialization. Merge newly supplied identity/retrieval fields into the existing `task.md` without overwriting better existing values, and add a test where the second matching record contributes new handles/artifact paths.

   → implemented: [`merge_record_into_existing`](../../../skills/literature-review/scripts/candidate_materializer.py) now fills blank identity/retrieval fields from later matched records without overwriting existing values, and [`test_materialize_merges_new_handles_into_existing_card`](../../../skills/literature-review/scripts/test_candidate_materializer.py) covers the second-record handle/path case.

2. **MAJOR** — [`rewrite_links`](../../../skills/literature-review/scripts/candidate_materializer.py#L423-L433) includes the bare `old_path.name` in a global substring replacement, so `promote` rewrites any occurrence of the candidate key in a candidate card as though it were a link. The task requires rewriting links and reporting unrewritten/ambiguous references for main-agent follow-up rather than guessing. Limit automatic rewrites to structured link targets/fields the tool can prove are path references, report ambiguous bare mentions, and cover that case in the promote test.

   → implemented: `promote` now rewrites Markdown link targets and known path fields only, reports unresolved bare key mentions, and the promote regression test verifies a plain prose mention remains unchanged while being reported.
