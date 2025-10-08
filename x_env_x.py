"""Environment helpers shared across orchestrator utilities."""

from __future__ import annotations

import os
import sys
from pathlib import Path

_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


def ensure_workspace_on_syspath() -> None:
    """Ensure the workspace root is present on ``sys.path``."""

    root_str = str(_WORKSPACE_ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def get_env_str(name: str, *, default: str | None = None) -> str | None:
    """Return the trimmed value of an environment variable."""

    value = os.environ.get(name)
    if value is None:
        return default
    stripped = value.strip()
    return stripped or default


def get_env_bool(name: str, *, default: bool = False) -> bool:
    """Interpret an environment variable as a truthy flag."""

    value = os.environ.get(name)
    if value is None:
        return default
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on"}:
        return True
    if lowered in {"0", "false", "no", "off"}:
        return False
    return default


__all__ = [
    "ensure_workspace_on_syspath",
    "get_env_bool",
    "get_env_str",
]
