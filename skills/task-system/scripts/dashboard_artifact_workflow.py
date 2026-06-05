"""Render the GitHub Actions workflow for dashboard artifact publishing."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


MANAGED_MARKER = "# Managed by superRA task-system dashboard artifact setup."
DEFAULT_WORKFLOW_NAME = "superRA Dashboard Artifact"
DEFAULT_TASK_ROOT = "superRA"
DEFAULT_OUTPUT_PATH = ".superra-dashboard/dashboard.html"
DEFAULT_ARTIFACT_PREFIX = "superra-dashboard"
DEFAULT_RETENTION_DAYS = 14

_TOKEN_REPLACEMENTS = {
    "__MANAGED_MARKER__": MANAGED_MARKER,
}


@dataclass(frozen=True)
class WorkflowConfig:
    """Configuration values substituted into the workflow template."""

    workflow_name: str = DEFAULT_WORKFLOW_NAME
    task_root: str = DEFAULT_TASK_ROOT
    output_path: str = DEFAULT_OUTPUT_PATH
    artifact_prefix: str = DEFAULT_ARTIFACT_PREFIX
    retention_days: int = DEFAULT_RETENTION_DAYS
    fail_on_missing_task_root: bool = True


def sanitize_artifact_slug(ref_name: str) -> str:
    """Return the branch slug used by the workflow's runtime shell step.

    The shell template lowercases the ref and replaces runs of characters outside
    ``[a-z0-9._-]`` with ``-``.  Keeping this helper in sync gives the setup
    command and tests a deterministic local preview of the artifact name.
    """
    slug = ref_name.lower()
    slug = re.sub(r"[^a-z0-9._-]+", "-", slug)
    slug = slug.strip("-")
    return slug or "ref"


def artifact_name_for_ref(ref_name: str, prefix: str = DEFAULT_ARTIFACT_PREFIX) -> str:
    """Return the dashboard artifact name for *ref_name*."""
    return f"{prefix}-{sanitize_artifact_slug(ref_name)}"


def _template_path() -> Path:
    return Path(__file__).parent / "templates" / "superra-dashboard-artifact.yml"


def render_workflow(config: WorkflowConfig | None = None) -> str:
    """Render the managed GitHub Actions workflow."""
    config = config or WorkflowConfig()
    template = _template_path().read_text(encoding="utf-8")
    replacements = dict(_TOKEN_REPLACEMENTS)
    replacements.update(
        {
            "__WORKFLOW_NAME__": config.workflow_name,
            "__TASK_ROOT__": config.task_root,
            "__OUTPUT_PATH__": config.output_path,
            "__ARTIFACT_PREFIX__": config.artifact_prefix,
            "__RETENTION_DAYS__": str(config.retention_days),
            "__MISSING_ROOT_GUARD__": _missing_root_guard(config),
        }
    )
    for token, value in replacements.items():
        template = template.replace(token, value)
    return template


def _missing_root_guard(config: WorkflowConfig) -> str:
    if config.fail_on_missing_task_root:
        return (
            f'if [ ! -f "{config.task_root}/task.md" ]; then\n'
            f'  echo "No {config.task_root}/task.md found in this ref." >&2\n'
            "  exit 1\n"
            "fi"
        )
    return (
        f'if [ ! -f "{config.task_root}/task.md" ]; then\n'
        f'  echo "No {config.task_root}/task.md found in this ref; skipping dashboard artifact."\n'
        "  exit 0\n"
        "fi"
    )
