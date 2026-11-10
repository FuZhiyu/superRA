"""Rendered DAG navigation and canvas input, using an isolated research fixture.

uv run --script tests/run_tests.py \
  skills/task-tree/scripts/tests/test_dag_workspace_browser.py
"""
import json
import socket
import sys
import threading
import time
from pathlib import Path
from urllib.parse import quote, unquote

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
            deps = [f'out/{i}-{j-1}.txt'] if j else ['out/1-3.txt'] if i == 3 else []
            steps.append({'name': name, 'cmd': f'echo {name}', 'deps': deps, 'outs': [f'out/{i}-{j}.txt']})
        import yaml
        prerequisite = 'depends_on: [analysis-1]\n' if i == 2 else ''
        status = {1: 'revise', 2: 'implemented'}.get(i, 'in-progress')
        (owner / 'task.md').write_text(f'---\ntitle: Analysis {i} with a readable research question\nstatus: {status}\n{prerequisite}---\n\n## Objective\n\nRead analysis {i}. [Own step](#step-step-{i}-0). [Other step](../analysis-1/task.md#step-step-1-2).\n\n## Reproduction\n\n```yaml\n' + yaml.safe_dump({'steps': steps}) + '```\n')
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
        'Build with producers', 'Build only this task', 'Force rebuild this task']
    assert 'superra repro build analysis-1 --only' in menu.inner_text()
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




def faded(page, selector):
    return sorted(page.eval_on_selector_all(selector, 'els => els.map(e => e.dataset.step || e.dataset.task)'))


def test_selection_traces_dependencies_and_the_filter_keeps_them(browser, workspace):
    page = browser.new_page(viewport={'width': 1372, 'height': 768})
    enter(page, workspace['url'], {'layout': 'graph', 'expanded': ['analysis-1', 'analysis-2', 'analysis-3']})
    page.wait_for_selector('#repro-node-step-1-3')
    page.evaluate("""() => { window._layouts = 0; const layout = reproHierarchyLayout;
      reproHierarchyLayout = m => { window._layouts++; return layout(m); }; }""")
    page.locator('#repro-node-step-1-3').dispatch_event('click')
    assert faded(page, '.has-lineage .repro-node:not(.in-lineage)') == [f'step-2-{j}' for j in range(4)]
    assert faded(page, '.has-lineage .rp-task:not(.in-lineage)') == ['analysis-0', 'analysis-2']
    assert page.locator('#repro-step-count').inner_text().startswith('Dependencies of step-1-3: 8 of 19 steps')
    page.locator('.rp-task-title[data-value="analysis-1"]').dispatch_event('click')
    assert faded(page, '.has-lineage .repro-node:not(.in-lineage)') == []
    assert faded(page, '.has-lineage .rp-task:not(.in-lineage)') == ['analysis-0']
    assert '12 of 19 steps' in page.locator('#repro-step-count').inner_text()
    assert page.evaluate('window._layouts') == 0, 'selection restyles in place'
    page.locator('.rp-legend-menu summary').click()
    assert page.locator('.rp-legend-menu .repro-legend-item.rp-missing .repro-count').inner_text() == '12'

    page.locator('#active-node .lineage-btn').click()
    page.wait_for_function("!document.querySelector('.rp-task[data-task=\"analysis-0\"]')")
    assert chips(page) == ['Dependencies of Analysis 1 with a readable research question']
    assert page.locator('#filter-trigger').inner_text() == 'Filter · 1'
    page.reload()
    page.wait_for_selector('#repro-node-step-1-3')
    assert page.locator('.rp-task[data-task="analysis-0"]').count() == 0
    page.locator('#btn-workspace').click()
    page.wait_for_function("document.querySelector('#nav-tree .task-node[data-path=analysis-2]\')")
    assert matched(page) == ['analysis-1', 'analysis-2', 'analysis-3']
    page.locator('.wf-chip-dir').click()
    assert chips(page) == ['Upstream of Analysis 1 with a readable research question']
    assert matched(page) == ['analysis-1']
    page.locator('.wf-clear').click()
    assert page.locator('#workspace-filter-bar').is_hidden()
    assert page.locator('#nav-tree .task-node[data-path="analysis-0"]').is_visible()
    assert 'filters' not in unquote(page.url)
    page.close()


