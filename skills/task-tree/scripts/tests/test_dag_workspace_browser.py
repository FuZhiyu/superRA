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
        (owner / 'task.md').write_text(f'---\ntitle: Analysis {i} with a readable research question\nstatus: in-progress\n---\n\n## Objective\n\nRead analysis {i}. [Own step](#step-step-{i}-0). [Other step](../analysis-1/task.md#step-step-1-2).\n\n## Reproduction\n\n```yaml\n' + yaml.safe_dump({'tier': 'required', 'steps': steps}) + '```\n')
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


@pytest.mark.parametrize('width,height', [(1372, 768), (1030, 768), (390, 844), (820, 1180)])
def test_preview_selection_full_reader_and_canvas_space(browser, workspace, width, height):
    page = browser.new_page(viewport={'width': width, 'height': height})
    errors = []
    page.on('pageerror', lambda exc: errors.append(str(exc)))
    enter(page, workspace['url'])
    assert page.locator('#task-preview').is_visible(), page.evaluate('({height:document.getElementById("workspace").clientHeight,bounds:reproPaneBounds()})')
    graph=page.locator('#view-reproduction').bounding_box();reader=page.locator('#task-preview').bounding_box()
    assert (reader['x'] >= graph['x']+graph['width']) if width>=1100 else (reader['y'] >= graph['y']+graph['height'])
    page.click('#repro-preview-toggle')
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
    if page.locator('#task-preview').is_visible(): page.click('#repro-preview-toggle')
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


def test_overview_legacy_links_and_offline_preview(browser, workspace):
    page = browser.new_page(viewport={'width': 1030, 'height': 768})
    enter(page, workspace['url'], {'roots': ['analysis-0'], 'mode': 'nearby', 'anchor': 'step-0-0', 'selected': 'step-0-0', 'tier': 'required'})
    assert page.evaluate('_reproNav.roots') == []
    assert page.locator('.rp-task[data-task="analysis-1"]').count() == 1
    assert page.locator('[data-rp-menu=trace], [data-rp-menu=options], #repro-tier').count() == 0
    page.locator('[data-rp-action=overview]').click()
    assert page.locator('.rp-task').count() == 4
    assert page.locator('.repro-node').count() == 0
    assert page.evaluate('_reproSelected') == 'step-0-0'
    assert 'Contains selected step' in page.locator('.rp-task[data-task="analysis-0"]').inner_text()
    assert 'step-0-0' in page.locator('#repro-detail').inner_text()
    page.locator('#dag-reader-controls [data-rp-action=show-selected]').click()
    page.wait_for_selector('#repro-node-step-0-0')
    page.route('http://**/*', lambda route: route.abort())
    page.route('https://**/*', lambda route: route.abort())
    enter(page, workspace['export'], {'roots': [], 'selected': 'step-0-0', 'view': 'graph'})
    assert page.locator('#task-preview').is_visible()
    assert page.locator('.repro-node.is-selected').count() == 1
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
        if page.locator('#task-preview').is_visible()!=preview:
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


