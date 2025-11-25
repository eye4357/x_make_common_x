from datetime import datetime
from pathlib import Path
from collections.abc import Mapping, MutableMapping

REPORTS_DIR_NAME: str
TIMESTAMP_FILENAME_FORMAT: str

def ensure_reports_dir(
    base_dir: Path | str | None = ...,
    *,
    reports_name: str = ...,
) -> Path: ...
def isoformat_timestamp(moment: datetime | None = ...) -> str: ...
def write_run_report(
    tool_slug: str,
    payload: Mapping[str, object] | MutableMapping[str, object],
    *,
    base_dir: Path | str | None = ...,
    filename: str | None = ...,
    timestamp: datetime | None = ...,
    reports_name: str = ...,
) -> Path: ...
