from __future__ import annotations

# ruff: noqa: S101
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest

if TYPE_CHECKING:
    from collections.abc import Sequence

    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
else:  # pragma: no cover - runtime stubs for type names
    CaptureFixture = object
    MonkeyPatch = object

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
root_str = str(WORKSPACE_ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

from x_make_common_x.telemetry import (  # noqa: E402,I001  # pylint: disable=wrong-import-position
    SCHEMA_VERSION,
    TELEMETRY_SCHEMA,
    TelemetryEvent,
    TelemetryValidationError,
    coerce_event,
    configure_event_sink,
    dumps,
    emit_event,
    ensure_timestamp,
    loads,
    make_event,
    validate_event,
)


TelemetryEventType = TelemetryEvent


def _sample_event(**overrides: object) -> TelemetryEventType:
    base = make_event(
        source="visitor",
        phase="inspection",
        status="succeeded",
        repository="x_make_common_x",
        tool="pytest",
        attempt=1,
        duration_ms=1200,
        details={
            "message": "pytest completed",
            "artifact_path": "out/reports/test.json",
        },
        timestamp=datetime(2025, 10, 13, 12, 30, tzinfo=UTC),
    )
    return coerce_event({**base, **overrides})


def test_make_event_uses_current_schema_version() -> None:
    event = _sample_event()
    assert event["version"] == SCHEMA_VERSION


def test_validate_event_accepts_sample_payload() -> None:
    event = _sample_event()
    validate_event(event)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source", "unknown"),
        ("status", "bogus"),
        ("attempt", 0),
        ("version", "0.20.1"),
    ],
)
def test_validate_event_rejects_invalid_values(field: str, value: object) -> None:
    event = _sample_event()
    broken: dict[str, object] = {**event, field: value}
    with pytest.raises(TelemetryValidationError):
        validate_event(broken)


def test_round_trip_preserves_payload() -> None:
    event = _sample_event()
    text = dumps(event)
    assert loads(text) == event


def test_ensure_timestamp_normalises_naive_datetime() -> None:
    naive = datetime(2025, 10, 13, 10, 0)  # noqa: DTZ001
    iso = ensure_timestamp(naive)
    assert iso.endswith("Z")
    parsed = datetime.fromisoformat(f"{iso.removesuffix('Z')}+00:00")
    assert parsed.tzinfo == UTC


def test_schema_rejects_additional_fields() -> None:
    with pytest.raises(TelemetryValidationError):
        _sample_event(extra="value")


def test_coerce_event_accepts_plain_mapping() -> None:
    event = _sample_event()
    mapping: dict[str, object] = dict(event)
    assert coerce_event(mapping) == event


def test_schema_definition_matches_required_fields() -> None:
    required = cast("Sequence[str]", TELEMETRY_SCHEMA["required"])
    fields = tuple(TelemetryEvent.__annotations__.keys())
    assert sorted(required) == sorted(fields)


def test_configured_sink_receives_events(
    tmp_path: Path, capfd: CaptureFixture[str]
) -> None:
    event = _sample_event()
    sink_path = Path(tmp_path) / "events.jsonl"
    with sink_path.open("a", encoding="utf-8") as handle:
        configure_event_sink(handle, echo=False)
        emit_event(event)
        configure_event_sink(None, echo=False)
    captured = capfd.readouterr()
    assert captured.out == ""
    lines = sink_path.read_text(encoding="utf-8").strip().splitlines()
    assert lines == [dumps(event)]


def test_stdout_suppression_env(
    monkeypatch: MonkeyPatch, capfd: CaptureFixture[str]
) -> None:
    event = _sample_event()
    monkeypatch.setenv("X_TELEMETRY_SUPPRESS_STDOUT", "1")
    emit_event(event)
    captured = capfd.readouterr()
    assert captured.out == ""
    monkeypatch.delenv("X_TELEMETRY_SUPPRESS_STDOUT", raising=False)


def test_sink_echo_mirrors_stdout(
    tmp_path: Path,
    capfd: CaptureFixture[str],
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.delenv("X_TELEMETRY_SUPPRESS_STDOUT", raising=False)
    event = _sample_event()
    sink_path = Path(tmp_path) / "echo.jsonl"
    with sink_path.open("a", encoding="utf-8") as handle:
        configure_event_sink(handle, echo=True)
        emit_event(event)
        configure_event_sink(None, echo=False)
    captured = capfd.readouterr()
    assert dumps(event) in captured.out
    lines = sink_path.read_text(encoding="utf-8").strip().splitlines()
    assert lines == [dumps(event)]
