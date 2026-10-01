"""Rendered DAG navigation and canvas input, using an isolated research fixture.

uv run --with pytest --with playwright --with pyyaml --with fastapi --with jinja2 \
  --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest \
  skills/task-tree/scripts/tests/test_dag_workspace_browser.py
"""
import json
import socket
import sys
import threading
import time
from pathlib import Path
from urllib.parse import quote

import pytest

pytest.importorskip('playwright.sync_api')
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import plan_dashboard as dashboard
import uvicorn


@pytest.fixture(scope='module')
def browser():
    with sync_playwright() as pw:
        chrome = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
        try:
            browser = pw.chromium.launch(**({'executable_path': str(chrome)} if chrome.exists() else {}))
        except Exception as exc:
            pytest.skip(f'Chromium unavailable: {exc}')
        yield browser
        browser.close()


@pytest.fixture(scope='module')
def workspace(tmp_path_factory):
    base = tmp_path_factory.mktemp('dag-workspace')
    root = base / 'superRA'
    root.mkdir()
    (root / 'task.md').write_text('---\ntitle: DAG interaction fixture\nstatus: in-progress\n---\n\n## Objective\n\nInspect dependencies.\n')
    (root / 'config.yaml').write_text('reproduction:\n  runners:\n    sh: sh {script}\n')
    for i in range(4):
        owner = root / f'analysis-{i}'
        owner.mkdir()
        steps = []
        for j in range(4):
            name = f'step-{i}-{j}'
            steps.append({'name': name, 'cmd': f'echo {name}', 'deps': [f'out/{i}-{j-1}.txt'] if j else [], 'outs': [f'out/{i}-{j}.txt']})
        import yaml
        (owner / 'task.md').write_text(f'---\ntitle: Analysis {i} with a readable research question\nstatus: in-progress\n---\n\n## Objective\n\nRead analysis {i}. [Own step](#step-step-{i}-0). [Other step](../analysis-1/task.md#step-step-1-2).\n\n## Reproduction\n\n```yaml\n' + yaml.safe_dump({'steps': steps}) + '```\n')
    for path in ('analysis-0/phase-a', 'analysis-0/phase-b', 'analysis-0/phase-a/leaf'):
        owner = root / path
        owner.mkdir(parents=True, exist_ok=True)
        name = path.replace('/', '-')
        (owner / 'task.md').write_text(f'---\ntitle: {path}\nstatus: in-progress\n---\n\n## Objective\n\nInspect nested work.\n\n## Reproduction\n\n```yaml\nsteps:\n  - name: {name}\n    cmd: echo nested\n    outs: [out/{name}.txt]\n```\n')
    previous = dashboard.PLAN_ROOT
    dashboard.PLAN_ROOT = root
    dashboard.rebuild_tree()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(dashboard.app, host='127.0.0.1', port=port, log_level='error'))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 15
    while not server.started:
        assert time.monotonic() < deadline, 'Fixture server did not start'
        time.sleep(.05)
    yield {'url': f'http://127.0.0.1:{port}'}
    server.should_exit = True
    thread.join(5)
    dashboard.PLAN_ROOT = previous


def enter(page, url, nav=None):
    url += '#/analysis-0?repro=' + quote(json.dumps(nav or {'roots': [], 'view': 'graph'}))
    page.goto(url)
    page.wait_for_selector('.rp-task')
    page.evaluate('fetchWorktrees()')
    page.evaluate('document.fonts.ready')


def test_dag_renders_and_selection_works(browser, workspace):
    page = browser.new_page(viewport={'width': 1372, 'height': 768})
    enter(page, workspace['url'])
    assert page.locator('.rp-task').count() >= 4
    page.locator('[data-rp-action=fold][data-value="analysis-0"]').click()
    page.wait_for_selector('#repro-node-step-0-0')
    page.locator('#repro-node-step-0-0').dispatch_event('click')
    assert page.evaluate('_reproSelected') == 'step-0-0'
    assert 'step-0-0' in page.locator('#repro-detail').inner_text()
    assert not page.locator('#repro-notice').inner_text()
    page.close()


def test_build_menu_and_explain_card(browser, workspace):
    page = browser.new_page(viewport={'width': 1372, 'height': 768})
    enter(page, workspace['url'])
    page.locator('[data-rp-action=fold][data-value="analysis-1"]').click()
    page.wait_for_selector('#repro-node-step-1-0')
    chip = page.locator('.rp-task[data-task="analysis-1"] .rp-build-chip')
    assert chip.evaluate('el => getComputedStyle(el).opacity') == '0'
    page.locator('.rp-task[data-task="analysis-1"] .rp-task-head').hover()
    page.wait_for_function('el => getComputedStyle(el).opacity === "1"', arg=chip.element_handle())
    chip.click()
    menu = page.locator('#rp-build-menu')
    assert [menu.locator('[role=menuitem] .rp-build-label').nth(i).inner_text() for i in range(3)] == [
        'Build this task', 'Build with upstream', 'Rebuild all']
    assert 'superra repro build analysis-1 --upstream' in menu.inner_text()
    assert '4 steps would run' in menu.locator('[data-mode=""]').inner_text()
    page.keyboard.press('Escape')
    assert page.locator('#rp-build-menu').count() == 0
    page.locator('#repro-node-step-1-0').hover()
    page.wait_for_selector('#rp-explain-card .rp-explain-body section, #rp-explain-card .rp-explain-body .repro-hint:not(:has-text("Loading"))')
    assert 'step-1-0' in page.locator('#rp-explain-card').inner_text()
    page.mouse.move(2, 2)
    page.wait_for_selector('#rp-explain-card', state='detached')
    page.locator('.rp-task[data-task="analysis-2"] .rp-task-summary').hover()
    page.wait_for_selector('#rp-explain-card[data-target="analysis-2"]')
    assert '4 of 4 steps not fresh' in page.locator('#rp-explain-card').inner_text()
    step_chip = page.locator('#repro-node-step-1-0 + .rp-build-chip-step')
    assert step_chip.get_attribute('data-value') == 'analysis-1#step-1-0'
    page.close()

