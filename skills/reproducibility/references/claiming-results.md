# Claiming Results

`[BLOCKING]` Before `## Results` claims a result reproduces, every step `superra repro status <targets>` reports is `fresh`; add `--upstream` when the claim covers the producer chain.

1. **Produce the result through the graph** — `superra repro build <targets>`, or [accept](rerun-or-accept.md#accept) a result already produced from the same committed code.
2. **State what the evidence covers in `## Results`:** the targets, the saved and external inputs they read, the check outcomes, and which steps executed versus which were accepted.
3. **Commit the changed `repro-lock.json` and `repro-acceptance/` records with the work.**
