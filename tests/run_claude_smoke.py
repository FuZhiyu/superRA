#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["claude-agent-sdk==0.2.165"]
#
# [tool.uv]
# exclude-newer = "2026-10-10T00:00:00Z"
# ///
"""Run a manual Claude smoke in the locked Agent SDK environment."""

import argparse
import os
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script")
    parser.add_argument("args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    os.execv(sys.executable, [sys.executable, args.script, *args.args])
