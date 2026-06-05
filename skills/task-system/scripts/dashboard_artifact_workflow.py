"""Render the GitHub Actions workflow for dashboard artifact publishing."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


MANAGED_MARKER = "# Managed by superRA task-system dashboard artifact setup."
DEFAULT_WORKFLOW_NAME = "superRA Dashboard Artifact"
DEFAULT_TASK_ROOT = "superRA"
DEFAULT_OUTPUT_PATH = ".superra-dashboard/dashboard.html"
DEFAULT_ARTIFACT_PREFIX = "superra-dashboard"
DEFAULT_RETENTION_DAYS = 14
DEFAULT_WORKFLOW_PATH = ".github/workflows/superra-dashboard-artifact.yml"

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


@dataclass(frozen=True)
class InstallResult:
    """Result of installing the managed workflow."""

    path: Path
    artifact_name_preview: str
    created: bool


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
    ref_hash = hashlib.sha256(ref_name.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{sanitize_artifact_slug(ref_name)}-{ref_hash}"


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


def install_workflow(
    repo_root: Path,
    workflow_path: str = DEFAULT_WORKFLOW_PATH,
    config: WorkflowConfig | None = None,
    *,
    force: bool = False,
    preview_ref: str = "current-branch",
) -> InstallResult:
    """Install the managed dashboard artifact workflow into *repo_root*."""
    config = config or WorkflowConfig()
    target = (repo_root / workflow_path).resolve()
    root = repo_root.resolve()
    if not target.is_relative_to(root):
        raise ValueError(f"Workflow path escapes repository root: {workflow_path}")

    workflow = render_workflow(config)
    created = not target.exists()
    if target.exists():
        existing = target.read_text(encoding="utf-8")
        if MANAGED_MARKER not in existing and not force:
            raise FileExistsError(
                f"{target} exists and is not managed by superRA; pass --force to overwrite"
            )

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(workflow, encoding="utf-8")
    return InstallResult(
        path=target,
        artifact_name_preview=artifact_name_for_ref(preview_ref, config.artifact_prefix),
        created=created,
    )


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