def chips(page):
    return [label.removeprefix('Edit ') for label in page.eval_on_selector_all('.wf-chip-edit', 'els => els.map(e => e.getAttribute("aria-label"))')]


def matched(page):
    """Task paths the Tree shows as matches, not context; the root excluded."""
    return sorted(page.eval_on_selector_all('#nav-tree .task-node', """els => els.filter(e => e.dataset.path
      && !e.classList.contains('filter-context') && !e.closest('.task-node[style*="none"]')).map(e => e.dataset.path)"""))


def graph_steps(page):
    return sorted(page.eval_on_selector_all('.repro-node[data-step]', 'els => els.map(e => e.dataset.step)'))


def varied_states(route):
    """Serve every step `missing` except a stale chain in analysis-1, one fresh, and one failed step."""
    response = route.fetch()
    data = response.json()
    states = {'step-1-0': ('stale', 'stale'), 'step-1-1': ('stale', 'fresh'), 'step-2-0': ('fresh', 'fresh'), 'step-3-0': ('failed', 'failed')}
    for entry in data['steps']:
        if entry['name'] in states:
            entry['status'], entry['local_status'] = states[entry['name']]
    route.fulfill(response=response, json=data)


def show_graph(page, expanded):
    page.locator('#btn-reproduction').click()
    page.evaluate(f"reproNavigate({{expanded:{json.dumps(expanded)}}},false)")
    page.wait_for_function('!!document.querySelector(".repro-node[data-step]")')
    steps = graph_steps(page)
    page.locator('#btn-workspace').click()
    return steps


def open_add(page):
    bar_add = page.locator('#filter-add')
    (bar_add if bar_add.is_visible() else page.locator('#filter-trigger')).click()
    page.wait_for_selector('#wf-pop .wf-pop-search')


