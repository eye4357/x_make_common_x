from __future__ import annotations

import json
from collections.abc import Mapping, MutableMapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

__all__ = [
    "REPORTS_DIR_NAME",
    "TIMESTAMP_FILENAME_FORMAT",
    "ensure_reports_dir",
    "isoformat_timestamp",
    "write_run_report",
]

REPORTS_DIR_NAME = "reports"
TIMESTAMP_FILENAME_FORMAT = "%Y%m%d_%H%M%S"


def _to_path(base_dir: Path | str | None) -> Path:
    if base_dir is None:
        return Path.cwd()
    if isinstance(base_dir, Path):
        return base_dir
    return Path(base_dir)


def ensure_reports_dir(
    base_dir: Path | str | None = None,
    *,
    reports_name: str = REPORTS_DIR_NAME,
) -> Path:
    base_path = _to_path(base_dir)
    reports_dir = base_path / reports_name
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def isoformat_timestamp(moment: datetime | None = None) -> str:
    current = (moment or datetime.now(UTC)).replace(microsecond=0)
    return current.isoformat().replace("+00:00", "Z")


def _ensure_mapping(payload: Mapping[str, Any] | MutableMapping[str, Any]) -> dict[str, Any]:
    if isinstance(payload, dict):
        return dict(payload)
    return {str(key): value for key, value in payload.items()}


def write_run_report(
    tool_slug: str,
    payload: Mapping[str, Any] | MutableMapping[str, Any],
    *,
    base_dir: Path | str | None = None,
    filename: str | None = None,
    timestamp: datetime | None = None,
    reports_name: str = REPORTS_DIR_NAME,
) -> Path:
    moment = timestamp or datetime.now(UTC)
    reports_dir = ensure_reports_dir(base_dir, reports_name=reports_name)
    stamp = moment.strftime(TIMESTAMP_FILENAME_FORMAT)
    resolved_filename = filename or f"{tool_slug}_run_{stamp}.json"
    report_path = reports_dir / resolved_filename

    data = _ensure_mapping(payload)
    data.setdefault("tool", tool_slug)
    data.setdefault("generated_at", isoformat_timestamp(moment))

    report_path.write_text(
        json.dumps(data, indent=2, sort_keys=False),
        encoding="utf-8",
    )
    return report_path
