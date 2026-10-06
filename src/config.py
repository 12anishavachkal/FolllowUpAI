"""Loads settings from config/settings.yaml so paths and limits live outside the logic."""

from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PATH = PROJECT_ROOT / "config" / "settings.yaml"


def load_settings() -> dict:
    """Read and return the YAML settings file as a dictionary."""
    with open(SETTINGS_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_path(relative_path: str) -> Path:
    """Turn a project-relative path from the settings into an absolute path."""
    return PROJECT_ROOT / relative_path