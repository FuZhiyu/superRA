# Theory-Modeling Vertical — Results

> Mirrors `PLAN.md` structure. Updated after each task with key findings.
> New agents: read `PLAN.md` for what to do, `RESULTS.md` for what was found.

**Last updated:** 2026-04-22 (review fixes incorporated; verification checks passed)
**Status:** In Progress

---

## Task 1: Create the `theory-modeling` domain skill and its stage-scoped references

**Status:** Implemented (review fixes incorporated)

### Key Findings
- Added `skills/theory-modeling/SKILL.md` with a proactive trigger surface, stage-scoped load table, an iron law centered on defined objects plus stated assumptions, and a shared `Define–Derive–Validate` checklist.
- The checklist makes notation discipline, interpretable primitive-level assumptions, stepwise derivations, and proof / special-case / numerical verification `[BLOCKING]` requirements.
- Added planning, drift-test, and integration references so the vertical has a complete PLAN / Phase A / Phase B path without inventing a new workflow or rendering utility.

### Notes
- The skill explicitly points human-facing equation/table/figure rendering back to `superRA:report-in-markdown`.
- Review feedback on the planning template has already been incorporated: the inventory now includes explicit sections for timing / information structure, solution concept, and notation conventions, and the hard gate no longer implies task drafting before researcher approval.

## Task 2: Wire the new vertical into runtime surfaces, docs, and discovery

**Status:** Implemented (review fixes incorporated)

### Key Findings
- Added `theory-modeling` to the `using-superRA` inventory and manifest, the `planning-workflow` routing table, and the `refactor-and-integrate` domain-specific integration pointers.
- Generalized the planning template and exit-plan-mode reminder so a second planning hard gate is first-class rather than a data-only exception.
- Updated contributor/runtime docs (`README.md`, `skills/CATEGORIES.md`, `CLAUDE.md`) to present theory/modeling as an implemented vertical, added `.agents/skills/theory-modeling`, and extended `tests/check-harness-compatibility.sh` with discovery/wiring assertions.

### Notes
- A review pass surfaced remaining single-vertical assumptions in the canonical agent prompts and generic integration/merge references; the task now includes fixes for those surfaces plus stronger compatibility assertions.
- The compatibility suite and targeted smoke checks are being treated as Task 3 verification rather than as Task 2 completion criteria.
- Generated `.codex/agents/*` artifacts were refreshed after the canonical agent prompt updates and are now in sync with the checked-in source prompts.

## Task 3: Verify the new vertical end to end and reconcile any drift

**Status:** Implemented (final structural verification passed; pending final review)

### Key Findings
- `bash tests/check-harness-compatibility.sh` passed after the final Task 3 fixes. The merge-quality portion now requires the generalized Tier 3 phrases `sample construction / model setup`, `specifications / solution concepts`, `data processing / derivation logic`, `results / headline outputs`, and `active domain-discipline artifacts`, and explicitly fails if stale data-only phrases such as `econometric specifications` or `removing data discipline artifacts` reappear.
- The same harness-compatibility run re-ran the embedded Codex agent generation checks (`python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py` and `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check`), and both passed.
- A targeted smoke check passed for repo-local discovery and routing semantics: `.agents/skills/theory-modeling` resolves to `../../skills/theory-modeling`, `planning-workflow` routes to `superRA:theory-modeling`, `using-superRA` lists the vertical in its manifest, and the `Model Inventory / Assumption Map` hard gate remains present in the theory-modeling planning reference.

### Notes
- Remaining risk: this pass was structural and workflow-facing. It did not run a live Claude/Codex end-to-end dispatch session against a toy modeling prompt in this turn.
- No generated artifacts needed reconciliation in this round because the only code changes were the merge-quality reference and the structural compatibility test.

### Verification Commands
```bash
bash tests/check-harness-compatibility.sh

python3 - <<'PY'
import os
from pathlib import Path

link = Path('.agents/skills/theory-modeling')
assert link.is_symlink(), '.agents/skills/theory-modeling must be a symlink'
assert os.readlink(link) == '../../skills/theory-modeling', os.readlink(link)
using_text = Path('skills/using-superRA/SKILL.md').read_text(encoding='utf-8')
planning_text = Path('skills/planning-workflow/SKILL.md').read_text(encoding='utf-8')
theory_planning_text = Path('skills/theory-modeling/references/planning.md').read_text(encoding='utf-8')
assert 'superRA:theory-modeling' in using_text, 'using-superRA manifest must mention theory-modeling'
assert '`superRA:theory-modeling`' in planning_text, 'planning-workflow routing must mention theory-modeling'
assert 'Model Inventory / Assumption Map' in theory_planning_text, 'theory-modeling planning reference must expose the hard gate'
print('theory-modeling discovery/routing smoke check passed')
PY
```
