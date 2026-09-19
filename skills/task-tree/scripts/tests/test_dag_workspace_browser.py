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
    (root / 'config.yaml').write_text('reproduction:\n  code_roots: [code]\n')
    for i in range(4):
        owner = root / f'analysis-{i}'
        owner.mkdir()
        steps = []
        for j in range(4):
            name = f'step-{i}-{j}'
            steps.append({'name': name, 'cmd': f'echo {name}', 'deps': [f'out/{i}-{j-1}.txt'] if j else [], 'outs': [f'out/{i}-{j}.txt']})
        import yaml
        (owner / 'task.md').write_text(f'---\ntitle: Analysis {i} with a readable research question\nstatus: in-progress\n---\n\n## Objective\n\nRead analysis {i}.\n\n## Reproduction\n\n```yaml\n' + yaml.safe_dump({'tier': 'required', 'steps': steps}) + '```\n')
    for path in ('analysis-0/phase-a', 'analysis-0/phase-b', 'analysis-0/phase-a/leaf'):
        owner = root / path
        owner.mkdir(parents=True, exist_ok=True)
        name = path.replace('/', '-')
        (owner / 'task.md').write_text(f'---\ntitle: {path}\nstatus: in-progress\n---\n\n## Objective\n\nInspect nested work.\n\n## Reproduction\n\n```yaml\ntier: required\nsteps:\n  - name: {name}\n    cmd: echo nested\n    outs: [out/{name}.txt]\n```\n')
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
    export = base / 'offline.html'
    export.write_text(dashboard.render_standalone_html(root, output_path=export))
    yield {'url': f'http://127.0.0.1:{port}', 'export': export.as_uri()}
    server.should_exit = True
    thread.join(5)
    dashboard.PLAN_ROOT = previous


def enter(page, url, nav=None):
    url += '#/analysis-0?repro=' + quote(json.dumps(nav or {'roots': [], 'view': 'graph'}))
    page.goto(url)
    page.wait_for_selector('.rp-task')
    page.evaluate('fetchWorktrees()')
    page.evaluate('document.fonts.ready')


def viewport(page):
    return page.evaluate('({..._reproViewport})')


def menu(page, title):
    page.locator('.rp-menu > summary').filter(has_text=title).click()


@pytest.mark.parametrize('width,height', [(1372, 768), (1030, 768), (390, 844)])
def test_preview_selection_full_reader_and_canvas_space(browser, workspace, width, height):
    page = browser.new_page(viewport={'width': width, 'height': height})
    errors = []
    page.on('pageerror', lambda exc: errors.append(str(exc)))
    enter(page, workspace['url'])
    assert not page.locator('#task-preview').is_visible()
    box = page.locator('.repro-canvas').bounding_box()
    assert box['height'] >= height * .45
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.locator('.rp-task-title[data-value="analysis-0"]').click()
    assert not page.locator('#task-preview').is_visible()
    page.locator('[data-rp-action=fold][data-value="analysis-0"]').click()
    # The selection API is also used by search and legacy step links; it must not open the preview.
    page.evaluate("selectReproStep('step-0-0')")
    assert not page.locator('#task-preview').is_visible()
    before = viewport(page)
    page.click('#repro-preview-toggle')
    assert page.locator('#task-preview').is_visible()
    assert 'step-0-0' in page.locator('#repro-detail').inner_text()
    assert viewport(page) == before
    page.locator('[data-rp-action=full-reader]').click()
    assert not page.locator('.repro-canvas').is_visible()
    page.locator('[data-rp-action=close-reader]').click()
    assert page.locator('.repro-canvas').is_visible()
    assert not page.locator('#task-preview').is_visible()
    assert viewport(page) == before
    assert page.locator('#repro-preview-toggle').evaluate('(e)=>e===document.activeElement')
    page.click('#btn-workspace')
    assert page.locator('#task-preview').is_visible()
    page.click('#btn-reproduction')
    assert not page.locator('#task-preview').is_visible()
    assert not errors
    page.close()


