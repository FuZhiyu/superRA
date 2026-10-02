"""Rendered reproduction states: the reported and own-state channels, online-only files, and the Build menu.

uv run --with pytest --with playwright --with pyyaml --with fastapi --with jinja2 \
  --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest \
  skills/task-tree/scripts/tests/test_repro_states_browser.py

Online-only files are simulated by patching `_repro_state.file_flags` to report
`SF_DATALESS` for the fixture's cloud file, as `test_repro_online.py` does.
"""
import os
import socket
import sys
import threading
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _repro_state
import repro_run

# One fixture holds every state: an own-stale step with two inherited-stale
# descendants, an `unverified` task, an `unverified` step behind a stale
# producer, a never-built step, a failed step, and a check step.
TASKS = {
    '01-survey-panel': ('Clean the survey panel', [
        {'name': 'clean', 'cmd': 'cp Data/survey.csv out/clean.csv', 'deps': ['Data/survey.csv'], 'outs': ['out/clean.csv']},
        {'name': 'codebook-check', 'kind': 'check', 'cmd': 'test -s Data/codebook.csv', 'deps': ['Data/codebook.csv']},
    ]),
    '02-panel-model': ('Estimate the panel model', [
        {'name': 'merge', 'cmd': 'cp out/clean.csv out/merged.csv', 'deps': ['out/clean.csv'], 'outs': ['out/merged.csv']},
        {'name': 'report', 'cmd': 'wc -l out/merged.csv > out/report.txt', 'deps': ['out/merged.csv'], 'outs': ['out/report.txt']},
        {'name': 'vendor-join', 'cmd': 'cat out/clean.csv Data/vendor.csv > out/joined.csv',
         'deps': ['out/clean.csv', 'Data/vendor.csv'], 'outs': ['out/joined.csv']},
        {'name': 'figures', 'cmd': 'cp Data/codebook.csv out/figures.txt', 'deps': ['Data/codebook.csv'], 'outs': ['out/figures.txt']},
        {'name': 'robustness', 'cmd': 'exit 1', 'deps': ['Data/codebook.csv'], 'outs': ['out/robust.txt']},
    ]),
    '03-vendor-archive': ('Summarize the vendor archive', [
        {'name': 'vendor-rows', 'cmd': 'wc -l Data/vendor.csv > out/vendor-rows.txt', 'deps': ['Data/vendor.csv'], 'outs': ['out/vendor-rows.txt']},
        {'name': 'vendor-bytes', 'cmd': 'wc -c Data/vendor.csv > out/vendor-bytes.txt', 'deps': ['Data/vendor.csv'], 'outs': ['out/vendor-bytes.txt']},
    ]),
}
CLOUD_FILE = 'Data/vendor.csv'
CLOUD_SIZE = 2_400_000