def test_selection_folding_search_and_history_preserve_project(browser, workspace):
    page = browser.new_page(viewport={'width': 1372, 'height': 768})
    enter(page, workspace['url'])
    page.locator('[data-rp-action=fold][data-value="analysis-1"]').click()
    page.locator('[data-rp-action=fold][data-value="analysis-0"]').click()
    before = viewport(page)
    nodes = page.locator('[data-node-id]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.nodeId)')
    page.locator('#repro-node-step-0-0').dispatch_event('click')
    assert viewport(page) == before
    assert page.locator('[data-node-id]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.nodeId)') == nodes
    page.locator('[data-rp-action=fold][data-value="analysis-0"]').dispatch_event('click')
    assert page.evaluate('_reproSelected') == 'step-0-0'
    assert 'step-0-0' in page.locator('#repro-detail').inner_text()
    assert page.locator('.rp-task[data-task="analysis-0"] .rp-selected-inside').is_visible()
    assert 'analysis-1' in page.evaluate('_reproNav.expanded')
    assert not page.locator('#repro-notice').inner_text()
    page.reload()
    page.wait_for_selector('.rp-task')
    assert page.locator('#repro-node-step-0-0').count() == 0
    assert page.evaluate('_reproSelected') == 'step-0-0'
    page.locator('#dag-reader-controls [data-rp-action=show-selected]').click()
    page.wait_for_selector('#repro-node-step-0-0')
    page.fill('#repro-search', 'step-3-3')
    page.locator('#repro-search-results [data-rp-action=open]').click()
    page.wait_for_selector('#repro-node-step-3-3')
    assert page.evaluate('_reproSelected') == 'step-3-3'
    assert {'analysis-0', 'analysis-1', 'analysis-3'} <= set(page.evaluate('_reproNav.expanded'))
    assert page.locator('#repro-node-step-0-0').count() == 1
    page.go_back()
    page.wait_for_function('_reproSelected === "step-0-0"')
    assert page.locator('.rp-task[data-task="analysis-2"]').count() == 1
    page.locator('[data-rp-action=overview]').click()
    assert page.locator('.rp-selected-inside:not([hidden])').count() == 1
    page.locator('.rp-task-title[data-value="analysis-2"]').click()
    assert page.evaluate('_reproSelected') == ''
    assert page.locator('.rp-selected-inside:not([hidden])').count() == 0
    page.close()


def test_resized_desktop_preview_fits_phone_with_all_toolbar_controls(browser, workspace):
    page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    enter(page, workspace['url'])
    page.locator('#dag-preview-resizer').focus()
    page.keyboard.press('Shift+ArrowLeft')
    page.set_viewport_size({'width': 390, 'height': 844})
    for selector in ('#task-preview', '[data-rp-action=close-reader]', '[data-rp-action=overview]'):
        for box in page.locator(selector).all():
            bounds = box.bounding_box()
            assert bounds['x'] >= 0
            assert bounds['x'] + bounds['width'] <= 390
    reader = page.locator('#task-preview').bounding_box()
    assert reader['y'] >= 0
    assert reader['y'] + reader['height'] <= 844
    assert page.locator('[data-rp-action=overview]').is_visible()
    page.close()


def test_connection_hover_keyboard_endpoints_and_cycle_labels(browser, workspace):
    page = browser.new_page(viewport={'width': 1372, 'height': 900})
    enter(page, workspace['url'])
    if page.locator('#task-preview').is_visible(): page.click('#repro-preview-toggle')
    page.evaluate("""() => {
      const ids=['heterogeneity','treasury','elasticity','paper','downstream'];
      const titles=['Heterogeneity estimates','Treasury bounds','Elasticity estimates','Reproduce paper','Publish results'];
      const pairs=[[0,1],[0,2],[0,3],[1,3],[2,3],[3,0],[3,4]];
      const graph={steps:ids.map((id,i)=>({name:id,task:id,tier:'required',kind:'command'})),step_edges:pairs.map(([a,b])=>({from:ids[a],to:ids[b],via:'out.csv'})),dependencies:{tasks:ids.map((id,i)=>({path:id,title:titles[i],status:'in-progress'})),boundaries:{}}};
      _reproData.graph=graph;_reproNav={roots:[],expanded:[],tier:'all',mode:'scope',anchor:'',selected:''};
      _reproLayoutCache=null;drawReproView(document.getElementById('view-reproduction'),_reproData);
    }""")
    assert page.locator('#rp-arrow-cycle').get_attribute('markerUnits') == 'userSpaceOnUse'
    assert page.locator('#rp-arrow-cycle').get_attribute('markerHeight') == '6'
    cycle = page.locator('.rp-wire.is-cycle').first
    assert page.locator('.rp-wire.is-cycle').count() == 6
    assert 'Heterogeneity estimates → Treasury bounds' in cycle.get_attribute('aria-label')
    assert 'Task-group cycle' in cycle.get_attribute('aria-label')
    cycle.focus()
    assert page.locator('.is-edge-endpoint').count() == 2
    assert page.locator('.is-edge-active').count() == 1
    assert 'Heterogeneity estimates → Treasury bounds' in page.locator('#repro-connection-label').inner_text()
    accent = cycle.evaluate('(el)=>getComputedStyle(el).stroke')
    cycle.press('Enter')
    assert 'Heterogeneity estimates → Treasury bounds' in page.locator('#repro-edge-detail h3').inner_text()
    page.locator('.repro-canvas').focus()
    assert page.locator('.is-edge-endpoint').count() == 0
    ordinary = page.locator('.rp-wire:not(.is-cycle)').first
    ordinary.dispatch_event('pointerover')
    assert page.locator('.is-edge-endpoint').count() == 2
    assert 'Publish results' in page.locator('#repro-connection-label').inner_text()
    ordinary.dispatch_event('pointerout')
    assert page.locator('.is-edge-endpoint').count() == 0
    cycle.dispatch_event('pointerover')
    assert cycle.evaluate('(el)=>getComputedStyle(el).stroke') == accent
    assert page.locator('.rp-task.is-cycle').count() == 4
    cycle.focus()
    focused = cycle.get_attribute('id')
    page.evaluate("drawReproView(document.getElementById('view-reproduction'),_reproData)")
    assert page.evaluate('document.activeElement.id') == focused
    assert page.locator('.is-edge-endpoint').count() == 2
    assert page.locator('.rp-task.is-cycle').count() == 4
    assert page.locator('.rp-cycle-label[aria-label="Task-group cycle"]').count() == 4
    page.close()