def test_wheel_pinch_safari_gestures_and_keyboard_recovery(browser, workspace):
    page = browser.new_page(viewport={'width': 1030, 'height': 768})
    enter(page, workspace['url'])
    canvas = page.locator('.repro-canvas')
    before = viewport(page)
    box = canvas.bounding_box()
    page.mouse.move(box['x'] + 350, box['y'] + 250)
    page.mouse.wheel(90, 120)
    page.wait_for_function('_reproViewport.x === ' + str(before['x'] - 90))
    after = viewport(page)
    assert after['y'] == before['y'] - 120
    assert after['zoom'] == before['zoom']
    assert page.evaluate('scrollY') == 0
    # Dispatch platform events into the installed production listeners. This is not a physical pinch.
    result = canvas.evaluate('''e=>{
      const r=e.getBoundingClientRect(), x=180, y=100;
      const before={..._reproViewport};
      const wheel=new WheelEvent('wheel',{deltaY:-25,ctrlKey:true,clientX:r.left+x,clientY:r.top+y,bubbles:true,cancelable:true});
      e.dispatchEvent(wheel);
      const after={..._reproViewport};
      return {before,after,cancelled:wheel.defaultPrevented,x,y};
    }''')
    assert result['cancelled']
    for axis in ('x', 'y'):
        assert (result[axis] - result['after'][axis]) / result['after']['zoom'] == pytest.approx((result[axis] - result['before'][axis]) / result['before']['zoom'])
    result = canvas.evaluate('''e=>{
      const r=e.getBoundingClientRect(), before={..._reproViewport};
      function gesture(type,scale){const v=new Event(type,{bubbles:true,cancelable:true});Object.assign(v,{scale,clientX:r.left+180,clientY:r.top+100});e.dispatchEvent(v);return v.defaultPrevented;}
      const start=gesture('gesturestart',1), change=gesture('gesturechange',1.4);
      const after={..._reproViewport};
      e.dispatchEvent(new WheelEvent('wheel',{deltaY:-25,ctrlKey:true,cancelable:true}));
      const duplicate={..._reproViewport};
      const end=gesture('gestureend',1.4);
      return {before,after,duplicate,start,change,end};
    }''')
    assert result['start'] and result['change'] and result['end']
    assert result['after']['zoom'] == pytest.approx(result['before']['zoom'] * 1.4)
    assert result['duplicate'] == result['after']
    # Rebinding a preserved canvas after status refresh must not double wheel motion.
    page.evaluate('drawReproView(document.getElementById("view-reproduction"),_reproData)')
    before = viewport(page)
    canvas.dispatch_event('wheel', {'deltaX': 20, 'deltaY': 30, 'deltaMode': 0})
    assert viewport(page)['x'] == before['x'] - 20
    canvas.focus()
    canvas.press('0')
    assert viewport(page)['zoom'] <= 1
    before = viewport(page)
    canvas.press('ArrowRight')
    assert viewport(page)['x'] == before['x'] - 40
    canvas.press('+')
    assert viewport(page)['zoom'] == pytest.approx(before['zoom'] * 1.25)
    page.close()


