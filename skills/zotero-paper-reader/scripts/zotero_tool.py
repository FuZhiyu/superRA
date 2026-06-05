#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyzotero==1.13.0",
# ]
# ///
"""Unified pyzotero command surface for the zotero-paper-reader skill.

Local-first reads through the Zotero Desktop local API, with the Zotero Web API
as a fallback. Every subcommand emits JSON on stdout for agent consumption.
Credentials are read from the environment or a project-local ``Notes/.env`` and
are never printed to stdout/stderr.

Run from anywhere via the bundled path, e.g.:

    uv run --script <skill-root>/scripts/zotero_tool.py health

See ``references/access-modes.md`` for access-mode rules and configuration.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

LOCAL_API_BASE = "http://localhost:23119/api"
# The local API exposes the desktop's default user library at id 0.
LOCAL_LIBRARY_ID = "0"
PDF_MIN_BYTES = 1024


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def emit(payload: object) -> None:
    """Write a JSON result to stdout."""
    json.dump(payload, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


def fail(message: str, code: int = 1) -> "int":
    """Emit a structured error to stderr and return an exit code.

    The message is constructed by the tool, never echoing credential values.
    """
    eprint(f"error: {message}")
    return code


# --------------------------------------------------------------------------- #
# Configuration                                                               #
# --------------------------------------------------------------------------- #


def load_env_file() -> dict[str, str]:
    """Read ``Notes/.env`` from the current working directory if present.

    Returns a mapping of variable name to value. Values are never logged.
    Environment variables already set take precedence over file values.
    """
    env_path = Path("Notes/.env")
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        values[key.strip()] = val.strip().strip('"').strip("'")
    return values


def get_config() -> dict[str, str | None]:
    """Resolve Zotero configuration from the environment, then ``Notes/.env``.

    Environment variables win over file values. Returns only what is present;
    no value is printed.
    """
    file_values = load_env_file()

    def resolve(name: str) -> str | None:
        return os.environ.get(name) or file_values.get(name) or None

    return {
        "library_id": resolve("ZOTERO_LIBRARY_ID"),
        "library_type": resolve("ZOTERO_LIBRARY_TYPE") or "user",
        "api_key": resolve("ZOTERO_API_KEY"),
    }


# --------------------------------------------------------------------------- #
# Access-mode detection and client construction                               #
# --------------------------------------------------------------------------- #


def local_api_available() -> bool:
    """Probe the Zotero Desktop local API.

    Returns True only when the local API is enabled and serving requests, not
    merely when the Zotero connector port answers. The connector port responds
    even with the local API disabled, so we check an actual ``/api`` path.
    """
    import urllib.error
    import urllib.request

    url = f"{LOCAL_API_BASE}/users/{LOCAL_LIBRARY_ID}/items?limit=1"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:  # noqa: S310
            return 200 <= resp.status < 300
    except urllib.error.HTTPError:
        # Any HTTP response (e.g. 403 "Local API is not enabled") means the
        # local API path is not usable for our reads.
        return False
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def parse_library(spec: str | None) -> "tuple[str, str | None]":
    """Resolve a ``--library`` spec to ``(library_type, group_id)``.

    ``user`` (or None) -> ``("user", None)``; a bare numeric id or ``group:<id>``
    -> ``("group", "<id>")``. Raises RuntimeError on an unparseable spec.
    """
    if spec is None or spec == "user":
        return "user", None
    gid = spec.split(":", 1)[1] if spec.startswith("group:") else spec
    if not gid.isdigit():
        raise RuntimeError(
            f"invalid --library {spec!r}: use 'user', a numeric group id, "
            "or 'group:<id>' (list ids with the 'libraries' command)"
        )
    return "group", gid


def make_client(prefer: str = "auto", library: str | None = "user"):
    """Construct a pyzotero client, choosing local or web mode and target library.

    ``prefer`` is one of ``auto`` (local if available, else web), ``local``,
    or ``web``. ``library`` is ``user`` (default), a numeric group id, or
    ``group:<id>``. Raises RuntimeError with a credential-free message when the
    requested mode cannot be constructed.
    """
    from pyzotero.zotero import Zotero

    cfg = get_config()
    lib_type, group_id = parse_library(library)

    def build_local() -> "tuple[object, str]":
        # pyzotero 1.13.0 requires library_id + library_type even in local mode.
        # The local API serves the desktop's default user library at id 0 and
        # each group library at its group id.
        if lib_type == "group":
            zot = Zotero(library_id=group_id, library_type="group", local=True)
        else:
            zot = Zotero(library_id=LOCAL_LIBRARY_ID, library_type="user", local=True)
        return zot, "local"

    def build_web() -> "tuple[object, str]":
        if not cfg["api_key"]:
            raise RuntimeError(
                "Web API mode needs ZOTERO_LIBRARY_ID and ZOTERO_API_KEY "
                "(set in the environment or Notes/.env)"
            )
        if lib_type == "group":
            zot = Zotero(
                library_id=group_id, library_type="group", api_key=str(cfg["api_key"])
            )
            return zot, "web"
        if not cfg["library_id"]:
            raise RuntimeError(
                "Web API mode needs ZOTERO_LIBRARY_ID and ZOTERO_API_KEY "
                "(set in the environment or Notes/.env)"
            )
        zot = Zotero(
            library_id=str(cfg["library_id"]),
            library_type=str(cfg["library_type"]),
            api_key=str(cfg["api_key"]),
        )
        return zot, "web"

    if prefer == "local":
        return build_local()
    if prefer == "web":
        return build_web()

    # auto
    if local_api_available():
        return build_local()
    return build_web()


def pyzotero_version() -> str:
    from importlib.metadata import version

    return version("pyzotero")


# --------------------------------------------------------------------------- #
# Subcommand handlers                                                          #
# --------------------------------------------------------------------------- #


def cmd_health(args: argparse.Namespace) -> int:
    cfg = get_config()
    local_ok = local_api_available()
    web_configured = bool(cfg["library_id"] and cfg["api_key"])
    if local_ok:
        active = "local"
    elif web_configured:
        active = "web"
    else:
        active = None
    emit(
        {
            "pyzotero_version": pyzotero_version(),
            "local_api_available": local_ok,
            "web_api_configured": web_configured,
            "library_type": cfg["library_type"],
            "active_mode": active,
            # Booleans only — never the values themselves.
            "config_present": {
                "ZOTERO_LIBRARY_ID": bool(cfg["library_id"]),
                "ZOTERO_API_KEY": bool(cfg["api_key"]),
            },
        }
    )
    sys.stdout.flush()
    if active is None:
        eprint(
            "no usable access mode: enable the Zotero Desktop local API or "
            "configure Web API credentials (see references/access-modes.md)"
        )
        return 1
    return 0


def cmd_libraries(args: argparse.Namespace) -> int:
    """List accessible libraries: the user library plus all group libraries."""
    zot, mode = make_client(prefer=args.mode)
    cfg = get_config()
    user_id = (
        LOCAL_LIBRARY_ID
        if mode == "local"
        else (str(cfg["library_id"]) if cfg["library_id"] else None)
    )
    libraries = [{"library_id": user_id, "library_type": "user", "name": "My Library"}]
    try:
        groups = zot.everything(zot.groups())
    except Exception as exc:  # noqa: BLE001
        return fail(f"could not list group libraries: {exc}")
    for g in groups:
        libraries.append(
            {
                "library_id": str(g.get("id")),
                "library_type": "group",
                "name": g.get("data", {}).get("name"),
            }
        )
    emit({"mode": mode, "count": len(libraries), "libraries": libraries})
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    # Full-text search uses qmode="everything" (matches indexed content); plain
    # search uses qmode="titleCreatorYear". Both qmodes are served by the local
    # API and the Web API, so honor the requested access mode in either case.
    qmode = "everything" if args.fulltext else "titleCreatorYear"
    zot, mode = make_client(prefer=args.mode, library=args.library)
    results = zot.items(q=args.query, qmode=qmode, limit=args.limit)
    emit({"mode": mode, "count": len(results), "items": results})
    return 0


def cmd_item(args: argparse.Namespace) -> int:
    zot, mode = make_client(prefer=args.mode, library=args.library)
    emit({"mode": mode, "item": zot.item(args.item_key)})
    return 0


def cmd_children(args: argparse.Namespace) -> int:
    zot, mode = make_client(prefer=args.mode, library=args.library)
    children = zot.children(args.item_key)
    emit({"mode": mode, "count": len(children), "children": children})
    return 0


def cmd_collections(args: argparse.Namespace) -> int:
    zot, mode = make_client(prefer=args.mode, library=args.library)
    cols = zot.everything(zot.collections())
    emit({"mode": mode, "count": len(cols), "collections": cols})
    return 0


def cmd_tags(args: argparse.Namespace) -> int:
    zot, mode = make_client(prefer=args.mode, library=args.library)
    tags = zot.everything(zot.tags())
    emit({"mode": mode, "count": len(tags), "tags": tags})
    return 0


def cmd_fulltext(args: argparse.Namespace) -> int:
    """Retrieve the indexed full text of one attachment."""
    zot, mode = make_client(prefer=args.mode, library=args.library)
    try:
        result = zot.fulltext_item(args.attachment_key)
    except Exception as exc:  # noqa: BLE001
        return fail(f"could not retrieve full text for attachment: {exc}")
    emit({"mode": mode, "attachment_key": args.attachment_key, "fulltext": result})
    return 0


def cmd_doiindex(args: argparse.Namespace) -> int:
    """Build a DOI -> item-key index across the top-level library items."""
    zot, mode = make_client(prefer=args.mode, library=args.library)
    items = zot.everything(zot.top())
    index: dict[str, str] = {}
    for it in items:
        data = it.get("data", {})
        doi = data.get("DOI")
        if doi:
            index[doi] = data.get("key", it.get("key"))
    emit({"mode": mode, "count": len(index), "doi_index": index})
    return 0


def cmd_pdf(args: argparse.Namespace) -> int:
    """Resolve a PDF path: local Zotero storage first, then Web API download.

    Preserves the legacy local-storage-first behavior. Prints the resolved
    path on stdout (as JSON) and returns non-zero if no valid PDF is found.
    """
    key = args.attachment_key

    # 1. Local Zotero storage.
    storage = Path.home() / "Zotero" / "storage" / key
    if storage.is_dir():
        pdfs = sorted(storage.glob("*.pdf"))
        if pdfs:
            emit({"source": "local-storage", "path": str(pdfs[0])})
            return 0

    # 2. Web API download.
    try:
        zot, _ = make_client(prefer="web", library=args.library)
    except RuntimeError as exc:
        return fail(
            f"PDF not in local storage and Web API not configured for download — {exc}"
        )

    # Recover the original filename from item metadata; fall back to the key.
    try:
        meta = zot.item(key)
        filename = meta.get("data", {}).get("filename") or f"{key}.pdf"
    except Exception:  # noqa: BLE001
        filename = f"{key}.pdf"

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    try:
        content = zot.file(key)
    except Exception as exc:  # noqa: BLE001
        return fail(f"Web API download failed: {exc}")

    out_path.write_bytes(content)
    if not out_path.exists() or out_path.stat().st_size < PDF_MIN_BYTES:
        return fail(
            f"downloaded file is too small ({out_path.stat().st_size} bytes); "
            "the attachment may be a linked file or have no stored PDF"
        )
    emit({"source": "web-download", "path": str(out_path)})
    return 0


# --------------------------------------------------------------------------- #
# Argument parsing                                                            #
# --------------------------------------------------------------------------- #


def add_mode_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--mode",
        choices=["auto", "local", "web"],
        default="auto",
        help="access mode (default: auto — local if available, else web)",
    )


def add_library_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--library",
        default="user",
        metavar="LIB",
        help="target library: 'user' (default), a numeric group id, or "
        "'group:<id>' (list ids with the 'libraries' command)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zotero_tool.py",
        description="Local-first pyzotero command surface (JSON output).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("health", help="report version and detected access mode")
    p.set_defaults(func=cmd_health)

    p = sub.add_parser(
        "libraries", help="list the user library and all group libraries"
    )
    add_mode_arg(p)
    p.set_defaults(func=cmd_libraries)

    p = sub.add_parser("search", help="metadata or full-text library search")
    p.add_argument("query", help="search terms")
    p.add_argument(
        "--fulltext",
        action="store_true",
        help="full-text search of indexed content (local or web)",
    )
    p.add_argument("--limit", type=int, default=25, help="max results (default 25)")
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("item", help="get a single item by key")
    p.add_argument("item_key")
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_item)

    p = sub.add_parser("children", help="list child items / attachments of an item")
    p.add_argument("item_key")
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_children)

    p = sub.add_parser("collections", help="list all collections")
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_collections)

    p = sub.add_parser("tags", help="list all tags")
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_tags)

    p = sub.add_parser(
        "fulltext", help="retrieve indexed full text of one attachment"
    )
    p.add_argument("attachment_key")
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_fulltext)

    p = sub.add_parser("doiindex", help="build a DOI -> item-key index")
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_doiindex)

    p = sub.add_parser(
        "pdf", help="resolve PDF path (local storage first, then web download)"
    )
    p.add_argument("attachment_key")
    p.add_argument(
        "--out-dir", default="/tmp", help="download directory (default /tmp)"
    )
    add_library_arg(p)
    p.set_defaults(func=cmd_pdf)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as exc:
        return fail(str(exc))
    except Exception as exc:  # noqa: BLE001
        # Defensive: pyzotero / network errors. Message is tool-constructed and
        # the exception text from pyzotero does not contain credential values.
        return fail(f"{type(exc).__name__}: {exc}")


if __name__ == "__main__":
    sys.exit(main())