def test_disconnected_bands_are_labeled_and_isolated_cards_stay_away_from_routes(browser, workspace):
    from runpy import run_path
    routing_fixture = run_path(str(Path(__file__).with_name("navigation_browser.py")))["routing_fixture"]
    page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    enter(page, workspace['url'])
    if page.locator('#task-preview').is_visible(): page.click('#repro-preview-toggle')
    page.evaluate("""graph => {
      _reproData.graph=graph;_reproNav={roots:[],expanded:[],tier:'all',mode:'scope',anchor:'',selected:''};
      _reproLayoutCache=null;drawReproView(document.getElementById('view-reproduction'),_reproData);
    }""", routing_fixture('components'))
    page.locator('[data-rp-action=fit]').click()
    headings = page.locator('.rp-component-label[data-component-parent=""]')
    assert headings.all_text_contents() == ['Dependency group 1', 'Dependency group 2', 'No connections in this view']
    assert page.locator('.rp-task').count() == 9
    assert page.locator('.rp-wire').count() == 3
    assert not page.locator('#task-preview').is_visible()
    isolated = page.locator('[data-component-kind=isolated]').bounding_box()
    first_card = page.locator('.rp-task[data-task=notes]').bounding_box()
    assert first_card['y'] > isolated['y'] + isolated['height']
    assert page.evaluate("""() => {
      const l=_reproLayoutCache.layout,b=l.bands.find(b=>b.isolated);
      return l.edges.every(e=>e.points.every(p=>p[1]<b.y));
    }""")
    page.locator('.rp-task-title[data-value=notes]').focus()
    assert page.locator('.rp-task-title[data-value=notes]').evaluate('(el)=>el===document.activeElement')
    page.evaluate("drawReproView(document.getElementById('view-reproduction'),_reproData)")
    assert headings.all_text_contents() == ['Dependency group 1', 'Dependency group 2', 'No connections in this view']
    page.close()


