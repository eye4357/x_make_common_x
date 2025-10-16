"""Shared telemetry schema and helpers for orchestrator packages."""

from __future__ import annotations

import json
import os
import pathlib
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Final, Protocol, TextIO, TypedDict, cast

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping
    from pathlib import Path

    from jsonschema import (  # type: ignore[import-untyped]
        Draft202012Validator as _DraftValidatorType,
    )
    from jsonschema import (
        ValidationError as _ValidationErrorType,
    )
else:
    Path = pathlib.Path
    from jsonschema import (  # type: ignore[import-untyped]
        Draft202012Validator as _DraftValidatorType,
    )
    from jsonschema import (
        ValidationError as _ValidationErrorType,
    )

SCHEMA_VERSION: Final[str] = "0.20.2"


JSONValue = str | int | float | bool | None | list["JSONValue"] | dict[str, "JSONValue"]


class TelemetryEvent(TypedDict):
    """Typed contract for orchestrator telemetry events."""

    version: str
    timestamp: str
    source: str
    phase: str
    repository: str | None
    tool: str | None
    status: str
    attempt: int
    duration_ms: int | None
    details: dict[str, JSONValue]


# JSON Schema definition mirrors the TypedDict above. We keep it close to the
# data shape so unit tests and downstream consumers can validate external events
# without importing Python types.
TELEMETRY_SCHEMA: Final[dict[str, object]] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/eye4357/x_runner_x/telemetry-event.schema.json",
    "type": "object",
    "required": [
        "version",
        "timestamp",
        "source",
        "phase",
        "repository",
        "tool",
        "status",
        "attempt",
        "duration_ms",
        "details",
    ],
    "properties": {
        "version": {
            "type": "string",
            "const": SCHEMA_VERSION,
        },
        "timestamp": {
            "type": "string",
            "format": "date-time",
        },
        "source": {
            "type": "string",
            "enum": [
                "orchestrator",
                "legatus",
                "clones",
                "visitor",
                "pip_updates",
                "pypi",
            ],
        },
        "phase": {
            "type": "string",
            "pattern": "^[a-z0-9_]+$",
            "minLength": 1,
        },
        "repository": {
            "type": ["string", "null"],
        },
        "tool": {
            "type": ["string", "null"],
        },
        "status": {
            "type": "string",
            "enum": [
                "started",
                "succeeded",
                "failed",
                "skipped",
                "retried",
                "quarantined",
            ],
        },
        "attempt": {
            "type": "integer",
            "minimum": 1,
        },
        "duration_ms": {
            "type": ["integer", "null"],
            "minimum": 0,
        },
        "details": {
            "type": "object",
            "additionalProperties": True,
        },
    },
    "additionalProperties": False,
}


class _JsonSchemaValidator(Protocol):
    def validate(self, instance: Mapping[str, object]) -> None: ...


class _JsonSchemaValidatorFactory(Protocol):
    def __call__(self, schema: Mapping[str, object]) -> _JsonSchemaValidator: ...


class _ValidationError(Protocol):
    path: Iterable[object]
    message: str


Draft202012Validator = cast("_JsonSchemaValidatorFactory", _DraftValidatorType)
ValidationError = cast("type[Exception]", _ValidationErrorType)


_VALIDATOR: _JsonSchemaValidator = Draft202012Validator(TELEMETRY_SCHEMA)
_LISTENER_LOCK = threading.RLock()
_EVENT_LISTENERS: list[Callable[[TelemetryEvent], None]] = []
_SINK_LOCK = threading.RLock()
_default_sink: TextIO | None = None
_echo_stdout: bool = False
_SUPPRESS_ENV = "X_TELEMETRY_SUPPRESS_STDOUT"


@dataclass(frozen=True)
class TelemetryValidationError(Exception):
    """Raised when telemetry payloads fail schema validation."""

    message: str

    def __str__(self) -> str:  # pragma: no cover - dataclass repr adequate
        return self.message


def validate_event(payload: Mapping[str, object]) -> None:
    """Validate a telemetry payload against the canonical schema.

    Raises:
        TelemetryValidationError: if the payload violates the JSON schema.
    """

    candidate: dict[str, object] = dict(payload)
    try:
        _VALIDATOR.validate(candidate)
    except ValidationError as exc:
        error = cast("_ValidationError", exc)
        path_iter = tuple(error.path)
        path = "/".join(str(part) for part in path_iter)
        message_text = error.message
        prefix = (
            f"Telemetry payload invalid at {path}: "
            if path
            else "Telemetry payload invalid: "
        )
        raise TelemetryValidationError(prefix + message_text) from exc


def coerce_event(event: Mapping[str, object]) -> TelemetryEvent:
    """Return a TelemetryEvent after validating the mapping."""

    candidate = dict(event)
    validate_event(candidate)
    return cast("TelemetryEvent", candidate)


