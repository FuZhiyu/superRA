"""Headless-browser review of the dashboard Graph view on two scratch fixtures.

uv run --with playwright --with pyyaml --with fastapi --with jinja2 \
  --with 'uvicorn[standard]' --with watchfiles --with httpx python \
  superRA/reproducibility/14-review-revisions/06-dashboard/attachments/graph_review.py \
  --evidence superRA/reproducibility/14-review-revisions/06-dashboard/attachments/browser

Writes screenshots and measurements.json into --evidence; exits 1 when a check fails.
"""
import argparse
import contextlib
import json
import platform
import socket
import sys
import tempfile
import threading
import time
from pathlib import Path
from urllib.parse import quote

import yaml

SCRIPTS = Path(__file__).resolve().parents[5] / 'skills' / 'task-tree' / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import plan_dashboard as dashboard  # noqa: E402
import uvicorn  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

TITLE = 'Long-horizon heterogeneity estimates for group {g} task {c}'


def write_task(root, path, title, *, depends_on=(), steps=None, raw_section=None):
    folder = root / path
    folder.mkdir(parents=True, exist_ok=True)
    text = f'---\ntitle: "{title}"\nstatus: in-progress\ndepends_on: [{", ".join(depends_on)}]\n---\n\n## Objective\n\nReview fixture.\n'
    if steps is not None:
        text += '\n## Reproduction\n\n```yaml\n' + yaml.safe_dump({'steps': steps}, sort_keys=False) + '```\n'
    if raw_section is not None:
        text += '\n## Reproduction\n\n```yaml\n' + raw_section + '```\n'
    (folder / 'task.md').write_text(text)


def large_fixture(base):
    """50 tasks in 10 top-level groups; 200 steps; file edges plus logical-only edges."""
    root = base / 'superRA'
    root.mkdir(parents=True)
    write_task(root, '', 'Graph review: 50 tasks')
    (root / 'config.yaml').write_text('reproduction:\n  runners:\n    sh: sh {script}\n')
    for g in range(10):
        write_task(root, f'group-{g:02}', f'Research stage {g}: estimation and verification')
        for c in range(4):
            steps = []
            for s in range(5):
                k = (g * 4 + c) * 5 + s
                deps = [f'out/{k - 1}.txt'] if s else ([f'out/{k - 1}.txt'] if c else ([f'out/{k - 16}.txt'] if g else []))
                steps.append({'name': f'step-{k:03}', 'cmd': f'echo {k}', 'deps': deps, 'outs': [f'out/{k}.txt']})
            write_task(root, f'group-{g:02}/task-{c}', TITLE.format(g=g, c=c),
                       depends_on=['task-1'] if c == 3 else (), steps=steps)
    return root


def invalid_fixture(base):
    """A malformed section, a step cycle across two tasks, a logical-only task, and a
    depends_on running against the file flow (a dependency warning)."""
    root = base / 'superRA'
    root.mkdir(parents=True)
    write_task(root, '', 'Graph review: invalid graph')
    (root / 'config.yaml').write_text('reproduction:\n  runners:\n    sh: sh {script}\n')
    write_task(root, 'data', 'Data', depends_on=['estimate'], steps=[{'name': 'build', 'cmd': 'echo', 'outs': ['out/data.txt']}])
    write_task(root, 'estimate', 'Estimate', steps=[{'name': 'estimate', 'cmd': 'echo', 'deps': ['out/data.txt'], 'outs': ['out/est.txt']}])
    write_task(root, 'notes', 'Notes (logical only)', depends_on=['estimate'])
    write_task(root, 'malformed', 'Malformed', raw_section='steps:\n  - name: broken\n    cmd: [unclosed\n')
    write_task(root, 'cycle-a', 'Cycle A', steps=[{'name': 'left', 'cmd': 'echo', 'deps': ['out/right.txt'], 'outs': ['out/left.txt']}])
    write_task(root, 'cycle-b', 'Cycle B', steps=[{'name': 'right', 'cmd': 'echo', 'deps': ['out/left.txt'], 'outs': ['out/right.txt']}])
    return root