@pytest.mark.parametrize('width,height,axis', [(1440,900,'width'), (820,1180,'height')])
def test_preview_divider_drag_keyboard_and_persisted_orientation_sizes(browser, workspace, width, height, axis):
    page=browser.new_page(viewport={'width':width,'height':height})
    enter(page,workspace['url'])
    divider=page.locator('#dag-preview-resizer');reader=page.locator('#task-preview')
    assert divider.get_attribute('aria-orientation') == ('vertical' if axis=='width' else 'horizontal')
    before=reader.bounding_box()[axis];position=viewport(page);box=divider.bounding_box()
    x,y=box['x']+box['width']/2,box['y']+box['height']/2
    page.mouse.move(x,y);page.mouse.down();page.mouse.move(x-80 if axis=='width' else x,y-80 if axis=='height' else y,steps=8);page.mouse.up()
    assert reader.bounding_box()[axis] == pytest.approx(before+80,abs=1)
    assert viewport(page)==position
    divider.focus();divider.press('Home')
    assert reader.bounding_box()[axis] == pytest.approx(float(divider.get_attribute('aria-valuemin')),abs=1)
    divider.press('End')
    assert reader.bounding_box()[axis] == pytest.approx(float(divider.get_attribute('aria-valuemax')),abs=1)
    divider.press('ArrowRight' if axis=='width' else 'ArrowDown')
    preferred=reader.bounding_box()[axis]
    page.set_viewport_size({'width':390,'height':844} if axis=='width' else {'width':1440,'height':900})
    page.reload();page.wait_for_selector('.rp-task')
    page.set_viewport_size({'width':width,'height':height})
    page.wait_for_timeout(100)
    assert reader.bounding_box()[axis] == pytest.approx(preferred,abs=1)
    page.click('#btn-workspace')
    assert not divider.is_visible()
    assert page.locator('#task-preview').evaluate('(e)=>getComputedStyle(e).position')!='fixed'
    page.click('#btn-reproduction')
    assert reader.bounding_box()[axis] == pytest.approx(preferred,abs=1)
    page.close()


def test_preview_manual_visibility_short_window_and_full_reader_recovery(browser, workspace):
    page=browser.new_page(viewport={'width':1440,'height':400})
    enter(page,workspace['url'])
    assert not page.locator('#task-preview').is_visible()
    page.set_viewport_size({'width':1440,'height':900});page.wait_for_timeout(100)
    assert page.locator('#task-preview').is_visible()
    page.locator('[data-rp-action=full-reader]').click()
    page.set_viewport_size({'width':390,'height':500});page.wait_for_timeout(100)
    assert page.locator('#task-preview').is_visible()
    assert not page.locator('#view-reproduction').is_visible()
    page.locator('[data-rp-action=full-reader]').click()
    # Explicit opening in a short portrait window still provides a reachable hide control.
    page.locator('#repro-preview-toggle').click()
    assert page.locator('#task-preview').is_visible()
    assert not page.locator('#view-reproduction').is_visible()
    reader=page.locator('#task-preview').bounding_box()
    assert reader['y']+reader['height']<=500
    assert page.locator('[data-rp-action=full-reader]').inner_text()=='Back to graph'
    page.locator('[data-rp-action=close-reader]').click()
    page.set_viewport_size({'width':1440,'height':900});page.reload();page.wait_for_selector('.rp-task')
    assert not page.locator('#task-preview').is_visible()
    page.set_viewport_size({'width':820,'height':1180});page.wait_for_timeout(100)
    assert not page.locator('#task-preview').is_visible()
    page.click('#repro-preview-toggle');page.reload();page.wait_for_selector('.rp-task')
    assert page.locator('#task-preview').is_visible()
    page.close()


def test_sidebar_can_read_long_titles_and_restore_large_preference_after_narrow_reload(browser, workspace):
    page=browser.new_page(viewport={'width':1440,'height':900})
    enter(page,workspace['url']);page.click('#btn-workspace')
    divider=page.locator('#sidebar-resizer');box=divider.bounding_box()
    page.mouse.move(box['x']+box['width']/2,box['y']+80);page.mouse.down();page.mouse.move(700,box['y']+80,steps=10);page.mouse.up()
    assert float(divider.get_attribute('aria-valuenow'))>680
    preferred=page.evaluate('sbWidth')
    divider.focus();divider.press('End')
    assert float(divider.get_attribute('aria-valuenow'))==1080
    assert page.locator('#task-preview').bounding_box()['width']>=360
    page.evaluate('applySidebarWidth('+str(preferred)+');persistSidebarWidth()')
    page.set_viewport_size({'width':980,'height':900});page.reload();page.wait_for_selector('#sidebar-resizer')
    assert float(divider.get_attribute('aria-valuenow'))==620
    assert page.evaluate('sbWidth')==preferred
    page.set_viewport_size({'width':1440,'height':900});page.wait_for_timeout(100)
    assert float(divider.get_attribute('aria-valuenow'))==preferred
    page.close()


