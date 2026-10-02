---
title: "Dashboard Shows Each State, Where Staleness Starts, and What Is Online-Only"
status: revise
depends_on: [02-upstream-default]
---

## Objective

Extend the dashboard's reproduction design language so a reader sees at a glance, in the Graph, the Tree, and the step panel, three things: each step's state, which step a staleness starts at, and which steps and files are online-only on this machine.

- **One rule splits each card into two channels.**

  | Card part | Shows | Values |
  |---|---|---|
  | **Left border, glyph, label** | the reported state | its state hue, as today |
  | **Fill** | the step's own state | a tint of its own state's hue (today's look); **empty** when its own state is `fresh` but it is reported `stale` (inherited); **diagonal hatching** in the `unverified` hue when its own state is `unverified` |

  - Today's cards keep their look whenever the two states agree. Only the step where staleness starts has a stale tint; its descendants show a stale border around an empty fill and the label `stale · upstream`.
  - An `unverified` step shows a cloud glyph and the label `unverified · online-only`. If its producer is also stale, it gets a stale border around hatching.
- **Reserved meanings stay put.** Dashed borders mean a check step ([dashboard.css:1704](../../../../skills/task-tree/scripts/templates/dashboard.css#L1704)); dashed wires mean `depends_on` only. Fading means a zero-count legend item ([:1592](../../../../skills/task-tree/scripts/templates/dashboard.css#L1592)) and an unfocused wire during edge focus ([:2527](../../../../skills/task-tree/scripts/templates/dashboard.css#L2527)). The new channels use neither.
- **Tokens.** Replace the `--rp-external` tokens with `--rp-unverified` in both themes, and remove `external` from `REPRO_STATES`, filters, and the legend.
- **Task rollups.** Group nodes and Tree rows count their steps per state, with the same glyphs. A task whose steps are all `unverified` gets the hatched fill.
- **Step panel.**
  - The state line shows the reported state with its reason. When the step's own state differs, a second line reads "Own evidence: fresh" (or `unverified`), followed by when the step would rerun and a link to the origin step.
  - Input and output lists mark each online-only file with the cloud glyph and its size, and lead with a summary: "N files online-only here (size)", followed by a pointer to [online-only-files.md](../../../../skills/reproducibility/references/online-only-files.md).
- **Legend.** Two groups: the states (`fresh`, `stale`, `missing`, `failed`, `unverified`), and how to read a fill (tinted = the step's own state, empty = inherited from upstream, hatched = online-only here).
- **Build menu.** Build (with producers), only this, and force, end to end:
  - the command string ([dashboard.js:2277](../../../../skills/task-tree/scripts/templates/dashboard.js#L2277)) and the scope helper `reproBuildScope` ([dashboard.js:2297](../../../../skills/task-tree/scripts/templates/dashboard.js#L2297));
  - the cost estimate, which today counts every step in scope under force ([dashboard.js:2316](../../../../skills/task-tree/scripts/templates/dashboard.js#L2316));
  - the `POST /api/repro/build` body, which gains `only`, and `_build_args` ([plan_dashboard.py:1849](../../../../skills/task-tree/scripts/plan_dashboard.py#L1849));
  - a build the download gate stops shows the gate's file list instead of a generic error.
- **Docs.**
  - [internals.md](../../../../skills/task-tree/references/internals.md): §Graph actions, and the reproduction workspace description.
  - The [docs-site dashboard page](../../../../docs/site/04-utility-skills/01-task-tree/04-dashboard/task.md): line 26's Build menu, and how to read a card.

### Constraints

- **State is never carried by color alone:** each channel also has a glyph or label. Hatching stays light enough for text to meet contrast in both themes.
- **Wires.** Dashed wires already mean `depends_on` only. The upstream channel lives on card borders, never on wires.

### Validation

- Browser screenshots of the Graph and the Tree, in light and dark themes, on a fixture holding each state. The fixture includes an own-stale step with two inherited-stale descendants, an `unverified` task, an `unverified` step with a stale producer, and a check step. Attach them to `## Results`.
- [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py) and [tests/test_dag_workspace_browser.py](../../../../skills/task-tree/scripts/tests/test_dag_workspace_browser.py) cover the new classes, the panel's own-evidence line, the online-only file list, the legend, and the Build menu's `only` request.

## Details

- **Current design language.** Each state has a tinted background, a colored left border, and a glyph ([dashboard.css:68-72](../../../../skills/task-tree/scripts/templates/dashboard.css#L68-L72) light, [:128-132](../../../../skills/task-tree/scripts/templates/dashboard.css#L128-L132) dark, classes at [:1731-1750](../../../../skills/task-tree/scripts/templates/dashboard.css#L1731-L1750)). Glyphs live in `REPRO_STATES` ([dashboard.js:1059-1066](../../../../skills/task-tree/scripts/templates/dashboard.js#L1059-L1066)), and the legend in [dashboard.js:1881-1896](../../../../skills/task-tree/scripts/templates/dashboard.js#L1881-L1896).
- **Where the inherited state is computed.** The dashboard already receives `status`, `reason`, and `local_status` per step and prints "For saved inputs: …" in the panel ([dashboard.js:2233](../../../../skills/task-tree/scripts/templates/dashboard.js#L2233)). Inherited-only means `status` is `stale` while `local_status` is `fresh` or `unverified`.
- **Review focus.** This task is mostly visual judgment. A review should look at the screenshots, not only the tests.

## Results

Every step card in the Graph, the Tree, the task-page step table, the step panel, and the explain card now shows two things. Its border, glyph, and label show the reported state. Its fill shows the step's own state: a tint, an empty fill when the staleness is inherited, or hatching when files are online-only. The Build menu sends `only`, and a build stopped by the download gate shows the gate's file list. On the every-state fixture below, only `clean` has a stale tint; `merge` and `report` have empty fills labelled `stale · upstream`; `vendor-join` has a stale border around hatching; the `03-vendor` task is hatched.

### How a card reads

- **One mapping, `reproChannels`** ([dashboard.js:1090](../../../../skills/task-tree/scripts/templates/dashboard.js#L1090)). It returns the reported state's class, glyph, and label, plus a fill modifier:

  | Own state vs reported | Fill class | Label |
  |---|---|---|
  | Same | none (today's tint) | the state |
  | Own `fresh`, reported `stale` | `rp-inherited`: the card surface | `stale · upstream` |
  | Own `unverified`, reported `unverified` | `rp-hatched` | `☁ unverified · online-only` |
  | Own `unverified`, reported `stale` | `rp-hatched` | `stale · upstream`, plus a `☁ online-only` tag beside the name |

- **Hatching keeps text contrast.** Light theme: the stripes are the unverified wash on the card surface, two surfaces `--text` and `--rp-ink-2` already clear 4.5:1 on. Dark theme: the wash sits too close to `--bg-card` to read as stripes, so it takes 10% of the unverified ink. `--rp-ink-2` keeps about 4.8:1 on the stripe. The pattern is one token, `--rp-hatch` ([dashboard.css:77](../../../../skills/task-tree/scripts/templates/dashboard.css#L77), dark [:141](../../../../skills/task-tree/scripts/templates/dashboard.css#L141)). A first draft used 16% ink stripes, which dropped `--rp-ink-2` to about 4.0:1 in light and 4.3:1 in dark.
- **The cloud is a text glyph** (U+2601 U+FE0E). Menlo and IBM Plex Mono draw it as a squat mark, so `.repro-cloud` and the unverified glyph use Hiragino Sans or Lucida Grande ([dashboard.css:1769](../../../../skills/task-tree/scripts/templates/dashboard.css#L1769)).
- **Tokens.** `--rp-external` became `--rp-unverified` in both themes, with the same validated purple. `external` is gone from `REPRO_STATES`, the legend, the class rules, `reproExplainable`, and the estimate. The view had no state filter to update.
- **Reserved meanings are unchanged.** The new channels use no dashed borders and no fading. Check steps had lost their `is-check` class in an earlier rewrite, though the CSS rule was still there. The class is back, so check cards are dashed again, and check rows in the Tree are too.

### Graph, Tree, panel, legend

- **Task rollups** (`reproRollup`, [dashboard.js:1081](../../../../skills/task-tree/scripts/templates/dashboard.js#L1081)) count each task's steps by reported state, using the state glyphs.
  - On a task card, the rollup replaces the summary line.
  - On a Tree row, it is a compact badge (`◐3 ○1 ✕1`) before the status badge.
  - A task whose steps all have own state `unverified` gets hatching: the whole card when collapsed, the head band when expanded, or the badge in the Tree.
- **Tree step rows** (`syncTreeSteps`, [dashboard.js:574](../../../../skills/task-tree/scripts/templates/dashboard.js#L574)) used to show only the step name. Each row now shows the glyph, name, and label, with the same border and fill as a card. A selected row has an accent outline, so its fill stays visible.
- **Step panel** (`renderReproDetail`, [dashboard.js:2256](../../../../skills/task-tree/scripts/templates/dashboard.js#L2256)).
  - The status chip carries both channels.
  - When the step's own state differs, a second line reads `Own evidence: fresh.` or `Own evidence: unverified — <reason>.` It says a build reruns the step only if its inputs change after the upstream steps rerun, and it links the origin step. This line replaces "For saved inputs: …".
  - Outputs and Inputs start with a summary (`1 file online-only here (2.3 MiB)`) and a pointer to `references/online-only-files.md`. Each online-only file shows the cloud tag and its size. The Inputs header carries the tag too, and that section opens by default when it holds online-only files.
- **Legend** ([dashboard.js:1902](../../../../skills/task-tree/scripts/templates/dashboard.js#L1902)) has two groups. *State · border, glyph, label* lists the five states, with `unknown` only when present, plus check step. *Fill · the step's own evidence* lists tinted, empty, and hatched, each with a swatch.

![Graph, light: clean is the only stale tint; merge and report are inherited; vendor-join is a stale border around hatching; 03-vendor is hatched](attachments/graph-light.png)

![Graph, dark](attachments/graph-dark.png)

![Tree and step panel, light: Tree rows count states; vendor-join's panel names its own evidence and the origin step](attachments/tree-light.png)

![Tree and step panel, dark](attachments/tree-dark.png)

![Step panel inputs, light: the online-only summary and the online-only file with its size](attachments/panel-light.png)

![Step panel inputs, dark](attachments/panel-dark.png)

![Legend, light](attachments/legend-light.png) ![Legend, dark](attachments/legend-dark.png)

### Build menu and the download gate

- **Three items:** Build with producers (`superra repro build X`), Build only this task or step (`--only`), and Force rebuild (`--force`). The page sends `{target, only, force}`. `_build_args` emits `--only` ([plan_dashboard.py:1849](../../../../skills/task-tree/scripts/plan_dashboard.py#L1849)), and the job record stores `only` in place of `upstream`.
- **The estimate follows the runner's rule** (`reproBuildEstimate`, [dashboard.js:2359](../../../../skills/task-tree/scripts/templates/dashboard.js#L2359)). It counts the steps whose own state is `stale`, `missing`, or `failed`, plus the forced targets. Inherited-stale steps whose origin is in scope count as "more if their inputs change". `unverified` steps count as "online-only, not run". Force covers the targets, not every step in scope.
- **Gate display.** `_build_summary` ([plan_dashboard.py:1976](../../../../skills/task-tree/scripts/plan_dashboard.py#L1976)) returns an `Error:` summary together with the lines after it as `detail`. The page prints those lines under "Last build". A real gated build on the test fixture returned `code/fetch.sh  -  not on disk, and no step produces it`.

![Build menu for 02-estimate: with producers runs clean, figures, and robustness, and counts merge and report as rerunning only if their inputs change](attachments/build-menu.png)

![A build stopped by the download gate lists the file it would read](attachments/build-gate.png)

### Docs

- [internals.md](../../../../skills/task-tree/references/internals.md). A new **Card channels** paragraph sits after the workspace description. §Graph actions covers the three modes, `{target, only, force}`, the estimate rule, and `detail`. The file-preview paragraph notes that online-only files never preview.
- [Docs-site dashboard page](../../../../docs/site/04-utility-skills/01-task-tree/04-dashboard/task.md). The state list now reads `unverified`. A "Read a card in two parts" list explains the two channels and the three fills. The Build menu paragraph names the three items and the gate.

### Deviations and decisions

- **The state-fixture browser tests live in a new module,** [tests/test_repro_states_browser.py](../../../../skills/task-tree/scripts/tests/test_repro_states_browser.py), not in `test_dag_workspace_browser.py`. Each module runs one in-process server bound to the global `PLAN_ROOT`, so two module-scoped fixtures in one file would serve the wrong tree. `test_dag_workspace_browser.py` keeps its menu test, updated to the new labels and `--only`.
- **Online-only file links carry no `data-peek`.** Hovering `/api/file-peek` reads the file's first 4 KiB, which would download it. The server route itself has no online-only guard (see below).
- **The screenshot script is not a reproduction step.** The screenshots depend on the browser, the fonts, and the run timestamps and durations they show, so they are regenerated per machine. Registering the script would also make every later `dashboard.js` edit stale it. The repo's other dashboard tasks register none. The command is at the top of [screenshots.py](attachments/screenshots.py).
- **The Tree row badge costs slug width.** In the default-width sidebar, the active `02-estimate` row truncates to `0…`. The badge's title attribute spells out the counts.

### Out of scope, found while working

- **`GET /api/file-peek` has no online-only check,** so a direct request or a body link to an online-only file would download it. The step panel avoids this by not attaching the preview. A server-side check belongs with 01's guarded reads.
- **Switching from Graph to Tree on one page can reorder sidebar rows** (01, 03, 02). It also happened on the pre-change code in one of two runs. The screenshots use a fresh page for the Tree.

### Verification

- **Tests.** The full suite, playwright included, passed: 1121 tests, none skipped. Command: `uv run --with pytest --with playwright --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts`.
  - [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py):
    - the card classes, the hatched task card, and both legend groups, rendered under node;
    - the estimate for each mode on an inherited-stale and an unverified fixture;
    - `_build_args` with `--only`;
    - `_build_summary` keeping an error's lines;
    - a live `only` build stopped by the gate, whose job carries the file in `detail`.
  - [test_repro_states_browser.py](../../../../skills/task-tree/scripts/tests/test_repro_states_browser.py), on the every-state fixture with `SF_DATALESS` simulated:
    - the Graph classes and labels, the check class, the hatched task, and the legend text;
    - the Tree rollup and step classes;
    - the own-evidence line, the origin link, the online-only summary, the file size, and the missing `data-peek`;
    - the menu's `only` POST body and the gate detail rendering.
- **Screenshots.** [screenshots.py](attachments/screenshots.py) builds the same fixture and wrote every image above on OlinStudio with Chrome.

## Review Notes

Tier: thorough. Focuses: visual design against the channel rule and reserved meanings (all ten screenshots, light and dark); the state mapping from `status`, `local_status`, `origin`, and `files`; the Build menu's `only` request end to end; test quality. Verified by rerunning the every-state fixture through `superra repro build` and `--dry-run` with `SF_DATALESS` simulated.

1. **[BLOCKING] `GET /api/file-peek` reads online-only files, and the step panel still reaches it on click.**
   - [plan_dashboard.py:1592-1620](../../../../skills/task-tree/scripts/plan_dashboard.py#L1592-L1620) opens any text file for a 4 KiB head with no online-only check.
   - Removing `data-peek` ([dashboard.js:2070](../../../../skills/task-tree/scripts/templates/dashboard.js#L2070)) stops only the hover. The link still opens the in-page file view, which calls the route and then previews from `/files/` ([dashboard.js:3566](../../../../skills/task-tree/scripts/templates/dashboard.js#L3566), [:3599](../../../../skills/task-tree/scripts/templates/dashboard.js#L3599)). This breaks the parent's rule that nothing downloads implicitly.
   - Fix: in `_file_peek`, test `is_online_only(resolved, info)` right after the `stat`. For an online-only file, return `exists`, `online_only: true`, `size`, and `mtime_ns`, and skip the head read. `loadProjectFile` then shows "online-only here" with the size, plus the pointer to `online-only-files.md`, and renders no preview. Add a route test with `SF_DATALESS` simulated. Then update the internals.md file-preview paragraph, and drop the "Out of scope" item from `## Results`.

2. **[BLOCKING] The Tree rollup badge squeezes task slugs down to one character.**
   - [tree-light.png](attachments/tree-light.png) shows `0…`, `01-c…`, and `03-ven…`. The badge ([dashboard.js:581](../../../../skills/task-tree/scripts/templates/dashboard.js#L581), `flex:none` at [dashboard.css:2625](../../../../skills/task-tree/scripts/templates/dashboard.css#L2625)) goes on every task that has steps, so this is not rare. Real slugs such as `02-upstream-default` are longer than the fixture's.
   - Fix: keep the slug legible at the default sidebar width. Options: move the rollup to its own line under the row, let the badge shrink before the slug does, or collapse it to the most severe state's glyph and count. Re-shoot the Tree to show the result.

3. **[BLOCKING] The Force estimate ignores the download gate.**
   - [build-menu.png](attachments/build-menu.png) shows "Force rebuild this task … 6 steps would run · ~28ms". On the same fixture, `superra repro build --dry-run --force 02-estimate` prints "1 file(s) the build reads are not on this machine, so the build would run nothing: Data/vendor.csv 2.4 MB online-only here (read by vendor-join)".
   - [dashboard.js:2365](../../../../skills/task-tree/scripts/templates/dashboard.js#L2365) pushes a forced `unverified` target into the run set without checking what it reads. [test_dashboard.py:6879](../../../../skills/task-tree/scripts/test_dashboard.py#L6879) asserts the wrong text: it counts the forced `unverified` steps `x` and `y` as running. This contradicts the Results claim that "the estimate follows the runner's rule".
   - Fix: mirror `_gate` ([repro_run.py:405](../../../../skills/task-tree/scripts/repro_run.py#L405)) in `reproBuildEstimate`. If a step in the run set has a `dependency` row in `files` that is online-only, or absent with no producer, and no other step in the run set writes it, the item reads that the download gate stops the build, with the count and size of those files, instead of a step count. Update the test.

4. **[BLOCKING] `screenshots.py` is retained and its PNGs are cited in `## Results`, but it is not registered as a step.**
   - This fails the `[BLOCKING]` registration gate in [designing-the-graph.md](../../../../skills/reproducibility/references/designing-the-graph.md#what-earns-a-step). `superra task check` reports 10 warnings for this task.
   - None of the three reasons in Deviations holds:
     - "Leave files regenerated per machine unregistered" covers machine-local files such as sysimages. These PNGs are committed evidence. Their varying bytes only cost early cutoff, and no step reads them.
     - A `dashboard.js` edit that makes the screenshots stale is the true signal. The stale rule then decides between accepting and rerunning.
     - Other tasks registering none is precedent, not a reason.
   - Fix: add `## Reproduction` with one `screenshots` step.
     - `cmd`: the `uv run` line at the top of `screenshots.py`.
     - `deps`: `screenshots.py`, `tests/test_repro_states_browser.py`, `plan_dashboard.py`, and the `templates/` files the page loads (`dashboard.js`, `dashboard.css`, `base.html`).
     - `outs`: the ten PNGs.
   - Then build the step, or accept the current outputs. Commit `repro-lock.json`, and state the evidence in `## Results` per reproducibility §Recording a Result.

5. **[ADVISORY] An `unverified` step behind a stale producer is attempted, then fails at the step-start gate, but the panel and the estimate say it will not run.**
   - The panel line ([dashboard.js:2279](../../../../skills/task-tree/scripts/templates/dashboard.js#L2279)) says "A build reruns it only if its inputs change". The menu counts it as "online-only, not run".
   - On the fixture, `superra repro build 02-estimate` reran `clean` and then failed `vendor-join`: "cannot start: 1 input(s) not on this machine". "Last build" reads only "6 step(s): 4 executed, 2 failed", with no file list, because `_build_summary` keeps detail only after an `Error:` line.
   - Fix: for own `unverified`, say that a build stops at this step if its inputs change, and count it that way in the estimate.

6. **[ADVISORY] The cloud tag touches the step name.** It renders as `vendor-join☁ online-only` ([graph-light.png](attachments/graph-light.png)). Give `.repro-node-name .repro-cloud-tag` a left margin.

7. **[ADVISORY] Tree check rows say only `fresh`.** The check kind shows only through a faint dashed border ([tree-light.png](attachments/tree-light.png), `codebook-check`), while Graph cards add `· check`. Add the same suffix to `.nav-step-state`.

8. **[ADVISORY] The Results claim about the fresh page does not match two screenshots.** `## Results` says "The screenshots use a fresh page for the Tree", which implies the row-order bug is avoided. [tree-dark.png](attachments/tree-dark.png) and [panel-dark.png](attachments/panel-dark.png) still show the rows in order 01, 03, 02. Re-shoot those two, or drop the claim.
