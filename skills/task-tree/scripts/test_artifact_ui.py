#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest", "httpx", "pyyaml", "fastapi", "jinja2", "playwright"]
# ///
"""Attachment-tree and full-width reading-pane regressions."""

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


def _attachment_tree(tmp_path: Path, *, label: str = "A") -> Path:
    root = tmp_path / "superRA"
    root.mkdir(parents=True)
    _write_task_md(root / "task.md", f"Attachment project {label}", "in-progress")
    task = root / "01-reader"
    task.mkdir()
    _write_task_md(
        task / "task.md",
        f"Attachment reader {label}",
        "in-progress",
        objective="Read task-local attachments in the normal detail pane.",
    )
    attachments = task / "attachments"
    (attachments / "notes").mkdir(parents=True)
    (attachments / "images").mkdir()
    (attachments / "note.md").write_text(
        "# Main note\n\n[report](notes/report.md)\n\n"
        "![tiny](images/tiny.png)\n\n<script>window.noteEvil=1</script>\n",
        encoding="utf-8",
    )
    (attachments / "notes" / "report.md").write_text(
        "# Nested report\n\n![tiny](../images/tiny.png)\n",
        encoding="utf-8",
    )
    (attachments / "model.py").write_text(
        "def answer(value: int) -> int:\n    return value + 42\n",
        encoding="utf-8",
    )
    (attachments / "solver.jl").write_text(
        "function twice(x)\n    2x\nend\n", encoding="utf-8"
    )
    (attachments / "ANALYSIS.R").write_text(
        "estimate <- lm(y ~ x, data = d)\n", encoding="utf-8"
    )
    png = _write_tiny_png(attachments / "images" / "tiny.png")
    (attachments / "paper.pdf").write_bytes(
        b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\n%%EOF\n"
    )
    (attachments / "readme.txt").write_text(
        f"attachment from {label}\n", encoding="utf-8"
    )

    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {"kernelspec": {"language": "python", "name": "python3"}},
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["## Notebook\n\n$x^2$ ![tiny](attachment:tiny.png)"],
                "attachments": {
                    "tiny.png": {
                        "image/png": base64.b64encode(png).decode("ascii")
                    }
                },
            },
            {"cell_type": "raw", "metadata": {}, "source": ["<b>raw text</b>"]},
            {
                "cell_type": "code",
                "metadata": {},
                "execution_count": 1,
                "source": ["print('hello')"],
                "outputs": [
                    {"output_type": "stream", "name": "stdout", "text": "hello\n"},
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
                            "text/html": (
                                "<b id='safe-html'>safe</b>"
                                "<script>window.notebookEvil=1</script>"
                            )
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
                                "<svg xmlns='http://www.w3.org/2000/svg' "
                                "onload='window.svgEvil=1'><script>"
                                "window.svgEvil=2</script><circle r='3'/></svg>"
                            )
                        },
                    },
                    {
                        "output_type": "display_data",
                        "metadata": {},
                        "data": {"application/javascript": "window.outputEvil=1"},
                    },
                ],
            },
        ],
    }
    (attachments / "model.ipynb").write_text(
        json.dumps(notebook), encoding="utf-8"
    )
    following = root / "02-following"
    following.mkdir()
    _write_task_md(
        following / "task.md",
        "Following task",
        "not-started",
        objective="Verify attachment navigation exits to the following task.",
    )
    return root


def _have_chromium() -> bool:
    try:
        from playwright.sync_api import sync_playwright

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
    assert plan_dashboard._wait_for_bind(port, timeout=5)
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


def _broadcast_task(loop, task_path):
    async def broadcast():
        state = plan_dashboard._worktree_cache[plan_dashboard._launch_wt_id]
        await plan_dashboard._broadcast(
            f"task:{task_path}",
            plan_dashboard._render_nav_node(state.task_index[task_path]),
            state.wt_id,
        )

    asyncio.run_coroutine_threadsafe(broadcast(), loop).result(timeout=5)


class TestAttachmentSurfaceServer:
    def test_shell_has_one_reading_surface_and_offline_payload(self, tmp_path):
        from starlette.testclient import TestClient

        root = _attachment_tree(tmp_path)
        plan_dashboard.PLAN_ROOT = root
        plan_dashboard._jinja_env = None
        plan_dashboard.rebuild_tree()
        with TestClient(plan_dashboard.app) as client:
            page = client.get("/").text
            assert 'id="artifact-sidecar"' not in page
            assert "artifact-toggle-btn" not in page
            assert page.index("/static/purify.min.js") < page.index(
                "/static/notebook.min.js"
            )
            manifest = client.get(
                "/api/artifacts", params={"task": "01-reader"}
            ).json()
            assert manifest["files"]
            assert all(
                entry["path"].startswith("attachments/")
                and "placement" not in entry
                for entry in manifest["files"]
            )
            assert "model.py" not in client.get("/kanban").text
            graph = client.get(
                "/api/children-graph", params={"root": "01-reader"}
            ).json()
            assert "model.py" not in json.dumps(graph)
        standalone = plan_dashboard.render_standalone_html(root)
        assert "var STANDALONE_ARTIFACTS =" in standalone
        assert "function loadActiveArtifact" in standalone
        assert "notebook.min.js" not in standalone
        assert "0.8.3" in standalone