@contextlib.contextmanager
def serve(root):
    dashboard.PLAN_ROOT = root
    dashboard.rebuild_tree()
    dashboard._repro_graph_cache.clear()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(dashboard.app, host='127.0.0.1', port=port, log_level='error'))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    while not server.started:
        time.sleep(.05)
    try:
        yield f'http://127.0.0.1:{port}'
    finally:
        server.should_exit = True
        thread.join(5)


def graph_url(url, task, state):
    return f'{url}/#/{task}?repro=' + quote(json.dumps({'layout': 'graph', **state}))


def open_graph(browser, url, errors):
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(url)
    page.wait_for_selector('.rp-task')
    page.wait_for_timeout(200)
    return page


def payload_facts(page):
    return page.evaluate('''async () => {
      const graph = await (await fetch('/api/repro/graph')).text();
      const status = await (await fetch('/api/repro/status')).text();
      const g = JSON.parse(graph), s = JSON.parse(status);
      const copies = [g.findings, (g.dependencies || {}).findings, s.findings].flatMap(list => list || []);
      return {graphBytes: graph.length, statusBytes: status.length, graphKeys: Object.keys(g).sort(),
        dependencyKeys: Object.keys(g.dependencies || {}).sort(), statusHasFindings: 'findings' in s,
        findings: g.findings, copies: copies.map(f => f.message)};
    }''')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', type=Path, required=True)
    evidence = parser.parse_args().evidence
    evidence.mkdir(parents=True, exist_ok=True)
    checks, facts, errors = {}, {'machine': platform.platform()}, []
    with tempfile.TemporaryDirectory(prefix='graph-review-') as tmp, sync_playwright() as pw:
        chrome = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
        browser = pw.chromium.launch(**({'executable_path': str(chrome)} if chrome.exists() else {}))
        facts['browser'] = browser.version

        large = large_fixture(Path(tmp) / 'large')
        with serve(large) as url:
            page = open_graph(browser, graph_url(url, '', {}), errors)
            facts['large'] = {'counts': page.evaluate('({steps:_reproData.graph.steps.length,tasks:reproTasks(_reproData.graph).length})'),
                              'collapsedOpenZoom': page.evaluate('_reproViewport.zoom')}
            page.screenshot(path=str(evidence / 'collapsed-open.png'))
            checks['collapsed graph opens at >= 80%'] = facts['large']['collapsedOpenZoom'] >= 0.8
            checks['file edges are solid'] = page.locator('.rp-wire:not(.is-logical)').first.evaluate('e => getComputedStyle(e).strokeDasharray') == 'none'
            page.locator('[data-rp-action=fit]').click()
            facts['large']['fitZoom'] = page.evaluate('_reproViewport.zoom')
            page.close()

            page = open_graph(browser, graph_url(url, 'group-03/task-2', {'expanded': []}), errors)
            all_tasks = page.evaluate('reproTasks(_reproData.graph)')
            page.close()
            page = open_graph(browser, graph_url(url, 'group-03/task-2', {'expanded': all_tasks}), errors)
            large_facts = facts['large']
            large_facts['expandedOpenZoom'] = page.evaluate('_reproViewport.zoom')
            large_facts['expandedStepNodes'] = page.locator('.repro-node').count()
            large_facts['selectedCardInView'] = page.evaluate('''(() => {
              const card = document.querySelector('.rp-task[data-task="group-03/task-2"]').getBoundingClientRect();
              const canvas = document.querySelector('.repro-canvas').getBoundingClientRect();
              return card.left >= canvas.left && card.left + 200 <= canvas.right && card.top >= canvas.top && card.top + 60 <= canvas.bottom;
            })()''')
            large_facts['timingsMs'] = page.evaluate('''(() => {
              const layout = [], draw = [];
              for (let i = 0; i < 5; i++) {
                const model = reproHierarchy(workspaceGraph(_reproData.graph), _reproNav, reproProject(_reproData.graph, _reproNav, []));
                let t = performance.now(); reproHierarchyLayout(model); layout.push(performance.now() - t);
                t = performance.now(); _reproLayoutCache = null; drawReproView(document.getElementById('view-reproduction'), _reproData); draw.push(performance.now() - t);
              }
              return {layout: Math.min(...layout), draw: Math.min(...draw)};
            })()''')
            page.screenshot(path=str(evidence / 'expanded-open.png'))
            logical = page.locator('.rp-wire.is-logical').first
            large_facts['logicalDash'] = logical.evaluate('e => getComputedStyle(e).strokeDasharray') if logical.count() else None
            checks['logical-only edges are dashed'] = large_facts['logicalDash'] not in (None, 'none')
            checks['expanded graph opens at >= 80%'] = large_facts['expandedOpenZoom'] >= 0.8
            checks['expanded graph shows all 200 steps'] = large_facts['expandedStepNodes'] == 200
            checks['open shows the selected task title'] = large_facts['selectedCardInView']
            payload = payload_facts(page)
            large_facts['payload'] = {k: payload[k] for k in ('graphBytes', 'statusBytes', 'graphKeys', 'dependencyKeys', 'statusHasFindings')}
            checks['graph payload carries no task_edges'] = 'task_edges' not in payload['graphKeys']
            checks['graph payload carries no boundaries or dependency findings'] = not {'boundaries', 'edges', 'findings'} & set(payload['dependencyKeys'])
            checks['status payload carries no findings'] = not payload['statusHasFindings']
            page.close()

        invalid = invalid_fixture(Path(tmp) / 'invalid')
        with serve(invalid) as url:
            page = open_graph(browser, graph_url(url, '', {}), errors)
            payload = payload_facts(page)
            messages = [f['message'] for f in payload['findings']]
            facts['invalid'] = {'findings': messages, 'copiesSent': len(payload['copies']),
                                'diagnostics': page.locator('.rp-diagnostics > summary').inner_text()}
            checks['each finding is sent once'] = sorted(payload['copies']) == sorted(set(messages))
            checks['a step cycle is reported once'] = sum('cycle' in m for m in messages) == 1
            card = page.locator('.rp-task[data-task="malformed"]')
            checks['malformed card is marked as an error'] = 'is-error' in (card.get_attribute('class') or '')
            marker = card.locator('[data-rp-action=finding]')
            if marker.count():
                marker.click()
            checks['error marker opens its finding'] = page.evaluate('''(() => {
              const menu = document.querySelector('.rp-diagnostics');
              const row = document.activeElement.closest('li');
              return menu.open && !!row && row.dataset.findingTask === 'malformed';
            })()''')
            page.screenshot(path=str(evidence / 'invalid-graph.png'))
            page.keyboard.press('Escape')
            page.screenshot(path=str(evidence / 'invalid-graph-cards.png'))
            checks['logical edge into Notes is dashed'] = page.evaluate('''(() => {
              const wire = document.querySelector('.rp-wire[data-to="task:notes"]');
              return !!wire && wire.classList.contains('is-logical') && getComputedStyle(wire).strokeDasharray !== 'none';
            })()''')
            checks['step cycle nodes are labeled'] = page.locator('.rp-task.is-cycle').count() == 2
            checks['graph blocked header shows'] = 'graph blocked' in facts['invalid']['diagnostics']
            page.close()
        browser.close()
    checks['no page errors'] = not errors
    facts['pageErrors'] = errors
    (evidence / 'measurements.json').write_text(json.dumps({'checks': checks, 'facts': facts}, indent=2) + '\n')
    failed = [name for name, ok in checks.items() if not ok]
    print(json.dumps({'failed': failed}, indent=2))
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
