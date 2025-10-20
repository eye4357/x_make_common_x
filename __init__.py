"""Public interface for shared x_make_common_x utilities."""

from __future__ import annotations

from .exporters import (  # re-export shared exporters
    CommandRunner,
    ExportResult,
    export_graphviz_to_svg,
    export_markdown_to_pdf,
    export_mermaid_to_svg,
)
from .json_board import (
    BoardState as JsonBoardState,
)
from .json_board import (
    CardRecord as JsonCardRecord,
)
from .json_board import (
    board_from_records,
    dump_board,
)
from .json_board import (
    load_board as load_json_board,
)
from .json_board import (
    save_board as save_json_board,
)
from .json_contracts import validate_payload, validate_schema
from .run_reports import (
    REPORTS_DIR_NAME,
    TIMESTAMP_FILENAME_FORMAT,
    ensure_reports_dir,
    isoformat_timestamp,
    write_run_report,
)
from .telemetry import JSONValue, TelemetryEvent, emit_event, make_event
from .x_env_x import ensure_workspace_on_syspath, get_env_bool, get_env_str
from .x_http_client_x import HttpClient, HttpError, HttpResponse
from .x_logging_utils_x import get_logger, log_debug, log_error, log_info
from .x_subprocess_utils_x import CommandError, run_command

__all__ = [
    "REPORTS_DIR_NAME",
    "TIMESTAMP_FILENAME_FORMAT",
    "CommandError",
    "CommandRunner",
    "ExportResult",
    "HttpClient",
    "HttpError",
    "HttpResponse",
    "JSONValue",
    "JsonBoardState",
    "JsonCardRecord",
    "TelemetryEvent",
    "board_from_records",
    "dump_board",
    "emit_event",
    "ensure_reports_dir",
    "ensure_workspace_on_syspath",
    "export_graphviz_to_svg",
    "export_markdown_to_pdf",
    "export_mermaid_to_svg",
    "get_env_bool",
    "get_env_str",
    "get_logger",
    "isoformat_timestamp",
    "load_json_board",
    "log_debug",
    "log_error",
    "log_info",
    "make_event",
    "run_command",
    "save_json_board",
    "validate_payload",
    "validate_schema",
    "write_run_report",
]
