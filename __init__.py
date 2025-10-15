"""Public interface for shared x_make_common_x utilities."""

from __future__ import annotations

from .json_board import (
    BoardState as JsonBoardState,
    CardRecord as JsonCardRecord,
    board_from_records,
    dump_board,
    load_board as load_json_board,
    save_board as save_json_board,
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
    "JsonBoardState",
    "JsonCardRecord",
    "SCHEMA_VERSION",
    "TELEMETRY_SCHEMA",
    "board_from_records",
    "dump_board",
    "load_json_board",
    "save_json_board",
    "CommandError",
    "HttpClient",
    "HttpError",
    "HttpResponse",
    "TelemetryEvent",
    "TelemetryValidationError",
    "coerce_event",
    "configure_event_sink",
    "dump_to_file",
    "dumps",
    "emit_event",
    "ensure_timestamp",
    "ensure_workspace_on_syspath",
    "get_env_bool",
    "get_env_str",
    "get_logger",
    "loads",
    "log_debug",
    "log_error",
    "log_info",
    "make_event",
    "register_listener",
    "run_command",
    "unregister_listener",
    "validate_event",
]
