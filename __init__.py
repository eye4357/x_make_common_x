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
from .run_reports import (
    REPORTS_DIR_NAME,
    TIMESTAMP_FILENAME_FORMAT,
    ensure_reports_dir,
    isoformat_timestamp,
    write_run_report,
)
from .telemetry import (
    SCHEMA_VERSION,
    TELEMETRY_SCHEMA,
    TelemetryEvent,
    TelemetryValidationError,
    coerce_event,
    configure_event_sink,
    dump_to_file,
    dumps,
    emit_event,
    ensure_timestamp,
    loads,
    make_event,
    register_listener,
    unregister_listener,
    validate_event,
)
from .x_env_x import ensure_workspace_on_syspath, get_env_bool, get_env_str
from .x_http_client_x import HttpClient, HttpError, HttpResponse
from .x_logging_utils_x import get_logger, log_debug, log_error, log_info
from .x_subprocess_utils_x import CommandError, run_command

__all__ = [
    "REPORTS_DIR_NAME",
    "SCHEMA_VERSION",
    "TELEMETRY_SCHEMA",
    "TIMESTAMP_FILENAME_FORMAT",
    "CommandError",
    "CommandRunner",
    "ExportResult",
    "HttpClient",
    "HttpError",
    "HttpResponse",
    "JsonBoardState",
    "JsonCardRecord",
    "TelemetryEvent",
    "TelemetryValidationError",
    "board_from_records",
    "coerce_event",
    "configure_event_sink",
    "dump_board",
    "dump_to_file",
    "dumps",
    "emit_event",
    "ensure_reports_dir",
    "ensure_timestamp",
    "ensure_workspace_on_syspath",
    "export_graphviz_to_svg",
    "export_markdown_to_pdf",
    "export_mermaid_to_svg",
    "get_env_bool",
    "get_env_str",
    "get_logger",
    "isoformat_timestamp",
    "load_json_board",
    "loads",
    "log_debug",
    "log_error",
    "log_info",
    "make_event",
    "register_listener",
    "run_command",
    "save_json_board",
    "unregister_listener",
    "validate_event",
    "write_run_report",
]
