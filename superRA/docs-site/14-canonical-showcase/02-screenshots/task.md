---
title: "Capture Task-Detail + Kanban Views and Compress All Quickstart Screenshots"
status: approved
depends_on: []
tags: []
created: 2026-06-17
---

## Objective

Give the rewritten Quickstart the two dashboard views it still needs from the *real* study tree, and shrink every dashboard screenshot it uses.

- **Capture two new views** of the real [showcase-analysis](../../../showcase-analysis/task.md) tree, full chrome (the standard `generate` export, never `--doc-mode`), matching the existing progression shots in [13-real-analysis-showcase/02-quickstart-screenshots/attachments](../../13-real-analysis-showcase/02-quickstart-screenshots/attachments/):
  - **Task detail** — a single task open with its `## Objective` and `## Results` showing (e.g. `02-analysis`). Reachable headlessly via the hash route `#/<task-path>` the standalone export uses.
  - **Kanban** — the board view. The Kanban view is a `showView('kanban')` JS toggle with **no URL route** (documented in `13-real-analysis-showcase/02-quickstart-screenshots`), so a hash route will not reach it; capture it by invoking the toggle before the screenshot (Playwright `page.evaluate("showView('kanban')")`, or equivalent injected JS). If the toggle proves brittle on a three-task board — where a three-card Kanban is not very illustrative anyway — drop the dedicated Kanban shot and record that decision; `04-rewrite-quickstart` will lean on the Workspace views instead.
- **Compress all dashboard screenshots the Quickstart embeds** to 256-color palette PNG, in place, keeping the `.png` filenames so no markdown or inliner change is needed: the three existing progression shots (`showcase-after-planning.png`, `showcase-mid-implement.png`, `showcase-complete.png`) plus the two new captures. Use Pillow: `Image.open(p).convert("RGB").quantize(colors=256, method=Image.MEDIANCUT).save(p, optimize=True)`. Benchmarked ~60% reduction (≈400 KB → ≈170 KB) with no visible loss on flat-UI screenshots. Do **not** touch the matplotlib study-result figures under `showcase-analysis/*/attachments/`.
- **Commit** the new PNGs into the same `13-real-analysis-showcase/02-quickstart-screenshots/attachments/` directory as the existing shots, so the Quickstart's relative-path scheme stays uniform. Document the capture + compress recipe (commands, window size, the Kanban toggle step) so every image regenerates, extending the recipe already recorded in that task's `## Results`.

**Validation:** every committed PNG opens and shows its intended view/composition with text legible after quantization; each is meaningfully smaller than before (record before/after sizes); if the Kanban shot was dropped, the reason is recorded.

## Results

Captured the two new dashboard views of the real [showcase-analysis](../../../showcase-analysis/task.md) tree (full chrome, current `HEAD`) and compressed all five dashboard screenshots the Quickstart uses, in place, into the shared [13-real-analysis-showcase/02-quickstart-screenshots/attachments](../../13-real-analysis-showcase/02-quickstart-screenshots/attachments/) directory.

The **Kanban toggle was not brittle** — `showView('kanban')` rendered cleanly via headless Chromium, so the dedicated Kanban shot is kept. The three-task board is sparse (all three cards land in the Approved column at `HEAD`), but it legibly shows the six-column structure and the rollup header, which is what the Quickstart needs to illustrate the board view; `04-rewrite-quickstart` decides how prominently to use it.

**New captures** (full chrome, `--root showcase-analysis`):

| File | View | How captured |
|---|---|---|
| [showcase-task-detail.png](../../13-real-analysis-showcase/02-quickstart-screenshots/attachments/showcase-task-detail.png) | Single task open (`02-analysis`) — Objective with regression equations and Results showing | hash route `#/02-analysis` at `--window-size=1500,1900` (matches the progression shots) |
| [showcase-kanban.png](../../13-real-analysis-showcase/02-quickstart-screenshots/attachments/showcase-kanban.png) | Kanban board — six status columns, three cards in Approved, `3/3 approved` rollup | Playwright `page.evaluate("showView('kanban')")` before screenshot, viewport `1500x560` (tight to the board, no excess whitespace) |

**Compression** (Pillow 256-color MEDIANCUT, in place, filenames unchanged — no markdown/inliner edit needed):

| File | Before | After | Reduction |
|---|---:|---:|---:|
| showcase-after-planning.png | 403,020 | 165,907 | 58.8% |
| showcase-mid-implement.png | 403,696 | 165,125 | 59.1% |
| showcase-complete.png | 433,703 | 177,906 | 59.0% |
| showcase-task-detail.png | 451,973 | 184,151 | 59.3% |
| showcase-kanban.png | 50,992 | 21,610 | 57.6% |

All five reopened and verified legible after quantization (title, status pills, KaTeX equations, card text, column headers all crisp). The matplotlib study-result figures under `showcase-analysis/*/attachments/` were left untouched.

### Regeneration recipe (capture + compress)

Extends the three-state progression recipe in [13-real-analysis-showcase/02-quickstart-screenshots/task.md](../../13-real-analysis-showcase/02-quickstart-screenshots/task.md) `## Results` (which captures the after-planning / mid-implement / complete states from git history via temp detached worktrees). The two new views below capture from current `HEAD`. Run from the repo root.

```bash
ATT="superRA/docs-site/13-real-analysis-showcase/02-quickstart-screenshots/attachments"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Export the study tree once (full chrome, scoped to the showcase-analysis subtree)
uv run --script skills/task-tree/scripts/plan_dashboard.py generate \
  --plan-root superRA --root showcase-analysis \
  --output /tmp/study.html --repo-file-prefix superRA/showcase-analysis

# Task detail — hash route reaches the open task directly
"$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --window-size=1500,1900 --virtual-time-budget=4000 \
  --screenshot="$ATT/showcase-task-detail.png" "file:///tmp/study.html#/02-analysis"

# Kanban — no URL route, so toggle showView('kanban') before the shot (Playwright)
cat > /tmp/kanban_shot.py <<'PY'
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright"]
# ///
import sys
from playwright.sync_api import sync_playwright
html, out = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1500, "height": 560})
    pg.goto(f"file://{html}")
    pg.wait_for_timeout(1500)
    pg.evaluate("showView('kanban')")
    pg.wait_for_timeout(1500)
    pg.screenshot(path=out, full_page=False)
    b.close()
PY
uv run --script /tmp/kanban_shot.py /tmp/study.html "$ATT/showcase-kanban.png"

# Compress all five Quickstart dashboard screenshots in place (filenames unchanged)
uv run --with pillow python - "$ATT" <<'PY'
import sys, os
from PIL import Image
att = sys.argv[1]
for f in ["showcase-after-planning.png","showcase-mid-implement.png","showcase-complete.png",
          "showcase-task-detail.png","showcase-kanban.png"]:
    p = os.path.join(att, f)
    Image.open(p).convert("RGB").quantize(colors=256, method=Image.MEDIANCUT).save(p, optimize=True)
PY
```

Note: Playwright's first run installs Chromium for it (`playwright install chromium`) if not already cached; the headless-Chrome capture for the task-detail shot uses the system Google Chrome directly.