def test_filter_bar_facets_filter_tree_and_graph(browser, workspace):
    page = browser.new_page(viewport={'width': 1372, 'height': 768})
    page.route('**/api/repro/status*', varied_states)
    page.goto(workspace['url'] + '#/analysis-0')
    page.wait_for_function('!!_reproData && document.querySelector("#nav-tree .task-node[data-path=analysis-3]")')
    assert page.locator('#workspace-filter-bar').is_hidden()

    # Task status: a typed value, then the editor's only, group, and is-not controls.
    open_add(page)
    page.keyboard.type('revis')
    page.keyboard.press('Enter')
    assert chips(page) == ['Status is revise'] and matched(page) == ['analysis-1']
    assert show_graph(page, ['analysis-0', 'analysis-1']) == [f'step-1-{j}' for j in range(4)], 'Graph keeps only matching tasks'
    page.locator('[data-wf-edit=status]').click()
    row = page.locator('#wf-pop .wf-row:has([data-wf-value="status|implemented"])')
    assert row.locator('.wf-cnt').inner_text() == '1', 'counts ignore the facet being edited'
    row.hover()
    row.locator('.wf-only').click()
    assert chips(page) == ['Status is implemented'] and matched(page) == ['analysis-2']
    page.locator('[data-wf-group="status|not-started,in-progress,revise"]').click()
    assert chips(page) == ['Status is any of implemented, in-progress, not-started +1']
    page.locator('[data-wf-neg=true]').click()
    assert chips(page)[0].startswith('Status is not') and 'analysis-1' not in matched(page)
    page.keyboard.press('Escape')
    page.locator('[data-wf-remove=status]').click()
    assert page.locator('#workspace-filter-bar').is_hidden()

    # Step state: the group toggle, then one value; a typed state adds another. Inherited staleness matches stale.
    open_add(page)
    page.locator('#wf-pop [data-wf-item]:has-text("Step state")').click()
    attention = page.locator('[data-wf-group="steps|stale,missing,failed"]')
    attention.click()
    assert chips(page) == ['Steps are stale, missing, failed'] and attention.inner_text() == 'none'
    attention.click()
    assert page.locator('#workspace-filter-bar').is_hidden() and attention.inner_text() == 'all'
    page.locator('input[data-wf-value="steps|stale"]').check()
    assert chips(page) == ['Steps are stale'] and matched(page) == ['analysis-1']
    assert page.locator('#workspace-filter-bar .wf-count').inner_text() == '1 of 8 tasks · 2 of 19 steps'
    page.keyboard.press('Escape')
    open_add(page)
    page.keyboard.type('failed')
    page.keyboard.press('Enter')
    assert chips(page) == ['Steps are stale, failed'] and matched(page) == ['analysis-1', 'analysis-3']
    page.locator('#btn-reproduction').click()
    page.evaluate("reproNavigate({expanded:['analysis-1','analysis-3']},false)")
    page.wait_for_selector('#repro-node-step-3-0')
    assert graph_steps(page) == ['step-1-0', 'step-1-1', 'step-3-0']
    page.locator('#btn-workspace').click()
    page.locator('.wf-clear').click()

    # Task subtree: a typed task adds an In chip; the not-under switch edits a separate Not in list.
    open_add(page)
    page.keyboard.type('Analysis 0')
    page.keyboard.press('Enter')
    assert chips(page) == ['In Analysis 0 with a readable research question']
    assert matched(page) == ['analysis-0', 'analysis-0/phase-a', 'analysis-0/phase-a/leaf', 'analysis-0/phase-b']
    page.locator('[data-wf-edit=scope-in]').click()
    assert page.locator('input[data-wf-scope="analysis-0/phase-a"]').is_disabled()
    page.locator('[data-wf-scope-list=out]').click()
    page.locator('input[data-wf-scope="analysis-0/phase-a"]').check()
    assert chips(page) == ['In Analysis 0 with a readable research question', 'Not in analysis-0/phase-a']
    assert matched(page) == ['analysis-0', 'analysis-0/phase-b']
    page.keyboard.press('Escape')
    assert show_graph(page, ['analysis-0', 'analysis-0/phase-a', 'analysis-0/phase-b']) == ['analysis-0-phase-b'] + [f'step-0-{j}' for j in range(4)]
    page.locator('[data-wf-remove=scope-in]').click()
    assert chips(page) == ['Not in analysis-0/phase-a'] and matched(page) == ['analysis-0', 'analysis-0/phase-b', 'analysis-1', 'analysis-2', 'analysis-3']
    page.locator('[data-wf-edit=scope-out]').click()
    assert page.locator('[data-wf-scope-list=out]').get_attribute('aria-pressed') == 'true', 'a Not in chip opens on its own list'
    page.keyboard.press('Escape')
    page.locator('.wf-clear').click()
    open_add(page)
    page.keyboard.type('Analysis 3')
    page.locator('#wf-pop [data-wf-in="analysis-3"]').click()
    assert chips(page) == ['In Analysis 3 with a readable research question'] and matched(page) == ['analysis-3']
    page.locator('.wf-clear').click()

    # Dependencies: the picker anchors a step without typing; the chip's arrow cycles its direction.
    open_add(page)
    page.locator('#wf-pop [data-wf-item]:has-text("Dependencies of")').click()
    page.locator('[data-wf-depdir=up]').click()
    page.locator('[data-wf-pick="step|step-1-3"]').click()
    assert chips(page) == ['Upstream of step-1-3'] and matched(page) == ['analysis-1']
    page.locator('.wf-chip-dir').click()
    assert chips(page) == ['Downstream of step-1-3'] and matched(page) == ['analysis-1', 'analysis-3']
    assert 'filter-context' in page.locator('#nav-tree .task-node[data-path=""]').get_attribute('class'), 'the root is context'
    page.locator('[data-wf-edit="lineage:0"]').click()
    page.locator('[data-wf-setdir=up]').click()
    assert chips(page) == ['Upstream of step-1-3'] and matched(page) == ['analysis-1']
    page.locator('[data-wf-setdir=down]').click()
    page.keyboard.press('Escape')
    open_add(page)
    page.keyboard.type('Analysis 2')
    page.keyboard.press('Shift+Enter')
    assert chips(page) == ['Downstream of step-1-3', 'Dependencies of Analysis 2 with a readable research question']

    page.reload()
    page.wait_for_function('!!_reproData')
    assert chips(page) == ['Downstream of step-1-3', 'Dependencies of Analysis 2 with a readable research question']
    page.locator('.wf-clear').click()
    assert page.evaluate('location.hash').find('filters') == -1
    page.close()


