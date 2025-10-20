"""Lightweight telemetry helpers for x_make tools."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

from .run_reports import isoformat_timestamp
from .x_logging_utils_x import get_logger

JSONPrimitive = str | int | float | bool | None
JSONValue = JSONPrimitive | Mapping[str, "JSONValue"] | Sequence["JSONValue"]


def _coerce_json_mapping(mapping: Mapping[str, JSONValue] | None) -> Mapping[str, JSONValue] | None:
    if mapping is None:
        return None
    # Normalise nested values into JSON-compatible structures.
    normalised: dict[str, JSONValue] = {}
    for key, value in mapping.items():
        normalised[str(key)] = _json_ready(value)
    return normalised


def _json_ready(value: JSONValue | object) -> JSONValue:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(k): _json_ready(v) for k, v in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_json_ready(entry) for entry in value]
    return str(value)


@dataclass(slots=True, frozen=True)
class TelemetryEvent:
    """Structured telemetry envelope with JSON-serialisable payload."""

    timestamp: str
    source: str
    phase: str
    status: str
    repository: str | None = None
    tool: str | None = None
    attempt: int | None = None
    duration_ms: int | None = None
    details: Mapping[str, JSONValue] | None = None

    def as_dict(self) -> dict[str, JSONValue]:
        payload: dict[str, JSONValue] = {
            "timestamp": self.timestamp,
            "source": self.source,
            "phase": self.phase,
            "status": self.status,
        }
        if self.repository is not None:
            payload["repository"] = self.repository
        if self.tool is not None:
            payload["tool"] = self.tool
        if self.attempt is not None:
            payload["attempt"] = self.attempt
        if self.duration_ms is not None:
            payload["duration_ms"] = self.duration_ms
        if self.details is not None:
            payload["details"] = {
                key: _json_ready(value)
                for key, value in self.details.items()
            }
        return payload


def make_event(
    *,
    source: str,
    phase: str,
    status: str,
    repository: str | None = None,
    tool: str | None = None,
    attempt: int | None = None,
    duration_ms: int | None = None,
    details: Mapping[str, JSONValue] | None = None,
    timestamp: datetime | None = None,
) -> TelemetryEvent:
    """Build a :class:`TelemetryEvent` for downstream emission."""

    event_timestamp = isoformat_timestamp(timestamp or datetime.now(UTC))
    return TelemetryEvent(
        timestamp=event_timestamp,
        source=source,
        phase=phase,
        status=status,
        repository=repository,
        tool=tool,
        attempt=attempt,
        duration_ms=duration_ms,
        details=_coerce_json_mapping(details),
    )


def emit_event(event: Mapping[str, JSONValue] | TelemetryEvent) -> None:
    """Emit telemetry to the shared logger.

    The return value is intentionally ``None`` so callers can chain this helper
    inside pipelines without disrupting their flow.
    """

    logger = get_logger("x_make.telemetry")
    payload: Mapping[str, JSONValue]
    if isinstance(event, TelemetryEvent):
        payload = event.as_dict()
    else:
        payload = event
    logger.info("telemetry event: %s", payload)


__all__ = [
    "JSONValue",
    "TelemetryEvent",
    "emit_event",
    "make_event",
]
