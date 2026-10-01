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
    yield {'url': f'http://127.0.0.1:{port}', 'base': base}
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
    page.mouse.move(2, 2)
    page.evaluate('document.activeElement.blur()')  # the fold toggle keeps focus, which reveals the chip
    page.wait_for_function('el => getComputedStyle(el).opacity === "0"', arg=chip.element_handle())
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



def _tiny_pdf():
    objs = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
            b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 100] /Contents 4 0 R >>']
    draw = b'0 0 1 rg 20 20 160 60 re f'
    objs.append(b'<< /Length %d >>\nstream\n%s\nendstream' % (len(draw), draw))
    out, offsets = bytearray(b'%PDF-1.4\n'), []
    for i, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += b'%d 0 obj\n%s\nendobj\n' % (i, body)
    xref = len(out)
    out += b'xref\n0 %d\n0000000000 65535 f \n' % (len(objs) + 1) + b''.join(b'%010d 00000 n \n' % o for o in offsets)
    out += b'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objs) + 1, xref)
    return bytes(out)


def test_file_hover_preview(browser, workspace):
    figs = workspace['base'] / 'figs'
    figs.mkdir(exist_ok=True)
    (figs / 'table.csv').write_text('year,ret\n2001,0.10\n')
    (figs / 'fig.pdf').write_bytes(_tiny_pdf())
    page = browser.new_page(viewport={'width': 1372, 'height': 768})
    enter(page, workspace['url'])
    page.locator('[data-rp-action=fold][data-value="analysis-0"]').click()
    page.wait_for_selector('#repro-node-step-0-0')
    page.locator('#repro-node-step-0-0').dispatch_event('click')
    output = page.locator('#repro-detail [data-peek="out/0-0.txt"]')
    output.hover()
    page.wait_for_selector('#file-peek :text("Not built yet")')
    page.evaluate("""() => ['figs/table.csv', 'figs/fig.pdf'].forEach(path => {
      const a = document.createElement('a'); a.href = '#'; a.textContent = path; a.dataset.peek = path; a.style.display = 'block';
      document.querySelector('#repro-detail').prepend(a); })""")
    page.locator('[data-peek="figs/table.csv"]').hover()
    page.wait_for_selector('#file-peek .file-peek-text:has-text("2001,0.10")')
    assert page.evaluate('_pdfjs') is None
    page.locator('[data-peek="figs/fig.pdf"]').hover()
    page.wait_for_selector('#file-peek img[src^="data:image/png"]')
    page.mouse.move(2, 2)
    page.wait_for_selector('#file-peek', state='detached')
    page.close()


def test_task_body_file_links_preview_on_hover(browser, workspace):
    figs = workspace['base'] / 'figs'
    figs.mkdir(exist_ok=True)
    (figs / 'table.csv').write_text('year,ret\n2001,0.10\n')
    page = browser.new_page(viewport={'width': 1372, 'height': 768})
    enter(page, workspace['url'])
    page.evaluate("""() => { const div = document.createElement('div');
      div.innerHTML = renderMarkdown('[table](../../figs/table.csv#L2)', null, 'analysis-0');
      div.style.cssText = 'position:relative;z-index:999;background:#fff';
      document.body.prepend(div); }""")
    link = page.locator('a:has-text("table")').first
    assert link.get_attribute('data-peek') == 'figs/table.csv'
    link.hover()
    page.wait_for_selector('#file-peek .file-peek-text:has-text("2001,0.10")')
    page.close()


def remote(page):
    """Serve the page as a browser on another machine sees it."""
    def rewrite(route):
        if route.request.resource_type != 'document':
            return route.continue_()
        response = route.fetch()
        route.fulfill(response=response, body=response.text().replace('window.LOCAL_OPEN = true', 'window.LOCAL_OPEN = false'))
    page.route('**/*', rewrite)


def test_remote_file_links_open_the_reading_pane(browser, workspace):
    figs = workspace['base'] / 'figs'
    figs.mkdir(exist_ok=True)
    (figs / 'big.csv').write_text('year,ret\n' + '2001,0.10\n' * 300_000)
    (figs / 'fig.pdf').write_bytes(_tiny_pdf())
    context = browser.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True)
    page = context.new_page()
    remote(page)
    enter(page, workspace['url'])
    assert page.evaluate('window.LOCAL_OPEN') is False
    page.locator('[data-rp-action=fold][data-value="analysis-0"]').click()
    page.wait_for_selector('#repro-node-step-0-0')
    page.locator('#repro-node-step-0-0').dispatch_event('click')
    link = page.locator('#repro-detail [data-peek="out/0-0.txt"]')
    assert link.get_attribute('href') == '#/analysis-0?file=out%2F0-0.txt'
    link.tap()
    page.wait_for_selector('#active-node :text("Not built yet.")')
    assert page.locator('#file-peek').count() == 0
    assert 'file=out%2F0-0.txt' in page.url and page.evaluate('_reproSelected') == ''
    page.goto(workspace['url'] + '#/analysis-0?file=figs%2Fbig.csv')
    page.wait_for_selector('#active-node :text("Showing the first")')
    assert page.locator('#active-node pre').inner_text().startswith('year,ret')
    page.goto(workspace['url'] + '#/analysis-0?file=figs%2Ffig.pdf')
    page.wait_for_selector('#active-node iframe.artifact-pdf-preview')
    assert page.locator('#active-node iframe').get_attribute('src').startswith('/files/figs/fig.pdf?v=')
    page.locator('.attachment-owner-action').tap()
    page.wait_for_function("location.hash.indexOf('file=') === -1")
    context.close()
