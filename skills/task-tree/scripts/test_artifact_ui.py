#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest", "httpx", "pyyaml", "fastapi", "jinja2", "playwright"]
# ///
"""Dashboard companion-file canvas regressions."""

from __future__ import annotations

import asyncio
import base64
import json
import socket
import sys
import threading
import time
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

import _artifacts
import plan_dashboard
from _worktree_discovery import WorktreeInfo
from conftest import _write_task_md, _write_tiny_png


def _artifact_tree(tmp_path: Path, *, label: str = "A") -> Path:
    root = tmp_path / "superRA"
    root.mkdir(parents=True)
    _write_task_md(root / "task.md", f"Artifact project {label}", "in-progress",
                   objective="Browse task-local files.")
    task = root / "01-artifact"
    task.mkdir()
    _write_task_md(
        task / "task.md",
        f"Artifact task {label}",
        "in-progress",
        objective="\n\n".join(f"Reading paragraph {i}." for i in range(60)),
    )
    (task / "note.md").write_text(
        "# Direct note\n\n"
        "[nested report](attachments/notes/report.md)\n\n"
        "<img src=\"attachments/nested/figure.png\" onerror=\"window.noteEvil=1\">\n",
        encoding="utf-8",
    )
    (task / "model.py").write_text("def answer():\n    return 42\n", encoding="utf-8")
    (task / "solver.jl").write_text("function twice(x)\n    2x\nend\n", encoding="utf-8")
    (task / "ANALYSIS.R").write_text("estimate <- lm(y ~ x, data = d)\n", encoding="utf-8")

    attachments = task / "attachments"
    (attachments / "notes").mkdir(parents=True)
    (attachments / "nested").mkdir()
    (attachments / "notes" / "report.md").write_text(
        "# Nested report\n\n"
        "[figure file](../nested/figure.png)\n\n"
        "![figure](../nested/figure.png)\n\n"
        "<script>window.reportEvil=1</script>\n",
        encoding="utf-8",
    )
    png = _write_tiny_png(attachments / "nested" / "figure.png")
    (attachments / "readme.txt").write_text(f"attachment from {label}\n", encoding="utf-8")
    (attachments / "paper.pdf").write_bytes(
        b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\n%%EOF\n"
    )
    (task / "legacy.bin").write_bytes(b"\x00legacy")

    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {"kernelspec": {"language": "python", "name": "python3"}},
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Notebook markdown\n\n",
                    "Inline math $x^2$ and ![attached](attachment:tiny.png).\n",
                ],
                "attachments": {
                    "tiny.png": {
                        "image/png": base64.b64encode(png).decode("ascii"),
                    }
                },
            },
            {
                "cell_type": "raw",
                "metadata": {},
                "source": ["<b>raw stays text</b>"],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "execution_count": 1,
                "source": ["print('hello')\n"],
                "outputs": [
                    {"output_type": "stream", "name": "stdout", "text": ["hello\n"]},
                    {
                        "output_type": "error",
                        "ename": "ValueError",
                        "evalue": "bad",
                        "traceback": ["ValueError: bad"],
                    },
                    {
                        "output_type": "display_data",
                        "metadata": {},
                        "data": {
                            "text/html": [
                                "<b id='safe-html'>safe html</b>",
                                "<script>window.notebookEvil=1</script>",
                                "<img src='missing.png' onerror='window.notebookEvil=2'>",
                            ]
                        },
                    },
                    {
                        "output_type": "display_data",
                        "metadata": {},
                        "data": {"text/markdown": "**markdown output**"},
                    },
                    {
                        "output_type": "display_data",
                        "metadata": {},
                        "data": {"text/latex": r"\alpha + \beta"},
                    },
                    {
                        "output_type": "display_data",
                        "metadata": {},
                        "data": {
                            "image/svg+xml": (
                                "<svg xmlns='http://www.w3.org/2000/svg' onload='window.svgEvil=1'>"
                                "<script>window.svgEvil=2</script><circle cx='4' cy='4' r='3'/></svg>"
                            )
                        },
                    },
                    {
                        "output_type": "display_data",
                        "metadata": {},
                        "data": {"application/javascript": "window.outputEvil=1"},
                    },
                    {
                        "output_type": "display_data",
                        "metadata": {},
                        "data": {
                            "application/vnd.jupyter.widget-view+json": {
                                "model_id": "unsafe-widget"
                            }
                        },
                    },
                ],
            },
        ],
    }
    (task / "model.ipynb").write_text(json.dumps(notebook), encoding="utf-8")
    return root


