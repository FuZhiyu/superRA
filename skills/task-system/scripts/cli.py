#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Console entry point for the task-system command surface.

Run via `uv run --script cli.py …` (or `python3 cli.py …`). The core is
stdlib-only; pyyaml is declared for the lazy comment-sidecar parsing in
`_comments.py`. The `dashboard` subcommand is NOT routed here at the wrapper
level — the wrapper sends `dashboard` straight to `plan_dashboard.py` so the
web stack never lands on this task hot path. The in-process `dashboard` handler
below stays the single home for the user-facing-surface translation;
`plan_dashboard.py` delegates back to it when the wrapper routes `dashboard`
there, so the translation has one home.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path
from typing import Callable

if __package__:
    from ._task_io import TASK_ROOT_DIRNAME, resolve_path, resolve_plan_root_arg
    from .dashboard_artifact_workflow import (
        DEFAULT_ARTIFACT_PREFIX,
        DEFAULT_OUTPUT_PATH,
        DEFAULT_RETENTION_DAYS,
        DEFAULT_TASK_ROOT,
        DEFAULT_WORKFLOW_PATH,
        WorkflowConfig,
        install_workflow,
    )
else:  # pragma: no cover - exercised by direct script users, not package imports
    sys.path.insert(0, str(Path(__file__).parent))
    from _task_io import TASK_ROOT_DIRNAME, resolve_path, resolve_plan_root_arg
    from dashboard_artifact_workflow import (
        DEFAULT_ARTIFACT_PREFIX,
        DEFAULT_OUTPUT_PATH,
        DEFAULT_RETENTION_DAYS,
        DEFAULT_TASK_ROOT,
        DEFAULT_WORKFLOW_PATH,
        WorkflowConfig,
        install_workflow,
    )


def _module_main(module_name: str, argv: list[str] | None = None, *, pass_argv: bool = True) -> None:
    if __package__:
        module = importlib.import_module(f"{__package__}.{module_name}")
    else:
        module = importlib.import_module(module_name)
    if pass_argv:
        module.main(argv)
    else:
        module.main()


def _root_args(root: str | None) -> list[str]:
    if root is None:
        return []
    return ["--plan-root", root]


def _resolved_root_value(root: str | None) -> str:
    if root is not None:
        return root
    detected = resolve_plan_root_arg(None)
    if detected is not None:
        return str(detected)
    return TASK_ROOT_DIRNAME


def _checked_task_root_args(root: str | None, *task_paths: str) -> list[str]:
    root_value = _resolved_root_value(root)
    plan_root = Path(root_value)
    for task_path in task_paths:
        try:
            resolve_path(plan_root, task_path)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
    return ["--plan-root", root_value]


def _check_sibling_slug(sibling_slug: str) -> None:
    if (
        not sibling_slug
        or sibling_slug in {".", ".."}
        or "/" in sibling_slug
        or "\\" in sibling_slug
        or Path(sibling_slug).is_absolute()
    ):
        print(f"Error: dependency must be a sibling slug: {sibling_slug!r}", file=sys.stderr)
        sys.exit(1)


def _append_optional(argv: list[str], flag: str, value: str | None) -> None:
    if value:
        argv.extend([flag, value])


def _append_many(argv: list[str], flag: str, values: list[str] | None) -> None:
    if values:
        argv.append(flag)
        argv.extend(values)


def _append_repeated(argv: list[str], flag: str, values: list[str] | None) -> None:
    for value in values or []:
        argv.extend([flag, value])


def _run_dashboard(args: argparse.Namespace) -> None:
    root = _resolved_root_value(args.root)
    if args.dashboard_command == "export":
        argv = ["generate", "--plan-root", root]
        _append_optional(argv, "--output", args.output)
        _append_optional(argv, "--root", args.subtree)
        _append_optional(argv, "--repo-file-base", args.repo_file_base)
    elif args.dashboard_command == "artifact":
        _run_dashboard_artifact(args)
        return
    elif args.dashboard_command == "stop":
        argv = ["stop", "--root", root]
    else:
        argv = ["serve", "--root", root]
        if args.port is not None:
            argv.extend(["--port", str(args.port)])
        if args.no_open:
            argv.append("--no-open")
        if args.foreground:
            argv.append("--foreground")
    _module_main("plan_dashboard", argv)


