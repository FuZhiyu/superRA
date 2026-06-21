# Bundle Two Tasks Fixture

This fixture is a disposable superRA task tree for instruction-following tests.
It is intentionally small but exercises several structural requirements in one
agent dispatch:

- `superra task read` exposes root, parent, and target objective sentinels.
- sibling dependency metadata is visible while dependency `## Results` content
  is not inherited by target reads.
- unresolved comments surface in `task read`.
- marker files outside the task tree must be read explicitly.
- two target leaf tasks let one bundle dispatch require multiple task reads
  before writing `loading-evidence.json`.

The expected artifact shape is stored in
[expected/loading-evidence.expected.json](expected/loading-evidence.expected.json).