def _have_chromium() -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return False
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            browser.close()
        return True
    except Exception:
        return False


def _start_server(plan_root: Path):
    import uvicorn

    plan_dashboard.PLAN_ROOT = plan_root
    plan_dashboard._jinja_env = None
    plan_dashboard._worktree_cache.clear()
    plan_dashboard.rebuild_tree()

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    loop = asyncio.new_event_loop()
    server = uvicorn.Server(
        uvicorn.Config(
            plan_dashboard.app,
            host="127.0.0.1",
            port=port,
            log_level="warning",
        )
    )
    plan_dashboard._server = server

    def run():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(server.serve())

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    assert plan_dashboard._wait_for_bind(port, timeout=5), "dashboard did not bind"
    return port, server, loop, thread


def _stop_server(server, thread):
    server.should_exit = True
    thread.join(timeout=5)
    plan_dashboard._worktree_cache.clear()


def _broadcast_manifest(loop, task_path):
    async def broadcast():
        state = plan_dashboard._worktree_cache[plan_dashboard._launch_wt_id]
        manifest = _artifacts.build_manifest(
            state.plan_root, state.task_index[task_path]
        )
        await plan_dashboard._broadcast(
            f"artifacts:{task_path}",
            json.dumps(manifest, separators=(",", ":")),
            state.wt_id,
        )

    asyncio.run_coroutine_threadsafe(broadcast(), loop).result(timeout=5)


class TestArtifactCanvasServerRendering:
    def test_vendor_shell_and_standalone_payload(self, tmp_path):
        from starlette.testclient import TestClient

        root = _artifact_tree(tmp_path)
        plan_dashboard.PLAN_ROOT = root
        plan_dashboard._jinja_env = None
        plan_dashboard.rebuild_tree()
        with TestClient(plan_dashboard.app, raise_server_exceptions=True) as client:
            page = client.get("/").text
            assert 'id="artifact-sidecar"' in page
            assert page.index("/static/purify.min.js") < page.index("/static/notebook.min.js")
            notebook = client.get("/static/notebook.min.js")
            assert notebook.status_code == 200
            assert notebook.headers["content-type"].startswith("text/javascript")
            assert b"0.8.3" in notebook.content
            manifest = client.get(
                "/api/artifacts", params={"task": "01-artifact"}
            ).json()
            placements = [entry["placement"] for entry in manifest["files"]]
            assert placements[:5] == ["direct"] * 5
            assert "attachment" in placements[5:-1]
            assert placements[-1] == "legacy"

        assets = plan_dashboard._build_standalone_assets()
        assert "0.8.3" in assets["notebook_js"]
        standalone = plan_dashboard.render_standalone_html(root)
        assert "var STANDALONE_ARTIFACTS =" in standalone
        assert "function renderNotebookPreview" in standalone
        assert "cdn.jsdelivr.net/npm/notebookjs" not in standalone

    def test_artifact_event_stays_task_scoped(self, tmp_path):
        root = _artifact_tree(tmp_path)
        state = plan_dashboard._build_worktree_state("selected", root)
        task = state.task_index["01-artifact"]
        manifest = _artifacts.build_manifest(root, task)
        assert manifest["task"] == "01-artifact"
        assert all("children" not in entry for entry in manifest["files"])


