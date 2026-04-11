# Merge Integration Quality Standards

Shared domain reference for merge proposals and merge review. Both the implementer (merge proposer) and reviewer use this checklist.

## Intent Preservation

- [ ] **Incoming intent understood:** Correctly identified what the incoming changes were trying to accomplish — read commits and diffs to understand WHY, not just WHAT
- [ ] **Current branch preserved:** Current branch's work is preserved where intended
- [ ] **Synthesis coherent:** Where both sides were combined, result is logically consistent
- [ ] **No silent losses:** No changes from either side silently dropped without justification

## Research Integrity

- [ ] **No silent result changes:** Analysis outputs are either unchanged, or the change was flagged to the user
- [ ] **Variable definitions consistent:** Variables used across merged code have consistent definitions
- [ ] **Sample construction preserved:** Sample filters and data sources are correct in the merged result
- [ ] **User decisions implemented:** (Tier 3) The user's decisions on research-meaningful conflicts were implemented correctly

## Two-Commit Structure

**Commit 1 (mechanical merge):**
- Complete the merge with lowest-assumption reconciliation
- Preserve information from both sides
- Restore a buildable, runnable state
- No opportunistic cleanup or reinterpretation
- Message: `"merge [incoming] into [current]: mechanical resolution"`

**Commit 2 (integration):**
- Adapt code, docs, tests, and generated artifacts so the branch incorporates the incoming objective
- Rewrite stale names, labels, paths, and references
- Regenerate derived outputs from merged source code
- Message: `"integrate [incoming] intent: [brief description]"`

**Quality checks:**
- [ ] Commit 1 is minimal — no opportunistic cleanup beyond conflict resolution
- [ ] Commit 2 adapts intent — code, docs, tests reflect the merged state
- [ ] Generated artifacts regenerated, not hand-edited

## Research-Meaningful Escalation (Tier 3)

These conflicts **MUST** be flagged for the user (mark as ASK USER):

- **Variable definitions:** Incoming changes redefine a variable used in this branch's analysis
- **Sample construction:** Incoming changes alter sample filters or data sources
- **Econometric specifications:** Incoming changes alter model specifications, control variables, or clustering
- **Data processing:** Incoming changes alter merge logic, data cleaning, or transformations
- **Results:** Incoming changes affect analysis outputs

**Never:**
- Silently change analysis results
- Choose ours/theirs for research-meaningful conflicts
- Remove data discipline artifacts
- Judge whether a methodology choice is correct

## Integration Map Format

For each conflict area, document:
- File and location
- Classification (analysis / data-processing / methodology / infrastructure / docs / generated / config)
- Decision: keep-incoming / keep-current / synthesize / regenerate / ASK USER
- Rationale (why this resolution)

Present user decisions in terms of **intent and consequences**, not raw diffs.

## Verification

- [ ] **Drift tests pass** (or failures appropriately escalated to user)
- [ ] **No stale references:** Old variable names, file paths, function names updated
- [ ] **No outdated labels:** Comments, docstrings, and documentation reflect the merged state
- [ ] **Pipeline runs** (if applicable): End-to-end pipeline produces expected outputs

## Data Discipline

- [ ] Data discipline artifacts (description steps, row counts, validation checks, documentation cells) preserved through the merge
- [ ] See loaded `econ-data-analysis` for the full list of artifacts
