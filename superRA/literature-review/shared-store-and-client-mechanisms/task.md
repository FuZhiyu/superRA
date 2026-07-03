---
title: "Shared Store And Client Mechanisms"
status: not-started
depends_on:
  - task-tree-native-orchestration
---

## Objective

Give the shared candidate store and citation client the mechanics that make concurrent, read-once dispatching safe. The candidate store is the coordination space for parallel review agents; these four capabilities are its backbone:

1. **Concurrency-safe materialization** — parallel dispatches write into the same shared non-git candidate store; `materialize` must merge concurrent writes for the same paper safely rather than racing.
2. **Atomic claim-on-open** — a way for an agent to atomically claim a candidate before opening its source, so concurrent claims for the same paper yield exactly one winner; the loser adopts the existing record instead of re-reading.
3. **Move-based promotion** — a `candidate_materializer.py promote` subcommand that moves (not copies) a candidate folder into `superRA/<review>/papers/` and repoints any candidate-store links that pointed at its old path.
4. **Version-DOI union on the citation client** — a tool-level way to union forward citations across a paper's NBER/SSRN/journal version DOIs, replacing per-dispatch manual looping.

### Required design

- `candidate_materializer.py materialize`: make folder creation/merge safe under concurrent invocation — atomic create-if-absent (mirror `citation_client.py`'s existing `fcntl`-guarded critical-section pattern for its rate gate). A test drives concurrent materialize calls for the same paper and asserts one clean merged folder, not a race or corrupted `task.md`.
- Claim-on-open: an atomic claim operation (e.g. `candidate_materializer.py claim <key> --by <dispatch-label>`, or a `--claim` flag on `materialize`) that records the claimant in the candidate record and reports in machine output whether the caller won. Claiming an already-claimed or already-decided candidate loses cleanly and returns the existing state. A test drives concurrent claims for the same paper and asserts exactly one winner.
- New `candidate_materializer.py promote` subcommand: given a candidate key/path and a destination under `superRA/<review>/papers/`, move the folder, then find candidate-store links pointing at the old path (`## Discovery Provenance` `Discovered via:` links, and any other candidate record referencing it) and rewrite them to the new promoted path. Report unrewritten/ambiguous links for main-agent follow-up rather than guessing at them.
- `citation_client.py`: add a way to union forward citations across multiple version DOIs for the same work (NBER `10.3386/*`, SSRN `10.2139/ssrn.*`, journal DOI) — one call, deduplicated normalized-record output, `source` retained per member. This absorbs the manual per-DOI looping the workflow layer currently owns.
- Update `references/citation-client.md`'s command-surface docs for both additions; remove the "a workflow step, not a tool feature" framing for version-DOI union now that the tool does it.

### Files to update

- `skills/literature-review/scripts/candidate_materializer.py` — locking/atomicity, `promote` subcommand.
- `skills/literature-review/scripts/test_candidate_materializer.py` — concurrency test, promote test (move + link repoint).
- `skills/literature-review/scripts/citation_client.py` — version-DOI union.
- `skills/literature-review/scripts/test_citation_client.py` — union test.
- `skills/literature-review/references/citation-client.md` — document both additions.

### Validation criteria

- Concurrent `materialize` calls for the same paper converge to one folder with no partial/corrupted `task.md`.
- Concurrent claims for the same paper yield exactly one winner; the loser receives the existing record state.
- `promote` moves the folder (destination exists, source directory gone) and updates at least one dependent candidate-store link in the test fixture.
- The version-DOI union path returns a deduplicated record set from ≥2 fake-transport DOIs in the offline test suite.
- `uv run --with pytest --with pyyaml python -m pytest skills/literature-review/scripts` passes.

## Planner Guidance

Keep this task to the four mechanisms above — do not touch workflow or agent-protocol prose here. The dependent task (`read-once-review-agent`) wires the new commands into agent-facing instructions once they exist and are named; land this task first so that one can reference concrete command names.
