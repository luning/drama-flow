"""YAML config loader — pure utility, no target knowledge."""

from pathlib import Path
from typing import Any

import yaml


def load_config(path: str) -> dict[str, Any]:
    """Load a YAML config file. Returns empty dict if not found."""
    config_path = Path(path)
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return yaml.safe_load(f) or {}