def test_menus_scope_removal_and_offline_preview(browser, workspace):
    page = browser.new_page(viewport={'width': 1030, 'height': 768})
    enter(page, workspace['url'], {'roots': ['analysis-0', 'analysis-1'], 'view': 'graph'})
    menu(page, 'Graph options')
    page.locator('[data-rp-action=remove-root][data-value="analysis-1"]').click()
    assert page.evaluate('_reproNav.roots') == ['analysis-0']
    menu(page, 'Graph options')
    page.keyboard.press('Escape')
    assert page.locator('.rp-menu[open]').count() == 0
    menu(page, 'Graph options')
    page.locator('.repro-canvas').click(position={'x': 10, 'y': 10})
    assert page.locator('.rp-menu[open]').count() == 0
    page.locator('.rp-task-title[data-value="analysis-0"]').click()
    menu(page, 'Graph options')
    page.locator('[data-rp-action=clear]').click()
    page.locator('.rp-task-title[data-value="analysis-1"]').click()
    menu(page, 'Graph options')
    page.locator('[data-rp-action=focus-selected]').click()
    page.wait_for_function('_reproNav.roots[0] === "analysis-1"')
    assert page.evaluate('activePath') == 'analysis-1'
    page.route('http://**/*', lambda route: route.abort())
    page.route('https://**/*', lambda route: route.abort())
    enter(page, workspace['export'], {'roots': [], 'selected': 'step-0-0', 'view': 'graph'})
    assert not page.locator('#task-preview').is_visible()
    assert page.locator('.repro-node.is-selected').count() == 1
    page.click('#repro-preview-toggle')
    assert page.locator('#task-preview').is_visible()
    assert 'step-0-0' in page.locator('#repro-detail').inner_text()
    page.locator('[data-rp-action=declaration]').click()
    assert page.locator('#workspace.dag-full-reader').count() == 1
    assert page.locator('#active-node [data-section="Reproduction"] .section-content').is_visible()
    heading = page.locator('#active-node [data-section="Reproduction"] > .section-toggle').bounding_box()
    controls = page.locator('#dag-reader-controls').bounding_box()
    assert heading['y'] >= controls['y'] + controls['height']
    back = page.locator('[data-rp-action=full-reader]').bounding_box()
    assert 0 <= back['y'] < 768 - back['height']
    page.locator('[data-rp-action=full-reader]').click()
    assert page.locator('.repro-canvas').is_visible()
    page.close()


@pytest.mark.parametrize('width,height', [(1030, 768), (390, 844)])
def test_diagnostics_stay_inside_graph_with_preview_open_or_closed(browser, workspace, width, height):
    page = browser.new_page(viewport={'width': width, 'height': height})
    def with_findings(route):
        response = route.fetch()
        graph = response.json()
        graph['findings'] = [{'severity': 'error', 'task_path': 'analysis-0', 'message': 'Dependency cycle in the fixture declarations.'}]
        graph['findings'] += [{'severity': 'warning', 'task_path': 'analysis-1', 'message': f'External input {i} needs inspection.'} for i in range(15)]
        route.fulfill(response=response, json=graph)
    page.route('**/api/repro/graph*', with_findings)
    enter(page, workspace['url'])
    for preview in (False, True):
        if preview:
            page.click('#repro-preview-toggle')
        summary = page.locator('.rp-diagnostics > summary')
        assert 'graph blocked' in summary.inner_text()
        assert not page.locator('.rp-diagnostics').evaluate('(e)=>e.open')
        summary.click()
        panel = page.locator('.rp-diagnostics .rp-menu-body').bounding_box()
        graph = page.locator('#view-reproduction').bounding_box()
        assert panel['x'] >= graph['x']
        assert panel['x'] + panel['width'] <= graph['x'] + graph['width']
        assert panel['x'] + panel['width'] <= width
        assert 'Dependency cycle' in page.locator('.repro-findings').inner_text()
        page.keyboard.press('Escape')
    page.close()


