---
title: "Dashboard Shows Each State, Where Staleness Starts, and What Is Online-Only"
status: not-started
depends_on: [02-upstream-default]
---

## Objective

Extend the dashboard's reproduction design language so a reader sees at a glance, in the Graph, the Tree, and the step panel, three things: each step's state, which step a staleness starts at, and which steps and files are online-only on this machine.

- **Two visual channels on top of the existing state hue.** The hue, glyph, and label still say the state.
  - **Solid vs dashed: whose evidence.** A step whose own files are `stale`, `missing`, or `failed` keeps today's solid card (tinted fill, solid left border). A step `stale` only through upstream gets no fill, a dashed left border in the `stale` hue, and the label `stale · upstream`. Only the step where staleness starts is solid.
  - **Opaque vs faded: what this machine holds.** An `unverified` step's card fades its fill and border, keeps text at full contrast, and shows a cloud glyph and the label `unverified · online-only`. Its outgoing wires fade with it.
- **Tokens.** Replace the `--rp-external` tokens with `--rp-unverified` in both themes, and remove `external` from `REPRO_STATES`, filters, and the legend.
- **Task rollups.** Group nodes and Tree rows count their steps per state, with the same glyphs. A task whose steps are all `unverified` fades like a step.
- **Step panel.**
  - The state line shows the reported state with its reason. When the step's own state differs, a second line reads "Own evidence: fresh", followed by when the step would rerun and a link to the producer where staleness starts.
  - Input and output lists mark each online-only file with the cloud glyph and its size, and lead with a summary: "N files online-only here (size)", followed by the download note.
- **Legend.** Two groups: the states (`fresh`, `stale`, `missing`, `failed`, `unverified`), and how to read a card (solid = own evidence, dashed = inherited from upstream, faded = online-only here).
- **Build menu.** Build (with producers), only this, and force, end to end:
  - the command string and scope helper `reproBuildScope` ([dashboard.js:2277](../../../../skills/task-tree/scripts/templates/dashboard.js#L2277));
  - the cost estimate, which today counts every step in scope under force ([dashboard.js:2316](../../../../skills/task-tree/scripts/templates/dashboard.js#L2316));
  - the `POST /api/repro/build` body, which gains `only`, and `_build_args` ([plan_dashboard.py:1849](../../../../skills/task-tree/scripts/plan_dashboard.py#L1849));
  - a build the download gate stops shows the gate's file list instead of a generic error.
- **Docs.** [internals.md](../../../../skills/task-tree/references/internals.md) §Graph actions and the dashboard's reproduction description.

### Constraints

- **State is never carried by color alone:** each channel also has a glyph or label. Both themes meet text contrast at the faded opacity; fade fills and borders, not text.
- **Wires.** Dashed wires already mean `depends_on` only. The upstream channel lives on card borders, never on wires.

### Validation

- Browser screenshots of the Graph and the Tree, in light and dark themes, on a fixture holding each state. The fixture includes an own-stale step with two inherited-stale descendants and an `unverified` task. Attach them to `## Results`.
- [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py) and [tests/test_dag_workspace_browser.py](../../../../skills/task-tree/scripts/tests/test_dag_workspace_browser.py) cover the new classes, the panel's own-evidence line, the online-only file list, the legend, and the Build menu's `only` request.

## Details

- **Current design language.** Each state has a tinted background, a colored left border, and a glyph ([dashboard.css:68-72](../../../../skills/task-tree/scripts/templates/dashboard.css#L68-L72) light, [:128-132](../../../../skills/task-tree/scripts/templates/dashboard.css#L128-L132) dark, classes at [:1731-1750](../../../../skills/task-tree/scripts/templates/dashboard.css#L1731-L1750)). Glyphs live in `REPRO_STATES` ([dashboard.js:1059-1066](../../../../skills/task-tree/scripts/templates/dashboard.js#L1059-L1066)), and the legend in [dashboard.js:1881-1896](../../../../skills/task-tree/scripts/templates/dashboard.js#L1881-L1896).
- **Where the inherited state is computed.** The dashboard already receives `status`, `reason`, and `local_status` per step and prints "For saved inputs: …" in the panel ([dashboard.js:2233](../../../../skills/task-tree/scripts/templates/dashboard.js#L2233)). Inherited-only means `status` is `stale` while `local_status` is `fresh` or `unverified`.
- **Review focus.** This task is mostly visual judgment. A review should look at the screenshots, not only the tests.
