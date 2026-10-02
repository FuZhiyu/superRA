"""Screenshot the Graph and the Tree, light and dark, on the every-state fixture.

uv run --with pytest --with playwright --with pyyaml --with fastapi --with jinja2 \
  --with 'uvicorn[standard]' --with watchfiles --with httpx \
  python superRA/reproducibility/11-local-builds/03-state-display/attachments/screenshots.py [OUT_DIR]

Builds the fixture from tests/test_repro_states_browser.py in a temp dir and
writes graph-, legend-, tree- and panel-{light,dark}.png, then build-menu.png
and build-gate.png (light), to OUT_DIR (default: this attachments folder).
"""
import json
import socket
import sys
import tempfile
import threading
import time
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parents[4] / 'skills/task-tree/scripts'
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / 'tests')]

import plan_dashboard as dashboard  # noqa: E402
import uvicorn  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
from test_repro_states_browser import TASKS, build_state_fixture, simulate_online_only  # noqa: E402


ROW_ORDER = "Array.from(document.querySelectorAll('#nav-tree .task-node')).map(n => n.dataset.path)"


def serve(root: Path) -> str:
    dashboard.PLAN_ROOT = root
    dashboard.rebuild_tree()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(dashboard.app, host='127.0.0.1', port=port, log_level='error'))
    threading.Thread(target=server.run, daemon=True).start()
    while not server.started:
        time.sleep(.05)
    return f'http://127.0.0.1:{port}'


def main(out: Path) -> None:
    base = Path(tempfile.mkdtemp())
    root = build_state_fixture(base)
    simulate_online_only(base)
    url = serve(root)
    tasks = list(TASKS)
    graph = {'layout': 'graph', 'expanded': tasks, 'selected': 'vendor-join'}
    tree = {'layout': 'tree', 'expanded': [], 'selected': 'vendor-join'}
    with sync_playwright() as pw:
        chrome = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
        browser = pw.chromium.launch(**({'executable_path': str(chrome)} if chrome.exists() else {}))
        for theme in ('light', 'dark'):
            context = browser.new_context(viewport={'width': 1500, 'height': 1250}, device_scale_factor=2)
            context.add_init_script(f"localStorage.setItem('dashboard-theme', '{theme}')")
            page = context.new_page()
            page.goto(f'{url}/#/?repro=' + quote(json.dumps(graph)))
            page.wait_for_selector('.repro-node')
            page.evaluate('document.fonts.ready')
            page.evaluate('reproSetReader(false); reproFit()')
            page.wait_for_timeout(400)
            page.screenshot(path=str(out / f'graph-{theme}.png'))
            page.locator('[data-rp-menu=legend] > summary').click()
            page.wait_for_timeout(300)
            page.locator('[data-rp-menu=legend] .rp-menu-body').screenshot(path=str(out / f'legend-{theme}.png'))
            page.evaluate('reproSetReader(true)')
            page.close()
            # Sidebar rows sometimes land out of order (a pre-existing bug); reload until they read in tree order.
            page = context.new_page()
            page.set_viewport_size({'width': 1440, 'height': 900})
            for _ in range(5):
                page.goto(f'{url}/#/02-panel-model?repro=' + quote(json.dumps(tree)))
                page.reload()
                page.wait_for_selector('#repro-detail .repro-status-line')
                page.wait_for_timeout(500)
                if page.evaluate(ROW_ORDER) == ['', *tasks]:
                    break
            else:
                raise SystemExit('sidebar rows stayed out of order')
            page.evaluate("document.querySelectorAll('#nav-tree .task-node').forEach(n => { const c = n.querySelector(':scope > .task-children'); if (c) c.style.display = ''; })")
            page.evaluate("document.querySelectorAll('#repro-detail details').forEach(d => d.open = true)")
            page.wait_for_timeout(400)
            page.screenshot(path=str(out / f'tree-{theme}.png'))
            page.wait_for_function("document.querySelector('#repro-detail li.is-online-only')")
            page.evaluate("document.querySelector('#repro-detail li.is-online-only').scrollIntoView({block: 'center'})")
            page.wait_for_timeout(300)
            page.screenshot(path=str(out / f'panel-{theme}.png'))
            context.close()
        # The Build menu, then the download gate: `figures` reads Data/codebook.csv, now absent with no producer.
        page = browser.new_page(viewport={'width': 1440, 'height': 700}, device_scale_factor=2)
        page.goto(f'{url}/#/?repro=' + quote(json.dumps(graph)))
        page.wait_for_selector('.repro-node')
        page.evaluate("reproOpenBuildMenu(document.querySelector('.rp-task[data-task=\"02-panel-model\"] .rp-build-chip'))")
        page.wait_for_selector('#rp-build-menu')
        page.locator('#rp-build-menu').screenshot(path=str(out / 'build-menu.png'))
        (base / 'Data/codebook.csv').unlink()
        page.evaluate("reproStartBuild('02-panel-model#figures', 'only')")
        page.wait_for_selector('.rp-build-detail', timeout=60000)
        page.locator('.repro-summary').screenshot(path=str(out / 'build-gate.png'))
        page.close()
        browser.close()


if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else HERE)