def test_legacy_filter_hashes_load(browser, workspace):
    page = browser.new_page(viewport={'width': 1372, 'height': 768})
    legacy = {'layout': 'tree', 'filters': {'statuses': ['revise'], 'tasks': None, 'lineage': {'anchors': [{'task': 'analysis-1'}], 'direction': 'up'}}}
    page.goto(workspace['url'] + '#/analysis-0?repro=' + quote(json.dumps(legacy)))
    page.wait_for_function('!!_reproData')
    assert chips(page) == ['Status is revise', 'Upstream of Analysis 1 with a readable research question']
    everything_but_analysis_0 = ['', 'analysis-1', 'analysis-2', 'analysis-3']
    page.goto(workspace['url'] + '#/analysis-1?repro=' + quote(json.dumps({'layout': 'tree', 'filters': {'tasks': everything_but_analysis_0}})))
    page.wait_for_function('document.querySelectorAll(".wf-chip").length === 1')
    assert chips(page) == ['Not in Analysis 0 with a readable research question']
    assert matched(page) == ['analysis-1', 'analysis-2', 'analysis-3']
    page.close()


def test_tree_row_menu_by_mouse_and_keyboard(browser, workspace):
    page = browser.new_page(viewport={'width': 1372, 'height': 768})
    page.goto(workspace['url'] + '#/analysis-0')
    page.wait_for_function('!!_reproData && document.querySelector("#nav-tree .task-node[data-path=analysis-1]")')
    row = page.locator('#nav-tree .task-node[data-path="analysis-1"] > .task-row')
    row.click(button='right')
    menu = page.locator('#row-menu[role=menu]')
    assert menu.locator('[role=menuitem]').all_text_contents() == ['⊂Show only this subtree', '⊄Hide this subtree',
        '⇡Show what it depends onupstream', '⇣Show what depends on itdownstream', '⇅Show both directions', '↗Open task']
    assert page.evaluate('document.activeElement.dataset.rowAction') == 'in'
    page.keyboard.press('ArrowDown')
    assert page.evaluate('document.activeElement.dataset.rowAction') == 'out'
    page.keyboard.press('Escape')
    assert menu.count() == 0 and page.evaluate('document.activeElement.closest(".task-node").dataset.path') == 'analysis-1'

    more = row.locator('.task-row-more')
    page.evaluate('document.activeElement.blur()')
    page.mouse.move(700, 700)
    assert more.is_hidden()
    width = row.locator('.badge').bounding_box()['x']
    row.hover()
    assert more.is_visible() and row.locator('.badge').bounding_box()['x'] == width, 'the ⋯ overlays the row end'
    more.click()
    assert 'is-sheet' not in menu.get_attribute('class') and more.get_attribute('aria-expanded') == 'true'
    menu.locator('[data-row-action=out]').click()
    assert chips(page) == ['Not in Analysis 1 with a readable research question'] and 'analysis-1' not in matched(page)
    page.locator('.wf-clear').click()

    # Hiding inside an In subtree keeps the In chip and the hidden leaf's parent.
    page.locator('#nav-tree .task-node[data-path="analysis-0"] > .task-row').click(button='right')
    menu.locator('[data-row-action=in]').click()
    page.evaluate("restoreExpandedNavPaths(['analysis-0', 'analysis-0/phase-a'])")
    page.locator('#nav-tree .task-node[data-path="analysis-0/phase-a/leaf"] > .task-row').click(button='right')
    menu.locator('[data-row-action=out]').click()
    assert chips(page) == ['In Analysis 0 with a readable research question', 'Not in analysis-0/phase-a/leaf']
    assert matched(page) == ['analysis-0', 'analysis-0/phase-a', 'analysis-0/phase-b']
    page.locator('.wf-clear').click()

    row.focus()
    page.keyboard.press('Shift+F10')
    for _ in range(2):
        page.keyboard.press('ArrowDown')
    page.keyboard.press('Enter')
    assert chips(page) == ['Upstream of Analysis 1 with a readable research question']
    page.locator('.wf-clear').click()

    page.locator('#nav-tree .task-node[data-path=""] > .task-row').click(button='right')
    assert menu.locator('[data-row-action]').evaluate_all('els => els.map(e => e.dataset.rowAction)') == ['in', 'out', 'open'], \
        'the project root offers no dependency items'
    page.keyboard.press('Escape')
    page.close()


