#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyobjc-framework-Cocoa==12.2.2; sys_platform == 'darwin'",
#     "pyobjc-core==12.2.2; sys_platform == 'darwin'",
# ]
#
# [tool.uv]
# exclude-newer = "2026-10-10T00:00:00Z"
# ///
"""Request a coordinated read of macOS File Provider files."""

import argparse
import os
import sys


UF_DATALESS = 0x40000000  # macOS file flag for online-only contents.


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()
    if sys.platform != "darwin":
        parser.error("File Provider downloads require macOS")

    from Foundation import NSFileCoordinator, NSURL

    failed = False
    for path in args.files:
        coordinator = NSFileCoordinator.alloc().initWithFilePresenter_(None)
        url = NSURL.fileURLWithPath_(os.path.abspath(path))
        error = coordinator.coordinateReadingItemAtURL_options_error_byAccessor_(
            url, 0, None, lambda local_url: None
        )
        if error is None:
            try:
                dataless = bool(os.lstat(path).st_flags & UF_DATALESS)
            except OSError as exc:
                error = exc
            else:
                print(path, "still online-only" if dataless else "local")
                failed |= dataless
                continue

        print(path, error, file=sys.stderr)
        failed = True
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