def build_state_fixture(base: Path) -> Path:
    """Write, build, and age the fixture under *base*; returns its plan root.

    Evicting `Data/vendor.csv` is left to `simulate_online_only`, which must run
    in the process that serves the dashboard.
    """
    import yaml
    root = base / 'superRA'
    root.mkdir(parents=True)
    (root / 'task.md').write_text('---\ntitle: Reproduction states\nstatus: in-progress\n---\n\n## Objective\n\nShow every state.\n')
    for path, (title, steps) in TASKS.items():
        (root / path).mkdir()
        (root / path / 'task.md').write_text(f'---\ntitle: {title}\nstatus: in-progress\n---\n\n## Objective\n\n{title}.\n\n'
                                             '## Reproduction\n\n```yaml\n' + yaml.safe_dump({'steps': steps}, sort_keys=False) + '```\n')
    (base / 'Data').mkdir()
    (base / 'out').mkdir()
    (base / 'Data/survey.csv').write_text('id,y\n1,2\n')
    (base / 'Data/codebook.csv').write_text('var,label\ny,outcome\n')
    (base / CLOUD_FILE).write_bytes(b'v\n' * (CLOUD_SIZE // 2))
    built = [f'{task}#{s["name"]}' for task, (_, steps) in TASKS.items() for s in steps if s['name'] != 'figures']
    try:
        repro_run.main(['--plan-root', str(root), 'build', '--only', *built])
    except SystemExit:
        pass  # `robustness` fails by design
    (base / 'Data/survey.csv').write_text('id,y\n1,3\n')  # `clean` turns stale
    _repro_state.runner_paths(base).cache_file.unlink(missing_ok=True)
    return root


def simulate_online_only(base: Path, patch=None) -> None:
    """Make `Data/vendor.csv` read as `SF_DATALESS` in this process."""
    info = os.stat(base / CLOUD_FILE)
    dataless = {(info.st_dev, info.st_ino)}
    flags = lambda stat: _repro_state.SF_DATALESS if (stat.st_dev, stat.st_ino) in dataless else 0  # noqa: E731
    if patch is None:
        _repro_state.file_flags = flags
    else:
        patch.setattr(_repro_state, 'file_flags', flags)


# ---------------------------------------------------------------------------
# Browser tests
# ---------------------------------------------------------------------------

import json  # noqa: E402
from urllib.parse import quote  # noqa: E402

pytest.importorskip('playwright.sync_api')
from playwright.sync_api import sync_playwright  # noqa: E402
import plan_dashboard as dashboard  # noqa: E402
import uvicorn  # noqa: E402


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
def states(tmp_path_factory):
    base = tmp_path_factory.mktemp('repro-states')
    root = build_state_fixture(base)
    patch = pytest.MonkeyPatch()
    simulate_online_only(base, patch)
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
    yield f'http://127.0.0.1:{port}'
    server.should_exit = True
    thread.join(5)
    dashboard.PLAN_ROOT = previous
    patch.undo()


def open_view(browser, url, path='', layout='graph', selected=''):
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    nav = {'layout': layout, 'expanded': list(TASKS), 'selected': selected}
    page.goto(f'{url}/#/{path}?repro=' + quote(json.dumps(nav)))
    return page


def classes(page, selector):
    return set(page.locator(selector).get_attribute('class').split())


def test_graph_cards_carry_the_reported_state_on_the_border_and_their_own_on_the_fill(browser, states):
    page = open_view(browser, states)
    page.wait_for_selector('#repro-node-vendor-rows')
    assert {'rp-stale'} <= classes(page, '#repro-node-clean') and 'rp-inherited' not in classes(page, '#repro-node-clean')
    for name in ('merge', 'report'):
        assert {'rp-stale', 'rp-inherited'} <= classes(page, f'#repro-node-{name}')
        assert 'stale · upstream' in page.locator(f'#repro-node-{name}').inner_text()
    assert {'rp-stale', 'rp-hatched'} <= classes(page, '#repro-node-vendor-join')
    assert 'online-only' in page.locator('#repro-node-vendor-join .repro-cloud-tag').inner_text()
    assert {'rp-unverified', 'rp-hatched'} <= classes(page, '#repro-node-vendor-rows')
    assert 'unverified · online-only' in page.locator('#repro-node-vendor-rows').inner_text()
    assert {'rp-fresh', 'is-check'} <= classes(page, '#repro-node-codebook-check')
    assert 'rp-hatched' in classes(page, '.rp-task[data-task="03-vendor-archive"]')
    assert 'rp-hatched' not in classes(page, '.rp-task[data-task="02-panel-model"]')
    legend = page.locator('[data-rp-menu=legend] .rp-menu-body').text_content()
    assert 'unverified' in legend and 'external' not in legend
    for line in ("tinted the step's own state", 'empty inherited from upstream', 'hatched online-only here'):
        assert line in ' '.join(legend.split())
    page.close()


def test_tree_rows_count_states_and_steps_wear_both_channels(browser, states):
    page = open_view(browser, states, '02-panel-model', layout='tree')
    page.wait_for_selector('#nav-tree .nav-step[data-tree-step="merge"]')
    rollup = page.locator('#nav-tree .task-node[data-path="02-panel-model"] > .nav-repro-rollup')
    assert rollup.inner_text().split() == ['◐3', '○1', '✕1']
    assert 'rp-hatched' in classes(page, '#nav-tree .task-node[data-path="03-vendor-archive"] > .nav-repro-rollup')
    # The rollup sits on its own line, so the row's slug keeps the width it has without one.
    widths = page.evaluate('''() => Array.from(document.querySelectorAll('#nav-tree .task-node > .nav-repro-rollup')).map(badge => {
      const slug = badge.parentElement.querySelector(':scope > .task-row > .task-slug'), before = slug.getBoundingClientRect().width;
      badge.hidden = true; const after = slug.getBoundingClientRect().width; badge.hidden = false; return [before, after]; })''')
    assert len(widths) == 3 and all(before == after for before, after in widths)
    assert {'rp-stale', 'rp-inherited'} <= classes(page, '.nav-step[data-tree-step="merge"]')
    assert {'rp-stale', 'rp-hatched'} <= classes(page, '.nav-step[data-tree-step="vendor-join"]')
    assert page.locator('.nav-step[data-tree-step="codebook-check"] .nav-step-state').inner_text() == 'fresh · check'
    page.close()


def test_panel_names_the_own_evidence_the_origin_and_each_online_only_file(browser, states):
    page = open_view(browser, states, '02-panel-model', layout='tree', selected='vendor-join')
    page.wait_for_selector('#repro-detail .repro-own-line')
    own = page.locator('#repro-detail .repro-own-line')
    assert own.inner_text().startswith('Own evidence: unverified — dependency Data/vendor.csv is online-only here. '
                                       "A build runs it only if a producer's rerun changes its inputs, and then needs its online-only files here.")
    assert own.locator('[data-rp-action=related]').inner_text() == 'clean'
    summary = page.locator('#repro-detail .repro-online-summary').inner_text()
    assert '1 file online-only here (2.3 MiB).' in summary
    online = page.locator('#repro-detail li.is-online-only')
    assert online.count() == 1 and '2.3 MiB' in online.inner_text()
    online.locator('a').hover()
    page.wait_for_selector('#file-peek :text("Online-only here (2.3 MiB)")')
    page.mouse.move(2, 2)
    page.locator('#nav-tree .nav-step[data-tree-step="merge"]').click()
    page.wait_for_selector('#repro-detail[data-step="merge"] .repro-own-line')
    assert page.locator('#repro-detail .repro-own-line').inner_text().startswith(
        "Own evidence: fresh. A build reruns it only if a producer's rerun changes its inputs.")
    assert page.locator('#repro-detail .repro-online-summary').count() == 0
    page.close()


def test_file_view_of_an_online_only_file_shows_its_size_and_never_loads_it(browser, states):
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    loaded = []
    page.on('request', lambda request: loaded.append(request.url) if '/files/Data/vendor.csv' in request.url else None)
    page.goto(f'{states}/#/02-panel-model?file=Data%2Fvendor.csv')
    page.wait_for_selector('#active-node :text("Online-only here (2.3 MiB)")')
    assert page.locator('#active-node .artifact-action').count() == 0  # no Download link
    page.wait_for_timeout(300)
    assert loaded == []
    page.close()


def test_build_menu_sends_only_and_shows_a_gated_builds_files(browser, states):
    page = open_view(browser, states)
    page.wait_for_selector('.rp-task[data-task="02-panel-model"] .rp-build-chip')
    sent = []

    def build(route):
        if route.request.method != 'POST':
            return route.continue_()
        sent.append(json.loads(route.request.post_data))
        route.fulfill(status=409, content_type='application/json', body=json.dumps({'detail': 'refused in test'}))
    page.route('**/api/repro/build?*', build)
    page.route('**/api/repro/build', build)
    page.evaluate("""reproOpenBuildMenu(document.querySelector('.rp-task[data-task="02-panel-model"] .rp-build-chip'))""")
    menu = page.locator('#rp-build-menu')
    assert menu.locator('[data-mode=only] code').inner_text() == 'superra repro build 02-panel-model --only'
    assert menu.locator('[data-mode=""] code').inner_text() == 'superra repro build 02-panel-model'
    assert menu.locator('[data-mode=force] .rp-build-est').inner_text() == (
        'Would run nothing: 1 file not on this machine (2.3 MiB): Data/vendor.csv')
    menu.locator('[data-mode=only]').click()
    page.wait_for_function('() => _reproBuild.error')
    assert sent == [{'target': '02-panel-model', 'only': True, 'force': False}]
    detail = page.evaluate("""() => { _reproBuild.error = ''; _reproBuild.wt = ACTIVE_WT;
      _reproBuild.job = {ended_at: Date.now() / 1000, returncode: 1, summary: 'Error: 1 file(s) the build reads are not on this machine, so nothing was run:',
        detail: ['  Data/vendor.csv  2.3 MB  online-only here  (read by vendor-join)'], log_tail: ''};
      reproPaintBuild(); return document.querySelector('.rp-build-detail').textContent; }""")
    assert 'Data/vendor.csv' in detail and 'online-only here' in detail
    page.close()
