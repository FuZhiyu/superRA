"""Reproducible real-browser acceptance fixture; run directly with Playwright.

uv run --with playwright --with pyyaml --with fastapi --with jinja2 \
  --with 'uvicorn[standard]' --with watchfiles --with httpx python \
  skills/task-tree/scripts/tests/navigation_browser.py --evidence DIR
"""
import argparse
import json
import platform
import socket
import sys
import subprocess
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import plan_dashboard as dashboard
import uvicorn
from playwright.sync_api import sync_playwright


def fixture(base):
    root = base / 'superRA'
    root.mkdir()
    (root / 'task.md').write_text('---\ntitle: Navigation acceptance\nstatus: in-progress\n---\n\n## Objective\n\nInspect task dependencies.\n')
    (root / 'config.yaml').write_text('reproduction:\n  code_roots:\n    - code\n')
    owners = []
    for group in range(5):
        owners += [f'group-{group}'] + [f'group-{group}/task-{child}' for child in range(1, 10)]
    for i, owner in enumerate(owners):
        path = root / owner
        path.mkdir(parents=True, exist_ok=True)
        steps = []
        for j in range(10):
            k = i * 10 + j
            deps = [f'out/{n}.txt' for n in range(max(0, k - 3), k)]
            steps.append({'name': f'step-{k:03}', 'cmd': f'echo {k}', 'deps': deps, 'outs': [f'out/{k}.txt']})
        import yaml
        tier = 'required' if i % 2 else 'on-demand'
        text = f'---\ntitle: Analysis {i % 3} — Long-horizon heterogeneity estimates and research verification\nstatus: in-progress\n---\n\n## Objective\n\nRead {owner}.\n\n## Reproduction\n\n```yaml\n'
        (path / 'task.md').write_text(text + yaml.safe_dump({'tier': tier, 'steps': steps}, sort_keys=False) + '```\n')
    return root


def click_graph_action(page, selector):
    control = page.locator(selector)
    if not control.is_visible():
        control.locator('xpath=ancestor::details[contains(@class,"rp-menu")][1]').locator(':scope > summary').click()
    control.click()


def open_preview(page):
    if not page.locator('#task-preview').is_visible():
        page.locator('#repro-preview-toggle').click()


def routing_fixture(kind):
    """Small topology fixtures keep routing readable in retained screenshots."""
    if kind == 'components':
        ids = ['data', 'estimates', 'paper', 'inputs', 'checks', 'notes', 'literature', 'ideas', 'archive']
        titles = ['Build research data', 'Estimate heterogeneity', 'Manuscript exhibits', 'Separate input pipeline', 'Independent checks', 'Research notes', 'Literature review', 'Future questions', 'Reference material']
        pairs = [(0, 1), (1, 2), (3, 4)]
    elif kind == 'cycle':
        ids = ['heterogeneity', 'treasury', 'elasticity', 'paper', 'downstream']
        titles = ['Heterogeneity estimates', 'Treasury bounds', 'Elasticity estimates', 'Reproduce paper', 'Publish results']
        pairs = [(0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (3, 0), (3, 4)]
    else:
        ids = ['data', 'methods', 'estimates', 'verification', 'manuscript']
        titles = ['Build research data', 'Methods', 'Estimate heterogeneity', 'Verification checks', 'Manuscript exhibits']
        pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3), (2, 4), (3, 4)]
    return {'steps': [{'name': name, 'task': name, 'tier': 'required', 'kind': 'command'} for name in ids],
            'step_edges': [{'from': ids[a], 'to': ids[b], 'via': 'output.csv'} for a, b in pairs],
            'dependencies': {'tasks': [{'path': name, 'title': title, 'status': 'in-progress'} for name, title in zip(ids, titles)], 'boundaries': {}}}