def test_tree_row_menu_on_touch(browser, workspace):
    context = browser.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True)
    page = context.new_page()
    page.goto(workspace['url'] + '#/analysis-0')
    page.wait_for_function('!!_reproData && document.querySelector("#nav-tree .task-node[data-path=analysis-2]")')
    cdp = context.new_cdp_session(page)
    row = page.locator('#nav-tree .task-node[data-path="analysis-2"] > .task-row')
    more = row.locator('.task-row-more')
    assert more.is_visible(), 'touch has no hover, so the ⋯ always shows'
    hit = more.evaluate('el => { const s = getComputedStyle(el, "::before"); return el.offsetWidth - parseFloat(s.left) - parseFloat(s.right); }')
    assert hit >= 44

    def press(dx=0, hold=700):
        box = row.locator('.badge').bounding_box()
        x, y = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x, 'y': y}]})
        if dx:
            cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x + dx, 'y': y}]})
        page.wait_for_timeout(hold)
        cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        page.wait_for_timeout(100)

    press()
    sheet = page.locator('#row-menu.is-sheet')
    assert sheet.is_visible() and 'analysis-2' in sheet.locator('.row-menu-path').inner_text()
    assert page.evaluate('activePath') == 'analysis-0', 'the touch ending a long-press does not open the task'
    sheet.locator('[data-row-action=cancel]').tap()
    page.wait_for_selector('#row-menu', state='detached')

    press(dx=30)
    assert page.locator('#row-menu').count() == 0, 'moving cancels the long-press'

    more.tap()
    assert sheet.is_visible()
    page.locator('.row-menu-backdrop').tap(position={'x': 20, 'y': 20})
    page.wait_for_selector('#row-menu', state='detached')

    row.locator('.badge').tap()
    page.wait_for_function('activePath === "analysis-2"')
    context.close()


def test_five_chips_never_overflow_the_page(browser, workspace):
    nav = {'layout': 'tree', 'filters': {'status': {'neg': True, 'values': ['archived', 'postponed']}, 'steps': ['failed', 'missing', 'stale'],
           'scope': {'in': ['analysis-0', 'analysis-1'], 'out': ['analysis-0/phase-a']}, 'lineage': [{'task': 'analysis-1', 'direction': 'up'}]}}
    for width in (390, 768, 1440):
        for theme in ('light', 'dark'):
            page = browser.new_page(viewport={'width': width, 'height': 800})
            page.add_init_script(f'localStorage.setItem("dashboard-theme", "{theme}")')
            page.goto(workspace['url'] + '#/analysis-1?repro=' + quote(json.dumps(nav)))
            page.wait_for_function('!!_reproData && document.querySelectorAll(".wf-chip").length === 5')
            overflow = page.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
            assert overflow <= 0, f'{width}px {theme}: {overflow}px horizontal overflow'
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


def test_project_markdown_resolves_against_its_own_folder(browser, workspace):
    notes = workspace['base'] / 'notes'
    notes.mkdir(exist_ok=True)
    (notes / 'README.md').write_text('# Notes\n\n![fig](fig.png)\n\n[table](table.csv#L2)\n')
    (notes / 'table.csv').write_text('a\n1\n')
    page = browser.new_page(viewport={'width': 1372, 'height': 768})
    remote(page)
    page.goto(workspace['url'] + '#/analysis-0?file=notes%2FREADME.md')
    page.wait_for_selector('#active-node .rendered-md img')
    assert page.locator('#active-node .rendered-md img').get_attribute('src').startswith('/files/notes/fig.png')
    link = page.locator('#active-node .rendered-md a:has-text("table")')
    assert link.get_attribute('data-file-page') == 'notes/table.csv'
    page.close()


def test_standalone_export_keeps_editor_links(browser, tmp_path):
    root = tmp_path / 'superRA'
    (root / 'a').mkdir(parents=True)
    (root / 'task.md').write_text('---\ntitle: Export\nstatus: in-progress\n---\n\n## Objective\n\nx\n')
    (root / 'a' / 'task.md').write_text('---\ntitle: A\nstatus: in-progress\n---\n\n## Objective\n\n[table](../../figs/t.csv)\n')
    out = dashboard.generate_dashboard(root)
    page = browser.new_page()
    page.goto(out.as_uri() + '#/a')
    link = page.locator('#active-node a:has-text("table")')
    link.wait_for()
    assert link.get_attribute('href').startswith('vscode://file/')
    assert link.get_attribute('data-file-page') is None and link.get_attribute('data-peek') is None
    page.close()