def test_bottom_preview_divider_accepts_touch_drag(browser, workspace):
    context=browser.new_context(viewport={'width':820,'height':1180},is_mobile=True,has_touch=True)
    page=context.new_page();enter(page,workspace['url'])
    divider=page.locator('#dag-preview-resizer');box=divider.bounding_box();before=page.locator('#task-preview').bounding_box()['height']
    x,y=box['x']+box['width']/2,box['y']+box['height']/2;cdp=context.new_cdp_session(page)
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
    for delta in range(10,61,10):cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x,'y':y-delta}]})
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    assert page.locator('#task-preview').bounding_box()['height']==pytest.approx(before+60,abs=2)
    assert divider.evaluate('(e)=>getComputedStyle(e).touchAction')=='none'
    context.close()


@pytest.mark.parametrize('surface', ['url', 'export'])
def test_step_markdown_links_shared_urls_and_wrong_owner(browser, workspace, surface):
    page = browser.new_page(viewport={'width': 1372, 'height': 900})
    if surface == 'export':
        page.route('http://**/*', lambda route: route.abort())
        page.route('https://**/*', lambda route: route.abort())
    base = workspace[surface]
    page.goto(base + '#/analysis-0')
    page.get_by_role('link', name='Own step', exact=True).click()
    page.wait_for_selector('#repro-node-step-0-0')
    assert page.evaluate('_reproSelected') == 'step-0-0'
    assert page.locator('.rp-task[data-task="analysis-3"]').count() == 1
    page.get_by_role('link', name='Other step', exact=True).click()
    page.wait_for_selector('#repro-node-step-1-2')
    assert page.evaluate('_reproSelected') == 'step-1-2'
    assert page.evaluate('activePath') == 'analysis-1'
    page.goto(base + '#/analysis-0?step=step-1-2')
    page.wait_for_selector('.rp-task')
    assert 'not declared' in page.locator('#repro-notice').inner_text()
    assert page.evaluate('_reproSelected') == ''
    page.goto(base + '#/analysis-1?step=step-1-2')
    page.wait_for_selector('#repro-node-step-1-2')
    assert page.evaluate('_reproSelected') == 'step-1-2'
    page.locator('[data-rp-action=declaration]').click()
    page.wait_for_selector('tr[id="step-step-1-2"]')
    page.close()


def test_connection_details_group_files_without_losing_evidence(browser, workspace):
    page = browser.new_page(viewport={'width': 1372, 'height': 900})
    enter(page, workspace['url'], {'expanded': ['analysis-0'], 'selected': 'step-0-0'})
    page.evaluate("_reproData.graph.step_edges.push({from:'step-0-0',to:'step-0-1',via:'out/extra.txt'});drawReproView(document.getElementById('view-reproduction'),_reproData)")
    links = page.locator('#repro-detail [data-rp-action=related][data-value="step-0-1"]')
    assert links.count() == 1
    evidence = links.locator('..').inner_text()
    assert 'out/0-0.txt' in evidence and 'out/extra.txt' in evidence
    wire = page.locator('.rp-wire[data-from="step-0-0"][data-to="step-0-1"]')
    assert wire.count() == 1
    wire.dispatch_event('click')
    assert 'out/extra.txt' in page.locator('#repro-edge-detail').inner_text()
    assert 'out/0-0.txt' in page.locator('#repro-edge-detail').inner_text()
    page.close()
