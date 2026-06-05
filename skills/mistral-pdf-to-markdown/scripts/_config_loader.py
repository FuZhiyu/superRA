"""
Unified configuration loader for agent-contract plugins.

Lookup order:
1. .claude/agent-contract.yaml (project-specific)
2. ~/.config/agent-contract/config.yaml (global fallback)
"""

import os
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None


CONFIG_FILENAME = "agent-contract.yaml"
PROJECT_CONFIG_PATH = Path(".claude") / CONFIG_FILENAME
GLOBAL_CONFIG_PATH = Path.home() / ".config" / "agent-contract" / "config.yaml"


def get_config_path() -> Path | None:
    """
    Find the config file path using fallback logic.

    Returns:
        Path to config file, or None if not found.
    """
    # Check project-specific first
    if PROJECT_CONFIG_PATH.exists():
        return PROJECT_CONFIG_PATH

    # Fall back to global
    if GLOBAL_CONFIG_PATH.exists():
        return GLOBAL_CONFIG_PATH

    return None


def load_config(plugin_name: str | None = None) -> dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        plugin_name: If provided, return only that plugin's config section.
                    If None, return the entire config.

    Returns:
        Configuration dictionary.

    Raises:
        FileNotFoundError: If no config file exists.
        ImportError: If PyYAML is not installed.
    """
    if yaml is None:
        raise ImportError(
            "PyYAML is required for config loading. "
            "Install with: pip install pyyaml"
        )

    config_path = get_config_path()

    if config_path is None:
        raise FileNotFoundError(
            f"No config file found. Create one at:\n"
            f"  - {PROJECT_CONFIG_PATH} (project-specific)\n"
            f"  - {GLOBAL_CONFIG_PATH} (global)"
        )

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f) or {}

    if plugin_name is None:
        return config

    return config.get(plugin_name, {})


def get_api_key(plugin_name: str, key_name: str) -> str | None:
    """
    Get a specific API key from plugin config.

    Args:
        plugin_name: Plugin section name (e.g., 'paper-reader')
        key_name: Key name within plugin config (e.g., 'mistral_api_key')

    Returns:
        API key value, or None if not found.
    """
    try:
        config = load_config(plugin_name)
        return config.get(key_name)
    except (FileNotFoundError, ImportError):
        return None


# Convenience functions for common keys
def get_mistral_api_key() -> str | None:
    """Get Mistral API key from paper-reader config."""
    return get_api_key('paper-reader', 'mistral_api_key')


def get_zotero_config() -> dict[str, Any]:
    """Get Zotero configuration from paper-reader config."""
    config = load_config('paper-reader')
    return {
        'api_key': config.get('zotero_api_key'),
        'library_type': config.get('zotero_library_type', 'user'),
        'library_id': config.get('zotero_library_id'),
    }