def test_branch_expansion_counts_bounds_anchor_and_history(browser, workspace):
    page = browser.new_page(viewport={'width': 1372, 'height': 768})
    enter(page, workspace['url'])
    page.locator('.rp-task-title[data-value="analysis-1"]').click()
    page.locator('[data-rp-action=fold][data-value="analysis-1"]').click()
    page.locator('.rp-task-title[data-value="analysis-0"]').click()
    menu(page, 'Graph options')
    page.locator('[data-rp-action=expand-branch]').click()
    assert page.locator('#repro-branch-depth').input_value() == '2'
    assert '10 cards' in page.locator('#repro-branch-count').inner_text()
    assert 'analysis-0' in page.locator('.rp-branch-path').inner_text()
    page.keyboard.press('Escape')
    assert page.locator('#repro-options-toggle').evaluate('(e)=>e===document.activeElement')
    menu(page, 'Graph options')
    page.locator('[data-rp-action=expand-branch]').click()
    before = page.locator('.rp-task[data-task="analysis-0"]').bounding_box()
    canvas_before = page.locator('.repro-canvas').bounding_box()
    page.locator('[data-rp-action=branch-apply]').click()
    after = page.locator('.rp-task[data-task="analysis-0"]').bounding_box()
    assert page.locator('#repro-options-toggle').evaluate('(e)=>e===document.activeElement')
    assert after['x'] == pytest.approx(before['x'])
    canvas_after = page.locator('.repro-canvas').bounding_box()
    assert after['y'] - canvas_after['y'] == pytest.approx(before['y'] - canvas_before['y'])
    assert 'analysis-1' in page.evaluate('_reproNav.expanded')
    assert page.evaluate('_reproNav.roots') == []
    assert not page.locator('#task-preview').is_visible()
    # A smaller choice genuinely bounds a branch that was previously fully expanded.
    menu(page, 'Graph options')
    page.locator('[data-rp-action=expand-branch]').click()
    page.select_option('#repro-branch-depth', 'all')
    assert '11 cards' in page.locator('#repro-branch-count').inner_text()
    page.locator('[data-rp-action=branch-apply]').click()
    menu(page, 'Graph options')
    page.locator('[data-rp-action=expand-branch]').click()
    page.select_option('#repro-branch-depth', '1')
    assert '7 cards' in page.locator('#repro-branch-count').inner_text()
    page.evaluate('drawReproView(document.getElementById("view-reproduction"),_reproData)')
    assert page.locator('#repro-branch-depth').input_value() == '1'
    page.locator('[data-rp-action=branch-apply]').click()
    assert page.evaluate('_reproNav.expanded') == ['analysis-1', 'analysis-0']
    page.go_back()
    page.wait_for_function('_reproNav.expanded.includes("analysis-0/phase-a/leaf")')
    page.evaluate("reproFocus('analysis-1')")
    page.wait_for_function('_reproNav.roots[0] === "analysis-1"')
    page.evaluate("reproSelectTask('analysis-0')")
    menu(page, 'Graph options')
    page.locator('[data-rp-action=expand-branch]').click()
    assert page.locator('#repro-branch-apply').is_disabled()
    assert 'Focus selected task' in page.locator('#repro-branch-count').inner_text()
    assert page.locator('#repro-branch-count [data-rp-action=focus]').evaluate('(e)=>e===document.activeElement')
    assert page.evaluate('_reproNav.roots') == ['analysis-1']
    page.close()


def test_resized_desktop_preview_fits_phone_with_all_toolbar_controls(browser, workspace):
    page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    enter(page, workspace['url'])
    page.click('#repro-preview-toggle')
    # Native resizing stores an inline pixel width. Keep that state when narrowing the viewport.
    page.locator('#task-preview').evaluate('(e)=>e.style.width="600px"')
    page.set_viewport_size({'width': 390, 'height': 844})
    for selector in ('#task-preview', '[data-rp-action=close-reader]', '.repro-controls > .rp-menu > summary'):
        for box in page.locator(selector).all():
            bounds = box.bounding_box()
            assert bounds['x'] >= 0
            assert bounds['x'] + bounds['width'] <= 390
    reader = page.locator('#task-preview').bounding_box()
    assert reader['y'] >= 0
    assert reader['y'] + reader['height'] <= 844
    assert page.locator('.repro-controls > .rp-menu > summary').first.bounding_box()['y'] > page.locator('#repro-search').bounding_box()['y']
    page.close()