def _run_dashboard_artifact(args: argparse.Namespace) -> None:
    config = WorkflowConfig(
        task_root=args.task_root,
        output_path=args.output,
        artifact_prefix=args.artifact_prefix,
        retention_days=args.retention_days,
        fail_on_missing_task_root=not args.skip_missing_task_root,
        branch_patterns=tuple(args.branch or ["**"]),
    )
    try:
        result = install_workflow(
            Path(args.repo_root),
            workflow_path=args.workflow_path,
            config=config,
            force=args.force,
            preview_ref=args.preview_ref,
        )
    except (FileExistsError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    action = "Created" if result.created else "Updated"
    print(f"{action} {result.path}")
    print(f"Artifact name pattern: {args.artifact_prefix}-<branch-slug>-<ref-hash>")
    print(f"Preview for {args.preview_ref!r}: {result.artifact_name_preview}")


def _run_read(args: argparse.Namespace) -> None:
    argv = _root_args(args.root) + ["--path", args.path]
    if args.no_ancestors:
        argv.append("--no-ancestors")
    if args.as_json:
        argv.append("--json")
    _module_main("task_read", argv)


def _run_tree(args: argparse.Namespace) -> None:
    argv = _root_args(args.root) + ["--tree"]
    _append_optional(argv, "--status", args.status)
    _append_optional(argv, "--tag", args.tag)
    if args.as_json:
        argv.append("--json")
    _module_main("task_query", argv)


def _run_frontier(args: argparse.Namespace) -> None:
    argv = _root_args(args.root) + ["--frontier"]
    if args.as_json:
        argv.append("--json")
    _module_main("task_query", argv)


def _run_dag(args: argparse.Namespace) -> None:
    argv = _root_args(args.root) + ["--dag"]
    if args.subtree:
        argv.append(args.subtree)
    _module_main("task_query", argv)


def _run_check(args: argparse.Namespace) -> None:
    argv = _root_args(args.root)
    if args.as_json:
        argv.append("--json")
    _append_optional(argv, "--category", args.category)
    _module_main("task_check", argv)


def _run_create(args: argparse.Namespace) -> None:
    argv = ["--plan-root", _resolved_root_value(args.root), "--path", args.path, "--title", args.title]
    _append_optional(argv, "--objective", args.objective)
    _append_optional(argv, "--guidance", args.guidance)
    _append_many(argv, "--depends-on", args.depends_on)
    _append_optional(argv, "--script", args.script)
    _append_many(argv, "--input", args.input)
    _append_many(argv, "--output", args.output)
    _module_main("task_create", argv)


def _run_update(args: argparse.Namespace) -> None:
    argv = _checked_task_root_args(args.root, args.path) + ["--path", args.path]
    _append_optional(argv, "--status", args.status)
    _append_optional(argv, "--title", args.title)
    _append_repeated(argv, "--add-tag", args.add_tag)
    _append_repeated(argv, "--remove-tag", args.remove_tag)
    _append_optional(argv, "--script", args.script)
    _module_main("task_update", argv)


def _run_status_cascade(args: argparse.Namespace) -> None:
    argv = _checked_task_root_args(args.root, args.path) + [
        "--path", args.path, "--status", args.status, "--cascade",
    ]
    _module_main("task_update", argv)


def _run_status_propagate(args: argparse.Namespace) -> None:
    argv = _root_args(args.root) + ["--propagate-all"]
    _module_main("task_update", argv)


def _run_status_fix(args: argparse.Namespace) -> None:
    argv = _root_args(args.root) + ["--fix"]
    _module_main("task_update", argv)


def _run_result_add(args: argparse.Namespace) -> None:
    argv = _checked_task_root_args(args.root, args.path) + ["--path", args.path]
    _append_optional(argv, "--finding", args.finding)
    _append_optional(argv, "--figure", args.figure)
    _append_optional(argv, "--figure-caption", args.figure_caption)
    _append_optional(argv, "--note", args.note)
    _module_main("task_add_result", argv)


def _run_dep(args: argparse.Namespace) -> None:
    _check_sibling_slug(args.sibling_slug)
    argv = _checked_task_root_args(args.root, args.path) + ["--path", args.path, "--depends-on", args.sibling_slug]
    if args.dep_command == "remove":
        argv.append("--remove")
    _module_main("task_link", argv)


def _run_rename(args: argparse.Namespace) -> None:
    argv = _checked_task_root_args(args.root, args.from_path, args.to_path) + [
        "--from", args.from_path, "--to", args.to_path,
    ]
    _module_main("task_rename", argv)


def _run_comment(args: argparse.Namespace) -> None:
    command = "list-tree" if args.comment_command == "tree" else args.comment_command
    argv = ["--plan-root", _resolved_root_value(args.root), command]
    if args.comment_command in {"list", "resolve"}:
        argv.append(args.path)
    if args.comment_command == "resolve":
        argv.append(str(args.comment_id))
    if getattr(args, "show_all", False):
        argv.append("--all")
    if getattr(args, "as_json", False):
        argv.append("--json")
    _module_main("task_comment", argv)


def _run_migrate(args: argparse.Namespace) -> None:
    if args.migrate_command == "from-plan":
        argv = ["--plan-md", args.plan_md]
        _append_optional(argv, "--results-md", args.results_md)
        _append_optional(argv, "--output", args.output)
    elif args.migrate_command == "upgrade-status":
        argv = ["--upgrade-status", "--plan-root", _resolved_root_value(args.root)]
        if args.dry_run:
            argv.append("--dry-run")
    else:
        argv = ["--upgrade", "--plan-root", _resolved_root_value(args.root)]
    _module_main("plan_migrate", argv)


def _run_hook(args: argparse.Namespace) -> None:
    _module_main("task_hook", pass_argv=False)


def _run_wrapper(args: argparse.Namespace) -> None:
    if args.wrapper_command == "init":
        _module_main("wrapper_resolver", ["init"] + _root_args_wrapper(args.root))
    elif args.wrapper_command == "render-hook":
        argv = ["render-hook"]
        _append_optional(argv, "--output", args.output)
        _module_main("wrapper_resolver", argv)


def _root_args_wrapper(root: str | None) -> list[str]:
    return ["--root", root] if root is not None else []


def _set_runner(parser: argparse.ArgumentParser, runner: Callable[[argparse.Namespace], None]) -> None:
    parser.set_defaults(runner=runner)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="superra", description="superRA task-system CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    dashboard = sub.add_parser("dashboard", help="Start or export the task dashboard")
    dashboard.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    dashboard.add_argument("--port", type=int, default=None, help="Server port")
    dashboard.add_argument("--no-open", action="store_true", help="Skip auto-opening the browser")
    dashboard.add_argument(
        "--foreground",
        action="store_true",
        help="Run blocking in this terminal with logs on stdout (default: background)",
    )
    dash_sub = dashboard.add_subparsers(dest="dashboard_command")
    export = dash_sub.add_parser("export", help="Export a static dashboard HTML file")
    export.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    export.add_argument("--output", default="", help="Output HTML path")
    export.add_argument("--subtree", default="", help="Task path to scope the export")
    export.add_argument(
        "--repo-file-base",
        default="",
        help="Repository browser base for file links, e.g. https://github.com/owner/repo/blob/sha",
    )
    artifact = dash_sub.add_parser("artifact", help="Set up dashboard artifact publishing")
    artifact_sub = artifact.add_subparsers(dest="artifact_command", required=True)
    artifact_setup = artifact_sub.add_parser(
        "setup",
        help="Install the managed GitHub Actions workflow for dashboard artifacts",
    )
    artifact_setup.add_argument("--repo-root", default=".", help="Repository root to write into")
    artifact_setup.add_argument(
        "--workflow-path",
        default=DEFAULT_WORKFLOW_PATH,
        help="Workflow path relative to the repository root",
    )
    artifact_setup.add_argument(
        "--task-root",
        default=DEFAULT_TASK_ROOT,
        help=f"Task root path the workflow exports (default: {DEFAULT_TASK_ROOT})",
    )
    artifact_setup.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_PATH,
        help=f"Dashboard HTML output path inside the workflow (default: {DEFAULT_OUTPUT_PATH})",
    )
    artifact_setup.add_argument(
        "--artifact-prefix",
        default=DEFAULT_ARTIFACT_PREFIX,
        help=f"Artifact name prefix (default: {DEFAULT_ARTIFACT_PREFIX})",
    )
    artifact_setup.add_argument(
        "--retention-days",
        type=int,
        default=DEFAULT_RETENTION_DAYS,
        help=f"Artifact retention in days (default: {DEFAULT_RETENTION_DAYS})",
    )
    artifact_setup.add_argument(
        "--branch",
        action="append",
        default=[],
        help='Push branch pattern to include in the workflow trigger; repeatable (default: "**")',
    )
    artifact_setup.add_argument(
        "--skip-missing-task-root",
        action="store_true",
        help="Make the workflow exit successfully when the task root is absent",
    )
    artifact_setup.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing non-superRA-managed workflow file",
    )
    artifact_setup.add_argument(
        "--preview-ref",
        default="current-branch",
        help="Reference name used only for printing an artifact-name preview",
    )
    stop = dash_sub.add_parser("stop", help="Stop the background dashboard server for this repo")
    stop.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    _set_runner(dashboard, _run_dashboard)

    task = sub.add_parser("task", help="Read, query, and mutate task trees")
    task_sub = task.add_subparsers(dest="task_command", required=True)

    read = task_sub.add_parser("read", help="Read one task with inherited context")
    read.add_argument("path", help="Task path relative to the task root")
    read.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    read.add_argument("--no-ancestors", action="store_true", help="Skip ancestor context")
    read.add_argument("--json", action="store_true", dest="as_json", help="Output JSON")
    _set_runner(read, _run_read)

    tree = task_sub.add_parser("tree", help="Print the task tree")
    tree.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    tree.add_argument("--status", help="Filter by effective status")
    tree.add_argument("--tag", help="Filter by tag")
    tree.add_argument("--json", action="store_true", dest="as_json", help="Output JSON")
    _set_runner(tree, _run_tree)

    frontier = task_sub.add_parser("frontier", help="List dispatchable leaf tasks")
    frontier.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    frontier.add_argument("--json", action="store_true", dest="as_json", help="Output JSON")
    _set_runner(frontier, _run_frontier)

    dag = task_sub.add_parser("dag", help="Render a Mermaid dependency DAG")
    dag.add_argument("subtree", nargs="?", default="", help="Optional subtree path")
    dag.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    _set_runner(dag, _run_dag)

    check = task_sub.add_parser("check", help="Run read-only task tree diagnostics")
    check.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    check.add_argument("--json", action="store_true", dest="as_json", help="Output JSON")
    check.add_argument("--category", choices=["status", "dependency", "rollup", "placement"], help="Check one category")
    _set_runner(check, _run_check)

    create = task_sub.add_parser("create", help="Create a task directory")
    create.add_argument("path", help="Task path relative to the task root")
    create.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    create.add_argument("--title", required=True, help="Task title")
    create.add_argument("--objective", default="", help="Task objective")
    create.add_argument("--guidance", default="", help="Optional Planner Guidance text")
    create.add_argument("--depends-on", nargs="*", default=[], help="Sibling dependencies")
    create.add_argument("--script", default="", help="Script path")
    create.add_argument("--input", nargs="*", default=[], help="Input paths")
    create.add_argument("--output", nargs="*", default=[], help="Output paths")
    _set_runner(create, _run_create)

    update = task_sub.add_parser("update", help="Update task frontmatter fields")
    update.add_argument("path", help="Task path relative to the task root")
    update.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    update.add_argument("--status", help="Set task status")
    update.add_argument("--title", help="Set task title")
    update.add_argument("--add-tag", action="append", default=[], help="Add a tag")
    update.add_argument("--remove-tag", action="append", default=[], help="Remove a tag")
    update.add_argument("--script", help="Set script path")
    _set_runner(update, _run_update)

    status = task_sub.add_parser("status", help="Cascade or propagate task statuses")
    status_sub = status.add_subparsers(dest="status_command", required=True)
    cascade = status_sub.add_parser("cascade", help="Cascade an allowed status through a branch")
    cascade.add_argument("path", help="Branch task path")
    cascade.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    cascade.add_argument("--status", required=True, help="Status to cascade")
    _set_runner(cascade, _run_status_cascade)
    propagate = status_sub.add_parser("propagate", help="Propagate parent statuses from children")
    propagate.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    _set_runner(propagate, _run_status_propagate)
    fix = status_sub.add_parser("fix", help="Fix branch status fields to match child rollups")
    fix.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    _set_runner(fix, _run_status_fix)

    result = task_sub.add_parser("result", help="Update task results")
    result_sub = result.add_subparsers(dest="result_command", required=True)
    result_add = result_sub.add_parser("add", help="Append a finding, figure, or note")
    result_add.add_argument("path", help="Task path")
    result_add.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    result_add.add_argument("--finding", help="Key finding to append")
    result_add.add_argument("--figure", help="Figure path")
    result_add.add_argument("--figure-caption", default="", help="Figure caption")
    result_add.add_argument("--note", help="Note to append")
    _set_runner(result_add, _run_result_add)

    dep = task_sub.add_parser("dep", help="Manage sibling dependencies")
    dep_sub = dep.add_subparsers(dest="dep_command", required=True)
    dep_add = dep_sub.add_parser("add", help="Add a sibling dependency")
    dep_add.add_argument("path", help="Task path")
    dep_add.add_argument("sibling_slug", help="Sibling dependency slug")
    dep_add.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    _set_runner(dep_add, _run_dep)
    dep_remove = dep_sub.add_parser("remove", help="Remove a sibling dependency")
    dep_remove.add_argument("path", help="Task path")
    dep_remove.add_argument("sibling_slug", help="Sibling dependency slug")
    dep_remove.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    _set_runner(dep_remove, _run_dep)

    rename = task_sub.add_parser("rename", help="Rename a task within its parent")
    rename.add_argument("from_path", help="Current task path")
    rename.add_argument("to_path", help="New task path")
    rename.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    _set_runner(rename, _run_rename)

    comment = task_sub.add_parser("comment", help="Read and resolve task comments")
    comment_sub = comment.add_subparsers(dest="comment_command", required=True)
    comment_list = comment_sub.add_parser("list", help="List comments for a task")
    comment_list.add_argument("path", help="Task path")
    comment_list.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    comment_list.add_argument("--all", action="store_true", dest="show_all", help="Show resolved comments")
    comment_list.add_argument("--json", action="store_true", dest="as_json", help="Output JSON")
    _set_runner(comment_list, _run_comment)
    comment_resolve = comment_sub.add_parser("resolve", help="Toggle resolved status")
    comment_resolve.add_argument("path", help="Task path")
    comment_resolve.add_argument("comment_id", type=int, help="Comment ID")
    comment_resolve.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    _set_runner(comment_resolve, _run_comment)
    comment_tree = comment_sub.add_parser("tree", help="Show unresolved comment counts")
    comment_tree.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    comment_tree.add_argument("--json", action="store_true", dest="as_json", help="Output JSON")
    _set_runner(comment_tree, _run_comment)

    migrate = task_sub.add_parser("migrate", help="Migrate or upgrade task trees")
    migrate_sub = migrate.add_subparsers(dest="migrate_command", required=True)
    from_plan = migrate_sub.add_parser("from-plan", help="Migrate PLAN.md / RESULTS.md to a task tree")
    from_plan.add_argument("--plan-md", required=True, help="Path to PLAN.md")
    from_plan.add_argument("--results-md", default="", help="Optional RESULTS.md path")
    from_plan.add_argument("--output", default="", help="Output task root")
    _set_runner(from_plan, _run_migrate)
    upgrade = migrate_sub.add_parser("upgrade", help="Upgrade an existing task tree")
    upgrade.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    _set_runner(upgrade, _run_migrate)
    upgrade_status = migrate_sub.add_parser("upgrade-status", help="Upgrade legacy status fields")
    upgrade_status.add_argument(
        "--root",
        default=None,
        help=f"Path to the task root directory (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    upgrade_status.add_argument("--dry-run", action="store_true", help="Show status upgrades without writing")
    _set_runner(upgrade_status, _run_migrate)

    hook = task_sub.add_parser("hook", help="Run task-system hooks")
    hook_sub = hook.add_subparsers(dest="hook_command", required=True)
    post_tool_use = hook_sub.add_parser("post-tool-use", help="Run the PostToolUse hook")
    _set_runner(post_tool_use, _run_hook)

    wrapper = sub.add_parser("wrapper", help="Generate the resolver-carrying task-tree CLI wrapper")
    wrapper_sub = wrapper.add_subparsers(dest="wrapper_command", required=True)
    wrapper_init = wrapper_sub.add_parser(
        "init", help="Write an executable resolver wrapper into the task root"
    )
    wrapper_init.add_argument(
        "--root",
        default=None,
        help=f"Task root to write the wrapper into (default: auto-detect, preferring {TASK_ROOT_DIRNAME})",
    )
    _set_runner(wrapper_init, _run_wrapper)
    wrapper_render_hook = wrapper_sub.add_parser(
        "render-hook", help="Print or write the generated hooks/task-hook shim"
    )
    wrapper_render_hook.add_argument(
        "--output", default="", help="Write the shim to PATH (and chmod +x) instead of stdout"
    )
    _set_runner(wrapper_render_hook, _run_wrapper)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    runner = getattr(args, "runner", None)
    if runner is None:
        parser.print_help()
        sys.exit(2)
    runner(args)


if __name__ == "__main__":
    main()