def ensure_timestamp(timestamp: datetime | str | None) -> str:
    """Normalise timestamps to ISO-8601 UTC strings."""

    if isinstance(timestamp, str):
        return timestamp
    current = timestamp or datetime.now(UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return current.astimezone(UTC).isoformat().replace("+00:00", "Z")


def make_event(  # noqa: PLR0913
    *,
    source: str,
    phase: str,
    status: str,
    repository: str | None,
    tool: str | None,
    attempt: int,
    duration_ms: int | None,
    details: Mapping[str, JSONValue] | None = None,
    timestamp: datetime | str | None = None,
) -> TelemetryEvent:
    """Create a validated telemetry event from primitive data."""

    payload: dict[str, object] = {
        "version": SCHEMA_VERSION,
        "timestamp": ensure_timestamp(timestamp),
        "source": source,
        "phase": phase,
        "repository": repository,
        "tool": tool,
        "status": status,
        "attempt": attempt,
        "duration_ms": duration_ms,
    }
    detail_map: dict[str, JSONValue] = {} if details is None else dict(details)
    payload["details"] = detail_map
    return coerce_event(payload)


def dumps(event: TelemetryEvent, *, indent: int | None = None) -> str:
    """Serialize a telemetry event to JSON after validation."""

    validated = coerce_event(event)
    return json.dumps(validated, separators=(",", ":"), indent=indent, sort_keys=True)


def loads(payload: str) -> TelemetryEvent:
    """Deserialize a JSON payload into a validated telemetry event."""

    raw: object = json.loads(payload)
    if not isinstance(raw, dict):
        message = "Telemetry payload must decode to an object"
        raise TelemetryValidationError(message)
    typed = cast("dict[str, JSONValue]", raw)
    return coerce_event(typed)


def dump_to_file(event: TelemetryEvent, path: Path) -> None:
    """Write a telemetry event to disk as JSON lines."""

    line = dumps(event)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)
        handle.write("\n")


def register_listener(listener: Callable[[TelemetryEvent], None]) -> Callable[[], None]:
    """Register a callback invoked whenever ``emit_event`` is called.

    Returns a callable that removes the listener when invoked.
    """

    with _LISTENER_LOCK:
        _EVENT_LISTENERS.append(listener)

    def _remover() -> None:
        unregister_listener(listener)

    return _remover


def unregister_listener(listener: Callable[[TelemetryEvent], None]) -> None:
    """Remove a previously registered telemetry listener."""

    with _LISTENER_LOCK:
        try:
            _EVENT_LISTENERS.remove(listener)
        except ValueError:
            return


def configure_event_sink(sink: TextIO | None, *, echo: bool | None = None) -> None:
    """Configure the default telemetry sink and optional stdout echo.

    Args:
        sink: A file-like object that will receive JSON events. ``None`` resets
            the sink to the default behaviour (stdout).
        echo: When provided, controls whether events should continue to be
            echoed to stdout when a default sink is configured. ``False`` keeps
            stdout quiet; ``True`` mirrors events to stdout in addition to the
            sink. ``None`` leaves the previous echo preference unchanged.
    """

    with _SINK_LOCK:
        global _default_sink, _echo_stdout  # noqa: PLW0603
        _default_sink = sink
        if echo is not None:
            _echo_stdout = echo


def _stdout_enabled() -> bool:
    env_value = os.environ.get(_SUPPRESS_ENV)
    if env_value is None:
        return True
    lowered = env_value.strip().lower()
    return lowered not in {"1", "true", "yes", "on"}


def emit_event(event: TelemetryEvent, *, sink: TextIO | None = None) -> None:
    """Emit a telemetry event to stdout or an explicit text sink."""

    validated = coerce_event(event)
    with _LISTENER_LOCK:
        listeners = list(_EVENT_LISTENERS)
    with _SINK_LOCK:
        default_sink = _default_sink
        echo_stdout = _echo_stdout
    target_sink = sink if sink is not None else default_sink
    for listener in listeners:
        try:
            payload = cast("TelemetryEvent", dict(validated))
            listener(payload)
        except Exception:  # noqa: BLE001,S112
            continue
    line = dumps(validated)
    wrote_to_sink = False
    if target_sink is not None:
        try:
            target_sink.write(line)
            target_sink.write("\n")
            target_sink.flush()
            wrote_to_sink = True
        except Exception:  # noqa: BLE001
            # Fall back to stdout if sink write fails; consumer-side logging
            # can surface the issue without breaking telemetry propagation.
            wrote_to_sink = False
    should_print = sink is not None
    if sink is None:
        should_print = True if target_sink is None else echo_stdout
    if should_print and _stdout_enabled():
        print(line, flush=True)
    elif not wrote_to_sink and target_sink is not None and _stdout_enabled():
        # Ensure the event is not lost when both sink write and explicit echo
        # paths were skipped.
        print(line, flush=True)


__all__ = [
    "SCHEMA_VERSION",
    "TELEMETRY_SCHEMA",
    "TelemetryEvent",
    "TelemetryValidationError",
    "coerce_event",
    "configure_event_sink",
    "dump_to_file",
    "dumps",
    "emit_event",
    "ensure_timestamp",
    "loads",
    "make_event",
    "register_listener",
    "unregister_listener",
    "validate_event",
]