def run(evidence, snapshot=None):
    evidence.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='navigation-') as directory:
        base = Path(directory).resolve()
        if snapshot:
            captured = json.loads(snapshot.read_text())
            root = base / 'superRA'
            root.mkdir()
            for task in captured['graph']['dependencies']['tasks']:
                path = root / task['path']
                path.mkdir(parents=True, exist_ok=True)
                import yaml
                (path / 'task.md').write_text('---\n' + yaml.safe_dump({'title': task['title'], 'status': task['status']}, allow_unicode=True) + '---\n\n## Objective\n\nGraph-only verification fixture. Research task prose is omitted.\n')
            dashboard._repro_graph_payload = lambda state: captured['graph']
            dashboard._repro_status_payload = lambda state, tier: captured['status']
        else:
            root = fixture(base)
        dashboard.PLAN_ROOT = root
        dashboard.rebuild_tree()
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(dashboard.app, host='127.0.0.1', port=port, log_level='error'))
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        while not server.started:
            time.sleep(.05)
        export = base / 'offline.html'
        export.write_text(dashboard.render_standalone_html(root, output_path=export))
        results = {'machine': platform.platform(), 'live': f'http://127.0.0.1:{port}', 'project': str(root)}
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless=True, chromium_sandbox=True)
                results['browser'] = browser.version
                page = browser.new_page(viewport={'width': 1440, 'height': 1000})
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(results['live'])
                page.wait_for_selector('#active-node .task-node')
                page.click('#btn-reproduction')
                page.wait_for_selector('.rp-task')
                page.screenshot(path=str(evidence / 'dag-desktop.png'), full_page=True)
                results['counts'] = page.evaluate('({steps:_reproData.graph.steps.length,tasks:reproTasks(_reproData.graph).length,edges:_reproData.graph.step_edges.length})')
                results['initialZoom'] = page.evaluate('_reproViewport.zoom')
                assert page.locator('#rp-arrow path').evaluate('(e)=>getComputedStyle(e).fill') != 'none'
                if not snapshot:
                    assert results['counts']['steps'] == 500
                    assert results['counts']['edges'] == 1494
                    assert page.locator('.rp-task').count() == 5
                    scope = page.evaluate('JSON.stringify(_reproNav.roots)')
                    page.locator('[data-rp-action=task][data-value="group-0"]').click()
                    assert page.evaluate('activePath') == 'group-0'
                    assert page.evaluate('JSON.stringify(_reproNav.roots)') == scope
                    page.locator('[data-rp-action=fold][data-value="group-0"]').click()
                    assert page.locator('.rp-task').count() == 14
                    assert page.locator('.repro-node').count() == 10
                    page.locator('[data-rp-action=fold][data-value="group-0/task-1"]').click()
                    assert page.locator('.repro-node').count() == 20
                    page.evaluate("selectReproStep('step-010')")
                    assert page.evaluate('activePath') == 'group-0/task-1'
                    before = page.evaluate('JSON.stringify(_reproViewport)')
                    page.evaluate("selectReproStep('step-011')")
                    assert page.evaluate('JSON.stringify(_reproViewport)') == before
                    page.evaluate("document.querySelector('[data-rp-action=fold][data-value=\"group-0\"]').click()")
                    assert page.evaluate('_reproSelected') == 'step-011'
                    assert page.locator('.repro-node').count() == 0
                    assert 'Contains selected step' in page.locator('[data-task="group-0"]').inner_text()
                    page.evaluate("document.querySelector('[data-rp-action=fold][data-value=\"group-0\"]').click()")
                    assert page.locator('[data-task="group-0/task-1"].rp-expanded').count() == 1
                    page.fill('#repro-search', 'group-1')
                    page.locator('[data-rp-action=find-task][data-value="group-1"]').click()
                    assert page.evaluate('_reproNav.roots') == []
                    click_graph_action(page, '[data-rp-action=overview]')
                    # Repeated pure UI timings after both payloads are loaded.
                    results['timingsMs'] = page.evaluate('''(() => {let r={search:[],overview:[],full:[]};for(let i=0;i<5;i++){let t=performance.now();document.getElementById('repro-search').value='step-499';reproRenderSearch(false);r.search.push(performance.now()-t);t=performance.now();reproNavigate({expanded:[]},true);r.overview.push(performance.now()-t);}reproNavigate({roots:[],expanded:[]},true);for(let i=0;i<3;i++){let t=performance.now();reproNavigate({expanded:reproTasks(_reproData.graph)},false);r.full.push(performance.now()-t);reproNavigate({expanded:[]},false);}return r;})()''')
                    assert max(results['timingsMs']['search']) < 200
                    assert max(results['timingsMs']['overview']) < 200
                    assert max(results['timingsMs']['full']) < 2000
                    page.evaluate("revealReproStep('step-499')")
                    open_preview(page)
                    page.wait_for_selector('#repro-detail .repro-detail')
                    page.wait_for_function("_reproSelected==='step-499'")
                    positions = page.evaluate('JSON.stringify(_reproLayoutCache.layout.pos)')
                    canvas = page.locator('.repro-canvas').element_handle()
                    logs = base / '.superra-repro' / 'logs'
                    logs.mkdir(parents=True, exist_ok=True)
                    (logs / 'step-499.log').write_text('Last actual run log\n')
                    page.evaluate("onReproUpdated()")
                    page.wait_for_function("document.getElementById('repro-detail').innerText.includes('Last actual run log')")
                    assert page.evaluate('JSON.stringify(_reproLayoutCache.layout.pos)') == positions
                    assert canvas.evaluate('(e)=>e===document.querySelector(".repro-canvas")')
                    assert 'Last actual run log' in page.locator('#repro-detail').inner_text(), page.evaluate('({selected:_reproSelected,detail:document.getElementById("repro-detail").innerText,errors:window.__errors})')
                    link = page.url
                    page.reload()
                    open_preview(page)
                    page.wait_for_selector('#repro-detail .repro-detail')
                    assert page.evaluate('_reproSelected') == 'step-499'
                    page.locator('[data-rp-action=declaration]').click()
                    page.wait_for_selector('#active-node [data-section="Reproduction"]')
                    page.locator('[data-rp-action=full-reader]').click()
                    page.click('#btn-workspace')
                    assert page.evaluate('activePath') == 'group-4/task-9'
                    page.click('#btn-reproduction')
                    assert page.evaluate('_reproSelected') == 'step-499'
                    page.go_back()
                    page.wait_for_function('currentView === "workspace"')
                    page.go_forward()
                    page.wait_for_function('currentView === "reproduction"')
                    results['sharedReaderAndHistory'] = True
                    # Existing comment UI, persisted and read through the CLI.
                    page.locator('[data-rp-action=declaration]').click()
                    page.wait_for_selector('#active-node [data-section="Reproduction"] .comment-gutter-btn')
                    page.locator('#active-node [data-section="Reproduction"] .comment-gutter-btn').first.click()
                    page.locator('.comment-form textarea').fill('Check this dependency chain.')
                    page.locator('.comment-form').get_by_role('button', name='Comment', exact=True).click()
                    page.wait_for_selector('.comment-thread')
                    command = [sys.executable, str(Path(dashboard.__file__).with_name('cli.py')), 'task', 'comment', 'list', 'group-4/task-9', '--root', str(root), '--json']
                    comments = subprocess.run(command, capture_output=True, text=True, check=True).stdout
                    assert 'Check this dependency chain.' in comments and 'Reproduction' in comments
                    results['commentRoundTrip'] = True
                    page.locator('[data-rp-action=full-reader]').click()
                    # Keyboard search, selection, declaration, and dismissal.
                    page.locator('[data-rp-action=close-reader]').click()
                    page.locator('#repro-search').focus()
                    page.keyboard.type('step-499')
                    page.locator('#repro-search-results [data-rp-action=open][data-value=step-499]').focus()
                    page.keyboard.press('Enter')
                    open_preview(page)
                    page.wait_for_selector('#repro-detail .repro-detail')
                    page.locator('[data-rp-action=declaration]').focus()
                    page.keyboard.press('Enter')
                    page.wait_for_selector('#active-node [data-section="Reproduction"] .rendered-md[data-rendered]')
                    page.locator('[data-rp-action=full-reader]').click()
                    page.locator('[data-rp-action=close-reader]').focus()
                    page.keyboard.press('Enter')
                    assert page.locator('#repro-preview-toggle').evaluate('(e)=>e===document.activeElement')
                    page.locator('[data-rp-action=reader]').click()
                    # Drag the accessible divider beside the reading pane.
                    reader = page.locator('.detail-panel')
                    box = reader.bounding_box()
                    before = box['width']
                    divider=page.locator('#dag-preview-resizer').bounding_box()
                    page.mouse.move(divider['x']+divider['width']/2, divider['y']+divider['height']/2)
                    page.mouse.down()
                    page.mouse.move(divider['x']-90, divider['y']+divider['height']/2, steps=10)
                    page.mouse.up()
                    after = reader.bounding_box()['width']
                    assert abs(after-before) > 40, (before, after)
                    page.click('#btn-workspace');page.click('#btn-reproduction')
                    assert abs(reader.bounding_box()['width']-after) < 2
                    results['keyboardAndResize'] = True
                    # A separate worktree cache must not borrow graph or navigation state.
                    alternate = base / 'alternate' / 'superRA'
                    alternate.mkdir(parents=True)
                    (alternate / 'task.md').write_text('---\ntitle: Other worktree\nstatus: in-progress\n---\n\n## Objective\n\nIndependent task.\n')
                    archived = alternate / 'archived'
                    archived.mkdir()
                    (archived / 'task.md').write_text('---\ntitle: Archived example\nstatus: archived\n---\n\n## Objective\n\nReadable archived task.\n')
                    dashboard._worktree_cache['alternate'] = dashboard._build_worktree_state('alternate', alternate)
                    original = page.evaluate('ACTIVE_WT')
                    saved = page.evaluate('JSON.stringify(_reproNav)')
                    page.locator('[data-rp-action=full-reader]').click()
                    page.evaluate("async () => {await applyWorktree('alternate','');showView('reproduction');}")
                    page.wait_for_function('_reproData && _reproData.graph.steps.length === 0')
                    page.evaluate("showView('workspace');setActive('archived');showView('reproduction')")
                    page.wait_for_function("document.getElementById('repro-notice').innerText.includes('archived')")
                    assert page.locator('[data-task=archived]').count() == 0
                    assert page.locator('#task-preview').is_visible()
                    page.locator('[data-rp-action=close-reader]').click()
                    page.evaluate('(wt)=>applyWorktree(wt,"group-4/task-9")', original)
                    page.wait_for_function('_reproData && _reproData.graph.steps.length === 500')
                    assert page.evaluate('JSON.stringify(_reproNav)') == saved
                    assert not reader.is_visible()
                    assert page.locator('#view-reproduction').is_visible()
                    open_preview(page)
                    assert abs(reader.bounding_box()['width']-after) < 2
                    results['worktreeIsolation'] = True
                if snapshot:
                    page.fill('#repro-search', 'intermediary-build-factors-and-panel')
                    page.locator('#repro-search-results [data-rp-action=open]').first.click()
                    open_preview(page)
                    page.wait_for_selector('#repro-detail .repro-detail')
                    assert page.locator('.repro-findings').count() == 1
                    assert 'cycle' in page.locator('.repro-findings').inner_text()
                    assert page.evaluate('_reproNav.mode') == 'scope'
                    page.screenshot(path=str(evidence / 'dag-real-step.png'), full_page=True)
                    results['realGraphMixedInspection'] = True
                for width, theme in [(768, 'light'), (390, 'light'), (390, 'dark'), (1440, 'dark')]:
                    page.set_viewport_size({'width': width, 'height': 900})
                    page.evaluate(f"document.documentElement.dataset.theme='{theme}'")
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), page.evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth,overflow:[...document.querySelectorAll("body *")].filter(e=>!e.closest(".repro-plot")&&e.getBoundingClientRect().right>innerWidth+1).map(e=>[e.tagName,e.id,e.className,e.getBoundingClientRect().width]).slice(0,15)})')
                    page.screenshot(path=str(evidence / f'dag-{width}-{theme}.png'), full_page=True)
                if not snapshot:
                    # Cold legacy link restores the selected step and owner.
                    legacy = {'roots': ['group-4'], 'tier': 'required', 'view': 'graph', 'mode': 'scope', 'anchor': '', 'selected': 'step-499'}
                    from urllib.parse import quote
                    page.goto(results['live'] + '/#/group-4?repro=' + quote(json.dumps(legacy)))
                    page.wait_for_selector('#repro-node-step-499')
                    assert page.evaluate('activePath') == 'group-4/task-9'
                    # Structural removal arrives over the live server's SSE path.
                    (root / 'group-4/task-9/task.md').unlink()
                    page.wait_for_function('_reproData && !_reproData.graph.steps.some(s=>s.name==="step-499")')
                    assert 'removed' in page.locator('#repro-notice').inner_text()
                    assert page.evaluate('_reproSelected') == ''
                    results['legacyAndRemovalRecovery'] = True
                page.goto(export.as_uri())
                page.context.set_offline(True)
                page.click('#btn-reproduction')
                page.wait_for_selector('.rp-task')
                if not snapshot:
                    page.fill('#repro-search', 'step-499')
                    page.locator('#repro-search-results [data-rp-action=open][data-value=step-499]').click()
                    page.wait_for_function("_reproSelected==='step-499'")
                    assert page.evaluate('activePath') == 'group-4/task-9'
                    open_preview(page)
                    page.locator('[data-rp-action=declaration]').click()
                    page.wait_for_selector('#active-node [data-section="Reproduction"]')
                results['offline'] = True
                if not snapshot:
                    touch = browser.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True)
                    touch.set_offline(True)
                    phone = touch.new_page()
                    phone.goto(export.as_uri())
                    phone.locator('#btn-reproduction').tap()
                    phone.wait_for_selector('.rp-task')
                    assert phone.locator('#task-preview').is_visible()
                    phone.locator('#repro-search').tap();phone.locator('#repro-search').fill('step-499')
                    phone.locator('#repro-search-results [data-rp-action=open][data-value=step-499]').tap()
                    open_preview(phone)
                    phone.locator('[data-rp-action=declaration]').tap()
                    phone.wait_for_selector('#active-node [data-section="Reproduction"] .rendered-md[data-rendered]')
                    phone.locator('[data-rp-action=full-reader]').tap()
                    phone.locator('[data-rp-action=close-reader]').tap()
                    assert phone.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    canvas = phone.locator('.repro-canvas')
                    canvas.scroll_into_view_if_needed()
                    box = canvas.bounding_box()
                    x, y = phone.evaluate('''() => {let c=document.querySelector('.repro-canvas').getBoundingClientRect();for(let y=Math.min(innerHeight-30,c.bottom-30);y>Math.max(0,c.top)+20;y-=25){let x=c.left+40,e=document.elementFromPoint(x,y);if(e?.closest('.repro-canvas')&&!e.closest('button'))return [x,y];}throw Error('No empty pan surface');}''')
                    before = phone.evaluate('_reproViewport.x')
                    cdp = touch.new_cdp_session(phone)
                    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x, 'y': y}]})
                    for delta in range(10, 61, 10):
                        cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x + delta, 'y': y}]})
                    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
                    phone.evaluate('() => new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
                    assert phone.evaluate('_reproViewport.x') != before
                    phone.screenshot(path=str(evidence / 'dag-touch.png'), full_page=True)
                    results['touchNavigationAndPan'] = True
                    touch.close()
                routing = browser.new_page(viewport={'width': 1440, 'height': 900})
                routing.goto(results['live'])
                routing.click('#btn-reproduction')
                routing.wait_for_selector('.rp-task')
                if routing.locator('#task-preview').is_visible(): routing.locator('#repro-preview-toggle').click()
                for kind in ('cycle', 'fan', 'components'):
                    routing.evaluate("""graph => {
                        _reproData.graph=graph;_reproNav={roots:[],expanded:[],tier:'all',mode:'scope',anchor:'',selected:''};
                        _reproLayoutCache=null;drawReproView(document.getElementById('view-reproduction'),_reproData);
                    }""", routing_fixture(kind))
                    routing.locator('[data-rp-action=fit]').click()
                    routing.screenshot(path=str(evidence / f'dag-routing-{kind}.png'), full_page=True, animations='disabled')
                    routing.locator('.theme-toggle').click()
                    routing.screenshot(path=str(evidence / f'dag-routing-{kind}-dark.png'), full_page=True, animations='disabled')
                    routing.locator('.theme-toggle').click()
                    results[f'routing-{kind}'] = routing.evaluate('({nodes:_reproLayoutCache.layout.model.nodes.length,edges:_reproLayoutCache.layout.edges.length,cycleEdges:_reproLayoutCache.layout.edges.filter(e=>e.cycle).length,components:_reproLayoutCache.layout.bands.filter(b=>!b.parent&&!b.isolated).length,isolatedCards:_reproLayoutCache.layout.bands.filter(b=>!b.parent&&b.isolated).reduce((n,b)=>n+b.ids.length,0)})')
                routing.close()
                panes=browser.new_page(viewport={'width':1440,'height':900})
                panes.goto(results['live']);panes.click('#btn-reproduction');panes.wait_for_selector('.rp-task')
                panes.evaluate('document.fonts.ready')
                assert panes.locator('#task-preview').is_visible()
                panes.screenshot(path=str(evidence / 'dag-preview-side.png'),full_page=True,animations='disabled')
                panes.set_viewport_size({'width':390,'height':844})
                panes.wait_for_function("document.getElementById('workspace').classList.contains('dag-reader-bottom')")
                assert panes.locator('#task-preview').is_visible()
                panes.screenshot(path=str(evidence / 'dag-preview-bottom.png'),full_page=True,animations='disabled')
                panes.set_viewport_size({'width':1440,'height':900});panes.click('#btn-workspace')
                panes.locator('#sidebar-resizer').focus()
                for _ in range(9): panes.keyboard.press('Shift+ArrowRight')
                assert float(panes.locator('#sidebar-resizer').get_attribute('aria-valuenow'))>480
                panes.screenshot(path=str(evidence / 'tree-wide-sidebar.png'),full_page=True,animations='disabled')
                results['responsivePanes']={'side':True,'portraitBottom':True,'sidebarWidth':float(panes.locator('#sidebar-resizer').get_attribute('aria-valuenow'))}
                panes.close()
                results['errors'] = errors
                assert not errors, errors
                browser.close()
        finally:
            server.should_exit = True
            thread.join(timeout=5)
        (evidence / 'browser-results.json').write_text(json.dumps(results, indent=2) + '\n')
        print(json.dumps(results, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--graph-snapshot', type=Path)
    args = parser.parse_args()
    run(args.evidence.resolve(), args.graph_snapshot.resolve() if args.graph_snapshot else None)