@pytest.mark.skipif(not _have_chromium(), reason="playwright+chromium unavailable")
class TestAttachmentSurfaceBrowser:
    def test_tree_routing_renderers_history_and_hot_reload(self, tmp_path):
        from playwright.sync_api import sync_playwright

        root = _attachment_tree(tmp_path)
        port, server, loop, thread = _start_server(root)
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                page.goto(
                    f"http://127.0.0.1:{port}/#/01-reader",
                    wait_until="domcontentloaded",
                )
                branch = page.locator(
                    '.task-node[data-path="01-reader"] > .attachment-branch'
                )
                branch.wait_for()
                assert page.locator("#artifact-sidecar").count() == 0
                assert page.locator(".artifact-toggle-btn").count() == 0
                assert branch.locator(".attachment-branch-toggle").count() == 1
                assert branch.locator(".attachment-file-row").count() == 9
                assert branch.locator(".attachment-branch-children").is_hidden()
                assert branch.locator(".attachment-branch-toggle").get_attribute(
                    "role"
                ) == "treeitem"
                assert branch.locator(".attachment-branch-children").get_attribute(
                    "role"
                ) == "group"
                page.wait_for_function(
                    "() => document.querySelector("
                    "'.task-node[data-path=\"01-reader\"] > .task-row')"
                    ".getAttribute('tabindex') === '0'"
                )
                page.locator("#pin-toggle").focus()
                page.keyboard.press("Tab")
                assert page.evaluate(
                    "document.activeElement === document.querySelector("
                    "'.task-node[data-path=\"01-reader\"] > .task-row')"
                )
                page.keyboard.press("ArrowRight")
                assert page.evaluate(
                    "document.activeElement.classList.contains("
                    "'attachment-branch-toggle')"
                )
                assert page.locator(
                    "#nav-tree [tabindex='0']"
                ).count() == 1
                page.keyboard.press("ArrowRight")
                assert branch.locator(".attachment-branch-children").is_visible()
                page.keyboard.press("ArrowRight")
                assert page.evaluate(
                    "document.activeElement.classList.contains("
                    "'attachment-directory-row')"
                )
                page.keyboard.press("ArrowDown")
                assert page.evaluate(
                    "document.activeElement.classList.contains('attachment-file-row')"
                )
                page.keyboard.press("ArrowDown")
                assert page.evaluate(
                    "document.activeElement.textContent.trim().includes('notes')"
                )
                page.keyboard.press("ArrowRight")
                assert page.evaluate(
                    "document.activeElement.dataset.artifactPath"
                    " === 'attachments/notes/report.md'"
                )
                page.keyboard.press("ArrowLeft")
                page.keyboard.press("ArrowLeft")
                page.keyboard.press("ArrowLeft")
                assert page.evaluate(
                    "document.activeElement.classList.contains("
                    "'attachment-branch-toggle')"
                )
                page.keyboard.press("ArrowLeft")
                assert branch.locator(".attachment-branch-children").is_hidden()
                page.keyboard.press("ArrowLeft")
                assert page.evaluate(
                    "document.activeElement === document.querySelector("
                    "'.task-node[data-path=\"01-reader\"] > .task-row')"
                )
                page.keyboard.press("ArrowRight")
                assert page.evaluate(
                    "document.activeElement.classList.contains("
                    "'attachment-branch-toggle')"
                )
                page.keyboard.press("ArrowDown")
                assert page.evaluate(
                    "document.activeElement === document.querySelector("
                    "'.task-node[data-path=\"02-following\"] > .task-row')"
                )
                branch.locator(".attachment-branch-toggle").click()
                assert branch.locator(".attachment-branch-children").is_visible()
                assert branch.locator(".attachment-directory-label").all_inner_texts() == [
                    "images",
                    "notes",
                ]

                task_html = page.inner_html("#active-node")
                branch.locator(
                    '.attachment-file-row[data-artifact-path="attachments/note.md"]'
                ).click()
                page.wait_for_selector("#active-node .artifact-markdown-preview h1")
                assert page.inner_text("#active-node h1") == "Main note"
                assert "?attachment=attachments%2Fnote.md" in page.evaluate(
                    "location.hash"
                )
                assert page.locator("#active-node script").count() == 0
                report_href = page.get_attribute(
                    "#active-node .artifact-markdown-preview a", "href"
                )
                image_src = page.get_attribute(
                    "#active-node .artifact-markdown-preview img", "src"
                )
                assert "path=attachments%2Fnotes%2Freport.md" in report_href
                assert "path=attachments%2Fimages%2Ftiny.png" in image_src
                assert page.locator("#children-dag").inner_html() == ""
                assert page.locator(
                    '.attachment-file-row[data-artifact-path="attachments/note.md"].nav-active'
                ).count() == 1

                for artifact_path, language in (
                    ("attachments/model.py", "python"),
                    ("attachments/solver.jl", "julia"),
                    ("attachments/ANALYSIS.R", "r"),
                ):
                    branch.locator(
                        f'.attachment-file-row[data-artifact-path="{artifact_path}"]'
                    ).click()
                    code = page.locator(
                        f"#active-node code.language-{language}"
                    )
                    code.wait_for()
                    assert "hljs-" in code.inner_html()
                    assert code.locator("[class*='hljs-']").evaluate_all(
                        "els => els.some(el => getComputedStyle(el).color"
                        " !== getComputedStyle(el.parentElement).color)"
                    )

                branch.locator(
                    '.attachment-file-row[data-artifact-path="attachments/model.ipynb"]'
                ).click()
                page.wait_for_selector("#active-node .notebook-preview .nb-code-cell")
                page.wait_for_selector("#active-node #safe-html")
                page.locator("#active-node .katex").nth(1).wait_for()
                assert page.locator("#active-node .nb-markdown-cell").count() == 1
                assert page.locator("#active-node section.nb-raw-cell").count() == 1
                assert page.locator("#active-node .nb-stream-output").count() == 1
                assert page.locator("#active-node .nb-error-output").count() == 1
                assert page.locator("#active-node #safe-html").count() == 1
                assert page.locator("#active-node .katex").count() >= 2
                assert page.locator("#active-node .nb-unsupported-output").count() == 1
                assert page.locator("#active-node script").count() == 0
                assert page.locator("#active-node [onload]").count() == 0
                assert page.evaluate(
                    "typeof window.notebookEvil === 'undefined'"
                    " && typeof window.svgEvil === 'undefined'"
                    " && typeof window.outputEvil === 'undefined'"
                )

                page.go_back()
                page.wait_for_selector("#active-node code.language-r")
                page.go_back()
                page.wait_for_selector("#active-node code.language-julia")
                page.locator(".attachment-owner-action").click()
                page.wait_for_function(
                    "() => !location.hash.includes('attachment=')"
                )
                page.wait_for_function(
                    "() => document.querySelector('#active-node')"
                    ".textContent.includes('Read task-local attachments')"
                )
                assert "Read task-local attachments" in page.inner_text("#active-node")
                assert page.inner_html("#active-node") != task_html or task_html

                branch.locator(
                    '.attachment-file-row[data-artifact-path="attachments/note.md"]'
                ).click()
                page.wait_for_selector("#active-node .artifact-markdown-preview h1")
                deadline = time.monotonic() + 5
                while (
                    not plan_dashboard._worktree_clients.get(
                        plan_dashboard._launch_wt_id
                    )
                    and time.monotonic() < deadline
                ):
                    time.sleep(0.02)
                original_hash = page.evaluate("location.hash")
                _broadcast_task(loop, "01-reader")
                page.wait_for_function(
                    "() => document.querySelector("
                    "'.task-node[data-path=\"01-reader\"] > .attachment-branch')"
                )
                page.wait_for_selector("#active-node .artifact-markdown-preview h1")
                assert page.evaluate("location.hash") == original_hash
                assert page.inner_text("#active-node h1") == "Main note"
                assert page.locator(
                    '.task-node[data-path="01-reader"] '
                    "> .attachment-branch.expanded"
                ).count() == 1
                (root / "01-reader" / "attachments" / "note.md").write_text(
                    "# Updated attachment\n", encoding="utf-8"
                )
                _broadcast_manifest(loop, "01-reader")
                page.wait_for_function(
                    "() => document.querySelector('#active-node h1')"
                    " && document.querySelector('#active-node h1').textContent"
                    ".includes('Updated attachment')"
                )
                assert "?attachment=attachments%2Fnote.md" in page.evaluate(
                    "location.hash"
                )
                browser.close()
        finally:
            _stop_server(server, thread)

    def test_artifact_pane_open_hands_the_file_to_the_host(self, tmp_path, monkeypatch):
        """The pane's Open button behaves like the card head's task.md button: a
        plain click runs /api/open on the server's host and the page stays put,
        while the /api/artifact href remains for a modifier click.  Driven in a
        real browser — the delegated handler, the hit area, and the fetch are all
        seam behavior a source assertion cannot reach."""
        from playwright.sync_api import sync_playwright

        root = _attachment_tree(tmp_path)
        spawned: list[list[str]] = []
        monkeypatch.setattr(plan_dashboard, "_spawn", spawned.append)
        port, server, loop, thread = _start_server(root)
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page(viewport={"width": 1200, "height": 800})
                page.goto(
                    f"http://127.0.0.1:{port}/#/01-reader",
                    wait_until="domcontentloaded",
                )
                branch = page.locator(
                    '.task-node[data-path="01-reader"] > .attachment-branch'
                )
                branch.wait_for()
                branch.locator(".attachment-branch-toggle").click()
                branch.locator(
                    '.attachment-file-row[data-artifact-path="attachments/readme.txt"]'
                ).click()
                page.wait_for_selector("#active-node .attachment-active-body pre")
                open_btn = page.locator(
                    "#active-node .artifact-action", has_text="Open"
                )
                assert open_btn.count() == 1
                assert open_btn.get_attribute("data-open-path") == (
                    "superRA/01-reader/attachments/readme.txt"
                )
                assert "/api/artifact" in open_btn.get_attribute("href")
                open_btn.click()
                for _ in range(100):
                    if spawned:
                        break
                    time.sleep(0.05)
                # Plain click ran the route, not a navigation: the pane still
                # holds the same attachment.
                assert page.evaluate("location.hash") == (
                    "#/01-reader?attachment=attachments%2Freadme.txt"
                )
                browser.close()
        finally:
            _stop_server(server, thread)
        assert len(spawned) == 1
        assert spawned[0][-1] == str(
            (root / "01-reader" / "attachments" / "readme.txt").resolve()
        )

    def test_standalone_attachment_tree_and_download(self, tmp_path):
        from playwright.sync_api import sync_playwright

        root = _attachment_tree(tmp_path)
        export = tmp_path / "dashboard.html"
        export.write_text(
            plan_dashboard.render_standalone_html(root), encoding="utf-8"
        )
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={"width": 1200, "height": 800})
            page.goto(export.as_uri() + "#/01-reader")
            branch = page.locator(
                '.task-node[data-path="01-reader"] > .attachment-branch'
            )
            branch.wait_for()
            branch.locator(".attachment-branch-toggle").click()
            branch.locator(
                '.attachment-file-row[data-artifact-path="attachments/readme.txt"]'
            ).click()
            page.wait_for_selector("#active-node .attachment-active-body pre")
            assert "attachment from A" in page.inner_text(
                "#active-node .attachment-active-body"
            )
            download = page.locator("#active-node .artifact-action", has_text="Download")
            assert download.get_attribute("href").startswith("data:text/plain")
            browser.close()

    def test_worktree_switch_keeps_attachment_route_isolated(
        self, tmp_path, monkeypatch
    ):
        from playwright.sync_api import sync_playwright

        root_a = _attachment_tree(tmp_path / "wt-a", label="A")
        root_b = _attachment_tree(tmp_path / "wt-b", label="B")

        def info(root, branch):
            return WorktreeInfo(
                path=str(root.parent),
                branch=branch,
                head="a" * 40,
                plan_root=str(root),
                plan_title=branch,
                is_current=branch == "main",
                is_locked=False,
                is_prunable=False,
                is_agent=False,
                last_activity=1.0,
            )

        monkeypatch.setattr(
            plan_dashboard,
            "discover_worktrees",
            lambda: [info(root_a, "main"), info(root_b, "other")],
        )
        port, server, _loop, thread = _start_server(root_a)
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page()
                page.goto(f"http://127.0.0.1:{port}/#/01-reader")
                branch = page.locator(
                    '.task-node[data-path="01-reader"] > .attachment-branch'
                )
                branch.wait_for()
                branch.locator(".attachment-branch-toggle").click()
                branch.locator(
                    '[data-artifact-path="attachments/readme.txt"]'
                ).click()
                page.wait_for_selector("#active-node .attachment-active-body pre")
                assert "attachment from A" in page.inner_text("#active-node")
                page.select_option("#worktree-select", "wt-b")
                page.wait_for_function(
                    "() => document.querySelector('#active-node')"
                    ".textContent.includes('attachment from B')"
                )
                assert "attachment=attachments%2Freadme.txt" in page.evaluate(
                    "location.hash"
                )
                browser.close()
        finally:
            _stop_server(server, thread)