@pytest.mark.skipif(not _have_chromium(), reason="playwright+chromium unavailable")
class TestArtifactCanvasBrowser:
    def test_live_canvas_rendering_sanitization_and_hot_reload(self, tmp_path):
        from playwright.sync_api import sync_playwright

        root = _artifact_tree(tmp_path)
        port, server, loop, thread = _start_server(root)
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                page.goto(
                    f"http://127.0.0.1:{port}/#/01-artifact",
                    wait_until="domcontentloaded",
                )
                page.wait_for_selector(".artifact-toggle-btn .artifact-count", timeout=5000)
                page.wait_for_function(
                    "document.querySelector('.artifact-count').textContent === '10'"
                )
                original_hash = page.evaluate("location.hash")
                original_crumbs = page.inner_text("#crumbs")
                page.evaluate(
                    "document.documentElement.setAttribute('data-theme', 'dark');"
                    "document.querySelector('.detail-panel').scrollTop = 120"
                )

                page.click(".artifact-toggle-btn")
                page.wait_for_selector("#artifact-sidecar.open")
                assert page.get_attribute("#artifact-sidecar", "aria-hidden") == "false"
                assert page.get_attribute(".artifact-toggle-btn", "aria-expanded") == "true"
                assert page.evaluate("location.hash") == original_hash
                assert page.inner_text("#crumbs") == original_crumbs
                assert page.get_attribute("html", "data-theme") == "dark"
                groups = page.inner_text("#artifact-list")
                assert groups.index("Companions") < groups.index("Attachments")
                assert "attachments/notes/report.md" in groups
                assert "Other direct files (1)" in groups
                assert page.locator(".artifact-count-btn").count() == 1

                report_row = page.locator(
                    '.artifact-row[data-artifact-path="attachments/notes/report.md"]'
                )
                report_row.get_by_role("button", name="Open").click()
                page.wait_for_selector(".artifact-markdown-preview h1")
                assert "Nested report" in page.inner_text(".artifact-markdown-preview")
                assert page.locator(".artifact-markdown-preview script").count() == 0
                report_link = page.get_attribute(
                    ".artifact-markdown-preview a", "href"
                )
                report_image = page.get_attribute(
                    ".artifact-markdown-preview img", "src"
                )
                assert "task=01-artifact" in report_link
                assert "path=attachments%2Fnested%2Ffigure.png" in report_link
                assert "path=attachments%2Fnested%2Ffigure.png" in report_image
                assert "download=true" in report_row.get_by_role(
                    "link", name="Download"
                ).get_attribute("href")

                for artifact_path, language in (
                    ("model.py", "python"),
                    ("solver.jl", "julia"),
                    ("ANALYSIS.R", "r"),
                ):
                    page.locator(
                        f'.artifact-row[data-artifact-path="{artifact_path}"]'
                    ).get_by_role("button", name="Open").click()
                    page.wait_for_selector(
                        f".artifact-preview-body code.language-{language}"
                    )
                    highlighted = page.inner_html(
                        f".artifact-preview-body code.language-{language}"
                    )
                    assert "hljs-" in highlighted

                page.locator(
                    '.artifact-row[data-artifact-path="model.ipynb"]'
                ).get_by_role("button", name="Open").click()
                page.wait_for_selector(".notebook-preview .nb-code-cell")
                assert page.locator(".notebook-preview .nb-markdown-cell").count() == 1
                assert page.locator(".notebook-preview section.nb-raw-cell").count() == 1
                assert page.locator(".notebook-preview .nb-stream-output").count() == 1
                assert page.locator(".notebook-preview .nb-error-output").count() == 1
                assert page.locator(".notebook-preview #safe-html").count() == 1
                assert page.locator(".notebook-preview .katex").count() >= 1
                assert page.locator(".notebook-preview .nb-unsupported-output").count() == 2
                assert page.locator(".notebook-preview script").count() == 0
                assert page.locator(".notebook-preview [onerror]").count() == 0
                assert page.locator(".notebook-preview [onload]").count() == 0
                attachment_src = page.get_attribute(
                    ".notebook-preview .nb-markdown-cell img", "src"
                )
                assert attachment_src.startswith("data:image/png;base64,")
                assert page.evaluate(
                    "typeof window.notebookEvil === 'undefined'"
                    " && typeof window.svgEvil === 'undefined'"
                    " && typeof window.outputEvil === 'undefined'"
                )

                report = root / "01-artifact" / "attachments" / "notes" / "report.md"
                page.locator(
                    '.artifact-row[data-artifact-path="attachments/notes/report.md"]'
                ).get_by_role("button", name="Open").click()
                page.wait_for_selector(".artifact-markdown-preview h1")
                deadline = time.monotonic() + 5
                while (
                    not plan_dashboard._worktree_clients.get(
                        plan_dashboard._launch_wt_id
                    )
                    and time.monotonic() < deadline
                ):
                    time.sleep(0.02)
                assert plan_dashboard._worktree_clients.get(
                    plan_dashboard._launch_wt_id
                )
                page.eval_on_selector(
                    ".detail-panel", "element => { element.scrollTop = 120; }"
                )
                pre_event_scroll = page.eval_on_selector(
                    ".detail-panel", "element => element.scrollTop"
                )
                report.write_text(
                    "# Updated report\n\n![figure](../nested/figure.png)\n",
                    encoding="utf-8",
                )

                _broadcast_manifest(loop, "01-artifact")
                page.wait_for_function(
                    "(() => {"
                    " const heading = document.querySelector('.artifact-markdown-preview h1');"
                    " return !!heading && heading.textContent.indexOf('Updated report') >= 0;"
                    "})()",
                    timeout=5000,
                )
                assert page.evaluate("location.hash") == original_hash
                assert page.inner_text("#crumbs") == original_crumbs
                assert page.eval_on_selector(
                    ".detail-panel", "element => element.scrollTop"
                ) == pre_event_scroll
                assert page.get_attribute("html", "data-theme") == "dark"

                page.locator(".artifact-close").focus()
                page.keyboard.press("Enter")
                assert page.get_attribute("#artifact-sidecar", "aria-hidden") == "true"
                assert page.get_attribute(".artifact-toggle-btn", "aria-expanded") == "false"
                assert page.evaluate("document.activeElement.classList.contains('artifact-toggle-btn')")
                browser.close()
        finally:
            _stop_server(server, thread)

    @pytest.mark.parametrize("key", ["Enter", "Space"])
    def test_artifact_count_keyboard_opens_files_without_row_activation(
        self, tmp_path, key
    ):
        from playwright.sync_api import sync_playwright

        root = _artifact_tree(tmp_path)
        port, server, _loop, thread = _start_server(root)
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page()
                page.set_default_timeout(5000)
                page.goto(
                    f"http://127.0.0.1:{port}/#/01-artifact",
                    wait_until="domcontentloaded",
                )
                count = page.locator(".artifact-count-btn")
                count.wait_for()
                original_hash = page.evaluate("location.hash")
                original_title = page.inner_text(".active-node-title")
                count.focus()
                page.keyboard.press(key)
                page.wait_for_selector("#artifact-sidecar.open")
                assert page.evaluate("location.hash") == original_hash
                assert page.inner_text(".active-node-title") == original_title
                assert not page.evaluate(
                    "document.activeElement.classList.contains('active-node-title')"
                )

                page.locator(".artifact-close").focus()
                page.keyboard.press("Enter")
                assert page.get_attribute("#artifact-sidecar", "aria-hidden") == "true"
                assert page.evaluate(
                    "document.activeElement.classList.contains('artifact-count-btn')"
                )

                page.evaluate("setActive('')")
                page.wait_for_function("location.hash === '#/'")
                row = page.locator(
                    '#nav-tree .task-node[data-path="01-artifact"] > .task-row'
                )
                row.focus()
                page.keyboard.press("Enter")
                page.wait_for_function("location.hash === '#/01-artifact'")
                page.wait_for_function(
                    "document.querySelector('.active-node-title')"
                    " && document.querySelector('.active-node-title')"
                    ".textContent.includes('Artifact task')"
                )
                browser.close()
        finally:
            _stop_server(server, thread)

    def test_artifact_hot_reload_replaces_stale_preview_when_oversized(
        self, tmp_path
    ):
        from playwright.sync_api import sync_playwright

        root = _artifact_tree(tmp_path)
        port, server, loop, thread = _start_server(root)
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                page.set_default_timeout(5000)
                page.goto(
                    f"http://127.0.0.1:{port}/#/01-artifact",
                    wait_until="domcontentloaded",
                )
                page.wait_for_selector(".artifact-count-btn")
                page.click(".artifact-toggle-btn")
                report_row = page.locator(
                    '.artifact-row[data-artifact-path="attachments/notes/report.md"]'
                )
                report_row.get_by_role("button", name="Open").click()
                page.wait_for_selector(".artifact-markdown-preview h1")

                original_hash = page.evaluate("location.hash")
                original_crumbs = page.inner_text("#crumbs")
                page.evaluate(
                    "document.documentElement.setAttribute('data-theme', 'dark');"
                    "document.querySelector('.detail-panel').scrollTop = 120"
                )
                original_scroll = page.eval_on_selector(
                    ".detail-panel", "element => element.scrollTop"
                )
                report = root / "01-artifact" / "attachments" / "notes" / "report.md"
                report.write_bytes(
                    b"x" * (_artifacts.DEFAULT_ARTIFACT_LIMITS.max_preview_bytes + 1)
                )
                _broadcast_manifest(loop, "01-artifact")

                page.wait_for_selector(
                    ".artifact-preview-body .artifact-state-unavailable"
                )
                assert "exceeds the preview limit" in page.inner_text(
                    ".artifact-preview-body .artifact-state-unavailable"
                )
                assert page.locator(".artifact-markdown-preview").count() == 0
                assert report_row.get_by_role("button", name="Open").count() == 0
                assert page.evaluate("location.hash") == original_hash
                assert page.inner_text("#crumbs") == original_crumbs
                assert page.get_attribute("html", "data-theme") == "dark"
                assert page.eval_on_selector(
                    ".detail-panel", "element => element.scrollTop"
                ) == original_scroll
                browser.close()
        finally:
            _stop_server(server, thread)

    def test_standalone_canvas_previews_embedded_files(self, tmp_path):
        from playwright.sync_api import sync_playwright

        root = _artifact_tree(tmp_path)
        output = tmp_path / "artifact-dashboard.html"
        output.write_text(
            plan_dashboard.render_standalone_html(root, output_path=output),
            encoding="utf-8",
        )
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.goto(output.as_uri() + "#/01-artifact", wait_until="domcontentloaded")
            page.wait_for_selector(".artifact-toggle-btn .artifact-count")
            page.click(".artifact-toggle-btn")
            page.locator(
                '.artifact-row[data-artifact-path="attachments/notes/report.md"]'
            ).get_by_role("button", name="Open").click()
            page.wait_for_selector(".artifact-markdown-preview h1")
            assert page.get_attribute(
                ".artifact-markdown-preview img", "src"
            ).startswith("data:image/png;base64,")
            page.locator(
                '.artifact-row[data-artifact-path="model.ipynb"]'
            ).get_by_role("button", name="Open").click()
            page.wait_for_selector(".notebook-preview .nb-code-cell")
            assert page.locator(".notebook-preview .nb-unsupported-output").count() == 2
            assert page.locator(".artifact-row .artifact-action-disabled").count() == 0
            assert page.evaluate("location.hash") == "#/01-artifact"
            browser.close()

    def test_worktree_switch_refreshes_files_without_changing_task_hash(
        self, tmp_path, monkeypatch
    ):
        from playwright.sync_api import sync_playwright

        root_a = _artifact_tree(tmp_path / "worktree-a", label="A")
        root_b = _artifact_tree(tmp_path / "worktree-b", label="B")
        (root_b / "01-artifact" / "only-b.md").write_text(
            "# Worktree B only\n", encoding="utf-8"
        )
        infos = [
            WorktreeInfo(
                path=str(root_a.parent),
                branch="branch-a",
                head="a" * 12,
                plan_root=str(root_a),
                plan_title="Artifact project A",
                is_current=True,
                is_locked=False,
                is_prunable=False,
                is_agent=False,
                last_activity=2,
            ),
            WorktreeInfo(
                path=str(root_b.parent),
                branch="branch-b",
                head="b" * 12,
                plan_root=str(root_b),
                plan_title="Artifact project B",
                is_current=False,
                is_locked=False,
                is_prunable=False,
                is_agent=False,
                last_activity=1,
            ),
        ]
        monkeypatch.setattr(plan_dashboard, "discover_worktrees", lambda: infos)
        port, server, _loop, thread = _start_server(root_a)
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page()
                page.goto(
                    f"http://127.0.0.1:{port}/#/01-artifact",
                    wait_until="domcontentloaded",
                )
                page.wait_for_function(
                    "document.querySelectorAll('#worktree-select option').length === 2",
                    timeout=5000,
                )
                page.click(".artifact-toggle-btn")
                page.wait_for_function(
                    "document.querySelector('.artifact-count').textContent === '10'"
                )
                page.select_option("#worktree-select", "worktree-b")
                page.wait_for_function(
                    "document.querySelector('.artifact-count').textContent === '11'"
                )
                assert page.evaluate("location.hash") == "#/01-artifact"
                assert "only-b.md" in page.inner_text("#artifact-list")
                assert "wt=worktree-b" in page.evaluate("location.search")
                browser.close()
        finally:
            _stop_server(server, thread)
