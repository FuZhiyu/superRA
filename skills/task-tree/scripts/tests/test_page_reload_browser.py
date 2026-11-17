"""A page's live stream: one load fetches once, and a reconnect catches up.

uv run --script tests/run_tests.py \
  skills/task-tree/scripts/tests/test_page_reload_browser.py
"""
import socket
import sys
import threading
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from conftest import _write_task_md  # noqa: E402

pytest.importorskip('playwright.sync_api')
from playwright.sync_api import sync_playwright  # noqa: E402
import plan_dashboard as dashboard  # noqa: E402
import uvicorn  # noqa: E402

STREAM = "document.querySelector('.main-content')['htmx-internal-data'].sseEventSource"


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


class Server:
    """The dashboard app on one fixed port, stoppable and restartable."""

    def __init__(self, root: Path):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            self.port = sock.getsockname()[1]
        self.url = f'http://127.0.0.1:{self.port}'
        self.previous = dashboard.PLAN_ROOT
        dashboard.PLAN_ROOT = root

    def start(self):
        for registry in (dashboard._worktree_cache, dashboard._worktree_clients,
                         dashboard._worktree_watchers, dashboard._worktree_locks):
            registry.clear()
        self.server = uvicorn.Server(uvicorn.Config(
            dashboard.app, host='127.0.0.1', port=self.port, log_level='error',
            timeout_graceful_shutdown=1))
        self.thread = threading.Thread(target=self.server.run, daemon=True)
        self.thread.start()
        deadline = time.monotonic() + 15
        while not self.server.started:
            assert time.monotonic() < deadline, 'server did not start'
            time.sleep(.05)

    def stop(self):
        self.server.should_exit = True
        self.thread.join(10)
        assert not self.thread.is_alive(), 'server did not stop'


@pytest.fixture
def served(tmp_path, monkeypatch):
    root = tmp_path / 'project' / 'superRA'
    root.mkdir(parents=True)
    _write_task_md(root / 'task.md', 'Root', 'not-started', objective='root')
    (root / 'a').mkdir()
    _write_task_md(root / 'a' / 'task.md', 'Alpha', 'not-started', objective='a')
    # A dropped stream is noticed at the next heartbeat.
    monkeypatch.setattr(dashboard, 'HEARTBEAT_INTERVAL', 0.2)
    server = Server(root)
    server.start()
    yield server, root
    server.stop()
    dashboard.PLAN_ROOT = server.previous


def open_page(browser, url):
    page = browser.new_page()
    paths = []
    page.on('request', lambda r: paths.append(r.url.split('?')[0].replace(url, '')))
    page.goto(url + '/#/')
    page.wait_for_selector('#nav-tree [data-path="a"]')
    page.wait_for_function(f'{STREAM} && {STREAM}.readyState === 1')
    return page, paths


def title_shown(page, title):
    page.wait_for_function(
        'title => [...document.querySelectorAll("#nav-tree [data-path=\'a\']")]'
        '.some(row => row.textContent.includes(title))', arg=title, timeout=15000)


def wait_for(condition, timeout=10):
    deadline = time.monotonic() + timeout
    while not condition():
        assert time.monotonic() < deadline, 'condition not reached'
        time.sleep(.05)


def test_a_first_load_fetches_each_payload_once(browser, served):
    server, _ = served
    page, paths = open_page(browser, server.url)
    page.wait_for_timeout(1500)
    for path in ('/nav', '/api/repro/graph', '/api/repro/status'):
        assert paths.count(path) == 1, (path, paths)
    page.close()


def test_a_page_open_across_a_server_restart_shows_the_edit_made_while_down(browser, served):
    server, root = served
    page, _ = open_page(browser, server.url)
    server.stop()
    _write_task_md(root / 'a' / 'task.md', 'Alpha edited', 'not-started', objective='a')
    server.start()  # seeds its cache from disk, so it matches the edit
    title_shown(page, 'Alpha edited')
    page.close()


def test_a_reconnect_after_another_clients_watcher_came_and_went_shows_the_edit(browser, served):
    server, root = served
    page, _ = open_page(browser, server.url)
    page.evaluate(f'() => {{ window.__stream = {STREAM}; window.__stream.close(); }}')
    wait_for(lambda: not dashboard._worktree_clients)
    _write_task_md(root / 'a' / 'task.md', 'Alpha edited', 'not-started', objective='a')
    other, _ = open_page(browser, server.url)  # its watcher start rebuilds the cache
    title_shown(other, 'Alpha edited')
    other.close()
    wait_for(lambda: not dashboard._worktree_watchers)
    # The extension's own reconnect path, as after a dropped connection.
    page.evaluate('() => window.__stream.onerror(new Event("error"))')
    title_shown(page, 'Alpha edited')
    page.close()
