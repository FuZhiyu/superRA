#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest",
#     "pyyaml",
#     "fastapi",
#     "jinja2",
#     "uvicorn[standard]",
#     "watchfiles",
#     "httpx",
#     "playwright",
# ]
#
# [tool.uv]
# exclude-newer = "2026-10-10T00:00:00Z"
# ///
"""Run pytest with the locked development dependencies.

    uv run --script tests/run_tests.py skills/task-tree/scripts

Arguments pass through to pytest. Browser tests skip unless the locked
playwright's Chromium is installed.
"""

import os
import sys

import pytest

sys.path.insert(0, os.getcwd())
raise SystemExit(pytest.main(sys.argv[1:]))
